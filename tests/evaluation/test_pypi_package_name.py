"""
Tests that the PyPI lookup receives the bare package name, whatever
quoting, extras or version specifiers the command used.
"""

import pytest

from src.evaluation.handlers import rego_evaluator
from src.evaluation.parser import BashCommandParser
from src.evaluation.rego import package_base_name
from src.server.models import ToolUseEvent


@pytest.mark.parametrize(
    "word, expected",
    [
        ("httpx", "httpx"),
        ('"httpx"', "httpx"),
        ("'httpx'", "httpx"),
        ('"fastapi==0.118.0"', "fastapi"),
        # Quoted in part: the shell still passes fastapi==0.118.0
        ('"fastapi"==0.118.0', "fastapi"),
        ("fast'api'==0.118.0", "fastapi"),
        ("httpx==0.28.1", "httpx"),
        ("uvicorn[standard]", "uvicorn"),
        ('"uvicorn[standard]>=0.30"', "uvicorn"),
        ("requests~=2.31", "requests"),
        ("django!=4.0", "django"),
        ("pkg<2", "pkg"),
        ("pkg>1", "pkg"),
        ('"pkg; python_version>=\'3.8\'"', "pkg"),
        ("pkg @ https://example.com/pkg.whl", "pkg"),
    ],
)
def test_package_base_name(word, expected):
    assert package_base_name(word) == expected


@pytest.mark.parametrize(
    "command",
    [
        'uv add "fastapi==0.118.0"',
        "uv add fastapi==0.118.0",
        "uv add --dev 'fastapi[all]>=0.100'",
        'pip install "fastapi==0.118.0"',
    ],
)
def test_lookup_uses_bare_name(monkeypatch, command):
    looked_up = []
    monkeypatch.setattr(
        rego_evaluator, "_fetch_pypi_metadata", lambda name: looked_up.append(name)
    )
    event = ToolUseEvent(
        session_id="t",
        source_client="claude-code",
        tool_name="Bash",
        tool_is_bash=True,
        command=command,
    )
    parsed = BashCommandParser.parse(command)
    rego_evaluator._enrich_input(
        rego_evaluator._build_input_document(event, parsed), parsed
    )
    assert looked_up == ["fastapi"]
