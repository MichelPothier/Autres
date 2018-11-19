#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AfficherIdProgrammeNonConforme.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

""" Outil qui permet d'afficher les identifiants au programme contenus dans une non-conformit�.

    Les identifiants sont mise au programme selon une liste de code topographique d'�l�ment.
   
    Les corrections sont effectu�es selon un nom de classe pour lequel un lien (DBLINK=@BDG_VIEW)
    doit �tre fait entre ce dernier et le code topographique d'�l�ment.

    Param�tres d'entr�es:
    ---------------------
    env         : Type d'environnement.
    no_nc       : Num�ro de la non-conformit� � fermer.
    nom_classe  : Nom de la classe � corriger.

    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  Ex: 0=Succ�s, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 

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

# Importation des modules priv�s
import CompteSib

#*******************************************************************************************
class AfficherIdProgrammeNonConforme(object):
#*******************************************************************************************
    """ Afficher les identifiants au programme contenus dans une non-conformit�..
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement d'affichage des identifiants au programme contenus dans une non-conformit�.
        
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
    def executer(self, env, no_nc, nom_classe):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement d'affichage des identifiants au programme contenus dans une non-conformit�.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        no_nc       : Num�ro de la non-conformit� � fermer.
        nom_classe  : Nom de la classe � corriger.
               
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib        : Objet utilitaire pour traiter des services SIB.

        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Cr�er la requ�te SQL.
        arcpy.AddMessage("- Ex�cution du traitement d'affichage des identifiants au programme non-conforme")
        sSql = "SELECT DISTINCT PS.TY_PRODUIT,PS.IDENTIFIANT,PS.NO_MAP,TR.TY_TRAV,LO.CD_EQUIPE,LE.CD_ELEM_TOPO,FD.FEAT_TYPE_NAME_DATABASE FROM F502_PS PS,F705_PR NC,F502_LE LE,F503_TR TR,F601_LO LO,FEATURE_DESCRIPTION@BDG_VIEW FD WHERE NC.NO_NC=" + no_nc + " AND PS.E_PLSNRC = 'P' AND PS.IDENTIFIANT=NC.IDENTIFIANT AND PS.TY_PRODUIT=NC.TY_PRODUIT AND PS.NO_MAP=TR.NO_MAP AND PS.NO_MAP=LE.NO_MAP AND TR.NO_LOT=LO.NO_LOT AND LE.CD_ELEM_TOPO=FD.FEAT_TYPE_CODE_BD AND FD.FEAT_TYPE_NAME_DATABASE like upper('%" + nom_classe + "%') ORDER BY PS.IDENTIFIANT,NO_MAP,CD_ELEM_TOPO"
        #sSql = "SELECT * from f705_pr where no_nc = " + no_nc
        arcpy.AddMessage(sSql)
        
        #Ex�cuter la requ�te SQL
        resultat = oSib.requeteSib(sSql)
        
        #Afficher le r�sultat de la requ�te
        arcpy.AddMessage(" ")
        arcpy.AddMessage("INSTRUCTIONS :")
        arcpy.AddMessage("Les commandes suivantes permettent d'effectuer deux actions :")
        arcpy.AddMessage(" -Annuler le fichier de r�servation.")
        arcpy.AddMessage(" -Cr�er un nouveau fichier de r�servation.")
        arcpy.AddMessage("Vous devez COPIER les commandes et effectuer un COLLER dans un invit� de commandes CMD.")
        arcpy.AddMessage(" ")
        arcpy.AddMessage("IMPORTANT :")
        arcpy.AddMessage("Le fichier Log est cr�� dans le r�pertoire o� sont lanc�es les commandes.")
        arcpy.AddMessage("V�rifier sur les lignes de commandes si les valeurs des param�tres --exp_erreur et --exp_avis correspondent � vos �quipes respectives.")
        arcpy.AddMessage("Si ces valeurs sont erron�es, vos courriels se retrouveront dans les mauvaises bo�tes de courriel.")
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Les commandes � copier commencent ici :")
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
        arcpy.AddMessage("Les commandes � copier se terminent ici :")
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Nombre de mise au programme : " + str(len(resultat)))
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "SIB_PRO"
        no_nc = ""
        nom_classe = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper()

        if len(sys.argv) > 3:
            if sys.argv[3] <> "#":
                nom_classe = sys.argv[3]
        
        # D�finir l'objet d'affichage des identifiants au programme contenus dans une non-conformit�.
        oAfficherIdProgrammeNonConforme = AfficherIdProgrammeNonConforme()
        
        # Ex�cuter le traitement d'affichage des identifiants au programme contenus dans une non-conformit�.
        oAfficherIdProgrammeNonConforme.executer(env, no_nc, nom_classe)
    
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