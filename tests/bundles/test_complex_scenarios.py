"""Complex integration tests for bash parser with policy rules."""

import pytest
from src.evaluation import evaluate_bash_rules
from tests.helpers import assert_allow, assert_deny, assert_pass, assert_ask


def test_git_commit_with_complex_message(bash_event):
    """Test git commit with complex quoted messages containing special characters."""
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "Fix bug: handle edge case with \\"quotes\\""'))
    assert_allow(evaluate_bash_rules, bash_event("git commit -m 'Add feature: support $VAR expansion'"))
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "Update docs (closes #123)"'))
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "Refactor: split large function into smaller ones"'))


def test_git_commit_with_multiple_flags(bash_event):
    """Test git commit with multiple flags and options combined."""
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "message" --no-verify'))
    assert_allow(evaluate_bash_rules, bash_event('git commit --amend -m "updated message" --no-edit'))
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "fix" --author="John Doe <john@example.com>"'))


def test_git_add_with_multiple_paths(bash_event):
    """Test git add with multiple paths and wildcards."""
    assert_allow(evaluate_bash_rules, bash_event("git add file1.txt file2.txt file3.txt"))
    assert_allow(evaluate_bash_rules, bash_event("git add src/*.py"))
    assert_allow(evaluate_bash_rules, bash_event("git add src/components/*.tsx src/utils/*.ts"))
    assert_allow(evaluate_bash_rules, bash_event('git add "path with spaces/file.txt"'))


def test_git_mv_with_quoted_paths(bash_event):
    """Test git mv with paths containing spaces."""
    assert_allow(evaluate_bash_rules, bash_event('git mv "old name.txt" "new name.txt"'))
    assert_allow(evaluate_bash_rules, bash_event('git mv src/old\\ file.py src/new\\ file.py'))
    assert_deny(evaluate_bash_rules, bash_event('git mv /tmp/file.txt local.txt'))


def test_sleep_with_various_formats(bash_event):
    """Test sleep command with different time formats."""
    assert_allow(evaluate_bash_rules, bash_event("sleep 5"))
    assert_allow(evaluate_bash_rules, bash_event("sleep 60"))
    assert_deny(evaluate_bash_rules, bash_event("sleep 61"))
    assert_deny(evaluate_bash_rules, bash_event("sleep 999"))


def test_sqlite3_with_complex_queries(bash_event):
    """Test sqlite3 with complex SQL queries."""
    assert_allow(evaluate_bash_rules, bash_event(
        'sqlite3 test.db "SELECT u.id, u.name, COUNT(o.id) FROM users u LEFT JOIN orders o ON u.id = o.user_id GROUP BY u.id"'
    ))
    assert_allow(evaluate_bash_rules, bash_event(
        "sqlite3 test.db 'SELECT * FROM users WHERE email LIKE \"%@example.com\" ORDER BY created_at DESC LIMIT 10'"
    ))
    assert_deny(evaluate_bash_rules, bash_event(
        'sqlite3 test.db "DELETE FROM users WHERE created_at < datetime(\\"now\\", \\"-1 year\\")"'
    ))


def test_docker_build_with_multiple_options(bash_event):
    """Test docker build with multiple flags and options."""
    assert_allow(evaluate_bash_rules, bash_event("docker build -t myapp:latest --no-cache ."))
    assert_allow(evaluate_bash_rules, bash_event('docker build -t app:1.0 -f Dockerfile.prod --build-arg VERSION=1.0 .'))
    assert_allow(evaluate_bash_rules, bash_event("docker build --tag myapp:dev --target development ."))
    assert_deny(evaluate_bash_rules, bash_event("docker build -t app /absolute/path"))


def test_uv_add_multiple_packages(bash_event):
    """Test uv add with multiple packages in single command."""
    assert_allow(evaluate_bash_rules, bash_event("uv add requests httpx", bundles=["universal", "python_uv"]))
    assert_allow(evaluate_bash_rules, bash_event("uv add fastapi uvicorn pydantic", bundles=["universal", "python_uv"]))


