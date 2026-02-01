"""Test mv command with subdirectory paths."""
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow


def test_mv_to_subdirectory(bash_event):
    """Test mv file.txt subdir/file.txt should be allowed."""
    assert_allow(evaluate_bash_rules, bash_event("mv test_bash_evaluator.py core/test_bash_evaluator.py"))


def test_mv_simple_rename(bash_event):
    """Test mv file.txt newname.txt should be allowed."""
    assert_allow(evaluate_bash_rules, bash_event("mv oldfile.txt newfile.txt"))
