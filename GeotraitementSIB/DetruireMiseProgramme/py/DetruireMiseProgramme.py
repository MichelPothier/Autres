#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : D�truireMiseProgramme.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet de d�truire une liste de num�ros de de mise au programme qui ne sont pas dans l'�tat termin�.

    Les entr�es qui correspondent � la liste des num�ros de mise au programme pass� en pram�tre seront d�truit dans les tables suivantes :
    F502_PS, F502_NC, F502_LE, F503_TR, F602_ET et F603_IT
    
    Param�tres d'entr�e:
    --------------------
    env         : Type d'environnement.
    listeNoMap  : Liste des num�ros de mise au programme en production � d�truire.
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Cet outil fait appel au service "P0502_PR.pu_detruire_mise_au_programme" pour traiter la destruction du no_map.
        Les bases de donn�es doivent �tre op�rationnelles. 

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

# Importation des modules priv�s
import CompteSib

#*******************************************************************************************
class DetruireMiseProgramme(object):
#*******************************************************************************************
    """
    Permet de d�truire une liste de num�ros de de mise au programme qui ne sont pas dans l'�tat termin�.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de destruction d'une liste de num�ros de mise au programme.
        
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
    def validerParamObligatoire(self, listeNoMap):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        ListeNoMap  : Liste des num�ros de mise au programme � d�truire.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire.
        
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        #V�rifier la pr�sence du param�tre
        if (len(listeNoMap) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'listeNoMap')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNoMap):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de destruction des num�ros de mise au programme.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        listeNoMap      : Liste des num�ro de mise au programme � d�truire.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerBd       : Nom de l'usager de la Base de donn�es.
        sUsagerSib      : Nom de l'usager SIB.
        noMap           : Num�ro de mise au programme � d�truire.
        table           : Table SIB � traiter.
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
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS','PLAN'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        #Afficher le traitement de destruction des num�ros de mise au programme
        arcpy.AddMessage("- Ex�cution de la destruction des num�ros de mise au programme")
        arcpy.AddMessage("  Liste des NO_MAP : %s" % listeNoMap)
        listeNoMap = listeNoMap.replace("'","")
        listeNoMap = listeNoMap.split(",")
        
        #Traiter tous les noMap sp�cifi�s        
        for noMap in listeNoMap:
            #Extraire le noMap (la premi�re valeur) seulement
            noMap = noMap.split(' ')[0]
            
            #Traiter la destruction du NO_MAP
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Destruction du NO_MAP : %s" % noMap)
            code_retour = oSib.callServiceSib("P0502_PR.pu_detruire_mise_au_programme", cx_Oracle.STRING, [sUsagerSib, noMap], True)
            
            #V�rifier si le service a retourner une erreur
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
                #Ex�cuter la commande
                resultat = oSib.requeteSib('SELECT' + commande)
                #Traiter toutes les lignes
                for ligne in resultat:
                    #Initialiser les donn�es
                    data = ''
                    #Traiter toutes les valeurs
                    for valeur in ligne:
                        #Costruire les donn�es
                        data = data + str(valeur) + ','
                    #Afficher l'information de la ligne
                    arcpy.AddMessage('  (' + data[:-1] + ')')
                    
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
        env = "SIB_PRO"
        listeNoMap = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            listeNoMap = sys.argv[2].replace(";",",")
        
        # D�finir l'objet de destruction des num�ros de mise au programme.
        oDetruireMiseProgramme = DetruireMiseProgramme()
        
        #Valider les param�tres obligatoires
        oDetruireMiseProgramme.validerParamObligatoire(listeNoMap)
        
        # Ex�cuter le traitement de destruction des num�ros de mise au programme.
        oDetruireMiseProgramme.executer(env, listeNoMap)
    
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