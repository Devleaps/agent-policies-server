"""Bash command parser using bashlex for AST-based parsing.

This module provides accurate command parsing without relying on regex patterns.
It uses bashlex (Python port of GNU bash parser) to generate AST and extract
command components.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import bashlex

# $( or a backtick not escaped by an odd number of backslashes
_UNESCAPED_SUBSTITUTION = re.compile(r"(?<!\\)(?:\\\\)*(?:\$\(|`)")


class ParseError(Exception):
    """Raised when command parsing fails."""

    pass


@dataclass
class ParsedCommand:
    """Represents a parsed bash command with all its components.

    Attributes:
        executable: The command name (e.g., "git", "docker", "pytest")
        subcommand: Optional subcommand (e.g., "add" for "git add")
        arguments: Positional arguments (excludes flags and options)
        flags: Boolean flags (e.g., ["--force", "-v"])
        options: Options with values (e.g., {"-m": "message", "--tag": "v1.0"})
        redirects: List of redirect operations (e.g., [(">>", "output.log")])
        pipes: List of piped commands
        chained: List of chained commands (&&, ||, ;)
        process_substitutions: List of commands from <(...) or >(...) substitutions
        expanded_words: Words containing a shell parameter expansion ($X, ${X})
        test_paths: For test and [, the operands of file tests, in order
        original: Original command string
        pos: Position tuple (start, end) in original string for text extraction
    """

    executable: str
    subcommand: Optional[str] = None
    arguments: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    options: Dict[str, str] = field(default_factory=dict)
    redirects: List[Tuple[str, str]] = field(default_factory=list)
    pipes: List["ParsedCommand"] = field(default_factory=list)
    chained: List["ParsedCommand"] = field(default_factory=list)
    process_substitutions: List["ParsedCommand"] = field(default_factory=list)
    expanded_words: List[str] = field(default_factory=list)
    test_paths: List[str] = field(default_factory=list)
    original: str = ""
    pos: Optional[Tuple[int, int]] = None

    def get_command_text(self) -> str:
        """Extract this command's text from the original string using position info."""
        if self.pos and self.original:
            return self.original[self.pos[0] : self.pos[1]].strip()
        return self.original


# File tests of test / [: the operand(s) name a path
TEST_UNARY_FILE_OPS = {
    "-a", "-e", "-f", "-d", "-r", "-w", "-x", "-s", "-L", "-h", "-p", "-S",
    "-b", "-c", "-g", "-u", "-k", "-O", "-G", "-N",
}
TEST_BINARY_FILE_OPS = {"-nt", "-ot", "-ef"}
# After these, a test expression starts again (so -a there is "file exists")
TEST_EXPRESSION_STARTS = {"!", "(", "-a", "-o"}


def file_test_operands(words: List[str]) -> List[str]:
    """Return the operands of file tests in a test / [ expression, in order.

    -a is "file exists" where an expression starts and "and" between two
    expressions: [ -a x ] tests x, [ -f a -a -f b ] tests a and b.
    """
    if words and words[-1] == "]":
        words = words[:-1]
    paths = []
    for i, word in enumerate(words):
        has_next = i + 1 < len(words)
        starts_expression = i == 0 or words[i - 1] in TEST_EXPRESSION_STARTS
        if word in TEST_UNARY_FILE_OPS and has_next:
            if word != "-a" or starts_expression:
                paths.append(words[i + 1])
        elif word in TEST_BINARY_FILE_OPS and has_next and i > 0:
            paths.extend([words[i - 1], words[i + 1]])
    return paths


class BashCommandParser:
    """Parser for bash commands using bashlex AST.

    Handles:
    - Simple commands (git add file.txt)
    - Pipes (cat file.txt | grep pattern)
    - Logical operators (cmd1 && cmd2, cmd1 || cmd2, cmd1 ; cmd2)
    - Redirects (>, >>, <)
    - Flags and options (--flag, -f, --option=value, -o value)

    Does NOT handle (returns ParseError):
    - Command substitution ($(cmd), `cmd`)
    - Compound commands (if, for, while, case)
    """

    @classmethod
    def parse(cls, command: str) -> ParsedCommand:
        """Parse a bash command string into structured components.

        Args:
            command: The bash command string to parse

        Returns:
            ParsedCommand with extracted components

        Raises:
            ParseError: If command is too complex or invalid syntax
        """
        if not command or not command.strip():
            raise ParseError("Empty command")

        try:
            parts = bashlex.parse(command)
        except (bashlex.errors.ParsingError, Exception) as e:
            raise ParseError(f"Command too complex for policy validation: {e}")

        if not parts:
            raise ParseError("No parseable command found")

        # bashlex returns one node per line: every line runs, so every line
        # is chained, as if joined with ";"
        commands = []
        for node in parts:
            parsed = cls._parse_node(node, command)
            commands.append(parsed)
            commands.extend(parsed.chained)
            parsed.chained = []
        result = commands[0]
        result.chained = commands[1:]
        return result

    @classmethod
    def _parse_node(cls, node, original: str) -> ParsedCommand:
        """Parse a bashlex AST node into ParsedCommand."""

        if node.kind == "compound":
            raise ParseError("Compound commands (if/for/while) not supported")

        if node.kind == "commandsubstitution":
            raise ParseError("Command substitution not supported")

        if node.kind == "pipeline":
            commands = []
            for part_node in node.parts:
                if part_node.kind == "command":
                    parsed = cls._parse_command_node(part_node, original)
                    parsed.pos = part_node.pos
                    commands.append(parsed)
                elif part_node.kind not in ("pipe", "reservedword"):
                    # Skipping it would leave a command unevaluated
                    raise ParseError(f"Unsupported node in pipeline: {part_node.kind}")

            if commands:
                result = commands[0]
                result.pipes = commands[1:]
                return result
            raise ParseError("Empty pipeline")

        if node.kind == "list":
            if not node.parts:
                raise ParseError("Empty list")

            commands = []
            for part_node in node.parts:
                if part_node.kind in ("command", "pipeline"):
                    parsed = cls._parse_node(part_node, original)
                    parsed.pos = part_node.pos
                    parsed.original = original
                    commands.append(parsed)
                elif part_node.kind != "operator":
                    # Skipping it would leave a command unevaluated
                    raise ParseError(f"Unsupported node in list: {part_node.kind}")

            if not commands:
                raise ParseError("No commands found in list")

            result = commands[0]
            result.chained = commands[1:]
            return result

        if node.kind == "command":
            return cls._parse_command_node(node, original)

        raise ParseError(f"Unsupported node kind: {node.kind}")

    @classmethod
    def _word_substitutions(cls, word, original: str) -> list[ParsedCommand]:
        """Parse the process substitutions inside a word node."""
        substitutions = []
        for subpart in getattr(word, "parts", None) or []:
            if subpart.kind == "commandsubstitution":
                raise ParseError("Command substitution not supported")
            elif subpart.kind == "processsubstitution":
                if hasattr(subpart, "command"):
                    substitutions.append(cls._parse_node(subpart.command, original))
        return substitutions

    @classmethod
    def _parse_command_node(cls, node, original: str) -> ParsedCommand:
        """Parse a command node into ParsedCommand."""

        parts = []
        redirects = []
        process_substitutions = []
        expanded_words = []

        for part in node.parts:
            if part.kind == "word":
                process_substitutions.extend(cls._word_substitutions(part, original))
                if any(
                    sub.kind == "parameter"
                    for sub in (getattr(part, "parts", None) or [])
                ):
                    expanded_words.append(part.word)

                # bashlex's .word has shell quoting removed, so policies see
                # the path the shell will use: '/etc/passwd' -> /etc/passwd
                parts.append(part.word)
            elif part.kind == "assignment":
                # Prefix assignments (X=1 cmd) run their substitutions too
                for subpart in getattr(part, "parts", None) or []:
                    if subpart.kind in ("commandsubstitution", "processsubstitution"):
                        raise ParseError("Command substitution not supported")
            elif part.kind == "redirect":
                redirect_op = cls._get_redirect_operator(part)
                # A heredoc body or here-string runs its substitutions
                heredoc = getattr(part, "heredoc", None)
                if heredoc is not None and _UNESCAPED_SUBSTITUTION.search(
                    heredoc.value
                ):
                    raise ParseError("Command substitution in redirect not supported")
                if any(
                    sub.kind in ("commandsubstitution", "processsubstitution")
                    for sub in (getattr(part.output, "parts", None) or [])
                ):
                    raise ParseError("Command substitution in redirect not supported")
                # Handle both word nodes (with .pos) and file descriptors (int)
                if hasattr(part.output, "pos"):
                    # A redirect target such as < <(cmd) runs cmd too
                    process_substitutions.extend(
                        cls._word_substitutions(part.output, original)
                    )
                    redirect_target = part.output.word
                    redirects.append((redirect_op, redirect_target))
                    if any(
                        sub.kind == "parameter"
                        for sub in (getattr(part.output, "parts", None) or [])
                    ):
                        expanded_words.append(redirect_target)
                # Else: heredoc or file descriptor - skip for now (TODO: extract heredoc content)

        if not parts:
            raise ParseError("No executable found in command")

        # First part is the executable
        executable = parts[0]
        remaining = parts[1:]

        # Determine subcommand, arguments, flags, options
        subcommand = None
        arguments: list[str] = []
        flags = []
        options = {}

        i = 0
        while i < len(remaining):
            part = remaining[i]

            # Check if it's a flag or option
            if part.startswith("-"):
                # Check if it's an option with value (--key=value)
                if "=" in part:
                    key, value = part.split("=", 1)
                    options[key] = value
                    # --directory=$HOME: policies see only the value
                    if part in expanded_words:
                        expanded_words.append(value)
                # Check if next part is the value for this option
                elif i + 1 < len(remaining) and not remaining[i + 1].startswith("-"):
                    options[part] = remaining[i + 1]
                    i += 1  # Skip next part
                else:
                    # It's a boolean flag
                    flags.append(part)
            else:
                # It's a positional argument
                # First non-flag argument might be subcommand for certain executables
                if (
                    not subcommand
                    and not arguments
                    and cls._is_likely_subcommand(executable, part)
                ):
                    subcommand = part
                else:
                    arguments.append(part)

            i += 1

        return ParsedCommand(
            executable=executable,
            subcommand=subcommand,
            arguments=arguments,
            flags=flags,
            options=options,
            redirects=redirects,
            process_substitutions=process_substitutions,
            expanded_words=expanded_words,
            test_paths=(
                file_test_operands(remaining) if executable in ("test", "[") else []
            ),
            original=original,
        )

    @staticmethod
    def _get_redirect_operator(redirect_node) -> str:
        """Extract redirect operator from redirect node."""
        # Common operators: >, >>, <, 2>, &>, etc.
        if hasattr(redirect_node, "type"):
            return redirect_node.type
        return ">"

    @staticmethod
    def _is_likely_subcommand(executable: str, word: str) -> bool:
        """Heuristic to determine if word is a subcommand.

        Commands like git, docker, kubectl, terraform commonly have subcommands.
        """
        # Commands known to use subcommands
        subcommand_executables = {
            "git",
            "docker",
            "podman",
            "kubectl",
            "terraform",
            "terragrunt",
            "gh",
            "az",
            "gcloud",
            "aws",
            "npm",
            "pip",
            "uv",
            "cargo",
            "ruff",
            "mypy",
            "black",
            "pytest",
            "vale",
        }

        # If executable is known to use subcommands and word doesn't look like a path/file
        if executable in subcommand_executables:
            # Subcommands typically don't have path separators or extensions
            if "/" not in word and "." not in word:
                return True

        return False
