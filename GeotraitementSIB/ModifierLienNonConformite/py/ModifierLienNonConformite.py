#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierLienNonConformite.py
# Auteur    : Michel Pothier
# Date      : 19 septembre 2016

"""
    Application qui permet de modifier les liens d'une non-conformité avec d'autres non-conformités.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    no_nc                   Numéro de non-conformité à modifier.
                            défaut = 
    lien_nc         OP      La liste des numéros de non-conformité en lien avec celui traité.
                            défaut =
                            ATTENTION : Si aucun lien n'est spécifié, aucun lien ne sera présent.
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierLienNonConformite.py env no_nc lien_nc

    Exemple:
        ModifierLienNonConformite.py SIB_PRO 3034 3031,3032

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierLienNonConformite.py 2127 2016-09-19 15:32:57Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierLienNonConformite(object):
#*******************************************************************************************
    """
    Permet de modifier les liens d'une non-conformité avec d'autres non-conformités.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier les liens d'une non-conformité avec d'autres non-conformités.
        
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
    def validerParamObligatoire(self, env, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité à modifier.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(no_nc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'no_nc')
        
        #Sortir
        return
        
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, lien_nc):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier les liens d'une non-conformité avec d'autres non-conformités.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité à modifier.
        lien_nc         : La liste des numéros de non-conformité en lien avec celui à créer.
        
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
        
        # Définition du format de la date
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
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #------------------------------------------------------
        #Valider si la non-conformité est absente
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si la non-conformité est présente")
        sql = "SELECT NO_NC,DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + no_nc + "' AND DATE_FERMETURE IS NULL"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception("La non-conformité '" + no_nc + "' n'existe pas ou est fermée")
        #Vérifier la date de traitement
        if str(resultat[0][1]) <> "None":
            #Retourner un AVERTISSEMENT
            arcpy.AddWarning("Attention : La date de traitement est présente : " + str(resultat[0][1]))
        
        #------------------------------------------------------
        #Extraire les liens entre les non-conformités
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire les liens entre les non-conformités ...")
        listeLienConserver = []
        #Extraire les liens
        sql = "SELECT NO_NC FROM F704_LI WHERE NO_ACTION='" + no_nc + "' AND TY_LIEN='NC'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Retourner un AVERTISSEMENT
        arcpy.AddWarning("Nombre de lien(s) déjà présent(s) : " + str(len(resultat)))
        arcpy.AddWarning(str(resultat))
        
        #------------------------------------------------------
        #Détruire les liens entre les non-conformités
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Détruire les liens entre les non-conformités ...")
        #Initialiser le nombre de liens détruits
        nbLienDet = 0
        #Afficher les liens
        for nc in resultat:
            #Vérifier si le lien doit être détruit
            if nc[0] not in lien_nc:
                #Afficher et exécuter la commande
                sql = "DELETE F704_LI WHERE NO_ACTION='" + no_nc + "' AND NO_NC='" + nc[0] + "' AND TY_LIEN='NC'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
                #Compter le nombre de liens détruits
                nbLienDet = nbLienDet + 1
            #Si le lien est à conserver
            else:
                #Créer la liste des liens à conserver
                listeLienConserver.append(nc[0])
        #Vérifier le nombre de liens détruits
        if nbLienDet == 0:
            #Retourner un AVERTISSEMENT
            arcpy.AddWarning("Attention : Aucun Lien n'a été détruit!")
        
        #------------------------------------------------------
        #Créer les liens entre les non-conformités
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les liens entre les non-conformités ...")
        #Initialiser le nombre de liens détruits
        nbLienAdd = 0
        #Vérifier la présence des liens entre les NC
        if len(lien_nc) > 0:
            #Traiter tous les liens entre les non-conformités
            for lien in lien_nc.split(","):
                #Vérifier si le lien doit être ajouté
                if lien.split(":")[0] not in listeLienConserver:
                    #Compter le nombre de liens ajoutés
                    nbLienAdd = nbLienAdd + 1
                    #Ajouter un identifiant du produit non-conforme
                    sql = "INSERT INTO F704_LI VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + lien.split(":")[0] + "',P0G03_UTL.PU_HORODATEUR,'NC')"
                    arcpy.AddMessage(sql)
                    self.Sib.execute(sql)
        #Vérifier le nombre de liens ajoutés
        if nbLienAdd == 0:
            #Retourner un AVERTISSEMENT
            arcpy.AddWarning("Attention : Aucun Lien n'a été ajouté!")
        
        #------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
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
        lien_nc         = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            if sys.argv[3] <> "#":
                lien_nc = (sys.argv[3].replace(";",",")).replace("'","")
        
        #Définir l'objet pour modifier les liens d'une non-conformité avec d'autres non-conformités.
        oModifierLienNonConformite = ModifierLienNonConformite()
        
        #Valider les paramètres obligatoires
        oModifierLienNonConformite.validerParamObligatoire(env, no_nc)
        
        #Exécuter le traitement pour modifier les liens d'une non-conformité avec d'autres non-conformités.
        oModifierLienNonConformite.executer(env, no_nc, lien_nc)   

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