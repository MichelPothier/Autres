#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : AfficherInfoClasseCatalogue.py
# Auteur    : Michel Pothier
# Date      : 16 février 2015

"""
    Application qui permet d'afficher l'information sur les classes et attributs selon un catalogue. 
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue.
                            défaut = 1:BDG
    sousCatalogue   OB      Numéro du sous-catalogue de classes.
                            défaut =
                            Exemple:
                              92713:BDG-Classes actives (4.0.2)
    classe          OP      Nom d'une classe contenue dans le sous-catalogue spécifié.
                            défaut = 
    codeSpec        OP      Numéro d'un code spécifique contenue dans la classe spécifiée.
                            défaut = 
    attribut        OP      Nom d'un attribut lié au code spécifique.
                            défaut = 
    listeValeur     OP      Liste des valeurs d'attributs codés liées au nom d'attribut spécifié.
                            Aucune valeur n'est présente si l'attribut n'est pas codé.
                            défaut = 
    complet         OP      Indique si l'affichage doit être complet (True) ou partiel (False).
                            défaut = False
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        AfficherInfoClasseCatalogue.py env catalogue sousCatalogue [classe] [codeSpec] [attribut] [valeur]

    Exemple:
        AfficherInfoClasseCatalogue.py CATREL_PRO 1:BDG "92713:BDG-Classes actives (4.0.2)" NHN_HHYD_WATERBODY_2 "1480002:Région hydrique" WATER_DEFINITION "0:Aucun;1:Canal"

"""

