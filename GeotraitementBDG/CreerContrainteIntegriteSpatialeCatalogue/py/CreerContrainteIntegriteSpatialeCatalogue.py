#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CreerContrainteIntegriteSpatialeCatalogue.py
# Auteur    : Michel Pothier
# Date      : 26 Octobre 2015

"""
    Application qui permet de créer les contraintes d'intégrités spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue et sa description.
                            défaut = 1:BDG
    classe          OB      Liste des noms de classe du catalogue à valider.
                            défaut = <Toutes les classes présentes dans le catalogue>
    type            OB      Liste des types de contrainte d'intégrité spatiale du catalogue à valider.
                            défaut = <Tous les types présents dans le catalogue>
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerContrainteIntegriteSpatialeCatalogue.py env catalogue classe type 

    Exemple:
        CreerContrainteIntegriteSpatialeCatalogue.py CATREL_PRO 1:BDG NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 GeometrieValide;LongueurGeometrie 

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerContrainteIntegriteSpatialeCatalogue.py 1109 2016-06-15 19:44:58Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, re, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class CreerContrainteIntegriteSpatialeCatalogue(object):
#*******************************************************************************************
    """
    Permet de créer les contraintes d'intégrités spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer les contraintes d'intégrités spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.
        self.nbSql      : Compteur des SQL de contrainte d'intégrité.
        self.sqlInsert  : Commande SQL de création des contraintes d'intégrité.
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()

        #Initialiser le compteur des SQL de contrainte d'intégrité
        self.nbSql = 0
        
        #Initialiser la commande SQL de création des contraintes d'intégrité.
        self.sqlInsert = "Insert into CONTRAINTE_INTEGRITE_SPATIALE (ETAMPE,DT_C,DT_M,GROUPE,DESCRIPTION,MESSAGE,REQUETE_SPATIALE,NOM_REQUETE,NOM_TABLE) Values ('MPOTHIER',SYSDATE,SYSDATE" 
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, classe, type):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la géodatabase.
        type        : Liste des types de contrainte d'intégrité spatiale du catalogue à valider.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        #Valider la présence
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')
        
        #Valider la présence
        if (len(catalogue) == 0):
            raise Exception ('Paramètre obligatoire manquant: catalogue')
        
        #Valider la présence
        if (len(classe) == 0):
            raise Exception ('Paramètre obligatoire manquant: classe')
        
        #Valider la présence
        if (len(type) == 0):
            raise Exception ('Paramètre obligatoire manquant: type')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, cat):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des paramètres.
        
        Paramètres:
        -----------
        cat             : Numéro du catalogue sans description.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
         
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Vérification des valeurs des paramètres")
        
        #Créer la requête SQL pour vérifier si le catalogue est valide
        arcpy.AddMessage("- Vérifier si le catalogue est valide")
        sql = ("SELECT DISTINCT FEAT_CATAL_TYPE"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + cat + " ")
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Numéro de catalogue invalide : " + cat)
        
        #Sortir
        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, classe, type):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour créer les contraintes d'intégrités spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la géodatabase.
        type        : Liste des types de contrainte d'intégrité spatiale à valider.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requête SQL à exécuter.
        cat             : Numéro du catalogue sans description.
        cls             : Classe à traiter.
        clsResultat     : Liste des classes à traiter.
        """
        
        #Vérification de la présence des paramètres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, type)
               
        #Vérifier la connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Définir le numéro de catalogue
        cat = catalogue.split(":")[0]
        
        #Valider les valeurs des paramètres
        self.validerValeurParam(cat)
        
        #Envoyer un message
        arcpy.AddMessage("- Créer les contraintes d'intégrité spatiale de chaque classe")
        
        #Créer la SQL pour extraire le code générique de chaque classe à valider
        sql =  ("select distinct B.feat_type_name_database, substr(to_char(B.feat_type_code_bd),1,3)||'0009'"
                "  from feat_catalogue A, feat_type B"
                " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_name_database in ('" + classe.replace(",","','") + "')"
                " order by B.feat_type_name_database")
        arcpy.AddMessage(sql)
        
        #Exécuter la SQL
        clsResultat = self.BDG.query(sql)
        
        #Traiter toutes les classes
        for cls in clsResultat:
            #Afficher le nom de la classe avec son code générique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("--" + cls[0] + ":" + cls[1])
            
            #Traiter tous les types de contrainte spatiale
            for ty in type.split(","):
                #Afficher le type de contrainte spatiale
                #arcpy.AddMessage("  " + ty)
                #Si le type est GeometrieValide
                if ty == "GeometrieValide":
                    #Groupe dans lequel la contraite d'intégrité est située.
                    if cls[0][-1] == "0":
                        groupe = ty + "_VIDE"
                        parametre = ty + ' "' + cls[0] + '" "VIDE FAUX"'
                    elif cls[0][-1] == "1":
                        groupe = ty + "_VALIDE"
                        parametre = ty + ' "' + cls[0] + '" "VALIDE VRAI"'
                    elif cls[0][-1] == "2":
                        groupe = ty + "_VALIDE"
                        parametre = ty + ' "' + cls[0] + '" "VALIDE VRAI"'
                    
                    #Description de la contrainte d'intégrité
                    description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la géométrie soit valide."
                    
                    #Message indiquant comment corriger l'erreur.
                    message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la géométrie soit valide."

                    #Afficher la requete de création de la contrainte spatiale à valider
                    arcpy.AddMessage(" ")
                    arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                    
                    #Compter le nombre de contrainte
                    self.nbSql = self.nbSql + 1
                    
                #Si le type est GeometrieValide
                if ty == "AngleGeometrie":
                    #Groupe dans lequel la contraite d'intégrité est située.
                    if cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_ANICROCHE"
                        parametre = ty + ' "' + cls[0]  + '" "ANICROCHE 10"'
                        
                        #Description de la contrainte d'intégrité
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la géométrie ne possède pas d''angle d''anicroche."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la géométrie ne possède plus d''angle d''anicroche."
                        
                        #Afficher la requete de création de la contrainte spatiale à valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                    
                #Si le type est NombreGeometrie
                if ty == "NombreGeometrie":
                    #Groupe dans lequel la contraite d'intégrité est située.
                    if cls[0][-1] == "1":
                        groupe = ty + "_COMPOSANTE"
                        parametre = ty + ' "' + cls[0]  + '" "COMPOSANTE ^1$"'
                        
                        #Description de la contrainte d'intégrité
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la géométrie possède seulement une composante."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la géométrie possède seulement une composante."
                             
                        #Afficher la requete de création de la contrainte spatiale à valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                   
                    elif cls[0][-1] == "2":
                        groupe = ty + "_EXTERIEUR "
                        parametre = ty + ' "' + cls[0] + '" "EXTERIEUR ^1$"'
                       
                        #Description de la contrainte d'intégrité
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la surface possède seulement un polygone extérieur."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la surface possède seulement un polygone extérieur."
                            
                        #Afficher la requete de création de la contrainte spatiale à valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                    
                #Si le type est LongueurGeometrie
                if ty == "LongueurGeometrie":
                    #Groupe dans lequel la contraite d'intégrité est située.
                    if cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_SEGMENT"
                        parametre = ty + ' "' + cls[0]  + '" "SEGMENT 2.5"'
                        
                        #Description de la contrainte d'intégrité
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la géométrie ne possède pas de segment trop petit."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la géométrie ne possède plus de segment trop petit."
                        
                        #Afficher la requete de création de la contrainte spatiale à valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                    
                #Si le type est DecoupageElement
                if ty == "DecoupageElement":
                    #Groupe dans lequel la contraite d'intégrité est située.
                    if cls[0][-1] == "0" or cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_DATASET_NAME"
                        parametre = ty + ' "' + cls[0]  + '" "DATASET_NAME DATASET_NAME"'
                        
                        #Description de la contrainte d'intégrité
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que l''identifiant et la géométrie correspondent à l''élément de découpage."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que l''identifiant et la géométrie correspondent à l''élément de découpage."
                        
                        #Afficher la requete de création de la contrainte spatiale à valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                        
                #Si le type est DecoupageElement
                if ty == "RelationSpatiale":
                    #Groupe dans lequel la contraite d'intégrité est située.
                    if cls[0][-1] == "0" or cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_EST_INCLUS_FAUX_IDEM"
                        parametre = ty + ' "' + cls[0]  + '" "EST_INCLUS FAUX" "' + cls[0] + '"'
                        
                        #Description de la contrainte d'intégrité
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la géométrie ne possède pas de superposition avec un élément de même classe."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la géométrie ne possède pas de superposition avec un élément de même classe."
                        
                        #Afficher la requete de création de la contrainte spatiale à valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                     
        #Afficher le nombre de types de contrainte à traiter
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre de types de contrainte spatiale à traiter : " + str(len(type.split(","))))
        
        #Afficher le nombre de contrainte d'intégrité.
        arcpy.AddMessage("- Nombre de contraintes d'intégrité spatiale : " + str(self.nbSql))
        
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
        env         = "CATREL_PRO"
        catalogue   = "1:BDG"
        classe      = ""
        type        = ""
        
        #Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            classe = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            type = sys.argv[4].replace(";",",")
        
        #Définir l'objet pour créer les contraintes d'intégrités spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        oCreerContrainteIntegriteSpatialeCatalogue = CreerContrainteIntegriteSpatialeCatalogue()
        
        #Exécuter le traitement pour créer les contraintes d'intégrités spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        oCreerContrainteIntegriteSpatialeCatalogue.executer(env, catalogue, classe, type)
            
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