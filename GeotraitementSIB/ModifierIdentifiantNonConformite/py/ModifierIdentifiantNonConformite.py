#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierIdentifiantNonConformite.py
# Auteur    : Michel Pothier
# Date      : 14 septembre 2016

"""
    Application qui permet de modifier l'information d'un identifiant d'un produit pour une non-conformit�.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    no_nc                   Num�ro de non-conformit� � traiter.
                            d�faut = 
    ty_produit      OB      Type de produit qui est non-conforme.
                            d�faut = 
    identifiant     OB      Identifiants de la non-conformit� � modifier.
                            d�faut = 
    edVerDebut      OB      �dition et version de d�but de non-conformit�.
                            d�faut = 
    edVerFin        OB      �dition et version de fin de non-conformit�.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierIdentifiantNonConformite.py env no_nc ty_produit identifiants 

    Exemple:
        ModifierIdentifiantNonConformite.py SIB_PRO 03034 BDG 021M07;021M08

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierIdentifiantNonConformite.py 2117 2016-09-15 16:54:37Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierIdentifiantNonConformite(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'un identifiant d'un produit pour une non-conformit�.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier l'information d'un identifiant d'un produit pour une non-conformit�.
        
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
    def validerParamObligatoire(self, env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiant     : Identifiants de la non-conformit� � modifier.
        edVerDebut      : �dition et version de d�but de non-conformit�.
        edVerFin        : �dition et version de fin de non-conformit�.

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
        
        if (len(identifiant) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'identifiant')
        
        if (len(edVerDebut) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'edVerDebut')
        
        if (len(edVerFin) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'edVerFin')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier l'information d'un identifiant d'un produit pour une non-conformit�.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiant     : Identifiants de la non-conformit� � modifier.
        edVerDebut      : �dition et version de d�but de non-conformit�.
        edVerFin        : �dition et version de fin de non-conformit�.
        
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
        arcpy.AddMessage("- Valider l'identifiant de la non-conformit� ...")
        #Extraire les identifiants existants
        sql = "SELECT IDENTIFIANT,ED_DEBUT,VER_DEBUT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
        #Afficher et ex�cuter la commande
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'identifiant est absent de la non-conformit� : " + identifiant)
        #Afficher l'information d�j� pr�sente
        arcpy.AddMessage(str(resultat[0]))
        
        #------------------------------------------------------
        #Valider l'information de l'identifiant de la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider l'information de l'identifiant de la non-conformit� ...")   
        #Extraire les num�ros d'�dition et version du jeu de donn�es
        sql = "SELECT ED||'.'||VER FROM V200_IN WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Construire la liste des �ditions et versions valident
        listeEdVer = []
        for edVer in resultat:
            listeEdVer.append(edVer[0])
        
        #V�rifier l'�dition et version de d�but
        if edVerDebut not in listeEdVer:
            #Retourner une exception
            raise Exception(u"L'�dition et version de d�but est invalide : " + edVerDebut + "<>" + str(listeEdVer))
        #D�finir le num�ro d'�dition et version de d�but
        edDebut, verDebut = edVerDebut.split(".") 
        
        #V�rifier l'�dition et version de fin
        listeEdVer.append("99999.99")
        if edVerFin not in listeEdVer:
            #Retourner une exception
            raise Exception(u"L'�dition et version de fin est invalide : " + edVerFin + "<>" + str(listeEdVer))
        #D�finir le num�ro d'�dition et version de fin
        edFin, verFin = edVerFin.split(".") 
        
        #V�rifier l'�dition et version de d�but par rapport � celui de la fin
        if edVerDebut > edVerFin:
            #Retourner une exception
            raise Exception(u"L'�dition et version de d�but est plus grand que celui de fin : " + edVerDebut + ">" + edVerFin)
        
        #------------------------------------------------------
        #Modifier l'information de l'identifiant de la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information de l'identifiant de la non-conformit� ...")   
        #Construire la requ�te pour modifier l'information de l'identifiant de la non-conformit�
        sql = "UPDATE F705_PR SET ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ED_DEBUT=" + edDebut + ", VER_DEBUT=" + verDebut + ", ED_FIN=" + edFin + ", VER_FIN=" + verFin
        sql = sql + " WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
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
        identifiant     = ""
        edVerDebut      = ""
        edVerFin        = ""

        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            ty_produit = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            identifiant = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            edVerDebut = sys.argv[5]
        
        if len(sys.argv) > 6:
            edVerFin = sys.argv[6]
        
        #D�finir l'objet pour modifier l'information d'un identifiant d'un produit pour une non-conformit�.
        oModifierIdentifiantNonConformite = ModifierIdentifiantNonConformite()
        
        #Valider les param�tres obligatoires
        oModifierIdentifiantNonConformite.validerParamObligatoire(env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin)
        
        #Ex�cuter le traitement pour modifier l'information d'un identifiant d'un produit pour une non-conformit�.
        oModifierIdentifiantNonConformite.executer(env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin)   

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