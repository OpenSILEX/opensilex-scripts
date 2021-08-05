import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def find_event(pythonClient, device_uri, rdf_type=""):
    """Find the last event (of a specific type) in Phis that occurred on a specific device.

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param device_uri: uri of the device on which the event occurred
                :type device_uri: str
                :param rdf_type: type of event we are looking for
                :type rdf_type: str
                :return: uri of the last event found
                :rtype: str

    """
    api_instance = opensilexClientToolsPython.EventsApi(pythonClient)
    try:
        # Search events
        # order by descending end date because we want the last event
        api_response = api_instance.search_events(rdf_type=rdf_type, target=device_uri, order_by=["end=desc"], )
        # return the last event that occurred
        return api_response['result'][0]
    except ApiException as e:
        print('No calibration for this agent')


def delete_event(pythonClient, event_uri, move=False):
    """Delete an event.

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param event_uri: uri of the event to delete
                :type event_uri: str
                :param move: indicates if the event is a move or not
                :type move: bool

    """
    api_instance = opensilexClientToolsPython.EventsApi(pythonClient)
    try:
        if move:
            # Delete a move event
            api_response = api_instance.delete_move_event(event_uri, )
        else:
            # Delete an event
            api_response = api_instance.delete_event(event_uri, )
    except ApiException as e:
        print("Exception when calling EventsApi->delete_move_event: %s\n" % e)


def create_event(pythonClient, device_uri, rdf_type, date, description):
    """Create an event of a certain type for a specific device.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param device_uri: uri of the device
            :type device_uri: str
            :param rdf_type: type of event we want to create
            :type rdf_type: str
            :param date: date of the event
            :type date: str
            :param description: description of the event
            :type description: str

    """
    api_instance = opensilexClientToolsPython.EventsApi(pythonClient)
    body = [
        opensilexClientToolsPython.EventCreationDTO(rdf_type=rdf_type, end=date, is_instant=True, targets=[device_uri],
                                                    description=description)]  # list[EventCreationDTO] |  (optional)

    try:
        # Create a list of event
        api_response = api_instance.create_events(body=body, )
    except ApiException as e:
        print("Exception when calling EventsApi->create_events: %s\n" % e)