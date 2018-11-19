#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : ValiderIntegriteDonneesSpatialesLivrees.py
# Auteur    : Michel Pothier
# Date      : 16 décembre 2015

""" Outil qui permet de valider l'intégrité des données spatiales livrées dans la BDG selon une table de contraintes spatiales.

    Les actions suivantes sont effectuées pour chaque type de travail à traiter :
    -Créer un layer de découpage dont les éléments sélectionnés sont ceux livrés dans la BDG pour le type de travail traité.
    -Extraire toutes les classes liées au type de travail traité.
    -Lancer l'exécution de la validation des contraintes spatiales selon le layer de découpage et les classes liés au type de travail.

    Paramètres d'entrées:
    ---------------------
    envSib              : Environnement de travail SIB [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                          défaut=SIB_PRO
    geodatabase         : Nom de la géodatabase contenant les tables spatiales.
                          défaut="Database Connections\BDRS_PRO_BDG_DBA.sde"
    tableContraintes    : Nom de la table contenant les contraintes spatiales.
                          défaut=CONTRAINTE_INTEGRITE_SPATIALE
    classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de découpage.
                          défaut=GES_DECOUPAGE_SNRC50K_2
    attributDecoupage   : Nom de l'attribut de la classe de découpage contenant les identifiants de découpage.
                          défaut=DATASET_NAME
    repTravail          : Nom du répertoire de travail.
                          défaut=D:\Erreurs
    dateFin             : Date de fin du traitement de livraison des données BDG (ex:2015-12-15 16:21:54).
                          défaut=<24 heures avant la date et l'heure courante>
    typeTravail         : Liste des types de travaux présents dans la table SER_RECONCILE_LOG et
                          dont les identifiants ont été livrés après la date de fin spécifiée.
                          exemple: CORINT:2
                                   RHN_ANOM_2:33
                          défaut=<typeTravail:nombre de livraison>
    courriel            : Adresse courriel utilisée pour envoyer le rapport d'exécution.
                          défaut = michel.pothier@canada.ca;odette.trottier@canada.ca

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
        ValiderIntegriteDonneesSpatialesLivrees.py env geodatabase tableContraintes classeDecoupage attributDecoupage repTravail dateFin typeTravail courriel

    Exemple:
        ValiderIntegriteDonneesSpatialesLivrees.py SIB_PRO
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderIntegriteDonneesSpatialesLivrees.py 1194 2018-07-12 15:34:30Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules privés
import CompteSib

#*******************************************************************************************
class ValiderIntegriteDonneesSpatialesLivrees(object):
#*******************************************************************************************
    """ Valider l'intégrité des données spatiales livrées dans la BDG selon une table de contraintes spatiales.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider l'intégrité des données spatiales livrées dans la BDG selon une table de contraintes spatiales.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        # Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, courriel):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env                 : Type d'environnement
        geodatabase         : Nom de la géodatabase contenant les tables spatiales.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de découpage.
        attributDecoupage   : Nom de l'attribut de la classe de découpage contenant les identifiants de découpage.
        repTravail          : Nom du répertoire de travail.
        dateFin             : Date de fin du traitement de livraison des données BDG (ex:2015-12-15 16:21:54).
        courriel            : Adresse courriel utilisée pour envoyer le rapport d'exécution.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(geodatabase) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'geodatabase')

        if (len(tableContraintes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tableContraintes')

        if (len(classeDecoupage) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'classeDecoupage')

        if (len(attributDecoupage) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'attributDecoupage')

        if (len(repTravail) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'repTravail')

        if (len(dateFin) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'dateFin')

        if (len(courriel) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'courriel')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, typeTravail, courriel):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider l'intégrité des données spatiales livrées dans la BDG selon une table de contraintes spatiales.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.
        geodatabase         : Nom de la géodatabase contenant les tables spatiales.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de découpage.
        attributDecoupage   : Nom de l'attribut de la classe de découpage contenant les identifiants de découpage.
        repTravail          : Nom du répertoire de travail.
        dateFin             : Date de fin du traitement de livraison des données BDG (ex:2015-12-15 16:21:54).
        typeTravail         : Liste des types de travaux présents dans la table SER_RECONCILE_LOG et
                              dont les identifiants ont été livrés après la date de fin spécifiée.
        courriel            : Adresse courriel utilisée pour envoyer le rapport d'exécution.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Créer la requête SQL.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des travaux effectués sur le nombre d'identifiants livrés")
        sSql = ("SELECT TY_TRAV, COUNT(*)"
                " FROM SER_RECONCILE_LOG@BDG_DBA"
                " WHERE STATUT=9 AND DATE_FIN>TO_DATE('" + dateFin + "','yyyy-mm-dd HH24:MI:SS')")
        #Vérifier si on spécifier les types de travail dans la requête
        if len(typeTravail) > 0:
            #Initialiser la liste des travaux
            listeTrav = ""
            #Extraire les types de travaux
            for trav in typeTravail.split(";"):
                #Ajouter le travail à la liste
                listeTrav = listeTrav + trav.split(":")[0] + ","
                #Afficher le travail et le nombre d'identifiants
                arcpy.AddMessage(str(trav))
            #Ajouter la liste des travaux à la requête SQL
            sSql = sSql + " AND TY_TRAV IN ('" + listeTrav[:-1].replace(",","','") + "')"
        #Ajouter le regroupement et le tri dans la requête sql
        sSql = sSql + " GROUP BY TY_TRAV ORDER BY TY_TRAV"
        
        #Exécuter la requête SQL
        arcpy.AddMessage(sSql)
        resultatTrav = oSib.requeteSib(sSql)
        
        #Traiter tous les travaux
        for trav in resultatTrav:
            #Créer la requête SQL.
            arcpy.AddMessage(" ")
            arcpy.AddMessage(str(trav))
            
            #----------------------------------------------------------
            #Créer la requête SQL pour extraire les identifiants livrés
            sSql = ("SELECT IDENTIFIANT"
                    "  FROM SER_RECONCILE_LOG@BDG_DBA"
                    " WHERE STATUT=9 AND DATE_FIN>TO_DATE('" + dateFin + "','yyyy-mm-dd HH24:MI:SS')"
                    "   AND TY_TRAV='" + trav[0] + "'"
                    " ORDER BY IDENTIFIANT")
            
            #Exécuter la requête SQL
            #arcpy.AddMessage(sSql)
            resultatId = oSib.requeteSib(sSql)
            
            #Vérifier si aucun identifiant
            if len(resultatId) == 0:
                #Créer la liste des identifiants à traiter            
                raise Exception("ERREUR : Aucun identifiant à traiter")
             
            #Vérifier si le nombre est supérieur à 999
            if len(resultatId) > 999:
                #Créer la liste des identifiants à traiter            
                raise Exception("Nombre d'identifiant supérieur à la limite permise : (" + str(len(resultatId)) + ">999)")
            
            #Initialisation de la liste de sélection des identifiants
            listeId = ""
            #Traiter tous les identifiants
            for id in resultatId:
                #Ajouter l'identifiant à la liste
                listeId = listeId + id[0] + ","                
            #Définir la requete des identifiants
            requeteId = attributDecoupage + " IN ('" + listeId[:-1].replace(",","','") + "')"
            
            #Créer le Layer de découpage
            arcpy.AddMessage("- Création du Layer de découpage ...")
            dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            clsDecoupage = geodatabase + "\\" + classeDecoupage
            lyrDecoupage = "Decoupage_" + trav[0] + "_" + dateHeure + ".lyr"
            #Process: Make Feature Layer
            arcpy.AddMessage('MakeFeatureLayer_management "' + clsDecoupage + '" ' + geodatabase + ' "' + requeteId + '"')
            arcpy.MakeFeatureLayer_management(clsDecoupage, lyrDecoupage, requeteId)
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            #Process: Select Layer By Attribute
            arcpy.AddMessage("SelectLayerByAttribute_management " + lyrDecoupage + " NEW_SELECTION")
            arcpy.SelectLayerByAttribute_management(lyrDecoupage, "NEW_SELECTION")
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            #Process: Save To Layer File
            arcpy.AddMessage("SaveToLayerFile_management " + lyrDecoupage + " " + repTravail + "\\" + lyrDecoupage)
            arcpy.SaveToLayerFile_management(lyrDecoupage, repTravail + "\\" + lyrDecoupage)
            arcpy.AddMessage(arcpy.GetMessage(arcpy.GetMessageCount()-1))
            
            #----------------------------------------------------------
            #Créer la requête SQL pour extraire les identifiants livrés
            sSql = (" SELECT DISTINCT B.FEAT_TYPE_NAME_DATABASE"
                    " FROM FEAT_CATALOGUE@BDG_VIEW A, FEAT_TYPE@BDG_VIEW B"
                    " WHERE A.FEAT_CATAL_TYPE=1"
                    "   AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK" 
                    "   AND B.FEAT_TYPE_CODE_BD IN "
                    "   ("
                    "       SELECT DISTINCT LE.CD_ELEM_TOPO"
                    "      FROM F502_PS PS, F502_LE LE, F503_TR TR, F601_LO LO"
                    "     WHERE TR.TY_TRAV='" + trav[0] + "'"
                    "       AND PS.NO_MAP=TR.NO_MAP AND PS.NO_MAP=LE.NO_MAP AND TR.NO_LOT=LO.NO_LOT" 
                    "   )"
                    " ORDER BY B.FEAT_TYPE_NAME_DATABASE")
            
            #Exécuter la requête SQL
            resultatClasse = oSib.requeteSib(sSql)
            
            #Vérifier si aucune classe
            if len(resultatClasse) == 0:
                #Créer la liste des identifiants à traiter            
                arcpy.AddMessage(sSql)
                raise Exception("ERREUR : Aucune classe à traiter")
            
            #Initialisation de la liste des classes à traiter
            listeClasse = ""
            #Traiter toutes les classes
            for cls in resultatClasse:
                #Ajouter la classe à la liste
                listeClasse = listeClasse + cls[0] + ","                
            #Définir la requete des identifiants
            listeClasse = listeClasse[:-1]
            
            #----------------------------------------------------------
            #Afficher le message d'exécution du traitement de validation pour le travail
            arcpy.AddMessage("- Exécution du traitement de validation spatiale ...")
            #Définir le nom du rapport d'exécution
            nomRapport = repTravail + "\\Rapport_" + trav[0] + "_" + dateHeure + ".txt"
            #Définir la commande de validation
            cmd = ("D:\\cits\\EnvCits\\applications\\gestion_bdg\\pro\\Geotraitement\\exe\\ValiderIntegriteSpatiale.exe"
                   ' "' + geodatabase + '"'
                   " " + tableContraintes + ""
                   " #"
                   " " + listeClasse + ""
                   " " + nomRapport + ""
                   " " + repTravail + "\\%" + attributDecoupage + "%_" + trav[0] + "_" + dateHeure + ".mdb"
                   " " + courriel + ""
                   " " + repTravail + "\\" + lyrDecoupage + ""
                   " " + attributDecoupage + "")
            #Afficher la commande
            arcpy.AddMessage(cmd)
            #Exécuter la commande
            err = os.system(cmd + " > " + nomRapport.replace(".txt",".log"))
            
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "SIB_PRO"
        geodatabase = "Database Connections\BDRS_PRO_BDG_DBA.sde"
        tableContraintes = "CONTRAINTE_INTEGRITE_SPATIALE"
        classeDecoupage = "GES_DECOUPAGE_SNRC50K_2"
        attributDecoupage = "DATASET_NAME"
        repTravail = "D:\Erreurs"
        dateFin = str(datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(days=1))
        typeTravail = ""
        courriel = "michel.pothier@canada.ca;odette.trottier@canada.ca"
        
        # Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            geodatabase = sys.argv[2]
        
        if len(sys.argv) > 3:
            tableContraintes = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            classeDecoupage = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            attributDecoupage = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            repTravail = sys.argv[6]
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                dateFin = sys.argv[7]
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                typeTravail = sys.argv[8]
        
        if len(sys.argv) > 9:
            courriel = sys.argv[9]
        
        #Définir l'objet pour valider l'intégrité des données spatiales livrées dans la BDG selon une table de contraintes spatiales.
        oValiderIntegriteDonneesSpatialesLivrees = ValiderIntegriteDonneesSpatialesLivrees()
        
        #Valider les paramètres obligatoires
        oValiderIntegriteDonneesSpatialesLivrees.validerParamObligatoire(env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, courriel)
        
        #Exécuter le traitement pour valider l'intégrité des données spatiales livrées dans la BDG selon une table de contraintes spatiales.
        oValiderIntegriteDonneesSpatialesLivrees.executer(env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, typeTravail, courriel)
    
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