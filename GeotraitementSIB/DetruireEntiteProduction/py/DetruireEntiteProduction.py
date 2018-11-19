#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : DetruireEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 03 ao�t 2016

"""
    Application qui permet de d�truire l'information relative aux codes d'�l�ment topographique (entit� de production)
    non utilis�s pour toutes les normes de la BDG.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    listeCodeElem       OB      Liste des codes d'�l�ment topographique.
                                d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireEntiteProduction.py env codeElem

    Exemple:
        DetruireEntiteProduction.py SIB_PRO "1000000"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEntiteProduction.py 2086 2016-08-09 17:48:17Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de d�truire l'information relative aux codes d'�l�ment topographique
    (entit� de production) pour toutes les normes de la BDG.
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
    def validerParamObligatoire(self, env, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        codeElem            : Code de l'�l�ment topographique.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')
        
        if (len(listeCodeElem) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'listeCodeElem')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire l'information relative aux codes d'�l�ment topographique
        (entit� de production) pour toutes les normes de la BDG.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        listeCodeElem       : Liste des codes d'�l�ment topographique.
        
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
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #---------------------------------------------------------------------
        #Traiter tous les codes
        for code in listeCodeElem.split(","):
            #D�finir le code d'�l�ment topographique
            codeElem = code.replace("'","").split(" ")[0]
            
            #---------------------------------------------------------------------
            #Valider si le code d'�l�ment topographique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Valider le code d'�l�ment topographique ...")
            sql = "SELECT * FROM F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'AND CD_ELEM_TOPO NOT IN (SELECT DISTINCT CD_ELEM_TOPO FROM F132_EN)"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if not resultat:
                #Retourner une exception
                raise Exception(u"Le code de l'�l�ment topographique est absent ou encore utilis� : " + codeElem)
            
            #---------------------------------------------------------------------
            #D�truire l'information relative au code de l'�l�ment topographique
            arcpy.AddMessage("- D�truire l'information relative au code de l'�l�ment topographique ...")
            #D�finir la commande pour d�truire le code d'�l�ment topographique
            sql = "DELETE F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Afficher l'information d�truite
            arcpy.AddWarning(str(resultat))
            #Ex�cuter la commande
            self.Sib.execute(sql)
        
        #---------------------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB   
        
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
        listeCodeElem       = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeCodeElem = sys.argv[2].replace(";",",")
        
        #D�finir l'objet pour d�truire l'information relative aux codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG.
        oDetruireEntiteProduction = DetruireEntiteProduction()
        
        #Valider les param�tres obligatoires
        oDetruireEntiteProduction.validerParamObligatoire(env, listeCodeElem)
        
        #Ex�cuter le traitement pour d�truire l'information relative aux codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG.
        oDetruireEntiteProduction.executer(env, listeCodeElem)
    
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