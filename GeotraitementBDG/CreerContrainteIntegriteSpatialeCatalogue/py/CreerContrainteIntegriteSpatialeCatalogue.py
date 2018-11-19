#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CreerContrainteIntegriteSpatialeCatalogue.py
# Auteur    : Michel Pothier
# Date      : 26 Octobre 2015

"""
    Application qui permet de cr�er les contraintes d'int�grit�s spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue et sa description.
                            d�faut = 1:BDG
    classe          OB      Liste des noms de classe du catalogue � valider.
                            d�faut = <Toutes les classes pr�sentes dans le catalogue>
    type            OB      Liste des types de contrainte d'int�grit� spatiale du catalogue � valider.
                            d�faut = <Tous les types pr�sents dans le catalogue>
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class CreerContrainteIntegriteSpatialeCatalogue(object):
#*******************************************************************************************
    """
    Permet de cr�er les contraintes d'int�grit�s spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour cr�er les contraintes d'int�grit�s spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.
        self.nbSql      : Compteur des SQL de contrainte d'int�grit�.
        self.sqlInsert  : Commande SQL de cr�ation des contraintes d'int�grit�.
        """
        
        #D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()

        #Initialiser le compteur des SQL de contrainte d'int�grit�
        self.nbSql = 0
        
        #Initialiser la commande SQL de cr�ation des contraintes d'int�grit�.
        self.sqlInsert = "Insert into CONTRAINTE_INTEGRITE_SPATIALE (ETAMPE,DT_C,DT_M,GROUPE,DESCRIPTION,MESSAGE,REQUETE_SPATIALE,NOM_REQUETE,NOM_TABLE) Values ('MPOTHIER',SYSDATE,SYSDATE" 
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, classe, type):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la g�odatabase.
        type        : Liste des types de contrainte d'int�grit� spatiale du catalogue � valider.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        #Valider la pr�sence
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')
        
        #Valider la pr�sence
        if (len(catalogue) == 0):
            raise Exception ('Param�tre obligatoire manquant: catalogue')
        
        #Valider la pr�sence
        if (len(classe) == 0):
            raise Exception ('Param�tre obligatoire manquant: classe')
        
        #Valider la pr�sence
        if (len(type) == 0):
            raise Exception ('Param�tre obligatoire manquant: type')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, cat):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des param�tres.
        
        Param�tres:
        -----------
        cat             : Num�ro du catalogue sans description.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
         
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification des valeurs des param�tres")
        
        #Cr�er la requ�te SQL pour v�rifier si le catalogue est valide
        arcpy.AddMessage("- V�rifier si le catalogue est valide")
        sql = ("SELECT DISTINCT FEAT_CATAL_TYPE"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + cat + " ")
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Num�ro de catalogue invalide : " + cat)
        
        #Sortir
        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, classe, type):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour cr�er les contraintes d'int�grit�s spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la g�odatabase.
        type        : Liste des types de contrainte d'int�grit� spatiale � valider.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requ�te SQL � ex�cuter.
        cat             : Num�ro du catalogue sans description.
        cls             : Classe � traiter.
        clsResultat     : Liste des classes � traiter.
        """
        
        #V�rification de la pr�sence des param�tres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, type)
               
        #V�rifier la connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #D�finir le num�ro de catalogue
        cat = catalogue.split(":")[0]
        
        #Valider les valeurs des param�tres
        self.validerValeurParam(cat)
        
        #Envoyer un message
        arcpy.AddMessage("- Cr�er les contraintes d'int�grit� spatiale de chaque classe")
        
        #Cr�er la SQL pour extraire le code g�n�rique de chaque classe � valider
        sql =  ("select distinct B.feat_type_name_database, substr(to_char(B.feat_type_code_bd),1,3)||'0009'"
                "  from feat_catalogue A, feat_type B"
                " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_name_database in ('" + classe.replace(",","','") + "')"
                " order by B.feat_type_name_database")
        arcpy.AddMessage(sql)
        
        #Ex�cuter la SQL
        clsResultat = self.BDG.query(sql)
        
        #Traiter toutes les classes
        for cls in clsResultat:
            #Afficher le nom de la classe avec son code g�n�rique
            arcpy.AddMessage(" ")
            arcpy.AddMessage("--" + cls[0] + ":" + cls[1])
            
            #Traiter tous les types de contrainte spatiale
            for ty in type.split(","):
                #Afficher le type de contrainte spatiale
                #arcpy.AddMessage("  " + ty)
                #Si le type est GeometrieValide
                if ty == "GeometrieValide":
                    #Groupe dans lequel la contraite d'int�grit� est situ�e.
                    if cls[0][-1] == "0":
                        groupe = ty + "_VIDE"
                        parametre = ty + ' "' + cls[0] + '" "VIDE FAUX"'
                    elif cls[0][-1] == "1":
                        groupe = ty + "_VALIDE"
                        parametre = ty + ' "' + cls[0] + '" "VALIDE VRAI"'
                    elif cls[0][-1] == "2":
                        groupe = ty + "_VALIDE"
                        parametre = ty + ' "' + cls[0] + '" "VALIDE VRAI"'
                    
                    #Description de la contrainte d'int�grit�
                    description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la g�om�trie soit valide."
                    
                    #Message indiquant comment corriger l'erreur.
                    message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la g�om�trie soit valide."

                    #Afficher la requete de cr�ation de la contrainte spatiale � valider
                    arcpy.AddMessage(" ")
                    arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                    
                    #Compter le nombre de contrainte
                    self.nbSql = self.nbSql + 1
                    
                #Si le type est GeometrieValide
                if ty == "AngleGeometrie":
                    #Groupe dans lequel la contraite d'int�grit� est situ�e.
                    if cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_ANICROCHE"
                        parametre = ty + ' "' + cls[0]  + '" "ANICROCHE 10"'
                        
                        #Description de la contrainte d'int�grit�
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la g�om�trie ne poss�de pas d''angle d''anicroche."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la g�om�trie ne poss�de plus d''angle d''anicroche."
                        
                        #Afficher la requete de cr�ation de la contrainte spatiale � valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                    
                #Si le type est NombreGeometrie
                if ty == "NombreGeometrie":
                    #Groupe dans lequel la contraite d'int�grit� est situ�e.
                    if cls[0][-1] == "1":
                        groupe = ty + "_COMPOSANTE"
                        parametre = ty + ' "' + cls[0]  + '" "COMPOSANTE ^1$"'
                        
                        #Description de la contrainte d'int�grit�
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la g�om�trie poss�de seulement une composante."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la g�om�trie poss�de seulement une composante."
                             
                        #Afficher la requete de cr�ation de la contrainte spatiale � valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                   
                    elif cls[0][-1] == "2":
                        groupe = ty + "_EXTERIEUR "
                        parametre = ty + ' "' + cls[0] + '" "EXTERIEUR ^1$"'
                       
                        #Description de la contrainte d'int�grit�
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la surface poss�de seulement un polygone ext�rieur."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la surface poss�de seulement un polygone ext�rieur."
                            
                        #Afficher la requete de cr�ation de la contrainte spatiale � valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                    
                #Si le type est LongueurGeometrie
                if ty == "LongueurGeometrie":
                    #Groupe dans lequel la contraite d'int�grit� est situ�e.
                    if cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_SEGMENT"
                        parametre = ty + ' "' + cls[0]  + '" "SEGMENT 2.5"'
                        
                        #Description de la contrainte d'int�grit�
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la g�om�trie ne poss�de pas de segment trop petit."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la g�om�trie ne poss�de plus de segment trop petit."
                        
                        #Afficher la requete de cr�ation de la contrainte spatiale � valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                    
                #Si le type est DecoupageElement
                if ty == "DecoupageElement":
                    #Groupe dans lequel la contraite d'int�grit� est situ�e.
                    if cls[0][-1] == "0" or cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_DATASET_NAME"
                        parametre = ty + ' "' + cls[0]  + '" "DATASET_NAME DATASET_NAME"'
                        
                        #Description de la contrainte d'int�grit�
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que l''identifiant et la g�om�trie correspondent � l''�l�ment de d�coupage."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que l''identifiant et la g�om�trie correspondent � l''�l�ment de d�coupage."
                        
                        #Afficher la requete de cr�ation de la contrainte spatiale � valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                        
                #Si le type est DecoupageElement
                if ty == "RelationSpatiale":
                    #Groupe dans lequel la contraite d'int�grit� est situ�e.
                    if cls[0][-1] == "0" or cls[0][-1] == "1" or cls[0][-1] == "2":
                        groupe = ty + "_EST_INCLUS_FAUX_IDEM"
                        parametre = ty + ' "' + cls[0]  + '" "EST_INCLUS FAUX" "' + cls[0] + '"'
                        
                        #Description de la contrainte d'int�grit�
                        description = "Valider la contrainte spatiale " + ty + " de la classe " + cls[0] + " afin que la g�om�trie ne poss�de pas de superposition avec un �l�ment de m�me classe."
                        
                        #Message indiquant comment corriger l'erreur.
                        message = "Corriger l''erreur de " + ty + " de la classe " + cls[0] + " afin que la g�om�trie ne poss�de pas de superposition avec un �l�ment de m�me classe."
                        
                        #Afficher la requete de cr�ation de la contrainte spatiale � valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + parametre + "','" + ty + "','" + cls[0] + "');")
                        
                        #Compter le nombre de contrainte
                        self.nbSql = self.nbSql + 1
                     
        #Afficher le nombre de types de contrainte � traiter
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre de types de contrainte spatiale � traiter : " + str(len(type.split(","))))
        
        #Afficher le nombre de contrainte d'int�grit�.
        arcpy.AddMessage("- Nombre de contraintes d'int�grit� spatiale : " + str(self.nbSql))
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env         = "CATREL_PRO"
        catalogue   = "1:BDG"
        classe      = ""
        type        = ""
        
        #Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            classe = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            type = sys.argv[4].replace(";",",")
        
        #D�finir l'objet pour cr�er les contraintes d'int�grit�s spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        oCreerContrainteIntegriteSpatialeCatalogue = CreerContrainteIntegriteSpatialeCatalogue()
        
        #Ex�cuter le traitement pour cr�er les contraintes d'int�grit�s spatiale pour chaque classe et chaque type de contrainte contenue dans un catalogue.
        oCreerContrainteIntegriteSpatialeCatalogue.executer(env, catalogue, classe, type)
            
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