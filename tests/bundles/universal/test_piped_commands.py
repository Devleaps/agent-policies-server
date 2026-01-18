"""Test piped command combinations."""
from src.bundles_impl import bash_rules_bundle_universal


def test_pytest_pipe_head(bash_event):
    """Test that pytest | head works."""
    event = bash_event("pytest | head")
    results = list(bash_rules_bundle_universal(event))

    print(f"\nResults for 'pytest | head':")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') else ''}")

    actions = [r.action for r in results]
    assert "ask" not in actions, f"Should not ASK for 'pytest | head', got: {results}"
