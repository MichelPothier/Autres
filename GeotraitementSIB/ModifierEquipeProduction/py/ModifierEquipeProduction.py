#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de modifier l'information d'une �quipe de production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    cd_equipe       OB      Code d'�quipe de production � modifier.
                            d�faut = 
    nom             OB      Nom en fran�ais du code d'�quipe de production.
                            d�faut = 
    nom_an          OB      Nom en anglais du code d'�quipe de production.
                            d�faut = 
    active          OB      Indique si l'�quipe de production est actif ou non [0:Non/1:Oui].
                            d�faut = 
    rep_eq          OP      R�pertoire de l'�quipe de production.
                            d�faut =
                            Attention : Vous devez entrer la valeur NULL pour forcer la valeur � NULL.
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'une �quipe de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification de l'information d'une �quipe de production.
        
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
        cd_equipe       : Code d'�quipe de production � modifier.
        nom             : Nom den fran�ais du code d'�quipe de production.
        nom_an          : Nom en anglais du code d'�quipe de production.
        active          : Indique si l'�quipe de production est actif ou non [0:Non/1:Oui].

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
        Ex�cuter le traitement de modification de l'information d'une �quipe de production.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Code d'�quipe de production � modifier.
        nom             : Nom den fran�ais du code d'�quipe de production.
        nom_an          : Nom en anglais du code d'�quipe de production.
        active          : Indique si l'�quipe de production est actif ou non [0:Non/1:Oui].
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
        
        #Valider si l'�quipe de production est absent
        arcpy.AddMessage("- Valider si l'�quipe de production est absent")
        resultat = self.Sib.requeteSib("SELECT cd_equipe,rep_eq FROM F108_EQ WHERE CD_EQUIPE='" + cd_equipe + "'")
        #V�rifier si l'�quipe de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("L'�quipe de production '" + cd_equipe + "' n'existe pas")
        
        #V�rifier si on doit modifier l'information de l'�quipe de production
        if nom <> "" or nom_an <> "" or active <> "" or rep_eq <> "":
            #Initialiser la commande SQL de modifification
            sql = "UPDATE F108_EQ SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,UPDT_FLD=P0G03_UTL.PU_HORODATEUR"
            
            #V�rifier la pr�sence du nom fran�ais
            if nom <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM='" + nom.replace("'","''") + "'"
            
            #V�rifier la pr�sence du nom anglais
            if nom_an <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM_AN='" + nom_an.replace("'","''") + "'"
            
            #V�rifier la pr�sence de l'�tat
            if active <> "":
                #V�rifier si l'�tat est valide
                if active <> "0" and active <> "1":
                    #Retourner une exception
                    raise Exception("�tat invalide : %s" %'active')
                #Ajouter la modification de l'�tat
                sql = sql + ",ACTIF=" + active
            
            #V�rifier la pr�sence du r�pertoire d'�quipe
            if rep_eq <> "":
                #V�rifier la pr�sence du r�pertoire d'�quipe
                if rep_eq <> "NULL":
                    #Ajouter la modification du r�pertoire de l'�quipe
                    sql = sql + ",REP_EQ='" + rep_eq + "'"
                #Si le r�pertoire d'�quipe est NULL
                else:
                    #Ajouter la modification du r�pertoire de l'�quipe
                    sql = sql + ",REP_EQ=NULL"
            #Si le r�pertoire d'�quipe sp�cifi� est NULL mais que la valeur dans la BD n'est pas NULL
            elif resultat[0][1] <> "":
                #Ajouter la modification du r�pertoire de l'�quipe
                sql = sql + ",REP_EQ=NULL"
            
            #Ajouter le WHERE CLAUSE pour traiter seulement l'�quipe de production
            sql = sql + " WHERE CD_EQUIPE='" + cd_equipe + "'"
            
            #Modifier l'�quipe de production
            arcpy.AddMessage("- Modifier l'information de l'�quipe de production")
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
                active = sys.argv[5].split(":")[0]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                rep_eq = sys.argv[6]
        
        #D�finir l'objet de modification de l'information d'une �quipe de production dans SIB.
        oModifierEquipeProduction = ModifierEquipeProduction()
        
        #Valider les param�tres obligatoires
        oModifierEquipeProduction.validerParamObligatoire(env, cd_equipe, nom, nom_an, active)
        
        #Ex�cuter le traitement de modification de l'information d'une �quipe de production dans SIB.
        oModifierEquipeProduction.executer(env, cd_equipe, nom, nom_an, active, rep_eq)
    
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