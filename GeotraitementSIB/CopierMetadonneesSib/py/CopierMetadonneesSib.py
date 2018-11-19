#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : CopierMetadonneesSib.py
# Auteur    : Michel Pothier
# Date      : 19 d�cembre 2017

"""
Application qui permet de copier les m�tadonn�es FGDC d'une �dition et version d'un identifiant
de produit d'une base de donn�es SIB dans les m�mes tables d'une autre base de donn�es SIB.

Les tables des m�tadonn�es FGDC dans SIB correspondent aux tables F235_xx sauf pour la table F235_VP.

Le jeu courant contenu dans la table est corrig� selon l'�dition et la version la plsu haute.

Param�tres d'entr�es:
----------------------
env1        : Base de donn�es SIB dans laquelle les donn�es SIB d'origine � copier.
              D�faut= SIB_PRO
env2        : Base de donn�es SIB dans laquelle les donn�es de SIB de destination sont � coller.
              D�faut= SIB_TST
ty_produit  : Produit d'un identifiant des m�tadonn�es � copier.
              D�faut= BDG
identifiant : Identifiant d'un produit des m�tadonn�es � copier.
              D�faut= 
ed_ver      : �dition et version d'un identifiant d'un produit des m�tadonn�es � copier.
              D�faut=
              
Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
Usage:
    CopierMetadonneesSib.py env1 env2 ty_produit identifiant ed_ver

Exemple:
    CopierMetadonneesSib.py SIB_PRO SIB_TST BDG 021M07 10.1

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CopierMetadonneesSib.py 2150 2017-12-19 19:52:19Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CopierMetadonneesSib(object):
#*******************************************************************************************
    """
    Application qui permet de copier les m�tadonn�es d'une �dition et version d'un identifiant
    de produit d'une base de donn�es SIB dans les m�mes tables d'une autre base de donn�es SIB.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour copier les m�tadonn�es d'une �dition et version d'un identifiant de produit SIB.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, env2, ty_produit, identifiant, ed_ver):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env1        : Base de donn�es SIB dans laquelle les donn�es SIB d'origine � copier.
        env2        : Base de donn�es SIB dans laquelle les donn�es de SIB de destination sont � coller.
        ty_produit  : Produit d'un identifiant des m�tadonn�es � copier.
        identifiant : Identifiant d'un produit des m�tadonn�es � copier.
        ed_ver      : �dition et version d'un identifiant d'un produit des m�tadonn�es � copier.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env1) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env1')

        if (len(env2) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env2')

        if (len(ty_produit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'ty_produit')

        if (len(identifiant) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'identifiant')

        if (len(ed_ver) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'ed_ver')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env1, env2, ty_produit, identifiant, ed_ver):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour copier les m�tadonn�es d'une �dition et version d'un identifiant de produit SIB.
        
        Param�tres:
        -----------
        env1        : Base de donn�es SIB dans laquelle les donn�es SIB d'origine � copier.
        env2        : Base de donn�es SIB dans laquelle les donn�es de SIB de destination sont � coller.
        ty_produit  : Produit d'un identifiant des m�tadonn�es � copier.
        identifiant : Identifiant d'un produit des m�tadonn�es � copier.
        ed_ver      : �dition et version d'un identifiant d'un produit des m�tadonn�es � copier.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD : " + env1)
        self.Sib1 = self.CompteSib.OuvrirConnexionSib(env1, env1)
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD : " + env2)
        self.Sib2 = self.CompteSib.OuvrirConnexionSib(env2, env2)
        
        #D�finition du format de la date
        self.Sib1.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        
        #D�finition du format de la date
        self.Sib2.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD HH24:MI:SS'")
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib1.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")

        #D�finir le num�ro d'�dition et deversion
        ed = ed_ver.split(".")[0]
        ver = ed_ver.split(".")[1]
        
        #Afficher le message pour valider l'identifiant de m�tadonn�es
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider l'identifiant du produit de m�tadonn�es ... ")
        #Extraire les nomdes  table
        sql = "SELECT * FROM F235_PR WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + ed + " AND VER=" + ver
        arcpy.AddMessage(sql)
        nbId = self.Sib1.requeteSib(sql)
        #V�rifier si l'�dision, version de l'identifiant du produit est valide
        if len(nbId) == 0:
            #Retourner une exception
            raise Exception("Le produit, l'identifiant, l'�dition et/ou la version est invalide : " + ty_produit + " " + identifiant + " " + ed + " " + ver)
        
        #Afficher le message de copie des tables
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire la liste des tables de m�tadonn�es ... ")
        #Extraire les noms des  table
        sql = "SELECT TNAME FROM TAB WHERE TNAME LIKE 'F235_%' AND TNAME <> 'F235_VP' ORDER BY TNAME"
        #arcpy.AddMessage(sql)
        listeTables = self.Sib1.requeteSib(sql)
        
        #Traiter toutes les tables � copier
        for table in listeTables:
            #Afficher le message de copie des tables
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Copie des m�tadonn�es de la table : " + table[0])
            #Extraire les m�tadonn�es de la table
            sql = "  SELECT * FROM " + table[0] + " WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + ed + " AND VER=" + ver
            #Afficher la requ�te SQL
            arcpy.AddMessage(sql)
            #Effectuer la requ�te SQL
            resultat1 = self.Sib1.requeteSib(sql)
            #Effectuer la requ�te SQL
            resultat2 = self.Sib2.requeteSib(sql)
            #Afficher le message u nombre de valeurs
            arcpy.AddMessage("  Nombre valeurs : " + str(len(resultat1)) + " / " + str(len(resultat2)))
            #V�rifier la pr�sence de donn�es
            if len(resultat1) > 0:  
                #V�rifier l'absence de donn�es
                if len(resultat2) == 0:
                    #Copier la table
                    for item in resultat1:
                        #Afficher le message u nombre de valeurs
                        #arcpy.AddMessage(str(item))
                        #Ins�rer les donn�es dans la table
                        sql = "  INSERT INTO " + table[0] + " VALUES ("
                        #Traiter toutes les valeurs
                        for val in item:
                            #Afficher le message u nombre de valeurs
                            if val == None:
                                sql = sql + "NULL" + ","
                            elif type(val) is datetime.datetime:
                                sql = sql + "'" + val.strftime('%Y/%m/%d %H:%M:%S') + "',"
                            elif type(val) is str:
                                sql = sql + "'" + val.replace("'","''") + "',"
                            else:
                                sql = sql + str(val) + ","
                        #Terminer la requ�te ad�quatement
                        sql = sql[:-1] + ")"
                        #Ex�cuter l'insersion
                        arcpy.AddMessage(sql)
                        self.Sib2.execute(sql)
                else:
                    #Message
                    arcpy.AddMessage("  Aucune copie effectu�e!")
            else:
                #Message
                arcpy.AddMessage("  Aucune copie effectu�e!")
        
        #Afficher le message pour valider le jeu de donn�es courant
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le jeu de donn�es courant ... ")
        #Extraire les jeux courants
        sql = "  SELECT ED,VER FROM F235_PR WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND JEU_COUR=1 ORDER BY ED,VER"
        arcpy.AddMessage(sql)
        jeuxCourant = self.Sib2.requeteSib(sql)
        #Traiter les jeux de donn�es courants
        for i in xrange(len(jeuxCourant)-1):
            #Corriger les jeu courant
            sql = "  UPDATE F235_PR SET JEU_COUR=0 WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(jeuxCourant[i][0]) + " AND VER=" + str(jeuxCourant[i][1])
            arcpy.AddMessage(sql)
            self.Sib2.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        #arcpy.AddMessage(sql)
        self.Sib2.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        self.Sib1.fermerConnexionSib()
        self.Sib2.fermerConnexionSib()
        
        #Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env1        = "SIB_PRO"
        env2        = "SIB_TST"
        ty_produit  = "BDG"
        identifiant = ""
        ed_ver      = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env1 = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            env2 = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            ty_produit = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            identifiant = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            ed_ver = sys.argv[5].upper()
        
        #D�finir l'objet pour copier les m�tadonn�es d'une �dition et version d'un identifiant de produit SIB.
        oCopierMetadonneesSib = CopierMetadonneesSib()
        
        #Valider les param�tres obligatoires.
        oCopierMetadonneesSib.validerParamObligatoire(env1, env2, ty_produit, identifiant, ed_ver)
        
        #Ex�cuter le traitement pour copier les m�tadonn�es d'une �dition et version d'un identifiant de produit SIB.
        oCopierMetadonneesSib.executer(env1, env2, ty_produit, identifiant, ed_ver)
        
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