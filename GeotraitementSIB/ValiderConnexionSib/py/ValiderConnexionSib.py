#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ValiderConnexion.py
# Auteur    : Michel Pothier
# Date      : 25 novembre 2014

"""
    Outil qui permet la validation de toutes les connexions SIB contenu dans le 
    fichier de configuration.    

    Paramètres:
    -----------
    Aucun
     
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ValiderConnexion.py
        
    Exemple:
        ValiderConnexion.py
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderConnexionSib.py 2057 2016-06-15 21:03:15Z mpothier $"
#********************************************************************************************

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés
import CompteSib

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        # Définir l'objet de gestion des comptes Sib.
        oCompteSib = CompteSib.CompteSib()
        
        # Exécuter le traitement de validation des connexions contenue dans le fichier de configuration.
        oCompteSib.ValiderConnexionSib()
    
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