def test_python_module_with_complex_args(bash_event):
    """Test python -m with complex module arguments."""
    assert_deny(evaluate_bash_rules, bash_event("python -m pytest tests/", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("python -m pytest -v -s tests/test_integration.py", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event('python -m pytest --maxfail=1 -k "test_user"', bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("python3 -m http.server 8000", bundles=["universal", "python_uv"]))


def test_pytest_with_various_options(bash_event):
    """Test pytest with different flag and option combinations."""
    assert_deny(evaluate_bash_rules, bash_event("pytest", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("pytest -v", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("pytest tests/", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("pytest -v -s --maxfail=1 tests/", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event('pytest -k "test_user" tests/test_auth.py', bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("pytest --cov=src --cov-report=html tests/", bundles=["universal", "python_uv"]))


def test_commands_with_special_characters(bash_event):
    """Test commands with special characters in arguments."""
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "feat(api): add new endpoint"'))
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "fix: resolve issue #123 & #124"'))
    assert_allow(evaluate_bash_rules, bash_event("git add src/**/*.{ts,tsx}"))


def test_commands_with_environment_variables(bash_event):
    """Test commands that reference environment variables."""
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "Deploy to $ENVIRONMENT"'))
    assert_ask(evaluate_bash_rules, bash_event("export DEBUG=1"))


def test_commands_with_redirects_and_pipes(bash_event):
    """Test that redirects are properly parsed."""
    pass


def test_edge_case_empty_and_whitespace(bash_event):
    """Test edge cases with whitespace."""
    assert_allow(evaluate_bash_rules, bash_event('  git commit -m "message"  '))


def test_subcommand_with_options_before_and_after(bash_event):
    """Test commands with options both before and after subcommand."""
    assert_allow(evaluate_bash_rules, bash_event('git -C /repo commit -m "message"'))
    assert_allow(evaluate_bash_rules, bash_event("git -C src add file.txt"))


def test_numeric_arguments(bash_event):
    """Test commands with numeric arguments."""
    assert_allow(evaluate_bash_rules, bash_event("sleep 5"))
    assert_allow(evaluate_bash_rules, bash_event("sleep 30"))
    assert_deny(evaluate_bash_rules, bash_event("sleep 999"))


def test_boolean_flags_vs_options(bash_event):
    """Test distinction between boolean flags and options."""
    assert_allow(evaluate_bash_rules, bash_event("git commit --amend"))
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "msg" --no-verify'))
    assert_deny(evaluate_bash_rules, bash_event("git commit -a"))


def test_quoted_vs_unquoted_arguments(bash_event):
    """Test that quoted and unquoted arguments are handled correctly."""
    assert_allow(evaluate_bash_rules, bash_event('git commit -m message'))
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "message with spaces"'))
    assert_allow(evaluate_bash_rules, bash_event("git add file.txt"))
    assert_allow(evaluate_bash_rules, bash_event('git add "file with spaces.txt"'))


def test_commands_with_glob_patterns(bash_event):
    """Test commands with glob patterns."""
    assert_allow(evaluate_bash_rules, bash_event("git add *.py"))
    assert_allow(evaluate_bash_rules, bash_event("git add src/**/*.ts"))
    assert_allow(evaluate_bash_rules, bash_event("git add tests/test_*.py"))


def test_commands_with_escaped_characters(bash_event):
    """Test commands with escaped characters."""
    assert_allow(evaluate_bash_rules, bash_event('git add file\\ with\\ spaces.txt'))
    assert_allow(evaluate_bash_rules, bash_event('git commit -m "Add \\$VARIABLE support"'))


def test_long_complex_command(bash_event):
    """Test a very long complex command."""
    assert_allow(evaluate_bash_rules, bash_event(
        'git commit -m "feat(auth): implement OAuth2 authentication flow with PKCE" '
        '--author="Developer <dev@example.com>" --no-verify'
    ))


def test_commands_with_multiple_short_flags_combined(bash_event):
    """Test commands with combined short flags like -vvv or -la."""
    # Parser should handle these, though specific rule behavior may vary
    assert_deny(evaluate_bash_rules, bash_event("pytest -vvv", bundles=["universal", "python_uv"]))
    assert_deny(evaluate_bash_rules, bash_event("pytest -vsx", bundles=["universal", "python_uv"]))


def test_sqlite3_queries_with_semicolons(bash_event):
    """Test sqlite3 with multiple statements separated by semicolons."""
    assert_allow(evaluate_bash_rules, bash_event(
        'sqlite3 test.db "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM orders;"'
    ))
    assert_deny(evaluate_bash_rules, bash_event(
        'sqlite3 test.db "SELECT * FROM users; DELETE FROM sessions;"'
    ))


def test_commands_with_equals_in_options(bash_event):
    """Test commands with options using = syntax."""
    assert_allow(evaluate_bash_rules, bash_event("docker build --tag=myapp:latest ."))
    assert_deny(evaluate_bash_rules, bash_event("pytest --maxfail=1 tests/", bundles=["universal", "python_uv"]))


def test_chained_cd_rmdir_with_stderr_redirect_and_fallback(bash_event):
    """Test cd && rmdir with stderr redirect and || true fallback."""
    assert_allow(evaluate_bash_rules, bash_event(
        "cd project-dir && rmdir dir1 dir2 dir3 2>/dev/null || true"
    ))


def test_chained_safe_commands_allowed(bash_event):
    """Test that chained safe commands are allowed."""
    assert_allow(evaluate_bash_rules, bash_event("cd .. && ls"))
    assert_allow(evaluate_bash_rules, bash_event("git status && git diff"))
    assert_allow(evaluate_bash_rules, bash_event("cd src && cat file.txt && cd .."))


def test_chained_dangerous_commands_blocked(bash_event):
    """Test that dangerous commands in chains are blocked (security vulnerability fix)."""
    # timeout is blocked - should be denied even in a chain
    assert_deny(evaluate_bash_rules, bash_event("cd .. && timeout 120 sleep 120"))

    # sudo is blocked - should be denied even when chained after safe command
    assert_deny(evaluate_bash_rules, bash_event("ls && sudo rm -rf /"))

    # kill is blocked - should be denied in chain
    assert_deny(evaluate_bash_rules, bash_event("git status && kill 1234"))

    # xargs is blocked - should be denied in chain
    assert_deny(evaluate_bash_rules, bash_event("cd project && ls | xargs rm"))


def test_chained_timeout_docker_build_blocked(bash_event):
    """Test the specific vulnerability case: cd .. && timeout docker build."""
    assert_deny(evaluate_bash_rules, bash_event(
        "cd .. && cd agent-internal-policies && timeout 120 docker build -t app:latest . 2>&1 | tail"
    ))


def test_piped_dangerous_commands_blocked(bash_event):
    """Test that dangerous commands in pipes are also evaluated."""
    # xargs is blocked - should be denied in pipe
    assert_deny(evaluate_bash_rules, bash_event("ls | xargs rm"))

    # awk is blocked - should be denied in pipe
    assert_deny(evaluate_bash_rules, bash_event("cat file.txt | awk '{print $1}'"))


def test_safe_pipes_allowed(bash_event):
    """Test that safe piped commands are allowed."""
    assert_allow(evaluate_bash_rules, bash_event("cat file.txt | head -10"))
    assert_allow(evaluate_bash_rules, bash_event("git log | grep 'fix'"))
    assert_allow(evaluate_bash_rules, bash_event("ls -la | tail -20"))
