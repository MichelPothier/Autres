#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerEtapeProduction.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de cr�er une nouvelle �tape de production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    cd_etp          OB      Code d'�tape de production � cr�er.
                            d�faut = 
    nom             OB      Nom en fran�ais du code d'�tape de production.
                            d�faut = 
    nom_an          OB      Nom en anglais du code d'�tape de production.
                            d�faut = 
    active          OB      Indique si l'�tape de production est actif ou non [0:Non/1:Oui].
                            d�faut = 1
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        CreerEtapeProduction.py env cd_etp nom nom_an active

    Exemple:
        CreerEtapeProduction.py SIB_PRO PREP 'Pr�paration' 'Preparation' 1

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerEtapeProduction.py 2103 2016-08-22 17:38:36Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerEtapeProduction(object):
#*******************************************************************************************
    """
    Permet de cr�er une nouvelle �tape de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'une nouvelle �tape de production dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_etp, nom, nom_an, active):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        cd_etp          : Code d'�tape de production � cr�er.
        nom             : Nom den fran�ais du code d'�tape de production.
        nom_an          : Nom en anglais du code d'�tape de production.
        active          : Indique si l'�tape de production est actif ou non [0:Non/1:Oui].

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(cd_etp) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_etp')

        if (len(nom) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom_an')

        if active <> "0" and active <> "1":
            raise Exception("Param�tre obligatoire manquant: %s" %'active')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_etp, nom, nom_an, active):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'une nouvelle �tape de production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        cd_etp          : Code d'�tape de production � cr�er.
        nom             : Nom den fran�ais du code d'�tape de production.
        nom_an          : Nom en anglais du code d'�tape de production.
        active          : Indique si l'�tape de production est actif ou non [0:Non/1:Oui].
        
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
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Valider si l'�tape de production est d�j� pr�sent
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider l'�tape de production est d�j� pr�sent")
        sql = "SELECT CD_ETP FROM F117_ET WHERE CD_ETP='" + cd_etp + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'�tape de production est pr�sent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("L'�tape de production '" + cd_etp + "' est d�j� pr�sent")
        
        #Cr�er l'�tape de production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Cr�er l'�tape de production")
        sql = "INSERT INTO F117_ET VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + cd_etp + "','" + nom.replace("'", "''") + "','" + nom_an.replace("'", "''") + "'," + active + ")"
        arcpy.AddMessage(sql)
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        cd_etp      = ""
        nom         = ""
        nom_an      = ""
        active      = "1"

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_etp = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            nom = sys.argv[3]
        
        if len(sys.argv) > 4:
            nom_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                active = sys.argv[5].upper()
        
        #D�finir l'objet de cr�ation d'une nouvelle �tape de production dans SIB.
        oCreerEtapeProduction = CreerEtapeProduction()
        
        #Valider les param�tres obligatoires
        oCreerEtapeProduction.validerParamObligatoire(env, cd_etp, nom, nom_an, active)
        
        #Ex�cuter le traitement de cr�ation d'une nouvelle �tape de production dans SIB.
        oCreerEtapeProduction.executer(env, cd_etp, nom, nom_an, active)
    
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