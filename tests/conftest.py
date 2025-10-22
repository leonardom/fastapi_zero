import pytest
from fastapi.testclient import TestClient

from fastapi_zero.app import app


@pytest.fixture
def client() -> TestClient:
    """Fixture to provide a TestClient for FastAPI app."""
    return TestClient(app)
