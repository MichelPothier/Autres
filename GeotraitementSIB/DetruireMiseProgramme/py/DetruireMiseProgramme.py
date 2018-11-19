#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : DétruireMiseProgramme.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet de détruire une liste de numéros de de mise au programme qui ne sont pas dans l'état terminé.

    Les entrées qui correspondent à la liste des numéros de mise au programme passé en pramètre seront détruit dans les tables suivantes :
    F502_PS, F502_NC, F502_LE, F503_TR, F602_ET et F603_IT
    
    Paramètres d'entrée:
    --------------------
    env         : Type d'environnement.
    listeNoMap  : Liste des numéros de mise au programme en production à détruire.
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Cet outil fait appel au service "P0502_PR.pu_detruire_mise_au_programme" pour traiter la destruction du no_map.
        Les bases de données doivent être opérationnelles. 

    Usage:
        DetruireMiseProgramme.py env listeNoMap

    Exemple:
        DetruireMiseProgramme.py SIB_PRO 849291,849292

"""
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireMiseProgramme.py 2141 2017-10-19 15:42:25Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés
import CompteSib

#*******************************************************************************************
class DetruireMiseProgramme(object):
#*******************************************************************************************
    """
    Permet de détruire une liste de numéros de de mise au programme qui ne sont pas dans l'état terminé.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de destruction d'une liste de numéros de mise au programme.
        
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
    def validerParamObligatoire(self, listeNoMap):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        ListeNoMap  : Liste des numéros de mise au programme à détruire.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire.
        
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        #Vérifier la présence du paramètre
        if (len(listeNoMap) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'listeNoMap')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNoMap):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de destruction des numéros de mise au programme.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        listeNoMap      : Liste des numéro de mise au programme à détruire.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerBd       : Nom de l'usager de la Base de données.
        sUsagerSib      : Nom de l'usager SIB.
        noMap           : Numéro de mise au programme à détruire.
        table           : Table SIB à traiter.
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
        
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS','PLAN'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")
        
        #Afficher le traitement de destruction des numéros de mise au programme
        arcpy.AddMessage("- Exécution de la destruction des numéros de mise au programme")
        arcpy.AddMessage("  Liste des NO_MAP : %s" % listeNoMap)
        listeNoMap = listeNoMap.replace("'","")
        listeNoMap = listeNoMap.split(",")
        
        #Traiter tous les noMap spécifiés        
        for noMap in listeNoMap:
            #Extraire le noMap (la première valeur) seulement
            noMap = noMap.split(' ')[0]
            
            #Traiter la destruction du NO_MAP
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Destruction du NO_MAP : %s" % noMap)
            code_retour = oSib.callServiceSib("P0502_PR.pu_detruire_mise_au_programme", cx_Oracle.STRING, [sUsagerSib, noMap], True)
            
            #Vérifier si le service a retourner une erreur
            if code_retour <> None:
                #Extraire le message d'erreur
                message = oSib.cursor.callfunc("P0008_ERR.pu_extraire_message", cx_Oracle.STRING, [code_retour, 1, 'F'])
                #Lancer une exception
                raise Exception(message)
            
            #Afficher l'information de toutes les tables en lien avec la mise au programme
            for table in ['F502_PS','F502_NC','F502_LE','F503_TR','F602_ET','F603_IT']:
                #Construire la commande
                commande = " * FROM " + table + " WHERE NO_MAP = " + noMap
                #Afficher la commande
                arcpy.AddMessage('  DELETE' + commande)
                #Exécuter la commande
                resultat = oSib.requeteSib('SELECT' + commande)
                #Traiter toutes les lignes
                for ligne in resultat:
                    #Initialiser les données
                    data = ''
                    #Traiter toutes les valeurs
                    for valeur in ligne:
                        #Costruire les données
                        data = data + str(valeur) + ','
                    #Afficher l'information de la ligne
                    arcpy.AddMessage('  (' + data[:-1] + ')')
                    
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
        env = "SIB_PRO"
        listeNoMap = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            listeNoMap = sys.argv[2].replace(";",",")
        
        # Définir l'objet de destruction des numéros de mise au programme.
        oDetruireMiseProgramme = DetruireMiseProgramme()
        
        #Valider les paramètres obligatoires
        oDetruireMiseProgramme.validerParamObligatoire(listeNoMap)
        
        # Exécuter le traitement de destruction des numéros de mise au programme.
        oDetruireMiseProgramme.executer(env, listeNoMap)
    
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