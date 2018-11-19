#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : DetruireTraitementLivraisonLSF.py
# Auteur    : Michel Pothier
# Date      : 23 octobre 2014

"""
    Application qui permet de d�truire les traitements de livraison des donn�es BDG en cours d'ex�cution dans une queue LSF
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
                                    
         jobid              OB      Liste des jobid de LSF � d�truire.
                                    D�faut : ""
       
    Param�tres de sortie:
    ---------------------
        Aucun
        
    Valeurs de retour:
        errorLevel          Code du r�sultat de l'ex�cution du programme.
                            (Ex: 0=Succ�s, 1=Erreur)

    Usage:
        DetruireTraitementLivraisonLSF.py usager queue jobid
        
    Exemple:
        DetruireTraitementLivraisonLSF.py mpothier qBDG_LIVRSDE jobid
        DetruireTraitementLivraisonLSF.py all # 51553;51554
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireTraitementLivraisonLSF.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, time, arcpy, subprocess, traceback

#*******************************************************************************************
class DetruireTraitementLivraisonLSF:
#*******************************************************************************************
    """
    Permet de d�truire les traitements de livraison des donn�es BDG en cours d'ex�cution dans une queue LSF.
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
    def validerParamObligatoire(self, usager, queue, jobid):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        usager          : Nom de l'usager pour lequel on veut voir les traitements en cours.
        queue           : Nom de la queue LSF pour lequel on veut voir les traitements en cours.
        jobid           : liste des jobid de LSF � d�truire.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """

        #Valider la pr�sence de l'environnement
        if (len(usager) == 0):
            raise Exception ('Param�tre obligatoire manquant: usager')

        #Valider la pr�sence de l'environnement
        if (len(queue) == 0):
            raise Exception ('Param�tre obligatoire manquant: queue')

        #Valider la pr�sence de l'environnement
        if (len(jobid) == 0):
            raise Exception ('Param�tre obligatoire manquant: jobid')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, usager, queue, jobid):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�truire les traitements de livraison des donn�es BDG en cours d'ex�cution dans une queue LSF.
        
        Param�tres:
        -----------
        usager          : Nom de l'usager pour lequel on veut voir les traitements en cours.
        queue           : Nom de la queue LSF pour lequel on veut voir les traitements en cours.
        jobid           : liste des jobid de LSF � d�truire.
        
        Retour:
        -------
        
        """
        
        #------------------------------------------------------
        #D�finir la commande pour afficher l'�tat de la queue LSF
        commande = "plink lsf bqueues -w -u " + usager + " " + queue
        
        #Afficher la commande pour afficher l'�tat de la queue LSF
        arcpy.AddMessage(" ")
        arcpy.AddMessage(commande)
        
        #Ex�cuter la commande pour afficher les traitements LSF
        message = subprocess.check_output(commande, shell=True)
        
        #Afficher le r�sultat
        arcpy.AddMessage(message)
        
        #------------------------------------------------------
        #D�finir la commande pour afficher les traitements LSF
        commande = "plink lsf bjobs -w -u " + usager + " -q " + queue
        
        #Afficher la commande pour afficher les traitements LSF
        #arcpy.AddMessage(" ")
        arcpy.AddMessage(commande)
        
        #Ex�cuter la commande pour afficher les traitements LSF
        message = subprocess.check_output(commande, shell=True)
        
        #Afficher le r�sultat
        arcpy.AddMessage(message)
        
        #------------------------------------------------------
        #D�finir la commande pour afficher les traitements LSF
        commande = "plink lsf bkill "
        
        #Traiter toutes les JOBID
        for job in jobid.split(","):
            #Extraire le num�ro de la Job
            noJob = job.split(" ")[0]
            
            #Afficher la commande pour afficher les traitements LSF
            #arcpy.AddMessage(" ")
            arcpy.AddMessage(commande + noJob)
            
            #Ex�cuter la commande pour afficher les traitements LSF
            message = subprocess.check_output(commande + noJob, shell=True)
            
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
        jobid   = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            usager = sys.argv[1]
        
        if len(sys.argv) > 2:
            queue = sys.argv[2].replace("#","")
        
        if len(sys.argv) > 3:
            jobid = sys.argv[3].replace(";",",").replace("'","")
        
        #Instanciation de la classe DetruireTraitementLivraisonLSF
        oDetruireTraitementLivraisonLSF = DetruireTraitementLivraisonLSF()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oDetruireTraitementLivraisonLSF.validerParamObligatoire(usager, queue, jobid)
        
        #Ex�cuter le traitement
        arcpy.AddMessage("- Destruction des traitements LSF")
        oDetruireTraitementLivraisonLSF.executer(usager, queue, jobid)
        
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