#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : AjouterListeIdentifiantNonConformite.py
# Auteur    : Michel Pothier
# Date      : 14 septembre 2016

"""
    Application qui permet d'ajouter des identifiants d'un produit pour une non-conformité selon une liste d'identifiants spécifiés en paramètre.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    no_nc                   Numéro de non-conformité à traiter.
                            défaut = 
    ty_produit      OB      Type de produit qui est non-conforme.
                            défaut = 
    identifiants    OB      Liste d'identifiants à ajouter à la non-conformité.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class AjouterListeIdentifiantNonConformite(object):
#*******************************************************************************************
    """
    Permet d'ajouter des identifiants d'un produit pour une non-conformité selon une liste d'identifiants spécifiés en paramètre.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour ajouter des identifiants d'un produit pour une non-conformité selon une liste d'identifiants spécifiés en paramètre.
        
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
    def validerParamObligatoire(self, env, no_nc, ty_produit, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité à traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiants    : Liste d'identifiants à ajouter à la non-conformité.

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
        
        if (len(identifiants) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'identifiants')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, ty_produit, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour ajouter des identifiants d'un produit pour une non-conformité selon une liste d'identifiants spécifiés en paramètre.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité à traiter.
        ty_produit      : Type de produit qui est non-conforme.
        identifiants    : Liste d'identifiants à ajouter à la non-conformité.
        
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
        arcpy.AddMessage("- Extraire le nombre d'identifiants existants de la non-conformité ...")
        #Extraire les identifiants existants
        sql = "SELECT TY_PRODUIT, COUNT(*) FROM F705_PR WHERE NO_NC='" + no_nc + "' GROUP BY TY_PRODUIT ORDER BY TY_PRODUIT"
        #Afficher et exécuter la commande
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
        arcpy.AddMessage("- Ajouter les identifiants sélectionnés à la non-conformité ...")
        #Initialiser le compteur d'identifiants sélectionnés
        nbSel = 0
        nbSelEx = 0
        #Traiter tous les identifiants
        for id in identifiants.split(","):
            #Compteur d'identifiants sélectionnés
            nbSel = nbSel + 1
            #Définir l'identifiant
            identifiant = id.split(" ")[0]
            #Afficher l'entête de l'identifiant traité
            arcpy.AddMessage(str(nbSel) + " : " + identifiant)
            
            #------------------------------------------------------
            #Extraire le numéro d'édition et version du jeu de données courant
            sql = "SELECT ED,VER FROM V200_IN WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND JEU_COUR=1"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception(u"Il n'y a pas de jeu de données courant pour l'identifiant : " + identifiant)
            #Définir l'édition et version de début et fin de l'identifiant non-conforme
            ed_deb = str(resultat[0][0])
            ver_deb = str(resultat[0][1])
            ed_fin = '99999'
            ver_fin = '99'
            
            #------------------------------------------------------
            #Vérifier si l'identifiants est déjà existant
            sql = "SELECT TY_PRODUIT,IDENTIFIANT,ED_DEBUT,VER_DEBUT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
            #Afficher et exécuter la commande
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si l'identifiant sélectionné est inexistant
            if not resultat:
                #Ajouter un identifiant du produit non-conforme
                sql = "INSERT INTO F705_PR VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + ty_produit + "','" + identifiant + "'," + ed_deb + "," + ver_deb
                sql = sql + ",P0G03_UTL.PU_HORODATEUR," + ed_fin + "," + ver_fin + ")"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            #si l'identifiant sélectionné est déjà existant dans la non-conformité
            else:
                #Compter le nombre d'identifiants sélectionnés existants
                nbSelEx = nbSelEx + 1
                #Afficher l'édition et version du jeu courant
                arcpy.AddWarning("Édition et version du jeu courant : " + str(ed_deb) + "." + str(ver_deb))
                #Afficher le message d'avertissement
                arcpy.AddWarning("Identifiant déjà existant dans la non-conformité : " + str(resultat))
            #Afficher un séparateur
            arcpy.AddMessage(" ")
        
        #------------------------------------------------------
        #Vérifier si aucun identifiant n'est sélectionné
        if nbSel == 0:
            #Retourner une exception
            raise Exception(u"Vous n'avez sélectionné aucun identifiant dans la classe de découpage.")
        #Afficher le nombre d'identifiants non-conformes à ajouter
        arcpy.AddWarning("Nombre total d'identifiants sélectionnés : " + str(nbSel))
        #Afficher le nombre d'identifiants non-conformes à ajouter
        arcpy.AddWarning("Nombre total d'identifiants présents dans la non-conformité : " + str(nbSel + nbEx - nbSelEx))
        
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
        identifiants    = ""

        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            ty_produit = sys.argv[3].upper().split(":")[0]
        
        if len(sys.argv) > 4:
            identifiants = sys.argv[4].replace(";",",").replace("'","")
        
        #Définir l'objet pour ajouter des identifiants d'un produit pour une non-conformité selon une liste d'identifiants spécifiés en paramètre.
        oAjouterListeIdentifiantNonConformite = AjouterListeIdentifiantNonConformite()
        
        #Valider les paramètres obligatoires
        oAjouterListeIdentifiantNonConformite.validerParamObligatoire(env, no_nc, ty_produit, identifiants)
        
        #Exécuter le traitement pour ajouter des identifiants d'un produit pour une non-conformité selon une liste d'identifiants spécifiés en paramètre.
        oAjouterListeIdentifiantNonConformite.executer(env, no_nc, ty_produit, identifiants)   

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