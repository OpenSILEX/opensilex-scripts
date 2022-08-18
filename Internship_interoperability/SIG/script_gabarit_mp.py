import arcpy
import sys
import os
import numpy as np
import pandas as pd

# obtenir le chemin de la couche en entrée
fc = arcpy.GetParameterAsText(0)

# champ avec l'alias
alias = arcpy.GetParameterAsText(1)

# champ essai
essai = arcpy.GetParameterAsText(2)

# champ avec le bloc
bloc = arcpy.GetParameterAsText(3)

# champ avec l'uri de l'uc
uri_uc = arcpy.GetParameterAsText(4)

# champ avec l'uri du germplasm
uri_var = arcpy.GetParameterAsText(5)

# champ facultatif 1 (autre uri de germplasm ou uri de modalité de facteur)
facult1 = arcpy.GetParameterAsText(6)

# champ facultatif 2 (autre uri de germplasm ou uri de modalité de facteur)
facult2 = arcpy.GetParameterAsText(7)

# champ facultatif 3 (autre uri de germplasm ou uri de modalité de facteur)
facult3 = arcpy.GetParameterAsText(8)

# champ facultatif 4 (autre uri de germplasm ou uri de modalité de facteur)
facult4 = arcpy.GetParameterAsText(9)
   
# obtenir la liste de valeur unique dans le champ 'essai'
ess=[]
with arcpy.da.SearchCursor(fc, essai) as cursor:
    for row_ini in cursor:
        row = [i.encode('utf-8') if isinstance(i, (str,unicode)) else i for i in row_ini]
        ess.append(str(row[0]))
liste_essai = np.unique(ess)

# champs utiles (la géométrie au format WKT dans le champ "caché" SHAPE@WKT)
fields = [alias,'SHAPE@WKT',essai,bloc,uri_uc,uri_var,facult1,facult2,facult3,facult4]

