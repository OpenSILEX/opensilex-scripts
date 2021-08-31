#******************************************************************************
# // project.py
# // Eva Minot
# // OpenSILEX - Licence AGPL V3.0 - https://www.gnu.org/licenses/agpl-3.0.en.html
# // OpenSILEX - ClientToolsPyhton V1.0.0-beta+2 - https://github.com/OpenSILEX/opensilexClientToolsPython/releases/tag/1.0.0-beta%2B2
# // Copyright © INRAE 2021
# // Contact: eva.mnt15@gmail.com, isabelle.alic@inrae.fr, nicolas.langlade@inrae.fr
# //*********

import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def find_project(pythonClient, name):
    """Find a project in Phis by its name.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the project
            :type name: str
            :return: uri corresponding to the project in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.ProjectsApi(pythonClient)
    try:
        # Search projects
        api_response = api_instance.search_projects(name=name)
        return api_response["result"][0].uri
    except ApiException as e:
        print("Exception when calling ProjectsApi->search_projects: %s\n" % e)