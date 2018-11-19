#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : DemonTestServeurXmlRpc.py
# Auteur    : Michel Pothier
# Date      : 06 novembre 2014

"""
Outil qui permet de tester si le serveur xml-rpc est actif et fonctionnel.

Param�tres d'entr�e:
--------------------
env     OB      type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV]
                d�faut = BDRS_PRO

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG, xmlrpclib
import util_ressources
import ssl
from util_config import Config

#*******************************************************************************************
class DemonTestServeurXmlRpc(object):
#*******************************************************************************************
    """
    Relancer la livraison des donn�es BDG.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour relancer la livraison des donn�es BDG.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        # Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def extraireValeurParametre(self, bd_ressources, ressource, parametre):
    #-------------------------------------------------------------------------------------
        """
            M�thode permettant d'extraire la valeur d'un param�tre de la BD ressources
            tout en tenant compte des erreurs.
               
            Param�tres:
            ressource                   Nom de la ressource
            parametre                   Param�tre pour lequel on d�sire conna�tre
                                        la valeur
               
            Valeur de retour:
                La valeur du param�tre extrait de la BD ressources.
        """

        valeur_de_retour = bd_ressources.extraireValeurParam(ressource, parametre)
        if valeur_de_retour[0:5] == "ERROR":
            raise Exception(1, "La BD ressources n'a pas de valeur pour le param�tre �%s� de la ressource �%s�" % (parametre, ressource))
            
        return valeur_de_retour
    
    #-------------------------------------------------------------------------------------
    def executer(self, sEnv):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour tester le serveur Xml-Rpc.
        
        Param�tres:
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
        
        #Ouverture de la BD ressource et lecture des valeurs de param�tre
        arcpy.AddMessage("- Ouverture de la BD des ressources")
        bd_ressources = util_ressources.Ressources(sEnv, config.COMPTE_BDG_RESS, config.PASS_BDG_RESS)
        bd_ressources.open()
        
        #Extraction des param�tres de connexion au serveur Xml-Rpc
        arcpy.AddMessage("- Extraction des param�tres de connexion au serveur Xml-Rpc")
        ressource = "CONNEXION_SERVICE_SIGBDSP"
        parametre = "HOST"
        host = self.extraireValeurParametre(bd_ressources, ressource, parametre)
        parametre = "PORT"
        port = self.extraireValeurParametre(bd_ressources, ressource, parametre)
        
        #Connexion au serveur Xml-Rpc. Selon la version de python, les param�tres de connexion sont diff�rents
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
        # De toute fa�on ce n'est que l'ex�cution du service et la connectivit� � la base de donn�es ORACLE (via le service) qui sont v�rifi�es
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
        
        #D�finir l'objet pour tester le serveur Xml-Rpc.
        oDemonTestServeurXmlRpc = DemonTestServeurXmlRpc()
        
        #Ex�cuter le traitement pour tester le serveur Xml-Rpc.
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
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage(" ")
    arcpy.AddMessage("- Succ�s du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)