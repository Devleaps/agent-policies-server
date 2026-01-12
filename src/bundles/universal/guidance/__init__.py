"""Guidance rules for PostFileEditEvent.

Provides non-blocking guidance and suggestions for code quality improvements.
"""

from src.bundles.universal.guidance.comment_ratio import comment_ratio_guidance_rule
from src.bundles.universal.guidance.comment_overlap import comment_overlap_guidance_rule
from src.bundles.universal.guidance.commented_code import commented_code_guidance_rule
from src.bundles.universal.guidance.legacy_code import legacy_code_guidance_rule
from src.bundles.universal.guidance.mid_code_import import mid_code_import_guidance_rule
from src.bundles.universal.guidance.readme_license import readme_license_guidance_rule

all_guidance_rules = [
    comment_ratio_guidance_rule,
    comment_overlap_guidance_rule,
    commented_code_guidance_rule,
    legacy_code_guidance_rule,
    mid_code_import_guidance_rule,
    readme_license_guidance_rule,
]

__all__ = ["all_guidance_rules"]
