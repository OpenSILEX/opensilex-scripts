import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException
import json

from phis_functions import date


def add_image(pythonClient, path, date_str, scientific_object, provenance, experiment, prov_object_type):
    """Add an image to a scientific object

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param path: absolute path where the file is located (locally)
                :type path: str
                :param date_str: creation date of the file
                :type date_str: str
                :param scientific_object: uri of the scientific object to be linked with the image
                :type scientific_object: str
                :param provenance: provenance of the image
                :type provenance: str
                :return: api response to the request
                :rtype: ObjectUriResponse
    """
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)
    description = {"rdf_type": "http://www.opensilex.org/vocabulary/oeso#Image", "date": date.transformDate(date_str),
                   "scientific_object": scientific_object, "provenance": {"uri": provenance, "prov_used": [
            {"uri": scientific_object, "rdf_type": prov_object_type}], "experiments": [experiment]}}
    description_json = json.dumps(description)
    try:
        start_date = date.transformDate(date_str)
        end_date = date.add_1s(date.transformDate(date_str))
        # First check if the datafile already exists, if yes return its uri
        check_exist = api_instance.get_data_file_descriptions_by_search(rdf_type="http://www.opensilex.org/vocabulary/oeso#Image", start_date=start_date, end_date=end_date,  experiment=[experiment], scientific_objects=[scientific_object], provenances=[provenance], )
        if check_exist['result'] != [] :
            return check_exist['result'][0].uri
        else:
            # Add a data file
            api_response = api_instance.post_data_file(description_json, path, )
            return api_response['result'][0]
    except ApiException as e:
        print("Exception when calling DataApi->post_data_file: %s\n" % e)