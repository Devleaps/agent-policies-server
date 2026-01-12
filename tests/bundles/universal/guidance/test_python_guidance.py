import pytest
from devleaps.policies.server.common.models import PostFileEditEvent
from src.bundles.universal.guidance.comment_overlap import comment_overlap_guidance_rule
from src.bundles.universal.guidance.comment_ratio import comment_ratio_guidance_rule
from src.bundles.universal.guidance.commented_code import commented_code_guidance_rule
from src.bundles.universal.guidance.mid_code_import import mid_code_import_guidance_rule
from src.bundles.universal.guidance.legacy_code import legacy_code_guidance_rule
from src.bundles.universal.guidance.readme_license import readme_license_guidance_rule
from tests.helpers import assert_pass, assert_guidance


def test_comment_ratio(file_edit_event):
    assert_pass(comment_ratio_guidance_rule, file_edit_event("test.py", [
        ("added", "# Comment explaining the function"),
        ("added", "def calculate():"),
        ("added", "    x = 1"),
        ("added", "    y = 2"),
        ("added", "    return x + y"),
    ]))

    assert_guidance(comment_ratio_guidance_rule, file_edit_event("test.py", [
        ("added", "# Comment 1"),
        ("added", "# Comment 2"),
        ("added", "# Comment 3"),
        ("added", "# Comment 4"),
        ("added", "# Comment 5"),
        ("added", "code = 1"),
        ("added", "code = 2"),
    ]))


def test_comment_overlap(file_edit_event):
    assert_pass(comment_overlap_guidance_rule, file_edit_event("test.py", [
        ("added", "# Cache the result"),
        ("added", "cached_value = compute()"),
    ]))

    assert_guidance(comment_overlap_guidance_rule, file_edit_event("test.py", [
        ("added", "# Significant overlap with code"),
        ("added", "significant_overlap_with_code = True"),
    ]))


def test_commented_code(file_edit_event):
    assert_pass(commented_code_guidance_rule, file_edit_event("test.py", [
        ("added", "def foo():"),
        ("added", "    # This is a comment"),
        ("added", "    return True"),
    ]))

    assert_guidance(commented_code_guidance_rule, file_edit_event("test.py", [
        ("added", "def foo():"),
        ("added", "    # old_code = 1"),
        ("added", "    # old_code = 2"),
        ("added", "    return True"),
    ]))


def test_legacy_deprecated(file_edit_event):
    assert_guidance(legacy_code_guidance_rule, file_edit_event("test.py", [
        ("added", "# DEPRECATED: This function will be removed"),
        ("added", "def old_function():"),
        ("added", "    pass"),
    ]))

    assert_guidance(legacy_code_guidance_rule, file_edit_event("test.py", [
        ("added", "# This method is deprecated"),
        ("added", "def old_method():"),
        ("added", "    pass"),
    ]))


def test_readme_license(file_edit_event):
    assert_guidance(readme_license_guidance_rule, file_edit_event("README.md", [
        ("added", "## LICENSE"),
        ("added", "MIT License"),
    ]))

    assert_guidance(readme_license_guidance_rule, file_edit_event("readme.md", [
        ("added", "## license"),
        ("added", "Apache 2.0"),
    ]))

    assert_pass(readme_license_guidance_rule, file_edit_event("other.md", [
        ("added", "## LICENSE"),
    ]))


def test_mid_code_import(file_edit_event):
    assert_pass(mid_code_import_guidance_rule, file_edit_event("test.txt", [
        ("added", "def function():"),
        ("added", "    import os"),
    ]))

    event = PostFileEditEvent(
        session_id="test-session",
        source_client="claude_code",
        file_path="test.py",
        operation="write",
        structured_patch=None
    )
    assert_pass(mid_code_import_guidance_rule, event)

    assert_pass(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "import os"),
        ("added", "import sys"),
        ("added", "from typing import List"),
    ]))

    assert_pass(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "# import x"),
        ("added", "# from x import y"),
        ("added", "def function():"),
        ("added", "    # import z"),
        ("added", "    pass"),
    ]))

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "    import os"),
    ]))

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "    from os import path"),
    ]))

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "class MyClass:"),
        ("added", "    import json"),
    ]))

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "def outer():"),
        ("added", "    def inner():"),
        ("added", "        import sys"),
    ]))

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "def function():"),
        ("added", "\timport os"),
    ]))

    results = list(mid_code_import_guidance_rule(file_edit_event("test.py", [
        ("added", "def function1():"),
        ("added", "    import os"),
        ("added", ""),
        ("added", "def function2():"),
        ("added", "    import sys"),
    ])))
    assert len(results) == 1

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "import os"),
        ("added", "from typing import List"),
        ("added", ""),
        ("added", "def function():"),
        ("added", "    import json"),
    ]))

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "import os"),
        ("added", "from typing import Optional"),
        ("added", ""),
        ("added", ""),
        ("added", "class MyClass:"),
        ("added", '    """A sample class."""'),
        ("added", ""),
        ("added", "    def process(self):"),
        ("added", "        # Lazy import for performance"),
        ("added", "        import expensive_module"),
        ("added", "        return expensive_module.process()"),
    ]))

    assert_guidance(mid_code_import_guidance_rule, file_edit_event("test.py", [
        ("added", "def process_data(self, data: Any) -> Result:"),
        ("added", '    """Process the data."""'),
        ("added", "    import json"),
        ("added", "    return json.loads(data)"),
    ]))
