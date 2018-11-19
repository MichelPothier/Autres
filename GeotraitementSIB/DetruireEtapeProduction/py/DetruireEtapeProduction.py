#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireEtapeProduction.py
# Auteur    : Michel Pothier
# Date      : 09 ao�t 2016

"""
    Application qui permet de d�truire l'information d'une ou plusieurs �tapes de production dans SIB qui sont inactives et non utilis�es.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    listeEtape      OB      Liste des codes d'�tape de production non actifs et non utilis�s.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireEtapeProduction.py env listeEtape

    Exemple:
        DetruireEtapeProduction.py SIB_PRO PREP;INS

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEtapeProduction.py 2105 2016-08-22 17:40:14Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireEtapeProduction(object):
#*******************************************************************************************
    """
    Permet de d�truire l'information d'une ou plusieurs �tapes de production dans SIB qui sont inactives et non utilis�es.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification de l'information d'une �tape de production.
        
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
    def validerParamObligatoire(self, env, listeEtape):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        listeEtape      : Liste des codes d'�tape de production non actifs et non utilis�s.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(listeEtape) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'listeEtape')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, listeEtape):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire l'information d'une ou plusieurs �tapes de production dans SIB qui sont inactives et non utilis�es.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        listeEtape      : Liste des codes d'�tape de production non actifs et non utilis�s.
        
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
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        #D�finir la commande SQL
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        #Afficher la commande SQL
        arcpy.AddMessage(sql)
        #Ex�cuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Traiter toutes les �tapes de production
        for etp in listeEtape.split(","):
            #D�finir le cd_etp sans description
            cd_etp = etp.replace("'","").split(" ")[0]
            
            #Valider si l'�tape de production est valide
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Valider l'�tape de production ...")
            #D�finir la commande pour valider l'�tape
            sql = "SELECT * FROM F117_ET WHERE CD_ETP='" + cd_etp + "' AND ACTIVE=0 AND CD_ETP NOT IN (SELECT DISTINCT CD_ETP FROM F106_EI)"
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Ex�cuter la commande sql
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si l'�tape de production est invalide
            if not resultat:
                #Retourner une exception
                raise Exception("L'�tape de production n'existe pas ou est encore active : " + cd_etp)
            
            #Modifier l'�tape de production
            arcpy.AddMessage("- D�truire l'information de l'�tape de production ...")
            #D�finir la commande SQL pour d�truire l'�tape
            sql = "DELETE F117_ET WHERE CD_ETP='" + cd_etp + "' AND ACTIVE=0"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Afficher l'information de l'�tape
            arcpy.AddWarning(str(resultat[0]))
            #Ex�cuter la commande
            self.Sib.execute(sql)
        
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        listeEtape  = ""

        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeEtape = sys.argv[2].replace(";'","").replace(";",",")
        
        #D�finir l'objet pour d�truire l'information d'une ou plusieurs �tapes de production dans SIB qui sont inactives et non utilis�es.
        oDetruireEtapeProduction = DetruireEtapeProduction()
        
        #Valider les param�tres obligatoires
        oDetruireEtapeProduction.validerParamObligatoire(env, listeEtape)
        
        #Ex�cuter le traitement pour d�truire l'information d'une ou plusieurs �tapes de production dans SIB qui sont inactives et non utilis�es.
        oDetruireEtapeProduction.executer(env, listeEtape)
    
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