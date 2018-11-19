#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : ValiderFilamentaireListeSnrcBDG.py
# Auteur    : Michel Pothier
# Date      : 10 février 2015

"""
    Application qui permet de valider les données filamentaires inférés (NETWORK_FLOW_TYPE=2) qui se retrouvent sur la terre
    (pas inclut dans une région hydrique) selon une liste de SNRC de la BDG.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    featureClass        OB      Nom de la FeatureClass Filamentaire inféré à valider dans la BDG.
                                défaut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1"
    featureClassCompare OB      Nom de la FeatureClass utilisée pour comparer.
                                défaut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2"
    listeSnrc           OB      Liste des SNRC 50K à traiter dans la BDG.
                                La liste des SNRC permis correcpond à celle de la table F101_SN pour le produit BDG et l'échelle 50000.
                                défaut = ""
    repLayerErreur      OB      Nom du répertoire contenant les FeatureLayer des éléments en erreurs.
                                défaut = ""
    featureClassErreur  OP      Nom de la FeatureClass contenant les géométries des éléments en erreurs.
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
        ValiderFilamentaireListeSnrcBDG.py env featureClass featureClassCompare listeSnrc repLayerErreur [featureClassErreur]
    
    Exemple:
        ValiderFilamentaireListeSnrcBDG.py SIB_PRO "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1" "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2" 021M07,021M08 

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderFilamentaireListeSnrcBDG.py 1011 2015-02-12 18:06:48Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy

#Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ValiderFilamentaireListeSnrcBDG:
#*******************************************************************************************
    """
    Permet de valider les données.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les données filamentaires inférés.
        
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
    def validerParamObligatoire(self, env, featureClass, featureClassCompare, listeSnrc, repLayerErreur):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        featureClass        : Nom de la FeatureClass à valider.
        featureClassCompare : Nom de la FeatureClass utilisée pour comparer.
        listeSnrc           : Liste des SNRC à traiter.
        repLayerErreur      : Nom du FeatureLayer contenant les éléments en erreurs.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Valider la présence
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')
        
        #Valider la présence
        if (len(featureClass) == 0):
            raise Exception ('Paramètre obligatoire manquant: featureClass')
        
        #Valider la présence
        if (len(featureClassCompare) == 0):
            raise Exception ('Paramètre obligatoire manquant: featureClassCompare')
        
        #Valider la présence
        if (len(listeSnrc) == 0):
            raise Exception ('Paramètre obligatoire manquant: listeSnrc')
        
        #Valider la présence
        if (len(repLayerErreur) == 0):
            raise Exception ('Paramètre obligatoire manquant: repLayerErreur')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, featureClass, featureClassCompare, listeSnrc, repLayerErreur, featureClassErreur):
    #-------------------------------------------------------------------------------------
        """
        Permet d'exécuter le traitement pour valider les données filamentaires inférés.
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        featureClass        : Nom de la FeatureClass à valider.
        featureClassCompare : Nom de la FeatureClass utilisée pour comparer.
        listeSnrc           : Liste des SNRC à traiter.
        repLayerErreur      : Nom du FeatureLayer contenant les éléments en erreurs.
        featureClassErreur  : Nom de la FeatureClass à créer et contenant les géométries des éléments en erreurs.
        
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
            desc = arcpy.Describe(featureClass)
            
            #Vérifier si la FeatureClass est présente
            if arcpy.Exists(featureClassErreur):
                #Message de vérification de la FeatureClass d'erreur
                arcpy.AddWarning("FeatureClass déjà présente")
                
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
        
        #Traiter tous les SNRC
        for snrc in listeSnrc.split(","):
            #Message de validation d'un SNRC
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Validation des données du SNRC : " + snrc)
            
            # Process: Make Feature Layer
            lyrErrName = snrc + "_Erreur"
            arcpy.AddMessage("MakeFeatureLayer_management " + featureClass + " " + lyrErrName + " DATASET_NAME='" + snrc + "' AND NETWORK_FLOW_TYPE=2")
            #arcpy.MakeFeatureLayer_management(featureClass, lyrErrName, "DATASET_NAME='" + snrc + "' AND NETWORK_FLOW_TYPE=2", "", "OBJECTID OBJECTID VISIBLE NONE;VALIDITY_DATE VALIDITY_DATE VISIBLE NONE;ACQUISITION_TECHNIQUE ACQUISITION_TECHNIQUE VISIBLE NONE;DATASET_NAME DATASET_NAME VISIBLE NONE;PLANIMETRIC_ACCURACY PLANIMETRIC_ACCURACY VISIBLE NONE;PROVIDER PROVIDER VISIBLE NONE;COMPLETELY_COVER COMPLETELY_COVER VISIBLE NONE;BDG_ID BDG_ID VISIBLE NONE;MEP_ID MEP_ID VISIBLE NONE;MD_ID MD_ID VISIBLE NONE;ZT_ID ZT_ID VISIBLE NONE;PERMANENCY PERMANENCY VISIBLE NONE;WATER_DEFINITION WATER_DEFINITION VISIBLE NONE;FLOW_DIRECTION FLOW_DIRECTION VISIBLE NONE;LEVEL_PRIORITY LEVEL_PRIORITY VISIBLE NONE;NETWORK_FLOW_TYPE NETWORK_FLOW_TYPE VISIBLE NONE;CODE_SPEC CODE_SPEC VISIBLE NONE;CD_ELEM_TOPO CD_ELEM_TOPO VISIBLE NONE;GEONAMEDB GEONAMEDB VISIBLE NONE;NAMEID_1 NAMEID_1 VISIBLE NONE;NAMEID_2 NAMEID_2 VISIBLE NONE;IDDATE IDDATE VISIBLE NONE;SHAPE SHAPE VISIBLE NONE;SHAPE.LEN SHAPE.LEN VISIBLE NONE")
            arcpy.MakeFeatureLayer_management(featureClass, lyrErrName, "DATASET_NAME='" + snrc + "' AND NETWORK_FLOW_TYPE=2")
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            # Process: Select Layer By Attribute
            arcpy.AddMessage("SelectLayerByAttribute_management " + lyrErrName + " NEW_SELECTION NETWORK_FLOW_TYPE=2")
            arcpy.SelectLayerByAttribute_management(lyrErrName, "NEW_SELECTION", "NETWORK_FLOW_TYPE=2")
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            # Process: Make Feature Layer (2)
            desc = arcpy.Describe(featureClassCompare)
            lyrName = desc.baseName.split(".")[-1]
            arcpy.AddMessage("MakeFeatureLayer_management " + featureClassCompare + " " + lyrName + " DATASET_NAME='" + snrc + "'")
            #arcpy.MakeFeatureLayer_management(featureClassCompare, lyrName, "DATASET_NAME='" + snrc + "'", "", "OBJECTID OBJECTID VISIBLE NONE;VALIDITY_DATE VALIDITY_DATE VISIBLE NONE;ACQUISITION_TECHNIQUE ACQUISITION_TECHNIQUE VISIBLE NONE;DATASET_NAME DATASET_NAME VISIBLE NONE;PLANIMETRIC_ACCURACY PLANIMETRIC_ACCURACY VISIBLE NONE;PROVIDER PROVIDER VISIBLE NONE;COMPLETELY_COVER COMPLETELY_COVER VISIBLE NONE;BDG_ID BDG_ID VISIBLE NONE;MEP_ID MEP_ID VISIBLE NONE;MD_ID MD_ID VISIBLE NONE;ZT_ID ZT_ID VISIBLE NONE;WATER_DEFINITION WATER_DEFINITION VISIBLE NONE;SHORELINE_WATER_LEVEL SHORELINE_WATER_LEVEL VISIBLE NONE;PERMANENCY PERMANENCY VISIBLE NONE;CODE_SPEC CODE_SPEC VISIBLE NONE;CD_ELEM_TOPO CD_ELEM_TOPO VISIBLE NONE;GEONAMEDB GEONAMEDB VISIBLE NONE;LAKEID_1 LAKEID_1 VISIBLE NONE;LAKEID_2 LAKEID_2 VISIBLE NONE;RIVID_1 RIVID_1 VISIBLE NONE;RIVID_2 RIVID_2 VISIBLE NONE;IDDATE IDDATE VISIBLE NONE;ISOLATED ISOLATED VISIBLE NONE;SHAPE SHAPE VISIBLE NONE;SHAPE.AREA SHAPE.AREA VISIBLE NONE;SHAPE.LEN SHAPE.LEN VISIBLE NONE")
            arcpy.MakeFeatureLayer_management(featureClassCompare, lyrName, "DATASET_NAME='" + snrc + "'")
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            # Process: Select Layer By Location
            arcpy.AddMessage("SelectLayerByLocation_management " + lyrErrName + " HAVE_THEIR_CENTER_IN " + lyrName + " REMOVE_FROM_SELECTION")
            lyrErr = arcpy.SelectLayerByLocation_management(lyrErrName, "HAVE_THEIR_CENTER_IN", lyrName, "", "REMOVE_FROM_SELECTION")
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
        env                 = "SIB_PRO"
        featureClass        = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1"
        featureClassCompare = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2"
        listeSnrc           = ""
        repLayerErreur      = ""
        featureClassErreur  = ""
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            featureClass = sys.argv[2]
        
        if len(sys.argv) > 3:
            featureClassCompare = sys.argv[3]
        
        if len(sys.argv) > 4:
            listeSnrc = sys.argv[4].replace(";",",")
        
        if len(sys.argv) > 5:
            repLayerErreur = sys.argv[5]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                featureClassErreur = sys.argv[6]
        
        #Instanciation de la classe pour valider les données filamentaires inférés.
        oValiderFilamentaireListeSnrcBDG = ValiderFilamentaireListeSnrcBDG()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oValiderFilamentaireListeSnrcBDG.validerParamObligatoire(env, featureClass, featureClassCompare, listeSnrc, repLayerErreur)
        
        #Exécuter le traitement pour valider les données filamentaires inférés.
        arcpy.AddMessage("- Exécuter la validation des données")
        oValiderFilamentaireListeSnrcBDG.executer(env, featureClass, featureClassCompare, listeSnrc, repLayerErreur, featureClassErreur)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)