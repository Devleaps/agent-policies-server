"""
HTTP Integration Tests for Python Package Managers

Tests uv and pip policies through the FastAPI HTTP endpoint
using real Claude Code event payloads.
"""

from tests.http.conftest import check_policy


# ============================================================================
# UV Commands (without python_uv bundle)
# ============================================================================

def test_uv_sync_without_bundle_ask(client, base_event):
    """uv sync without python_uv bundle should ask"""
    base_event["bundles"] = ["universal"]
    check_policy(client, base_event, "uv sync", "ask")


def test_uv_add_without_bundle_ask(client, base_event):
    """uv add without python_uv bundle should ask"""
    base_event["bundles"] = ["universal"]
    check_policy(client, base_event, "uv add requests", "ask")


# ============================================================================
# UV Commands (with python_uv bundle)
# ============================================================================

def test_uv_sync_with_bundle_allowed(client, base_event):
    """uv sync with python_uv bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv sync", "allow")


def test_uv_add_with_bundle_allowed(client, base_event):
    """uv add with python_uv bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv add fastapi", "allow")


def test_uv_remove_with_bundle_allowed(client, base_event):
    """uv remove with python_uv bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv remove old-package", "allow")


def test_uv_pip_install_denied(client, base_event):
    """uv pip install is denied (use uv add instead)"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv pip install pytest", "deny")


def test_uv_run_python_denied(client, base_event):
    """uv run python is denied (redundant, use uv run directly)"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv run python script.py", "deny")


def test_uv_run_pytest_with_bundle_allowed(client, base_event):
    """uv run pytest with python_uv bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv run pytest", "allow")


def test_uv_run_pytest_absolute_path_denied(client, base_event):
    """uv run pytest with absolute path should be denied"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv run pytest /tmp/test.py", "deny")


# ============================================================================
# Pip Commands (with python_pip bundle)
# ============================================================================

def test_pip_install_requests_with_bundle_allowed(client, base_event):
    """pip install requests with python_pip bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "pip install requests", "allow")


def test_pip_install_pytest_with_bundle_allowed(client, base_event):
    """pip install pytest with python_pip bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "pip install pytest", "allow")


def test_pip_install_requirements_with_bundle_allowed(client, base_event):
    """pip install -r requirements.txt with python_pip bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "pip install -r requirements.txt", "allow")


def test_pip_install_mature_package_allowed(client, base_event):
    """pip install mature package should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    # Mature packages (> N days old) should be allowed
    check_policy(client, base_event, "pip install requests", "allow")


# ============================================================================
# Python Quality Tools (with python_pip bundle)
# ============================================================================

def test_black_with_bundle_allowed(client, base_event):
    """black with python_pip bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "black .", "allow")


def test_ruff_with_bundle_allowed(client, base_event):
    """ruff with python_pip bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "ruff check .", "allow")


def test_mypy_with_bundle_allowed(client, base_event):
    """mypy with python_pip bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "mypy src/", "allow")


def test_pytest_with_pip_bundle_allowed(client, base_event):
    """pytest with python_pip bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "pytest tests/", "allow")


# ============================================================================
# Combined Bundles
# ============================================================================

def test_uv_pytest_with_both_bundles_allowed(client, base_event):
    """uv run pytest with both bundles should be allowed"""
    base_event["bundles"] = ["universal", "python_uv", "python_pip"]
    check_policy(client, base_event, "uv run pytest", "allow")


# ============================================================================
# Piped Commands
# ============================================================================

def test_pytest_piped_head_allowed(client, base_event):
    """pytest | head should be allowed"""
    base_event["bundles"] = ["universal", "python_pip"]
    check_policy(client, base_event, "pytest | head", "allow")


def test_uv_pytest_piped_head_with_bundle_allowed(client, base_event):
    """uv run pytest | head with python_uv bundle should be allowed"""
    base_event["bundles"] = ["universal", "python_uv"]
    check_policy(client, base_event, "uv run pytest | head", "allow")
