#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ValiderDonneesGeodatabaseCatalogue.py
# Auteur    : Michel Pothier
# Date      : 25 f�vrier 2015

"""
    Application qui permet de valider les donn�es d'une g�odatabase en fonction de l'information contenue dans un catalogue.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue.
                            d�faut = 1:BDG
    classe          OB      Liste des noms de classe du catalogue � valider.
                            d�faut = <Toutes les classes pr�sentes dans le catalogue>
    attribut        OB      Liste des noms d'attribut du catalogue � valider.
                            d�faut = <Tous les attributs pr�sents dans le catalogue>
    exclure         OB      Liste des attributs � exclure de la validation.
                            defaut="SHAPE.LEN,SHAPE.AREA,SHAPE,OBJECTID,CODE_SPEC"
    workspace       OB      Nom de la g�odatabase contenant les donn�es � valider.
                            d�faut = "Database Connections\BDRS_PRO.sde"
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderDonneesGeodatabaseCatalogue(object):
#*******************************************************************************************
    """
    Permet de valider les donn�es d'une g�odatabase en fonction de l'information contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les donn�es d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        #D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, workspace, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        workspace   : Nom de la g�odatabase contenant les donn�es � valider.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        #Valider la pr�sence
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')
        
        #Valider la pr�sence
        if (len(catalogue) == 0):
            raise Exception ('Param�tre obligatoire manquant: catalogue')
        
        #Valider la pr�sence
        if (len(classe) == 0):
            raise Exception ('Param�tre obligatoire manquant: classe')
        
        #Valider la pr�sence
        if (len(attribut) == 0):
            raise Exception ('Param�tre obligatoire manquant: attribut')
        
        #Valider la pr�sence
        if (len(workspace) == 0):
            raise Exception ('Param�tre obligatoire manquant: workspace')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, catalogue, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des param�tres.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        workspace   : Nom de la g�odatabase contenant les donn�es � valider.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
         
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification des valeurs des param�tres")
        
        #Cr�er la requ�te SQL pour v�rifier si le catalogue est valide
        arcpy.AddMessage("- V�rifier si le catalogue est valide")
        sql = ("SELECT DISTINCT FEAT_CATAL_BDG_VER_NUM"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " ")
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #V�rifier si le Workspace est valide
        arcpy.AddMessage("- V�rifier si le Workspace est valide")
        #V�rifier si le Workspace est absent
        if not arcpy.Exists(workspace):
            #Envoyer une exception
            raise Exception("Workspace absent : " + workspace)
        #V�rifier si le Workspace est invalide
        if arcpy.Describe(workspace).DataType <> "Workspace":
            #Envoyer une exception
            raise Exception("Workspace invalide : " + workspace)
        #Extraire l'information du Workspace
        desc = arcpy.Describe(workspace)
        #Conserver l'usager
        self.user = desc.connectionProperties.user
        #Envoyer un message
        arcpy.AddMessage(u"  Usag� propri�taire des classes : " + self.user)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerClasses(self, catalogue, classe, workspace):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la liste des classes entre le catalogue et la G�odatabase.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        classe      : Liste des noms de classe du catalogue � valider.
        workspace   : Nom de la g�odatabase contenant les donn�es � valider.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        cls             : Nom de la classe du catalogue � traiter.
        clsGDB          : Nom de la classe de la G�odatabase � traiter.
        clsResultat     : Liste des classes extraites du catalogue.
        fcResultat      : Liste des feature classes extraites de la G�odatabase.
        tblResultat     : Liste des tables extraites de la G�odatabase.
        clsCatalogue    : Ensemble des classes du catalogue � traiter.
        clsGeodatabase  : Ensemble des classes de la G�odatabase � traiter.
        clsCatalogueErr : Ensemble des classes du catalogue en erreur.
        clsGeodatabaseErr: Ensemble des classes de la G�odatabase en erreur.
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider les classes entre le catalogue et la G�odatabase")        
        
        #Cr�er la SQL pour d�finir la liste des classes du catalogue
        sql = ("select distinct B.feat_type_name_database"
               "  from feat_catalogue A, feat_type B"
               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_name_database is not NULL"
               " order by B.feat_type_name_database")
        #arcpy.AddMessage(sql)
        #Ex�cuter la SQL
        clsResultat = self.BDG.query(sql)
        #Initialiser la liste des classes du catalogue
        clsCatalogue = set([])
        #Cr�er la liste des classes du catalogue
        for cls in clsResultat:
            #Ajouter la classe � la liste
            clsCatalogue.add(cls[0])
        
        #Initialiser la liste des classes de la g�odatabase
        clsGeodatabase = set([])
        #D�finir le workspace par d�faut
        arcpy.env.workspace = workspace
        
        #Extraire la liste des featureClasses de la G�odatabase
        fcResultat = arcpy.ListFeatureClasses(self.user + "*")
        #Cr�er la liste des classes de la G�odatabase
        for cls in fcResultat:
            #Ajouter la classe � la liste
            clsGeodatabase.add(cls.upper().split(".")[1])
        #Extraire la liste des tables de la G�odatabase
        tblResultat = arcpy.ListTables(self.user + "*")
        #Ajouter les tables � la liste des classes de la G�odatabase
        for clsGDB in tblResultat:
            #D�finir le nom de la classe selon le catalogue
            cls = clsGDB.upper().split(".")[1]
            #Ajouter la table � la liste
            clsGeodatabase.add(cls)
        
        #D�finir la liste des classes du catalogue en erreur
        clsCatalogueErr = clsCatalogue.difference(clsGeodatabase)
        #Afficher le r�sultat du catalogue
        arcpy.AddMessage(" Catalogue")
        arcpy.AddMessage("  Nombre de classes : " + str(len(clsCatalogue)))
        if len(clsCatalogueErr) > 0:
            arcpy.AddWarning("   Classes absentes de la g�odatabase : ")
            for cls in sorted(clsCatalogueErr):
                #Si la classes est pr�sente dans la liste � traiter
                if cls in classe:
                    arcpy.AddError("    " + cls)
        
        #D�finir la liste des classes de la g�odatabase en erreur
        clsGeodatabaseErr = clsGeodatabase.difference(clsCatalogue)
        #Afficher le r�sultat de la Geodatabase
        arcpy.AddMessage(" G�odatabase")
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
        Permet de valider la liste des attributs par classe entre le catalogue et la G�odatabase.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        classe      : Liste des noms de classe du catalogue � valider.
        attribut    : Liste des noms d'attribut du catalogue � valider.
        exclure     : Liste des attributs � exclure de la validation.
        workspace   : Nom de la g�odatabase contenant les donn�es � valider.
        
        Variables:
        ----------
        cls             : Nom de la classe du catalogue � traiter.
        attExlure       : Ensemble des attributs � exclure de la validation.
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider les attributs de chaque classe entre le catalogue et la G�odatabase")
        
        #D�finir les attributs � exclure
        attExclure = set(exclure.split(","))
        
        #Traiter toutes les classes � valider
        for cls in classe.split(","):
            #Afficher la classe � valider
            arcpy.AddMessage(cls)
            
            #V�rifier si la classe est pr�sente dans la G�odatabase
            if arcpy.Exists(self.user + "." + cls):
                #Valider les attributs (absence et type) pour une classe du catalogue
                self.validerAttributClasse(catalogue, cls, attribut, attExclure)
                
                #Valider les valeurs des attributs cod�s pour une classe en fonction des domaines du catalogue
                self.validerDomaineAttributCodeClasse(catalogue, cls, attribut, workspace)
            else:
                #Afficher la classe absente
                arcpy.AddWarning(" Classe absente")
                
            #Afficher un s�parateur
            arcpy.AddMessage(" ")
            
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerAttributClasse(self, catalogue, cls, attribut, attExclure):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider l'absence et le type d'attribut par classe entre le catalogue et la G�odatabase.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        cls         : Nom de la classe du catalogue � valider.
        attribut    : Liste des noms d'attribut du catalogue � valider.
        attExclure  : Ensemble des attributs � exclure de la validation.
        
        Variables:
        ----------
        sql                 : Requ�te SQL � ex�cuter.
        att                 : Nom de l'attribut � traiter.
        attResultat         : Liste des attributs � traiter.
        attCatalogue        : Ensemble des attributs du catalogue � traiter.
        attTypeCatalogue    : Ensemble des types d'attributs du catalogue � traiter.
        attCatalogueErr     : Ensemble des attributs du catalogue en erreur.
        attTypeCatalogueErr : Ensemble des types d'attributs du catalogue en erreur.
        attGeodatabase      : Ensemble des attributs du catalogue � traiter.
        attTypeGeodatabase  : Ensemble des types d'attributs du catalogue � traiter.
        attGeodatabaseErr   : Ensemble des attributs du catalogue en erreur.
        attTypeGeodatabaseErr: Ensemble des types d'attributs du catalogue en erreur.
        """
        
        #Cr�er la SQL pour d�finir la liste des attributs
        sql = ("select distinct D.feat_attr_name_database,D.feat_attr_data_type"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id"
               "   and B.feat_type_name_database='" + cls + "'"
               " order by D.feat_attr_name_database")
        #arcpy.AddMessage(sql)
        #Ex�cuter la SQL
        attResultat = self.BDG.query(sql)
        #Initialiser la liste des attributs du catalogue
        attCatalogue = set([])
        attTypeCatalogue = set([])
        #Cr�er la liste des attributs du catalogue
        for att in attResultat:
            #Ajouter l'attribut � la liste
            attCatalogue.add(str(att[0]))
            #Ajouter le type de l'attribut � la liste
            attTypeCatalogue.add(str(att[0]) + ":" + str(att[1]).replace(" ","").replace('DECIMAL','Double').replace('INTEGER','Integer').replace('CHARACTER','String').replace("IDUU","String(32)"))
        
        #Initialiser la liste des attributs de la g�odatabase
        attGeodatabase = set([])
        attTypeGeodatabase = set([])
        #Extraire la liste des attributs de la G�odatabase
        attResultat = arcpy.ListFields(self.user + "." + cls)
        #Cr�er la liste des attributs de la G�odatabase
        for att in attResultat:
            #V�rifier si l'attribut n'est pas exclut
            if att.name not in attExclure:
                #Ajouter l'attribut � la liste
                attGeodatabase.add(att.name)
                #Ajouter le type de l'attribut � la liste
                if att.type <> "String":
                    attTypeGeodatabase.add(att.name + ":" + att.type)
                else:
                    attTypeGeodatabase.add(att.name + ":" + att.type + "(" + str(att.length) + ")")
        
        #D�finir la liste des attributs du catalogue en erreur
        attCatalogueErr = attCatalogue.difference(attGeodatabase)
        attTypeCatalogueErr = attTypeCatalogue.difference(attTypeGeodatabase)
        #Afficher le r�sultat du catalogue
        arcpy.AddMessage(" Catalogue")
        arcpy.AddMessage("  Nombre d'attributs : " + str(len(attCatalogue)))
        if len(attCatalogueErr) > 0:
            arcpy.AddError("   Attributs absents de la G�odatabase : " + str(len(attCatalogueErr)))
            for att in sorted(attCatalogueErr):
                #V�rifier si l'attribut est pr�sent dans la liste � traiter
                if att in attribut:
                    arcpy.AddError("    " + att)
        if len(attTypeCatalogueErr) > 0:
            arcpy.AddWarning("   Types diff�rents de la G�odatabase : " + str(len(attTypeCatalogueErr)))
            for attType in sorted(attTypeCatalogueErr):
                #D�finir le nom de l'attribut
                att = attType.split(":")[0]
                #V�rifier si l'attribut est pr�sent dans la liste � traiter
                if att in attribut:
                    arcpy.AddWarning("    " + attType)
        
        #D�finir la liste des attributs de la g�odatabase en erreur
        attGeodatabaseErr = attGeodatabase.difference(attCatalogue).difference(attExclure)
        attTypeGeodatabaseErr = attTypeGeodatabase.difference(attTypeCatalogue)
        #Afficher le r�sultat de la G�odatabase
        arcpy.AddMessage(" G�odatabase")
        arcpy.AddMessage("  Nombre d'attributs : " + str(len(attGeodatabase)))
        if len(attGeodatabaseErr) > 0:
            arcpy.AddWarning("   Attributs absents du catalogue : " + str(len(attGeodatabaseErr)))
            for att in sorted(attGeodatabaseErr):
                arcpy.AddWarning("    " + att)
        if len(attTypeGeodatabaseErr) > 0:
            arcpy.AddWarning("   Types diff�rents du catalogue : " + str(len(attTypeGeodatabaseErr)))
            for att in sorted(attTypeGeodatabaseErr):
                arcpy.AddWarning("    " + att)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerDomaineAttributCodeClasse(self, catalogue, cls, attribut, workspace, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut cod� pour une classe de la G�odatabase en fonction du domaine contenu dans le catalogue.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        cls         : Nom de la classe du catalogue � valider.
        attribut    : Liste des noms d'attribut du catalogue � valider.
        workspace   : Nom de la g�odatabase contenant les donn�es � valider.
        codeSpec    : Nom de l'attribut de la G�odatabase contenant le code sp�cifique.
        
        Variables:
        ----------
        sql                 : Requ�te SQL � ex�cuter.
        att                 : Nom de l'attribut et du code sp�cifique � traiter.
        attResultat         : Liste des attributs et codes sp�cifiques � traiter.
        valCatalogue        : Ensemble des valeurs d'attributs du catalogue � traiter.
        attCatalogueErr     : Ensemble des valeurs attributs du catalogue en erreur.
        valGeodatabase      : Ensemble des valeurs d'attributs du catalogue � traiter.
        attGeodatabaseErr   : Ensemble des valeurs d'attributs du catalogue en erreur.
        """
        #Initialiser le code sp�cifique trait�
        code = ""
        nbElem = 0
        
        #Cr�er la SQL pour d�finir la liste des codes sp�cifiques pour chaque attribut cod�
        sql = ("select distinct D.feat_attr_name_database, B.feat_type_code_bd, B.feat_type_name_fr"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database in ('" + attribut.replace(",","','") + "')"
               " order by B.feat_type_code_bd, D.feat_attr_name_database")
        #arcpy.AddMessage(sql)
        #Ex�cuter la SQL
        attResultat = self.BDG.query(sql)
        
        #Cr�er la liste des codes sp�cifiques par attribut cod�
        for att in attResultat:
            #V�rifier si c'est un code diff�rent
            if str(att[1]) <> code:
                #D�finir le code trait�
                code = str(att[1])
                #Afficher le code sp�cifique
                arcpy.AddMessage(" ")
                arcpy.AddMessage(cls)
                arcpy.AddMessage(" " + code + ":" + str(att[2]))
                
                #Cr�er la SQL pour d�finir l'ensemble des valeurs de la G�odatabase
                sql = "select count(*) from " + self.user + "." + cls + " where " + codeSpec + "=" + str(att[1])
                #arcpy.AddMessage(sql)
                try:
                    #Ex�cuter la SQL
                    nbElem = int(self.SDE.execute(sql))
                except Exception as err:
                    nbElem = 0
                    #arcpy.AddError(" " + err.message)
                
                #V�rifier la pr�sence d'�l�ments
                if nbElem > 0:
                    #Afficher le nombre d'�l�ment
                    arcpy.AddMessage(u"  Nombre d'�l�ments dans la G�odatabase : " + str(nbElem))
                #Si aucun �l�ment
                else:
                    #Afficher le nombre d'�l�ment
                    arcpy.AddWarning(u"  Aucun �l�ment pr�sent dans la G�odatabase")
            
            #V�rifier la pr�sence d'�l�ments
            if nbElem > 0:
                #Afficher l'attribut trait�
                arcpy.AddMessage("  " + str(att[0]))
                
                #Initialiser l'ensemble des valeurs du catalogue
                valCatalogue = set([])
                #Cr�er la SQL pour d�finir l'ensemble des valeurs du catalogue
                sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE"
                       "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                       " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                       "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                       "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + str(att[0]) + "' and B.feat_type_code_bd='" + str(att[1]) + "'"
                       " order by E.ATTR_VALUE_INTERNAL_CODE")
                #arcpy.AddMessage(sql)
                #Ex�cuter la SQL
                valResultat = self.BDG.query(sql)
                #Traiter tous les r�sultats pour d�finir l'ensemble des valeurs du catalogue
                for val in valResultat:
                    #Ajouter l'attribut � la liste
                    valCatalogue.add(val[0])
                
                #Initialiser l'ensemble des valeurs de la G�odatabase
                valGeodatabase = set([])
                #Cr�er la SQL pour d�finir l'ensemble des valeurs de la G�odatabase
                sql = "select distinct " + str(att[0]) + " from " + self.user + "." + cls + " where " + codeSpec + "=" + str(att[1]) + " order by " + str(att[0])
                try:
                    #arcpy.AddMessage(sql)
                    #Ex�cuter la SQL
                    valResultat = self.SDE.execute(sql)
                    #V�rifier si le r�sultat est une list
                    if type(valResultat) == list:
                        #Traiter tous les r�sultats pour d�finir l'ensemble des valeurs de la G�odatabase
                        for val in valResultat:                        
                            #Ajouter la valeur d'attribut � la liste
                            valGeodatabase.add(val[0])
                    #Si le r�sultat est un entier
                    elif type(valResultat) == int:
                        #Ajouter la valeur d'attribut � la liste
                        valGeodatabase.add(valResultat)
                except Exception as err:
                    arcpy.AddError("   " + err.message)
                
                #D�finir la liste des valeurs d'attributs du catalogue en erreur
                valCatalogueErr = valCatalogue.difference(valGeodatabase)
                #Afficher le r�sultat du catalogue
                arcpy.AddMessage("   Catalogue")
                arcpy.AddMessage("    Nombre de valeurs d'attributs : " + str(len(valCatalogue)))
                arcpy.AddMessage("     " + str(sorted(valCatalogue)))
                if len(valCatalogueErr) > 0:
                    arcpy.AddWarning("    Valeur d'attributs absentes de la G�odatabase : " + str(len(valCatalogueErr)))
                    arcpy.AddWarning("     " + str(sorted(valCatalogueErr)))
                
                #D�finir la liste des valeurs d'attributs de la g�odatabase en erreur
                valGeodatabaseErr = valGeodatabase.difference(valCatalogue)
                #Afficher le r�sultat de la G�odatabase
                arcpy.AddMessage("   G�odatabase")
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
        Ex�cuter le traitement pour valider les donn�es d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        exclure     :Liste des attributs � exclure de la validation.
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requ�te SQL � ex�cuter.
        """
        
        #V�rification de la pr�sence des param�tres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, attribut, workspace)
        
        #V�rifier la connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #V�rifier la connexion � SDE
        arcpy.AddMessage("- Connexion � SDE")
        self.SDE = arcpy.ArcSDESQLExecute(workspace)
        
        #Valider les valeurs des param�tres
        self.validerValeurParam(catalogue, workspace)
        
        #Valider les classes entre le catalogue et la G�odatabase
        self.validerClasses(catalogue, classe, workspace)
        
        #Valider les attributs de chaque classe entre le catalogue et la G�odatabase
        self.validerAttributs(catalogue, classe, attribut, exclure, workspace)
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env         = "CATREL_PRO"
        catalogue   = "1:BDG"
        classe      = ""
        attribut    = ""
        exclure     = "SHAPE.LEN,SHAPE.AREA,SHAPE,OBJECTID,CODE_SPEC"
        workspace   = "Database Connections\BDRS_PRO.sde"
        
        #Lecture des param�tres
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
        
        #D�finir l'objet pour valider les donn�es d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oValiderDonneesGeodatabaseCatalogue = ValiderDonneesGeodatabaseCatalogue()
        
        #Ex�cuter le traitement pour valider les donn�es d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oValiderDonneesGeodatabaseCatalogue.executer(env, catalogue, classe, attribut, exclure, workspace)
            
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("- Succ�s du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)