from src.bundles_impl import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny


def test_curl_localhost(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("curl http://localhost:8080"))
    assert_allow(evaluate_bash_rules, bash_event("curl http://127.0.0.1:3000"))
    assert_allow(evaluate_bash_rules, bash_event("curl http://[::1]:5000"))


def test_curl_allowed_domains(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("curl https://agent-policies.devleaps.nl"))
    assert_allow(evaluate_bash_rules, bash_event("curl https://agent-policies.dev.devleaps.nl"))
    assert_allow(evaluate_bash_rules, bash_event("curl https://requests.readthedocs.io/en/latest/"))
    assert_allow(evaluate_bash_rules, bash_event("curl https://docs.python.org.readthedocs.io"))


def test_curl_disallowed_domains(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("curl https://google.com"))
    assert_deny(evaluate_bash_rules, bash_event("curl https://example.com"))
    assert_deny(evaluate_bash_rules, bash_event("curl http://api.github.com"))
