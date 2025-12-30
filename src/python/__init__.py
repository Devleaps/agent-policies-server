"""Python - Shared package whitelist and universal guidance policies.

Only includes policies that work with ANY tool execution method (pip or uv).
Tool-specific policies (black, ruff, mypy, pytest) are in python_pip bundle.
"""

from src.python.comment_ratio_guidance import comment_ratio_guidance_rule
from src.python.comment_overlap_guidance import comment_overlap_guidance_rule
from src.python.mid_code_import_guidance import mid_code_import_guidance_rule

# Centralized whitelist of allowed packages for both pip and uv
ALLOWED_PACKAGES = {
    "requests",
    "fastapi",
    "uvicorn",
    "uvicorn[standard]",
    "pydantic",
    "pytest",
    "httpx",
    "fire",
    "jinja2",
    "streamlit",
    "pandas",
    "numpy",
    "sqlalchemy",
    "python-dotenv",
    "pyyaml",
    "toml",
}

all_rules = []

all_post_file_edit_rules = [
    comment_ratio_guidance_rule,
    comment_overlap_guidance_rule,
    mid_code_import_guidance_rule,
]

all_middleware = []

__all__ = ["ALLOWED_PACKAGES", "all_rules", "all_post_file_edit_rules", "all_middleware"]
