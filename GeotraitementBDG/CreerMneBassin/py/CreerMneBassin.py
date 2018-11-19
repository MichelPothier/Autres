#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : CreerMneBassin.py
# Auteur    : Michel Pothier
# Date      : 24 f�vrier 2016

"""
    Application qui permet de cr�er les MNEs des Bassin-Versant selon les �l�ments s�lectionn�s dans un FeatureLayer de d�coupage des Bassins-Versants.
    Le nom de l'identifiant est pr�sent dans l'attribut d'identifiant sp�cifi� du FeatureLayer.
    
    Param�tres d'entr�e:
    --------------------
    featureLayer        OB      FeatureLayer contenant les identifiants s�lectionn�s des Bassins-Versants.
                                d�faut = ""
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
                                d�faut = DATASET_NAME
    repertoireSortie    OB      R�pertoire de sortie dans lequel les MNEs des Bassin-Versants seront cr��s.
                                d�faut = "D:\MNE_BASSIN"
    
    Param�tres de sortie:
    ---------------------
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        CreerMneBassin.py featureLayer attributIdentifiant repertoireSortie

    Exemple:
        CreerMneBassin.py "DECOUPAGE-BASSIN" "DATASET_NAME" "D:\MNE_BASSIN"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerMneBassin.py 1994 2015-08-26 13:21:06Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, subprocess, traceback

# Importation des modules priv�s (Cits)

#*******************************************************************************************
class ExceptionCreerMneBassin(Exception):
#*******************************************************************************************
    """
    Classe d'exception d�riv�e de la classe Exception pour g�rer un probl�me
    dans l'ex�cution du programme.
    
    Lors de l'instanciation, passez une cha�ne de caract�re en argument
    pour d'�crire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CreerMneBassin:
