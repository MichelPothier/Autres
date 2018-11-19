#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEtapeProduction.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de modifier l'information d'une étape de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_etp          OB      Code d'étape de production à modifier.
                            défaut = 
    nom             OB      Nom en français du code d'étape de production.
                            défaut = 
    nom_an          OB      Nom en anglais du code d'étape de production.
                            défaut = 
    active          OB      Indique si l'étape de production est actif ou non [0:Non/1:Oui].
                            défaut = 1
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierEtapeProduction.py env cd_etp nom nom_an active

    Exemple:
        ModifierEtapeProduction.py SIB_PRO PREP 'Préparation' 'Preparation' 1

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEtapeProduction.py 2104 2016-08-22 17:39:11Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtapeProduction(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'une étape de production dans SIB.
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
    def validerParamObligatoire(self, env, cd_etp, nom, nom_an, active):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        cd_etp          : Code d'étape de production à modifier.
        nom             : Nom den français du code d'étape de production.
        nom_an          : Nom en anglais du code d'étape de production.
        active          : Indique si l'étape de production est actif ou non [0:Non/1:Oui].

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(cd_etp) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_etp')

        if (len(nom) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom_an')

        if active <> "0" and active <> "1":
            raise Exception("Paramètre obligatoire manquant: %s" %'active')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_etp, nom, nom_an, active):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de modification de l'information d'une étape de production.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        cd_etp          : Code d'étape de production à modifier.
        nom             : Nom den français du code d'étape de production.
        nom_an          : Nom en anglais du code d'étape de production.
        active          : Indique si l'étape de production est actif ou non [0:Non/1:Oui].
        
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
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Valider si l'étape de production est absent
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'étape de production est absent")
        sql = "SELECT CD_ETP FROM F117_ET WHERE CD_ETP='" + cd_etp + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'étape de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("L'étape de production '" + cd_etp + "' n'existe pas")
        
        #Vérifier si on doit modifier l'information de l'étape de production
        if nom <> "" or nom_an <> "" or active <> "":
            #Initialiser la commande SQL de modifification
            sql = "UPDATE F117_ET SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,UPDT_FLD=P0G03_UTL.PU_HORODATEUR"
            
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
                sql = sql + ",ACTIVE=" + active
            
            #Ajouter le WHERE CLAUSE pour traiter seulement l'étape de production
            sql = sql + " WHERE CD_ETP='" + cd_etp + "'"
            
            #Modifier l'étape de production
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Modifier l'information de l'étape de production")
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env         = "SIB_PRO"
        cd_etp      = ""
        nom         = ""
        nom_an      = ""
        active      = "1"

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_etp = sys.argv[2].upper().split(" ")[0]
        
        if len(sys.argv) > 3:
            nom = sys.argv[3]
        
        if len(sys.argv) > 4:
            nom_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                active = sys.argv[5].split(":")[0]
        
        #Définir l'objet de modification de l'information d'une étape de production dans SIB.
        oModifierEtapeProduction = ModifierEtapeProduction()
        
        #Valider les paramètres obligatoires
        oModifierEtapeProduction.validerParamObligatoire(env, cd_etp, nom, nom_an, active)
        
        #Exécuter le traitement de modification de l'information d'une étape de production dans SIB.
        oModifierEtapeProduction.executer(env, cd_etp, nom, nom_an, active)
    
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