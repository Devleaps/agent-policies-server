"""
HTTP Integration Tests for OPA bundle serving
"""

from pathlib import Path

import pytest


@pytest.fixture
def bundle_file(tmp_path, monkeypatch):
    """Point the bundles router at a scratch dir with one fake bundle file."""
    from src.server import bundles as bundles_module

    bundle_path = tmp_path / "universal.tar.gz"
    bundle_path.write_bytes(b"fake-bundle-contents")
    monkeypatch.setattr(bundles_module, "BUNDLES_DIR", tmp_path)
    return bundle_path


def test_known_bundle_is_served(client, bundle_file):
    response = client.get("/bundles/universal.tar.gz")
    assert response.status_code == 200
    assert response.content == b"fake-bundle-contents"
    assert response.headers["content-type"] == "application/gzip"


def test_unknown_bundle_name_is_rejected(client):
    """Name must be in the explicit allowlist, not just any file on disk."""
    response = client.get("/bundles/not-a-real-bundle.tar.gz")
    assert response.status_code == 404


def test_known_bundle_missing_from_disk_is_404(client, tmp_path, monkeypatch):
    from src.server import bundles as bundles_module

    monkeypatch.setattr(bundles_module, "BUNDLES_DIR", tmp_path)
    response = client.get("/bundles/universal.tar.gz")
    assert response.status_code == 404


def test_all_known_bundles_are_actually_built():
    """Guards against KNOWN_BUNDLES drifting from build_bundles.sh's list."""
    from src.server.bundles import KNOWN_BUNDLES

    script = Path("scripts/build_bundles.sh").read_text()
    for name in KNOWN_BUNDLES:
        assert name in script, f"{name} is in KNOWN_BUNDLES but not build_bundles.sh"