#*******************************************************************************************
    """
    Classe qui permet de cr�er les MNEs des Bassin-Versant selon les �l�ments s�lectionn�s
    dans un FeatureLayer de d�coupage des Bassins-Versants.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        
        """
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, featureLayer, attributIdentifiant, repertoireSortie):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        featureLayer        : FeatureLayer contenant les identifiants s�lectionn�s des Bassins-Versants.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'�l�ment.
        repertoireSortie    : R�pertoire de sortie dans lequel les MNEs des Bassin-Versants seront cr��s.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(featureLayer) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'featureLayer')
        
        if (len(attributIdentifiant) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'attributIdentifiant')
        
        if (len(repertoireSortie) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'repertoireSortie')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, featureLayer, attributIdentifiant, repertoireSortie):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation des MNE de bassin correspondants aux �l�ments d'identifiant de d�coupage s�lectionn�s.
        
        Param�tres:
        ----------- 
        featureLayer        : FeatureLayer contenant les identifiants s�lectionn�s des Bassins-Versants.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'�l�ment.
        repertoireSortie    : R�pertoire de sortie dans lequel les MNEs des Bassin-Versants seront cr��s.
        
        Variables:
        ----------
        cursor          : Contient les �l�ments de d�coupage s�lectionn�s.
        row             : Contient un �l�ment de d�coupage trait�.
        identifiant     : Contient la valeur de l'identifiant de d�coupage d'un bassin trait�.
        fichierShp      : Contient le nom du fichier contenant le polygone de d�coupage.
        fichierTmp      : Contient le nom du fichier Tif du MNE temporaire.
        fichierTif      : Contient le nom du fichier Tif du MNE final.
        fichierLog      : Contient le nom du fichier journal d'ex�cution.
        cmd             : Contient la commande d'�x�cution de la cr�ation du MNE du bassin trait�.
        
        Valeurs de retour:
        -----------------
        
        """
        #Traiter tous les �l�ments d'identifiant de d�coupage s�lectionn�s
        arcpy.AddMessage("- Traiter tous les �l�ments du FeatureLayer : " + featureLayer)
        
        #Cr�er le curseur pour la recherche
        cursor = arcpy.SearchCursor(featureLayer)
        
        #Extraire le premier �l�ment
        row = cursor.next()
        
        #traiter tant qu'il y aura des �l�ments
        while row:
            #D�finir l'identifiant trait�
            identifiant = str(row.getValue(attributIdentifiant))

            #D�finir la g�om�trie
            geometrie = row.getValue("SHAPE")
            
            #Afficher le message de cr�ation du MNE du bassin trait�
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Cr�er le MNE du bassin : %s ..." %identifiant)
            
            #D�finir les fichiers
            FichierShp = repertoireSortie + "\\" + identifiant + ".shp"
            FichierTmp = repertoireSortie + "\\" + identifiant + "_tmp.tif"
            FichierTif = repertoireSortie + "\\" + identifiant + ".tif"
            fichierLog = repertoireSortie + "\\" + identifiant + ".log"
 
            #Cr�er le fichier .shp de d�coupage du bassin trait�
            arcpy.AddMessage("CopyFeatures_management(SHAPE, " + FichierShp + ")")
            arcpy.CopyFeatures_management(geometrie, FichierShp)
            
            #D�finir la commande de cr�ation du MNE du bassin trait�
            cmd = "%fme2015% \\\\dfscitsh\\cits\\EnvCits\\applications\\bdgrid\\pro\\fme\\PostgisRasterSpatialExtractor.fmw"
            cmd = cmd + " --IN_VECTOR_GEOMETRY " + FichierShp
            cmd = cmd + " --IN_VECTOR_SRID EPSG:4617 --IN_VECTOR_TYPE FILE"
            cmd = cmd + " --IN_POSTGIS_SERVER pghost --IN_POSTGIS_PORT 14095 --IN_POSTGIS_USERID postgis_view --IN_POSTGIS_PASSWORD bcg4view"
            cmd = cmd + " --IN_POSTGIS_DBNAME bcg_pro --IN_POSTGIS_SCHEMA gridcoverage_pgis --IN_POSTGIS_RASTER_TABLE_NAME gridcoverage_cdem75 --IN_POSTGIS_RASTER_ATT rast"
            cmd = cmd + " --OUT_RASTER_DIR " + repertoireSortie + " --OUT_RASTER_FILE " + identifiant + "_tmp.tif --OUT_RASTER_FORMAT GEOTIFF --OUT_RASTER_RES Best"
            cmd = cmd + " --LOG_FILE " + fichierLog
            
            #Afficher la commande de cr�ation du MNE du bassin trait�
            arcpy.AddMessage(cmd)
            
            try:
                #Ex�cuter la commande de cr�ation du MNE du bassin trait�
                message = subprocess.check_output(cmd, shell=True)
                
                 #Afficher le message
                arcpy.AddMessage(message)
                
                #Compression et cr�ation des statistiques lors de la copie
                arcpy.AddMessage("CopyRaster_management(" + FichierTmp + ", " + FichierTif + ")")
                arcpy.CopyRaster_management(FichierTmp, FichierTif)
                
                #D�truire le fichier temporaire
                arcpy.AddMessage("DELETE " + FichierTmp)
                os.remove(FichierTmp)
                
            except Exception, err:
                #Lire le fichier log contenant l'erreur
                #file = open(fichierLog, 'r')
                #Retourner l'erreur
                #raise ExceptionCreerMneBassin(file.read())
                arcpy.AddError("ERREUR : Cr�ation du MNE : " + identifiant)
            
            #extraire le prochain �l�ment
            row = cursor.next()
        
        # Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB") 
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        featureLayer        = ""
        attributIdentifiant = "DATASET_NAME"
        repertoireSortie    = "D:\MNE_BASSIN"

        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            featureLayer = sys.argv[1].upper()
            
        if len(sys.argv) > 2:
            attributIdentifiant = sys.argv[2].upper()
            
        if len(sys.argv) > 3:
            repertoireSortie = sys.argv[3]
        
        # D�finir l'objet
        oCreerMneBassin = CreerMneBassin()
        
        #Valider les param�tres obligatoires
        oCreerMneBassin.validerParamObligatoire(featureLayer, attributIdentifiant, repertoireSortie)
        
        # Ex�cuter le traitement
        oCreerMneBassin.executer(featureLayer, attributIdentifiant, repertoireSortie)
    
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