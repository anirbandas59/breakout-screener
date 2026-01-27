"""
Database connection test utility.
Tests connection using credentials from environment variables.
"""
import psycopg2
from app.config import settings
from urllib.parse import urlparse

# Parse database URL from settings
parsed_url = urlparse(settings.database_url)

try:
    conn = psycopg2.connect(
        dbname=parsed_url.path.lstrip('/'),
        user=parsed_url.username,
        password=parsed_url.password,
        host=parsed_url.hostname,
        port=parsed_url.port or 5432
    )

    print("✅ Database connection successful")
    print(f"   Connected to: {parsed_url.hostname}:{parsed_url.port or 5432}/{parsed_url.path.lstrip('/')}")
    print(f"   User: {parsed_url.username}")

    conn.close()
except Exception as e:
    print(f"❌ Database connection failed: {e}")
