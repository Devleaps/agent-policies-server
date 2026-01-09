import pytest
from src.python_uv.uv_add_validate import uv_add_validate_rule, is_package_allowed
from src.python_uv.uv_pip_install_guidance import uv_pip_install_deny_rule
from src.python_uv.uv_python_deny import uv_python_direct_deny_rule, uv_python_run_escape_deny_rule
from src.python_uv.uv_tools_allow import uv_tools_run_allow_rule
from src.python_uv.uv_tools_deny import uv_tools_direct_deny_rule
from tests.helpers import assert_allow, assert_deny, assert_pass, assert_ask, eval_rule


def test_uv_add(bash_event):
    assert_allow(uv_add_validate_rule, bash_event("uv add requests"))
    assert_allow(uv_add_validate_rule, bash_event("uv add httpx"))
    assert_deny(uv_add_validate_rule, bash_event("uv add this-package-definitely-does-not-exist-12345"), "not found")


def test_uv_add_direct():
    allowed, reason = is_package_allowed("requests")
    assert allowed is True
    assert "year" in reason.lower()

    allowed, reason = is_package_allowed("this-does-not-exist-12345")
    assert allowed is False
    assert "not found" in reason.lower() or "failed" in reason.lower()


def test_uv_pip_install(bash_event):
    assert_deny(uv_pip_install_deny_rule, bash_event("uv pip install requests"), "uv add")
    assert_deny(uv_pip_install_deny_rule, bash_event("uv pip install requests==2.28.0"))
    assert_pass(uv_pip_install_deny_rule, bash_event("uv pip list"))


def test_uv_python(bash_event):
    assert_deny(uv_python_direct_deny_rule, bash_event("python script.py"), "uv run script.py")
    assert_deny(uv_python_direct_deny_rule, bash_event("python -m pytest"), "uv run pytest")
    assert_deny(uv_python_direct_deny_rule, bash_event("python3 -m mymodule"), "uv run mymodule")
    assert_ask(uv_python_direct_deny_rule, bash_event("python scripts/something.py"))

    results = eval_rule(uv_python_run_escape_deny_rule, bash_event("uv run python script.py"))
    assert len(results) == 1
    assert results[0].action == "deny"
    assert "pytest" in results[0].reason or "scripts/" in results[0].reason


def test_pytest_uv_requirement(bash_event):
    assert_deny(uv_tools_direct_deny_rule, bash_event("pytest tests/"), "uv run pytest")
    assert_deny(uv_tools_direct_deny_rule, bash_event("pytest -v tests/test_something.py"))
    assert_allow(uv_tools_run_allow_rule, bash_event("uv run pytest tests/"))
    assert_allow(uv_tools_run_allow_rule, bash_event("uv run pytest -v tests/"))
