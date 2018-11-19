#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : CopierDonneesTablesSib.py
# Auteur    : Michel Pothier
# Date      : 20 janvier 2015

"""
Application qui permet de copier les donn�es des tables de la base de donn�es de SIB_PRO
dans les m�mes tables de la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.

Param�tres d'entr�es:
----------------------
env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les donn�es de SIB_PRO.
tables      : Liste des tables que l'on veut copier.

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
Usage:
    CopierDonneesTablesSib.py env tables

Exemple:
    CopierDonneesTablesSib.py SIB_TST F502_PS,F503_TR

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CopierDonneesTablesSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CopierDonneesTablesSib(object):
#*******************************************************************************************
    """
    Application qui permet de copier les donn�es des tables de la base de donn�es de SIB_PRO
    dans les m�mes tables de la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les donn�es des tables de SIB_PRO dans une autre BD de SIB.
        
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
    def validerParamObligatoire(self, env, tables):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les donn�es de SIB_PRO.
        tables      : Liste des tables que l'on veut copier.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(tables) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'tables')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, tables):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour copier les donn�es des tables de SIB_PRO dans une autre BD de SIB.
        
        Param�tres:
        -----------
        env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les donn�es de SIB_PRO.
        tables      : Liste des tables que l'on veut copier.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.SibPro = self.CompteSib.OuvrirConnexionSib("SIB_PRO")
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #D�finition du format de la date
        self.SibPro.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        
        #D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.SibPro.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Traiter toutes les tables � copier
        for table in tables.split(","):
            #Afficher le message de copie des tables
            arcpy.AddMessage("- Copie de la table : " + table)
            #Extraire l'information de la table
            sql = "DELETE " + table
            #arcpy.AddMessage(sql)
            self.Sib.execute(sql)
            #Extraire l'information de la table
            sql = "SELECT * FROM " + table
            #arcpy.AddMessage(sql)
            resultat = self.SibPro.requeteSib(sql)
            #Afficher le message u nombre de valeurs
            arcpy.AddMessage("  Nombre valeurs : " + str(len(resultat)))
            #Copier la table
            for item in resultat:
                #Ins�rer les donn�es dans la table
                sql = "INSERT INTO " + table + " VALUES ("
                #Traiter toutes les valeurs
                for val in item:
                    if val == None:
                        sql = sql + "NULL" + ","
                    elif type(val) is datetime.datetime:
                        sql = sql + "'" + val.strftime('%Y/%m/%d %H:%M:%S') + "',"
                    elif type(val) is str:
                        sql = sql + "'" + val.replace("'","''") + "',"
                    else:
                        sql = sql + str(val) + ","
                #Terminer la requ�te ad�quatement
                sql = sql[:-1] + ")"
                #arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            
            #Accepter les modifications
            #arcpy.AddMessage("- Accepter les modifications")
            sql = "COMMIT"
            #arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
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
        env         = "SIB_TST"
        tables      = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            tables = sys.argv[2].replace(";",",")
        
        #D�finir l'objet pour copier les donn�es des tables de SIB_PRO.
        oCopierDonneesTablesSib = CopierDonneesTablesSib()
        
        #Valider les param�tres obligatoires.
        oCopierDonneesTablesSib.validerParamObligatoire(env, tables)
        
        #Ex�cuter le traitement pour copier les donn�es des tables de SIB_PRO.
        oCopierDonneesTablesSib.executer(env, tables)
        
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