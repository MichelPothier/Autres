#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEtatEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 01 septembre 2015

"""
    Application qui permet de modifier l'�tat d'une ou plusieurs �quipes de production dans SIB (actif � inactif ou vice versa).
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                            d�faut = SIB_PRO
    etat            OB      �tat recherch� [0:INACTIF/1:ACTIF].
                            d�faut = 1:ACTIF
    cd_equipe       OB      Codes et noms des �quipes de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierEtatEquipeProduction.py env etat �quipe

    Exemple:
        ModifierEtatEquipeProduction.py SIB_PRO 1:ACTIF "RRC:R�seau Routier Canadien;MNE:DNEC"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEtatEquipeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtatEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de modifier l'�tat d'une ou plusieurs �quipes de production dans SIB (actif � inactif ou vice versa).
    
    """
    
    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier l'�tat d'une ou plusieurs �quipes de production dans SIB (actif � inactif ou vice versa).
        
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
    def validerParamObligatoire(self, env, etat, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        etat            : �tat recherch� [0:INACTIF/1:ACTIF].
        cd_equipe       : Codes et noms des �quipes de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).

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
        
        if (len(cd_equipe) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_equipe')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, etat, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier l'�tat d'une ou plusieurs �quipes de production dans SIB (actif � inactif ou vice versa).
        
        Param�tres:
        -----------
        env             : Type d'environnement
        etat            : �tat recherch� [0:INACTIF/1:ACTIF].
        cd_equipe       : Codes et noms des �quipes de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
        
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
        
        #Traiter toutes les �quipes sp�cifi�es
        for equipe in cd_equipe.split(","):
            #D�finir le code de l'�quipe
            cd_equ = equipe.split(":")[0]
            
            #Valider le code de l'�quipe
            arcpy.AddMessage("- Valider le code de l'�quipe : " + equipe)
            #D�finir la requ�te sql
            sql = "SELECT CD_EQUIPE, ACTIF FROM F108_EQ WHERE CD_EQUIPE='" + cd_equ + "'"
            #Extraire l'information de l'�quipe dans SIB
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si le code de l'�quipe est pr�sent
            if not resultat:
                #Envoyer une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'�quipe n'existe pas : %s" %cd_equ)
            
            #V�rifier si l'�tat est diff�rent
            if etat <> str(resultat[0][1]):
                #Modifier l'�tat de l'�quipe dans la table F108_EQ
                sql = ("UPDATE F108_EQ"
                       " SET ACTIF=" +  etat + ", UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE"
                       " WHERE CD_EQUIPE='" + cd_equ + "'")
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            #Si l'�tat est pareil
            else:
                #Envoyer un avertissement
                arcpy.AddMessage("L'�quipe est d�j� � l'�tat : %s" %etat)
            
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
        cd_equipe   = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            etat = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            cd_equipe = sys.argv[3].upper().replace("'","").replace(";",",")
         
        #D�finir l'objet pour modifier l'�tat d'une ou plusieurs �quipes de production dans SIB (actif � inactif ou vice versa).
        oModifierEtatEquipeProduction = ModifierEtatEquipeProduction()
        
        #Valider les param�tres obligatoires
        oModifierEtatEquipeProduction.validerParamObligatoire(env, etat, cd_equipe)
        
        #Ex�cuter le traitement pour modifier l'�tat d'une ou plusieurs �quipes de production dans SIB (actif � inactif ou vice versa).
        oModifierEtatEquipeProduction.executer(env, etat, cd_equipe)
        
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