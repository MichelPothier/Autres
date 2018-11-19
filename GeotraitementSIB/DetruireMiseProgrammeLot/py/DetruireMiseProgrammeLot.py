#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DétruireMiseAuProgrammeLot.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet de détruire tous les numéros de mise au programme d'une liste de numéros de lot dans SIB.
    Les numéros de lot et de mise au programme ne doivent pas être à l'état terminé.

    Les entrés qui correspondent aux numéros de lot passés en paramètre seront détruit dans les tables suivantes :
    F601_LO, F601_GR et F606_GE
    
    Les entrées des numéros de mise au programme qui appartiennent aux numéros de lot passés en pramètre seront détruit dans les tables suivantes :
    F502_PS, F502_NC, F502_LE, F503_TR, F602_ET et F603_IT
    
    Paramètres d'entrée:
    --------------------
    environnement       Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                        Défaut = SIB_PRO
    listeNoLot          Liste des numéros de lot en production à détruire.
                        Défaut = ''
    detruireLot         Indique si on doit détruire les lots [True/False].
                        Défaut = True
    continuer           Indique si on doit continuer même si une erreur survient lors de la destruction d'un noMap
                        Défaut = False
    
    Paramètres de sortie:
    ---------------------
        Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Cet outil fait appel au service "P0502_PR.pu_detruire_mise_au_programme" pour traiter la destruction d'un no_map.
        Les bases de données doivent être opérationnelles. 

    Usage:
        DetruireMiseAuProgrammeLot.py environnement listeNoLot detruireLot

    Exemple:
        DetruireMiseAuProgrammeLot.py SIB_PRO 170684 True

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireMiseProgrammeLot.py 2142 2017-10-19 15:42:40Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés
import CompteSib

#*******************************************************************************************
class DetruireMiseProgrammeLot(object):
#*******************************************************************************************
    """
    Permet de détruire tous les numéros de mise au programme d'une liste de numéros de lot dans SIB
    qui ne sont pas dans l'état terminé.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de destruction des numéros de mise au programme d'une liste de lot.
        
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
    def validerParamObligatoire(self, listeNoLot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        ListeNoLot              Liste des numéros de lot à détruire et leurs numéros de mise au programme correspondants.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        #Vérifier la présence du paramètre
        if (len(listeNoLot) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'listeNoLot')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNoLot, detruireLot, continuer):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de destruction des numéros de mise au programme.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        listeNoLot      : Liste des numéro de lot pour lesquels on veut détruire tous les numéros de mise au programme.
        detruireLot     : Indique si on doit détruire les lots.
        continuer       : Indique si on doit continuer même si une erreur survient lors de la destruction d'un noMap
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
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
        arcpy.AddMessage("- Exécution de la destruction des NO_MAP pour les NO_LOT")
        arcpy.AddMessage("  Liste des NO_LOT : %s" % listeNoLot)
        listeNoLot = listeNoLot.replace("'","")
        listeNoLot = listeNoLot.split(",")
        
        #Traiter tous les NO_LOT spécifiés        
        for noLot in listeNoLot:
            #Extraire le noLot (la première valeur) seulement
            noLot = noLot.split(' ')[0]
            
            #Extraire la liste des NO_MAP pour le lot traité
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Extraire la liste des NO_MAP pour le LOT : %s" % noLot)
            listeNoMap = oSib.requeteSib("SELECT NO_MAP FROM F503_TR WHERE NO_LOT = '" + noLot + "'")
            arcpy.AddMessage("  Liste des NO_MAP : %s" % str(listeNoMap))
            
            #Traiter tous les NO_MAP du lot traité
            for noMap in listeNoMap:
                #Extraire le NoMap
                noMap = str(noMap[0])
                
                #Traiter la destruction du NO_MAP
                arcpy.AddMessage("- Destruction du NO_MAP : %s" % noMap)
                code_retour = oSib.callServiceSib("P0502_PR.pu_detruire_mise_au_programme", cx_Oracle.STRING, [sUsagerSib, noMap], True)
                
                #Vérifier si le service a retourner une erreur
                if code_retour <> None:
                    #Extraire le message d'erreur
                    message = oSib.cursor.callfunc("P0008_ERR.pu_extraire_message", cx_Oracle.STRING, [code_retour, 1, 'F'])
                    #Vérifier si on doit continuer même si une erreur survient
                    if continuer:
                        #Afficher un avertissement de noMap non détruit
                        arcpy.AddWarning("  Numéro de mise au programme non détruit : " + noMap)
                    else:
                        #Lancer une exception
                        raise Exception(message)
                
                #Si aucune erreur
                else:
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

            #Vérifier si on doit détruire le lot
            if detruireLot:
                #Traiter la destruction du NO_LOT et de ses NO_MAP
                arcpy.AddMessage("- Destruction du NO_LOT : %s" % noLot)
                code_retour = oSib.callServiceSib("P0502_PR.pu_detruire_MAP_lot", cx_Oracle.STRING, [sUsagerSib, noLot], True)
                
                #Vérifier si le service a retourné une erreur
                if code_retour <> None:
                    #Extraire le message d'erreur
                    message = oSib.cursor.callfunc("P0008_ERR.pu_extraire_message", cx_Oracle.STRING, [code_retour, 1, 'F'])
                    #Vérifier si on doit continuer même si une erreur survient
                    if continuer:
                        #Afficher un avertissement de noLot non détruit
                        arcpy.AddWarning("  Numéro de lot non détruit : " + noLot)
                    else:
                        #Lancer une exception
                        raise Exception(message)
                    
                #Si pas d'erreur
                else:
                    #Afficher l'information de toutes les tables en lien avec le NO_LOT
                    for table in ['F601_LO','F601_GR','F606_GE']:
                        #Construire la commande
                        commande = " * FROM " + table + " WHERE NO_LOT = '" + noLot + "'"
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
        listeNoLot = ""
        detruireLot = True
        continuer = False
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeNoLot = sys.argv[2].replace(";",",")
        
        if len(sys.argv) > 3:
            if sys.argv[3] <> '#':
                detruireLot = sys.argv[3].upper()=='TRUE'
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> '#':
                continuer = sys.argv[4].upper()=='TRUE'
        
        # Définir l'objet de destruction de tous les numéros de mise au programme d'une liste de lot.
        oDetruireMiseProgrammeLot = DetruireMiseProgrammeLot()
        
        #Valider les paramètres obligatoires
        oDetruireMiseProgrammeLot.validerParamObligatoire(listeNoLot)
        
        # Exécuter le traitement de destruction de tous les numéros de mise au programme d'une liste de lot.
        oDetruireMiseProgrammeLot.executer(env, listeNoLot, detruireLot, continuer)
    
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