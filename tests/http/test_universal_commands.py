"""
HTTP Integration Tests for Universal Commands

Tests common system commands (pwd, ps, ls, cat, etc.) and file operations
through the FastAPI HTTP endpoint using real Claude Code event payloads.
"""

from tests.http.conftest import check_policy

# ============================================================================
# Always Allowed Commands
# ============================================================================


def test_pwd_allowed(client, base_event):
    """pwd should be allowed"""
    check_policy(client, base_event, "pwd", "allow")


def test_ps_allowed(client, base_event):
    """ps should be allowed"""
    check_policy(client, base_event, "ps aux", "allow")


def test_which_allowed(client, base_event):
    """which should be allowed"""
    check_policy(client, base_event, "which python", "allow")


def test_ls_relative_path_allowed(client, base_event):
    """ls with relative path should be allowed"""
    check_policy(client, base_event, "ls src/", "allow")


def test_cat_relative_path_allowed(client, base_event):
    """cat with relative path should be allowed"""
    check_policy(client, base_event, "cat README.md", "allow")


def test_head_allowed(client, base_event):
    """head should be allowed"""
    check_policy(client, base_event, "head -n 10 file.txt", "allow")


def test_head_unsafe_argument_with_safe_option_denied(client, base_event):
    """head with an unsafe positional path must be denied even when its
    option values (e.g. -n 10) are safe on their own — all_args_and_options_safe
    must require both sides to be safe, not just one."""
    check_policy(client, base_event, "head -n 10 /tmp/secret", "deny")


def test_tail_allowed(client, base_event):
    """tail should be allowed"""
    check_policy(client, base_event, "tail -f log.txt", "allow")


def test_grep_allowed(client, base_event):
    """grep should be allowed"""
    check_policy(client, base_event, "grep pattern file.txt", "allow")


def test_find_allowed(client, base_event):
    """find should be allowed"""
    check_policy(client, base_event, "find . -name '*.py'", "allow")


def test_tree_allowed(client, base_event):
    """tree should be allowed"""
    check_policy(client, base_event, "tree src/", "allow")


def test_wc_allowed(client, base_event):
    """wc should be allowed"""
    check_policy(client, base_event, "wc -l file.txt", "allow")


def test_diff_allowed(client, base_event):
    """diff should be allowed"""
    check_policy(client, base_event, "diff file1.txt file2.txt", "allow")


def test_sort_allowed(client, base_event):
    """sort should be allowed"""
    check_policy(client, base_event, "sort file.txt", "allow")


def test_cut_allowed(client, base_event):
    """cut should be allowed"""
    check_policy(client, base_event, "cut -d',' -f1 data.csv", "allow")


def test_test_command_allowed(client, base_event):
    """test command should be allowed"""
    check_policy(client, base_event, "test -f file.txt", "allow")


def test_bracket_command_allowed(client, base_event):
    """[ ] command should be allowed"""
    check_policy(client, base_event, "[ -f file.txt ]", "allow")


# ============================================================================
# File Operations
# ============================================================================


def test_mkdir_relative_allowed(client, base_event):
    """mkdir with relative path should be allowed"""
    check_policy(client, base_event, "mkdir new-dir", "allow")


def test_cp_relative_allowed(client, base_event):
    """cp with relative paths should be allowed"""
    check_policy(client, base_event, "cp file.txt backup.txt", "allow")


def test_mv_relative_allowed(client, base_event):
    """mv with relative paths should be allowed"""
    check_policy(client, base_event, "mv old.txt new.txt", "allow")


def test_mv_to_subdir_allowed(client, base_event):
    """mv to subdirectory should be allowed"""
    check_policy(client, base_event, "mv file.txt subdir/", "allow")


def test_touch_relative_allowed(client, base_event):
    """touch with relative path should be allowed"""
    check_policy(client, base_event, "touch newfile.txt", "allow")


def test_trash_relative_allowed(client, base_event):
    """trash with relative path should be allowed"""
    check_policy(client, base_event, "trash oldfile.txt", "allow")


def test_chmod_relative_allowed(client, base_event):
    """chmod with relative path should be allowed"""
    check_policy(client, base_event, "chmod +x script.sh", "allow")


def test_du_allowed(client, base_event):
    """du should be allowed"""
    check_policy(client, base_event, "du -sh src/", "allow")


# ============================================================================
# Path Traversal - DENY
# ============================================================================


def test_ls_absolute_path_denied(client, base_event):
    """ls with absolute path should be denied"""
    check_policy(client, base_event, "ls /etc", "deny")


def test_cat_path_traversal_denied(client, base_event):
    """cat with path traversal should be denied"""
    check_policy(client, base_event, "cat ../../etc/passwd", "deny")


def test_chmod_absolute_path_denied(client, base_event):
    """chmod with absolute path should be denied"""
    check_policy(client, base_event, "chmod 777 /usr/bin/sudo", "deny")


