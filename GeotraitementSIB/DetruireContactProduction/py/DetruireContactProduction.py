#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireContactProduction.py
# Auteur    : Michel Pothier
# Date      : 13 janvier 2015

"""
    Application qui permet de détruire un ou plusieurs contacts pour un exécutant de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_execu        OB      Code de l'exécutant de production du contact.
                            défaut = 
    no_contact      OB      Liste des numéros de contact de production à détruire.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireContactProduction.py env cd_execu no_contact

    Exemple:
        DetruireContactProduction.py SIB_PRO CIT 1386:Michel Pothier;1387:Jean Huot"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireContactProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireContactProduction(object):
#*******************************************************************************************
    """
    Permet de détruire un ou plusieurs contacts pour un exécutant de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification d'un contact pour un exécutant de production dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_execu, no_contact):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'exécutant de production.
        no_contact      : Liste des numéros de contact de production à détruire.

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

        if (len(no_contact) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'no_contact')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_execu, no_contact):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de modification d'un contact pour un exécutant de production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'exécutant de production.
        no_contact      : Liste des numéros de contact de production à détruire.
        
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
        
        #Valider si l'exécutant de production est absent
        arcpy.AddMessage("- Valider le code de l'exécutant de production")
        resultat = self.Sib.requeteSib("SELECT CD_EXECU, FIRME, NO_CONTACT FROM F604_EX WHERE CD_EXECU='" + cd_execu + "'")
        #Vérifier si l'exécutant de production est présent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le code de l'exécutant de production '" + cd_execu + "' est absent")
        #Afficher l'exécutant
        arcpy.AddWarning(str(resultat[0]))
        #Conserver le numéro du contact principal
        noContactPrincipal = str(resultat[0][2])
        
        #Traiter tous les contacts à détruire
        for contact in no_contact.split(","):
            #Détruire le contact
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Détruire le contact : " + contact)
            
            #Définir le numéro de contact
            noContact = contact.split(":")[0]
            
            #Vérifier si l'exécutant de production est présent
            if noContact == noContactPrincipal:
                #Retourner une exception
                raise Exception("Le numéro de contact de l'exécutant ne peut être détruit car il est le contact principal : '" + contact + "'")
            
            #Vérifier l'information du contact dans la table F607_CO
            sql = "SELECT * FROM F607_CO WHERE CD_EXECU='" + cd_execu + "' AND NO_CONTACT=" + noContact
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            
            #Vérifier si l'exécutant de production est présent
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception("Le numéro de contact de production '" + noContact + "' est absent pour l'exécutant '" + cd_execu + "'")

            #Afficher l'information du contact
            arcpy.AddWarning(resultat[0])
            
            #Détruire le contact dans la table F607_CO
            sql = "DELETE F607_CO WHERE CD_EXECU='" + cd_execu + "' AND NO_CONTACT=" + noContact
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
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
        no_contact  = ""

        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_execu = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            no_contact = sys.argv[3].replace("'","").replace(";",",")
        
        #Définir l'objet pour détruire un ou plusieurs contacts pour un exécutant de production dans SIB.
        oDetruireContactProduction = DetruireContactProduction()
        
        #Valider les paramètres obligatoires
        oDetruireContactProduction.validerParamObligatoire(env,cd_execu,no_contact)
        
        #Exécuter le traitement pour détruire un ou plusieurs contacts d'un contact pour un exécutant de production dans SIB.
        oDetruireContactProduction.executer(env,cd_execu,no_contact)
    
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