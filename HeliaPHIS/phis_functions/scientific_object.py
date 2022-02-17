import datetime

import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def create_scientific_object(pythonClient, rdf_type, name, experiment, additional_information=None):
    """Create a scientific object in Phis.

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param name: name of the object
                :type name: str
                :param rdf_type: type of the object
                :type rdf_type: str
                :param experiment: uri of the experiment to which the object belongs
                :type experiment: str
                :param additional_information: list of other relations for the object
                :type additional_information: list[RDFObjectRelationDTO]
                :return: uri of the scientific object in phis
                :rtype: str
        """
    api_instance = opensilexClientToolsPython.ScientificObjectsApi(pythonClient)

    scientific_object = opensilexClientToolsPython.ScientificObjectCreationDTO(rdf_type=rdf_type, name=name,
                                                                               experiment=experiment,
                                                                               relations=additional_information)
    try:
        # Create a scientific object for the given experiment
        api_response = api_instance.create_scientific_object(scientific_object, )
        return api_response['result'][0]
    except ApiException as e:
        print("Exception when calling ScientificObjectsApi->create_scientific_object: %s\n" % e)


def find_scientific_object(pythonClient, name, experiment, rdf_type):
    """Find a scientific object in Phis by its name (can find several similar objects, for example some plants can
        be in the same pot and have almost the same name)

                   :param pythonClient: Current client in Phis
                   :type pythonClient: TokenGetDTO
                   :param name: Name of the scientific object
                   :type name: str
                   :param experiment: Uri of the scientific object's experiment (mandatory or too slow)
                   :type experiment: str
                   :param rdf_type: type of scientific object to be created
                   :type rdf_type: str
                   :return: Uri(s) of the scientific object(s)
                   :rtype: list[str]
    """
    api_instance = opensilexClientToolsPython.ScientificObjectsApi(pythonClient)
    try:
        api_response = api_instance.search_scientific_objects(name=name, experiment=experiment, rdf_types=[rdf_type],
                                                              page_size=200)
        # can fin more than one scientific object (two or more plants in one pot)
        uris = []
        for result in api_response['result']:
            uris.append(result.uri)
        return uris
    except ApiException as e:
        print("Exception when calling ScientificObjectsApi->search_scientific_objects: %s\n" % e)


def delete_scientific_object(pythonClient, uri, experiment):
    """Delete a scientific object.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param uri: uri of the scientific object to be deleted
            :type uri: str
            :param experiment: uri of the experiment of the scientific object
            :type experiment: str

    """
    api_instance = opensilexClientToolsPython.ScientificObjectsApi(pythonClient)
    try:
        # Delete a scientific object
        api_response = api_instance.delete_scientific_object(uri=uri, experiment=experiment, )
    except ApiException as e:
        print("Exception when calling ScientificObjectsApi->delete_scientific_object: %s\n" % e)


def create_object_relation(property, value):
    """Create a relation for a scientific object.

            :param property: name of the property
            :type property: str
            :param value: value associated to the property
            :type value: depends on the type of value expected for the property
            :return: relation
            :rtype: RDFObjectRelationDTO
    """
    return opensilexClientToolsPython.RDFObjectRelationDTO(_property=property, value=value)


def set_textual_position(pythonClient, target, position):
    """Creates a move on an object (target) to set its local position (in the field textual position)

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param target: uri of the object on which we want to make the move
                :type target: str
                :param position: new position to indicate
                :type position: str

    """
    api_instance = opensilexClientToolsPython.EventsApi(pythonClient)
    textual_position = opensilexClientToolsPython.PositionCreationDTO(text=position)
    targets_position = [
        opensilexClientToolsPython.ConcernedItemPositionCreationDTO(target=target, position=textual_position)]
    date = datetime.datetime.strftime(datetime.datetime.today(), "%Y-%m-%dT%H:%M:%S-%m:%H")
    body = [opensilexClientToolsPython.MoveCreationDTO(targets=[target], targets_positions=targets_position,
                                                       is_instant=True, start=date,
                                                       end=date)]  # list[MoveCreationDTO] |  (optional)

    try:
        # Create a list of move event
        api_response = api_instance.create_moves(body=body, )
    except ApiException as e:
        print("Exception when calling EventsApi->create_moves: %s\n" % e)


def get_all_objects_of_experiment(pythonClient, experiment_uri, rdf_types):
    """Get all the scientific objects of a certain type of an experiment

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param experiment_uri: uri of the experiment
                :type experiment_uri: str
                :param rdf_type: types of objects you want to get
                :type rdf_type: list[str]
                :return: list of scientific objects
                :rtype: list[str]

    """
    api_instance = opensilexClientToolsPython.ScientificObjectsApi(pythonClient)

    try:
        # Search list of scientific objects
        api_response = api_instance.search_scientific_objects(experiment=experiment_uri, rdf_types=rdf_types,
                                                              page_size=100, )

        return api_response['result']
    except ApiException as e:
        print("Exception when calling ScientificObjectsApi->search_scientific_objects: %s\n" % e)