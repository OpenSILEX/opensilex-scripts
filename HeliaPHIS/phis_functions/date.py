#******************************************************************************
# // date.py
# // Eva Minot
# // OpenSILEX - Licence AGPL V3.0 - https://www.gnu.org/licenses/agpl-3.0.en.html
# // OpenSILEX - ClientToolsPyhton V1.0.0-beta+2 - https://github.com/OpenSILEX/opensilexClientToolsPython/releases/tag/1.0.0-beta%2B2
# // Copyright © INRAE 2021
# // Contact: eva.mnt15@gmail.com, isabelle.alic@inrae.fr, nicolas.langlade@inrae.fr
# //*********

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
