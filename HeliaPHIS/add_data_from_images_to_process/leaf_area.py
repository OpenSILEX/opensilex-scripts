import csv
import datetime
import os
import re
import time
import numpy as np
import csv_phis
from phis_functions import experiment, scientific_object, data
# fichier_model = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/Data/leaf_area/reprex/model_area/model_area_global.rds"


file_list = []
model = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/models/18HP010_RobustLinearModel.txt"


def get_info_from_phis(pythonClient, plant, experiment_name, start_date, end_date):
    # list of data in phis for this plant collected on this date (between start date and end date)
    experiment_uri = experiment.find_experiment_by_name(pythonClient, experiment_name)
    plant_uri = scientific_object.find_scientific_object(pythonClient, plant, experiment_uri, "vocabulary:Plant")[0]
    data_list = data.collect_info_of_plant(pythonClient, plant, experiment_uri, start_date, end_date)
    if not data_list:
        return None
    else:
        path = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/Data/leaf_area/fichiers_features/{}".format(
            experiment_name)
        if not os.path.exists(path):
            os.makedirs(path)
        file = os.path.join(path, plant + "_" + datetime.date.strftime(start_date, "%Y-%m-%d") + '.csv')
        with open(file, "w", newline='', encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            # list of the variables we need to calculate the leaf area
            variables = ["experiment", "plant", "date", "provenance", "image", 'centroid_x', 'centroid_y', 'perimeter',
                         'hull_area', 'shape_solidity', 'shape_extend', 'straight_bounding_rectangle_left',
                         'straight_bounding_rectangle_width', 'straight_bounding_rectangle_top',
                         'straight_bounding_rectangle_height', 'rotated_bounding_rectangle_cx',
                         'rotated_bounding_rectangle_cy', 'rotated_bounding_rectangle_width',
                         'rotated_bounding_rectangle_height', 'rotated_bounding_rectangle_rotation',
                         'minimum_enclosing_circle_cx', 'minimum_enclosing_circle_cy',
                         'minimum_enclosing_circle_radius', 'shape_height', 'shape_width', 'shape_width_min',
                         'shape_width_max', 'shape_width_avg', 'shape_width_std', 'quantile_width_1_4_area',
                         'quantile_width_1_4_hull', 'quantile_width_1_4_solidity', 'quantile_width_1_4_min_width',
                         'quantile_width_1_4_max_width', 'quantile_width_1_4_avg_width', 'quantile_width_1_4_std_width',
                         'quantile_width_2_4_area', 'quantile_width_2_4_hull', 'quantile_width_2_4_solidity',
                         'quantile_width_2_4_min_width', 'quantile_width_2_4_max_width', 'quantile_width_2_4_avg_width',
                         'quantile_width_2_4_std_width', 'quantile_width_3_4_area', 'quantile_width_3_4_hull',
                         'quantile_width_3_4_solidity', 'quantile_width_3_4_min_width', 'quantile_width_3_4_max_width',
                         'quantile_width_3_4_avg_width', 'quantile_width_3_4_std_width', 'quantile_width_4_4_area',
                         'quantile_width_4_4_hull', 'quantile_width_4_4_solidity', 'quantile_width_4_4_min_width',
                         'quantile_width_4_4_max_width', 'quantile_width_4_4_avg_width', 'quantile_width_4_4_std_width']

            writer.writerow(variables)
            # list of the values of these variables in Phis (same size than the list of variables)
            values = [""] * len(variables)
            # add the values in the correct variable column
            values[0] = experiment_name
            values[1] = plant
            for data_object in data_list:
                matches = []
                data_name = data_object.variable
                provenance_uri = data_object.provenance.uri
                image = data_object.provenance.prov_used[0].uri
                values[3] = provenance_uri
                values[2] = data_object._date
                values[4] = image
                for variable in variables[5:]:
                    match = re.search(variable.lower(), data_name)
                    if match:
                        matches.append(variable)
                if matches:
                    closest_match = ""
                    for m in matches:
                        if len(m) > len(closest_match):
                            closest_match = m
                    values[variables.index(closest_match)] = data_object.value

            writer.writerow(values)
        return file


# def calculate_leaf_area(fichier_features, fichier_model, fichier_sortie):
#     command = ["Rscript", "reprex_model_area.r", fichier_features, fichier_model, fichier_sortie]
#     subprocess.run(command)


def calculate_leaf_area(pythonClient, fichier_features, sortie):
    global model
    area_out = csv_phis.create_csv_file(sortie, "leaf_area_data")
    with open(model, "r") as model_file:
        with open(fichier_features) as features_file:
            rmodel = csv.reader(model_file, delimiter=",")
            rfeatures = csv.reader(features_file, delimiter=",")
            constant = float(next(rmodel)[1])
            variables = next(rfeatures)[5:]
            vector_model = []
            experiment_uri = plant_uri = date = provenance_uri = image_uri = ""
            for m_row in rmodel:
                vector_model.append(m_row[1])

            f_row = next(rfeatures)
            experiment_uri = experiment.find_experiment_by_name(pythonClient, f_row[0])
            plant_uri = scientific_object.find_scientific_object(pythonClient, f_row[1], experiment_uri, "vocabulary:Plant")[0]
            date = f_row[2]
            provenance_uri = f_row[3]
            image_uri = f_row[4]
            vector_model = np.asarray(vector_model, dtype='float64')
            vector_features = np.asarray(f_row[5:], dtype='float64')

            scalar_product= sum([x * y for x, y in zip(vector_model, vector_features)])
            leaf_area = (constant + scalar_product) / 2

            csv_phis.add_data_csv(area_out, uri="", date=date, timezone="Europe/Paris", experiment=experiment_uri, scientific_object=plant_uri, variable="field:set/variables#variable.hp_leaf_area", value=leaf_area, provenance=provenance_uri, image=image_uri, metadata="", raw_data="")


def calculate_all_areas_from_experiment(pythonClient, experiment_uri, start_date=None):
    plants = scientific_object.get_all_objects_of_experiment(pythonClient, experiment_uri, ["vocabulary:Plant"])
    dates_explored = []
    experiment_name = experiment.get_experiment_name(pythonClient, experiment_uri)
    if start_date is None:
        # case where there is no specific date where we want to calculate the leaf area, so we calculate the leaf areas
        # of all the plants at all the dates between the start date of the experiment and the end date
        start_date = experiment.get_experiment_period(pythonClient, experiment_uri)[0]
        end_date = experiment.get_experiment_period(pythonClient, experiment_uri)[1]
    else:
        # case where a date was specified for when the leaf area should be calculated
        # convert the datetime.datetime to a datetime.date
        start_date = datetime.datetime.date(start_date)
        end_date = start_date
    current_date = start_date
    global fichier_model
    while current_date <= end_date:
        print(current_date)
        # add 1 day to the current date to find the next date
        timestamp = current_date.timetuple()
        timestamp = time.mktime(timestamp)
        next_date = datetime.date.fromtimestamp(timestamp + 86400)
        for plant in plants:
            fichier_features = get_info_from_phis(pythonClient, plant.name, experiment_name, current_date, next_date)
            if fichier_features is None:
                continue
            else:
                path = "/mnt/GRP_ASTR/GRP_ASTR/Priv/ASTR/RESSOURCES_INFO/PYTHON/HeliaPHIS/Data/leaf_area/sorties/{}".format(
                    experiment_name)
                if not os.path.exists(path):
                    os.makedirs(path)
                sortie_name = plant.name + "_" + datetime.date.strftime(current_date, "%y-%m-%d")
                sortie = os.path.join(path, sortie_name + '.csv')
                calculate_leaf_area(pythonClient, fichier_features, sortie)
                data.send_data_to_phis(pythonClient, sortie)
        current_date = next_date
