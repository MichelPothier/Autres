#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : DétruireEntiteNormeProduction.py
# Auteur    : Michel Pothier
# Date      : 08 août 2016

"""
    Application qui permet de détruire l'information relative aux codes d'élément topographique (entité de production) pour un numéro de normes de la BDG.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    normes              OB      Normes de la BDG.
                                défaut = 4.2.2
    listeCodeElem       OP      Liste des codes de l'élément topographique.
                                défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DétruireEntiteNormeProduction.py env normes listeCodeElem

    Exemple:
        DétruireEntiteNormeProduction.py SIB_PRO 4.2.2 "1000000;10000001"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEntiteNormeProduction.py 2113 2016-09-13 18:29:52Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireEntiteNormeProduction:
#*******************************************************************************************
    """
    Classe qui permet de détruire l'information relative aux codes d'élément topographique
    (entité de production) pour un numéro de normes de la BDG.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de mise au programme.
        
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
    def validerParamObligatoire(self, env, normes, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        normes              : Normes de la BDG.
        listeCodeElem       : Liste des codes de l'élément topographique.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(normes) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'normes')
        
        if (len(listeCodeElem) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'listeCodeElem')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, normes, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire l'information relative aux codes d'élément topographique
        (entité de production) pour un numéro de normes de la BDG.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        normes              : Normes de la BDG.
        listeCodeElem       : Liste des codes de l'élément topographique.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #---------------------------------------------------------------------
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #---------------------------------------------------------------------
        #Extraire les codes d'éléments topographiques existants
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire les codes d'éléments topographiques existants ...")
        #Extraire les codes d'éléments topographiques existants
        sql = "SELECT CD_ELEM_TOPO FROM F132_EN WHERE NORMES='" + normes + "'" 
        #Afficher la commande sql
        arcpy.AddMessage(sql)
        #Exécuter la commande sql
        resultat = self.Sib.requeteSib(sql)
        #Initialiser la liste
        listeCodeExistant =[]
        #Traiter tous les codes
        for code in resultat:
            #Ajouter le code à la liste
            listeCodeExistant.append(code[0])
        
        #---------------------------------------------------------------------
        #Détruire l'information relative au code d'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Détruire l'information relative au code d'élément topographique")
        #Traiter tous les codes d'élément topographique
        for codeDesc in listeCodeElem.split(","):
            #Définir le code d'élément sans description
            codeElem = codeDesc.split(" ")[0]
            
            #Vérifier si le code est existant
            if codeElem in listeCodeExistant:
                #Extraire les codes d'éléments topographiques existants
                sql = "SELECT * FROM F132_EN WHERE NORMES='" + normes + "' AND CD_ELEM_TOPO='" + codeElem + "'"
                #Exécuter la commande sql
                resultat = self.Sib.requeteSib(sql)
                #Définir la commande pour DÉTRUIRE le code d'élément topographique
                sql = "DELETE F132_EN WHERE CD_ELEM_TOPO='" + codeElem + "' AND NORMES='" + normes + "'"
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Afficher la valeur à détruire
                arcpy.AddWarning(str(resultat[0]))
                #Exécuter la commande
                self.Sib.execute(sql)
            
            #Si le code est inexistant
            else:
                #Afficher la commande
                arcpy.AddWarning("ATTENTION : Le code d'élément topographique est absent : " + codeDesc)
        
        #---------------------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB   
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env                 = "SIB_PRO"
        normes              = "4.0.2"
        listeCodeElem       = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            normes = sys.argv[2]
         
        if len(sys.argv) > 3:
            listeCodeElem = sys.argv[3].replace("'","").replace(";",",")
        
        #Définir l'objet pour détruire l'information relative aux codes d'élément topographique (entité de production) pour un numéro de normes de la BDG.
        oDetruireEntiteNormeProduction = DetruireEntiteNormeProduction()
        
        #Valider les paramètres obligatoires
        oDetruireEntiteNormeProduction.validerParamObligatoire(env, normes, listeCodeElem)
        
        #Exécuter le traitement pour détruire l'information relative aux codes d'élément topographique (entité de production) pour un numéro de normes de la BDG.
        oDetruireEntiteNormeProduction.executer(env, normes, listeCodeElem)
    
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