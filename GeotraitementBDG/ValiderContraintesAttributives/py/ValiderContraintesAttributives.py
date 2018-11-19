#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderContraintesAttributives.py
# Auteur    : Michel Pothier
# Date      : 20 f�vrier 2018

"""
Outil qui permet de valider l'int�grit� des contraintes attributives pour les donn�es contenues dans une base de donn�es Oracle (G�odatabase).

Les contraintes attributives sont sous forme de requ�tes SQL et sont contenues dans une table.

Param�tres d'entr�es:
----------------------
geodatabase OB  Nom de la G�odatabase dans lesquels les tables � valider sont pr�sentes.
                d�faut = "Database connections\BDRS_PRO_BDG_DBA.sde"
table       OB  Nom de la table contenant l'information pour valider les donn�es via des requ�tes SQL.
                d�faut : "Database connections\BDRS_PRO_BDG_DBA.sde\BDG_DBA.CONTRAINTE_INTEGRITE_SQL"
fitre       OP  Requete attributive pour traiter seulement une partie des contraintes.
                d�faut = 
courriel    OB  Adresses de courriel utilis�es pour envoyer le rapport d'ex�cution.
                d�faut = michel.pothier@canada.ca;odette.trottier@canada.ca

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import EnvoyerCourriel

#*******************************************************************************************
class ValiderContraintesAttributives(object):
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
        self.dateDebut : Contient la date de d�but sans microseconde.
        
        """

        #D�finir la date de d�but
        self.dateDebut = datetime.datetime.now().replace(microsecond=0)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, geodatabase, table, courriel):
    #-------------------------------------------------------------------------------------
        """
        Valider les param�tres obligatoires.
        
        Param�tres:
        -----------
        geodatabase : Nom de la G�odatabase dans lesquels les tables � valider sont pr�sentes.
        table       : Nom de la table contenant l'information pour valider les donn�es via des requ�tes SQL.
        courriel    : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        #arcpy.AddMessage("-V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(geodatabase) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'geodatabase')
        
        if (len(table) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'table')
        
        if (len(courriel) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'courriel')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, geodatabase, table, filtre, courriel):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider l'int�grit� des donn�es.
        
        Param�tres:
        -----------
        geodatabase : Nom de la G�odatabase dans lesquels les tables � valider sont pr�sentes.
        table       : Nom de la table contenant l'information pour valider les donn�es via des requ�tes SQL.
        filtre      : Requete attributive pour traiter seulement une partie des contraintes.
        courriel    : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
        
        Variables:
        ----------      
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        resultat        : R�sultat de la requ�te BDG.
        cptSql          : Nombre de validation effectu�e.
        """
        
        #Initialiser le contenu du courriel
        contenu = ""
        #Remplir la commande dans le contenu du courriel
        for item in sys.argv:
            contenu = contenu + item + " "
        
        #Remplir la date de d�but dans le contenu du courriel
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-D�but : " + str(self.dateDebut))
        contenu = contenu + "\n\n-D�but : " + str(self.dateDebut)
        
        #--------------------
        arcpy.AddMessage("-Validation de la table des contraintes : " + table)
        contenu = contenu + "\n-Validation de la table des contraintes : " + table
        #D�finr la G�odatabase
        arcpy.env.workspace = os.path.dirname(table)
        #D�finir la table des contraintes
        tbls = arcpy.ListTables(os.path.basename(table))
        #Validation de la table des contraintes
        if len(tbls)<>1:
            #Sortir en erreur
            raise Exception("ERREUR : La table des contraintes est invalide : " + table)
        #D�finir la table
        tbl = tbls[0]
        
        #--------------------
        #D�finir la connexion � la g�odatabase
        arcpy.AddMessage("-Connexion de la G�odatabase : " + geodatabase)
        contenu = contenu + "\n-Connexion � la BDG : " + geodatabase
        self.BDG = arcpy.ArcSDESQLExecute(geodatabase)
        
        #--------------------
        #Cr�er la requ�te SQL pour l'extraction des identifiants livr�s dans la BDG.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("----------------------------")
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
        resultat = self.BDG.execute(sql)
        #V�rifier la pr�sence d'une livraison
        if type(resultat) is list:
            #Afficher les identifiants livr�s dans la BDG depuis la date sp�cifi�e
            for trav in resultat:
                #Afficher le nombre d'identifiants livr�s du travail 
                arcpy.AddMessage(str(trav).replace(".0,",","))
                contenu = contenu + "\n" + str(trav).replace(".0,",",")
        
        #--------------------
        #Cr�er la requ�te SQL pour l'extraction de l'information de la table des contraintes d'int�grit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("----------------------------")
        arcpy.AddMessage("-Extraction de l'information de la table des contraintes d'int�grit� : " + tbl)
        #D�finir la SQL de base
        sql = "SELECT GROUPE, DESCRIPTION, REQUETE_SQL, MESSAGE FROM " + tbl
        #V�rifier si un filtre est sp�cifi�
        if len(filtre) > 0:
            #Ajouter le filtre dans la requ�te SQL
            sql = sql + " WHERE " + filtre
        #Ajouter le tri
        sql = sql + " ORDER BY GROUPE, REQUETE_SQL"
        #Afficher la requ�te SQL
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.execute(sql)
        
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
            resultat = self.BDG.execute(sql)
            #V�rifier la pr�sence d'une erreur
            if type(resultat) is list:
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
                        arcpy.AddWarning(str(valeur).replace(".0,",","))
                        #Conserver les valeurs en erreur
                        sql = sql + "\n" + str(valeur).replace(".0,",",")
                #Ajouter la commande SQL en erreur
                sqlErr.append(sql)
        
        #--------------------
        #Afficher le nombre d'erreurs
        arcpy.AddMessage(" ")
        arcpy.AddMessage("----------------------------")
        arcpy.AddMessage("-Liste des erreurs trouv�es dans les donn�es.")
        arcpy.AddMessage("Nombre total d'erreurs : " + str(nbErr).replace(".0",""))
        arcpy.AddMessage("Nombre total de requ�tes SQL contenant des erreurs : " + str(len(sqlErr)) + "/" + str(nbSql))
        #�crire le nombre d'erreurs dans le contenu du courriel
        contenu = contenu + "\n\n----------------------------\n"
        contenu = contenu + "-Liste des erreurs trouv�es dans les donn�es.\n"
        contenu = contenu + "Nombre total d'erreurs : " + str(nbErr).replace(".0","") + "\n"
        contenu = contenu + "Nombre total de requetes SQL contenant des erreurs : " + str(len(sqlErr)) + "/" + str(nbSql) + "\n"
        #Traiter toutes les commandes SQL en erreur
        for sql in sqlErr:
            #Afficher le SQL en erreur
            arcpy.AddMessage(" ")
            arcpy.AddWarning(sql)
            contenu = contenu + "\n" + sql + "\n"
        
        #Fermeture de la connexion de la G�odatabase
        arcpy.AddMessage(" ")
        arcpy.AddMessage("-Fermeture de la connexion de la G�odatabase")
        del self.BDG
        
        #--------------------
        #Envoit d'un courriel aux responsables
        arcpy.AddMessage("-Envoit d'un courriel aux responsables")
        #Envoyer un courriel aux responsables
        for destinataire in courriel.split(";"):
            #Envoyer un courriel
            sujet = "Rapport d'int�grit� : " + table
            contenu = contenu + "\nFin : " + str(datetime.datetime.now()) + "\n"
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
        geodatabase = "Database connections\BDRS_PRO_BDG_DBA.sde"
        table = "Database connections\BDRS_PRO_BDG_DBA.sde\CONTRAINTE_INTEGRITE_SQL"
        filtre = ""
        courriel = "michel.pothier@canada.ca"
        
        # Lecture des param�tres
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
        
        #D�finir l'objet de validation des donn�es via des requ�tes SQL.
        oValiderContraintesAttributives = ValiderContraintesAttributives()
        
        #Valider les param�tres obligatoires
        oValiderContraintesAttributives.validerParamObligatoire(geodatabase, table, courriel)
        
        #Ex�cuter le traitement de validation des donn�es via des requ�tes SQL.
        oValiderContraintesAttributives.executer(geodatabase, table, filtre, courriel)
        
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