def test_chmod_path_traversal_denied(client, base_event):
    """chmod with path traversal should be denied"""
    check_policy(client, base_event, "chmod +x ../../../script.sh", "deny")


def test_touch_absolute_path_denied(client, base_event):
    """touch with absolute path should be denied"""
    check_policy(client, base_event, "touch /tmp/newfile", "deny")


def test_trash_absolute_path_denied(client, base_event):
    """trash with absolute path should be denied"""
    check_policy(client, base_event, "trash /home/user/file.txt", "deny")


def test_ls_tilde_home_denied(client, base_event):
    """ls with tilde home path should be denied when no client home is known"""
    check_policy(client, base_event, "ls ~/", "deny")


def test_ls_tilde_subdir_denied(client, base_event):
    """ls ~/.ssh/ should be denied — tilde paths escape the workspace"""
    check_policy(client, base_event, "ls ~/.ssh/", "deny")


def test_ls_tilde_flags_denied(client, base_event):
    """ls -la ~/.ssh/ should be denied"""
    check_policy(client, base_event, "ls -la ~/.ssh/", "deny")


def test_ls_absolute_option_value_inside_workspace_allowed(client, base_event):
    """ls -la /workspace/subdir should be allowed — the option value is an
    absolute path, but it resolves to a workspace-relative path just like a
    positional argument would, and must not be denied outright."""
    check_policy(client, base_event, "ls -la /workspace/subdir", "allow")


def test_ls_tilde_option_value_inside_workspace_allowed_with_client_home(client, base_event):
    """ls -la ~/subdir should be allowed when the client-supplied home makes
    the option value resolve inside the workspace root."""
    base_event["home"] = "/workspace"
    check_policy(client, base_event, "ls -la ~/subdir", "allow")


def test_cat_tilde_path_denied(client, base_event):
    """cat with tilde path should be denied"""
    check_policy(client, base_event, "cat ~/.bashrc", "deny")


def test_cat_tilde_outside_workspace_denied_with_client_home(client, base_event):
    """~ resolved against the client-supplied home should still be denied
    when it points outside the workspace root."""
    base_event["home"] = "/home/clientuser"
    check_policy(client, base_event, "cat ~/.ssh/id_rsa", "deny")


def test_cat_tilde_inside_workspace_allowed_with_client_home(client, base_event):
    """~ resolved against the client-supplied home should be allowed
    when it points inside the workspace root."""
    base_event["home"] = "/workspace"
    check_policy(client, base_event, "cat ~/README.md", "allow")


def test_cat_tilde_does_not_resolve_against_server_home(client, base_event, monkeypatch):
    """~ must never be resolved against the server process's own home directory.

    Simulates a server whose own $HOME happens to sit under the workspace root
    (e.g. a misconfigured or containerized deployment). Without a client-supplied
    `home`, resolving ~ using the server's home would be a security bug — it must
    stay unresolved and be denied by the raw tilde check instead.
    """
    monkeypatch.setenv("HOME", "/workspace")
    base_event.pop("home", None)
    check_policy(client, base_event, "cat ~/README.md", "deny")


def test_cat_tilde_subdir_workspace_allowed_with_client_home(client, base_event):
    """~ should resolve correctly when the workspace is a subfolder under home,
    e.g. home=/home/user and workspace_root=/home/user/workspace/project."""
    base_event["workspace_root"] = "/home/user/workspace/project"
    base_event["event"]["cwd"] = "/home/user/workspace/project"
    base_event["home"] = "/home/user"
    check_policy(client, base_event, "cat ~/workspace/project/README.md", "allow")


def test_cat_tilde_sibling_of_workspace_denied_with_client_home(client, base_event):
    """~ should still be denied when home and workspace are siblings under the
    same parent, e.g. home=/home/user and workspace_root=/home/workspace —
    home is not a prefix of workspace_root, so escaping via ~ must not be allowed."""
    base_event["workspace_root"] = "/home/workspace"
    base_event["event"]["cwd"] = "/home/workspace"
    base_event["home"] = "/home/user"
    check_policy(client, base_event, "cat ~/secrets.txt", "deny")


# ============================================================================
# Dangerous Commands - DENY
# ============================================================================


def test_rm_rf_denied(client, base_event):
    """rm -rf should be denied"""
    check_policy(client, base_event, "rm -rf directory/", "deny")


def test_sudo_denied(client, base_event):
    """sudo should be denied"""
    check_policy(client, base_event, "sudo apt-get update", "deny")


# ============================================================================
# Redirects
# ============================================================================


def test_redirect_to_tmp_denied(client, base_event):
    """Redirect to /tmp should be denied"""
    check_policy(client, base_event, "echo test > /tmp/file.txt", "deny")


def test_redirect_relative_allowed(client, base_event):
    """Redirect to relative path should be allowed"""
    check_policy(client, base_event, "echo test > output.txt", "allow")


def test_whoami_allowed(client, base_event):
    """whoami should be allowed"""
    check_policy(client, base_event, "whoami", "allow")


