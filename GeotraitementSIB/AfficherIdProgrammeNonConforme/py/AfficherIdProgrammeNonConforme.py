#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AfficherIdProgrammeNonConforme.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

""" Outil qui permet d'afficher les identifiants au programme contenus dans une non-conformité.

    Les identifiants sont mise au programme selon une liste de code topographique d'élément.
   
    Les corrections sont effectuées selon un nom de classe pour lequel un lien (DBLINK=@BDG_VIEW)
    doit être fait entre ce dernier et le code topographique d'élément.

    Paramètres d'entrées:
    ---------------------
    env         : Type d'environnement.
    no_nc       : Numéro de la non-conformité à fermer.
    nom_classe  : Nom de la classe à corriger.

    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du résultat de l'exécution du programme.
                  Ex: 0=Succès, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 

    Usage:
        AfficherIdProgrammeNonConforme.py env no_nc nom_classe

    Exemple:
        AfficherIdProgrammeNonConforme.py SIB_PRO 22434 NHN_WATERBODY_2
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherIdProgrammeNonConforme.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules privés
import CompteSib

#*******************************************************************************************
class AfficherIdProgrammeNonConforme(object):
#*******************************************************************************************
    """ Afficher les identifiants au programme contenus dans une non-conformité..
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement d'affichage des identifiants au programme contenus dans une non-conformité.
        
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
    def executer(self, env, no_nc, nom_classe):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement d'affichage des identifiants au programme contenus dans une non-conformité.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        no_nc       : Numéro de la non-conformité à fermer.
        nom_classe  : Nom de la classe à corriger.
               
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib        : Objet utilitaire pour traiter des services SIB.

        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Créer la requête SQL.
        arcpy.AddMessage("- Exécution du traitement d'affichage des identifiants au programme non-conforme")
        sSql = "SELECT DISTINCT PS.TY_PRODUIT,PS.IDENTIFIANT,PS.NO_MAP,TR.TY_TRAV,LO.CD_EQUIPE,LE.CD_ELEM_TOPO,FD.FEAT_TYPE_NAME_DATABASE FROM F502_PS PS,F705_PR NC,F502_LE LE,F503_TR TR,F601_LO LO,FEATURE_DESCRIPTION@BDG_VIEW FD WHERE NC.NO_NC=" + no_nc + " AND PS.E_PLSNRC = 'P' AND PS.IDENTIFIANT=NC.IDENTIFIANT AND PS.TY_PRODUIT=NC.TY_PRODUIT AND PS.NO_MAP=TR.NO_MAP AND PS.NO_MAP=LE.NO_MAP AND TR.NO_LOT=LO.NO_LOT AND LE.CD_ELEM_TOPO=FD.FEAT_TYPE_CODE_BD AND FD.FEAT_TYPE_NAME_DATABASE like upper('%" + nom_classe + "%') ORDER BY PS.IDENTIFIANT,NO_MAP,CD_ELEM_TOPO"
        #sSql = "SELECT * from f705_pr where no_nc = " + no_nc
        arcpy.AddMessage(sSql)
        
        #Exécuter la requête SQL
        resultat = oSib.requeteSib(sSql)
        
        #Afficher le résultat de la requête
        arcpy.AddMessage(" ")
        arcpy.AddMessage("INSTRUCTIONS :")
        arcpy.AddMessage("Les commandes suivantes permettent d'effectuer deux actions :")
        arcpy.AddMessage(" -Annuler le fichier de réservation.")
        arcpy.AddMessage(" -Créer un nouveau fichier de réservation.")
        arcpy.AddMessage("Vous devez COPIER les commandes et effectuer un COLLER dans un invité de commandes CMD.")
        arcpy.AddMessage(" ")
        arcpy.AddMessage("IMPORTANT :")
        arcpy.AddMessage("Le fichier Log est créé dans le répertoire où sont lancées les commandes.")
        arcpy.AddMessage("Vérifier sur les lignes de commandes si les valeurs des paramètres --exp_erreur et --exp_avis correspondent à vos équipes respectives.")
        arcpy.AddMessage("Si ces valeurs sont erronées, vos courriels se retrouveront dans les mauvaises boîtes de courriel.")
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Les commandes à copier commencent ici :")
        for _ligne in resultat:
            _depot = _ligne[0]
            _no_map = str(_ligne[2])
            _ty_trav = str(_ligne[3])
            _equipe = str(_ligne[4])
            _expediteur = _depot + "-" + _ty_trav
            arcpy.AddMessage(" ")
            arcpy.AddMessage("REM " + str(_ligne))
            arcpy.AddMessage("%PYTHON27% \\\\dfscitsh\\CITS\\EnvCits\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py AnnulerReservation --depot " + _depot + " --env PRO --no_map " + _no_map + " --exp_erreur " + _expediteur + "-Erreur --exp_avis " + _expediteur + "-Avis --log " + _expediteur + "-" + _no_map + "_annulerReservation.log")
            arcpy.AddMessage("%PYTHON27% \\\\dfscitsh\\CITS\\EnvCits\\applications\\gestion_bdg\\pro\\Gestion_BDSpatiales\\py\\util_Gestion_BDSpatiales.py Reserver --depot " + _depot + " --env PRO --no_map " + _no_map + " --exp_erreur " + _expediteur + "-Erreur --exp_avis " + _expediteur + "-Avis --log " + _expediteur + "-" + _no_map + "_reservation.log")
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Les commandes à copier se terminent ici :")
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Nombre de mise au programme : " + str(len(resultat)))
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "SIB_PRO"
        no_nc = ""
        nom_classe = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper()

        if len(sys.argv) > 3:
            if sys.argv[3] <> "#":
                nom_classe = sys.argv[3]
        
        # Définir l'objet d'affichage des identifiants au programme contenus dans une non-conformité.
        oAfficherIdProgrammeNonConforme = AfficherIdProgrammeNonConforme()
        
        # Exécuter le traitement d'affichage des identifiants au programme contenus dans une non-conformité.
        oAfficherIdProgrammeNonConforme.executer(env, no_nc, nom_classe)
    
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