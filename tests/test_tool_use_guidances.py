"""Test Rego-based guidances for ToolUseEvent and PostFileEditEvent.

Covers all four skill pairs from agent-skills:
- python-common + python-devleaps (triggered by python/uv/pip/pytest/ruff/mypy/black)
- python-fastapi-common + python-fastapi-devleaps (triggered by uvicorn/fastapi)
- python-streamlit-common + python-streamlit-devleaps (triggered by streamlit)
- readme-common + readme-devleaps (triggered by README.md file edits)
"""

import pytest
from src.server.models import PolicyGuidance
from src.server.session import get_flag, clear_flags, initialize_flags_storage
from src.server.executor import execute_handlers_generic


@pytest.fixture(autouse=True)
def setup_session():
    """Initialize flags storage and clear session before each test."""
    initialize_flags_storage()
    yield
    clear_flags("test-session")


# --- Python skill (python-common + python-devleaps) ---

def test_uv_triggers_python_skill(bash_event):
    """Test that uv triggers python skill activation."""
    event = bash_event("uv sync", bundles=["universal", "python_uv", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    python_guidances = [g for g in guidances if "python-common" in g.content]
    assert len(python_guidances) == 1


def test_pytest_triggers_python_skill(bash_event):
    """Test that pytest triggers python skill activation."""
    event = bash_event("pytest tests/", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    python_guidances = [g for g in guidances if "python-common" in g.content]
    assert len(python_guidances) == 1


def test_ruff_triggers_python_skill(bash_event):
    """Test that ruff triggers python skill activation."""
    event = bash_event("ruff check .", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    python_guidances = [g for g in guidances if "python-common" in g.content]
    assert len(python_guidances) == 1


def test_python_skill_cooldown(bash_event):
    """Test that python skill guidance is suppressed after cooldown."""
    event1 = bash_event("uv sync", bundles=["universal", "python_uv", "devleaps"])
    list(execute_handlers_generic(event1))
    assert get_flag("test-session", "skill_python_activated") is True

    # Second call - should not emit python guidance
    event2 = bash_event("pytest tests/", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event2))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    python_guidances = [g for g in guidances if "python-common" in g.content]
    assert len(python_guidances) == 0


# --- FastAPI skill (python-fastapi-common + python-fastapi-devleaps) ---

def test_uvicorn_triggers_fastapi_skill(bash_event):
    """Test that uvicorn triggers FastAPI skill activation."""
    event = bash_event("uvicorn main:app", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    fastapi_guidances = [g for g in guidances if "python-fastapi-common" in g.content]
    assert len(fastapi_guidances) == 1


def test_uv_run_uvicorn_triggers_fastapi_skill(bash_event):
    """Test that uv run uvicorn triggers FastAPI skill activation."""
    event = bash_event("uv run uvicorn main:app", bundles=["universal", "python_uv", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    fastapi_guidances = [g for g in guidances if "python-fastapi-common" in g.content]
    assert len(fastapi_guidances) == 1


def test_uv_run_fastapi_triggers_fastapi_skill(bash_event):
    """Test that uv run fastapi triggers FastAPI skill activation."""
    event = bash_event("uv run fastapi dev", bundles=["universal", "python_uv", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    fastapi_guidances = [g for g in guidances if "python-fastapi-common" in g.content]
    assert len(fastapi_guidances) == 1


def test_fastapi_skill_cooldown(bash_event):
    """Test that FastAPI skill guidance is suppressed after cooldown."""
    event1 = bash_event("uvicorn main:app", bundles=["universal", "devleaps"])
    list(execute_handlers_generic(event1))
    assert get_flag("test-session", "skill_python_fastapi_activated") is True

    event2 = bash_event("uvicorn main:app --reload", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event2))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    fastapi_guidances = [g for g in guidances if "python-fastapi-common" in g.content]
    assert len(fastapi_guidances) == 0


def test_uvicorn_also_triggers_python_skill(bash_event):
    """Test that uvicorn also triggers the base python skill (not just FastAPI)."""
    event = bash_event("uvicorn main:app", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    # Should NOT trigger python skill - uvicorn is not in python_executables set
    python_guidances = [g for g in guidances if "python-common" in g.content]
    assert len(python_guidances) == 0

    # Should trigger fastapi skill
    fastapi_guidances = [g for g in guidances if "python-fastapi-common" in g.content]
    assert len(fastapi_guidances) == 1


# --- Streamlit skill (python-streamlit-common + python-streamlit-devleaps) ---

def test_streamlit_triggers_streamlit_skill(bash_event):
    """Test that streamlit triggers Streamlit skill activation."""
    event = bash_event("streamlit run app.py", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    streamlit_guidances = [g for g in guidances if "python-streamlit-common" in g.content]
    assert len(streamlit_guidances) == 1


def test_uv_run_streamlit_triggers_streamlit_skill(bash_event):
    """Test that uv run streamlit triggers Streamlit skill activation."""
    event = bash_event("uv run streamlit run app.py", bundles=["universal", "python_uv", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    streamlit_guidances = [g for g in guidances if "python-streamlit-common" in g.content]
    assert len(streamlit_guidances) == 1


def test_streamlit_skill_cooldown(bash_event):
    """Test that Streamlit skill guidance is suppressed after cooldown."""
    event1 = bash_event("streamlit run app.py", bundles=["universal", "devleaps"])
    list(execute_handlers_generic(event1))
    assert get_flag("test-session", "skill_python_streamlit_activated") is True

    event2 = bash_event("streamlit run app.py", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event2))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    streamlit_guidances = [g for g in guidances if "python-streamlit-common" in g.content]
    assert len(streamlit_guidances) == 0


# --- README skill (readme-common + readme-devleaps) ---

def test_readme_edit_yields_guidance(file_edit_event):
    """Test that a PostFileEditEvent for README.md yields a guidance."""
    event = file_edit_event("README.md", ["# Title"], bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    readme_guidances = [g for g in guidances if "readme-common" in g.content.lower()]
    assert len(readme_guidances) == 1


def test_readme_guidance_sets_cooldown_flag(file_edit_event):
    """Test that README guidance sets the cooldown flag."""
    event = file_edit_event("README.md", ["# Title"], bundles=["universal", "devleaps"])
    list(execute_handlers_generic(event))

    assert get_flag("test-session", "skill_readme_activated") is True


def test_readme_guidance_suppressed_after_cooldown(file_edit_event):
    """Test that README guidance is not emitted on second evaluation."""
    event1 = file_edit_event("README.md", ["# Title"], bundles=["universal", "devleaps"])
    list(execute_handlers_generic(event1))

    event2 = file_edit_event("README.md", ["# Updated title"], bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event2))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    readme_guidances = [g for g in guidances if "readme-common" in g.content.lower()]
    assert len(readme_guidances) == 0


# --- Negative cases ---

def test_non_python_command_yields_no_guidances(bash_event):
    """Test that non-Python commands don't trigger any devleaps guidances."""
    event = bash_event("ls", bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    assert len(guidances) == 0


def test_non_readme_edit_yields_no_readme_guidance(file_edit_event):
    """Test that non-README file edits don't trigger README guidance."""
    event = file_edit_event("test.txt", ["some content"], bundles=["universal", "devleaps"])
    results = list(execute_handlers_generic(event))

    guidances = [r for r in results if isinstance(r, PolicyGuidance)]
    readme_guidances = [g for g in guidances if "readme" in g.content.lower()]
    assert len(readme_guidances) == 0
