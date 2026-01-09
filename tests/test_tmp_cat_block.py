"""Tests for blocking cat writes to /tmp/."""

import pytest
from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient
from src.universal.tmp_cat_block import tmp_cat_block_rule


@pytest.fixture
def create_tool_use_event():
    """Factory fixture to create ToolUseEvent."""
    def _create(command: str, tool_is_bash: bool = True) -> ToolUseEvent:
        return ToolUseEvent(
            session_id="test-session",
            source_client=SourceClient.CLAUDE_CODE,
            tool_name="Bash" if tool_is_bash else "Read",
            tool_is_bash=tool_is_bash,
            command=command,
            parameters={"command": command}
        )
    return _create


def test_cat_heredoc_to_tmp_denied(create_tool_use_event):
    """cat with heredoc writing to /tmp/ should be denied."""
    event = create_tool_use_event("cat > /tmp/file.txt << EOF")
    results = list(tmp_cat_block_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_cat_append_to_tmp_denied(create_tool_use_event):
    """cat appending to /tmp/ should be denied."""
    event = create_tool_use_event("cat >> /tmp/output.log << EOF")
    results = list(tmp_cat_block_rule(event))
    assert len(results) == 1
    assert results[0].action == "deny"


def test_cat_to_workspace_file_match_no_policies(create_tool_use_event):
    """cat writing to workspace file should match no policies."""
    event = create_tool_use_event("cat > output.txt << EOF")
    results = list(tmp_cat_block_rule(event))
    assert len(results) == 0


def test_cat_reading_from_tmp_match_no_policies(create_tool_use_event):
    """cat reading from /tmp/ should match no policies."""
    event = create_tool_use_event("cat /tmp/file.txt")
    results = list(tmp_cat_block_rule(event))
    assert len(results) == 0
