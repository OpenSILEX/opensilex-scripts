import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def create_agent(uri, rdf_type, settings=None):
    """Create an agent with the model used in phis.

            :param uri: uri of the agent
            :type uri: str
            :param rdf_type: type of the agent
            :type rdf_type: str
            :return: Model of the agent needed
            :rtype: AgentModel
    """
    return opensilexClientToolsPython.AgentModel(uri=uri, rdf_type=rdf_type, settings=settings)


def find_agent(pythonClient, name):
    """Find an agent in Phis by its name.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the agent
            :type name: str
            :return: Model of the agent found (with its uri and its type)
            :rtype: AgentModel

    """
    api_instance = opensilexClientToolsPython.DevicesApi(pythonClient)
    try:
        # Search devices
        api_response = api_instance.search_devices(name=name)
        uri = api_response['result'][0].uri
        rdf_type = api_response['result'][0].rdf_type
        agent = create_agent(uri=uri, rdf_type=rdf_type)
        return agent
    except ApiException as e:
        print("Exception when calling DevicesApi->search_devices: %s\n" % e)