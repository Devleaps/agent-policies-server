"""
HTTP Integration Tests for uv tool install
"""

from tests.http.conftest import check_policy


def test_uv_tool_install_allowed(client, base_event):
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv tool install some-package", "allow")


def test_uv_tool_install_local_allowed(client, base_event):
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv tool install .", "allow")
