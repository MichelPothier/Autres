#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ValiderDomaineSqlCatalogue.py
# Auteur    : Michel Pothier
# Date      : 08 septembre 2015

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
    workspace       OB      Nom de la g�odatabase contenant les donn�es � valider.
                            d�faut = "Database Connections\BDRS_PRO.sde"
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderDomaineSqlCatalogue(object):
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
        self.nbErr      : Contient le nombre total d'erreurs.
        self.sqlErr     : Contient les SQL avec des erreurs.
        self.sqlVal     : Contient les SQL sans validation.
        """
        
        #D�finir l'objet de gestion des comptes BDG.
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
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
        
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
        
        #Valider la pr�sence
        if (len(workspace) == 0):
            raise Exception ('Param�tre obligatoire manquant: workspace')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, catalogue, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des param�tres.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue et sa description.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
        
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
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " ")
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #V�rifier si le Workspace est valide
        arcpy.AddMessage("- V�rifier si le Workspace est valide")
        
        #V�rifier si le Workspace est absent
        if not arcpy.Exists(workspace):
            #Envoyer une exception
            raise Exception("Workspace absent : " + workspace)
        
        #V�rifier si le Workspace est invalide
        if arcpy.Describe(workspace).DataType <> "Workspace":
            #Envoyer une exception
            raise Exception("Workspace invalide : " + workspace)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerDomaineAttributClasse(self, cat, cls, codeGen, att, workspace, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut cod� pour une classe de la G�odatabase en fonction du domaine contenu dans le catalogue.
        
        Param�tres:
        -----------
        cat         : Num�ro du catalogue sans description.
        cls         : Nom de la classe du catalogue � valider.
        codeGen     : Code g�n�rique de la classe du catalogue � valider.
        att         : Nom d'attribut du catalogue � valider.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
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
                        #D�finir la requ�te SQL
                        sql =("SELECT COUNT(*)," + att + " "
                              "  FROM " + cls + " "
                              " WHERE NOT REGEXP_LIKE(" + att + ", '" + expResultat[0][0] + "')")
                        
                        #V�rifier si le codeSpec n'est pas g�n�rique
                        if str(code[0]) <> str(codeGen):
                            #Ajouter le code sp�cifique dans la requ�te SQL
                            sql = sql + "  AND " + codeSpec + "=" + str(code[0]) + " "
                        
                        #Ajouter le regroupement
                        sql = sql + " GROUP BY " + att + " ORDER BY " + att + " "
                        
                        #Afficher la valeur de l'attribut � valider
                        arcpy.AddMessage(sql)

                        #Ex�cuter la requ�te
                        try:
                            #Ex�cuter la SQL
                            valResultat = self.SDE.execute(sql)

                            #V�rifier la pr�sence d'un r�sultat
                            if valResultat and type(valResultat) == list:
                                #Afficher le nombre de valeurs en erreur
                                nbVal = len(valResultat)
                                arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbVal))
                                
                                #Traiter tous les r�sultats
                                for val in valResultat:
                                    #Afficher le r�sultat
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
                            
        #si l'attribut ne poss�de pas de validation
        else:
            #D�finir la requ�te SQL de base
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
        sql         : Requ�te SQL � ex�cuter.
        val         : Valeur d'attribut cod� du catalogue.
        valResultat : Ensemble des valeurs d'attributs cod�s du catalogue.
        listeValeur : Liste de toutes les valeurs permises de l'attribut trait�.
        listeVal    : Liste de toutes les valeurs permises de l'attribut trait� pour un code sp�cifique.
        code        : Code sp�cifique � trait�.
        codeResultat: Liste des codes sp�cifiques � trait�s.
        nbVal       : Nombre de valeurs en erreur.
        """
        
        #Cr�er la SQL pour d�finir l'ensemble des valeurs du catalogue
        sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "'"
               " order by E.ATTR_VALUE_INTERNAL_CODE")
        #arcpy.AddMessage(sql)
        
        #Ex�cuter la SQL
        valResultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if valResultat:
            #Initialiser la liste des valeurs
            listeValeur = ""
            #Construire la liste des valeurs
            for val in valResultat:
                listeValeur = listeValeur + str(val[0]) + ","
            listeValeur = listeValeur[:-1]
            
            #D�finir la requ�te SQL
            sql =("SELECT COUNT(*)," + att + " "
                  "  FROM " + cls + " "
                  " WHERE " + att + " NOT IN (" + listeValeur + ")"
                  " GROUP BY " + att + " ORDER BY " + att + " ")
            
            #Afficher la valeur de l'attribut � valider
            arcpy.AddMessage(sql)
            
            #Ex�cuter la requ�te
            try:
                #Ex�cuter la SQL
                valResultat = self.SDE.execute(sql)
                #valResultat = None
                
                #V�rifier la pr�sence d'un r�sultat
                if valResultat and type(valResultat) == list:
                    #Afficher le nombre de valeurs en erreur
                    nbVal = len(valResultat)
                    arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbVal))
                    
                    #Traiter tous les r�sultats
                    for val in valResultat:
                        #Afficher le r�sultat
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
        #Cr�er la SQL pour d�finir la liste des codes sp�cifiques pour chaque attribut cod�
        sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
               " where A.feat_catal_type=" + cat + " and A.feat_catal_id=B.feat_catal_fk"
               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
               "   and B.feat_type_name_database='" + cls + "' and D.feat_attr_name_database='" + att + "'"
               " order by B.feat_type_code_bd")
        #arcpy.AddMessage(sql)
        
        #Ex�cuter la SQL
        codeResultat = self.BDG.query(sql)
        
        #Cr�er la liste des codes sp�cifiques par attribut cod�
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
                #Initialiser la liste des valeurs
                listeVal = ""
                #Construire la liste des valeurs
                for val in valResultat:
                    listeVal = listeVal + str(val[0]) + ","
                listeVal = listeVal[:-1]
                
                #V�rifier si la liste du code est la m�me que la liste de la classe
                if listeVal <> listeValeur:
                    #D�finir la requ�te SQL
                    sql =("SELECT COUNT(*)," + att + " "
                          "  FROM " + cls + " "
                          " WHERE " + att + " NOT IN (" + listeVal + ") AND " + codeSpec + "=" + str(code[0]) + " "
                          " GROUP BY " + att + " ORDER BY " + att + " ")
                    
                    #Afficher la valeur de l'attribut � valider
                    arcpy.AddMessage(sql)
                    
                    #Ex�cuter la requ�te
                    try:
                        #Ex�cuter la SQL
                        valResultat = self.SDE.execute(sql)
                        #valResultat = None
                        
                        #V�rifier la pr�sence d'un r�sultat
                        if valResultat and type(valResultat) == list:
                            #Afficher le nombre de valeurs en erreur
                            nbVal = len(valResultat)
                            arcpy.AddWarning("Nombre de valeurs en erreur : " + str(nbVal))
                            
                            #Traiter tous les r�sultats
                            for val in valResultat:
                                #Afficher le r�sultat
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
        Ex�cuter le traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue et sa description.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
        
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
        self.nbErr      : Contient le nombre total d'erreurs.
        self.sqlErr     : Contient les SQL avec des erreurs.
        self.sqlVal     : Contient les SQL sans validation.
        """
        
        #V�rification de la pr�sence des param�tres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, attribut, workspace)
               
        #V�rifier la connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #V�rifier la connexion � SDE
        arcpy.AddMessage("- Connexion � SDE")
        self.SDE = arcpy.ArcSDESQLExecute(workspace)
        
        #Valider les valeurs des param�tres
        self.validerValeurParam(catalogue, workspace)
        
        #Envoyer un message
        arcpy.AddMessage("- Valider les valeurs des attributs de chaque classe")
        
        #D�finir le num�ro de catalogue
        cat = catalogue.split(":")[0]
        
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
            arcpy.AddMessage(" ")
            arcpy.AddMessage("--" + cls[0] + ":" + cls[1])
            
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
                arcpy.AddMessage("--" + str(att[0]) + ":" + str(att[1]) + ":" + str(att[2]) + ":" + str(att[3]))
                
                #V�rifier si l'attribut est de type cod�
                if str(att[3]) == "-1":
                    #Valider les valeurs des attributs cod�s pour une classe en fonction des domaines du catalogue
                    self.validerDomaineAttributCodeClasse(cat, cls[0], att[0], workspace)
                    
                #Sinon on consid�re une expression r�guli�re
                else:
                    #Valider les valeurs des attributs pour une classe en fonction des expressions r�guli�res du catalogue
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
        workspace   = "Database Connections\BDRS_PRO.sde"
        
        #Lecture des param�tres
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
        
        #D�finir l'objet pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oValiderDomaineSqlCatalogue = ValiderDomaineSqlCatalogue()
        
        #Ex�cuter le traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oValiderDomaineSqlCatalogue.executer(env, catalogue, classe, attribut, workspace)
            
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