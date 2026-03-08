"""HTTP integration tests for the demo_bundles bundle_selection policy."""

from tests.http.conftest import check_policy


def test_denies_any_command_without_python_bundle(client, base_event):
    """demo_bundles active but no python bundle -> deny any command."""
    base_event["bundles"] = ["universal", "demo_bundles"]
    check_policy(client, base_event, "ls", "deny")


def test_allows_with_python_uv_bundle(client, base_event):
    """demo_bundles + python_uv -> no deny from bundle_selection."""
    base_event["bundles"] = ["universal", "demo_bundles", "python_uv"]
    result = check_policy(client, base_event, "ls", "allow")
    assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
