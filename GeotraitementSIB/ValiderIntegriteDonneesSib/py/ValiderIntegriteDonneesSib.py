#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderIntegriteSib.py
# Auteur    : Michel Pothier
# Date      : 14 janvier 2015

"""
Outil qui permet de valider les valeurs minimum et maximum de date de validité et de précision altimétrique et planimétrique
dans les métadonnées par rapport aux informations sur les données pour tous les identifiants d'une non-conformité.


Paramètres d'entrées:
----------------------
env         : Type d'environnement.
xml         : Nom du fichier XML contenant l'information pour valider les données SIB.

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    ValiderIntegriteSib.py env xml

Exemple:
    ValiderIntegriteSib.py SIB_PRO /EnvCits/Sql_PlSql/pro/sib/0000_VAL/ValidationSib.xml

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderIntegriteDonneesSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback
from xml.dom import minidom

# Importation des modules privés (Cits)
import CompteSib

#Définition des constantes
NODE_NIVEAU = "Niveau"
NODE_NUMERO = "Numero"
NODE_TABLE = "Table"
NODE_NOM = "Nom"
NODE_BOOLEEN = "Booleen"
NODE_COLONNE = "Colonne"
NODE_SQL_LIBRE = "SqlLibre"
NODE_REQUETE = "Requette"
NODE_TEXTE_COURRIEL = "TexteCourriel"
NODE_MAITRE_DETAIL = "MaitreDetail"
NODE_TABLE_MAITRE = "TableMaitre"
NODE_COLONNE_MAITRE = "ColonneMaitre"
NODE_COLONNE_DETAIL = "ColonneDetail"
NODE_WHERE_MAITRE = "WhereMaitre"
NODE_WHERE_DETAIL = "WhereDetail"
NODE_CODE_SYSTEME = "CodeSysteme"
NODE_COLONNE = "Colonne"
NODE_TYPE = "Type"
NODE_NOM_CODE = "NomCode"
NODE_VALEUR_NULL = "ValeurNull"
NODE_TYPE_PRODUIT = "TypeProduit"

#*******************************************************************************************
class ValiderIntegriteSib(object):
#*******************************************************************************************
    """
    Application qui permet de valider l'intégrité des données contenues dans la Base de données SIB.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider l'intégrité des données.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        #Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, xml):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider l'intégrité des données.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        xml         : Nom du fichier XML contenant l'information pour valider les données SIB.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : Résultat de la requête SIB.
        nbVal           : Nombre de validation effectuée.
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Vérifier si le fichier XML est absent
        if not os.path.exists(xml):
            #Retourner une exception
            raise Exception("Fichier XML absent: %s" %xml)
        
        #Lire le fichier XML et conserver le contenu
        arcpy.AddMessage("- Lecture du fichier XML : " + xml)
        documentXML = minidom.parse(xml)
        
        #Extraire la liste des noeuds à traiter
        listeNiveau = documentXML.getElementsByTagName(NODE_NIVEAU)
        
        #Traiter tous les niveaux
        nbVal = 0
        nbErr = 0
        sqlErr = []
        for niveau in listeNiveau:
            #Extraire la liste des numéros
            listeNumero = niveau.getElementsByTagName(NODE_NUMERO)
            #Définir le numéro du niveau
            numero = listeNumero[0].childNodes[0].nodeValue
            #Afficher le numéro du niveau à valider
            arcpy.AddMessage("--Validation du " + numero)
            
            #Extraire la liste des tables
            listeTable = niveau.getElementsByTagName(NODE_TABLE)
            #Traiter toutes les tables
            for table in listeTable:
                #Extraire la liste des noms de table
                listeNom = table.getElementsByTagName(NODE_NOM)
                #Définir le nom de la table à valider
                nom = listeNom[0].childNodes[0].nodeValue
                #Afficher le nom de la table à valider
                arcpy.AddMessage("--Validation de la table " + nom)
                
                #Extraire la liste des Booleen à valider
                listeBooleen = table.getElementsByTagName(NODE_BOOLEEN)
                #Traiter tous les Booleen
                for booleen in listeBooleen:
                    #Extraire la liste des colonnes à valider
                    listeColonne = booleen.getElementsByTagName(NODE_COLONNE)
                    #Définir la colonne à valider
                    colonne = listeColonne[0].childNodes[0].nodeValue
                    #Définir la requête SQL de validation
                    sql = "SELECT COUNT(*) FROM " + nom + " WHERE " + colonne + " NOT IN (0,1)"
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requête SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Exécuter la requête de validation
                    resultat = self.Sib.requeteSib(sql)
                    #Vérifier le résultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la résultat en erreur
                        arcpy.AddError(str(nbErr) + " : Nombre de valeurs en erreur : " + str(resultat[0][0]))
                        #Ajouter le commande SQL en erreur
                        sqlErr.append(sql)
                
                #Extraire la liste des MaitreDetail à valider
                listeMaitreDetail = table.getElementsByTagName(NODE_MAITRE_DETAIL)
                #Traiter tous les MaitreDetail
                for MaitreDetail in listeMaitreDetail:
                    #Extraire la liste des TableMaitre à valider
                    listeTableMaitre = MaitreDetail.getElementsByTagName(NODE_TABLE_MAITRE)
                    #Définir la TableMaitre à valider
                    tableMaitre = listeTableMaitre[0].childNodes[0].nodeValue
                    #Extraire la liste des ColonneMaitre à valider
                    listeColonneMaitre = MaitreDetail.getElementsByTagName(NODE_COLONNE_MAITRE)
                    #Définir la ColonneMaitre à valider
                    colonneMaitre = listeColonneMaitre[0].childNodes[0].nodeValue
                    #Extraire la liste des ColonneDetail à valider
                    listeColonneDetail = MaitreDetail.getElementsByTagName(NODE_COLONNE_DETAIL)
                    #Définir la ColonneDetail à valider
                    colonneDetail = listeColonneDetail[0].childNodes[0].nodeValue
                    #Extraire la liste des WhereMaitre à valider
                    listeWhereMaitre = MaitreDetail.getElementsByTagName(NODE_WHERE_MAITRE)
                    whereMaitre = ""
                    #Vérifier la présence du noeud WhereMaitre
                    if len(listeWhereMaitre) > 0:
                        #Définir la WhereMaitre à valider
                        whereMaitre = " WHERE " + listeWhereMaitre[0].childNodes[0].nodeValue
                    #Extraire la liste des WhereDetail à valider
                    listeWhereDetail = MaitreDetail.getElementsByTagName(NODE_WHERE_DETAIL)
                    whereDetail = ""
                    #Vérifier la présence du noeud WhereDetail
                    if len(listeWhereDetail) > 0:
                        #Définir la WhereDetail à valider
                        whereDetail = " WHERE " + listeWhereDetail[0].childNodes[0].nodeValue
                    #Définir la requête SQL de validation
                    sql = "SELECT COUNT(*) FROM (SELECT " + colonneDetail + " FROM " + nom + whereDetail + " MINUS SELECT " + colonneMaitre + " FROM " + tableMaitre + whereMaitre + ")"
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requête SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Exécuter la requête de validation
                    resultat = self.Sib.requeteSib(sql)
                    #Vérifier le résultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la résultat en erreur
                        arcpy.AddError(str(nbErr) + " : Nombre de valeurs en erreur : " + str(resultat[0][0]))
                        #Ajouter le commande SQL en erreur
                        sqlErr.append(sql)
                
                #Extraire la liste des CodeSysteme à valider
                listeCodeSysteme = table.getElementsByTagName(NODE_CODE_SYSTEME)
                #Traiter tous les CodeSysteme
                for codeSysteme in listeCodeSysteme:
                    #Extraire la liste des colonnes à valider
                    listeColonne = codeSysteme.getElementsByTagName(NODE_COLONNE)
                    #Définir la colonne à valider
                    colonne = listeColonne[0].childNodes[0].nodeValue
                    #Extraire la liste des ValeurNull à valider
                    listeValeurNull = codeSysteme.getElementsByTagName(NODE_VALEUR_NULL)
                    #Définir la ValeurNull à valider par défaut
                    valeurNull = ""
                    #Vérifier la présence du Noeud
                    if len(listeValeurNull) > 0:
                        #Vérifier la ValeurNull à valider
                        if listeValeurNull[0].childNodes[0].nodeValue == "TRUE":
                            #Définir la ValeurNull à valider
                            valeurNull = " WHERE " + colonne + " IS NOT NULL"
                    #Extraire la liste des Type à valider
                    listeType = codeSysteme.getElementsByTagName(NODE_TYPE)
                    #Définir le Type à valider
                    type = listeType[0].childNodes[0].nodeValue
                    #Extraire la liste des NomCode à valider
                    listeNomCode = codeSysteme.getElementsByTagName(NODE_NOM_CODE)
                    #Définir le NomCode à valider
                    nomCode = listeNomCode[0].childNodes[0].nodeValue.lower()
                    #Vérifier si le Type contient le type de produit (longueur du type=3)
                    sql = ""
                    typeProduit = ""
                    if len(type) == 3:
                        #Extraire la liste des TypeProduit à valider
                        listeTypeProduit = codeSysteme.getElementsByTagName(NODE_TYPE_PRODUIT)
                        #Définir le NomCode à valider
                        typeProduit = listeTypeProduit[0].childNodes[0].nodeValue.upper()
                    #Vérifier si le Type est CS (Code Système)
                    if type == "CS":
                        #Définir la requête SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT CD_VALEUR FROM F002_VA WHERE CD_CHAMP='" + nomCode + "')"
                    #Vérifier si le Type est CSP (Code Système par Produit)
                    if type == "CSP":
                        #Définir la requête SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT CD_VALEUR FROM F002_VP WHERE CD_CHAMP='" + nomCode + "' AND TY_PRODUIT='" + typeProduit + "')"
                    #Vérifier si le Type est CDP (Code Dictionnaire par Produit)
                    if type == "CDP":
                        #Définir la requête SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT CD_VALEUR FROM F102_VP WHERE CD_CHAMP='" + nomCode + "' AND TY_PRODUIT='" + typeProduit + "')"
                    #Vérifier si le Type est ISP (Intervalle Système par Produit)
                    if type == "ISP":
                        #Définir la requête SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT " + colonne + " FROM " + nom + ",F002_RP where " + colonne + " >=BORNE_MIN AND " + colonne + "<=BORNE_MAX AND CD_CHAMP='" + nomCode + "' AND TY_PRODUIT='" + typeProduit + "')"
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requête SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Exécuter la requête de validation
                    resultat = self.Sib.requeteSib(sql)
                    #Vérifier le résultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la résultat en erreur
                        arcpy.AddError(str(nbErr) + " : Nombre de valeurs en erreur : " + str(resultat[0][0]))
                        #Ajouter le commande SQL en erreur
                        sqlErr.append(sql)
                
                #Extraire la liste des SqlLibre à valider
                listeSqlLibre = table.getElementsByTagName(NODE_SQL_LIBRE)
                #Traiter toutes les SqlLibre
                for sqlLibre in listeSqlLibre:
                    #Extraire la liste des requêtes à valider
                    listeRequete = sqlLibre.getElementsByTagName(NODE_REQUETE)
                    #Définir la requête SQL de validation
                    sql = listeRequete[0].childNodes[0].nodeValue
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requête SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Exécuter la requête de validation
                    resultat = self.Sib.requeteSib(sql)
                    #Vérifier le résultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la résultat en erreur
                        arcpy.AddError(str(nbErr) + " : Nombre de valeurs en erreur : " + str(resultat[0][0]))
                        #Ajouter le commande SQL en erreur
                        sqlErr.append(sql)
        
        #Afficher les erreurs
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre total d'erreurs : " + str(nbErr))
        #Traiter toutes les commendes SQL en erreur
        for sql in sqlErr:
            #Afficher le SQL en erreur
            arcpy.AddMessage(sql + ";")
            
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        self.Sib.fermerConnexionSib()
        
        #Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "SIB_PRO"
        xml = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            xml = sys.argv[2]
        
        #Définir l'objet de validation des données SIB.
        oValiderIntegriteSib = ValiderIntegriteSib()
        
        #Exécuter le traitement de validation des données SIB.
        oValiderIntegriteSib.executer(env, xml)
        
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