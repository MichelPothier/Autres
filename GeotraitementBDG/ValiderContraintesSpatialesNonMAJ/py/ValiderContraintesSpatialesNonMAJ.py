#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : ValiderContrainteSpatialesNonMAJ.py
# Auteur    : Michel Pothier
# Date      : 20 juin 2018

""" Outil qui permet de valider les contraintes spatiales des donn�es non mis � jour en fonction d'une classe et une contrainte spatiale et d'une table de statistiques d'erreurs.

    Param�tres d'entr�es:
    ---------------------
    geodatabase         : Nom de la g�odatabase contenant les tables spatiales.
                          d�faut="Database Connections\BDRS_PRO_BDG_DBA.sde"
    classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de d�coupage.
                          d�faut="GES_DECOUPAGE_SNRC50K_CANADA_2"
    attributDecoupage   : Nom de l'attribut de la classe de d�coupage contenant les identifiants de d�coupage.
                          d�faut="DATASET_NAME"
    tableErreurs        : Nom de la table contenant les statistiques d'erreurs.
                          d�faut="TBL_STATISTIQUE_ELEMENT_ERREUR"
    tableContraintes    : Nom de la table contenant les contraintes spatiales.
                          d�faut : CONTRAINTE_INTEGRITE_SPATIALE
    tableLivraisons     : Nom de la table contenant les livraisons des jeux de donn�es.
                          d�faut="SER_RECONCILE_LOG"
    classe              : Nom de la classe spatiale � valider.
                          d�faut=""
    contrainte          : Nom de la contrainte spatiale � valider.
                          d�faut=""
    courriel            : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
                          d�faut = michel.pothier@canada.ca;odette.trottier@canada.ca
    maxIdCmd            : Nombre maximum d'identifiants dans un traitement.
                          d�faut=100
    maxBatch            : Nombre maximum de batch ex�cut� simultan�ment.
                          d�faut=10
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  Ex: 0=Succ�s, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 

    Usage:
        ValiderContrainteSpatialesNonMAJ.py geodatabase classeDecoupage attributDecoupage tableErreurs tableLivraisons classe contrainte courriel maxIdCmd maxBatch

    Exemple:
        ValiderContrainteSpatialesNonMAJ.py "Database Connections\BDRS_PRO_BDG_DBA.sde" GES_DECOUPAGE_SNRC50K_2 DATASET_NAME TBL_STATISTIQUE_ELEMENT_ERREUR CONTRAINTE_INTEGRITE_SPATIALE SER_RECONCILE_LOG BDG_COURBE_NIVEAU_1 EquidistanceCourbe_ELEVATION
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderContraintesSpatialesNonMAJ.py 1173 2018-06-27 19:50:03Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, subprocess, traceback

#*******************************************************************************************
class ValiderContrainteSpatialesNonMAJ(object):
#*******************************************************************************************
    """ Valider l'int�grit� des donn�es spatiales non mis � jour en fonction d'une classe et une contrainte spatiale et d'une table de statistiques d'erreurs.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider l'int�grit� des donn�es spatiales non trait�es.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        
        """
        
        #D�finir la g�odatabase par d�faut
        arcpy.env.workspace = "Database Connections\BDRS_PRO_BDG_DBA.sde"
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, geodatabase, classeDecoupage, attributDecoupage, tableErreurs, tableContraintes, tableLivraisons, classe, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        geodatabase         : Nom de la g�odatabase contenant les tables spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de d�coupage.
        attributDecoupage   : Nom de l'attribut de la classe de d�coupage contenant les identifiants de d�coupage.
        tableErreurs        : Nom de la table contenant les statistiques d'erreurs.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        tableLivraisons     : Nom de la table contenant les livraisons des jeux de donn�es.
        classe              : Nom de la classe spatiale � valider.
        contrainte          : Nom de la contrainte spatiale � valider.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(geodatabase) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'geodatabase')

        if (len(classeDecoupage) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'classeDecoupage')

        if (len(attributDecoupage) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'attributDecoupage')

        if (len(tableErreurs) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'tableErreurs')

        if (len(tableContraintes) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'tableContraintes')

        if (len(tableLivraisons) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'tableLivraisons')

        if (len(classe) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'classe')

        if (len(contrainte) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'contrainte')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, geodatabase, classeDecoupage, attributDecoupage, tableErreurs, tableContraintes, tableLivraisons, classe, contrainte, courriel, maxIdCmd, maxBatch):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider l'int�grit� des donn�es spatiales non mis � jour en fonction d'une classe et une contrainte spatiale et d'une table de statistiques d'erreurs.
        
        Param�tres:
        -----------
        geodatabase         : Nom de la g�odatabase contenant les tables spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de d�coupage.
        attributDecoupage   : Nom de l'attribut de la classe de d�coupage contenant les identifiants de d�coupage.
        tableErreurs        : Nom de la table contenant les statistiques d'erreurs.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        tableLivraisons     : Nom de la table contenant les livraisons des jeux de donn�es.
        classe              : Nom de la classe spatiale � valider.
        contrainte          : Nom de la contrainte spatiale � valider.
        courriel            : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
        maxIdCmd            : Nombre maximum d'identifiants dans un traitement.
        maxBatch            : Nombre maximum de batch ex�cut� simultan�ment.
        
        Variables:
        ----------

        """
        #D�finir le r�pertoire de travail
        repTravail = "D:"
        
        #Permet de remplacer les fichier existants
        arcpy.env.overwriteOutput = True 
        
        #D�finir la g�odatabase
        arcpy.env.workspace = geodatabase
        
        #D�finir la G�odatabase de la classe des contraintes
        bdg = arcpy.ArcSDESQLExecute(geodatabase)
        
        #----------------------------------------------------------        
        #Cr�er la requ�te SQL pour extraire les identifiants � traiter par classe et contrainte.
        #----------------------------------------------------------
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des identifiants de la table des statistiques d'erreurs non mis � jour")
        sql = ("SELECT DISTINCT A.IDENTIFIANT FROM " + tableErreurs + " A, (SELECT IDENTIFIANT, MAX(DATE_FIN) AS DATE_FIN FROM " + tableLivraisons + " GROUP BY IDENTIFIANT) B "
               "WHERE A.NOM_TABLE='" + classe + "' AND A.CONTRAINTE='" + contrainte + "' AND A.IDENTIFIANT=B.IDENTIFIANT AND B.DATE_FIN>A.DT_M AND A.NB_ELEMENT_TOTAL>0 ORDER BY A.IDENTIFIANT")
        
        #Afficher la commande SQL           
        arcpy.AddMessage(sql)
        #Extraire la liste des classes dans la table des contraintes
        resultat = bdg.execute(sql)
                
        # Fermeture de la G�odatabase
        arcpy.AddMessage("- Fermeture de la G�odatabase")
        del bdg

        #V�rifier aucun identifiant � traiter
        if type(resultat) is not list:
            #Retourner une erreur
            arcpy.AddMessage(" ")
            arcpy.AddWarning("ATTENTION : Aucun identifiant � traiter!")
            arcpy.AddMessage(" ")
        
        #Si un ou plusieurs identifiants � traiter
        else:
            #Initialiser les identifiants � traiter
            maxIdBatch = (len(resultat) / maxBatch) + 1
            listeId = ""
            nbIdCmd = 0
            nbIdBatch = 0
            nb = 0
            nbCmd = 0
            nbBatch = 0
            
            #----------------------------------------------------------
            #Afficher le message d'�criture du fichier de traitement de validation pour le travail
            #----------------------------------------------------------
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Cr�er le fichier batch de traitement de validation spatiale ...") 
            #D�finir la date et l'heure de traitement
            dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            #Compter le nombre de batch
            nbBatch = nbBatch + 1
            #D�finir le nom du fichier batch
            nomBatch = repTravail + "\\Batch_" + dateHeure + "_" + contrainte + "_" + str(nbBatch) + ".bat"
            #Cr�er le fichier batch
            batch = open(nomBatch, 'a')
            
            #Traiter tous les identifiants correspondant au type de travail
            for id in resultat:
                #Initialiser les compteurs
                nb = nb + 1
                nbIdCmd = nbIdCmd + 1
                nbIdBatch = nbIdBatch + 1
                #D�finir la liste des Id
                listeId = listeId + "'" + id[0] + "'"
                
                #V�rifier le nombre d'identifiants maximum par traitement
                if nbIdCmd == maxIdCmd or nbIdBatch == maxIdBatch or nb == len(resultat):
                    #Compter le nombre de commandes
                    nbCmd = nbCmd + 1
                    
                    #D�finir le nom du rapport d'ex�cution
                    nomRapport = repTravail + "\\Rapport_[DATE_TIME]_" + contrainte + "_" + str(nbCmd) + ".txt"
                    #D�finir le nom du journal d'ex�cution
                    nomJournal = repTravail + "\\Journal_[DATE_TIME]_" + contrainte + "_" + str(nbCmd) + ".log"
                    #D�finir le nom de la Geodatabase d'erreurs
                    nomErreur = repTravail + "\\Erreurs_[DATE_TIME]_[DATASET_NAME]_" + contrainte + "_" + str(nbCmd) + ".mdb"
                    #D�finir la commande de validation
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
                           ' "' + tableErreurs + '"')
                    
                    #Afficher le traitement � ex�cuter
                    arcpy.AddMessage(cmd)
                    #�criture du fichier batch
                    batch.write("\n" + cmd + "\n")
                    
                    #Initialiser les identifiants � traiter
                    listeId = ""
                    nbIdCmd = 0

                #V�rifier le nombre d'identifiants maximum par batch
                if nbIdBatch == maxIdBatch or nb == len(resultat):
                    #Afficher le traitement � ex�cuter
                    #arcpy.AddMessage("total:" + str(len(resultat)))
                    #arcpy.AddMessage("maxIdCmd:" + str(maxIdCmd))
                    #arcpy.AddMessage("maxIdBatch:" + str(maxIdBatch))
                    #arcpy.AddMessage("nb:" + str(nb))
                    #arcpy.AddMessage("nbIdCmd:" + str(nbIdCmd))
                    #arcpy.AddMessage("nbIdBatch:" + str(nbIdBatch))
                    #arcpy.AddMessage("listeId:" + listeId)
                    
                    #Fermer le fichier batch
                    batch.close()   
                    #Ex�cuter le fichier batch
                    arcpy.AddWarning(nomBatch)
                    process = subprocess.Popen(nomBatch, shell=False)
                    
                    #V�rifier le nombre d'identifiants maximum par batch
                    if nb < len(resultat):
                       #----------------------------------------------------------
                        #Afficher le message d'�criture du fichier de traitement de validation pour le travail
                        #----------------------------------------------------------
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage("- Cr�er le fichier batch de traitement de validation spatiale ...")  
                        #D�finir la date et l'heure de traitement
                        dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        #Compter le nombre de batch
                        nbBatch = nbBatch + 1
                        #D�finir le nom du fichier batch
                        nomBatch = repTravail + "\\Batch_" + dateHeure + "_" + contrainte + "_" + str(nbBatch) + ".bat"
                        #Cr�er le fichier batch
                        batch = open(nomBatch, 'a')
                        
                        #Initialiser les identifiants � traiter
                        nbIdBatch = 0
        
            #----------------------------------------------------------
            #Afficher le nombre d'identifiant et le nombre de traitement � effectuer
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Valeur par d�faut
        geodatabase = "Database Connections\BDRS_PRO_BDG_DBA.sde"
        classeDecoupage = "GES_DECOUPAGE_SNRC50K_2"
        attributDecoupage = "DATASET_NAME"
        tableErreurs = "TBL_STATISTIQUE_ELEMENT_ERREUR"
        tableContraintes = "CONTRAINTE_INTEGRITE_SPATIALE"
        tableLivraisons = "SER_RECONCILE_LOG"
        classe = ""
        contrainte = ""
        courriel = ""   
        maxIdCmd = 100
        maxBatch = 10
        
        # Lecture des param�tres
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
            tableLivraisons = sys.argv[6]
        
        if len(sys.argv) > 7:
            classe = sys.argv[7].upper()
        
        if len(sys.argv) > 8:
            contrainte = sys.argv[8].split(":")[0]
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                courriel = sys.argv[9]
        
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                maxIdCmd = int(sys.argv[10])
        
        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                maxBatch = int(sys.argv[11])
        
        #D�finir l'objet pour valider l'int�grit� des donn�es spatiales non mis � jour dans la BDG selon une table de contraintes spatiales.
        oValiderContrainteSpatialesNonMAJ = ValiderContrainteSpatialesNonMAJ()
        
        #Valider les param�tres obligatoires
        oValiderContrainteSpatialesNonMAJ.validerParamObligatoire(geodatabase, classeDecoupage, attributDecoupage, tableContraintes, tableErreurs, tableLivraisons, classe, contrainte)
        
        #Ex�cuter le traitement pour valider l'int�grit� des donn�es spatiales non mis � jour dans la BDG selon une table de contraintes spatiales.
        oValiderContrainteSpatialesNonMAJ.executer(geodatabase, classeDecoupage, attributDecoupage, tableErreurs, tableContraintes, tableLivraisons, classe, contrainte, courriel, maxIdCmd, maxBatch)
    
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