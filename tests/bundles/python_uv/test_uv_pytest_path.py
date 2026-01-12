"""Test uv run pytest with paths."""
from src.bundles.python_uv import bash_rules_bundle_python_uv


def test_uv_run_pytest_with_file_path(bash_event):
    """Test uv run pytest with file path."""
    event = bash_event("uv run pytest tests/test_piped_uv.py::test_pytest_pipe_head_with_uv_bundle -xvs")
    results = list(bash_rules_bundle_python_uv(event))

    print(f"\nResults for 'uv run pytest tests/...':")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else 'None'}")

    actions = [r.action for r in results]
    assert "allow" in actions, f"Should ALLOW uv run pytest, got: {actions}"
