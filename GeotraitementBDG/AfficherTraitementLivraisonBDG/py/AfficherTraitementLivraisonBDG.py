#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""
Outil qui permet d'afficher les traitements de livraison des donn�es BDG.

L'information est extraite de la table SER_RECONCILE_LOG du compte BDRS_GEST_DBA.

Nom: AfficherTraitementLivraisonBDG.py

Auteur: Michel Pothier         Date: 18 ao�t 2015

Param�tres:
-----------
env         : Type d'environnement.
statut      : Statut du traitement de livraion.
              99:Pause
              -1:Erreur
              0:M�nage
              1:Attente
              2:Ex�cution
              9:Termin�e
              D�faut:99,-1,0,1,2
date        : Date � partir de laquelle on veut voir les livraisons.
              D�faut:hier si le statut contient l'�tat "9:Termin�e"

Classe:
-------
 Nom                            Description
 -----------------------------  --------------------------------------------------------------------
 AfficherTraitementLivraisonBDG          Finaliser la livraison des donn�es BDG.
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherTraitementLivraisonBDG.py 1111 2016-06-15 19:51:31Z mpothier $"
#********************************************************************************************

# Importation des modules publics
import os, sys, arcpy, datetime, cx_Oracle, shutil, traceback

# Importation des modules priv�s (Cits)
import CompteBDG, util_bd

#*******************************************************************************************
class AfficherTraitementLivraisonBDG(object):
#*******************************************************************************************
    """
    Afficher les traitements de livraison des donn�es BDG.
    
    Retour:
        ErrorLevel  Integer  Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher les traitements de livraison des donn�es BDG.
        
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
    def executer(self, env, statut, date):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour afficher les traitements de livraison des donn�es BDG.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        statut      : Statut du traitement de livraison.
        date        : Date � partir de laquelle on veut afficher les livraisons.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        oBDG            : Objet utilitaire pour traiter des services BDG.
        """
        
        #Instanciation de la classe BDG et connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        oBDG = self.CompteBDG.OuvrirConnexionBDG(env, env)   

        #Extraire tous les statuts
        etat = []
        for stat in statut.split(";"):
            #Ajouter l'�tat
            etat.append(int(stat.split(":")[0]))
        
        #Cr�er la requ�te SQL.
        arcpy.AddMessage("- Extraction de l'information de la livraison dans SER_RECONCILE_LOG")
        sSql = ("SELECT JOB_ID, TY_TRAV, NO_LOT, IDENTIFIANT, STATUT, ETAPE, DATE_ENTREE, DATE_DEBUT, DATE_FIN, EXP_ERREUR, EXP_AVIS, FORCER"
                "  FROM SER_RECONCILE_LOG"
                " WHERE STATUT IN " + str(etat).replace("[","(").replace("]",")"))
        #V�rifier si la date est sp�cifi�e
        if len(date) > 0:
            #Ajouter le test de la date dans la requ�te
            sSql = sSql + " AND DATE_ENTREE > to_date('" + date + "','yyyy-mm-dd HH24:MI:SS')"
        #V�rifier si le statut contient ceux termin�es
        elif 9 in etat:
            #Ajouter le test de la date par d�faut dans la requ�te
            sSql = sSql + " AND DATE_ENTREE > to_date('" + str(datetime.date.today()- datetime.timedelta(days=1)) + "','yyyy-mm-dd HH24:MI:SS')"

        #Ajouter le tri dans la requ�te
        sSql = sSql + " ORDER BY DATE_ENTREE DESC"
        #Afficher la requ�te SQL
        arcpy.AddMessage(sSql)
        #Ex�cuter la requ�te SQL
        resultat = oBDG.query(sSql)
        
        #Initialiser la valeur de la livraison
        livraison = ""
        #Afficher l'ent�te de l'information
        arcpy.AddMessage(" ")
        entete = ['JOB_ID',
                  'TY_TRAV       ',
                  'NO_LOT',
                  'IDENTIFIANT',
                  'STATUT',
                  'ETAPE',
                  'DATE_ENTREE        ',
                  'DATE_DEBUT         ',
                  'DATE_FIN           ',
                  'EXP_ERREUR             ',
                  'EXP_AVIS               ',
                  'FORCER']
        #Traiter toutes les valeurs
        for i in range(0, len(entete)):
            #Remplir les valeurs de livraison
            livraison = livraison + entete[i] + "  "
        #Afficher l'information
        arcpy.AddMessage(livraison)
       
        #Extraire toutes les livraisons
        for item in  resultat:
            #Initialiser la valeur de la livraison
            livraison = ""
            #Traiter toutes les valeurs
            for i in range(0, len(entete)):
                #Remplir les valeurs de livraison
                livraison = livraison + str(item[i]).ljust(len(entete[i]),' ') + "  "
            #Afficher l'information
            arcpy.AddMessage(livraison)
        
        #Mettre un espace
        arcpy.AddMessage(" ")
       
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
        statut = ""
        date = ""
        
        # Lecture des param�tres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            statut = sys.argv[2]

        if len(sys.argv) > 3:
            if sys.argv[3] <> '#':
                date = sys.argv[3]

        # D�finir l'objet pour afficher les traitements de livraison des donn�es BDG.
        oAfficherTraitementLivraisonBDG = AfficherTraitementLivraisonBDG()
        
        # Ex�cuter le traitement pour afficher les traitements de livraison des donn�es BDG.
        oAfficherTraitementLivraisonBDG.executer(env, statut, date)
    
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