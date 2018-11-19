#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireEquipeProduction.py
# Auteur    : Michel Pothier
# Date      : 01 septembre 2015

"""
    Application qui permet de détruire un ou plusieurs codes d'équipe qui sont désactifs en production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_equipe       OB      Codes des équipes inactifs à détruire dans SIB.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireEquipeProduction.py env cd_equipe

    Exemple:
        DetruireEquipeProduction.py SIB_PRO "RRC:Réseau Routier Canadien;MNE:DNEC"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEquipeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireEquipeProduction(object):
#*******************************************************************************************
    """
    Permet de détruire un ou plusieurs codes d'équipe qui sont désactifs en production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire un ou plusieurs codes d'équipe qui sont désactifs en production dans SIB.
        
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
    def validerParamObligatoire(self, env, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Codes des équipes inactifs à détruire dans SIB.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(cd_equipe) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_equipe')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_equipe):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs codes d'équipe qui sont désactifs en production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        cd_equipe       : Codes des équipes inactifs à détruire dans SIB.
        
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
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")

        #Traiter la liste des codes d'équipe
        for equipe in cd_equipe.split(','):
            #Extraire le code d'équipe à détruire
            cd_equ = equipe.split(":")[0]
            #Détruire le code d'équipe
            arcpy.AddMessage("- Détruire le code d'équipe : " + cd_equ)
            #Valider le code d'équipe de production dans la table F108_EQ
            sql = "SELECT CD_EQUIPE, ACTIF FROM F108_EQ WHERE CD_EQUIPE='" + cd_equ + "'"
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si le code d'équipe de production est absent
            if len(resultat) == 0:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code d'équipe de production '" + cd_equ + "' est absent") 
            #Vérifier si le code d'équipe de production est actif
            if resultat[0][1] == 1:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le code d'équipe de production '" + cd_equ + "' est actif et ne peut être détruit")
            
            #Vérifier l'exécutant de production dans la table F108_EQ
            arcpy.AddMessage("- Vérifier le code d'équipe de production")
            sql = "SELECT * FROM F108_EQ WHERE CD_EQUIPE='" + cd_equ + "'"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Afficher l'information du code d'équipe de production
            arcpy.AddWarning(str(resultat[0]))
            #Initialiser la commande SQL de modifification
            arcpy.AddMessage("- Détruire le code d'équipe de production")
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env             = "SIB_PRO"
        cd_equipe       = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_equipe = sys.argv[2].replace(";",",").replace("'","")
        
        #Définir l'objet pour détruire un ou plusieurs codes d'équipe de production dans SIB.
        oDetruireEquipeProduction = DetruireEquipeProduction()
        
        #Valider les paramètres obligatoires
        oDetruireEquipeProduction.validerParamObligatoire(env, cd_equipe)
        
        #Exécuter le traitement pour détruire un ou plusieurs codes d'équipe de production dans SIB.
        oDetruireEquipeProduction.executer(env, cd_equipe)
    
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