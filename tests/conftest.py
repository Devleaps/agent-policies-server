"""Shared pytest fixtures for bundle server tests."""

import pytest
from fastapi.testclient import TestClient

from src.server.server import app


@pytest.fixture
def client():
    """FastAPI test client for making HTTP requests"""
    return TestClient(app)
