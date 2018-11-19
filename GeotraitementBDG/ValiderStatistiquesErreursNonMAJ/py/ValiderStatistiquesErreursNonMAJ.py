#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       :ValiderStatistiquesErreursNonMAJ.py
# Auteur    : Michel Pothier
# Date      : 01 Août 2018

"""
Outil qui permet de valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales par identifiant, par classe et par contrainte.
-Vérifier si toutes les statistiques sont à jour par rapport à la table des livraisons des jeux de données.
-Les statistiques d'erreurs non à jour seront mis à jour en lançant les traitements de validation des contraintes spatiales via LSF.

Paramètres d'entrées:
----------------------
env                 OB  Type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV].
                        défaut = BDRS_PRO
tableContraintes    OB  Nom de la table contenant les contraintes spatiales.
                        défaut : CONTRAINTE_INTEGRITE_SPATIALE
tableStatistiques   OB  Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
                        défaut : TBL_STATISTIQUE_ELEMENT_ERREUR
tableLivraisons     OB  Nom de la table contenant les jeux de données livrés.
                        défaut : SER_RECONCILE_LOG
contraintes         OB  Liste des contraintes présentent dans la table des contraintes spatiales.
                        défaut :
executer            OP  Indiquer si les identifiants non traités ou non mis à jour doivent être exécutées.
                        défaut : False
maxIdCmd            OP  Indiquer le nombre maximum d'identifiants par commande à exécuter.
                        défaut : 500
maxBatch            OP  Indiquer le nombre maximum de batch à exécuter.
                        défaut : 10
serveur             OP  Nom du serveur utilisé pour exéuter la queue LSF.
                        défaut : s-she-dumas

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    ValiderStatistiquesErreurs.py env tableContraintes tableStatistiques tableLivraisons classes executer maxIdCmd maxBatch serveur

Exemple:
    ValiderStatistiquesErreurs.py BDRS_PRO # # # NHN_HHYD_WATERBODY_2;NHN_HNET_NETWORK_LINEAR_FLOW True 500 10 s-she-dumas

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderStatistiquesErreursNonMAJ.py 1203 2018-08-02 13:20:47Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, subprocess, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ValiderStatistiquesErreursNonMAJ(object):
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
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        # Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        #Définir la date de début
        self.dateDebut = datetime.datetime.now().replace(microsecond=0)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, tableContraintes, tableStatistiques, tableLivraisons, contraintes):
    #-------------------------------------------------------------------------------------
        """
        Valider les paramètres obligatoires.
        
        Paramètres:
        -----------
        env                : Type d'environnement.
        tableContraintes   : Nom de la table contenant les contraintes spatiales.
        tableStatistiques  : Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
        tableLivraisons    : Nom de la table contenant les jeux de données livrés.
        contraintes        : Liste des contraintes présentent dans la table des contraintes spatiales.
        
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
        
        if (len(tableLivraisons) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tableLivraisons')
        
        if (len(contraintes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'contraintes')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, tableContraintes, tableStatistiques, tableLivraisons, contraintes, executer, maxIdCmd, maxBatch, serveur):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales par identifiant, par classe et par contrainte.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        tableStatistiques   : Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
        tableLivraisons     : Nom de la table contenant les jeux de données livrés.
        contraintes         : Liste des contraintes présentent dans la table des contraintes spatiales.
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
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Extraire l'usager de la BD
        sUsagerBd = self.CompteSib.UsagerBd()
        
        #Initialiser la nombre de batch
        self.nbBatch = 0
        
        #Traiter toutes les classes
        for contrainte in contraintes.split(','):     
            #Afficher le message
            arcpy.AddMessage(" ")
            arcpy.AddMessage(" -Valider les identifiants de la contrainte spatiale : " + contrainte + " ...")
            
            #-----------------------------------------------------
            #Vérifier si tous les identifiants de la contrainte dans la table des statistiques sont à jour par rapport à la table des livraisons
            #-----------------------------------------------------
            #Définir la requête SQL pour extraire les identifiants de la contrainte non à jour
            sql = ("SELECT DISTINCT AA.IDENTIFIANT, AA.NOM_TABLE"
                   "  FROM (SELECT A.IDENTIFIANT, C.FEAT_TYPE_NAME_DATABASE AS NOM_TABLE, A.DATE_FIN AS DT_M"
                   "          FROM SER_RECONCILE_LOG@BDG_DBA A," 
                   "               (SELECT IDENTIFIANT, MAX(DATE_FIN) AS DATE_FIN FROM " + tableLivraisons + "@BDG_DBA GROUP BY IDENTIFIANT) B,"
                   "               (SELECT DISTINCT FT.FEAT_TYPE_NAME_DATABASE, FT.FEAT_TYPE_CODE_BD FROM FEAT_CATALOGUE@BDG_VIEW FC, FEAT_TYPE@BDG_VIEW FT WHERE FC.FEAT_CATAL_TYPE=1 AND FC.FEAT_CATAL_ID=FT.FEAT_CATAL_FK and FT.FEAT_TYPE_NAME_DATABASE IS NOT NULL) C,"
                   "               (SELECT DISTINCT LE.CD_ELEM_TOPO, LO.NO_LOT FROM F502_PS PS, F502_LE LE, F503_TR TR, F601_LO LO WHERE PS.NO_MAP=TR.NO_MAP AND PS.NO_MAP=LE.NO_MAP AND TR.NO_LOT=LO.NO_LOT) D"
                   "         WHERE A.IDENTIFIANT=B.IDENTIFIANT AND A.DATE_FIN=B.DATE_FIN AND C.FEAT_TYPE_CODE_BD IN (D.CD_ELEM_TOPO) AND A.NO_LOT=D.NO_LOT) AA,"
                   "       (SELECT IDENTIFIANT, NOM_TABLE, DT_M"
                   "          FROM " + tableStatistiques + "@BDG_DBA" 
                   "         WHERE CONTRAINTE='" + contrainte + "' AND NB_ELEMENT_TOTAL>0) BB"
                   " WHERE AA.IDENTIFIANT=BB.IDENTIFIANT AND AA.NOM_TABLE=BB.NOM_TABLE AND AA.DT_M>BB.DT_M"
                   " ORDER BY AA.NOM_TABLE,AA.IDENTIFIANT")
            #Exécuter la requête
            #arcpy.AddMessage(" " + sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier si le résultat
            if resultat:
                #Afficher le nombre d'identifiants non à jour
                arcpy.AddWarning("  Nombre d'identifiants non à jour : " + str(len(resultat)))
                
                #Vérifier si on peut exécuter la validation des contraintes spatiales
                if executer:
                    #Écrire les commandes pour valider les identifiants selon une classe et une contrainte
                    oValiderStatistiquesErreursNonMAJ.ecrireBatch(tableContraintes, tableStatistiques, tableLivraisons, contrainte, resultat, maxIdCmd, maxBatch, serveur)
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()   
        
        #Sortir du traitement
        return

    #-------------------------------------------------------------------------------------
    def ecrireBatch(self, tableContraintes, tableStatistiques, tableLivraisons, contrainte, resultat, maxIdCmd, maxBatch, serveur):
    #-------------------------------------------------------------------------------------
        """
        Écrire les commandes dans le fichier Batch pour exécuter lea validation des identifiants non mis à jour.
        
        Paramètres:
        -----------
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        tableStatistiques   : Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
        tableLivraisons     : Nom de la table contenant les jeux de données livrés.
        contrainte          : Nom de la contrainte à valider.
        resultat            : Résultat de la requête contenant la liste des identifiants qui doivent être validés.
        maxIdCmd            : Indiquer le nombre maximum d'identifiants par commande à exécuter.
        maxBatch            : Indiquer le nombre maximum de batch à exécuter.
        serveur             : Nom du serveur utilisé pour exéuter la queue LSF.
        
        Variables:
        ----------
        classe              : Nom de la classe à valider.
        """
        
        #Vérifier si le nombre maximum de batch n'est pas atteint
        if self.nbBatch < maxBatch: 
            #Initialiser les identifiants à traiter
            maxIdBatch = len(resultat) + 1
            listeId = ""
            nbIdCmd = 0
            nbIdBatch = 0
            nb = 0
            nbCmd = 0
            classe = ""
            
            #Définir la date et l'heure de traitement
            dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            #Traiter tous les identifiants
            for item in resultat:
                #Vérifier si la classe précédente est absente
                if classe == "":
                    #Définir la classe
                    classe = item[1]
                
                #Vérifier le nombre d'identifiants maximum par traitement
                if nbIdCmd == maxIdCmd or nbIdBatch == maxIdBatch or item[1] <> classe:
                    #Écrire et exécuter la batch
                    oValiderStatistiquesErreursNonMAJ.executerBatch(tableContraintes, tableStatistiques, tableLivraisons, classe, contrainte, dateHeure, listeId, serveur)
                    
                    #Initialiser les identifiants à traiter
                    nbIdBatch = 0
                    listeId = ""
                    nbIdCmd = 0
                    nbCmd = nbCmd + 1
                    
                    #Afficher le traitement à exécuter
                    #arcpy.AddMessage("total:" + str(len(resultat)))
                    #arcpy.AddMessage("maxIdCmd:" + str(maxIdCmd))
                    #arcpy.AddMessage("maxIdBatch:" + str(maxIdBatch))
                    #arcpy.AddMessage("nb:" + str(nb))
                    #arcpy.AddMessage("nbIdCmd:" + str(nbIdCmd))
                    #arcpy.AddMessage("nbIdBatch:" + str(nbIdBatch))
                    #arcpy.AddMessage("listeId:" + listeId)
                    
                    #Vérifier si le nombre maximum de batch n'est pas atteint
                    if self.nbBatch == maxBatch:
                        #Sortir de la fonction
                        return
                
                #Initialiser les compteurs
                nb = nb + 1
                nbIdCmd = nbIdCmd + 1
                nbIdBatch = nbIdBatch + 1
                #Définir la liste des Id
                listeId = listeId + "'" + item[0] + "'"
                #Définir le nom de la classe
                classe = item[1]
            
            #Vérifier le nombre d'identifiants maximum par traitement
            if nb == len(resultat):
                #Écrire et exécuter la batch
                oValiderStatistiquesErreursNonMAJ.executerBatch(tableContraintes, tableStatistiques, tableLivraisons, classe, contrainte, dateHeure, listeId, serveur)
        
        #Sortir du traitement
        return
 
    #-------------------------------------------------------------------------------------
    def executerBatch(self, tableContraintes, tableStatistiques, tableLivraisons, classe, contrainte, dateHeure, listeId, serveur):
    #-------------------------------------------------------------------------------------
        """
        Écrire et exécuter le fichier Batch.
        
        Paramètres:
        -----------
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        tableStatistiques   : Nom de la table contenant les statistiques d'erreurs des contraintes spatiales.
        tableLivraisons     : Nom de la table contenant les jeux de données livrés.
        classe              : Nom de la classe à valider.
        contrainte          : Nom de la contrainte à valider.
        dateHeure           : Date et heure de début de traitement.
        listeId             : Liste des identifiants à traiter.
        serveur             : Nom du serveur utilisé pour exéuter la queue LSF.
        
        Variables:
        ----------
        repTravail          : Répertoire de travail dans lequel les fichier seront créés.

        """
        #Définir le répertoire de travail
        repTravail = "\\\\DFSCITSH\\CITS\\Travail\\Gestion_BDSpatiales\\validation"
        
        #Définir les paramètres de la commande
        geodatabase = repTravail + "\\BDRS_PRO_BDG.sde"
        classeDecoupage = "GES_DECOUPAGE_SNRC50K_CANADA_2"
        attributDecoupage = "DATASET_NAME"
        courriel = "michel.pothier@canada.ca"
            
        #Compter le nombre de batch
        self.nbBatch = self.nbBatch + 1
        #Définir le nom du fichier batch
        nomBatch = repTravail + "\\Batch_" + dateHeure + "_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".bat"
        #Créer le fichier batch
        batch = open(nomBatch, 'a')
        
        #Définir le nom du rapport d'exécution
        nomRapport = repTravail + "\\Rapport_[DATE_TIME]_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".txt"
        #Définir le nom du journal d'exécution
        nomJournal = repTravail + "\\Journal_[DATE_TIME]_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".log"
        #Définir le nom de la Geodatabase d'erreurs
        nomErreur = repTravail + "\\Erreurs_[DATE_TIME]_" + classe + "_" + contrainte + "_" + str(self.nbBatch) + ".mdb"
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
        
        #Fermer le fichier batch
        batch.close()
        
        #Définir la Job à lancer
        job = 'plink lsf bsub -q qTest -m ' + serveur + ' -oo "' + nomBatch.replace("\\","\\\\").replace(".bat","_lsf.log") + '" "' + nomBatch.replace("\\","\\\\") + '"'
        #Afficher la job à lancer
        arcpy.AddMessage('  ' + job)
        #Exécuter la job à lancer
        process = subprocess.Popen(job, shell=False)
        
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
        tableLivraisons = "SER_RECONCILE_LOG"
        contraintes = ""
        executer = False
        maxIdCmd = 500
        maxBatch = 10
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
                tableLivraisons = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> '#':
                contraintes = sys.argv[5].replace(";",",")
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> '#':
                executer = sys.argv[6].upper()=="TRUE"
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> '#':
                maxIdCmd = int(sys.argv[7])
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> '#':
                maxBatch = int(sys.argv[8])
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> '#':
                serveur = sys.argv[9].lower()
        
        #Définir l'objet pour valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales
        oValiderStatistiquesErreursNonMAJ = ValiderStatistiquesErreursNonMAJ()
        
        #Valider les paramètres obligatoires
        oValiderStatistiquesErreursNonMAJ.validerParamObligatoire(env, tableContraintes, tableStatistiques, tableLivraisons, contraintes)
        
        #Exécuter le traitement pour valider la table des statistiques d'erreurs des contraintes d'intégrité spatiales
        oValiderStatistiquesErreursNonMAJ.executer(env, tableContraintes, tableStatistiques, tableLivraisons, contraintes, executer, maxIdCmd, maxBatch, serveur)
        
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