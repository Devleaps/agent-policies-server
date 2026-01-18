import pytest
from src.bundles_impl import bash_rules_bundle_python_uv
from tests.helpers import assert_allow, assert_deny, assert_pass, assert_ask


def test_uv_add(bash_event):
    assert_allow(bash_rules_bundle_python_uv, bash_event("uv add requests"))
    assert_allow(bash_rules_bundle_python_uv, bash_event("uv add httpx"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("uv add this-package-definitely-does-not-exist-12345"))


def test_uv_pip_install(bash_event):
    assert_deny(bash_rules_bundle_python_uv, bash_event("uv pip install requests"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("uv pip install requests==2.28.0"))
    assert_ask(bash_rules_bundle_python_uv, bash_event("uv pip list"))


def test_uv_python(bash_event):
    assert_deny(bash_rules_bundle_python_uv, bash_event("python script.py"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("python -m pytest"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("python3 -m mymodule"))
    assert_ask(bash_rules_bundle_python_uv, bash_event("python scripts/something.py"))


def test_pytest_uv_requirement(bash_event):
    assert_deny(bash_rules_bundle_python_uv, bash_event("pytest tests/"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("pytest -v tests/test_something.py"))
    assert_allow(bash_rules_bundle_python_uv, bash_event("uv run pytest tests/"))
    assert_allow(bash_rules_bundle_python_uv, bash_event("uv run pytest -v tests/"))


def test_uv_run_python_deny(bash_event):
    """Test that 'uv run python script.py' is denied in favor of 'uv run script.py'."""
    assert_deny(bash_rules_bundle_python_uv, bash_event("uv run python script.py"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("uv run python3 script.py"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("uv run python3.11 script.py"))
    assert_deny(bash_rules_bundle_python_uv, bash_event("uv run python -m module"))
