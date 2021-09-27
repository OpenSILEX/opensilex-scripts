import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def create_experiment(pythonClient, name, start_date, objective, description, species, organisations, projects,
                      scientific_supervisors):
    """Create an experiment in Phis.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the experiment
            :type name: str
            :param start_date: start_date of the experiment
            :type start_date: str
            :param objective: objective of the experiment
            :type objective: str
            :param description: description of the experiment
            :type description: str
            :param species: species on which the experiment is/was done (list of uris)
            :type species: list[str]
            :param organisations: list of organisations related to the experiment (list of uris)
            :type organisations: list[str]
            :param projects: list of projects related to the experiment (list of uris)
            :type projects: list[str]
            :param scientific_supervisors: list of the scientific supervisors of the experiment (list of uris)
            :type scientific_supervisors: list[str]
            :return: uri corresponding to the experiment created in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.ExperimentsApi(pythonClient)
    body = opensilexClientToolsPython.ExperimentCreationDTO(name=name, start_date=start_date, objective=objective,
                                                            description=description, species=species,
                                                            organisations=organisations, projects=projects,
                                                            scientific_supervisors=scientific_supervisors)
    try:
        # Add an experiment
        api_response = api_instance.create_experiment(body=body, )
        return api_response['result'][0]
    except ApiException as e:
        print("Exception when calling ExperimentsApi->create_experiment: %s\n" % e)


def find_experiment_by_name(pythonClient, name):
    """Find an experiment in Phis by its name (we suppose that experiments dont't have similar names so only
        one result will be found)

                   :param pythonClient: Current client in Phis
                   :type pythonClient: TokenGetDTO
                   :param name: Name of the experiment
                   :type name: str
                   :return: uri of the experiment
                   :rtype: list[str]
    """
    api_instance = opensilexClientToolsPython.ExperimentsApi(pythonClient)
    try:
        api_response = api_instance.search_experiments(name=name)
        return api_response['result'][0].uri
    except ApiException as e:
        print("Exception when calling ExperimentsApi->search_experiments: %s\n" % e)


def find_experiment_by_uri(pythonClient, uri):
    """Find an experiment in Phis by its uri (useful to check the validity of a provided uri for an experiment).

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param uri: uri of the experiment
            :type uri: str
            :return: experiment attributes
            :rtype: ExperimentGetDTO
    """
    api_instance = opensilexClientToolsPython.ExperimentsApi(pythonClient)
    try:
        # Get an experiment
        api_response = api_instance.get_experiment(uri, )
        return api_response['result']
    except ApiException as e:
        print("Exception when calling ExperimentsApi->get_experiment: %s\n" % e)


def get_experiment_name(pythonClient, experiment_uri):
    """Get the name of an experiment.

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param experiment_uri: uri of the experiment
                :type experiment_uri: str
                :return: name of the experimentF
                :rtype: str

    """
    api_instance = opensilexClientToolsPython.ExperimentsApi(pythonClient)
    try:
        # Get an experiment
        api_response = api_instance.get_experiment(experiment_uri, )
        return api_response['result'].name
    except ApiException as e:
        print("Exception when calling ExperimentsApi->get_experiment: %s\n" % e)


def get_experiment_period(pythonClient, experiment_uri):
    """Get the start and end date of an experiment

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param experiment_uri: uri of the experiment
                :type experiment_uri: str
                :return: start date and end date
                :rtype: list[datetime]

    """
    api_instance = opensilexClientToolsPython.ExperimentsApi(pythonClient)
    try:
        # Get an experiment
        api_response = api_instance.get_experiment(experiment_uri, )
        start_date = api_response['result'].start_date
        end_date = api_response['result'].end_date
        return [start_date, end_date]
    except ApiException as e:
        print("Exception when calling ExperimentsApi->get_experiment: %s\n" % e)

