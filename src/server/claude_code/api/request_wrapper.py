"""Generic request wrapper for bundle-aware hook processing."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class RequestWrapper(BaseModel):
    """Wrapper for hook requests that includes bundle filtering."""

    bundles: List[str]
    workspace_root: Optional[str] = None
    event: Dict[str, Any]
