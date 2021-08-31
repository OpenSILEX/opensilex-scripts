import _io
import csv
import os

import ipsophen_functions
import weights
import leaf_area
# global variables, necessary to handle file size


line_count = 0
number = 0
file_name = ""
path = ""
data_type = ""


def create_csv_file(filename, datatype, number=0):
    """Create a csv file adapted to the format required for the data by Phis.

        :param filename: Name given to the csv file created
        :type filename: str
        :param number: indicates the number of files have been created to parse the file
        :type number: int
        :param datatype: indicates which kind data will be added in the csv file (weights or ipsophen data)
        :type datatype: str
        :return: csv file's name
        :rtype: str
    """

    # we use global variables to be able to handle the max file size (50 000)
    # we want to create a new file named like this: filename.csv(x) each time the limit is reached
    global file_name
    global path
    global data_type
    if number != 0:
        file_name = str(filename) + "(" + str(number) + ")"
    else:
        file_name = filename

    # this part is just used to determine where the outputs should be put
    data_type = datatype
    folder_name = file_name.split("_")[1]
    folder_name = folder_name.split(".")[0]
    if data_type == "ipsophen_data":
        path = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/Data/ipsophen_data_out/{}".format(folder_name)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, file_name)
        ipsophen_functions.file_list.append(path)
    elif data_type == "weights_data":
        folder_date = "20" + folder_name[0:4]
        path = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/Data/weights_data_out/{}".format(folder_date)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, file_name)
        weights.file_list.append(path)
    elif data_type == "leaf_area_data":
        path = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/Data/leaf_area/sorties/{}".format(folder_name)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, file_name)
        leaf_area.file_list.append(path)

    # creation of the csv file with the format expected by Phis for data
    with open(path, "w", newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["uri", "date", "timezone", "experiment", "scientific_object", "variable", "value", "confidence",
                         "provenance", "image", "metadata", "raw_data"])
    return file_name


def add_data_csv(file, uri, date, timezone, experiment, scientific_object, variable, value,
                 provenance, image, metadata, raw_data):
    """Add data to the data csv file for Phis.

        :param file: Name of the csv file where the data needs to be added
        :type file: str
        :param uri: uri of the data (usually null)
        :type uri: str
        :param date: date of the acquisition of the data
        :type date: str
        :param timezone: timezone of the date
        :type timezone: str
        :param experiment: experiment where the data was collected
        :type experiment: str
        :param scientific_object: uri of the scientific object associated to the data
        :type scientific_object: str
        :param variable: uri of the variable representing the data collected
        :type variable: str
        :param value: value of the data
        :type value: str
        :param provenance: uri of the provenance associated to the data
        :type provenance: str
        :param image: uri of the image in phis that was used to calculate the data with ipso phen
        :type image: str
        :param metadata: metadata of the data (usually null)
        :type metadata: str
        :param raw_data: raw data
        :type raw_data: str
    """
    global line_count
    # if we reach the limit, create another file in which the next data will be written
    if line_count == 50000:
        global number
        number += 1
        create_csv_file(filename=file, number=number, datatype=data_type)
        line_count = 0
    global file_name
    global path

    with open(path, "a", newline='', encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([uri, date, timezone, experiment, scientific_object, variable, value, "",
                         provenance, image, metadata, raw_data])
        line_count += 1


def csv_not_empty(file):
    line_count = 0
    with open(file, "r", newline='') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            line_count += 1
            if line_count > 1:
                return True
        return False