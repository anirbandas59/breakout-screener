# Database Migration Setup

This directory contains Alembic migration files for the Breakout Screener V2 database schema.

## Overview

The migration setup includes:
- Manual migration files for V2 schema
- Database utilities for management 
- Migration scripts for schema changes

## Environment Setup

Set the database URL environment variable:
```bash
export DATABASE_URL="postgresql+asyncpg://user:password@localhost/breakout_screener_v2"
```

## Migration Commands

### Using Alembic (Manual migrations)

```bash
# Check current migration status
alembic current

# Upgrade to latest migration  
alembic upgrade head

# Downgrade one revision
alembic downgrade -1

# Show migration history
alembic history
```

### Using Migration Script

```bash
# Run database migration (creates tables)
python scripts/migrate_database.py migrate

# Drop all tables (use with caution!)
python scripts/migrate_database.py drop --force
```

## Migration Files

- `001_initial_v2_models.py` - Initial V2 schema with all tables and indexes

## Database Schema

The V2 schema includes:

### Tables
- `stocks` - Stock master data
- `breakout_data` - Daily breakout analysis data  
- `master_breakout_data` - Historical snapshot tracking
- `analysis_sessions` - Analysis run tracking
- `performance_metrics` - Performance measurement data

### Enums
- `BreakoutStatus` - Breakout detection results
- `PivotType` - Bullish/Bearish/Neutral classifications  
- `AnalysisStatus` - Processing status tracking
- `PerformanceMetricType` - Metric type categories

### Indexes
- Primary keys on all tables (UUID)
- Unique constraints for business logic
- Performance indexes for common queries
- Foreign key indexes for joins

## Best Practices

1. **Always backup before migrations** in production
2. **Test migrations** on staging environment first
3. **Review generated SQL** before applying 
4. **Use transactions** for multi-step migrations
5. **Document breaking changes** in migration comments

## Troubleshooting

### Connection Issues
- Verify DATABASE_URL environment variable
- Check PostgreSQL service is running
- Ensure database exists and accessible

### Migration Errors  
- Check Alembic revision history with `alembic history`
- Verify current database state with `alembic current`
- Use `alembic show` to inspect specific revisions

### Performance Issues
- Run `ANALYZE` after large data migrations
- Consider `REINDEX` for index rebuilds
- Monitor query performance post-migration