#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderIntegriteSib.py
# Auteur    : Michel Pothier
# Date      : 14 janvier 2015

"""
Outil qui permet de valider les valeurs minimum et maximum de date de validit� et de pr�cision altim�trique et planim�trique
dans les m�tadonn�es par rapport aux informations sur les donn�es pour tous les identifiants d'une non-conformit�.


Param�tres d'entr�es:
----------------------
env         : Type d'environnement.
xml         : Nom du fichier XML contenant l'information pour valider les donn�es SIB.

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#D�finition des constantes
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
    Application qui permet de valider l'int�grit� des donn�es contenues dans la Base de donn�es SIB.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider l'int�grit� des donn�es.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, xml):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider l'int�grit� des donn�es.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        xml         : Nom du fichier XML contenant l'information pour valider les donn�es SIB.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        nbVal           : Nombre de validation effectu�e.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #V�rifier si le fichier XML est absent
        if not os.path.exists(xml):
            #Retourner une exception
            raise Exception("Fichier XML absent: %s" %xml)
        
        #Lire le fichier XML et conserver le contenu
        arcpy.AddMessage("- Lecture du fichier XML : " + xml)
        documentXML = minidom.parse(xml)
        
        #Extraire la liste des noeuds � traiter
        listeNiveau = documentXML.getElementsByTagName(NODE_NIVEAU)
        
        #Traiter tous les niveaux
        nbVal = 0
        nbErr = 0
        sqlErr = []
        for niveau in listeNiveau:
            #Extraire la liste des num�ros
            listeNumero = niveau.getElementsByTagName(NODE_NUMERO)
            #D�finir le num�ro du niveau
            numero = listeNumero[0].childNodes[0].nodeValue
            #Afficher le num�ro du niveau � valider
            arcpy.AddMessage("--Validation du " + numero)
            
            #Extraire la liste des tables
            listeTable = niveau.getElementsByTagName(NODE_TABLE)
            #Traiter toutes les tables
            for table in listeTable:
                #Extraire la liste des noms de table
                listeNom = table.getElementsByTagName(NODE_NOM)
                #D�finir le nom de la table � valider
                nom = listeNom[0].childNodes[0].nodeValue
                #Afficher le nom de la table � valider
                arcpy.AddMessage("--Validation de la table " + nom)
                
                #Extraire la liste des Booleen � valider
                listeBooleen = table.getElementsByTagName(NODE_BOOLEEN)
                #Traiter tous les Booleen
                for booleen in listeBooleen:
                    #Extraire la liste des colonnes � valider
                    listeColonne = booleen.getElementsByTagName(NODE_COLONNE)
                    #D�finir la colonne � valider
                    colonne = listeColonne[0].childNodes[0].nodeValue
                    #D�finir la requ�te SQL de validation
                    sql = "SELECT COUNT(*) FROM " + nom + " WHERE " + colonne + " NOT IN (0,1)"
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requ�te SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Ex�cuter la requ�te de validation
                    resultat = self.Sib.requeteSib(sql)
                    #V�rifier le r�sultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la r�sultat en erreur
                        arcpy.AddError(str(nbErr) + " : Nombre de valeurs en erreur : " + str(resultat[0][0]))
                        #Ajouter le commande SQL en erreur
                        sqlErr.append(sql)
                
                #Extraire la liste des MaitreDetail � valider
                listeMaitreDetail = table.getElementsByTagName(NODE_MAITRE_DETAIL)
                #Traiter tous les MaitreDetail
                for MaitreDetail in listeMaitreDetail:
                    #Extraire la liste des TableMaitre � valider
                    listeTableMaitre = MaitreDetail.getElementsByTagName(NODE_TABLE_MAITRE)
                    #D�finir la TableMaitre � valider
                    tableMaitre = listeTableMaitre[0].childNodes[0].nodeValue
                    #Extraire la liste des ColonneMaitre � valider
                    listeColonneMaitre = MaitreDetail.getElementsByTagName(NODE_COLONNE_MAITRE)
                    #D�finir la ColonneMaitre � valider
                    colonneMaitre = listeColonneMaitre[0].childNodes[0].nodeValue
                    #Extraire la liste des ColonneDetail � valider
                    listeColonneDetail = MaitreDetail.getElementsByTagName(NODE_COLONNE_DETAIL)
                    #D�finir la ColonneDetail � valider
                    colonneDetail = listeColonneDetail[0].childNodes[0].nodeValue
                    #Extraire la liste des WhereMaitre � valider
                    listeWhereMaitre = MaitreDetail.getElementsByTagName(NODE_WHERE_MAITRE)
                    whereMaitre = ""
                    #V�rifier la pr�sence du noeud WhereMaitre
                    if len(listeWhereMaitre) > 0:
                        #D�finir la WhereMaitre � valider
                        whereMaitre = " WHERE " + listeWhereMaitre[0].childNodes[0].nodeValue
                    #Extraire la liste des WhereDetail � valider
                    listeWhereDetail = MaitreDetail.getElementsByTagName(NODE_WHERE_DETAIL)
                    whereDetail = ""
                    #V�rifier la pr�sence du noeud WhereDetail
                    if len(listeWhereDetail) > 0:
                        #D�finir la WhereDetail � valider
                        whereDetail = " WHERE " + listeWhereDetail[0].childNodes[0].nodeValue
                    #D�finir la requ�te SQL de validation
                    sql = "SELECT COUNT(*) FROM (SELECT " + colonneDetail + " FROM " + nom + whereDetail + " MINUS SELECT " + colonneMaitre + " FROM " + tableMaitre + whereMaitre + ")"
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requ�te SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Ex�cuter la requ�te de validation
                    resultat = self.Sib.requeteSib(sql)
                    #V�rifier le r�sultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la r�sultat en erreur
                        arcpy.AddError(str(nbErr) + " : Nombre de valeurs en erreur : " + str(resultat[0][0]))
                        #Ajouter le commande SQL en erreur
                        sqlErr.append(sql)
                
                #Extraire la liste des CodeSysteme � valider
                listeCodeSysteme = table.getElementsByTagName(NODE_CODE_SYSTEME)
                #Traiter tous les CodeSysteme
                for codeSysteme in listeCodeSysteme:
                    #Extraire la liste des colonnes � valider
                    listeColonne = codeSysteme.getElementsByTagName(NODE_COLONNE)
                    #D�finir la colonne � valider
                    colonne = listeColonne[0].childNodes[0].nodeValue
                    #Extraire la liste des ValeurNull � valider
                    listeValeurNull = codeSysteme.getElementsByTagName(NODE_VALEUR_NULL)
                    #D�finir la ValeurNull � valider par d�faut
                    valeurNull = ""
                    #V�rifier la pr�sence du Noeud
                    if len(listeValeurNull) > 0:
                        #V�rifier la ValeurNull � valider
                        if listeValeurNull[0].childNodes[0].nodeValue == "TRUE":
                            #D�finir la ValeurNull � valider
                            valeurNull = " WHERE " + colonne + " IS NOT NULL"
                    #Extraire la liste des Type � valider
                    listeType = codeSysteme.getElementsByTagName(NODE_TYPE)
                    #D�finir le Type � valider
                    type = listeType[0].childNodes[0].nodeValue
                    #Extraire la liste des NomCode � valider
                    listeNomCode = codeSysteme.getElementsByTagName(NODE_NOM_CODE)
                    #D�finir le NomCode � valider
                    nomCode = listeNomCode[0].childNodes[0].nodeValue.lower()
                    #V�rifier si le Type contient le type de produit (longueur du type=3)
                    sql = ""
                    typeProduit = ""
                    if len(type) == 3:
                        #Extraire la liste des TypeProduit � valider
                        listeTypeProduit = codeSysteme.getElementsByTagName(NODE_TYPE_PRODUIT)
                        #D�finir le NomCode � valider
                        typeProduit = listeTypeProduit[0].childNodes[0].nodeValue.upper()
                    #V�rifier si le Type est CS (Code Syst�me)
                    if type == "CS":
                        #D�finir la requ�te SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT CD_VALEUR FROM F002_VA WHERE CD_CHAMP='" + nomCode + "')"
                    #V�rifier si le Type est CSP (Code Syst�me par Produit)
                    if type == "CSP":
                        #D�finir la requ�te SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT CD_VALEUR FROM F002_VP WHERE CD_CHAMP='" + nomCode + "' AND TY_PRODUIT='" + typeProduit + "')"
                    #V�rifier si le Type est CDP (Code Dictionnaire par Produit)
                    if type == "CDP":
                        #D�finir la requ�te SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT CD_VALEUR FROM F102_VP WHERE CD_CHAMP='" + nomCode + "' AND TY_PRODUIT='" + typeProduit + "')"
                    #V�rifier si le Type est ISP (Intervalle Syst�me par Produit)
                    if type == "ISP":
                        #D�finir la requ�te SQL de validation
                        sql = "SELECT COUNT(*) FROM (SELECT " + colonne + " FROM " + nom + valeurNull + " MINUS SELECT " + colonne + " FROM " + nom + ",F002_RP where " + colonne + " >=BORNE_MIN AND " + colonne + "<=BORNE_MAX AND CD_CHAMP='" + nomCode + "' AND TY_PRODUIT='" + typeProduit + "')"
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requ�te SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Ex�cuter la requ�te de validation
                    resultat = self.Sib.requeteSib(sql)
                    #V�rifier le r�sultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la r�sultat en erreur
                        arcpy.AddError(str(nbErr) + " : Nombre de valeurs en erreur : " + str(resultat[0][0]))
                        #Ajouter le commande SQL en erreur
                        sqlErr.append(sql)
                
                #Extraire la liste des SqlLibre � valider
                listeSqlLibre = table.getElementsByTagName(NODE_SQL_LIBRE)
                #Traiter toutes les SqlLibre
                for sqlLibre in listeSqlLibre:
                    #Extraire la liste des requ�tes � valider
                    listeRequete = sqlLibre.getElementsByTagName(NODE_REQUETE)
                    #D�finir la requ�te SQL de validation
                    sql = listeRequete[0].childNodes[0].nodeValue
                    #Compter le nombre de validation
                    nbVal = nbVal + 1
                    #Afficher la requ�te SQL de validation
                    arcpy.AddMessage(str(nbVal) + " : " + sql)
                    #Ex�cuter la requ�te de validation
                    resultat = self.Sib.requeteSib(sql)
                    #V�rifier le r�sultat
                    if resultat[0][0] > 0:
                        #Compter le nombre d'erreur
                        nbErr = nbErr + 1
                        #Afficher la r�sultat en erreur
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "SIB_PRO"
        xml = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            xml = sys.argv[2]
        
        #D�finir l'objet de validation des donn�es SIB.
        oValiderIntegriteSib = ValiderIntegriteSib()
        
        #Ex�cuter le traitement de validation des donn�es SIB.
        oValiderIntegriteSib.executer(env, xml)
        
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