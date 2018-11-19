#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : AjouterIdentifiantBassin.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet d'ajouter un identifiant de bassin de base ou plusieurs parties de bassin.

    Lorsqu'un identifiant de base est trait�, il est ajout� � la liste des identifiants de bassin avec son nom fran�ais et anglais.

    Lorsqu'un identifiant de partie est trait�, tous les identifiants de partie compris entre 1 et le dernier chiffre son ajout� avec le nom fran�ais et anglais
    de l'identifiant de base en y ajoutant le texte " (partie)" pour le nom fran�ais et le texte " (part of)" en anglais.
    
    Param�tres d'entr�e:
    --------------------
    environnement      OB     Type d'environnement [TST/PRO]
                              d�faut = TST
    identifiant        OB     Identifiant de bassin trait�.
                              Il peut s'agir d'un identifiant de base (se termine par un 000) ou de partie (ne se termine pas par un 000)
                              d�faut = ""
    nomFrancais        OP     Nom francais de l'identifiant.
                              Attention : Obligatoire s'il s'agit d'un identifiant de base.
                              d�faut = ""
    nomAnglais         OP     Nom anglais de l'identifiant.
                              Attention : Obligatoire s'il s'agit d'un identifiant de base.
                              d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Cet outil fait appel au service "P0201_MEP.pu_ajouter_identifiant_bassin" pour traiter l'ajout d'identifiant.
        Les bases de donn�es doivent �tre op�rationnelles. 

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

# Importation des modules priv�s
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
    def validerParamObligatoire(self, identifiant, nomFrancais, nomAnglais):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        identifiant             type de produit associ� au lot
        nomFrancais             Nom francais de l'identifiant.
        nomAnglais              Nom anglais de l'identifiant.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        #V�rifier la pr�sence du param�tre identifiant
        if (len(identifiant) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'identifiant')

        #V�rifier la longueur du param�tre identifiant
        if (len(identifiant) <> 7):
            raise Exception("- La longueur de l'identifiant doit �tre de 7: %s" %'identifiant')
        
        #V�rifier si c'est un bassin de base
        if (identifiant[4:7] == "000"):
            #V�rifier la pr�sence du param�tre nomFrancais
            if (len(nomFrancais) == 0):
                raise Exception("- Param�tre obligatoire manquant: %s" %'nomFrancais')

            #V�rifier la pr�sence du param�tre nomAnglais
            if (len(nomAnglais) == 0):
                raise Exception("- Param�tre obligatoire manquant: %s" %'nomAnglais')

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, identifiant, nomFrancais, nomAnglais):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        identifiant     : Identifiant de bassin trait�.
                          Il peut s'agir d'un identifiant de base (se termine par un 000) ou de partie (ne se termine pas par un 000)
        nomFrancais     : Nom francais de l'identifiant.
                          Attention : Obligatoire s'il s'agit d'un identifiant de base.
        nomAnglais      : Nom anglais de l'identifiant.
                          Attention : Obligatoire s'il s'agit d'un identifiant de base.
        
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
        
        #Traiter l'ajout de l'identifiant de bassin
        arcpy.AddMessage("- Ex�cution de l'ajout de l'identifiant de bassin")
        code_retour = oSib.callServiceSib("P0201_MEP.pu_ajouter_identifiant_bassin", cx_Oracle.STRING, [sUsagerSib, identifiant, nomFrancais, nomAnglais], True)
        arcpy.AddMessage("  Code d'erreur = %s" % str(code_retour) )

        #V�rifier si le service a retourner une erreur
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
        
        #Requ�te pour v�rifier les identifiants trait�s
        arcpy.AddMessage("- Identifiants des bassins pr�sents dans SIB")
        resultat = oSib.requeteSib("SELECT IDENTIFIANT, NOM_FR, NOM_AN FROM F101_BV WHERE IDENTIFIANT LIKE '" + identifiant[:4] + "%'")
        #Extraire tous les identifiants pr�sents
        for item in resultat:
            #Afficher le r�sultat de la requ�te
            arcpy.AddMessage("  " + str(item)[1:-1])

        # Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB   

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
        nomFrancais      = ""
        nomAnglais       = ""

        #extraction des param�tres d'ex�cution
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
        
        # D�finir l'objet d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassin = AjouterIdentifiantBassin()
        
        #Valider les param�tres obligatoires
        oAjouterIdentifiantBassin.validerParamObligatoire(identifiant, nomFrancais, nomAnglais)
        
        # Ex�cuter le traitement d'ajout d'un identifiant de bassin de base ou plusieurs parties de bassin.
        oAjouterIdentifiantBassin.executer(env, identifiant, nomFrancais, nomAnglais)
    
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