#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEtatCompteSib.py
# Auteur    : Michel Pothier
# Date      : 26 ao�t 2015

"""
    Application qui permet de modifier l'�tat d'un ou plusieurs comptes existants dans SIB (actif � inactif ou vice versa).
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                            d�faut = SIB_PRO
    etat            OB      �tat recherch�.
                            d�faut = 1:ACTIF
    cd_user         OB      Codes des usagers SIB qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierEtatCompteSib.py env etat cd_user

    Exemple:
        ModifierEtatCompteSib.py SIB_PRO 1:ACTIF MPOTHIER;LDION

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEtatCompteSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtatCompteSib(object):
#*******************************************************************************************
    """
    Permet de modifier l'�tat d'un ou plusieurs comptes existants dans SIB (actif � inactif ou vice versa).
    
    """
    
    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier l'�tat d'un ou plusieurs comptes existants dans SIB (actif � inactif ou vice versa).
        
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
    def validerParamObligatoire(self, env, etat, cd_user):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        etat            : �tat recherch�.
        cd_user         : Codes des usagers SIB qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(etat) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'etat')
        
        if (len(cd_user) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_user')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, etat, cd_user):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier l'�tat d'un ou plusieurs comptes existants dans SIB (actif � inactif ou vice versa).
        
        Param�tres:
        -----------
        env             : Type d'environnement
        etat            : �tat recherch�.
        cd_user         : Codes des usagers SIB qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
        
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

        #D�finir et valider l'�tat selon l'�tat recherch�
        actif = etat.split(":")[0]
        
        #Valider l'�tat
        if actif not in "0,1":
            #Retourner une exception
            raise Exception("L'�tat est invalide : " + etat)
        
        #D�finir l'�tat
        if actif == "0":
            etat = "1"
        else:
            etat = "0"
        
        #Traiter tous les usagers sp�cifi�s
        for user in cd_user.split(","):
            #D�finir le code de l'usager
            usager = user.split(":")[0]
            
            #Valider le code de l'usager
            arcpy.AddMessage("- Valider le code de l'usag� : " + usager)
            #D�finir la requ�te sql
            sql = "SELECT CD_USER, ACTIF FROM F005_US WHERE CD_USER='" + usager + "'"
            #Extraire l'information de l'usager dans SIB
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si le code de l'usager est pr�sent
            if not resultat:
                #Envoyer une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'usager n'existe pas : %s" %usager)
            
            #V�rifier si l'�tat est diff�rent
            if etat <> str(resultat[0][1]):
                #Modifier l'�tat de l'usager dans la table F005_US
                sql = "UPDATE F005_US SET ACTIF=" +  etat + ", UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE WHERE CD_USER='" + usager + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            #Si l'�tat est pareil
            else:
                #Envoyer un avertissement
                arcpy.AddMessage("Le compte de l'usager est d�ja � l'�tat : %s" %etat)
            
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
        etat        = "1:ACTIF"
        cd_user     = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            etat = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            cd_user = sys.argv[3].upper().replace("'","").replace(";",",")
         
        #D�finir l'objet pour modifier l'�tat d'un ou plusieurs comptes existants dans SIB (actif � inactif ou vice versa).
        oModifierEtatCompteSib = ModifierEtatCompteSib()
        
        #Valider les param�tres obligatoires
        oModifierEtatCompteSib.validerParamObligatoire(env, etat, cd_user)
        
        #Ex�cuter le traitement pour modifier l'�tat d'un ou plusieurs comptes existants dans SIB (actif � inactif ou vice versa).
        oModifierEtatCompteSib.executer(env, etat, cd_user)
        
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