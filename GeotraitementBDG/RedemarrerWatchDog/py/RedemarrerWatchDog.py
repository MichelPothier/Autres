#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""
Outil qui permet de redémarrer le traitement du WatchDog qui repart le serveur XmlRPC à toutes les 5 minutes s'il est arrêté.

Le fichier contient le statut du "watchdog" du serveur XML-RPC.

Le statut du "watchdog" est géré par l'extension du nom de ce fichier.
- xmlrpc_watchdog.on   -> Le "watchdog" est actif et tente de repartir le serveur XML-RPC s'il est inactif.
- xmlrpc_watchdog.off  -> Le "watchdog" est inactif et ne tente pas de repartir le serveur XML-RPC s'il est inactif.

Nom: RedemarrerWatchDog.py

Auteur: Michel Pothier         Date: 13 août 2015

Paramètres:
-----------
env         : Type d'environnement.

Classe:
-------
 Nom                            Description
 -----------------------------  --------------------------------------------------------------------
 RedemarrerWatchDog             Redémarrer le traitement du WatchDog.
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
    Redémarrer le traitement du WatchDog.
    
    Retour:
        ErrorLevel  Integer  Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour redémarrer le traitement du WatchDog.
        
        Paramètres:
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
        Exécuter le traitement pour redémarrer le traitement du WatchDog.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
               
        Variables:
        ----------
        repertoire  : Répertoire dans lequel se trouve les fichier du WatchDog.
        fichierOn   : Nom du fichier WatchDog lorsqu'il est actif.
        fichierOff  : Nom du fichier WatchDog lorsqu'il est désactif.
        """

        #Définir les répertoires par défaut
        repertoire = "S:\\applications\\gestion_bdg\\" + env + "\\Gestion_BDSpatiales\\xmlrpc\\"

        #Définir le nom du fichier WatchDog lorsqu'il est actif
        fichierOn = "xmlrpc_watchdog.on"
        
        #Définir le nom du fichier WatchDog lorsqu'il est désactif
        fichierOff = "xmlrpc_watchdog.off"
        
        #Vérifier si le fichier du WatchDog est déjà actif
        if os.path.exists(repertoire + fichierOn):
            #Renommer le fichier du WatchDog
            arcpy.AddMessage(" ")
            arcpy.AddWarning("- Le fichier du WatchDog est déjà en mode actif !")
            arcpy.AddWarning(repertoire + fichierOn)
            
        #Vérifier si le fichier du WatchDog désactif est présent
        elif os.path.exists(repertoire + fichierOff):
            #Renommer le fichier du WatchDog pour le mettre en mode actif
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Renommer le fichier du WatchDog pour le mettre en mode actif !")
            arcpy.AddMessage("RENAME " + repertoire + fichierOff + " " + repertoire + fichierOn)
            os.rename(repertoire + fichierOff, repertoire + fichierOn)
            
        #Si aucun fichier n'est présent
        else:
            #Afficher un message d'erreur
            arcpy.AddMessage(" ")
            arcpy.AddError("- Aucun fichier du WatchDog n'est présent !")
            arcpy.AddError("  Répertoire : " + repertoire)
            arcpy.AddError("  FichierOn  : " + fichierOn)
            arcpy.AddError("  FichierOff : " + fichierOff)
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "PRO"
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        # Définir l'objet pour redémarrer le traitement du WatchDog.
        oRedemarrerWatchDog = RedemarrerWatchDog()
        
        # Exécuter le traitement pour redémarrer le traitement du WatchDog.
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
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage(" ")
    arcpy.AddMessage("- Succès du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)