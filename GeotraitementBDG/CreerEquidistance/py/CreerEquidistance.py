#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : CreerEquidistance.py
# Auteur    : Michel Pothier
# Date      : 13 f�vrier 2018

"""
    Application qui permet de cr�er une table contenant les �quidistances des courbes de niveau par identifiant.

    Param�tres d'entr�e:
    --------------------
    geodatabase             OB  Nom de la G�odatabase contenant les classes pour lesquelles on veut cr�er une contrainte.
                                d�faut = "Database Connections\BDRS_PRO_BDG_DBA.sde"
    tableEquidistance       OB  Nom de la table contenant les �quidistances.
                                d�faut = "TBL_EQUIDISTANCE_COURBE"
    fichierTxt              OB  Nom du fichier texte contenant les �quidistances.
                                d�faut = "D:\equidistance_courbe.txt"
                                
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
        CreerEquidistance.py geodatabase tableEquidistance fichierTxt
    
    Exemple:
        CreerEquidistance.py "Database Connections\BDRS_PRO_BDG_DBA.sde" "TBL_EQUIDISTANCE_COURBE" "D:\equidistance_courbe.txt"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerEquidistance.py 1160 2018-02-13 16:32:55Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, traceback

#Importation des modules priv�s (Cits)
#import CompteSib

#*******************************************************************************************
class CreerEquidistance:
#*******************************************************************************************
    """
    Permet de cr�er une table contenant les �quidistances des courbes de niveau par identifiant.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour cr�er une table contenant les �quidistances des courbes de niveau par identifiant.
        
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
    def validerParamObligatoire(self, geodatabase, tableEquidistance, fichierTxt):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        geodatabase             : Nom de la G�odatabase utiliser pour cr�er la FGDB.
        tableEquidistance       : Nom de la table contenant les �quidistances.
        fichierTxt              : Nom du fichier texte contenant les �quidistances.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Valider la pr�sence
        if (len(geodatabase) == 0):
            raise Exception ('Param�tre obligatoire manquant: geodatabase')
        
        #Valider la pr�sence
        if (len(tableEquidistance) == 0):
            raise Exception ('Param�tre obligatoire manquant: tableEquidistance')
        
        #Valider la pr�sence
        if (len(fichierTxt) == 0):
            raise Exception ('Param�tre obligatoire manquant: fichierTxt')
         
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, geodatabase, tableEquidistance, fichierTxt):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traitement pour cr�er une table contenant les �quidistances des courbes de niveau par identifiant.
        
        Param�tres:
        -----------
        geodatabase             : Nom de la G�odatabase utiliser pour cr�er la FGDB.
        tableEquidistance       : Nom de la table contenant les �quidistances.
        fichierTxt              : Nom du fichier texte contenant les �quidistances.
        
        Retour:
        -------
        Aucun
        
        """
        #D�finir le Workspace par d�faut
        arcpy.env.workspace = geodatabase
        
        #Afficher le message pour ajouter les �quidistances dans la table
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les �quidistances dans la table ...")
        
        #Cr�er le curseur pour ajouter les equidistances dans la table
        cursor = arcpy.da.InsertCursor(tableEquidistance, ["ETAMPE","DT_C","DT_M","IDENTIFIANT","ELEVATION_MIN","ELEVATION_MAX", "EQUIDISTANCE"])
        
        #D�finir les valeurs l'�tampe
        etampe = os.environ['username']
        #D�finir la date
        date = str(datetime.datetime.now()).split(".")[0]
        
        #Lire le fichier texte
        fp = open(fichierTxt)
        lignes = fp.read().split("\n")
        fp.close()
        
        #Traiter toutes les lignes
        for ligne in lignes:
            #D�finir l'information contenue dans la ligne
            info = ligne.split(",")
            
            #Afficher la contrainte
            arcpy.AddMessage("'" + etampe + "', '" + date + "', '" + date + "', '" + info[0] + "', " + info[1] + ", " + info[2] + ", " + info[3])
            
            #Ins�rer la contrainte dans la table
            cursor.insertRow([etampe, date, date, info[0], info[1], info[2], info[3]])
        
        #Afficher le nombre d'�quidistances
        arcpy.AddMessage("Nombre total d'�quidistances : " + str(len(lignes)))
        
        #D�truire le curseur et accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        del cursor
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        geodatabase         = r"Database Connections\BDRS_PRO_BDG_DBA.sde"
        tableEquidistance   = r"TBL_EQUIDISTANCE_COURBE"
        fichierTxt          = r"D:\equidistance.txt"
        
        #Extraction des param�tres d'ex�cution        
        if len(sys.argv) > 1:
            geodatabase = sys.argv[1]
        
        if len(sys.argv) > 2:
            tableEquidistance = sys.argv[2]
        
        if len(sys.argv) > 3:
            fichierTxt = sys.argv[3] 
        
        #Instanciation de la classe pour cr�er une table contenant les �quidistances des courbes de niveau par identifiant.
        oCreerEquidistance = CreerEquidistance()
        
        #V�rification de la pr�sence des param�tres obligatoires
        oCreerEquidistance.validerParamObligatoire(geodatabase, tableEquidistance, fichierTxt)
        
        #Ex�cuter le traitement pour cr�er une table contenant les �quidistances des courbes de niveau par identifiant.
        oCreerEquidistance.executer(geodatabase, tableEquidistance, fichierTxt)
        
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