"""Test with multiple bundles combined."""
from src.evaluation import evaluate_bash_rules


def test_uv_pytest_with_both_bundles(bash_event):
    """Test uv run pytest with both universal and python_uv bundles."""
    event = bash_event("uv run pytest tests/test_piped_uv.py -xvs", bundles=["universal", "python_uv"])

    # Evaluate with both bundles enabled
    all_results = list(evaluate_bash_rules(event))

    print(f"\nResults for 'uv run pytest ...' with BOTH bundles:")
    for r in all_results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else 'None'}")

    actions = [r.action for r in all_results]
    print(f"\nAll actions: {actions}")
