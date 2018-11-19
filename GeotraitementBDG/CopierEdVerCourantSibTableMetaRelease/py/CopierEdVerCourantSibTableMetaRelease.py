#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CopierEdVerCourantSibTableMetaRelease.py
# Auteur    : Michel Pothier
# Date      : 26 janvier 2015

"""
Application qui permet de copier les édition et version des jeux de données courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.

Paramètres d'entrée:
--------------------
env         OB      type d'environnement [BDRS_GEST_DBA]
                    défaut = BDRS_GEST_DBA
release     OB      Numéro du relase ou de la copie à traiter.
                    (Exemple : release=17 ou copie = 17.1)
                    défaut =

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du résultat de l'exécution du programme.
                  (Ex: 0=Succès, 1=Erreur)
Usage:
    CopierEdVerCourantSibTableMetaRelease.py env release

Exemple:
    CopierEdVerCourantSibTableMetaRelease.py BDRS_GEST_DBA 17
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CopierEdVerCourantSibTableMetaRelease.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class CopierEdVerCourantSibTableMetaRelease(object):
#*******************************************************************************************
    """
    Permet de copier les édition et version des jeux de données courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les édition et version des jeux de données courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        # Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, release):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour copier les édition et version des jeux de données courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        release     : Numéro du relase ou de la copie à traiter.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        oBDG            : Objet utilitaire pour traiter des services BDG.

        """
        
        #Instanciation de la classe BDG et connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        oBDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Vérifier si le numéro de release ou de la copie est numérique
        if not release.replace(".","").isdigit():
            #Retourner une exception
            raise Exception("Le numéro de la release ou de la copie n'est pas numérique : " + release)
        
        #Créer la requête SQL pour vérifier si le release ou la copie est déjà traité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Vérifier si le release ou la copie est déjà traité")
        sSql = "SELECT COUNT(*) FROM BDRS_GEST_DBA.META_RELEASE WHERE RELS_ID=" + release
        arcpy.AddMessage(sSql)
        #Exécuter la requête SQL
        resultat = oBDG.query(sSql)
        #Vérifier le résultat
        if resultat[0][0] <> 0:
            #Retourner une exception
            raise Exception("Le numéro de la release ou de la copie est déjà traité : " + release + ", Nb=" + str(resultat[0][0]))
        
        #Ajouter les jeux de données courants pour le release de la table META_RELEASE
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les numéros d'édition et version courants des jeux de données pour le release dans SIB")
        cmd = "INSERT INTO BDRS_GEST_DBA.META_RELEASE SELECT IDENTIFIANT,ED,VER," + release + " FROM F235_PR@SIB_PRO WHERE TY_PRODUIT='BDG' AND JEU_COUR=1"
        arcpy.AddMessage(cmd)
        oBDG.execute(cmd)
        
        #Détruire les jeux de données courants pour le release de la table META_RELEASE
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Détruire les numéros d'édition et version courants des jeux de données dans SIB")
        cmd = "DELETE BDG_DBA.META_RELEASE"
        arcpy.AddMessage(cmd)
        oBDG.execute(cmd)
        
        #Ajouter les jeux de données courants pour le release de la table META_RELEASE
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les numéros d'édition et version courants des jeux de données dans SIB")
        cmd = "INSERT INTO BDG_DBA.META_RELEASE SELECT IDENTIFIANT,ED,VER FROM F235_PR@SIB_PRO WHERE TY_PRODUIT='BDG' AND JEU_COUR=1"
        arcpy.AddMessage(cmd)
        oBDG.execute(cmd)
        
        #Accepter les ajouts
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Sauvegarder les données ajoutées")
        arcpy.AddMessage("COMMIT")
        oBDG.execute("COMMIT")
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        oBDG.close()
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "BDRS_GEST_DBA"
        release = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            release = sys.argv[2]
        
        #Définir l'objet pour copier l'édition et version des jeux de données courants de SIB
        oCopierEdVerCourantSibTableMetaRelease = CopierEdVerCourantSibTableMetaRelease()
        
        #Exécuter le traitement pour copier l'édition et version des jeux de données courants de SIB dans la table META_RELEASE.
        oCopierEdVerCourantSibTableMetaRelease.executer(env, release)
        
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