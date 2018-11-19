#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AjouterIdentifiantBassinPartie.py
# Auteur    : Michel Pothier
# Date      : 07 mars 2018

"""
    Application qui permet d'ajouter un ou plusieurs identifiants de partie de bassin à partir d'un identifiant de base existant.

    Tous les identifiants de partie compris entre le numéro de début et le numéro de fin de partie inclusivement sont ajoutés
    avec le nom français et anglais de l'identifiant de base en y ajoutant le texte " (partie)" pour le nom français
    et le texte " (part of)" en anglais.
    
    Paramètres d'entrée:
    --------------------
    environnement      OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV]
                              défaut = "SIB_PRO"
    identifiant        OB     Identifiant de bassin de base.
                              Un identifiant de base (se termine par un 000).
                              défaut = ""
    noDebut            OB     Numéro de début de l'identifiant de partie à ajouter.
                              Défaut=
    noFin              OB     Numéro de fin de l'identifiant de partie à ajouter.
                              Défaut=
    nomFrancais        OP     Nom francais de l'identifiant de partie.
                              défaut = nomFrancais + " (partie)"
    nomAnglais         OP     Nom anglais de l'identifiant de partie.
                              défaut = nomAnglais + " (part of)"
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel  : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 

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

# Importation des modules privés
import CompteSib

#*******************************************************************************************
class AjouterIdentifiantBassinPartie(object):
#*******************************************************************************************
    """
    Permet d'ajouter un ou plusieurs identifiants de partie de bassin à partir d'un identifiant de base existant.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour ajouter un ou plusieurs identifiants de partie de bassin à partir d'un identifiant de base existant.
        
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
    def validerParamObligatoire(self, env, identifiant, noDebut, noFin):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.
        identifiant     : Identifiant de bassin traité.
        noDebut         : Numéro de début de l'identifiant de partie à ajouter.
        noFin           : Numéro de fin de l'identifiant de partie à ajouter.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        #Vérifier la présence du paramètre identifiant
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')

        #Vérifier la présence du paramètre identifiant
        if (len(identifiant) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'identifiant')

        #Vérifier la longueur du paramètre identifiant
        if (len(identifiant) <> 7):
            raise Exception("- La longueur de l'identifiant doit être de 7: %s" %'identifiant')

        #Vérifier si le numéro de début est valide
        if (noDebut == 0):
            raise Exception("- Le numéro de début doit être supérieur à 0")

        #Vérifier si le numéro de début est valide
        if (noDebut > noFin):
            raise Exception("- Le numéro de début doit être inférieur ou égale à de celui de la fin")

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, identifiant, noDebut, noFin, nomFrancais, nomAnglais):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour ajouter un ou plusieurs identifiants de partie de bassin à partir d'un identifiant de base existant.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        identifiant     : Identifiant de bassin traité.
        noDebut         : Numéro de début de l'identifiant de partie à ajouter.
        noFin           : Numéro de fin de l'identifiant de partie à ajouter.
        nomFrancais     : Nom francais de l'identifiant de partie.
        nomAnglais      : Nom anglais de l'identifiant de partie.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        resultat        : Résultat de la requête.
        message         : Message d'erreur.
        code_retour     : Code de retour d'un service SIB.
        
        Retour:
        -------
        Exception s'il y a une erreur.
        
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'PLAN'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'PLAN'")
        
        #Requête pour vérifier les identifiants traités
        arcpy.AddMessage("- Valider l'identifiant de bassin de base : " + identifiant)
        resultat = oSib.requeteSib("SELECT IDENTIFIANT, NOM_FR, NOM_AN FROM F101_BV WHERE IDENTIFIANT='" + identifiant + "'")
        #Vérifier si aucun résultat
        if not resultat:
           raise Exception("- L'identifiant de de bassin de base est invalide : " + identifiant)
        
        #Valider le numéro de début et de fin
        arcpy.AddMessage("- Valider le numéro de début et de fin ...")
        #Valider le numéro d'identifiant de partie de début
        if noDebut == 0:
           raise Exception("- Le numéro de début doit être supérieure à zéro")
        #Valider le numéro d'identifiant de partie de début
        if noDebut > noFin:
           raise Exception("- Le numéro de début doit être supérieure ou égale au numéro de fin")
        #Valider le numéro d'identifiant de partie de fin
        if noFin > 999:
           raise Exception("- Le numéro de fin doit être inférieure ou égale à 999")
        
        #Vérifier si le nom français est spécifié
        if len(nomFrancais) == 0:
            #Définir le nom français par défaut
            nomFrancais = resultat[0][1] + " (partie)"

        #Vérifier si le nom français est spécifié
        if len(nomAnglais) == 0:
            #Définir le nom anglais par défaut
            nomAnglais = resultat[0][2] + " (part of)"
        
        #Définir le début de l'identifiant de partie
        id = identifiant[0:4]
        
        #Valider le numéro de début et de fin
        arcpy.AddMessage("- Ajouter les identifiants de partie ...")
        #Traiter tous les identifiant de bassin de partie
        for i in range(noDebut,noFin+1):
            #Définir le numéro de partie
            idPartie = id + str(i).rjust(3,'0')
            #Définir la requête pour vérifier si l'identifiant de partie existe
            resultat = oSib.requeteSib("SELECT IDENTIFIANT, NOM_FR, NOM_AN FROM F101_BV WHERE IDENTIFIANT='" + idPartie + "'")
            #Vérifier si aucun résultat
            if not resultat:
                #Définir la commande SQL pour insérer l'identifiant de partie
                sql = "INSERT INTO F101_BV VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, '" + idPartie + "', '" + nomFrancais + "', '" + nomAnglais + "')"
                #Afficher la commande SQL
                arcpy.AddMessage(sql)
                #Ajouter l'identifiant de partie
                oSib.execute(sql)
            #Si l'identifiant de partie existe déjà
            else:
                #Afficher l'identifiant de partie
                arcpy.AddWarning("Identifiant de partie déjà présent : " + resultat[0][0] + " " + resultat[0][1] + " " + resultat[0][2])
        
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env              = "SIB_PRO"
        identifiant      = ""
        noDebut          = 1
        noFin            = 1
        nomFrancais      = ""
        nomAnglais       = ""

        #extraction des paramètres d'exécution
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
        
        # Définir l'objet d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassinPartie = AjouterIdentifiantBassinPartie()
        
        #Valider les paramètres obligatoires
        oAjouterIdentifiantBassinPartie.validerParamObligatoire(env, identifiant, noDebut, noFin)
        
        # Exécuter le traitement d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassinPartie.executer(env, identifiant, noDebut, noFin, nomFrancais, nomAnglais)
    
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