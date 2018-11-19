#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEtatExecutantProduction.py
# Auteur    : Michel Pothier
# Date      : 31 août 2015

"""
    Application qui permet de modifier l'état d'un ou plusieurs exécutants de production dans SIB (actif à inactif ou vice versa).
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                            défaut = SIB_PRO
    etat            OB      État recherché [0:INACTIF/1:ACTIF].
                            défaut = 1:ACTIF
    executant       OB      Codes et noms des exécutants de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierEtatExecutantProduction.py env etat executant

    Exemple:
        ModifierEtatExecutantProduction.py SIB_PRO 1:ACTIF TRIFID:Groupe Trifide Inc.;DIGIT:Digital environmental

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEtatExecutantProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtatExecutantProduction(object):
#*******************************************************************************************
    """
    Permet de modifier l'état d'un ou plusieurs exécutants de production dans SIB (actif à inactif ou vice versa).
    
    """
    
    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier l'état d'un ou plusieurs exécutants de production dans SIB (actif à inactif ou vice versa).
        
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
    def validerParamObligatoire(self, env, etat, executant):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        etat            : État recherché [0:INACTIF/1:ACTIF].
        executant       : Codes et noms des exécutants de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).

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
        
        if (len(executant) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'executant')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, etat, executant):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'état d'un ou plusieurs exécutants de production dans SIB (actif à inactif ou vice versa).
        
        Paramètres:
        -----------
        env             : Type d'environnement
        etat            : État recherché [0:INACTIF/1:ACTIF].
        executant       : Codes et noms des exécutants de production qui sont actifs (ACTIF=1) ou inactifs (ACTIF=0).
        
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
        
        #Traiter tous les exécutants spécifiés
        for execu in executant.split(","):
            #Définir le code de l'exécutant
            execu = execu.split(":")[0]
            
            #Valider le code de l'exéctant
            arcpy.AddMessage("- Valider le code de l'exécutant : " + execu)
            #Définir la requête sql
            sql = "SELECT CD_EXECU, ACTIF FROM F604_EX WHERE CD_EXECU='" + execu + "'"
            #Extraire l'information de l'exécutant dans SIB
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si le code de l'exécutant est présent
            if not resultat:
                #Envoyer une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'exécutant n'existe pas : %s" %execu)
            
            #Vérifier si l'état est différent
            if etat <> str(resultat[0][1]):
                #Modifier l'état de l'exécutant dans la table F604_EX
                sql = "UPDATE F604_EX SET ACTIF=" +  etat + ", UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE WHERE CD_EXECU='" + execu + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            #Si l'état est pareil
            else:
                #Envoyer un avertissement
                arcpy.AddMessage("L'exécutant est déjà à l'état : %s" %etat)
            
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
        executant   = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            etat = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            executant = sys.argv[3].upper().replace("'","").replace(";",",")
         
        #Définir l'objet pour modifier l'état d'un ou plusieurs exécutants de production dans SIB (actif à inactif ou vice versa).
        oModifierEtatExecutantProduction = ModifierEtatExecutantProduction()
        
        #Valider les paramètres obligatoires
        oModifierEtatExecutantProduction.validerParamObligatoire(env, etat, executant)
        
        #Exécuter le traitement pour modifier l'état d'un ou plusieurs exécutants de production dans SIB (actif à inactif ou vice versa).
        oModifierEtatExecutantProduction.executer(env, etat, executant)
        
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