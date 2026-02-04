"""
HTTP Integration Tests for Network Commands
"""

from tests.http.conftest import check_policy


def test_curl_localhost_allowed(client, base_event):
    check_policy(client, base_event, "curl http://localhost:8080", "allow")


def test_curl_localhost_with_port_allowed(client, base_event):
    check_policy(client, base_event, "curl http://localhost:3000/api", "allow")


def test_curl_127_0_0_1_allowed(client, base_event):
    check_policy(client, base_event, "curl http://127.0.0.1:8000", "allow")


def test_curl_localhost_with_flags_allowed(client, base_event):
    check_policy(client, base_event, "curl -X POST http://localhost:8000/api -H 'Content-Type: application/json'", "allow")


def test_curl_external_url_denied(client, base_event):
    data = check_policy(client, base_event, "curl https://example.com", "deny")
    reason = data["hookSpecificOutput"]["permissionDecisionReason"].lower()
    assert "localhost" in reason or "not allowed" in reason


def test_curl_github_denied(client, base_event):
    check_policy(client, base_event, "curl https://github.com/user/repo", "deny")


def test_curl_api_denied(client, base_event):
    check_policy(client, base_event, "curl https://api.example.com/data", "deny")


def test_curl_127_variant_allowed(client, base_event):
    check_policy(client, base_event, "curl http://127.1.2.3:9000", "allow")


def test_curl_ipv6_localhost_allowed(client, base_event):
    check_policy(client, base_event, "curl http://[::1]:8000", "allow")


def test_curl_localhost_in_query_param_denied(client, base_event):
    check_policy(client, base_event, "curl https://google.com?localhost=true", "deny")


def test_curl_localhost_subdomain_denied(client, base_event):
    check_policy(client, base_event, "curl https://localhost.evil.com", "deny")


def test_curl_127_in_subdomain_denied(client, base_event):
    check_policy(client, base_event, "curl https://127.0.0.1.evil.com", "deny")


def test_curl_localhost_in_path_denied(client, base_event):
    check_policy(client, base_event, "curl https://evil.com/localhost/api", "deny")


def test_curl_remote_ip_denied(client, base_event):
    check_policy(client, base_event, "curl http://192.168.1.1", "deny")


def test_curl_ip_containing_127_denied(client, base_event):
    check_policy(client, base_event, "curl http://192.168.127.100", "deny")
