#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : ValiderRelationSelectID.py
# Auteur    : Michel Pothier
# Date      : 12 f�vrier 2015

"""
    Application qui permet de valider les donn�es entre deux classes selon une requ�te spatiale pour tous les �l�ments de d�coupage s�lectionn�s.

    Param�tres d'entr�e:
    --------------------
    env                     OB  Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    featureLayerDecoupage   OB  Nom du FeatureLayer contenant les �l�ments de d�coupage � valider.
                                d�faut = "DECOUPAGE-SNRC(50K)"
    attributDecoupage       OB  Nom de l'attribut du FeatureLayer contenant l'identifiant de d�coupage � valider.
                                d�faut = "DATASET_NAME"
    featureClassValider     OB  Nom de la FeatureClass � valider.
                                d�faut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hnet_Network_Linear_Flow_1"
    requeteClassValider     OB  Requ�te attributive utilis�e de la classe � valider.
                                ATTENTION : Le text <DECOUPAGE> sera remplac� par la valeur de l'attribut de de d�coupage trait�.
                                d�faut = "DATASET_NAME='<DECOUPAGE>' AND NETWORK_FLOW_TYPE=2"
    relationSpatiale        OB  Relation spatiale pour effectuer la validation.
                                ATTENTION : Pour plus de d�tails, voir la documentation ESRI de "Select Layer By Location" dans "Data Management Tools - Layers and Tables Views".
                                d�faut = "HAVE_THEIR_CENTER_IN"
    typeSelection           OB  Type de s�lection appliqu� sur le r�sultat obtenu de la relation spatiale.
                                REMOVE_FROM_SELECTION : Utilis� lorsque la relation spatiale entre les 2 classes est l�gale (bonne).
                                NEW_SELECTION : Utilis� lorsque la relation spatiale entre les 2 classes est ill�gale (mauvaise).
                                d�faut = "REMOVE_FROM_SELECTION"
    featureClassRelation    OB  Nom de la FeatureClass en relation.
                                d�faut = "Database Connections\BDRS_PRO.sde\BDG_DBA.nhn_hhyd_Waterbody_2"
    requeteClassRelation    OB  Requ�te attributive de la classe en relation.
                                ATTENTION : Le text <DECOUPAGE> sera remplac� par la valeur de l'attribut de de d�coupage trait�.
                                d�faut = "DATASET_NAME='<DECOUPAGE>'"
    repLayerErreur          OB  Nom du r�pertoire contenant les FeatureLayer des �l�ments en erreurs.
                                d�faut = ""
    featureClassErreur      OP  Nom de la FeatureClass contenant les g�om�tries des �l�ments en erreurs.
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

#Importation des modules priv�s (Cits)
#import CompteSib

#*******************************************************************************************
class ValiderRelationSelectID:
#*******************************************************************************************
    """
    Permet de valider les donn�es entre deux classes selon une requ�te spatiale pour tous les �l�ments de d�coupage s�lectionn�s.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les donn�es entre deux classes selon une requ�te spatial pour tous les �l�ments de d�coupage s�lectionn�s.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        # D�finir l'objet de gestion des comptes Sib.
        #self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self,env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env                     : Environnement de travail
        featureLayerDecoupage   : Nom du FeatureLayer contenant les �l�ments de d�coupage � valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de d�coupage � valider.
        featureClassValider     : Nom de la FeatureClass � valider.
        requeteClassValider     : Requ�te attributive utilis�e de la classe � valider.
        relationSpatiale        : Relation spatiale pour effectuer la validation.
        typeSelection           : Type de s�lection appliqu� sur le r�sultat obtenu de la relation spatiale.
        featureClassRelation    : Nom de la FeatureClass en relation.
        requeteClassRelation    : Requ�te attributive de la classe en relation.
        repLayerErreur          : Nom du r�pertoire contenant les FeatureLayer des �l�ments en erreurs.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Valider la pr�sence
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')
        
        #Valider la pr�sence
        if (len(featureLayerDecoupage) == 0):
            raise Exception ('Param�tre obligatoire manquant: featureLayerDecoupage')
        
        #Valider la pr�sence
        if (len(attributDecoupage) == 0):
            raise Exception ('Param�tre obligatoire manquant: attributDecoupage')
        
        #Valider la pr�sence
        if (len(featureClassValider) == 0):
            raise Exception ('Param�tre obligatoire manquant: featureClassValider')
        
        #Valider la pr�sence
        if (len(requeteClassValider) == 0):
            raise Exception ('Param�tre obligatoire manquant: requeteClassValider')
        
        #Valider la pr�sence
        if (len(relationSpatiale) == 0):
            raise Exception ('Param�tre obligatoire manquant: relationSpatiale')
        
        #Valider la pr�sence
        if (len(typeSelection) == 0):
            raise Exception ('Param�tre obligatoire manquant: typeSelection')
        
        #Valider la pr�sence
        if (len(featureClassRelation) == 0):
            raise Exception ('Param�tre obligatoire manquant: featureClassRelation')
        
        #Valider la pr�sence
        if (len(requeteClassRelation) == 0):
            raise Exception ('Param�tre obligatoire manquant: requeteClassRelation')
        
        #Valider la pr�sence
        if (len(repLayerErreur) == 0):
            raise Exception ('Param�tre obligatoire manquant: repLayerErreur')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self,env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur,featureClassErreur):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traitement pour valider les donn�es entre deux classes selon une requ�te spatiale pour tous les �l�ments de d�coupage s�lectionn�s.
        
        Param�tres:
        -----------
        env                     : Environnement de travail
        featureLayerDecoupage   : Nom du FeatureLayer contenant les �l�ments de d�coupage � valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de d�coupage � valider.
        featureClassValider     : Nom de la FeatureClass � valider.
        requeteClassValider     : Requ�te attributive utilis�e de la classe � valider.
        relationSpatiale        : Relation spatiale pour effectuer la validation.
        typeSelection           : Type de s�lection appliqu� sur le r�sultat obtenu de la relation spatiale.
        featureClassRelation    : Nom de la FeatureClass en relation.
        requeteClassRelation    : Requ�te attributive de la classe en relation.
        repLayerErreur          : Nom du r�pertoire contenant les FeatureLayer des �l�ments en erreurs.
        featureClassErreur      : Nom de la FeatureClass contenant les g�om�tries des �l�ments en erreurs.
        
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
            desc = arcpy.Describe(featureClassValider)
            
            #V�rifier si la FeatureClass est pr�sente
            if arcpy.Exists(featureClassErreur):
                #Message de v�rification de la FeatureClass d'erreur
                arcpy.AddWarning("FeatureClass d�j� pr�sente : " + featureClassErreur)
                
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
        
        #Afficher le message pour traiter tous les �l�ments s�lectionn�s dans le FeatureLayer de d�coupage
        arcpy.AddMessage("- Traiter tous les �l�ments s�lectionn�s du FeatureLayer de d�coupage : " + featureLayerDecoupage)
        
        #Cr�er le curseur des �l�ments de d�coupage
        cursorDecoupage = arcpy.SearchCursor(featureLayerDecoupage)
        
        #Extraire le premier �l�ment
        feature = cursorDecoupage.next()
        
        #Traiter tant qu'il y aura des �l�ments de d�coupage
        while feature:        
            #D�finir le d�coupage trait�
            decoupage = str(feature.getValue(attributDecoupage))
            
            #Message de validation du d�coupage
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Validation des donn�es : " + attributDecoupage + "=" + decoupage)
            
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
            
            #Extraire le prochain �l�ment
            feature = cursorDecoupage.next()
            
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
        
        #Extraction des param�tres d'ex�cution
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
        
        #V�rifier si on ex�cute le programme dans une nouvelle console
        if console:
            #On ex�cute le programme dans une nouvelle console
            arcpy.AddMessage('start cmd /K C:\Python27\python.exe "' + sys.argv[0] + '" "' + sys.argv[1] + '" "' + sys.argv[2] + '" "' + sys.argv[3] + '" "' + sys.argv[4] + '" "' + sys.argv[5] + '" "' + sys.argv[6] + '" "' + sys.argv[7] + '" "' + sys.argv[8] + '" "' + sys.argv[9] + '" "' + sys.argv[10] + '" "' + sys.argv[11] + '"')
            os.system('start cmd /K C:\Python27\python.exe "' + sys.argv[0] + '" "' + sys.argv[1] + '" "' + sys.argv[2] + '" "' + sys.argv[3] + '" "' + sys.argv[4] + '" "' + sys.argv[5] + '" "' + sys.argv[6] + '" "' + sys.argv[7] + '" "' + sys.argv[8] + '" "' + sys.argv[9] + '" "' + sys.argv[10] + '" "' + sys.argv[11] + '"')
            
        #On ex�cute le programme normalement
        else:
            #Instanciation de la classe pour valider les donn�es entre deux classes selon une requ�te spatiale pour tous les �l�ments de d�coupage s�lectionn�s.
            oValiderRelationSelectID = ValiderRelationSelectID()
            
            #V�rification de la pr�sence des param�tres obligatoires
            arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
            oValiderRelationSelectID.validerParamObligatoire(env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur)
            
            #Ex�cuter le traitement pour valider les donn�es entre deux classes selon une requ�te spatiale pour tous les �l�ments de d�coupage s�lectionn�s.
            arcpy.AddMessage("- Ex�cuter la validation des donn�es")
            oValiderRelationSelectID.executer(env,featureLayerDecoupage,attributDecoupage,featureClassValider,requeteClassValider,relationSpatiale,typeSelection,featureClassRelation,requeteClassRelation,repLayerErreur,featureClassErreur)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)