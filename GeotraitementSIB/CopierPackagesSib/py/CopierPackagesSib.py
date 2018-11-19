#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : CopierPackagesSib.py
# Auteur    : Michel Pothier
# Date      : 21 janvier 2015

"""
Application qui permet de copier les packages de la base de donn�es de SIB_PRO dans la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.


Param�tres d'entr�es:
----------------------
env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les packages de SIB_PRO.
packages    : Liste des packages que l'on veut copier.

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
Usage:
    CopierPackagesSib.py env packages

Exemple:
    CopierPackagesSib.py SIB_TST ACCES_SQL,POOO_UTI,S000_UTI

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CopierPackagesSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, re, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CopierPackagesSib(object):
#*******************************************************************************************
    """
    Application qui permet de copier les packages de la base de donn�es de SIB_PRO
    dans la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les packages de SIB.
        
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
    def validerParamObligatoire(self, env, packages):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les packages de SIB_PRO.
        packages    : Liste des packages que l'on veut copier.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(packages) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'packages')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, packages):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour copier les packages de la base de donn�es de SIB_PRO
        
        Param�tres:
        -----------
        env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les packages de SIB_PRO.
        packages    : Liste des packages que l'on veut copier.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.SibPro     : Objet utilitaire pour traiter des services SIB_PRO.
        self.Sib        : Objet utilitaire pour traiter des services SIB_?.
        sUsagerSib      : Nom de l'usager SIB.
        sUsagerBdPro    : Nom de l'usager de la BD SIB_PRO
        sUsagerBd       : Nom de l'usager de la BD SIB_?
        resultat        : R�sultat de la requ�te SIB.
        sql             : Commande SQL � ex�cuter.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.SibPro = self.CompteSib.OuvrirConnexionSib("SIB_PRO")
        #D�finition du format de la date
        self.SibPro.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        #Extraire le nom de l'usager BD de PRO
        sUsagerBdPro = self.CompteSib.UsagerBd().upper()
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib().upper()
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        #D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        #Extraire le nom de l'usager BD de PRO
        sUsagerBd = self.CompteSib.UsagerBd().upper()
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.SibPro.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Traiter tous les packages
        for package in packages.split(","):
            #Afficher le message de copie d'un package
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Copie du package : " + package)
            
            #Extraire l'information du packages
            sql ="SELECT DBMS_METADATA.GET_DDL ('PACKAGE', OBJECT_NAME) DDL_STRING FROM DBA_OBJECTS WHERE OBJECT_TYPE = 'PACKAGE' AND OBJECT_NAME = '" + package + "' AND OWNER='" + sUsagerBdPro + "'"
            arcpy.AddMessage(sql)
            resultat = self.SibPro.requeteSib(sql)
            
            #V�rifier le r�sultat
            if resultat:
                #Lire la d�finition du package
                sql = resultat[0][0].read()
                sql = sql.replace(sUsagerBdPro, sUsagerBd)
                #sql = sql.replace(package.lower(), package.upper())
                sql = re.sub("(?i)" + package,package, sql)
                
                #Ajouter un s�parateur entre chaque partie du package (SPEC et BODY)
                sql = sql.replace(package + ";", package + ";\n/\n")
                #Traiter chaque partie (SPEC et BODY) du package
                item = sql.split("\n/\n")
                #Ex�cuter la d�finition du package SPEC
                arcpy.AddMessage("SPEC")
                #arcpy.AddMessage(item[0])
                self.Sib.execute(item[0])
                #V�rifier si les deux parties sont pr�sentes
                if len(item) > 1:
                    #V�rifier si le mot CREATE est pr�sent dans le text
                    if "CREATE " in item[1]:
                        #Ex�cuter la d�finition du package BODY
                        arcpy.AddMessage("BODY")
                        #arcpy.AddMessage(item[1])
                        self.Sib.execute(item[1])
                
                #Compiler le package en mode DEBUG
                arcpy.AddMessage("- Compilation du package : " + package)
                sql = "ALTER PACKAGE " + package + " COMPILE DEBUG PACKAGE"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
        
        #V�rifier la pr�sence d'erreurs
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- V�rifier la pr�sence d'erreurs")
        sql = "SELECT * FROM SYS.USER_ERRORS WHERE TYPE LIKE 'PACKAGE%'"
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if resultat:
            #Retourner une exception
            raise Exception(str(resultat))
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
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
        packages    = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            packages = sys.argv[2].replace(";",",")
        
        #D�finir l'objet pour copier les packages de SIB.
        oCopierPackagesSib = CopierPackagesSib()
        
        #Valider les param�tres obligatoires.
        oCopierPackagesSib.validerParamObligatoire(env, packages)
        
        #Ex�cuter le traitement pour copier les packages de SIB.
        oCopierPackagesSib.executer(env, packages)
        
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