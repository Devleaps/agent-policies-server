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

Composed bundles are cached under COMPOSED_DIR, keyed by both the requested
bundle-name set and a hash of the actual .rego source content under each
policy directory - so repeat requests for the same bundle set are free, and
editing a policy file invalidates the cache automatically rather than
requiring a manual restart or cache-clear.
"""

import hashlib
import logging
import os
import subprocess
import tempfile
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


def _hash_rego_sources(build_paths: List[str]) -> str:
    """Hash the content of every .rego file under each build path, in a
    stable (sorted) order, so a cache key changes whenever policy source
    actually changes - not just when the requested bundle-name set does.
    """
    hasher = hashlib.sha256()
    for build_path in build_paths:
        for rego_file in sorted(Path(build_path).rglob("*.rego")):
            hasher.update(str(rego_file).encode())
            hasher.update(rego_file.read_bytes())
    return hasher.hexdigest()[:16]


def _cache_key(names: List[str], build_paths: List[str]) -> str:
    """Content-address a bundle set by its sorted, deduplicated name list
    *and* the actual .rego source content under each path - a name-only key
    would keep serving a stale cached artifact forever after a policy edit,
    since the name set doesn't change when a file's contents do.
    """
    canonical = ",".join(sorted(set(names)))
    content_digest = _hash_rego_sources(build_paths)
    return f"{canonical.replace(',', '+')}-{content_digest}"


@router.get("")
async def list_known_bundles() -> dict:
    """The allowlist itself, so clients (agent-policies-adapter's daemon.js)
    can validate a configured bundle name locally before ever hitting
    /composed, instead of hardcoding a second copy of KNOWN_BUNDLES that
    silently drifts out of sync with this one.
    """
    return {"bundles": sorted(KNOWN_BUNDLES)}


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

    build_paths = [str(HELPERS_DIR)] + [str(POLICIES_DIR / n) for n in sorted(set(requested))]
    key = _cache_key(requested, build_paths)
    output_path = COMPOSED_DIR / f"{key}.tar.gz"

    if not output_path.is_file():
        COMPOSED_DIR.mkdir(parents=True, exist_ok=True)

        # Build to a temp file in the same directory and atomically publish
        # via os.replace on success, so a concurrent request for the same
        # key can never observe a partially-written tarball through the
        # is_file() check above - it either sees nothing (and builds its
        # own, redundantly but safely) or the complete final file.
        fd, tmp_path_str = tempfile.mkstemp(dir=COMPOSED_DIR, suffix=".tar.gz.tmp")
        os.close(fd)
        tmp_path = Path(tmp_path_str)

        cmd = ["opa", "build", "-o", str(tmp_path)]
        for p in build_paths:
            cmd += ["-b", p]

        logger.info(f"Composing bundle for {sorted(set(requested))}: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"opa build failed for {requested}: {result.stderr}")
            tmp_path.unlink(missing_ok=True)
            # Full stderr (absolute server paths, Rego internals) is logged
            # above but never sent to the client - only a generic message.
            raise HTTPException(status_code=500, detail="Failed to compose bundle")

        os.replace(tmp_path, output_path)

    return FileResponse(
        output_path,
        media_type="application/gzip",
        filename=f"{key}.tar.gz",
    )
