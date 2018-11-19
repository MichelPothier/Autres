#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""
Outil qui permet de red�marrer le traitement du WatchDog qui repart le serveur XmlRPC � toutes les 5 minutes s'il est arr�t�.

Le fichier contient le statut du "watchdog" du serveur XML-RPC.

Le statut du "watchdog" est g�r� par l'extension du nom de ce fichier.
- xmlrpc_watchdog.on   -> Le "watchdog" est actif et tente de repartir le serveur XML-RPC s'il est inactif.
- xmlrpc_watchdog.off  -> Le "watchdog" est inactif et ne tente pas de repartir le serveur XML-RPC s'il est inactif.

Nom: RedemarrerWatchDog.py

Auteur: Michel Pothier         Date: 13 ao�t 2015

Param�tres:
-----------
env         : Type d'environnement.

Classe:
-------
 Nom                            Description
 -----------------------------  --------------------------------------------------------------------
 RedemarrerWatchDog             Red�marrer le traitement du WatchDog.
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: RedemarrerWatchDog.py 1111 2016-06-15 19:51:31Z mpothier $"
#********************************************************************************************

# Importation des modules publics
import os, arcpy, traceback

#*******************************************************************************************
class RedemarrerWatchDog(object):
#*******************************************************************************************
    """
    Red�marrer le traitement du WatchDog.
    
    Retour:
        ErrorLevel  Integer  Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour red�marrer le traitement du WatchDog.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        
        """
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour red�marrer le traitement du WatchDog.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
               
        Variables:
        ----------
        repertoire  : R�pertoire dans lequel se trouve les fichier du WatchDog.
        fichierOn   : Nom du fichier WatchDog lorsqu'il est actif.
        fichierOff  : Nom du fichier WatchDog lorsqu'il est d�sactif.
        """

        #D�finir les r�pertoires par d�faut
        repertoire = "S:\\applications\\gestion_bdg\\" + env + "\\Gestion_BDSpatiales\\xmlrpc\\"

        #D�finir le nom du fichier WatchDog lorsqu'il est actif
        fichierOn = "xmlrpc_watchdog.on"
        
        #D�finir le nom du fichier WatchDog lorsqu'il est d�sactif
        fichierOff = "xmlrpc_watchdog.off"
        
        #V�rifier si le fichier du WatchDog est d�j� actif
        if os.path.exists(repertoire + fichierOn):
            #Renommer le fichier du WatchDog
            arcpy.AddMessage(" ")
            arcpy.AddWarning("- Le fichier du WatchDog est d�j� en mode actif !")
            arcpy.AddWarning(repertoire + fichierOn)
            
        #V�rifier si le fichier du WatchDog d�sactif est pr�sent
        elif os.path.exists(repertoire + fichierOff):
            #Renommer le fichier du WatchDog pour le mettre en mode actif
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Renommer le fichier du WatchDog pour le mettre en mode actif !")
            arcpy.AddMessage("RENAME " + repertoire + fichierOff + " " + repertoire + fichierOn)
            os.rename(repertoire + fichierOff, repertoire + fichierOn)
            
        #Si aucun fichier n'est pr�sent
        else:
            #Afficher un message d'erreur
            arcpy.AddMessage(" ")
            arcpy.AddError("- Aucun fichier du WatchDog n'est pr�sent !")
            arcpy.AddError("  R�pertoire : " + repertoire)
            arcpy.AddError("  FichierOn  : " + fichierOn)
            arcpy.AddError("  FichierOff : " + fichierOff)
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "PRO"
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        # D�finir l'objet pour red�marrer le traitement du WatchDog.
        oRedemarrerWatchDog = RedemarrerWatchDog()
        
        # Ex�cuter le traitement pour red�marrer le traitement du WatchDog.
        oRedemarrerWatchDog.executer(env)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddMessage(" ")
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage(" ")
    arcpy.AddMessage("- Succ�s du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)