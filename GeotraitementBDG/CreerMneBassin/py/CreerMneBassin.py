#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : CreerMneBassin.py
# Auteur    : Michel Pothier
# Date      : 24 février 2016

"""
    Application qui permet de créer les MNEs des Bassin-Versant selon les éléments sélectionnés dans un FeatureLayer de découpage des Bassins-Versants.
    Le nom de l'identifiant est présent dans l'attribut d'identifiant spécifié du FeatureLayer.
    
    Paramètres d'entrée:
    --------------------
    featureLayer        OB      FeatureLayer contenant les identifiants sélectionnés des Bassins-Versants.
                                défaut = ""
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
                                défaut = DATASET_NAME
    repertoireSortie    OB      Répertoire de sortie dans lequel les MNEs des Bassin-Versants seront créés.
                                défaut = "D:\MNE_BASSIN"
    
    Paramètres de sortie:
    ---------------------
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)

#*******************************************************************************************
class ExceptionCreerMneBassin(Exception):
#*******************************************************************************************
    """
    Classe d'exception dérivée de la classe Exception pour gèrer un problème
    dans l'exécution du programme.
    
    Lors de l'instanciation, passez une chaîne de caractère en argument
    pour d'écrire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CreerMneBassin:
#*******************************************************************************************
    """
    Classe qui permet de créer les MNEs des Bassin-Versant selon les éléments sélectionnés
    dans un FeatureLayer de découpage des Bassins-Versants.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement.
        
        Paramètres:
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
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        featureLayer        : FeatureLayer contenant les identifiants sélectionnés des Bassins-Versants.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'élément.
        repertoireSortie    : Répertoire de sortie dans lequel les MNEs des Bassin-Versants seront créés.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(featureLayer) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'featureLayer')
        
        if (len(attributIdentifiant) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'attributIdentifiant')
        
        if (len(repertoireSortie) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'repertoireSortie')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, featureLayer, attributIdentifiant, repertoireSortie):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création des MNE de bassin correspondants aux éléments d'identifiant de découpage sélectionnés.
        
        Paramètres:
        ----------- 
        featureLayer        : FeatureLayer contenant les identifiants sélectionnés des Bassins-Versants.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'élément.
        repertoireSortie    : Répertoire de sortie dans lequel les MNEs des Bassin-Versants seront créés.
        
        Variables:
        ----------
        cursor          : Contient les éléments de découpage sélectionnés.
        row             : Contient un élément de découpage traité.
        identifiant     : Contient la valeur de l'identifiant de découpage d'un bassin traité.
        fichierShp      : Contient le nom du fichier contenant le polygone de découpage.
        fichierTmp      : Contient le nom du fichier Tif du MNE temporaire.
        fichierTif      : Contient le nom du fichier Tif du MNE final.
        fichierLog      : Contient le nom du fichier journal d'exécution.
        cmd             : Contient la commande d'éxécution de la création du MNE du bassin traité.
        
        Valeurs de retour:
        -----------------
        
        """
        #Traiter tous les éléments d'identifiant de découpage sélectionnés
        arcpy.AddMessage("- Traiter tous les éléments du FeatureLayer : " + featureLayer)
        
        #Créer le curseur pour la recherche
        cursor = arcpy.SearchCursor(featureLayer)
        
        #Extraire le premier élément
        row = cursor.next()
        
        #traiter tant qu'il y aura des éléments
        while row:
            #Définir l'identifiant traité
            identifiant = str(row.getValue(attributIdentifiant))

            #Définir la géométrie
            geometrie = row.getValue("SHAPE")
            
            #Afficher le message de création du MNE du bassin traité
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Créer le MNE du bassin : %s ..." %identifiant)
            
            #Définir les fichiers
            FichierShp = repertoireSortie + "\\" + identifiant + ".shp"
            FichierTmp = repertoireSortie + "\\" + identifiant + "_tmp.tif"
            FichierTif = repertoireSortie + "\\" + identifiant + ".tif"
            fichierLog = repertoireSortie + "\\" + identifiant + ".log"
 
            #Créer le fichier .shp de découpage du bassin traité
            arcpy.AddMessage("CopyFeatures_management(SHAPE, " + FichierShp + ")")
            arcpy.CopyFeatures_management(geometrie, FichierShp)
            
            #Définir la commande de création du MNE du bassin traité
            cmd = "%fme2015% \\\\dfscitsh\\cits\\EnvCits\\applications\\bdgrid\\pro\\fme\\PostgisRasterSpatialExtractor.fmw"
            cmd = cmd + " --IN_VECTOR_GEOMETRY " + FichierShp
            cmd = cmd + " --IN_VECTOR_SRID EPSG:4617 --IN_VECTOR_TYPE FILE"
            cmd = cmd + " --IN_POSTGIS_SERVER pghost --IN_POSTGIS_PORT 14095 --IN_POSTGIS_USERID postgis_view --IN_POSTGIS_PASSWORD bcg4view"
            cmd = cmd + " --IN_POSTGIS_DBNAME bcg_pro --IN_POSTGIS_SCHEMA gridcoverage_pgis --IN_POSTGIS_RASTER_TABLE_NAME gridcoverage_cdem75 --IN_POSTGIS_RASTER_ATT rast"
            cmd = cmd + " --OUT_RASTER_DIR " + repertoireSortie + " --OUT_RASTER_FILE " + identifiant + "_tmp.tif --OUT_RASTER_FORMAT GEOTIFF --OUT_RASTER_RES Best"
            cmd = cmd + " --LOG_FILE " + fichierLog
            
            #Afficher la commande de création du MNE du bassin traité
            arcpy.AddMessage(cmd)
            
            try:
                #Exécuter la commande de création du MNE du bassin traité
                message = subprocess.check_output(cmd, shell=True)
                
                 #Afficher le message
                arcpy.AddMessage(message)
                
                #Compression et création des statistiques lors de la copie
                arcpy.AddMessage("CopyRaster_management(" + FichierTmp + ", " + FichierTif + ")")
                arcpy.CopyRaster_management(FichierTmp, FichierTif)
                
                #Détruire le fichier temporaire
                arcpy.AddMessage("DELETE " + FichierTmp)
                os.remove(FichierTmp)
                
            except Exception, err:
                #Lire le fichier log contenant l'erreur
                #file = open(fichierLog, 'r')
                #Retourner l'erreur
                #raise ExceptionCreerMneBassin(file.read())
                arcpy.AddError("ERREUR : Création du MNE : " + identifiant)
            
            #extraire le prochain élément
            row = cursor.next()
        
        # Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB") 
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        featureLayer        = ""
        attributIdentifiant = "DATASET_NAME"
        repertoireSortie    = "D:\MNE_BASSIN"

        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            featureLayer = sys.argv[1].upper()
            
        if len(sys.argv) > 2:
            attributIdentifiant = sys.argv[2].upper()
            
        if len(sys.argv) > 3:
            repertoireSortie = sys.argv[3]
        
        # Définir l'objet
        oCreerMneBassin = CreerMneBassin()
        
        #Valider les paramètres obligatoires
        oCreerMneBassin.validerParamObligatoire(featureLayer, attributIdentifiant, repertoireSortie)
        
        # Exécuter le traitement
        oCreerMneBassin.executer(featureLayer, attributIdentifiant, repertoireSortie)
    
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