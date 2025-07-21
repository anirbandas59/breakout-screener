#!/usr/bin/env python3
"""
Database migration script for Breakout Screener V2
Manages database schema creation and updates
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine

from src.breakout_screener.core.config import config
from src.breakout_screener.core.logging import get_logger

logger = get_logger(__name__)


async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Parse database URL
        db_url = config.database_url
        if 'asyncpg' in db_url:
            # Extract connection params for asyncpg
            url_parts = db_url.replace('postgresql+asyncpg://', '').split('/')
            connection_part = url_parts[0]
            database_name = url_parts[1] if len(url_parts) > 1 else 'breakout_screener_v2'

            if '@' in connection_part:
                auth_part, host_part = connection_part.split('@')
                user, password = auth_part.split(':')
                host, port = host_part.split(':') if ':' in host_part else (host_part, '5432')
            else:
                host, port = connection_part.split(':') if ':' in connection_part else (connection_part, '5432')
                user, password = 'postgres', 'password'

            # Connect to postgres database to create our database
            conn = await asyncpg.connect(
                user=user,
                password=password,
                host=host,
                port=port,
                database='postgres'
            )

            # Check if database exists
            exists = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", database_name
            )

            if not exists:
                await conn.execute(f'CREATE DATABASE "{database_name}"')
                logger.info(f"Created database: {database_name}")
            else:
                logger.info(f"Database already exists: {database_name}")

            await conn.close()

    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise


async def run_migration():
    """Run database migration using our models"""
    try:
        # Create database if needed
        await create_database_if_not_exists()

        # Import models to register them
        from src.breakout_screener.models.base import Base

        # Create async engine
        engine = create_async_engine(config.database_url, echo=True)

        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()
        logger.info("Database migration completed successfully")

    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise


async def drop_all_tables():
    """Drop all tables - use with caution!"""
    try:
        from src.breakout_screener.models.base import Base

        engine = create_async_engine(config.database_url, echo=True)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        await engine.dispose()
        logger.info("All tables dropped successfully")

    except Exception as e:
        logger.error(f"Failed to drop tables: {e}")
        raise


def main():
    """Main migration script"""
    import argparse

    parser = argparse.ArgumentParser(description='Database migration script')
    parser.add_argument(
        'action',
        choices=['migrate', 'drop'],
        help='Action to perform'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force the action without confirmation'
    )

    args = parser.parse_args()

    if args.action == 'drop' and not args.force:
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() != 'yes':
            print("Operation cancelled")
            return

    if args.action == 'migrate':
        asyncio.run(run_migration())
    elif args.action == 'drop':
        asyncio.run(drop_all_tables())


if __name__ == "__main__":
    main()
