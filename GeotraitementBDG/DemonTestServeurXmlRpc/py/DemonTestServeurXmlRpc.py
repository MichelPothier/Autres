#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : DemonTestServeurXmlRpc.py
# Auteur    : Michel Pothier
# Date      : 06 novembre 2014

"""
Outil qui permet de tester si le serveur xml-rpc est actif et fonctionnel.

Paramètres d'entrée:
--------------------
env     OB      type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV]
                défaut = BDRS_PRO

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)
Usage:
    RelancerLivraisonBDG.py env no_job

Exemple:
    RelancerLivraisonBDG.py BDRS_PRO 54677
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DemonTestServeurXmlRpc.py 1155 2017-10-02 17:00:37Z jhuot $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, subprocess, traceback

# Importation des modules privés (Cits)
import CompteBDG, xmlrpclib
import util_ressources
import ssl
from util_config import Config

#*******************************************************************************************
class DemonTestServeurXmlRpc(object):
#*******************************************************************************************
    """
    Relancer la livraison des données BDG.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour relancer la livraison des données BDG.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        # Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def extraireValeurParametre(self, bd_ressources, ressource, parametre):
    #-------------------------------------------------------------------------------------
        """
            Méthode permettant d'extraire la valeur d'un paramètre de la BD ressources
            tout en tenant compte des erreurs.
               
            Paramètres:
            ressource                   Nom de la ressource
            parametre                   Paramètre pour lequel on désire connaître
                                        la valeur
               
            Valeur de retour:
                La valeur du paramètre extrait de la BD ressources.
        """

        valeur_de_retour = bd_ressources.extraireValeurParam(ressource, parametre)
        if valeur_de_retour[0:5] == "ERROR":
            raise Exception(1, "La BD ressources n'a pas de valeur pour le paramètre «%s» de la ressource «%s»" % (parametre, ressource))
            
        return valeur_de_retour
    
    #-------------------------------------------------------------------------------------
    def executer(self, sEnv):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour tester le serveur Xml-Rpc.
        
        Paramètres:
        -----------
        sEnv         : Type d'environnement.
        
        Variables:
        ----------

        """
        #Initialisation
        depot = ''
        
        # On va chercher le fichier config
        try:
            arcpy.AddMessage("- Ouverture du fichier de config")
            config = Config(depot, env=sEnv)
        except TypeError:
            raise Exception(1, "Impossible d'ouvrir le fichier config")
        
        #Ouverture de la BD ressource et lecture des valeurs de paramètre
        arcpy.AddMessage("- Ouverture de la BD des ressources")
        bd_ressources = util_ressources.Ressources(sEnv, config.COMPTE_BDG_RESS, config.PASS_BDG_RESS)
        bd_ressources.open()
        
        #Extraction des paramètres de connexion au serveur Xml-Rpc
        arcpy.AddMessage("- Extraction des paramètres de connexion au serveur Xml-Rpc")
        ressource = "CONNEXION_SERVICE_SIGBDSP"
        parametre = "HOST"
        host = self.extraireValeurParametre(bd_ressources, ressource, parametre)
        parametre = "PORT"
        port = self.extraireValeurParametre(bd_ressources, ressource, parametre)
        
        #Connexion au serveur Xml-Rpc. Selon la version de python, les paramètres de connexion sont différents
        arcpy.AddMessage("- Connexion au serveur Xml-Rpc")
        if sys.version_info >= (2,7,13):
            service = xmlrpclib.ServerProxy("https://%s:%s" % (host, port),
                                            context=ssl._create_unverified_context())
        else:
            service = xmlrpclib.ServerProxy("https://%s:%s" % (host, port))
        
        # On test si le serveur est disponible
        try:
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Tester si le serveur XML-RPC est actif")
            service.test_connection()
            arcpy.AddMessage("Le serveur XML-RPC est actif!")
        except:
            raise Exception,"Le service pour l'environnement '%s' n'est pas actif." % sEnv

        # On verifie si le serveur est fonctionnel
        # Appel du service obtenir_ser_reconcile_log
        # Le job_id 1424 existe dans les environnements TST et PRO
        # De toute façon ce n'est que l'exécution du service et la connectivité à la base de données ORACLE (via le service) qui sont vérifiées
        try:
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Tester si le serveur XML-RPC est fonctionnel")
            resultat = service.obtenir_ser_reconcile_log("BDG", "job_id=1424")
            arcpy.AddMessage("Le serveur XML-RPC est fonctionnel!")
            #arcpy.AddMessage(resultat)
        except:
            raise Exception,"Le serveur XML-RPC n'est pas fonctionnel!" % sEnv
        
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
        
        #Définir l'objet pour tester le serveur Xml-Rpc.
        oDemonTestServeurXmlRpc = DemonTestServeurXmlRpc()
        
        #Exécuter le traitement pour tester le serveur Xml-Rpc.
        oDemonTestServeurXmlRpc.executer(env)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddMessage(" ")
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage(" ")
    arcpy.AddMessage("- Succès du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)