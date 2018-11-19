#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AjouterIdentifiantBassinPartie.py
# Auteur    : Michel Pothier
# Date      : 07 mars 2018

"""
    Application qui permet d'ajouter un ou plusieurs identifiants de partie de bassin � partir d'un identifiant de base existant.

    Tous les identifiants de partie compris entre le num�ro de d�but et le num�ro de fin de partie inclusivement sont ajout�s
    avec le nom fran�ais et anglais de l'identifiant de base en y ajoutant le texte " (partie)" pour le nom fran�ais
    et le texte " (part of)" en anglais.
    
    Param�tres d'entr�e:
    --------------------
    environnement      OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV]
                              d�faut = "SIB_PRO"
    identifiant        OB     Identifiant de bassin de base.
                              Un identifiant de base (se termine par un 000).
                              d�faut = ""
    noDebut            OB     Num�ro de d�but de l'identifiant de partie � ajouter.
                              D�faut=
    noFin              OB     Num�ro de fin de l'identifiant de partie � ajouter.
                              D�faut=
    nomFrancais        OP     Nom francais de l'identifiant de partie.
                              d�faut = nomFrancais + " (partie)"
    nomAnglais         OP     Nom anglais de l'identifiant de partie.
                              d�faut = nomAnglais + " (part of)"
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 

    Usage:
        AjouterIdentifiantBassinPartie.py environnement identifiant noDebut noFin [nomFrancais] [nomAnglais]

    Exemple:
        AjouterIdentifiantBassinPartie.py TST 1234000 10 54 "nom francais" "nom anglais"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AjouterIdentifiantBassinPartie.py 2155 2018-03-13 18:04:33Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s
import CompteSib

#*******************************************************************************************
class AjouterIdentifiantBassinPartie(object):
#*******************************************************************************************
    """
    Permet d'ajouter un ou plusieurs identifiants de partie de bassin � partir d'un identifiant de base existant.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour ajouter un ou plusieurs identifiants de partie de bassin � partir d'un identifiant de base existant.
        
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
    def validerParamObligatoire(self, env, identifiant, noDebut, noFin):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement.
        identifiant     : Identifiant de bassin trait�.
        noDebut         : Num�ro de d�but de l'identifiant de partie � ajouter.
        noFin           : Num�ro de fin de l'identifiant de partie � ajouter.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        #V�rifier la pr�sence du param�tre identifiant
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')

        #V�rifier la pr�sence du param�tre identifiant
        if (len(identifiant) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'identifiant')

        #V�rifier la longueur du param�tre identifiant
        if (len(identifiant) <> 7):
            raise Exception("- La longueur de l'identifiant doit �tre de 7: %s" %'identifiant')

        #V�rifier si le num�ro de d�but est valide
        if (noDebut == 0):
            raise Exception("- Le num�ro de d�but doit �tre sup�rieur � 0")

        #V�rifier si le num�ro de d�but est valide
        if (noDebut > noFin):
            raise Exception("- Le num�ro de d�but doit �tre inf�rieur ou �gale � de celui de la fin")

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, identifiant, noDebut, noFin, nomFrancais, nomAnglais):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour ajouter un ou plusieurs identifiants de partie de bassin � partir d'un identifiant de base existant.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        identifiant     : Identifiant de bassin trait�.
        noDebut         : Num�ro de d�but de l'identifiant de partie � ajouter.
        noFin           : Num�ro de fin de l'identifiant de partie � ajouter.
        nomFrancais     : Nom francais de l'identifiant de partie.
        nomAnglais      : Nom anglais de l'identifiant de partie.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        resultat        : R�sultat de la requ�te.
        message         : Message d'erreur.
        code_retour     : Code de retour d'un service SIB.
        
        Retour:
        -------
        Exception s'il y a une erreur.
        
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'PLAN'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'PLAN'")
        
        #Requ�te pour v�rifier les identifiants trait�s
        arcpy.AddMessage("- Valider l'identifiant de bassin de base : " + identifiant)
        resultat = oSib.requeteSib("SELECT IDENTIFIANT, NOM_FR, NOM_AN FROM F101_BV WHERE IDENTIFIANT='" + identifiant + "'")
        #V�rifier si aucun r�sultat
        if not resultat:
           raise Exception("- L'identifiant de de bassin de base est invalide : " + identifiant)
        
        #Valider le num�ro de d�but et de fin
        arcpy.AddMessage("- Valider le num�ro de d�but et de fin ...")
        #Valider le num�ro d'identifiant de partie de d�but
        if noDebut == 0:
           raise Exception("- Le num�ro de d�but doit �tre sup�rieure � z�ro")
        #Valider le num�ro d'identifiant de partie de d�but
        if noDebut > noFin:
           raise Exception("- Le num�ro de d�but doit �tre sup�rieure ou �gale au num�ro de fin")
        #Valider le num�ro d'identifiant de partie de fin
        if noFin > 999:
           raise Exception("- Le num�ro de fin doit �tre inf�rieure ou �gale � 999")
        
        #V�rifier si le nom fran�ais est sp�cifi�
        if len(nomFrancais) == 0:
            #D�finir le nom fran�ais par d�faut
            nomFrancais = resultat[0][1] + " (partie)"

        #V�rifier si le nom fran�ais est sp�cifi�
        if len(nomAnglais) == 0:
            #D�finir le nom anglais par d�faut
            nomAnglais = resultat[0][2] + " (part of)"
        
        #D�finir le d�but de l'identifiant de partie
        id = identifiant[0:4]
        
        #Valider le num�ro de d�but et de fin
        arcpy.AddMessage("- Ajouter les identifiants de partie ...")
        #Traiter tous les identifiant de bassin de partie
        for i in range(noDebut,noFin+1):
            #D�finir le num�ro de partie
            idPartie = id + str(i).rjust(3,'0')
            #D�finir la requ�te pour v�rifier si l'identifiant de partie existe
            resultat = oSib.requeteSib("SELECT IDENTIFIANT, NOM_FR, NOM_AN FROM F101_BV WHERE IDENTIFIANT='" + idPartie + "'")
            #V�rifier si aucun r�sultat
            if not resultat:
                #D�finir la commande SQL pour ins�rer l'identifiant de partie
                sql = "INSERT INTO F101_BV VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, '" + idPartie + "', '" + nomFrancais + "', '" + nomAnglais + "')"
                #Afficher la commande SQL
                arcpy.AddMessage(sql)
                #Ajouter l'identifiant de partie
                oSib.execute(sql)
            #Si l'identifiant de partie existe d�j�
            else:
                #Afficher l'identifiant de partie
                arcpy.AddWarning("Identifiant de partie d�j� pr�sent : " + resultat[0][0] + " " + resultat[0][1] + " " + resultat[0][2])
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Afficher le message de fermeture de la connexion SIB
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        #Fermeture de la connexion de la BD SIB  
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
        identifiant      = ""
        noDebut          = 1
        noFin            = 1
        nomFrancais      = ""
        nomAnglais       = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            identifiant = sys.argv[2].upper().split(":")[0]

        if len(sys.argv) > 3:
            noDebut = int(sys.argv[3])

        if len(sys.argv) > 4:
            noFin = int(sys.argv[4])

        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                nomFrancais = sys.argv[5]

        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                nomAnglais = sys.argv[6]
        
        # D�finir l'objet d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassinPartie = AjouterIdentifiantBassinPartie()
        
        #Valider les param�tres obligatoires
        oAjouterIdentifiantBassinPartie.validerParamObligatoire(env, identifiant, noDebut, noFin)
        
        # Ex�cuter le traitement d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassinPartie.executer(env, identifiant, noDebut, noFin, nomFrancais, nomAnglais)
    
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