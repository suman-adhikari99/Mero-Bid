import datetime
def expirey_days(days=3):
    after_three_days=datetime.datetime.now() + datetime.timedelta(days =days)
    return datetime.datetime.strftime(after_three_days, "%a, %d-%b-%Y %H:%M:%S GMT")
def expirey_hours(hours=3):
    after_three_hours=datetime.datetime.now() + datetime.timedelta(hours = hours)
    return datetime.datetime.strftime(after_three_hours, "%a, %d-%b-%Y %H:%M:%S GMT")

