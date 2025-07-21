"""
Integration tests for Stock API endpoints
"""

import pytest
from uuid import UUID
from fastapi.testclient import TestClient
from httpx import AsyncClient

from breakout_screener.main import app


@pytest.fixture
def client():
    """Test client for the FastAPI app"""
    return TestClient(app)


@pytest.mark.asyncio
class TestStocksAPI:
    """Integration tests for Stock API endpoints"""

    async def test_health_check(self, client: TestClient):
        """Test API health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_list_stocks_empty(self, client: TestClient):
        """Test listing stocks when database is empty"""
        response = client.get("/api/v1/stocks/")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []
        assert data["page"] == 1
        assert data["limit"] == 50

    async def test_create_stock_success(self, client: TestClient):
        """Test successful stock creation"""
        stock_data = {
            "symbol": "TESTSTOCK",
            "company_name": "Test Company Ltd",
            "stock_group": "A",
            "sector": "Technology",
            "is_active": True
        }
        
        response = client.post("/api/v1/stocks/", json=stock_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["symbol"] == "TESTSTOCK"
        assert data["company_name"] == "Test Company Ltd"
        assert data["stock_group"] == "A"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_stock_duplicate_symbol(self, client: TestClient):
        """Test creating stock with duplicate symbol"""
        stock_data = {
            "symbol": "DUPLICATE",
            "company_name": "First Company",
            "stock_group": "A",
            "is_active": True
        }
        
        # Create first stock
        response1 = client.post("/api/v1/stocks/", json=stock_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        stock_data["company_name"] = "Second Company"
        response2 = client.post("/api/v1/stocks/", json=stock_data)
        assert response2.status_code == 409
        assert "already exists" in response2.json()["detail"]

    async def test_get_stock_by_id_success(self, client: TestClient):
        """Test retrieving stock by ID"""
        # Create a stock first
        stock_data = {
            "symbol": "GETTEST",
            "company_name": "Get Test Company",
            "stock_group": "A",
            "is_active": True
        }
        
        create_response = client.post("/api/v1/stocks/", json=stock_data)
        assert create_response.status_code == 201
        created_stock = create_response.json()
        stock_id = created_stock["id"]
        
        # Get the stock by ID
        response = client.get(f"/api/v1/stocks/{stock_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == stock_id
        assert data["symbol"] == "GETTEST"
        assert data["company_name"] == "Get Test Company"

    async def test_get_stock_by_id_not_found(self, client: TestClient):
        """Test getting non-existent stock by ID"""
        fake_uuid = "550e8400-e29b-41d4-a716-446655440000"
        response = client.get(f"/api/v1/stocks/{fake_uuid}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_get_stock_by_symbol_success(self, client: TestClient):
        """Test retrieving stock by symbol"""
        # Create a stock first
        stock_data = {
            "symbol": "SYMBOLTEST",
            "company_name": "Symbol Test Company",
            "stock_group": "B",
            "is_active": True
        }
        
        create_response = client.post("/api/v1/stocks/", json=stock_data)
        assert create_response.status_code == 201
        
        # Get by symbol
        response = client.get("/api/v1/stocks/symbol/SYMBOLTEST")
        assert response.status_code == 200
        
        data = response.json()
        assert data["symbol"] == "SYMBOLTEST"
        assert data["company_name"] == "Symbol Test Company"

    async def test_get_stock_by_symbol_not_found(self, client: TestClient):
        """Test getting non-existent stock by symbol"""
        response = client.get("/api/v1/stocks/symbol/NONEXISTENT")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    async def test_update_stock_success(self, client: TestClient):
        """Test successful stock update"""
        # Create a stock first
        stock_data = {
            "symbol": "UPDATETEST",
            "company_name": "Original Company",
            "stock_group": "A",
            "is_active": True
        }
        
        create_response = client.post("/api/v1/stocks/", json=stock_data)
        assert create_response.status_code == 201
        created_stock = create_response.json()
        stock_id = created_stock["id"]
        
        # Update the stock
        update_data = {
            "company_name": "Updated Company Name",
            "sector": "Updated Sector",
            "is_active": False
        }
        
        response = client.put(f"/api/v1/stocks/{stock_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["company_name"] == "Updated Company Name"
        assert data["sector"] == "Updated Sector"
        assert data["is_active"] is False
        assert data["symbol"] == "UPDATETEST"  # Should remain unchanged

    async def test_delete_stock_success(self, client: TestClient):
        """Test successful stock deletion"""
        # Create a stock first
        stock_data = {
            "symbol": "DELETETEST",
            "company_name": "Delete Test Company",
            "stock_group": "A",
            "is_active": True
        }
        
        create_response = client.post("/api/v1/stocks/", json=stock_data)
        assert create_response.status_code == 201
        created_stock = create_response.json()
        stock_id = created_stock["id"]
        
        # Delete the stock
        response = client.delete(f"/api/v1/stocks/{stock_id}")
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/stocks/{stock_id}")
        assert get_response.status_code == 404

    async def test_search_stocks(self, client: TestClient):
        """Test stock search functionality"""
        # Create test stocks
        stocks_data = [
            {
                "symbol": "SEARCH1",
                "company_name": "Search Test Company One",
                "stock_group": "A",
                "is_active": True
            },
            {
                "symbol": "SEARCH2",
                "company_name": "Search Test Company Two",
                "stock_group": "B",
                "is_active": True
            },
            {
                "symbol": "OTHER",
                "company_name": "Other Company",
                "stock_group": "A",
                "is_active": False
            }
        ]
        
        # Create stocks
        for stock_data in stocks_data:
            response = client.post("/api/v1/stocks/", json=stock_data)
            assert response.status_code == 201
        
        # Search by symbol pattern
        response = client.get("/api/v1/stocks/search/", params={"query": "SEARCH"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Search by company name
        response = client.get("/api/v1/stocks/search/", params={"query": "Test Company"})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # Search inactive stocks
        response = client.get("/api/v1/stocks/search/", params={
            "query": "OTHER",
            "active_only": False
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    async def test_list_stocks_with_filters(self, client: TestClient):
        """Test stock listing with filters and pagination"""
        # Create test stocks with different attributes
        stocks_data = [
            {
                "symbol": "FILTER1",
                "company_name": "Filter Company A",
                "stock_group": "A",
                "sector": "Technology",
                "is_active": True
            },
            {
                "symbol": "FILTER2",
                "company_name": "Filter Company B",
                "stock_group": "B",
                "sector": "Finance",
                "is_active": True
            },
            {
                "symbol": "FILTER3",
                "company_name": "Filter Company C",
                "stock_group": "A",
                "sector": "Technology",
                "is_active": False
            }
        ]
        
        # Create stocks
        for stock_data in stocks_data:
            response = client.post("/api/v1/stocks/", json=stock_data)
            assert response.status_code == 201
        
        # Filter by stock group
        response = client.get("/api/v1/stocks/", params={"stock_group": "A"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2  # At least our test stocks
        
        # Filter by sector
        response = client.get("/api/v1/stocks/", params={"sector": "Technology"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        
        # Filter by active status
        response = client.get("/api/v1/stocks/", params={"is_active": True})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        
        # Test pagination
        response = client.get("/api/v1/stocks/", params={"page": 1, "limit": 2})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2
        assert data["limit"] == 2

    async def test_stock_summary(self, client: TestClient):
        """Test stock summary statistics"""
        response = client.get("/api/v1/stocks/summary/")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_stocks" in data
        assert "active_stocks" in data
        assert "inactive_stocks" in data
        assert "groups_breakdown" in data
        assert "sectors_breakdown" in data
        assert "market_cap_stats" in data

    async def test_bulk_create_stocks(self, client: TestClient):
        """Test bulk stock creation"""
        bulk_data = {
            "stocks": [
                {
                    "symbol": "BULK1",
                    "company_name": "Bulk Company 1",
                    "stock_group": "A",
                    "is_active": True
                },
                {
                    "symbol": "BULK2",
                    "company_name": "Bulk Company 2",
                    "stock_group": "B",
                    "is_active": True
                },
                {
                    "symbol": "BULK3",
                    "company_name": "Bulk Company 3",
                    "stock_group": "A",
                    "is_active": False
                }
            ]
        }
        
        response = client.post("/api/v1/stocks/bulk/", json=bulk_data)
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
        
        # Verify all stocks were created
        for i, stock in enumerate(data):
            assert stock["symbol"] == f"BULK{i+1}"
            assert "id" in stock

    async def test_api_validation_errors(self, client: TestClient):
        """Test API validation error handling"""
        # Missing required fields
        response = client.post("/api/v1/stocks/", json={})
        assert response.status_code == 422
        
        # Invalid data types
        invalid_data = {
            "symbol": "",  # Empty symbol
            "company_name": "Test",
            "stock_group": "INVALID_GROUP",
            "is_active": "not_boolean"
        }
        
        response = client.post("/api/v1/stocks/", json=invalid_data)
        assert response.status_code == 422
        
        # Invalid UUID for get/update/delete operations
        response = client.get("/api/v1/stocks/invalid-uuid")
        assert response.status_code == 422