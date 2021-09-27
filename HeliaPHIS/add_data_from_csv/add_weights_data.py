import os
import shutil
from os import listdir
from os.path import isfile, join

from colorama import Fore, Style
from opensilexClientToolsPython.rest import ApiException

import csv_phis
import weights
import folder_gestion
from phis_functions import connection, data

if __name__ == '__main__':
    identifier = "phenotoul_auto@inrae.fr"
    pwd = "phenotoul_auto"


    # is a dict where the keys are the folder dates and the values are a list of the dates of
    # the files in the folder
    # --> {2021-07: [2021-07-08, 2021-07-09]}
    timestamps = {}

    # get_timestamp_weight returns a list : [folder_timestamp, file_timestamp]
    latest_folder_timestamp = folder_gestion.get_timestamp_weight()[0]
    latest_file_timestamp = folder_gestion.get_timestamp_weight()[1]

    # change here to put the correct path of the weights directory
    for folder in os.scandir("/mnt/Shared/Helia/Data_Out/"):
        # is it this current month's weights folder
        # if yes process its files
        if folder.is_dir() and folder_gestion.check_type_folder_weights(folder):
            print(folder)
            folder_date = folder_gestion.get_date_from_weights_folder(folder)
            print(folder_date)
            # is the folder date more recent than the latest folder date we found ?
            # if yes process its files 
            if folder_date is not None and folder_gestion.check_creation_date_weight_folder(folder_date, latest_folder_timestamp):
                print("to be processed")
                weights.file_list = []
                timestamps[folder_date] = []
                folder_in = folder.path
                files = [f for f in listdir(folder) if isfile(join(folder, f))]
                for file in files:
                    print(file)
                    file_date = folder_gestion.get_date_from_weight_file(file)
                    try:
                        client = connection.connect_to_phis(identifier, pwd)
                    except ApiException as e:
                        print(Fore.RED + "Access denied. ID or pwd incorrect.\n")
                        print(Style.RESET_ALL)
                    if folder_gestion.check_creation_date_weight_file(file_date, latest_file_timestamp):
                        print("to be processed")
                        timestamps[folder_date].append(file_date)
                        file_path = os.path.join(folder_in, file)

                        # get the csv(s) of weights data for phis
                        weights_files = weights.get_weights(client, file_path, "weights_" + file)
                        for weight_file in weights_files:
                            # if the only file in weights files is empty, skip
                            if len(weights_files) == 1 and not csv_phis.csv_not_empty(weight_file):
                                continue
                            else:
                                data.send_data_to_phis(client, weight_file)

    if len(timestamps) != 0:
        latest_folder_timestamp = folder_gestion.get_max_timestamp(timestamps.keys())
        latest_file_timestamp = folder_gestion.get_max_timestamp(timestamps[latest_folder_timestamp])
        folder_gestion.print_timestamp_weight(latest_folder_timestamp, latest_file_timestamp)