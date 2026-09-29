"""Bash command parser using bashlex for AST-based parsing.

This module provides accurate command parsing without relying on regex patterns.
It uses bashlex (Python port of GNU bash parser) to generate AST and extract
command components.
"""

import dataclasses
import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
import bashlex


class ParseError(Exception):
    """Raised when command parsing fails."""

    pass


# More statements than this (loops unrolled per item) is not worth evaluating
MAX_STATEMENTS = 200
# A for loop over more literal items is evaluated once, with its variable unknown
MAX_FOR_ITEMS = 20

_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_NAME_PREFIX = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*")
# A substituted value with these would be split or globbed by the shell
_UNSAFE_VALUE_CHARS = set(" \t\n*?[")

# Builtins that set the variables named in their arguments
_DECLARING = {"export", "declare", "typeset", "local", "readonly"}
_ASSIGNING = {"read", "mapfile", "readarray", "getopts", "let", "unset", "printf"}
# Builtins that can set any variable
_ENV_REPLACING = {"source", ".", "eval"}
# Variables that change how the shell expands words and resolves cd
_SHELL_BEHAVIOUR_VARS = ("IFS", "HOME", "CDPATH")


@dataclass
class ParsedCommand:
    """Represents a parsed bash command with all its components.

    Attributes:
        executable: The command name (e.g., "git", "docker", "pytest"); empty
            for a group or an assignment-only statement
        subcommand: Optional subcommand (e.g., "add" for "git add")
        arguments: Positional arguments (excludes flags and options)
        flags: Boolean flags (e.g., ["--force", "-v"])
        options: Options with values (e.g., {"-m": "message", "--tag": "v1.0"})
        redirects: List of redirect operations (e.g., [(">>", "output.log")])
        pipes: List of piped commands
        chained: List of chained commands (&&, ||, ;), and every statement of
            loops, conditionals and brace groups, flattened in order
        process_substitutions: Commands from <(...), >(...), $(...) and `...`
        expanded_words: Words whose value is not known before running
        group: Statements of a subshell, when this is one
        operator: The list operator after this statement (&&, ||, ;, &)
        location_unknown_before: The working directory is unknown here
        location_unknown_after: The working directory is unknown after this
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
    group: Optional[List["ParsedCommand"]] = None
    operator: Optional[str] = None
    location_unknown_before: bool = False
    location_unknown_after: bool = False
    original: str = ""
    pos: Optional[Tuple[int, int]] = None

    def get_command_text(self) -> str:
        """Extract this command's text from the original string using position info."""
        if self.pos and self.original:
            return self.original[self.pos[0] : self.pos[1]].strip()
        return self.original


@dataclass
class _Context:
    """Parser state while walking one shell.

    env holds the variables assigned earlier in the command: a value when it
    is known, None when it is not. Variables that are not in env come from
    the caller's environment and are unknown too.
    """

    original: str
    env: Dict[str, Optional[str]]
    budget: List[int]
    # An assignment here may not run: after && or ||, or inside a loop or if
    conditional: bool = False
    # Inside a loop or if: a cd here leaves the directory unknown
    in_compound: bool = False

    def subshell(self) -> "_Context":
        return dataclasses.replace(
            self, env=dict(self.env), conditional=False, in_compound=False
        )

    def with_conditional(
        self, conditional: bool, in_compound: Optional[bool] = None
    ) -> "_Context":
        return dataclasses.replace(
            self,
            conditional=conditional,
            in_compound=self.in_compound if in_compound is None else in_compound,
        )

    def assign(self, word: str, value: Optional[str]) -> None:
        name = word.split("=", 1)[0]
        match = _NAME_PREFIX.match(name)
        if not match:
            return
        if match.group(0) != name or self.conditional:
            # X+=y, X[0]=y, or an assignment that may not run
            value = None
        self.env[match.group(0)] = value

    def forget_all(self) -> None:
        """After source or eval, any variable may have been set."""
        self.env.clear()
        self.env.update({name: None for name in _SHELL_BEHAVIOUR_VARS})

    def spend(self) -> None:
        self.budget[0] -= 1
        if self.budget[0] < 0:
            raise ParseError("Command too large for policy validation")


