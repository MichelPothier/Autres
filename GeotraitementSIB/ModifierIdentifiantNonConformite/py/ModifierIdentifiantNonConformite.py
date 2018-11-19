#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierIdentifiantNonConformite.py
# Auteur    : Michel Pothier
# Date      : 14 septembre 2016

"""
    Application qui permet de modifier l'information d'un identifiant d'un produit pour une non-conformité.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    no_nc                   Numéro de non-conformité à traiter.
                            défaut = 
    ty_produit      OB      Type de produit qui est non-conforme.
                            défaut = 
    identifiant     OB      Identifiants de la non-conformité à modifier.
                            défaut = 
    edVerDebut      OB      Édition et version de début de non-conformité.
                            défaut = 
    edVerFin        OB      Édition et version de fin de non-conformité.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierIdentifiantNonConformite(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'un identifiant d'un produit pour une non-conformité.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier l'information d'un identifiant d'un produit pour une non-conformité.
        
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
    def validerParamObligatoire(self, env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité à traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiant     : Identifiants de la non-conformité à modifier.
        edVerDebut      : Édition et version de début de non-conformité.
        edVerFin        : Édition et version de fin de non-conformité.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')

        if (len(no_nc) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(ty_produit) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'ty_produit')
        
        if (len(identifiant) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'identifiant')
        
        if (len(edVerDebut) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'edVerDebut')
        
        if (len(edVerFin) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'edVerFin')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'information d'un identifiant d'un produit pour une non-conformité.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité à traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiant     : Identifiants de la non-conformité à modifier.
        edVerDebut      : Édition et version de début de non-conformité.
        edVerFin        : Édition et version de fin de non-conformité.
        
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
        
        #Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #------------------------------------------------------
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #------------------------------------------------------
        #Valider si la non-conformité est absente
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si la non-conformité est déjà présente ...")
        sql = "SELECT NO_NC,DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + no_nc + "' AND DATE_FERMETURE IS NULL"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception(u"La non-conformité '" + no_nc + "' n'existe pas ou est fermée")
        #Vérifier la date de traitement
        if str(resultat[0][1]) <> "None":
            #Retourner un avertissement
            arcpy.AddWarning("ATTENTION : La date de traitement est présente : " + str(resultat[0][1]))
        
        #------------------------------------------------------
        #Extraire le nombre d'identifiants existants de la non-conformité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider l'identifiant de la non-conformité ...")
        #Extraire les identifiants existants
        sql = "SELECT IDENTIFIANT,ED_DEBUT,VER_DEBUT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
        #Afficher et exécuter la commande
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'identifiant est absent de la non-conformité : " + identifiant)
        #Afficher l'information déjà présente
        arcpy.AddMessage(str(resultat[0]))
        
        #------------------------------------------------------
        #Valider l'information de l'identifiant de la non-conformité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider l'information de l'identifiant de la non-conformité ...")   
        #Extraire les numéros d'édition et version du jeu de données
        sql = "SELECT ED||'.'||VER FROM V200_IN WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Construire la liste des éditions et versions valident
        listeEdVer = []
        for edVer in resultat:
            listeEdVer.append(edVer[0])
        
        #Vérifier l'édition et version de début
        if edVerDebut not in listeEdVer:
            #Retourner une exception
            raise Exception(u"L'édition et version de début est invalide : " + edVerDebut + "<>" + str(listeEdVer))
        #Définir le numéro d'édition et version de début
        edDebut, verDebut = edVerDebut.split(".") 
        
        #Vérifier l'édition et version de fin
        listeEdVer.append("99999.99")
        if edVerFin not in listeEdVer:
            #Retourner une exception
            raise Exception(u"L'édition et version de fin est invalide : " + edVerFin + "<>" + str(listeEdVer))
        #Définir le numéro d'édition et version de fin
        edFin, verFin = edVerFin.split(".") 
        
        #Vérifier l'édition et version de début par rapport à celui de la fin
        if edVerDebut > edVerFin:
            #Retourner une exception
            raise Exception(u"L'édition et version de début est plus grand que celui de fin : " + edVerDebut + ">" + edVerFin)
        
        #------------------------------------------------------
        #Modifier l'information de l'identifiant de la non-conformité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information de l'identifiant de la non-conformité ...")   
        #Construire la requête pour modifier l'information de l'identifiant de la non-conformité
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env             = "SIB_PRO"
        no_nc           = ""
        ty_produit      = ""
        identifiant     = ""
        edVerDebut      = ""
        edVerFin        = ""

        #extraction des paramètres d'exécution
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
        
        #Définir l'objet pour modifier l'information d'un identifiant d'un produit pour une non-conformité.
        oModifierIdentifiantNonConformite = ModifierIdentifiantNonConformite()
        
        #Valider les paramètres obligatoires
        oModifierIdentifiantNonConformite.validerParamObligatoire(env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin)
        
        #Exécuter le traitement pour modifier l'information d'un identifiant d'un produit pour une non-conformité.
        oModifierIdentifiantNonConformite.executer(env, no_nc, ty_produit, identifiant, edVerDebut, edVerFin)   

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