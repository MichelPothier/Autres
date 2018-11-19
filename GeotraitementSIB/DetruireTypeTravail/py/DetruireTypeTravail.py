#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 25 ao�t 2015

"""
    Application qui permet de d�truire un ou plusieurs type de travail qui n'ont jamais �t� utilis�s en production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    ty_travail      OB      Type de travail � modifier.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireTypeTravail.py env ty_travail

    Exemple:
        DetruireTypeTravail.py SIB_PRO PREP

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireTypeTravail.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireTypeTravail(object):
#*******************************************************************************************
    """
    Permet de d�truire un ou plusieurs type de travail qui n'ont jamais �t� utilis�s en production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire un ou plusieurs type de travail qui n'ont jamais �t� utilis�s en production dans SIB.
        
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
    def validerParamObligatoire(self, env, ty_travail):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail � modifier.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(ty_travail) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'ty_travail')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire un ou plusieurs type de travail qui n'ont jamais �t� utilis�s en production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail � modifier.
        
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
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #D�truire les types de travail
        arcpy.AddMessage("- D�truire les types de travail")
        #Traiter la liste des types de travail
        for travail in ty_travail.split(','):
            #Extraire le type de travail � d�truire
            ty_trav = travail.split(":")[0]
            #D�truire le travail
            arcpy.AddMessage("- D�truire le type de travail : " + ty_trav)
            
            #Valider si le type de travail est d�j� pr�sent
            arcpy.AddMessage("- Valider le type de travail")
            sql = "SELECT TY_TRAV FROM F104_TT WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si le type de travail est pr�sent
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception("Le type de travail '" + ty_travail + "' n'existe pas")
            
            #Valider si le type de travail a d�j� �t� trait� en production
            arcpy.AddMessage("- Valider si le type de travail a d�j� �t� trait� en production")
            sql = "SELECT TY_TRAV FROM F104_TT WHERE TY_TRAV NOT IN (SELECT TY_TRAV FROM F503_TR)"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si le type de travail a d�j� �t� trait� en production
            if (ty_trav,) not in resultat:
                #Retourner une exception
                raise Exception("Le type de travail '" + ty_travail + "' a d�j� �t� trait� en production et ne peut �tre d�truit")
            
            #V�rifier le type de travail dans la table F105_ET associ� � un type de produit
            arcpy.AddMessage("- V�rifier le type de travail est associ� � un type de produit")
            sql = "SELECT * FROM F105_ET WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les items du r�sultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #D�truire le type de travail dans la table F105_ET associ� � un type de produit
                sql = "DELETE F105_ET WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donn�e pr�sente")                
            
            #V�rifier le type de travail dans la table F106_EI �tape et associ� � un type de produit
            arcpy.AddMessage("- V�rifier le type de travail est associ� � une �tape et � un type de produit")
            sql = "SELECT * FROM F106_EI WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les items du r�sultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #D�truire le type de travail dans la table F106_EI �tape et associ� � un type de produit
                sql = "DELETE F106_EI WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donn�e pr�sente")                
            
            #V�rifier le type de travail dans la table F116_MI associ� � un mod�le
            arcpy.AddMessage("- V�rifier le type de travail est associ� � un mod�le")
            sql = "SELECT * FROM F116_MI WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les items du r�sultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #D�truire le type de travail dans la table F116_MI associ� � un mod�le
                sql = "DELETE F116_MI WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donn�e pr�sente")                
            
            #V�rifier le type de travail dans la table F605_QL associ� � un ex�cutant qualifi�
            arcpy.AddMessage("- V�rifier le type de travail est associ� � un ex�cutant qualifi�")
            sql = "SELECT * FROM F605_QL WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les items du r�sultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #D�truire le type de travail dans la table F605_QL associ� � un ex�cutant qualifi�
                sql = "DELETE F605_QL WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donn�e pr�sente")                
            
            #V�rifier le type de travail dans la table F607_QL associ� � un contact d'un ex�cutant qualifi�
            arcpy.AddMessage("- V�rifier le type de travail est associ� � un contact d'un ex�cutant qualifi�")
            sql = "SELECT * FROM F607_QL WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les items du r�sultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #D�truire le type de travail dans la table F607_QL associ� � un contact d'un ex�cutant qualifi�
                sql = "DELETE F607_QL WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donn�e pr�sente")                
            
            #V�rifier le type de travail dans la table F104_TT
            arcpy.AddMessage("- V�rifier l'information du type de travail")
            sql = "SELECT * FROM F104_TT WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            arcpy.AddWarning(resultat[0])
            #D�truire le type de travail dans la table F104_TT
            sql = "DELETE F104_TT WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
            
            #Afficher un message de s�paration
            arcpy.AddMessage(" ")
        
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
        env             = "SIB_PRO"
        ty_travail      = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_travail = sys.argv[2].replace(";",",").replace("'","")
        
        #D�finir l'objet pour d�truire un type de travail pour la production dans SIB.
        oDetruireTypeTravail = DetruireTypeTravail()
        
        #Valider les param�tres obligatoires
        oDetruireTypeTravail.validerParamObligatoire(env, ty_travail)
        
        #Ex�cuter le traitement dpour d�truire un type de travail pour la production dans SIB.
        oDetruireTypeTravail.executer(env, ty_travail)
    
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