def _walk(node):
    yield node
    for attr in ("parts", "list"):
        for child in getattr(node, attr, None) or []:
            yield from _walk(child)
    for attr in ("command", "output"):
        child = getattr(node, attr, None)
        if hasattr(child, "kind"):
            yield from _walk(child)


def _assigned_names(nodes) -> Optional[set]:
    """Names of the variables the nodes may assign; None if it may be any."""
    if not isinstance(nodes, list):
        nodes = [nodes]
    names = set()
    for node in nodes:
        for n in _walk(node):
            if n.kind == "assignment":
                names.add(n.word.split("=", 1)[0])
            elif n.kind == "for":
                names.add(n.parts[1].word)
            elif n.kind == "command":
                words = [p.word for p in n.parts if p.kind == "word"]
                if not words:
                    continue
                if words[0] in _ENV_REPLACING:
                    return None
                if words[0] in _DECLARING | _ASSIGNING:
                    names.update(w.split("=", 1)[0] for w in words[1:])
    return {m.group(0) for m in map(_NAME_PREFIX.match, names) if m}


def _known_output(command: "ParsedCommand") -> Optional[str]:
    """What a command substitution prints, when that is known: a plain echo
    of literal words."""
    if (
        command.executable == "echo"
        and not command.flags
        and not command.options
        and not command.redirects
        and not command.expanded_words
        and not command.chained
        and not command.pipes
        and not command.process_substitutions
    ):
        return " ".join(command.arguments)
    return None


def _contains_cd(node) -> bool:
    return any(
        n.kind == "command"
        and any(p.kind == "word" for p in n.parts)
        and next(p for p in n.parts if p.kind == "word").word == "cd"
        for n in _walk(node)
    )


