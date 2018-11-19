#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderIntegriteDonneesRequeteSQL.py
# Auteur    : Michel Pothier
# Date      : 02 septembre 2015

"""
Outil qui permet de valider l'int�grit� des donn�es dans une base de donn�es via des requ�tes SQL contenues dans une table.

Param�tres d'entr�es:
----------------------
env         OB  Type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV].
                d�faut = BDRS_PRO
table       OB  Nom de la table contenant l'information pour valider les donn�es via des requ�tes SQL.
                d�faut : CONTRAINTE_INTEGRITE_SQL
groupe      OP  Liste des groupes de contrainte pour lesquels on veut effectuer la validation.
                d�faut = <tous les groupes>
courriel    OP  Adresses de courriel utilis�es pour envoyer le rapport d'ex�cution.
                d�faut = michel.pothier@canada.ca;odette.trottier@canada.ca

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
Usage:
    ValiderIntegriteDonneesRequeteSQL.py env table groupe courriel

Exemple:
    ValiderIntegriteDonneesRequeteSQL.py BDG_PRO CONTRAINTE_INTEGRITE_SQL "BDG-Longueur-BDG_ID;BDG-Espace-BDG_ID" michel.pothier@canada.ca

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderIntegriteDonneesRequeteSQL.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteBDG, EnvoyerCourriel

#*******************************************************************************************
class ValiderIntegriteDonneesRequeteSQL(object):
#*******************************************************************************************
    """
    Application qui permet de valider l'int�grit� des donn�es contenues dans la Base de donn�es via des requ�tes SQL.

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
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        #D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #D�finir la date de d�but
        self.dateDebut = datetime.datetime.now().replace(microsecond=0)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, table, courriel):
    #-------------------------------------------------------------------------------------
        """
        Valider les param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        table       : Nom de la table contenant l'information pour valider les donn�es via des requ�tes SQL.
        courriel    : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("-V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(table) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'table')
        
        if (len(courriel) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'courriel')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, table, groupe, courriel):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider l'int�grit� des donn�es.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        table       : Nom de la table contenant l'information pour valider les donn�es via des requ�tes SQL.
        groupe      : Liste des groupes de contrainte pour lesquels on veut effectuer la validation.
        courriel    : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        resultat        : R�sultat de la requ�te BDG.
        cptSql           : Nombre de validation effectu�e.
        """
        
        #Remplir la date de d�but dans le contenu du courriel
        contenu = "D�but : " + str(self.dateDebut) + "\n\n"
        
        #Remplir la commande dans le contenu du courriel
        for item in sys.argv:
            contenu = contenu + item + " "
        
        #Connexion � la BDG
        arcpy.AddMessage("-Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Extraire l'usager de la BD
        sUsagerBd = self.CompteBDG.UsagerBd()
        
        #--------------------
        #Cr�er la requ�te SQL pour l'extraction des tables modifi�es dans la BDG.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Extraction des tables modifi�es dans la BDG.")
        contenu = contenu + "\n\n-Extraction des tables modifi�es dans la BDG."
        #D�finir la SQL de base
        sql = ("DBMS_STATS.FLUSH_DATABASE_MONITORING_INFO")
        #Afficher la requ�te SQL
        arcpy.AddMessage("EXECUTE " + sql + ";")
        contenu = contenu + "\nEXECUTE " + sql + ";"
        #Ex�cuter la proc�dure SQL
        self.BDG.cursor.callproc('DBMS_STATS.FLUSH_DATABASE_MONITORING_INFO')
        #D�finir la SQL de base
        sql = ("SELECT TABLE_NAME,INSERTS,UPDATES,DELETES,TIMESTAMP"
               "  FROM ALL_TAB_MODIFICATIONS"
               " WHERE REGEXP_LIKE (TABLE_NAME, '^(BDG_|GES_|INC_|LIM_|NHN_|NRN_|PAT_|TA_)')"
               "   AND TIMESTAMP>TO_DATE('" + str(self.dateDebut-datetime.timedelta(days=1)) + "','yyyy-mm-dd HH24:MI:SS')"
               " ORDER BY TABLE_NAME")
        #Afficher la requ�te SQL
        arcpy.AddMessage(sql + ";")
        contenu = contenu + "\n" + sql + ";\n"
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        #Si un r�sultat est pr�sent
        if resultat:
            #Afficher les donn�es
            arcpy.AddMessage(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
            contenu = contenu + " " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat)
        
        #--------------------
        #Cr�er la requ�te SQL pour l'extraction des identifiants livr�s dans la BDG.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Extraction des identifiants livr�s dans la BDG par type de travail.")
        contenu = contenu + "\n\n-Extraction des identifiants livr�s dans la BDG par type de travail."
        #D�finir la SQL de base
        sql = ("SELECT COUNT(*), TY_TRAV"
               "  FROM SER_RECONCILE_LOG"
               " WHERE STATUT=9 AND DATE_FIN>TO_DATE('" + str(self.dateDebut-datetime.timedelta(days=1)) + "','yyyy-mm-dd HH24:MI:SS')"
               " GROUP BY TY_TRAV ORDER BY TY_TRAV")
        #Afficher la requ�te SQL
        arcpy.AddMessage(sql + ";")
        contenu = contenu + "\n" + sql + ";"
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        #Afficher les identifiants livr�s dans la BDG depuis la date sp�cifi�e
        for trav in resultat:
            #Afficher le nombre d'identifiants livr�s du travail 
            arcpy.AddMessage(str(trav))
            contenu = contenu + "\n" + str(trav)
        
        #--------------------
        #Cr�er la requ�te SQL pour l'extraction de l'information de la table des contraintes d'int�grit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Extraction de l'information de la table des contraintes d'int�grit� : " + table)
        #D�finir la SQL de base
        sql = "SELECT GROUPE, DESCRIPTION, REQUETE_SQL, MESSAGE FROM " + table
        #V�rifier si un groupe est sp�cifi�
        if len(groupe) > 0:
            #Ajouter la condition de groupe
            sql = sql + " WHERE GROUPE IN ('" + groupe + "')"
        #Ajouter le tri
        sql = sql + " ORDER BY GROUPE, REQUETE_SQL"
        #Afficher la requ�te SQL
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #Initialiser les variables de travail
        nbSql = len(resultat)
        cptSql = 0
        nbErr = 0
        nbSqlErr = 0
        sqlErr = []
        #Traiter toutes les contraintes d'int�grit� SQL
        for contrainte in resultat:
            #D�finir la requ�te SQL de validation
            groupe = contrainte[0]
            description = contrainte[1]
            sql = contrainte[2]
            message = contrainte[3]
            #Compter le nombre de validation
            cptSql = cptSql + 1
            #Afficher la requ�te SQL de validation
            arcpy.AddMessage(" ")
            arcpy.AddMessage(str(cptSql) + "/" + str(nbSql) + " : " + groupe + " : " + str(datetime.datetime.now()))
            arcpy.AddMessage(sql)
            #Ex�cuter la requ�te SQL de validation
            resultat = self.BDG.query(sql)
            #V�rifier la pr�sence d'une erreur
            if resultat:
                #Afficher la r�sultat en erreur
                nbSqlErr = len(resultat)
                arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbSqlErr))
                #Compl�ter la commande SQL
                sql = "-"*80 + "\n-" + description + "\n-" + message + "\n" + "-"*80 + "\n" + sql + ";\n" + "Nombre de valeurs en erreur : " + str(nbSqlErr)
                #Traiter tous les r�sultats
                for valeur in resultat:
                    #Compter le nombre de valeurs en erreur
                    nbErr = nbErr + valeur[0]
                    #V�rifier le nombre de valeurs trouv�es
                    if nbSqlErr < 100:
                        #Afficher les valeurs en erreur
                        arcpy.AddWarning(str(valeur))
                        #Conserver les valeurs en erreur
                        sql = sql + "\n" + str(valeur)
                #Ajouter la commande SQL en erreur
                sqlErr.append(sql)
        
        #--------------------
        #Afficher le nombre d'erreurs
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Liste des erreurs trouv�es dans les donn�es.")
        arcpy.AddMessage("Nombre total d'erreurs : " + str(nbErr))
        arcpy.AddMessage("Nombre total de requ�tes SQL contenant des erreurs : " + str(len(sqlErr)) + "/" + str(nbSql))
        #�crire le nombre d'erreurs dans le contenu du courriel
        contenu = contenu + "\n\n-Liste des erreurs trouv�es dans les donn�es.\n"
        contenu = contenu + "Nombre total d'erreurs : " + str(nbErr) + "\n"
        contenu = contenu + "Nombre total de requetes SQL contenant des erreurs : " + str(len(sqlErr)) + "/" + str(nbSql) + "\n"
        #Traiter toutes les commandes SQL en erreur
        for sql in sqlErr:
            #Afficher le SQL en erreur
            arcpy.AddMessage(" ")
            arcpy.AddWarning(sql)
            contenu = contenu + "\n" + sql + "\n"
        
        #Fermeture de la connexion de la BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Fermeture de la connexion BDG")
        self.BDG.close()
        
        #--------------------
        #Envoit d'un courriel aux responsables
        arcpy.AddMessage("-Envoit d'un courriel aux responsables")
        #Envoyer un courriel aux responsables
        for destinataire in courriel.split(";"):
            #Envoyer un courriel
            sujet = "Rapport d'int�grit� " + env
            contenu = contenu + "\nFin : " + str(datetime.datetime.now()) + "\n"
            contenu = contenu + "\nUsagerBD : " + sUsagerBd
            arcpy.AddMessage("EnvoyerCourriel('" + destinataire + "','" + sujet + "')")
            try:
                EnvoyerCourriel.EnvoyerCourriel(destinataire, contenu, unicode(sujet,"utf-8"))
            except:
                EnvoyerCourriel.EnvoyerCourriel(destinataire, contenu, sujet)
        
        #Sortir du traitement
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "BDRS_PRO"
        table = "CONTRAINTE_INTEGRITE_SQL"
        groupe = ""
        courriel = "michel.pothier@canada.ca"
        
        # Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            table = sys.argv[2]
        
        if len(sys.argv) > 3:
            if sys.argv[3] <> '#':
                groupe = sys.argv[3].replace(";","','")
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> '#':
                courriel = sys.argv[4]
        
        #D�finir l'objet de validation des donn�es via des requ�tes SQL.
        oValiderIntegriteDonneesRequeteSQL = ValiderIntegriteDonneesRequeteSQL()
        
        #Valider les param�tres obligatoires
        oValiderIntegriteDonneesRequeteSQL.validerParamObligatoire(env, table, courriel)
        
        #Ex�cuter le traitement de validation des donn�es via des requ�tes SQL.
        oValiderIntegriteDonneesRequeteSQL.executer(env, table, groupe, courriel)
        
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("-Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("-Succ�s du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)