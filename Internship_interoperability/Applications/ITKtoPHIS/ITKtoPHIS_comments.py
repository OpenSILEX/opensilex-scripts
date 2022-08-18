import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog
from PyQt5.uic import loadUi
from PyQt5.QtCore import QSettings


import json
import pandas as pd
import requests, urllib
import opensilexClientToolsPython as opensilexWSClient
import zipfile
from datetime import datetime, timezone


# définir le repertoire de travail par défaut dans le dossier dans lequel est le script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Interface principale de l'application
class MainWindow(QDialog):
    def __init__(self) :
        super(MainWindow,self).__init__()
        loadUi("interf.ui",self)
        self.browse_in.clicked.connect(self.browsefiles_in)
        self.config_client.clicked.connect(self.config_client_phis)
        
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        
        self.push.clicked.connect(self.exec_script)

    # fonction qui permet d'ouvrir l'interface qui permet de configurer le client de PHIS
    def config_client_phis(self):
        client_phis=Client_PHIS()
        widget.addWidget(client_phis)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(485)
        widget.setFixedHeight(200)

    # fonction qui permet de sélectionner le chemin du fichier en entrée via l'explorateur
    def browsefiles_in(self):
        fname=QFileDialog.getOpenFileName(self,'Ouvrir le fichier')
        self.filename.setText(fname[0])

    # fonction qui permet d'exéuter le script "utile" de l'application
    def exec_script(self):

        try :
            # lire le contenu des fichiers 'Action' et 'Field' du fichier zip en entrée
            filepath = self.filename.text()
            zip = zipfile.ZipFile(filepath)
            
            actions_str = str(zip.read('Action.Json'),encoding='utf-8-sig')
            field_str = str(zip.read('Field.Json'),encoding='utf-8-sig')

            # convertir en dictionnaire le contenu des deux fichiers
            actions_json = json.loads(actions_str)
            field_json = json.loads(field_str)

            # récup infos des parcelles (fields) et des interventions (activities) dans des listes de dicos
            fields = field_json['Fields']
            activities = actions_json['Activities']

            # première valeur d'avancement (pour montrer que le script s'est bien lancé)
            self.progressBar.setValue(50)

            # lines_f est un liste de dictionnaire comportant l'info de l'identifiant de la parcelle (Id_parcelle) et son nom (Nom_parcelle) de toutes les parcelles contenues dans Field
            lines_f = []
            for field in fields:
                line = dict()
                line['Id_parcelle'] = field['Id']
                line['Nom_parcelle'] = field['Name']
                lines_f.append(line)


            # Fonction qui permet de récupérer la correspondance entre les types d'interventions de Geofolia et les types d'évènements de PHIS
            def getTypeUri(typeName):
                typeURI = {
                    'Travail du sol' : 'oeev:Tillage',
                    'Semis/Plantation' : 'oeev:Sowing',
                    'Traitement' : 'oeev:Treatment',
                    'Fertilisation' : 'oeev:Fertilization',
                    'Récolte' : 'oeev:Harvesting',
                    'Autre' : 'oeev:ScientificObjectManagement'
                }

                return typeURI[typeName]

            # Fonction qui permet de récupérer le nom d'une parcelle en connaissant son identifiant
            def getNameParcelle(Id,lines_f) :
                ret=None
                for l in lines_f:
                    if l['Id_parcelle'] == Id :
                        ret = l['Nom_parcelle']
                        break
                return(ret)

            # Fonction qui permet à partir de la liste des produits utilisé pour une intervention sur une parcelle donné (rid) de récupérer une liste de listes contenant : [Nom du produit, la quantité,l'unité] pour les interventions nécessitant des produits
            def getProdQteUnit_RId (liste_produit, rid) : 
                liste_p_act=[None]
                if liste_produit :
                    liste_p_act=[]
                    for l in liste_produit :
                        if l["RecognitionId"] == rid :
                            ret = [l["SupplyName"],l["Quantity"],l["ReferentialUnitSymbol"]]
                            liste_p_act.append(ret)
                return(liste_p_act)

            # on récupère les informations pour configurer le client de PHIS
            host = Client_PHIS().get_host_value()
            user = Client_PHIS().get_id_value()
            password = Client_PHIS().get_mdp_value()

            # configuration du client
            pythonClient = opensilexWSClient.ApiClient()

            # fonction qui permet de chercher un OS dans Phis à partir d'un nom (renvoie des informations des OS trouvés dont l'URI)
            def getOS_uri(name,pythonClient):
                pythonClient.connect_to_opensilex_ws(identifier=user, password=password, host=host)
                auth_api = opensilexWSClient.AuthenticationApi(pythonClient)
                body = opensilexWSClient.AuthenticationDTO(identifier=user, password=password)
                token = auth_api.authenticate(body=body)['result'].token


                headers = {
                    'Content-Type': 'application/json',
                    'accept' : 'application/json',
                    'Authorization':'Bearer '+token
                }
                url =   host+"/core/scientific_objects?"+\
                        "name="+urllib.parse.quote_plus(str(name))+\
                        "&order_by=uri%3Dasc&page=0&page_size=1000"

                response = requests.get(url, headers=headers)
                r = response.json()
                ret = []
                
                for os in r["result"]:
                    if os['name'] == name: # correspondance exacte seulement (sauf majuscule)
                        ret.append(os)
                return ret
            
            # Construction de la liste lines_a qui contient un dico pour chaque interventions
            lines_a =[]
            for activity in activities:
                acts = activity['CropZoneIds'] # pour chaque interventions (à une date donnée) liste avec un dico contenant des infos des parcelles impliquées

                # pour chaque parcelle où a eu lieu l'intervention on ajoute un dico dans lines_a
                for index_parcelle in range(0,len(acts)) :
                    line=dict()
                       
                    line['Start'] = activity['StartingDate']+"-10:00" # ajoute dans l'index 'start' du dico la date de début de l'intervention au format de date de PHIS (-10:00 pour être sûr d'avoir une heure qui ne fait pas changer de jour la date)
                    line['End'] = activity['EndingDate']+"-10:00" # ajoute dans l'index 'End' du dico la date de fin de l'intervention au format de date de PHIS (-10:00 pour être sûr d'avoir une heure qui ne fait pas changer de jour la date)
                    line['EventType'] = getTypeUri(activity['OperationCategory']) # ajoute dans l'index 'EventType' du dico le type d'intervention de PHIS à partir de celui de geofolia
                    line['Nom_parcelle'] = getNameParcelle(acts[index_parcelle]['PlotId'],lines_f) # ajoute dans l'index 'Nom_parcelle' du dico le nom de la parcelle où l'intervention a eu lieu
                    
                    rid = acts[index_parcelle]["RecognitionId"] # identifiant de l'intervention sur la parcelle
                    surf = acts[index_parcelle]["WorkedSurface"] # surface sur laquelle l'intervention a eu lieu
                    
                    PQU = getProdQteUnit_RId(activity["ProductIds"],rid) # on récupère une liste de listes contenant : [Nom du produit, la quantité, l'unité] utilisé sur la parcelle et [none] si l'intervention n'a pas nécésité de produit
                    
                    if PQU[0] : # si l'intervention a nécessité des produits
                        line['Description'] = activity['OperationName']+" " # ajoute dans l'index 'Description' du dico le nom de l'intervention suivi d'un espace
                        for k in range (0,len(PQU)): # pour chaque produit dans la liste
                            # on ajoute dans l'index 'Description' le nom du produit avec la quantité calculé à l'ha et l'unité
                            line['Description'] += " "+str(PQU[k][0])+" "+str(round(float(PQU[k][1])/(float(surf)*0.0001),2))+" "+str(PQU[k][2]+"/ha")

                    else : # si l'intervention n'a pas nécessité des produits
                        line['Description'] = activity['OperationName'] # ajoute dans l'index 'Description' du dico le nom de l'intervention

                    lines_a.append(line)

            # on supprime de lines_a les dico d'intervention ayant exactement les mêmes informations : on obtient la liste des interventions uniques
            lines_a_u = pd.DataFrame(lines_a).drop_duplicates().to_dict('records')

            
            #On construit lines_corresp = liste avec un dico pour chaque parcelle où a eu lieu au moins une intervention. Dans chaque dico on a : nom de la parcelle et uri de l'OS correspondant dans PHIS s'il existe sinon none 
            #1 avoir une dico par parcelle avec interventions avec le nom de la parcelle
            lines_corresp = pd.DataFrame(lines_a_u).drop(columns=['Start','End','EventType','Description']).drop_duplicates().to_dict('records')


            #2 : on ajoute dans lines_corresp l'URI des OS correspondant aux parcelles si trouvé dans PHIS (None sinon)
            # partie la plus longue lors de l'exécution du script : c'est pourquoi on met un compteur dans la boucle pour suivre l'avancement de la récupération des URI
            nb_parc= len(lines_corresp)
            aa=0
            for line in lines_corresp:
                OS_ = getOS_uri(line['Nom_parcelle'],pythonClient)
                if OS_ != []:
                    line['Target']=OS_[0]['uri']
                else :
                    line['Target']=None
                aa+=1
                a=int((aa/nb_parc)*100)
                self.progressBar.setValue(a)
                


            # fonction permet d'aller chercher dans lines_coresp l'URI à partir de 'Nom_parcelle'
            def getTarget(nom, lines_corresp):
                ret=None
                for l in lines_corresp :
                    if l['Nom_parcelle'] == nom :
                        ret= l['Target']
                        break
                return(ret)           

            # On ajoute l'URI des OS dans l'index 'Target' des dico d'intervention : on obtient liste de dicos finales lines_a_phis = 1 dico par interventions sur des OS déclarés dans PHIS
            
            lines_a_phis =[]
            for l in lines_a_u :
                l['Targets']=[getTarget(l['Nom_parcelle'],lines_corresp)]
                if l['Targets']!= [None]:
                    lines_a_phis.append(l)
            
            # On construit la liste bodys qui contient les body pour déclarer chaque intervention comme des évènements dans PHIS
            bodys = []

            for line in lines_a_phis:
                targets = line['Targets']
                rdf_type = line['EventType']
                end = line['End']
                start = line['Start']
                description = line['Description']
                instant = 'false'

                bodys.append(opensilexWSClient.EventCreationDTO(rdf_type=rdf_type,
                                                        end=end,
                                                        start=start,
                                                        is_instant=instant,
                                                        targets=targets,
                                                        description=description,
                                                        relations = [] ))

            # Fonction qui permet de déclarer dans PHIS les évènements qui ne sont pas déjà déclarés: on obtient en sortie une liste d'URI d'OS dont l'évènement est déjà déclaré et le nombre d'interventions déclarées
            def sendEventCheckExist(bodys,pythonClient):
                event_api = opensilexWSClient.EventsApi(pythonClient)
                errors = []
                sent = 0
                for body in bodys:                 
                    exist = event_api.search_events(rdf_type=body.rdf_type, start= body.start, end=body.end, target=body.targets[0], description=body.description)['metadata']["pagination"]['totalCount']>0

                    if exist:
                        errors.append(body.targets[0])
                    else:
                        event_api.create_events(body = [body])
                        sent+=1
                return errors,sent

            # On exécute la focntion sendEventCheckExist
            logs, nsend = sendEventCheckExist(bodys,pythonClient)

            # On construit le texte contenant le détail de l'exécution
            uri_count=""
            concerne=""
            if len(logs)>0 : # si au moins un évènement déjà déclaré
                # on convertit en dataframe la liste des URI d'OS dont l'évènement est déjà déclaré 
                df_err=pd.DataFrame({"uri":logs})
                # on récupère combien de fois on retrouve chaque URI = nbre d'évènement déjà déclaré par OS
                uri_count=df_err["uri"].value_counts()
                concerne="Concerne le(s) OS :"

            txt_detail = "Nombre d'interventions déclarées : {0}\n\nNombre d'interventions déjà déclarées : {1} \n{2} \n{3}".format(nsend,len(logs),concerne,uri_count).replace("Name: uri, dtype: int64","")
            
            # Affiche le pop-up pour indiquer le résultat de l'exécution
            reussi=Reussi()
            reussi.get_detail(txt_detail)
            widget.addWidget(reussi)
            widget.setCurrentIndex(widget.currentIndex()+1)
            widget.setFixedWidth(513)
            widget.setFixedHeight(300)
        
        # Afficher le pop-up d'erreur et l'erreur
        except Exception as err:
            txt_erreur = "{0}".format(err)
            erreur=Erreur()
            erreur.get_err(txt_erreur)
            widget.addWidget(erreur)
            widget.setCurrentIndex(widget.currentIndex()+1)
            widget.setFixedWidth(511)
            widget.setFixedHeight(211)

