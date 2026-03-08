"""
Common Gemini hook models and types.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GeminiRequestWrapper(BaseModel):
    """Wrapper for Gemini hook requests that includes bundle filtering."""

    bundles: List[str]
    default_policy_behavior: str = "ask"
    event: Dict[str, Any]


class GeminiDecision(str, Enum):
    """Decision values for Gemini hooks."""

    ALLOW = "allow"
    DENY = "deny"


class GeminiBaseOutput(BaseModel):
    """Base output for all Gemini hooks."""

    model_config = ConfigDict(populate_by_name=True)

    decision: Optional[GeminiDecision] = None
    reason: Optional[str] = None
    continue_: Optional[bool] = Field(default=None, serialization_alias="continue")
    systemMessage: Optional[str] = None
