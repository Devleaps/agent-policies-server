"""Test heredoc command parsing."""
import pytest
from src.evaluation.parser import BashCommandParser, ParseError


def test_heredoc_incomplete_raises_error():
    """Incomplete heredoc raises ParseError."""
    with pytest.raises(ParseError):
        BashCommandParser.parse("cat > /tmp/test.py << 'EOF'")


def test_heredoc_variants_unparseable():
    """Heredoc variants without content can't be parsed."""
    test_cases = [
        "cat > output.txt <<EOF",
        "cat > /tmp/test.py <<'EOF'",
        "cat >> log.txt <<EOF",
    ]

    for cmd_str in test_cases:
        with pytest.raises(ParseError):
            BashCommandParser.parse(cmd_str)


def test_multiple_redirects_with_heredoc():
    """Test command with both input and output redirects."""
    cmd_str = "sort < input.txt > output.txt"
    cmd = BashCommandParser.parse(cmd_str)

    assert cmd.executable == "sort"
    assert len(cmd.redirects) == 2
