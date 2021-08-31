#******************************************************************************
# //delete_objects.py
# // Eva Minot
# // OpenSILEX - Licence AGPL V3.0 - https://www.gnu.org/licenses/agpl-3.0.en.html
# // OpenSILEX - ClientToolsPyhton V1.0.0-beta+2 - https://github.com/OpenSILEX/opensilexClientToolsPython/releases/tag/1.0.0-beta%2B2
# // Copyright © INRAE 2021
# // Contact: eva.mnt15@gmail.com, isabelle.alic@inrae.fr, nicolas.langlade@inrae.fr
# //*********

from phis_functions import connection, scientific_object, event

# put your correct information here
identifier="your_id"
pwd = 'your_password'
client = connection.connect_to_phis(identifier, pwd)
experiment = "uri of the experiment"

while True :
    # remplacer le 2eme argument par le nom par lequel les objets commencent
    # remplacer le dernier argument par le type d'objet à supprimer (vocabulary:Pot ou vocabulary:Plant)
    objects = scientific_object.find_scientific_object(client, "common part of the objects names", experiment, "vocabulary:Pot")
    if len(objects) == 0:
        break
    for object in objects:
        events = event.find_event(client, object)
        print(events)
        for event in events:
            event.delete_event(client, event.uri, True)

        event.delete_scientific_object(client, object, experiment)
