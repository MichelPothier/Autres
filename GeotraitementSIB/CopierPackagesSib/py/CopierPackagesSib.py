#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : CopierPackagesSib.py
# Auteur    : Michel Pothier
# Date      : 21 janvier 2015

"""
Application qui permet de copier les packages de la base de données de SIB_PRO dans la base de données de SIB_TST, SIB_DEV ou BDG_SIB_TST.


Paramètres d'entrées:
----------------------
env         : Base de données SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les packages de SIB_PRO.
packages    : Liste des packages que l'on veut copier.

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CopierPackagesSib(object):
#*******************************************************************************************
    """
    Application qui permet de copier les packages de la base de données de SIB_PRO
    dans la base de données de SIB_TST, SIB_DEV ou BDG_SIB_TST.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les packages de SIB.
        
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
    def validerParamObligatoire(self, env, packages):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env         : Base de données SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les packages de SIB_PRO.
        packages    : Liste des packages que l'on veut copier.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(packages) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'packages')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, packages):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour copier les packages de la base de données de SIB_PRO
        
        Paramètres:
        -----------
        env         : Base de données SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les packages de SIB_PRO.
        packages    : Liste des packages que l'on veut copier.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.SibPro     : Objet utilitaire pour traiter des services SIB_PRO.
        self.Sib        : Objet utilitaire pour traiter des services SIB_?.
        sUsagerSib      : Nom de l'usager SIB.
        sUsagerBdPro    : Nom de l'usager de la BD SIB_PRO
        sUsagerBd       : Nom de l'usager de la BD SIB_?
        resultat        : Résultat de la requête SIB.
        sql             : Commande SQL à exécuter.
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        self.SibPro = self.CompteSib.OuvrirConnexionSib("SIB_PRO")
        #Définition du format de la date
        self.SibPro.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        #Extraire le nom de l'usager BD de PRO
        sUsagerBdPro = self.CompteSib.UsagerBd().upper()
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib().upper()
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        #Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        #Extraire le nom de l'usager BD de PRO
        sUsagerBd = self.CompteSib.UsagerBd().upper()
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        resultat = self.SibPro.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Traiter tous les packages
        for package in packages.split(","):
            #Afficher le message de copie d'un package
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Copie du package : " + package)
            
            #Extraire l'information du packages
            sql ="SELECT DBMS_METADATA.GET_DDL ('PACKAGE', OBJECT_NAME) DDL_STRING FROM DBA_OBJECTS WHERE OBJECT_TYPE = 'PACKAGE' AND OBJECT_NAME = '" + package + "' AND OWNER='" + sUsagerBdPro + "'"
            arcpy.AddMessage(sql)
            resultat = self.SibPro.requeteSib(sql)
            
            #Vérifier le résultat
            if resultat:
                #Lire la définition du package
                sql = resultat[0][0].read()
                sql = sql.replace(sUsagerBdPro, sUsagerBd)
                #sql = sql.replace(package.lower(), package.upper())
                sql = re.sub("(?i)" + package,package, sql)
                
                #Ajouter un séparateur entre chaque partie du package (SPEC et BODY)
                sql = sql.replace(package + ";", package + ";\n/\n")
                #Traiter chaque partie (SPEC et BODY) du package
                item = sql.split("\n/\n")
                #Exécuter la définition du package SPEC
                arcpy.AddMessage("SPEC")
                #arcpy.AddMessage(item[0])
                self.Sib.execute(item[0])
                #Vérifier si les deux parties sont présentes
                if len(item) > 1:
                    #Vérifier si le mot CREATE est présent dans le text
                    if "CREATE " in item[1]:
                        #Exécuter la définition du package BODY
                        arcpy.AddMessage("BODY")
                        #arcpy.AddMessage(item[1])
                        self.Sib.execute(item[1])
                
                #Compiler le package en mode DEBUG
                arcpy.AddMessage("- Compilation du package : " + package)
                sql = "ALTER PACKAGE " + package + " COMPILE DEBUG PACKAGE"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
        
        #Vérifier la présence d'erreurs
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Vérifier la présence d'erreurs")
        sql = "SELECT * FROM SYS.USER_ERRORS WHERE TYPE LIKE 'PACKAGE%'"
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env         = "SIB_TST"
        packages    = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            packages = sys.argv[2].replace(";",",")
        
        #Définir l'objet pour copier les packages de SIB.
        oCopierPackagesSib = CopierPackagesSib()
        
        #Valider les paramètres obligatoires.
        oCopierPackagesSib.validerParamObligatoire(env, packages)
        
        #Exécuter le traitement pour copier les packages de SIB.
        oCopierPackagesSib.executer(env, packages)
        
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