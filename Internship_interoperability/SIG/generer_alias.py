# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# generer_alias.py
# Created on: 2022-08-19 08:26:39.00000
#   (generated by ArcGIS/ModelBuilder)
# Usage: generer_alias <Couche_en_entrée> <Saisir_n°_de_la_campagne> <Saisir_code_de_la_parcelle> <Sélectionner_le_champ_contenant_les_n°_d_essai> <Sélectionner_le_champ_contenant_les_n°_de_planche> <Sélectionner_le_champ_contenant_les_n°_de_ligne> 
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy

# Load required toolboxes
arcpy.ImportToolbox("Modéliser les fonctions")

# Script arguments
Couche_en_entrée = arcpy.GetParameterAsText(0)

Saisir_n°_de_la_campagne = arcpy.GetParameterAsText(1)

Saisir_code_de_la_parcelle = arcpy.GetParameterAsText(2)

Sélectionner_le_champ_contenant_les_n°_d_essai = arcpy.GetParameterAsText(3)

Sélectionner_le_champ_contenant_les_n°_de_planche = arcpy.GetParameterAsText(4)

Sélectionner_le_champ_contenant_les_n°_de_ligne = arcpy.GetParameterAsText(5)

# Local variables:
avec_alias_vide = Couche_en_entrée
planche = Couche_en_entrée
ligne = Couche_en_entrée
essai = Couche_en_entrée
Classe_d’entités_en_sortie = avec_alias_vide

# Process: Ajouter un champ
arcpy.AddField_management(Couche_en_entrée, "alias", "TEXT", "", "", "", "", "NULLABLE", "NON_REQUIRED", "")

# Process: Calculer un champ
arcpy.CalculateField_management(avec_alias_vide, "alias", "\"%Saisir n° de la campagne%\"&\"%Saisir code de la parcelle%\"&[%Sélectionner le champ contenant les n° d'essai%]&\"_\"&\"Y\"&format_P&\"X\"&format_L", "VB", "format_P = Right (\"00\"&[%Sélectionner le champ contenant les n° de planche%], 2)
format_L = Right (\"000\"&[%Sélectionner le champ contenant les n° de ligne%], 3)")

# Process: Obtenir une valeur de champ
arcpy.GetFieldValue_mb(Couche_en_entrée, Sélectionner_le_champ_contenant_les_n°_de_planche, "Chaîne", "0")

# Process: Obtenir une valeur de champ (2)
arcpy.GetFieldValue_mb(Couche_en_entrée, Sélectionner_le_champ_contenant_les_n°_de_ligne, "Chaîne", "0")

# Process: Obtenir une valeur de champ (3)
arcpy.GetFieldValue_mb(Couche_en_entrée, Sélectionner_le_champ_contenant_les_n°_d_essai, "Chaîne", "0")
