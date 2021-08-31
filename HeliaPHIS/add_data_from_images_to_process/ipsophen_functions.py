import csv
import json
import re

import os

import time

import ipso_phen


import csv_phis
import datetime

from phis_functions import agent, event, activity, provenance, connection, experiment, scientific_object, image, variable

file_list = []

def process(image_folder, out_file_name):
    """Process an image in ipso phen.

        :param image_folder: Path of the folder containing the images to be processed
        :type image_folder: str
        :param out_file_name: Name of the csv file containing the result that will be created
        :type out_file_name: str
        :return: Path of the result csv file
        :rtype: Normalized version of the out file's pathname
    """
    folder_name = out_file_name.split("_")[1]
    path = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/Data/ipsophen_data_out/{}/{}".format(folder_name, out_file_name)
    if not os.path.exists(path):
        os.makedirs(path)
    os.system(
        'ipso_cli --image-folder {} --script /mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS'
        '/Scripts/heliasen_qc_tfi.json  --output-folder {} --csv-file-name {}'.format(image_folder, path, out_file_name))
    return os.path.abspath(path + "/{}.csv".format(out_file_name))


# check if the version of IPSO Phen that is used matches the version entered in Phis for the agent IPSO Phen
def check_version(client):
    """Check the version of IPSO Phen, if a new version is detected compared to the one that is currently in PHIS, update the settings of the agent in Phis

            :param client: Current client in Phis
            :type client: TokenGetDTO

    """
    ipsophen_agent_uri = agent.find_agent(client, "IPSO Phen").uri
    version = ipso_phen.version
    today = datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%S-%m:%H')
    info = {'version': version}
    try:
        last_calibration = event.find_event(client, ipsophen_agent_uri, "oeev:Calibration")
        if last_calibration is not None:
            last_version = json.loads(event.find_event(client, ipsophen_agent_uri, "oeev:Calibration").description)["version"]
            if last_version != version:
                event.create_event(pythonClient=client, device_uri=ipsophen_agent_uri, rdf_type="oeev:Calibration", date=today, description=json.dumps(info))
        else:
            event.create_event(pythonClient=client, device_uri=ipsophen_agent_uri, rdf_type="oeev:Calibration",
                                        date=today, description=json.dumps(info))
    except IndexError:
        event.create_event(pythonClient=client, device_uri=ipsophen_agent_uri, rdf_type="oeev:Calibration",
                                    date=today, description=json.dumps(info))

def parse_ipsophen_csv(client, csv_file_in, csv_file_out_date, line_number=0):
    """Creates a csv in the format required by Phis for the data from a csv returned by ipso phen

            :param client: Current client in Phis
            :type client: TokenGetDTO
            :param csv_file_in: csv file returned by ipso phen
            :type csv_file_in: str
            :return: Path of the csv file of data
            :rtype: Normalized version of the out file's pathname
    """

    # create the provenance (or retrieve the last one that is already in Phis if no agent settings has been changed)
    activity_data = [
        activity.create_activity(rdf_type="vocabulary:ImageAnalysis")]

    agents = [
              agent.find_agent(client, "IPSO Phen")]
    provenance_uri = provenance.create_provenance(client, name="Image_Analysis_Heliaphen", date=csv_file_out_date,
                                                  prov_agent=agents,
                                                  description="Provenance of the data (processed by IPSO Phen)",
                                                  prov_activity=activity_data)
    # create the provenance of the images (or retrieve it)
    activity_image = [
        activity.create_activity(rdf_type="vocabulary:ImageAcquisition")]
    image_provenance_uri = provenance.create_provenance(client, "Image_Acquisition_Heliaphen", date=csv_file_out_date, prov_agent=[agents[0]],
                                                        prov_activity=activity_image,
                                                        description="Provenance of the image")
    # uris of the variables
    variable_uris = {}

    # uris of the experiments
    experiments = {}

    # name of the csv file out that will contain the data information in the format required by phis
    csv_file_out = "phis_" + csv_file_out_date + ".csv"
    global file_list
    try:
        # parse the csv file
        with open(csv_file_in, "r") as file:
            reader = csv.reader(file, delimiter=',')
            line_count = 0
            start_time = time.time()
            for row in reader:
                current_time = time.time()
                # refresh connection if needed
                if current_time - start_time > 180:
                    print("renewing token")
                    connection.refresh_connection(client)
                    start_time = current_time
                # first line of the csv = variable names
                if line_count == 0:
                    out_file = csv_phis.create_csv_file(csv_file_out, "ipsophen_data")
                    variables = row
                else:
                    experiment_name = row[0]
                    # if this experiment has not been seen yet in the csv, retrieve its uri in Phis and save it in the dict of experiments
                    if experiment_name not in experiments:
                        try:
                            experiment_uri = experiment.find_experiment_by_name(client, experiment_name)
                            experiments[experiment_name] = experiment_uri
                        except IndexError:
                            # This error appears if no experiment was found under this name, must not block the process
                            experiments[experiment_name] = ""
                            print("No experiment found in Phis under the name " + experiment_name + " --> no data will be "
                                                                                                    "added in Phis for "
                                                                                                    "this experiment.")
                            # no experiment was found --> not created in phis
                            # keep parsing but no data will be added for this experiment
                            continue
                    # if is in the dict of experiments, just get the associated uri
                    else:
                        experiment_uri = experiments[experiment_name]
                        if experiment_uri == "":
                            continue
                    # scientific object name = name of the experiment + number of the plant
                    # Phis doesn't seem to be case sensitive, but put it in uppercase to follow the nomenclature to be sure
                    scientific_object_name = row[0].upper() + row[1].upper()

                    # several objects can be found under the same name (two plants in one pot..)
                    scientific_object_uris = scientific_object.find_scientific_object(client, scientific_object_name,
                                                                                   experiment_uri, 'vocabulary:Plant')
                    date_str = row[2]
                    image_source = row[6]
                    # add the image used to collect the data in phis and link it with the scientific object(s)
                    for scientific_object_uri in scientific_object_uris:
                        image_uri = image.add_image(client, path=image_source, date_str=date_str,
                                                             scientific_object=scientific_object_uri,
                                                             provenance=image_provenance_uri, experiment=experiment_uri, prov_object_type="vocabulary:Plant")

                    # retrieve the values associated to the variables we want to put in Phis
                    for var in range(7,len(row)):
                        # get the name of the variable of the current value
                        variable_name = variables[var]
                        # check if it matches with one of the variables we want to keep (some are not useful)
                        keep_variable = re.match(
                            "(.*area)|(shape_*)|(centroid_*)|(rotated_bounding_rectangle_*)|(""minimum_enclosing_circle_*)"
                            "|(above_bound_*)|(below_bound_*)|(quantile_*)|(.*perimeter)|(straight_bounding_rectangle_*)",
                            variable_name)
                        if not keep_variable:
                            continue
                        if variable_name not in variable_uris:
                            # retrieve the uri of the variable in Phis (here, they all start by "hp_")
                            variable_uris[variable_name] = variable.find_variable(client, "hp_" + variable_name)
                        value = row[var]
                        date_str = row[2]
                        timezone = "Europe/Paris"

                        for scientific_object_uri in scientific_object_uris:
                            # add a row in the csv out for this value
                            csv_phis.add_data_csv(out_file, "", date_str, timezone, experiment_uri, scientific_object_uri,
                                                  variable_uris[variable_name], value,
                                                  provenance_uri, image_uri, "", "")

                line_count += 1

        return file_list, experiments
    except FileNotFoundError:
        return None


