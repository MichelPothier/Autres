#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireLotProduction.py
# Auteur    : Michel Pothier
# Date      : 05 février 2015

"""
    Application qui permet de détruire un ou plusieurs lot de production qui ne sont pas mis au programme dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    listeNoLot         OB     Liste des numéros du lot de production à détruire.
                              défaut = ""
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireLotProduction.py env listeNoLot

    Exemple:
        DetruireLotProduction.py SIB_PRO 35444,36445

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireLotProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireLotProduction(object):
#*******************************************************************************************
    """
    Permet de détruire un ou plusieurs lot de production qui ne sont pas mis au programme dans SIB.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire un ou plusieurs lot de production qui ne sont pas mis au programme dans SIB.
        
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
    def validerParamObligatoire(self, env, listeNoLot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        listeNoLot      : Liste des numéros du lot de production à détruire.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(listeNoLot) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'listeNoLot')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNoLot):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs lot de production qui ne sont pas mis au programme dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        listeNoLot      : Liste des numéros du lot de production à détruire.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #Vérifier si l'usager SIB possède les privilège de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'PLAN' ou 'G-SYS'")
        
        #Traiter tous les numéros de lot à détruire
        arcpy.AddMessage("- Destruction des lots de production qui ne sont pas au programme")
        for noLot in listeNoLot.split(","):
            #Valider si le lot de production est au programme
            noLot = noLot.split(":")[0]
            resultat = oSib.requeteSib("SELECT DISTINCT NO_LOT FROM F503_TR WHERE NO_LOT='" + noLot + "'")
            #Vérifier si le lot de production est présent
            if resultat:
                #Retourner une exception
                raise Exception("Le lot de production est au programme dans la table F503_TR : " + noLot)
            
            #Détruire le lot de production
            arcpy.AddMessage(" ")
            sql = "SELECT * FROM F601_LO WHERE NO_LOT='" + noLot + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données du lot de production
                arcpy.AddMessage(str(resultat))
                #Détruire le lot de production
                sql = "DELETE F601_LO WHERE NO_LOT='" + noLot + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            #Si le lot de production absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning("Lot de production absent")
            
            #Détruire les groupes du lot de production
            sql = "SELECT * FROM F601_GR WHERE NO_LOT='" + noLot + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données des groupes du lot de production
                for groupe in resultat:
                    arcpy.AddMessage(str(groupe))
                #Détruire le lot de production
                sql = "DELETE F601_GR WHERE NO_LOT='" + noLot + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            #Si les groupes du lot de production sont absents
            else:
                #Afficher un message d'absence
                arcpy.AddWarning("Groupes du lot de production absents")
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env              = "SIB_PRO"
        listeNoLot       = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeNoLot = sys.argv[2].replace(";",",").replace("'","")
        
        #Définir l'objet pour détruire un ou plusieurs lot de production qui ne sont pas mis au programme dans SIB.
        oDetruireLotProduction = DetruireLotProduction()
        
        #Valider les paramètres obligatoires
        oDetruireLotProduction.validerParamObligatoire(env, listeNoLot)
        
        #Exécuter le traitement pour détruire un ou plusieurs lot de production qui ne sont pas mis au programme dans SIB.
        oDetruireLotProduction.executer(env, listeNoLot)
        
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