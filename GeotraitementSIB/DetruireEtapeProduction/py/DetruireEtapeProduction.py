#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireEtapeProduction.py
# Auteur    : Michel Pothier
# Date      : 09 août 2016

"""
    Application qui permet de détruire l'information d'une ou plusieurs étapes de production dans SIB qui sont inactives et non utilisées.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    listeEtape      OB      Liste des codes d'étape de production non actifs et non utilisés.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireEtapeProduction.py env listeEtape

    Exemple:
        DetruireEtapeProduction.py SIB_PRO PREP;INS

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEtapeProduction.py 2105 2016-08-22 17:40:14Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireEtapeProduction(object):
#*******************************************************************************************
    """
    Permet de détruire l'information d'une ou plusieurs étapes de production dans SIB qui sont inactives et non utilisées.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification de l'information d'une étape de production.
        
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
    def validerParamObligatoire(self, env, listeEtape):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        listeEtape      : Liste des codes d'étape de production non actifs et non utilisés.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(listeEtape) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'listeEtape')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, listeEtape):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire l'information d'une ou plusieurs étapes de production dans SIB qui sont inactives et non utilisées.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        listeEtape      : Liste des codes d'étape de production non actifs et non utilisés.
        
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
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        #Définir la commande SQL
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        #Afficher la commande SQL
        arcpy.AddMessage(sql)
        #Exécuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Traiter toutes les étapes de production
        for etp in listeEtape.split(","):
            #Définir le cd_etp sans description
            cd_etp = etp.replace("'","").split(" ")[0]
            
            #Valider si l'étape de production est valide
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Valider l'étape de production ...")
            #Définir la commande pour valider l'étape
            sql = "SELECT * FROM F117_ET WHERE CD_ETP='" + cd_etp + "' AND ACTIVE=0 AND CD_ETP NOT IN (SELECT DISTINCT CD_ETP FROM F106_EI)"
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Exécuter la commande sql
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si l'étape de production est invalide
            if not resultat:
                #Retourner une exception
                raise Exception("L'étape de production n'existe pas ou est encore active : " + cd_etp)
            
            #Modifier l'étape de production
            arcpy.AddMessage("- Détruire l'information de l'étape de production ...")
            #Définir la commande SQL pour détruire l'étape
            sql = "DELETE F117_ET WHERE CD_ETP='" + cd_etp + "' AND ACTIVE=0"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Afficher l'information de l'étape
            arcpy.AddWarning(str(resultat[0]))
            #Exécuter la commande
            self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
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
        listeEtape  = ""

        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeEtape = sys.argv[2].replace(";'","").replace(";",",")
        
        #Définir l'objet pour détruire l'information d'une ou plusieurs étapes de production dans SIB qui sont inactives et non utilisées.
        oDetruireEtapeProduction = DetruireEtapeProduction()
        
        #Valider les paramètres obligatoires
        oDetruireEtapeProduction.validerParamObligatoire(env, listeEtape)
        
        #Exécuter le traitement pour détruire l'information d'une ou plusieurs étapes de production dans SIB qui sont inactives et non utilisées.
        oDetruireEtapeProduction.executer(env, listeEtape)
    
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