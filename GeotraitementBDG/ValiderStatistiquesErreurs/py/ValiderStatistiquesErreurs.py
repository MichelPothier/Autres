#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       :ValiderStatistiquesErreurs.py
# Auteur    : Michel Pothier
# Date      : 19 Juin 2018

"""
Outil qui permet de valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales par identifiant, par classe et par contrainte.
-Vérifier si toutes les contraintes présentent dans la table des statistiques sont présentes dans la table des contraintes spatiales.
-Les statistiques d'erreurs absentes de la table des contraintes seront détruites de la tables des statistiques d'erreurs.
-Vérifier si toutes les contraintes présentent dans la table des contraintes spatiales sont présentes dans la table des statistiques.
-Les statistiques d'erreurs absentes seront ajoutées en lançant les traitements de validation des contraintes spatiales via LSF.

Paramètres d'entrées:
----------------------
env                 OB  Type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV].
                        défaut = BDRS_PRO
tableContraintes    OB  Nom de la table contenant les contraintes spatiales.
                        défaut : CONTRAINTE_INTEGRITE_SPATIALE
tableStatistiques   OB  Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
                        défaut : TBL_STATISTIQUE_ELEMENT_ERREUR
classes             OB  Liste des classes présentent dans la table des contraintes spatiales.
                        défaut :
executer            OP  Indiquer si les identifiants non traités doivent être exécutées.
                        défaut : False
maxIdCmd            OP  Indiquer le nombre maximum d'identifiants par commande à exécuter.
                        défaut : 500
maxBatch            OP  Indiquer le nombre maximum de batch à exécuter.
                        défaut : 10
serveur             OP  Nom du serveur utilisé pour exéuter la queue LSF.
                        défaut : s-she-fermat

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    ValiderStatistiquesErreurs.py env tableContraintes tableStatistiques classes executer maxIdCmd maxBatch serveur

Exemple:
    ValiderStatistiquesErreurs.py BDRS_PRO # # # NHN_HHYD_WATERBODY_2;NHN_HNET_NETWORK_LINEAR_FLOW True 500 10 s-she-dumas

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderStatistiquesErreurs.py 1202 2018-08-02 13:16:47Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, subprocess, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderStatistiquesErreurs(object):
#*******************************************************************************************
    """
    Application qui permet de valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales par identifiant, par classe et par contrainte.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer un fichier PDF contenant les cartes des statistiques d'erreurs par classe et contrainte.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Définir la date de début
        self.dateDebut = datetime.datetime.now().replace(microsecond=0)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, tableContraintes, tableStatistiques, classes):
    #-------------------------------------------------------------------------------------
        """
        Valider les paramètres obligatoires.
        
        Paramètres:
        -----------
        env                : Type d'environnement.
        tableContraintes   : Nom de la table contenant les contraintes spatiales.
        tableStatistiques  : Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
        classes            : Liste des classes présentent dans la table des contraintes spatiales.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(tableContraintes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tableContraintes')
        
        if (len(tableStatistiques) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tableStatistiques')
        
        if (len(classes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'classes')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, tableContraintes, tableStatistiques, classes, executer, maxIdCmd, maxBatch, serveur):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales par identifiant, par classe et par contrainte.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        tableStatistiques   : Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
        classes             : Liste des classes présentent dans la table des contraintes spatiales.
        executer            : Indiquer si les mises à jour identifiées doivent être exécutées.
        maxIdCmd            : Indiquer le nombre maximum d'identifiants par commande à exécuter.
        maxBatch            : Indiquer le nombre maximum de batch à exécuter.
        serveur             : Nom du serveur utilisé pour exéuter la queue LSF.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        self.nbBatch    : Nombre de batch écrite.
        resultat        : Résultat de la requête BDG.
        """
        
        #Connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Extraire l'usager de la BD
        sUsagerBd = self.CompteBDG.UsagerBd()

        #Initialiser la nombre de batch
        self.nbBatch = 0
        
        #Traiter toutes les classes
        for classe in classes.split(','):     
            #Afficher le message
            arcpy.AddMessage(" ")
            arcpy.AddMessage("-Classe spatiale : " + classe)
            
            #-----------------------------------------------------
            #Vérifier si toutes les contraintes de la table des statistiques sont présentes dans la table des contraintes spatiales
            #-----------------------------------------------------
            arcpy.AddMessage(" -Valider les contraintes spatiales ...")
            #Définir la requête SQL pour extraire les contraintes absentes de la table des contraintes spatiales
            sql = ("select distinct CONTRAINTE from " + tableStatistiques + " where NOM_TABLE='" + classe + "'"
                   " minus "
                   "select distinct groupe as CONTRAINTE from " + tableContraintes + " where NOM_TABLE='" + classe + "'")
            #Exécuter la requête
            #arcpy.AddMessage(" " + sql)
            resultat = self.BDG.query(sql)
            #Vérifier si le résultat
            if resultat:
                #Afficher le nombre d'identifiants absents
                arcpy.AddWarning("  Nombre de contraintes spatiales invalides : " + str(len(resultat)))
                #Traiter toutes les contraintes
                for contrainte in resultat:
                    #Afficher la contrainte invalide
                    arcpy.AddWarning("  " + contrainte[0])
                    
                    #Vérifier si on peut exécuter la validation des contraintes spatiales
                    if executer:
                        #Définir la commande SQL
                        sql = "  DELETE tbl_statistique_element_erreur WHERE NOM_TABLE='" + classe + "' AND CONTRAINTE='" + contrainte[0] + "'"
                        #Afficher la commande
                        arcpy.AddMessage(sql)
                        #Exécuter la commande
                        self.BDG.execute(sql)
                        #Exécuter la commande
                        self.BDG.execute("COMMIT")
            
            #-----------------------------------------------------
            #Traiter toutes les contraintes de la classe
            #-----------------------------------------------------
            #Définir la requête SQL pour extraire les contraintes de la classe
            sql = "SELECT GROUPE FROM " + tableContraintes + " WHERE NOM_TABLE='" + classe + "'"
            #Exécuter la requête
            #arcpy.AddMessage(sql)
            resultat = self.BDG.query(sql)
            
            #Traiter toutes les contraintes de la classe
            for contrainte in resultat:
                #Afficher le message
                arcpy.AddMessage(" -Valider les identifiants de la contrainte spatiale : " + contrainte[0] + " ...")
                
                #-----------------------------------------------------
                #Vérifier si tous les identifiants de la contrainte de la classe sont présents dans la table des statistiques
                #-----------------------------------------------------
                #Définir la requête SQL pour extraire les identifiants absents de la table des statistiques pour cette contrainte
                sql = ("select identifiant from tbl_statistique_element_sommet where identifiant<>'CANADA' and nb_element>0 and NOM_TABLE='" + classe + "'"
                       " minus "
                       "select identifiant from " + tableStatistiques + " where CONTRAINTE = '" + contrainte[0] + "' and NOM_TABLE='" + classe + "'")
                #Exécuter la requête
                #arcpy.AddMessage(" " + sql)
                resultat = self.BDG.query(sql)
                #Vérifier si le résultat
                if resultat:
                    #Afficher le nombre d'identifiants absents
                    arcpy.AddWarning("  Nombre d'identifiants absents : " + str(len(resultat)))
                    
                    #Vérifier si on peut exécuter la validation des contraintes spatiales
                    if executer:
                        #Écrire les commandes pour valider les identifiants selon une classe et une contrainte
                        oValiderStatistiquesErreurs.ecrireBatch(tableContraintes, tableStatistiques, classe, contrainte[0], resultat, maxIdCmd, maxBatch, serveur)
        
        #Fermeture de la connexion de la BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir du traitement
        return

    #-------------------------------------------------------------------------------------
    def ecrireBatch(self, tableContraintes, tableStatistiques, classe, contrainte, resultat, maxIdCmd, maxBatch, serveur):
    #-------------------------------------------------------------------------------------
        """
        Écrire les commandes dans le fichier Batch pour exécuter lea validation des identifiants non traités ou non mis à jour.
        
        Paramètres:
        -----------
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        tableStatistiques   : Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
        classe              : Nom de la classe à valider.
        contrainte          : Nom de la contrainte à valider.
        resultat            : Résultat de la requête contenant la liste des identifiants qui doivent être validés.
        maxIdCmd            : Indiquer le nombre maximum d'identifiants par commande à exécuter.
        maxBatch            : Indiquer le nombre maximum de batch à exécuter.
        serveur             : Nom du serveur utilisé pour exéuter la queue LSF.
        
        Variables:
        ----------

        """
        
        #Vérifier si le nombre maximum de batch n'est pas atteint
        if self.nbBatch < maxBatch: 
            #Définir le répertoire de travail
            repTravail = "\\\\DFSCITSH\\CITS\\Travail\\Gestion_BDSpatiales\\validation"
            
            #Définir les paramètres de la commande
            geodatabase = repTravail + "\\BDRS_PRO_BDG.sde"
            classeDecoupage = "GES_DECOUPAGE_SNRC50K_CANADA_2"
            attributDecoupage = "DATASET_NAME"
            courriel = "michel.pothier@canada.ca"
            
            #Initialiser les identifiants à traiter
            maxIdBatch = len(resultat) + 1
            listeId = ""
            nbIdCmd = 0
            nbIdBatch = 0
            nb = 0
            nbCmd = 0
            
            #Définir la date et l'heure de traitement
            dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            #Compter le nombre de batch
            self.nbBatch = self.nbBatch + 1
            #Définir le nom du fichier batch
            nomBatch = repTravail + "\\Batch_" + dateHeure + "_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".bat"
            #Créer le fichier batch
            batch = open(nomBatch, 'a') 
            
            #Traiter tous les identifiants
            for id in resultat:
                #Initialiser les compteurs
                nb = nb + 1
                nbIdCmd = nbIdCmd + 1
                nbIdBatch = nbIdBatch + 1
                #Définir la liste des Id
                listeId = listeId + "'" + id[0] + "'"
                
                #Vérifier le nombre d'identifiants maximum par traitement
                if nbIdCmd == maxIdCmd or nbIdBatch == maxIdBatch or nb == len(resultat):
                    #Compter le nombre de commandes
                    nbCmd = nbCmd + 1
                    
                    #Définir le nom du rapport d'exécution
                    nomRapport = repTravail + "\\Rapport_[DATE_TIME]_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".txt"
                    #Définir le nom du journal d'exécution
                    nomJournal = repTravail + "\\Journal_[DATE_TIME]_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".log"
                    #Définir le nom de la Geodatabase d'erreurs
                    nomErreur = repTravail + "\\Erreurs_[DATE_TIME]_[DATASET_NAME]_" + contrainte + "_" + str(self.nbBatch) + ".mdb"
                    nomErreur = ""
                    #Définir la commande de validation
                    cmd = (repTravail + "\\ValiderContrainte.exe"
                           ' "' + geodatabase + '"'
                           ' "' + tableContraintes + '"'
                           ' "' + "NOM_TABLE='" + classe + "' AND GROUPE='" + contrainte + "'" + '"'
                           ' "' + classeDecoupage + ":" + attributDecoupage + " IN (" + listeId.replace("''","','") + ")" + '"'
                           ' "' + attributDecoupage + '"'
                           ' "' + nomErreur + '"'
                           ' "' + nomRapport + '"'
                           ' "' + nomJournal + '"'
                           ' "' + courriel + '"'
                           ' "' + tableStatistiques + '"')
                    
                    #Afficher le traitement à exécuter
                    #arcpy.AddMessage(cmd)
                    #Écriture du fichier batch
                    batch.write("\n" + cmd + "\n")
                    
                    #Initialiser les identifiants à traiter
                    listeId = ""
                    nbIdCmd = 0
                    
                    #Afficher le traitement à exécuter
                    #arcpy.AddMessage("total:" + str(len(resultat)))
                    #arcpy.AddMessage("maxIdCmd:" + str(maxIdCmd))
                    #arcpy.AddMessage("maxIdBatch:" + str(maxIdBatch))
                    #arcpy.AddMessage("nb:" + str(nb))
                    #arcpy.AddMessage("nbIdCmd:" + str(nbIdCmd))
                    #arcpy.AddMessage("nbIdBatch:" + str(nbIdBatch))
                    #arcpy.AddMessage("listeId:" + listeId)
                    
                    #Fermer le fichier batch
                    batch.close()
                    
                    #Définir la Job à lancer
                    job = 'plink lsf bsub -q qTest -m ' + serveur + ' -oo "' + nomBatch.replace("\\","\\\\").replace(".bat","_lsf.log") + '" "' + nomBatch.replace("\\","\\\\") + '"'
                    #Afficher la job à lancer
                    arcpy.AddMessage('  ' + job)
                    #Exécuter la job à lancer
                    process = subprocess.Popen(job, shell=False)
                    
                    #Initialiser les identifiants à traiter
                    nbIdBatch = 0
                    
                    #Vérifier si le nombre maximum de batch n'est pas atteint
                    if self.nbBatch == maxBatch:
                        #Sortir de la fonction
                        return
                    
                    #Vérifier si tous les identifiants ont été traités
                    if nb < len(resultat):
                        #----------------------------------------------------------
                        #Afficher le message d'écriture du fichier de traitement de validation pour le travail
                        #----------------------------------------------------------
                        #arcpy.AddMessage(" ")
                        #arcpy.AddMessage("- Créer le fichier batch de traitement de validation spatiale ...")  
                        #Définir la date et l'heure de traitement
                        dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        #Compter le nombre de batch
                        self.nbBatch = self.nbBatch + 1
                        #Définir le nom du fichier batch
                        nomBatch = repTravail + "\\Batch_" + dateHeure + "_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".bat"
                        #Créer le fichier batch
                        batch = open(nomBatch, 'a')
        
        #Sortir du traitement
        return
 
