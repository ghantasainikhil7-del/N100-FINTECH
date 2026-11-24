import pytest
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_health_check_status_code():
    """Verify GET /api/v1/health returns HTTP 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_check_payload():
    """Verify health response structure has status=ok and db_row_counts."""
    response = client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "db_row_counts" in data
    assert isinstance(data["db_row_counts"], dict)
