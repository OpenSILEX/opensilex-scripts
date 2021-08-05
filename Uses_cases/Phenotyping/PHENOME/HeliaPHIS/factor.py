import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def create_factor(pythonClient, name, experiment, level_names):
    """Create a factor.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the factor
            :type name: str
            :param experiment: uri of the experiment where the factor is used
            :type experiment: str
            :param level_names: list of factor levels (names)
            :type level_names: list[str]
    """
    api_instance = opensilexClientToolsPython.FactorsApi(pythonClient)

    levels = []
    try:
        # search if the factor already exists for this experiment
        exists = api_instance.search_factors(name=name, experiment=experiment)
        if exists['result']:
            factor_uri = exists['result'][0].uri
            # this factor already exists, check if the level also exists
            for level_name in level_names:
                levels.append(opensilexClientToolsPython.FactorLevelCreationDTO(name=level_name))
            if levels:
                factor_update = opensilexClientToolsPython.FactorUpdateDTO(uri=factor_uri, name=name, levels=levels)
                api_response = api_instance.update_factor(body=factor_update, )

        else:
            # the factor doesn't exist, create it
            for level_name in level_names:
                levels.append(opensilexClientToolsPython.FactorLevelCreationDTO(name=level_name))
            factor = opensilexClientToolsPython.FactorCreationDTO(name=name, experiment=experiment, levels=levels)
            api_instance.create_factor(body=factor, )
            factor_uri = api_instance.search_factors(name=name, experiment=experiment)['result'][0].uri
        return factor_uri
    except ApiException as e:
        print("Exception when calling FactorsApi->update_factor: %s\n" % e)


def get_factor_level(pythonClient, factor_uri, name):
    """Get a specific factor level of a factor.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the factor_level
            :type name: str
            :param factor_uri: uri of the factor
            :type factor_uri: str
            :return: uri of the factor level
            :rtype: str

    """
    api_instance = opensilexClientToolsPython.FactorsApi(pythonClient)
    try:
        # Get factor levels
        factor_levels = api_instance.get_factor_levels(factor_uri, )['result']
        for factor_level in factor_levels:
            if factor_level.name == name:
                return factor_level.uri
    except ApiException as e:
        print("Exception when calling FactorsApi->get_factor_levels: %s\n" % e)
