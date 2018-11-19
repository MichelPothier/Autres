#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 01 septembre 2015

"""
    Application qui permet de d�truire un ou plusieurs codes d'�quipe qui sont d�sactifs en production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    cd_equipe       OB      Codes des �quipes inactifs � d�truire dans SIB.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireEquipeProduction.py env cd_equipe

    Exemple:
        DetruireEquipeProduction.py SIB_PRO "RRC:R�seau Routier Canadien;MNE:DNEC"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEquipeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de d�truire un ou plusieurs codes d'�quipe qui sont d�sactifs en production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire un ou plusieurs codes d'�quipe qui sont d�sactifs en production dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Codes des �quipes inactifs � d�truire dans SIB.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(cd_equipe) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_equipe')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire un ou plusieurs codes d'�quipe qui sont d�sactifs en production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Codes des �quipes inactifs � d�truire dans SIB.
        
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
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")

        #Traiter la liste des codes d'�quipe
        for equipe in cd_equipe.split(','):
            #Extraire le code d'�quipe � d�truire
            cd_equ = equipe.split(":")[0]
            #D�truire le code d'�quipe
            arcpy.AddMessage("- D�truire le code d'�quipe : " + cd_equ)
            #Valider le code d'�quipe de production dans la table F108_EQ
            sql = "SELECT CD_EQUIPE, ACTIF FROM F108_EQ WHERE CD_EQUIPE='" + cd_equ + "'"
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si le code d'�quipe de production est absent
            if len(resultat) == 0:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code d'�quipe de production '" + cd_equ + "' est absent") 
            #V�rifier si le code d'�quipe de production est actif
            if resultat[0][1] == 1:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code d'�quipe de production '" + cd_equ + "' est actif et ne peut �tre d�truit")
            
            #V�rifier l'ex�cutant de production dans la table F108_EQ
            arcpy.AddMessage("- V�rifier le code d'�quipe de production")
            sql = "SELECT * FROM F108_EQ WHERE CD_EQUIPE='" + cd_equ + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Afficher l'information du code d'�quipe de production
            arcpy.AddWarning(str(resultat[0]))
            #Initialiser la commande SQL de modifification
            arcpy.AddMessage("- D�truire le code d'�quipe de production")
            sql = "DELETE F108_EQ WHERE CD_EQUIPE='" + cd_equ + "'"
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
        cd_equipe       = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_equipe = sys.argv[2].replace(";",",").replace("'","")
        
        #D�finir l'objet pour d�truire un ou plusieurs codes d'�quipe de production dans SIB.
        oDetruireEquipeProduction = DetruireEquipeProduction()
        
        #Valider les param�tres obligatoires
        oDetruireEquipeProduction.validerParamObligatoire(env, cd_equipe)
        
        #Ex�cuter le traitement pour d�truire un ou plusieurs codes d'�quipe de production dans SIB.
        oDetruireEquipeProduction.executer(env, cd_equipe)
    
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