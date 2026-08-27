"""Prove the corpus extraction is faithful: regenerate pytest assertions from
tests/corpus/extracted_bash.yaml and run them against the live server. Any
diff between this and the original tests/http/*.py suite would mean the
extraction changed behavior, which must never happen since the corpus is
meant to be an exact restatement of the same assertions in a different
format, not a new test suite.
"""

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from src.main import setup_all_policies
from src.server.server import app

setup_all_policies()


def load_corpus_cases():
    """Minimal hand-rolled YAML reader for this file's exact narrow shape
    (see scripts/extract_corpus.py's render_yaml) - avoids depending on
    PyYAML for a one-off verification script."""
    text = Path("tests/corpus/extracted_bash.yaml").read_text()
    cases = []
    current_bundles = ["universal"]
    current_bash = None
    current_expect = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("bundles:"):
            inner = stripped[len("bundles:") :].strip().strip("[]")
            current_bundles = [b.strip() for b in inner.split(",") if b.strip()]
        elif stripped.startswith("- bash:"):
            current_bash = ast.literal_eval(stripped[len("- bash:") :].strip())
        elif stripped.startswith("expect:"):
            current_expect = ast.literal_eval(stripped[len("expect:") :].strip())
            cases.append((current_bash, current_expect, current_bundles))
    return cases


def main():
    client = TestClient(app)
    base_event = {
        "workspace_root": "/workspace",
        "event": {
            "session_id": "corpus-verify-session",
            "transcript_path": "/tmp/transcript.jsonl",
            "cwd": "/workspace",
            "hook_event_name": "PreToolUse",
            "tool_name": "Bash",
            "tool_input": {"command": ""},
            "tool_use_id": "toolu_corpus_verify",
        },
        "bundles": ["universal"],
    }

    cases = load_corpus_cases()
    failures = []

    for i, (command, expect, bundles) in enumerate(cases):
        event = {
            **base_event,
            "bundles": bundles,
            "event": {
                **base_event["event"],
                "tool_input": {"command": command},
                "session_id": f"corpus-verify-session-{i}",
            },
        }
        response = client.post("/policy/claude-code/PreToolUse", json=event)
        data = response.json()
        actual_decision = data.get("hookSpecificOutput", {}).get("permissionDecision")

        if expect == "pass":
            if actual_decision is not None:
                failures.append((command, expect, actual_decision))
        else:
            if actual_decision != expect:
                failures.append((command, expect, actual_decision))

    print(f"{len(cases)} cases checked, {len(failures)} mismatches", file=sys.stderr)
    for command, expect, actual in failures:
        print(f"  MISMATCH: {command!r} expected {expect!r} got {actual!r}", file=sys.stderr)

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
