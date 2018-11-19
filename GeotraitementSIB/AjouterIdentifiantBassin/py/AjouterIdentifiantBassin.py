#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AjouterIdentifiantBassin.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet d'ajouter un identifiant de bassin de base ou plusieurs parties de bassin.

    Lorsqu'un identifiant de base est traité, il est ajouté à la liste des identifiants de bassin avec son nom français et anglais.

    Lorsqu'un identifiant de partie est traité, tous les identifiants de partie compris entre 1 et le dernier chiffre son ajouté avec le nom français et anglais
    de l'identifiant de base en y ajoutant le texte " (partie)" pour le nom français et le texte " (part of)" en anglais.
    
    Paramètres d'entrée:
    --------------------
    environnement      OB     Type d'environnement [TST/PRO]
                              défaut = TST
    identifiant        OB     Identifiant de bassin traité.
                              Il peut s'agir d'un identifiant de base (se termine par un 000) ou de partie (ne se termine pas par un 000)
                              défaut = ""
    nomFrancais        OP     Nom francais de l'identifiant.
                              Attention : Obligatoire s'il s'agit d'un identifiant de base.
                              défaut = ""
    nomAnglais         OP     Nom anglais de l'identifiant.
                              Attention : Obligatoire s'il s'agit d'un identifiant de base.
                              défaut = ""
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel  : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Cet outil fait appel au service "P0201_MEP.pu_ajouter_identifiant_bassin" pour traiter l'ajout d'identifiant.
        Les bases de données doivent être opérationnelles. 

    Usage:
        AjouterIdentifiantBassin.py environnement identifiant [nomFrancais] [nomAnglais]

    Exemple:
        AjouterIdentifiantBassin.py TST 1234000 "nom francais" "nom anglais"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AjouterIdentifiantBassin.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés
import CompteSib

#*******************************************************************************************
class AjouterIdentifiantBassin(object):
#*******************************************************************************************
    """
    Permet d'ajouter un identifiant de bassin de base ou plusieurs parties de bassin.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        
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
    def validerParamObligatoire(self, identifiant, nomFrancais, nomAnglais):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        identifiant             type de produit associé au lot
        nomFrancais             Nom francais de l'identifiant.
        nomAnglais              Nom anglais de l'identifiant.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        #Vérifier la présence du paramètre identifiant
        if (len(identifiant) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'identifiant')

        #Vérifier la longueur du paramètre identifiant
        if (len(identifiant) <> 7):
            raise Exception("- La longueur de l'identifiant doit être de 7: %s" %'identifiant')
        
        #Vérifier si c'est un bassin de base
        if (identifiant[4:7] == "000"):
            #Vérifier la présence du paramètre nomFrancais
            if (len(nomFrancais) == 0):
                raise Exception("- Paramètre obligatoire manquant: %s" %'nomFrancais')

            #Vérifier la présence du paramètre nomAnglais
            if (len(nomAnglais) == 0):
                raise Exception("- Paramètre obligatoire manquant: %s" %'nomAnglais')

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, identifiant, nomFrancais, nomAnglais):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        identifiant     : Identifiant de bassin traité.
                          Il peut s'agir d'un identifiant de base (se termine par un 000) ou de partie (ne se termine pas par un 000)
        nomFrancais     : Nom francais de l'identifiant.
                          Attention : Obligatoire s'il s'agit d'un identifiant de base.
        nomAnglais      : Nom anglais de l'identifiant.
                          Attention : Obligatoire s'il s'agit d'un identifiant de base.
        
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
        
        #Traiter l'ajout de l'identifiant de bassin
        arcpy.AddMessage("- Exécution de l'ajout de l'identifiant de bassin")
        code_retour = oSib.callServiceSib("P0201_MEP.pu_ajouter_identifiant_bassin", cx_Oracle.STRING, [sUsagerSib, identifiant, nomFrancais, nomAnglais], True)
        arcpy.AddMessage("  Code d'erreur = %s" % str(code_retour) )

        #Vérifier si le service a retourner une erreur
        if code_retour <> None:
            #Extraire le nombre de message
            nbMessSib = oSib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [code_retour])
            count = 1
            #Extraire tous les messages
            message = []
            while nbMessSib >= count:
                messageSib = oSib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [code_retour, count, 'F'])
                message.append(messageSib)
                count += 1
            #Retourner le message d'erreur
            raise Exception(message)
        
        #Requête pour vérifier les identifiants traités
        arcpy.AddMessage("- Identifiants des bassins présents dans SIB")
        resultat = oSib.requeteSib("SELECT IDENTIFIANT, NOM_FR, NOM_AN FROM F101_BV WHERE IDENTIFIANT LIKE '" + identifiant[:4] + "%'")
        #Extraire tous les identifiants présents
        for item in resultat:
            #Afficher le résultat de la requête
            arcpy.AddMessage("  " + str(item)[1:-1])

        # Sortie normale pour une exécution réussie
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB   

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
        nomFrancais      = ""
        nomAnglais       = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            identifiant = sys.argv[2].upper()

        if len(sys.argv) > 3:
            if sys.argv[3] <> "#":
                nomFrancais = sys.argv[3]

        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                nomAnglais = sys.argv[4]
        
        # Définir l'objet d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassin = AjouterIdentifiantBassin()
        
        #Valider les paramètres obligatoires
        oAjouterIdentifiantBassin.validerParamObligatoire(identifiant, nomFrancais, nomAnglais)
        
        # Exécuter le traitement d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassin.executer(env, identifiant, nomFrancais, nomAnglais)
    
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