#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ValiderConnexionBDG.py
# Auteur    : Michel Pothier
# Date      : 03 décembre 2014

"""
    Outil qui permet la validation de toutes les connexions BDG contenu dans le fichier de configuration.    

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
        ValiderConnexionBDG.py
        
    Exemple:
        ValiderConnexionBDG.py
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderConnexionBDG.py 1111 2016-06-15 19:51:31Z mpothier $"
#********************************************************************************************

# Identification des librairies utilisees 
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        # Définir l'objet de gestion des comptes BDG.
        oCompteBDG = CompteBDG.CompteBDG()
        
        # Exécuter le traitement de validation des connexions contenue dans le fichier de configuration.
        oCompteBDG.ValiderConnexionBDG()
    
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