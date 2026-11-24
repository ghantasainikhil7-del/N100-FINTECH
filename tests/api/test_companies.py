import pytest
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_list_companies_success():
    """Verify GET /api/v1/companies returns a list of company records."""
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]


def test_get_valid_company_profile():
    """Verify GET /api/v1/companies/TCS returns profile data."""
    response = client.get("/api/v1/companies/TCS")
    assert response.status_code == 200
    data = response.json()
    assert "company" in data or "id" in data


def test_get_invalid_company_profile():
    """Verify GET /api/v1/companies/INVALID returns HTTP 404."""
    response = client.get("/api/v1/companies/INVALID_TICKER_XYZ")
    assert response.status_code == 404
