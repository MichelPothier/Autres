#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ReserverDonneesBDG.py
# Auteur    : Michel Pothier
# Date      : 07 novembre 2014

"""
Outil qui permet de réserver des données BDG.

Le fichier de réservation est utilisé afin de vérifier si les données ont été modifiés dans la BDG avant la livraison.

La date de réservation est présente dans le fichier de réservation sous l'attribut DATE_RESERVATION de la table RESERVATION_6.

Paramètres d'entrée:
--------------------
env             OB      Type d'environnement [PRO/TST/DEV]
                        défaut = PRO
ty_produit      OB      Type de produit [BDG]
                        défaut = BDG
no_map          OB      Numéro de mise au programme.
                        défaut =

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)
Usage:
    ReserverDonneesBDG.py env ty_produit no_map

Exemple:
    ReserverDonneesBDG.py PRO BDG 761823
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ReserverDonneesBDG.py 10242 2014-07-04 13:54:15Z mpothier $"

#####################################################################################################################################

# Identification des librairies utilisees 
import os, sys, arcpy, subprocess, traceback

# Importation des modules privés
import CompteSib, CompteBDG

#*******************************************************************************************
class ExceptionReserverDonneesBDG(Exception):
#*******************************************************************************************
    """
    Classe d'exception dérivée de la classe Exception pour gèrer un problème
    dans l'exécution du programme.
    
    Lors de l'instanciation, passez une chaîne de caractère en argument
    pour d'écrire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class ReserverDonneesBDG(object):
#*******************************************************************************************
    """
    Réserver des données BDG.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour réserver des données BDG.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------

        """
        
        # Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_produit, no_map):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour réserver des données BDG.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        ty_produit  : Type de produit.
        no_map      : Numéro de mise au programme.
               
        Variables:
        ----------

        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib("SIB_" + env, "SIB_" + env)  
        
        #Extraire l'information de SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire l'information de SIB")
        sql = ("SELECT A.NO_MAP, A.IDENTIFIANT, B.NO_LOT, B.TY_TRAV"
               "  FROM F502_PS A, F503_TR B"
               " WHERE A.E_PLSNRC = 'P' AND A.NO_MAP = B.NO_MAP AND A.TY_PRODUIT = '" + ty_produit + "' AND A.NO_MAP=" + no_map)
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise ExceptionReserverDonneesBDG("Numéro de mise au programme invalide : " + no_map)
        
        #Afficher l'information de SIB
        identifiant = resultat[0][1]
        arcpy.AddMessage(" Identifiant : " + identifiant)
        no_lot = resultat[0][2]
        arcpy.AddMessage(" Numéro de lot : " + no_lot)
        ty_travail = resultat[0][3]
        arcpy.AddMessage(" Type de travail : " + ty_travail)
        
        #Fermeture de la connexion SIB
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib() 
        
        #Instanciation de la classe BDG et connexion à la BDG
        arcpy.AddMessage(" ")
        oBDG = self.CompteBDG.OuvrirConnexionBDG("BDRS_" + env)  
        
        #Vérifier la présence du sémaphore de réservation
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Vérifier la présence du sémaphore de réservation")
        sql = ("SELECT DATE_CREATION, IDENTIFIANT, JOB_ID"
               "  FROM bdrs_gest_dba.SER_SEMAPHORE_BDG"
               " WHERE IDENTIFIANT='" + identifiant + "'")
        arcpy.AddMessage(sql)
        resultat = oBDG.query(sql)
        #Vérifier le résultat
        if resultat:
            #Retourner une exception
            raise ExceptionReserverDonneesBDG("Un sémaphore de réservation est déjà présent : " + str(resultat))
        
        #Fermeture de la connexion SIB
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        oBDG.close()
        
        #Réserver un jeu de données BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Réserver les données BDG")
        cmd = "%python27% S:\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py "
        cmd = cmd + "Reserver --depot " + ty_produit + " --env " + env + " --no_map " + no_map
        cmd = cmd + " --exp_erreur " + ty_travail + "-ERREUR-pro --exp_avis " + ty_travail + "-AVIS-pro"
        #Définir le fichier LOG dans la commande
        fichierLog = "\\\\dfscitsh\\cits\\Logs\\pro\\" + env.lower() + "_" + ty_produit.lower() + "_" + ty_travail + "_" + identifiant + "_Reservation.log"
        cmd = cmd + " --log " + fichierLog
        arcpy.AddMessage(cmd)
        
        #Exécution du programme de réservation
        try:
            message = subprocess.check_output(cmd, shell=True)
        except Exception, err:
            #Lire le fichier log contenant l'erreur
            file = open(fichierLog, 'r')
            #Retourner l'erreur
            raise ExceptionReserverDonneesBDG(file.read())
        
        #Afficher le message
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
        no_map = ""
        
        # Lecture des paramètres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_produit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            no_map = sys.argv[3].split(":")[0]
        
        #Définir l'objet pour réserver des données BDG.
        oReserverDonneesBDG = ReserverDonneesBDG()
        
        #Exécuter le traitement pour réserver des données BDG.
        oReserverDonneesBDG.executer(env, ty_produit, no_map)
    
    #Gestion des erreurs
    except ExceptionReserverDonneesBDG, err:
        #Afficher l'erreur
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
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