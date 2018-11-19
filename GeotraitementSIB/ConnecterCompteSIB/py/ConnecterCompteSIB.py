#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet de créer un fichier de configuration afin de permettre la connexion
   automatique aux comptes SIB.

   Ce programme utilise la classe utilitaire CompteSib contenue dans le fichier CompteSib.py.
   
Nom: ConnecterCompteSIB.py

Auteur: Michel Pothier         Date: 6 octobre 2014

Paramètres:
-----------
sEnv         : Type d'environnement correspondant au nom d'une base de données.
              Correspond à une section dans le fichier de configuration.
UsagerBd    : Nom de l'usager de la base de données pour lequel on désire se connecter.
MotPasseBd  : Mot de passe de l'usager de la base de données pour lequel on désire se connecter.
UsagerSib   : Nom de l'usager SIB pour lequel on désire se connecter.
MotPasseSib : Mot de passe de l'usager SIB pour lequel on désire se connecter.

Classe:
-------
 Nom                    Description
 ---------------------  --------------------------------------------------------------------
 CompteSIB              Permet la gestion des comptes SIB.

Retour:
-------
 ErrorLevel  Integer  Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ConnecterCompteSIB.py 2057 2016-06-15 21:03:15Z mpothier $"
#********************************************************************************************

# Importation des modules publics 
import os, sys, arcpy, datetime, util_sib, ConfigParser, cx_Oracle, traceback

# Importation des modules privés
import CompteSib

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        sEnv = "SIB_PRO"
        sUsagerBd = ""
        sMotPasseBd = ""
        sUsagerSib = ""
        sMotPasseSib = ""
        
        # Lecture des paramètres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            sEnv = sys.argv[1].upper()
        if len(sys.argv) > 2:
            sUsagerBd = sys.argv[2]
        if len(sys.argv) > 3:
            sMotPasseBd = sys.argv[3]
        if len(sys.argv) > 4:
            sUsagerSib = sys.argv[4]
        if len(sys.argv) > 5:
            sMotPasseSib = sys.argv[5][:8]
        
        # Définir l'objet de gestion des comptes Sib.
        oCompteSib = CompteSib.CompteSib()
        
        # Exécuter le traitement de connexion à un compte SIB via le fichier de configuration.
        oCompteSib.ConnecterCompteSib(sEnv, sUsagerBd, sMotPasseBd, sUsagerSib, sMotPasseSib)
    
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