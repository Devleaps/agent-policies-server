"""Tests for fluent API rule builder."""

import pytest
from devleaps.policies.server.common.models import PolicyAction
from src.core.rule_builder import command
from src.core.matchers import has_flag, has_option
from src.core.predicates import safe_path, matches_regex
from src.core.command_parser import BashCommandParser
from tests.helpers import assert_allow, assert_deny, assert_pass


def test_simple_allow(bash_event):
    git_add_rule = (
        command("git")
        .subcommand("add")
        .allow()
    )

    assert_allow(git_add_rule, bash_event("git add file.txt"))


def test_simple_deny(bash_event):
    sudo_rule = (
        command("sudo")
        .deny("sudo not allowed")
    )

    assert_deny(sudo_rule, bash_event("sudo apt install"))


def test_sequential_argument_validation(bash_event):
    git_mv_rule = (
        command("git")
        .subcommand("mv")
        .with_argument(safe_path)
        .with_argument(safe_path)
        .allow()
    )

    assert_allow(git_mv_rule, bash_event("git mv oldfile.txt newfile.txt"))
    assert_deny(git_mv_rule, bash_event("git mv /tmp/file.txt local.txt"))


def test_validate_all_arguments(bash_event):
    trash_rule = (
        command("trash")
        .with_arguments(safe_path)
        .allow()
    )

    assert_allow(trash_rule, bash_event("trash file1.txt file2.txt"))
    assert_deny(trash_rule, bash_event("trash file1.txt /tmp/file2.txt"))


def test_require_one_or_logic(bash_event):
    git_commit_rule = (
        command("git")
        .subcommand("commit")
        .require_one(
            has_option("-m"),
            has_option("--message"),
            has_flag("--amend")
        )
        .allow()
    )

    assert_allow(git_commit_rule, bash_event('git commit -m "message"'))
    assert_allow(git_commit_rule, bash_event("git commit --amend"))
    assert_deny(git_commit_rule, bash_event("git commit"))


def test_required_option_with_validation(bash_event):
    docker_build_rule = (
        command("docker")
        .subcommand("build")
        .with_option("--tag", matches_regex(r'^[a-z0-9-]+$'))
        .with_argument(safe_path)
        .allow()
    )

    assert_allow(docker_build_rule, bash_event("docker build --tag myapp ."))
    assert_deny(docker_build_rule, bash_event("docker build --tag MyApp ."))
    assert_deny(docker_build_rule, bash_event("docker build ."))


def test_conditional_deny_only(bash_event):
    git_push_force_rule = (
        command("git")
        .subcommand("push")
        .when(has_flag("--force", "-f"))
        .deny("Force push not allowed")
    )

    assert_deny(git_push_force_rule, bash_event("git push --force"))
    assert_pass(git_push_force_rule, bash_event("git push"))


def test_non_matching_executable_passes_through(bash_event):
    git_add_rule = (
        command("git")
        .subcommand("add")
        .allow()
    )

    assert_pass(git_add_rule, bash_event("docker build ."))


def test_non_bash_tool_passes_through(bash_event):
    git_add_rule = (
        command("git")
        .subcommand("add")
        .allow()
    )

    assert_pass(git_add_rule, bash_event("git add file.txt", tool_is_bash=False))


def test_complex_parsing_error_denies(bash_event):
    git_add_rule = (
        command("git")
        .subcommand("add")
        .allow()
    )

    event = bash_event("git add $(find . -name '*.txt')")
    assert_pass(git_add_rule, event)
