import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QProgressBar
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt, QSettings

import opensilexClientToolsPython as osCP
import json
import pandas as pd

# définir le repertoire de travail par défaut dans le dossier dans lequel est le script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Interface principale de l'application
class MainWindow(QDialog):
    def __init__(self) :
        super(MainWindow,self).__init__()
        loadUi("interf.ui",self)
        self.browse_in.clicked.connect(self.browsefiles_in)
        self.browse_out.clicked.connect(self.browsefiles_out)

        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        self.push.clicked.connect(self.exec_script)
        self.config_client.clicked.connect(self.config_client_phis)

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
    
    # fonction qui permet de sélectionner le chemin du fichier en sortie via l'explorateur
    def browsefiles_out(self):
        fname=QFileDialog.getSaveFileName(self,'Créer un nouveau fichier')
        self.filename_out.setText(fname[0])
    
    # fonction qui permet d'exéuter le script "utile" de l'application
    def exec_script(self):

        try :
            
            path_in = self.filename.text()
            path_out = self.filename_out.text()

            # configuration du client
            client_phis = osCP.ApiClient()
            client_phis.connect_to_opensilex_ws(
                host=Client_PHIS().get_host_value(),
                identifier = Client_PHIS().get_id_value(),
                password = Client_PHIS().get_mdp_value()
            )

            # on définit l'objet client pour intéragir avec l'API GermplasmAPI
            germ = osCP.GermplasmApi(client_phis)

            # import de la liste variétale sous forme d'un dataframe
            liste_var = pd.read_excel(path_in)

            # défini le type des germplasm recherchés
            rdf_type="vocabulary:Variety"

            # accéder au nom de la colonne contenant les variétés (la première colonne de l'excel)
            nom_col = liste_var.columns.values[0]

            # Si la colonne supplémentaire est renseignée dans l'Excel (s'il y plus de 2 colonnes)
            if len(liste_var.columns) >1 :
                nom_col_supp = liste_var.columns.values[1]

            # on ajoute des noms de variétés avec "_" en plus de ceux avec espace dans une liste (modifiée)
            liste_var_modif = []

            liste_var_ini =[]

            liste_supp = []

            # on itère sur le nom des variétés de la liste
            for i in range (0,len(liste_var[nom_col])):
                # on ajoute le nom de la variété dans les listes avec et sans le nom modifié et l'info contenue dans la colonne supplémentaire (si elle y est)
                var_ini = liste_var[nom_col][i]
                liste_var_modif.append(var_ini)
                liste_var_ini.append(var_ini)
                if len(liste_var.columns) >1 : 
                    val_supp = liste_var[nom_col_supp][i]
                    liste_supp.append(val_supp)
            # S'il y a un espace dans le nom : ajoute ce nom modifié dans le liste avec le nom modifié + ajoute le nom non modifié dans la liste sans les noms modifié +  l'info contenue dans la colonne supplémentaire (si elle y est)
                if ' ' in var_ini :
                    var_modif = var_ini.replace(" ","_")
                    liste_var_modif.append(var_modif)
                    liste_var_ini.append(var_ini)
                    if len(liste_var.columns) >1 : 
                        val_supp = liste_var[nom_col_supp][i]
                        liste_supp.append(val_supp)
                # S'il y a un "_" dans le nom : ajoute ce nom modifié dans le liste avec le nom modifié et ajoute le nom non modifié dans la liste sans les noms modifié +  l'info contenue dans la colonne supplémentaire (si elle y est)
                elif '_' in var_ini :
                    var_modif = var_ini.replace("_"," ")
                    liste_var_modif.append(var_modif)
                    liste_var_ini.append(var_ini)
                    if len(liste_var.columns) >1 : 
                        val_supp = liste_var[nom_col_supp][i]
                        liste_supp.append(val_supp)

            # liste qui contiendra les lignes du df final
            ligne_df = []

            # première valeur d'avancement
            self.progressBar.setValue(int((1/len(liste_var_modif)*100)/2))

            # on itère sur le nom des variétés de la liste modifiée
            # aa pour suivre l'avancement
            aa=0
            for k in range (0,len(liste_var_modif)) :
                # on récupère le nom de la variété
                var=liste_var_modif[k]

                # on récupère le nbre de résultats trouvé dans PHIS pour le nom de la variété
                nb_r = germ.search_germplasm(name=var,rdf_type=rdf_type)["metadata"]["pagination"]["totalCount"]
                # on récupère le résultat brut en précisant le nombre de résultat pour tous les récupérer
                resul = germ.search_germplasm(name=var,page_size=nb_r,rdf_type=rdf_type)
                aa+=1

                a=int(aa/len(liste_var_modif)*100)
                self.progressBar.setValue(a)
                
                # dans le cas où il n'y a pas de résultat
                if nb_r == 0 :
                    # on génère une ligne vide mais avec les mêmes colonnes que lorsqu'il y a un résultat
                    vide = str({'name': '', 'rdf_type': '','rdf_type_name': '','species': '','species_name': '', 'uri': ''}).replace("\'","\"")
                    dico = json.loads(vide)
                    df =pd.DataFrame.from_dict(dico,orient="index").transpose()
                    # on ajoute la colonne qui contient le nom de variété tel qu'il sont dans la liste initiale
                    df['nom_var_ini']= liste_var_ini[k]
                    if len(liste_var.columns) >1 : df[str(nom_col_supp)]=liste_supp[k]
                    
                    ligne_df.append(df)

                # dans le cas où il y a des résultats
                else :
                    # on génère une ligne par résultat
                    for i in range (0,nb_r):
                        # on récupère le résultat de la forme json au format string et en remplaçant ' par "
                        ch = str(resul["result"][i]).replace("\'","\"")
                        # on convertit la "string json" en dictionnaire
                        dico = json.loads(ch)
                        # on convertit le dictionnaire en df avec les attributs en colonne
                        df =pd.DataFrame.from_dict(dico,orient="index").transpose()
                        # on ajoute la colonne qui contient le nom de variété tel qu'il sont dans la liste initiale
                        df['nom_var_ini']= liste_var_ini[k]
                        if len(liste_var.columns) >1 : df[str(nom_col_supp)]=liste_supp[k]
                        ligne_df.append(df)

            # on concatène toutes les lignes pour faire le df final
            df = pd.concat(ligne_df)

            # ajoute les champs du gabarit
            df['subtaxa'] = ''
            df['code'] = ''
            df['institute'] = ''
            df['website'] = ''
            df['comment'] = ''

            # arrangement de l'ordre des champs du df
            if len(liste_var.columns) >1 : 
                df = df[['uri','name','subtaxa','code','species','institute','website','comment','nom_var_ini',str(nom_col_supp),'species_name','rdf_type_name']]
            else :
                df = df[['uri','name','subtaxa','code','species','institute','website','comment','nom_var_ini','species_name','rdf_type_name']]
            
            # ajout index :
            df=df.reset_index(drop=True)

            # Supprimer les doublons vides :
            # on récupère l'index des lignes vides
            index_vide = df[df['name']==''].index
            #On supprime ces lignes
            df.drop(index_vide,inplace=True)
            
            # ajouter une ligne vide pour les variétés nom trouvées :
            # avoir liste valeur unique de nom_var_ini
            liste_var_u =liste_var[nom_col]
            
            if len(liste_var.columns) >1 :
                #nom_col_supp = liste_var.columns.values[1]
                liste_supp_u = liste_var[nom_col_supp]            
                
                for index_var in range(0,len(liste_var_u)):
                    if liste_var_u[index_var] not in df['nom_var_ini'].values:
                        l_vide = [('','','','','','','','',liste_var_u[index_var],liste_supp_u[index_var],'','')]
                        df_l_vide = pd.DataFrame(l_vide, columns=['uri','name','subtaxa','code','species','institute','website','comment','nom_var_ini',str(nom_col_supp),'species_name','rdf_type_name'])
                        df=pd.concat([df,df_l_vide])
            else :
                for index_var in range(0,len(liste_var_u)):
                    if liste_var_u[index_var] not in df['nom_var_ini'].values:
                        l_vide = [('','','','','','','','',liste_var_u[index_var],'','')]
                        df_l_vide = pd.DataFrame(l_vide, columns=['uri','name','subtaxa','code','species','institute','website','comment','nom_var_ini','species_name','rdf_type_name'])
                        df=pd.concat([df,df_l_vide])


            
            # exporter le df en csv sans la colonne index (erreur si fichier existe déjà)
            df.to_csv(path_out+'.csv',index=False)
            
            reussi=Reussi()
            widget.addWidget(reussi)
            widget.setCurrentIndex(widget.currentIndex()+1)
            widget.setFixedWidth(271)
            widget.setFixedHeight(116)

        # Afficher le pop-up d'erreur et l'erreur
        except Exception as err:
            txt_erreur = "{0}".format(err)
            erreur=Erreur()
            erreur.get_err(txt_erreur)
            widget.addWidget(erreur)
            widget.setCurrentIndex(widget.currentIndex()+1)
            widget.setFixedWidth(511)
            widget.setFixedHeight(211)

# Interface qui s'affiche lorsque l'exéction a été un succès avec possibilité de revenir à l'interface principale en cliquant sur le bouton "OK"
class Reussi(QDialog):
    def __init__(self) :
        super(Reussi,self).__init__()
        loadUi("reussi.ui",self)
        self.r_retour.clicked.connect(self.retour)

    def retour(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(275)

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
        widget.setFixedHeight(275)

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
        self.setting_variables = QSettings('AppVerifGermplasm', 'Variables')

    # Pour sauvegarder les valeurs saisies dans les champs + retourner à la page principale après clic sur "OK"
    def retour(self):
        self.setting_variables.setValue('host', self.host.text())
        self.setting_variables.setValue('id', self.id.text())
        self.setting_variables.setValue('mdp', self.mdp.text())

        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(275)

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
widget.setFixedHeight(275)

widget.show()
sys.exit(app.exec_())
