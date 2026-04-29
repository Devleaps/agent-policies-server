"""
HTTP Integration Tests for WebFetch domain allowlisting
"""

import pytest
from fastapi.testclient import TestClient
from src.server.server import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def webfetch_event():
    """Factory for WebFetch PreToolUse events"""

    def _create(url):
        return {
            "event": {
                "session_id": "test-session",
                "transcript_path": "/tmp/transcript.jsonl",
                "cwd": "/workspace",
                "hook_event_name": "PreToolUse",
                "tool_name": "WebFetch",
                "tool_input": {"url": url},
                "tool_use_id": "toolu_test",
            },
            "bundles": ["universal"],
        }

    return _create


def check_webfetch(client, webfetch_event, url, expected_decision):
    event = webfetch_event(url)
    response = client.post("/policy/claude-code/PreToolUse", json=event)
    assert response.status_code == 200
    data = response.json()
    if expected_decision is None:
        assert "permissionDecision" not in data.get("hookSpecificOutput", {})
    else:
        assert data["hookSpecificOutput"]["permissionDecision"] == expected_decision
    return data


def test_webfetch_code_claude_allowed(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://code.claude.com/docs/setup", "allow")


def test_webfetch_docs_github_allowed(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://docs.github.com/en/actions", "allow")


def test_webfetch_developers_googleblog_allowed(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://developers.googleblog.com/some-post", "allow")


def test_webfetch_geminicli_allowed(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://geminicli.com/docs", "allow")


def test_webfetch_google_gemini_github_allowed(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://google-gemini.github.io/docs", "allow")


def test_webfetch_developers_openai_allowed(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://developers.openai.com/docs/api", "allow")


def test_webfetch_unknown_domain_no_decision(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://evil.com/malware", None)


def test_webfetch_random_domain_no_decision(client, webfetch_event):
    check_webfetch(client, webfetch_event, "https://example.com/page", None)