# fonction permettant de générer le texte t du gabarit
def wkt(fc,fields,num_essai):
    # on crée une nouvelle liste de champ mais sans les champs laissés vides '' (champs facultatifs)
    new_fields = [i for i in fields]
    nb_vide=fields.count('')
    if nb_vide >0 : 
        for i in range (nb_vide): 
            new_fields.remove('')

    # La façon de générer le texte du gabarit t est différente en fonction des champs facultatifs présents
    if nb_vide ==4: # pas de champ facultatif renseigné
        # On crée les 2 premières lignes du gabarit (en-têtes du gabarit obligatoires) 
        t='URI;type;name;vocabulary:hasCreationDate;vocabulary:hasDestructionDate;vocabulary:isHosted;vocabulary:isPartOf;rdfs:comment;geometry;vocabulary:hasReplication;vocabulary:hasGermplasm\n\"URI de l\'objet scientifique (auto-générée si vide)\nObligatoire: oui\";\"URI du type d\'objet scientifique\nObligatoire: oui\";\"Nom de l\'objet scientifique\nObligatoire: oui\";\"Date de création (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Date de destruction (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Installation technique initiale\nType de donnée: URI\nObligatoire: non\";\"URI ou nom du parent\nObligatoire: non\";\"Description\nType de donnée: Texte court\nObligatoire: non\";\"Coordonnées géospatiales (Format WKT)\nObligatoire: non\";\"réplication\nType de donnée: Texte court\nObligatoire: non\";\"Matériel génétique\nType de donnée: URI\nObligatoire: non\nCette colonne peut être présente plusieurs fois pour définir plusieurs valeurs\"\n'
        
        uc=[]
        # on itère sur chaque ligne dans la table attributaire de fc pour récupérer les infos de certains champs (ceux listés dans new_fields) pour les inclure dans une nouvelle ligne de t pour un num_essai donné
        with arcpy.da.SearchCursor(fc, new_fields) as cursor:
            for row_ini in cursor:
                row = [i.encode('utf-8') if isinstance(i, (str,unicode)) else i for i in row_ini]
                if str(row[2])==num_essai: #str pour que ça marche avec des données de n'importe quel type dans le champ 'essai'
                    t+=';vocabulary:Plot ;{0};;;;{3};;{1};{2};{4}\n'.format(row[0], row[1],row[3],row[4],row[5])
                    uc.append(row[4])   # on récupère dans une liste les uri_uc de chaque parcelle de l'essai

        liste_uri_uc = np.unique(uc) # on récupère les uri_uc des uc de l'essai
        # on ajoute à la fin du gabarit les infos pour déclarer les OS uc des uc de l'essai
        for i in liste_uri_uc:
            nom_uc=i[34:] # on garde seulement le nom de l'uc à partir de son uri (à partir du 34ième caractère de l'uri)
            t+='{0};vocabulary:ManagementUnit ;{1};;;;;;;;\n'.format(i, nom_uc)

    if nb_vide ==3: # 1 champ facultatif renseigné
        # On crée les 2 premières lignes du gabarit (en-têtes du gabarit obligatoires) 
        t='URI;type;name;vocabulary:hasCreationDate;vocabulary:hasDestructionDate;vocabulary:isHosted;vocabulary:isPartOf;rdfs:comment;geometry;vocabulary:hasReplication;vocabulary:hasGermplasm;\n\"URI de l\'objet scientifique (auto-générée si vide)\nObligatoire: oui\";\"URI du type d\'objet scientifique\nObligatoire: oui\";\"Nom de l\'objet scientifique\nObligatoire: oui\";\"Date de création (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Date de destruction (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Installation technique initiale\nType de donnée: URI\nObligatoire: non\";\"URI ou nom du parent\nObligatoire: non\";\"Description\nType de donnée: Texte court\nObligatoire: non\";\"Coordonnées géospatiales (Format WKT)\nObligatoire: non\";\"réplication\nType de donnée: Texte court\nObligatoire: non\";\"Matériel génétique\nType de donnée: URI\nObligatoire: non\nCette colonne peut être présente plusieurs fois pour définir plusieurs valeurs\";\n'
        
        uc=[]
        # on itère sur chaque ligne dans la table attributaire de fc pour récupérer les infos de certains champs (ceux listés dans new_fields) pour les inclure dans une nouvelle ligne de t pour un num_essai donné
        with arcpy.da.SearchCursor(fc, new_fields) as cursor:
            for row_ini in cursor:
                row = [i.encode('utf-8') if isinstance(i, (str,unicode)) else i for i in row_ini]
                if str(row[2])==num_essai: #str pour que ça marche avec des données de n'importe quel type dans le champ 'essai'
                    t+=';vocabulary:Plot ;{0};;;;{3};;{1};{2};{4};{5}\n'.format(row[0], row[1],row[3],row[4],row[5],row[6])
                    uc.append(row[4])   # on récupère dans une liste les uri_uc de chaque parcelle de l'essai

        liste_uri_uc = np.unique(uc) # on récupère les uri_uc des uc de l'essai
        # on ajoute à la fin du gabarit les infos pour déclarer les OS uc des uc de l'essai
        for i in liste_uri_uc:
            nom_uc=i[34:] # on garde seulement le nom de l'uc à partir de son uri (à partir du 34ième caractère de l'uri)
            t+='{0};vocabulary:ManagementUnit ;{1};;;;;;;;;\n'.format(i, nom_uc)

    if nb_vide ==2: # 2 champs facultatifs renseignés
        # On crée les 2 premières lignes du gabarit (en-têtes du gabarit obligatoires) 
        t='URI;type;name;vocabulary:hasCreationDate;vocabulary:hasDestructionDate;vocabulary:isHosted;vocabulary:isPartOf;rdfs:comment;geometry;vocabulary:hasReplication;vocabulary:hasGermplasm;;\n\"URI de l\'objet scientifique (auto-générée si vide)\nObligatoire: oui\";\"URI du type d\'objet scientifique\nObligatoire: oui\";\"Nom de l\'objet scientifique\nObligatoire: oui\";\"Date de création (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Date de destruction (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Installation technique initiale\nType de donnée: URI\nObligatoire: non\";\"URI ou nom du parent\nObligatoire: non\";\"Description\nType de donnée: Texte court\nObligatoire: non\";\"Coordonnées géospatiales (Format WKT)\nObligatoire: non\";\"réplication\nType de donnée: Texte court\nObligatoire: non\";\"Matériel génétique\nType de donnée: URI\nObligatoire: non\nCette colonne peut être présente plusieurs fois pour définir plusieurs valeurs\";;\n'
        
        uc=[]
        # on itère sur chaque ligne dans la table attributaire de fc pour récupérer les infos de certains champs (ceux listés dans new_fields) pour les inclure dans une nouvelle ligne de t pour un num_essai donné
        with arcpy.da.SearchCursor(fc, new_fields) as cursor:
            for row_ini in cursor:
                row = [i.encode('utf-8') if isinstance(i, (str,unicode)) else i for i in row_ini]
                if str(row[2])==num_essai: #str pour que ça marche avec des données de n'importe quel type dans le champ 'essai'
                    t+=';vocabulary:Plot ;{0};;;;{3};;{1};{2};{4};{5};{6}\n'.format(row[0], row[1],row[3],row[4],row[5],row[6],row[7])
                    uc.append(row[4])   # on récupère dans une liste les uri_uc de chaque parcelle de l'essai

        liste_uri_uc = np.unique(uc) # on récupère les uri_uc des uc de l'essai
        # on ajoute à la fin du gabarit les infos pour déclarer les OS uc des uc de l'essai
        for i in liste_uri_uc:
            nom_uc=i[34:] # on garde seulement le nom de l'uc à partir de son uri (à partir du 34ième caractère de l'uri)
            t+='{0};vocabulary:ManagementUnit ;{1};;;;;;;;;;\n'.format(i, nom_uc)

    if nb_vide ==1: # 3 champs facultatifs renseignés
        # On crée les 2 premières lignes du gabarit (en-têtes du gabarit obligatoires) 
        t='URI;type;name;vocabulary:hasCreationDate;vocabulary:hasDestructionDate;vocabulary:isHosted;vocabulary:isPartOf;rdfs:comment;geometry;vocabulary:hasReplication;vocabulary:hasGermplasm;;;\n\"URI de l\'objet scientifique (auto-générée si vide)\nObligatoire: oui\";\"URI du type d\'objet scientifique\nObligatoire: oui\";\"Nom de l\'objet scientifique\nObligatoire: oui\";\"Date de création (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Date de destruction (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Installation technique initiale\nType de donnée: URI\nObligatoire: non\";\"URI ou nom du parent\nObligatoire: non\";\"Description\nType de donnée: Texte court\nObligatoire: non\";\"Coordonnées géospatiales (Format WKT)\nObligatoire: non\";\"réplication\nType de donnée: Texte court\nObligatoire: non\";\"Matériel génétique\nType de donnée: URI\nObligatoire: non\nCette colonne peut être présente plusieurs fois pour définir plusieurs valeurs\";;;\n'
        
        uc=[]
        # on itère sur chaque ligne dans la table attributaire de fc pour récupérer les infos de certains champs (ceux listés dans new_fields) pour les inclure dans une nouvelle ligne de t pour un num_essai donné
        with arcpy.da.SearchCursor(fc, new_fields) as cursor:
            for row_ini in cursor:
                row = [i.encode('utf-8') if isinstance(i, (str,unicode)) else i for i in row_ini]
                if str(row[2])==num_essai: #str pour que ça marche avec des données de n'importe quel type dans le champ 'essai'
                    t+=';vocabulary:Plot ;{0};;;;{3};;{1};{2};{4};{5};{6};{7}\n'.format(row[0], row[1],row[3],row[4],row[5],row[6],row[7],row[8])
                    uc.append(row[4])   # on récupère dans une liste les uri_uc de chaque parcelle de l'essai

        liste_uri_uc = np.unique(uc) # on récupère les uri_uc des uc de l'essai
        # on ajoute à la fin du gabarit les infos pour déclarer les OS uc des uc de l'essai
        for i in liste_uri_uc:
            nom_uc=i[34:] # on garde seulement le nom de l'uc à partir de son uri (à partir du 34ième caractère de l'uri)
            t+='{0};vocabulary:ManagementUnit ;{1};;;;;;;;;;;\n'.format(i, nom_uc)

    if nb_vide ==0: # 4 champs facultatifs renseignés
        # On crée les 2 premières lignes du gabarit (en-têtes du gabarit obligatoires) 
        t='URI;type;name;vocabulary:hasCreationDate;vocabulary:hasDestructionDate;vocabulary:isHosted;vocabulary:isPartOf;rdfs:comment;geometry;vocabulary:hasReplication;vocabulary:hasGermplasm;;;;\n\"URI de l\'objet scientifique (auto-générée si vide)\nObligatoire: oui\";\"URI du type d\'objet scientifique\nObligatoire: oui\";\"Nom de l\'objet scientifique\nObligatoire: oui\";\"Date de création (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Date de destruction (format: AAAA-MM-JJ)\nType de donnée: Date\nObligatoire: non\";\"Installation technique initiale\nType de donnée: URI\nObligatoire: non\";\"URI ou nom du parent\nObligatoire: non\";\"Description\nType de donnée: Texte court\nObligatoire: non\";\"Coordonnées géospatiales (Format WKT)\nObligatoire: non\";\"réplication\nType de donnée: Texte court\nObligatoire: non\";\"Matériel génétique\nType de donnée: URI\nObligatoire: non\nCette colonne peut être présente plusieurs fois pour définir plusieurs valeurs\";;;;\n'
        
        uc=[]
        # on itère sur chaque ligne dans la table attributaire de fc pour récupérer les infos de certains champs (ceux listés dans new_fields) pour les inclure dans une nouvelle ligne de t pour un num_essai donné
        with arcpy.da.SearchCursor(fc, new_fields) as cursor:
            for row_ini in cursor:
                row = [i.encode('utf-8') if isinstance(i, (str,unicode)) else i for i in row_ini]
                if str(row[2])==num_essai: #str pour que ça marche avec des données de n'importe quel type dans le champ 'essai'
                    t+=';vocabulary:Plot ;{0};;;;{3};;{1};{2};{4};{5};{6};{7};{8}\n'.format(row[0], row[1],row[3],row[4],row[5],row[6],row[7],row[8],row[9])
                    uc.append(row[4])   # on récupère dans une liste les uri_uc de chaque parcelle de l'essai

        liste_uri_uc = np.unique(uc) # on récupère les uri_uc des uc de l'essai
        # on ajoute à la fin du gabarit les infos pour déclarer les OS uc des uc de l'essai
        for i in liste_uri_uc:
            nom_uc=i[34:] # on garde seulement le nom de l'uc à partir de son uri (à partir du 34ième caractère de l'uri)
            t+='{0};vocabulary:ManagementUnit ;{1};;;;;;;;;;;;\n'.format(i, nom_uc)

    return(t)


