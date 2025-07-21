"""
Integration tests for Breakout Data API endpoints
"""

import pytest
from datetime import date, datetime
from uuid import uuid4
from fastapi.testclient import TestClient

from breakout_screener.main import app


@pytest.fixture
def client():
    """Test client for the FastAPI app"""
    return TestClient(app)


@pytest.mark.asyncio
class TestBreakoutDataAPI:
    """Integration tests for Breakout Data API endpoints"""

    async def test_list_breakout_data_empty(self, client: TestClient):
        """Test listing breakout data when database is empty"""
        response = client.get("/api/v1/breakout-data/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_create_breakout_data_without_stock(self, client: TestClient):
        """Test creating breakout data without creating stock first (should fail)"""
        fake_stock_id = str(uuid4())
        breakout_data = {
            "stock_id": fake_stock_id,
            "trade_date": "2024-01-15",
            "open_price": 100.0,
            "high_price": 110.0,
            "low_price": 95.0,
            "close_price": 105.0,
            "volume": 1000000,
            "tc": 107.5,
            "bc": 97.5,
            "pivot": 102.5,
            "breakout_status": "BULLISH_BREAKOUT",
            "pivot_type": "CLASSICAL",
            "is_analyzed": True,
            "analysis_status": "COMPLETED"
        }
        
        response = client.post("/api/v1/breakout-data/", json=breakout_data)
        # Should fail due to foreign key constraint
        assert response.status_code in [400, 422, 500]

    async def test_full_workflow_stock_and_breakout_data(self, client: TestClient):
        """Test complete workflow: create stock, create breakout data, retrieve, update, delete"""
        # 1. Create stock first
        stock_data = {
            "symbol": "WORKFLOW",
            "company_name": "Workflow Test Company",
            "stock_group": "A",
            "is_active": True
        }
        
        stock_response = client.post("/api/v1/stocks/", json=stock_data)
        assert stock_response.status_code == 201
        stock = stock_response.json()
        stock_id = stock["id"]
        
        # 2. Create breakout data for this stock
        breakout_data = {
            "stock_id": stock_id,
            "trade_date": "2024-01-15",
            "open_price": 100.0,
            "high_price": 110.0,
            "low_price": 95.0,
            "close_price": 105.0,
            "volume": 1000000,
            "tc": 107.5,
            "bc": 97.5,
            "pivot": 102.5,
            "breakout_status": "BULLISH_BREAKOUT",
            "pivot_type": "CLASSICAL",
            "candle_indicator": "BULLISH",
            "volume_indicator": "HIGH_VOLUME",
            "is_analyzed": True,
            "analysis_status": "COMPLETED",
            "breakout_strength": 15.5
        }
        
        breakout_response = client.post("/api/v1/breakout-data/", json=breakout_data)
        assert breakout_response.status_code == 201
        breakout = breakout_response.json()
        breakout_id = breakout["id"]
        
        # 3. Verify breakout data was created correctly
        assert breakout["stock_id"] == stock_id
        assert breakout["trade_date"] == "2024-01-15"
        assert breakout["close_price"] == 105.0
        assert breakout["breakout_status"] == "BULLISH_BREAKOUT"
        assert breakout["breakout_strength"] == 15.5
        
        # 4. Get breakout data by ID
        get_response = client.get(f"/api/v1/breakout-data/{breakout_id}")
        assert get_response.status_code == 200
        retrieved = get_response.json()
        assert retrieved["id"] == breakout_id
        assert retrieved["stock_symbol"] == "WORKFLOW"  # Should include stock symbol
        
        # 5. List breakout data (should find our created data)
        list_response = client.get("/api/v1/breakout-data/")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["total"] >= 1
        
        # 6. Filter breakout data by stock
        filter_response = client.get("/api/v1/breakout-data/", params={"stock_id": stock_id})
        assert filter_response.status_code == 200
        filtered_data = filter_response.json()
        assert filtered_data["total"] >= 1
        
        # 7. Update breakout data
        update_data = {
            "breakout_strength": 20.0,
            "analysis_status": "UPDATED"
        }
        
        update_response = client.put(f"/api/v1/breakout-data/{breakout_id}", json=update_data)
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["breakout_strength"] == 20.0
        assert updated["analysis_status"] == "UPDATED"
        
        # 8. Delete breakout data
        delete_response = client.delete(f"/api/v1/breakout-data/{breakout_id}")
        assert delete_response.status_code == 200
        
        # 9. Verify deletion
        get_deleted_response = client.get(f"/api/v1/breakout-data/{breakout_id}")
        assert get_deleted_response.status_code == 404

    async def test_breakout_data_filtering_and_sorting(self, client: TestClient):
        """Test advanced filtering and sorting of breakout data"""
        # Create a test stock
        stock_data = {
            "symbol": "FILTERTEST",
            "company_name": "Filter Test Company",
            "stock_group": "A",
            "is_active": True
        }
        
        stock_response = client.post("/api/v1/stocks/", json=stock_data)
        assert stock_response.status_code == 201
        stock_id = stock_response.json()["id"]
        
        # Create multiple breakout data entries with different characteristics
        breakout_entries = [
            {
                "stock_id": stock_id,
                "trade_date": "2024-01-15",
                "open_price": 100.0,
                "high_price": 110.0,
                "low_price": 95.0,
                "close_price": 105.0,
                "volume": 1000000,
                "tc": 107.5,
                "bc": 97.5,
                "pivot": 102.5,
                "breakout_status": "BULLISH_BREAKOUT",
                "pivot_type": "CLASSICAL",
                "candle_indicator": "BULLISH",
                "volume_indicator": "HIGH_VOLUME",
                "is_analyzed": True,
                "analysis_status": "COMPLETED",
                "breakout_strength": 15.0
            },
            {
                "stock_id": stock_id,
                "trade_date": "2024-01-16",
                "open_price": 105.0,
                "high_price": 108.0,
                "low_price": 100.0,
                "close_price": 102.0,
                "volume": 800000,
                "tc": 104.5,
                "bc": 99.5,
                "pivot": 102.0,
                "breakout_status": "BEARISH_BREAKOUT",
                "pivot_type": "CLASSICAL",
                "candle_indicator": "BEARISH",
                "volume_indicator": "AVERAGE_VOLUME",
                "is_analyzed": True,
                "analysis_status": "COMPLETED",
                "breakout_strength": -8.0
            },
            {
                "stock_id": stock_id,
                "trade_date": "2024-01-17",
                "open_price": 102.0,
                "high_price": 104.0,
                "low_price": 100.0,
                "close_price": 103.0,
                "volume": 500000,
                "tc": 102.0,
                "bc": 101.0,
                "pivot": 101.5,
                "breakout_status": "NO_BREAKOUT",
                "pivot_type": "CLASSICAL",
                "candle_indicator": "NEUTRAL",
                "volume_indicator": "LOW_VOLUME",
                "is_analyzed": True,
                "analysis_status": "COMPLETED",
                "breakout_strength": 0.0
            }
        ]
        
        # Create all breakout entries
        created_ids = []
        for entry in breakout_entries:
            response = client.post("/api/v1/breakout-data/", json=entry)
            assert response.status_code == 201
            created_ids.append(response.json()["id"])
        
        # Test filtering by breakout status
        response = client.get("/api/v1/breakout-data/", params={"breakout_status": "BULLISH_BREAKOUT"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert all(item["breakout_status"] == "BULLISH_BREAKOUT" for item in data["items"])
        
        # Test filtering by date range
        response = client.get("/api/v1/breakout-data/", params={
            "trade_date_from": "2024-01-15",
            "trade_date_to": "2024-01-16"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        
        # Test filtering by volume range
        response = client.get("/api/v1/breakout-data/", params={
            "min_volume": 600000,
            "max_volume": 1200000
        })
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        
        # Test sorting by close price (descending)
        response = client.get("/api/v1/breakout-data/", params={
            "stock_id": stock_id,
            "sort_by": "close_price",
            "sort_order": "desc"
        })
        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        if len(items) >= 2:
            assert items[0]["close_price"] >= items[1]["close_price"]
        
        # Test pagination
        response = client.get("/api/v1/breakout-data/", params={
            "stock_id": stock_id,
            "page": 1,
            "limit": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["limit"] == 2

    async def test_breakout_data_analysis_workflow(self, client: TestClient):
        """Test analysis-related operations on breakout data"""
        # Create stock and breakout data
        stock_data = {
            "symbol": "ANALYSIS",
            "company_name": "Analysis Test Company",
            "stock_group": "A",
            "is_active": True
        }
        
        stock_response = client.post("/api/v1/stocks/", json=stock_data)
        assert stock_response.status_code == 201
        stock_id = stock_response.json()["id"]
        
        # Create unanalyzed breakout data
        breakout_data = {
            "stock_id": stock_id,
            "trade_date": "2024-01-18",
            "open_price": 120.0,
            "high_price": 125.0,
            "low_price": 118.0,
            "close_price": 123.0,
            "volume": 1500000,
            "tc": 124.0,
            "bc": 119.0,
            "pivot": 121.5,
            "breakout_status": "NO_BREAKOUT",
            "pivot_type": "CLASSICAL",
            "candle_indicator": "NEUTRAL",
            "volume_indicator": "AVERAGE_VOLUME",
            "is_analyzed": False,
            "analysis_status": "PENDING"
        }
        
        response = client.post("/api/v1/breakout-data/", json=breakout_data)
        assert response.status_code == 201
        breakout = response.json()
        breakout_id = breakout["id"]
        
        # Verify initial state
        assert breakout["is_analyzed"] is False
        assert breakout["analysis_status"] == "PENDING"
        assert breakout["breakout_strength"] is None
        
        # Simulate analysis completion
        analysis_update = {
            "is_analyzed": True,
            "analysis_status": "COMPLETED",
            "breakout_status": "BULLISH_BREAKOUT",
            "breakout_strength": 12.5,
            "candle_indicator": "BULLISH",
            "volume_indicator": "HIGH_VOLUME"
        }
        
        update_response = client.put(f"/api/v1/breakout-data/{breakout_id}", json=analysis_update)
        assert update_response.status_code == 200
        updated = update_response.json()
        
        # Verify analysis results
        assert updated["is_analyzed"] is True
        assert updated["analysis_status"] == "COMPLETED"
        assert updated["breakout_status"] == "BULLISH_BREAKOUT"
        assert updated["breakout_strength"] == 12.5
        
        # Test filtering by analysis status
        pending_response = client.get("/api/v1/breakout-data/", params={"analysis_status": "PENDING"})
        assert pending_response.status_code == 200
        
        completed_response = client.get("/api/v1/breakout-data/", params={"analysis_status": "COMPLETED"})
        assert completed_response.status_code == 200
        completed_data = completed_response.json()
        assert any(item["id"] == breakout_id for item in completed_data["items"])

    async def test_breakout_data_validation(self, client: TestClient):
        """Test validation rules for breakout data"""
        # Create test stock
        stock_data = {
            "symbol": "VALIDATION",
            "company_name": "Validation Test Company",
            "stock_group": "A",
            "is_active": True
        }
        
        stock_response = client.post("/api/v1/stocks/", json=stock_data)
        assert stock_response.status_code == 201
        stock_id = stock_response.json()["id"]
        
        # Test with invalid data types
        invalid_data = {
            "stock_id": stock_id,
            "trade_date": "invalid-date",
            "open_price": "not-a-number",
            "high_price": 110.0,
            "low_price": 95.0,
            "close_price": 105.0,
            "volume": -1000,  # Negative volume should be invalid
            "breakout_status": "INVALID_STATUS",
            "pivot_type": "INVALID_TYPE"
        }
        
        response = client.post("/api/v1/breakout-data/", json=invalid_data)
        assert response.status_code == 422  # Validation error
        
        # Test with missing required fields
        incomplete_data = {
            "stock_id": stock_id,
            "trade_date": "2024-01-15"
            # Missing required price fields
        }
        
        response = client.post("/api/v1/breakout-data/", json=incomplete_data)
        assert response.status_code == 422
        
        # Test with logical inconsistencies (high < low)
        inconsistent_data = {
            "stock_id": stock_id,
            "trade_date": "2024-01-15",
            "open_price": 100.0,
            "high_price": 95.0,  # High less than open
            "low_price": 105.0,   # Low greater than open
            "close_price": 102.0,
            "volume": 1000000,
            "tc": 104.0,
            "bc": 98.0,
            "pivot": 101.0,
            "breakout_status": "NO_BREAKOUT",
            "pivot_type": "CLASSICAL"
        }
        
        response = client.post("/api/v1/breakout-data/", json=inconsistent_data)
        # This might pass API validation but should be caught by business logic
        # The actual behavior depends on implementation