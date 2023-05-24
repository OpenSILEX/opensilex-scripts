# Script to send temperatures data to the sandbox instance for demonstration purposes
# Gabriel Besombes

import opensilexClientToolsPython as oCTP
import requests
import yaml
from datetime import datetime
from argparse import ArgumentParser


def get_connected_data_api(
    host : str,
    identifier : str,
    password : str,
):
    """
    This function returns a connected instance of the OpenSilex data API client.
    
    :param host: The host parameter is a string that represents the URL or IP address of the server
    where the data API is hosted
    :type host: str
    :param identifier: The identifier parameter is a string that represents the user's identification or
    username used to authenticate and connect to the OpenSilex web service
    :type identifier: str
    :param password: The password parameter is a string that represents the password required to
    authenticate the user with the specified identifier to access the OpenSilex web service hosted at
    the specified host
    :type password: str
    :return: an instance of the `DataApi` class from the `opensilexClientToolsPython` module, which is connected to an
    OpenSilex web service using the provided `host`, `identifier`, and `password` parameters.
    """
    my_client = oCTP.ApiClient(verbose=True) 
    my_client.connect_to_opensilex_ws(
        host=host,
        identifier=identifier,
        password=password,
    )
    data_api = oCTP.DataApi(my_client)
    return data_api

def get_current_temperature_from_open_meteo_api(
    latitude : str = "43.617460159728644",
    longitude : str = "3.8548877153186276"
):
    """
    This function retrieves the current temperature from the Open Meteo API for a given latitude and
    longitude.
    
    :param latitude: The latitude of the location for which we want to get the current temperature. In
    this case, it is set to the latitude of Montpellier SupAgro, a French agricultural university,
    defaults to 43.617460159728644
    :type latitude: str (optional)
    :param longitude: The longitude of the location for which we want to get the current temperature. In
    this case, it is set to the longitude of Montpellier SupAgro, a French agricultural university,
    defaults to 3.8548877153186276
    :type longitude: str (optional)
    :return: the current temperature in Celsius degrees at the specified latitude and longitude
    coordinates, obtained from the Open Meteo API.
    """
    url = "https://api.open-meteo.com/v1/forecast?latitude=" + latitude + "&longitude=" + longitude + "&current_weather=true"
    montpellier_supagro_temperature = requests.get(url).json()["current_weather"]["temperature"]
    return montpellier_supagro_temperature

def send_data_to_opensilex(
    value : float,
    data_api : oCTP.DataApi,
    variable : str = "http://opensilex.test/id/variable/air_temperature_datalogging_degreecelsius",
    provenance_uri : str = "opensilex-sandbox:id/provenance/datalogging",
    device_uri : str = "opensilex-sandbox:id/device/datalogging_temperature",
    device_rdf_type : str = "vocabulary:SensingDevice"
):
    """
    This function sends data to an OpenSilex instance with specified parameters.
    
    :param value: The value of the data point being sent to the OpenSilex platform. It should be a float
    value
    :type value: float
    :param data_api: The data_api parameter is an instance of the DataApi class, which is used to
    interact with the OpenSILEX API to send data
    :type data_api: opensilexClientToolsPython.DataApi
    :param variable: The URI of the OpenSILEX variable to which the data is being sent. In this case, it is
    "http://opensilex.test/id/variable/air_temperature_datalogging_degreecelsius".
    :type variable: str (optional)
    :param provenance_uri: The URI of the OpenSILEX provenance. In this case, it is set to "opensilex-sandbox:id/provenance/datalogging".
    :type provenance_uri: str (optional)
    :param device_uri: The URI of the OpenSILEX device used to collect the data,
    defaults to opensilex-sandbox:id/device/datalogging_temperature
    :type device_uri: str (optional)
    :param device_rdf_type: device_rdf_type is a string parameter that specifies the RDF type of the
    sensing device used to collect the data. It is used in the provenance information of the data to
    indicate the type of device used, defaults to vocabulary:SensingDevice
    :type device_rdf_type: str (optional)
    """
    data_api.add_list_data(
        body=[
            oCTP.DataCreationDTO(
                _date=datetime.now(), 
                variable=variable, 
                value=value, 
                provenance=oCTP.DataProvenanceModel(
                    uri=provenance_uri,
                    prov_was_associated_with=[oCTP.ProvEntityModel(
                        uri=device_uri, 
                        rdf_type=device_rdf_type
                    )]
                )
            )
        ]
    )

if __name__ == "__main__":
    """
    This Python script sends temperature data to an OpenSILEX instance for demonstration purposes, using
    data from the Open Meteo API.
    
    :param host: The OpenSILEX instance to send data to
    :type host: str
    :param identifier: The identifier is a parameter used for authentication on the OpenSILEX instance.
    :type identifier: str
    :param password: The password parameter is used for authentication on the OpenSILEX instance
    :type password: str
    :param config: Optional parameter to pass the OpenSILEX resources to link the data to and coordinates to get the temperature from.
    :type config: str (optional)
    :return: The script does not return anything, it sends data to an OpenSILEX instance.
    """

    parser = ArgumentParser()

    parser.add_argument(
        "-ho", "--host", 
        help="OpenSILEX instance to send data to",
        required=True
    )
    parser.add_argument(
        "-i", "--identifier", 
        help="Identifier for authentification on OpenSILEX instance",
        required=True
    )
    parser.add_argument(
        "-p", "--password", 
        help="Password for authentification on OpenSILEX instance",
        required=True
    )
    parser.add_argument(
        "-c", "--config", 
        help="Configuration yaml file",
        default=None,
        required=False
    )
    args=parser.parse_args()

    if args.config:
        with open(args.config, "r") as config_file:
            params = yaml.safe_load(config_file)
        send_data_to_opensilex(
            value=get_current_temperature_from_open_meteo_api(
                latitude=params["latitude"], 
                longitude=params["longitude"]
            ),
            data_api=get_connected_data_api(
                host=args.host,
                identifier=args.identifier,
                password=args.password,
            ),
            variable=params["variable"],
            provenance_uri=params["provenance_uri"],
            device_uri=params["device_uri"],
            device_rdf_type=params["device_rdf_type"]
        )
    else:
        send_data_to_opensilex(
            value=get_current_temperature_from_open_meteo_api(),
            data_api=get_connected_data_api(
                host=args.host,
                identifier=args.identifier,
                password=args.password,
            )
        )
        