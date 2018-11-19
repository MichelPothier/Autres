#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AfficherTraitementLivraisonLSF.py
# Auteur    : Michel Pothier
# Date      : 23 octobre 2014

"""
    Application qui permet d'afficher les traitements de livraison des donn�es BDG en cours d'ex�cution dans une queue LSF
    � partir d'une connexion SSH automatique nomm�e "lsf" sur le serveur Linux KIWI.

    Attention : il faut copier le fichier "C:\Windows\System32\plink.exe" dans le r�pertoire "C:\Windows\SysWOW64".   
    
    Param�tres d'entr�e:
    --------------------
        usager              OB      Nom de l'usager pour lequel on veut voir les traitements en cours.
                                    "all" pour afficher tous les usagers, "username" pour seulement l'usager. 
                                    D�faut = "all"
        queue               OB      Nom de la queue LSF pour lequel on veut voir les traitements en cours.
                                    "#" pour afficher toutes les queues.
                                    D�faut = "qBDG_LIVRSDE"
        
    Param�tres de sortie:
    ---------------------
        Aucun
        
    Valeurs de retour:
        errorLevel          Code du r�sultat de l'ex�cution du programme.
                            (Ex: 0=Succ�s, 1=Erreur)

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
    Permet d'afficher les traitements de livraison des donn�es BDG en cours d'ex�cution dans une queue LSF.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher les traitements de livraison des donn�es BDG en cours d'ex�cution dans une queue LSF.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        Aucune
        
        """
        
        #D�finir les variable par d�faut
        self.fichierLog = os.environ['TEMP'] + "\\LSF_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".log"
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, usager):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        usager          : Nom de l'usager pour lequel on veut voir les traitements en cours.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """

        #Valider la pr�sence de l'environnement
        if (len(usager) == 0):
            raise Exception ('Param�tre obligatoire manquant: usager')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, usager, queue):
    #-------------------------------------------------------------------------------------
        """
        Permet d'afficher les traitements de livraison des donn�es BDG en cours d'ex�cution dans une queue LSF.
        
        Param�tres:
        -----------
        usager          : Nom de l'usager pour lequel on veut voir les traitements en cours.
        queue           : Nom de la queue LSF pour lequel on veut voir les traitements en cours.
        
        Retour:
        -------
        
        """
        
        #D�finir la commande pour afficher l'�tat de la queue LSF
        commande = "plink lsf bqueues -w -u " + usager + " " + queue
        
        #Afficher la commande pour afficher l'�tat de la queue LSF
        arcpy.AddMessage(" ")
        arcpy.AddMessage(commande)
        
        #Ex�cuter la commande pour afficher les traitements LSF
        message = subprocess.check_output(commande, shell=True)
        #err = os.system(commande + " > " + self.fichierLog)
        
        #Lire et afficher le fichier Log
        #arcpy.AddMessage(self.fichierLog)
        #log = open(self.fichierLog)
        #message = log.read()
        #log.close()
        
        #Afficher le r�sultat
        arcpy.AddMessage(message)
        
        #V�rifier si la queue est sp�cifi�e
        if queue == "":
            #D�finir la commande pour afficher les traitements LSF
            commande = "plink lsf bjobs -w -u " + usager
        else:
            #D�finir la commande pour afficher les traitements LSF
            commande = "plink lsf bjobs -w -u " + usager + " -q " + queue
        #Afficher la commande pour afficher les traitements LSF
        #arcpy.AddMessage(" ")
        arcpy.AddMessage(commande)
        
        #Ex�cuter la commande pour afficher les traitements LSF
        message = subprocess.check_output(commande, shell=True)
        #err = os.system(commande + " > " + self.fichierLog)
        
        #Lire et afficher le fichier Log
        #arcpy.AddMessage(self.fichierLog)
        #log = open(self.fichierLog)
        #message = log.read()
        #log.close()
        
        #Afficher le r�sultat
        arcpy.AddMessage(message)
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par d�faut
        usager  = "all"
        queue   = "qBDG_LIVRSDE"
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            usager = sys.argv[1]
        
        if len(sys.argv) > 2:
            queue = sys.argv[2].replace("#","")
        
        #Instanciation de la classe AfficherTraitementLivraisonLSF
        oAfficherTraitementLivraisonLSF = AfficherTraitementLivraisonLSF()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oAfficherTraitementLivraisonLSF.validerParamObligatoire(usager)
        
        #Ex�cuter le lanceur de service
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
    
    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage(" ")
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)