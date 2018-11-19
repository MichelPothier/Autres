#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet de cr�er un fichier de configuration afin de permettre la connexion
   automatique aux comptes BDG.

   Ce programme utilise la classe utilitaire CompteBDG contenue dans le fichier CompteBDG.py.
   
Nom: ConnecterCompteBDG.py

Auteur: Michel Pothier         Date: 14 octobre 2014

Param�tres:
-----------
sEnv        : Type d'environnement correspondant au nom d'une base de donn�es.
              Correspond � une section dans le fichier de configuration.
UsagerBd    : Nom de l'usager de la base de donn�es pour lequel on d�sire se connecter.
MotPasseBd  : Mot de passe de l'usager de la base de donn�es pour lequel on d�sire se connecter.

Classe:
-------
 Nom                    Description
 ---------------------  --------------------------------------------------------------------
 CompteBDG              Permet la gestion des comptes BDG.

Retour:
-------
 ErrorLevel  Integer  Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ConnecterCompteBDG.py 1111 2016-06-15 19:51:31Z mpothier $"
#********************************************************************************************

# Importation des modules publics
import os, sys, arcpy, datetime, ConfigParser, cx_Oracle, traceback

# Importation des modules priv�s (Cits)
import  util_bd, CompteBDG

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        sEnv = "BDRS_PRO"
        sUsagerBd = ""
        sMotPasseBd = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            sEnv = sys.argv[1].upper()
        if len(sys.argv) > 2:
            sUsagerBd = sys.argv[2]
        if len(sys.argv) > 3:
            sMotPasseBd = sys.argv[3]
        
        # D�finir l'objet de gestion des comptes BDG.
        oCompteBDG = CompteBDG.CompteBDG()
        
        # Ex�cuter le traitement de connexion � un compte BDG via le fichier de configuration.
        oCompteBDG.ConnecterCompteBDG(sEnv, sUsagerBd, sMotPasseBd,)
    
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