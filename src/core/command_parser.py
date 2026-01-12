"""Bash command parser using bashlex for AST-based parsing.

This module provides accurate command parsing without relying on regex patterns.
It uses bashlex (Python port of GNU bash parser) to generate AST and extract
command components.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import bashlex


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
        original: Original command string
        pos: Position tuple (start, end) in original string for text extraction
    """
    executable: str
    subcommand: Optional[str] = None
    arguments: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    options: Dict[str, str] = field(default_factory=dict)
    redirects: List[Tuple[str, str]] = field(default_factory=list)
    pipes: List['ParsedCommand'] = field(default_factory=list)
    chained: List['ParsedCommand'] = field(default_factory=list)
    original: str = ""
    pos: Optional[Tuple[int, int]] = None

    def get_command_text(self) -> str:
        """Extract this command's text from the original string using position info."""
        if self.pos and self.original:
            return self.original[self.pos[0]:self.pos[1]].strip()
        return self.original


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

        node = parts[0]
        return cls._parse_node(node, command)

    @classmethod
    def _parse_node(cls, node, original: str) -> ParsedCommand:
        """Parse a bashlex AST node into ParsedCommand."""

        if node.kind == 'compound':
            raise ParseError("Compound commands (if/for/while) not supported")

        if node.kind == 'commandsubstitution':
            raise ParseError("Command substitution not supported")

        if node.kind == 'pipeline':
            commands = []
            for part_node in node.parts:
                if part_node.kind == 'command':
                    parsed = cls._parse_command_node(part_node, original)
                    parsed.pos = part_node.pos
                    commands.append(parsed)

            if commands:
                result = commands[0]
                result.pipes = commands[1:]
                return result
            raise ParseError("Empty pipeline")

        if node.kind == 'list':
            if not node.parts:
                raise ParseError("Empty list")

            commands = []
            for part_node in node.parts:
                if part_node.kind in ('command', 'pipeline'):
                    parsed = cls._parse_node(part_node, original)
                    parsed.pos = part_node.pos
                    parsed.original = original
                    commands.append(parsed)

            if not commands:
                raise ParseError("No commands found in list")

            result = commands[0]
            result.chained = commands[1:]
            return result

        if node.kind == 'command':
            return cls._parse_command_node(node, original)

        raise ParseError(f"Unsupported node kind: {node.kind}")

    @classmethod
    def _parse_command_node(cls, node, original: str) -> ParsedCommand:
        """Parse a command node into ParsedCommand."""

        parts = []
        redirects = []

        for part in node.parts:
            if part.kind == 'word':
                if hasattr(part, 'parts') and part.parts:
                    for subpart in part.parts:
                        if subpart.kind == 'commandsubstitution':
                            raise ParseError("Command substitution not supported")

                word_value = original[part.pos[0]:part.pos[1]]
                parts.append(word_value)
            elif part.kind == 'redirect':
                redirect_op = cls._get_redirect_operator(part)
                # Handle both word nodes (with .pos) and file descriptors (int)
                if hasattr(part.output, 'pos'):
                    redirect_target = original[part.output.pos[0]:part.output.pos[1]]
                    redirects.append((redirect_op, redirect_target))
                # Else: heredoc or file descriptor - skip for now (TODO: extract heredoc content)

        if not parts:
            raise ParseError("No executable found in command")

        # First part is the executable
        executable = parts[0]
        remaining = parts[1:]

        # Determine subcommand, arguments, flags, options
        subcommand = None
        arguments = []
        flags = []
        options = {}

        i = 0
        while i < len(remaining):
            part = remaining[i]

            # Check if it's a flag or option
            if part.startswith('-'):
                # Check if it's an option with value (--key=value)
                if '=' in part:
                    key, value = part.split('=', 1)
                    options[key] = value
                # Check if next part is the value for this option
                elif i + 1 < len(remaining) and not remaining[i + 1].startswith('-'):
                    options[part] = remaining[i + 1]
                    i += 1  # Skip next part
                else:
                    # It's a boolean flag
                    flags.append(part)
            else:
                # It's a positional argument
                # First non-flag argument might be subcommand for certain executables
                if not subcommand and not arguments and cls._is_likely_subcommand(executable, part):
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
            original=original
        )

    @staticmethod
    def _get_redirect_operator(redirect_node) -> str:
        """Extract redirect operator from redirect node."""
        # Common operators: >, >>, <, 2>, &>, etc.
        if hasattr(redirect_node, 'type'):
            return redirect_node.type
        return ">"

    @staticmethod
    def _is_likely_subcommand(executable: str, word: str) -> bool:
        """Heuristic to determine if word is a subcommand.

        Commands like git, docker, kubectl, terraform commonly have subcommands.
        """
        # Commands known to use subcommands
        subcommand_executables = {
            'git', 'docker', 'kubectl', 'terraform', 'terragrunt',
            'gh', 'az', 'gcloud', 'aws', 'npm', 'pip', 'uv', 'cargo'
        }

        # If executable is known to use subcommands and word doesn't look like a path/file
        if executable in subcommand_executables:
            # Subcommands typically don't have path separators or extensions
            if '/' not in word and '.' not in word:
                return True

        return False
