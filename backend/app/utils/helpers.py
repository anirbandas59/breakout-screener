import pytz
import logging
from datetime import datetime, timedelta
from app.utils.suspension_flag import SUSPEND_ANALYSIS


def get_current_date() -> str:
    """
    Get the current date based on the following logic:
    - Between 6 PM IST and 6 AM IST of the next day: Return the current date.
    - Between 6 AM IST and 6 PM IST: Return the previous day's date.

    Returns:
        str: Date string in the format YYYY-MM-DD.
    """
    # Define IST timezone
    ist = pytz.timezone("Asia/Kolkata")

    # Get the current time in IST
    now = datetime.now(ist)

    # Define 6 AM and 6 PM in IST
    six_am = now.replace(hour=6, minute=0, second=0, microsecond=0)
    six_pm = now.replace(hour=18, minute=0, second=0, microsecond=0)

    # Determine the date to return
    if six_am <= now < six_pm:
        # Between 6 AM and 6 PM: Return previous day's date
        date_to_return = now - timedelta(days=1)
    else:
        # Between 6 PM and 6 AM: Return the current date
        if now < six_am:
            date_to_return = now - timedelta(days=1)
        else:
            date_to_return = now

    return date_to_return.strftime("%Y-%m-%d")


def validate_date(date: str) -> bool:
    """
    Validate the date format (YYYY-MM-DD).

    Args:
        date (str): Date string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def suspend_action():
    """Sets the global suspension flag."""
    # global SUSPEND_ANALYSIS

    SUSPEND_ANALYSIS.set()
    logging.info("Suspension triggered. SUSPEND_ANALYSIS set to True.")
