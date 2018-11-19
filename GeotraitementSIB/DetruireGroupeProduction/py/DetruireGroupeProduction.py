#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireGroupeProduction.py
# Auteur    : Michel Pothier
# Date      : 05 f�vrier 2015

"""
    Application qui permet de d�truire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB    Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              d�faut = SIB_PRO
    noLot               OB    Num�ro du lot de production dont aucun groupe n'est au programme et dont les lots ont un groupe sup�rieur � 01.
                              d�faut = ""
    listeNoGroupe       OB    Liste des num�ros de groupes du lot de production � d�truire.
                              Attention : Seuls les groupes sup�rieurs � 01 peuvent �tre d�truits.
                              d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireGroupeProduction(object):
#*******************************************************************************************
    """
    Permet de d�truire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        
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
    def validerParamObligatoire(self, env, noLot, listeNoGroupe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement.    
        noLot           : Num�ro du lot de production.
        listeNoGroupe   : Liste des num�ros de groupes du lot de production � d�truire.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')
        
        if (len(noLot) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'noLot')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, noLot, listeNoGroupe):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        noLot           : Num�ro du lot de production.
        listeNoGroupe   : Liste des num�ros de groupes du lot de production � d�truire.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'PLAN' ou 'G-SYS'")
        
        #Valider si le lot de production est au programme
        arcpy.AddMessage("- Valider le num�ro du lot de production")
        resultat = oSib.requeteSib("SELECT NO_LOT FROM F503_TR WHERE NO_LOT='" + noLot + "'")
        #V�rifier si le lot de production est pr�sent
        if resultat:
            #Retourner une exception
            raise Exception("Le lot de production est au programme dans la table F503_TR : " + noLot)
        
        #Valider si les groupes du lot de production
        arcpy.AddMessage("- Valider les groupes du lot de production")
        #V�rifier si le groupe 01 est pr�sent
        if "01" in listeNoGroupe:
            #Retourner une exception
            raise Exception("Le groupe 01 du lot de production ne peut �tre d�truit")
        
        #Traiter tous les num�ros de lot � d�truire
        arcpy.AddMessage("- Destruction des groupes du lot de production qui ne sont pas au programme")
        for noGroupe in listeNoGroupe.split(","):
            #Valider si le groupe du lot de production est au programme
            resultat = oSib.requeteSib("SELECT DISTINCT NO_LOT,GROUPE FROM F503_TR WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'")
            #V�rifier si le groupe du lot de production est pr�sent
            if resultat:
                #Retourner une exception
                raise Exception("Le groupe du lot de production est au programme dans la table F503_TR : " + noLot + "-" + noGroupe)
            
            #D�truire le groupe du lot de production
            arcpy.AddMessage(" ")
            sql = "SELECT * FROM F601_GR WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Afficher les donn�es du groupe du lot de production
                arcpy.AddMessage(str(resultat))
                #D�truire le lot de production
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env              = "SIB_PRO"
        noLot            = ""
        listeNoGroupe    = ""
        
        #extraction des param�tres d'ex�cution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            noLot = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            listeNoGroupe = sys.argv[3].replace(";",",").replace("'","")
        
        #D�finir l'objet pour d�truire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        oDetruireGroupeProduction = DetruireGroupeProduction()
        
        #Valider les param�tres obligatoires
        oDetruireGroupeProduction.validerParamObligatoire(env, noLot, listeNoGroupe)
        
        #Ex�cuter le traitement pour d�truire un ou plusieurs groupes d'un lot de production qui ne sont pas mis au programme dans SIB.
        oDetruireGroupeProduction.executer(env, noLot, listeNoGroupe)
        
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