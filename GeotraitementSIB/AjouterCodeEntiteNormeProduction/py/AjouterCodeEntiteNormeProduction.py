#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : AjouterCodeEntiteNormeProduction.py
# Auteur    : Michel Pothier
# Date      : 17 ao�t 2016

"""
    Application qui permet d'ajouter des codes d'�l�ment topographique pour un num�ro de normes de la BDG.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    normes              OB      Normes de la BDG.
                                d�faut = 4.2.2
    altimetrie          OB      Indique si les codes d'�l�ment topographique poss�dent de l'information altim�trique.
                                d�faut = 0:Non
    patrimoine          OB      Indique si les codes d'�l�ment topographique font partie du patrimoine.
                                d�faut = 0:Non
    listeCodeElem       OB      Liste des codes de l'�l�ment topographique.
                                d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        AjouterCodeEntiteNormeProduction.py env normes altimetrie patrimoine listeCodeElem

    Exemple:
        AjouterCodeEntiteNormeProduction.py SIB_PRO 4.2.2 0 0 "1000000;10000001"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AjouterCodeEntiteNormeProduction.py 2100 2016-08-22 14:29:07Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class AjouterCodeEntiteNormeProduction:
#*******************************************************************************************
    """
    Classe qui permet d'ajouter des codes d'�l�ment topographique pour un num�ro de normes de la BDG.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de mise au programme.
        
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
    def validerParamObligatoire(self, env, normes, altimetrie, patrimoine, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        normes              : Normes de la BDG.
        altimetrie          : Indique si les codes d'�l�ment topographique poss�dent de l'information altim�trique.
        patrimoine          : Indique si les codes d'�l�ment topographique font partie du patrimoine.
        listeCodeElem       : Liste des codes de l'�l�ment topographique.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')
        
        if (len(normes) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'normes')
        
        if (len(altimetrie) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'altimetrie')
        
        if (len(patrimoine) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'patrimoine')
        
        if (len(listeCodeElem) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'listeCodeElem')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, normes, altimetrie, patrimoine, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour ajouter des codes d'�l�ment topographique pour un num�ro de normes de la BDG.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        normes              : Normes de la BDG.
        altimetrie          : Indique si les codes d'�l�ment topographique poss�dent de l'information altim�trique.
        patrimoine          : Indique si les codes d'�l�ment topographique font partie du patrimoine.
        listeCodeElem       : Liste des codes de l'�l�ment topographique.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #---------------------------------------------------------------------
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        #D�finir la commande SQL
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        #Afficher la commande SQL
        arcpy.AddMessage(sql)
        #Ex�cuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #---------------------------------------------------------------------
        #Extraire les codes d'�l�ments topographiques existants
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire les codes d'�l�ments topographiques existants ...")
        #Extraire les codes d'�l�ments topographiques existants
        sql = "SELECT CD_ELEM_TOPO FROM F132_EN WHERE NORMES='" + normes + "'"
        #Afficher la commande sql
        arcpy.AddMessage(sql)
        #Ex�cuter la commande sql
        resultat = self.Sib.requeteSib(sql)
        #Initialiser la liste
        listeCodeExistant =[]
        #Traiter tous les codes
        for code in resultat:
            #Ajouter le code � la liste
            listeCodeExistant.append(code[0])
        
        #Traiter tous les codes d'�l�ment topographique
        for codeDesc in listeCodeElem.split(","):
            #D�finir le code d'�l�ment sans description
            codeElem = codeDesc.split(" ")[0]
            
            #---------------------------------------------------------------------
            #Ajouter l'information relative au code d'�l�ment topographique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Ajouter l'information relative au code d'�l�ment topographique : " + codeElem)
        
            #---------------------------------------------------------------------
            #Valider le code d'�l�ment topographique
            sql = "SELECT CD_ELEM_TOPO FROM F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'"
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if not resultat:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception(u"Le code de l'�l�ment topographique est invalide : " + codeElem)
            
            #---------------------------------------------------------------------
            #V�rifier si le code est existant
            if codeElem not in listeCodeExistant:
                #D�finir la commande pour AJOUTER le code d'�l�ment topographique
                sql = "INSERT INTO F132_EN VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, '" + codeElem + "', '" + normes + "', " + altimetrie + ", " + patrimoine + ")"
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
            #Si le code est inexistant
            else:
                #Afficher le message
                arcpy.AddWarning("ATTENTION : Le code d'�l�ment topographique est d�j� pr�sent : " + codeDesc)
        
        #---------------------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        #Fermer la connexion SIB
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
        env                 = "SIB_PRO"
        normes              = "4.0.2"
        altimetrie          = "0:Non"
        patrimoine          = "0:Non"
        listeCodeElem       = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            normes = sys.argv[2]
        
        if len(sys.argv) > 3:
            altimetrie = sys.argv[3].split(":")[0]
        
        if len(sys.argv) > 4:
            patrimoine = sys.argv[4].split(":")[0]
         
        if len(sys.argv) > 5:
            listeCodeElem = sys.argv[5].replace("'","").replace(";",",")
        
        #D�finir l'objet pour ajouter des codes d'�l�ment topographique pour un num�ro de normes de la BDG.
        oAjouterCodeEntiteNormeProduction = AjouterCodeEntiteNormeProduction()
        
        #Valider les param�tres obligatoires
        oAjouterCodeEntiteNormeProduction.validerParamObligatoire(env, normes, altimetrie, patrimoine, listeCodeElem)
        
        #Ex�cuter le traitement pour ajouter des codes d'�l�ment topographique pour un num�ro de normes de la BDG.
        oAjouterCodeEntiteNormeProduction.executer(env, normes, altimetrie, patrimoine, listeCodeElem)
    
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