# Interface qui s'affiche lorsque l'exéction du script a été un succès avec possibilité de revenir à l'interface principale en cliquant sur le bouton "OK"
class Reussi(QDialog):
    def __init__(self) :
        super(Reussi,self).__init__()
        loadUi("reussi.ui",self)
        self.r_retour.clicked.connect(self.retour)
    
    # Permet de mettre le texte de détail de l'exécution du script dans l'espace prévu à cet effet 
    def get_detail(self,txt_detail) :
        self.details.setText(txt_detail)

    def retour(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(228)

# Interface qui s'affiche lorsque erreur lors de l'exécution du script avec possibilité de revenir à l'interface principale en cliquant sur le bouton "OK"
class Erreur(QDialog):
    def __init__(self) :
        super(Erreur,self).__init__()
        loadUi("erreur.ui",self)
        self.e_retour.clicked.connect(self.retour)

    # Permet de mettre le texte d'erreue dans l'espace prévu à cet effet
    def get_err(self,txt_erreur):
        self.err_descr.setText(txt_erreur)

    def retour(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(228)

# Interface qui permet de configurer le cient de l'API de PHIS avec possibilité de revenir à l'interface principale en cliquant sur le bouton "OK"
class Client_PHIS(QDialog):
    def __init__(self) :
        super(Client_PHIS,self).__init__()
        loadUi("client_phis.ui",self)
        
        # lance la méthode permettant de créer dans l'éditeur de registre le dossier qui contiendra la correspondance clé-valeur des paramètres du client PHIS
        self.getSetValues()
        # On crée les "clés"
        host=self.setting_variables.value('host')
        id=self.setting_variables.value('id')
        mdp=self.setting_variables.value('mdp')

        self.hostvalue = self.setting_variables.value('host')
        self.host.setText(self.hostvalue)
        self.idvalue = self.setting_variables.value('id')
        self.id.setText(self.idvalue)
        self.mdpvalue = self.setting_variables.value('mdp')
        self.mdp.setText(self.mdpvalue)

        self.valid_client.clicked.connect(self.retour)
    
    def getSetValues (self):
        self.setting_variables = QSettings('AppITKGeofoliaPHIS', 'Variables')

    # Pour sauvegarder les valeurs saisies dans les champs + retourner à la page principale après clic sur "OK"
    def retour(self):
        self.setting_variables.setValue('host', self.host.text())
        self.setting_variables.setValue('id', self.id.text())
        self.setting_variables.setValue('mdp', self.mdp.text())

        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(228)

    # Fonctions qui renvoient ce qui est contenu dans les champs de "ClientPHIS"
    def get_host_value(self):
        return(self.host.text())

    def get_id_value(self):
        return(self.id.text())

    def get_mdp_value(self):
        return(self.mdp.text())

# Permet d'afficher l'interface principale lors de l'ouverture de l'application
app = QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(500)
widget.setFixedHeight(228)

widget.show()
sys.exit(app.exec_())
