#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 17 novembre 2014

"""
    Application qui permet de cr�er une nouvelle �quipe de production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    cd_equipe       OB      Code d'�quipe de production � cr�er.
                            d�faut = 
    nom             OB      Nom en fran�ais du code d'�quipe de production.
                            d�faut = 
    nom_an          OB      Nom en anglais du code d'�quipe de production.
                            d�faut =
    active          OB      Indique si l'�quipe de production est active ou non [0:Non/1:Oui].
                            d�faut = 1
    rep_eq          OP      R�pertoire de l'�quipe de production.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        CreerEquipeProduction.py env cd_equipe nom nom_an active rep_eq

    Exemple:
        CreerEquipeProduction.py SIB_PRO CORR 'Correction' 'Correction' 1 'production'

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerEquipeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de cr�er une nouvelle �quipe de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'une nouvelle �quipe de production dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_equipe, nom, nom_an, active):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Code d'�quipe de production � cr�er.
        nom             : Nom den fran�ais du code d'�quipe de production.
        nom_an          : Nom en anglais du code d'�quipe de production.
        active          : Indique si l'�quipe de production est active ou non [0:Non/1:Oui].

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(cd_equipe) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_equipe')

        if (len(nom) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom_an')

        if active <> "0" and active <> "1":
            raise Exception("Param�tre obligatoire manquant: %s" %'active')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_equipe, nom, nom_an, active, rep_eq):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'une nouvelle �quipe de production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Code d'�quipe de production � cr�er.
        nom             : Nom den fran�ais du code d'�quipe de production.
        nom_an          : Nom en anglais du code d'�quipe de production.
        active          : Indique si l'�quipe de production est active ou non [0:Non/1:Oui].
        rep_eq          : R�pertoire de l'�quipe de production.
        
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
        
        #Valider si l'�quipe de production est d�j� pr�sent
        arcpy.AddMessage("- Valider l'�quipe de production est d�j� pr�sent")
        resultat = self.Sib.requeteSib("SELECT cd_equipe FROM F108_EQ WHERE cd_equipe='" + cd_equipe + "'")
        #V�rifier si l'�quipe de production est pr�sent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("L'�quipe de production '" + cd_equipe + "' est d�j� pr�sent")
        
        #V�rifier si le r�pertoire d'�quipe est vide
        if rep_eq == "":
            #La valeur doit �tre NULL
            rep_eq = "NULL"
        #Si le r�pertoire d'�quipe n'est pas vide
        else:
            #On doit ins�rer les apostrophes dans le r�pertoire
            rep_eq = "'" + rep_eq + "'"
        
        #Cr�er l'�quipe de production
        arcpy.AddMessage("- Cr�er l'�quipe de production")
        sql = "INSERT INTO F108_EQ VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + cd_equipe + "','" + nom.replace("'", "''") + "',P0G03_UTL.PU_HORODATEUR," + active + "," + rep_eq + ",'" + nom_an.replace("'", "''") + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        cd_equipe   = ""
        nom         = ""
        nom_an      = ""
        active      = "1"
        rep_eq      = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_equipe = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            nom = sys.argv[3]
        
        if len(sys.argv) > 4:
            nom_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                active = sys.argv[5].split(':')[0]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                rep_eq = sys.argv[6]
        
        #D�finir l'objet de cr�ation d'une nouvelle �quipe de production dans SIB.
        oCreerEquipeProduction = CreerEquipeProduction()
        
        #Valider les param�tres obligatoires
        oCreerEquipeProduction.validerParamObligatoire(env, cd_equipe, nom, nom_an, active)
        
        #Ex�cuter le traitement de cr�ation d'une nouvelle �quipe de production dans SIB.
        oCreerEquipeProduction.executer(env, cd_equipe, nom, nom_an, active, rep_eq)
    
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