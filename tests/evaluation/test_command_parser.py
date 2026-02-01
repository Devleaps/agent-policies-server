"""Tests for bashlex-based command parser."""

import pytest
from src.evaluation.parser import BashCommandParser, ParsedCommand, ParseError


def test_simple_command():
    cmd = BashCommandParser.parse("ls")
    assert cmd.executable == "ls"
    assert cmd.subcommand is None
    assert cmd.arguments == []
    assert cmd.flags == []
    assert cmd.options == {}


def test_command_with_arguments():
    cmd = BashCommandParser.parse("cat file.txt")
    assert cmd.executable == "cat"
    assert cmd.arguments == ["file.txt"]


def test_command_with_flags():
    cmd = BashCommandParser.parse("ls -la")
    assert cmd.executable == "ls"
    assert "-la" in cmd.flags


def test_command_with_separate_flags():
    cmd = BashCommandParser.parse("git add -A")
    assert cmd.executable == "git"
    assert cmd.subcommand == "add"
    assert "-A" in cmd.flags


def test_command_with_options():
    cmd = BashCommandParser.parse('git commit -m "message"')
    assert cmd.executable == "git"
    assert cmd.subcommand == "commit"
    assert cmd.options.get("-m") == '"message"'


def test_command_with_option_equals():
    cmd = BashCommandParser.parse("docker build --tag=myapp:latest .")
    assert cmd.executable == "docker"
    assert cmd.subcommand == "build"
    assert cmd.options.get("--tag") == "myapp:latest"
    assert "." in cmd.arguments


def test_git_subcommand_detection():
    cmd = BashCommandParser.parse("git add file.txt")
    assert cmd.executable == "git"
    assert cmd.subcommand == "add"
    assert cmd.arguments == ["file.txt"]


def test_docker_subcommand_detection():
    cmd = BashCommandParser.parse("docker build .")
    assert cmd.executable == "docker"
    assert cmd.subcommand == "build"
    assert cmd.arguments == ["."]


def test_command_with_redirect_output():
    cmd = BashCommandParser.parse("echo hello > output.txt")
    assert cmd.executable == "echo"
    assert cmd.arguments == ["hello"]
    assert len(cmd.redirects) == 1
    assert cmd.redirects[0][1] == "output.txt"


def test_command_with_redirect_append():
    cmd = BashCommandParser.parse("echo hello >> output.txt")
    assert cmd.executable == "echo"
    assert len(cmd.redirects) == 1
    assert cmd.redirects[0][1] == "output.txt"


def test_pipeline():
    cmd = BashCommandParser.parse("cat file.txt | grep pattern")
    assert cmd.executable == "cat"
    assert cmd.arguments == ["file.txt"]
    assert len(cmd.pipes) == 1
    assert cmd.pipes[0].executable == "grep"
    assert cmd.pipes[0].arguments == ["pattern"]


def test_multiple_pipes():
    cmd = BashCommandParser.parse("cat file.txt | grep pattern | wc -l")
    assert cmd.executable == "cat"
    assert len(cmd.pipes) == 2
    assert cmd.pipes[0].executable == "grep"
    assert cmd.pipes[1].executable == "wc"


def test_empty_command_raises_error():
    with pytest.raises(ParseError, match="Empty command"):
        BashCommandParser.parse("")


def test_command_substitution_blocked():
    with pytest.raises(ParseError, match="Command substitution"):
        BashCommandParser.parse("echo $(ls)")


def test_compound_command_blocked():
    with pytest.raises(ParseError, match="Compound commands"):
        BashCommandParser.parse("if [ -f file.txt ]; then cat file.txt; fi")


def test_mixed_flags_and_options():
    cmd = BashCommandParser.parse("pytest -v --maxfail=2 tests/")
    assert cmd.executable == "pytest"
    assert "-v" in cmd.flags
    assert cmd.options.get("--maxfail") == "2"
    assert "tests/" in cmd.arguments


def test_git_commit_with_multiple_options():
    cmd = BashCommandParser.parse('git commit -m "msg" --amend')
    assert cmd.executable == "git"
    assert cmd.subcommand == "commit"
    assert cmd.options.get("-m") == '"msg"'
    assert "--amend" in cmd.flags


def test_terraform_with_subcommand():
    cmd = BashCommandParser.parse("terraform plan -out=tfplan")
    assert cmd.executable == "terraform"
    assert cmd.subcommand == "plan"
    assert cmd.options.get("-out") == "tfplan"


def test_uv_add_packages():
    cmd = BashCommandParser.parse("uv add requests httpx")
    assert cmd.executable == "uv"
    assert cmd.subcommand == "add"
    assert cmd.arguments == ["requests", "httpx"]


def test_original_command_preserved():
    original = "git commit -m \"test message\""
    cmd = BashCommandParser.parse(original)
    assert cmd.original == original


def test_main_command_options():
    cmd = BashCommandParser.parse("git -C /path/to/repo add file.txt")
    assert cmd.executable == "git"
    assert cmd.options.get("-C") == "/path/to/repo"
    assert cmd.subcommand == "add"
    assert cmd.arguments == ["file.txt"]


def test_main_command_options_with_flags():
    cmd = BashCommandParser.parse("git -C src -c core.editor=vim commit -m \"msg\"")
    assert cmd.executable == "git"
    assert cmd.options.get("-C") == "src"
    assert cmd.options.get("-c") == "core.editor=vim"
    assert cmd.subcommand == "commit"
    assert cmd.options.get("-m") == '"msg"'
