"""
Tests for deduplication of policy results.

Verifies that duplicate reasons from multiple matching rules (e.g., the same
denied command appearing twice in a pipeline) are deduplicated in the output.
"""

from tests.http.conftest import check_policy


def test_piped_duplicate_commands_produce_single_reason(client, base_event):
    """When the same denied command appears twice in a pipe, the reason should appear only once."""
    data = check_policy(client, base_event, "sudo ls | sudo cat", "deny")
    reason = data["hookSpecificOutput"]["permissionDecisionReason"]
    lines = reason.strip().split("\n")
    assert len(lines) == len(set(lines)), f"Duplicate reasons found: {lines}"


def test_chained_duplicate_commands_produce_single_reason(client, base_event):
    """When the same denied command appears twice chained with &&, the reason should appear only once."""
    data = check_policy(client, base_event, "sudo ls && sudo cat", "deny")
    reason = data["hookSpecificOutput"]["permissionDecisionReason"]
    lines = reason.strip().split("\n")
    assert len(lines) == len(set(lines)), f"Duplicate reasons found: {lines}"


def test_distinct_reasons_are_preserved(client, base_event):
    """Different deny reasons from different commands should all be kept."""
    data = check_policy(client, base_event, "sudo ls | rm -rf /tmp", "deny")
    reason = data["hookSpecificOutput"]["permissionDecisionReason"]
    lines = reason.strip().split("\n")
    assert len(lines) >= 2, f"Expected multiple distinct reasons, got: {lines}"
