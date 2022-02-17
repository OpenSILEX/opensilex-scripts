import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def find_user(pythonClient, name):
    """Find an user in Phis by its name.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the user
            :type name: str
            :return: uri corresponding to the user in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.SecurityApi(pythonClient)
    try:
        # Search users
        api_response = api_instance.search_users(name=name)
        return api_response['result'][0].uri
    except ApiException as e:
        print("Exception when calling SecurityApi->search_users: %s\n" % e)