#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierGroupeProduction.py
# Auteur    : Michel Pothier
# Date      : 05 f�vrier 2015

"""
    Application qui permet de modifier toute l'information d'un groupe de lot de production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              d�faut = SIB_PRO
    noLot              OB     Num�ro du lot de production.
                              d�faut = ""
    noGroupe           OB     Num�ro de groupe d'un lot de production. Un groupe constitu un sous ensemble du lot. 
                              Il regroupe une partie des fichiers associ� au lot. Chaque groupe a ses propres donn�es de qualit�.
                              d�faut = ""
    dateReception      OP     Date d'�ch�ance qu'a le sous-traitant pour livrer les jeux de donn�es d'un groupe.
                              d�faut = ""
    qualContenu        OP     Qualit� du contenu. Une valeur calcul�e � partir du nombre d'erreur d�tect� dans les donn�es est inscrite dans ce champ par un processus automatique.
                              d�faut = ""
    precDeficiente     OP     Indique si la pr�cision des fichiers du groupe est d�ficiente. Pour certains types de contrat, une pr�cision d�ficiente r�sulte en une p�nalit� de 10%.
                              d�faut = ""
    boniPenalite       OP     Valeur du boni (positive) ou de la p�nalit� (n�gative) pour le groupe d'un lot de production.
                              Cette valeur tient compte de plusieurs param�tres (nombre d'it�ration, retard, QUAL_CONTENU).
                              d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
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
    def validerParamObligatoire(self, env, noLot, noGroupe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement.    
        noLot           : Num�ro du lot de production.
        noGroupe        : Num�ro de groupe d'un lot de production.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')
        
        if (len(noLot) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'noLot')
        
        if (len(noGroupe) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'noGroupe')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, noLot, noGroupe, dateReception, qualContenu, precDeficiente, boniPenalite):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier toute l'information d'un groupe de lot de production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        noLot           : Num�ro du lot de production.
        noGroupe        : Num�ro de groupe d'un lot de production.
        dateReception   : Date d'�ch�ance qu'a le sous-traitant pour livrer les jeux de donn�es d'un groupe.
        qualContenu     : Qualit� du contenu. Une valeur calcul�e � partir du nombre d'erreur d�tect� dans les donn�es est inscrite dans ce champ par un processus automatique.
        precDeficiente  : Indique si la pr�cision des fichiers du groupe est d�ficiente. Pour certains types de contrat, une pr�cision d�ficiente r�sulte en une p�nalit� de 10%.
        boniPenalite    : Valeur du boni (positive) ou de la p�nalit� (n�gative) pour le groupe d'un lot de production.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'PLAN' ou 'G-SYS'")
        
        #Valider si le lot de production est absent
        arcpy.AddMessage("- Valider le num�ro du lot de production")
        resultat = oSib.requeteSib("SELECT DISTINCT NO_LOT FROM F601_GR WHERE NO_LOT='" + noLot + "'")
        #V�rifier si le lot de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le lot de production '" + noLot + "' est absent")
        
        #Valider si le groupe du lot de production est absent
        arcpy.AddMessage("- Valider le groupe du lot de production")
        resultat = oSib.requeteSib("SELECT DISTINCT GROUPE FROM F601_GR WHERE NO_LOT='" + noLot + "' AND GROUPE='" + noGroupe + "'")
        #V�rifier si le groupe du lot de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le groupe du lot de production '" + noLot + "' est absent : " + noGroupe)
        
        #V�rifier si la date de r�ception est vide
        if dateReception == "":
            #Ajouter la valeur NULL
            dateReception = "NULL"
        #si la valeur n'est pas vide
        else:
            #Ajouter les apostrophes
            dateReception = "'" + dateReception + "'"
        
        #V�rifier si le qualificatif de contenu est vide
        if qualContenu == "":
            #Ajouter la valeur NULL
            qualContenu = "NULL"
        
        #V�rifier si la pr�cision d�ficiente est vide
        if precDeficiente == "":
            #Ajouter la valeur NULL
            precDeficiente = "NULL"
        
        #V�rifier si le boni et p�nalit� est vide
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env              = "SIB_PRO"
        noLot            = ""
        noGroupe         = ""
        dateReception    = ""
        qualContenu      = ""
        precDeficiente   = ""
        boniPenalite     = ""
        
        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet pour modifier l'information d'un groupe de lot de production.
        oModifierGroupeProduction = ModifierGroupeProduction()
        
        #Valider les param�tres obligatoires
        oModifierGroupeProduction.validerParamObligatoire(env, noLot, noGroupe)
        
        #Ex�cuter le traitement modifier l'information d'un groupe de lot de production.
        oModifierGroupeProduction.executer(env, noLot, noGroupe, dateReception, qualContenu, precDeficiente, boniPenalite)
    
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