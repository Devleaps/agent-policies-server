import pytest
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny, assert_pass, assert_ask


def test_uv_add(bash_event):
    assert_allow(evaluate_bash_rules, bash_event("uv add requests", bundles=["universal", "python_uv"]))
    assert_allow(evaluate_bash_rules, bash_event("uv add httpx", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv add this-package-definitely-does-not-exist-12345", bundles=["universal", "python_uv"]))


def test_uv_pip_install(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("uv pip install requests", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv pip install requests==2.28.0", bundles=["universal", "python_uv"]))
    assert_ask(evaluate_bash_rules, bash_event("uv pip list", bundles=["universal", "python_uv"]))


def test_uv_python(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("python script.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("python -m pytest", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("python3 -m mymodule", bundles=["universal", "python_uv"]))
    assert_ask(evaluate_bash_rules, bash_event("python scripts/something.py", bundles=["universal", "python_uv"]))


def test_pytest_uv_requirement(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("pytest tests/", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("pytest -v tests/test_something.py", bundles=["universal", "python_uv"]))
    assert_allow(evaluate_bash_rules, bash_event("uv run pytest tests/", bundles=["universal", "python_uv"]))
    assert_allow(evaluate_bash_rules, bash_event("uv run pytest -v tests/", bundles=["universal", "python_uv"]))


def test_uv_run_python_c_deny(bash_event):
    assert_deny(evaluate_bash_rules, bash_event('uv run python -c "print(123)"', bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event('uv run python -c "import os; os.system(\'echo 123\')"', bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event('uv run python3 -c "import sys"', bundles=["universal", "python_uv"]))


def test_uv_run_python_deny(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("uv run python script.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run python3 script.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run python3.11 script.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run python -m module", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run python -m pytest", bundles=["universal", "python_uv"]))


def test_uv_run_test_files_deny(bash_event):
    assert_deny(evaluate_bash_rules, bash_event("uv run test_something.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run test_auth.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run tests/test_api.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run unit_test.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("uv run integration_test.py", bundles=["universal", "python_uv"]))
    assert_ask(evaluate_bash_rules, bash_event("uv run script.py", bundles=["universal", "python_uv"]))
    assert_ask(evaluate_bash_rules, bash_event("uv run migrate.py", bundles=["universal", "python_uv"]))
    assert_ask(evaluate_bash_rules, bash_event("uv run some-command", bundles=["universal", "python_uv"]))
