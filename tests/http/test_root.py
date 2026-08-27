"""
HTTP Integration Tests for the root endpoint
"""


def test_root_returns_expected_shape(client):
    """GET / returns name, version, git_sha, editors, and endpoints"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Agent Policy Server by DevLeaps"
    assert "version" in data
    assert "git_sha" in data
    assert data["editors"] == ["claude-code"]
    assert "claude-code" in data["endpoints"]
    assert "bundles" in data["endpoints"]


def test_root_reflects_build_version_and_git_sha(monkeypatch):
    """version/git_sha in the response reflect the VERSION/GIT_SHA env vars
    present at process startup"""
    monkeypatch.setenv("VERSION", "v9.9.9")
    monkeypatch.setenv("GIT_SHA", "deadbeef")

    # server.py reads these env vars at import time, so the module must be
    # reloaded after patching the environment for this test to be meaningful.
    import importlib

    from src.server import server as server_module

    importlib.reload(server_module)
    try:
        from fastapi.testclient import TestClient

        response = TestClient(server_module.app).get("/")
        data = response.json()
        assert data["version"] == "v9.9.9"
        assert data["git_sha"] == "deadbeef"
        assert server_module.app.version == "v9.9.9"
    finally:
        importlib.reload(server_module)
