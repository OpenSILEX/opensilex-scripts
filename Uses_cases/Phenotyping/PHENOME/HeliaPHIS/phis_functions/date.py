import datetime


def transformDate(date):
    """Reformat a date

               :param date: date in format AAAA-MM-DD HH:MM:SS
               :type date: str
               :return: date in format AAAA-MM-DDTHH:MM:SSZ
               :rtype: str
    """
    date_object = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date_reformat = datetime.datetime.strftime(date_object, "%Y-%m-%dT%H:%M:%SZ")
    return date_reformat


def add_1s(date_string):

    # convert date in string to datetime
    try:
        date = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
    except:
        try:
            date = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")
        except:
            return None
    # get the date in seconds, add 1
    seconds = date.timestamp() + 1
    # get the date from the amount of seconds
    date = datetime.datetime.fromtimestamp(seconds)
    # convert the date in string with the good format
    date = datetime.datetime.strftime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date
