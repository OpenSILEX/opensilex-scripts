import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def find_variable(pythonClient, name):
    """Find the uri of a variable.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the variable
            :type name: str
            :return: uri of the variable in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.VariablesApi(pythonClient)
    try:
        # Search variables by name, long name, entity, characteristic, method or unit name
        api_response = api_instance.search_variables(name=name)
        return api_response['result'][0].uri
    except ApiException as e:
        print("Exception when calling VariablesApi->search_variables: %s\n" % e)
