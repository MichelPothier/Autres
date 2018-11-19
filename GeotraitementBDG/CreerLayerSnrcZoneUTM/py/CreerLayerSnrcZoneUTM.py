#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : CreerLayerSnrcZoneUTM.py
# Auteur    : Michel Pothier
# Date      : 126 octobre 2016

"""
Outil qui permet de créer un Layer par Zone UTM contenant la classe de SNRC avec une requête correspondant à la sélection
pour lesquels les éléments d'une classe sont présents dans le SNRC.

    Paramètres d'entrées:
    ---------------------
    nomClasse           : Nom de la classe traité.
                          défaut=
    classeSNRC          : Nom de la FeatureClass contenant les éléments du découpage SNRC.
                          défaut=Database Connections\BDRS_PRO_BDG.sde\BDG_DBA.ges_Decoupage_SNRC50K_2
    requete             : Requête attributive utilisé pour chaque Layer de zone UTM créée.
                          Le mot clé [NOM_CLASSE] est remplacé par le paramètre du nom de la classe.
                          Le mot clé [ZONE_UTM] est remplacé par la zone UTM traité et varie de 7 à 22.
                          défaut=DATASET_NAME IN (SELECT IDENTIFIANT FROM TBL_STATISTIQUE_ELEMENT_SOMMET WHERE NOM_TABLE='[NOM_CLASSE]') AND ZONE_UTM=[ZONE_UTM]
    repTravail          : Nom du répertoire de travail dans lequel les Layers par zone UTM seront créés.
                          Un répertoire par classe traité sera créé s'il est absent.
                          défaut=D:\ValiderContraintes

    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du résultat de l'exécution du programme.
                  Ex: 0=Succès, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 

    Usage:
        CreerLayerSnrcZoneUTM.py nomClasse classeSNRC requete repTravail

    Exemple:
        CreerLayerSnrcZoneUTM.py PAT_BATIMENT_0
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerLayerSnrcZoneUTM.py 1125 2016-10-26 16:35:18Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules privés
import CompteSib

#*******************************************************************************************
class CreerLayerSnrcZoneUTM(object):
#*******************************************************************************************
    """
    Permet de créer un Layer par Zone UTM contenant la classe de SNRC avec une requête correspondant à la sélection
    pour lesquels les éléments d'une classe sont présents dans le SNRC.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer un Layer par Zone UTM contenant la classe de SNRC avec une requête correspondant à la sélection
        pour lesquels les éléments d'une classe sont présents dans le SNRC.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        # Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, nomClasse, classeSNRC, requete, repTravail):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        nomClasse           : Nom de la classe traité.
        classeSNRC          : Nom de la FeatureClass contenant les éléments du découpage SNRC.
        requete             : Requête attributive utilisé pour chaque Layer de zone UTM créée.
        repTravail          : Nom du répertoire de travail dans lequel les Layers par zone UTM seront créés.
 
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(nomClasse) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nomClasse')

        if (len(classeSNRC) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'classeSNRC')

        if (len(requete) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'requete')

        if (len(repTravail) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'repTravail')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, nomClasse, classeSNRC, requete, repTravail):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour créer un Layer par Zone UTM contenant la classe de SNRC avec une requête correspondant à la sélection
        pour lesquels les éléments d'une classe sont présents dans le SNRC.
        
        Paramètres:
        -----------
        nomClasse           : Nom de la classe traité.
        classeSNRC          : Nom de la FeatureClass contenant les éléments du découpage SNRC.
        requete             : Requête attributive utilisé pour chaque Layer de zone UTM créée.
        repTravail          : Nom du répertoire de travail dans lequel les Layers par zone UTM seront créés.
               
        Variables:
        ----------
        """
        
        #Forcer la destruction des fichiers de sortie
        arcpy.env.overwriteOutput = True
        
        #Traiter toutes les zone UTM
        for zoneUTM in range(7,23):
            #Afficher la zone UTM traitée
            arcpy.AddMessage(" ")
            arcpy.AddMessage("-Traitement de la zone UTM :" + str(zoneUTM))
            
            #Définir la requête par zone UTM
            requeteZoneUtm = requete.replace("[NOM_CLASSE]",nomClasse).replace("[ZONE_UTM]",str(zoneUTM))
            
            #Définir le nom du Layer des SNRC à traiter pour la zone UTM
            lyrDecoupage = "BDG_DBA.ges_Decoupage_SNRC50K_2" + "_" + str(zoneUTM) + ".lyr"
            
            #Process: Make Feature Layer
            arcpy.AddMessage('MakeFeatureLayer_management "' + classeSNRC + '" ' + requeteZoneUtm + '"')
            arcpy.MakeFeatureLayer_management(classeSNRC, lyrDecoupage, requeteZoneUtm)
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            #Process: Select Layer By Attribute
            arcpy.AddMessage("SelectLayerByAttribute_management " + lyrDecoupage + " NEW_SELECTION")
            arcpy.SelectLayerByAttribute_management(lyrDecoupage, "NEW_SELECTION")
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            #Process: Save To Layer File
            arcpy.AddMessage("SaveToLayerFile_management " + lyrDecoupage + " " + repTravail + "\\" + nomClasse + "\\" + lyrDecoupage)
            arcpy.SaveToLayerFile_management(lyrDecoupage, repTravail + "\\" + nomClasse + "\\" + lyrDecoupage)
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        nomClasse = ""
        classeSNRC = "Database Connections\BDRS_PRO_BDG.sde\BDG_DBA.ges_Decoupage_SNRC50K_2"
        requete = "DATASET_NAME IN (SELECT IDENTIFIANT FROM TBL_STATISTIQUE_ELEMENT_SOMMET WHERE NOM_TABLE='[NOM_CLASSE]') AND ZONE_UTM=[ZONE_UTM]"
        repTravail = "D:\ValiderContraintes"
        
        # Lecture des paramètres
        if len(sys.argv) > 1:
            nomClasse = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            if sys.argv[2] <> "#":
                classeSNRC = sys.argv[2]
        
        if len(sys.argv) > 3:
            if sys.argv[3] <> "#":
                requete = sys.argv[3]
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                repTravail = sys.argv[4]
        
        #Définir l'objet pour créer un Layer par Zone UTM.
        oCreerLayerSnrcZoneUTM = CreerLayerSnrcZoneUTM()
        
        #Valider les paramètres obligatoires
        oCreerLayerSnrcZoneUTM.validerParamObligatoire(nomClasse, classeSNRC, requete, repTravail)
        
        #Exécuter le traitement pour vcréer un Layer par Zone UTM.
        oCreerLayerSnrcZoneUTM.executer(nomClasse, classeSNRC, requete, repTravail)
    
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