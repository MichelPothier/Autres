#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : D�truireMiseAuProgrammeLot.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet de d�truire tous les num�ros de mise au programme d'une liste de num�ros de lot dans SIB.
    Les num�ros de lot et de mise au programme ne doivent pas �tre � l'�tat termin�.

    Les entr�s qui correspondent aux num�ros de lot pass�s en param�tre seront d�truit dans les tables suivantes :
    F601_LO, F601_GR et F606_GE
    
    Les entr�es des num�ros de mise au programme qui appartiennent aux num�ros de lot pass�s en pram�tre seront d�truit dans les tables suivantes :
    F502_PS, F502_NC, F502_LE, F503_TR, F602_ET et F603_IT
    
    Param�tres d'entr�e:
    --------------------
    environnement       Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                        D�faut = SIB_PRO
    listeNoLot          Liste des num�ros de lot en production � d�truire.
                        D�faut = ''
    detruireLot         Indique si on doit d�truire les lots [True/False].
                        D�faut = True
    continuer           Indique si on doit continuer m�me si une erreur survient lors de la destruction d'un noMap
                        D�faut = False
    
    Param�tres de sortie:
    ---------------------
        Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Cet outil fait appel au service "P0502_PR.pu_detruire_mise_au_programme" pour traiter la destruction d'un no_map.
        Les bases de donn�es doivent �tre op�rationnelles. 

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

# Importation des modules priv�s
import CompteSib

#*******************************************************************************************
class DetruireMiseProgrammeLot(object):
#*******************************************************************************************
    """
    Permet de d�truire tous les num�ros de mise au programme d'une liste de num�ros de lot dans SIB
    qui ne sont pas dans l'�tat termin�.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de destruction des num�ros de mise au programme d'une liste de lot.
        
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
    def validerParamObligatoire(self, listeNoLot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        ListeNoLot              Liste des num�ros de lot � d�truire et leurs num�ros de mise au programme correspondants.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        #V�rifier la pr�sence du param�tre
        if (len(listeNoLot) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'listeNoLot')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNoLot, detruireLot, continuer):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de destruction des num�ros de mise au programme.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        listeNoLot      : Liste des num�ro de lot pour lesquels on veut d�truire tous les num�ros de mise au programme.
        detruireLot     : Indique si on doit d�truire les lots.
        continuer       : Indique si on doit continuer m�me si une erreur survient lors de la destruction d'un noMap
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
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
        arcpy.AddMessage("- Ex�cution de la destruction des NO_MAP pour les NO_LOT")
        arcpy.AddMessage("  Liste des NO_LOT : %s" % listeNoLot)
        listeNoLot = listeNoLot.replace("'","")
        listeNoLot = listeNoLot.split(",")
        
        #Traiter tous les NO_LOT sp�cifi�s        
        for noLot in listeNoLot:
            #Extraire le noLot (la premi�re valeur) seulement
            noLot = noLot.split(' ')[0]
            
            #Extraire la liste des NO_MAP pour le lot trait�
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Extraire la liste des NO_MAP pour le LOT : %s" % noLot)
            listeNoMap = oSib.requeteSib("SELECT NO_MAP FROM F503_TR WHERE NO_LOT = '" + noLot + "'")
            arcpy.AddMessage("  Liste des NO_MAP : %s" % str(listeNoMap))
            
            #Traiter tous les NO_MAP du lot trait�
            for noMap in listeNoMap:
                #Extraire le NoMap
                noMap = str(noMap[0])
                
                #Traiter la destruction du NO_MAP
                arcpy.AddMessage("- Destruction du NO_MAP : %s" % noMap)
                code_retour = oSib.callServiceSib("P0502_PR.pu_detruire_mise_au_programme", cx_Oracle.STRING, [sUsagerSib, noMap], True)
                
                #V�rifier si le service a retourner une erreur
                if code_retour <> None:
                    #Extraire le message d'erreur
                    message = oSib.cursor.callfunc("P0008_ERR.pu_extraire_message", cx_Oracle.STRING, [code_retour, 1, 'F'])
                    #V�rifier si on doit continuer m�me si une erreur survient
                    if continuer:
                        #Afficher un avertissement de noMap non d�truit
                        arcpy.AddWarning("  Num�ro de mise au programme non d�truit : " + noMap)
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

            #V�rifier si on doit d�truire le lot
            if detruireLot:
                #Traiter la destruction du NO_LOT et de ses NO_MAP
                arcpy.AddMessage("- Destruction du NO_LOT : %s" % noLot)
                code_retour = oSib.callServiceSib("P0502_PR.pu_detruire_MAP_lot", cx_Oracle.STRING, [sUsagerSib, noLot], True)
                
                #V�rifier si le service a retourn� une erreur
                if code_retour <> None:
                    #Extraire le message d'erreur
                    message = oSib.cursor.callfunc("P0008_ERR.pu_extraire_message", cx_Oracle.STRING, [code_retour, 1, 'F'])
                    #V�rifier si on doit continuer m�me si une erreur survient
                    if continuer:
                        #Afficher un avertissement de noLot non d�truit
                        arcpy.AddWarning("  Num�ro de lot non d�truit : " + noLot)
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
        listeNoLot = ""
        detruireLot = True
        continuer = False
        
        #extraction des param�tres d'ex�cution
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
        
        # D�finir l'objet de destruction de tous les num�ros de mise au programme d'une liste de lot.
        oDetruireMiseProgrammeLot = DetruireMiseProgrammeLot()
        
        #Valider les param�tres obligatoires
        oDetruireMiseProgrammeLot.validerParamObligatoire(listeNoLot)
        
        # Ex�cuter le traitement de destruction de tous les num�ros de mise au programme d'une liste de lot.
        oDetruireMiseProgrammeLot.executer(env, listeNoLot, detruireLot, continuer)
    
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