import datetime


def during_service_time(time_to_check: datetime.datetime):
    """
    The ferry does not go weekends and only between 5 and 22 hours
    """
    
# sourcery skip: merge-nested-ifs
    if time_to_check.weekday() < 5:  # workdays
        if time_to_check.hour >= 5 and time_to_check.hour < 22:  # ferry times
            return True

    return False
