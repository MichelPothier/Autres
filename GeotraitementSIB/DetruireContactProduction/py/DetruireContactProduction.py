#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireContactProduction.py
# Auteur    : Michel Pothier
# Date      : 13 janvier 2015

"""
    Application qui permet de d�truire un ou plusieurs contacts pour un ex�cutant de production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    cd_execu        OB      Code de l'ex�cutant de production du contact.
                            d�faut = 
    no_contact      OB      Liste des num�ros de contact de production � d�truire.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireContactProduction(object):
#*******************************************************************************************
    """
    Permet de d�truire un ou plusieurs contacts pour un ex�cutant de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification d'un contact pour un ex�cutant de production dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_execu, no_contact):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'ex�cutant de production.
        no_contact      : Liste des num�ros de contact de production � d�truire.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(cd_execu) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_execu')

        if (len(no_contact) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'no_contact')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_execu, no_contact):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de modification d'un contact pour un ex�cutant de production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'ex�cutant de production.
        no_contact      : Liste des num�ros de contact de production � d�truire.
        
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
        
        #Valider si l'ex�cutant de production est absent
        arcpy.AddMessage("- Valider le code de l'ex�cutant de production")
        resultat = self.Sib.requeteSib("SELECT CD_EXECU, FIRME, NO_CONTACT FROM F604_EX WHERE CD_EXECU='" + cd_execu + "'")
        #V�rifier si l'ex�cutant de production est pr�sent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le code de l'ex�cutant de production '" + cd_execu + "' est absent")
        #Afficher l'ex�cutant
        arcpy.AddWarning(str(resultat[0]))
        #Conserver le num�ro du contact principal
        noContactPrincipal = str(resultat[0][2])
        
        #Traiter tous les contacts � d�truire
        for contact in no_contact.split(","):
            #D�truire le contact
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- D�truire le contact : " + contact)
            
            #D�finir le num�ro de contact
            noContact = contact.split(":")[0]
            
            #V�rifier si l'ex�cutant de production est pr�sent
            if noContact == noContactPrincipal:
                #Retourner une exception
                raise Exception("Le num�ro de contact de l'ex�cutant ne peut �tre d�truit car il est le contact principal : '" + contact + "'")
            
            #V�rifier l'information du contact dans la table F607_CO
            sql = "SELECT * FROM F607_CO WHERE CD_EXECU='" + cd_execu + "' AND NO_CONTACT=" + noContact
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            
            #V�rifier si l'ex�cutant de production est pr�sent
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception("Le num�ro de contact de production '" + noContact + "' est absent pour l'ex�cutant '" + cd_execu + "'")

            #Afficher l'information du contact
            arcpy.AddWarning(resultat[0])
            
            #D�truire le contact dans la table F607_CO
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        cd_execu    = ""
        no_contact  = ""

        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_execu = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            no_contact = sys.argv[3].replace("'","").replace(";",",")
        
        #D�finir l'objet pour d�truire un ou plusieurs contacts pour un ex�cutant de production dans SIB.
        oDetruireContactProduction = DetruireContactProduction()
        
        #Valider les param�tres obligatoires
        oDetruireContactProduction.validerParamObligatoire(env,cd_execu,no_contact)
        
        #Ex�cuter le traitement pour d�truire un ou plusieurs contacts d'un contact pour un ex�cutant de production dans SIB.
        oDetruireContactProduction.executer(env,cd_execu,no_contact)
    
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