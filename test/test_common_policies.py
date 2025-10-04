"""
Test script to validate the common policy refactoring.

This verifies that:
1. Common policies can be imported
2. Rules are created correctly
3. The main module can be imported without errors
"""

def test_common_policies_import():
    """Test that common policies can be imported."""
    from src.common import whitelist_always, whitelist_safe_paths

    print("✓ Common policies imported successfully")

    # Check whitelist_always rules
    assert hasattr(whitelist_always, 'all_rules'), "whitelist_always should have all_rules"
    assert len(whitelist_always.all_rules) > 0, "whitelist_always should have rules"
    print(f"✓ whitelist_always has {len(whitelist_always.all_rules)} rule(s)")

    # Check whitelist_safe_paths rules
    assert hasattr(whitelist_safe_paths, 'all_rules'), "whitelist_safe_paths should have all_rules"
    assert len(whitelist_safe_paths.all_rules) > 0, "whitelist_safe_paths should have rules"
    print(f"✓ whitelist_safe_paths has {len(whitelist_safe_paths.all_rules)} rule(s)")


def test_main_module_import():
    """Test that main module can be imported."""
    import src.main

    print("✓ Main module imported successfully")

    assert hasattr(src.main, 'setup_all_policies'), "main should have setup_all_policies"
    print("✓ setup_all_policies function exists")


def test_policy_rule_creation():
    """Test that policy rules are created with correct attributes."""
    from src.common import whitelist_always, whitelist_safe_paths

    # Check whitelist_always rules have correct names
    for rule in whitelist_always.all_rules:
        assert callable(rule), f"Rule {rule} should be callable"
        assert hasattr(rule, '__name__'), f"Rule should have __name__"

    print(f"✓ All {len(whitelist_always.all_rules)} whitelist_always rule(s) are properly formed")

    # Check whitelist_safe_paths rules have correct names
    for rule in whitelist_safe_paths.all_rules:
        assert callable(rule), f"Rule {rule} should be callable"
        assert hasattr(rule, '__name__'), f"Rule should have __name__"

    print(f"✓ All {len(whitelist_safe_paths.all_rules)} whitelist_safe_paths rule(s) are properly formed")


def test_rule_functionality():
    """Test that rules can be called with mock data."""
    from src.common import whitelist_always
    from devleaps.policies.server.common.models import ToolUseEvent
    from devleaps.policies.server.common.enums import SourceClient

    # Create a mock event for pwd command
    mock_event = ToolUseEvent(
        session_id="test-session",
        tool_name="Bash",
        source_client=SourceClient.CLAUDE_CODE,
        tool_is_bash=True,
        command="pwd",
        parameters={"command": "pwd"}
    )

    # Get the whitelist_always rule
    rule = whitelist_always.all_rules[0]

    # Call the rule (it's a generator)
    result = list(rule(mock_event))
    assert len(result) == 1, "Should return 1 decision for whitelisted command"
    print(f"✓ whitelist_always rule executed successfully for pwd command")


if __name__ == "__main__":
    print("Testing common policy refactoring...\n")

    try:
        test_common_policies_import()
        print()

        test_main_module_import()
        print()

        test_policy_rule_creation()
        print()

        test_rule_functionality()
        print()

        print("=" * 50)
        print("All tests passed! ✓")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
