#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : CreerFgdbSelectID.py
# Auteur    : Michel Pothier
# Date      : 25 février 2015

"""
    Application qui permet de créer les FGDB de travail pour chaque identifiant sélectionné dans la classe de découpage.
    Pour chaque identifiant, les classes sélectionnées et leurs éléments seront copiés dans la FGDB.

    Paramètres d'entrée:
    --------------------
    featureLayerDecoupage   OB  Nom du FeatureLayer contenant les éléments de découpage à valider.
                                défaut = "DECOUPAGE-SNRC(50K)"
    attributDecoupage       OB  Nom de l'attribut du FeatureLayer contenant l'identifiant de découpage à valider.
                                défaut = "DATASET_NAME"
    geodatabase             OB  Nom de la Géodatabase utiliser pour créer la FGDB.
                                défaut = "Database Connections\BDRS_PRO.sde"
    classe                  OB  Liste des noms de classe contenus dans la géodatabase à copier dans la FGDB.
                                défaut = <Toutes les classes présentent dans la géodatabase>
    repertoire              OB  Nom du répertoire de travail.
                                défaut = "D:\Travail"
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel              : Code du résultat de l'exécution du programme.
                              (Ex: 0=Succès, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles.
    
    Usage:
        CreerFgdbSelectID.py featureLayerDecoupage attributDecoupage geodatabase classe repertoire
    
    Exemple:
        CreerFgdbSelectID.py "DECOUPAGE-SNRC(50K)" "DATASET_NAME" "Database Connections\BDRS_PRO.sde" "BDG_DBA.NHN_HHYD_WATERBODY_2;BDG_DBA.NHN_HNET_NETWORK_LINEAR_FLOW_1" "D:\Travail"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerFgdbSelectID.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, traceback

#Importation des modules privés (Cits)
#import CompteSib

#*******************************************************************************************
class CreerFgdbSelectID:
#*******************************************************************************************
    """
    Permet de créer les FGDB de travail pour chaque identifiant sélectionné dans la classe de découpage.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer les FGDB de travail pour chaque identifiant sélectionné dans la classe de découpage.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        # Définir l'objet de gestion des comptes Sib.
        #self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        featureLayerDecoupage   : Nom du FeatureLayer contenant les éléments de découpage à valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de découpage à valider.
        geodatabase             : Nom de la Géodatabase utiliser pour créer la FGDB.
        classe                  : Liste des noms de classe contenus dans la géodatabase à copier dans la FGDB.
        repertoire              : Nom du répertoire de travail.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Valider la présence
        if (len(featureLayerDecoupage) == 0):
            raise Exception ('Paramètre obligatoire manquant: featureLayerDecoupage')
        
        #Valider la présence
        if (len(attributDecoupage) == 0):
            raise Exception ('Paramètre obligatoire manquant: attributDecoupage')
        
        #Valider la présence
        if (len(geodatabase) == 0):
            raise Exception ('Paramètre obligatoire manquant: geodatabase')
        
        #Valider la présence
        if (len(classe) == 0):
            raise Exception ('Paramètre obligatoire manquant: classe')
        
        #Valider la présence
        if (len(repertoire) == 0):
            raise Exception ('Paramètre obligatoire manquant: repertoire')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire):
    #-------------------------------------------------------------------------------------
        """
        Permet d'exécuter le traitement pour créer les FGDB de travail pour chaque identifiant sélectionné dans la classe de découpage.
        
        Paramètres:
        -----------
        featureLayerDecoupage   : Nom du FeatureLayer contenant les éléments de découpage à valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de découpage à valider.
        geodatabase             : Nom de la Géodatabase utiliser pour créer la FGDB.
        classe                  : Liste des noms de classe contenus dans la géodatabase à copier dans la FGDB.
        repertoire              : Nom du répertoire de travail.
        
        Retour:
        -------
        Aucun
        
        """
        #Définir le Workspace par défaut
        arcpy.env.workspace = geodatabase
        
        #Afficher le message pour traiter tous les éléments sélectionnés dans le FeatureLayer de découpage
        arcpy.AddMessage("- Traiter tous les éléments sélectionnés du FeatureLayer de découpage : " + featureLayerDecoupage)
        
        #Créer le curseur des éléments de découpage
        cursorDecoupage = arcpy.SearchCursor(featureLayerDecoupage)
        
        #Extraire le premier élément
        feature = cursorDecoupage.next()
        
        #Traiter tant qu'il y aura des éléments de découpage
        while feature:        
            #Définir le découpage traité
            decoupage = str(feature.getValue(attributDecoupage))
            
            #Afficher le message
            arcpy.AddMessage(" ")
            arcpy.AddMessage("arcpy.CreateFileGDB_management('" + repertoire + "', '" + decoupage + ".gdb')")
            #Création de la FGDB
            arcpy.CreateFileGDB_management(repertoire, decoupage + ".gdb")
            #Définir le nom complet de la Geodatabase
            fgdb = repertoire + "\\" + decoupage + ".gdb"
            
            #Copier toutes les FeatureClass de la Geodatabase vers la FGDB
            for featureClass in classe.split(","):
                #Définir le propriétaire par défaut
                proprietaire = ""
                #Vérifier si le propriétaire est présent dans le nom
                if "." in featureClass:
                    #Définir le propriétaire
                    proprietaire = featureClass.split(".")[0] + "."
                #Copier la featureClass dans la FGDB
                arcpy.AddMessage(" ")
                arcpy.AddMessage("arcpy.FeatureClassToFeatureClass_conversion('" + featureClass + "', '" + fgdb + "', '" + featureClass.replace(proprietaire, "") + "', " + attributDecoupage + "='" + decoupage + "')")
                arcpy.FeatureClassToFeatureClass_conversion(featureClass, fgdb, featureClass.replace(proprietaire, ""), attributDecoupage + "='" + decoupage + "'")
                #Afficher tous les messages sauf le premier
                for i in range(1,arcpy.GetMessageCount()):
                    arcpy.AddMessage(arcpy.GetMessage(i))
            
            #Afficher le message
            arcpy.AddMessage(" ")
            arcpy.AddMessage("arcpy.Compact_management('" + fgdb + "')")
            #Compression de la FGDB
            arcpy.Compact_management(fgdb)
            arcpy.AddMessage(arcpy.GetMessages())
            
            #Extraire le prochain élément
            feature = cursorDecoupage.next()
        
        #Détruire le curseur de découpage
        arcpy.AddMessage(" ")
        del cursorDecoupage
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        featureLayerDecoupage   = "DECOUPAGE-SNRC(50K)"
        attributDecoupage       = "DATASET_NAME"
        geodatabase             = "Database Connections\BDRS_PRO.sde"
        classe                  = ""
        repertoire              = "D:\Travail"
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            featureLayerDecoupage = sys.argv[1]
        
        if len(sys.argv) > 2:
            attributDecoupage = sys.argv[2]
        
        if len(sys.argv) > 3:
            geodatabase = sys.argv[3]
        
        if len(sys.argv) > 4:
            classe = sys.argv[4].upper().replace(";",",")

        if len(sys.argv) > 5:
            repertoire = sys.argv[5]
        
        #Instanciation de la classe pour créer les FGDB de travail.
        oCreerFgdbSelectID = CreerFgdbSelectID()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oCreerFgdbSelectID.validerParamObligatoire(featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire)
        
        #Exécuter le traitement pour créer les FGDB de travail.
        arcpy.AddMessage("- Exécuter la création des FGDB de travail")
        oCreerFgdbSelectID.executer(featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)