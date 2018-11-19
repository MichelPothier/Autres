#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ValiderConnexionBDG.py
# Auteur    : Michel Pothier
# Date      : 03 d�cembre 2014

"""
    Outil qui permet la validation de toutes les connexions BDG contenu dans le fichier de configuration.    

    Param�tres:
    -----------
    Aucun
     
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        # D�finir l'objet de gestion des comptes BDG.
        oCompteBDG = CompteBDG.CompteBDG()
        
        # Ex�cuter le traitement de validation des connexions contenue dans le fichier de configuration.
        oCompteBDG.ValiderConnexionBDG()
    
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