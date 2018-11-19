#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireExecutantProduction.py
# Auteur    : Michel Pothier
# Date      : 27 août 2015

"""
    Application qui permet de détruire un ou plusieurs exécutants de production dans SIB et ses contacts.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_execu        OB      Liste des codes d'exécutant de production inactifs à détruire.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireExecutantProduction.py env cd_execu 

    Exemple:
        DetruireExecutantProduction.py SIB_PRO CITS;CITO

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireExecutantProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireExecutantProduction(object):
#*******************************************************************************************
    """
    Permet de détruire un ou plusieurs exécutants de production inactifs dans SIB et ses contacts.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire un ou plusieurs exécutants de production inactifs dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_execu):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Liste des codes d'exécutant de production inactifs à détruire.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(cd_execu) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_execu')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_execu):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs exécutants de production inactifs dans SIB et ses contacts.
        
        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Liste des codes d'exécutant de production inactifs à détruire.
        
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
        
        #Traiter tous les exécutants
        for executant in cd_execu.split(","):
            #Détruire le contact
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Détruire l'information de l'exécutant : ")
            arcpy.AddWarning(executant)
            
            #Définir le code de l'exécutant
            execu = executant.split(":")[0]
            
            #Valider l'exécutant de production dans la table F604_EX
            sql = "SELECT CD_EXECU, ACTIF FROM F604_EX WHERE CD_EXECU='" + execu + "'"
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si l'exécutant de production est absent
            if len(resultat) == 0:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'exécutant de production '" + execu + "' est absent") 
            #Vérifier si l'exécutant de production est actif
            if resultat[0][1] == 1:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'exécutant de production '" + execu + "' est actif et ne peut être détruit")
            
            #Vérifier l'exécutant de production dans la table F604_EX
            arcpy.AddMessage("- Vérifier l'exécutant de production")
            sql = "SELECT * FROM F604_EX WHERE CD_EXECU='" + execu + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Afficher l'information de l'exécutant de production
            arcpy.AddWarning(str(resultat[0]))
            #Initialiser la commande SQL de modifification
            arcpy.AddMessage("- Détruire l'exécutant de production")
            sql = "DELETE F604_EX WHERE CD_EXECU='" + execu + "'"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
            
            #Vérifier les contacts qui sont associés à un exécutant
            arcpy.AddMessage("- Vérifier les contacts qui sont associés à un exécutant")
            sql = "SELECT * FROM F607_CO WHERE CD_EXECU='" + execu + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Traiter tous les items du résultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #Détruire les contacts qui sont associés à un exécutant
                arcpy.AddMessage("- Détruire les contacts qui sont associés à un exécutant")
                sql = "DELETE F607_CO WHERE CD_EXECU='" + execu + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donnée présente")                
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
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
        cd_execu    = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_execu = sys.argv[2].replace("'","").replace(";",",")
        
        #Définir l'objet pour détruire un ou plusieurs exécutants de production inactifs dans SIB.
        oDetruireExecutantProduction = DetruireExecutantProduction()
        
        #Valider les paramètres obligatoires
        oDetruireExecutantProduction.validerParamObligatoire(env, cd_execu)
        
        #Exécuter le traitement pour détruire un ou plusieurs exécutants de production inactifs dans SIB.
        oDetruireExecutantProduction.executer(env, cd_execu)
    
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