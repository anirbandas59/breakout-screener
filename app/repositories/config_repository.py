"""
Repository for app_config table operations.

Provides dynamic configuration management, with NSE URLs
as the primary use case.
"""
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.app_config import AppConfig


class ConfigRepository:
    """Encapsulates all database operations for the app_config table."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_key(self, key: str) -> Optional[AppConfig]:
        """Fetch a config entry by its key."""
        return self.db.query(AppConfig).filter_by(key=key).first()

    def get_all(self) -> List[AppConfig]:
        """Fetch all config entries ordered by key."""
        return self.db.query(AppConfig).order_by(AppConfig.key.asc()).all()

    def get_nse_urls(self) -> List[str]:
        """
        Return all NSE URL values (rows where key starts with 'nse_url_').
        Returns an empty list if no URLs are configured in the database.
        """
        rows = (
            self.db.query(AppConfig)
            .filter(AppConfig.key.like('nse_url_%'))
            .order_by(AppConfig.key.asc())
            .all()
        )
        return [row.value for row in rows if row.value]

    def upsert(self, key: str, value: str, description: Optional[str] = None) -> AppConfig:
        """Insert or update a config entry."""
        existing = self.get_by_key(key)
        if existing:
            existing.value = value
            if description is not None:
                existing.description = description
            existing.updated_at = datetime.utcnow()
        else:
            existing = AppConfig(key=key, value=value, description=description)
            self.db.add(existing)
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def delete(self, key: str) -> bool:
        """Delete a config entry by key. Returns True if deleted, False if not found."""
        row = self.get_by_key(key)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
