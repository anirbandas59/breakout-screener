import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.fetch_scripts import fetch_script_symbols
from app.services.generate_bo_data import generate_BOData
from app.services.clear_chart import clear_chart_data
from app.services.clear_complete_data import clear_complete_data
from app.utils.helpers import get_current_date, suspend_action

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


@router.post("/generate_bodata")
def generate_bodata(db: Session = Depends(get_db)):
    today_date = get_current_date()
    pivot_val = 0.5
    try:
        return generate_BOData(db, today_date, pivot_val)
        # return json.dumps({
        #     "message": "Analysis completed"
        # })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear_chart", status_code=200)
def clear_chart(db: Session = Depends(get_db)):
    """
    Clear chart data for a specific date

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        JSON response indicating success or failure.
    """
    today_date = get_current_date()

    record = clear_chart_data(db, today_date)

    if not record:
        raise HTTPException(
            status_code=404,
            detail=f"No record found for date '{today_date}'."
        )

    return {"message": f"Chart data for '{today_date}' cleared successfully."}


@router.post("/clear_complete_data", status_code=200)
def clear_complete_data_endpoint(db: Session = Depends(get_db)):
    """
    Clear all data from breakout_data and push to master_table.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        JSON response indicating success.
    """

    try:
        clear_complete_data(db)
        return {"message": "All data cleared from breakout_data and moved to master_table."}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/suspend_action")
def api_suspend_action():
    """API to suspend the ongoing analysis."""
    try:
        suspend_action()
        return {"message": "Analysis suspension triggered successfully"}
    except Exception as e:
        logging.error(f"Error suspending analysis: {e}")
        return {"message": "Failed to suspend analysis", "error": str(e)}
