import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


import json

from phis_functions import agent, event


def create_provenance(pythonClient, name, date, prov_agent, prov_activity, description=None):
    """Create a provenance for data IF new settings in one of the agent are detected, otherwise returns the uri of the last provenance used for these agents.

            :param pythonClient: Current client in phis
            :type pythonClient: TokenGetDTO
            :param name: Name of the provenance
            :type name: str
            :param prov_agent: Agent(s) involved in the collection of the data
            :type prov_agent: list[AgentModel]
            :param prov_activity: Activity representing the data acquisition
            :type prov_activity: ActivityCreationDTO
            :param description: description of the provenance
            :type description: str, optional
            :return: Provenance uri
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)

    try:
        new_prov_agent = []
        create_new_provenance = False
        full_name = name + "_" + date
        # we check if we can find a similar provenance that was created before (we take the last one created)
        last_provenance = find_provenance(pythonClient, prov_agent, name)
        # if there is no similar provenance that has been created before, create it directly
        if last_provenance is None:
            for agent_object in prov_agent:
                # we check the last calibration that has been made on the device
                try:
                    last_calibration = event.find_event(pythonClient, agent_object.uri, "oeev:Calibration")
                    if last_calibration is not None:
                        new_prov_agent.append(
                            agent.create_agent(agent_object.uri, agent_object.rdf_type, json.loads(last_calibration.description)))
                    else:
                        new_prov_agent.append(agent_object)

                except IndexError:
                    new_prov_agent.append(agent_object)
            provenance = opensilexClientToolsPython.ProvenanceCreationDTO(uri=None, name=full_name,
                                                                          description=description,
                                                                          prov_activity=prov_activity,
                                                                          prov_agent=new_prov_agent)
            # Add the provenance to PHIS
            provenance_uri = api_instance.create_provenance(body=provenance, )['result'][0]

        # else if there is a similar provenance that was created before
        else:
            for agent_object in last_provenance.prov_agent:
                try:
                    # we check the last calibration that has been made on the device
                    last_calibration = event.find_event(pythonClient, agent_object.uri, "oeev:Calibration")
                    # if a calibration has been made after the last provenance that exists, we need to create a new provenance
                    if last_calibration is not None and agent_object.settings != json.loads(last_calibration.description):
                        new_prov_agent.append(
                            agent.create_agent(agent_object.uri, agent_object.rdf_type, json.loads(last_calibration.description)))
                        create_new_provenance = True
                    # if no calibration has been made after the last provenance was created, we don't need to change the settings of the agent
                    else:
                        new_prov_agent.append(agent_object)

                except IndexError:
                    new_prov_agent.append(agent_object)
            if create_new_provenance:
                provenance_object = opensilexClientToolsPython.ProvenanceCreationDTO(uri=None, name=full_name,
                                                                              description=description,
                                                                              prov_activity=prov_activity,
                                                                              prov_agent=new_prov_agent)
                # Add the provenance to PHIS
                provenance_uri = api_instance.create_provenance(body=provenance_object, )['result'][0]
            else:
                # a provenance already exists for the last calibration made so we don't need to create one
                provenance_uri = last_provenance.uri
        # return the URI of the provenance
        return provenance_uri
    except ApiException as e:
        print("Exception when calling DataApi->create_provenance: %s\n" % e)


def delete_provenance(pythonClient, uri):
    """Delete a provenance.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param uri: uri of the provenance
            :type uri: str
    """
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)
    try:
        # Add the provenance to PHIS
        api_response = api_instance.delete_provenance(uri, )
    except ApiException as e:
        print("Exception when calling DataApi->delete_provenance: %s\n" % e)


def find_provenance(pythonClient, prov_agent, name):
    """Find the last provenance that was created with a specific list of agents.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the provenance
            :type name: str
            :param prov_agent: list of agents that were used to create the provenance
            :type prov_agent: list[AgentModel]
            :return: uri of the last provenance found
            :rtype: str

    """
    # find the last provenance that matches a name pattern and that has the agents listed in prov_agent
    api_instance = opensilexClientToolsPython.DataApi(pythonClient)
    order_by = ['name=desc']
    try:
        # Get provenances
        provenances = api_instance.search_provenance(name=name, agent=prov_agent[0].uri, order_by=order_by)['result']
        agent_list1 = []
        for agent in prov_agent:
            agent_list1.append(agent.uri)
        for provenance in provenances:
            agent_list2 = []
            for agent in provenance.prov_agent:
                agent_list2.append(agent.uri)
            if agent_list1 == agent_list2:
                return provenance
    except ApiException as e:
        print("Exception when calling DataApi->search_provenance: %s\n" % e)

