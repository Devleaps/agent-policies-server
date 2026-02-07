"""Tests for Vale CLI policies."""


# --- Help and version ---


def test_vale_version_allowed(bash_event):
    """Test that vale --version is allowed."""
    event = bash_event("vale --version")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_help_allowed(bash_event):
    """Test that vale --help is allowed."""
    event = bash_event("vale --help")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


# --- Inspection commands ---


def test_vale_ls_config_allowed(bash_event):
    """Test that vale ls-config is allowed."""
    event = bash_event("vale ls-config")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_ls_dirs_allowed(bash_event):
    """Test that vale ls-dirs is allowed."""
    event = bash_event("vale ls-dirs")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_ls_vars_allowed(bash_event):
    """Test that vale ls-vars is allowed."""
    event = bash_event("vale ls-vars")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_ls_metrics_with_file_allowed(bash_event):
    """Test that vale ls-metrics with a file is allowed."""
    event = bash_event("vale ls-metrics README.md")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


# --- Sync command ---


def test_vale_sync_allowed(bash_event):
    """Test that vale sync is allowed."""
    event = bash_event("vale sync")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


# --- Linting operations ---


def test_vale_single_file_allowed(bash_event):
    """Test that vale with a single file is allowed."""
    event = bash_event("vale README.md")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_multiple_files_allowed(bash_event):
    """Test that vale with multiple files is allowed."""
    event = bash_event("vale README.md CONTRIBUTING.md docs/guide.md")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_directory_allowed(bash_event):
    """Test that vale with a directory is allowed."""
    event = bash_event("vale docs/")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_with_output_json_allowed(bash_event):
    """Test that vale --output=JSON is allowed."""
    event = bash_event("vale --output=JSON README.md")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_with_glob_allowed(bash_event):
    """Test that vale --glob is allowed."""
    event = bash_event("vale --glob='*.md' .")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_with_config_allowed(bash_event):
    """Test that vale --config is allowed."""
    event = bash_event("vale --config=.vale.ini README.md")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


def test_vale_with_no_global_allowed(bash_event):
    """Test that vale --no-global is allowed."""
    event = bash_event("vale --no-global README.md")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "allow" for d in decisions)


# --- Path safety ---


def test_vale_absolute_path_denied(bash_event):
    """Test that vale with absolute path is denied."""
    event = bash_event("vale /etc/passwd")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "deny" for d in decisions)


def test_vale_path_traversal_denied(bash_event):
    """Test that vale with path traversal is denied."""
    event = bash_event("vale ../../../etc/passwd")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "deny" for d in decisions)


def test_vale_ls_metrics_absolute_path_denied(bash_event):
    """Test that vale ls-metrics with absolute path is denied."""
    event = bash_event("vale ls-metrics /etc/passwd")
    from src.server.executor import execute_handlers_generic

    results = list(execute_handlers_generic(event))
    decisions = [r for r in results if hasattr(r, "action")]
    assert any(d.action == "deny" for d in decisions)
