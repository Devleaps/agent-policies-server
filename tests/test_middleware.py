import pytest
from src import universal
from src.universal.timeout_middleware import strip_timeout_prefix_middleware
from src.universal.time_middleware import strip_time_prefix_middleware


def test_timeout_basic(bash_event):
    result = list(strip_timeout_prefix_middleware(bash_event("timeout 30 pytest")))
    assert len(result) == 1
    assert result[0].command == "pytest"


def test_timeout_with_flags(bash_event):
    result = list(strip_timeout_prefix_middleware(bash_event("timeout -s KILL 60 python script.py")))
    assert len(result) == 1
    assert result[0].command == "python script.py"


def test_timeout_with_time_units(bash_event):
    result = list(strip_timeout_prefix_middleware(bash_event("timeout 5m npm test")))
    assert len(result) == 1
    assert result[0].command == "npm test"


def test_timeout_passthrough(bash_event):
    result = list(strip_timeout_prefix_middleware(bash_event("pytest")))
    assert len(result) == 1
    assert result[0].command == "pytest"


def test_time_basic(bash_event):
    result = list(strip_time_prefix_middleware(bash_event("time pytest")))
    assert len(result) == 1
    assert result[0].command == "pytest"


def test_time_with_flags(bash_event):
    result = list(strip_time_prefix_middleware(bash_event("time -p terraform plan")))
    assert len(result) == 1
    assert result[0].command == "terraform plan"


def test_time_passthrough(bash_event):
    result = list(strip_time_prefix_middleware(bash_event("pytest")))
    assert len(result) == 1
    assert result[0].command == "pytest"


def test_all_middleware_registered():
    assert hasattr(universal, 'all_middleware')
    assert len(universal.all_middleware) >= 3
