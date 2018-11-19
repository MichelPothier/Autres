#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerCopieBaseDonneesFGDB.py
# Auteur    : Michel Pothier
# Date      : 28 janvier 2015

"""
    Application qui permet de créer une copie d'une Base de Données spatiale dans une FGDB (FileGeoDataBase).

    Ce programme est utilisé entre autre pour effectuer un Release une Copie de la BDG.
    
    Paramètres d'entrée:
    --------------------
    database        OB      Nom de la Base de Données dans lequel on veut copier les tables et les FeatureClass dans une FGDB.
                            défaut = 
    repertoire      OB      Nom du répertoire dans lequel la FGDB doit être créée.
                            défaut = \\dfscitsh\cits\Travail\charg_rels
    fgdb            OB      Nom de la FGDB à créer.
                            défaut = Release_XX
    proprietaire    OB      Nom du propriétaire des tables ou featureClass à copier dans la FGDB.
                            défaut = BDG_DBA
    compression     OB      Indique si on doit effectuer une compression (True) ou non (False).
                            défaut = True
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerCopieBaseDonneesFGDB.py env corriger

    Exemple:
        CreerCopieBaseDonneesFGDB.py PROD_PRO True

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerCopieBaseDonneesFGDB.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

#Importation des modules publiques
import os, sys, arcpy, traceback

#Importation des modules privés (Cits)
#import 

#*******************************************************************************************
class CreerCopieBaseDonneesFGDB(object):
#*******************************************************************************************
    """
    Permet de créer une copie d'une Base de Données spatiale dans une FGDB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer une copie d'une Base de Données spatiale dans une FGDB.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        Aucun
        
        """
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, database, repertoire, fgdb, proprietaire):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        database        : Nom de la Base de Données dans lequel on veut copier les tables et les FeatureClass dans une FGDB.
        repertoire      : Nom du répertoire dans lequel la FGDB doit être créée.
        fgdb            : Nom de la FGDB à créer.
        proprietaire    : Nom du propriétaire des tables ou featureClass à copier dans la FGDB.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(database) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'database')
        
        if (len(repertoire) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'repertoire')
        
        if (len(fgdb) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'fgdb')
        
        if (len(proprietaire) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'proprietaire')

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, database, repertoire, fgdb, proprietaire, compression):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour créer une copie d'une Base de Données spatiale dans une FGDB.
        
        Paramètres:
        -----------
        database        : Nom de la Base de Données dans lequel on veut copier les tables et les FeatureClass dans une FGDB.
        repertoire      : Nom du répertoire dans lequel la FGDB doit être créée.
        fgdb            : Nom de la FGDB à créer.
        proprietaire    : Nom du propriétaire des tables ou featureClass à copier dans la FGDB.
        compression     : Indique si on doit effectuer une compression (True) ou non (False).
        
        Variables:
        ----------

        """

        #Définir le Workspace par défaut selan celui de la Base de Données
        arcpy.env.workspace = database
        
        #Extraire la liste des Tables
        listeTables = arcpy.ListTables(proprietaire + "*")
        
        #Extraire la liste des FeatureClass
        listeFeatureClass = arcpy.ListFeatureClasses(proprietaire + "*")
        
        #Vérifier si la FGDB existe déjà
        if arcpy.Exists(repertoire + "\\" + fgdb + ".gdb"):
            #Envoyer un avertissement
            arcpy.AddWarning("La FGDB existe déjà !")
            fgdb = repertoire + "\\" + fgdb + ".gdb"
        #Si la FGDB n'existe pas
        else:
            #Créer la FGDB
            arcpy.AddMessage(" ")
            fgdb = str(arcpy.CreateFileGDB_management(repertoire, fgdb))
            arcpy.AddMessage(arcpy.GetMessages())
        
        #Copier toutes les tables de la DataBase vers la FGDB
        for table in listeTables:
            #Afficher un message pour Copier la table dans la FGDB
            arcpy.AddMessage(" ")
            arcpy.AddMessage("Executing: TableToTable " + table + " " + fgdb + " " + table.replace(proprietaire + ".", ""))
            #Vérifier si la table existe déjà
            if arcpy.Exists(fgdb + "\\" + table.replace(proprietaire + ".", "")):
                #Envoyer un avertissement
                arcpy.AddWarning("La table existe déjà !")
            #Si la table n'existe pas
            else:
                try:
                     #Copier la table dans la FGDB
                    arcpy.TableToTable_conversion(table, fgdb, table.replace(proprietaire + ".", ""))
                    #Afficher tous les messages sauf le premier
                    for i in range(1,arcpy.GetMessageCount()):
                        arcpy.AddMessage(arcpy.GetMessage(i))
                        
               #Gestion des erreurs
                except Exception, err:                
                    #Afficher tous les messages sauf le premier
                    for i in range(1,arcpy.GetMessageCount()):
                        #Afficher un message d'erreur
                        arcpy.AddError(arcpy.GetMessage(i))
                        
        #Copier toutes les FeatureClass de la DataBase vers la FGDB
        for featureClass in listeFeatureClass:
            #Afficher un message pour Copier la featureClass dans la FGDB
            arcpy.AddMessage(" ")
            arcpy.AddMessage("Executing: FeatureClassToFeatureClass " + featureClass + " " + fgdb + " " + featureClass.replace(proprietaire + ".", ""))
            #Vérifier si la featureClass existe déjà
            if arcpy.Exists(fgdb + "\\" + featureClass.replace(proprietaire + ".", "")):
                #Envoyer un avertissement
                arcpy.AddWarning("La featureClass existe déjà !")
            #Si la featureClass n'existe pas
            else:
                #Copier la featureClass dans la FGDB
                arcpy.FeatureClassToFeatureClass_conversion(featureClass, fgdb, featureClass.replace(proprietaire + ".", ""))
                #Afficher tous les messages sauf le premier
                for i in range(1,arcpy.GetMessageCount()):
                    arcpy.AddMessage(arcpy.GetMessage(i))
        
        #Vérifier si on doit compresser la FGDB
        if compression:
            #Compression de la FGDB
            arcpy.AddMessage(" ")
            arcpy.AddMessage("Executing: CompressFileGeodatabaseData_management " + fgdb)
            arcpy.CompressFileGeodatabaseData_management(fgdb)
            arcpy.AddMessage(arcpy.GetMessages())
            
        #Sortir
        arcpy.AddMessage(" ")
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        database = ""
        repertoire = "\\dfscitsh\cits\Travail\charg_rels"
        fgdb = "Release_XX"
        proprietaire = "BDG_DBA"
        compression = True
        
        #Lecture des paramètres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            database = sys.argv[1]
        
        if len(sys.argv) > 2:
            repertoire = sys.argv[2]
        
        if len(sys.argv) > 3:
            fgdb = sys.argv[3]
        
        if len(sys.argv) > 4:
            proprietaire = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            compression = sys.argv[5].upper() == "TRUE"
        
        #Définir l'objet pour créer une copie d'une Base de Données spatiale dans une FGDB
        oCreerCopieBaseDonneesFGDB = CreerCopieBaseDonneesFGDB()
        
        #Exécuter le traitement pour créer une copie d'une Base de Données spatiale dans une FGDB
        oCreerCopieBaseDonneesFGDB.executer(database, repertoire, fgdb, proprietaire, compression)
    
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