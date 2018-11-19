#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ValiderModeleDonneesSDE.py
# Auteur    : Michel Pothier
# Date      : 04 novembre 2014

"""
    Application qui permet de valider et corriger le mod�le de donn�es SDE.

    Le mod�le de donn�es SDE est souvent corrompu car certaines tables SDE sont d�truites directement dans Oracle
    sans utiliser les commandes ESRI qui permettent de conserver l'int�grit� entres ces derni�res. 
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [PROD_PRO/PROD_TST/PROD_DEV]
                            d�faut = PROD_PRO
    corriger        OB      Indique si le mod�le SDE doit �tre corrig� (True) ou seulement valid� (False).
                            d�faut = False
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ValiderModeleDonneesSDE.py env corriger

    Exemple:
        ValiderModeleDonneesSDE.py PROD_PRO True

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderModeleDonneesSDE.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderModeleDonneesSDE(object):
#*******************************************************************************************
    """
    Valider et corriger le mod�le de donn�es SDE.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider et corriger le mod�le de donn�es SDE..
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        # D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerItemsFeatureClass(self, corriger):
    #-------------------------------------------------------------------------------------
        """
        Valider et corriger le mod�le de donn�es SDE pour les ITEMS de type FeatureClass.
        
        Param�tres:
        -----------
        corriger        : Indique si le mod�le SDE doit �tre corrig� (True) ou seulement valid� (False).
               
        Variables:
        ----------       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        nbErrItems1     : Nombre d'erreurs pour les items
        nbErrItems2     : Nombre d'erreurs pour les items qui ne sont plus en relation avec au moins un autre item
        """
        
        #Initialisation
        nbErrItems1 = 0
        
        #Validation de l'information sur les GDB_ITEMS de type FeatureClass
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation de l'information sur les GDB_ITEMS de type FeatureClass")
        sSql = "SELECT distinct IT.uuid, IT.physicalname from SDE.GDB_ITEMS IT, SDE.GDB_ITEMTYPES TY where IT.TYPE = TY.UUID and TY.NAME in ('Feature Class', 'Table') order by IT.physicalname"
        arcpy.AddMessage(sSql)
        resultat = self.BDG.query(sSql)
        
        #Traitement de l'information sur les GDB_ITEMS de type FeatureClass en erreur
        arcpy.AddMessage("Nombre de propri�taires/tables : " + str(len(resultat)))
        for rec in resultat:
            #V�rifier si l'attribut PHYSICALNAME contient le propri�taire et le nom de la table
            if '.' in rec[1]:
                #Extraire le nom du propri�taire de la FeatureClass � partir de l'attribut PHYSICALNAME de la table GDB_ITEMS
                sOwner = rec[1].split('.')[0]
                #Extraire le nom de la FeatureClass � partir de l'attribut PHYSICALNAME de la table GDB_ITEMS
                sTable_name = rec[1].split('.')[1]
                
                #Valider la pr�sence d'erreurs
                sSql = "SELECT COUNT(*) FROM DBA_TABLES WHERE UPPER(owner) = UPPER('" + sOwner + "') AND UPPER(table_name) = UPPER('" + sTable_name + "')"
                resultat = self.BDG.query(sSql)
                #V�rifier si aucun propri�taire est pr�sent
                if resultat[0][0] == 0:
                    #Compter le nombre d'erreurs
                    nbErrItems1 = nbErrItems1 + 2
                    
                    #Destruction des relations (GDB_ITEMRELATIONSHIPS) invalides
                    sSql_1 = "DELETE FROM SDE.GDB_ITEMRELATIONSHIPS WHERE DESTID = (SELECT UUID FROM SDE.GDB_ITEMS WHERE PHYSICALNAME = '" + rec[1] + "') OR ORIGINID = (SELECT UUID FROM SDE.GDB_ITEMS WHERE PHYSICALNAME = '" + rec[1] + "')"
                    arcpy.AddMessage(sSql_1)
                    
                    #Destruction des items (GDB_ITEMS) invalides
                    sSql_2 = "DELETE FROM SDE.GDB_ITEMS WHERE UUID = '" + rec[0] + "'"
                    arcpy.AddMessage(sSql_2)
                    
                    #V�rifier si on doit effectuer les corrections
                    if corriger:
                        #Effectuer les corrections invalides
                        arcpy.AddMessage("- Correction effectu�e")
                        self.BDG.execute(sSql_1)
                        self.BDG.execute(sSql_2)
        #Afficher le nombre d'erreurs
        arcpy.AddMessage("Nombre d'erreurs : " + str(nbErrItems1))

        #Validation des items (GDB_ITEMS) qui ne sont plus en relation avec au moins un autre item
        #Exclusion des types d'items 'DEFAULT', 'WORKSPACE'	
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation des items (GDB_ITEMS) qui ne sont plus en relation avec au moins un autre item")
        sSql_3 = "SELECT * FROM SDE.GDB_ITEMS WHERE UUID NOT IN (SELECT ORIGINID FROM SDE.GDB_ITEMRELATIONSHIPS) AND UUID NOT IN (SELECT DESTID FROM SDE.GDB_ITEMRELATIONSHIPS) AND PHYSICALNAME NOT IN ('DEFAULT','WORKSPACE')"
        arcpy.AddMessage(sSql_3)
        resultat = self.BDG.query(sSql_3)
        #V�rifier la pr�sence d'erreurs
        nbErrItems2 = len(resultat)
        if nbErrItems2 > 0:
            #Traitement des items (GDB_ITEMS) en erreur
            sSql_4 = "DELETE FROM SDE.GDB_ITEMS WHERE UUID NOT IN (SELECT ORIGINID FROM SDE.GDB_ITEMRELATIONSHIPS) AND UUID NOT IN (SELECT DESTID FROM SDE.GDB_ITEMRELATIONSHIPS) AND PHYSICALNAME NOT IN ('DEFAULT','WORKSPACE')"
            arcpy.AddMessage(sSql_4)
            #V�rifier si on doit effectuer les corrections
            if corriger:
                #Effectuer les corrections invalides
                arcpy.AddMessage("- Correction effectu�e")
                self.BDG.execute(sSql_4)
        #Afficher le nombre d'erreurs
        arcpy.AddMessage("Nombre d'erreurs : " + str(nbErrItems2))
        
        #Sortir et retourner le nombre d'erreurs
        return nbErrItems1 + nbErrItems2
    
    #-------------------------------------------------------------------------------------
    def validerTableRegistry(self, corriger):
    #-------------------------------------------------------------------------------------
        """
        Valider et corriger le mod�le de donn�es SDE pour les TABLE REGISTRY.
        
        Param�tres:
        -----------
        corriger        : Indique si le mod�le SDE doit �tre corrig� (True) ou seulement valid� (False).
               
        Variables:
        ----------       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        nbErr           : Nombre d'erreurs
        """
        
        #Initialisation
        nbErr =0
        
        #Validation de l'information sur les TABLE REGISTRY
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation de l'information sur les TABLE REGISTRY")
        sSql = "SELECT DISTINCT owner,table_name FROM sde.TABLE_REGISTRY ORDER BY owner,table_name"
        arcpy.AddMessage(sSql)
        resultat = self.BDG.query(sSql)
        
        #Traitement de l'information sur les TABLE REGISTRY
        arcpy.AddMessage("Nombre de propri�taires/tables : " + str(len(resultat)))
        for rec in resultat:
            #V�rifier la pr�sence des tables et des propri�taires
            sSql = "SELECT COUNT(*) FROM DBA_TABLES WHERE UPPER(owner) = UPPER('" + rec[0] + "') AND UPPER(table_name) = UPPER('" + rec[1] + "')"
            resultat = self.BDG.query(sSql)
            #V�rifier si aucun propri�taire est pr�sent
            if resultat[0][0] == 0:
                #Compter le nombre d'erreurs
                nbErr = nbErr + 3
                
                #Destruction des TABLE_REGISTRY invalides
                sSql_1 = "DELETE FROM SDE.TABLE_REGISTRY WHERE UPPER(owner) = UPPER('" + rec[0] + "') AND UPPER(table_name) = UPPER('" + rec[1] + "')"
                arcpy.AddMessage(sSql_1)
                
                #Destruction des COLUMN_REGISTRY invalides
                sSql_2 = "DELETE FROM SDE.COLUMN_REGISTRY WHERE UPPER(owner) = UPPER('" + rec[0] + "') AND UPPER(table_name) = UPPER('" + rec[1] + "')"
                arcpy.AddMessage(sSql_2)
                
                #Destruction des SDE_XML_DOC1 invalides
                sSql_3 = "DELETE FROM SDE.SDE_XML_DOC1 WHERE UPPER(XML_DOC_VAL) LIKE '%" + rec[0].upper() + "." + rec[1].upper() + "%'"
                arcpy.AddMessage(sSql_3)
            
                #V�rifier si on doit effectuer les corrections
                if corriger:
                    #Effectuer les corrections invalides
                    arcpy.AddMessage("- Correction effectu�e")
                    self.BDG.execute(sSql_1)
                    self.BDG.execute(sSql_2)
                    self.BDG.execute(sSql_3)
        #Afficher le nombre d'erreurs
        arcpy.AddMessage("Nombre d'erreurs : " + str(nbErr))
        
        #Sortir et retourner le nombre d'erreurs
        return nbErr
    
    #-------------------------------------------------------------------------------------
    def validerLayers(self, corriger):
    #-------------------------------------------------------------------------------------
        """
        Valider et corriger le mod�le de donn�es SDE pour les LAYERS.
        
        Param�tres:
        -----------
        corriger        : Indique si le mod�le SDE doit �tre corrig� (True) ou seulement valid� (False).
               
        Variables:
        ----------       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        nbErr           : Nombre d'erreurs
        """
        
        #Initialisation
        nbErr =0
        
        #Validation de l'information sur les LAYERS
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation de l'information sur les LAYERS")
        sSql = "SELECT DISTINCT owner,table_name,spatial_column FROM sde.LAYERS ORDER BY owner,table_name"
        arcpy.AddMessage(sSql)
        resultat = self.BDG.query(sSql)
        
        #Traitement de l'information sur les LAYERS
        arcpy.AddMessage("Nombre de propri�taires/tables : " + str(len(resultat)))
        for rec in resultat:
            #V�rifier la pr�sence des tables et des propri�taires
            sSql = "SELECT COUNT(*) FROM DBA_TABLES WHERE UPPER(owner) = UPPER('" + rec[0] + "') AND UPPER(table_name) = UPPER('" + rec[1] + "')"
            resultat = self.BDG.query(sSql)
            #V�rifier si aucun propri�taire est pr�sent
            if resultat[0][0] == 0:
                #Compter le nombre d'erreurs
                nbErr = nbErr + 2
                
                #Destruction des LAYERS invalides
                sSql_1 = "DELETE FROM SDE.LAYERS WHERE UPPER(owner) = UPPER('" + rec[0] + "') AND UPPER(table_name) = UPPER('" + rec[1] + "')"
                arcpy.AddMessage(sSql_1)
                
                #Destruction des GEOMETRY_COLUMNS invalides
                sSql_2 = "DELETE FROM SDE.GEOMETRY_COLUMNS WHERE UPPER(f_table_schema) = UPPER('" + rec[0] + "') AND UPPER(f_geometry_column) = UPPER('" + rec[2] + "')"
                arcpy.AddMessage(sSql_2)
                
                #V�rifier si on doit effectuer les corrections
                if corriger:
                    #Effectuer les corrections invalides
                    arcpy.AddMessage("- Correction effectu�e")
                    self.BDG.execute(sSql_1)
                    self.BDG.execute(sSql_2)
        #Afficher le nombre d'erreurs
        arcpy.AddMessage("Nombre d'erreurs : " + str(nbErr))
        
        #Sortir et retourner le nombre d'erreurs
        return nbErr
    
    #-------------------------------------------------------------------------------------
    def validerStGeometry(self, corriger):
    #-------------------------------------------------------------------------------------
        """
        Valider et corriger le mod�le de donn�es SDE pour les ST_GEOMETRY.
        
        Param�tres:
        -----------
        corriger        : Indique si le mod�le SDE doit �tre corrig� (True) ou seulement valid� (False).
               
        Variables:
        ----------       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        nbErr           : Nombre d'erreurs
        """
        
        #Initialisation
        nbErr =0
        
        #Validation de l'information sur les ST_GEOMETRY
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation de l'information sur les ST_GEOMETRY")
        sSql = "SELECT DISTINCT owner,table_name FROM sde.ST_GEOMETRY_COLUMNS ORDER BY owner,table_name"
        arcpy.AddMessage(sSql)
        resultat = self.BDG.query(sSql)
        
        #Traitement de l'information sur les ST_GEOMETRY
        arcpy.AddMessage("Nombre de propri�taires/tables : " + str(len(resultat)))
        for rec in resultat:
            #V�rifier la pr�sence des tables et des propri�taires
            sSql = "SELECT COUNT(*) FROM DBA_TABLES WHERE UPPER(owner) = UPPER('" + rec[0] + "') AND UPPER(table_name) = UPPER('" + rec[1] + "')"
            resultat = self.BDG.query(sSql)
            #arcpy.AddMessage(sSql)
            #V�rifier si aucun propri�taire est pr�sent
            if resultat[0][0] == 0:
                #Compter le nombre d'erreurs
                nbErr = nbErr + 2
                
                #Destruction des ST_GEOMETRY_COLUMNS invalides
                sSql_1 = "DELETE FROM SDE.ST_GEOMETRY_COLUMNS WHERE UPPER(owner) = UPPER('" + rec[0] + "') AND UPPER(table_name) = UPPER('" + rec[1] + "')"
                arcpy.AddMessage(sSql_1)
                
                #Destruction des ST_GEOMETRY_INDEX invalides
                sSql_2 = "DELETE FROM SDE.ST_GEOMETRY_INDEX WHERE UPPER(f_table_schema) = UPPER('" + rec[0] + "') AND UPPER(f_geometry_column) = UPPER('" + rec[1] + "')"
                arcpy.AddMessage(sSql_2)
                
                #V�rifier si on doit effectuer les corrections
                if corriger:
                    #Effectuer les corrections invalides
                    arcpy.AddMessage("- Correction effectu�e")
                    self.BDG.execute(sSql_1)
                    self.BDG.execute(sSql_2)
        #Afficher le nombre d'erreurs
        arcpy.AddMessage("Nombre d'erreurs : " + str(nbErr))
        
        #Sortir et retourner le nombre d'erreurs
        return nbErr
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, corriger):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider et corriger le mod�le de donn�es SDE.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        corriger    : Indique si le mod�le SDE doit �tre corrig� (True) ou seulement valid� (False).
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        nbErr           : Nombre d'erreurs
        """
        
        #Initialisation
        nbErr =0
        
        #Instanciation de la classe BDG et connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)   
        
        #Validation de l'information sur les GDB_ITEMS de type FeatureClass
        nbErr = nbErr + self.validerItemsFeatureClass(corriger)
        
        #Validation de l'information sur les TABLE REGISTRY
        nbErr = nbErr + self.validerTableRegistry(corriger)
        
        #Validation de l'information sur les LAYERS
        nbErr = nbErr + self.validerLayers(corriger)
        
        #Validation de l'information sur les ST GEOMETRY
        nbErr = nbErr + self.validerStGeometry(corriger)
        
        #Sauver les modifications si demand�
        if corriger:
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Sauver les corrections effectu�es")
            arcpy.AddMessage("COMMIT")
            self.BDG.execute("COMMIT")
        
        #Afficher le nombre d'erreurs total
        arcpy.AddMessage(" ")
        if nbErr == 0:
            arcpy.AddMessage("Nombre d'erreurs total : " + str(nbErr))
        else:
            arcpy.AddWarning("Nombre d'erreurs total : " + str(nbErr))
        
        # Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir et retourner le nombre d'erreurs
        return nbErr

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "BDRS_PRO"
        corriger = False
        
        #Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            corriger = sys.argv[2].upper() == "TRUE"
        
        #D�finir l'objet pour valider le mod�le de donn�es SDE.
        oValiderModeleDonneesSDE = ValiderModeleDonneesSDE()
        
        #Ex�cuter le traitement pour valider le mod�le de donn�es SDE.
        oValiderModeleDonneesSDE.executer(env, corriger)
    
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