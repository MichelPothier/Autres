#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : ValiderContrainteSpatialesNonTraitees.py
# Auteur    : Michel Pothier
# Date      : 28 février 2018

""" Outil qui permet de valider les contraintes spatiales des données non traitées en fonction d'une classe et une contrainte spatiale et d'une table de statistiques d'erreurs.

    Paramètres d'entrées:
    ---------------------
    geodatabase         : Nom de la géodatabase contenant les tables spatiales.
                          défaut="Database Connections\BDRS_PRO_BDG_DBA.sde"
    classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de découpage.
                          défaut="GES_DECOUPAGE_SNRC50K_CANADA_2"
    attributDecoupage   : Nom de l'attribut de la classe de découpage contenant les identifiants de découpage.
                          défaut="DATASET_NAME"
    tableErreurs        : Nom de la table contenant les statistiques d'erreurs.
                          défaut="TBL_STATISTIQUE_ELEMENT_ERREUR"
    tableContraintes    : Nom de la table contenant les contraintes spatiales.
                          défaut="CONTRAINTE_INTEGRITE_SPATIALE"
    classe              : Nom de la classe spatiale à valider.
                          défaut=""
    contrainte          : Nom de la contrainte spatiale à valider.
                          défaut=""
    courriel            : Adresse courriel utilisée pour envoyer le rapport d'exécution.
                          défaut = michel.pothier@canada.ca;odette.trottier@canada.ca
    date                : Date de traitement des données BDG (ex:2015-12-15 16:21:54).
                          défaut=<Ceux non traitées sans aucune entrée dans la table des statistiques d'erreurs>
    maxIdCmd            : Nombre maximum d'identifiants dans un traitement.
                          défaut=100
    maxBatch            : Nombre maximum de batch exécuté simultanément.
                          défaut=10
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du résultat de l'exécution du programme.
                  Ex: 0=Succès, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 

    Usage:
        ValiderContrainteSpatialesNonTraitees.py geodatabase classeDecoupage attributDecoupage tableErreurstableContraintes  classe contrainte courriel date

    Exemple:
        ValiderContrainteSpatialesNonTraitees.py "Database Connections\BDRS_PRO_BDG_DBA.sde" GES_DECOUPAGE_SNRC50K_2 DATASET_NAME TBL_STATISTIQUE_ELEMENT_ERREUR CONTRAINTE_INTEGRITE_SPATIALE BDG_COURBE_NIVEAU_1 EquidistanceCourbe_ELEVATION
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderContraintesSpatialesNonTraitees.py 1172 2018-06-27 19:48:38Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, subprocess, traceback

#*******************************************************************************************
class ValiderContrainteSpatialesNonTraitees(object):
#*******************************************************************************************
    """ Valider l'intégrité des données spatiales non traitées en fonction d'une classe et une contrainte spatiale et d'une table de statistiques d'erreurs.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider l'intégrité des données spatiales non traitées.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        
        """
        
        #Définir la géodatabase par défaut
        arcpy.env.workspace = "Database Connections\BDRS_PRO_BDG_DBA.sde"
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, geodatabase, classeDecoupage, attributDecoupage, tableErreurs, tableContraintes, classe, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        geodatabase         : Nom de la géodatabase contenant les tables spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de découpage.
        attributDecoupage   : Nom de l'attribut de la classe de découpage contenant les identifiants de découpage.
        tableErreurs        : Nom de la table contenant les statistiques d'erreurs.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        classe              : Nom de la classe spatiale à valider.
        contrainte          : Nom de la contrainte spatiale à valider.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(geodatabase) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'geodatabase')

        if (len(classeDecoupage) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'classeDecoupage')

        if (len(attributDecoupage) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'attributDecoupage')

        if (len(tableErreurs) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tableErreurs')

        if (len(tableContraintes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tableContraintes')

        if (len(classe) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'classe')

        if (len(contrainte) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'contrainte')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, geodatabase, classeDecoupage, attributDecoupage, tableErreurs, tableContraintes, classe, contrainte, courriel, date, maxIdCmd, maxBatch):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider l'intégrité des données spatiales non traitées en fonction d'une classe et une contrainte spatiale et d'une table de statistiques d'erreurs.
        
        Paramètres:
        -----------
        geodatabase         : Nom de la géodatabase contenant les tables spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de découpage.
        attributDecoupage   : Nom de l'attribut de la classe de découpage contenant les identifiants de découpage.
        tableErreurs        : Nom de la table contenant les statistiques d'erreurs.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        classe              : Nom de la classe spatiale à valider.
        contrainte          : Nom de la contrainte spatiale à valider.
        courriel            : Adresse courriel utilisée pour envoyer le rapport d'exécution.
        date                : Date de traitement de VALIDATION des données BDG (ex:2015-12-15 16:21:54).
        maxIdCmd            : Nombre maximum d'identifiants dans un traitement.
        maxBatch            : Nombre maximum de batch exécuté simultanément.
        
        Variables:
        ----------

        """
        #Définir le répertoire de travail
        repTravail = "D:"
        
        #Permet de remplacer les fichier existants
        arcpy.env.overwriteOutput = True 
        
        #Définir la géodatabase
        arcpy.env.workspace = geodatabase
        
        #Définir la Géodatabase de la classe des contraintes
        bdg = arcpy.ArcSDESQLExecute(geodatabase)
        
        #----------------------------------------------------------        
        #Créer la requête SQL pour extraire les identifiants à traiter par classe et contrainte.
        #----------------------------------------------------------
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des identifiants de la table des statistiques d'erreurs non traités")
        sql = ("SELECT IDENTIFIANT FROM TBL_STATISTIQUE_ELEMENT_SOMMET WHERE NB_ELEMENT>0 AND IDENTIFIANT<>'CANADA' AND NOM_TABLE='" + classe + "'"
               " MINUS "
               "SELECT IDENTIFIANT FROM TBL_STATISTIQUE_ELEMENT_ERREUR WHERE CONTRAINTE='" + contrainte + "' AND NOM_TABLE='" + classe + "'")
        #Vérifier si la date est spécifiée
        if len(date) > 0:
            #Ajouter la date dans la requête
            sql = sql + " AND DT_M>=TO_DATE('" + date + "','yyyy-mm-dd HH24:MI:SS')"
        
        #Ajouter la commande pour trier les identifiants dans la SQL
        sql = sql  + " ORDER BY IDENTIFIANT"
        
        #Extraire la liste des classes dans la table des contraintes
        arcpy.AddMessage(sql)
        resultat = bdg.execute(sql)
        
        # Fermeture de la Géodatabase
        arcpy.AddMessage("- Fermeture de la Géodatabase")
        del bdg
        
        #Vérifier aucun identifiant à traiter
        if type(resultat) is not list:
            #Retourner une erreur
            arcpy.AddMessage(" ")
            arcpy.AddWarning("ATTENTION : Aucun identifiant à traiter!")
            arcpy.AddMessage(" ")
        
        #Si un ou plusieurs identifiants à traiter
        else:        
            #Initialiser les identifiants à traiter
            maxIdBatch = (len(resultat) / maxBatch) + 1
            listeId = ""
            nbIdCmd = 0
            nbIdBatch = 0
            nb = 0
            nbCmd = 0
            nbBatch = 0
            
            #----------------------------------------------------------
            #Afficher le message d'écriture du fichier de traitement de validation pour le travail
            #----------------------------------------------------------
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Créer le fichier batch de traitement de validation spatiale ...") 
            #Définir la date et l'heure de traitement
            dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            #Compter le nombre de batch
            nbBatch = nbBatch + 1
            #Définir le nom du fichier batch
            nomBatch = repTravail + "\\Batch_" + dateHeure + "_" + contrainte + "_" + str(nbBatch) + ".bat"
            #Créer le fichier batch
            batch = open(nomBatch, 'a')
            
            #Traiter tous les identifiants correspondant au type de travail
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
                    nomRapport = repTravail + "\\Rapport_[DATE_TIME]_" + contrainte + "_" + str(nbCmd) + ".txt"
                    #Définir le nom du journal d'exécution
                    nomJournal = repTravail + "\\Journal_[DATE_TIME]_" + contrainte + "_" + str(nbCmd) + ".log"
                    #Définir le nom de la Geodatabase d'erreurs
                    nomErreur = repTravail + "\\Erreurs_[DATE_TIME]_[DATASET_NAME]_" + contrainte + "_" + str(nbCmd) + ".mdb"
                    #Définir la commande de validation
                    cmd = ("D:\\cits\EnvCits\\applications\\gestion_bdg\\pro\\Geotraitement\\exe\\ValiderContrainte.exe"
                           ' "' + geodatabase + '"'
                           ' "' + tableContraintes + '"'
                           ' "' + "NOM_TABLE='" + classe + "' AND GROUPE='" + contrainte + "'" + '"'
                           ' "' + classeDecoupage + ":" + attributDecoupage + " IN (" + listeId.replace("''","','") + ")" + '"'
                           ' "' + attributDecoupage + '"'
                           ' "' + nomErreur + '"'
                           ' "' + nomRapport + '"'
                           ' "' + nomJournal + '"'
                           ' "' + courriel + '"'
                           ' "TBL_STATISTIQUE_ELEMENT_ERREUR"')
                    
                    #Afficher le traitement à exécuter
                    arcpy.AddMessage(cmd)
                    #Écriture du fichier batch
                    batch.write("\n" + cmd + "\n")
                    
                    #Initialiser les identifiants à traiter
                    listeId = ""
                    nbIdCmd = 0

                #Vérifier le nombre d'identifiants maximum par batch
                if nbIdBatch == maxIdBatch or nb == len(resultat):
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
                    #Exécuter le fichier batch
                    arcpy.AddWarning(nomBatch)
                    process = subprocess.Popen(nomBatch, shell=False)
                    
                    #Vérifier le nombre d'identifiants maximum par batch
                    if nb < len(resultat):
                       #----------------------------------------------------------
                        #Afficher le message d'écriture du fichier de traitement de validation pour le travail
                        #----------------------------------------------------------
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage("- Créer le fichier batch de traitement de validation spatiale ...")  
                        #Définir la date et l'heure de traitement
                        dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        #Compter le nombre de batch
                        nbBatch = nbBatch + 1
                        #Définir le nom du fichier batch
                        nomBatch = repTravail + "\\Batch_" + dateHeure + "_" + contrainte + "_" + str(nbBatch) + ".bat"
                        #Créer le fichier batch
                        batch = open(nomBatch, 'a')
                        
                        #Initialiser les identifiants à traiter
                        nbIdBatch = 0
        
        #----------------------------------------------------------
        #Afficher le nombre d'identifiant et le nombre de traitement à effectuer
        #----------------------------------------------------------
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre maximum de batch : " + str(maxBatch))
        arcpy.AddMessage("- Nombre maximum d'identifiants par Batch : " + str(maxIdBatch))
        arcpy.AddMessage("- Nombre maximum d'identifiants par traitements : " + str(maxIdCmd))
        arcpy.AddMessage("- Nombre d'identifiants : " + str(nb))
        arcpy.AddMessage("- Nombre de traitements : " + str(nbCmd))
        arcpy.AddMessage("- Nombre de Batch : " + str(nbBatch))
        arcpy.AddMessage(" ")
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Valeur par défaut
        geodatabase = "Database Connections\BDRS_PRO_BDG_DBA.sde"
        classeDecoupage = "GES_DECOUPAGE_SNRC50K_2"
        attributDecoupage = "DATASET_NAME"
        tableErreurs = "TBL_STATISTIQUE_ELEMENT_ERREUR"
        tableContraintes = "CONTRAINTE_INTEGRITE_SPATIALE"
        classe = ""
        contrainte = ""
        courriel = ""
        date = ""      
        maxIdCmd = 100
        maxBatch = 10
        
        # Lecture des paramètres
        if len(sys.argv) > 1:
            geodatabase = sys.argv[1]
        
        if len(sys.argv) > 2:
            classeDecoupage = sys.argv[2]
        
        if len(sys.argv) > 3:
            attributDecoupage = sys.argv[3]
        
        if len(sys.argv) > 4:
            tableErreurs = sys.argv[4]
        
        if len(sys.argv) > 5:
            tableContraintes = sys.argv[5]
        
        if len(sys.argv) > 6:
            classe = sys.argv[6].upper()
        
        if len(sys.argv) > 7:
            contrainte = sys.argv[7].split(":")[0]
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                courriel = sys.argv[8]
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                date = sys.argv[9]
        
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                maxIdCmd = int(sys.argv[10])
        
        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                maxBatch = int(sys.argv[11])
        
        #Définir l'objet pour valider l'intégrité des données spatiales non traitées dans la BDG selon une table de contraintes spatiales.
        oValiderContrainteSpatialesNonTraitees = ValiderContrainteSpatialesNonTraitees()
        
        #Valider les paramètres obligatoires
        oValiderContrainteSpatialesNonTraitees.validerParamObligatoire(geodatabase, classeDecoupage, attributDecoupage, tableErreurs, tableContraintes, classe, contrainte)
        
        #Exécuter le traitement pour valider l'intégrité des données spatiales non traitées dans la BDG selon une table de contraintes spatiales.
        oValiderContrainteSpatialesNonTraitees.executer(geodatabase, classeDecoupage, attributDecoupage, tableErreurs, tableContraintes, classe, contrainte, courriel, date, maxIdCmd, maxBatch)
    
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