class BashCommandParser:
    """Parser for bash commands using bashlex AST.

    Handles:
    - Simple commands (git add file.txt)
    - Pipes (cat file.txt | grep pattern)
    - Logical operators (cmd1 && cmd2, cmd1 || cmd2, cmd1 ; cmd2)
    - Redirects (>, >>, <)
    - Flags and options (--flag, -f, --option=value, -o value)
    - Command substitution ($(cmd), `cmd`), as commands of their own
    - for, while, until, if, subshells and brace groups, flattened into the
      statements they run
    - Variables assigned earlier in the command ($X after X=value)

    Does NOT handle (returns ParseError):
    - case, functions, arithmetic expansion
    - Redirects on compound commands
    - Command substitution in here-documents
    """

    @classmethod
    def parse(cls, command: str) -> ParsedCommand:
        """Parse a bash command string into structured components.

        Args:
            command: The bash command string to parse

        Returns:
            ParsedCommand for the first statement; every later statement is
            in its .chained list, in the order the shell runs them

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
        ctx = _Context(original=command, env={}, budget=[MAX_STATEMENTS])
        statements: List[ParsedCommand] = []
        for node in parts:
            statements.extend(cls._statements(node, ctx))
        return cls._sequence_node(statements, command)

    @staticmethod
    def _sequence_node(
        statements: List[ParsedCommand], original: str
    ) -> ParsedCommand:
        """The first statement, carrying the rest in .chained."""
        if not statements:
            return ParsedCommand(executable="", group=[], original=original)
        first = statements[0]
        first.chained = statements[1:]
        return first

    @staticmethod
    def _group(statements: List[ParsedCommand], node, original: str) -> ParsedCommand:
        """A subshell: its statements run in order, but a cd inside it does
        not move the statements after it."""
        return ParsedCommand(
            executable="", group=statements, original=original, pos=node.pos
        )

    @classmethod
    def _statements(cls, node, ctx: _Context) -> List[ParsedCommand]:
        """Flatten a bashlex node into the statements the shell runs."""
        if node.kind == "list":
            return cls._list_statements(node, ctx)
        if node.kind == "pipeline":
            return [cls._pipeline(node, ctx)]
        if node.kind == "command":
            return [cls._parse_command_node(node, ctx)]
        if node.kind == "compound":
            return cls._compound_statements(node, ctx)
        raise ParseError(f"Unsupported node kind: {node.kind}")

    @classmethod
    def _list_statements(cls, node, ctx: _Context) -> List[ParsedCommand]:
        if not node.parts:
            raise ParseError("Empty list")

        statements: List[ParsedCommand] = []
        conditional = False
        parts = node.parts
        for i, part in enumerate(parts):
            if part.kind == "operator":
                # After && or ||, the next part may or may not run
                conditional = part.op in ("&&", "||")
                continue
            if part.kind not in ("command", "pipeline", "compound"):
                # Skipping it would leave a command unevaluated
                raise ParseError(f"Unsupported node in list: {part.kind}")

            op = None
            if i + 1 < len(parts) and parts[i + 1].kind == "operator":
                op = parts[i + 1].op

            if op == "&":
                # Backgrounded: runs in a subshell, so its cd and assignments
                # do not reach the next statement
                part_statements = [
                    cls._group(
                        cls._statements(part, ctx.subshell()), part, ctx.original
                    )
                ]
            else:
                part_ctx = ctx.with_conditional(ctx.conditional or conditional)
                part_statements = cls._statements(part, part_ctx)

            if part_statements and part_statements[-1].operator is None:
                part_statements[-1].operator = op
            statements.extend(part_statements)

        if not statements:
            raise ParseError("No commands found in list")
        return statements

    @classmethod
    def _pipeline(cls, node, ctx: _Context) -> ParsedCommand:
        elements = [p for p in node.parts if p.kind not in ("pipe", "reservedword")]
        if not elements:
            raise ParseError("Empty pipeline")
        if len(elements) == 1:
            # "! cmd": a single command, run in this shell
            statements = cls._statements(elements[0], ctx)
            if len(statements) == 1:
                return statements[0]
            return cls._group(statements, node, ctx.original)

        # Every element of a real pipeline runs in its own subshell
        commands = []
        for element in elements:
            if element.kind not in ("command", "compound"):
                # Skipping it would leave a command unevaluated
                raise ParseError(f"Unsupported node in pipeline: {element.kind}")
            statements = cls._statements(element, ctx.subshell())
            commands.append(cls._sequence_node(statements, ctx.original))
        result = commands[0]
        result.pipes = commands[1:]
        return result

    @classmethod
    def _compound_statements(cls, node, ctx: _Context) -> List[ParsedCommand]:
        if getattr(node, "redirects", None):
            raise ParseError("Redirects on compound commands not supported")

        body = node.list
        if body and body[0].kind == "reservedword" and body[0].word in ("(", "{"):
            inner = [n for n in body[1:-1] if n.kind != "reservedword"]
            if body[0].word == "(":
                sub = ctx.subshell()
                statements = cls._body_statements(inner, sub)
                return [cls._group(statements, node, ctx.original)]
            return cls._body_statements(inner, ctx)

        if len(body) != 1:
            raise ParseError("Unsupported compound command")
        construct = body[0]
        if construct.kind == "for":
            return cls._for_statements(construct, ctx)
        if construct.kind in ("while", "until", "if"):
            return cls._conditional_statements(construct, ctx)
        raise ParseError(f"Compound command not supported: {construct.kind}")

    @classmethod
    def _body_statements(cls, children, ctx: _Context) -> List[ParsedCommand]:
        statements = []
        for child in children:
            statements.extend(cls._statements(child, ctx))
        return statements

    @staticmethod
    def _enter_conditional(node, ctx: _Context) -> _Context:
        """Context for the inside of a loop or if.

        Variables it assigns are unknown from its start: a loop can reach any
        statement after any number of iterations, and after an if there is no
        telling which branch ran.
        """
        names = _assigned_names(node)
        if names is None:
            ctx.forget_all()
        else:
            for name in names:
                ctx.env[name] = None
        return ctx.with_conditional(True, in_compound=True)

    @classmethod
    def _conditional_statements(cls, node, ctx: _Context) -> List[ParsedCommand]:
        """while/until/if: every condition and branch, flattened in order."""
        inner = cls._enter_conditional(node, ctx)
        children = [p for p in node.parts if p.kind != "reservedword"]
        statements = cls._body_statements(children, inner)
        if node.kind != "if" and statements and _contains_cd(node):
            # A cd in an earlier iteration moves every later statement
            statements[0].location_unknown_before = True
        return statements

    @classmethod
    def _for_statements(cls, node, ctx: _Context) -> List[ParsedCommand]:
        """for VAR in ITEMS: the body once per literal item, else once with
        VAR unknown."""
        parts = node.parts
        var = parts[1].word
        reserved = [p.word if p.kind == "reservedword" else None for p in parts]
        do_index = reserved.index("do")
        has_in = len(parts) > 2 and reserved[2] == "in"
        words = [p for p in parts[3:do_index] if p.kind == "word"] if has_in else []
        body = [p for p in parts[do_index + 1 :] if p.kind != "reservedword"]

        statements: List[ParsedCommand] = []
        items: List[str] = []
        literal = has_in
        substitutions: List[ParsedCommand] = []
        for w in words:
            value, expanded, subs = cls._word(w, ctx)
            substitutions.extend(subs)
            raw = ctx.original[w.pos[0] : w.pos[1]]
            if expanded or any(c in raw for c in "*?[{~"):
                # Globs and brace expansion become other items at run time
                literal = False
            if value is not None:
                items.append(value)
        if substitutions:
            # for f in $(cmd): cmd runs once, before the loop
            ctx.spend()
            statements.append(
                ParsedCommand(
                    executable="",
                    group=[],
                    process_substitutions=substitutions,
                    original=ctx.original,
                    pos=node.pos,
                )
            )

        body_names = _assigned_names(body)
        reassigned = body_names is None or var in body_names
        inner = cls._enter_conditional(node, ctx)
        if literal and not reassigned and 0 < len(items) <= MAX_FOR_ITEMS:
            for item in items:
                inner.env[var] = item
                statements.extend(cls._body_statements(body, inner))
        else:
            inner.env[var] = None
            body_statements = cls._body_statements(body, inner)
            if body_statements and _contains_cd(node):
                # A cd in an earlier iteration moves every later statement
                body_statements[0].location_unknown_before = True
            statements.extend(body_statements)
        inner.env[var] = None
        return statements

    @classmethod
    def _word(
        cls, node, ctx: _Context
    ) -> Tuple[Optional[str], bool, List[ParsedCommand]]:
        """The value of a word node after the shell expands it.

        Returns (value, expanded, substitutions). value is None when the word
        expands to nothing, as an unquoted $(echo) does. expanded means the
        value is not known before running; substitutions are the $(...) and
        <(...) commands the word runs, each as a sequence of statements.
        """
        # bashlex's .word has shell quoting removed, so policies see the path
        # the shell will use: '/etc/passwd' -> /etc/passwd
        value = node.word
        substitutions = []
        # (start, end, value) of each part the shell replaces; None if unknown
        spans = []
        for sub in getattr(node, "parts", None) or []:
            if sub.kind == "commandsubstitution":
                substitution = cls._substitution(sub.command, ctx)
                substitutions.append(substitution)
                spans.append((sub.pos[0], sub.pos[1], _known_output(substitution)))
            elif sub.kind == "processsubstitution":
                substitutions.append(cls._substitution(sub.command, ctx))
            elif sub.kind == "parameter":
                known = ctx.env.get(sub.value) if _NAME.match(sub.value) else None
                spans.append((sub.pos[0], sub.pos[1], known))
            elif sub.kind == "tilde" and "HOME" in ctx.env:
                # ~ is $HOME, which the command itself changed
                spans.append((sub.pos[0], sub.pos[1], None))

        if not spans:
            return value, False, substitutions
        substituted = cls._substitute(node, spans, ctx)
        if substituted is None:
            return value, True, substitutions
        if substituted == "" and '"' not in ctx.original[node.pos[0] : node.pos[1]]:
            return None, False, substitutions
        return substituted, False, substitutions

    @staticmethod
    def _substitute(node, spans, ctx: _Context) -> Optional[str]:
        """Replace $X, ${X} and $(echo ...) with their known values.

        Returns None when a value is unknown or the quoting is anything but
        plain double quotes; the word is then treated as expanded.
        """
        raw = ctx.original[node.pos[0] : node.pos[1]]
        if "'" in raw or "\\" in raw or "IFS" in ctx.env:
            # A changed IFS splits values on other characters
            return None
        result = ""
        cursor = node.pos[0]
        for start, end, value in spans:
            if value is None or any(c in _UNSAFE_VALUE_CHARS for c in value):
                return None
            result += ctx.original[cursor:start] + value
            cursor = end
        result += ctx.original[cursor : node.pos[1]]
        return result.replace('"', "")

    @classmethod
    def _substitution(cls, command_node, ctx: _Context) -> ParsedCommand:
        """A $(...) or <(...) body: runs in a subshell."""
        return cls._sequence_node(
            cls._statements(command_node, ctx.subshell()), ctx.original
        )

    @classmethod
    def _parse_command_node(cls, node, ctx: _Context) -> ParsedCommand:
        """Parse a command node into ParsedCommand."""
        ctx.spend()

        parts = []
        redirects = []
        process_substitutions = []
        expanded_words = []
        assignments = []

        for part in node.parts:
            if part.kind == "word":
                value, expanded, subs = cls._word(part, ctx)
                process_substitutions.extend(subs)
                if value is None:
                    continue
                if expanded:
                    expanded_words.append(value)
                parts.append(value)
            elif part.kind == "assignment":
                # Prefix assignments (X=1 cmd) run their substitutions too
                value, expanded, subs = cls._word(part, ctx)
                process_substitutions.extend(subs)
                assignments.append((value, expanded))
            elif part.kind == "redirect":
                redirect_op = cls._get_redirect_operator(part)
                heredoc = getattr(part, "heredoc", None)
                if heredoc is not None and (
                    "$(" in heredoc.value or "`" in heredoc.value
                ):
                    raise ParseError(
                        "Command substitution in here-document not supported"
                    )
                # Handle both word nodes (with .pos) and file descriptors (int)
                if hasattr(part.output, "pos"):
                    target, expanded, subs = cls._word(part.output, ctx)
                    process_substitutions.extend(subs)
                    if target is None:
                        # Bash refuses an empty redirect target
                        target, expanded = part.output.word, True
                    redirects.append((redirect_op, target))
                    if expanded:
                        expanded_words.append(target)
                # Else: file descriptor

        if not parts:
            # Assignment-only statement: sets shell variables and runs only
            # its substitutions
            for value, expanded in assignments:
                ctx.assign(value, None if expanded else value.split("=", 1)[1])
            return ParsedCommand(
                executable="",
                group=[],
                redirects=redirects,
                process_substitutions=process_substitutions,
                original=ctx.original,
                pos=node.pos,
            )

        # First part is the executable
        executable = parts[0]
        remaining = parts[1:]
        cls._track_assignments(executable, remaining, expanded_words, ctx)

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
            # cd ~ and cd follow $HOME and $CDPATH; a changed one moves it
            location_unknown_after=executable == "cd"
            and (ctx.in_compound or "HOME" in ctx.env or "CDPATH" in ctx.env),
            original=ctx.original,
            pos=node.pos,
        )

    @staticmethod
    def _track_assignments(
        executable: str, words: List[str], expanded: List[str], ctx: _Context
    ) -> None:
        """Keep the known variables in step with builtins that set them."""
        if executable in _ENV_REPLACING:
            ctx.forget_all()
        elif executable in _DECLARING:
            # declare -n X=Y makes $X read Y: with any flag, values are unknown
            with_flags = any(word.startswith("-") for word in words)
            for word in words:
                if "=" in word:
                    known = not with_flags and word not in expanded
                    ctx.assign(word, word.split("=", 1)[1] if known else None)
        elif executable in _ASSIGNING:
            for word in words:
                ctx.assign(word, None)

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
