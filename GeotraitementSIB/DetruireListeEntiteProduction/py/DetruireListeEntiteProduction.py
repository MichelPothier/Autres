#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : DetruireListeEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 17 août 2016

"""
    Application qui permet de détruire une ou plusieurs listes de codes d'élément topographique pour toutes les normes de la BDG.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    listeNom            OB      Liste de nom de liste des codes de l'élément topographique.
                                défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireListeEntiteProduction.py env listeNom 

    Exemple:
        DetruireListeEntiteProduction.py SIB_PRO "FORTMCMURRAY;HYPSO" 
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireListeEntiteProduction.py 2090 2016-08-17 13:53:16Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireListeEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de détruire une ou plusieurs listes de codes d'élément topographique
    pour toutes les normes de la BDG.
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
    def validerParamObligatoire(self, env, listeNom):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        listeNom            : Liste de nom de liste des codes de l'élément topographique.
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(listeNom) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'listeNom')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNom):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire une ou plusieurs listes de codes d'élément topographique
        pour toutes les normes de la BDG.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        listeNom        : Liste de nom de liste des codes de l'élément topographique.
        
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
        
        #Traiter tous les noms de liste
        for nomListe in listeNom.split(","):
            #Définir le nom de la liste
            nom = nomListe.replace("'","").split(" ")[0]
            
            #---------------------------------------------------------------------
            #Valider le nom de la liste des codes d'élément topographique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Valider le nom de la liste des codes d'élément topographique ...")
            #Définir la commande
            sql = "SELECT * FROM F134_NL WHERE NOM_LISTE='" + nom + "'"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Exécuter la commande
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if not resultat:
                #Retourner une exception
                raise Exception(u"Le nom de la liste des codes d'élément topographique est invalide : " + nom)
            
            #---------------------------------------------------------------------
            #Détruire l'information de la liste des codes d'élément topographique
            arcpy.AddMessage("- Détruire l'information de la liste des codes d'élément topographique ...")
            #Définir la commande
            sql = "DELETE F134_NL WHERE NOM_LISTE='" + nom + "'"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Afficher l'information de la liste
            arcpy.AddWarning(str(resultat))
            #Exécuter la commande
            self.Sib.execute(sql)
            
            #---------------------------------------------------------------------
            #Détruire la liste des codes d'élément topographique
            arcpy.AddMessage("- Détruire l'information des codes d'élément topographique de la liste ...")               
            #Définir la commande
            sql = "SELECT * FROM F134_LE WHERE NOM_LISTE='" + nom + "'"
            #Afficher la commande
            #arcpy.AddMessage(sql)
            #Exécuter la commande
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Définir la commande
                sql = "DELETE F134_LE WHERE NOM_LISTE='" + nom + "'"
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Exécuter la commande
                self.Sib.execute(sql)
                #Afficher l'information détruite
                for code in resultat:
                    #Afficher l'information du code
                    arcpy.AddWarning(str(code))
       
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
        env         = "SIB_PRO"
        listeNom    = ""
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeNom = sys.argv[2].replace(";",",")
        
        #Définir l'objet pour détruire une ou plusieurs listes de codes d'élément topographique pour toutes les normes de la BDG.
        oDetruireListeEntiteProduction = DetruireListeEntiteProduction()
        
        #Valider les paramètres obligatoires
        oDetruireListeEntiteProduction.validerParamObligatoire(env, listeNom)
        
        #Exécuter le traitement pour détruire une ou plusieurs listes de codes d'élément topographique pour toutes les normes de la BDG.
        oDetruireListeEntiteProduction.executer(env, listeNom)
    
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