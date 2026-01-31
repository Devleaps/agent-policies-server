"""Test uv run pytest with paths."""
from src.bundles_impl import evaluate_bash_rules


def test_uv_run_pytest_with_file_path(bash_event):
    """Test uv run pytest with file path."""
    event = bash_event("uv run pytest tests/test_piped_uv.py::test_pytest_pipe_head_with_uv_bundle -xvs", bundles=["universal", "python_uv"])
    results = list(evaluate_bash_rules(event))

    print(f"\nResults for 'uv run pytest tests/...':")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else 'None'}")

    actions = [r.action for r in results]
    assert "allow" in actions, f"Should ALLOW uv run pytest, got: {actions}"
