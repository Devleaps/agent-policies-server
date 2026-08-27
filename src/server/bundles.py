"""HTTP serving of pre-built OPA bundles.

Bundles are built at image-build time by scripts/build_bundles.sh into
bundles/*.tar.gz (see the Dockerfile's "bundles" build stage). This module
only serves the resulting files; it does not build or evaluate anything.

Route shape matches OPA's bundle downloader convention (see
`opa run -s --set bundles.<name>.resource=/bundles/<name>.tar.gz`). Bundles
are small, so every request just serves the full file rather than handling
conditional (If-None-Match) requests.
"""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bundles")

BUNDLES_DIR = Path("bundles")

# Names must match scripts/build_bundles.sh's BUNDLES array exactly - this is
# an explicit allowlist, not a directory listing, so an unexpected file
# dropped into bundles/ can never be served.
KNOWN_BUNDLES = {"universal", "python_uv", "python_pip", "demo_bundles", "demo_flags"}


@router.get("/{name}.tar.gz")
async def get_bundle(name: str) -> FileResponse:
    if name not in KNOWN_BUNDLES:
        raise HTTPException(status_code=404, detail=f"Unknown bundle: {name}")

    bundle_path = BUNDLES_DIR / f"{name}.tar.gz"
    if not bundle_path.is_file():
        logger.error(f"Bundle file missing on disk: {bundle_path}")
        raise HTTPException(status_code=404, detail=f"Bundle not built: {name}")

    return FileResponse(
        bundle_path,
        media_type="application/gzip",
        filename=f"{name}.tar.gz",
    )
