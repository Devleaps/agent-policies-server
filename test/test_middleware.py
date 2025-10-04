"""
Test script to validate middleware functionality.

This verifies that:
1. Timeout middleware strips 'timeout {digit}' prefix
2. UV run middleware strips 'uv run' prefix
3. Time middleware strips 'time' prefix
4. All middleware can be imported and registered
"""

from devleaps.policies.server.common.models import ToolUseEvent
from devleaps.policies.server.common.enums import SourceClient


def test_timeout_middleware():
    """Test that timeout middleware strips timeout prefix."""
    from src.timeout.middleware import strip_timeout_prefix_middleware

    # Test basic timeout command
    event = ToolUseEvent(
        session_id="test",
        tool_name="Bash",
        source_client=SourceClient.CLAUDE_CODE,
        tool_is_bash=True,
        command="timeout 30 pytest",
        parameters={"command": "timeout 30 pytest"}
    )

    result = list(strip_timeout_prefix_middleware(event))
    assert len(result) == 1
    assert result[0].command == "pytest"
    print("✓ Basic timeout prefix stripped correctly")

    # Test timeout with flags
    event2 = ToolUseEvent(
        tool_name="Bash",
        command="timeout -s KILL 60 python script.py",
        parameters={"command": "timeout -s KILL 60 python script.py"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result2 = list(strip_timeout_prefix_middleware(event2))
    assert len(result2) == 1
    assert result2[0].command == "python script.py"
    print("✓ Timeout with flags stripped correctly")

    # Test timeout with time units
    event3 = ToolUseEvent(
        tool_name="Bash",
        command="timeout 5m npm test",
        parameters={"command": "timeout 5m npm test"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result3 = list(strip_timeout_prefix_middleware(event3))
    assert len(result3) == 1
    assert result3[0].command == "npm test"
    print("✓ Timeout with time units stripped correctly")

    # Test command without timeout
    event4 = ToolUseEvent(
        tool_name="Bash",
        command="pytest",
        parameters={"command": "pytest"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result4 = list(strip_timeout_prefix_middleware(event4))
    assert len(result4) == 1
    assert result4[0].command == "pytest"
    print("✓ Commands without timeout pass through unchanged")


def test_uv_run_middleware():
    """Test that uv run middleware strips uv run prefix."""
    from src.uv.middleware import strip_uv_run_prefix_middleware

    # Test basic uv run command
    event = ToolUseEvent(
        tool_name="Bash",
        command="uv run pytest",
        parameters={"command": "uv run pytest"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result = list(strip_uv_run_prefix_middleware(event))
    assert len(result) == 1
    assert result[0].command == "pytest"
    print("✓ Basic uv run prefix stripped correctly")

    # Test uv run with arguments
    event2 = ToolUseEvent(
        tool_name="Bash",
        command="uv run python -m pytest tests/",
        parameters={"command": "uv run python -m pytest tests/"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result2 = list(strip_uv_run_prefix_middleware(event2))
    assert len(result2) == 1
    assert result2[0].command == "python -m pytest tests/"
    print("✓ uv run with arguments stripped correctly")

    # Test command without uv run
    event3 = ToolUseEvent(
        tool_name="Bash",
        command="pytest",
        parameters={"command": "pytest"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result3 = list(strip_uv_run_prefix_middleware(event3))
    assert len(result3) == 1
    assert result3[0].command == "pytest"
    print("✓ Commands without uv run pass through unchanged")


def test_time_middleware():
    """Test that time middleware strips time prefix."""
    from src.time.middleware import strip_time_prefix_middleware

    # Test basic time command
    event = ToolUseEvent(
        tool_name="Bash",
        command="time pytest",
        parameters={"command": "time pytest"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result = list(strip_time_prefix_middleware(event))
    assert len(result) == 1
    assert result[0].command == "pytest"
    print("✓ Basic time prefix stripped correctly")

    # Test time with flags
    event2 = ToolUseEvent(
        tool_name="Bash",
        command="time -p terraform plan",
        parameters={"command": "time -p terraform plan"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result2 = list(strip_time_prefix_middleware(event2))
    assert len(result2) == 1
    assert result2[0].command == "terraform plan"
    print("✓ Time with flags stripped correctly")

    # Test command without time
    event3 = ToolUseEvent(
        tool_name="Bash",
        command="pytest",
        parameters={"command": "pytest"},
        session_id="test",
        source_client=SourceClient.CLAUDE_CODE, tool_is_bash=True
    )

    result3 = list(strip_time_prefix_middleware(event3))
    assert len(result3) == 1
    assert result3[0].command == "pytest"
    print("✓ Commands without time pass through unchanged")


def test_all_middleware_registered():
    """Test that all middleware can be imported and are registered in main."""
    import src.main

    # Import all middleware modules
    from src import bash, time, timeout, uv

    # Check they all have all_middleware
    assert hasattr(bash, 'all_middleware')
    assert hasattr(time, 'all_middleware')
    assert hasattr(timeout, 'all_middleware')
    assert hasattr(uv, 'all_middleware')

    print("✓ All middleware modules have all_middleware attribute")

    # Check counts
    assert len(bash.all_middleware) >= 1
    assert len(time.all_middleware) >= 1
    assert len(timeout.all_middleware) >= 1
    assert len(uv.all_middleware) >= 1

    print(f"✓ bash: {len(bash.all_middleware)} middleware")
    print(f"✓ time: {len(time.all_middleware)} middleware")
    print(f"✓ timeout: {len(timeout.all_middleware)} middleware")
    print(f"✓ uv: {len(uv.all_middleware)} middleware")


if __name__ == "__main__":
    print("Testing middleware functionality...\n")

    try:
        test_timeout_middleware()
        print()

        test_uv_run_middleware()
        print()

        test_time_middleware()
        print()

        test_all_middleware_registered()
        print()

        print("=" * 50)
        print("All middleware tests passed! ✓")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
