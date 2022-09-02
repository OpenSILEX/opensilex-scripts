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


os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

    def config_client_phis(self):
        client_phis=Client_PHIS()
        widget.addWidget(client_phis)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(485)
        widget.setFixedHeight(200)

    def browsefiles_in(self):
        fname=QFileDialog.getOpenFileName(self,'Ouvrir le fichier')
        self.filename.setText(fname[0])

    def exec_script(self):

        try :

            filepath = self.filename.text()
            zip = zipfile.ZipFile(filepath)
            
            actions_str = str(zip.read('Action.Json'),encoding='utf-8-sig')
            field_str = str(zip.read('Field.Json'),encoding='utf-8-sig')

            
            actions_json = json.loads(actions_str)
            field_json = json.loads(field_str)

            
            fields = field_json['Fields']
            activities = actions_json['Activities']

            
            self.progressBar.setValue(50)

            
            lines_f = []
            for field in fields:
                line = dict()
                line['Id_parcelle'] = field['Id']
                line['Nom_parcelle'] = field['Name']
                lines_f.append(line)


            
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

            
            def getNameParcelle(Id,lines_f) :
                ret=None
                for l in lines_f:
                    if l['Id_parcelle'] == Id :
                        ret = l['Nom_parcelle']
                        break
                return(ret)

           
            def getProdQteUnit_RId (liste_produit, rid) : 
                liste_p_act=[None]
                if liste_produit :
                    liste_p_act=[]
                    for l in liste_produit :
                        if l["RecognitionId"] == rid :
                            ret = [l["SupplyName"],l["Quantity"],l["ReferentialUnitSymbol"]]
                            liste_p_act.append(ret)
                return(liste_p_act)

            
            host = Client_PHIS().get_host_value()
            user = Client_PHIS().get_id_value()
            password = Client_PHIS().get_mdp_value()

            
            pythonClient = opensilexWSClient.ApiClient()

           
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
                    if os['name'] == name: 
                        ret.append(os)
                return ret
            
            
            lines_a =[]
            for activity in activities:
                acts = activity['CropZoneIds'] 

                for index_parcelle in range(0,len(acts)) :
                    line=dict()
                    
                    line['Start'] = activity['StartingDate']+"-10:00"
                    line['End'] = activity['EndingDate']+"-10:00"
                    line['EventType'] = getTypeUri(activity['OperationCategory'])
                    line['Nom_parcelle'] = getNameParcelle(acts[index_parcelle]['PlotId'],lines_f)
                    
                    rid = acts[index_parcelle]["RecognitionId"]
                    surf = acts[index_parcelle]["WorkedSurface"]
                    
                    PQU = getProdQteUnit_RId(activity["ProductIds"],rid)
                    
                    if PQU[0] :
                        line['Description'] = activity['OperationName']+" "
                        for k in range (0,len(PQU)):
                            line['Description'] += " "+str(PQU[k][0])+" "+str(round(float(PQU[k][1])/(float(surf)*0.0001),2))+" "+str(PQU[k][2]+"/ha")

                    else :
                        line['Description'] = activity['OperationName']

                    lines_a.append(line)

            
            lines_a_u = pd.DataFrame(lines_a).drop_duplicates().to_dict('records')

            lines_corresp = pd.DataFrame(lines_a_u).drop(columns=['Start','End','EventType','Description']).drop_duplicates().to_dict('records')

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
                

            def getTarget(nom, lines_corresp):
                ret=None
                for l in lines_corresp :
                    if l['Nom_parcelle'] == nom :
                        ret= l['Target']
                        break
                return(ret)           

            
            lines_a_phis =[]
            for l in lines_a_u :
                l['Targets']=[getTarget(l['Nom_parcelle'],lines_corresp)]
                if l['Targets']!= [None]:
                    lines_a_phis.append(l)
            
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

            
            logs, nsend = sendEventCheckExist(bodys,pythonClient)

            uri_count=""
            concerne=""
            if len(logs)>0 :
                df_err=pd.DataFrame({"uri":logs})
                uri_count=df_err["uri"].value_counts()
                concerne="Concerne le(s) OS :"

            txt_detail = "Nombre d'interventions déclarées : {0}\n\nNombre d'interventions déjà déclarées : {1} \n{2} \n{3}".format(nsend,len(logs),concerne,uri_count).replace("Name: uri, dtype: int64","")
            

            reussi=Reussi()
            reussi.get_detail(txt_detail)
            widget.addWidget(reussi)
            widget.setCurrentIndex(widget.currentIndex()+1)
            widget.setFixedWidth(513)
            widget.setFixedHeight(300)

        except Exception as err:
            txt_erreur = "{0}".format(err)
            erreur=Erreur()
            erreur.get_err(txt_erreur)
            widget.addWidget(erreur)
            widget.setCurrentIndex(widget.currentIndex()+1)
            widget.setFixedWidth(511)
            widget.setFixedHeight(211)

class Reussi(QDialog):
    def __init__(self) :
        super(Reussi,self).__init__()
        loadUi("reussi.ui",self)
        self.r_retour.clicked.connect(self.retour)
    
    def get_detail(self,txt_detail) :
        self.details.setText(txt_detail)

    def retour(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(228)


class Erreur(QDialog):
    def __init__(self) :
        super(Erreur,self).__init__()
        loadUi("erreur.ui",self)
        self.e_retour.clicked.connect(self.retour)

    def get_err(self,txt_erreur):
        self.err_descr.setText(txt_erreur)

    def retour(self):
        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(228)

class Client_PHIS(QDialog):
    def __init__(self) :
        super(Client_PHIS,self).__init__()
        loadUi("client_phis.ui",self)
        
        self.getSetValues()
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

    def retour(self):
        self.setting_variables.setValue('host', self.host.text())
        self.setting_variables.setValue('id', self.id.text())
        self.setting_variables.setValue('mdp', self.mdp.text())

        mainwindow=MainWindow()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        widget.setFixedWidth(500)
        widget.setFixedHeight(228)

    def get_host_value(self):
        return(self.host.text())

    def get_id_value(self):
        return(self.id.text())

    def get_mdp_value(self):
        return(self.mdp.text())

app = QApplication(sys.argv)
mainwindow=MainWindow()
widget=QtWidgets.QStackedWidget()
widget.addWidget(mainwindow)
widget.setFixedWidth(500)
widget.setFixedHeight(228)

widget.show()
sys.exit(app.exec_())
