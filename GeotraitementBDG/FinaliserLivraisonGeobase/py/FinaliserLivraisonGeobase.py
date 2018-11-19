#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet de finaliser la livraison des donn�es Geobase.

    1-Le r�pertoire de travail de livraison du jeu de donn�es n�est pas d�truit.
      D�truire le r�pertoire de travail du jeu de donn�es dans le r�pertoire de livraison.
      Exemple :
        T:\Gestion_BDSpatiales\transactionsGeobase\pro\livraison\rhn_gen\06EB000

    5-Le fichier de r�cup�ration n�a pas �t� cr��.
      .Remettre le statut=0 dans la table SER_RECONCILE_LOG.
      .Cr�er le fichier de r�cup�ration � *.txt � dans le r�pertoire de r�cup�ration afin que la t�che puisse se fermer correctement.
       Exemple :
         T:\Gestion_BDSpatiales\transactionsGeobase\pro\recuperation\06EB000_170479_rhn_gen_22337.txt
         id=06EB000
         lot=170479
         travail=rhn_gen
         jobid=22337
         exp_erreur=Support_bdg-Erreur
         exp_avis=Support_bdg-Avis
      .Le fichier de r�cup�ration sera enlev� automatiquement et un fichier LOG sera cr�� dans le r�pertoire de r�cup�ration lorsque termin�.
       Exemple :
         22337_06EB000_rhn_gen_170479_fermerTache_LSF.log

Nom: FinaliserLivraisonGeobase.py

Auteur: Michel Pothier         Date: 30 juin 2015

Param�tres:
-----------
env         : Type d'environnement.
listeJob    : Liste des num�ros de job LSF.

Classe:
-------
 Nom                            Description
 -----------------------------  --------------------------------------------------------------------
 FinaliserLivraisonGeobase          Finaliser la livraison des donn�es Geobase.
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FinaliserLivraisonGeobase.py 1120 2016-08-02 19:01:26Z mpothier $"
#********************************************************************************************

# Identification des librairies utilisees 
import os, sys, arcpy, datetime, cx_Oracle, shutil, glob, traceback

# Importation des modules priv�s (Cits)
import  CompteBDG

#*******************************************************************************************
class FinaliserLivraisonGeobase(object):
#*******************************************************************************************
    """
    Finaliser la livraison des donn�es Geobase.
    
    Retour:
        ErrorLevel  Integer  Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour finaliser la livraison des donn�es Geobase.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        # D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeJob):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour finalider la livraison des donn�es.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        listeJob    : Liste des num�ros de job LSF.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � geobase.       
        oBDG            : Objet utilitaire pour traiter des services BDG.
        env2            : Contient la 2i�me partie de l'environnement.
        """

        #D�finir la 2i�me partie de l'environnement
        env2 = env.lower().split("_")[1]
        
        #Instanciation de la classe BDG et connexion � la Geobase
        arcpy.AddMessage("- Connexion � la Geobase")
        oBDG = self.CompteBDG.OuvrirConnexionBDG(env, env)   

        #Traiter tous les no_job
        for job in listeJob.split(",")
            #D�finir le no_job
            no_job = job.split(":")[0]
            
            #Cr�er la requ�te SQL.
            arcpy.AddMessage("- Extraction de l'information de la livraison dans SER_RECONCILE_LOG")
            sSql = "SELECT JOB_ID,TY_TRAV,NO_LOT,IDENTIFIANT,STATUT FROM SER_RECONCILE_LOG WHERE ETAPE=0 AND STATUT<>9 AND JOB_ID=" + no_job
            arcpy.AddMessage(sSql)

            #Ex�cuter la requ�te SQL
            resultat = oBDG.query(sSql)
            
            #V�rifier si le no_job est valide
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
                raise Exception("Num�ro de job invalide : " + no_job)

            #D�finir les r�pertoires par d�faut
            repertoireLog = "\\\\dfscitsh\\CITS\\Logs\\gestion_bdg\\Gestion_BDSpatiales"
            repertoireTravail = "\\\\dfscitsh\\CITS\\Travail\\Gestion_BDSpatiales\\transactionsGeobase\\" + env2
            
            #D�truire le r�pertoire de travail du jeu de donn�es dans le r�pertoire de livraison.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- D�truire le r�pertoire de travail du jeu de donn�es dans le r�pertoire de livraison")
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
            
            #D�finir le nom du fichier de r�cup�ration avec erreur 
            src = repertoireTravail + "\\recuperation\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt_en_traitement_en_erreur"
            #D�finir le nom du fichier de r�cup�ration sans erreur 
            dst = repertoireTravail + "\\recuperation\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt"
            
            #V�rifier si le fichier de r�cup�ration est pr�sent mais en erreur
            if os.path.exists(src):
                #Renommer le fichier de r�cup�ration sans erreur
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Renommer le fichier de r�cup�ration sans erreur")
                arcpy.AddMessage("RENAME " + src + " " + dst)
                os.rename(src, dst)
                
            #Si le fichier de r�cup�ration en erreur est absent et que le fichier de r�cup�ration sans erreur est absent
            elif not os.path.exists(dst):
                #Cr�er le fichier de r�cup�ration dans le r�pertoire de r�cup�ration.
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Cr�er le fichier de r�cup�ration dans le r�pertoire de r�cup�ration:")
                src = repertoireTravail + "\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt"
                dst = repertoireTravail + "\\recuperation\\" + identifiant + "_" + no_lot + "_" + ty_trav + "_" + no_job + ".txt"
                fichierRecuperation = open(src,"w")
                #�criture du fichier
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
                
                #Renommer le fichier dans le r�pertoire de r�cup�ration
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Renommer le fichier dans le r�pertoire de r�cup�ration:")
                arcpy.AddMessage("rename " + src + " " + dst)
                os.rename(src, dst)
        
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
        listeJob = ""
        
        # Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            listeJob = sys.argv[2].replace(";",",")
        
        # D�finir l'objet pour finaliser la livraison Geobase.
        oFinaliserLivraisonGeobase = FinaliserLivraisonGeobase()
        
        # Ex�cuter le traitement pour finaliser la livraison Geobase.
        oFinaliserLivraisonGeobase.executer(env, listeJob)
    
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