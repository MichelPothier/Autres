#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 25 août 2015

"""
    Application qui permet de détruire un ou plusieurs type de travail qui n'ont jamais été utilisés en production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    ty_travail      OB      Type de travail à modifier.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireTypeTravail(object):
#*******************************************************************************************
    """
    Permet de détruire un ou plusieurs type de travail qui n'ont jamais été utilisés en production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire un ou plusieurs type de travail qui n'ont jamais été utilisés en production dans SIB.
        
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
    def validerParamObligatoire(self, env, ty_travail):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail à modifier.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(ty_travail) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'ty_travail')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs type de travail qui n'ont jamais été utilisés en production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail à modifier.
        
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
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Détruire les types de travail
        arcpy.AddMessage("- Détruire les types de travail")
        #Traiter la liste des types de travail
        for travail in ty_travail.split(','):
            #Extraire le type de travail à détruire
            ty_trav = travail.split(":")[0]
            #Détruire le travail
            arcpy.AddMessage("- Détruire le type de travail : " + ty_trav)
            
            #Valider si le type de travail est déjà présent
            arcpy.AddMessage("- Valider le type de travail")
            sql = "SELECT TY_TRAV FROM F104_TT WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si le type de travail est présent
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception("Le type de travail '" + ty_travail + "' n'existe pas")
            
            #Valider si le type de travail a déjà été traité en production
            arcpy.AddMessage("- Valider si le type de travail a déjà été traité en production")
            sql = "SELECT TY_TRAV FROM F104_TT WHERE TY_TRAV NOT IN (SELECT TY_TRAV FROM F503_TR)"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si le type de travail a déjà été traité en production
            if (ty_trav,) not in resultat:
                #Retourner une exception
                raise Exception("Le type de travail '" + ty_travail + "' a déjà été traité en production et ne peut être détruit")
            
            #Vérifier le type de travail dans la table F105_ET associé à un type de produit
            arcpy.AddMessage("- Vérifier le type de travail est associé à un type de produit")
            sql = "SELECT * FROM F105_ET WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Traiter tous les items du résultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #Détruire le type de travail dans la table F105_ET associé à un type de produit
                sql = "DELETE F105_ET WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donnée présente")                
            
            #Vérifier le type de travail dans la table F106_EI étape et associé à un type de produit
            arcpy.AddMessage("- Vérifier le type de travail est associé à une étape et à un type de produit")
            sql = "SELECT * FROM F106_EI WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Traiter tous les items du résultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #Détruire le type de travail dans la table F106_EI étape et associé à un type de produit
                sql = "DELETE F106_EI WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donnée présente")                
            
            #Vérifier le type de travail dans la table F116_MI associé à un modèle
            arcpy.AddMessage("- Vérifier le type de travail est associé à un modèle")
            sql = "SELECT * FROM F116_MI WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Traiter tous les items du résultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #Détruire le type de travail dans la table F116_MI associé à un modèle
                sql = "DELETE F116_MI WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donnée présente")                
            
            #Vérifier le type de travail dans la table F605_QL associé à un exécutant qualifié
            arcpy.AddMessage("- Vérifier le type de travail est associé à un exécutant qualifié")
            sql = "SELECT * FROM F605_QL WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Traiter tous les items du résultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #Détruire le type de travail dans la table F605_QL associé à un exécutant qualifié
                sql = "DELETE F605_QL WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donnée présente")                
            
            #Vérifier le type de travail dans la table F607_QL associé à un contact d'un exécutant qualifié
            arcpy.AddMessage("- Vérifier le type de travail est associé à un contact d'un exécutant qualifié")
            sql = "SELECT * FROM F607_QL WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Traiter tous les items du résultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #Détruire le type de travail dans la table F607_QL associé à un contact d'un exécutant qualifié
                sql = "DELETE F607_QL WHERE TY_TRAV='" + ty_trav + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donnée présente")                
            
            #Vérifier le type de travail dans la table F104_TT
            arcpy.AddMessage("- Vérifier l'information du type de travail")
            sql = "SELECT * FROM F104_TT WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            arcpy.AddWarning(resultat[0])
            #Détruire le type de travail dans la table F104_TT
            sql = "DELETE F104_TT WHERE TY_TRAV='" + ty_trav + "'"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
            
            #Afficher un message de séparation
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env             = "SIB_PRO"
        ty_travail      = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_travail = sys.argv[2].replace(";",",").replace("'","")
        
        #Définir l'objet pour détruire un type de travail pour la production dans SIB.
        oDetruireTypeTravail = DetruireTypeTravail()
        
        #Valider les paramètres obligatoires
        oDetruireTypeTravail.validerParamObligatoire(env, ty_travail)
        
        #Exécuter le traitement dpour détruire un type de travail pour la production dans SIB.
        oDetruireTypeTravail.executer(env, ty_travail)
    
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