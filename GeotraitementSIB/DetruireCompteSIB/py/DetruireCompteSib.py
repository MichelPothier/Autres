#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireCompteSib.py
# Auteur    : Michel Pothier
# Date      : 24 octobre 2014

"""
    Application qui permet de d�truire toute l'information d'un ou plusieurs comptes existants dans SIB qui sont inactifs (ACTIF=0).
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                            d�faut = SIB_PRO
    cd_user         OB      Codes des usagers SIB qui sont inactifs (ACTIF=0).
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireCompteSib.py env cd_user

    Exemple:
        DetruireCompteSib.py SIB_PRO MPOTHIER;LDION

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireCompteSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireCompteSib(object):
#*******************************************************************************************
    """
    Permet de d�truire un ou plusieurs comptes existants dans SIB qui sont inactifs (ACTIF=0).
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire un ou plusieurs comptes existants dans SIB qui sont inactifs (ACTIF=0).
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        # D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, cd_user):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        cd_user         : Codes des usagers SIB qui sont inactifs (ACTIF=0).

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(cd_user) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_user')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_user):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire un ou plusieurs comptes existants dans SIB qui sont inactifs (ACTIF=0).
        
        Param�tres:
        -----------
        env             : Type d'environnement
        cd_user         : Codes des usagers SIB qui sont inactifs (ACTIF=0).
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        
        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Traiter tous les usagers sp�cifi�s
        for user in cd_user.split(","):
            #D�finir le code de l'usager
            usager = user.split(":")[0]
            
            #Valider le code de l'usager
            arcpy.AddMessage("- Valider le code de l'usag� : " + usager)
            #D�finir la requ�te sql
            sql = "SELECT CD_USER, ACTIF FROM F005_US WHERE CD_USER='" + usager + "'"
            arcpy.AddMessage(sql)
            #Extraire l'information de l'usager dans SIB
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si le code de l'usager est pr�sent
            if not resultat:
                #Envoyer une exception
                raise Exception("Le code de l'usager n'existe pas : %s" %usager)
            #V�rifier si l'usager est ACTIF
            if resultat[0][1] == 1:
                #Envoyer une exception
                raise Exception("Le code de l'usager est ACTIF et ne peut �tre d�truit : %s" %usager)
            
            #V�rifier l'usager dans la table F007_UG des groupes d'usagers
            arcpy.AddMessage("- V�rifier l'usager dans la table F007_UG des groupes d'usagers")
            sql = "SELECT * FROM F007_UG WHERE CD_USER='" + usager + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les items du r�sultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #D�truire l'usager dans la table F007_UG des groupes d'usagers
                sql = "DELETE F007_UG WHERE CD_USER='" + usager + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donn�e pr�sente")               
            
            #V�rifier l'usager dans la table F005_US
            arcpy.AddMessage("- V�rifier l'information de l'usager")
            sql = "SELECT * FROM F005_US WHERE CD_USER='" + usager + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            arcpy.AddWarning(resultat[0])
            #D�truire l'usager dans la table F005_US
            sql = "DELETE F005_US WHERE CD_USER='" + usager + "'"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
            
            #Afficher un message de s�paration
            arcpy.AddMessage(" ")

        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        cd_user     = ""

        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            cd_user = sys.argv[2].upper().replace("'","").replace(";",",")
 
        #D�finir l'objet pour d�truire un ou plusieurs comptes existants dans SIB.
        oDetruireCompteSib = DetruireCompteSib()
        
        #Valider les param�tres obligatoires
        oDetruireCompteSib.validerParamObligatoire(env, cd_user)
        
        #Ex�cuter le traitement pour d�truire un ou plusieurs comptes existants dans SIB.
        oDetruireCompteSib.executer(env, cd_user)
    
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