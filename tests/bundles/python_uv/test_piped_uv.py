"""Test piped commands with python_uv bundle."""
from src.bundles_impl import evaluate_bash_rules


def test_pytest_pipe_head_with_uv_bundle(bash_event):
    """Test pytest | head with python_uv bundle."""
    event = bash_event("pytest | head", bundles=["universal", "python_uv"])
    results = list(evaluate_bash_rules(event))

    print(f"\nResults for 'pytest | head' with python_uv bundle:")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') else ''}")

    actions = [r.action for r in results]
    if "deny" in actions:
        print("  (DENY because python_uv blocks direct pytest)")
