import pytz


def convert_pacific_to_utc(the_date):
    pacific_tz = pytz.timezone('US/Pacific')
    local = pacific_tz.localize(the_date)
    return local.astimezone(pytz.utc)


def get_pacific_tz_year():
    """
    Return the current year from Pacific Timezone
    """
    return pytz.datetime.datetime.now(tz=pytz.timezone('US/Pacific')).year


def unix_ts_to_dt(unix_timestamp):
    """
    Convert unix timestamp to datetime object
    """
    return pytz.datetime.datetime.fromtimestamp(unix_timestamp)
