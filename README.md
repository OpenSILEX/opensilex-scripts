# opensilex-ws-client-use-cases

This project will catch all scripts that have been made using OpenSILEX clients.

If you want to add to this repo you should give these informations :

* Contact info
* Version of the opensilexClientToolsPython package you used (and additional requirements)
* Add examples and description text (can include diagrams and images)

## Structure

```bash
.
├── Example
│   ├── GrainSample.csv
│   └── GrainSample_secondary_var_test.ipynb
└── HeliaPHIS
```

### HeliaPhis scripts (Author : Eva Minot)

* Add_data_from_images_to_process : script files allowing to automate the processing of image files by software (here IPSO Phen),  the data csv of the output of the processing allows the creation of one (or more) new ( x) csv adapted to the phis data format to be able to send them to phis afterwards.

* Add_data_from_csv : scripts folder to retrieve the desired data in a csv and put them in a new csv adapted to PHIS data format to be able to send them to PHIS.

* Create_csv_of_data_for_phis  :script that allows you to create csv adapted to PHIS data format, taking into account the maximum limit for sending at one time (which is 50,000).
