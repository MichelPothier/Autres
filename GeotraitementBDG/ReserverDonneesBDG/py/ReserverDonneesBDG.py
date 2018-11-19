#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ReserverDonneesBDG.py
# Auteur    : Michel Pothier
# Date      : 07 novembre 2014

"""
Outil qui permet de r�server des donn�es BDG.

Le fichier de r�servation est utilis� afin de v�rifier si les donn�es ont �t� modifi�s dans la BDG avant la livraison.

La date de r�servation est pr�sente dans le fichier de r�servation sous l'attribut DATE_RESERVATION de la table RESERVATION_6.

Param�tres d'entr�e:
--------------------
env             OB      Type d'environnement [PRO/TST/DEV]
                        d�faut = PRO
ty_produit      OB      Type de produit [BDG]
                        d�faut = BDG
no_map          OB      Num�ro de mise au programme.
                        d�faut =

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s
import CompteSib, CompteBDG

#*******************************************************************************************
class ExceptionReserverDonneesBDG(Exception):
#*******************************************************************************************
    """
    Classe d'exception d�riv�e de la classe Exception pour g�rer un probl�me
    dans l'ex�cution du programme.
    
    Lors de l'instanciation, passez une cha�ne de caract�re en argument
    pour d'�crire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class ReserverDonneesBDG(object):
#*******************************************************************************************
    """
    R�server des donn�es BDG.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour r�server des donn�es BDG.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------

        """
        
        # D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_produit, no_map):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour r�server des donn�es BDG.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        ty_produit  : Type de produit.
        no_map      : Num�ro de mise au programme.
               
        Variables:
        ----------

        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib("SIB_" + env, "SIB_" + env)  
        
        #Extraire l'information de SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire l'information de SIB")
        sql = ("SELECT A.NO_MAP, A.IDENTIFIANT, B.NO_LOT, B.TY_TRAV"
               "  FROM F502_PS A, F503_TR B"
               " WHERE A.E_PLSNRC = 'P' AND A.NO_MAP = B.NO_MAP AND A.TY_PRODUIT = '" + ty_produit + "' AND A.NO_MAP=" + no_map)
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise ExceptionReserverDonneesBDG("Num�ro de mise au programme invalide : " + no_map)
        
        #Afficher l'information de SIB
        identifiant = resultat[0][1]
        arcpy.AddMessage(" Identifiant : " + identifiant)
        no_lot = resultat[0][2]
        arcpy.AddMessage(" Num�ro de lot : " + no_lot)
        ty_travail = resultat[0][3]
        arcpy.AddMessage(" Type de travail : " + ty_travail)
        
        #Fermeture de la connexion SIB
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib() 
        
        #Instanciation de la classe BDG et connexion � la BDG
        arcpy.AddMessage(" ")
        oBDG = self.CompteBDG.OuvrirConnexionBDG("BDRS_" + env)  
        
        #V�rifier la pr�sence du s�maphore de r�servation
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- V�rifier la pr�sence du s�maphore de r�servation")
        sql = ("SELECT DATE_CREATION, IDENTIFIANT, JOB_ID"
               "  FROM bdrs_gest_dba.SER_SEMAPHORE_BDG"
               " WHERE IDENTIFIANT='" + identifiant + "'")
        arcpy.AddMessage(sql)
        resultat = oBDG.query(sql)
        #V�rifier le r�sultat
        if resultat:
            #Retourner une exception
            raise ExceptionReserverDonneesBDG("Un s�maphore de r�servation est d�j� pr�sent : " + str(resultat))
        
        #Fermeture de la connexion SIB
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        oBDG.close()
        
        #R�server un jeu de donn�es BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- R�server les donn�es BDG")
        cmd = "%python27% S:\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py "
        cmd = cmd + "Reserver --depot " + ty_produit + " --env " + env + " --no_map " + no_map
        cmd = cmd + " --exp_erreur " + ty_travail + "-ERREUR-pro --exp_avis " + ty_travail + "-AVIS-pro"
        #D�finir le fichier LOG dans la commande
        fichierLog = "\\\\dfscitsh\\cits\\Logs\\pro\\" + env.lower() + "_" + ty_produit.lower() + "_" + ty_travail + "_" + identifiant + "_Reservation.log"
        cmd = cmd + " --log " + fichierLog
        arcpy.AddMessage(cmd)
        
        #Ex�cution du programme de r�servation
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "PRO"
        ty_produit = "BDG"
        no_map = ""
        
        # Lecture des param�tres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_produit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            no_map = sys.argv[3].split(":")[0]
        
        #D�finir l'objet pour r�server des donn�es BDG.
        oReserverDonneesBDG = ReserverDonneesBDG()
        
        #Ex�cuter le traitement pour r�server des donn�es BDG.
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
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("- Succ�s du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)