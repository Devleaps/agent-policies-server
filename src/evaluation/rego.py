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
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

import httpx
from regopy import Interpreter, NodeKind
from src.server.models import (
    ToolUseEvent,
    PostFileEditEvent,
    PolicyDecision,
    PolicyGuidance,
    PolicyAction,
)

from src.evaluation.parser import ParsedCommand

logger = logging.getLogger(__name__)


def _is_within(path: str, root: str) -> bool:
    # /workspace/../etc is not inside /workspace
    path = os.path.normpath(path)
    root = os.path.normpath(root).rstrip("/")
    return path == root or path.startswith(root + "/")


@dataclass(frozen=True)
class Location:
    """Where a command in a chain runs, as far as the policy can tell.

    `cwd` is the absolute directory, or None when unknown. `outside` means the
    directory is outside the workspace or cannot be determined; relative
    paths used from there are never workspace-relative.
    """

    cwd: Optional[str]
    outside: bool

    @classmethod
    def initial(cls, event: ToolUseEvent) -> "Location":
        if event.workspace_root and event.cwd:
            cwd = os.path.normpath(event.cwd)
            return cls(cwd, not _is_within(cwd, event.workspace_root))
        # Without a workspace root, relative paths are assumed to be inside
        return cls(event.cwd, False)

    def after_cd(self, event: ToolUseEvent, cd: ParsedCommand) -> "Location":
        unknown = Location(None, True)
        if cd.flags or cd.options:
            return unknown
        target = cd.arguments[0] if cd.arguments else "~"
        if target == "-" or target in cd.expanded_words:
            return unknown

        if target == "~" or target.startswith("~/"):
            if not event.home:
                return unknown
            target = event.home + target[1:]
        elif target.startswith("~"):
            return unknown

        climbs = os.path.isabs(target) or ".." in target.split("/")
        if os.path.isabs(target):
            new_cwd = os.path.normpath(target)
        elif self.cwd:
            new_cwd = os.path.normpath(os.path.join(self.cwd, target))
        else:
            # Unknown starting directory: only a plain descent stays inside
            return Location(None, self.outside or climbs)

        if event.workspace_root:
            return Location(new_cwd, not _is_within(new_cwd, event.workspace_root))
        return Location(new_cwd, self.outside or climbs)


UNKNOWN_LOCATION = Location(None, True)

# Where a statement may run from, most likely first
Locations = Tuple[Location, ...]

# Past this many possible locations, the location is taken as unknown
MAX_LOCATIONS = 8


def _unique(locations) -> Locations:
    result = tuple(dict.fromkeys(locations))
    if len(result) > MAX_LOCATIONS:
        return (UNKNOWN_LOCATION,)
    return result


