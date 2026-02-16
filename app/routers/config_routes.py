"""Config routes for dynamic application configuration management."""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.app_config import AppConfig
from app.repositories import ConfigRepository
from app.models.schemas import AppConfigItem, AppConfigListResponse, UpsertConfigRequest
from app.utils.error_handlers import handle_service_error

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/nse-urls", response_model=AppConfigListResponse)
def list_nse_urls(db: Session = Depends(get_db)):
    """List all NSE URL configuration entries."""
    try:
        repo = ConfigRepository(db)
        rows = (
            db.query(AppConfig)
            .filter(AppConfig.key.like('nse_url_%'))
            .order_by(AppConfig.key.asc())
            .all()
        )
        return {"items": rows}
    except Exception as e:
        raise handle_service_error(e, {"operation": "list_nse_urls"}) from e


@router.get("", response_model=AppConfigListResponse)
def list_all_config(db: Session = Depends(get_db)):
    """List all application configuration entries."""
    try:
        repo = ConfigRepository(db)
        return {"items": repo.get_all()}
    except Exception as e:
        raise handle_service_error(e, {"operation": "list_all_config"}) from e


@router.post("/nse-urls", response_model=AppConfigItem, status_code=status.HTTP_201_CREATED)
def create_nse_url(request: UpsertConfigRequest, db: Session = Depends(get_db)):
    """Add a new NSE URL configuration entry."""
    try:
        repo = ConfigRepository(db)
        item = repo.upsert(request.key, request.value, request.description)
        logging.info("Config upserted: key=%s", request.key)
        return item
    except Exception as e:
        raise handle_service_error(e, {"operation": "create_nse_url"}) from e


@router.put("/nse-urls/{key}", response_model=AppConfigItem)
def update_nse_url(key: str, request: UpsertConfigRequest, db: Session = Depends(get_db)):
    """Update an existing NSE URL configuration entry by key."""
    try:
        repo = ConfigRepository(db)
        existing = repo.get_by_key(key)
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Config key '{key}' not found")
        item = repo.upsert(key, request.value, request.description)
        logging.info("Config updated: key=%s", key)
        return item
    except HTTPException:
        raise
    except Exception as e:
        raise handle_service_error(e, {"operation": "update_nse_url", "key": key}) from e


@router.delete("/nse-urls/{key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_nse_url(key: str, db: Session = Depends(get_db)):
    """Delete an NSE URL configuration entry by key."""
    try:
        repo = ConfigRepository(db)
        deleted = repo.delete(key)
        if not deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Config key '{key}' not found")
        logging.info("Config deleted: key=%s", key)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_service_error(e, {"operation": "delete_nse_url", "key": key}) from e
