#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireExecutantProduction.py
# Auteur    : Michel Pothier
# Date      : 27 ao�t 2015

"""
    Application qui permet de d�truire un ou plusieurs ex�cutants de production dans SIB et ses contacts.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    cd_execu        OB      Liste des codes d'ex�cutant de production inactifs � d�truire.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireExecutantProduction.py env cd_execu 

    Exemple:
        DetruireExecutantProduction.py SIB_PRO CITS;CITO

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireExecutantProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireExecutantProduction(object):
#*******************************************************************************************
    """
    Permet de d�truire un ou plusieurs ex�cutants de production inactifs dans SIB et ses contacts.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire un ou plusieurs ex�cutants de production inactifs dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_execu):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Liste des codes d'ex�cutant de production inactifs � d�truire.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(cd_execu) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_execu')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_execu):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire un ou plusieurs ex�cutants de production inactifs dans SIB et ses contacts.
        
        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Liste des codes d'ex�cutant de production inactifs � d�truire.
        
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
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Traiter tous les ex�cutants
        for executant in cd_execu.split(","):
            #D�truire le contact
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- D�truire l'information de l'ex�cutant : ")
            arcpy.AddWarning(executant)
            
            #D�finir le code de l'ex�cutant
            execu = executant.split(":")[0]
            
            #Valider l'ex�cutant de production dans la table F604_EX
            sql = "SELECT CD_EXECU, ACTIF FROM F604_EX WHERE CD_EXECU='" + execu + "'"
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si l'ex�cutant de production est absent
            if len(resultat) == 0:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'ex�cutant de production '" + execu + "' est absent") 
            #V�rifier si l'ex�cutant de production est actif
            if resultat[0][1] == 1:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code de l'ex�cutant de production '" + execu + "' est actif et ne peut �tre d�truit")
            
            #V�rifier l'ex�cutant de production dans la table F604_EX
            arcpy.AddMessage("- V�rifier l'ex�cutant de production")
            sql = "SELECT * FROM F604_EX WHERE CD_EXECU='" + execu + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Afficher l'information de l'ex�cutant de production
            arcpy.AddWarning(str(resultat[0]))
            #Initialiser la commande SQL de modifification
            arcpy.AddMessage("- D�truire l'ex�cutant de production")
            sql = "DELETE F604_EX WHERE CD_EXECU='" + execu + "'"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
            
            #V�rifier les contacts qui sont associ�s � un ex�cutant
            arcpy.AddMessage("- V�rifier les contacts qui sont associ�s � un ex�cutant")
            sql = "SELECT * FROM F607_CO WHERE CD_EXECU='" + execu + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les items du r�sultat
                for item in resultat:
                    #Afficher l'item
                    arcpy.AddWarning(str(item))
                #D�truire les contacts qui sont associ�s � un ex�cutant
                arcpy.AddMessage("- D�truire les contacts qui sont associ�s � un ex�cutant")
                sql = "DELETE F607_CO WHERE CD_EXECU='" + execu + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            else:
                #Afficher le message
                arcpy.AddWarning("Aucune donn�e pr�sente")                
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
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
        cd_execu    = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_execu = sys.argv[2].replace("'","").replace(";",",")
        
        #D�finir l'objet pour d�truire un ou plusieurs ex�cutants de production inactifs dans SIB.
        oDetruireExecutantProduction = DetruireExecutantProduction()
        
        #Valider les param�tres obligatoires
        oDetruireExecutantProduction.validerParamObligatoire(env, cd_execu)
        
        #Ex�cuter le traitement pour d�truire un ou plusieurs ex�cutants de production inactifs dans SIB.
        oDetruireExecutantProduction.executer(env, cd_execu)
    
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