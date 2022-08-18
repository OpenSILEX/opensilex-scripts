import arcpy
import sys
import os
import numpy as np


# obtenir le chemin de la couche en entrée
fc = arcpy.GetParameterAsText(0)

# obtenir le nom du champ comportant le nom des uc
uc = arcpy.GetParameterAsText(1)

# champs utiles (la géométrie au format WKT dans le champ "caché" SHAPE@WKT)
fields = [uc,'SHAPE@WKT']

# fonction permettant de générer le texte t du gabarit
def wkt(fc,fields):
    # On crée les 2 premières lignes du gabarit (en-têtes du gabarit obligatoires) 
    t='URI;type;name;vocabulary:hasCreationDate;vocabulary:hasDestructionDate;vocabulary:isHosted;vocabulary:isPartOf;rdfs:comment;geometry;vocabulary:hasReplication;vocabulary:hasFactorLevel;vocabulary:hasGermplasm\n\"URI de l\'objet scientifique (auto-générée si vide)\nObligatoire: oui\";\"URI du type d\'objet scientifique\nObligatoire: oui\";\"Nom de l\'objet scientifique\nObligatoire: oui\";\"Date de création (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Date de destruction (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Installation technique initiale\nType de donnée: URI\nObligatoire: non\";\"URI ou nom du parent\nObligatoire: non\";\"Description\nType de donnée: Texte court\nObligatoire: non\";\"Coordonnées géospatiales (Format WKT)\nObligatoire: non\";\"réplication\nType de donnée: Texte court\nObligatoire: non\";\"Modalité de facteur\nType de donnée: URI\nObligatoire: non\nCette colonne peut être présente plusieurs fois pour définir plusieurs valeurs\";\"Matériel génétique\nType de donnée: URI\nObligatoire: non\nCette colonne peut être présente plusieurs fois pour définir plusieurs valeurs\"\n'

    # on itère sur chaque ligne dans la table attributaire de fc pour récupérer les infos de certains champs (ceux listés dans fields) pour les inclure dans une nouvelle ligne de t
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row_ini in cursor:
            row = [i.encode('utf-8') if isinstance(i, (str,unicode)) else i for i in row_ini]
            t+=';vocabulary:ManagementUnit ;{0};;;;;;{1};;;\n'.format(row[0], row[1])
    return(t)

# Création et écriture du gabarit
# Construire le csv en fonction de l'emplacement sélectionné par l'utilisateur (avec u"" pour mettre en unicode pour que ça marche avec accents dans le chemin)
filepath =u"{0}\{1}.csv".format(os.path.dirname(arcpy.GetParameterAsText(2)),os.path.splitext(os.path.basename(arcpy.GetParameterAsText(2)))[0])      

f = open(filepath,"w") 
f.write(wkt(fc,fields))
f.close()
