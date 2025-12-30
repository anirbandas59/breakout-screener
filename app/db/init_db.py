"""Database initialization script - creates all tables"""
import logging
from sqlalchemy import inspect
from app.db.session import engine, Base
from app.models.breakout_data import BreakoutData
from app.models.master_data import MasterBOData

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize database tables"""
    try:
        # Test connection
        with engine.connect() as conn:
            logger.info("✓ Database connection successful")

        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        logger.info(f"Existing tables: {existing_tables}")

        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        logger.info("✓ All tables created/verified")

        # Verify tables exist
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        required_tables = ['breakout_data', 'master_breakout_data']

        for table in required_tables:
            if table in tables:
                columns = [col['name'] for col in inspector.get_columns(table)]
                logger.info(f"✓ Table '{table}' exists with {len(columns)} columns")
                logger.info(f"  Columns: {', '.join(columns)}")
            else:
                logger.error(f"✗ Table '{table}' NOT FOUND")
                return False

        return True

    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    exit(0 if success else 1)
