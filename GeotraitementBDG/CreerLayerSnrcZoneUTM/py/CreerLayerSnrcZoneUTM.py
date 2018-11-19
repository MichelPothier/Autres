#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : CreerLayerSnrcZoneUTM.py
# Auteur    : Michel Pothier
# Date      : 126 octobre 2016

"""
Outil qui permet de cr�er un Layer par Zone UTM contenant la classe de SNRC avec une requ�te correspondant � la s�lection
pour lesquels les �l�ments d'une classe sont pr�sents dans le SNRC.

    Param�tres d'entr�es:
    ---------------------
    nomClasse           : Nom de la classe trait�.
                          d�faut=
    classeSNRC          : Nom de la FeatureClass contenant les �l�ments du d�coupage SNRC.
                          d�faut=Database Connections\BDRS_PRO_BDG.sde\BDG_DBA.ges_Decoupage_SNRC50K_2
    requete             : Requ�te attributive utilis� pour chaque Layer de zone UTM cr��e.
                          Le mot cl� [NOM_CLASSE] est remplac� par le param�tre du nom de la classe.
                          Le mot cl� [ZONE_UTM] est remplac� par la zone UTM trait� et varie de 7 � 22.
                          d�faut=DATASET_NAME IN (SELECT IDENTIFIANT FROM TBL_STATISTIQUE_ELEMENT_SOMMET WHERE NOM_TABLE='[NOM_CLASSE]') AND ZONE_UTM=[ZONE_UTM]
    repTravail          : Nom du r�pertoire de travail dans lequel les Layers par zone UTM seront cr��s.
                          Un r�pertoire par classe trait� sera cr�� s'il est absent.
                          d�faut=D:\ValiderContraintes

    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  Ex: 0=Succ�s, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 

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

# Importation des modules priv�s
import CompteSib

#*******************************************************************************************
class CreerLayerSnrcZoneUTM(object):
#*******************************************************************************************
    """
    Permet de cr�er un Layer par Zone UTM contenant la classe de SNRC avec une requ�te correspondant � la s�lection
    pour lesquels les �l�ments d'une classe sont pr�sents dans le SNRC.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour cr�er un Layer par Zone UTM contenant la classe de SNRC avec une requ�te correspondant � la s�lection
        pour lesquels les �l�ments d'une classe sont pr�sents dans le SNRC.
        
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
    def validerParamObligatoire(self, nomClasse, classeSNRC, requete, repTravail):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        nomClasse           : Nom de la classe trait�.
        classeSNRC          : Nom de la FeatureClass contenant les �l�ments du d�coupage SNRC.
        requete             : Requ�te attributive utilis� pour chaque Layer de zone UTM cr��e.
        repTravail          : Nom du r�pertoire de travail dans lequel les Layers par zone UTM seront cr��s.
 
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(nomClasse) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nomClasse')

        if (len(classeSNRC) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'classeSNRC')

        if (len(requete) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'requete')

        if (len(repTravail) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'repTravail')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, nomClasse, classeSNRC, requete, repTravail):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour cr�er un Layer par Zone UTM contenant la classe de SNRC avec une requ�te correspondant � la s�lection
        pour lesquels les �l�ments d'une classe sont pr�sents dans le SNRC.
        
        Param�tres:
        -----------
        nomClasse           : Nom de la classe trait�.
        classeSNRC          : Nom de la FeatureClass contenant les �l�ments du d�coupage SNRC.
        requete             : Requ�te attributive utilis� pour chaque Layer de zone UTM cr��e.
        repTravail          : Nom du r�pertoire de travail dans lequel les Layers par zone UTM seront cr��s.
               
        Variables:
        ----------
        """
        
        #Forcer la destruction des fichiers de sortie
        arcpy.env.overwriteOutput = True
        
        #Traiter toutes les zone UTM
        for zoneUTM in range(7,23):
            #Afficher la zone UTM trait�e
            arcpy.AddMessage(" ")
            arcpy.AddMessage("-Traitement de la zone UTM :" + str(zoneUTM))
            
            #D�finir la requ�te par zone UTM
            requeteZoneUtm = requete.replace("[NOM_CLASSE]",nomClasse).replace("[ZONE_UTM]",str(zoneUTM))
            
            #D�finir le nom du Layer des SNRC � traiter pour la zone UTM
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        nomClasse = ""
        classeSNRC = "Database Connections\BDRS_PRO_BDG.sde\BDG_DBA.ges_Decoupage_SNRC50K_2"
        requete = "DATASET_NAME IN (SELECT IDENTIFIANT FROM TBL_STATISTIQUE_ELEMENT_SOMMET WHERE NOM_TABLE='[NOM_CLASSE]') AND ZONE_UTM=[ZONE_UTM]"
        repTravail = "D:\ValiderContraintes"
        
        # Lecture des param�tres
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
        
        #D�finir l'objet pour cr�er un Layer par Zone UTM.
        oCreerLayerSnrcZoneUTM = CreerLayerSnrcZoneUTM()
        
        #Valider les param�tres obligatoires
        oCreerLayerSnrcZoneUTM.validerParamObligatoire(nomClasse, classeSNRC, requete, repTravail)
        
        #Ex�cuter le traitement pour vcr�er un Layer par Zone UTM.
        oCreerLayerSnrcZoneUTM.executer(nomClasse, classeSNRC, requete, repTravail)
    
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