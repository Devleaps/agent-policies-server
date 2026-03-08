"""
HTTP Integration Tests for OPA Commands
"""

from tests.http.conftest import check_policy


def test_opa_test_allowed(client, base_event):
    check_policy(client, base_event, "opa test .", "allow")


def test_opa_eval_defers_to_user(client, base_event):
    check_policy(client, base_event, "opa eval 'data.example.allow'", None)


def test_opa_run_defers_to_user(client, base_event):
    check_policy(client, base_event, "opa run server", None)
