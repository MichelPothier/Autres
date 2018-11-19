#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet de finaliser la livraison des données Geobase.

    1-Le répertoire de travail de livraison du jeu de données n’est pas détruit.
      Détruire le répertoire de travail du jeu de données dans le répertoire de livraison.
      Exemple :
        T:\Gestion_BDSpatiales\transactionsGeobase\pro\livraison\rhn_gen\06EB000

    5-Le fichier de récupération n’a pas été créé.
      .Remettre le statut=0 dans la table SER_RECONCILE_LOG.
      .Créer le fichier de récupération « *.txt » dans le répertoire de récupération afin que la tâche puisse se fermer correctement.
       Exemple :
         T:\Gestion_BDSpatiales\transactionsGeobase\pro\recuperation\06EB000_170479_rhn_gen_22337.txt
         id=06EB000
         lot=170479
         travail=rhn_gen
         jobid=22337
         exp_erreur=Support_bdg-Erreur
         exp_avis=Support_bdg-Avis
      .Le fichier de récupération sera enlevé automatiquement et un fichier LOG sera créé dans le répertoire de récupération lorsque terminé.
       Exemple :
         22337_06EB000_rhn_gen_170479_fermerTache_LSF.log

Nom: FinaliserLivraisonGeobase.py

Auteur: Michel Pothier         Date: 30 juin 2015

Paramètres:
-----------
env         : Type d'environnement.
listeJob    : Liste des numéros de job LSF.

Classe:
-------
 Nom                            Description
 -----------------------------  --------------------------------------------------------------------
 FinaliserLivraisonGeobase          Finaliser la livraison des données Geobase.
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FinaliserLivraisonGeobase.py 1120 2016-08-02 19:01:26Z mpothier $"
#********************************************************************************************

# Identification des librairies utilisees 
import os, sys, arcpy, datetime, cx_Oracle, shutil, glob, traceback

# Importation des modules privés (Cits)
import  CompteBDG

#*******************************************************************************************
class FinaliserLivraisonGeobase(object):
#*******************************************************************************************
    """
    Finaliser la livraison des données Geobase.
    
    Retour:
        ErrorLevel  Integer  Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour finaliser la livraison des données Geobase.
        
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
    def executer(self, env, listeJob):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour finalider la livraison des données.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        listeJob    : Liste des numéros de job LSF.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à geobase.       
        oBDG            : Objet utilitaire pour traiter des services BDG.
        env2            : Contient la 2ième partie de l'environnement.
        """

        #Définir la 2ième partie de l'environnement
        env2 = env.lower().split("_")[1]
        
        #Instanciation de la classe BDG et connexion à la Geobase
        arcpy.AddMessage("- Connexion à la Geobase")
        oBDG = self.CompteBDG.OuvrirConnexionBDG(env, env)   

        #Traiter tous les no_job
        for job in listeJob.split(",")
            #Définir le no_job
            no_job = job.split(":")[0]
            
            #Créer la requête SQL.
            arcpy.AddMessage("- Extraction de l'information de la livraison dans SER_RECONCILE_LOG")
            sSql = "SELECT JOB_ID,TY_TRAV,NO_LOT,IDENTIFIANT,STATUT FROM SER_RECONCILE_LOG WHERE ETAPE=0 AND STATUT<>9 AND JOB_ID=" + no_job
            arcpy.AddMessage(sSql)

            #Exécuter la requête SQL
            resultat = oBDG.query(sSql)
            
            #Vérifier si le no_job est valide
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
            #Si le no_job est invalide
            else:
                #Envoyer une exception
                raise Exception("Numéro de job invalide : " + no_job)

            #Définir les répertoires par défaut
            repertoireLog = "\\\\dfscitsh\\CITS\\Logs\\gestion_bdg\\Gestion_BDSpatiales"
            repertoireTravail = "\\\\dfscitsh\\CITS\\Travail\\Gestion_BDSpatiales\\transactionsGeobase\\" + env2
            
            #Détruire le répertoire de travail du jeu de données dans le répertoire de livraison.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Détruire le répertoire de travail du jeu de données dans le répertoire de livraison")
            src = repertoireTravail + "\\livraison\\" + ty_trav + "\\" + identifiant
            arcpy.AddMessage("RMDIR /Q /S " + src)
            try:
                shutil.rmtree(src)
            except Exception, err:
                arcpy.AddMessage(err)

            #Remettre le statut=0 dans la table SER_RECONCILE_LOG.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Remettre le statut=0 dans la table SER_RECONCILE_LOG")
            cmd = "UPDATE SER_RECONCILE_LOG SET statut=0 WHERE job_id=" + no_job + " AND no_lot=" + no_lot
            arcpy.AddMessage(cmd)
            oBDG.execute(cmd)
            arcpy.AddMessage("commit")
            oBDG.execute("commit")
            
            # Fermeture de la connexion de la BD Geobase
            arcpy.AddMessage("- Fermeture de la connexion Geobase")
            oBDG.close()   
            
            #Définir le nom du fichier de récupération avec erreur 
            src = repertoireTravail + "\\recuperation\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt_en_traitement_en_erreur"
            #Définir le nom du fichier de récupération sans erreur 
            dst = repertoireTravail + "\\recuperation\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt"
            
            #Vérifier si le fichier de récupération est présent mais en erreur
            if os.path.exists(src):
                #Renommer le fichier de récupération sans erreur
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Renommer le fichier de récupération sans erreur")
                arcpy.AddMessage("RENAME " + src + " " + dst)
                os.rename(src, dst)
                
            #Si le fichier de récupération en erreur est absent et que le fichier de récupération sans erreur est absent
            elif not os.path.exists(dst):
                #Créer le fichier de récupération dans le répertoire de récupération.
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Créer le fichier de récupération dans le répertoire de récupération:")
                src = repertoireTravail + "\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt"
                dst = repertoireTravail + "\\recuperation\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt"
                fichierRecuperation = open(src,"w")
                #Écriture du fichier
                fichierRecuperation.write("id=" + identifiant + "\n")
                fichierRecuperation.write("lot=" + no_lot + "\n")
                fichierRecuperation.write("travail=" + ty_trav + "\n")
                fichierRecuperation.write("jobid=" + no_job + "\n")
                fichierRecuperation.write("exp_erreur=Support_bdg-Erreur\n")
                fichierRecuperation.write("exp_avis=Support_bdg-Avis")
                fichierRecuperation.close()
                #Lecture du fichier
                fichierRecuperation = open(src)
                arcpy.AddMessage(src)
                arcpy.AddMessage(fichierRecuperation.read())        
                fichierRecuperation.close()
                
                #Renommer le fichier dans le répertoire de récupération
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Renommer le fichier dans le répertoire de récupération:")
                arcpy.AddMessage("rename " + src + " " + dst)
                os.rename(src, dst)
        
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
        listeJob = ""
        
        # Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            listeJob = sys.argv[2].replace(";",",")
        
        # Définir l'objet pour finaliser la livraison Geobase.
        oFinaliserLivraisonGeobase = FinaliserLivraisonGeobase()
        
        # Exécuter le traitement pour finaliser la livraison Geobase.
        oFinaliserLivraisonGeobase.executer(env, listeJob)
    
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