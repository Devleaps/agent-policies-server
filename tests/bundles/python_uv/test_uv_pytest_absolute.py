"""Test uv run pytest with absolute paths."""
from src.bundles.python_uv import bash_rules_bundle_python_uv


def test_uv_run_pytest_with_absolute_path(bash_event):
    """Test uv run pytest with absolute path."""
    event = bash_event("uv run pytest /Users/philipp/DevLeaps/agent-internal-policies/tests/test_piped_uv.py -xvs")
    results = list(bash_rules_bundle_python_uv(event))

    print(f"\nResults for 'uv run pytest /absolute/path':")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else 'None'}")
