#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ValiderDonneesGeodatabaseCatalogue.py
# Auteur    : Michel Pothier
# Date      : 25 février 2015

"""
    Application qui permet de valider les données d'une géodatabase en fonction de l'information contenue dans un catalogue.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue.
                            défaut = 1:BDG
    classe          OB      Liste des noms de classe du catalogue à valider.
                            défaut = <Toutes les classes présentes dans le catalogue>
    attribut        OB      Liste des noms d'attribut du catalogue à valider.
                            défaut = <Tous les attributs présents dans le catalogue>
    exclure         OB      Liste des attributs à exclure de la validation.
                            defaut="SHAPE.LEN,SHAPE.AREA,SHAPE,OBJECTID,CODE_SPEC"
    workspace       OB      Nom de la géodatabase contenant les données à valider.
                            défaut = "Database Connections\BDRS_PRO.sde"
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ValiderDonneesGeodatabaseCatalogue.py env catalogue classe attribut exclure workspace

    Exemple:
        ValiderDonneesGeodatabaseCatalogue.py CATREL_PRO 1:BDG NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 WATER_DEFINITION,PERMANENCY "SHAPE.LEN,SHAPE.AREA,SHAPE,OBJECTID,CODE_SPEC" "Database Connections\BDRS_PRO.sde"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderDonneesGeodatabaseCatalogue.py 1121 2016-08-02 20:51:38Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderDonneesGeodatabaseCatalogue(object):
#*******************************************************************************************
    """
    Permet de valider les données d'une géodatabase en fonction de l'information contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les données d'une géodatabase en fonction de l'information contenue dans un catalogue.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, workspace, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        workspace   : Nom de la géodatabase contenant les données à valider.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        #Valider la présence
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')
        
        #Valider la présence
        if (len(catalogue) == 0):
            raise Exception ('Paramètre obligatoire manquant: catalogue')
        
        #Valider la présence
        if (len(classe) == 0):
            raise Exception ('Paramètre obligatoire manquant: classe')
        
        #Valider la présence
        if (len(attribut) == 0):
            raise Exception ('Paramètre obligatoire manquant: attribut')
        
        #Valider la présence
        if (len(workspace) == 0):
            raise Exception ('Paramètre obligatoire manquant: workspace')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, catalogue, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des paramètres.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue.
        workspace   : Nom de la géodatabase contenant les données à valider.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
         
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Vérification des valeurs des paramètres")
        
        #Créer la requête SQL pour vérifier si le catalogue est valide
        arcpy.AddMessage("- Vérifier si le catalogue est valide")
        sql = ("SELECT DISTINCT FEAT_CATAL_BDG_VER_NUM"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " ")
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #Vérifier si le Workspace est valide
        arcpy.AddMessage("- Vérifier si le Workspace est valide")
        #Vérifier si le Workspace est absent
        if not arcpy.Exists(workspace):
            #Envoyer une exception
            raise Exception("Workspace absent : " + workspace)
        #Vérifier si le Workspace est invalide
        if arcpy.Describe(workspace).DataType <> "Workspace":
            #Envoyer une exception
            raise Exception("Workspace invalide : " + workspace)
        #Extraire l'information du Workspace
        desc = arcpy.Describe(workspace)
        #Conserver l'usager
        self.user = desc.connectionProperties.user
        #Envoyer un message
        arcpy.AddMessage(u"  Usagé propriétaire des classes : " + self.user)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerClasses(self, catalogue, classe, workspace):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la liste des classes entre le catalogue et la Géodatabase.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        classe      : Liste des noms de classe du catalogue à valider.
        workspace   : Nom de la géodatabase contenant les données à valider.
        
        Variables:
        ----------
        sql             : Requête SQL à exécuter.
        cls             : Nom de la classe du catalogue à traiter.
        clsGDB          : Nom de la classe de la Géodatabase à traiter.
        clsResultat     : Liste des classes extraites du catalogue.
        fcResultat      : Liste des feature classes extraites de la Géodatabase.
        tblResultat     : Liste des tables extraites de la Géodatabase.
        clsCatalogue    : Ensemble des classes du catalogue à traiter.
        clsGeodatabase  : Ensemble des classes de la Géodatabase à traiter.
        clsCatalogueErr : Ensemble des classes du catalogue en erreur.
        clsGeodatabaseErr: Ensemble des classes de la Géodatabase en erreur.
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider les classes entre le catalogue et la Géodatabase")        
        
        #Créer la SQL pour définir la liste des classes du catalogue
        sql = ("select distinct B.feat_type_name_database"
               "  from feat_catalogue A, feat_type B"
               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_name_database is not NULL"
               " order by B.feat_type_name_database")
        #arcpy.AddMessage(sql)
        #Exécuter la SQL
        clsResultat = self.BDG.query(sql)
        #Initialiser la liste des classes du catalogue
        clsCatalogue = set([])
        #Créer la liste des classes du catalogue
        for cls in clsResultat:
            #Ajouter la classe à la liste
            clsCatalogue.add(cls[0])
        
        #Initialiser la liste des classes de la géodatabase
        clsGeodatabase = set([])
        #Définir le workspace par défaut
        arcpy.env.workspace = workspace
        
        #Extraire la liste des featureClasses de la Géodatabase
        fcResultat = arcpy.ListFeatureClasses(self.user + "*")
        #Créer la liste des classes de la Géodatabase
        for cls in fcResultat:
            #Ajouter la classe à la liste
            clsGeodatabase.add(cls.upper().split(".")[1])
        #Extraire la liste des tables de la Géodatabase
        tblResultat = arcpy.ListTables(self.user + "*")
        #Ajouter les tables à la liste des classes de la Géodatabase
        for clsGDB in tblResultat:
            #Définir le nom de la classe selon le catalogue
            cls = clsGDB.upper().split(".")[1]
            #Ajouter la table à la liste
            clsGeodatabase.add(cls)
        
        #Définir la liste des classes du catalogue en erreur
        clsCatalogueErr = clsCatalogue.difference(clsGeodatabase)
        #Afficher le résultat du catalogue
        arcpy.AddMessage(" Catalogue")
        arcpy.AddMessage("  Nombre de classes : " + str(len(clsCatalogue)))
        if len(clsCatalogueErr) > 0:
            arcpy.AddWarning("   Classes absentes de la géodatabase : ")
            for cls in sorted(clsCatalogueErr):
                #Si la classes est présente dans la liste à traiter
                if cls in classe:
                    arcpy.AddError("    " + cls)
        
        #Définir la liste des classes de la géodatabase en erreur
        clsGeodatabaseErr = clsGeodatabase.difference(clsCatalogue)
        #Afficher le résultat de la Geodatabase
        arcpy.AddMessage(" Géodatabase")
        arcpy.AddMessage("  Nombre de classes : " + str(len(clsGeodatabase)))
        if len(clsGeodatabaseErr) > 0:
            arcpy.AddWarning("   Classes absentes du catalogue : ")
            for cls in sorted(clsGeodatabaseErr):
                arcpy.AddWarning("    " + cls)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerAttributs(self, catalogue, classe, attribut, exclure, workspace):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la liste des attributs par classe entre le catalogue et la Géodatabase.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        classe      : Liste des noms de classe du catalogue à valider.
        attribut    : Liste des noms d'attribut du catalogue à valider.
        exclure     : Liste des attributs à exclure de la validation.
        workspace   : Nom de la géodatabase contenant les données à valider.
        
        Variables:
        ----------
        cls             : Nom de la classe du catalogue à traiter.
        attExlure       : Ensemble des attributs à exclure de la validation.
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider les attributs de chaque classe entre le catalogue et la Géodatabase")
        
        #Définir les attributs à exclure
        attExclure = set(exclure.split(","))
        
        #Traiter toutes les classes à valider
        for cls in classe.split(","):
            #Afficher la classe à valider
            arcpy.AddMessage(cls)
            
            #Vérifier si la classe est présente dans la Géodatabase
            if arcpy.Exists(self.user + "." + cls):
                #Valider les attributs (absence et type) pour une classe du catalogue
                self.validerAttributClasse(catalogue, cls, attribut, attExclure)
                
                #Valider les valeurs des attributs codés pour une classe en fonction des domaines du catalogue
                self.validerDomaineAttributCodeClasse(catalogue, cls, attribut, workspace)
            else:
                #Afficher la classe absente
                arcpy.AddWarning(" Classe absente")
                
            #Afficher un séparateur
            arcpy.AddMessage(" ")
            
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerAttributClasse(self, catalogue, cls, attribut, attExclure):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider l'absence et le type d'attribut par classe entre le catalogue et la Géodatabase.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        cls         : Nom de la classe du catalogue à valider.
        attribut    : Liste des noms d'attribut du catalogue à valider.
        attExclure  : Ensemble des attributs à exclure de la validation.
        
        Variables:
        ----------
        sql                 : Requête SQL à exécuter.
        att                 : Nom de l'attribut à traiter.
        attResultat         : Liste des attributs à traiter.
        attCatalogue        : Ensemble des attributs du catalogue à traiter.
        attTypeCatalogue    : Ensemble des types d'attributs du catalogue à traiter.
        attCatalogueErr     : Ensemble des attributs du catalogue en erreur.
        attTypeCatalogueErr : Ensemble des types d'attributs du catalogue en erreur.
        attGeodatabase      : Ensemble des attributs du catalogue à traiter.
        attTypeGeodatabase  : Ensemble des types d'attributs du catalogue à traiter.
        attGeodatabaseErr   : Ensemble des attributs du catalogue en erreur.
        attTypeGeodatabaseErr: Ensemble des types d'attributs du catalogue en erreur.
        """
        
        #Créer la SQL pour définir la liste des attributs
        sql = ("select distinct D.feat_attr_name_database,D.feat_attr_data_type"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id"
               "   and B.feat_type_name_database='" + cls + "'"
               " order by D.feat_attr_name_database")
        #arcpy.AddMessage(sql)
        #Exécuter la SQL
        attResultat = self.BDG.query(sql)
        #Initialiser la liste des attributs du catalogue
        attCatalogue = set([])
        attTypeCatalogue = set([])
        #Créer la liste des attributs du catalogue
        for att in attResultat:
            #Ajouter l'attribut à la liste
            attCatalogue.add(str(att[0]))
            #Ajouter le type de l'attribut à la liste
            attTypeCatalogue.add(str(att[0]) + ":" + str(att[1]).replace(" ","").replace('DECIMAL','Double').replace('INTEGER','Integer').replace('CHARACTER','String').replace("IDUU","String(32)"))
        
        #Initialiser la liste des attributs de la géodatabase
        attGeodatabase = set([])
        attTypeGeodatabase = set([])
        #Extraire la liste des attributs de la Géodatabase
        attResultat = arcpy.ListFields(self.user + "." + cls)
        #Créer la liste des attributs de la Géodatabase
        for att in attResultat:
            #Vérifier si l'attribut n'est pas exclut
            if att.name not in attExclure:
                #Ajouter l'attribut à la liste
                attGeodatabase.add(att.name)
                #Ajouter le type de l'attribut à la liste
                if att.type <> "String":
                    attTypeGeodatabase.add(att.name + ":" + att.type)
                else:
                    attTypeGeodatabase.add(att.name + ":" + att.type + "(" + str(att.length) + ")")
        
        #Définir la liste des attributs du catalogue en erreur
        attCatalogueErr = attCatalogue.difference(attGeodatabase)
        attTypeCatalogueErr = attTypeCatalogue.difference(attTypeGeodatabase)
        #Afficher le résultat du catalogue
        arcpy.AddMessage(" Catalogue")
        arcpy.AddMessage("  Nombre d'attributs : " + str(len(attCatalogue)))
        if len(attCatalogueErr) > 0:
            arcpy.AddError("   Attributs absents de la Géodatabase : " + str(len(attCatalogueErr)))
            for att in sorted(attCatalogueErr):
                #Vérifier si l'attribut est présent dans la liste à traiter
                if att in attribut:
                    arcpy.AddError("    " + att)
        if len(attTypeCatalogueErr) > 0:
            arcpy.AddWarning("   Types différents de la Géodatabase : " + str(len(attTypeCatalogueErr)))
            for attType in sorted(attTypeCatalogueErr):
                #Définir le nom de l'attribut
                att = attType.split(":")[0]
                #Vérifier si l'attribut est présent dans la liste à traiter
                if att in attribut:
                    arcpy.AddWarning("    " + attType)
        
        #Définir la liste des attributs de la géodatabase en erreur
        attGeodatabaseErr = attGeodatabase.difference(attCatalogue).difference(attExclure)
        attTypeGeodatabaseErr = attTypeGeodatabase.difference(attTypeCatalogue)
        #Afficher le résultat de la Géodatabase
        arcpy.AddMessage(" Géodatabase")
        arcpy.AddMessage("  Nombre d'attributs : " + str(len(attGeodatabase)))
        if len(attGeodatabaseErr) > 0:
            arcpy.AddWarning("   Attributs absents du catalogue : " + str(len(attGeodatabaseErr)))
            for att in sorted(attGeodatabaseErr):
                arcpy.AddWarning("    " + att)
        if len(attTypeGeodatabaseErr) > 0:
            arcpy.AddWarning("   Types différents du catalogue : " + str(len(attTypeGeodatabaseErr)))
            for att in sorted(attTypeGeodatabaseErr):
                arcpy.AddWarning("    " + att)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerDomaineAttributCodeClasse(self, catalogue, cls, attribut, workspace, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut codé pour une classe de la Géodatabase en fonction du domaine contenu dans le catalogue.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        cls         : Nom de la classe du catalogue à valider.
        attribut    : Liste des noms d'attribut du catalogue à valider.
        workspace   : Nom de la géodatabase contenant les données à valider.
        codeSpec    : Nom de l'attribut de la Géodatabase contenant le code spécifique.
        
        Variables:
        ----------
        sql                 : Requête SQL à exécuter.
        att                 : Nom de l'attribut et du code spécifique à traiter.
        attResultat         : Liste des attributs et codes spécifiques à traiter.
        valCatalogue        : Ensemble des valeurs d'attributs du catalogue à traiter.
        attCatalogueErr     : Ensemble des valeurs attributs du catalogue en erreur.
        valGeodatabase      : Ensemble des valeurs d'attributs du catalogue à traiter.
        attGeodatabaseErr   : Ensemble des valeurs d'attributs du catalogue en erreur.
        """
        #Initialiser le code spécifique traité
        code = ""
        nbElem = 0
        
        #Créer la SQL pour définir la liste des codes spécifiques pour chaque attribut codé
        sql = ("select distinct D.feat_attr_name_database, B.feat_type_code_bd, B.feat_type_name_fr"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database in ('" + attribut.replace(",","','") + "')"
               " order by B.feat_type_code_bd, D.feat_attr_name_database")
        #arcpy.AddMessage(sql)
        #Exécuter la SQL
        attResultat = self.BDG.query(sql)
        
        #Créer la liste des codes spécifiques par attribut codé
        for att in attResultat:
            #Vérifier si c'est un code différent
            if str(att[1]) <> code:
                #Définir le code traité
                code = str(att[1])
                #Afficher le code spécifique
                arcpy.AddMessage(" ")
                arcpy.AddMessage(cls)
                arcpy.AddMessage(" " + code + ":" + str(att[2]))
                
                #Créer la SQL pour définir l'ensemble des valeurs de la Géodatabase
                sql = "select count(*) from " + self.user + "." + cls + " where " + codeSpec + "=" + str(att[1])
                #arcpy.AddMessage(sql)
                try:
                    #Exécuter la SQL
                    nbElem = int(self.SDE.execute(sql))
                except Exception as err:
                    nbElem = 0
                    #arcpy.AddError(" " + err.message)
                
                #Vérifier la présence d'éléments
                if nbElem > 0:
                    #Afficher le nombre d'élément
                    arcpy.AddMessage(u"  Nombre d'éléments dans la Géodatabase : " + str(nbElem))
                #Si aucun élément
                else:
                    #Afficher le nombre d'élément
                    arcpy.AddWarning(u"  Aucun élément présent dans la Géodatabase")
            
            #Vérifier la présence d'éléments
            if nbElem > 0:
                #Afficher l'attribut traité
                arcpy.AddMessage("  " + str(att[0]))
                
                #Initialiser l'ensemble des valeurs du catalogue
                valCatalogue = set([])
                #Créer la SQL pour définir l'ensemble des valeurs du catalogue
                sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE"
                       "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                       " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                       "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                       "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + str(att[0]) + "' and B.feat_type_code_bd='" + str(att[1]) + "'"
                       " order by E.ATTR_VALUE_INTERNAL_CODE")
                #arcpy.AddMessage(sql)
                #Exécuter la SQL
                valResultat = self.BDG.query(sql)
                #Traiter tous les résultats pour définir l'ensemble des valeurs du catalogue
                for val in valResultat:
                    #Ajouter l'attribut à la liste
                    valCatalogue.add(val[0])
                
                #Initialiser l'ensemble des valeurs de la Géodatabase
                valGeodatabase = set([])
                #Créer la SQL pour définir l'ensemble des valeurs de la Géodatabase
                sql = "select distinct " + str(att[0]) + " from " + self.user + "." + cls + " where " + codeSpec + "=" + str(att[1]) + " order by " + str(att[0])
                try:
                    #arcpy.AddMessage(sql)
                    #Exécuter la SQL
                    valResultat = self.SDE.execute(sql)
                    #Vérifier si le résultat est une list
                    if type(valResultat) == list:
                        #Traiter tous les résultats pour définir l'ensemble des valeurs de la Géodatabase
                        for val in valResultat:                        
                            #Ajouter la valeur d'attribut à la liste
                            valGeodatabase.add(val[0])
                    #Si le résultat est un entier
                    elif type(valResultat) == int:
                        #Ajouter la valeur d'attribut à la liste
                        valGeodatabase.add(valResultat)
                except Exception as err:
                    arcpy.AddError("   " + err.message)
                
                #Définir la liste des valeurs d'attributs du catalogue en erreur
                valCatalogueErr = valCatalogue.difference(valGeodatabase)
                #Afficher le résultat du catalogue
                arcpy.AddMessage("   Catalogue")
                arcpy.AddMessage("    Nombre de valeurs d'attributs : " + str(len(valCatalogue)))
                arcpy.AddMessage("     " + str(sorted(valCatalogue)))
                if len(valCatalogueErr) > 0:
                    arcpy.AddWarning("    Valeur d'attributs absentes de la Géodatabase : " + str(len(valCatalogueErr)))
                    arcpy.AddWarning("     " + str(sorted(valCatalogueErr)))
                
                #Définir la liste des valeurs d'attributs de la géodatabase en erreur
                valGeodatabaseErr = valGeodatabase.difference(valCatalogue)
                #Afficher le résultat de la Géodatabase
                arcpy.AddMessage("   Géodatabase")
                arcpy.AddMessage("    Nombre de valeurs d'attributs : " + str(len(valGeodatabase)))
                arcpy.AddMessage("     " + str(sorted(valGeodatabase)))
                if len(valGeodatabaseErr) > 0:
                    arcpy.AddError("    Valeur d'attributs absentes du catalogue : " + str(len(valGeodatabaseErr)))
                    arcpy.AddError("     " + str(sorted(valGeodatabaseErr)))
                
        #Sortir
        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, classe, attribut, exclure, workspace):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider les données d'une géodatabase en fonction de l'information contenue dans un catalogue.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        exclure     :Liste des attributs à exclure de la validation.
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requête SQL à exécuter.
        """
        
        #Vérification de la présence des paramètres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, attribut, workspace)
        
        #Vérifier la connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Vérifier la connexion à SDE
        arcpy.AddMessage("- Connexion à SDE")
        self.SDE = arcpy.ArcSDESQLExecute(workspace)
        
        #Valider les valeurs des paramètres
        self.validerValeurParam(catalogue, workspace)
        
        #Valider les classes entre le catalogue et la Géodatabase
        self.validerClasses(catalogue, classe, workspace)
        
        #Valider les attributs de chaque classe entre le catalogue et la Géodatabase
        self.validerAttributs(catalogue, classe, attribut, exclure, workspace)
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env         = "CATREL_PRO"
        catalogue   = "1:BDG"
        classe      = ""
        attribut    = ""
        exclure     = "SHAPE.LEN,SHAPE.AREA,SHAPE,OBJECTID,CODE_SPEC"
        workspace   = "Database Connections\BDRS_PRO.sde"
        
        #Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            classe = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            attribut = sys.argv[4].upper().replace(";",",")
        
        if len(sys.argv) > 5:
            exclure = sys.argv[5]
        
        if len(sys.argv) > 6:
            workspace = sys.argv[6]
        
        #Définir l'objet pour valider les données d'une géodatabase en fonction de l'information contenue dans un catalogue.
        oValiderDonneesGeodatabaseCatalogue = ValiderDonneesGeodatabaseCatalogue()
        
        #Exécuter le traitement pour valider les données d'une géodatabase en fonction de l'information contenue dans un catalogue.
        oValiderDonneesGeodatabaseCatalogue.executer(env, catalogue, classe, attribut, exclure, workspace)
            
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("- Succès du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)