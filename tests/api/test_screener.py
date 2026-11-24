import pytest
pytest.importorskip("httpx")
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_screener_valid_filter():
    """Verify screener with min_roe filter returns HTTP 200 and matches criteria."""
    response = client.get("/api/v1/screener?min_roe=15")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    for co in data:
        if "return_on_equity_pct" in co and co["return_on_equity_pct"] is not None:
            assert co["return_on_equity_pct"] >= 15.0


def test_screener_invalid_param_error():
    """Verify screener returns HTTP 400 for negative max_de or invalid roe."""
    response = client.get("/api/v1/screener?max_de=-2.0")
    assert response.status_code == 400
