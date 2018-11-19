#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : RelancerLivraisonGeobase.py
# Auteur    : Michel Pothier
# Date      : 05 novembre 2014

"""
Outil qui permet de relancer la livraison des donn�es Geobase en fonction du num�ro d'�tape en probl�me.

Param�tres d'entr�e:
--------------------
env         OB      Type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV]
                    d�faut = BDRS_PRO
listeNoJob  OB      Liste des num�ros de job LSF � traiter.
                    d�faut =

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)
Usage:
    RelancerLivraisonGeobase.py env listeNoJob

Exemple:
    RelancerLivraisonGeobase.py BDRS_PRO 54677,54678
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: RelancerLivraisonGeobase.py 1124 2016-10-13 12:50:29Z mpothier $"

#####################################################################################################################################

# Identification des librairies utilisees 
import os, sys, arcpy, subprocess, traceback

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class RelancerLivraisonGeobase(object):
#*******************************************************************************************
    """
    Relancer la livraison des donn�es Geobase.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour relancer la livraison des donn�es Geobase.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � Geobase.
        
        """
        
        # D�finir l'objet de gestion des comptes Geobase.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNoJob):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour finalider la livraison des donn�es.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        listeNoJob  : Liste des num�ros de job LSF � traiter.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � Geobase.       
        oGeobase            : Objet utilitaire pour traiter des services Geobase.

        """
        
        #Instanciation de la classe Geobase et connexion � la Geobase
        arcpy.AddMessage("- Connexion � la Geobase")
        oGeobase = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Traiter la liste des num�ros de Job LSF
        for noJob in listeNoJob.split(","):
            #Extraire seulement le num�ro de JOB
            no_job = noJob.split(":")[0]
            #Cr�er la requ�te SQL.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Extraction de l'information de la livraison dans SER_RECONCILE_LOG")
            sSql = "SELECT JOB_ID,TY_TRAV,NO_LOT,IDENTIFIANT,STATUT,ETAPE,DATE_DEBUT FROM SER_RECONCILE_LOG WHERE ETAPE NOT IN (0,9) AND (STATUT=-1 OR SYSDATE-DATE_DEBUT>0.1) AND JOB_ID=" + no_job
            arcpy.AddMessage(sSql)
            
            #Ex�cuter la requ�te SQL
            resultat = oGeobase.query(sSql)
            
            #V�rifier si le NoJob est valide
            if len(resultat) > 0:
                #Extraire l'information
                ty_produit = "GEOBASE"
                arcpy.AddMessage(" ty_produit:" + ty_produit)
                ty_trav = resultat[0][1].lower()
                arcpy.AddMessage(" ty_trav:" + ty_trav)
                no_lot = str(resultat[0][2])
                arcpy.AddMessage(" no_lot:" + no_lot)
                identifiant = resultat[0][3]
                arcpy.AddMessage(" identifiant:" + identifiant)
                statut = resultat[0][4]
                arcpy.AddMessage(" statut:" + str(statut))
                etape = resultat[0][5]
                arcpy.AddMessage(" etape:" + str(etape))
                date_debut = resultat[0][6]
                arcpy.AddMessage(" date_debut:" + str(date_debut))
                
            #Si le NoJob est invalide
            else:
                #Envoyer une exception
                raise Exception("Num�ro de job invalide : " + no_job)
            
            #V�rifier si l'�tape est 4:Charger la PGDB dans la BD
            if etape == 4:
                #Remettre le l'�tape � 3 dans la table SER_RECONCILE_LOG.
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Remettre le statut=0 dans la table SER_RECONCILE_LOG")
                cmd = "UPDATE SER_RECONCILE_LOG SET ETAPE=3 WHERE job_id=" + no_job + " AND no_lot=" + no_lot
                arcpy.AddMessage(cmd)
                oGeobase.execute(cmd)
                arcpy.AddMessage("COMMIT")
                oGeobase.execute("COMMIT")
            
            #Relancer la livraison
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Relancer la livraison des donn�es")
            cmd = "%python27% S:\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py "
            cmd = cmd + "RelancerLivraison --depot " + ty_produit + " --env PRO --travail " + ty_trav + " --lot " + no_lot + " --identifiant " + identifiant + " --password 123hiroshima --exp_erreur Support_bdg-Erreur --exp_avis Support_bdg-Avis"
            arcpy.AddMessage(cmd)   
            message = subprocess.check_output(cmd, shell=True)
            arcpy.AddMessage(message)
        
        # Fermeture de la connexion de la BD Geobase
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion Geobase")
        oGeobase.close()
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "BDRS_PRO"
        listeNoJob = ""
        
        #Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeNoJob = sys.argv[2].replace(";",",").replace("'","")
        
        #D�finir l'objet pour relancer la livraison Geobase.
        oRelancerLivraisonGeobase = RelancerLivraisonGeobase()
        
        #Ex�cuter le traitement pour relancer la livraison Geobase.
        oRelancerLivraisonGeobase.executer(env, listeNoJob)
    
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