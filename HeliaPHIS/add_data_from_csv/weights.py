import csv
from datetime import datetime
import re
import time
import csv_phis
from phis_functions import activity, agent, provenance, experiment, variable, scientific_object

file_list = []


def add_1s(date_string):
    # convert date in string to datetime
    date = datetime.strptime(date_string, "%d-%m-%Y %H:%M:%S")
    # get the date in seconds, add 1
    seconds = date.timestamp() + 1
    # get the date from the amount of seconds
    date = datetime.fromtimestamp(seconds)
    # convert the date in string with the good format
    date = datetime.strftime(date, "%d-%m-%Y %H:%M:%S")
    return date


def swap_date(date):
    # in weights file dates are in format DD MM YYYY instead of YYYY MM DD
    split_date = date.split(" ")
    dmy = split_date[0]
    split_dmy = dmy.split("-")
    ydm = split_dmy[2] + "-" + split_dmy[1] + "-" + split_dmy[0]
    return ydm + " " + split_date[1]

def get_weights(client, csv_file_in, csv_file_out):
    """Parse a csv containing weights info, and return a new csv adapted to phis' data format

            :param client: current client in phis
            :type client: TokenGetDTO
            :param csv_file_in: csv containing the original weights info
            :type csv_file_in: str
            :param csv_file_out: csv containing the data info for phis
            :type csv_file_out: str
            :return: List of csv files containing the data information for phis
            :rtype: list[str]
    """
    global file_list
    file_list = []
    activity_object = activity.create_activity(rdf_type="vocabulary:Measure")
    agent_uri = agent.find_agent(client, "RapidoScan light curtain")
    today = datetime.today()
    today = datetime.strftime(today,"%Y-%m-%d")
    provenance_uri = provenance.create_provenance(client, name="Weights_Provenance_Heliaphen", date=today, prov_agent=[agent_uri], prov_activity=[activity_object])
    variables = ""
    out_file=""
    date_avant_index=""
    date_après_index = ""
    with open(csv_file_in, "r", newline='', encoding="windows-1252") as file:
        reader = csv.reader(file, delimiter='\t')
        line_count = 0
        variables_uris = {}
        start_time = time.time()
        for row in reader:
            current_time = time.time()
            # refresh connection if needed
            if current_time - start_time > 180:
                print("renewing token")
                connection.refresh_connection(client)
                start_time = current_time
            if line_count == 0:
                out_file = csv_phis.create_csv_file(csv_file_out,"weights_data")
                variables = row
                # index de la case de la date d'avant arrosage
                date_avant_index = row.index("Poids avant arrosage date")
                # index de la case de la date d'après arrosage
                date_après_index = row.index("Poids après arrosage date")
            else:
                experiment_name = row[0][0:6]
                try:
                    experiment_uri = experiment.find_experiment_by_name(client, experiment_name)
                except IndexError:
                    line_count += 1
                    continue
                # should use range(len(row)) instead but sometimes len(row) = 92 in some files --> bug
                for var in range(0,91):
                    variable_name = variables[var]
                    value = row[var]
                    keep_variable = re.match("(Poids avant arrosage mesure)|(Poids après arrosage mesure)|(Diametre)",
                                             variable_name)
                    if not keep_variable:
                        continue
                    if keep_variable.group(1) is not None:
                        # poids avant arrosage
                        date = row[date_avant_index]
                        if variable_name not in variables_uris:
                            variables_uris[variable_name] = variable.find_variable(pythonClient=client, name="Pot_Accessories_dry_weight")
                    elif keep_variable.group(2) is not None:
                        # poids apres arrosage
                        date = row[date_après_index]
                        date = add_1s(date)
                        if variable_name not in variables_uris:
                            variables_uris[variable_name] = variable.find_variable(pythonClient=client, name="Pot_fresh_weight")
                    else:
                        # diametre
                        date = row[date_avant_index]
                        if variable_name not in variables_uris:
                            variables_uris[variable_name] = variable.find_variable(pythonClient=client, name="HP_Pot_Diameter")

                    scientific_object_name = row[0].upper()
                    scientific_object_uris = scientific_object.find_scientific_object(client, scientific_object_name,
                                                                                   experiment_uri, 'vocabulary:Pot')
                    for scientific_object_uri in scientific_object_uris:
                        csv_phis.add_data_csv(out_file, "", swap_date(date), "", experiment_uri, scientific_object_uri, variables_uris[variable_name], value,
                                              provenance_uri, "", "", "")
            line_count += 1
    return file_list
