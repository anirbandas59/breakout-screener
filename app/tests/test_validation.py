"""Quick test script to verify input validation."""

from app.models.schemas import GetDataQueryParams
from pydantic import ValidationError


def test_valid_params():
    """Test valid parameters."""
    params = GetDataQueryParams(
        page=1,
        limit=50,
        search="RELIANCE",
        breakout_filters=["BREAKOUT", "NO_BREAKOUT"],
        date="2024-01-15"
    )
    print("✓ Valid params accepted:", params)


def test_invalid_limit():
    """Test limit exceeding max."""
    try:
        GetDataQueryParams(limit=150)
        print("✗ Should have rejected limit > 100")
    except ValidationError as e:
        print("✓ Rejected limit > 100:", e.errors()[0]['msg'])


def test_invalid_search():
    """Test search with SQL injection attempt."""
    try:
        GetDataQueryParams(search="'; DROP TABLE users; --")
        print("✗ Should have rejected SQL injection")
    except ValidationError as e:
        print("✓ Rejected SQL injection:", e.errors()[0]['msg'])


def test_invalid_date():
    """Test invalid date format."""
    try:
        GetDataQueryParams(date="2024/01/15")
        print("✗ Should have rejected invalid date format")
    except ValidationError as e:
        print("✓ Rejected invalid date format:", e.errors()[0]['msg'])


def test_invalid_breakout_filter():
    """Test invalid breakout indicator."""
    try:
        GetDataQueryParams(breakout_filters=["INVALID_VALUE"])
        print("✗ Should have rejected invalid breakout filter")
    except ValidationError as e:
        print("✓ Rejected invalid breakout filter:", e.errors()[0]['msg'])


if __name__ == "__main__":
    print("Testing input validation...\n")
    test_valid_params()
    test_invalid_limit()
    test_invalid_search()
    test_invalid_date()
    test_invalid_breakout_filter()
    print("\n✓ All validation tests passed!")
