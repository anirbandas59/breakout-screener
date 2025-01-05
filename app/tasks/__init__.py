import logging

from celery import shared_task
from sqlalchemy.orm import Session

from app.celery import celery_app
from app.db.session import SessionLocal
from app.services import fetch_script_symbols


@celery_app.task
def example_task(name: str):
    """
    A simple Celery task to demonstrate functionality.
    """
    return f"Hello, {name}!"


# def example_task(x, y):
#     return x + y

# @shared_task
@celery_app.task
def fetch_script_symbols_task():
    """Celery Task to fetch script symbol"""
    db: Session = SessionLocal()

    try:
        logging.info("Starting Celery task to fetch script symbols...")
        fetch_script_symbols(db)

        logging.info(
            "Celery task completed: Script symbols fetched successfully.")
        return "Script symbols fetched successfully."

    except Exception as e:
        logging.error(
            "Error in Celery task for fetching script symbols: %s", str(e))
        raise e
    finally:
        db.close()

    # fetch_script_symbols(db)

    # return
