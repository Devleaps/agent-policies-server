"""
HTTP Integration Tests: cd is allowed anywhere, and later commands in the
chain are checked from the cd target.
"""

import pytest

from tests.http.conftest import check_policy


def _event(base_event, cwd="/workspace/repo", workspace_root="/workspace"):
    base_event["workspace_root"] = workspace_root
    base_event["home"] = "/home/user"
    base_event["event"]["cwd"] = cwd
    return base_event


@pytest.mark.parametrize(
    "command",
    [
        "cd ../other",
        "cd /etc",
        "cd ~",
        "cd",
        "cd -",
        "cd $SOMEWHERE",
        "cd ../../other-client/some-repo",
    ],
)
def test_cd_alone_allowed(client, base_event, command):
    check_policy(client, _event(base_event), command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "cd ../other && cat README.md",
        "cd .. && cd repo && cat README.md",
        "cd /tmp && cd /workspace && cat README.md",
        "cd /etc && cat /workspace/repo/README.md",
        "cd /etc && cat ../workspace/repo/README.md",
        "cd sub && git status",
    ],
)
def test_chain_after_cd_inside_workspace_allowed(client, base_event, command):
    check_policy(client, _event(base_event), command, "allow")


def test_to_do_file_example_allowed(client, base_event):
    """cd ../../other-client/... from a repo two levels below the workspace root."""
    event = _event(base_event, cwd="/workspace/Devleaps/agent-policies-server")
    check_policy(client, event, "cd ../../other-client/some-repo && ls src", "allow")


@pytest.mark.parametrize(
    "command",
    [
        "cd ../../.. && cat .ssh/id_rsa",
        "cd /etc && cat passwd",
        "cd ~ && cat .ssh/id_rsa",
        "cd && cat .ssh/id_rsa",
        "cd $HOME && cat .aws/credentials",
        "cd - && cat secrets.txt",
        "cd /etc; cat passwd",
        "cd /etc && echo x > hosts",
    ],
)
def test_chain_after_cd_outside_workspace_denied(client, base_event, command):
    check_policy(client, _event(base_event), command, "deny")


def test_pipe_does_not_move_location(client, base_event):
    """cd in a pipeline runs in a subshell; the pipe's own paths are checked
    from the original directory."""
    check_policy(client, _event(base_event), "cat README.md | grep foo", "allow")


def test_event_cwd_outside_workspace_denies_relative_paths(client, base_event):
    check_policy(client, _event(base_event, cwd="/etc"), "cat passwd", "deny")


@pytest.mark.parametrize(
    "command, expected",
    [
        ("cd sub && cat README.md", "allow"),
        ("cd .. && cat secrets.txt", "deny"),
        ("cd /etc && cat passwd", "deny"),
        ("cd ~ && cat .ssh/id_rsa", "deny"),
    ],
)
def test_without_workspace_root_only_plain_descent_stays_inside(
    client, base_event, command, expected
):
    event = _event(base_event, workspace_root=None)
    check_policy(client, event, command, expected)
