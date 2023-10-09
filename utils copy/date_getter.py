""" File to hold methods to get the dates wanted """
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


TODAY = datetime.today()
print(TODAY)

def get_months_ago(months_to_subtract: int):
    return TODAY - relativedelta(months=months_to_subtract)
def get_weeks_ago(weeks_to_subtract: int):
    return TODAY - timedelta(weeks=weeks_to_subtract)
def get_days_ago(days_to_subtract: int):
    return TODAY - timedelta(days=days_to_subtract)
def get_hours_ago(hours_to_subtract: int):
    return TODAY - timedelta(hours=hours_to_subtract)
def get_previous_sunday():
    delta_day = 0 - TODAY.isoweekday()
    if delta_day >= 0: 
        delta_day -= 7 # go back 7 days
    return TODAY + timedelta(days=delta_day)

# if __name__ == "__main__":
    # print(get_months_ago(3))
    # print(get_weeks_ago(3))
    # print(get_days_ago(3))
    # print(get_hours_ago(3))
    # print(get_previous_sunday())


