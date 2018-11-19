#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 10 novembre 2014

"""
    Application qui permet de modifier un type de travail pour la production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    ty_travail      OB      Type de travail à modifier.
                            défaut = 
    listeTyProduit  OB      Liste des types de produit sur lequel le type de travail peut être exécuté.
                            défaut = <Liste des produits actuels>
    nom             OP      Nom en français du type de travail.
                            défaut = <Même que celui actuel>
    nom_an          OP      Nom en anglais du type de travail.
                            défaut = <Même que celui actuel>
    impact          OP      Impact du type de travail sur le jeu de données [E:Édition/V:Version/N:Sans objet].
                            défaut = <Même que celui actuel>
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierTypeTravail.py env ty_travail nom nom_an impact listeTyProduit

    Exemple:
        ModifierTypeTravail.py SIB_PRO PREP "Préparation révision par imagerie" "Preparation for revision by Sat. Imagery" N BDG,ESSIM

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierTypeTravail.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierTypeTravail(object):
#*******************************************************************************************
    """
    Permet de modifier un type de travail pour la production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification d'un type de travail pour la production dans SIB.
        
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
    def validerParamObligatoire(self, env, ty_travail, listeTyProduit):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail à modifier.
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

        if (len(listeTyProduit) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'listeTyProduit')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, listeTyProduit, nom, nom_an, impact):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de modification d'un type de travail pour la production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail à modifier.
        listeTyProduit  : Liste des types de produit sur lequel le type de travail peut être exécuté.
        nom             : Nom den français du type de travail.
        nom_an          : Nom en anglais du type de travail.
        impact          : Impact du type de travail sur le jeu de données [E:Édition/V:Version/N:Sans objet]
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        listeProduit    : Liste des types de produit valident.
        tyProduit       : Type de produit traité.
        actif           : Indique si le type de travail pour le produit est actif (1:Actif).
        listeProduitActuel : Liste des types de produit actuels

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
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le type de travail '" + ty_travail + "' n'existe pas")
        
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
        
        #Vérifier si on doit modifier l'information du type de travail
        if nom <> "" or nom_an <> "" or impact <> "":
            #Initialiser la commande SQL de modifification
            sql = "UPDATE F104_TT SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,UPDT_FLD=P0G03_UTL.PU_HORODATEUR"
            
            #Vérifier la présence du nom français
            if nom <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM='" + nom + "'"
            
            #Vérifier la présence du nom anglais
            if nom_an <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM_AN='" + nom_an + "'"
            
            #Vérifier la présence de l'impact
            if impact <> "":
                #Vérifier si l'impact est valide
                if impact <> "E" and impact <> "V" and impact <> "N":
                    #Retourner une exception
                    raise Exception("Impact invalide : %s" %'impact')
                #Ajouter la modification de l'impact
                sql = sql + ",IMPACT='" + impact + "'"
            
            #Ajouter le WHERE CLAUSE pour traiter seulement le type de travail
            sql = sql + " WHERE TY_TRAV='" + ty_travail + "'"
            
            #Créer le type de travail
            arcpy.AddMessage("- Modifier l'information du type de travail")
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)

        #Extraire les types de produit actuels
        arcpy.AddMessage("- Extraire les types de produit actuels")
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F105_ET WHERE TY_TRAV='" + ty_travail + "'")
        #Créer la liste des types de produits valident
        listeProduitActuel = []
        for tyProduit in resultat:
            #Ajouter le type de produit à la liste
            listeProduitActuel.append(tyProduit[0])
        
        #Détruire les types de produit
        arcpy.AddMessage("- Détruire les types de produit en trop")
        arcpy.AddMessage(" Produit actuel : " + str(listeProduitActuel))
        arcpy.AddMessage(" Produit listé : " + listeTyProduit)
        #Traiter la liste des types de produit
        for tyProduit in listeProduitActuel:
            #Vérifier si le produit est déjà présent
            if tyProduit not in listeTyProduit.split(","):
                #Détruire le type de produit associé au type de travail
                sql = "DELETE F105_ET WHERE TY_PRODUIT='" + tyProduit + "' AND TY_TRAV='" + ty_travail + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
        
        #Ajouter les types de produit associés au type de travail
        arcpy.AddMessage("- Ajouter les types de produit manquants")
        #Traiter la liste des types de produit
        for tyProduit in listeTyProduit.split(","):
            #Vérifier si le produit est déjà présent
            if tyProduit not in listeProduitActuel:
                #Ajouter le type de produit associé au type de travail
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
        env             = "SIB_PRO"
        ty_travail      = ""
        listeTyProduit  = ""
        nom             = ""
        nom_an          = ""
        impact          = ""


        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_travail = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            listeTyProduit = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                nom = sys.argv[4]
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                nom_an = sys.argv[5]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                impact = sys.argv[6].upper()
        
        #Définir l'objet de  modification d'un type de travail pour la production dans SIB.
        oModifierTypeTravail = ModifierTypeTravail()
        
        #Valider les paramètres obligatoires
        oModifierTypeTravail.validerParamObligatoire(env, ty_travail, listeTyProduit)
        
        #Exécuter le traitement de  modification d'un type de travail pour la production dans SIB.
        oModifierTypeTravail.executer(env, ty_travail, listeTyProduit, nom, nom_an, impact)
    
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