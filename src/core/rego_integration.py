"""Rego policy evaluation integration.

This module provides the bridge between Python and Rego policies:
- Loads and compiles .rego policies at server startup using regopy
- Evaluates policies using embedded Rego interpreter
- Enriches input with external data (PyPI metadata, etc.)
- Converts ToolUseEvent + ParsedCommand to Rego input
- Converts Rego results back to PolicyDecision objects
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

import httpx
from regopy import Interpreter, NodeKind
from src.server.common.models import ToolUseEvent, PostFileEditEvent, PolicyDecision, PolicyAction

from src.core.command_parser import ParsedCommand

logger = logging.getLogger(__name__)


class RegoEvaluator:
    """Evaluates policies using regopy (embedded Rego interpreter).

    Policies are loaded once at initialization for fast per-request evaluation.
    """

    def __init__(self, policy_dir: str = "policies"):
        """Initialize Rego interpreter and load all policies.

        Args:
            policy_dir: Directory containing .rego policy files
        """
        self.policy_dir = Path(policy_dir)
        self.interpreter = Interpreter()

        if not self.policy_dir.exists():
            logger.warning(f"Policy directory {self.policy_dir} does not exist, creating it")
            self.policy_dir.mkdir(parents=True, exist_ok=True)
            return

        # Load system policies
        self._load_all_policies()

        logger.info("Rego evaluator initialized successfully")

    def _load_all_policies(self):
        """Load all .rego files from policy directory."""
        rego_files = list(self.policy_dir.rglob("*.rego"))

        if not rego_files:
            logger.warning(f"No .rego files found in {self.policy_dir}")
            return

        logger.info(f"Loading {len(rego_files)} .rego policy files")

        for rego_file in rego_files:
            try:
                policy_content = rego_file.read_text()
                module_name = str(rego_file.relative_to(self.policy_dir))
                self.interpreter.add_module(module_name, policy_content)
                logger.debug(f"Loaded policy: {rego_file}")
            except Exception as e:
                logger.error(f"Failed to load policy {rego_file}: {e}")
                raise

    def evaluate(
        self,
        event: ToolUseEvent,
        parsed: ParsedCommand,
        bundles: List[str]
    ) -> List[PolicyDecision]:
        """Evaluate policies against an event.

        Recursively evaluates the main command plus all chained (&&, ||, ;) and
        piped (|) commands to ensure security policies are enforced on the entire
        command chain.

        Args:
            event: The tool use event from the client
            parsed: Parsed command structure (from bashlex)
            bundles: List of policy bundles to evaluate (e.g., ["universal", "python_uv"])

        Returns:
            List of PolicyDecision objects from all matching rules across all commands
        """
        all_decisions = []

        # Evaluate this command's policies
        input_doc = self._build_input_document(event, parsed)
        self._enrich_input(input_doc, parsed)

        for bundle in bundles:
            try:
                bundle_decisions = self._evaluate_bundle(bundle, input_doc)
                all_decisions.extend(bundle_decisions)
            except Exception as e:
                logger.error(f"Error evaluating bundle '{bundle}': {e}")
                all_decisions.append(PolicyDecision(
                    action=PolicyAction.ASK,
                    reason=f"Policy evaluation error in bundle '{bundle}': {str(e)}"
                ))

        # Recursively evaluate all chained commands (&&, ||, ;)
        for chained_cmd in parsed.chained:
            chained_decisions = self.evaluate(event, chained_cmd, bundles)
            all_decisions.extend(chained_decisions)

        # Recursively evaluate all piped commands (|)
        for piped_cmd in parsed.pipes:
            piped_decisions = self.evaluate(event, piped_cmd, bundles)
            all_decisions.extend(piped_decisions)

        return all_decisions

    def evaluate_guidance_activations(
        self,
        event: PostFileEditEvent,
        bundles: List[str]
    ) -> List[str]:
        """Evaluate which guidance checks should be activated for a file edit.

        Args:
            event: The file edit event from the client
            bundles: List of policy bundles to evaluate (e.g., ["universal", "python_uv"])

        Returns:
            List of guidance check names to activate (e.g., ["comment_ratio", "mid_code_import"])
        """
        all_activations = []

        # Build input document from file edit event
        input_doc = self._build_file_edit_input_document(event)

        for bundle in bundles:
            try:
                bundle_activations = self._evaluate_guidance_activations_bundle(bundle, input_doc)
                all_activations.extend(bundle_activations)
            except Exception as e:
                logger.error(f"Error evaluating guidance activations for bundle '{bundle}': {e}")

        return list(set(all_activations))

    def _build_input_document(self, event: ToolUseEvent, parsed: ParsedCommand) -> Dict[str, Any]:
        """Convert ToolUseEvent and ParsedCommand to Rego input.

        Args:
            event: The tool use event
            parsed: Parsed command structure

        Returns:
            Dictionary suitable for Rego input
        """
        parsed_dict = {
            "executable": parsed.executable,
            "subcommand": parsed.subcommand,
            "arguments": parsed.arguments,
            "flags": parsed.flags,
            "options": parsed.options,
            "redirects": [{"op": op, "path": path} for op, path in parsed.redirects],
            "original": parsed.original,
        }

        input_doc = {
            "event": {
                "session_id": event.session_id,
                "source_client": event.source_client,
                "tool_name": event.tool_name,
                "tool_is_bash": event.tool_is_bash,
                "command": event.command,
                "parameters": event.parameters or {},
            },
            "parsed": parsed_dict,
        }

        return input_doc

    def _build_file_edit_input_document(self, event: PostFileEditEvent) -> Dict[str, Any]:
        """Convert PostFileEditEvent to Rego input.

        Args:
            event: The file edit event

        Returns:
            Dictionary suitable for Rego input
        """
        input_doc = {
            "event": {
                "session_id": event.session_id,
                "source_client": event.source_client,
            },
            "file_path": event.file_path,
            "structured_patch": [
                {
                    "old_start": patch.oldStart,
                    "old_lines": patch.oldLines,
                    "new_start": patch.newStart,
                    "new_lines": patch.newLines,
                    "lines": [
                        {
                            "operation": line.operation,
                            "content": line.content
                        }
                        for line in patch.lines
                    ]
                }
                for patch in (event.structured_patch or [])
            ]
        }

        return input_doc

    def _enrich_input(self, input_doc: Dict[str, Any], parsed: ParsedCommand) -> None:
        """Enrich input document with external data.

        This method calls Python functions to fetch external data (PyPI, npm, etc.)
        and adds it to the input document before policy evaluation.

        Args:
            input_doc: Input document to enrich (modified in place)
            parsed: Parsed command for context
        """
        # PyPI package metadata enrichment
        if parsed.executable == "uv" and parsed.subcommand == "add":
            if parsed.arguments:
                package_name = parsed.arguments[0]
                metadata = self._fetch_pypi_metadata(package_name)
                if metadata:
                    input_doc["pypi_metadata"] = metadata

        elif parsed.executable == "pip" and parsed.subcommand == "install":
            if parsed.arguments:
                package_name = parsed.arguments[0]
                metadata = self._fetch_pypi_metadata(package_name)
                if metadata:
                    input_doc["pypi_metadata"] = metadata

    def _fetch_pypi_metadata(self, package_name: str) -> Optional[Dict[str, Any]]:
        """Fetch package metadata from PyPI.

        Args:
            package_name: Package name to look up

        Returns:
            Dictionary with metadata or None on error
        """
        try:
            response = httpx.get(
                f"https://pypi.org/pypi/{package_name}/json",
                timeout=5.0,
                follow_redirects=True
            )
            response.raise_for_status()
            data = response.json()

            # Extract upload date from first release
            releases = data.get("releases", {})
            first_version = None
            oldest_date = None

            for version, files in releases.items():
                if files:
                    upload_date_str = files[0].get("upload_time_iso_8601")
                    if upload_date_str:
                        upload_date = datetime.fromisoformat(upload_date_str.replace("Z", "+00:00"))
                        if oldest_date is None or upload_date < oldest_date:
                            oldest_date = upload_date
                            first_version = version

            if oldest_date:
                age_days = (datetime.now(oldest_date.tzinfo) - oldest_date).days
                return {
                    "name": package_name,
                    "age_days": age_days,
                    "first_version": first_version,
                    "first_upload_date": oldest_date.isoformat()
                }

            logger.warning(f"No release data found for package: {package_name}")
            return None

        except httpx.HTTPStatusError as e:
            logger.warning(f"PyPI package not found: {package_name} (status {e.response.status_code})")
            return None
        except Exception as e:
            logger.error(f"Error fetching PyPI metadata for {package_name}: {e}")
            return None

    def _evaluate_bundle(self, bundle: str, input_doc: Dict[str, Any]) -> List[PolicyDecision]:
        """Evaluate a specific bundle's policies.

        Args:
            bundle: Bundle name (e.g., "universal", "python_uv")
            input_doc: Rego input document

        Returns:
            List of PolicyDecision objects from this bundle
        """
        query = f"data.{bundle}.decisions"

        try:
            self.interpreter.set_input(input_doc)
            output = self.interpreter.query(query)

            if not output.ok():
                return []

            # Get the first expression result (not binding, since we're querying a data path)
            decisions_node = output.expressions(index=0)
            if decisions_node is None:
                return []

            decisions = self._node_to_python(decisions_node)
            logger.debug(f"Decisions from bundle '{bundle}': {decisions}")

            if not decisions:
                return []

            return self._convert_rego_output(decisions)

        except Exception as e:
            logger.error(f"Rego query failed for bundle '{bundle}': {e}")
            raise

    def _evaluate_guidance_activations_bundle(self, bundle: str, input_doc: Dict[str, Any]) -> List[str]:
        """Evaluate a specific bundle's guidance activation rules.

        Args:
            bundle: Bundle name (e.g., "universal", "python_uv")
            input_doc: Rego input document

        Returns:
            List of guidance check names (e.g., ["comment_ratio", "mid_code_import"])
        """
        query = f"data.{bundle}.guidance_activations"

        try:
            self.interpreter.set_input(input_doc)
            output = self.interpreter.query(query)

            if not output.ok():
                return []

            activations_node = output.expressions(index=0)
            if activations_node is None:
                return []

            activations = self._node_to_python(activations_node)
            logger.debug(f"Guidance activations from bundle '{bundle}': {activations}")

            if not activations:
                return []

            return self._convert_rego_guidance_activations(activations)

        except Exception as e:
            logger.error(f"Rego query failed for guidance activations in bundle '{bundle}': {e}")
            raise

    def _node_to_python(self, node) -> Any:
        """Convert regopy Node to Python object.

        Args:
            node: regopy Node object

        Returns:
            Python equivalent (list, dict, str, int, float, bool, None)
        """
        kind = node.kind

        if kind == NodeKind.Int:
            return node.value
        elif kind == NodeKind.Float:
            return node.value
        elif kind == NodeKind.String:
            return node.value
        elif kind == NodeKind.True_:
            return True
        elif kind == NodeKind.False_:
            return False
        elif kind == NodeKind.Null:
            return None
        elif kind == NodeKind.Array:
            result = []
            index = 0
            while True:
                try:
                    item = node.index(index)
                    result.append(self._node_to_python(item))
                    index += 1
                except:
                    break
            return result
        elif kind == NodeKind.Object:
            # Convert object to dict by iterating keys
            # Note: regopy doesn't provide direct key iteration,
            # so we use json() and parse it
            return json.loads(node.json())
        elif kind == NodeKind.Set:
            return json.loads(node.json())
        else:
            return json.loads(node.json())

    def _convert_rego_output(self, rego_decisions: List[Dict[str, Any]]) -> List[PolicyDecision]:
        """Convert Rego decision results to PolicyDecision objects.

        Args:
            rego_decisions: List of set elements from Rego decisions[decision]
                           Format: [{"json_string": true}, ...]
                           Where json_string is the serialized decision object

        Returns:
            List of PolicyDecision objects
        """
        decisions = []

        for decision_set_item in rego_decisions:
            try:
                if not isinstance(decision_set_item, dict):
                    logger.warning(f"Unexpected decision format: {decision_set_item}")
                    continue

                # Rego sets are represented as {element: true, element2: true, ...}
                # Multiple rules can match and add multiple decisions to the set
                # Iterate through ALL keys in the set
                for decision_json_str in decision_set_item.keys():
                    try:
                        decision_obj = json.loads(decision_json_str)

                        action_str = decision_obj.get("action", "").lower()
                        reason = decision_obj.get("reason")

                        action_map = {
                            "allow": PolicyAction.ALLOW,
                            "deny": PolicyAction.DENY,
                            "ask": PolicyAction.ASK,
                        }

                        action = action_map.get(action_str)
                        if not action:
                            logger.warning(f"Unknown action '{action_str}' in decision, skipping")
                            continue

                        decisions.append(PolicyDecision(action=action, reason=reason))

                    except Exception as e:
                        logger.error(f"Failed to convert decision to PolicyDecision: {e}")
                        logger.debug(f"Decision data: {decision_json_str}")
                        continue

            except Exception as e:
                logger.error(f"Failed to process decision set: {e}")
                logger.debug(f"Decision set data: {decision_set_item}")
                continue

        return decisions

    def _convert_rego_guidance_activations(self, rego_activations: List[Dict[str, Any]]) -> List[str]:
        """Convert Rego guidance activation results to list of check names.

        Args:
            rego_activations: List of set elements from Rego guidance_activations[check]
                             Format: [{"check_name": true}, ...]
                             Where check_name is the guidance check identifier

        Returns:
            List of guidance check names (strings)
        """
        check_names = []

        for activation_set_item in rego_activations:
            try:
                if not isinstance(activation_set_item, dict):
                    logger.warning(f"Unexpected activation format: {activation_set_item}")
                    continue

                for check_name in activation_set_item.keys():
                    if isinstance(check_name, str):
                        check_names.append(check_name)
                    else:
                        logger.warning(f"Unexpected check name type: {type(check_name)}, value: {check_name}")

            except Exception as e:
                logger.error(f"Failed to process guidance activation: {e}")
                logger.debug(f"Activation data: {activation_set_item}")
                continue

        return check_names
