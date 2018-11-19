#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : RelancerLivraisonBDG.py
# Auteur    : Michel Pothier
# Date      : 05 novembre 2014

"""
Outil qui permet de relancer la livraison des données BDG en fonction du numéro d'étape en problème.

Paramètres d'entrée:
--------------------
env         OB      type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV]
                    défaut = BDRS_PRO
listeNoJob  OB      Liste des numéros de job LSF à traiter.
                    défaut =

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)
Usage:
    RelancerLivraisonBDG.py env listeNoJob

Exemple:
    RelancerLivraisonBDG.py BDRS_PRO 54677,54678
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: RelancerLivraisonBDG.py 1157 2018-01-16 21:20:09Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, subprocess, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class RelancerLivraisonBDG(object):
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
        
        # Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNoJob):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour finalider la livraison des données.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        listeNoJob  : Liste des numéros de job LSF à traiter.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        oBDG            : Objet utilitaire pour traiter des services BDG.

        """
        
        #Instanciation de la classe BDG et connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        oBDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Traiter la liste des numéros de Job LSF
        for noJob in listeNoJob.split(","):
            #Extraire seulement le numéro de JOB
            no_job = noJob.split(":")[0]
            #Créer la requête SQL.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Extraction de l'information de la livraison dans SER_RECONCILE_LOG")
            sSql = "SELECT JOB_ID,TY_TRAV,NO_LOT,IDENTIFIANT,STATUT,ETAPE,DATE_DEBUT FROM SER_RECONCILE_LOG WHERE ETAPE NOT IN (0,9) AND (STATUT=-1 OR SYSDATE-DATE_DEBUT>0.05) AND JOB_ID=" + no_job
            arcpy.AddMessage(sSql)
            
            #Exécuter la requête SQL
            resultat = oBDG.query(sSql)
            
            #Vérifier si le NoJob est valide
            if len(resultat) > 0:
                #Extraire l'information
                ty_produit = "BDG"
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
                raise Exception("Numéro de job invalide : " + no_job)
            
            #Vérifier si l'étape est 4:Charger la PGDB dans la BD
            if etape == 4:
                #Remettre le l'étape à 3 dans la table SER_RECONCILE_LOG.
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Remettre le statut=0 dans la table SER_RECONCILE_LOG")
                cmd = "UPDATE SER_RECONCILE_LOG SET ETAPE=3 WHERE job_id=" + no_job + " AND no_lot=" + no_lot
                arcpy.AddMessage(cmd)
                oBDG.execute(cmd)
                arcpy.AddMessage("COMMIT")
                oBDG.execute("COMMIT")
                
            #Vérifier si l'étape est 7:Corréler les métadonnées de SIB vers la BDRS
            if etape == 7:
                #Extraire le ZT_ID
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Extraction du ZT_ID à partir de la table SYS_ZT_2")
                sSql = "SELECT MAX(ZT_ID) FROM SYS_ZT_2 WHERE ZT_ID LIKE '" + identifiant + "_BDG_%' AND CREATION_DATE >= '" + str(date_debut).split(" ")[0] + "'" 
                arcpy.AddMessage(sSql)
                resultat = oBDG.query(sSql)
                #Vérifier la présence d'un résultat
                if resultat[0][0] <> None:
                    #Définir le ZT_ID
                    zt_id = resultat[0][0]
                    
                    #Définir le fichier log
                    log_file = "W:\\Logs\\gestion_bdg\\Gestion_BDSpatiales\\Livraison\\" + env.split("_")[1] + "\\bdg\\" + ty_trav + "\\" + identifiant + "\\" + no_lot + "\\EffacerZT_BDG.log"
                    
                    #Effacer les métadonnées et la ZT via le programme 
                    arcpy.AddMessage(" ")
                    arcpy.AddMessage("- Effacer les métadonnées et la ZT via le programme")
                    cmd = "%FME2017% W:\\Equipe\\Unix\\gestion_bdg\\Outil\\fme\\EffacerZT-BDG.fmw"
                    cmd = cmd + " --ZT_ID " + zt_id + " --LOG_FILE " + log_file
                    #Vérifier si l'environnement est BDRS_TST
                    if env == "BDRS_TST":
                        #Ajouter les paramètres
                        cmd = cmd + " --OUT_BD_INSTANCE BDRS_TST --OUT_BDRS_INSTANCE sde:oracle11g:BDRS_TST --OUT_BDRS_DATA_PASSWORD tst --OUT_BDRS_META_PASSWORD tst"
                    arcpy.AddMessage(cmd)   
                    message = subprocess.check_output(cmd, shell=True)
                    arcpy.AddMessage(message)
                    
                #Si aucun ZT_ID
                else:
                    #Afficher un avertissement
                    arcpy.AddWarning("Aucun ZT_ID n'est présent dans la table SYS_ZT_2")
            
            #Relancer la livraison
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Relancer la livraison des données")
            cmd = "%python27% S:\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py "
            cmd = cmd + "RelancerLivraison --depot " + ty_produit + " --env " + env.split("_")[1] + " --travail " + ty_trav + " --lot " + no_lot + " --identifiant " + identifiant + " --password 123hiroshima --exp_erreur Support_bdg-Erreur --exp_avis Support_bdg-Avis"
            arcpy.AddMessage(cmd)   
            message = subprocess.check_output(cmd, shell=True)
            arcpy.AddMessage(message)
        
        # Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        oBDG.close()
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "BDRS_PRO"
        listeNoJob = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeNoJob = sys.argv[2].replace(";",",").replace("'","")
        
        # Définir l'objet pour relancer la livraison BDG.
        oRelancerLivraisonBDG = RelancerLivraisonBDG()
        
        # Exécuter le traitement pour relancer la livraison BDG.
        oRelancerLivraisonBDG.executer(env, listeNoJob)
    
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