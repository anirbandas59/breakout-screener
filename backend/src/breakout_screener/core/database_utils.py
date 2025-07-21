"""
Database utilities for migration and management
"""

from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .config import config
from .logging import get_logger

logger = get_logger(__name__)


class DatabaseManager:
    """Database management utilities"""

    def __init__(self, engine: AsyncEngine | None = None):
        self.engine = engine or create_async_engine(config.database_url)

    async def check_connection(self) -> bool:
        """Check if database connection is working"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
            return True
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return False

    async def get_table_info(self) -> dict[str, Any]:
        """Get information about existing tables"""
        try:
            async with self.engine.begin() as conn:
                # Get all tables
                tables_result = await conn.execute(
                    text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
                )
                tables = [row[0] for row in tables_result]

                # Get table sizes
                sizes_result = await conn.execute(
                    text("""
                    SELECT
                        schemaname,
                        tablename,
                        attname,
                        n_distinct,
                        correlation
                    FROM pg_stats
                    WHERE schemaname = 'public'
                    ORDER BY tablename, attname
                """)
                )

                table_info = {
                    "tables": tables,
                    "count": len(tables),
                    "stats": [dict(row._mapping) for row in sizes_result],
                }

                logger.info(f"Found {len(tables)} tables in database")
                return table_info

        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return {"tables": [], "count": 0, "stats": []}

    async def backup_table_data(self, table_name: str) -> list[dict[str, Any]]:
        """Backup data from a specific table"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(f"SELECT * FROM {table_name}"))
                data = [dict(row._mapping) for row in result]

                logger.info(f"Backed up {len(data)} rows from {table_name}")
                return data

        except Exception as e:
            logger.error(f"Failed to backup table {table_name}: {e}")
            return []

    async def restore_table_data(
        self, table_name: str, data: list[dict[str, Any]]
    ) -> bool:
        """Restore data to a specific table"""
        try:
            if not data:
                logger.info(f"No data to restore for {table_name}")
                return True

            async with self.engine.begin() as conn:
                # Clear existing data
                await conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))

                # Insert data
                columns = list(data[0].keys())
                placeholders = ", ".join([f":{col}" for col in columns])
                insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

                await conn.execute(text(insert_sql), data)

                logger.info(f"Restored {len(data)} rows to {table_name}")
                return True

        except Exception as e:
            logger.error(f"Failed to restore table {table_name}: {e}")
            return False

    async def execute_sql_file(self, file_path: str) -> bool:
        """Execute SQL commands from a file"""
        try:
            with open(file_path) as f:
                sql_content = f.read()

            # Split by semicolon and execute each statement
            statements = [
                stmt.strip() for stmt in sql_content.split(";") if stmt.strip()
            ]

            async with self.engine.begin() as conn:
                for statement in statements:
                    await conn.execute(text(statement))

            logger.info(f"Executed SQL file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to execute SQL file {file_path}: {e}")
            return False

    async def create_indexes(self) -> bool:
        """Create additional performance indexes"""
        indexes = [
            # Stock indexes
            "CREATE INDEX IF NOT EXISTS idx_stocks_symbol_active ON stocks(symbol, is_active)",
            "CREATE INDEX IF NOT EXISTS idx_stocks_sector_industry ON stocks(sector, industry)",
            # BreakoutData indexes
            "CREATE INDEX IF NOT EXISTS idx_breakout_data_stock_date ON breakout_data(stock_id, trade_date)",
            "CREATE INDEX IF NOT EXISTS idx_breakout_data_status_date ON breakout_data(breakout_status, trade_date)",
            "CREATE INDEX IF NOT EXISTS idx_breakout_data_analysis_status ON breakout_data(analysis_status, is_analyzed)",
            # MasterBreakoutData indexes
            "CREATE INDEX IF NOT EXISTS idx_master_data_source_date ON master_breakout_data(data_source, snapshot_date)",
            "CREATE INDEX IF NOT EXISTS idx_master_data_active_snapshot ON master_breakout_data(is_active, snapshot_date)",
            # Analysis indexes
            "CREATE INDEX IF NOT EXISTS idx_analysis_session_date_status ON analysis_sessions(analysis_date, status)",
            "CREATE INDEX IF NOT EXISTS idx_performance_metrics_type_date ON performance_metrics(metric_type, metric_date)",
        ]

        try:
            async with self.engine.begin() as conn:
                for index_sql in indexes:
                    await conn.execute(text(index_sql))

            logger.info(f"Created {len(indexes)} performance indexes")
            return True

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            return False

    async def analyze_tables(self) -> bool:
        """Run ANALYZE on all tables to update statistics"""
        try:
            async with self.engine.begin() as conn:
                await conn.execute(text("ANALYZE"))

            logger.info("Database analysis completed")
            return True

        except Exception as e:
            logger.error(f"Failed to analyze tables: {e}")
            return False

    async def cleanup_old_data(self, days_to_keep: int = 90) -> dict[str, int]:
        """Clean up old data based on retention policy"""
        cleanup_results = {}

        try:
            async with self.engine.begin() as conn:
                # Clean old analysis sessions
                result = await conn.execute(
                    text("""
                    DELETE FROM analysis_sessions
                    WHERE created_at < NOW() - INTERVAL '%s days'
                    AND status IN ('COMPLETED', 'FAILED')
                """),
                    (days_to_keep,),
                )
                cleanup_results["analysis_sessions"] = result.rowcount

                # Clean old performance metrics
                result = await conn.execute(
                    text("""
                    DELETE FROM performance_metrics
                    WHERE created_at < NOW() - INTERVAL '%s days'
                """),
                    (days_to_keep,),
                )
                cleanup_results["performance_metrics"] = result.rowcount

                logger.info(f"Cleanup completed: {cleanup_results}")
                return cleanup_results

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return {}

    async def close(self):
        """Close database connections"""
        if self.engine:
            await self.engine.dispose()


# Utility functions
async def get_database_version() -> str | None:
    """Get PostgreSQL version"""
    try:
        engine = create_async_engine(config.database_url)
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
        await engine.dispose()
        return version
    except Exception as e:
        logger.error(f"Failed to get database version: {e}")
        return None


async def check_database_health() -> dict[str, Any]:
    """Comprehensive database health check"""
    health_status = {
        "connection": False,
        "version": None,
        "tables": [],
        "indexes_exist": False,
        "last_vacuum": None,
        "database_size": None,
    }

    try:
        db_manager = DatabaseManager()

        # Check connection
        health_status["connection"] = await db_manager.check_connection()

        if health_status["connection"]:
            # Get version
            health_status["version"] = await get_database_version()

            # Get table info
            table_info = await db_manager.get_table_info()
            health_status["tables"] = table_info["tables"]

            # Check if our indexes exist
            async with db_manager.engine.begin() as conn:
                result = await conn.execute(
                    text("""
                    SELECT COUNT(*) FROM pg_indexes
                    WHERE schemaname = 'public'
                    AND indexname LIKE 'idx_%'
                """)
                )
                index_count = result.scalar()
                health_status["indexes_exist"] = index_count > 0

                # Get database size
                result = await conn.execute(
                    text("""
                    SELECT pg_size_pretty(pg_database_size(current_database()))
                """)
                )
                health_status["database_size"] = result.scalar()

        await db_manager.close()
        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return health_status
