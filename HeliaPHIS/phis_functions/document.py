import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException
import json

def add_document(pythonClient, path, rdf_type, rdf_type_name, title, date, targets, format, authors=[]):
    """Add a document in an experiment.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param path: absolute path where the file is located (locally)
            :type path: str
            :param rdf_type: type of document
            :type rdf_type: str
            :param rdf_type_name: name of the document type
            :type rdf_type_name: str
            :param title: title of the document
            :type title: str
            :param date: creation date of the file
            :type date: str
            :param targets: list of experiment uris where the document should be added
            :type targets: list[str]
            :param format: file format
            :type format: str
            :param authors: authors of the document
            :type authors: list[str]
            :return: api response to the request
            :rtype: ObjectUriResponse
    """
    api_instance = opensilexClientToolsPython.DocumentsApi(pythonClient)
    description = {"rdf_type": rdf_type, "rdf_type_name": rdf_type_name, "title": title, "date": date,
                   "targets": targets, "authors": authors, "format": format}
    description_json = json.dumps(description)
    try:
        # Add a document
        api_response = api_instance.create_document(description_json, file=path, )
        return api_response
    except ApiException as e:
        print("Exception when calling DocumentsApi->create_document: %s\n" % e)
