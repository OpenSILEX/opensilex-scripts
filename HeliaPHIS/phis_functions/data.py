import csv
import datetime

import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException
from phis_functions import scientific_object, date


def send_data_to_phis(pythonClient, file_path):
    """Send data from a csv file to Phis.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param file_path: path of the csv file
            :type file_path: str
            :return: list of the uris of the data sent in phis
            :rtype: str list
    """
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)
    data_list = get_data_list(file_path)
    try:
        # Add data
        api_response = api_instance.add_list_data(body=data_list, )
        return api_response['result']
    except ApiException as e:
        print("Exception when calling DataApi->post_data_file: %s\n" % e)


def get_data_list(file_path):
    """Create a list of data contained in a csv file.

                :param file_path: path of the csv file
                :type file_path: str
                :return: list of data
                :rtype: DataCreationDTO list
    """
    data_list = []
    with open(file_path, 'r', encoding="windows-1252") as file:
        reader = csv.reader(file, delimiter=',')
        line_count = 0
        for row in reader:
            if line_count != 0:
                try:
                    date_str = date.transformDate(row[1])
                except ValueError:
                    date_str = row[1]
                if row[9] != "":
                    data = opensilexClientToolsPython.DataCreationDTO(uri=row[0], _date=date_str,
                                                                      variable=row[5],
                                                                      scientific_object=row[4],
                                                                      value=float(row[6].replace(",", ".")),
                                                                      provenance=opensilexClientToolsPython.DataProvenanceModel(
                                                                          uri=row[8], experiments=[row[3]], prov_used=[
                                                                              opensilexClientToolsPython.ProvEntityModel(
                                                                                  uri=row[9],
                                                                                  rdf_type="http://www.opensilex.org/vocabulary/oeso#Image")]),
                                                                      metadata=row[10])
                else:
                    data = opensilexClientToolsPython.DataCreationDTO(uri=row[0], _date=date_str,
                                                                      variable=row[5],
                                                                      scientific_object=row[4],
                                                                      value=float(row[6].replace(",", ".")),
                                                                      provenance=opensilexClientToolsPython.DataProvenanceModel(
                                                                          uri=row[8], experiments=[row[3]]),
                                                                      metadata=row[10])
                data_list.append(data)
            line_count += 1
    return data_list


def delete_data(pythonClient, data_list):
    """Delete data in a list of uris.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param data_list: list of data uris
            :type data_list: list[str]

    """
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)
    try:
        for data in data_list:
            # Delete data
            api_response = api_instance.delete_data(data, )
    except ApiException as e:
        print("Exception when calling DataApi->delete_data: %s\n" % e)


def collect_info_of_plant(pythonClient, plant_name, experiment_uri, start_date, end_date):
    plant_uri = scientific_object.find_scientific_object(pythonClient, plant_name, experiment_uri, "vocabulary:Plant")[0]
    data_list = find_data(pythonClient, plant_uri, experiment_uri, start_date, end_date)
    return data_list


def find_data(pythonClient, scientific_object, experiment, start_date=None, end_date=None):
    """Find data linked with a scientific object, created between start date and end date.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param scientific_object: uri of the scientific_object
            :type scientific_object: str
            :param experiment: uri of the experiment of the scientific object
            :type experiment: str
            :param start_date: min date of creation of the data
            :type start_date: str
            :param end_date: max date of creation of the data
            :type end_date: datetime.date
            :return: data list
            :rtype: list[DataGetDTO]

    """
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)
    if type(start_date) == datetime.date:
        start_date = datetime.date.strftime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    if type(end_date) == datetime.date:
        end_date = datetime.date.strftime(end_date, "%Y-%m-%dT%H:%M:%S.%fZ")
    try:
        # Search data
        api_response = \
        api_instance.search_data_list(experiment=[experiment], scientific_objects=[scientific_object], start_date=start_date,
                                      end_date=end_date, page_size=100)['result']
        return api_response
    except ApiException as e:
        print("no data found for object " + scientific_object)


def find_data_bis(pythonClient, scientific_object, experiment):
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)
    try:
        # Search data
        data_list = []
        api_response = api_instance.search_data_list(experiment=[experiment], scientific_objects=[scientific_object])['result']
        for data in api_response:
            data_list.append(data.uri)
        return data_list
    except ApiException as e:
        print("no data found for object " + scientific_object)