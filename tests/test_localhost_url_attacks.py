"""Test that localhost URL detection is defensive against attack vectors."""
from src.core.rego_integration import RegoEvaluator
from src.core.command_parser import BashCommandParser
from src.server.common.models import ToolUseEvent


def test_localhost_in_query_param_should_deny():
    """URLs with localhost in query params should be denied."""
    evaluator = RegoEvaluator()

    cmd = "curl https://google.com?localhost=true"
    event = ToolUseEvent(
        session_id="test",
        source_client="test",
        tool_name="Bash",
        tool_is_bash=True,
        command=cmd,
        parameters={"command": cmd}
    )
    parsed = BashCommandParser.parse(cmd)
    decisions = evaluator.evaluate(event, parsed, ["universal"])

    # Should be denied - localhost is only in query param
    assert len(decisions) == 1
    assert decisions[0].action.value == "deny"


def test_localhost_subdomain_should_deny():
    """URLs with localhost as subdomain should be denied."""
    evaluator = RegoEvaluator()

    cmd = "curl https://localhost.evil.com"
    event = ToolUseEvent(
        session_id="test",
        source_client="test",
        tool_name="Bash",
        tool_is_bash=True,
        command=cmd,
        parameters={"command": cmd}
    )
    parsed = BashCommandParser.parse(cmd)
    decisions = evaluator.evaluate(event, parsed, ["universal"])

    # Should be denied - localhost is subdomain, not the actual host
    assert len(decisions) == 1
    assert decisions[0].action.value == "deny"


def test_127_in_subdomain_should_deny():
    """URLs with 127.x.x.x as subdomain should be denied."""
    evaluator = RegoEvaluator()

    cmd = "curl https://127.0.0.1.evil.com"
    event = ToolUseEvent(
        session_id="test",
        source_client="test",
        tool_name="Bash",
        tool_is_bash=True,
        command=cmd,
        parameters={"command": cmd}
    )
    parsed = BashCommandParser.parse(cmd)
    decisions = evaluator.evaluate(event, parsed, ["universal"])

    # Should be denied - 127.0.0.1 is subdomain, not the actual host
    assert len(decisions) == 1
    assert decisions[0].action.value == "deny"


def test_localhost_in_path_should_deny():
    """URLs with localhost in path should be denied."""
    evaluator = RegoEvaluator()

    cmd = "curl https://evil.com/localhost/api"
    event = ToolUseEvent(
        session_id="test",
        source_client="test",
        tool_name="Bash",
        tool_is_bash=True,
        command=cmd,
        parameters={"command": cmd}
    )
    parsed = BashCommandParser.parse(cmd)
    decisions = evaluator.evaluate(event, parsed, ["universal"])

    # Should be denied - localhost is only in path
    assert len(decisions) == 1
    assert decisions[0].action.value == "deny"


def test_actual_localhost_should_allow():
    """Actual localhost URLs should be allowed."""
    evaluator = RegoEvaluator()

    for url in [
        "http://localhost:8080",
        "https://localhost",
        "http://127.0.0.1:3000",
        "http://127.1.2.3",
        "http://[::1]:8000",
    ]:
        cmd = f"curl {url}"
        event = ToolUseEvent(
            session_id="test",
            source_client="test",
            tool_name="Bash",
            tool_is_bash=True,
            command=cmd,
            parameters={"command": cmd}
        )
        parsed = BashCommandParser.parse(cmd)
        decisions = evaluator.evaluate(event, parsed, ["universal"])

        # Should be allowed
        assert len(decisions) == 1, f"Expected 1 decision for {url}, got {len(decisions)}"
        assert decisions[0].action.value == "allow", f"Expected allow for {url}, got {decisions[0].action.value}"
