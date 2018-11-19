#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 17 novembre 2014

"""
    Application qui permet de créer une nouvelle équipe de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_equipe       OB      Code d'équipe de production à créer.
                            défaut = 
    nom             OB      Nom en français du code d'équipe de production.
                            défaut = 
    nom_an          OB      Nom en anglais du code d'équipe de production.
                            défaut =
    active          OB      Indique si l'équipe de production est active ou non [0:Non/1:Oui].
                            défaut = 1
    rep_eq          OP      Répertoire de l'équipe de production.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de créer une nouvelle équipe de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'une nouvelle équipe de production dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_equipe, nom, nom_an, active):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Code d'équipe de production à créer.
        nom             : Nom den français du code d'équipe de production.
        nom_an          : Nom en anglais du code d'équipe de production.
        active          : Indique si l'équipe de production est active ou non [0:Non/1:Oui].

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(cd_equipe) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_equipe')

        if (len(nom) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom_an')

        if active <> "0" and active <> "1":
            raise Exception("Paramètre obligatoire manquant: %s" %'active')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_equipe, nom, nom_an, active, rep_eq):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'une nouvelle équipe de production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Code d'équipe de production à créer.
        nom             : Nom den français du code d'équipe de production.
        nom_an          : Nom en anglais du code d'équipe de production.
        active          : Indique si l'équipe de production est active ou non [0:Non/1:Oui].
        rep_eq          : Répertoire de l'équipe de production.
        
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
        
        #Valider si l'équipe de production est déjà présent
        arcpy.AddMessage("- Valider l'équipe de production est déjà présent")
        resultat = self.Sib.requeteSib("SELECT cd_equipe FROM F108_EQ WHERE cd_equipe='" + cd_equipe + "'")
        #Vérifier si l'équipe de production est présent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("L'équipe de production '" + cd_equipe + "' est déjà présent")
        
        #Vérifier si le répertoire d'équipe est vide
        if rep_eq == "":
            #La valeur doit être NULL
            rep_eq = "NULL"
        #Si le répertoire d'équipe n'est pas vide
        else:
            #On doit insérer les apostrophes dans le répertoire
            rep_eq = "'" + rep_eq + "'"
        
        #Créer l'équipe de production
        arcpy.AddMessage("- Créer l'équipe de production")
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env         = "SIB_PRO"
        cd_equipe   = ""
        nom         = ""
        nom_an      = ""
        active      = "1"
        rep_eq      = ""

        #extraction des paramètres d'exécution
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
        
        #Définir l'objet de création d'une nouvelle équipe de production dans SIB.
        oCreerEquipeProduction = CreerEquipeProduction()
        
        #Valider les paramètres obligatoires
        oCreerEquipeProduction.validerParamObligatoire(env, cd_equipe, nom, nom_an, active)
        
        #Exécuter le traitement de création d'une nouvelle équipe de production dans SIB.
        oCreerEquipeProduction.executer(env, cd_equipe, nom, nom_an, active, rep_eq)
    
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