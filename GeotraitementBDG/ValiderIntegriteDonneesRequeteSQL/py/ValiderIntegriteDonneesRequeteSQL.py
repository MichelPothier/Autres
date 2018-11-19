#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderIntegriteDonneesRequeteSQL.py
# Auteur    : Michel Pothier
# Date      : 02 septembre 2015

"""
Outil qui permet de valider l'intégrité des données dans une base de données via des requêtes SQL contenues dans une table.

Paramètres d'entrées:
----------------------
env         OB  Type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV].
                défaut = BDRS_PRO
table       OB  Nom de la table contenant l'information pour valider les données via des requêtes SQL.
                défaut : CONTRAINTE_INTEGRITE_SQL
groupe      OP  Liste des groupes de contrainte pour lesquels on veut effectuer la validation.
                défaut = <tous les groupes>
courriel    OP  Adresses de courriel utilisées pour envoyer le rapport d'exécution.
                défaut = michel.pothier@canada.ca;odette.trottier@canada.ca

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)
import CompteBDG, EnvoyerCourriel

#*******************************************************************************************
class ValiderIntegriteDonneesRequeteSQL(object):
#*******************************************************************************************
    """
    Application qui permet de valider l'intégrité des données contenues dans la Base de données via des requêtes SQL.

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
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Définir la date de début
        self.dateDebut = datetime.datetime.now().replace(microsecond=0)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, table, courriel):
    #-------------------------------------------------------------------------------------
        """
        Valider les paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        table       : Nom de la table contenant l'information pour valider les données via des requêtes SQL.
        courriel    : Adresse courriel utilisée pour envoyer le rapport d'exécution.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("-Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(table) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'table')
        
        if (len(courriel) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'courriel')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, table, groupe, courriel):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider l'intégrité des données.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        table       : Nom de la table contenant l'information pour valider les données via des requêtes SQL.
        groupe      : Liste des groupes de contrainte pour lesquels on veut effectuer la validation.
        courriel    : Adresse courriel utilisée pour envoyer le rapport d'exécution.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        resultat        : Résultat de la requête BDG.
        cptSql           : Nombre de validation effectuée.
        """
        
        #Remplir la date de début dans le contenu du courriel
        contenu = "Début : " + str(self.dateDebut) + "\n\n"
        
        #Remplir la commande dans le contenu du courriel
        for item in sys.argv:
            contenu = contenu + item + " "
        
        #Connexion à la BDG
        arcpy.AddMessage("-Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Extraire l'usager de la BD
        sUsagerBd = self.CompteBDG.UsagerBd()
        
        #--------------------
        #Créer la requête SQL pour l'extraction des tables modifiées dans la BDG.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Extraction des tables modifiées dans la BDG.")
        contenu = contenu + "\n\n-Extraction des tables modifiées dans la BDG."
        #Définir la SQL de base
        sql = ("DBMS_STATS.FLUSH_DATABASE_MONITORING_INFO")
        #Afficher la requête SQL
        arcpy.AddMessage("EXECUTE " + sql + ";")
        contenu = contenu + "\nEXECUTE " + sql + ";"
        #Exécuter la procédure SQL
        self.BDG.cursor.callproc('DBMS_STATS.FLUSH_DATABASE_MONITORING_INFO')
        #Définir la SQL de base
        sql = ("SELECT TABLE_NAME,INSERTS,UPDATES,DELETES,TIMESTAMP"
               "  FROM ALL_TAB_MODIFICATIONS"
               " WHERE REGEXP_LIKE (TABLE_NAME, '^(BDG_|GES_|INC_|LIM_|NHN_|NRN_|PAT_|TA_)')"
               "   AND TIMESTAMP>TO_DATE('" + str(self.dateDebut-datetime.timedelta(days=1)) + "','yyyy-mm-dd HH24:MI:SS')"
               " ORDER BY TABLE_NAME")
        #Afficher la requête SQL
        arcpy.AddMessage(sql + ";")
        contenu = contenu + "\n" + sql + ";\n"
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        #Si un résultat est présent
        if resultat:
            #Afficher les données
            arcpy.AddMessage(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
            contenu = contenu + " " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat)
        
        #--------------------
        #Créer la requête SQL pour l'extraction des identifiants livrés dans la BDG.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Extraction des identifiants livrés dans la BDG par type de travail.")
        contenu = contenu + "\n\n-Extraction des identifiants livrés dans la BDG par type de travail."
        #Définir la SQL de base
        sql = ("SELECT COUNT(*), TY_TRAV"
               "  FROM SER_RECONCILE_LOG"
               " WHERE STATUT=9 AND DATE_FIN>TO_DATE('" + str(self.dateDebut-datetime.timedelta(days=1)) + "','yyyy-mm-dd HH24:MI:SS')"
               " GROUP BY TY_TRAV ORDER BY TY_TRAV")
        #Afficher la requête SQL
        arcpy.AddMessage(sql + ";")
        contenu = contenu + "\n" + sql + ";"
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        #Afficher les identifiants livrés dans la BDG depuis la date spécifiée
        for trav in resultat:
            #Afficher le nombre d'identifiants livrés du travail 
            arcpy.AddMessage(str(trav))
            contenu = contenu + "\n" + str(trav)
        
        #--------------------
        #Créer la requête SQL pour l'extraction de l'information de la table des contraintes d'intégrité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Extraction de l'information de la table des contraintes d'intégrité : " + table)
        #Définir la SQL de base
        sql = "SELECT GROUPE, DESCRIPTION, REQUETE_SQL, MESSAGE FROM " + table
        #Vérifier si un groupe est spécifié
        if len(groupe) > 0:
            #Ajouter la condition de groupe
            sql = sql + " WHERE GROUPE IN ('" + groupe + "')"
        #Ajouter le tri
        sql = sql + " ORDER BY GROUPE, REQUETE_SQL"
        #Afficher la requête SQL
        arcpy.AddMessage(sql)
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Initialiser les variables de travail
        nbSql = len(resultat)
        cptSql = 0
        nbErr = 0
        nbSqlErr = 0
        sqlErr = []
        #Traiter toutes les contraintes d'intégrité SQL
        for contrainte in resultat:
            #Définir la requête SQL de validation
            groupe = contrainte[0]
            description = contrainte[1]
            sql = contrainte[2]
            message = contrainte[3]
            #Compter le nombre de validation
            cptSql = cptSql + 1
            #Afficher la requête SQL de validation
            arcpy.AddMessage(" ")
            arcpy.AddMessage(str(cptSql) + "/" + str(nbSql) + " : " + groupe + " : " + str(datetime.datetime.now()))
            arcpy.AddMessage(sql)
            #Exécuter la requête SQL de validation
            resultat = self.BDG.query(sql)
            #Vérifier la présence d'une erreur
            if resultat:
                #Afficher la résultat en erreur
                nbSqlErr = len(resultat)
                arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbSqlErr))
                #Compléter la commande SQL
                sql = "-"*80 + "\n-" + description + "\n-" + message + "\n" + "-"*80 + "\n" + sql + ";\n" + "Nombre de valeurs en erreur : " + str(nbSqlErr)
                #Traiter tous les résultats
                for valeur in resultat:
                    #Compter le nombre de valeurs en erreur
                    nbErr = nbErr + valeur[0]
                    #Vérifier le nombre de valeurs trouvées
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
        arcpy.AddMessage("-Liste des erreurs trouvées dans les données.")
        arcpy.AddMessage("Nombre total d'erreurs : " + str(nbErr))
        arcpy.AddMessage("Nombre total de requêtes SQL contenant des erreurs : " + str(len(sqlErr)) + "/" + str(nbSql))
        #Écrire le nombre d'erreurs dans le contenu du courriel
        contenu = contenu + "\n\n-Liste des erreurs trouvées dans les données.\n"
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
            sujet = "Rapport d'intégrité " + env
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "BDRS_PRO"
        table = "CONTRAINTE_INTEGRITE_SQL"
        groupe = ""
        courriel = "michel.pothier@canada.ca"
        
        # Lecture des paramètres
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
        
        #Définir l'objet de validation des données via des requêtes SQL.
        oValiderIntegriteDonneesRequeteSQL = ValiderIntegriteDonneesRequeteSQL()
        
        #Valider les paramètres obligatoires
        oValiderIntegriteDonneesRequeteSQL.validerParamObligatoire(env, table, courriel)
        
        #Exécuter le traitement de validation des données via des requêtes SQL.
        oValiderIntegriteDonneesRequeteSQL.executer(env, table, groupe, courriel)
        
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("-Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("-Succès du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)