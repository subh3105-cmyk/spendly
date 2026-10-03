from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def validate_date(date_str):
    """
    Validates if a date string is in YYYY-MM-DD format.
    Returns the date string if valid, otherwise None.
    """
    if not date_str:
        return None
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        return None

def get_profile_presets():
    """
    Calculates the current date presets for the profile page.
    """
    today = date.today()
    return {
        "this_month": {
            "from": (today.replace(day=1)).strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d")
        },
        "last_3_months": {
            "from": (today - relativedelta(months=3)).strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d")
        },
        "last_6_months": {
            "from": (today - relativedelta(months=6)).strftime("%Y-%m-%d"),
            "to": today.strftime("%Y-%m-%d")
        }
    }
