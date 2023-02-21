import datetime

def during_service_time(time_to_check: datetime.datetime):
    if time_to_check.weekday() < 5:
        if time_to_check.hour >= 5 and time_to_check.hour < 22:
            return True
        
    return False