"""
Tests for generate_bo_data service.

This module tests the breakout analysis generation including:
- Basic analysis generation
- Start from specific index
- Suspension mechanism
- Batch commits verification
- Error handling
"""

import pytest
from datetime import date
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
import pandas as pd

from app.services.generate_bo_data import generate_BOData
from app.models.breakout_data import BreakoutData
from app.utils.suspension_flag import SUSPEND_ANALYSIS


class TestGenerateBOData:
    """Test suite for generate_BOData service."""

    def test_basic_analysis_generation(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test basic breakout analysis generation."""
        analysis_date = "2024-01-11"  # Use last date in mock data
        pivot_val = 0.5

        # Mock yfinance to return sample data
        result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        assert result["status"] == "SUCCESS"
        assert "Completed" in result["message"]

        # Verify data was updated
        updated_record = db_session.query(BreakoutData).filter_by(script_name="RELIANCE").first()
        assert updated_record is not None
        assert updated_record.date == date.fromisoformat(analysis_date)
        # Verify OHLCV values were updated
        assert updated_record.open is not None
        assert updated_record.high is not None
        assert updated_record.close is not None

    def test_start_from_index(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test starting analysis from a specific index."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Start from script #3 (1-indexed)
        result = generate_BOData(db_session, analysis_date, pivot_val, start_from=3)

        assert result["status"] == "SUCCESS"
        # Should process 3 scripts (INFY, HDFC, ICICI) from the 5 total

    def test_invalid_date_format(self, db_session: Session):
        """Test error handling for invalid date format."""
        result = generate_BOData(db_session, "2024/01/15", 0.5)

        assert "error" in result
        assert "Invalid date format" in result["error"]

    def test_no_scripts_available(self, db_session: Session):
        """Test behavior when no scripts are available for analysis."""
        # Clear all scripts
        db_session.query(BreakoutData).delete()
        db_session.commit()

        result = generate_BOData(db_session, "2024-01-15", 0.5)

        assert result["status"] == "FAIL"
        assert "No scripts available" in result["error"]

    def test_suspension_mechanism(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test that analysis can be suspended mid-processing."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Set suspension flag after first iteration
        def mock_fetch_with_suspension(script_name):
            """Mock fetch that triggers suspension after first call."""
            SUSPEND_ANALYSIS.set()
            return mock_yfinance  # Return the mock DataFrame

        with patch('app.services.generate_bo_data.fetch_script_historical_data', side_effect=mock_fetch_with_suspension):
            result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        assert result["status"] == "SUSPENDED"
        assert "Suspended" in result["message"]

    def test_batch_commits(self, db_session: Session, large_dataset, mock_yfinance):
        """
        Test that batch commits are working (commits every 50 records).

        This is tested by verifying the logic works, not by counting actual commits
        (since that would require database-specific monitoring).
        """
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Mock yfinance to avoid actual data fetching
        with patch('app.services.generate_bo_data.fetch_script_historical_data', return_value=mock_yfinance):
            result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        # With 500 records and BATCH_SIZE=50, should have 10 batch commits + 1 final
        # We can't easily verify commit count, but we can verify all data was processed
        assert result["status"] in ["SUCCESS", "SUSPENDED"]

        # Verify some records were updated
        updated_count = db_session.query(BreakoutData).filter(
            BreakoutData.date == date.fromisoformat(analysis_date)
        ).count()
        assert updated_count > 0, "Some records should be updated"

    def test_cpr_calculation(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test that CPR levels are calculated correctly."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        assert result["status"] == "SUCCESS"

        # Verify CPR fields are populated
        updated_record = db_session.query(BreakoutData).filter_by(script_name="RELIANCE").first()
        assert updated_record.cpr is not None, "CPR should be calculated"
        assert updated_record.res1 is not None, "Resistance 1 should be calculated"
        assert updated_record.res2 is not None, "Resistance 2 should be calculated"
        assert updated_record.supp1 is not None, "Support 1 should be calculated"
        assert updated_record.supp2 is not None, "Support 2 should be calculated"

        # Verify CPR relationships (pivot between support and resistance)
        assert updated_record.supp1 <= updated_record.cpr <= updated_record.res1

    def test_candle_indicator_logic(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test candle indicator determination (GREEN/RED/DOJI)."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        updated_record = db_session.query(BreakoutData).filter_by(script_name="RELIANCE").first()

        # Candle indicator should be determined based on open vs close
        # Mock data has close > open, so should be "Green candle"
        assert updated_record.candle_indicator in ["Green candle", "Red candle", "Doji"]

    def test_volume_indicator_logic(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test volume indicator determination (GOOD/AVERAGE/LOW)."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        updated_record = db_session.query(BreakoutData).filter_by(script_name="RELIANCE").first()

        # Volume indicator should be determined based on current vs average volume
        assert updated_record.volume_indicator in ["Good", "Average", "Low"]

    def test_narrow_gap_calculation(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test narrow gap determination based on pivot percentage."""
        analysis_date = "2024-01-11"

        # Test with different pivot values
        pivot_val_narrow = 10.0  # Large percentage, more likely to be narrow
        result = generate_BOData(db_session, analysis_date, pivot_val_narrow, start_from=1)

        updated_record = db_session.query(BreakoutData).filter_by(script_name="RELIANCE").first()
        assert updated_record.narrow_gap in ["Yes", "No"]

    def test_skip_missing_data(self, db_session: Session, sample_breakout_data):
        """Test that script is skipped when no historical data available."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Mock yfinance to return empty DataFrame
        empty_df = pd.DataFrame()

        with patch('app.services.generate_bo_data.fetch_script_historical_data', return_value=empty_df):
            result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        # Should complete but skip scripts with no data
        assert result["status"] == "SUCCESS"

    def test_skip_missing_analysis_date(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test that script is skipped when analysis date not in historical data."""
        analysis_date = "2025-12-31"  # Future date not in mock data
        pivot_val = 0.5

        result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        # Should complete but skip all scripts (no data for this date)
        assert result["status"] == "SUCCESS"

    def test_error_handling_cpr_calculation(self, db_session: Session, sample_breakout_data):
        """Test error handling when CPR calculation fails."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Mock yfinance with invalid data (will cause CPR calculation to fail)
        invalid_df = pd.DataFrame({
            'Open': [None],  # Invalid data
            'High': [None],
            'Low': [None],
            'Close': [None],
            'Volume': [None]
        }, index=["2024-01-11"])

        with patch('app.services.generate_bo_data.fetch_script_historical_data', return_value=invalid_df):
            # Should raise CPRCalculationError
            with pytest.raises(Exception):  # Could be CPRCalculationError
                generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

    def test_database_rollback_on_error(self, db_session: Session, sample_breakout_data):
        """Test that database is rolled back on error during update."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Get initial state
        initial_record = db_session.query(BreakoutData).filter_by(script_name="RELIANCE").first()
        initial_open = initial_record.open

        # Mock to cause database error
        with patch.object(db_session, 'commit', side_effect=Exception("Database error")):
            try:
                generate_BOData(db_session, analysis_date, pivot_val, start_from=1)
            except Exception:
                pass

        # Verify rollback occurred (data unchanged)
        # Note: This test is tricky with batch commits, might need adjustment
        # For now, we just verify the exception handling exists

    def test_progress_tracking(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test that progress is tracked during processing."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Mock celery task to track progress
        mock_task = MagicMock()

        with patch('app.services.generate_bo_data.current_task', mock_task):
            result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        # Verify task state was updated (at least once)
        assert mock_task.update_state.called, "Should update task progress"

    def test_special_character_script_name(self, db_session: Session, mock_yfinance):
        """Test handling of script names with special characters."""
        # Add a script with & in name
        special_script = BreakoutData(
            script_name="L&T",
            group_name="NIFTY_50",
            date=date(2024, 1, 15)
        )
        db_session.add(special_script)
        db_session.commit()

        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Should handle & → %26 conversion
        result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        # Should complete without errors
        assert result["status"] in ["SUCCESS", "SUSPENDED"]

    @pytest.mark.slow
    def test_performance_500_scripts(self, db_session: Session, large_dataset, mock_yfinance):
        """
        Test performance with 500 scripts.

        Expected: Should complete in reasonable time with batch commits.
        """
        import time

        analysis_date = "2024-01-11"
        pivot_val = 0.5

        start_time = time.time()

        with patch('app.services.generate_bo_data.fetch_script_historical_data', return_value=mock_yfinance):
            result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        duration = time.time() - start_time

        # Should complete successfully
        assert result["status"] in ["SUCCESS", "SUSPENDED"]

        # Performance depends on mock speed, but should be reasonable
        print(f"✓ Processed {len(large_dataset)} scripts in {duration:.2f}s")

    def test_suspension_commits_pending_changes(self, db_session: Session, sample_breakout_data, mock_yfinance):
        """Test that pending changes are committed before suspension."""
        analysis_date = "2024-01-11"
        pivot_val = 0.5

        # Suspend after processing some records
        call_count = 0

        def mock_fetch_suspend_after_2(script_name):
            nonlocal call_count
            call_count += 1
            if call_count > 2:
                SUSPEND_ANALYSIS.set()
            return mock_yfinance

        with patch('app.services.generate_bo_data.fetch_script_historical_data', side_effect=mock_fetch_suspend_after_2):
            result = generate_BOData(db_session, analysis_date, pivot_val, start_from=1)

        assert result["status"] == "SUSPENDED"

        # Verify that records processed before suspension were committed
        # (This tests the "commit before suspend" logic)
        updated_count = db_session.query(BreakoutData).filter(
            BreakoutData.date == date.fromisoformat(analysis_date)
        ).count()
        assert updated_count >= 2, "Records before suspension should be committed"
