#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEtatEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 01 septembre 2015

"""
    Application qui permet de modifier l'état d'une ou plusieurs équipes de production dans SIB (actif à inactif ou vice versa).
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                            défaut = SIB_PRO
    etat            OB      État recherché [0:INACTIF/1:ACTIF].
                            défaut = 1:ACTIF
    cd_equipe       OB      Codes et noms des équipes de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierEtatEquipeProduction.py env etat équipe

    Exemple:
        ModifierEtatEquipeProduction.py SIB_PRO 1:ACTIF "RRC:Réseau Routier Canadien;MNE:DNEC"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEtatEquipeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtatEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de modifier l'état d'une ou plusieurs équipes de production dans SIB (actif à inactif ou vice versa).
    
    """
    
    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier l'état d'une ou plusieurs équipes de production dans SIB (actif à inactif ou vice versa).
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        # Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, etat, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        etat            : État recherché [0:INACTIF/1:ACTIF].
        cd_equipe       : Codes et noms des équipes de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(etat) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'etat')
        
        if (len(cd_equipe) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_equipe')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, etat, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'état d'une ou plusieurs équipes de production dans SIB (actif à inactif ou vice versa).
        
        Paramètres:
        -----------
        env             : Type d'environnement
        etat            : État recherché [0:INACTIF/1:ACTIF].
        cd_equipe       : Codes et noms des équipes de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        
        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")

        #Définir et valider l'état selon l'état recherché
        actif = etat.split(":")[0]
        
        #Valider l'état
        if actif not in "0,1":
            #Retourner une exception
            raise Exception("L'état est invalide : " + etat)
        
        #Définir l'état
        if actif == "0":
            etat = "1"
        else:
            etat = "0"
        
        #Traiter toutes les équipes spécifiées
        for equipe in cd_equipe.split(","):
            #Définir le code de l'équipe
            cd_equ = equipe.split(":")[0]
            
            #Valider le code de l'équipe
            arcpy.AddMessage("- Valider le code de l'équipe : " + equipe)
            #Définir la requête sql
            sql = "SELECT CD_EQUIPE, ACTIF FROM F108_EQ WHERE CD_EQUIPE='" + cd_equ + "'"
            #Extraire l'information de l'équipe dans SIB
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si le code de l'équipe est présent
            if not resultat:
                #Envoyer une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'équipe n'existe pas : %s" %cd_equ)
            
            #Vérifier si l'état est différent
            if etat <> str(resultat[0][1]):
                #Modifier l'état de l'équipe dans la table F108_EQ
                sql = ("UPDATE F108_EQ"
                       " SET ACTIF=" +  etat + ", UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE"
                       " WHERE CD_EQUIPE='" + cd_equ + "'")
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            #Si l'état est pareil
            else:
                #Envoyer un avertissement
                arcpy.AddMessage("L'équipe est déjà à l'état : %s" %etat)
            
            #Afficher un message de séparation
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env         = "SIB_PRO"
        etat        = "1:ACTIF"
        cd_equipe   = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            etat = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            cd_equipe = sys.argv[3].upper().replace("'","").replace(";",",")
         
        #Définir l'objet pour modifier l'état d'une ou plusieurs équipes de production dans SIB (actif à inactif ou vice versa).
        oModifierEtatEquipeProduction = ModifierEtatEquipeProduction()
        
        #Valider les paramètres obligatoires
        oModifierEtatEquipeProduction.validerParamObligatoire(env, etat, cd_equipe)
        
        #Exécuter le traitement pour modifier l'état d'une ou plusieurs équipes de production dans SIB (actif à inactif ou vice versa).
        oModifierEtatEquipeProduction.executer(env, etat, cd_equipe)
        
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