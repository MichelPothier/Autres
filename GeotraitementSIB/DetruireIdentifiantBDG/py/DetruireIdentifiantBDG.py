#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireIdentifiantBDG.py
# Auteur    : Michel Pothier
# Date      : 22 juin 2016

"""
    Application qui permet de d�truire une liste d'identifiants BDG de d�coupage SNRC 50000 pour la production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    snrc            OB      Liste d'identifiants SNRC � d�truire.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireIdentifiantBDG(object):
#*******************************************************************************************
    """
    Permet de d�truire une liste d'identifiants BDG de d�coupage SNRC 50000 pour la production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire une liste d'identifiants BDG de d�coupage SNRC 50000 pour la production dans SIB.
        
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
    def validerParamObligatoire(self, env, snrc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC � d�truire.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(snrc) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'snrc')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, snrc):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire une liste d'identifiants BDG de d�coupage SNRC 50000 pour la production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC � d�truire.
        
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
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'PLAN'")
        
        #D�truire les identifiants SNRC de la table F101_SN
        arcpy.AddMessage("- D�truire les identifiants dans la table F101_SN ...")
        #Extraire les identifiants � d�truire
        resultat = self.Sib.requeteSib("SELECT * FROM F101_SN WHERE SNRC IN ('" + snrc.replace(",","','") + "')")
        #Traiter tous les SNRCs
        for id in resultat:
            #Afficher l'information du SNRC
            arcpy.AddWarning(str(id))
        #D�truire les SNRC dans la table F101_SN
        sql = "DELETE F101_SN WHERE SNRC IN ('" + snrc.replace(",","','") + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #D�truire les identifiants SNRC de la table F101_BG
        arcpy.AddMessage("- D�truire les identifiants dans la table F101_BG ...")
        #Extraire les identifiants � d�truire
        resultat = self.Sib.requeteSib("SELECT * FROM F101_BG WHERE IDENTIFIANT IN ('" + snrc.replace(",","','") + "')")
        #Traiter tous les SNRCs
        for id in resultat:
            #Afficher l'information du SNRC
            arcpy.AddWarning(str(id))
        #D�truire les SNRC dans la table F101_BG
        sql = "DELETE F101_BG WHERE IDENTIFIANT IN ('" + snrc.replace(",","','") + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #D�truire les identifiants SNRC de la table F103_PS
        arcpy.AddMessage("- D�truire les identifiants dans la table F103_PS ...")
        #Extraire les identifiants � d�truire
        resultat = self.Sib.requeteSib("SELECT * FROM F103_PS WHERE SNRC IN ('" + snrc.replace(",","','") + "')")
        #Traiter tous les SNRCs
        for id in resultat:
            #Afficher l'information du SNRC
            arcpy.AddWarning(str(id))
        #D�truire les SNRC dans la table F103_PS
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        snrc        = ""

        #extraction des param�tres d'ex�cution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            snrc = sys.argv[2].upper().replace(";",",")
        
        #D�finir l'objet pour d�truire une liste d'identifiants d'un identifiant BDG de d�coupage SNRC 50000 pour la production dans SIB.
        oDetruireIdentifiantBDG = DetruireIdentifiantBDG()
        
        #Valider les param�tres obligatoires
        oDetruireIdentifiantBDG.validerParamObligatoire(env, snrc)
        
        #Ex�cuter le traitement pour d�truire une liste d'identifiants BDG de d�coupage SNRC 50000 pour la production dans SIB.
        oDetruireIdentifiantBDG.executer(env, snrc)
    
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