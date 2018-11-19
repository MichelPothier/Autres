#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ValiderDomaineSqlCatalogue.py
# Auteur    : Michel Pothier
# Date      : 08 septembre 2015

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
    workspace       OB      Nom de la géodatabase contenant les données à valider.
                            défaut = "Database Connections\BDRS_PRO.sde"
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ValiderDomaineSqlCatalogue.py env catalogue classe attribut workspace

    Exemple:
        ValiderDomaineSqlCatalogue.py CATREL_PRO 1:BDG NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 WATER_DEFINITION,PERMANENCY "Database Connections\BDRS_PRO.sde"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderDomaineSqlCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, re, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderDomaineSqlCatalogue(object):
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
        self.nbErr      : Contient le nombre total d'erreurs.
        self.sqlErr     : Contient les SQL avec des erreurs.
        self.sqlVal     : Contient les SQL sans validation.
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Initialiser le nombre total d'erreurs
        self.nbErr = 0
        
        #Initialiser les SQL avec des erreurs
        self.sqlErr = []
        
        #Initialiser les SQL sans validation
        self.sqlVal = []
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, workspace, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        workspace   : Nom de la géodatabase contenant les valeurs d'attribut à valider.
        
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
        
        #Valider la présence
        if (len(workspace) == 0):
            raise Exception ('Paramètre obligatoire manquant: workspace')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, catalogue, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des paramètres.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue et sa description.
        workspace   : Nom de la géodatabase contenant les valeurs d'attribut à valider.
        
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
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " ")
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #Vérifier si le Workspace est valide
        arcpy.AddMessage("- Vérifier si le Workspace est valide")
        
        #Vérifier si le Workspace est absent
        if not arcpy.Exists(workspace):
            #Envoyer une exception
            raise Exception("Workspace absent : " + workspace)
        
        #Vérifier si le Workspace est invalide
        if arcpy.Describe(workspace).DataType <> "Workspace":
            #Envoyer une exception
            raise Exception("Workspace invalide : " + workspace)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerDomaineAttributClasse(self, cat, cls, codeGen, att, workspace, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut codé pour une classe de la Géodatabase en fonction du domaine contenu dans le catalogue.
        
        Paramètres:
        -----------
        cat         : Numéro du catalogue sans description.
        cls         : Nom de la classe du catalogue à valider.
        codeGen     : Code générique de la classe du catalogue à valider.
        att         : Nom d'attribut du catalogue à valider.
        workspace   : Nom de la géodatabase contenant les valeurs d'attribut à valider.
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
                        #Définir la requête SQL
                        sql =("SELECT COUNT(*)," + att + " "
                              "  FROM " + cls + " "
                              " WHERE NOT REGEXP_LIKE(" + att + ", '" + expResultat[0][0] + "')")
                        
                        #Vérifier si le codeSpec n'est pas générique
                        if str(code[0]) <> str(codeGen):
                            #Ajouter le code spécifique dans la requête SQL
                            sql = sql + "  AND " + codeSpec + "=" + str(code[0]) + " "
                        
                        #Ajouter le regroupement
                        sql = sql + " GROUP BY " + att + " ORDER BY " + att + " "
                        
                        #Afficher la valeur de l'attribut à valider
                        arcpy.AddMessage(sql)

                        #Exécuter la requête
                        try:
                            #Exécuter la SQL
                            valResultat = self.SDE.execute(sql)

                            #Vérifier la présence d'un résultat
                            if valResultat and type(valResultat) == list:
                                #Afficher le nombre de valeurs en erreur
                                nbVal = len(valResultat)
                                arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbVal))
                                
                                #Traiter tous les résultats
                                for val in valResultat:
                                    #Afficher le résultat
                                    arcpy.AddWarning(str(val))
                                    #Ajouter la valeur en erreur avec la sql
                                    sql = sql + "\n" + str(val)
                                    
                                    #Compter le nombre d'erreurs
                                    self.nbErr = self.nbErr + int(val[0])
                                
                                #Ajouter la SQL avec des erreurs
                                self.sqlErr.append(sql)
                                
                        #Gestion des erreurs
                        except Exception, err:
                            #Afficher l'erreur
                            arcpy.AddError("Classe ou Attribut en erreur.")
                            
        #si l'attribut ne possède pas de validation
        else:
            #Définir la requête SQL de base
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM " + cls + " "
                  " WHERE " + att + " IS NULL")
            
            #Afficher l'erreur
            arcpy.AddWarning(sql)

            #Ajouter la sql sans validation
            self.sqlVal.append(sql)
                        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerDomaineAttributCodeClasse(self, cat, cls, att, workspace, codeSpec='CODE_SPEC'):
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
        sql         : Requête SQL à exécuter.
        val         : Valeur d'attribut codé du catalogue.
        valResultat : Ensemble des valeurs d'attributs codés du catalogue.
        listeValeur : Liste de toutes les valeurs permises de l'attribut traité.
        listeVal    : Liste de toutes les valeurs permises de l'attribut traité pour un code spécifique.
        code        : Code spécifique à traité.
        codeResultat: Liste des codes spécifiques à traités.
        nbVal       : Nombre de valeurs en erreur.
        """
        
        #Créer la SQL pour définir l'ensemble des valeurs du catalogue
        sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "'"
               " order by E.ATTR_VALUE_INTERNAL_CODE")
        #arcpy.AddMessage(sql)
        
        #Exécuter la SQL
        valResultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if valResultat:
            #Initialiser la liste des valeurs
            listeValeur = ""
            #Construire la liste des valeurs
            for val in valResultat:
                listeValeur = listeValeur + str(val[0]) + ","
            listeValeur = listeValeur[:-1]
            
            #Définir la requête SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM " + cls + " "
                  " WHERE " + att + " NOT IN (" + listeValeur + ")"
                  " GROUP BY " + att + " ORDER BY " + att + " ")
            
            #Afficher la valeur de l'attribut à valider
            arcpy.AddMessage(sql)
            
            #Exécuter la requête
            try:
                #Exécuter la SQL
                valResultat = self.SDE.execute(sql)
                #valResultat = None
                
                #Vérifier la présence d'un résultat
                if valResultat and type(valResultat) == list:
                    #Afficher le nombre de valeurs en erreur
                    nbVal = len(valResultat)
                    arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbVal))
                    
                    #Traiter tous les résultats
                    for val in valResultat:
                        #Afficher le résultat
                        arcpy.AddWarning(str(val))
                        #Ajouter la valeur en erreur avec la sql
                        sql = sql + "\n" + str(val)
                        
                        #Compter le nombre d'erreurs
                        self.nbErr = self.nbErr + int(val[0])
                    
                    #Ajouter la SQL avec des erreurs
                    self.sqlErr.append(sql)
                    
            #Gestion des erreurs
            except Exception, err:
                #Afficher l'erreur
                arcpy.AddError("Classe ou Attribut en erreur.")
        
        #----------------------------------------------------------------------------------
        #Créer la SQL pour définir la liste des codes spécifiques pour chaque attribut codé
        sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "'"
               " order by B.feat_type_code_bd")
        #arcpy.AddMessage(sql)
        
        #Exécuter la SQL
        codeResultat = self.BDG.query(sql)
        
        #Créer la liste des codes spécifiques par attribut codé
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
                #Initialiser la liste des valeurs
                listeVal = ""
                #Construire la liste des valeurs
                for val in valResultat:
                    listeVal = listeVal + str(val[0]) + ","
                listeVal = listeVal[:-1]
                
                #Vérifier si la liste du code est la même que la liste de la classe
                if listeVal <> listeValeur:
                    #Définir la requête SQL
                    sql =("SELECT COUNT(*)," + att + " "
                          "  FROM " + cls + " "
                          " WHERE " + att + " NOT IN (" + listeVal + ") AND " + codeSpec + "=" + str(code[0]) + " "
                          " GROUP BY " + att + " ORDER BY " + att + " ")
                    
                    #Afficher la valeur de l'attribut à valider
                    arcpy.AddMessage(sql)
                    
                    #Exécuter la requête
                    try:
                        #Exécuter la SQL
                        valResultat = self.SDE.execute(sql)
                        #valResultat = None
                        
                        #Vérifier la présence d'un résultat
                        if valResultat and type(valResultat) == list:
                            #Afficher le nombre de valeurs en erreur
                            nbVal = len(valResultat)
                            arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbVal))
                            
                            #Traiter tous les résultats
                            for val in valResultat:
                                #Afficher le résultat
                                arcpy.AddWarning(str(val))
                                #Ajouter la valeur en erreur avec la sql
                                sql = sql + "\n" + str(val)
                                
                                #Compter le nombre d'erreurs
                                self.nbErr = self.nbErr + int(val[0])
                            
                            #Ajouter la SQL avec des erreurs
                            self.sqlErr.append(sql)
                            
                    #Gestion des erreurs
                    except Exception, err:
                        #Afficher l'erreur
                        arcpy.AddError("Classe ou Attribut en erreur.")
                
        #Sortir
        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, classe, attribut, workspace):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        workspace   : Nom de la géodatabase contenant les valeurs d'attribut à valider.
        
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
        self.nbErr      : Contient le nombre total d'erreurs.
        self.sqlErr     : Contient les SQL avec des erreurs.
        self.sqlVal     : Contient les SQL sans validation.
        """
        
        #Vérification de la présence des paramètres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, attribut, workspace)
               
        #Vérifier la connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Vérifier la connexion à SDE
        arcpy.AddMessage("- Connexion à SDE")
        self.SDE = arcpy.ArcSDESQLExecute(workspace)
        
        #Valider les valeurs des paramètres
        self.validerValeurParam(catalogue, workspace)
        
        #Envoyer un message
        arcpy.AddMessage("- Valider les valeurs des attributs de chaque classe")
        
        #Définir le numéro de catalogue
        cat = catalogue.split(":")[0]
        
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
            arcpy.AddMessage(" ")
            arcpy.AddMessage("--" + cls[0] + ":" + cls[1])
            
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
                arcpy.AddMessage("--" + str(att[0]) + ":" + str(att[1]) + ":" + str(att[2]) + ":" + str(att[3]))
                
                #Vérifier si l'attribut est de type codé
                if str(att[3]) == "-1":
                    #Valider les valeurs des attributs codés pour une classe en fonction des domaines du catalogue
                    self.validerDomaineAttributCodeClasse(cat, cls[0], att[0], workspace)
                    
                #Sinon on considère une expression régulière
                else:
                    #Valider les valeurs des attributs pour une classe en fonction des expressions régulières du catalogue
                    self.validerDomaineAttributClasse(cat, cls[0], cls[1], att[0], workspace)
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Afficher le nombre d'erreur
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Nombre total d'erreurs : " + str(self.nbErr))
        arcpy.AddMessage(" ")
        #Afficher les SQL en erreur
        for sql in self.sqlErr:
            #Afficher la sql
            arcpy.AddWarning(sql)
            arcpy.AddMessage(" ")
        
        #Afficher le nombre d'attributs sans validation

        arcpy.AddMessage("- Nombre total d'attributs sans validation : " + str(len(self.sqlVal)))
        arcpy.AddMessage(" ")
        #Afficher les SQL en erreur
        for sql in self.sqlVal:
            #Afficher la sql
            arcpy.AddWarning(sql)
        
        arcpy.AddMessage(" ")
        
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
        workspace   = "Database Connections\BDRS_PRO.sde"
        
        #Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            classe = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            attribut = sys.argv[4].upper().replace(";",",").replace("'","")
            
        if len(sys.argv) > 5:
            workspace = sys.argv[5]
        
        #Définir l'objet pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        oValiderDomaineSqlCatalogue = ValiderDomaineSqlCatalogue()
        
        #Exécuter le traitement pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        oValiderDomaineSqlCatalogue.executer(env, catalogue, classe, attribut, workspace)
            
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