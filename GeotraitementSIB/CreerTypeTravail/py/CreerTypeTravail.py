#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 10 novembre 2014

"""
    Application qui permet de créer un nouveau type de travail pour la production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    ty_travail      OB      Type de travail à créer
                            défaut = 
    nom             OB      Nom den français du type de travail.
                            défaut = 
    nom_an          OB      Nom en anglais du type de travail.
                            défaut = 
    impact          OB      Impact du type de travail sur le jeu de données [E:Édition/V:Version/N:Sans objet]
                            défaut = N
    listeTyProduit  OB      Liste des types de produit sur lequel le type de travail peut être exécuté.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerTypeTravail.py env ty_travail nom nom_an impact listeTyProduit

    Exemple:
        CreerTypeTravail.py SIB_PRO PREP "Préparation révision par imagerie" "Preparation for revision by Sat. Imagery" N BDG,ESSIM

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerTypeTravail.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerTypeTravail(object):
#*******************************************************************************************
    """
    Permet de créer un nouveau type de travail pour la production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'un nouveau type de travail pour la production dans SIB.
        
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
    def validerParamObligatoire(self, env, ty_travail, nom, nom_an, impact, listeTyProduit):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail à créer
        nom             : Nom den français du type de travail.
        nom_an          : Nom en anglais du type de travail.
        impact          : Impact du type de travail sur le jeu de données [E:Édition/V:Version/N:Sans objet]
        listeTyProduit  : Liste des types de produit sur lequel le type de travail peut être exécuté.

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

        if (len(nom) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom_an')

        if impact <> "E" and impact <> "V" and impact <> "N":
            raise Exception("Paramètre obligatoire manquant: %s" %'impact')

        if (len(listeTyProduit) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'listeTyProduit')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, nom, nom_an, impact, listeTyProduit):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un nouveau type de travail pour la production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail à créer
        nom             : Nom den français du type de travail.
        nom_an          : Nom en anglais du type de travail.
        impact          : Impact du type de travail sur le jeu de données [E:Édition/V:Version/N:Sans objet]
        listeTyProduit  : Liste des types de produit sur lequel le type de travail peut être exécuté.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        listeProduit    : Liste des types de produit valident.
        tyProduit       : Type de produit traité.
        actif           : Indique si le type de travail pour le produit est actif (1:Actif).

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
        
        #Valider si le type de travail est déjà présent
        arcpy.AddMessage("- Valider le type de travail")
        resultat = self.Sib.requeteSib("SELECT TY_TRAV FROM F104_TT WHERE TY_TRAV='" + ty_travail + "'")
        #Vérifier si le type de travail est présent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("Le type de travail '" + ty_travail + "' est déjà présent")
        
        #Valider les types de produit
        arcpy.AddMessage("- Valider les types de produit")
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F000_PR")
        #Créer la liste des types de produits valident
        listeProduit = []
        for tyProduit in resultat:
            #Ajouter le type de produit à la liste
            listeProduit.append(tyProduit[0])
        #Traiter la liste des types de produit
        for tyProduit in listeTyProduit.split(","):
            #Valider le type de produit
            if not tyProduit in listeProduit:
                #Retourner une exception
                raise Exception("Le type de produit '" + tyProduit + "' est invalide : " + str(listeProduit))
        
        #Créer le type de travail
        arcpy.AddMessage("- Créer le type de travail")
        sql = "INSERT INTO F104_TT VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + ty_travail + "','" + nom + "',P0G03_UTL.PU_HORODATEUR,'" + nom_an + "','" + impact + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Ajouter les types de produit associés au type de travail
        arcpy.AddMessage("- Ajouter les types de produit")
        #Traiter la liste des types de produit
        for tyProduit in listeTyProduit.split(","):
            #Extraire le groupe des noms
            actif = '1'
            sql = "INSERT INTO F105_ET VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + tyProduit + "','" + ty_travail + "','" + actif + "')"
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
        ty_travail  = ""
        nom         = ""
        nom_an      = ""
        impact      = "N"
        listeTyProduit  = ""


        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_travail = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            nom = sys.argv[3]
        
        if len(sys.argv) > 4:
            nom_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                impact = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            listeTyProduit = sys.argv[6].upper().replace(";",",")
        
        #Définir l'objet de création d'un nouveau type de travail pour la production dans SIB.
        oCreerTypeTravail = CreerTypeTravail()
        
        #Valider les paramètres obligatoires
        oCreerTypeTravail.validerParamObligatoire(env, ty_travail, nom, nom_an, impact, listeTyProduit)
        
        #Exécuter le traitement de création d'un nouveau type de travail pour la production dans SIB.
        oCreerTypeTravail.executer(env, ty_travail, nom, nom_an, impact, listeTyProduit)
    
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