#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "BDRS_PRO"
        tableContraintes = "CONTRAINTE_INTEGRITE_SPATIALE"
        tableStatistiques = "TBL_STATISTIQUE_ELEMENT_ERREUR"
        classes = ""
        executer = False
        maxIdCmd = 500
        maxBatch = 100
        serveur = "s-she-fermat"

        # Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            if sys.argv[2] <> '#':
                tableContraintes = sys.argv[2].upper()
         
        if len(sys.argv) > 3:
            if sys.argv[3] <> '#':
                tableStatistiques = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> '#':
                classes = sys.argv[4].replace(";",",")
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> '#':
                executer = sys.argv[5].upper()=="TRUE"
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> '#':
                maxIdCmd = int(sys.argv[6])
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> '#':
                maxBatch = int(sys.argv[7])
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> '#':
                serveur = sys.argv[8].lower()
        
        #Définir l'objet pour valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales
        oValiderStatistiquesErreurs = ValiderStatistiquesErreurs()
        
        #Valider les paramètres obligatoires
        oValiderStatistiquesErreurs.validerParamObligatoire(env, tableContraintes, tableStatistiques, classes)
        
        #Exécuter le traitement pour valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales
        oValiderStatistiquesErreurs.executer(env, tableContraintes, tableStatistiques, classes, executer, maxIdCmd, maxBatch, serveur)
        
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