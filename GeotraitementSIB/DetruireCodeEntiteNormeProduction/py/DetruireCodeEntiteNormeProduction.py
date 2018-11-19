#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : DetruireCodeEntiteNormeProduction.py
# Auteur    : Michel Pothier
# Date      : 17 août 2016

"""
    Application qui permet de détruire un ou plusieurs codes d'élément topographique pour un numéro de normes de la BDG.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    normes              OB      Normes de la BDG.
                                défaut = 4.2.2
    altimetrie          OB      Indique si les codes d'élément topographique possèdent de l'information altimétrique.
                                défaut = 0:Non
    patrimoine          OB      Indique si les codes d'élément topographique font partie du patrimoine.
                                défaut = 0:Non
    listeCodeElem       OB      Liste des codes de l'élément topographique.
                                défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireCodeEntiteNormeProduction.py env normes altimetrie patrimoine listeCodeElem

    Exemple:
        DetruireCodeEntiteNormeProduction.py SIB_PRO 4.2.2 0 0 "1000000;10000001"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireCodeEntiteNormeProduction.py 2101 2016-08-22 14:31:11Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireCodeEntiteNormeProduction:
#*******************************************************************************************
    """
    Classe qui permet de détruire un ou plusieurs codes d'élément topographique pour un numéro de normes de la BDG.
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
    def validerParamObligatoire(self, env, normes, altimetrie, patrimoine, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        normes              : Normes de la BDG.
        altimetrie          : Indique si les codes d'élément topographique possèdent de l'information altimétrique.
        patrimoine          : Indique si les codes d'élément topographique font partie du patrimoine.
        listeCodeElem       : Liste des codes de l'élément topographique.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(normes) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'normes')
        
        if (len(altimetrie) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'altimetrie')
        
        if (len(patrimoine) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'patrimoine')
        
        if (len(listeCodeElem) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'listeCodeElem')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, normes, altimetrie, patrimoine, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs codes d'élément topographique pour un numéro de normes de la BDG.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        normes              : Normes de la BDG.
        altimetrie          : Indique si les codes d'élément topographique possèdent de l'information altimétrique.
        patrimoine          : Indique si les codes d'élément topographique font partie du patrimoine.
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
        #Définir la commande SQL
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        #Afficher la commande SQL
        arcpy.AddMessage(sql)
        #Exécuter la commande SQL
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
        
        #Traiter tous les codes d'élément topographique
        for codeDesc in listeCodeElem.split(","):
            #Définir le code d'élément sans description
            codeElem = codeDesc.split(" ")[0]
            
            #---------------------------------------------------------------------
            #Détruire l'information relative au code d'élément topographique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Détruire l'information relative au code d'élément topographique : " + codeElem)
            
            #---------------------------------------------------------------------
            #Valider le code d'élément topographique
            sql = "SELECT CD_ELEM_TOPO FROM F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'"
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if not resultat:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception(u"Le code de l'élément topographique est invalide : " + codeElem)
            
            #---------------------------------------------------------------------
            #Vérifier si le code est existant
            if codeElem in listeCodeExistant:
                #Définir la commande pour extraire l'information du code d'élément topographique
                sql = "SELECT * FROM F132_EN WHERE CD_ELEM_TOPO='" + codeElem + "' AND NORMES='" + normes + "' AND ALTIMETRIE=" + altimetrie + " AND PATRIMOINE=" + patrimoine
                #Afficher la commande
                #arcpy.AddMessage(sql)
                #Exécuter la commande
                resultat = self.Sib.requeteSib(sql)
                #Définir la commande pour DÉTRUIRE le code d'élément topographique
                sql = "DELETE F132_EN WHERE CD_ELEM_TOPO='" + codeElem + "' AND NORMES='" + normes + "' AND ALTIMETRIE=" + altimetrie + " AND PATRIMOINE=" + patrimoine
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Afficher l'information détruite
                arcpy.AddWarning(str(resultat[0]))
                #Exécuter la commande
                self.Sib.execute(sql)
            #Si le code est absent
            else:
                #Afficher le message
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
        #Fermer la connexion SIB
        self.CompteSib.FermerConnexionSib() 
        
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
        altimetrie          = "0:Non"
        patrimoine          = "0:Non"
        listeCodeElem       = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            normes = sys.argv[2]
        
        if len(sys.argv) > 3:
            altimetrie = sys.argv[3].split(":")[0]
        
        if len(sys.argv) > 4:
            patrimoine = sys.argv[4].split(":")[0]
         
        if len(sys.argv) > 5:
            listeCodeElem = sys.argv[5].replace("'","").replace(";",",")
        
        #Définir l'objet pour détruire un ou plusieurs codes d'élément topographique pour un numéro de normes de la BDG.
        oDetruireCodeEntiteNormeProduction = DetruireCodeEntiteNormeProduction()
        
        #Valider les paramètres obligatoires
        oDetruireCodeEntiteNormeProduction.validerParamObligatoire(env, normes, altimetrie, patrimoine, listeCodeElem)
        
        #Exécuter le traitement pour détruire un ou plusieurs codes d'élément topographique pour un numéro de normes de la BDG.
        oDetruireCodeEntiteNormeProduction.executer(env, normes, altimetrie, patrimoine, listeCodeElem)
    
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