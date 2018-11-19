#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : CreerFgdbSelectID.py
# Auteur    : Michel Pothier
# Date      : 25 f�vrier 2015

"""
    Application qui permet de cr�er les FGDB de travail pour chaque identifiant s�lectionn� dans la classe de d�coupage.
    Pour chaque identifiant, les classes s�lectionn�es et leurs �l�ments seront copi�s dans la FGDB.

    Param�tres d'entr�e:
    --------------------
    featureLayerDecoupage   OB  Nom du FeatureLayer contenant les �l�ments de d�coupage � valider.
                                d�faut = "DECOUPAGE-SNRC(50K)"
    attributDecoupage       OB  Nom de l'attribut du FeatureLayer contenant l'identifiant de d�coupage � valider.
                                d�faut = "DATASET_NAME"
    geodatabase             OB  Nom de la G�odatabase utiliser pour cr�er la FGDB.
                                d�faut = "Database Connections\BDRS_PRO.sde"
    classe                  OB  Liste des noms de classe contenus dans la g�odatabase � copier dans la FGDB.
                                d�faut = <Toutes les classes pr�sentent dans la g�odatabase>
    repertoire              OB  Nom du r�pertoire de travail.
                                d�faut = "D:\Travail"
    
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
        CreerFgdbSelectID.py featureLayerDecoupage attributDecoupage geodatabase classe repertoire
    
    Exemple:
        CreerFgdbSelectID.py "DECOUPAGE-SNRC(50K)" "DATASET_NAME" "Database Connections\BDRS_PRO.sde" "BDG_DBA.NHN_HHYD_WATERBODY_2;BDG_DBA.NHN_HNET_NETWORK_LINEAR_FLOW_1" "D:\Travail"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerFgdbSelectID.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, traceback

#Importation des modules priv�s (Cits)
#import CompteSib

#*******************************************************************************************
class CreerFgdbSelectID:
#*******************************************************************************************
    """
    Permet de cr�er les FGDB de travail pour chaque identifiant s�lectionn� dans la classe de d�coupage.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour cr�er les FGDB de travail pour chaque identifiant s�lectionn� dans la classe de d�coupage.
        
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
    def validerParamObligatoire(self, featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        featureLayerDecoupage   : Nom du FeatureLayer contenant les �l�ments de d�coupage � valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de d�coupage � valider.
        geodatabase             : Nom de la G�odatabase utiliser pour cr�er la FGDB.
        classe                  : Liste des noms de classe contenus dans la g�odatabase � copier dans la FGDB.
        repertoire              : Nom du r�pertoire de travail.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Valider la pr�sence
        if (len(featureLayerDecoupage) == 0):
            raise Exception ('Param�tre obligatoire manquant: featureLayerDecoupage')
        
        #Valider la pr�sence
        if (len(attributDecoupage) == 0):
            raise Exception ('Param�tre obligatoire manquant: attributDecoupage')
        
        #Valider la pr�sence
        if (len(geodatabase) == 0):
            raise Exception ('Param�tre obligatoire manquant: geodatabase')
        
        #Valider la pr�sence
        if (len(classe) == 0):
            raise Exception ('Param�tre obligatoire manquant: classe')
        
        #Valider la pr�sence
        if (len(repertoire) == 0):
            raise Exception ('Param�tre obligatoire manquant: repertoire')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traitement pour cr�er les FGDB de travail pour chaque identifiant s�lectionn� dans la classe de d�coupage.
        
        Param�tres:
        -----------
        featureLayerDecoupage   : Nom du FeatureLayer contenant les �l�ments de d�coupage � valider.
        attributDecoupage       : Nom de l'attribut du FeatureLayer contenant l'identifiant de d�coupage � valider.
        geodatabase             : Nom de la G�odatabase utiliser pour cr�er la FGDB.
        classe                  : Liste des noms de classe contenus dans la g�odatabase � copier dans la FGDB.
        repertoire              : Nom du r�pertoire de travail.
        
        Retour:
        -------
        Aucun
        
        """
        #D�finir le Workspace par d�faut
        arcpy.env.workspace = geodatabase
        
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
            
            #Afficher le message
            arcpy.AddMessage(" ")
            arcpy.AddMessage("arcpy.CreateFileGDB_management('" + repertoire + "', '" + decoupage + ".gdb')")
            #Cr�ation de la FGDB
            arcpy.CreateFileGDB_management(repertoire, decoupage + ".gdb")
            #D�finir le nom complet de la Geodatabase
            fgdb = repertoire + "\\" + decoupage + ".gdb"
            
            #Copier toutes les FeatureClass de la Geodatabase vers la FGDB
            for featureClass in classe.split(","):
                #D�finir le propri�taire par d�faut
                proprietaire = ""
                #V�rifier si le propri�taire est pr�sent dans le nom
                if "." in featureClass:
                    #D�finir le propri�taire
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
            
            #Extraire le prochain �l�ment
            feature = cursorDecoupage.next()
        
        #D�truire le curseur de d�coupage
        arcpy.AddMessage(" ")
        del cursorDecoupage
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        featureLayerDecoupage   = "DECOUPAGE-SNRC(50K)"
        attributDecoupage       = "DATASET_NAME"
        geodatabase             = "Database Connections\BDRS_PRO.sde"
        classe                  = ""
        repertoire              = "D:\Travail"
        
        #Extraction des param�tres d'ex�cution
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
        
        #Instanciation de la classe pour cr�er les FGDB de travail.
        oCreerFgdbSelectID = CreerFgdbSelectID()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oCreerFgdbSelectID.validerParamObligatoire(featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire)
        
        #Ex�cuter le traitement pour cr�er les FGDB de travail.
        arcpy.AddMessage("- Ex�cuter la cr�ation des FGDB de travail")
        oCreerFgdbSelectID.executer(featureLayerDecoupage, attributDecoupage, geodatabase, classe, repertoire)
        
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