#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 10 novembre 2014

"""
    Application qui permet de cr�er un nouveau type de travail pour la production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    ty_travail      OB      Type de travail � cr�er
                            d�faut = 
    nom             OB      Nom den fran�ais du type de travail.
                            d�faut = 
    nom_an          OB      Nom en anglais du type de travail.
                            d�faut = 
    impact          OB      Impact du type de travail sur le jeu de donn�es [E:�dition/V:Version/N:Sans objet]
                            d�faut = N
    listeTyProduit  OB      Liste des types de produit sur lequel le type de travail peut �tre ex�cut�.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        CreerTypeTravail.py env ty_travail nom nom_an impact listeTyProduit

    Exemple:
        CreerTypeTravail.py SIB_PRO PREP "Pr�paration r�vision par imagerie" "Preparation for revision by Sat. Imagery" N BDG,ESSIM

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerTypeTravail.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerTypeTravail(object):
#*******************************************************************************************
    """
    Permet de cr�er un nouveau type de travail pour la production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'un nouveau type de travail pour la production dans SIB.
        
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
    def validerParamObligatoire(self, env, ty_travail, nom, nom_an, impact, listeTyProduit):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail � cr�er
        nom             : Nom den fran�ais du type de travail.
        nom_an          : Nom en anglais du type de travail.
        impact          : Impact du type de travail sur le jeu de donn�es [E:�dition/V:Version/N:Sans objet]
        listeTyProduit  : Liste des types de produit sur lequel le type de travail peut �tre ex�cut�.

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

        if (len(nom) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom_an')

        if impact <> "E" and impact <> "V" and impact <> "N":
            raise Exception("Param�tre obligatoire manquant: %s" %'impact')

        if (len(listeTyProduit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'listeTyProduit')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, nom, nom_an, impact, listeTyProduit):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'un nouveau type de travail pour la production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail � cr�er
        nom             : Nom den fran�ais du type de travail.
        nom_an          : Nom en anglais du type de travail.
        impact          : Impact du type de travail sur le jeu de donn�es [E:�dition/V:Version/N:Sans objet]
        listeTyProduit  : Liste des types de produit sur lequel le type de travail peut �tre ex�cut�.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        listeProduit    : Liste des types de produit valident.
        tyProduit       : Type de produit trait�.
        actif           : Indique si le type de travail pour le produit est actif (1:Actif).

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
        
        #Valider si le type de travail est d�j� pr�sent
        arcpy.AddMessage("- Valider le type de travail")
        resultat = self.Sib.requeteSib("SELECT TY_TRAV FROM F104_TT WHERE TY_TRAV='" + ty_travail + "'")
        #V�rifier si le type de travail est pr�sent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("Le type de travail '" + ty_travail + "' est d�j� pr�sent")
        
        #Valider les types de produit
        arcpy.AddMessage("- Valider les types de produit")
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F000_PR")
        #Cr�er la liste des types de produits valident
        listeProduit = []
        for tyProduit in resultat:
            #Ajouter le type de produit � la liste
            listeProduit.append(tyProduit[0])
        #Traiter la liste des types de produit
        for tyProduit in listeTyProduit.split(","):
            #Valider le type de produit
            if not tyProduit in listeProduit:
                #Retourner une exception
                raise Exception("Le type de produit '" + tyProduit + "' est invalide : " + str(listeProduit))
        
        #Cr�er le type de travail
        arcpy.AddMessage("- Cr�er le type de travail")
        sql = "INSERT INTO F104_TT VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + ty_travail + "','" + nom + "',P0G03_UTL.PU_HORODATEUR,'" + nom_an + "','" + impact + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Ajouter les types de produit associ�s au type de travail
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        ty_travail  = ""
        nom         = ""
        nom_an      = ""
        impact      = "N"
        listeTyProduit  = ""


        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet de cr�ation d'un nouveau type de travail pour la production dans SIB.
        oCreerTypeTravail = CreerTypeTravail()
        
        #Valider les param�tres obligatoires
        oCreerTypeTravail.validerParamObligatoire(env, ty_travail, nom, nom_an, impact, listeTyProduit)
        
        #Ex�cuter le traitement de cr�ation d'un nouveau type de travail pour la production dans SIB.
        oCreerTypeTravail.executer(env, ty_travail, nom, nom_an, impact, listeTyProduit)
    
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