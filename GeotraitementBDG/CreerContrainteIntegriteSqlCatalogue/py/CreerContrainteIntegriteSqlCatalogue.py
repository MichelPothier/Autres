#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CreerContrainteIntegriteSqlCatalogue.py
# Auteur    : Michel Pothier
# Date      : 09 septembre 2015

"""
    Application qui permet de valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.

    Le catalogue contient des valeurs cod�es et/ou des expressions r�guli�res pour chaque attribut d'un code sp�cifique.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue et sa description.
                            d�faut = 1:BDG
    classe          OB      Liste des noms de classe du catalogue � valider.
                            d�faut = <Toutes les classes pr�sentes dans le catalogue>
    attribut        OB      Liste des noms d'attribut du catalogue � valider.
                            d�faut = <Tous les attributs pr�sents dans le catalogue>
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class CreerContrainteIntegriteSqlCatalogue(object):
#*******************************************************************************************
    """
    Permet de valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        
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
        self.sqlInsert = "Insert into CONTRAINTE_INTEGRITE_SQL (ETAMPE,DT_C,DT_M,GROUPE,DESCRIPTION,MESSAGE,REQUETE_SQL) Values ('MPOTHIER',SYSDATE,SYSDATE" 
        
        #Initialiser les attributs sans contrainte d'int�grit�.
        self.sqlErr = []
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        
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
        if (len(attribut) == 0):
            raise Exception ('Param�tre obligatoire manquant: attribut')
        
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
    def validerDomaineAttributClasse(self, cat, cls, codeGen, att, type, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut cod� pour une classe de la G�odatabase en fonction du domaine contenu dans le catalogue.
        
        Param�tres:
        -----------
        cat         : Num�ro du catalogue sans description.
        cls         : Nom de la classe du catalogue � valider.
        codeGen     : Code g�n�rique de la classe du catalogue � valider.
        att         : Nom d'attribut du catalogue � valider.
        type        : Type d'attribut � valider.
        codeSpec    : Nom de l'attribut de la G�odatabase contenant le code sp�cifique.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        code            : Code sp�cifique � traiter.
        codeResultat    : Liste des codes sp�cifiques � traiter.
        relResultat     : Contient le num�ro de la relation pour extraire l'expression r�guli�re.
        expResultat     : Contient l'expression r�guli�re � valider.
        val             : Valeur en erreur.
        valResultat     : Liste des valeurs en erreurs.
        groupe          : Groupe dans lequel la contraite d'int�grit� est situ�e.
        description     : Description de la contrainte d'int�grit�.
        message         : Message indiquant comment corriger l'erreur.
        """
        
        #Cr�er la SQL pour d�finir la liste des codes sp�cifiques poss�dants des expressions r�guli�res
        sql =  (" select distinct B.feat_type_code_bd"
                "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk and E.const_param_fk=116089"
                "   and (B.feat_type_name_database='" + cls + "' or B.feat_type_code_bd=" + codeGen + ") and F.p_value='" + att + "'"
                " order by F.p_value")
        #arcpy.AddMessage(sql)
        
        #Ex�cuter la SQL
        codeResultat = self.BDG.query(sql)
        
        #V�rifier si l'attribut poss�de une expression r�guli�re � valider
        if codeResultat:       
            #Compter les SQL de contrainte d'int�grit�
            self.nbSql = self.nbSql + 1
            
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-EXPRESSION_REGULIERE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " via l''expression r�guli�re du catalogue."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de respecter l''expression r�guli�re du catalogue."
        
            #Traiter tous les codes sp�cifiques qui poss�dent une expression r�guli�re � valider
            for code in codeResultat:
                #Afficher le code sp�cifique et l'attribut � valider
                #arcpy.AddMessage("--" + str(code[0]) + ":" + att)  
                
                #Cr�er la SQL pour extraire le nom du code sp�cifique et le num�ro de relation
                sql =  (" select D.relation_id, B.feat_type_code_bd, B.feat_type_name_fr"
                        "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                        " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                        "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                        "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk"
                        "   and (B.feat_type_code_bd=" + str(code[0]) + "or B.feat_type_code_bd=" + codeGen + ") AND F.p_value='" + att + "'")
                #arcpy.AddMessage(sql)
                
                #Ex�cuter la SQL
                relResultat = self.BDG.query(sql)
                
                #V�rifier le r�sultat
                if relResultat:
                    #Afficher la valeur de l'attribut � valider
                    #arcpy.AddMessage("      " + str(relResultat[0][1]) + ":" + relResultat[0][2] + " (rel=" + str(relResultat[0][0]) + ")")
                    
                    #Cr�er la SQL pour extraire l'expression r�guli�re du code sp�cifique
                    sql =  (" select F.p_value"
                            "  from relation D, parameter E, p_value F"
                            " where D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk and E.const_param_fk=116090 and D.relation_id=" + str(relResultat[0][0]))
                    #arcpy.AddMessage(sql)
                    
                    #Ex�cuter la SQL
                    expResultat = self.BDG.query(sql)
                    
                    #V�rifier le r�sultat
                    if expResultat:
                        #V�rifier si le type est un caract�re
                        if "CARAC" in type.upper():
                            #D�finir la requ�te SQL
                            sql =("SELECT COUNT(*)," + att + " "
                                  "  FROM bdg_dba." + cls + " "
                                  " WHERE NOT REGEXP_LIKE(NVL(" + att + ",''-''), ''" + expResultat[0][0] + "'')")
                        else:
                            #D�finir la requ�te SQL
                            sql =("SELECT COUNT(*)," + att + " "
                                  "  FROM bdg_dba." + cls + " "
                                  " WHERE NOT REGEXP_LIKE(NVL(" + att + ",-9999), ''" + expResultat[0][0] + "'')")
                        
                        #V�rifier si le codeSpec n'est pas g�n�rique
                        if str(code[0]) <> str(codeGen):
                            #Ajouter le code sp�cifique dans la requ�te SQL
                            sql = sql + "  AND " + codeSpec + "=" + str(code[0]) + " "
                        
                        #Ajouter le regroupement
                        sql = sql + " GROUP BY " + att + " ORDER BY " + att
                        
                        #Afficher la valeur de l'attribut � valider
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un PLANIMETRIC_ACCURACY
        elif att == "PLANIMETRIC_ACCURACY" or att == "ALTIMETRIC_ACCURACY":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-PRECISION"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin d''avoir une pr�cision > 0."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin d''avoir une pr�cision > 0."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",-9999), ''^-1|[1-9]|[1-9]\d|100$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un VALIDITY_DATE ou un CREATION_DATE ou un REVISION_DATE
        elif att == "VALIDITY_DATE" or att == "CREATION_DATE" or att == "REVISION_DATE" or att == "IDDATE":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-DATE_TEXTE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les sp�cifications d''une date texte (exemple:20151230)."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de correspondre � une date texte sous la forme pour AAAAMMJJ ou le mois et jour sont optionels."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^(19[4-9]\d|20[0-1]\d)(0[1-9]|1[0-2])?([0-2]\d|3[0-1])?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est une Latitude
        elif "LAT_" in att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-LATITUDE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les sp�cifications d''une latitude."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre � une latitude."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",0), ''^[4-8][0-9](\.(25|5|75))?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est une Longitude
        elif "LON_" in att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-LONGITUDE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les sp�cifications d''une Longitude."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre � une Longitude."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",0), ''^-(1[0-4][0-9]|[4-9][0-9])(\.(25|5|75))?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un MERIDIEN_CENTRAL
        elif att == "MERIDIEN_CENTRAL":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-LONGITUDE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les sp�cifications d''une Longitude."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre � une Longitude."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",0), ''^-(1[0-9][0-9]|[5-9][1,3,5,7,9])$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un DATASET_NAME
        elif att == "DATASET_NAME":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-DECOUPAGE_SNRC"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les sp�cifications d''un identifiant de d�coupage SNRC."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre � un identifiant de d�coupage SNRC."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^\d\d\d[A-P]0[1-9]|1[0-6]$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un SNRC
        elif "SNRC" in att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-SNRC_REFERENCE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les sp�cifications d''un identifiant de d�coupage SNRC."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut  " + att + " de la classe " + cls + " afin de correspondre � un identifiant de d�coupage SNRC."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + " NOT IN (SELECT DATASET_NAME FROM " + cls + ")"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un ZT_ID
        elif att == "ZT_ID":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-ZONE_TRANSACTION"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il respecte les sp�cifications d''un identifiant de ZT."
            #Message indiquant comment corriger l'erreur.
            message = "G�n�rer un nouvel identifiant de ZT pour la valeur de l''attribut " + att + " de la classe " + cls + "."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^(NC\d\d\d\d\d_)?\d\d\d[A-P]0[1-9]|1[0-6]_BDG_\d{14}$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique de 36 caract�res
        elif att == "MD_ID":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-IDENTIFIANT_UNIQUE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle, ait une longueur de 36 et sans espace vide."
            #Message indiquant comment corriger l'erreur.
            message = "G�n�rer un nouvel identifiant unique pour la valeur de l''attribut " + att + " de la classe " + cls + "."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[a-fA-F0-9]{8}(-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est une adresse WEB
        elif att == "REFERENCE_WEB":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-ADRESSE_WEB"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et correspond � une adresse WEB."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin de correspondre � une adresse WEB."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^(http://)'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique
        elif ("_ID" in att and "CARAC" in type.upper()) or "RIVID" in att or "LAKEID" in att or att == "NID":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-IDENTIFIANT_UNIQUE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle, ait une longueur de 32 et sans espace vide."
            #Message indiquant comment corriger l'erreur.
            message = "G�n�rer un nouvel identifiant unique pour la valeur de l''attribut " + att + " de la classe " + cls + "."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[a-fA-F0-9]{32}$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique
        elif att == "ID_CANAC":
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-IDENTIFIANT_CANAC"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle, ait une longueur de 4 et sans espace vide."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de correspondre aux sp�cifications d''un identifiant CANAC."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[C|S][A-Z][A-Z0-9][A-Z0-9]$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si c'est un identifiant unique
        elif "ID_LOCAL" in att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-IDENTIFIANT_NUMERIQUE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la table GES_TOPONYMIC_INFO."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin qu''il soit inclus dans la table GES_TOPONYMIC_INFO."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NOT REGEXP_LIKE (NVL(" + att + ",''-''), ''^[1-9]([0-9]{2})([0-9])?([0-9])?([0-9])?([0-9])?([0-9])?([0-9])?$'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un identifiant unique
        elif "GEONAMEDB" == att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-NAMEID_1_NAMEID_2"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin de s''assurer que le NAMEID_1 ou NAMEID_2 soit pr�sent."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin que le NAMEID_1 ou NAMEID_2 soit pr�sent."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + " IS NOT NULL AND (NAMEID_1 IS NULL AND NAMEID_2 IS NULL)"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Si c'est un identifiant unique
        elif "GEONAMEDB_LEGAL" in att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-NOM_LEGAL"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la liste permise."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin qu''il soit inclus dans la liste permise."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NVL(" + att + ",''-'') NOT IN (''CITS-MUNI-LEGAL'')"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")

        #Si c'est un identifiant unique
        elif "NAMEID" in att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-IDENTIFIANT_REFERENCE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la table GES_TOPONYMIC_INFO."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin qu''il soit inclus dans la table GES_TOPONYMIC_INFO."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + "='0ca095ca849c20c3331d2ef43a41a056'"
                  " GROUP BY " + att + " ORDER BY " + att + ";")
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(sql)

        #Si c'est un identifiant unique
        elif "NAMEID_" in att:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-IDENTIFIANT_REFERENCE"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin qu''il ne soit pas nulle et soit inclus dans la table GES_TOPONYMIC_INFO."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + "afin qu''il soit inclus dans la table GES_TOPONYMIC_INFO."
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NVL(" + att + ",''-'') NOT IN (SELECT DISTINCT NAMEID  FROM bdg_dba.GES_TOPONYMIC_INFO)"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #si l'attribut ne poss�de pas de validation
        else:
            #Groupe dans lequel la contraite d'int�grit� est situ�e.
            groupe = "BDG-" + att + "-SANS_VALIDATION"
            #Description de la contrainte d'int�grit�
            description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " afin de respecter les valeurs permises."
            #Message indiquant comment corriger l'erreur.
            message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de respecter les valeurs permises."

            #D�finir la requ�te SQL de base
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE " + att + " IS NULL"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
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
        Permet de valider les valeurs d'un attribut cod� pour une classe de la G�odatabase en fonction du domaine contenu dans le catalogue.
        
        Param�tres:
        -----------
        cat         : Num�ro du catalogue sans description.
        cls         : Nom de la classe du catalogue � valider.
        att         : Nom d'un attribut du catalogue � valider.
        workspace   : Nom de la g�odatabase contenant les donn�es � valider.
        codeSpec    : Nom de l'attribut de la G�odatabase contenant le code sp�cifique.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        val             : Valeur d'attribut cod� du catalogue.
        valResultat     : Ensemble des valeurs d'attributs cod�s du catalogue.
        listeValeur     : Liste de toutes les valeurs permises de l'attribut trait�.
        listeVal        : Liste de toutes les valeurs permises de l'attribut trait� pour un code sp�cifique.
        code            : Code sp�cifique � trait�.
        codeResultat    : Liste des codes sp�cifiques � trait�s.
        nbVal           : Nombre de valeurs en erreur.
        groupe          : Groupe dans lequel la contraite d'int�grit� est situ�e.
        description     : Description de la contrainte d'int�grit�.
        message         : Message indiquant comment corriger l'erreur.
        """
        
        #Initialiser la liste des domaines
        domaines = {}
        
        #Groupe dans lequel la contraite d'int�grit� est situ�e.
        groupe = "BDG-" + att + "-ATTRIBUT_CODE"
        #Description de la contrainte d'int�grit�
        description = "Valider la valeur d''attribut " + att + " de la classe " + cls + " via les attributs cod�s du catalogue."
        #Message indiquant comment corriger l'erreur.
        message = "Corriger la valeur de l''attribut " + att + " de la classe " + cls + " afin de respecter les attributs cod�s du catalogue."
        
        #Cr�er la SQL pour d�finir la liste des codes sp�cifiques pour chaque attribut cod�
        sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk AND B.FEAT_TYPE_CLASS_TYPE=20014"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "'"
               " order by B.feat_type_code_bd")
        #arcpy.AddMessage(sql)
        
        #Ex�cuter la SQL
        codeResultat = self.BDG.query(sql)
        
        #Cr�er la liste des attributs cod�s pour chaque code sp�cifique
        for code in codeResultat:
            #Afficher les codes trait�s
            #arcpy.AddMessage("--" + str(code[0]) + ":" + str(code[1]))
            
            #Cr�er la SQL pour d�finir l'ensemble des valeurs du catalogue
            sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                   " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "' and B.feat_type_code_bd='" + str(code[0]) + "'"
                   " order by E.ATTR_VALUE_INTERNAL_CODE")
            #arcpy.AddMessage(sql)
            
            #Ex�cuter la SQL
            valResultat = self.BDG.query(sql)
            
            #V�rifier le r�sultat
            if valResultat:
                #Cr�er la SQL pour extraire l'expression r�guli�re du code sp�cifique
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
                
                #Ex�cuter la SQL
                expResultat = self.BDG.query(sql)

                #D�finir l'expression r�guli�re du code sp�cifique par d�faut
                expression = "\d"
                #V�rifier la pr�sence d'une expression r�guli�re
                if len(expResultat) == 1:
                    #D�finir l'expression r�guli�re du code sp�cifique
                    expression = expResultat[0][0]
                #arcpy.AddMessage("Expression reguliere: " + expression + ", Code: " + str(code[0]))
                
                #Initialiser la liste des valeurs
                listeVal = ""
                #Initialiser la liste des valeurs
                listeValExp = ""
                
                #Construire la liste des valeurs cod�es
                for val in valResultat:
                    #Ajouter le code � la liste 
                    listeVal = listeVal + str(val[0]) + ","
                    #V�rifier si la valeur respecte l'expression r�guli�re
                    if re.match(expression, str(val[0])):
                        #Ajouter le code � la liste 
                        listeValExp = listeValExp + str(val[0]) + ","
                
                #Enlever la derni�re virgule
                listeVal = listeVal[:-1]
                #Enlever la derni�re virgule
                listeValExp = listeValExp[:-1]
                #V�rifier la pr�sence de la liste selon l'expression r�guli�re
                if len(listeValExp) > 0:
                    #R�finir la liste des valeurs
                    listeVal = listeValExp
            
                #V�rifier si le domaine est d�j� pr�sent
                if domaines.has_key(listeVal):
                    #Extraire la liste des codes du domaine
                    codes = domaines[listeVal]
                    #Ajouter le code sp�cifique dans la liste des codes du domaine
                    codes.append(code[0])
                    #Red�finir la liste des codes du domaine
                    domaines[listeVal] = codes
                #Si aucun domaine pr�sent
                else:
                    #Initialiser la liste des codes
                    codes = []
                    #Ajouter le code sp�cifique dans la liste des codes du domaine
                    codes.append(code[0])
                    #D�finir la liste des codes du domaine
                    domaines[listeVal] = codes
        
        #V�rifier si plusieurs domaines
        if len(domaines) > 1:
            #Cr�er la requ�te pour chaque domaine
            for dom,codes in domaines.iteritems():
                #Compter les SQL de contrainte d'int�grit�
                self.nbSql = self.nbSql + 1
                
                #D�finir la requ�te SQL
                sql =("SELECT COUNT(*)," + att + " "
                      "  FROM bdg_dba." + cls + " "
                      " WHERE NVL(" + att + ",-9999) NOT IN (" + dom + ") AND " + codeSpec + " IN (" + str(codes)[1:-1] + ")"
                      " GROUP BY " + att + " ORDER BY " + att)
                
                #Afficher la valeur de l'attribut � valider
                arcpy.AddMessage(" ")
                arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
        
        #Si seulement un domaine
        else:
            #Compter les SQL de contrainte d'int�grit�
            self.nbSql = self.nbSql + 1
                
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM bdg_dba." + cls + " "
                  " WHERE NVL(" + att + ",-9999) NOT IN (" + domaines.keys()[0] + ")"
                  " GROUP BY " + att + " ORDER BY " + att)
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(" ")
            arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
        #Sortir
        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requ�te SQL � ex�cuter.
        cat             : Num�ro du catalogue sans description.
        cls             : Classe � traiter.
        clsResultat     : Liste des classes � traiter.
        att             : Attribut � traiter.
        attResultat     : Liste des attributs � traiter.
        """
        
        #V�rification de la pr�sence des param�tres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, attribut)
               
        #V�rifier la connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #D�finir le num�ro de catalogue
        cat = catalogue.split(":")[0]
        
        #Valider les valeurs des param�tres
        self.validerValeurParam(cat)
        
        #Envoyer un message
        arcpy.AddMessage("- Cr�er les contraintes d'int�grit� des attributs de chaque classe")
        
        #Cr�er la SQL pour extraire le code g�n�rique de chaque classe � valider
        sql =  (" select distinct B.feat_type_name_database, substr(to_char(B.feat_type_code_bd),1,3)||'0009'"
                "  from feat_catalogue A, feat_type B"
                " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_name_database in ('" + classe.replace(",","','") + "')"
                " order by B.feat_type_name_database")
        #arcpy.AddMessage(sql)
        
        #Ex�cuter la SQL
        clsResultat = self.BDG.query(sql)
        
        #Traiter toutes les classes
        for cls in clsResultat:
            #Afficher le nom de la classe avec son code g�n�rique
            #arcpy.AddMessage(" ")
            #arcpy.AddMessage("--" + cls[0] + ":" + cls[1])
            
            #V�rifier si l'attribut CODE_SPEC est sp�cifi�
            if "CODE_SPEC" in attribut:
                #Groupe dans lequel la contraite d'int�grit� est situ�e.
                groupe = "BDG-CODE_SPEC-ATTRIBUT_CODE"
                #Description de la contrainte d'int�grit�
                description = "Valider la valeur d''attribut CODE_SPEC de la classe " + cls[0] + " via les attributs cod�s du catalogue."
                #Message indiquant comment corriger l'erreur.
                message = "Corriger la valeur de l''attribut CODE_SPEC de la classe " + cls[0] + " afin de respecter les attributs cod�s du catalogue."
                
                #Cr�er la SQL pour extraire les codes sp�cifiques
                sql =  (" select B.feat_type_code_bd"
                        "  from feat_catalogue A, feat_type B"
                        " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk  AND B.FEAT_TYPE_CLASS_TYPE=20014"
                        "   and B.feat_type_name_database='" + cls[0] + "'"
                        " order by B.feat_type_code_bd")
                #arcpy.AddMessage(sql)
                
                #Ex�cuter la SQL
                valResultat = self.BDG.query(sql)
                
                #V�rifier si un r�sultat est pr�sent
                if valResultat:
                    #Compter les SQL de contrainte d'int�grit�
                    self.nbSql = self.nbSql + 1
                    
                    #Initialiser la liste des valeurs
                    listeValeur = ""
                    
                    #Construire la liste des valeurs
                    for val in valResultat:
                        listeValeur = listeValeur + str(val[0]) + ","
                    listeValeur = listeValeur[:-1]
                    
                    #D�finir la requ�te SQL
                    sql =("SELECT COUNT(*),CODE_SPEC"
                          "  FROM bdg_dba." + cls[0] + " "
                          " WHERE NVL(CODE_SPEC,-9999) NOT IN (" + listeValeur + ")"
                          " GROUP BY CODE_SPEC ORDER BY CODE_SPEC")
                    
                    #Afficher la valeur de l'attribut � valider
                    arcpy.AddMessage(" ")
                    arcpy.AddMessage(self.sqlInsert + ",\n'" + groupe + "',\n'" + description + "',\n'" + message + "',\n'" + sql + "');")
            
            #Cr�er la SQL pour extraire les attributs de la classe
            sql = (" SELECT DISTINCT D.FEAT_ATTR_NAME_DATABASE, D.FEAT_ATTR_NAME_FR, D.FEAT_ATTR_DATA_TYPE, D.FEAT_ATTR_DOMAIN_TYPE"
                   "   FROM FEAT_CATALOGUE A,FEAT_TYPE B,RELATION_FEAT_ATTR C,FEAT_ATTR D"
                   "  WHERE A.FEAT_CATAL_TYPE=" + cat + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"
                   "   AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID"
                   "   AND B.FEAT_TYPE_NAME_DATABASE='" + cls[0] + "'"
                   "   AND D.FEAT_ATTR_NAME_DATABASE IN ('" + attribut.replace(",","','") + "')"
                   " ORDER BY D.FEAT_ATTR_NAME_DATABASE")
            #arcpy.AddMessage(sql)
            
            #Ex�cuter la SQL
            attResultat = self.BDG.query(sql)
            
            #Traiter tous les attributs de laclasse
            for att in attResultat:
                #Afficher le nom de l'attribut, sa description et son type
                #arcpy.AddMessage("--" + str(att[0]) + ":" + str(att[1]) + ":" + str(att[2]) + ":" + str(att[3]))
                
                #V�rifier si l'attribut est de type cod�
                if str(att[3]) == "-1":
                    #Valider les valeurs des attributs cod�s pour une classe en fonction des domaines du catalogue
                    self.validerDomaineAttributCodeClasse(cat, cls[0], att[0])
                    
                #Sinon on consid�re une expression r�guli�re
                else:
                    #Valider les valeurs des attributs pour une classe en fonction des expressions r�guli�res du catalogue
                    self.validerDomaineAttributClasse(cat, cls[0], cls[1], att[0], att[2])
        
        #Afficher le nombre d'attributs � traiter
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre d'attributs � traiter : " + str(len(attribut.split(","))))
        
        #Afficher le nombre de SQL des contrainte d'int�grit�.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre de SQL des contraintes d'int�grit� : " + str(self.nbSql))
        
        #Afficher les attrributs sans contrainte d'int�grit�.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre d'attributs sans contrainte d'int�grit� : " + str(len(self.sqlErr)))
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env         = "CATREL_PRO"
        catalogue   = "1:BDG"
        classe      = ""
        attribut    = ""
        
        #Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            classe = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            attribut = sys.argv[4].upper().replace(";",",").replace("'","")
        
        #D�finir l'objet pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oCreerContrainteIntegriteSqlCatalogue = CreerContrainteIntegriteSqlCatalogue()
        
        #Ex�cuter le traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oCreerContrainteIntegriteSqlCatalogue.executer(env, catalogue, classe, attribut)
            
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