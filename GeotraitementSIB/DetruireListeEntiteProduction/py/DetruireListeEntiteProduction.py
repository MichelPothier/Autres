#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : DetruireListeEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 17 ao�t 2016

"""
    Application qui permet de d�truire une ou plusieurs listes de codes d'�l�ment topographique pour toutes les normes de la BDG.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    listeNom            OB      Liste de nom de liste des codes de l'�l�ment topographique.
                                d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireListeEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de d�truire une ou plusieurs listes de codes d'�l�ment topographique
    pour toutes les normes de la BDG.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de mise au programme.
        
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
    def validerParamObligatoire(self, env, listeNom):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        listeNom            : Liste de nom de liste des codes de l'�l�ment topographique.
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')
        
        if (len(listeNom) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'listeNom')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, listeNom):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire une ou plusieurs listes de codes d'�l�ment topographique
        pour toutes les normes de la BDG.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        listeNom        : Liste de nom de liste des codes de l'�l�ment topographique.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #---------------------------------------------------------------------
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Traiter tous les noms de liste
        for nomListe in listeNom.split(","):
            #D�finir le nom de la liste
            nom = nomListe.replace("'","").split(" ")[0]
            
            #---------------------------------------------------------------------
            #Valider le nom de la liste des codes d'�l�ment topographique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Valider le nom de la liste des codes d'�l�ment topographique ...")
            #D�finir la commande
            sql = "SELECT * FROM F134_NL WHERE NOM_LISTE='" + nom + "'"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Ex�cuter la commande
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if not resultat:
                #Retourner une exception
                raise Exception(u"Le nom de la liste des codes d'�l�ment topographique est invalide : " + nom)
            
            #---------------------------------------------------------------------
            #D�truire l'information de la liste des codes d'�l�ment topographique
            arcpy.AddMessage("- D�truire l'information de la liste des codes d'�l�ment topographique ...")
            #D�finir la commande
            sql = "DELETE F134_NL WHERE NOM_LISTE='" + nom + "'"
            #Afficher la commande
            arcpy.AddMessage(sql)
            #Afficher l'information de la liste
            arcpy.AddWarning(str(resultat))
            #Ex�cuter la commande
            self.Sib.execute(sql)
            
            #---------------------------------------------------------------------
            #D�truire la liste des codes d'�l�ment topographique
            arcpy.AddMessage("- D�truire l'information des codes d'�l�ment topographique de la liste ...")               
            #D�finir la commande
            sql = "SELECT * FROM F134_LE WHERE NOM_LISTE='" + nom + "'"
            #Afficher la commande
            #arcpy.AddMessage(sql)
            #Ex�cuter la commande
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #D�finir la commande
                sql = "DELETE F134_LE WHERE NOM_LISTE='" + nom + "'"
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
                #Afficher l'information d�truite
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
        
        #Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        #Fermer la connexion SIB
        self.CompteSib.FermerConnexionSib()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        listeNom    = ""
        
        #Extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeNom = sys.argv[2].replace(";",",")
        
        #D�finir l'objet pour d�truire une ou plusieurs listes de codes d'�l�ment topographique pour toutes les normes de la BDG.
        oDetruireListeEntiteProduction = DetruireListeEntiteProduction()
        
        #Valider les param�tres obligatoires
        oDetruireListeEntiteProduction.validerParamObligatoire(env, listeNom)
        
        #Ex�cuter le traitement pour d�truire une ou plusieurs listes de codes d'�l�ment topographique pour toutes les normes de la BDG.
        oDetruireListeEntiteProduction.executer(env, listeNom)
    
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