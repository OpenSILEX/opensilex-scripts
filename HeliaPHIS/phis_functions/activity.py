#******************************************************************************
# // activity.py
# // Eva Minot
# // OpenSILEX - Licence AGPL V3.0 - https://www.gnu.org/licenses/agpl-3.0.en.html
# // OpenSILEX - ClientToolsPyhton V1.0.0-beta+2 - https://github.com/OpenSILEX/opensilexClientToolsPython/releases/tag/1.0.0-beta%2B2
# // Copyright © INRAE 2021
# // Contact: eva.mnt15@gmail.com, isabelle.alic@inrae.fr, nicolas.langlade@inrae.fr
# //*********

import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException

def create_activity(rdf_type, start_date=None):
    """Create an activity.

            :param rdf_type: type of the activity
            :type start_date: start date of the activity
            :return: Activity
            :rtype: ActivityCreationDTO
    """
    if start_date is not None:
        # need to reshape the date or error
        x = start_date.split()
        start_date = x[0] + "T" + x[1] + "Z"
    return opensilexClientToolsPython.ActivityCreationDTO(rdf_type=rdf_type, start_date=start_date)