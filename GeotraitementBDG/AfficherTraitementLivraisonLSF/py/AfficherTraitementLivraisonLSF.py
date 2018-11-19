#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AfficherTraitementLivraisonLSF.py
# Auteur    : Michel Pothier
# Date      : 23 octobre 2014

"""
    Application qui permet d'afficher les traitements de livraison des données BDG en cours d'exécution dans une queue LSF
    à partir d'une connexion SSH automatique nommée "lsf" sur le serveur Linux KIWI.

    Attention : il faut copier le fichier "C:\Windows\System32\plink.exe" dans le répertoire "C:\Windows\SysWOW64".   
    
    Paramètres d'entrée:
    --------------------
        usager              OB      Nom de l'usager pour lequel on veut voir les traitements en cours.
                                    "all" pour afficher tous les usagers, "username" pour seulement l'usager. 
                                    Défaut = "all"
        queue               OB      Nom de la queue LSF pour lequel on veut voir les traitements en cours.
                                    "#" pour afficher toutes les queues.
                                    Défaut = "qBDG_LIVRSDE"
        
    Paramètres de sortie:
    ---------------------
        Aucun
        
    Valeurs de retour:
        errorLevel          Code du résultat de l'exécution du programme.
                            (Ex: 0=Succès, 1=Erreur)

    Usage:
        AfficherTraitementLivraisonLSF.py usager queue
        
    Exemple:
        AfficherTraitementLivraisonLSF.py mpothier qBDG_LIVRSDE
        AfficherTraitementLivraisonLSF.py all #
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherTraitementLivraisonLSF.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, time, arcpy, subprocess

#*******************************************************************************************
class AfficherTraitementLivraisonLSF:
#*******************************************************************************************
    """
    Permet d'afficher les traitements de livraison des données BDG en cours d'exécution dans une queue LSF.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher les traitements de livraison des données BDG en cours d'exécution dans une queue LSF.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        Aucune
        
        """
        
        #Définir les variable par défaut
        self.fichierLog = os.environ['TEMP'] + "\\LSF_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, usager):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        usager          : Nom de l'usager pour lequel on veut voir les traitements en cours.
        
        Retour:
        -------
        Exception s'il y a un problème
        """

        #Valider la présence de l'environnement
        if (len(usager) == 0):
            raise Exception ('Paramètre obligatoire manquant: usager')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, usager, queue):
    #-------------------------------------------------------------------------------------
        """
        Permet d'afficher les traitements de livraison des données BDG en cours d'exécution dans une queue LSF.
        
        Paramètres:
        -----------
        usager          : Nom de l'usager pour lequel on veut voir les traitements en cours.
        queue           : Nom de la queue LSF pour lequel on veut voir les traitements en cours.
        
        Retour:
        -------
        
        """
        
        #Définir la commande pour afficher l'état de la queue LSF
        commande = "plink lsf bqueues -w -u " + usager + " " + queue
        
        #Afficher la commande pour afficher l'état de la queue LSF
        arcpy.AddMessage(" ")
        arcpy.AddMessage(commande)
        
        #Exécuter la commande pour afficher les traitements LSF
        message = subprocess.check_output(commande, shell=True)
        #err = os.system(commande + " > " + self.fichierLog)
        
        #Lire et afficher le fichier Log
        #arcpy.AddMessage(self.fichierLog)
        #log = open(self.fichierLog)
        #message = log.read()
        #log.close()
        
        #Afficher le résultat
        arcpy.AddMessage(message)
        
        #Vérifier si la queue est spécifiée
        if queue == "":
            #Définir la commande pour afficher les traitements LSF
            commande = "plink lsf bjobs -w -u " + usager
        else:
            #Définir la commande pour afficher les traitements LSF
            commande = "plink lsf bjobs -w -u " + usager + " -q " + queue
        #Afficher la commande pour afficher les traitements LSF
        #arcpy.AddMessage(" ")
        arcpy.AddMessage(commande)
        
        #Exécuter la commande pour afficher les traitements LSF
        message = subprocess.check_output(commande, shell=True)
        #err = os.system(commande + " > " + self.fichierLog)
        
        #Lire et afficher le fichier Log
        #arcpy.AddMessage(self.fichierLog)
        #log = open(self.fichierLog)
        #message = log.read()
        #log.close()
        
        #Afficher le résultat
        arcpy.AddMessage(message)
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par défaut
        usager  = "all"
        queue   = "qBDG_LIVRSDE"
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            usager = sys.argv[1]
        
        if len(sys.argv) > 2:
            queue = sys.argv[2].replace("#","")
        
        #Instanciation de la classe AfficherTraitementLivraisonLSF
        oAfficherTraitementLivraisonLSF = AfficherTraitementLivraisonLSF()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oAfficherTraitementLivraisonLSF.validerParamObligatoire(usager)
        
        #Exécuter le lanceur de service
        arcpy.AddMessage("- Affichage des traitements LSF")
        oAfficherTraitementLivraisonLSF.executer(usager, queue)
        
    except Exception, err:
        #gestion de l'erreur
        arcpy.AddMessage(" ")
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #sortir avec une erreur
        sys.exit(1)
    
    #Sortie normale pour une exécution réussie
    arcpy.AddMessage(" ")
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)