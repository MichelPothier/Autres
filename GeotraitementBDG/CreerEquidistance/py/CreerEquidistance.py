#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : CreerEquidistance.py
# Auteur    : Michel Pothier
# Date      : 13 février 2018

"""
    Application qui permet de créer une table contenant les équidistances des courbes de niveau par identifiant.

    Paramètres d'entrée:
    --------------------
    geodatabase             OB  Nom de la Géodatabase contenant les classes pour lesquelles on veut créer une contrainte.
                                défaut = "Database Connections\BDRS_PRO_BDG_DBA.sde"
    tableEquidistance       OB  Nom de la table contenant les équidistances.
                                défaut = "TBL_EQUIDISTANCE_COURBE"
    fichierTxt              OB  Nom du fichier texte contenant les équidistances.
                                défaut = "D:\equidistance_courbe.txt"
                                
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
        CreerEquidistance.py geodatabase tableEquidistance fichierTxt
    
    Exemple:
        CreerEquidistance.py "Database Connections\BDRS_PRO_BDG_DBA.sde" "TBL_EQUIDISTANCE_COURBE" "D:\equidistance_courbe.txt"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerEquidistance.py 1160 2018-02-13 16:32:55Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, traceback

#Importation des modules privés (Cits)
#import CompteSib

#*******************************************************************************************
class CreerEquidistance:
#*******************************************************************************************
    """
    Permet de créer une table contenant les équidistances des courbes de niveau par identifiant.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer une table contenant les équidistances des courbes de niveau par identifiant.
        
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
    def validerParamObligatoire(self, geodatabase, tableEquidistance, fichierTxt):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        geodatabase             : Nom de la Géodatabase utiliser pour créer la FGDB.
        tableEquidistance       : Nom de la table contenant les équidistances.
        fichierTxt              : Nom du fichier texte contenant les équidistances.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Valider la présence
        if (len(geodatabase) == 0):
            raise Exception ('Paramètre obligatoire manquant: geodatabase')
        
        #Valider la présence
        if (len(tableEquidistance) == 0):
            raise Exception ('Paramètre obligatoire manquant: tableEquidistance')
        
        #Valider la présence
        if (len(fichierTxt) == 0):
            raise Exception ('Paramètre obligatoire manquant: fichierTxt')
         
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, geodatabase, tableEquidistance, fichierTxt):
    #-------------------------------------------------------------------------------------
        """
        Permet d'exécuter le traitement pour créer une table contenant les équidistances des courbes de niveau par identifiant.
        
        Paramètres:
        -----------
        geodatabase             : Nom de la Géodatabase utiliser pour créer la FGDB.
        tableEquidistance       : Nom de la table contenant les équidistances.
        fichierTxt              : Nom du fichier texte contenant les équidistances.
        
        Retour:
        -------
        Aucun
        
        """
        #Définir le Workspace par défaut
        arcpy.env.workspace = geodatabase
        
        #Afficher le message pour ajouter les équidistances dans la table
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les équidistances dans la table ...")
        
        #Créer le curseur pour ajouter les equidistances dans la table
        cursor = arcpy.da.InsertCursor(tableEquidistance, ["ETAMPE","DT_C","DT_M","IDENTIFIANT","ELEVATION_MIN","ELEVATION_MAX", "EQUIDISTANCE"])
        
        #Définir les valeurs l'étampe
        etampe = os.environ['username']
        #Définir la date
        date = str(datetime.datetime.now()).split(".")[0]
        
        #Lire le fichier texte
        fp = open(fichierTxt)
        lignes = fp.read().split("\n")
        fp.close()
        
        #Traiter toutes les lignes
        for ligne in lignes:
            #Définir l'information contenue dans la ligne
            info = ligne.split(",")
            
            #Afficher la contrainte
            arcpy.AddMessage("'" + etampe + "', '" + date + "', '" + date + "', '" + info[0] + "', " + info[1] + ", " + info[2] + ", " + info[3])
            
            #Insérer la contrainte dans la table
            cursor.insertRow([etampe, date, date, info[0], info[1], info[2], info[3]])
        
        #Afficher le nombre d'équidistances
        arcpy.AddMessage("Nombre total d'équidistances : " + str(len(lignes)))
        
        #Détruire le curseur et accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        del cursor
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        geodatabase         = r"Database Connections\BDRS_PRO_BDG_DBA.sde"
        tableEquidistance   = r"TBL_EQUIDISTANCE_COURBE"
        fichierTxt          = r"D:\equidistance.txt"
        
        #Extraction des paramètres d'exécution        
        if len(sys.argv) > 1:
            geodatabase = sys.argv[1]
        
        if len(sys.argv) > 2:
            tableEquidistance = sys.argv[2]
        
        if len(sys.argv) > 3:
            fichierTxt = sys.argv[3] 
        
        #Instanciation de la classe pour créer une table contenant les équidistances des courbes de niveau par identifiant.
        oCreerEquidistance = CreerEquidistance()
        
        #Vérification de la présence des paramètres obligatoires
        oCreerEquidistance.validerParamObligatoire(geodatabase, tableEquidistance, fichierTxt)
        
        #Exécuter le traitement pour créer une table contenant les équidistances des courbes de niveau par identifiant.
        oCreerEquidistance.executer(geodatabase, tableEquidistance, fichierTxt)
        
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