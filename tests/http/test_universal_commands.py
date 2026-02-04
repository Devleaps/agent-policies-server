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