# Création et écriture des gabarits csv pour chaque essai
for k in liste_essai :
    # Construire le chemin et le nom du csv en fonction de l'emplacement sélectionné par l'utilisateur et du nom/num de l'essai (avec u"" pour mettre en unicode pour que ça marche avec accents dans le chemin)
    filepath =u"{0}\{1}_{2}.csv".format(os.path.dirname(arcpy.GetParameterAsText(10)),os.path.splitext(os.path.basename(arcpy.GetParameterAsText(10)))[0],k)
    
    # on remplis le csv avec la fonction wkt()
    f = open(filepath,"w") 
    f.write(wkt(fc,fields,k))
    f.close()

    # on modifie le csv pour avoir la géométrie avec un format en POLYGON plutôt qu'en MULTIPOLYGON (pour PhenoIHM)
    f = open(filepath,"r")
    l=f.readlines()
    nouv =''
    for i in l:
        nouv+=i.replace('MULTI','').replace('(((','((').replace(')))','))')
    f.close()

    n = open(filepath,"w")
    n.write(nouv)
    n.close()

    # Pour supprimer les colonnes vides du csv s'il y en a
    df=pd.read_csv(filepath, sep=";")
    dfr=df.replace(r'^\s*$',np.nan,regex=True)
    cols_vides=[col for col in dfr.columns if dfr[col].isnull().all()]
    dfr.drop(cols_vides, axis=1,inplace=True)
    dfr.to_csv(filepath, sep=";",index=False)

    # Pour inverser l'orientation des points pour construire la geométrie des polygones (sens anti-horaire vers sens horaire) car PhenoIHM n'accepte que la géométrie en sens horaire
    dfc=pd.read_csv(filepath, sep=";")
    for i in range (1,len(dfc['geometry'])) :
        if isinstance(dfc['geometry'][i],str):
            dfc['geometry'][i]= dfc['geometry'][i].replace('POLYGON ((','').replace('))','').split(',')
            dfc['geometry'][i][1], dfc['geometry'][i][3] = dfc['geometry'][i][3], dfc['geometry'][i][1]
            dfc['geometry'][i]= 'POLYGON (({0}))'.format(','.join(dfc['geometry'][i]))

    dfc.to_csv(filepath, sep=";",index=False)
