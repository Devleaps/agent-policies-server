"""
HTTP Integration Tests: loops, conditionals, subshells, command substitution
and shell variables are evaluated through the commands they run.
"""

import pytest

from src.evaluation.parser import BashCommandParser, ParseError
from tests.http.conftest import check_policy


def executables(command):
    parsed = BashCommandParser.parse(command)
    return [parsed.executable] + [c.executable for c in parsed.chained]


# The examples from the agent-policies to-do list
@pytest.mark.parametrize(
    "command",
    [
        "for f in tests/test_llm.py tests/test_prompt_overlap.py tests/test_agent_turn.py tests/test_tools.py; do\n"
        "     echo \"$f: $(grep -c 'app\\.llm\\.anthropic\\|app\\.llm\\.httpx' \"$f\")\"\n"
        "   done",
        'pwd ; grep -n "AppConfig(" -A 7 /dev/null $(echo) ; true',
        "export A=$(pwd)",
        'until [ "$(gh run list --repo example-org/example-repo --limit 1 --json status'
        " --jq '.[0].status')\" = \"completed\" ]; do sleep 10; done",
    ],
)
def test_todo_examples_are_allowed(client, base_event, command):
    check_policy(client, base_event, command, "allow")


@pytest.mark.parametrize(
    "command",
    [
        "echo $(rm -rf build)",
        "echo `sudo ls`",
        'echo "$(git push --force)"',
        "for f in a b; do rm -rf $f; done",
        "while true; do sudo ls; done",
        "if true; then pwd; else rm -rf build; fi",
        "(cd src && rm -rf build)",
        "ls | while read d; do rm -rf \"$d\"; done",
        "for f in $(rm -rf build); do echo $f; done",
        "A=$(rm -rf build)",
        "export A=$(rm -rf build)",
        "{ pwd; rm -rf build; }",
        "pwd & rm -rf build",
        "cat <(rm -rf build)",
    ],
)
def test_denied_inner_command_denies(client, base_event, command):
    check_policy(client, base_event, command, "deny")


@pytest.mark.parametrize(
    "command",
    [
        "echo $(bash evil.sh)",
        "for f in a; do bash evil.sh; done",
        "(pwd; bash evil.sh)",
    ],
)
def test_undecided_inner_command_defers_to_user(client, base_event, command):
    check_policy(client, base_event, command, None)


def test_for_loop_body_runs_once_per_literal_item():
    parsed = BashCommandParser.parse("for f in a b; do cat $f; done")
    commands = [parsed] + parsed.chained
    assert [c.arguments for c in commands] == [["a"], ["b"]]
    assert commands[0].expanded_words == []


def test_for_loop_over_a_glob_leaves_the_variable_unknown():
    parsed = BashCommandParser.parse("for f in *.py; do cat $f; done")
    assert parsed.expanded_words == ["$f"]
    assert parsed.chained == []


def test_for_loop_variable_reassigned_in_body_is_unknown():
    parsed = BashCommandParser.parse("for f in a; do f=/etc/passwd; cat $f; done")
    assert parsed.chained[0].expanded_words == ["$f"]


@pytest.mark.parametrize(
    "command, path",
    [
        ("R=src; cat $R/main.py", "src/main.py"),
        ('R="src"; cat "$R/main.py"', "src/main.py"),
        ("R=src; cat ${R}/main.py", "src/main.py"),
        ("export R=src; cat $R/main.py", "src/main.py"),
    ],
)
def test_known_variable_is_substituted(command, path):
    parsed = BashCommandParser.parse(command)
    cat = parsed.chained[0]
    assert cat.arguments == [path]
    assert cat.expanded_words == []


@pytest.mark.parametrize(
    "command",
    [
        # From the caller's environment
        "cat $HOME/x",
        # Only assigned when the first command succeeds
        "true && R=src; cat $R/x",
        # Assigned in a loop or conditional
        "if true; then R=src; fi; cat $R/x",
        "while true; do R=src; done; cat $R/x",
        # Assigned in a subshell or pipeline, which does not reach this shell
        "(R=src); cat $R/x",
        # Set at run time
        "read R; cat $R/x",
        "R=$(pwd); cat $R/x",
        "R=src; source env.sh; cat $R/x",
        # Values the shell would split or glob
        'R="a b"; cat $R',
        "R='*'; cat $R",
        # Quoting other than plain double quotes
        "R=src; cat '$R'/x",
        "R=src; cat \\\\$R/x",
        # Parameter operators
        "R=src; cat ${R:-/etc}/x",
        "R=src; cat ${#R}",
    ],
)
def test_unknown_variable_stays_expanded(command):
    parsed = BashCommandParser.parse(command)
    last = ([parsed] + parsed.chained)[-1]
    assert last.expanded_words


