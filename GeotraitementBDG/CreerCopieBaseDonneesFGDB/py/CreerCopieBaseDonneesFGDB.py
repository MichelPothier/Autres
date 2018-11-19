#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerCopieBaseDonneesFGDB.py
# Auteur    : Michel Pothier
# Date      : 28 janvier 2015

"""
    Application qui permet de cr�er une copie d'une Base de Donn�es spatiale dans une FGDB (FileGeoDataBase).

    Ce programme est utilis� entre autre pour effectuer un Release une Copie de la BDG.
    
    Param�tres d'entr�e:
    --------------------
    database        OB      Nom de la Base de Donn�es dans lequel on veut copier les tables et les FeatureClass dans une FGDB.
                            d�faut = 
    repertoire      OB      Nom du r�pertoire dans lequel la FGDB doit �tre cr��e.
                            d�faut = \\dfscitsh\cits\Travail\charg_rels
    fgdb            OB      Nom de la FGDB � cr�er.
                            d�faut = Release_XX
    proprietaire    OB      Nom du propri�taire des tables ou featureClass � copier dans la FGDB.
                            d�faut = BDG_DBA
    compression     OB      Indique si on doit effectuer une compression (True) ou non (False).
                            d�faut = True
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

#Importation des modules priv�s (Cits)
#import 

#*******************************************************************************************
class CreerCopieBaseDonneesFGDB(object):
#*******************************************************************************************
    """
    Permet de cr�er une copie d'une Base de Donn�es spatiale dans une FGDB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour cr�er une copie d'une Base de Donn�es spatiale dans une FGDB.
        
        Param�tres:
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
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        database        : Nom de la Base de Donn�es dans lequel on veut copier les tables et les FeatureClass dans une FGDB.
        repertoire      : Nom du r�pertoire dans lequel la FGDB doit �tre cr��e.
        fgdb            : Nom de la FGDB � cr�er.
        proprietaire    : Nom du propri�taire des tables ou featureClass � copier dans la FGDB.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(database) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'database')
        
        if (len(repertoire) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'repertoire')
        
        if (len(fgdb) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'fgdb')
        
        if (len(proprietaire) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'proprietaire')

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, database, repertoire, fgdb, proprietaire, compression):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour cr�er une copie d'une Base de Donn�es spatiale dans une FGDB.
        
        Param�tres:
        -----------
        database        : Nom de la Base de Donn�es dans lequel on veut copier les tables et les FeatureClass dans une FGDB.
        repertoire      : Nom du r�pertoire dans lequel la FGDB doit �tre cr��e.
        fgdb            : Nom de la FGDB � cr�er.
        proprietaire    : Nom du propri�taire des tables ou featureClass � copier dans la FGDB.
        compression     : Indique si on doit effectuer une compression (True) ou non (False).
        
        Variables:
        ----------

        """

        #D�finir le Workspace par d�faut selan celui de la Base de Donn�es
        arcpy.env.workspace = database
        
        #Extraire la liste des Tables
        listeTables = arcpy.ListTables(proprietaire + "*")
        
        #Extraire la liste des FeatureClass
        listeFeatureClass = arcpy.ListFeatureClasses(proprietaire + "*")
        
        #V�rifier si la FGDB existe d�j�
        if arcpy.Exists(repertoire + "\\" + fgdb + ".gdb"):
            #Envoyer un avertissement
            arcpy.AddWarning("La FGDB existe d�j� !")
            fgdb = repertoire + "\\" + fgdb + ".gdb"
        #Si la FGDB n'existe pas
        else:
            #Cr�er la FGDB
            arcpy.AddMessage(" ")
            fgdb = str(arcpy.CreateFileGDB_management(repertoire, fgdb))
            arcpy.AddMessage(arcpy.GetMessages())
        
        #Copier toutes les tables de la DataBase vers la FGDB
        for table in listeTables:
            #Afficher un message pour Copier la table dans la FGDB
            arcpy.AddMessage(" ")
            arcpy.AddMessage("Executing: TableToTable " + table + " " + fgdb + " " + table.replace(proprietaire + ".", ""))
            #V�rifier si la table existe d�j�
            if arcpy.Exists(fgdb + "\\" + table.replace(proprietaire + ".", "")):
                #Envoyer un avertissement
                arcpy.AddWarning("La table existe d�j� !")
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
            #V�rifier si la featureClass existe d�j�
            if arcpy.Exists(fgdb + "\\" + featureClass.replace(proprietaire + ".", "")):
                #Envoyer un avertissement
                arcpy.AddWarning("La featureClass existe d�j� !")
            #Si la featureClass n'existe pas
            else:
                #Copier la featureClass dans la FGDB
                arcpy.FeatureClassToFeatureClass_conversion(featureClass, fgdb, featureClass.replace(proprietaire + ".", ""))
                #Afficher tous les messages sauf le premier
                for i in range(1,arcpy.GetMessageCount()):
                    arcpy.AddMessage(arcpy.GetMessage(i))
        
        #V�rifier si on doit compresser la FGDB
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        database = ""
        repertoire = "\\dfscitsh\cits\Travail\charg_rels"
        fgdb = "Release_XX"
        proprietaire = "BDG_DBA"
        compression = True
        
        #Lecture des param�tres
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
        
        #D�finir l'objet pour cr�er une copie d'une Base de Donn�es spatiale dans une FGDB
        oCreerCopieBaseDonneesFGDB = CreerCopieBaseDonneesFGDB()
        
        #Ex�cuter le traitement pour cr�er une copie d'une Base de Donn�es spatiale dans une FGDB
        oCreerCopieBaseDonneesFGDB.executer(database, repertoire, fgdb, proprietaire, compression)
    
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