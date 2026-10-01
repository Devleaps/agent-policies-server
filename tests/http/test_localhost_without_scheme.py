"""
HTTP Integration Tests for curl to localhost URLs written without a scheme.
"""

import pytest

from tests.http.conftest import check_policy


@pytest.mark.parametrize(
    "command",
    [
        "curl localhost:8123/v1/health",
        "curl -s localhost",
        "curl 127.0.0.1:8080/api",
        "curl '[::1]:8080/'",
        "curl -s -X PUT localhost:8123/v1/log/2026-09-08 -H 'Content-Type: application/json' -d '{}'",
        "curl -s -X PUT 'localhost:8123/v1/log/2026-09-08' -d '{}'",
        # :// in the query is not a scheme
        "curl 'localhost?next=http://example.com'",
        "curl 'localhost:8123/cb?redirect=https://example.com/x'",
    ],
)
def test_curl_localhost_without_scheme_allowed(client, base_event, command):
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "curl localhost.evil.com/x",
        "curl 127.0.0.1.evil.com:80/x",
        "curl evil.com/localhost",
        "curl evil.com/?u=http://localhost",
        "curl example.com",
    ],
)
def test_curl_lookalike_without_scheme_denied(client, base_event, command):
    check_policy(client, base_event, command, "deny")
