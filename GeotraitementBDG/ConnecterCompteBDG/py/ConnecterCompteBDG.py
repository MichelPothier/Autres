#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet de créer un fichier de configuration afin de permettre la connexion
   automatique aux comptes BDG.

   Ce programme utilise la classe utilitaire CompteBDG contenue dans le fichier CompteBDG.py.
   
Nom: ConnecterCompteBDG.py

Auteur: Michel Pothier         Date: 14 octobre 2014

Paramètres:
-----------
sEnv        : Type d'environnement correspondant au nom d'une base de données.
              Correspond à une section dans le fichier de configuration.
UsagerBd    : Nom de l'usager de la base de données pour lequel on désire se connecter.
MotPasseBd  : Mot de passe de l'usager de la base de données pour lequel on désire se connecter.

Classe:
-------
 Nom                    Description
 ---------------------  --------------------------------------------------------------------
 CompteBDG              Permet la gestion des comptes BDG.

Retour:
-------
 ErrorLevel  Integer  Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ConnecterCompteBDG.py 1111 2016-06-15 19:51:31Z mpothier $"
#********************************************************************************************

# Importation des modules publics
import os, sys, arcpy, datetime, ConfigParser, cx_Oracle, traceback

# Importation des modules privés (Cits)
import  util_bd, CompteBDG

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        sEnv = "BDRS_PRO"
        sUsagerBd = ""
        sMotPasseBd = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            sEnv = sys.argv[1].upper()
        if len(sys.argv) > 2:
            sUsagerBd = sys.argv[2]
        if len(sys.argv) > 3:
            sMotPasseBd = sys.argv[3]
        
        # Définir l'objet de gestion des comptes BDG.
        oCompteBDG = CompteBDG.CompteBDG()
        
        # Exécuter le traitement de connexion à un compte BDG via le fichier de configuration.
        oCompteBDG.ConnecterCompteBDG(sEnv, sUsagerBd, sMotPasseBd,)
    
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