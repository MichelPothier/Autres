#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de modifier l'information d'une équipe de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_equipe       OB      Code d'équipe de production à modifier.
                            défaut = 
    nom             OB      Nom en français du code d'équipe de production.
                            défaut = 
    nom_an          OB      Nom en anglais du code d'équipe de production.
                            défaut = 
    active          OB      Indique si l'équipe de production est actif ou non [0:Non/1:Oui].
                            défaut = 
    rep_eq          OP      Répertoire de l'équipe de production.
                            défaut =
                            Attention : Vous devez entrer la valeur NULL pour forcer la valeur à NULL.
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierEquipeProduction.py env cd_equipe nom nom_an active rep_eq

    Exemple:
        ModifierEquipeProduction.py SIB_PRO CORR 'Correction' 'Correction' 1 'production'

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEquipeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'une équipe de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification de l'information d'une équipe de production.
        
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
        cd_equipe       : Code d'équipe de production à modifier.
        nom             : Nom den français du code d'équipe de production.
        nom_an          : Nom en anglais du code d'équipe de production.
        active          : Indique si l'équipe de production est actif ou non [0:Non/1:Oui].

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
        Exécuter le traitement de modification de l'information d'une équipe de production.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Code d'équipe de production à modifier.
        nom             : Nom den français du code d'équipe de production.
        nom_an          : Nom en anglais du code d'équipe de production.
        active          : Indique si l'équipe de production est actif ou non [0:Non/1:Oui].
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
        
        #Valider si l'équipe de production est absent
        arcpy.AddMessage("- Valider si l'équipe de production est absent")
        resultat = self.Sib.requeteSib("SELECT cd_equipe,rep_eq FROM F108_EQ WHERE CD_EQUIPE='" + cd_equipe + "'")
        #Vérifier si l'équipe de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("L'équipe de production '" + cd_equipe + "' n'existe pas")
        
        #Vérifier si on doit modifier l'information de l'équipe de production
        if nom <> "" or nom_an <> "" or active <> "" or rep_eq <> "":
            #Initialiser la commande SQL de modifification
            sql = "UPDATE F108_EQ SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,UPDT_FLD=P0G03_UTL.PU_HORODATEUR"
            
            #Vérifier la présence du nom français
            if nom <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM='" + nom.replace("'","''") + "'"
            
            #Vérifier la présence du nom anglais
            if nom_an <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM_AN='" + nom_an.replace("'","''") + "'"
            
            #Vérifier la présence de l'état
            if active <> "":
                #Vérifier si l'état est valide
                if active <> "0" and active <> "1":
                    #Retourner une exception
                    raise Exception("État invalide : %s" %'active')
                #Ajouter la modification de l'état
                sql = sql + ",ACTIF=" + active
            
            #Vérifier la présence du répertoire d'équipe
            if rep_eq <> "":
                #Vérifier la présence du répertoire d'équipe
                if rep_eq <> "NULL":
                    #Ajouter la modification du répertoire de l'équipe
                    sql = sql + ",REP_EQ='" + rep_eq + "'"
                #Si le répertoire d'équipe est NULL
                else:
                    #Ajouter la modification du répertoire de l'équipe
                    sql = sql + ",REP_EQ=NULL"
            #Si le répertoire d'équipe spécifié est NULL mais que la valeur dans la BD n'est pas NULL
            elif resultat[0][1] <> "":
                #Ajouter la modification du répertoire de l'équipe
                sql = sql + ",REP_EQ=NULL"
            
            #Ajouter le WHERE CLAUSE pour traiter seulement l'équipe de production
            sql = sql + " WHERE CD_EQUIPE='" + cd_equipe + "'"
            
            #Modifier l'équipe de production
            arcpy.AddMessage("- Modifier l'information de l'équipe de production")
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
                active = sys.argv[5].split(":")[0]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                rep_eq = sys.argv[6]
        
        #Définir l'objet de modification de l'information d'une équipe de production dans SIB.
        oModifierEquipeProduction = ModifierEquipeProduction()
        
        #Valider les paramètres obligatoires
        oModifierEquipeProduction.validerParamObligatoire(env, cd_equipe, nom, nom_an, active)
        
        #Exécuter le traitement de modification de l'information d'une équipe de production dans SIB.
        oModifierEquipeProduction.executer(env, cd_equipe, nom, nom_an, active, rep_eq)
    
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