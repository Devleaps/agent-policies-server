"""Test piped commands with python-uv bundle."""
from src.bundles.python_uv import bash_rules_bundle_python_uv


def test_pytest_pipe_head_with_uv_bundle(bash_event):
    """Test pytest | head with python-uv bundle."""
    event = bash_event("pytest | head")
    results = list(bash_rules_bundle_python_uv(event))

    print(f"\nResults for 'pytest | head' with python-uv bundle:")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') else ''}")

    actions = [r.action for r in results]
    if "deny" in actions:
        print("  (DENY because python-uv blocks direct pytest)")
