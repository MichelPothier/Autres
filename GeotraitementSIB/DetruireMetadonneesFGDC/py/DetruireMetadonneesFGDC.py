#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireMetadonneesFGDC.py
# Auteur    : Michel Pothier
# Date      : 19 octobre 2017

"""
    Application qui permet de d�truire les m�tadonn�es FGDC d'un identifiant de produit dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                                d�faut = SIB_PRO
    typeProduit         OB      Type de produit de l'identifiant.
                                d�faut = "BDG"
    identifiant         OB      Identifiant avec ou sans �dition.version courante du produit � traiter.
                                d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireMetadonneesFGDC.py env typeProduit identifiant

    Exemple:
        DetruireMetadonneesFGDC.py SIB_PRO BDG 021M07
        DetruireMetadonneesFGDC.py SIB_PRO BDG "021M07 12.0"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireMetadonneesFGDC.py 2149 2017-10-19 17:44:30Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireMetadonneesFGDC(object):
#*******************************************************************************************
    """
    Permet de d�truire les m�tadonn�es FGDC d'un identifiant de produit dans SIB.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de destruction de m�tadonn�es FGDC.
        
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
    def validerParamObligatoire(self, env, typeProduit, identifiant):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit d'un identifiant.
        identifiant         : Identifiant avec ou sans �dition.version courante du produit � traiter.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """
        
        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'typeProduit')
        
        if (len(identifiant) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'identifiant')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, identifiant):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de destruction des m�tadonn�es FGDC d'un identifiant de produit dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        typeProduit     : Type de produit d'un identifiant.
        identifiant     : Identifiant avec ou sans �dition.version courante du produit � traiter.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur g�n�r�s par le service de transaction SIB.
        messageSib      : Description du message re�ue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucune
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")  
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS','PLAN'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')"
        resultat = oSib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        #Valider le num�ro d'�dition et version de l'identifiant courant
        arcpy.AddMessage("- Valider le num�ro courant d'�dition et version de l'identifiant '" + identifiant + "' du produit '" + typeProduit + "'")
        #Extraire l'identifiant
        id = identifiant.split(" ")[0]
        #Ex�cuter la requ�te dans SIB
        sql = "SELECT ED, VER FROM F235_PR WHERE TY_PRODUIT='" + typeProduit + "' AND IDENTIFIANT='" + id + "' AND JEU_COUR=1"
        resultat = oSib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            arcpy.AddMessage(sql)
            raise Exception("L'identifiant '" + id + "' du produit '" + typeProduit + "' de SIB est invalide ou ne poss�de pas de jeu courant!")

        #D�finir le num�ro d'�dition et version du jeu de donn�es courant
        ed = resultat[0][0]
        ver = resultat[0][1]
        
        #Appel du service de transaction SIB qui annule la mise en place FGDC dans SIB.
        arcpy.AddMessage("- Appel du service SIB : P0201_AMP.pu_annuler_mise_en_place_fgdc (" + sUsagerSib + ", " + typeProduit + ", " + id + ", " + str(ed) + ", " + str(ver) + ")")
        codeRetour = oSib.cursor.callfunc("P0201_AMP.pu_annuler_mise_en_place_fgdc", cx_Oracle.STRING, [sUsagerSib, typeProduit, id, ed, ver])
        
        #V�rifier le succ�s du service SIB 
        if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
            #Afficher le message de succ�s du traitraitement
            arcpy.AddMessage("- Succ�s d'ex�cution du service SIB : P0201_AMP.pu_annuler_mise_en_place_fgdc")
        
        #l'initialisation de l'ajout d'un lot n'a pas r�ussi
        else:
            #Extraire le nombre de message
            nbMessSib = oSib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
            count = 1
            #Extraire tous les messages
            message = []
            while nbMessSib >= count:
                messageSib = oSib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                message.append(messageSib)
                count += 1
            raise Exception(message)
         
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
        typeProduit      = "BDG"
        identifiant      = ""
        
        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            identifiant = sys.argv[3].upper()
        
        # D�finir l'objet de destruction des m�tadonn�es FGDC.
        oDetruireMetadonneesFGDC = DetruireMetadonneesFGDC()
        
        #Valider les param�tres obligatoires
        oDetruireMetadonneesFGDC.validerParamObligatoire(env, typeProduit, identifiant)
        
        # Ex�cuter le traitement de destruction des m�tadonn�es FGDC.
        oDetruireMetadonneesFGDC.executer(env, typeProduit, identifiant)
    
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