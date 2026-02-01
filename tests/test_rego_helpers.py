"""Tests for Rego helper functions in policies/helpers/utils.rego."""

import pytest
from src.evaluation.rego import RegoEvaluator
from src.evaluation.parser import BashCommandParser
from tests.helpers import assert_allow, assert_deny


@pytest.fixture
def rego_eval():
    """Create Rego evaluator for testing helpers."""
    return RegoEvaluator(policy_dir="policies")


class TestIsSafePath:
    """Test is_safe_path helper function."""

    def test_allows_relative_paths(self, rego_eval, bash_event):
        """Relative paths should be allowed."""
        event = bash_event("cat src/file.py")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_allows_simple_filename(self, rego_eval, bash_event):
        """Simple filenames should be allowed."""
        event = bash_event("cat file.txt")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_allows_nested_relative(self, rego_eval, bash_event):
        """Nested relative paths should be allowed."""
        event = bash_event("cat src/core/file.py")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_blocks_absolute_paths(self, rego_eval, bash_event):
        """Absolute paths should be blocked."""
        event = bash_event("cat /etc/passwd")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_blocks_home_directory(self, rego_eval, bash_event):
        """Home directory paths should be blocked."""
        event = bash_event("cat ~/file.txt")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_blocks_path_traversal(self, rego_eval, bash_event):
        """Path traversal should be blocked."""
        event = bash_event("cat ../secrets")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_blocks_dot_dot(self, rego_eval, bash_event):
        """.. should be blocked."""
        event = bash_event("cat ..")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_blocks_embedded_traversal(self, rego_eval, bash_event):
        """Embedded path traversal should be blocked."""
        event = bash_event("cat src/../etc/passwd")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_blocks_tmp_directory(self, rego_eval, bash_event):
        """Paths in /tmp should be blocked."""
        event = bash_event("cat /tmp/file.txt")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)


class TestIsLocalhostURL:
    """Test is_localhost_url helper function."""

    def test_accepts_localhost_http(self, rego_eval, bash_event):
        """HTTP localhost URLs should be allowed."""
        event = bash_event("curl http://localhost:8000")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_accepts_localhost_https(self, rego_eval, bash_event):
        """HTTPS localhost URLs should be allowed."""
        event = bash_event("curl https://localhost:3000/api")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_accepts_127_0_0_1(self, rego_eval, bash_event):
        """127.0.0.1 URLs should be allowed."""
        event = bash_event("curl http://127.0.0.1:8080")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_accepts_127_variant(self, rego_eval, bash_event):
        """127.x.x.x variant URLs should be allowed."""
        event = bash_event("curl http://127.1.2.3:9000")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_accepts_ipv6_localhost(self, rego_eval, bash_event):
        """IPv6 localhost URLs should be allowed."""
        event = bash_event("curl http://[::1]:8000")
        from src.evaluation import evaluate_bash_rules
        assert_allow(evaluate_bash_rules, event)

    def test_rejects_remote_domain(self, rego_eval, bash_event):
        """Remote domain URLs should be blocked."""
        event = bash_event("curl https://example.com")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_rejects_remote_ip(self, rego_eval, bash_event):
        """Remote IP URLs should be blocked."""
        event = bash_event("curl http://192.168.1.1")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_rejects_ip_with_127_in_it(self, rego_eval, bash_event):
        """IPs containing 127 but not 127.x.x.x should be blocked."""
        event = bash_event("curl http://192.168.127.100")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)

    def test_rejects_localhost_in_query_param(self, rego_eval, bash_event):
        """URLs with localhost in query params should be blocked."""
        event = bash_event("curl https://evil.com/?redirect=http://127.0.0.1")
        from src.evaluation import evaluate_bash_rules
        assert_deny(evaluate_bash_rules, event)
