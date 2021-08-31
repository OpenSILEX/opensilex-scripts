import os
import shutil
import re
from datetime import date, datetime

from colorama import init, Fore, Style
from opensilexClientToolsPython.rest import ApiException

import ipsophen_functions


# check if a folder was created less than 24 hours before the execution of the script
import folder_gestion
import leaf_area
from phis_functions import connection, data

if __name__ == '__main__':
    try:
        init()
        # change here to put the correct path of the image directory
        timestamps = []
        latest_timestamp = folder_gestion.get_timestamp_ipsophen()

        for folder in os.scandir("/mnt/Shared/Helia/Data_Out/"):
            # for each folder in the directory
            # check if it is an image folder (and not a weight folder or something else)
            if folder.is_dir() and folder_gestion.check_type_folder_ipsophen(folder):
                folder_date = folder_gestion.get_date_from_image_folder(folder)
                folder_in = folder.path
                print(folder_in)
                x = datetime.strftime(folder_date, "%Y-%m-%d")
                month = x.split("-")[1]

                if folder_date is not None and folder_gestion.check_creation_date_image_folder(folder_date, latest_timestamp):
                    # reinitialize the list of phis csv files
                    # (it's global so if you don't do it it will add in the list previously
                    # created for another image folder)
                    f.write(datetime.strftime(folder_date, "%Y-%m-%d") + "\n")
                    ipsophen_functions.file_list = []
                    print("to be processed")
                    timestamps.append(folder_date)

                    # process the image folder with ipso phen
                    out_file_path = ipsophen_functions.process(folder_in, "ipsophen_" + folder.name)

                    # connection to Phis
                    identifier = "phenotoul_auto@inrae.fr"
                    pwd = "phenotoul_auto"
                    try:
                        client = connection.connect_to_phis(identifier, pwd)
                    except ApiException as e:
                        print(Fore.RED + "Access denied. ID or pwd incorrect.\n")
                        print(Style.RESET_ALL)
                    ipsophen_functions.check_version(client)
                    print("Adding data to Phis...\n")

                    result = ipsophen_functions.parse_ipsophen_csv(client, out_file_path, folder.name)
                    # result is none if no bmp image is in the folder (nothing processed)
                    if result is not None:
                        phis_csv_list = result[0]
                        # add data of the csv file(s) in phis
                        for phis_csv in phis_csv_list:
                            data.send_data_to_phis(client, phis_csv)
                        # calculate the leaf area
                        experiment_list = result[1] # dict where keys are experiments names and values are their uris
                        for experiment in experiment_list:
                            if experiment != "":
                                leaf_area.calculate_all_areas_from_experiment(client, experiment_list[experiment], start_date=folder_date)
                        print("Data successfully added to Phis.")


        if len(timestamps) != 0:
            latest_timestamp = folder_gestion.get_max_timestamp(timestamps)
            folder_gestion.print_timestamp_ipsophen(latest_timestamp)
        f.close()
    except EOFError as e:
        f.close()
        exit(0)
