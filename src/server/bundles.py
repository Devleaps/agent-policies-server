"""HTTP serving of OPA bundles, composed on demand.

`helpers` is a shared Rego dependency imported by several bundles
(`universal`, `python_uv`, `python_pip`, `demo_bundles`, `demo_flags`), and
`opa build` needs it present at build time to typecheck cross-package calls -
but two independently-built bundles that each merge in a copy of `helpers`
cannot be loaded into the same OPA instance: `opa run` rejects it with
"overlapping roots" the moment more than one bundle claims the same root.
There is no supported OPA pattern for "N independent bundles sharing a common
dependency, loaded together" (OPA's own docs recommend aggregating centrally
instead), so this module composes exactly one bundle per request, containing
`helpers` plus whichever policy bundles the caller asked for. The client's
`opa run` config therefore always has exactly one `bundles.<name>` entry,
never several that could collide.

Composed bundles are content-addressed and cached under COMPOSED_DIR so
repeat requests for the same bundle set are free.
"""

import hashlib
import logging
import subprocess
from pathlib import Path
from typing import List

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bundles")

POLICIES_DIR = Path("policies")
COMPOSED_DIR = Path("bundles/composed")

# Names must match directories under policies/ exactly - this is an explicit
# allowlist, not a directory listing, so an arbitrary path can never be
# smuggled into the `opa build` invocation below.
KNOWN_BUNDLES = {"universal", "python_uv", "python_pip", "demo_bundles", "demo_flags"}

# helpers is a build-time dependency only; it is never itself a selectable
# bundle name, since it has no decisions/guidances of its own.
HELPERS_DIR = POLICIES_DIR / "helpers"


def _cache_key(names: List[str]) -> str:
    """Content-address a bundle set by its sorted, deduplicated name list."""
    canonical = ",".join(sorted(set(names)))
    digest = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    return f"{canonical.replace(',', '+')}-{digest}"


@router.get("/composed")
async def get_composed_bundle(
    names: str = Query(..., description="Comma-separated bundle names, e.g. 'universal,python_uv'"),
) -> FileResponse:
    requested = [n.strip() for n in names.split(",") if n.strip()]
    if not requested:
        raise HTTPException(status_code=400, detail="No bundle names given")

    unknown = [n for n in requested if n not in KNOWN_BUNDLES]
    if unknown:
        raise HTTPException(status_code=404, detail=f"Unknown bundle(s): {unknown}")

    key = _cache_key(requested)
    output_path = COMPOSED_DIR / f"{key}.tar.gz"

    if not output_path.is_file():
        COMPOSED_DIR.mkdir(parents=True, exist_ok=True)
        build_paths = [str(HELPERS_DIR)] + [str(POLICIES_DIR / n) for n in sorted(set(requested))]

        cmd = ["opa", "build", "-o", str(output_path)]
        for p in build_paths:
            cmd += ["-b", p]

        logger.info(f"Composing bundle for {sorted(set(requested))}: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"opa build failed for {requested}: {result.stderr}")
            if output_path.exists():
                output_path.unlink()
            raise HTTPException(
                status_code=500, detail=f"Failed to compose bundle: {result.stderr}"
            )

    return FileResponse(
        output_path,
        media_type="application/gzip",
        filename=f"{key}.tar.gz",
    )
