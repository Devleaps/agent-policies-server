"""Test mv command with subdirectory paths."""
from src.bundles_impl import bash_rules_bundle_universal
from tests.helpers import assert_allow


def test_mv_to_subdirectory(bash_event):
    """Test mv file.txt subdir/file.txt should be allowed."""
    assert_allow(bash_rules_bundle_universal, bash_event("mv test_bash_evaluator.py core/test_bash_evaluator.py"))


def test_mv_simple_rename(bash_event):
    """Test mv file.txt newname.txt should be allowed."""
    assert_allow(bash_rules_bundle_universal, bash_event("mv oldfile.txt newfile.txt"))
