#******************************************************************************
# //delete_data.py
# // Eva Minot
# // OpenSILEX - Licence AGPL V3.0 - https://www.gnu.org/licenses/agpl-3.0.en.html
# // OpenSILEX - ClientToolsPyhton V1.0.0-beta+2 - https://github.com/OpenSILEX/opensilexClientToolsPython/releases/tag/1.0.0-beta%2B2
# // Copyright © INRAE 2021
# // Contact: eva.mnt15@gmail.com, isabelle.alic@inrae.fr, nicolas.langlade@inrae.fr
# //*********

from phis_functions import connection, scientific_object, data

# put your correct information here
identifier="your_id"
pwd = 'your_password'
client = connection.connect_to_phis(identifier, pwd)
experiment = "uri of the experiment"

# change here the second argument by the name by which the objects start
# and last argument by the type of the objects you want to delete the data linked with
objects = scientific_object.find_scientific_object(client, "common part of the object names", experiment, "vocabulary:Pot")
print(objects)
for object in objects:
   print(object)
   while True:
      data_list = data.find_data_bis(client, experiment=experiment, scientific_object=object)
      if data_list == [] or data_list is None:
         break
      data.delete_data(client, data_list)