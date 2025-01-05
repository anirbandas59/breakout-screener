from app.main import app
from fastapi.testclient import TestClient
from json import load
from httpx import AsyncClient
import pytest
import sys
import os
from dotenv import load_dotenv

print(f"{sys.path} =======> \n")

load_dotenv()

# print(settings.model_dump(), "============>>")


@pytest.mark.asyncio
async def test_get_data():
    async with AsyncClient(base_url="http://localhost:8000/") as client:
        response = await client.post("/api/get_data")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_fetch_script_symbols():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/fetch_script_symbols")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_generate_bodata():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/generate_bodata")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_suspend_action():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/suspend_action")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_clear_chart():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/clear_chart")
    assert response.status_code == 200
    assert "message" in response.json()


@pytest.mark.asyncio
async def test_clear_complete_data():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/api/clear_complete_data")
    assert response.status_code == 200
    assert "message" in response.json()
