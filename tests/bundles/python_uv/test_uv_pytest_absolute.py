"""Test uv run pytest with absolute paths."""
from src.bundles_impl import evaluate_bash_rules


def test_uv_run_pytest_with_absolute_path(bash_event):
    """Test uv run pytest with absolute path."""
    event = bash_event("uv run pytest /Users/philipp/DevLeaps/agent-internal-policies/tests/test_piped_uv.py -xvs", bundles=["universal", "python_uv"])
    results = list(evaluate_bash_rules(event))

    print(f"\nResults for 'uv run pytest /absolute/path':")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else 'None'}")
