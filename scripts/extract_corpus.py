"""Mechanically extract check_policy(client, base_event, cmd, expected) calls
from tests/http/*.py into a declarative YAML corpus.

Only the uniform one-liner form is extracted here - stateful/sequential
tests (session flags, demo bundle selection) and the parser's own test suite
are intentionally out of scope; they get hand-ported separately since they
don't fit this single-step shape.

Writes YAML by hand rather than depending on PyYAML: the output shape is a
narrow, fixed structure (list of {name, bundles, steps: [{bash, expect}]})
and every string value is a single-line bash command or a plain identifier,
so a minimal quoting scheme covers it without needing a general-purpose
YAML library as a dependency for a one-off dev script.
"""

import ast
import sys
from pathlib import Path


def yaml_scalar(value: str) -> str:
    """Quote a string as a YAML double-quoted scalar, escaping backslashes
    and double quotes. Safe for any single-line string, including ones
    containing '#', ':', or other YAML-significant characters that would
    otherwise require careful unquoted-scalar handling."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _is_base_event_subscript_assign(stmt, *keys):
    """Match `base_event["k1"]["k2"] = <constant>` for the given key path,
    returning the assigned constant, or None if stmt doesn't match."""
    if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
        return None
    target = stmt.targets[0]
    remaining = list(keys)
    while remaining and isinstance(target, ast.Subscript):
        key = remaining.pop()
        if not (isinstance(target.slice, ast.Constant) and target.slice.value == key):
            return None
        target = target.value
    if remaining or not (isinstance(target, ast.Name) and target.id == "base_event"):
        return None
    if isinstance(stmt.value, ast.Constant):
        return stmt.value.value
    if isinstance(stmt.value, ast.List) and all(isinstance(e, ast.Constant) for e in stmt.value.elts):
        return [e.value for e in stmt.value.elts]
    return None


def _is_base_event_context_mutation(stmt):
    """Detect base_event["home"|"workspace_root"] or base_event["event"]["cwd"]
    assignments, or monkeypatch.setenv/base_event.pop calls - any of which
    make a test's outcome depend on context this extractor doesn't model.
    Cases inside such a function are skipped rather than mis-extracted with
    the wrong (default) workspace context."""
    if _is_base_event_subscript_assign(stmt, "home") is not None:
        return True
    if _is_base_event_subscript_assign(stmt, "workspace_root") is not None:
        return True
    if _is_base_event_subscript_assign(stmt, "event", "cwd") is not None:
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        call = stmt.value
        if isinstance(call.func, ast.Attribute):
            if call.func.attr in ("setenv", "pop", "delenv"):
                return True
    return False


def extract_calls(source: str, filename: str):
    tree = ast.parse(source, filename=filename)
    cases = []

    for func_node in ast.walk(tree):
        if not isinstance(func_node, ast.FunctionDef) or not func_node.name.startswith("test_"):
            continue

        current_bundles = None
        skip_function = False

        for stmt in ast.walk(func_node):
            if isinstance(stmt, ast.FunctionDef) and stmt is not func_node:
                continue  # don't descend into nested defs (there are none, but be safe)

            if _is_base_event_context_mutation(stmt):
                skip_function = True

            bundles_value = _is_base_event_subscript_assign(stmt, "bundles")
            if bundles_value is not None:
                current_bundles = bundles_value

            if not (isinstance(stmt, ast.Call) and isinstance(stmt.func, ast.Name) and stmt.func.id == "check_policy"):
                continue

            args = stmt.args
            if len(args) < 4:
                continue

            command_node = args[2]
            expected_node = args[3]

            if not isinstance(command_node, ast.Constant) or not isinstance(command_node.value, str):
                continue
            if not isinstance(expected_node, ast.Constant):
                continue

            expected_value = expected_node.value
            cases.append(
                {
                    "command": command_node.value,
                    "expect": expected_value if expected_value is not None else "pass",
                    "bundles": current_bundles or ["universal"],
                    "skip": skip_function,
                }
            )

    return [c for c in cases if not c["skip"]]


def render_yaml(cases_with_source) -> str:
    lines = []
    for case in cases_with_source:
        name = f"{case['source']}: {case['command']}"
        bundles_str = ", ".join(case["bundles"])
        lines.append(f"- name: {yaml_scalar(name)}")
        lines.append(f"  bundles: [{bundles_str}]")
        lines.append("  steps:")
        lines.append(f"    - bash: {yaml_scalar(case['command'])}")
        lines.append(f"      expect: {yaml_scalar(case['expect'])}")
    return "\n".join(lines) + "\n"


def main():
    tests_dir = Path("tests/http")
    all_cases = []

    for path in sorted(tests_dir.glob("*.py")):
        source = path.read_text()
        cases = extract_calls(source, str(path))
        for case in cases:
            case["source"] = path.name
            all_cases.append(case)

    print(f"Extracted {len(all_cases)} cases", file=sys.stderr)

    out_path = Path("tests/corpus/extracted_bash.yaml")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_yaml(all_cases))

    print(f"Wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
