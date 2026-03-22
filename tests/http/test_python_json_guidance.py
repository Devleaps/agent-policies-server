"""
HTTP Integration Tests for Python JSON Guidance

Tests that the policy server suggests using jq instead of python -c for JSON
processing in bash commands.
"""

from tests.http.conftest import check_policy


def test_python_c_import_json_returns_guidance(client, base_event):
    """python -c with import json should return guidance suggesting jq."""
    data = check_policy(
        client,
        base_event,
        'python -c "import json; print(json.dumps({}))"',
        None,
    )
    reason = (
        data.get("hookSpecificOutput", {}).get("permissionDecisionReason") or ""
    )
    assert "jq" in reason


def test_python3_c_import_json_returns_guidance(client, base_event):
    """python3 -c with import json should return guidance suggesting jq."""
    data = check_policy(
        client,
        base_event,
        'python3 -c "import json; print(json.loads(s))"',
        None,
    )
    reason = (
        data.get("hookSpecificOutput", {}).get("permissionDecisionReason") or ""
    )
    assert "jq" in reason


def test_python_c_no_json_no_guidance(client, base_event):
    """python -c without json should not return guidance."""
    data = check_policy(
        client,
        base_event,
        "python -c \"print('hello')\"",
        None,
    )
    reason = (
        data.get("hookSpecificOutput", {}).get("permissionDecisionReason") or ""
    )
    assert "jq" not in reason


def test_python_script_no_guidance(client, base_event):
    """python script.py (not -c) should not return guidance."""
    data = check_policy(
        client,
        base_event,
        "python script.py",
        None,
    )
    reason = (
        data.get("hookSpecificOutput", {}).get("permissionDecisionReason") or ""
    )
    assert "jq" not in reason
