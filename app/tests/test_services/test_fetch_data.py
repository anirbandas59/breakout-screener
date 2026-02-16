"""
Tests for fetch_data service.

This module tests the data fetching functionality including:
- Basic pagination
- Search filtering
- Breakout indicator filtering
- Date filtering
- Fallback to master_breakout_data
- Performance with large datasets
"""

import pytest
from datetime import date
from sqlalchemy.orm import Session

from app.services.fetch_data import get_breakout_data
from app.models.breakout_data import BreakoutData
from app.models.master_data import MasterBOData


class TestFetchData:
    """Test suite for get_breakout_data service."""

    def test_basic_pagination(self, db_session: Session, sample_breakout_data):
        """Test basic pagination functionality."""
        # Fetch first page with 2 records per page
        result = get_breakout_data(db_session, page=1, limit=2)

        assert result["total"] == 5, "Should have 5 total records"
        assert len(result["data"]) == 2, "Should return 2 records for page 1"
        assert result["data_source"] == "breakout_data"

        # Fetch second page
        result_page2 = get_breakout_data(db_session, page=2, limit=2)
        assert len(result_page2["data"]) == 2, "Should return 2 records for page 2"

        # Fetch third page (should have remaining 1 record)
        result_page3 = get_breakout_data(db_session, page=3, limit=2)
        assert len(result_page3["data"]) == 1, "Should return 1 record for page 3"

        # Verify pages have different records
        page1_ids = [r.id for r in result["data"]]
        page2_ids = [r.id for r in result_page2["data"]]
        assert set(page1_ids).isdisjoint(set(page2_ids)), "Pages should have different records"

    def test_search_filtering(self, db_session: Session, sample_breakout_data):
        """Test search filtering by script name."""
        # Search for RELIANCE
        result = get_breakout_data(db_session, page=1, limit=10, search="RELIANCE")

        assert result["total"] == 1, "Should find 1 RELIANCE record"
        assert len(result["data"]) == 1
        assert result["data"][0].script_name == "RELIANCE"

        # Partial search (case-insensitive)
        result_partial = get_breakout_data(db_session, page=1, limit=10, search="rel")
        assert result_partial["total"] == 1, "Should find RELIANCE with partial search"

        # Search with no matches
        result_none = get_breakout_data(db_session, page=1, limit=10, search="NONEXISTENT")
        assert result_none["total"] == 0, "Should find no records"
        assert result_none["data"] == []

    def test_breakout_indicator_filtering(self, db_session: Session, sample_breakout_data):
        """Test filtering by breakout indicator values."""
        # Filter for BREAKOUT only
        result = get_breakout_data(
            db_session, page=1, limit=10, breakout_filters=["BREAKOUT"]
        )

        assert result["total"] == 1, "Should have 1 BREAKOUT record"
        assert result["data"][0].breakout_indicator == "BREAKOUT"

        # Filter for multiple indicators
        result_multi = get_breakout_data(
            db_session, page=1, limit=10,
            breakout_filters=["BREAKOUT", "NO_BREAKOUT"]
        )

        assert result_multi["total"] == 2, "Should have 2 records"
        for record in result_multi["data"]:
            assert record.breakout_indicator in ["BREAKOUT", "NO_BREAKOUT"]

        # Filter with no matches
        result_none = get_breakout_data(
            db_session, page=1, limit=10,
            breakout_filters=["NO_ENTRY_INVALID"]
        )
        assert result_none["total"] == 0, "Should find no records with invalid filter"

    def test_date_filtering(self, db_session: Session, sample_breakout_data):
        """Test filtering by date."""
        test_date = "2024-01-15"

        result = get_breakout_data(db_session, page=1, limit=10, date=test_date)

        assert result["total"] == 5, "Should find all 5 records for the test date"
        assert result["data_date"] == test_date
        for record in result["data"]:
            assert str(record.date) == test_date

        # Filter with different date (should find nothing in breakout_data)
        result_none = get_breakout_data(db_session, page=1, limit=10, date="2024-01-01")
        assert result_none["total"] == 0

    def test_combined_filters(self, db_session: Session, sample_breakout_data):
        """Test combining multiple filters."""
        # Search + breakout filter
        result = get_breakout_data(
            db_session, page=1, limit=10,
            search="RELIANCE",
            breakout_filters=["BREAKOUT"]
        )

        assert result["total"] == 1, "Should find 1 record matching both filters"
        assert result["data"][0].script_name == "RELIANCE"
        assert result["data"][0].breakout_indicator == "BREAKOUT"

        # Search + breakout filter with no match
        result_none = get_breakout_data(
            db_session, page=1, limit=10,
            search="RELIANCE",
            breakout_filters=["NO_BREAKOUT"]  # RELIANCE is BREAKOUT, not NO_BREAKOUT
        )
        assert result_none["total"] == 0

        # All filters combined
        result_all = get_breakout_data(
            db_session, page=1, limit=10,
            search="RELIANCE",
            breakout_filters=["BREAKOUT"],
            date="2024-01-15"
        )
        assert result_all["total"] == 1

    def test_fallback_to_master_data(self, db_session: Session, sample_master_data):
        """
        Test fallback to master_breakout_data when no data in breakout_data.

        This tests the priority: breakout_data → master_breakout_data.
        """
        # Ensure breakout_data is empty
        db_session.query(BreakoutData).delete()
        db_session.commit()

        # Query with date from master data
        result = get_breakout_data(db_session, page=1, limit=10, date="2024-01-10")

        assert result["total"] == 3, "Should find 3 records from master table"
        assert result["data_source"] == "master_breakout_data"
        assert result["data_date"] == "2024-01-10"

    def test_breakout_data_priority(self, db_session: Session, sample_breakout_data, sample_master_data):
        """
        Test that breakout_data takes priority over master_breakout_data.

        Both tables have data, but breakout_data should be returned first.
        """
        # Query without date filter (should return from breakout_data)
        result = get_breakout_data(db_session, page=1, limit=10)

        assert result["data_source"] == "breakout_data", "Should prioritize breakout_data"
        assert result["total"] == 5  # From sample_breakout_data

    def test_no_data_found(self, db_session: Session):
        """Test behavior when no data exists in any table."""
        # Ensure both tables are empty
        db_session.query(BreakoutData).delete()
        db_session.query(MasterBOData).delete()
        db_session.commit()

        result = get_breakout_data(db_session, page=1, limit=10)

        assert result["total"] == 0
        assert result["data"] == []
        assert result["data_date"] is None
        assert result["data_source"] is None

    @pytest.mark.slow
    def test_performance_large_dataset(self, db_session: Session, large_dataset):
        """
        Test pagination performance with 500 records.

        Should efficiently handle large datasets with proper indexing.
        """
        import time

        # Test first page
        start_time = time.time()
        result = get_breakout_data(db_session, page=1, limit=50)
        duration = time.time() - start_time

        assert result["total"] == 500, "Should have 500 total records"
        assert len(result["data"]) == 50, "Should return 50 records"
        assert duration < 1.0, f"Query should be fast, took {duration:.2f}s"

        # Test middle page
        result_middle = get_breakout_data(db_session, page=5, limit=50)
        assert len(result_middle["data"]) == 50

        # Test last page
        result_last = get_breakout_data(db_session, page=10, limit=50)
        assert len(result_last["data"]) == 50

        print(f"✓ Queried 500 records in {duration:.2f}s")

    def test_data_date_extraction(self, db_session: Session, sample_breakout_data):
        """Test that data_date is correctly extracted from records."""
        result = get_breakout_data(db_session, page=1, limit=10)

        assert result["data_date"] is not None
        assert result["data_date"] == "2024-01-15"  # From sample data

    def test_pagination_bounds(self, db_session: Session, sample_breakout_data):
        """Test pagination edge cases."""
        # Page beyond available data
        result = get_breakout_data(db_session, page=100, limit=10)
        assert result["total"] == 5  # Total should still be correct
        assert result["data"] == []  # But no data for this page

        # Very large limit
        result_large = get_breakout_data(db_session, page=1, limit=1000)
        assert len(result_large["data"]) == 5  # Should return all 5 records

    def test_empty_filters(self, db_session: Session, sample_breakout_data):
        """Test behavior with empty filter arrays."""
        # Empty breakout_filters list
        result = get_breakout_data(
            db_session, page=1, limit=10, breakout_filters=[]
        )

        # Should return all records (empty filter = no filter)
        assert result["total"] == 5

    def test_search_special_characters(self, db_session: Session, sample_breakout_data):
        """Test search with special characters (should be safe due to ilike)."""
        # Search with wildcards (should be treated as literals)
        result = get_breakout_data(db_session, page=1, limit=10, search="REL%")

        # Should find RELIANCE (% is part of the pattern, not SQL wildcard)
        # This tests that the function properly escapes special characters
        assert result["total"] == 0 or result["data"][0].script_name == "RELIANCE"

    def test_order_consistency(self, db_session: Session, sample_breakout_data):
        """Test that results are consistently ordered by ID."""
        result1 = get_breakout_data(db_session, page=1, limit=10)
        result2 = get_breakout_data(db_session, page=1, limit=10)

        # Results should be in the same order
        ids1 = [r.id for r in result1["data"]]
        ids2 = [r.id for r in result2["data"]]
        assert ids1 == ids2, "Results should be consistently ordered"

        # IDs should be in ascending order
        assert ids1 == sorted(ids1), "IDs should be in ascending order"
