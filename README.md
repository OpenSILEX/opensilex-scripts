# opensilex-scripts

This repository will contain different scripts that have been made using the OpenSILEX clients or that directly call the OpenSILEX webservices.

If you want to add to this repo you should give these informations :

* Contact info
* Version of OpenSILEX and client package used (and additional requirements)
* Add examples and description text (can include diagrams and images)

## Structure

```bash
.
├── Adonis
├── Check_agrovoc_uris
├── Example
│   ├── GrainSample.csv
│   └── GrainSample_secondary_var_test.ipynb
├── HeliaPHIS
├── Internship_interoperability
│   ├── Applications
│   │   ├── App_verif_germplasm
│   │   └── ITKtoPHIS
│   └── SIG
├── Sensor_showcase
│   ├── phis-egi-demo_config.yml
│   ├── sandbox_config.yml
│   ├── send_data_regularly.py
│   └── test_config.yml
└── README.md
```

### Adonis (Author : Jean-Eudes Hollebecq)

Scripts to extract data from Adonis' xml outputs and upload it to  OpenSILEX.

### Check_agrovoc_uris (Author : Gabriel Besombes)

Notebook to check for mistakes in the concepts from agrovoc that are used to declare germplasms

### Example (Author : Gabriel Besombes)

Simple examples of scripts in jupyter notebook format.

### HeliaPhis (Author : Eva Minot)

* Add_data_from_images_to_process : script files allowing to automate the processing of image files by software (here IPSO Phen),  the data csv of the output of the processing allows the creation of one (or more) new ( x) csv adapted to the phis data format to be able to send them to phis afterwards.

* Add_data_from_csv : scripts folder to retrieve the desired data in a csv and put them in a new csv adapted to PHIS data format to be able to send them to PHIS.

* Create_csv_of_data_for_phis  :script that allows you to create csv adapted to PHIS data format, taking into account the maximum limit for sending at one time (which is 50,000).

### Internship_interoperability (Author : Paul Faucher)

* Application/App_verif_germplasm : application to check germplasm existance/validity against an opensilex instance

* Application/ITKtoPHIS : application to import treatment data from Geofolia into an opensilex instance

* SIG : __NOTE__ This is quite specific to "Unité Expérimentale d'AgroEcologie et de Phénotypage des Cultures, Toulouse" from INRAE and to ArcGIS but can still be usefull for other applications. This is meant to facilitate the exchange of data between an opensilex instance and an ArcGIS server.

### Sensor_showcase (Author : Gabriel Besombes)

* send_data_regularly.py : script to get data from a free weather api to simulate a weather sensor and send said data to an opensilex instance.
* .yml files : configuration files used by the script.
* send_data_regularly.md : documentation sur le script.