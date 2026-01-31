from src.bundles_impl import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny


def test_chmod_safe_paths(bash_event):
    """Test that chmod is allowed on safe workspace-relative paths"""
    assert_allow(evaluate_bash_rules, bash_event("chmod +x script.sh"))
    assert_allow(evaluate_bash_rules, bash_event("chmod 755 deploy.sh"))
    assert_allow(evaluate_bash_rules, bash_event("chmod -R 644 src/"))
    assert_allow(evaluate_bash_rules, bash_event("chmod u+w docs/README.md"))


def test_chmod_unsafe_absolute_paths(bash_event):
    """Test that chmod is blocked on absolute paths"""
    assert_deny(evaluate_bash_rules, bash_event("chmod +x /usr/bin/script"))
    assert_deny(evaluate_bash_rules, bash_event("chmod 777 /etc/passwd"))
    assert_deny(evaluate_bash_rules, bash_event("chmod -R 755 /var/www"))


def test_chmod_unsafe_path_traversal(bash_event):
    """Test that chmod is blocked on path traversal attempts"""
    assert_deny(evaluate_bash_rules, bash_event("chmod +x ../../../etc/passwd"))
    assert_deny(evaluate_bash_rules, bash_event("chmod 755 ../../secrets/key.pem"))


def test_chmod_unsafe_tmp(bash_event):
    """Test that chmod is blocked on /tmp paths"""
    assert_deny(evaluate_bash_rules, bash_event("chmod 777 /tmp/malicious"))


def test_chmod_unsafe_home(bash_event):
    """Test that chmod is blocked on home directory paths"""
    assert_deny(evaluate_bash_rules, bash_event("chmod 600 ~/.ssh/id_rsa"))
    assert_deny(evaluate_bash_rules, bash_event("chmod -R 755 ~/bin"))
