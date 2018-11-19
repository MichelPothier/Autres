#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : AjouterListeIdentifiantNonConformite.py
# Auteur    : Michel Pothier
# Date      : 14 septembre 2016

"""
    Application qui permet d'ajouter des identifiants d'un produit pour une non-conformit� selon une liste d'identifiants sp�cifi�s en param�tre.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    no_nc                   Num�ro de non-conformit� � traiter.
                            d�faut = 
    ty_produit      OB      Type de produit qui est non-conforme.
                            d�faut = 
    identifiants    OB      Liste d'identifiants � ajouter � la non-conformit�.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        AjouterListeIdentifiantNonConformite.py env no_nc ty_produit identifiants 

    Exemple:
        AjouterListeIdentifiantNonConformite.py SIB_PRO 03034 BDG 021M07;021M08

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AjouterListeIdentifiantNonConformite.py 2114 2016-09-15 16:49:02Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class AjouterListeIdentifiantNonConformite(object):
#*******************************************************************************************
    """
    Permet d'ajouter des identifiants d'un produit pour une non-conformit� selon une liste d'identifiants sp�cifi�s en param�tre.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour ajouter des identifiants d'un produit pour une non-conformit� selon une liste d'identifiants sp�cifi�s en param�tre.
        
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
    def validerParamObligatoire(self, env, no_nc, ty_produit, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiants    : Liste d'identifiants � ajouter � la non-conformit�.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')

        if (len(no_nc) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')
        
        if (len(ty_produit) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'ty_produit')
        
        if (len(identifiants) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'identifiants')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, ty_produit, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour ajouter des identifiants d'un produit pour une non-conformit� selon une liste d'identifiants sp�cifi�s en param�tre.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiants    : Liste d'identifiants � ajouter � la non-conformit�.
        
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
        
        #D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #------------------------------------------------------
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'ISO-RQNC'")
        
        #------------------------------------------------------
        #Valider si la non-conformit� est absente
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si la non-conformit� est d�j� pr�sente ...")
        sql = "SELECT NO_NC,DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + no_nc + "' AND DATE_FERMETURE IS NULL"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception(u"La non-conformit� '" + no_nc + "' n'existe pas ou est ferm�e")
        #V�rifier la date de traitement
        if str(resultat[0][1]) <> "None":
            #Retourner un avertissement
            arcpy.AddWarning("ATTENTION : La date de traitement est pr�sente : " + str(resultat[0][1]))
        
        #------------------------------------------------------
        #Extraire le nombre d'identifiants existants de la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire le nombre d'identifiants existants de la non-conformit� ...")
        #Extraire les identifiants existants
        sql = "SELECT TY_PRODUIT, COUNT(*) FROM F705_PR WHERE NO_NC='" + no_nc + "' GROUP BY TY_PRODUIT ORDER BY TY_PRODUIT"
        #Afficher et ex�cuter la commande
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Conserver le nombre d'identifiants non-conformes existants
        nbEx = 0
        #Compter le nombre d'identifiants existants
        for produit in resultat:
            #Compter les identifiants non-conformes existants
            nbEx = nbEx + produit[1]
            #Afficher le nombre d'identifiants par produit
            arcpy.AddWarning(produit[0] + " : " + str(produit[1]))            
        #Afficher le nombre d'identifiants non-conformes existants
        arcpy.AddWarning("Nombre total d'identifiants existants : " + str(nbEx))
        
        #------------------------------------------------------
        #Ajouter les identifiants du produit non-conformes
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les identifiants s�lectionn�s � la non-conformit� ...")
        #Initialiser le compteur d'identifiants s�lectionn�s
        nbSel = 0
        nbSelEx = 0
        #Traiter tous les identifiants
        for id in identifiants.split(","):
            #Compteur d'identifiants s�lectionn�s
            nbSel = nbSel + 1
            #D�finir l'identifiant
            identifiant = id.split(" ")[0]
            #Afficher l'ent�te de l'identifiant trait�
            arcpy.AddMessage(str(nbSel) + " : " + identifiant)
            
            #------------------------------------------------------
            #Extraire le num�ro d'�dition et version du jeu de donn�es courant
            sql = "SELECT ED,VER FROM V200_IN WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND JEU_COUR=1"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception(u"Il n'y a pas de jeu de donn�es courant pour l'identifiant : " + identifiant)
            #D�finir l'�dition et version de d�but et fin de l'identifiant non-conforme
            ed_deb = str(resultat[0][0])
            ver_deb = str(resultat[0][1])
            ed_fin = '99999'
            ver_fin = '99'
            
            #------------------------------------------------------
            #V�rifier si l'identifiants est d�j� existant
            sql = "SELECT TY_PRODUIT,IDENTIFIANT,ED_DEBUT,VER_DEBUT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
            #Afficher et ex�cuter la commande
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si l'identifiant s�lectionn� est inexistant
            if not resultat:
                #Ajouter un identifiant du produit non-conforme
                sql = "INSERT INTO F705_PR VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + ty_produit + "','" + identifiant + "'," + ed_deb + "," + ver_deb
                sql = sql + ",P0G03_UTL.PU_HORODATEUR," + ed_fin + "," + ver_fin + ")"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            #si l'identifiant s�lectionn� est d�j� existant dans la non-conformit�
            else:
                #Compter le nombre d'identifiants s�lectionn�s existants
                nbSelEx = nbSelEx + 1
                #Afficher l'�dition et version du jeu courant
                arcpy.AddWarning("�dition et version du jeu courant : " + str(ed_deb) + "." + str(ver_deb))
                #Afficher le message d'avertissement
                arcpy.AddWarning("Identifiant d�j� existant dans la non-conformit� : " + str(resultat))
            #Afficher un s�parateur
            arcpy.AddMessage(" ")
        
        #------------------------------------------------------
        #V�rifier si aucun identifiant n'est s�lectionn�
        if nbSel == 0:
            #Retourner une exception
            raise Exception(u"Vous n'avez s�lectionn� aucun identifiant dans la classe de d�coupage.")
        #Afficher le nombre d'identifiants non-conformes � ajouter
        arcpy.AddWarning("Nombre total d'identifiants s�lectionn�s : " + str(nbSel))
        #Afficher le nombre d'identifiants non-conformes � ajouter
        arcpy.AddWarning("Nombre total d'identifiants pr�sents dans la non-conformit� : " + str(nbSel + nbEx - nbSelEx))
        
        #------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #------------------------------------------------------
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
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
        no_nc           = ""
        ty_produit      = ""
        identifiants    = ""

        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            ty_produit = sys.argv[3].upper().split(":")[0]
        
        if len(sys.argv) > 4:
            identifiants = sys.argv[4].replace(";",",").replace("'","")
        
        #D�finir l'objet pour ajouter des identifiants d'un produit pour une non-conformit� selon une liste d'identifiants sp�cifi�s en param�tre.
        oAjouterListeIdentifiantNonConformite = AjouterListeIdentifiantNonConformite()
        
        #Valider les param�tres obligatoires
        oAjouterListeIdentifiantNonConformite.validerParamObligatoire(env, no_nc, ty_produit, identifiants)
        
        #Ex�cuter le traitement pour ajouter des identifiants d'un produit pour une non-conformit� selon une liste d'identifiants sp�cifi�s en param�tre.
        oAjouterListeIdentifiantNonConformite.executer(env, no_nc, ty_produit, identifiants)   

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