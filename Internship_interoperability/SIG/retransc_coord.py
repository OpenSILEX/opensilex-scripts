import arcpy
import os

# chemin du vecteur directeur (choix de l'utilisateur)
fc = arcpy.GetParameterAsText(0)
# chemin du quadrillage en sortie (choix de l'utilisateur)
filepath = arcpy.GetParameterAsText(1)

fields = ['SHAPE@WKT']

# Pour récupérer les coordonnées des deux sommets du vecteur dans une liste
def wkt(fc,fields):
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        for row in cursor:
            t=row[0].replace('MULTILINESTRING ','').replace('(','').replace(')','').split(', ')
    return(t)


# On récupère les coordonnées de l'origine du vecteur
originCoordinate = wkt(fc,fields)[0]

# On récupère les coordonnées de l'autre sommet du vecteur
yAxisCoordinate = wkt(fc,fields)[1]

# Largeur et hauteur des cellules du quadrillage (choix de l'utilisateur)
cellSizeWidth = arcpy.GetParameterAsText(2)
cellSizeHeight = arcpy.GetParameterAsText(3)

# Nombre de colonnes et de lignes (choix de l'utilisateur)
numRows =  arcpy.GetParameterAsText(4)
numColumns = arcpy.GetParameterAsText(5)

# Méthode de création du quadrillage issue de ArcPy
arcpy.CreateFishnet_management(filepath, originCoordinate, yAxisCoordinate, cellSizeWidth, cellSizeHeight, numRows, numColumns, labels=False)

