#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireGroupeProduction.py
# Auteur    : Michel Pothier
# Date      : 05 février 2015

"""
    Application qui permet de détruire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env                 OB    Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    noLot               OB    Numéro du lot de production dont aucun groupe n'est au programme et dont les lots ont un groupe supérieur à 01.
                              défaut = ""
    listeNoGroupe       OB    Liste des numéros de groupes du lot de production à détruire.
                              Attention : Seuls les groupes supérieurs à 01 peuvent être détruits.
                              défaut = ""
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireGroupeProduction.py env noLot listeNoGroupe

    Exemple:
        DetruireGroupeProduction.py SIB_PRO 35444 02,03

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireGroupeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireGroupeProduction(object):
#*******************************************************************************************
    """
    Permet de détruire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        
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
    def validerParamObligatoire(self, env, noLot, listeNoGroupe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        noLot           : Numéro du lot de production.
        listeNoGroupe   : Liste des numéros de groupes du lot de production à détruire.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(noLot) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noLot')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, noLot, listeNoGroupe):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        noLot           : Numéro du lot de production.
        listeNoGroupe   : Liste des numéros de groupes du lot de production à détruire.
        
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
        
        #Valider si le lot de production est au programme
        arcpy.AddMessage("- Valider le numéro du lot de production")
        resultat = oSib.requeteSib("SELECT NO_LOT FROM F503_TR WHERE NO_LOT='" + noLot + "'")
        #Vérifier si le lot de production est présent
        if resultat:
            #Retourner une exception
            raise Exception("Le lot de production est au programme dans la table F503_TR : " + noLot)
        
        #Valider si les groupes du lot de production
        arcpy.AddMessage("- Valider les groupes du lot de production")
        #Vérifier si le groupe 01 est présent
        if "01" in listeNoGroupe:
            #Retourner une exception
            raise Exception("Le groupe 01 du lot de production ne peut être détruit")
        
        #Traiter tous les numéros de lot à détruire
        arcpy.AddMessage("- Destruction des groupes du lot de production qui ne sont pas au programme")
        for noGroupe in listeNoGroupe.split(","):
            #Valider si le groupe du lot de production est au programme
            resultat = oSib.requeteSib("SELECT DISTINCT NO_LOT,GROUPE FROM F503_TR WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'")
            #Vérifier si le groupe du lot de production est présent
            if resultat:
                #Retourner une exception
                raise Exception("Le groupe du lot de production est au programme dans la table F503_TR : " + noLot + "-" + noGroupe)
            
            #Détruire le groupe du lot de production
            arcpy.AddMessage(" ")
            sql = "SELECT * FROM F601_GR WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données du groupe du lot de production
                arcpy.AddMessage(str(resultat))
                #Détruire le lot de production
                sql = "DELETE F601_GR WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            #Si le groupe du lot de production est absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning("Groupe du lot de production absent")
        
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
        noLot            = ""
        listeNoGroupe    = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            noLot = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            listeNoGroupe = sys.argv[3].replace(";",",").replace("'","")
        
        #Définir l'objet pour détruire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        oDetruireGroupeProduction = DetruireGroupeProduction()
        
        #Valider les paramètres obligatoires
        oDetruireGroupeProduction.validerParamObligatoire(env, noLot, listeNoGroupe)
        
        #Exécuter le traitement pour détruire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        oDetruireGroupeProduction.executer(env, noLot, listeNoGroupe)
        
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