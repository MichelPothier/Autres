#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : CopierVuesSib.py
# Auteur    : Michel Pothier
# Date      : 21 janvier 2015

"""
Application qui permet de copier les vues de la base de donn�es de SIB_PRO dans la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.

Param�tres d'entr�es:
----------------------
env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les vues de SIB_PRO.
vues        : Liste des vues que l'on veut copier.

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CopierVuesSib(object):
#*******************************************************************************************
    """
    Application qui permet de copier les vues de la base de donn�es de SIB_PRO dans la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les vues de la base de donn�es de SIB_PRO dans la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.
        
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
    def validerParamObligatoire(self, env, vues):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les vues de SIB_PRO.
        vues        : Liste des vues que l'on veut copier.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(vues) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'vues')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, vues):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour copier les vues de la base de donn�es de SIB_PRO dans la base de donn�es de SIB_TST, SIB_DEV ou BDG_SIB_TST.
        
        Param�tres:
        -----------
        env         : Base de donn�es SIB [SIB_TST/SIB_DEV/BDG_SIB_TST] dans lequel on veut copier les vues de SIB_PRO.
        vues        : Liste des vues que l'on veut copier.
               
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
        
        #Traiter toutes les vues
        for vue in vues.split(","):
            #Afficher le message de copie d'une vue
            arcpy.AddMessage("- Copie de la vue : " + vue)
            
            #Extraire l'information de la vue
            sql ="SELECT DBMS_METADATA.GET_DDL ('VIEW' ,OBJECT_NAME) DDL_STRING FROM DBA_OBJECTS WHERE OBJECT_TYPE = 'VIEW' AND OBJECT_NAME = '" + vue + "' AND OWNER='" + sUsagerBdPro + "' ORDER BY OBJECT_NAME"
            arcpy.AddMessage(sql)
            resultat = self.SibPro.requeteSib(sql)
            
            #V�rifier le r�sultat
            if resultat:
                #Lire la d�finition de la vue
                sql = resultat[0][0].read()
                sql = sql.replace(sUsagerBdPro,sUsagerBd)
                
                #Ex�cuter la d�finition de la vue
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env         = "SIB_TST"
        vues        = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            vues = sys.argv[2].replace(";",",")
        
        #D�finir l'objet pour copier les vues de SIB.
        oCopierVuesSib = CopierVuesSib()
        
        #Valider les param�tres obligatoires.
        oCopierVuesSib.validerParamObligatoire(env, vues)
        
        #Ex�cuter le traitement pour copier les vues de SIB.
        oCopierVuesSib.executer(env, vues)
        
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