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