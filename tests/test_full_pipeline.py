"""Test full policy evaluation pipeline to see actual final decisions."""

from devleaps.policies.server.common.models import POLICY_PRECEDENCE, PolicyAction, PolicyDecision
from src.bundles.universal import bash_rules_bundle_universal
from tests.helpers import eval_rule


def get_final_decision(results):
    """Apply precedence logic to get final decision like the framework does."""
    decisions = [r for r in results if isinstance(r, PolicyDecision)]

    if not decisions:
        return None

    # Use POLICY_PRECEDENCE to find highest priority
    for action in POLICY_PRECEDENCE:
        matching = [d for d in decisions if d.action == action]
        if matching:
            return matching[0]
    return None


def test_cat_to_tmp_full_pipeline(bash_event):
    """Test cat > /tmp/test.txt through full pipeline."""
    event = bash_event("cat > /tmp/test.txt")

    results = eval_rule(bash_rules_bundle_universal, event)

    print(f"\n=== cat > /tmp/test.txt ===")
    print(f"Total results: {len(results)}")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else '(no reason)'}")

    final = get_final_decision(results)
    print(f"Final decision: {final.action if final else 'None'}")

    assert final is not None, "Expected a decision"
    assert final.action == PolicyAction.DENY, f"Expected DENY for /tmp/ redirect, got {final.action}"


def test_echo_to_tmp_full_pipeline(bash_event):
    """Test echo > /tmp/test.txt through full pipeline."""
    event = bash_event("echo 'test' > /tmp/test.txt")

    results = eval_rule(bash_rules_bundle_universal, event)

    print(f"\n=== echo > /tmp/test.txt ===")
    print(f"Total results: {len(results)}")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else '(no reason)'}")

    final = get_final_decision(results)
    print(f"Final decision: {final.action if final else 'None'}")

    assert final is not None, "Expected a decision"
    assert final.action == PolicyAction.DENY, f"Expected DENY for /tmp/ redirect, got {final.action}"


def test_cat_heredoc_to_tmp_full_pipeline(bash_event):
    """Test cat > /tmp/script.sh << 'EOF' through full pipeline."""
    command = """cat > /tmp/script.sh << 'EOF'
#!/bin/bash
echo "test"
EOF"""

    event = bash_event(command)

    results = eval_rule(bash_rules_bundle_universal, event)

    print(f"\n=== cat heredoc to /tmp ===")
    print(f"Total results: {len(results)}")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else '(no reason)'}")

    final = get_final_decision(results)
    print(f"Final decision: {final.action if final else 'None'}")

    if final:
        print(f"Action: {final.action}")
    else:
        print("No final decision - would default to ASK")


def test_cat_to_workspace_full_pipeline(bash_event):
    """Test cat > file.txt (safe) through full pipeline."""
    event = bash_event("cat > test.txt")

    results = eval_rule(bash_rules_bundle_universal, event)

    print(f"\n=== cat > test.txt (safe) ===")
    print(f"Total results: {len(results)}")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else '(no reason)'}")

    final = get_final_decision(results)
    print(f"Final decision: {final.action if final else 'None'}")

    assert final is not None, "Expected a decision"
    assert final.action == PolicyAction.ALLOW, f"Expected ALLOW for workspace redirect, got {final.action}"


def test_complex_multiline_command(bash_event):
    """Test the original complex command from the issue."""
    command = """cat > /tmp/add_lifecycle_ignore.sh << 'EOF'
#!/bin/bash
services=(
  "service-a"
  "service-b"
)

for project in proj1 proj2; do
  for env in dev prod; do
    file="config/$project/env/$env/vars.tfvars"
    if [ -f "$file" ]; then
      echo "Processing $file..."
    fi
  done
done
EOF
chmod +x /tmp/add_lifecycle_ignore.sh
/tmp/add_lifecycle_ignore.sh"""

    event = bash_event(command)

    results = eval_rule(bash_rules_bundle_universal, event)

    print(f"\n=== Complex multiline command ===")
    print(f"Total results: {len(results)}")
    for r in results:
        print(f"  {r.action}: {r.reason if hasattr(r, 'reason') and r.reason else '(no reason)'}")

    final = get_final_decision(results)
    print(f"Final decision: {final.action if final else 'None'}")

    if final:
        print(f"This explains the behavior: {final.action}")
