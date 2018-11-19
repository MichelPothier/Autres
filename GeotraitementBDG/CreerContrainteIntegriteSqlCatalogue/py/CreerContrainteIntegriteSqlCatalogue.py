#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CreerContrainteIntegriteSqlCatalogue.py
# Auteur    : Michel Pothier
# Date      : 09 septembre 2015

"""
    Application qui permet de valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.

    Le catalogue contient des valeurs codées et/ou des expressions régulières pour chaque attribut d'un code spécifique.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue et sa description.
                            défaut = 1:BDG
    classe          OB      Liste des noms de classe du catalogue à valider.
                            défaut = <Toutes les classes présentes dans le catalogue>
    attribut        OB      Liste des noms d'attribut du catalogue à valider.
                            défaut = <Tous les attributs présents dans le catalogue>
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerContrainteIntegriteSqlCatalogue.py env catalogue classe attribut 

    Exemple:
        CreerContrainteIntegriteSqlCatalogue.py CATREL_PRO 1:BDG NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 WATER_DEFINITION,PERMANENCY 

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerContrainteIntegriteSqlCatalogue.py 1110 2016-06-15 19:45:26Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, re, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class CreerContrainteIntegriteSqlCatalogue(object):
#*******************************************************************************************
    """
    Permet de valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        
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
        self.sqlInsert = "Insert into CONTRAINTE_INTEGRITE_SQL (ETAMPE,DT_C,DT_M,GROUPE,DESCRIPTION,MESSAGE,REQUETE_SQL) Values ('MPOTHIER',SYSDATE,SYSDATE" 
        
        #Initialiser les attributs sans contrainte d'intégrité.
        self.sqlErr = []
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        
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
        if (len(attribut) == 0):
            raise Exception ('Paramètre obligatoire manquant: attribut')
        
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
    def validerDomaineAttributClasse(self, cat, cls, codeGen, att, type, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut codé pour une classe de la Géodatabase en fonction du domaine contenu dans le catalogue.
        
        Paramètres:
        -----------
        cat         : Numéro du catalogue sans description.
        cls         : Nom de la classe du catalogue à valider.
        codeGen     : Code générique de la classe du catalogue à valider.
        att         : Nom d'attribut du catalogue à valider.
        type        : Type d'attribut à valider.
        codeSpec    : Nom de l'attribut de la Géodatabase contenant le code spécifique.
        
        Variables:
        ----------
        sql             : Requête SQL à exécuter.
        code            : Code spécifique à traiter.
        codeResultat    : Liste des codes spécifiques à traiter.
        relResultat     : Contient le numéro de la relation pour extraire l'expression régulière.
        expResultat     : Contient l'expression régulière à valider.
        val             : Valeur en erreur.
        valResultat     : Liste des valeurs en erreurs.
        groupe          : Groupe dans lequel la contraite d'intégrité est située.
        description     : Description de la contrainte d'intégrité.
        message         : Message indiquant comment corriger l'erreur.
        """
        
        #Créer la SQL pour définir la liste des codes spécifiques possédants des expressions régulières
        sql =  (" select distinct B.feat_type_code_bd"
                "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk and E.const_param_fk=116089"
                "   and (B.feat_type_name_database='" + cls + "' or B.feat_type_code_bd=" + codeGen + ") and F.p_value='" + att + "'"
                " order by F.p_value")
        #arcpy.AddMessage(sql)
        
        #Exécuter la SQL
        codeResultat = self.BDG.query(sql)
        
        #Vérifier si l'attribut possède une expression régulière à valider
        if codeResultat:       
            #Compter les SQL de contrainte d'intégrité
            self.nbSql = self.nbSql + 1
            
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-EXPRESSION_REGULIERE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " via l''expression régulière du catalogue."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de respecter l''expression régulière du catalogue."
        
            #Traiter tous les codes spécifiques qui possèdent une expression régulière à valider
            for code in codeResultat:
                #Afficher le code spécifique et l'attribut à valider
                #arcpy.AddMessage("--" + str(code[0]) + ":" + att)  
                
                #Créer la SQL pour extraire le nom du code spécifique et le numéro de relation
                sql =  (" select D.relation_id, B.feat_type_code_bd, B.feat_type_name_fr"
                        "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                        " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                        "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                        "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk"
                        "   and (B.feat_type_code_bd=" + str(code[0]) + "or B.feat_type_code_bd=" + codeGen + ") AND F.p_value='" + att + "'")
                #arcpy.AddMessage(sql)
                
                #Exécuter la SQL
                relResultat = self.BDG.query(sql)
                
                #Vérifier le résultat
                if relResultat:
                    #Afficher la valeur de l'attribut à valider
                    #arcpy.AddMessage("      " + str(relResultat[0][1]) + ":" + relResultat[0][2] + " (rel=" + str(relResultat[0][0]) + ")")
                    
                    #Créer la SQL pour extraire l'expression régulière du code spécifique
                    sql =  (" select F.p_value"
                            "  from relation D, parameter E, p_value F"
                            " where D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk and E.const_param_fk=116090 and D.relation_id=" + str(relResultat[0][0]))
                    #arcpy.AddMessage(sql)
                    
                    #Exécuter la SQL
                    expResultat = self.BDG.query(sql)
                    
                    #Vérifier le résultat
                    if expResultat:
                        #Vérifier si le type est un caractère
                        if "CARAC" in type.upper():
                            #Définir la requête SQL
                            sql =("SELECT COUNT(*)," + att + " "
                                  "  FROM bdg_dba." + cls + " "
                                  " WHERE NOT REGEXP_LIKE(NVL(" + att + ",''-''), ''" + expResultat[0][0] + "'')")
                        else:
                            #Définir la requête SQL
                            sql =("SELECT COUNT(*)," + att + " "
                                  "  FROM bdg_dba." + cls + " "
                                  " WHERE NOT REGEXP_LIKE(NVL(" + att + ",-9999), ''" + expResultat[0][0] + "'')")
                        
                        #Vérifier si le codeSpec n'est pas générique
                        if str(code[0]) <> str(codeGen):
                            #Ajouter le code spécifique dans la requête SQL
                            sql = sql + "  AND " + codeSpec + "=" + str(code[0]) + " "
                        
                        #Ajouter le regroupement
                        sql = sql + " GROUP BY " + att + " ORDER BY " + att
                        
                        #Afficher la valeur de l'attribut à valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un PLANIMETRIC_ACCURACY
        elif att == "PLANIMETRIC_ACCURACY" or att == "ALTIMETRIC_ACCURACY":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-PRECISION"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin d''avoir une précision > 0."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin d''avoir une précision > 0."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",-9999), ''^-1|[1-9]|[1-9]\d|100$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un VALIDITY_DATE ou un CREATION_DATE ou un REVISION_DATE
        elif att == "VALIDITY_DATE" or att == "CREATION_DATE" or att == "REVISION_DATE" or att == "IDDATE":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-DATE_TEXTE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les spécifications d''une date texte (exemple:20151230)."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de correspondre à une date texte sous la forme pour AAAAMMJJ ou le mois et jour sont optionels."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^(19[4-9]\d|20[0-1]\d)(0[1-9]|1[0-2])?([0-2]\d|3[0-1])?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est une Latitude
        elif "LAT_" in att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-LATITUDE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les spécifications d''une latitude."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre à une latitude."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",0), ''^[4-8][0-9](\.(25|5|75))?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est une Longitude
        elif "LON_" in att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-LONGITUDE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les spécifications d''une Longitude."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre à une Longitude."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",0), ''^-(1[0-4][0-9]|[4-9][0-9])(\.(25|5|75))?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un MERIDIEN_CENTRAL
        elif att == "MERIDIEN_CENTRAL":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-LONGITUDE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les spécifications d''une Longitude."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre à une Longitude."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",0), ''^-(1[0-9][0-9]|[5-9][1,3,5,7,9])$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un DATASET_NAME
        elif att == "DATASET_NAME":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-DECOUPAGE_SNRC"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les spécifications d''un identifiant de découpage SNRC."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre à un identifiant de découpage SNRC."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^\d\d\d[A-P]0[1-9]|1[0-6]$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un SNRC
        elif "SNRC" in att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-SNRC_REFERENCE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les spécifications d''un identifiant de découpage SNRC."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre à un identifiant de découpage SNRC."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + " NOT IN (SELECT DATASET_NAME FROM " + cls + ")"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un ZT_ID
        elif att == "ZT_ID":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-ZONE_TRANSACTION"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les spécifications d''un identifiant de ZT."
            #Message indiquant comment corriger l'erreur.
            message = "Générer un nouvel identifiant de ZT pour la valeur de l''attribut " + att + " de la classe " + cls + "."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^(NC\d\d\d\d\d_)?\d\d\d[A-P]0[1-9]|1[0-6]_BDG_\d{14}$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique de 36 caractères
        elif att == "MD_ID":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-IDENTIFIANT_UNIQUE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle, ait une longueur de 36 et sans espace vide."
            #Message indiquant comment corriger l'erreur.
            message = "Générer un nouvel identifiant unique pour la valeur de l''attribut " + att + " de la classe " + cls + "."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[a-fA-F0-9]{8}(-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est une adresse WEB
        elif att == "REFERENCE_WEB":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-ADRESSE_WEB"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et correspond à une adresse WEB."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin de correspondre à une adresse WEB."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^(http://)'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique
        elif ("_ID" in att and "CARAC" in type.upper()) or "RIVID" in att or "LAKEID" in att or att == "NID":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-IDENTIFIANT_UNIQUE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle, ait une longueur de 32 et sans espace vide."
            #Message indiquant comment corriger l'erreur.
            message = "Générer un nouvel identifiant unique pour la valeur de l''attribut " + att + " de la classe " + cls + "."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[a-fA-F0-9]{32}$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique
        elif att == "ID_CANAC":
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-IDENTIFIANT_CANAC"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle, ait une longueur de 4 et sans espace vide."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de correspondre aux spécifications d''un identifiant CANAC."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[C|S][A-Z][A-Z0-9][A-Z0-9]$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique
        elif "ID_LOCAL" in att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-IDENTIFIANT_NUMERIQUE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la table GES_TOPONYMIC_INFO."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin qu''il soit inclus dans la table GES_TOPONYMIC_INFO."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[1-9]([0-9]{2})([0-9])?([0-9])?([0-9])?([0-9])?([0-9])?([0-9])?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un identifiant unique
        elif "GEONAMEDB" == att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-NAMEID_1_NAMEID_2"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin de s''assurer que le NAMEID_1 ou NAMEID_2 soit présent."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin que le NAMEID_1 ou NAMEID_2 soit présent."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + " IS NOT NULL AND (NAMEID_1 IS NULL AND NAMEID_2 IS NULL)"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un identifiant unique
        elif "GEONAMEDB_LEGAL" in att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-NOM_LEGAL"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la liste permise."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin qu''il soit inclus dans la liste permise."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NVL(" + att + ",''-'') NOT IN (''CITS-MUNI-LEGAL'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")

        #Si c'est un identifiant unique
        elif "NAMEID" in att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-IDENTIFIANT_REFERENCE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la table GES_TOPONYMIC_INFO."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin qu''il soit inclus dans la table GES_TOPONYMIC_INFO."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + "='0ca095ca849c20c3331d2ef43a41a056'"
                  " GROUP BY " + att + " ORDER BY " + att + ";")
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(sql)

        #Si c'est un identifiant unique
        elif "NAMEID_" in att:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-IDENTIFIANT_REFERENCE"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la table GES_TOPONYMIC_INFO."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin qu''il soit inclus dans la table GES_TOPONYMIC_INFO."
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NVL(" + att + ",''-'') NOT IN (SELECT DISTINCT NAMEID  FROM bdg_dba.GES_TOPONYMIC_INFO)"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #si l'attribut ne possède pas de validation
        else:
            #Groupe dans lequel la contraite d'intégrité est située.
            groupe = "BDG-" + att + "-SANS_VALIDATION"
            #Description de la contrainte d'intégrité
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin de respecter les valeurs permises."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de respecter les valeurs permises."

            #Définir la requête SQL de base
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + " IS NULL"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            #arcpy.AddMessage(" ")
            #arcpy.AddWarning(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
            #Conserver la SQL de l'attribut sans validation
            self.sqlErr.append(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerDomaineAttributCodeClasse(self, cat, cls, att, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut codé pour une classe de la Géodatabase en fonction du domaine contenu dans le catalogue.
        
        Paramètres:
        -----------
        cat         : Numéro du catalogue sans description.
        cls         : Nom de la classe du catalogue à valider.
        att         : Nom d'un attribut du catalogue à valider.
        workspace   : Nom de la géodatabase contenant les données à valider.
        codeSpec    : Nom de l'attribut de la Géodatabase contenant le code spécifique.
        
        Variables:
        ----------
        sql             : Requête SQL à exécuter.
        val             : Valeur d'attribut codé du catalogue.
        valResultat     : Ensemble des valeurs d'attributs codés du catalogue.
        listeValeur     : Liste de toutes les valeurs permises de l'attribut traité.
        listeVal        : Liste de toutes les valeurs permises de l'attribut traité pour un code spécifique.
        code            : Code spécifique à traité.
        codeResultat    : Liste des codes spécifiques à traités.
        nbVal           : Nombre de valeurs en erreur.
        groupe          : Groupe dans lequel la contraite d'intégrité est située.
        description     : Description de la contrainte d'intégrité.
        message         : Message indiquant comment corriger l'erreur.
        """
        
        #Initialiser la liste des domaines
        domaines = {}
        
        #Groupe dans lequel la contraite d'intégrité est située.
        groupe = "BDG-" + att + "-ATTRIBUT_CODE"
        #Description de la contrainte d'intégrité
        description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " via les attributs codés du catalogue."
        #Message indiquant comment corriger l'erreur.
        message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de respecter les attributs codés du catalogue."
        
        #Créer la SQL pour définir la liste des codes spécifiques pour chaque attribut codé
        sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk AND B.FEAT_TYPE_CLASS_TYPE=20014"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "'"
               " order by B.feat_type_code_bd")
        #arcpy.AddMessage(sql)
        
        #Exécuter la SQL
        codeResultat = self.BDG.query(sql)
        
        #Créer la liste des attributs codés pour chaque code spécifique
        for code in codeResultat:
            #Afficher les codes traités
            #arcpy.AddMessage("--" + str(code[0]) + ":" + str(code[1]))
            
            #Créer la SQL pour définir l'ensemble des valeurs du catalogue
            sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                   " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "' and B.feat_type_code_bd='" + str(code[0]) + "'"
                   " order by E.ATTR_VALUE_INTERNAL_CODE")
            #arcpy.AddMessage(sql)
            
            #Exécuter la SQL
            valResultat = self.BDG.query(sql)
            
            #Vérifier le résultat
            if valResultat:
                #Créer la SQL pour extraire l'expression régulière du code spécifique
                sql =  ("select F.p_value"
                        "  from relation D, parameter E, p_value F"
                        " where D.relation_id=E.rel_id_fk"
                        "   and E.parameter_id=F.parameter_fk"
                        "   and E.const_param_fk=116090"
                        "   and D.relation_id in ("
                                "select D.relation_id"
                                "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                                " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                                "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                                "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk"
                                "   and B.feat_type_code_bd=" + str(code[0]) + " AND F.p_value='" + att + "')")
                #arcpy.AddMessage(sql)
                
                #Exécuter la SQL
                expResultat = self.BDG.query(sql)

                #Définir l'expression régulière du code spécifique par défaut
                expression = "\d"
                #Vérifier la présence d'une expression régulière
                if len(expResultat) == 1:
                    #Définir l'expression régulière du code spécifique
                    expression = expResultat[0][0]
                #arcpy.AddMessage("Expression reguliere: " + expression + ", Code: " + str(code[0]))
                
                #Initialiser la liste des valeurs
                listeVal = ""
                #Initialiser la liste des valeurs
                listeValExp = ""
                
                #Construire la liste des valeurs codées
                for val in valResultat:
                    #Ajouter le code à la liste 
                    listeVal = listeVal + str(val[0]) + ","
                    #Vérifier si la valeur respecte l'expression régulière
                    if re.match(expression, str(val[0])):
                        #Ajouter le code à la liste 
                        listeValExp = listeValExp + str(val[0]) + ","
                
                #Enlever la dernière virgule
                listeVal = listeVal[:-1]
                #Enlever la dernière virgule
                listeValExp = listeValExp[:-1]
                #Vérifier la présence de la liste selon l'expression régulière
                if len(listeValExp) > 0:
                    #Réfinir la liste des valeurs
                    listeVal = listeValExp
            
                #Vérifier si le domaine est déjà présent
                if domaines.has_key(listeVal):
                    #Extraire la liste des codes du domaine
                    codes = domaines[listeVal]
                    #Ajouter le code spécifique dans la liste des codes du domaine
                    codes.append(code[0])
                    #Redéfinir la liste des codes du domaine
                    domaines[listeVal] = codes
                #Si aucun domaine présent
                else:
                    #Initialiser la liste des codes
                    codes = []
                    #Ajouter le code spécifique dans la liste des codes du domaine
                    codes.append(code[0])
                    #Définir la liste des codes du domaine
                    domaines[listeVal] = codes
        
        #Vérifier si plusieurs domaines
        if len(domaines) > 1:
            #Créer la requête pour chaque domaine
            for dom,codes in domaines.iteritems():
                #Compter les SQL de contrainte d'intégrité
                self.nbSql = self.nbSql + 1
                
                #Définir la requête SQL
                sql =("SELECT COUNT(*)," + att + " "
                      "  FROM bdg_dba." + cls + " "
                      " WHERE NVL(" + att + ",-9999) NOT IN (" + dom + ") AND " + codeSpec + " IN (" + str(codes)[1:-1] + ")"
                      " GROUP BY " + att + " ORDER BY " + att)
                
                #Afficher la valeur de l'attribut à valider
                arcpy.AddMessage(" ")
                arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si seulement un domaine
        else:
            #Compter les SQL de contrainte d'intégrité
            self.nbSql = self.nbSql + 1
                
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NVL(" + att + ",-9999) NOT IN (" + domaines.keys()[0] + ")"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Sortir
        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requête SQL à exécuter.
        cat             : Numéro du catalogue sans description.
        cls             : Classe à traiter.
        clsResultat     : Liste des classes à traiter.
        att             : Attribut à traiter.
        attResultat     : Liste des attributs à traiter.
        """
        
        #Vérification de la présence des paramètres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, attribut)
               
        #Vérifier la connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Définir le numéro de catalogue
        cat = catalogue.split(":")[0]
        
        #Valider les valeurs des paramètres
        self.validerValeurParam(cat)
        
        #Envoyer un message
        arcpy.AddMessage("- Créer les contraintes d'intégrité des attributs de chaque classe")
        
        #Créer la SQL pour extraire le code générique de chaque classe à valider
        sql =  (" select distinct B.feat_type_name_database, substr(to_char(B.feat_type_code_bd),1,3)||'0009'"
                "  from feat_catalogue A, feat_type B"
                " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_name_database in ('" + classe.replace(",","','") + "')"
                " order by B.feat_type_name_database")
        #arcpy.AddMessage(sql)
        
        #Exécuter la SQL
        clsResultat = self.BDG.query(sql)
        
        #Traiter toutes les classes
        for cls in clsResultat:
            #Afficher le nom de la classe avec son code générique
            #arcpy.AddMessage(" ")
            #arcpy.AddMessage("--" + cls[0] + ":" + cls[1])
            
            #Vérifier si l'attribut CODE_SPEC est spécifié
            if "CODE_SPEC" in attribut:
                #Groupe dans lequel la contraite d'intégrité est située.
                groupe = "BDG-CODE_SPEC-ATTRIBUT_CODE"
                #Description de la contrainte d'intégrité
                description = "Valider la valeur d''attribut CODE_SPEC de la classe " + cls[0] + " via les attributs codés du catalogue."
                #Message indiquant comment corriger l'erreur.
                message = "Corriger la valeur de l''attribut CODE_SPEC de la classe " + cls[0] + " afin de respecter les attributs codés du catalogue."
                
                #Créer la SQL pour extraire les codes spécifiques
                sql =  (" select B.feat_type_code_bd"
                        "  from feat_catalogue A, feat_type B"
                        " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk  AND B.FEAT_TYPE_CLASS_TYPE=20014"
                        "   and B.feat_type_name_database='" + cls[0] + "'"
                        " order by B.feat_type_code_bd")
                #arcpy.AddMessage(sql)
                
                #Exécuter la SQL
                valResultat = self.BDG.query(sql)
                
                #Vérifier si un résultat est présent
                if valResultat:
                    #Compter les SQL de contrainte d'intégrité
                    self.nbSql = self.nbSql + 1
                    
                    #Initialiser la liste des valeurs
                    listeValeur = ""
                    
                    #Construire la liste des valeurs
                    for val in valResultat:
                        listeValeur = listeValeur + str(val[0]) + ","
                    listeValeur = listeValeur[:-1]
                    
                    #Définir la requête SQL
                    sql =("SELECT COUNT(*),CODE_SPEC"
                          "  FROM bdg_dba." + cls[0] + " "
                          " WHERE NVL(CODE_SPEC,-9999) NOT IN (" + listeValeur + ")"
                          " GROUP BY CODE_SPEC ORDER BY CODE_SPEC")
                    
                    #Afficher la valeur de l'attribut à valider
                    arcpy.AddMessage(" ")
                    arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
            #Créer la SQL pour extraire les attributs de la classe
            sql = (" SELECT DISTINCT D.FEAT_ATTR_NAME_DATABASE, D.FEAT_ATTR_NAME_FR, D.FEAT_ATTR_DATA_TYPE, D.FEAT_ATTR_DOMAIN_TYPE"
                   "   FROM FEAT_CATALOGUE A,FEAT_TYPE B,RELATION_FEAT_ATTR C,FEAT_ATTR D"
                   "  WHERE A.FEAT_CATAL_TYPE=" + cat + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"
                   "   AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID"
                   "   AND B.FEAT_TYPE_NAME_DATABASE='" + cls[0] + "'"
                   "   AND D.FEAT_ATTR_NAME_DATABASE IN ('" + attribut.replace(",","','") + "')"
                   " ORDER BY D.FEAT_ATTR_NAME_DATABASE")
            #arcpy.AddMessage(sql)
            
            #Exécuter la SQL
            attResultat = self.BDG.query(sql)
            
            #Traiter tous les attributs de laclasse
            for att in attResultat:
                #Afficher le nom de l'attribut, sa description et son type
                #arcpy.AddMessage("--" + str(att[0]) + ":" + str(att[1]) + ":" + str(att[2]) + ":" + str(att[3]))
                
                #Vérifier si l'attribut est de type codé
                if str(att[3]) == "-1":
                    #Valider les valeurs des attributs codés pour une classe en fonction des domaines du catalogue
                    self.validerDomaineAttributCodeClasse(cat, cls[0], att[0])
                    
                #Sinon on considère une expression régulière
                else:
                    #Valider les valeurs des attributs pour une classe en fonction des expressions régulières du catalogue
                    self.validerDomaineAttributClasse(cat, cls[0], cls[1], att[0], att[2])
        
        #Afficher le nombre d'attributs à traiter
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre d'attributs à traiter : " + str(len(attribut.split(","))))
        
        #Afficher le nombre de SQL des contrainte d'intégrité.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre de SQL des contraintes d'intégrité : " + str(self.nbSql))
        
        #Afficher les attrributs sans contrainte d'intégrité.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre d'attributs sans contrainte d'intégrité : " + str(len(self.sqlErr)))
        for sql in self.sqlErr:
            arcpy.AddMessage(" ")
            arcpy.AddWarning(sql)
        
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
        attribut    = ""
        
        #Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            classe = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            attribut = sys.argv[4].upper().replace(";",",").replace("'","")
        
        #Définir l'objet pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        oCreerContrainteIntegriteSqlCatalogue = CreerContrainteIntegriteSqlCatalogue()
        
        #Exécuter le traitement pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        oCreerContrainteIntegriteSqlCatalogue.executer(env, catalogue, classe, attribut)
            
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