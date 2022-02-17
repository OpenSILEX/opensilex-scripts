#******************************************************************************
# //folder_gestion.py
# // Eva Minot
# // Copyright © INRAE 2021
# // Contact: eva.mnt15@gmail.com, isabelle.alic@inrae.fr, nicolas.langlade@inrae.fr
# //*********

import datetime
import re


def check_type_folder_weights(folder):
    valid = re.match("^[0-9]{4}-[0-9]{2}$", folder.name)
    if valid:
        return True
    else:
        return False


# check if a folder is an image folder (has a format like : YYYY-MM-DD)
def check_type_folder_ipsophen(folder):
    """Check if a folder is an image folder (has a name like YYY-MM-DD)

            :param folder: folder we want to check
            :type folder: str
            :return: True if the folder's name matches the image folder shape, False if not
            :rtype: bool
    """
    valid = re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", folder.name)
    if valid:
        return True
    else:
        return False


def get_date_from_image_folder(folder):
    """Get the date of an image folder (named like this : YYYY-MM-DD)

            :param folder: folder we want to check
            :type folder: str
            :return: date
            :rtype: date
    """
    date_string = folder.name
    try:
        date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return None
    return date


def get_date_from_weights_folder(folder):
    """Get the date of a weight folder (named like this : YYYY-MM)

            :param folder: folder we want to check
            :type folder: str
            :return: date
            :rtype: date
    """
    date_string = folder.name
    try:
        date = datetime.datetime.strptime(date_string, "%Y-%m")
        #date = datetime.date.strftime(date,"%Y-%m")
    except ValueError:
        return None
    return date


def get_date_from_weight_file(file):
    """Get the date of a weight file (named like this : YYMMDDxx)

            :param file: file we want to check
            :type file: str
            :return: date
            :rtype: datetime
    """

    # take off the extension of the file, just get its name
    file_name = file.split(".")[0]
    date_string = "20" + file_name[0:6]
    try:
        date = datetime.datetime.strptime(date_string, "%Y%m%d")
        return date
    except ValueError:
        return None


def check_creation_date_image_folder(folder_date, timestamp):
    """Check if an image folder was created after the timestamp given.

                :param folder_date: date associated to the folder
                :type folder_date: date
                :param timestamp: timestamp
                :type timestamp: datetime
                :return: True if the folder was created after the timestamp, false otherwise
                :rtype: bool
    """
    return folder_date > timestamp


def check_creation_date_weight_folder(folder_date, timestamp):
    """Check if a weight folder was created after the timestamp given.

                :param folder_date: date associated to the folder
                :type folder_date: date
                :param timestamp: timestamp
                :type timestamp: datetime
                :return: True if the folder was created after the timestamp, false otherwise
                :rtype: bool
    """
    return folder_date >= timestamp


def check_creation_date_weight_file(file_date, timestamp):
    """Check if a weight file was created after the timestamp given.

                    :param file_date: date associated to the file
                    :type file_date: date
                    :param timestamp: timestamp
                    :type timestamp: datetime
                    :return: True if the file was created after the timestamp, false otherwise
                    :rtype: bool
        """
    return file_date > timestamp


def get_max_timestamp(list_timestamps):
    """Get the latest timestamp in a list of timestamps.

                :param list_timestamps: list of timestamps
                :type list_timestamps: list[datetime]
                :return: Latest timestamp of the list (max)
                :rtype: datetime
    """
    return max(list_timestamps)


def print_timestamp_ipsophen(timestamp):
    """Print a timestamp in a text file.

                :param timestamp: timestamp to write in the file
                :type timestamp: datetime

    """
    timestamp_string = datetime.datetime.strftime(timestamp, "%Y-%m-%d")
    # change here to put the correct file path
    path = "path/to/textfile.txt"
    file = open(path, "w")
    file.write(timestamp_string)
    file.close()


def get_timestamp_ipsophen():
    """Get the timestamp written in the text file.

                :return: Timestamp
                :rtype: datetime
    """
    # change here to put the correct file path
    path = "path/to/textfile.txt"
    file = open(path, "r")
    timestamp = datetime.datetime.strptime(file.readline().rstrip(), "%Y-%m-%d")
    file.close()
    return timestamp


def print_timestamp_weight(timestamp_folder, timestamp_file):
    """Print a timestamp in a text file.

                :param timestamp_folder: timestamp of the last folder processed to write in the file
                :type timestamp_folder: datetime
                :param timestamp_file: timestamp of the last file processed to write in the file
                :type timestamp_file: datetime

    """
    timestamp_folder_string = datetime.datetime.strftime(timestamp_folder, "%Y-%m")
    timestamp_file_string = datetime.datetime.strftime(timestamp_file, "%Y-%m-%d")
    # change here to put the correct file path
    path = "path/to/textfile.txt"
    file = open(path, "w")
    line = timestamp_folder_string + " " + timestamp_file_string
    file.write(line)
    file.close()


def get_timestamp_weight():
    """Get the timestamps written in the text file.

                :return: Timestamp of the last folder processed and of the last file processed
                :rtype: list[datetime]
    """
    # change here to put the correct file path
    path = "path/to/textfile.txt"
    file = open(path, "r")
    dates = file.readline().rstrip().split(" ")
    timestamp_folder = datetime.datetime.strptime(dates[0], "%Y-%m")
    timestamp_file = datetime.datetime.strptime(dates[1], "%Y-%m-%d")
    file.close()
    return [timestamp_folder, timestamp_file]

