#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireIdentifiantBDG.py
# Auteur    : Michel Pothier
# Date      : 22 juin 2016

"""
    Application qui permet de détruire une liste d'identifiants BDG de découpage SNRC 50000 pour la production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    snrc            OB      Liste d'identifiants SNRC à détruire.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireIdentifiantBDG.py env snrc

    Exemple:
        DetruireIdentifiantBDG.py SIB_PRO 021M07,021M08

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireIdentifiantBDG.py 2063 2016-06-22 18:08:21Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireIdentifiantBDG(object):
#*******************************************************************************************
    """
    Permet de détruire une liste d'identifiants BDG de découpage SNRC 50000 pour la production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire une liste d'identifiants BDG de découpage SNRC 50000 pour la production dans SIB.
        
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
    def validerParamObligatoire(self, env, snrc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC à détruire.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(snrc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'snrc')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, snrc):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire une liste d'identifiants BDG de découpage SNRC 50000 pour la production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC à détruire.
        
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
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'PLAN'")
        
        #Détruire les identifiants SNRC de la table F101_SN
        arcpy.AddMessage("- Détruire les identifiants dans la table F101_SN ...")
        #Extraire les identifiants à détruire
        resultat = self.Sib.requeteSib("SELECT * FROM F101_SN WHERE SNRC IN ('" + snrc.replace(",","','") + "')")
        #Traiter tous les SNRCs
        for id in resultat:
            #Afficher l'information du SNRC
            arcpy.AddWarning(str(id))
        #Détruire les SNRC dans la table F101_SN
        sql = "DELETE F101_SN WHERE SNRC IN ('" + snrc.replace(",","','") + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Détruire les identifiants SNRC de la table F101_BG
        arcpy.AddMessage("- Détruire les identifiants dans la table F101_BG ...")
        #Extraire les identifiants à détruire
        resultat = self.Sib.requeteSib("SELECT * FROM F101_BG WHERE IDENTIFIANT IN ('" + snrc.replace(",","','") + "')")
        #Traiter tous les SNRCs
        for id in resultat:
            #Afficher l'information du SNRC
            arcpy.AddWarning(str(id))
        #Détruire les SNRC dans la table F101_BG
        sql = "DELETE F101_BG WHERE IDENTIFIANT IN ('" + snrc.replace(",","','") + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Détruire les identifiants SNRC de la table F103_PS
        arcpy.AddMessage("- Détruire les identifiants dans la table F103_PS ...")
        #Extraire les identifiants à détruire
        resultat = self.Sib.requeteSib("SELECT * FROM F103_PS WHERE SNRC IN ('" + snrc.replace(",","','") + "')")
        #Traiter tous les SNRCs
        for id in resultat:
            #Afficher l'information du SNRC
            arcpy.AddWarning(str(id))
        #Détruire les SNRC dans la table F103_PS
        sql = "DELETE F103_PS WHERE SNRC IN ('" + snrc.replace(",","','") + "')"
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
        snrc        = ""

        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            snrc = sys.argv[2].upper().replace(";",",")
        
        #Définir l'objet pour détruire une liste d'identifiants d'un identifiant BDG de découpage SNRC 50000 pour la production dans SIB.
        oDetruireIdentifiantBDG = DetruireIdentifiantBDG()
        
        #Valider les paramètres obligatoires
        oDetruireIdentifiantBDG.validerParamObligatoire(env, snrc)
        
        #Exécuter le traitement pour détruire une liste d'identifiants BDG de découpage SNRC 50000 pour la production dans SIB.
        oDetruireIdentifiantBDG.executer(env, snrc)
    
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