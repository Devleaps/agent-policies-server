"""
Guidance checks must judge the file as it reads after the edit: removed
lines are not additions and must not trigger guidance.
"""

import pytest

from src.guidance.python_comments import (
    comment_overlap_guidance_rule,
    comment_ratio_guidance_rule,
    commented_code_guidance_rule,
    legacy_code_guidance_rule,
)
from src.guidance.python_imports import mid_code_import_guidance_rule
from src.server.models import PatchLine, PostFileEditEvent, StructuredPatch


def _event(lines):
    patch_lines = [PatchLine(operation=op, content=content) for op, content in lines]
    return PostFileEditEvent(
        session_id="t",
        source_client="claude-code",
        file_path="module.py",
        structured_patch=[
            StructuredPatch(
                oldStart=1, oldLines=1, newStart=1, newLines=1, lines=patch_lines
            )
        ],
    )


CASES = {
    "comment_ratio": (
        comment_ratio_guidance_rule,
        [
            ("removed", "# one"),
            ("removed", "# two"),
            ("removed", "# three"),
            ("unchanged", "x = 1"),
        ],
    ),
    "comment_overlap": (
        comment_overlap_guidance_rule,
        [("removed", "# add to counter"), ("unchanged", "counter += 1")],
    ),
    "commented_code": (
        commented_code_guidance_rule,
        [("removed", "#    x = 1"), ("removed", "#    y = 2"), ("unchanged", "z = 3")],
    ),
    "legacy_code": (
        legacy_code_guidance_rule,
        [("removed", "# legacy shim, remove later"), ("unchanged", "z = 3")],
    ),
    "mid_code_import": (
        mid_code_import_guidance_rule,
        [("removed", "    import os"), ("unchanged", "z = 3")],
    ),
}


@pytest.mark.parametrize("name", CASES)
def test_removed_lines_do_not_trigger_guidance(name):
    rule, lines = CASES[name]
    assert list(rule(_event(lines))) == []


@pytest.mark.parametrize("name", CASES)
def test_same_lines_added_still_trigger_guidance(name):
    rule, lines = CASES[name]
    added = [("added" if op == "removed" else op, content) for op, content in lines]
    assert len(list(rule(_event(added)))) == 1


def test_overlap_skips_removed_line_between_comment_and_code():
    """The line after a comment is the next line that survives the edit."""
    lines = [
        ("added", "# add to counter"),
        ("removed", "total = compute_everything()"),
        ("added", "counter += 1"),
    ]
    assert len(list(comment_overlap_guidance_rule(_event(lines)))) == 1