def test_df_allowed(client, base_event):
    """df should be allowed"""
    check_policy(client, base_event, "df -h", "allow")


def test_file_safe_path_allowed(client, base_event):
    """file with safe path should be allowed"""
    check_policy(client, base_event, "file ./README.md", "allow")


def test_file_relative_path_allowed(client, base_event):
    """file with relative path should be allowed"""
    check_policy(client, base_event, "file src/main.py", "allow")


def test_file_absolute_path_denied(client, base_event):
    """file with absolute path should be denied"""
    check_policy(client, base_event, "file /etc/passwd", "deny")


def test_file_tmp_denied(client, base_event):
    """file with /tmp path should be denied"""
    check_policy(client, base_event, "file /tmp/test.txt", "deny")


def test_grep_safe_path_allowed(client, base_event):
    """grep with safe paths should be allowed"""
    check_policy(
        client,
        base_event,
        'grep -n "guidance_activations" policies/demo_flags/*.rego',
        "allow",
    )


def test_grep_relative_path_allowed(client, base_event):
    """grep with relative path should be allowed"""
    check_policy(client, base_event, "grep -r 'TODO' src/", "allow")


def test_grep_absolute_path_denied(client, base_event):
    """grep with absolute path should be denied"""
    check_policy(client, base_event, "grep 'pattern' /etc/hosts", "deny")


def test_grep_parent_path_denied(client, base_event):
    """grep with parent path traversal should be denied"""
    check_policy(client, base_event, "grep 'test' ../other-project/file.txt", "deny")


# ============================================================================
# Workspace-Relative Absolute Paths
# The base_event fixture uses cwd=/workspace, so /workspace/... paths are allowed
# when they resolve within the workspace. Paths that escape via .. are denied.
# ============================================================================


def test_cat_workspace_absolute_path_allowed(client, base_event):
    """cat with absolute path inside workspace should be allowed"""
    check_policy(client, base_event, "cat /workspace/src/main.py", "allow")


def test_ls_workspace_absolute_path_allowed(client, base_event):
    """ls with absolute path inside workspace should be allowed"""
    check_policy(client, base_event, "ls /workspace/src/", "allow")


def test_grep_workspace_absolute_path_allowed(client, base_event):
    """grep with absolute path inside workspace should be allowed"""
    check_policy(client, base_event, "grep 'TODO' /workspace/src/main.py", "allow")


def test_cat_workspace_dotdot_resolves_within_allowed(client, base_event):
    """cat with dotdot that resolves within workspace should be allowed"""
    check_policy(client, base_event, "cat /workspace/src/../lib/file.py", "allow")


def test_cat_relative_dotdot_resolves_within_allowed(client, base_event):
    """cat with relative dotdot that resolves within workspace should be allowed"""
    check_policy(client, base_event, "cat src/../lib/file.py", "allow")


def test_cat_absolute_path_outside_workspace_denied(client, base_event):
    """cat with absolute path outside workspace should be denied"""
    check_policy(client, base_event, "cat /etc/passwd", "deny")


def test_ls_workspace_prefix_false_match_denied(client, base_event):
    """ls with path that only shares a string prefix (no slash boundary) should be denied"""
    check_policy(client, base_event, "ls /workspacefoo/bar", "deny")


def test_cat_workspace_traversal_escapes_denied(client, base_event):
    """cat with workspace-rooted path that normalizes outside workspace should be denied"""
    check_policy(client, base_event, "cat /workspace/src/../../etc/passwd", "deny")


# ============================================================================
# CWD-Relative Path Resolution
# cwd is set 2 directories below the workspace root (/workspace/a/b).
# Relative dotdot paths are resolved against cwd, not the workspace root.
# ============================================================================


def test_touch_dotdot_within_workspace_allowed(client, base_event):
    """touch ../../file from cwd 2 dirs deep resolves to workspace level — allowed"""
    base_event["event"]["cwd"] = "/workspace/a/b"
    check_policy(client, base_event, "touch ../../demo.txt", "allow")


def test_cat_dotdot_within_workspace_allowed(client, base_event):
    """cat ../../file from cwd 2 dirs deep resolves within workspace — allowed"""
    base_event["event"]["cwd"] = "/workspace/a/b"
    check_policy(client, base_event, "cat ../../README.md", "allow")


def test_touch_dotdot_escapes_workspace_denied(client, base_event):
    """touch ../../../file from cwd 2 dirs deep resolves outside workspace — denied"""
    base_event["event"]["cwd"] = "/workspace/a/b"
    check_policy(client, base_event, "touch ../../../outside.txt", "deny")


def test_cat_dotdot_escapes_to_system_path_denied(client, base_event):
    """cat ../../../etc/passwd from cwd 2 dirs deep resolves outside workspace — denied"""
    base_event["event"]["cwd"] = "/workspace/a/b"
    check_policy(client, base_event, "cat ../../../etc/passwd", "deny")
