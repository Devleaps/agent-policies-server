"""
Mappers to convert Gemini hook inputs/outputs to/from generic models.
"""

from typing import List, Union

from ..enums import SourceClient
from ..mapper_utils import find_highest_priority_decision, separate_results
from ..models import PolicyAction, PolicyDecision, PolicyGuidance, PostToolUseEvent, ToolUseEvent
from .api.after_tool import AfterToolInput, AfterToolHookSpecificOutput, AfterToolOutput
from .api.before_tool import BeforeToolInput, BeforeToolOutput
from .api.common import GeminiDecision, GeminiRequestWrapper

# Gemini CLI tool names that represent shell/bash execution
GEMINI_BASH_TOOL_NAMES = {
    "run_shell_command",
}

# ============================================================================
# INPUT MAPPERS: Gemini → Generic
# ============================================================================


def map_before_tool_input(
    wrapper: GeminiRequestWrapper, input_data: BeforeToolInput
) -> ToolUseEvent:
    """Map Gemini BeforeTool to ToolUseEvent."""
    tool_is_bash = input_data.tool_name in GEMINI_BASH_TOOL_NAMES

    command = None
    parameters = None

    if tool_is_bash:
        tool_input = input_data.tool_input or {}
        command = tool_input.get("command")
    else:
        parameters = input_data.tool_input if input_data.tool_input else None

    return ToolUseEvent(
        session_id=input_data.session_id,
        tool_name=input_data.tool_name,
        source_client=SourceClient.GEMINI,
        tool_is_bash=tool_is_bash,
        tool_is_mcp=False,
        command=command,
        parameters=parameters,
        workspace_roots=None,
        source_event=input_data,
        enabled_bundles=wrapper.bundles,
    )


def map_after_tool_input(
    wrapper: GeminiRequestWrapper, input_data: AfterToolInput
) -> PostToolUseEvent:
    """Map Gemini AfterTool to PostToolUseEvent."""
    tool_is_bash = input_data.tool_name in GEMINI_BASH_TOOL_NAMES

    command = None
    parameters = None

    if tool_is_bash:
        tool_input = input_data.tool_input or {}
        command = tool_input.get("command")
    else:
        parameters = input_data.tool_input if input_data.tool_input else None

    return PostToolUseEvent(
        session_id=input_data.session_id,
        tool_name=input_data.tool_name,
        source_client=SourceClient.GEMINI,
        tool_is_bash=tool_is_bash,
        tool_is_mcp=False,
        command=command,
        parameters=parameters,
        workspace_roots=None,
        source_event=input_data,
        enabled_bundles=wrapper.bundles,
    )


# ============================================================================
# OUTPUT MAPPERS: Generic → Gemini
# ============================================================================

_POLICY_TO_GEMINI_DECISION = {
    PolicyAction.ALLOW: GeminiDecision.ALLOW,
    PolicyAction.DENY: GeminiDecision.DENY,
    # ASK maps to None — Gemini has no native tri-state; omit decision entirely
    PolicyAction.ASK: None,
}


def map_to_before_tool_output(
    results: List[Union[PolicyDecision, PolicyGuidance]],
    default_output: BeforeToolOutput,
) -> BeforeToolOutput:
    """Map generic results to BeforeToolOutput."""
    decisions, guidances = separate_results(results)

    if not decisions and not guidances:
        return default_output

    final_decision = find_highest_priority_decision(decisions) if decisions else None

    gemini_decision = None
    if final_decision:
        gemini_decision = _POLICY_TO_GEMINI_DECISION.get(final_decision.action)

    deny_reasons = (
        [d.reason for d in decisions if d.action == final_decision.action and d.reason]
        if final_decision
        else []
    )
    guidance_texts = [g.content for g in guidances]

    reason = "\n".join(deny_reasons) if deny_reasons else None
    system_message_parts = deny_reasons + guidance_texts
    system_message = "\n".join(system_message_parts) if system_message_parts else None

    return BeforeToolOutput(
        decision=gemini_decision,
        reason=reason,
        systemMessage=system_message,
    )


def map_to_after_tool_output(
    results: List[Union[PolicyDecision, PolicyGuidance]],
    default_output: AfterToolOutput,
) -> AfterToolOutput:
    """Map generic results to AfterToolOutput."""
    decisions, guidances = separate_results(results)

    if not decisions and not guidances:
        return default_output

    final_decision = find_highest_priority_decision(decisions) if decisions else None

    gemini_decision = None
    if final_decision:
        gemini_decision = _POLICY_TO_GEMINI_DECISION.get(final_decision.action)

    deny_reasons = (
        [d.reason for d in decisions if d.action == final_decision.action and d.reason]
        if final_decision
        else []
    )
    guidance_texts = [g.content for g in guidances]

    reason = "\n".join(deny_reasons) if deny_reasons else None
    additional_context = "\n".join(guidance_texts) if guidance_texts else None

    hook_specific = (
        AfterToolHookSpecificOutput(additionalContext=additional_context)
        if additional_context
        else None
    )

    return AfterToolOutput(
        decision=gemini_decision,
        reason=reason,
        hookSpecificOutput=hook_specific,
    )
