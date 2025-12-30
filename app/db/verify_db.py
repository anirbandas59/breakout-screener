"""Test script to verify connection and query"""
from app.db.session import SessionLocal
from app.models.breakout_data import BreakoutData
from app.models.master_data import MasterBOData

def verify_database():
    db = SessionLocal()
    try:
        # Test query on breakout_data
        count = db.query(BreakoutData).count()
        print(f"✓ breakout_data table accessible, {count} rows")

        # Test query on master_breakout_data
        count = db.query(MasterBOData).count()
        print(f"✓ master_breakout_data table accessible, {count} rows")

        return True
    except Exception as e:
        print(f"✗ Database verification failed: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = verify_database()
    exit(0 if success else 1)
