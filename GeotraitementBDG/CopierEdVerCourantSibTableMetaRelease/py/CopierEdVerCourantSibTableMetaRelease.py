#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CopierEdVerCourantSibTableMetaRelease.py
# Auteur    : Michel Pothier
# Date      : 26 janvier 2015

"""
Application qui permet de copier les �dition et version des jeux de donn�es courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.

Param�tres d'entr�e:
--------------------
env         OB      type d'environnement [BDRS_GEST_DBA]
                    d�faut = BDRS_GEST_DBA
release     OB      Num�ro du relase ou de la copie � traiter.
                    (Exemple : release=17 ou copie = 17.1)
                    d�faut =

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel      : Code du r�sultat de l'ex�cution du programme.
                  (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class CopierEdVerCourantSibTableMetaRelease(object):
#*******************************************************************************************
    """
    Permet de copier les �dition et version des jeux de donn�es courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les �dition et version des jeux de donn�es courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        # D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, release):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour copier les �dition et version des jeux de donn�es courants de SIB dans la table BDRS_GEST_DBA.META_RELEASE.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        release     : Num�ro du relase ou de la copie � traiter.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        oBDG            : Objet utilitaire pour traiter des services BDG.

        """
        
        #Instanciation de la classe BDG et connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        oBDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #V�rifier si le num�ro de release ou de la copie est num�rique
        if not release.replace(".","").isdigit():
            #Retourner une exception
            raise Exception("Le num�ro de la release ou de la copie n'est pas num�rique : " + release)
        
        #Cr�er la requ�te SQL pour v�rifier si le release ou la copie est d�j� trait�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- V�rifier si le release ou la copie est d�j� trait�")
        sSql = "SELECT COUNT(*) FROM BDRS_GEST_DBA.META_RELEASE WHERE RELS_ID=" + release
        arcpy.AddMessage(sSql)
        #Ex�cuter la requ�te SQL
        resultat = oBDG.query(sSql)
        #V�rifier le r�sultat
        if resultat[0][0] <> 0:
            #Retourner une exception
            raise Exception("Le num�ro de la release ou de la copie est d�j� trait� : " + release + ", Nb=" + str(resultat[0][0]))
        
        #Ajouter les jeux de donn�es courants pour le release de la table META_RELEASE
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les num�ros d'�dition et version courants des jeux de donn�es pour le release dans SIB")
        cmd = "INSERT INTO BDRS_GEST_DBA.META_RELEASE SELECT IDENTIFIANT,ED,VER," + release + " FROM F235_PR@SIB_PRO WHERE TY_PRODUIT='BDG' AND JEU_COUR=1"
        arcpy.AddMessage(cmd)
        oBDG.execute(cmd)
        
        #D�truire les jeux de donn�es courants pour le release de la table META_RELEASE
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�truire les num�ros d'�dition et version courants des jeux de donn�es dans SIB")
        cmd = "DELETE BDG_DBA.META_RELEASE"
        arcpy.AddMessage(cmd)
        oBDG.execute(cmd)
        
        #Ajouter les jeux de donn�es courants pour le release de la table META_RELEASE
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les num�ros d'�dition et version courants des jeux de donn�es dans SIB")
        cmd = "INSERT INTO BDG_DBA.META_RELEASE SELECT IDENTIFIANT,ED,VER FROM F235_PR@SIB_PRO WHERE TY_PRODUIT='BDG' AND JEU_COUR=1"
        arcpy.AddMessage(cmd)
        oBDG.execute(cmd)
        
        #Accepter les ajouts
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Sauvegarder les donn�es ajout�es")
        arcpy.AddMessage("COMMIT")
        oBDG.execute("COMMIT")
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        oBDG.close()
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "BDRS_GEST_DBA"
        release = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            release = sys.argv[2]
        
        #D�finir l'objet pour copier l'�dition et version des jeux de donn�es courants de SIB
        oCopierEdVerCourantSibTableMetaRelease = CopierEdVerCourantSibTableMetaRelease()
        
        #Ex�cuter le traitement pour copier l'�dition et version des jeux de donn�es courants de SIB dans la table META_RELEASE.
        oCopierEdVerCourantSibTableMetaRelease.executer(env, release)
        
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