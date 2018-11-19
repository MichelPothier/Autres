#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : ValiderRelationSelectID.py
# Auteur    : Michel Pothier
# Date      : 12 février 2015

"""
    Application qui permet de valider les données entre deux classes selon une requête spatiale pour tous les éléments de découpage sélectionnés.

    Paramètres d'entrée:
    --------------------
    env                     OB  Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    featureLayerDecoupage   OB  Nom du FeatureLayer contenant les éléments de découpage à valider.
                                défaut = "DECOUPAGE-SNRC(50K)"
    attributDecoupage       OB  Nom de l'attribut du FeatureLayer contenant l'identifiant de découpage à valider.
                                défaut = "DATASET_NAME"
    featureClassValider     OB  Nom de la FeatureClass à valider.
                                défaut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1"
    requeteClassValider     OB  Requête attributive utilisée de la classe à valider.
                                ATTENTION : Le text <DECOUPAGE> sera remplacé par la valeur de l'attribut de de découpage traité.
                                défaut = "DATASET_NAME='<DECOUPAGE>' AND NETWORK_FLOW_TYPE=2"
    relationSpatiale        OB  Relation spatiale pour effectuer la validation.
                                ATTENTION : Pour plus de détails, voir la documentation ESRI de "Select Layer By Location" dans "Data Management Tools - Layers and Tables Views".
                                défaut = "HAVE_THEIR_CENTER_IN"
    typeSelection           OB  Type de sélection appliqué sur le résultat obtenu de la relation spatiale.
                                REMOVE_FROM_SELECTION : Utilisé lorsque la relation spatiale entre les 2 classes est légale (bonne).
                                NEW_SELECTION : Utilisé lorsque la relation spatiale entre les 2 classes est illégale (mauvaise).
                                défaut = "REMOVE_FROM_SELECTION"
    featureClassRelation    OB  Nom de la FeatureClass en relation.
                                défaut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2"
    requeteClassRelation    OB  Requête attributive de la classe en relation.
                                ATTENTION : Le text <DECOUPAGE> sera remplacé par la valeur de l'attribut de de découpage traité.
                                défaut = "DATASET_NAME='<DECOUPAGE>'"
    repLayerErreur          OB  Nom du répertoire contenant les FeatureLayer des éléments en erreurs.
                                défaut = ""
    featureClassErreur      OP  Nom de la FeatureClass contenant les géométries des éléments en erreurs.
                                Si la FeatureClass est absente, elle sera créée.
                                défaut = ""
    
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
        ValiderRelationSelectID.py env featureLayerDecoupage attributDecoupage featureClassValider requeteClassValider relationSpatiale typeSelection featureClassRelation requeteClassRelation repLayerErreur [featureClassErreur]
    
    Exemple:
        ValiderRelationSelectID.py SIB_PRO "DECOUPAGE-SNRC(50K)" "DATASET_NAME" "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1" "DATASET_NAME='<DECOUPAGE>' AND NETWORK_FLOW_TYPE=2"
        HAVE_THEIR_CENTER_IN REMOVE_FROM_SELECTION "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2" DATASET_NAME='<DECOUPAGE>' D:\Travail #

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderRelationSelectID.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, traceback

#Importation des modules privés (Cits)
#import CompteSib

#*******************************************************************************************
class ValiderRelationSelectID:
#*******************************************************************************************
    """
    Permet de valider les données entre deux classes selon une requête spatiale pour tous les éléments de découpage sélectionnés.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les données entre deux classes selon une requête spatial pour tous les éléments de découpage sélectionnés.
        
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
    def validerParamObligatoire(self,env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env                     : Environnement de travail
        featureLayerDecoupage   : Nom du FeatureLayer contenant les éléments de découpage à valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de découpage à valider.
        featureClassValider     : Nom de la FeatureClass à valider.
        requeteClassValider     : Requête attributive utilisée de la classe à valider.
        relationSpatiale        : Relation spatiale pour effectuer la validation.
        typeSelection           : Type de sélection appliqué sur le résultat obtenu de la relation spatiale.
        featureClassRelation    : Nom de la FeatureClass en relation.
        requeteClassRelation    : Requête attributive de la classe en relation.
        repLayerErreur          : Nom du répertoire contenant les FeatureLayer des éléments en erreurs.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Valider la présence
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')
        
        #Valider la présence
        if (len(featureLayerDecoupage) == 0):
            raise Exception ('Paramètre obligatoire manquant: featureLayerDecoupage')
        
        #Valider la présence
        if (len(attributDecoupage) == 0):
            raise Exception ('Paramètre obligatoire manquant: attributDecoupage')
        
        #Valider la présence
        if (len(featureClassValider) == 0):
            raise Exception ('Paramètre obligatoire manquant: featureClassValider')
        
        #Valider la présence
        if (len(requeteClassValider) == 0):
            raise Exception ('Paramètre obligatoire manquant: requeteClassValider')
        
        #Valider la présence
        if (len(relationSpatiale) == 0):
            raise Exception ('Paramètre obligatoire manquant: relationSpatiale')
        
        #Valider la présence
        if (len(typeSelection) == 0):
            raise Exception ('Paramètre obligatoire manquant: typeSelection')
        
        #Valider la présence
        if (len(featureClassRelation) == 0):
            raise Exception ('Paramètre obligatoire manquant: featureClassRelation')
        
        #Valider la présence
        if (len(requeteClassRelation) == 0):
            raise Exception ('Paramètre obligatoire manquant: requeteClassRelation')
        
        #Valider la présence
        if (len(repLayerErreur) == 0):
            raise Exception ('Paramètre obligatoire manquant: repLayerErreur')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self,env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur,featureClassErreur):
    #-------------------------------------------------------------------------------------
        """
        Permet d'exécuter le traitement pour valider les données entre deux classes selon une requête spatiale pour tous les éléments de découpage sélectionnés.
        
        Paramètres:
        -----------
        env                     : Environnement de travail
        featureLayerDecoupage   : Nom du FeatureLayer contenant les éléments de découpage à valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de découpage à valider.
        featureClassValider     : Nom de la FeatureClass à valider.
        requeteClassValider     : Requête attributive utilisée de la classe à valider.
        relationSpatiale        : Relation spatiale pour effectuer la validation.
        typeSelection           : Type de sélection appliqué sur le résultat obtenu de la relation spatiale.
        featureClassRelation    : Nom de la FeatureClass en relation.
        requeteClassRelation    : Requête attributive de la classe en relation.
        repLayerErreur          : Nom du répertoire contenant les FeatureLayer des éléments en erreurs.
        featureClassErreur      : Nom de la FeatureClass contenant les géométries des éléments en erreurs.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Initialisation du nombre total d'erreurs
        nbErrTotal = 0
        
        #Vérifier si on doit écrire les erreurs dans une FeatureClass d'erreurs
        if len(featureClassErreur) > 0:
            #Message de vérification de la FeatureClass d'erreurs
            arcpy.AddMessage("- Vérifier la FeatureClass d'erreurs")
            
            #Extraire la desciption de la FeatureClass à valider
            desc = arcpy.Describe(featureClassValider)
            
            #Vérifier si la FeatureClass est présente
            if arcpy.Exists(featureClassErreur):
                #Message de vérification de la FeatureClass d'erreur
                arcpy.AddWarning("FeatureClass déjà présente : " + featureClassErreur)
                
                #Extraire la desciption de la FeaturClass d'erreurs
                descClsErr = arcpy.Describe(featureClassErreur)
                
                #Vérifier si le type de géométrie correspond
                if desc.shapeType <> descClsErr.shapeType:
                    #Retourner une exception
                    raise Exception ("Le type de géométrie entre la FeatureClass à valider et celle d'erreurs ne correspond pas : " + desc.shapeType + "<>" + descClsErr.shapeType)
            
            #Si elle est absente
            else:
                #Définir le nom de la classe
                baseName = os.path.basename(featureClassErreur)
                
                #Créer la FeatureClass d'erreurs
                arcpy.AddMessage("CreateFeatureclass_management " + featureClassErreur.replace(baseName,"") + " " + baseName + " " + desc.shapeType + " " + desc.spatialReference.name)
                arcpy.CreateFeatureclass_management(featureClassErreur.replace(baseName,""), baseName, desc.shapeType, spatial_reference=desc.spatialReference)
                arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            #Créer le curseur pour ajouter les éléments dans la FeatureClass d'erreurs
            cursor = arcpy.da.InsertCursor(featureClassErreur, ["SHAPE@"])
        
        #Forcer la destruction des fichiers de sortie
        arcpy.env.overwriteOutput = True
        
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
            
            #Message de validation du découpage
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Validation des données : " + attributDecoupage + "=" + decoupage)
            
            # Process: Make Feature Layer
            lyrErrName = decoupage + "_Erreur"
            arcpy.AddMessage("MakeFeatureLayer_management " + featureClassValider + " " + lyrErrName + " " + requeteClassValider.replace("<DECOUPAGE>",decoupage))
            arcpy.MakeFeatureLayer_management(featureClassValider, lyrErrName, requeteClassValider.replace("<DECOUPAGE>",decoupage))
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            # Process: Select Layer By Attribute
            arcpy.AddMessage("SelectLayerByAttribute_management " + lyrErrName + " NEW_SELECTION")
            arcpy.SelectLayerByAttribute_management(lyrErrName, "NEW_SELECTION")
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            # Process: Make Feature Layer (2)
            desc = arcpy.Describe(featureClassRelation)
            lyrName = desc.baseName.split(".")[-1]
            arcpy.AddMessage("MakeFeatureLayer_management " + featureClassRelation + " " + lyrName + " " + requeteClassRelation.replace("<DECOUPAGE>",decoupage))
            arcpy.MakeFeatureLayer_management(featureClassRelation, lyrName, requeteClassRelation.replace("<DECOUPAGE>",decoupage))
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            # Process: Select Layer By Location
            arcpy.AddMessage("SelectLayerByLocation_management " + lyrErrName + " " + relationSpatiale + " " + lyrName + " " + typeSelection)
            lyrErr = arcpy.SelectLayerByLocation_management(lyrErrName, relationSpatiale, lyrName, "", typeSelection)
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            #Initialiser le nombre d'erreurs
            nbErr = 0
            
            #Extraire la desciption du FeatureLayer d'erreurs
            descLyrErr = arcpy.Describe(lyrErr)
            
            #Vérifier la présence d'erreurs
            if len(descLyrErr.fidSet) > 0:
                #Définir le nombre d'erreurs
                nbErr = len(descLyrErr.fidSet.split(";"))
                nbErrTotal = nbErrTotal + nbErr
                
                #Mettre le featureLayer non-visible
                lyrErr.visible = False
                #Définir le nom du featureLayer à écrire sur disque
                featureLayerErreurSnrc = repLayerErreur + "\\" + lyrErrName
                
                #Vérifier si le FeatureLayer est déjà présent
                if os.path.exists(featureLayerErreurSnrc):
                    #Détruire le FeatureLayer
                    os.remove(featureLayerErreurSnrc)
                
                # Process: Save To Layer File
                arcpy.AddMessage("SaveToLayerFile_management " + lyrErrName + " " + featureLayerErreurSnrc)
                arcpy.SaveToLayerFile_management(lyrErrName, featureLayerErreurSnrc)
                arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
                
                #Vérifier si on doit écrire les erreurs dans une FeatureClass d'erreurs
                if len(featureClassErreur) > 0:
                    #Écriture des erreus dans la FeatureClass
                    arcpy.AddMessage("Écriture des erreurs dans : " + featureClassErreur)
                    #Traiter tous les éléments du FeatureLayer d'erreurs
                    for row in arcpy.SearchCursor(lyrErr):
                        #Extraire le OBJECTID
                        #arcpy.AddMessage(str(row.getValue("OBJECTID")))
                        
                        #Extraire la géométrie
                        geometrie = row.getValue("SHAPE")
                        
                        #Insérer l'élément dans la FeatureClass
                        cursor.insertRow([geometrie])
            
            #Afficher le nombre d'erreurs
            arcpy.AddMessage("Nombre d'erreurs : " + str(nbErr))
            
            #Extraire le prochain élément
            feature = cursorDecoupage.next()
            
        #Vérifier si on doit écrire les erreurs dans une FeatureClass d'erreurs
        if len(featureClassErreur) > 0:
            #Accepter les modifications
            del cursor
        
        #Afficher le nombre total d'erreurs
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Nombre total d'erreurs : " + str(nbErrTotal))
        arcpy.AddMessage(" ")
       
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env                     = "SIB_PRO"
        featureLayerDecoupage   = "DECOUPAGE-SNRC(50K)"
        attributDecoupage       = "DATASET_NAME"
        featureClassValider     = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1"
        requeteClassValider     = "DATASET_NAME='<DECOUPAGE>' AND NETWORK_FLOW_TYPE=2"
        relationSpatiale        = "HAVE_THEIR_CENTER_IN"
        typeSelection           = "REMOVE_FROM_SELECTION"
        featureClassRelation    = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2"
        requeteClassRelation    = "DATASET_NAME='<DECOUPAGE>'"
        repLayerErreur          = "D:\Travail"
        featureClassErreur      = ""
        console                 = False
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            featureLayerDecoupage = sys.argv[2]
        
        if len(sys.argv) > 3:
            attributDecoupage = sys.argv[3]
        
        if len(sys.argv) > 4:
            featureClassValider = sys.argv[4]
        
        if len(sys.argv) > 5:
            requeteClassValider = sys.argv[5]
        
        if len(sys.argv) > 6:
            relationSpatiale = sys.argv[6]
        
        if len(sys.argv) > 7:
            typeSelection = sys.argv[7]
        
        if len(sys.argv) > 8:
            featureClassRelation = sys.argv[8]
        
        if len(sys.argv) > 9:
            requeteClassRelation = sys.argv[9]

        if len(sys.argv) > 10:
            repLayerErreur = sys.argv[10]
        
        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                featureClassErreur = sys.argv[11]
        
        if len(sys.argv) > 12:
            if sys.argv[12] <> "#":
                console = sys.argv[12].upper() == "TRUE"
        
        #Vérifier si on exécute le programme dans une nouvelle console
        if console:
            #On exécute le programme dans une nouvelle console
            arcpy.AddMessage('start cmd /K C:\Python27\python.exe "' + sys.argv[0] + '" "' + sys.argv[1] + '" "' + sys.argv[2] + '" "' + sys.argv[3] + '" "' + sys.argv[4] + '" "' + sys.argv[5] + '" "' + sys.argv[6] + '" "' + sys.argv[7] + '" "' + sys.argv[8] + '" "' + sys.argv[9] + '" "' + sys.argv[10] + '" "' + sys.argv[11] + '"')
            os.system('start cmd /K C:\Python27\python.exe "' + sys.argv[0] + '" "' + sys.argv[1] + '" "' + sys.argv[2] + '" "' + sys.argv[3] + '" "' + sys.argv[4] + '" "' + sys.argv[5] + '" "' + sys.argv[6] + '" "' + sys.argv[7] + '" "' + sys.argv[8] + '" "' + sys.argv[9] + '" "' + sys.argv[10] + '" "' + sys.argv[11] + '"')
            
        #On exécute le programme normalement
        else:
            #Instanciation de la classe pour valider les données entre deux classes selon une requête spatiale pour tous les éléments de découpage sélectionnés.
            oValiderRelationSelectID = ValiderRelationSelectID()
            
            #Vérification de la présence des paramètres obligatoires
            arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
            oValiderRelationSelectID.validerParamObligatoire(env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur)
            
            #Exécuter le traitement pour valider les données entre deux classes selon une requête spatiale pour tous les éléments de découpage sélectionnés.
            arcpy.AddMessage("- Exécuter la validation des données")
            oValiderRelationSelectID.executer(env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur,featureClassErreur)
        
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