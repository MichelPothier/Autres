#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : DetruireCodeListeEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 17 août 2016

"""
    Application qui permet de détruire un ou plusieurs codes d'élément topographique à une liste pour toutes les normes de la BDG.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    nom                 OB      Nom de la liste des codes de l'élément topographique.
                                défaut = 
    collActive          OB      Indique si la collision est active ou non pour les codes d'élément topographique.
                                défaut = 1:Oui
    listeCodes          OB      Liste des codes d'élément topographique.
                                défaut =
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireCodeListeEntiteProduction.py env nom collActive listeCodes

    Exemple:
        DetruireCodeListeEntiteProduction.py SIB_PRO "FORTMCMURRAY" "1:Oui" 10000001;10000002
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireCodeListeEntiteProduction.py 2095 2016-08-17 17:01:47Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireCodeListeEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de détruire un ou plusieurs codes d'élément topographique à une liste pour toutes les normes de la BDG.
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
    def validerParamObligatoire(self, env, nom, collActive, listeCodes):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        nom                 : Nom de la liste des codes de l'élément topographique.
        collActive          : Indique si la collision est active ou non pour les codes d'élément topographique.
        listeCodes          : Liste des codes d'élément topographique.
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(nom) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'nom')
        
        if (len(collActive) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'collActive')
        
        if (len(listeCodes) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'listeCodes')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, nom, collActive, listeCodes):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs codes d'élément topographique à une liste pour toutes les normes de la BDG.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        nom                 : Nom de la liste des codes de l'élément topographique.
        collActive          : Indique si la collision est active ou non pour les codes d'élément topographique.
        listeCodes          : Liste des codes d'élément topographique.
        
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
        #Valider le nom de la liste des codes d'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le nom de la liste des codes d'élément topographique ...")
        #Définir la commande SQL
        sql = "SELECT NOM_LISTE, DESCR, DESCR_AN FROM F134_NL WHERE NOM_LISTE='" + nom + "'"
        #Afficher la commande SQL
        arcpy.AddMessage(sql)
        #Exécuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"Le nom de la liste des codes d'élément topographique est invalide : " + nom)
        
        #---------------------------------------------------------------------
        #Détruire les codes de la liste des codes d'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Détruire les codes de la liste des codes d'élément topographique ...")
        #Traiter tous les codes d'élément topographique
        for code in listeCodes.split(","):
            #Définir le code sans la description
            codeElem = code.replace("'","").split(" ")[0]
            
            #Définir la commande SQL
            sql = "SELECT * FROM F134_LE WHERE NOM_LISTE='" + nom + "' AND CD_ELEM_TOPO=" + codeElem + " AND COLLISION_ACTIVE=" + collActive
            #Afficher la commande SQL
            #arcpy.AddMessage(sql)
            #Exécuter la commande SQL
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Définir la commande pour détruire le code d'élément topographique à la liste
                sql = "DELETE F134_LE WHERE NOM_LISTE='" + nom + "' AND CD_ELEM_TOPO=" + codeElem + " AND COLLISION_ACTIVE=" + collActive
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Afficher l'information
                arcpy.AddWarning(str(resultat[0]))
                #Exécuter la commande
                self.Sib.execute(sql)
            #Si le code est absent
            else:
                #Afficher l'information
                arcpy.AddWarning("Code d'élément topographique absent : " + codeElem)
        
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
        nom                 = ""
        collActive          = "1:Oui"
        listeCodes          = ""
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            nom = sys.argv[2].replace("'","").split(" ")[0].upper()
        
        if len(sys.argv) > 3:
            collActive = sys.argv[3].split(":")[0]
        
        if len(sys.argv) > 4:
            listeCodes = sys.argv[4].replace(";",",")
        
        #Définir l'objet pour détruire un ou plusieurs codes d'élément topographique à une liste pour toutes les normes de la BDG.
        oDetruireCodeListeEntiteProduction = DetruireCodeListeEntiteProduction()
        
        #Valider les paramètres obligatoires
        oDetruireCodeListeEntiteProduction.validerParamObligatoire(env, nom, collActive, listeCodes)
        
        #Exécuter le traitement pour détruire un ou plusieurs codes d'élément topographique à une liste pour toutes les normes de la BDG.
        oDetruireCodeListeEntiteProduction.executer(env, nom, collActive, listeCodes)
    
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