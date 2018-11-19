#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : ValiderFilamentaireListeSnrcBDG.py
# Auteur    : Michel Pothier
# Date      : 10 f�vrier 2015

"""
    Application qui permet de valider les donn�es filamentaires inf�r�s (NETWORK_FLOW_TYPE=2) qui se retrouvent sur la terre
    (pas inclut dans une r�gion hydrique) selon une liste de SNRC de la BDG.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    featureClass        OB      Nom de la FeatureClass Filamentaire inf�r� � valider dans la BDG.
                                d�faut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1"
    featureClassCompare OB      Nom de la FeatureClass utilis�e pour comparer.
                                d�faut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2"
    listeSnrc           OB      Liste des SNRC 50K � traiter dans la BDG.
                                La liste des SNRC permis correcpond � celle de la table F101_SN pour le produit BDG et l'�chelle 50000.
                                d�faut = ""
    repLayerErreur      OB      Nom du r�pertoire contenant les FeatureLayer des �l�ments en erreurs.
                                d�faut = ""
    featureClassErreur  OP      Nom de la FeatureClass contenant les g�om�tries des �l�ments en erreurs.
                                Si la FeatureClass est absente, elle sera cr��e.
                                d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel              : Code du r�sultat de l'ex�cution du programme.
                              (Ex: 0=Succ�s, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles.
    
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

#Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ValiderFilamentaireListeSnrcBDG:
#*******************************************************************************************
    """
    Permet de valider les donn�es.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les donn�es filamentaires inf�r�s.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        # D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, featureClass, featureClassCompare, listeSnrc, repLayerErreur):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        featureClass        : Nom de la FeatureClass � valider.
        featureClassCompare : Nom de la FeatureClass utilis�e pour comparer.
        listeSnrc           : Liste des SNRC � traiter.
        repLayerErreur      : Nom du FeatureLayer contenant les �l�ments en erreurs.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Valider la pr�sence
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')
        
        #Valider la pr�sence
        if (len(featureClass) == 0):
            raise Exception ('Param�tre obligatoire manquant: featureClass')
        
        #Valider la pr�sence
        if (len(featureClassCompare) == 0):
            raise Exception ('Param�tre obligatoire manquant: featureClassCompare')
        
        #Valider la pr�sence
        if (len(listeSnrc) == 0):
            raise Exception ('Param�tre obligatoire manquant: listeSnrc')
        
        #Valider la pr�sence
        if (len(repLayerErreur) == 0):
            raise Exception ('Param�tre obligatoire manquant: repLayerErreur')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, featureClass, featureClassCompare, listeSnrc, repLayerErreur, featureClassErreur):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traitement pour valider les donn�es filamentaires inf�r�s.
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        featureClass        : Nom de la FeatureClass � valider.
        featureClassCompare : Nom de la FeatureClass utilis�e pour comparer.
        listeSnrc           : Liste des SNRC � traiter.
        repLayerErreur      : Nom du FeatureLayer contenant les �l�ments en erreurs.
        featureClassErreur  : Nom de la FeatureClass � cr�er et contenant les g�om�tries des �l�ments en erreurs.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Initialisation du nombre total d'erreurs
        nbErrTotal = 0
        
        #V�rifier si on doit �crire les erreurs dans une FeatureClass d'erreurs
        if len(featureClassErreur) > 0:
            #Message de v�rification de la FeatureClass d'erreurs
            arcpy.AddMessage("- V�rifier la FeatureClass d'erreurs")
            
            #Extraire la desciption de la FeatureClass � valider
            desc = arcpy.Describe(featureClass)
            
            #V�rifier si la FeatureClass est pr�sente
            if arcpy.Exists(featureClassErreur):
                #Message de v�rification de la FeatureClass d'erreur
                arcpy.AddWarning("FeatureClass d�j� pr�sente")
                
                #Extraire la desciption de la FeaturClass d'erreurs
                descClsErr = arcpy.Describe(featureClassErreur)
                
                #V�rifier si le type de g�om�trie correspond
                if desc.shapeType <> descClsErr.shapeType:
                    #Retourner une exception
                    raise Exception ("Le type de g�om�trie entre la FeatureClass � valider et celle d'erreurs ne correspond pas : " + desc.shapeType + "<>" + descClsErr.shapeType)
            
            #Si elle est absente
            else:
                #D�finir le nom de la classe
                baseName = os.path.basename(featureClassErreur)
                
                #Cr�er la FeatureClass d'erreurs
                arcpy.AddMessage("CreateFeatureclass_management " + featureClassErreur.replace(baseName,"") + " " + baseName + " " + desc.shapeType + " " + desc.spatialReference.name)
                arcpy.CreateFeatureclass_management(featureClassErreur.replace(baseName,""), baseName, desc.shapeType, spatial_reference=desc.spatialReference)
                arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            #Cr�er le curseur pour ajouter les �l�ments dans la FeatureClass d'erreurs
            cursor = arcpy.da.InsertCursor(featureClassErreur, ["SHAPE@"])
        
        #Forcer la destruction des fichiers de sortie
        arcpy.env.overwriteOutput = True
        
        #Traiter tous les SNRC
        for snrc in listeSnrc.split(","):
            #Message de validation d'un SNRC
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Validation des donn�es du SNRC : " + snrc)
            
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
            
            #V�rifier la pr�sence d'erreurs
            if len(descLyrErr.fidSet) > 0:
                #D�finir le nombre d'erreurs
                nbErr = len(descLyrErr.fidSet.split(";"))
                nbErrTotal = nbErrTotal + nbErr
                
                #Mettre le featureLayer non-visible
                lyrErr.visible = False
                #D�finir le nom du featureLayer � �crire sur disque
                featureLayerErreurSnrc = repLayerErreur + "\\" + lyrErrName
                
                #V�rifier si le FeatureLayer est d�j� pr�sent
                if os.path.exists(featureLayerErreurSnrc):
                    #D�truire le FeatureLayer
                    os.remove(featureLayerErreurSnrc)
                
                # Process: Save To Layer File
                arcpy.AddMessage("SaveToLayerFile_management " + lyrErrName + " " + featureLayerErreurSnrc)
                arcpy.SaveToLayerFile_management(lyrErrName, featureLayerErreurSnrc)
                arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
                
                #V�rifier si on doit �crire les erreurs dans une FeatureClass d'erreurs
                if len(featureClassErreur) > 0:
                    #�criture des erreus dans la FeatureClass
                    arcpy.AddMessage("�criture des erreurs dans : " + featureClassErreur)
                    #Traiter tous les �l�ments du FeatureLayer d'erreurs
                    for row in arcpy.SearchCursor(lyrErr):
                        #Extraire le OBJECTID
                        #arcpy.AddMessage(str(row.getValue("OBJECTID")))
                        
                        #Extraire la g�om�trie
                        geometrie = row.getValue("SHAPE")
                        
                        #Ins�rer l'�l�ment dans la FeatureClass
                        cursor.insertRow([geometrie])
            
            #Afficher le nombre d'erreurs
            arcpy.AddMessage("Nombre d'erreurs : " + str(nbErr))
            
        #V�rifier si on doit �crire les erreurs dans une FeatureClass d'erreurs
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env                 = "SIB_PRO"
        featureClass        = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1"
        featureClassCompare = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2"
        listeSnrc           = ""
        repLayerErreur      = ""
        featureClassErreur  = ""
        
        #Extraction des param�tres d'ex�cution
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
        
        #Instanciation de la classe pour valider les donn�es filamentaires inf�r�s.
        oValiderFilamentaireListeSnrcBDG = ValiderFilamentaireListeSnrcBDG()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oValiderFilamentaireListeSnrcBDG.validerParamObligatoire(env, featureClass, featureClassCompare, listeSnrc, repLayerErreur)
        
        #Ex�cuter le traitement pour valider les donn�es filamentaires inf�r�s.
        arcpy.AddMessage("- Ex�cuter la validation des donn�es")
        oValiderFilamentaireListeSnrcBDG.executer(env, featureClass, featureClassCompare, listeSnrc, repLayerErreur, featureClassErreur)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)