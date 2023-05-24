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
        