def _is_workspace_relative(path: str) -> bool:
    # Any .. segment may climb out: x/../../secret
    return not path.startswith(("/", "~")) and ".." not in path.split("/")


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
            logger.warning(
                f"Policy directory {self.policy_dir} does not exist, creating it"
            )
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
        self, event: ToolUseEvent, parsed: ParsedCommand, bundles: List[str]
    ) -> List[PolicyDecision]:
        """Evaluate policies against an event.

        Recursively evaluates the main command plus all chained (&&, ||, ;) and
        piped (|) commands to ensure security policies are enforced on the entire
        command chain.

        Args:
            event: The tool use event from the client
            parsed: Parsed command structure (from bashlex)
            bundles: List of policy bundles to evaluate (e.g., ["universal", "python_uv"])

        A command is only as allowed as its least-decided segment: if any
        segment matches no rule, ALLOW decisions from the other segments are
        dropped so the client's own permission system decides. DENY and ASK
        from any segment still apply.

        Returns:
            List of PolicyDecision objects from all matching rules across all commands
        """
        segments = self.evaluate_segments(event, parsed, bundles)
        all_decisions = [d for segment in segments for d in segment]

        if any(not segment for segment in segments):
            return [d for d in all_decisions if d.action != PolicyAction.ALLOW]

        return all_decisions

    def evaluate_segments(
        self,
        event: ToolUseEvent,
        parsed: ParsedCommand,
        bundles: List[str],
        locations: Optional[Locations] = None,
    ) -> List[List[PolicyDecision]]:
        """Evaluate each command in the chain, pipes and process substitutions.

        Returns one list of decisions per command segment, in order; an empty
        list means no rule matched that segment.
        """
        if locations is None:
            locations = (Location.initial(event),)
        return self._evaluate_sequence(
            event, [parsed] + parsed.chained, bundles, locations
        )

    def _evaluate_sequence(
        self,
        event: ToolUseEvent,
        commands: List[ParsedCommand],
        bundles: List[str],
        locations: Locations,
    ) -> List[List[PolicyDecision]]:
        """Evaluate statements that run one after the other in one shell.

        A `cd` moves the location the later statements are evaluated from, so
        `cd ../.. && cat x` checks x where it really is. A cd may fail, so
        past anything but `&&` a statement may also run from where the cd
        started: every such location is kept, newest first. Pipes, process
        substitutions and subshells do not move it.
        """
        segments = []
        # Every location seen since the last operator other than &&
        run = list(locations)
        previous_operator = None
        for command in commands:
            if command.location_unknown_before:
                locations = (UNKNOWN_LOCATION,)
            segments.extend(
                self._evaluate_command_segments(event, command, bundles, locations)
            )
            # A piped cd runs in a subshell
            if command.executable == "cd" and not command.pipes:
                moved = tuple(loc.after_cd(event, command) for loc in locations)
                # After ||, the cd is skipped when the command before it
                # succeeded: in "a || cd x && cat y", cat may run from either
                if previous_operator == "||":
                    moved += locations
                locations = _unique(moved)
            if command.location_unknown_after:
                locations = (UNKNOWN_LOCATION,)
            run.extend(locations)
            if command.operator != "&&":
                locations = _unique(reversed(run))
                run = list(locations)
            previous_operator = command.operator
        return segments

    def _evaluate_command_segments(
        self,
        event: ToolUseEvent,
        parsed: ParsedCommand,
        bundles: List[str],
        locations: Locations,
    ) -> List[List[PolicyDecision]]:
        """Evaluate one command plus its pipes and process substitutions."""
        segments = []
        if parsed.group is not None:
            # A subshell or an assignment: only the commands inside it run
            segments.extend(
                self._evaluate_sequence(event, parsed.group, bundles, locations)
            )
        else:
            input_doc = self._build_input_document(event, parsed, locations)
            self._enrich_input(input_doc, parsed)

            current_command_decisions = []
            for bundle in bundles:
                try:
                    bundle_decisions = self._evaluate_bundle(bundle, input_doc)
                    current_command_decisions.extend(bundle_decisions)
                except Exception as e:
                    logger.error(f"Error evaluating bundle '{bundle}': {e}")
                    current_command_decisions.append(
                        PolicyDecision(
                            action=PolicyAction.ASK,
                            reason=f"Policy evaluation error in bundle '{bundle}': {str(e)}",
                        )
                    )
            # Outside the workspace, or somewhere unknown (cd $(...), cd $X,
            # cd -), even a command without paths reads that directory: cd /etc
            # && ls lists it. Nothing is allowed there; deny still is. cd
            # itself only moves, so cd /workspace from /etc stays allowed.
            if parsed.executable != "cd" and any(
                location.outside for location in locations
            ):
                current_command_decisions = [
                    d
                    for d in current_command_decisions
                    if d.action != PolicyAction.ALLOW
                ]
            # PATH=. git status runs ./git: no decision, like export PATH=.
            if parsed.sensitive_assignment:
                current_command_decisions = [
                    d
                    for d in current_command_decisions
                    if d.action != PolicyAction.ALLOW
                ]
            segments.append(current_command_decisions)

        for sub_command in parsed.pipes + parsed.process_substitutions:
            segments.extend(
                self.evaluate_segments(event, sub_command, bundles, locations)
            )

        return segments

    def evaluate_file_edit_decisions(
        self, event: PostFileEditEvent, bundles: List[str]
    ) -> List[PolicyDecision]:
        """Evaluate decisions rules for a file edit event.

        Lets Rego `decisions` rules react to file edits (by file_path or
        structured_patch) in addition to the `guidances` rules.

        Args:
            event: The file edit event from the client
            bundles: List of policy bundles to evaluate

        Returns:
            List of PolicyDecision objects from all matching rules
        """
        all_decisions = []
        input_doc = self._build_file_edit_input_document(event)

        for bundle in bundles:
            try:
                bundle_decisions = self._evaluate_bundle(bundle, input_doc)
                all_decisions.extend(bundle_decisions)
            except Exception as e:
                logger.error(
                    f"Error evaluating file edit decisions for bundle '{bundle}': {e}"
                )

        return all_decisions

    def evaluate_guidance_activations(
        self, event: PostFileEditEvent, bundles: List[str]
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
                bundle_activations = self._evaluate_guidance_activations_bundle(
                    bundle, input_doc
                )
                all_activations.extend(bundle_activations)
            except Exception as e:
                logger.error(
                    f"Error evaluating guidance activations for bundle '{bundle}': {e}"
                )

        return list(set(all_activations))

    def _normalize_path(
        self,
        path: str,
        workspace_root: Optional[str],
        cwd: Optional[str] = None,
        home: Optional[str] = None,
    ) -> str:
        """Resolve path to workspace-relative form, or return it unchanged for Rego to block.

        Skips non-path arguments (URLs, package names, etc.) — only acts on absolute
        paths, tilde paths, or relative paths containing '..'. Uses cwd as the base for
        relative resolution so paths like ../../file.py from a subdirectory resolve correctly.

        Tilde paths are resolved against the client-supplied `home` only. The server's own
        home directory must never be used to expand `~` — it has no relation to the client
        machine. If `home` is not provided, tilde paths are left unresolved (Rego's
        is_safe_path denies raw "~"-prefixed paths as a safe default).
        """
        if not path or not workspace_root:
            return path
        if path.startswith("~"):
            if not home:
                return path
            if path == "~" or path.startswith("~/"):
                path = home + path[1:]
            else:
                # "~otheruser/..." — no client-side info to resolve this; leave unresolved
                return path
        if not os.path.isabs(path) and ".." not in path.split("/"):
            return path

        try:
            if os.path.isabs(path):
                resolved = os.path.normpath(path)
            elif cwd:
                resolved = os.path.normpath(os.path.join(cwd, path))
            else:
                return path

            root = workspace_root.rstrip("/")
            if resolved == root or resolved.startswith(root + "/"):
                return os.path.relpath(resolved, root)
        except Exception:
            pass

        return path

    @staticmethod
    def _outside_path(path: str, location: Location, workspace_root: Optional[str]):
        """Resolve a relative path used from outside the workspace.

        Returns the workspace-relative form if it lands back inside, and the
        absolute path otherwise, which fails is_safe_path. When the directory
        is unknown the path stays as it is: nothing is allowed from there
        anyway, and cd $X && cat README.md should defer to the user, not be
        denied as a path outside the workspace.
        """
        if not location.cwd:
            return path
        resolved = os.path.normpath(os.path.join(location.cwd, path))
        if workspace_root and _is_within(resolved, workspace_root):
            return os.path.relpath(resolved, workspace_root.rstrip("/"))
        return resolved

    def _resolve_path(self, path: str, location: Location, event: ToolUseEvent) -> str:
        r = self._normalize_path(path, event.workspace_root, location.cwd, event.home)
        if location.outside and r == path and path and not path.startswith(("/", "~")):
            r = self._outside_path(path, location, event.workspace_root)
        return r

    def _build_input_document(
        self,
        event: ToolUseEvent,
        parsed: ParsedCommand,
        locations: Optional[Locations] = None,
    ) -> Dict[str, Any]:
        """Convert ToolUseEvent and ParsedCommand to Rego input.

        Args:
            event: The tool use event
            parsed: Parsed command structure
            locations: Where the command may run, most likely first; defaults
                to the event's cwd

        Returns:
            Dictionary suitable for Rego input
        """
        if locations is None:
            locations = (Location.initial(event),)
        workspace_root = event.workspace_root

        paths = (
            [a for a in parsed.arguments]
            + [path for _, path in parsed.redirects]
            + list(parsed.options.values())
            + [v for values in parsed.repeated_options.values() for v in values]
            + parsed.test_paths
        )
        resolved_paths = {}
        for p in paths:
            candidates = [self._resolve_path(p, loc, event) for loc in locations]
            # A path is only as safe as it is from every possible location
            r = next(
                (c for c in candidates if not _is_workspace_relative(c)),
                candidates[0],
            )
            if r != p:
                resolved_paths[p] = r

        parsed_dict = {
            "executable": parsed.executable,
            "subcommand": parsed.subcommand,
            "arguments": parsed.arguments,
            "flags": parsed.flags,
            "options": parsed.options,
            "repeated_options": parsed.repeated_options,
            "test_paths": parsed.test_paths,
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
                "enabled_bundles": event.enabled_bundles,
                "workspace_root": workspace_root,
            },
            "parsed": parsed_dict,
            "resolved_paths": resolved_paths,
            "expanded_words": {word: True for word in parsed.expanded_words},
        }

        return input_doc

    def _build_file_edit_input_document(
        self, event: PostFileEditEvent
    ) -> Dict[str, Any]:
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
                "enabled_bundles": event.enabled_bundles,
            },
            "file_path": event.file_path,
            "structured_patch": [
                {
                    "old_start": patch.oldStart,
                    "old_lines": patch.oldLines,
                    "new_start": patch.newStart,
                    "new_lines": patch.newLines,
                    "lines": [
                        {"operation": line.operation, "content": line.content}
                        for line in patch.lines
                    ],
                }
                for patch in (event.structured_patch or [])
            ],
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
            package_name = None

            # Try to find package name in arguments first
            if parsed.arguments:
                # Find first non-flag argument (package name)
                package_name = next(
                    (arg for arg in parsed.arguments if not arg.startswith("-")), None
                )

            # If not in arguments, check common flags that take package name as value
            if not package_name and parsed.options:
                # Check --dev, --group, --optional flags which may contain the package name
                for flag in ["--dev", "-d", "--group", "--optional"]:
                    if flag in parsed.options:
                        potential_pkg = parsed.options[flag]
                        # Make sure it's a package name, not another flag
                        if potential_pkg and not potential_pkg.startswith("-"):
                            package_name = potential_pkg
                            break

            if package_name:
                # Strip extras (e.g., "uvicorn[standard]" → "uvicorn")
                base_name = package_name.split("[")[0]
                metadata = self._fetch_pypi_metadata(base_name)
                if metadata:
                    input_doc["pypi_metadata"] = metadata

        elif parsed.executable == "pip" and parsed.subcommand == "install":
            if parsed.arguments:
                # Find first non-flag argument (package name)
                package_name = next(
                    (arg for arg in parsed.arguments if not arg.startswith("-")), None
                )
                if package_name:
                    # Strip extras (e.g., "uvicorn[standard]" → "uvicorn")
                    base_name = package_name.split("[")[0]
                    metadata = self._fetch_pypi_metadata(base_name)
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
                follow_redirects=True,
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
                        upload_date = datetime.fromisoformat(
                            upload_date_str.replace("Z", "+00:00")
                        )
                        if oldest_date is None or upload_date < oldest_date:
                            oldest_date = upload_date
                            first_version = version

            if oldest_date:
                age_days = (datetime.now(oldest_date.tzinfo) - oldest_date).days
                return {
                    "name": package_name,
                    "age_days": age_days,
                    "first_version": first_version,
                    "first_upload_date": oldest_date.isoformat(),
                }

            logger.warning(f"No release data found for package: {package_name}")
            return None

        except httpx.HTTPStatusError as e:
            logger.warning(
                f"PyPI package not found: {package_name} (status {e.response.status_code})"
            )
            return None
        except Exception as e:
            logger.error(f"Error fetching PyPI metadata for {package_name}: {e}")
            return None

    def _evaluate_bundle(
        self, bundle: str, input_doc: Dict[str, Any]
    ) -> List[PolicyDecision]:
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

            # regopy's C++ backend aborts if expressions() is called on
            # an undefined result (e.g. bundle doesn't define decisions).
            # Check the string representation before touching expressions().
            if str(output) == "undefined":
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

    def _evaluate_guidance_activations_bundle(
        self, bundle: str, input_doc: Dict[str, Any]
    ) -> List[str]:
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

            if str(output) == "undefined":
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
            logger.error(
                f"Rego query failed for guidance activations in bundle '{bundle}': {e}"
            )
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
                except (IndexError, Exception):
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

    def _convert_rego_output(
        self, rego_decisions: List[Dict[str, Any]]
    ) -> List[PolicyDecision]:
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
                            logger.warning(
                                f"Unknown action '{action_str}' in decision, skipping"
                            )
                            continue

                        decisions.append(PolicyDecision(action=action, reason=reason))

                    except Exception as e:
                        logger.error(
                            f"Failed to convert decision to PolicyDecision: {e}"
                        )
                        logger.debug(f"Decision data: {decision_json_str}")
                        continue

            except Exception as e:
                logger.error(f"Failed to process decision set: {e}")
                logger.debug(f"Decision set data: {decision_set_item}")
                continue

        return decisions

    def _convert_rego_guidance_activations(
        self, rego_activations: List[Dict[str, Any]]
    ) -> List[str]:
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
                    logger.warning(
                        f"Unexpected activation format: {activation_set_item}"
                    )
                    continue

                for check_name in activation_set_item.keys():
                    if isinstance(check_name, str):
                        check_names.append(check_name)
                    else:
                        logger.warning(
                            f"Unexpected check name type: {type(check_name)}, value: {check_name}"
                        )

            except Exception as e:
                logger.error(f"Failed to process guidance activation: {e}")
                logger.debug(f"Activation data: {activation_set_item}")
                continue

        return check_names

    def evaluate_guidances(
        self, event: ToolUseEvent, parsed: ParsedCommand, bundles: List[str]
    ) -> List[PolicyGuidance]:
        """Evaluate guidances for bash commands.

        Recursively evaluates the main command plus all chained and piped
        commands, same as evaluate() does for decisions.

        Args:
            event: The tool use event from the client
            parsed: Parsed command structure (from bashlex)
            bundles: List of policy bundles to evaluate

        Returns:
            List of PolicyGuidance objects from all matching rules
        """
        all_guidances = []

        if parsed.group is None:
            input_doc = self._build_input_document(event, parsed)
            self._enrich_input(input_doc, parsed)

            for bundle in bundles:
                try:
                    bundle_guidances = self._evaluate_guidances_bundle(
                        bundle, input_doc
                    )
                    all_guidances.extend(bundle_guidances)
                except Exception as e:
                    logger.error(
                        f"Error evaluating guidances for bundle '{bundle}': {e}"
                    )

        # Recursively evaluate every other command the shell runs
        for sub_command in (
            (parsed.group or [])
            + parsed.chained
            + parsed.pipes
            + parsed.process_substitutions
        ):
            all_guidances.extend(self.evaluate_guidances(event, sub_command, bundles))

        return all_guidances

    def evaluate_file_edit_guidances(
        self, event: PostFileEditEvent, bundles: List[str]
    ) -> List[PolicyGuidance]:
        """Evaluate guidances for file edits.

        Args:
            event: The file edit event from the client
            bundles: List of policy bundles to evaluate

        Returns:
            List of PolicyGuidance objects from all matching rules
        """
        all_guidances = []
        input_doc = self._build_file_edit_input_document(event)

        for bundle in bundles:
            try:
                bundle_guidances = self._evaluate_guidances_bundle(bundle, input_doc)
                all_guidances.extend(bundle_guidances)
            except Exception as e:
                logger.error(
                    f"Error evaluating file edit guidances for bundle '{bundle}': {e}"
                )

        return all_guidances

    def _evaluate_guidances_bundle(
        self, bundle: str, input_doc: Dict[str, Any]
    ) -> List[PolicyGuidance]:
        """Evaluate a specific bundle's guidances.

        Args:
            bundle: Bundle name (e.g., "universal", "demo_guidances")
            input_doc: Rego input document

        Returns:
            List of PolicyGuidance objects from this bundle
        """
        query = f"data.{bundle}.guidances"

        try:
            self.interpreter.set_input(input_doc)
            output = self.interpreter.query(query)

            if not output.ok():
                return []

            if str(output) == "undefined":
                return []

            guidances_node = output.expressions(index=0)
            if guidances_node is None:
                return []

            guidances = self._node_to_python(guidances_node)
            logger.debug(f"Guidances from bundle '{bundle}': {guidances}")

            if not guidances:
                return []

            return self._convert_rego_guidances(guidances)

        except Exception as e:
            logger.error(f"Rego query failed for guidances in bundle '{bundle}': {e}")
            raise

    def _convert_rego_guidances(
        self, rego_guidances: List[Dict[str, Any]]
    ) -> List[PolicyGuidance]:
        """Convert Rego guidance results to PolicyGuidance objects.

        Args:
            rego_guidances: List of set elements from Rego guidances[g]
                           Format: [{"json_string": true}, ...]
                           Where json_string is the serialized guidance object

        Returns:
            List of PolicyGuidance objects
        """
        guidances = []

        for guidance_set_item in rego_guidances:
            try:
                if not isinstance(guidance_set_item, dict):
                    logger.warning(f"Unexpected guidance format: {guidance_set_item}")
                    continue

                for guidance_json_str in guidance_set_item.keys():
                    try:
                        guidance_obj = json.loads(guidance_json_str)

                        content = guidance_obj.get("content", "")

                        if not content:
                            logger.warning("Guidance with empty content, skipping")
                            continue

                        guidances.append(PolicyGuidance(content=content))

                    except Exception as e:
                        logger.error(
                            f"Failed to convert guidance to PolicyGuidance: {e}"
                        )
                        logger.debug(f"Guidance data: {guidance_json_str}")
                        continue

            except Exception as e:
                logger.error(f"Failed to process guidance set: {e}")
                logger.debug(f"Guidance set data: {guidance_set_item}")
                continue

        return guidances
