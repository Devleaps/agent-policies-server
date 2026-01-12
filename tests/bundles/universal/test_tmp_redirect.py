"""Test /tmp redirect blocking."""
import pytest
from src.bundles.universal import bash_rules_bundle_universal
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_tmp_redirect_simple(bash_event):
    """Test that simple redirects to /tmp are blocked."""
    assert_deny(bash_rules_bundle_universal, bash_event("echo test > /tmp/file.txt"))
    assert_deny(bash_rules_bundle_universal, bash_event("cat data.txt > /tmp/output.log"))
    assert_deny(bash_rules_bundle_universal, bash_event("echo hello >> /tmp/append.txt"))


def test_tmp_redirect_safe_paths(bash_event):
    """Test that workspace redirects are allowed."""
    assert_allow(bash_rules_bundle_universal, bash_event("echo test > output.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("cat data > ./logs/output.log"))
    assert_allow(bash_rules_bundle_universal, bash_event("echo hello >> results.txt"))


def test_tmp_redirect_heredoc_unparseable(bash_event):
    """Heredoc commands can't be parsed (incomplete) so default to ASK."""
    assert_pass(bash_rules_bundle_universal, bash_event("cat > /tmp/test.py << 'EOF'"))
    assert_pass(bash_rules_bundle_universal, bash_event("cat > /tmp/script.sh <<EOF"))


def test_tmp_redirect_no_redirect(bash_event):
    """Test commands without redirects are allowed."""
    assert_allow(bash_rules_bundle_universal, bash_event("echo hello"))
    assert_allow(bash_rules_bundle_universal, bash_event("cat file.txt"))
    assert_allow(bash_rules_bundle_universal, bash_event("ls -la"))
