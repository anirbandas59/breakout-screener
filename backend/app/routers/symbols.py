from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.fetch_scripts import fetch_script_symbols

router = APIRouter()


@router.post("/fetch_script_symbols")
def fetch_scripts(db: Session = Depends(get_db)):
    try:
        fetch_script_symbols(db)
        return {
            "message": "Script symbols fetched successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
