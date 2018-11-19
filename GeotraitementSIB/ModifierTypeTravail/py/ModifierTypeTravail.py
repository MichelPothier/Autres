#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 10 novembre 2014

"""
    Application qui permet de modifier un type de travail pour la production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    ty_travail      OB      Type de travail � modifier.
                            d�faut = 
    listeTyProduit  OB      Liste des types de produit sur lequel le type de travail peut �tre ex�cut�.
                            d�faut = <Liste des produits actuels>
    nom             OP      Nom en fran�ais du type de travail.
                            d�faut = <M�me que celui actuel>
    nom_an          OP      Nom en anglais du type de travail.
                            d�faut = <M�me que celui actuel>
    impact          OP      Impact du type de travail sur le jeu de donn�es [E:�dition/V:Version/N:Sans objet].
                            d�faut = <M�me que celui actuel>
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierTypeTravail.py env ty_travail nom nom_an impact listeTyProduit

    Exemple:
        ModifierTypeTravail.py SIB_PRO PREP "Pr�paration r�vision par imagerie" "Preparation for revision by Sat. Imagery" N BDG,ESSIM

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierTypeTravail.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
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
    def validerParamObligatoire(self, env, ty_travail, listeTyProduit):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail � modifier.
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

        if (len(listeTyProduit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'listeTyProduit')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, listeTyProduit, nom, nom_an, impact):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de modification d'un type de travail pour la production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail � modifier.
        listeTyProduit  : Liste des types de produit sur lequel le type de travail peut �tre ex�cut�.
        nom             : Nom den fran�ais du type de travail.
        nom_an          : Nom en anglais du type de travail.
        impact          : Impact du type de travail sur le jeu de donn�es [E:�dition/V:Version/N:Sans objet]
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        listeProduit    : Liste des types de produit valident.
        tyProduit       : Type de produit trait�.
        actif           : Indique si le type de travail pour le produit est actif (1:Actif).
        listeProduitActuel : Liste des types de produit actuels

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
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le type de travail '" + ty_travail + "' n'existe pas")
        
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
        
        #V�rifier si on doit modifier l'information du type de travail
        if nom <> "" or nom_an <> "" or impact <> "":
            #Initialiser la commande SQL de modifification
            sql = "UPDATE F104_TT SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,UPDT_FLD=P0G03_UTL.PU_HORODATEUR"
            
            #V�rifier la pr�sence du nom fran�ais
            if nom <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM='" + nom + "'"
            
            #V�rifier la pr�sence du nom anglais
            if nom_an <> "":
                #Ajouter la modification de l'impact
                sql = sql + ",NOM_AN='" + nom_an + "'"
            
            #V�rifier la pr�sence de l'impact
            if impact <> "":
                #V�rifier si l'impact est valide
                if impact <> "E" and impact <> "V" and impact <> "N":
                    #Retourner une exception
                    raise Exception("Impact invalide : %s" %'impact')
                #Ajouter la modification de l'impact
                sql = sql + ",IMPACT='" + impact + "'"
            
            #Ajouter le WHERE CLAUSE pour traiter seulement le type de travail
            sql = sql + " WHERE TY_TRAV='" + ty_travail + "'"
            
            #Cr�er le type de travail
            arcpy.AddMessage("- Modifier l'information du type de travail")
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)

        #Extraire les types de produit actuels
        arcpy.AddMessage("- Extraire les types de produit actuels")
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F105_ET WHERE TY_TRAV='" + ty_travail + "'")
        #Cr�er la liste des types de produits valident
        listeProduitActuel = []
        for tyProduit in resultat:
            #Ajouter le type de produit � la liste
            listeProduitActuel.append(tyProduit[0])
        
        #D�truire les types de produit
        arcpy.AddMessage("- D�truire les types de produit en trop")
        arcpy.AddMessage(" Produit actuel : " + str(listeProduitActuel))
        arcpy.AddMessage(" Produit list� : " + listeTyProduit)
        #Traiter la liste des types de produit
        for tyProduit in listeProduitActuel:
            #V�rifier si le produit est d�j� pr�sent
            if tyProduit not in listeTyProduit.split(","):
                #D�truire le type de produit associ� au type de travail
                sql = "DELETE F105_ET WHERE TY_PRODUIT='" + tyProduit + "' AND TY_TRAV='" + ty_travail + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
        
        #Ajouter les types de produit associ�s au type de travail
        arcpy.AddMessage("- Ajouter les types de produit manquants")
        #Traiter la liste des types de produit
        for tyProduit in listeTyProduit.split(","):
            #V�rifier si le produit est d�j� pr�sent
            if tyProduit not in listeProduitActuel:
                #Ajouter le type de produit associ� au type de travail
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
        env             = "SIB_PRO"
        ty_travail      = ""
        listeTyProduit  = ""
        nom             = ""
        nom_an          = ""
        impact          = ""


        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet de  modification d'un type de travail pour la production dans SIB.
        oModifierTypeTravail = ModifierTypeTravail()
        
        #Valider les param�tres obligatoires
        oModifierTypeTravail.validerParamObligatoire(env, ty_travail, listeTyProduit)
        
        #Ex�cuter le traitement de  modification d'un type de travail pour la production dans SIB.
        oModifierTypeTravail.executer(env, ty_travail, listeTyProduit, nom, nom_an, impact)
    
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