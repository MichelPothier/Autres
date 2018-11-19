#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : DetruireEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 03 août 2016

"""
    Application qui permet de détruire l'information relative aux codes d'élément topographique (entité de production)
    non utilisés pour toutes les normes de la BDG.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    listeCodeElem       OB      Liste des codes d'élément topographique.
                                défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireEntiteProduction.py env codeElem

    Exemple:
        DetruireEntiteProduction.py SIB_PRO "1000000"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEntiteProduction.py 2086 2016-08-09 17:48:17Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de détruire l'information relative aux codes d'élément topographique
    (entité de production) pour toutes les normes de la BDG.
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
    def validerParamObligatoire(self, env, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        codeElem            : Code de l'élément topographique.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(listeCodeElem) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'listeCodeElem')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire l'information relative aux codes d'élément topographique
        (entité de production) pour toutes les normes de la BDG.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        listeCodeElem       : Liste des codes d'élément topographique.
        
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
        #Traiter tous les codes
        for code in listeCodeElem.split(","):
            #Définir le code d'élément topographique
            codeElem = code.replace("'","").split(" ")[0]
            
            #---------------------------------------------------------------------
            #Valider si le code d'élément topographique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Valider le code d'élément topographique ...")
            sql = "SELECT * FROM F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'AND CD_ELEM_TOPO NOT IN (SELECT DISTINCT CD_ELEM_TOPO FROM F132_EN)"
            arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if not resultat:
                #Retourner une exception
                raise Exception(u"Le code de l'élément topographique est absent ou encore utilisé : " + codeElem)
            
            #---------------------------------------------------------------------
            #Détruire l'information relative au code de l'élément topographique
            arcpy.AddMessage("- Détruire l'information relative au code de l'élément topographique ...")
            #Définir la commande pour détruire le code d'élément topographique
            sql = "DELETE F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Afficher l'information détruite
            arcpy.AddWarning(str(resultat))
            #Exécuter la commande
            self.Sib.execute(sql)
        
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
        listeCodeElem       = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeCodeElem = sys.argv[2].replace(";",",")
        
        #Définir l'objet pour détruire l'information relative aux codes d'élément topographique (entité de production) pour toutes les normes de la BDG.
        oDetruireEntiteProduction = DetruireEntiteProduction()
        
        #Valider les paramètres obligatoires
        oDetruireEntiteProduction.validerParamObligatoire(env, listeCodeElem)
        
        #Exécuter le traitement pour détruire l'information relative aux codes d'élément topographique (entité de production) pour toutes les normes de la BDG.
        oDetruireEntiteProduction.executer(env, listeCodeElem)
    
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