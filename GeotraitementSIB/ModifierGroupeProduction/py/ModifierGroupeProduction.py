#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierGroupeProduction.py
# Auteur    : Michel Pothier
# Date      : 05 février 2015

"""
    Application qui permet de modifier toute l'information d'un groupe de lot de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    noLot              OB     Numéro du lot de production.
                              défaut = ""
    noGroupe           OB     Numéro de groupe d'un lot de production. Un groupe constitu un sous ensemble du lot. 
                              Il regroupe une partie des fichiers associé au lot. Chaque groupe a ses propres données de qualité.
                              défaut = ""
    dateReception      OP     Date d'échéance qu'a le sous-traitant pour livrer les jeux de données d'un groupe.
                              défaut = ""
    qualContenu        OP     Qualité du contenu. Une valeur calculée à partir du nombre d'erreur détecté dans les données est inscrite dans ce champ par un processus automatique.
                              défaut = ""
    precDeficiente     OP     Indique si la précision des fichiers du groupe est déficiente. Pour certains types de contrat, une précision déficiente résulte en une pénalité de 10%.
                              défaut = ""
    boniPenalite       OP     Valeur du boni (positive) ou de la pénalité (négative) pour le groupe d'un lot de production.
                              Cette valeur tient compte de plusieurs paramètres (nombre d'itération, retard, QUAL_CONTENU).
                              défaut = ""
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierGroupeProduction.py env noLot noGroupe [dateReception] [qualContenu] [precDeficiente] [boniPenalite]

    Exemple:
        ModifierGroupeProduction.py SIB_PRO 35444 01 2015-02-03 0 0 0

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierGroupeProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierGroupeProduction(object):
#*******************************************************************************************
    """
    Permet de modifier toute l'information d'un groupe de lot de production dans SIB.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier toute l'information d'un groupe de lot de production dans SIB.
        
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
    def validerParamObligatoire(self, env, noLot, noGroupe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        noLot           : Numéro du lot de production.
        noGroupe        : Numéro de groupe d'un lot de production.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(noLot) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noLot')
        
        if (len(noGroupe) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noGroupe')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, noLot, noGroupe, dateReception, qualContenu, precDeficiente, boniPenalite):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier toute l'information d'un groupe de lot de production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        noLot           : Numéro du lot de production.
        noGroupe        : Numéro de groupe d'un lot de production.
        dateReception   : Date d'échéance qu'a le sous-traitant pour livrer les jeux de données d'un groupe.
        qualContenu     : Qualité du contenu. Une valeur calculée à partir du nombre d'erreur détecté dans les données est inscrite dans ce champ par un processus automatique.
        precDeficiente  : Indique si la précision des fichiers du groupe est déficiente. Pour certains types de contrat, une précision déficiente résulte en une pénalité de 10%.
        boniPenalite    : Valeur du boni (positive) ou de la pénalité (négative) pour le groupe d'un lot de production.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #Vérifier si l'usager SIB possède les privilège de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'PLAN' ou 'G-SYS'")
        
        #Valider si le lot de production est absent
        arcpy.AddMessage("- Valider le numéro du lot de production")
        resultat = oSib.requeteSib("SELECT DISTINCT NO_LOT FROM F601_GR WHERE NO_LOT='" + noLot + "'")
        #Vérifier si le lot de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le lot de production '" + noLot + "' est absent")
        
        #Valider si le groupe du lot de production est absent
        arcpy.AddMessage("- Valider le groupe du lot de production")
        resultat = oSib.requeteSib("SELECT DISTINCT GROUPE FROM F601_GR WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'")
        #Vérifier si le groupe du lot de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le groupe du lot de production '" + noLot + "' est absent : " + noGroupe)
        
        #Vérifier si la date de réception est vide
        if dateReception == "":
            #Ajouter la valeur NULL
            dateReception = "NULL"
        #si la valeur n'est pas vide
        else:
            #Ajouter les apostrophes
            dateReception = "'" + dateReception + "'"
        
        #Vérifier si le qualificatif de contenu est vide
        if qualContenu == "":
            #Ajouter la valeur NULL
            qualContenu = "NULL"
        
        #Vérifier si la précision déficiente est vide
        if precDeficiente == "":
            #Ajouter la valeur NULL
            precDeficiente = "NULL"
        
        #Vérifier si le boni et pénalité est vide
        if boniPenalite == "":
            #Ajouter la valeur NULL
            boniPenalite = "NULL"
        
        #Modifier l'information du groupe du lot de production
        arcpy.AddMessage("- Modifier l'information du groupe du lot de production")
        #Initialiser la commande SQL de modifification
        sql = "UPDATE F601_GR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE"
        sql = sql + ",DT_RECEP=TO_DATE(" + dateReception + "),QUAL_CONTENU=" + qualContenu + ",PREC_DEFICIENTE=" + precDeficiente + ",BONI_PENALITE=" + boniPenalite
        sql = sql + " WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env              = "SIB_PRO"
        noLot            = ""
        noGroupe         = ""
        dateReception    = ""
        qualContenu      = ""
        precDeficiente   = ""
        boniPenalite     = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            noLot = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            noGroupe = sys.argv[3]
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                dateReception = sys.argv[4]
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                qualContenu = sys.argv[5]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                precDeficiente = sys.argv[6]
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                boniPenalite = sys.argv[7]
        
        #Définir l'objet pour modifier l'information d'un groupe de lot de production.
        oModifierGroupeProduction = ModifierGroupeProduction()
        
        #Valider les paramètres obligatoires
        oModifierGroupeProduction.validerParamObligatoire(env, noLot, noGroupe)
        
        #Exécuter le traitement modifier l'information d'un groupe de lot de production.
        oModifierGroupeProduction.executer(env, noLot, noGroupe, dateReception, qualContenu, precDeficiente, boniPenalite)
    
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