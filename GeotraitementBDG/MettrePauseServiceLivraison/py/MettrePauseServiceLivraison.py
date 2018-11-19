#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : MettrePauseLivraison.py
# Auteur    : Michel Pothier
# Date      : 06 novembre 2014

"""
Outil qui permet de mettre à pause le service de livraison des données.

Paramètres d'entrée:
--------------------
env             OB      Type d'environnement [PRO/TST/DEV]
                        défaut = PRO
ty_produit      OB      Type de produit [BDG/GEOBASE]
                        défaut = BDG

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)
Usage:
    MettrePauseLivraison.py env ty_produit

Exemple:
    MettrePauseLivraison.py PRO BDG
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: MettrePauseServiceLivraison.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics 
import os, sys, arcpy, subprocess, traceback

#*******************************************************************************************
class MettrePauseLivraison(object):
#*******************************************************************************************
    """
    Mettre à pause le service de livraison.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour mettre à pause le service de livraison.
        
        Paramètres:
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
        Exécuter le traitement pour mettre à pause le service de livraison.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        ty_produit  : Type de produit.
               
        Variables:
        ----------

        """
        
        #Relancer la livraison
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Mettre à pause le service de livraison des données")
        cmd = "%python27% S:\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py "
        cmd = cmd + "PauseServiceLivraison --depot " + ty_produit + " --env " + env + " --password 123hiroshima"
        arcpy.AddMessage(cmd)
        message = subprocess.check_output(cmd, shell=True)
        arcpy.AddMessage(message)
        
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
        ty_produit = "BDG"

        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
            
        if len(sys.argv) > 2:
            if sys.argv[2] <> "#":
                ty_produit = sys.argv[2].upper()
        
        # Définir l'objet pour mettre à pause le service de livraison.
        oMettrePauseLivraison = MettrePauseLivraison()
        
        # Exécuter le traitement pour mettre à pause le service de livraison.
        oMettrePauseLivraison.executer(env, ty_produit)
    
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