__catalogue__ = "--catalogue-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherInfoClasseCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, cx_Oracle, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class AfficherInfoClasseCatalogue(object):
#*******************************************************************************************
    """
    Permet d'afficher l'information sur les classes d'un cataloguee.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher l'information sur les classes d'un catalogue.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du sous-catalogue.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Valider la présence
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')
        
        #Valider la présence
        if (len(catalogue) == 0):
            raise Exception ('Paramètre obligatoire manquant: catalogue')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCatalogue(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les catalogues
        
        Paramètres:
        -----------
        catalogue     : Numéro de la catalogue du sousCatalogue.
        
        Variables:
        ----------
        sql         : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Afficher l'information
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Catalogue")
        
        #Créer la requête SQL pour vérifier si la catalogue est valide
        #arcpy.AddMessage("- Vérifier si la catalogue est valide : " + catalogue)
        sql = "SELECT DISTINCT FEAT_CATAL_TYPE FROM FEAT_CATALOGUE WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " "
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #Traiter tous les résultats
        for item in resultat:
            #Afficher l'information complète
            if complet:
                #Afficher l'information
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_TYPE = " + str(item[0]))
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage(" " + catalogue)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def afficherSousCatalogue(self, catalogue, sousCatalogue):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les sous-catalogues
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        
        Variables:
        ----------
        sql         : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Afficher l'information
        arcpy.AddMessage("Sous-catalogue")
        
        #Créer la requête SQL pour vérifier si le nom du sousCatalogue est valide
        #arcpy.AddMessage("- Vérifier si le nom du sousCatalogue est valide : " + sousCatalogue)
        sql = ("SELECT FEAT_CATAL_ID,FEAT_CATAL_NAME_FR,FEAT_CATAL_NAME_EN,FEAT_CATAL_BDG_VER_NUM,FEAT_CATAL_VERSION_DATE"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0])
        #Vérifier si le sousCatalogue est présent
        if len(sousCatalogue) > 0:
            #Ajouter le nom du sousCatalogue à rechercher
            sql = sql + " AND FEAT_CATAL_ID='" + sousCatalogue.split(":")[0] + "'"
        #Ajouter le tri à la SQL
        sql =sql + " ORDER BY FEAT_CATAL_NAME_FR"
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Numéro du sous-catalogue invalide : " + sousCatalogue)
        
        #Traiter tous les résultats
        for item in resultat:
            #Afficher l'information complète
            if complet:
                #Afficher l'information
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_ID = " + str(item[0]))
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_NAME_FR = '" + item[1] + "'")
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_NAME_EN = '" + item[2] + "'")
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_BDG_VER_NUM = '" + str(item[3]) + "'")
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_VERSION_DATE = '" + str(item[3]) + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage(" " + str(item[0]) + " : " + item[1] + " / " + item[2] + " (" + str(item[3]) + ")")
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherClasse(self, catalogue, sousCatalogue, classe):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les classes
        
        Paramètres:
        -----------
        catalogue       : Numéro de la catalogue du sousCatalogue.
        sousCatalogue   : Numéro du sous-catalogue pour un groupe de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        attribut        : Nom d'un attribut lié au code spécifique.
        listeValeur     : Liste des valeurs d'attributs codés liées au nom d'attribut spécifié.
        complet         : Indique si l'affichage doit être complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier si la classe est valide
        sql = ("SELECT DISTINCT B.FEAT_TYPE_NAME_DATABASE"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND FEAT_CATAL_ID='" + sousCatalogue.split(":")[0] + "'")
        #Vérifier si la classe est présente
        if len(classe) > 0:
            #Ajouter le nom de la classe à rechercher
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE='" + classe + "'"
        #Si la classe est absente
        else:
            #Ajouter le nom de la classe à rechercher
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IS NOT NULL"
        #Ajouter le tri à la SQL
        sql =sql + " ORDER BY B.FEAT_TYPE_NAME_DATABASE"
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Nom de la classe invalide : " + classe)
        
        #Traiter tous les résultats
        for item in resultat:
            #Afficher l'information complète
            if complet:
                #Afficher l'information
                arcpy.AddMessage("   FEAT_TYPE.FEAT_TYPE_NAME_DATABASE = '" + item[0] + "'")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("   " + item[0])
            
            #Afficher l'information
            self.afficherCodeSpec(catalogue, sousCatalogue, item[0], codeSpec)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCodeSpec(self, catalogue, sousCatalogue, classe, codeSpec):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les codes spécifiques
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        attribut        : Nom d'un attribut lié au code spécifique.
        listeValeur     : Liste des valeurs d'attributs codés liées au nom d'attribut spécifié.
        complet         : Indique si l'affichage doit être complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier si le codeSpec est valide
        sql = ("SELECT B.FEAT_TYPE_ID, B.FEAT_TYPE_CODE_BD, B.FEAT_TYPE_NAME_FR, B.FEAT_TYPE_DEFINITION_FR, B.FEAT_TYPE_NAME_EN, B.FEAT_TYPE_DEFINITION_EN"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK")
        #Vérifier si la classe est présente
        if classe <> None:
            #Ajouter le nom du code spécifique à rechercher
            sql = sql +  " AND B.FEAT_TYPE_NAME_DATABASE='" + classe + "'"       
        #Si la classe est absente
        else:
            #Ajouter le nom du code spécifique à rechercher
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IS NULL"
        #Vérifier si le codeSpec est présent
        if len(codeSpec) > 0:
            #Ajouter le nom du code spécifique à rechercher
            sql = sql + " AND B.FEAT_TYPE_CODE_BD=" + codeSpec
        #Ajouter le tri à la SQL
        sql =sql + " ORDER BY B.FEAT_TYPE_CODE_BD"
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Code spécifique invalide : " + codeSpec)
        
        #Traiter tous les résultats
        for item in resultat:
            #Afficher l'information complète
            if complet:
                #Afficher l'information
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_ID = " + str(item[0]))
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_CODE_BD = " + str(item[1]))
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_NAME_FR = '" + item[2] + "'")
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_DEFINITION_FR = '" + item[3] + "'")
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_NAME_EN = '" + item[4] + "'")
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_DEFINITION_EN = '" + item[5] + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("     " + str(item[1]) + " : " + item[2] + " / " + item[4])
            
            #Afficher l'information
            self.afficherAttribut(catalogue, sousCatalogue, classe, str(item[1]), attribut)
            arcpy.AddMessage(" ")
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherAttribut(self, catalogue, sousCatalogue, classe, codeSpec, attribut):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les attributs
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        attribut        : Nom d'un attribut lié au code spécifique.
        listeValeur     : Liste des valeurs d'attributs codés liées au nom d'attribut spécifié.
        complet         : Indique si l'affichage doit être complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier si l'attribut est valide
        #arcpy.AddMessage("- Vérifier si l'attribut est valide : " + attribut)
        sql = ("SELECT D.FEAT_ATTR_ID,D.FEAT_ATTR_NAME_DATABASE,D.FEAT_ATTR_DATA_TYPE,D.FEAT_ATTR_NAME_FR,D.FEAT_ATTR_DEFINITION_FR,D.FEAT_ATTR_NAME_EN,D.FEAT_ATTR_DEFINITION_EN"
               "  FROM FEAT_CATALOGUE A,FEAT_TYPE B,RELATION_FEAT_ATTR C,FEAT_ATTR D"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"
               "   AND B.FEAT_TYPE_CODE_BD=" + codeSpec + " AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID")
        #Vérifier si l'attribut est présent
        if len(attribut) > 0:
            #Ajouter le nom de l'attribut à rechercher
            sql = sql + " AND D.FEAT_ATTR_NAME_DATABASE='" + attribut + "'"
        #Ajouter le tri à la SQL
        sql =sql + " ORDER BY D.FEAT_ATTR_NAME_DATABASE"
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Attribut invalide : " + attribut)
        
        #Traiter tous les résultats
        for item in resultat:
            #Afficher l'information complète
            if complet:
                #Afficher l'information
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_ID = " + str(item[0]))
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_NAME_DATABASE = '" + item[1] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_DATA_TYPE = '" + str(item[2]) + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_NAME_FR = '" + item[3] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_DEFINITION_FR = '" + item[4] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_NAME_EN = '" + item[5] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_DEFINITION_EN = '" + item[6] + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("       " + item[1].ljust(25," ") + " : " + str(item[2]).ljust(20," ") + " : " + item[3] + " / " + item[5])
            
            #Afficher l'information
            self.afficherValeurAttribut(catalogue, sousCatalogue, classe, codeSpec, item[1], listeValeur)
            
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherValeurAttribut(self, catalogue, sousCatalogue, classe, codeSpec, attribut, listeValeur):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les valeurs d'attributs.
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        attribut        : Nom d'un attribut lié au code spécifique.
        listeValeur     : Liste des valeurs d'attributs codés liées au nom d'attribut spécifié.
        complet         : Indique si l'affichage doit être complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier la valeur d'attribut
        #arcpy.AddMessage("- Vérifier la liste des valeurs d'attribut : " + listeValeur)
        sql = ("SELECT E.ATTR_VALUE_ID,E.ATTR_VALUE_INTERNAL_CODE,E.ATTR_VALUE_LABEL_FR,E.ATTR_VALUE_DEFINITION_FR,E.ATTR_VALUE_LABEL_EN,E.ATTR_VALUE_DEFINITION_EN"
               "  FROM FEAT_CATALOGUE A,FEAT_TYPE B,RELATION_FEAT_ATTR C,FEAT_ATTR D,FEAT_ATTR_VALUE E"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"
               " AND B.FEAT_TYPE_CODE_BD=" + codeSpec + " AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID"
               " AND D.FEAT_ATTR_NAME_DATABASE='" + attribut + "' AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK")
        #Vérifier si la liste des valeurs d'attribut est présente
        if len(listeValeur) > 0:
            #Initialiser les valeurs d'attribut à rechercher
            valeurs = ""
            #Traiter toutes les valeurs de la liste
            for valeur in listeValeur.split(","):
                #Ajouter les valeurs d'attributs à rechercher
                valeurs = valeurs + valeur.split(":")[0] + ","
            #Ajouter les valeurs d'attribut à rechercher dans la SQL
            sql = sql + " AND E.ATTR_VALUE_INTERNAL_CODE IN (" + valeurs[:-1] + ")"
        #Ajouter le tri à la SQL
        sql =sql + " ORDER BY E.ATTR_VALUE_INTERNAL_CODE"
            
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Vérifier une valeur est spécifiée
            if len(listeValeur) > 0:
                #Afficher la commande SQL
                arcpy.AddMessage(sql)
                #Envoyer une exception
                arcpy.AddWarning("Valeur d'attribut invalide : " + listeValeur)
        
        #Traiter tous les résultats
        for item in resultat:
            #Afficher l'information complète
            if complet:
                #Afficher l'information
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_ID = " + str(item[0]))
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_INTERNAL_CODE = " + str(item[1]))
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_LABEL_FR = '" + item[2] + "'")
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_DEFINITION_FR = '" + item[3] + "'")
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_LABEL_EN = '" + item[4] + "'")
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_DEFINITION_EN = '" + item[5] + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("         " + str(item[1]).rjust(3," ") + " : " + item[2] + " / " + item[4])
            
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, sousCatalogue, classe, codeSpec, attribut, listeValeur, complet=False):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour afficher l'information sur les classes d'un catalogue.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        attribut        : Nom d'un attribut lié au code spécifique.
        listeValeur     : Liste des valeurs d'attributs codés liées au nom d'attribut spécifié.
        complet         : Indique si l'affichage doit être complet (True) ou partiel (False).
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requête SQL à exécuter.
        """
        
        #Instanciation de la classe BDG et connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Afficher l'information
        self.afficherCatalogue(catalogue)
        
        #Afficher l'information
        self.afficherSousCatalogue(catalogue, sousCatalogue)
        
        #Afficher l'information
        self.afficherClasse(catalogue, sousCatalogue, classe)
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env             = "CATREL_PRO"
        catalogue       = "1:BDG"
        sousCatalogue   = ""
        classe          = ""
        codeSpec        = ""
        attribut        = ""
        listeValeur     = ""
        complet         = False
        
        #Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            sousCatalogue = sys.argv[3]

        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                classe = sys.argv[4].upper()

        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                codeSpec = sys.argv[5].split(":")[0]

        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                attribut = sys.argv[6].upper()

        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                listeValeur = sys.argv[7].replace(";",",").replace("'","")

        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                complet = sys.argv[8].upper() == "TRUE"
        
        #Définir l'objet pour afficher l'information sur les classes d'un catalogue.
        oAfficherInfoClasseCatalogue = AfficherInfoClasseCatalogue()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oAfficherInfoClasseCatalogue.validerParamObligatoire(env, catalogue)
        
        #Exécuter le traitement pour afficher l'information sur les classes d'un catalogue.
        oAfficherInfoClasseCatalogue.executer(env, catalogue, sousCatalogue, classe, codeSpec, attribut, listeValeur, complet)
    
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