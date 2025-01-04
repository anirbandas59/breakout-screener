# import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services import (
    fetch_script_symbols,
    generate_BOData,
    clear_complete_data,
    clear_chart_data,
    get_breakout_data,
)
from app.utils import get_current_date, suspend_action, validate_date
from app.models import GenerateBODataRequest

router = APIRouter()


@router.get("/get_data", status_code=200)
def get_data(db: Session = Depends(get_db), page: int = 1, limit: int = 10):
    """
    Fetch processed breakout data.

    Args:
        page (int): Page number for pagination.
        limit (int): Number of records per page.
        db (Session): SQLAlchemy database session.

    Returns:
        JSON response with breakout data.
    """
    try:
        logging.info("Fetching processed breakout data...")
        result = get_breakout_data(db, page, limit)

        if result:
            total, data = result["total"], result["data"]

        logging.info("Fetched processed breakout data successfully.")
        return {"total": total, "data": data, "page": page, "limit": limit}
    except Exception as e:
        logging.error("Error fetching processed breakout data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/fetch_script_symbols", status_code=200)
def fetch_scripts(db: Session = Depends(get_db)):
    """
    Fetch script symbols from NSE and save to database.

    Args:
        db (Session): SQLAlchemy database session.

    Returns:
        JSON response indicating success or failure.
    """
    try:
        logging.info("Starting to fetch script symbols...")
        fetch_script_symbols(db)

        logging.info("Script symbols fetched successfully.")
        return {"message": "Script symbols fetched successfully"}

    except Exception as e:
        logging.error("Error fetching script symbols: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/generate_bodata", status_code=200)
def generate_bodata(
    request: GenerateBODataRequest,
    db: Session = Depends(get_db)
):
    """
    Generate breakout data for all scripts in the breakout_data table.

    Args:
        request (GenerateBODataRequest): Request object containing
            the date and pivot value for the analysis.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Status of the analysis.
    """
    # Fetch the pivot value from the request
    pivot_val = request.pivot_val

    # Validate the date format
    analysis_date_val = request.date if not validate_date(
        request.date) else get_current_date()

    try:
        logging.info(
            "Starting BO Data generation for date: %s with pivot value: %s",
            analysis_date_val,
            pivot_val,
        )
        # Call the function to generate the BO Data
        response = generate_BOData(db, analysis_date_val, pivot_val)
        logging.info("BO Data generation completed successfully.")

        return response
    except Exception as e:
        logging.error("Error during BO Data generation: %s", str(e))
        # Raise an HTTPException if the analysis fails
        raise HTTPException(status_code=500, detail=str(e)) from e


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

    logging.info("Clearing BO Data for date: %s", today_date)
    record = clear_chart_data(db, today_date)

    if not record:
        raise HTTPException(
            status_code=404, detail=f"No record found for date '{today_date}'."
        )

    logging.info("BO Data clearing completed successfully.")
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
        logging.info("Clearing BO Data.")
        clear_complete_data(db)

        logging.info("BO Data clearing completed successfully.")
        return {
            "message": "All data cleared from breakout_data and moved to master_table."
        }

    except Exception as e:
        logging.error("Error during BO Data generation: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {str(e)}"
        ) from e


@router.post("/suspend_action")
def api_suspend_action():
    """API to suspend the ongoing analysis."""
    try:
        logging.info("Suspending analysis...")
        suspend_action()
        return {"message": "Analysis suspension triggered successfully"}
    except RuntimeError as e:
        logging.error("Error suspending analysis: %s", str(e))
        return {"message": "Failed to suspend analysis", "error": str(e)}


@router.get('/simulate_error')
def simulate_error():
    raise Exception('Simulated error')
