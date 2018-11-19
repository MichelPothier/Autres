#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderContraintesAttributives.py
# Auteur    : Michel Pothier
# Date      : 20 février 2018

"""
Outil qui permet de valider l'intégrité des contraintes attributives pour les données contenues dans une base de données Oracle (Géodatabase).

Les contraintes attributives sont sous forme de requêtes SQL et sont contenues dans une table.

Paramètres d'entrées:
----------------------
geodatabase OB  Nom de la Géodatabase dans lesquels les tables à valider sont présentes.
                défaut = "Database connections\BDRS_PRO_BDG_DBA.sde"
table       OB  Nom de la table contenant l'information pour valider les données via des requêtes SQL.
                défaut : "Database connections\BDRS_PRO_BDG_DBA.sde\BDG_DBA.CONTRAINTE_INTEGRITE_SQL"
fitre       OP  Requete attributive pour traiter seulement une partie des contraintes.
                défaut = 
courriel    OB  Adresses de courriel utilisées pour envoyer le rapport d'exécution.
                défaut = michel.pothier@canada.ca;odette.trottier@canada.ca

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    ValiderContraintesAttributives.py geodatabase table filtre courriel

Exemple:
    ValiderContraintesAttributives.py "Database connections\BDRS_PRO_BDG_DBA.sde" "Database connections\BDRS_PRO_BDG_DBA.sde\BDG_DBA.CONTRAINTE_INTEGRITE_SQL" "NOM_TABLE='BDG_AIRE_DESIGNEE_0'" michel.pothier@canada.ca

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderContraintesAttributives.py 1161 2018-02-21 14:56:11Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import EnvoyerCourriel

#*******************************************************************************************
class ValiderContraintesAttributives(object):
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
        self.dateDebut : Contient la date de début sans microseconde.
        
        """

        #Définir la date de début
        self.dateDebut = datetime.datetime.now().replace(microsecond=0)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, geodatabase, table, courriel):
    #-------------------------------------------------------------------------------------
        """
        Valider les paramètres obligatoires.
        
        Paramètres:
        -----------
        geodatabase : Nom de la Géodatabase dans lesquels les tables à valider sont présentes.
        table       : Nom de la table contenant l'information pour valider les données via des requêtes SQL.
        courriel    : Adresse courriel utilisée pour envoyer le rapport d'exécution.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        #arcpy.AddMessage("-Vérification de la présence des paramètres obligatoires")
        
        if (len(geodatabase) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'geodatabase')
        
        if (len(table) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'table')
        
        if (len(courriel) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'courriel')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, geodatabase, table, filtre, courriel):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider l'intégrité des données.
        
        Paramètres:
        -----------
        geodatabase : Nom de la Géodatabase dans lesquels les tables à valider sont présentes.
        table       : Nom de la table contenant l'information pour valider les données via des requêtes SQL.
        filtre      : Requete attributive pour traiter seulement une partie des contraintes.
        courriel    : Adresse courriel utilisée pour envoyer le rapport d'exécution.
        
        Variables:
        ----------      
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        resultat        : Résultat de la requête BDG.
        cptSql          : Nombre de validation effectuée.
        """
        
        #Initialiser le contenu du courriel
        contenu = ""
        #Remplir la commande dans le contenu du courriel
        for item in sys.argv:
            contenu = contenu + item + " "
        
        #Remplir la date de début dans le contenu du courriel
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Début : " + str(self.dateDebut))
        contenu = contenu + "\n\n-Début : " + str(self.dateDebut)
        
        #--------------------
        arcpy.AddMessage("-Validation de la table des contraintes : " + table)
        contenu = contenu + "\n-Validation de la table des contraintes : " + table
        #Définr la Géodatabase
        arcpy.env.workspace = os.path.dirname(table)
        #Définir la table des contraintes
        tbls = arcpy.ListTables(os.path.basename(table))
        #Validation de la table des contraintes
        if len(tbls)<>1:
            #Sortir en erreur
            raise Exception("ERREUR : La table des contraintes est invalide : " + table)
        #Définir la table
        tbl = tbls[0]
        
        #--------------------
        #Définir la connexion à la géodatabase
        arcpy.AddMessage("-Connexion de la Géodatabase : " + geodatabase)
        contenu = contenu + "\n-Connexion à la BDG : " + geodatabase
        self.BDG = arcpy.ArcSDESQLExecute(geodatabase)
        
        #--------------------
        #Créer la requête SQL pour l'extraction des identifiants livrés dans la BDG.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("----------------------------")
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
        resultat = self.BDG.execute(sql)
        #Vérifier la présence d'une livraison
        if type(resultat) is list:
            #Afficher les identifiants livrés dans la BDG depuis la date spécifiée
            for trav in resultat:
                #Afficher le nombre d'identifiants livrés du travail 
                arcpy.AddMessage(str(trav).replace(".0,",","))
                contenu = contenu + "\n" + str(trav).replace(".0,",",")
        
        #--------------------
        #Créer la requête SQL pour l'extraction de l'information de la table des contraintes d'intégrité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("----------------------------")
        arcpy.AddMessage("-Extraction de l'information de la table des contraintes d'intégrité : " + tbl)
        #Définir la SQL de base
        sql = "SELECT GROUPE, DESCRIPTION, REQUETE_SQL, MESSAGE FROM " + tbl
        #Vérifier si un filtre est spécifié
        if len(filtre) > 0:
            #Ajouter le filtre dans la requête SQL
            sql = sql + " WHERE " + filtre
        #Ajouter le tri
        sql = sql + " ORDER BY GROUPE, REQUETE_SQL"
        #Afficher la requête SQL
        arcpy.AddMessage(sql)
        #Exécuter la requête SQL
        resultat = self.BDG.execute(sql)
        
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
            resultat = self.BDG.execute(sql)
            #Vérifier la présence d'une erreur
            if type(resultat) is list:
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
                        arcpy.AddWarning(str(valeur).replace(".0,",","))
                        #Conserver les valeurs en erreur
                        sql = sql + "\n" + str(valeur).replace(".0,",",")
                #Ajouter la commande SQL en erreur
                sqlErr.append(sql)
        
        #--------------------
        #Afficher le nombre d'erreurs
        arcpy.AddMessage(" ")
        arcpy.AddMessage("----------------------------")
        arcpy.AddMessage("-Liste des erreurs trouvées dans les données.")
        arcpy.AddMessage("Nombre total d'erreurs : " + str(nbErr).replace(".0",""))
        arcpy.AddMessage("Nombre total de requêtes SQL contenant des erreurs : " + str(len(sqlErr)) + "/" + str(nbSql))
        #Écrire le nombre d'erreurs dans le contenu du courriel
        contenu = contenu + "\n\n----------------------------\n"
        contenu = contenu + "-Liste des erreurs trouvées dans les données.\n"
        contenu = contenu + "Nombre total d'erreurs : " + str(nbErr).replace(".0","") + "\n"
        contenu = contenu + "Nombre total de requetes SQL contenant des erreurs : " + str(len(sqlErr)) + "/" + str(nbSql) + "\n"
        #Traiter toutes les commandes SQL en erreur
        for sql in sqlErr:
            #Afficher le SQL en erreur
            arcpy.AddMessage(" ")
            arcpy.AddWarning(sql)
            contenu = contenu + "\n" + sql + "\n"
        
        #Fermeture de la connexion de la Géodatabase
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Fermeture de la connexion de la Géodatabase")
        del self.BDG
        
        #--------------------
        #Envoit d'un courriel aux responsables
        arcpy.AddMessage("-Envoit d'un courriel aux responsables")
        #Envoyer un courriel aux responsables
        for destinataire in courriel.split(";"):
            #Envoyer un courriel
            sujet = "Rapport d'intégrité : " + table
            contenu = contenu + "\nFin : " + str(datetime.datetime.now()) + "\n"
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
        geodatabase = "Database connections\BDRS_PRO_BDG_DBA.sde"
        table = "Database connections\BDRS_PRO_BDG_DBA.sde\CONTRAINTE_INTEGRITE_SQL"
        filtre = ""
        courriel = "michel.pothier@canada.ca"
        
        # Lecture des paramètres
        if len(sys.argv) > 1:
            geodatabase = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            table = sys.argv[2]
        
        if len(sys.argv) > 3:
            if sys.argv[3] <> '#':
                filtre = sys.argv[3]
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> '#':
                courriel = sys.argv[4]
        
        #Définir l'objet de validation des données via des requêtes SQL.
        oValiderContraintesAttributives = ValiderContraintesAttributives()
        
        #Valider les paramètres obligatoires
        oValiderContraintesAttributives.validerParamObligatoire(geodatabase, table, courriel)
        
        #Exécuter le traitement de validation des données via des requêtes SQL.
        oValiderContraintesAttributives.executer(geodatabase, table, filtre, courriel)
        
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