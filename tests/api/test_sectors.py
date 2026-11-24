import pytest
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_list_sectors():
    """Verify GET /api/v1/sectors returns 11 broad sectors."""
    response = client.get("/api/v1/sectors")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 11
    assert "sector" in data[0]
    assert "median_roe" in data[0]


def test_get_sector_constituents_unknown():
    """Verify GET /api/v1/sectors/UNKNOWN/companies returns HTTP 404."""
    response = client.get("/api/v1/sectors/NON_EXISTENT_SECTOR_ABC/companies")
    assert response.status_code == 404
