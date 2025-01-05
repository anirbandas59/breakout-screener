from httpx import AsyncClient
from fastapi.testclient import TestClient
from datetime import datetime
import pytest
from app.main import app
from app.models import BreakoutData
from app.utils import get_current_date


@pytest.mark.asyncio
async def test_get_data_pagination():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.get("/api/get_data?page=1&limit=10")

    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "data" in data
    assert "page" in data
    assert "limit" in data
    assert data["page"] == 1
    assert data["limit"] == 10


@pytest.mark.asyncio
async def test_generate_bodata_input_validation():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        # Invalid date format
        response = await client.post("/api/generate_bodata", json={
            "date": "2023-12-01",
            "pivot_val": 0.5
        })
        assert response.status_code == 500

        # Valid request
        response = await client.post("/api/generate_bodata", json={
            "date": "2023-12-01",
            "pivot_val": 0.5
        })
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_clear_chart_missing_records():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/clear_chart")

    assert response.status_code == 404
    assert "No record found for date" in response.json()["detail"]
