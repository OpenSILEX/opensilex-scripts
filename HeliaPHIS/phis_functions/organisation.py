import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def find_organisation(pythonClient, name):
    """Find an organisation in Phis by its name.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the organisation
            :type name: str
            :return: uri corresponding to the organisation in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.OrganisationsApi(pythonClient)
    try:
        # Search organisations
        api_response = api_instance.search_infrastructures_tree(pattern=name, )
        return api_response['result'][0].children[0].uri
    except ApiException as e:
        print("Exception when calling OrganisationsApi->search_infrastructures_tree: %s\n" % e)
