#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : RedemarrerServiceLivraison.py
# Auteur    : Michel Pothier
# Date      : 06 novembre 2014

"""
Outil qui permet de red�marrer le service de livraison des donn�es.

Param�tres d'entr�e:
--------------------
env             OB      Type d'environnement [PRO/TST/DEV]
                        d�faut = PRO
ty_produit      OB      Type de produit [BDG/GEOBASE]
                        d�faut = BDG

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)
Usage:
    RedemarrerServiceLivraison.py env ty_produit

Exemple:
    RedemarrerServiceLivraison.py PRO BDG
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: RedemarrerServiceLivraison.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Identification des librairies utilisees 
import os, sys, arcpy, subprocess, traceback

#*******************************************************************************************
class RedemarrerServiceLivraison(object):
#*******************************************************************************************
    """
    Red�marrer le service de livraison.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour red�marrer le service de livraison.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------

        """

        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_produit):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour red�marrer le service de livraison.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        ty_produit  : Type de produit.
               
        Variables:
        ----------

        """
        
        #Relancer la livraison
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- red�marrer le service de livraison des donn�es")
        cmd = "%python27% S:\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py "
        cmd = cmd + "RedemarrerServiceLivraison --depot " + ty_produit + " --env " + env + " --password 123hiroshima"
        arcpy.AddMessage(cmd)
        message = subprocess.check_output(cmd, shell=True)
        arcpy.AddMessage(message)
        
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
        ty_produit = "BDG"

        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
            
        if len(sys.argv) > 2:
            if sys.argv[2] <> "#":
                ty_produit = sys.argv[2].upper()
        
        # D�finir l'objet pour red�marrer le service de livraison.
        oRedemarrerServiceLivraison = RedemarrerServiceLivraison()
        
        # Ex�cuter le traitement pour red�marrer le service de livraison.
        oRedemarrerServiceLivraison.executer(env, ty_produit)
    
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