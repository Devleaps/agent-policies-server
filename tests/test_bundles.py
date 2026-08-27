"""
HTTP Integration Tests for OPA bundle composition and serving
"""

import subprocess

import pytest


@pytest.fixture
def scratch_cache(tmp_path, monkeypatch):
    """Point the bundles router's compose cache at a scratch dir."""
    from src.server import bundles as bundles_module

    monkeypatch.setattr(bundles_module, "COMPOSED_DIR", tmp_path)
    return tmp_path


def test_missing_names_param_is_rejected(client):
    response = client.get("/bundles/composed")
    assert response.status_code == 422


def test_empty_names_is_rejected(client, scratch_cache):
    response = client.get("/bundles/composed", params={"names": "  ,  "})
    assert response.status_code == 400


def test_unknown_bundle_name_is_rejected(client, scratch_cache):
    response = client.get("/bundles/composed", params={"names": "not-a-real-bundle"})
    assert response.status_code == 404


def test_composes_single_bundle(client, scratch_cache):
    response = client.get("/bundles/composed", params={"names": "universal"})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/gzip"
    assert len(response.content) > 0


def test_composes_multiple_bundles_without_root_conflict(client, scratch_cache):
    """This is the exact scenario that broke when universal and python_uv
    each shipped their own copy of helpers: opa run rejected them together
    with 'overlapping roots'. Composing helpers + both into ONE bundle
    avoids that entirely."""
    response = client.get("/bundles/composed", params={"names": "universal,python_uv"})
    assert response.status_code == 200
    assert len(response.content) > 0


def test_composed_bundle_is_a_valid_opa_bundle(client, scratch_cache, tmp_path):
    """Round-trip through the real opa binary: build via the endpoint, then
    load and query the result, proving it's not just bytes but an actually
    loadable, evaluable bundle with helpers resolved."""
    response = client.get("/bundles/composed", params={"names": "universal"})
    assert response.status_code == 200

    bundle_path = tmp_path / "out.tar.gz"
    bundle_path.write_bytes(response.content)

    result = subprocess.run(
        [
            "opa",
            "eval",
            "-b",
            str(bundle_path),
            "--stdin-input",
            "--format=values",
            "data.universal.decisions",
        ],
        input='{"parsed":{"executable":"cat","arguments":["a.txt"],"options":{}}}',
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    # opa eval's --format=values prints the decision set's JSON-string key
    # backslash-escaped, e.g. "{\"action\":\"allow\"}": true
    assert '\\"action\\":\\"allow\\"' in result.stdout


def test_bundle_set_order_does_not_affect_cache_key(client, scratch_cache):
    """universal,python_uv and python_uv,universal must hit the same cached
    artifact, not build two redundant copies."""
    first = client.get("/bundles/composed", params={"names": "universal,python_uv"})
    second = client.get("/bundles/composed", params={"names": "python_uv,universal"})
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.content == second.content

    cached_files = list(scratch_cache.glob("*.tar.gz"))
    assert len(cached_files) == 1


def test_repeat_request_is_served_from_cache(client, scratch_cache, monkeypatch):
    """Second request for the same bundle set must not invoke opa build
    again."""
    from src.server import bundles as bundles_module

    first = client.get("/bundles/composed", params={"names": "universal"})
    assert first.status_code == 200

    original_run = bundles_module.subprocess.run

    def fail_if_called(*args, **kwargs):
        raise AssertionError("opa build should not run again for a cached bundle set")

    monkeypatch.setattr(bundles_module.subprocess, "run", fail_if_called)
    try:
        second = client.get("/bundles/composed", params={"names": "universal"})
    finally:
        monkeypatch.setattr(bundles_module.subprocess, "run", original_run)

    assert second.status_code == 200
    assert second.content == first.content


def test_build_failure_returns_500_and_does_not_cache_broken_output(
    client, scratch_cache, monkeypatch
):
    from src.server import bundles as bundles_module

    class FakeResult:
        returncode = 1
        stderr = "synthetic failure"

    monkeypatch.setattr(bundles_module.subprocess, "run", lambda *a, **k: FakeResult())

    response = client.get("/bundles/composed", params={"names": "universal"})
    assert response.status_code == 500
    assert list(scratch_cache.glob("*.tar.gz")) == []
