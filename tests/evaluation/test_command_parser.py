"""Tests for bashlex-based command parser."""

import pytest
from src.evaluation.parser import BashCommandParser, ParseError


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


def test_process_substitution_simple():
    cmd = BashCommandParser.parse("diff <(cat file1.txt) <(cat file2.txt)")
    assert cmd.executable == "diff"
    assert len(cmd.process_substitutions) == 2
    assert cmd.process_substitutions[0].executable == "cat"
    assert cmd.process_substitutions[0].arguments == ["file1.txt"]
    assert cmd.process_substitutions[1].executable == "cat"
    assert cmd.process_substitutions[1].arguments == ["file2.txt"]


def test_process_substitution_with_pipeline():
    cmd = BashCommandParser.parse("diff <(ls | grep pattern | sort)")
    assert cmd.executable == "diff"
    assert len(cmd.process_substitutions) == 1
    ps = cmd.process_substitutions[0]
    assert ps.executable == "ls"
    assert len(ps.pipes) == 2
    assert ps.pipes[0].executable == "grep"
    assert ps.pipes[1].executable == "sort"


def test_process_substitution_with_chained_commands():
    cmd = BashCommandParser.parse('diff <(ls) file.txt && echo "done"')
    assert cmd.executable == "diff"
    assert len(cmd.process_substitutions) == 1
    assert cmd.process_substitutions[0].executable == "ls"
    assert len(cmd.chained) == 1
    assert cmd.chained[0].executable == "echo"


def test_command_substitution_blocked():
    with pytest.raises(ParseError, match="Command substitution"):
        BashCommandParser.parse("echo $(ls)")


def test_process_substitution_with_and_operator_fails():
    with pytest.raises(ParseError):
        BashCommandParser.parse("diff <(cmd1 && cmd2)")


def test_process_substitution_with_or_operator_fails():
    with pytest.raises(ParseError):
        BashCommandParser.parse("diff <(cmd1 || cmd2)")


def test_process_substitution_with_semicolon_works():
    cmd = BashCommandParser.parse("diff <(cmd1 ; cmd2)")
    assert len(cmd.process_substitutions) == 1
    ps = cmd.process_substitutions[0]
    assert ps.executable == "cmd1"
    assert len(ps.chained) == 1
    assert ps.chained[0].executable == "cmd2"


def test_process_substitution_multiple_works():
    cmd = BashCommandParser.parse("diff <(cat file1) <(cat file2) <(cat file3)")
    assert len(cmd.process_substitutions) == 3


def test_process_substitution_nested_pipes_works():
    cmd = BashCommandParser.parse("diff <(cat file | grep a | sort | uniq)")
    assert len(cmd.process_substitutions) == 1
    assert len(cmd.process_substitutions[0].pipes) == 3


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
    original = 'git commit -m "test message"'
    cmd = BashCommandParser.parse(original)
    assert cmd.original == original


def test_main_command_options():
    cmd = BashCommandParser.parse("git -C /path/to/repo add file.txt")
    assert cmd.executable == "git"
    assert cmd.options.get("-C") == "/path/to/repo"
    assert cmd.subcommand == "add"
    assert cmd.arguments == ["file.txt"]


def test_main_command_options_with_flags():
    cmd = BashCommandParser.parse('git -C src -c core.editor=vim commit -m "msg"')
    assert cmd.executable == "git"
    assert cmd.options.get("-C") == "src"
    assert cmd.options.get("-c") == "core.editor=vim"
    assert cmd.subcommand == "commit"
    assert cmd.options.get("-m") == '"msg"'
