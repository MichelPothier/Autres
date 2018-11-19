#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : CopierVuesSib.py
# Auteur    : Michel Pothier
# Date      : 21 janvier 2015

"""
Application qui permet de copier les vues de la base de données de SIB_PRO dans la base de données de SIB_TST, SIB_DEV ou BDG_SIB_TST.

Paramètres d'entrées:
----------------------
env         : Base de données SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les vues de SIB_PRO.
vues        : Liste des vues que l'on veut copier.

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    CopierVuesSib.py env vues

Exemple:
    CopierVuesSib.py SIB_TST V503_TR,V502_NC

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CopierVuesSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CopierVuesSib(object):
#*******************************************************************************************
    """
    Application qui permet de copier les vues de la base de données de SIB_PRO dans la base de données de SIB_TST, SIB_DEV ou BDG_SIB_TST.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les vues de la base de données de SIB_PRO dans la base de données de SIB_TST, SIB_DEV ou BDG_SIB_TST.
        
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
    def validerParamObligatoire(self, env, vues):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env         : Base de données SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les vues de SIB_PRO.
        vues        : Liste des vues que l'on veut copier.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(vues) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'vues')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, vues):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour copier les vues de la base de données de SIB_PRO dans la base de données de SIB_TST, SIB_DEV ou BDG_SIB_TST.
        
        Paramètres:
        -----------
        env         : Base de données SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les vues de SIB_PRO.
        vues        : Liste des vues que l'on veut copier.
               
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
        
        #Traiter toutes les vues
        for vue in vues.split(","):
            #Afficher le message de copie d'une vue
            arcpy.AddMessage("- Copie de la vue : " + vue)
            
            #Extraire l'information de la vue
            sql ="SELECT DBMS_METADATA.GET_DDL ('VIEW' ,OBJECT_NAME) DDL_STRING FROM DBA_OBJECTS WHERE OBJECT_TYPE = 'VIEW' AND OBJECT_NAME = '" + vue + "' AND OWNER='" + sUsagerBdPro + "' ORDER BY OBJECT_NAME"
            arcpy.AddMessage(sql)
            resultat = self.SibPro.requeteSib(sql)
            
            #Vérifier le résultat
            if resultat:
                #Lire la définition de la vue
                sql = resultat[0][0].read()
                sql = sql.replace(sUsagerBdPro,sUsagerBd)
                
                #Exécuter la définition de la vue
                #arcpy.AddMessage(sql)
                self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env         = "SIB_TST"
        vues        = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            vues = sys.argv[2].replace(";",",")
        
        #Définir l'objet pour copier les vues de SIB.
        oCopierVuesSib = CopierVuesSib()
        
        #Valider les paramètres obligatoires.
        oCopierVuesSib.validerParamObligatoire(env, vues)
        
        #Exécuter le traitement pour copier les vues de SIB.
        oCopierVuesSib.executer(env, vues)
        
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