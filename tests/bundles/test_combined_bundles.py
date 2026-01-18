"""Test with multiple bundles combined."""
from src.bundles_impl import bash_rules_bundle_universal
from src.bundles_impl import bash_rules_bundle_python_uv


def test_uv_pytest_with_both_bundles(bash_event):
    """Test uv run pytest with both universal and python-uv bundles."""
    event = bash_event("uv run pytest tests/test_piped_uv.py -xvs")

    # Simulate server running both bundles
    all_results = []
    all_results.extend(list(bash_rules_bundle_universal(event)))
    all_results.extend(list(bash_rules_bundle_python_uv(event)))

    print(f"\nResults for 'uv run pytest ...' with BOTH bundles:")
    for r in all_results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else 'None'}")

    actions = [r.action for r in all_results]
    print(f"\nAll actions: {actions}")
