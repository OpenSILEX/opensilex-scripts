---
title: Envoi de données de façon régulière
---

## Généralités

Pour l'envoi de données de façon régulière nous utilisons un script python qui envoie une seule donnée récupérée depuis une API. Ce script est appelé de façon régulière grace à un 'Schedule' Gitlab. Pour d'autres utilisation cela peut être remplacé par [Cron](https://doc.ubuntu-fr.org/cron) sur linux par exemple.

## Fonctionnement du script python

La récupération de données de températures passe par une [API gratuite](https://open-meteo.com/en/docs).
L'appel à cette API et l'envoi des données sont réalisés par le script python send_data_regularly.py

Ce script a besoin au moins de l'adresse de l'instance sur laquelle on veut envoyer les données ainsi que de l'identifiant et du mot de passe.
Il est aussi possible d'ajouter un fichier yaml de configuration (voir les différents fichiers _config.yml d'exemples).

Détails de la config :

```yml
# Geographical location to get temperature from
# This one is the "La Gaillarde" campus in Montpellier, France
latitude: "43.617460159728644"
longitude: "3.8548877153186276"

# These elements must exist in the corresponding OpenSILEX instance
variable: "http://opensilex.test/id/variable/air_temperature_datalogging_degreecelsius"
provenance_uri: "opensilex-sandbox:id/provenance/datalogging"
device_uri: "opensilex-sandbox:id/device/datalogging_temperature"
device_rdf_type: "vocabulary:SensingDevice"
```

Ces valeurs sont celles par défaut. Une configuration doit contenir __tous ces champs__.

Pour obtenir de l'aide sur ce script le flag -h est disponible :

```bash
python3 send_data_regularly.py -h
usage: send_data_regularly.py [-h] -ho HOST -i IDENTIFIER -p PASSWORD [-c CONFIG]

optional arguments:
  -h, --help            show this help message and exit
  -ho HOST, --host HOST
                        OpenSILEX instance to send data to
  -i IDENTIFIER, --identifier IDENTIFIER
                        Identifier for authentification on OpenSILEX instance
  -p PASSWORD, --password PASSWORD
                        Password for authentification on OpenSILEX instance
  -c CONFIG, --config CONFIG
                        Configuration yaml file
```
