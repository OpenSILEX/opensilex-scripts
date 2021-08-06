import opensilexClientToolsPython
from opensilexClientToolsPython.rest import ApiException


def create_germplasm(pythonClient, name, species, variety):
    """Create a germplasm in Phis (seed lot), or return its uri if it already exists.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the germplasm
            :type name: str
            :param species: species of the germplasm
            :type species: str
            :param variety: variety of the germplasm
            :type variety: str
            :return: uri corresponding to the germplasm created/found in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.GermplasmApi(pythonClient)

    try:
        # check if already exists
        check_exist = api_instance.search_germplasm(name=name, rdf_type="vocabulary:SeedLot", species=species,
                                                    variety=variety)
        if len(check_exist['result']) != 0:
            return check_exist['result'][0].uri
        else:
            germplasm = opensilexClientToolsPython.GermplasmCreationDTO(name=name, rdf_type="vocabulary:SeedLot",
                                                                        species=species,
                                                                        variety=variety)
            # Add a germplasm
            api_response = api_instance.create_germplasm(body=germplasm, )
            return api_response['result'][0]
    except ApiException as e:
        print("Exception when calling GermplasmApi->create_germplasm: %s\n" % e)


def create_variety(pythonClient, name, species):
    """Create a variety in Phis, or simply return the uri of the variety if it already exists.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the variety
            :type name: str
            :param species: uri of the variety's species
            :type species: str
            :return: uri corresponding to the variety created/found in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.GermplasmApi(pythonClient)

    try:
        # check if already exists
        check_exist = api_instance.search_germplasm(name=name, rdf_type="vocabulary:Variety", species=species)
        if len(check_exist['result']) != 0:
            return check_exist['result'][0].uri
        else:
            germplasm = opensilexClientToolsPython.GermplasmCreationDTO(name=name, rdf_type="vocabulary:Variety",
                                                                        species=species)
            # Add a variety
            api_response = api_instance.create_germplasm(body=germplasm, )
            return api_response['result'][0]
    except ApiException as e:
        print("Exception when calling GermplasmApi->create_germplasm: %s\n" % e)


def find_species(pythonClient, name):
    """Try to find a species in Phis. If the species is found, return its uri, otherwise create it and return the uri.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the species
            :type name: str
            :return: uri corresponding to the species created or found in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.SpeciesApi(pythonClient)

    try:
        # get species (no pagination)
        list_species = api_instance.get_all_species()['result']
        for species in list_species:
            if species.name == name:
                return species.uri
        # if no species has been found, we create one
        return create_species(pythonClient, name)
    except ApiException as e:
        print("Exception when calling SpeciesApi->get_all_species: %s\n" % e)


def check_species_uri(pythonClient, species_uri):
    api_instance = opensilexClientToolsPython.GermplasmApi(pythonClient)
    try:
        # Search germplasm
        api_response = api_instance.search_germplasm(uri=species_uri, rdf_type="vocabulary:Species")
        if api_response['result']:
            return True
        else:
            return False
    except ApiException as e:
        print("Exception when calling GermplasmApi->search_germplasm: %s\n" % e)


def create_species(pythonClient, name):
    """Create a species in Phis.

            :param pythonClient: current client in phis
            :type pythonClient: TokenGetDTO
            :param name: name of the species
            :type name: str
            :return: uri corresponding to the species created in Phis
            :rtype: str
    """
    api_instance = opensilexClientToolsPython.GermplasmApi(pythonClient)

    try:
        # in phis, a species is a kind of germplasm, so we create a germplasm of type species
        species = opensilexClientToolsPython.GermplasmCreationDTO(name=name, rdf_type="vocabulary:Species")
        api_response = api_instance.create_germplasm(body=species, )
        return api_response['result'][0]
    except ApiException as e:
        print("Exception when calling GermplasmApi->create_germplasm: %s\n" % e)


def get_variety_of_seed_lot(pythonClient, seedLot):
    """Find the variety of a seed lot

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param seedLot: uri of the seed lot
                :type seedLot: str
                :return: variety(name)
                :rtype: str

    """
    api_instance = opensilexClientToolsPython.GermplasmApi(pythonClient)

    try:
        # Get a germplasm
        api_response = api_instance.get_germplasm(seedLot, )
        variety_uri = api_response['result'].variety
        variety_name = api_instance.get_germplasm(variety_uri, )
        return variety_name['result'].name
    except ApiException as e:
        print("Exception when calling GermplasmApi->get_germplasm: %s\n" % e)


def get_plant_genotype(pythonClient, plant_uri, experiment_uri):
    """Find the genotype (variety) of a plant.

                :param pythonClient: current client in phis
                :type pythonClient: TokenGetDTO
                :param plant_uri: uri of the plant
                :type plant_uri: str
                :param experiment_uri: uri of the experiment
                :type experiment_uri: str
                :return: name of the genotype
                :rtype: str

        """
    api_instance = opensilexClientToolsPython.ScientificObjectsApi(pythonClient)
    try:
        # Get scientific object detail
        api_response = api_instance.get_scientific_object_detail(plant_uri, experiment=experiment_uri, )
        # can have multiple relations, we are looking for the hasFactorLevel relation.
        for relation in api_response['result'].relations:
            # when we find it, we want to return its value
            if relation._property == 'vocabulary:hasGermplasm':
                seedlot_uri = relation.value
                genotype = get_variety_of_seed_lot(pythonClient, seedlot_uri)
                return genotype
        return None
    except ApiException as e:
        print("Exception when calling ScientificObjectsApi->get_scientific_object_detail: %s\n" % e)

