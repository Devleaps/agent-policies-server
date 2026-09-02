"""
HTTP Integration Tests for OPA bundle composition and serving
"""

import concurrent.futures
import subprocess

import pytest

from src.server.bundles import KNOWN_BUNDLES


@pytest.fixture
def scratch_cache(tmp_path, monkeypatch):
    """Point the bundles router's compose cache at a scratch dir."""
    from src.server import bundles as bundles_module

    monkeypatch.setattr(bundles_module, "COMPOSED_DIR", tmp_path)
    return tmp_path


def test_list_known_bundles_returns_the_allowlist(client):
    response = client.get("/bundles")
    assert response.status_code == 200
    assert response.json() == {"bundles": sorted(KNOWN_BUNDLES)}


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
    # decisions is a `contains` (modern set) rule, so opa eval's
    # --format=values prints it as a plain JSON array of decision objects.
    assert '"action": "allow"' in result.stdout


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


def test_build_failure_response_does_not_leak_raw_stderr(client, scratch_cache, monkeypatch):
    """A build failure must not put opa's raw stderr (absolute server paths,
    Rego internals) into the HTTP response body - only into server logs."""
    from src.server import bundles as bundles_module

    class FakeResult:
        returncode = 1
        stderr = "/very/secret/server/path/policies/universal/foo.rego:12: rego_parse_error"

    monkeypatch.setattr(bundles_module.subprocess, "run", lambda *a, **k: FakeResult())

    response = client.get("/bundles/composed", params={"names": "universal"})
    assert response.status_code == 500
    assert "/very/secret/server/path" not in response.text
    assert "rego_parse_error" not in response.text


def test_build_failure_leaves_no_temp_file_behind(client, scratch_cache, monkeypatch):
    """A failed build must not leave its .tar.gz.tmp staging file lying
    around in the cache dir."""
    from src.server import bundles as bundles_module

    class FakeResult:
        returncode = 1
        stderr = "synthetic failure"

    monkeypatch.setattr(bundles_module.subprocess, "run", lambda *a, **k: FakeResult())

    response = client.get("/bundles/composed", params={"names": "universal"})
    assert response.status_code == 500
    assert list(scratch_cache.iterdir()) == []


@pytest.fixture
def scratch_policies(tmp_path, monkeypatch):
    """Point POLICIES_DIR/HELPERS_DIR at a scratch policy tree this test
    fully controls, so a cache-invalidation test can mutate .rego source
    without touching the real policies/ directory."""
    from src.server import bundles as bundles_module

    policies_dir = tmp_path / "policies"
    helpers_dir = policies_dir / "helpers"
    universal_dir = policies_dir / "universal"
    helpers_dir.mkdir(parents=True)
    universal_dir.mkdir(parents=True)
    (helpers_dir / ".manifest").write_text('{"roots": ["helpers"]}')
    (helpers_dir / "helpers.rego").write_text("package helpers\n")
    (universal_dir / ".manifest").write_text('{"roots": ["universal"]}')
    (universal_dir / "policy.rego").write_text(
        'package universal\n\ndecisions[decision] if {\n\tdecision := {"action": "allow"}\n}\n'
    )

    monkeypatch.setattr(bundles_module, "POLICIES_DIR", policies_dir)
    monkeypatch.setattr(bundles_module, "HELPERS_DIR", helpers_dir)
    monkeypatch.setattr(bundles_module, "KNOWN_BUNDLES", {"universal"})
    return universal_dir


def test_editing_policy_source_invalidates_the_cache(client, scratch_cache, scratch_policies):
    """The exact bug found and worked around manually this session: a cache
    keyed only by bundle names keeps serving a stale artifact forever after
    a .rego file changes. Confirm the new content-hashed key picks up the
    edit and the served bundle actually reflects it."""
    first = client.get("/bundles/composed", params={"names": "universal"})
    assert first.status_code == 200

    (scratch_policies / "policy.rego").write_text(
        'package universal\n\ndecisions[decision] if {\n\tdecision := {"action": "deny", "reason": "changed"}\n}\n'
    )

    second = client.get("/bundles/composed", params={"names": "universal"})
    assert second.status_code == 200
    assert second.content != first.content, "edited policy source must produce a different bundle"

    # Both artifacts must still be individually valid/cached - two distinct
    # entries, not an overwrite of the first.
    cached_files = list(scratch_cache.glob("*.tar.gz"))
    assert len(cached_files) == 2


def test_concurrent_requests_for_an_uncached_key_both_get_a_complete_bundle(
    client, scratch_cache, scratch_policies
):
    """Two simultaneous first-requests for the same uncached bundle set must
    each observe either nothing or a complete tarball - never a partially
    written one - proving the atomic-publish fix actually closes the race."""

    def fetch():
        return client.get("/bundles/composed", params={"names": "universal"})

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        first, second = [f.result() for f in [pool.submit(fetch), pool.submit(fetch)]]

    assert first.status_code == 200
    assert second.status_code == 200
    assert len(first.content) > 0
    assert len(second.content) > 0
    assert first.content == second.content

    # No leftover .tmp staging files, regardless of which request "won" the
    # race to build - and exactly one final cached artifact, not two.
    remaining = list(scratch_cache.iterdir())
    assert all(not p.name.endswith(".tmp") for p in remaining)
    assert len([p for p in remaining if p.name.endswith(".tar.gz")]) == 1
