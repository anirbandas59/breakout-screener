import logging

from celery import shared_task
from sqlalchemy.orm import Session

from app.celery import celery_app
from app.db.session import SessionLocal
from app.services import (
    fetch_script_symbols,
    generate_BOData,
    clear_chart_data,
    clear_complete_data,
)


# @celery_app.task
# def example_task(name: str):
#     """
#     A simple Celery task to demonstrate functionality.
#     """
#     return f"Hello, {name}!"


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

        logging.info("Celery task completed: Script symbols.")
        return {
            "status": "SUCCESS",
            "message": "Script symbols task completed successfully.",
        }

    except Exception as e:
        logging.error(
            "Error in Celery task for fetching script symbols: %s", str(e))
        return {"status": "FAIL", "message": f"Failed to run Celery task. {e}"}
    finally:
        db.close()


@celery_app.task
def generate_bo_data_task(date, pivot):
    """
    Celery task to generate BO data for all symbols.

    This task is used to generate BO data for all symbols in the database. The
    task takes two parameters: date and pivot. The date parameter is the date
    for which the BO data needs to be generated and the pivot parameter is the
    percentage of the gap to be considered narrow.

    The task returns a string message indicating the status of the task.
    """
    db: Session = SessionLocal()

    try:
        logging.info(
            "Starting Celery task to generate BO data for all symbols ...")
        result = generate_BOData(db, date, pivot)

        logging.info("Celery task completed: Generate BO Data task")

        if result["status"] != "SUCCESS":
            raise ValueError(
                f"BO data generation task failed: {
                    result['error']}"
            )

        return {
            "status": "SUCCESS",
            "message": f"BO data generation task {result['status']}: {result['message']}",
        }
    except Exception as e:
        logging.error(
            "Error in Celery task for fetching script symbols: %s", str(e))
        return {"status": "FAIL", "message": f"Failed to run Celery task. {e}"}
    finally:
        db.close()


@celery_app.task
def clear_chart_data_task(date: str):
    """
    Celery task to clear chart data for a specific date

    Returns:
        str: A success message indicating that the task has been completed.
    """
    db: Session = SessionLocal()

    try:
        logging.info("Starting Celery task to clear chart data symbols...")
        result = clear_chart_data(db, date)

        if not result:
            logging.info("Celery task completed: Clear Chart Data.")
            return {"status": "SUCCESS", "message": "Chart data task clearing skipped."}

        logging.info("Celery task completed: Chart data task.")
        return {"status": "SUCCESS", "message": "Chart data task cleared successfully"}
    except Exception as e:
        logging.error("Error in Celery task: %s", str(e))
        return {"status": "FAIL", "message": f" Failed to run Celery task: {str(e)}"}
    finally:
        db.close()


# @celery_app.task
# def clear_complete_data_task():
#     """
#     Celery task to clear complete data from table.

#     Returns:
#         dict: A dictionary with a "status" key and a "message" key.
#             - The status will be "SUCCESS" if the task was successful, and "FAIL" otherwise.
#             - The message will contain information about any errors that occurred.
#     """
#     db: Session = SessionLocal()

#     try:
#         logging.info("Starting Celery task to fetch script symbols...")
#         clear_complete_data(db)

#         logging.info(
#             "Celery task completed: Table data cleared successfully.")

#         return {"status": "SUCCESS", "message": "Table data cleared successfully"}

#     except Exception as e:
#         logging.error(
#             "Error in Celery task for fetching script symbols: %s", str(e))

#         return {"status": "FAIL", "message": str(e)}

#     finally:
#         db.close()


@celery_app.task
def clear_complete_data_task():
    """
    Celery task to clear all data from breakout_data and push to master_table.

    Returns:
        dict: Task result containing the status and a message.
    """
    db: Session = SessionLocal()

    try:
        logging.info(
            "Starting Celery task to clear complete data from breakout_data..."
        )

        # Call the service function to clear and migrate data
        clear_complete_data(db)

        logging.info("Celery task completed successfully.")
        return {
            "status": "SUCCESS",
            "message": "Data cleared and pushed to master_table successfully.",
        }

    except Exception as e:
        logging.error(
            "Error in Celery task for clearing complete data: %s", str(e))
        return {"status": "FAIL", "message": f"Failed to run Celery task: {str(e)}"}

    finally:
        db.close()