def test_variable_path_is_checked_where_it_points(client, base_event):
    check_policy(client, base_event, "R=src; cat $R/main.py", "allow")
    check_policy(client, base_event, "R=/etc; cat $R/passwd", "deny")


def test_variable_command_name_is_evaluated(client, base_event):
    check_policy(client, base_event, "C=rm; $C -rf build", "deny")


def test_prefix_assignment_does_not_set_the_shell_variable():
    parsed = BashCommandParser.parse("R=src ls; cat $R/x")
    assert parsed.chained[0].expanded_words == ["$R/x"]


@pytest.mark.parametrize(
    "command",
    [
        "case a in a) echo;; esac",
        "f() { rm -rf build; }; f",
        "echo $((1 + 2))",
        "for f in a; do echo $f; done > out.txt",
        "cat << EOF\n$(rm -rf build)\nEOF",
        "cat << EOF\n`rm -rf build`\nEOF",
    ],
)
def test_unsupported_constructs_raise(command):
    with pytest.raises(ParseError):
        BashCommandParser.parse(command)


def test_heredoc_without_substitution_still_parses():
    assert executables("cat << EOF\nplain $HOME text\nEOF") == ["cat"]


def test_large_unrolled_loop_raises():
    items = " ".join(str(i) for i in range(20))
    with pytest.raises(ParseError, match="too large"):
        BashCommandParser.parse(
            f"for a in {items}; do for b in {items}; do echo $a $b; done; done"
        )


def test_long_loop_is_evaluated_once_with_unknown_variable():
    items = " ".join(str(i) for i in range(21))
    parsed = BashCommandParser.parse(f"for a in {items}; do echo $a; done")
    assert parsed.chained == []
    assert parsed.expanded_words == ["$a"]


# Working directory tracking through compound commands


def test_cd_in_subshell_does_not_move_later_commands(client, base_event):
    check_policy(client, base_event, "(cd /etc) && cat passwd", "allow")
    check_policy(client, base_event, "(cd /etc && cat passwd)", "deny")


def test_cd_in_brace_group_moves_later_commands(client, base_event):
    check_policy(client, base_event, "{ cd /etc && cat passwd; }", "deny")


def test_backgrounded_cd_does_not_move_later_commands(client, base_event):
    check_policy(client, base_event, "cd /etc & cat passwd", "allow")


@pytest.mark.parametrize(
    "command",
    [
        # After a cd that may fail, both directories are possible
        "cd subdir; cat ../README.md",
        "cd subdir || cat ../README.md",
        "cd subdir && pwd; cat ../README.md",
        # A cd in a loop or branch leaves the directory unknown
        "if true; then cd subdir; fi; cat ../README.md",
        "for d in a b; do cat README.md; cd ..; done",
        "while true; do cat README.md; cd ..; done",
    ],
)
def test_uncertain_cd_never_makes_an_outside_path_safe(client, base_event, command):
    check_policy(client, base_event, command, "deny")


def test_cd_followed_by_and_still_tracks(client, base_event):
    check_policy(client, base_event, "cd subdir && cat ../README.md", "allow")


@pytest.mark.parametrize(
    "command",
    [
        # A changed IFS splits values on other characters
        "IFS=/; R=src; cat $R",
        # declare -n makes $X read another variable
        "declare -n X=HOME; cat $X/.ssh/id_rsa",
        # After source, any variable may be set
        "R=src; . env.sh; cat $R",
    ],
)
def test_shell_behaviour_changes_leave_values_unknown(command):
    parsed = BashCommandParser.parse(command)
    last = ([parsed] + parsed.chained)[-1]
    assert last.expanded_words


def test_changed_home_makes_tilde_unknown():
    parsed = BashCommandParser.parse("HOME=src; cat ~/x")
    assert parsed.chained[0].expanded_words == ["~/x"]


@pytest.mark.parametrize(
    "command",
    [
        "HOME=/etc; cd && cat passwd",
        "CDPATH=/; cd etc && cat passwd",
    ],
)
def test_changed_home_or_cdpath_makes_cd_unknown(client, base_event, command):
    check_policy(client, base_event, command, "deny")


def test_known_echo_output_is_substituted():
    parsed = BashCommandParser.parse("cat $(echo src/main.py) $(echo)")
    assert parsed.arguments == ["src/main.py"]
    assert parsed.expanded_words == []


def test_echo_with_unknown_output_stays_expanded(client, base_event):
    check_policy(client, base_event, "cat $(echo $HOME/.ssh/id_rsa)", "deny")
    check_policy(client, base_event, "cat $(echo /etc/passwd)", "deny")


def test_piped_cd_does_not_move_later_commands(client, base_event):
    check_policy(client, base_event, "cd subdir | true && cat ../README.md", "deny")
