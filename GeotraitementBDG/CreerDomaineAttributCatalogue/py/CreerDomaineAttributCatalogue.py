#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CreerDomaineAttributCatalogue.py
# Auteur    : Michel Pothier
# Date      : 18 février 2015

"""
    Application qui permet de créer les domaines d'attributs codés dans une géodatabase à partir de l'information contenue dans un catalogue. 
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue.
                            défaut = 1:BDG
    methode         OB      Nom de la méthode utilisée pour créer les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
                            DOM_ATTRIBUT : Les domaines sont créés à partir seulement du nom des attributs codés pour les classes sélectionnées.
                            DOM_CLASSE_ATTRIBUT : Les domaines sont créés à partir des noms de classe et des attributs codés pour les classes sélectionnées.
                            DOM_CODE_ATTRIBUT : Les domaines sont créés à partir des codes spécifiques et des attributs codés pour les classes sélectionnées.
                            défaut = DOM_ATTRIBUT
    workspace       OB      Nom de la géodatabase ou les domaines seront créés.
                            défaut =
    classe          OB      Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
                            défaut = <Toutes les classes présentent dans la géodatabase>
    attribut        OB      Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
                            défaut = <Tous les attributs codés selon les classes sélectionnées>
    prefixe         OB      Nom du préfixe utilisé pour créer les domaines d'attribut.
                            Exemple : Si l'attribut est "PROVIDER", le domaine sera DOM_PROVIDER ou DOM_PROVIDER_X si plusieurs domaines par attribut sont présents.
                            défaut = "DOM"
    detruire        OP      Indique si tous les domaines déjà présents dans la Géodatabase seront détruits (True) ou mis à jour (False).
                            défaut = True
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerDomaineAttributCatalogue.py env catalogue methode workspace classe attribut prefixe [detruire]

    Exemple:
        CreerDomaineAttributCatalogue.py CATREL_PRO 1:BDG DOM_ATTRIBUT "Database Connections\BDRS_PRO.sde" NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 WATER_DEFINITION,PERMANENCY DOM True

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerDomaineAttributCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class CreerDomaineAttributCatalogue(object):
#*******************************************************************************************
    """
    Permet de créer les domaines d'attributs codés dans une géodatabase à partir de l'information contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer les domaines d'attributs codés dans une géodatabase à partir de l'information contenue dans un catalogue.
        
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
    def definirListeDomaine(self, catalogue, methode, classe, prefixe):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir la liste des domaines d'attributs codés.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        methode     : Nom de la méthode utilisée pour créer les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Créer la liste des domaines d'attributs codés")
        
        #Formatter la liste des classes pour la SQL
        listeClasse = "'" + classe.replace(",","','") + "'"
        
        #Liste des domaines par attribut
        if methode == "DOM_ATTRIBUT":
            #Créer la SQL
            sql = ("select distinct D.feat_attr_name_database"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in ('" + listeClasse + "')"
                   " order by D.feat_attr_name_database")
        
        #Liste des domaines par classe et attribut
        elif methode == "DOM_CLASSE_ATTRIBUT":
            #Créer la SQL
            sql = ("select distinct B.feat_type_name_database,D.feat_attr_name_database"
                  "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
                  " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                  "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id and D.feat_attr_domain_type=-1"
                  "   and B.feat_type_name_database in ('" + listeClasse + "')"
                  " order by B.feat_type_name_database,D.feat_attr_name_database")
        
        #Liste des domaines par code spécifique et attribut
        elif methode == "DOM_CODE_ATTRIBUT":
            #Créer la SQL
            sql = ("select distinct B.feat_type_code_bd,D.feat_attr_name_database"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in ('" + listeClasse + "')"
                   " order by D.feat_attr_name_database,B.feat_type_code_bd")
        
        #Définir la liste des domaines d'attributs codés
        resultat = self.BDG.query(sql)
        listeDomaine = []
        for domaine in resultat:
            if len(domaine) == 1:
                listeDomaine.append(prefixe + "_" + domaine[0])
            else:
                listeDomaine.append(prefixe + "_" + str(domaine[0]) + "_" + domaine[1])        
        
        #Sortir
        return listeDomaine

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, methode, workspace, classe, attribut, prefixe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue.
        methode     : Nom de la méthode utilisée pour créer les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        workspace   : Nom de la géodatabase ou les domaines seront créés.
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
        if (len(methode) == 0):
            raise Exception ('Paramètre obligatoire manquant: methode')
        
        #Valider la présence
        if (len(workspace) == 0):
            raise Exception ('Paramètre obligatoire manquant: workspace')
        
        #Valider la présence
        if (len(classe) == 0):
            raise Exception ('Paramètre obligatoire manquant: classe')
        
        #Valider la présence
        if (len(attribut) == 0):
            raise Exception ('Paramètre obligatoire manquant: attribut')
        
        #Valider la présence
        if (len(prefixe) == 0):
            raise Exception ('Paramètre obligatoire manquant: prefixe')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, env, catalogue, methode, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des paramètres.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue.
        methode     : Nom de la méthode utilisée pour créer les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        
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
        
        #Vérifier si la méthode est valide
        arcpy.AddMessage("- Vérifier si la méthode est valide")
        #Définir la liste des méthodes
        listeMethode = ['DOM_ATTRIBUT','DOM_CLASSE_ATTRIBUT','DOM_CODE_ATTRIBUT']
        #Vérifier si le Workspace est absent
        if methode not in (listeMethode):
            #Envoyer une exception
            raise Exception("Méthode invalide : " + methode)
        
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
    def detruireDomaineAttribut(self, workspace):
    #-------------------------------------------------------------------------------------
        """
        Permet de détruire tous les domaines existants dans la Géodatabase.
        
        Paramètres:
        -----------
        workspace   : Nom de la géodatabase ou les domaines seront détruits.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Détruire tous les domaines existants dans les classes de la Géodatabase")
        
        #Définir le workspace par défaut
        arcpy.env.workspace = workspace
        
        #Extraire la description de la Géodatabase
        #for fc in classe.split(","):
        for fc in arcpy.ListFeatureClasses():
            #Extraire les fields
            fields = arcpy.ListFields(fc)
            
            #Traiter tous les fields
            for field in fields:
                #Vérifier la présence d'un domaine
                if len(field.domain) > 0:
                    #Vérifier si l'attribut est présent dans la liste des attribut
                    #if field.name in attribut:
                    
                    #Afficher le message
                    arcpy.AddMessage(" RemoveDomainFromField_management('" + fc + "', '" + field.name + "')")
                    
                    #Détruire un domaine dans un attribut d'une classe
                    arcpy.RemoveDomainFromField_management(fc, field.name)
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Détruire tous les domaines existants dans la Géodatabase")
        
        #Extraire la description de la Géodatabase
        desc = arcpy.Describe(workspace)
        
        #Extraire tous les domaines existants de la Géodatabase
        domains = desc.domains
        
        #Traiter tous les domaines
        for domain in domains:
            #Vérifier si c'est un domaine
            #if "DOM_" in domain:
            
            #Afficher le message
            arcpy.AddMessage(" DeleteDomain_management('" + workspace + "', '" + domain + "')")
            
            try:
                #Détruire un domaine
                arcpy.DeleteDomain_management(workspace, domain)
            #Gestion des erreurs
            except Exception, err:
                #Afficher l'erreur
                arcpy.AddWarning(err.message)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def creerDomaineSubtype(self, catalogue, workspace, classe, prefixe, subtype='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de créer les domaines des SubTypes dans les classes de la Géodatabase.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        prefixe     : Nom du préfixe utilisé pour créer les domaines d'attribut.
        subtype     : Nom de l'attribut contenant les subtypes.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer les domaines de SubTypes dans les classes de la Géodatabase")
        
        #Définir le workspace par défaut
        arcpy.env.workspace = workspace
        
        #Extraire la description de la Géodatabase
        for fc in classe.split(","):
            #Définir le nom du domaine
            domaine = prefixe + "_" + subtype + "_" + fc
            
            #Afficher la création du domaine
            arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'LONG')")
            #Créer le domaine dans la Géodatabase
            arcpy.CreateDomain_management(workspace, domaine, domaine, "LONG")
            
            #Définir aucun propriétaire de la classe par défaut
            prop = ""
            #Vérifier si le propriétaire est présent dans le nom de la classe
            if "." in fc:
                #Définir le propriétaire de la classe
                prop = fc.split(".")[0] + "."
            
            #Créer la SQL pour extraire les subtypes
            sql = ("select distinct B.feat_type_code_bd, B.feat_type_NAME_FR"
                   "  from feat_catalogue A, feat_type B"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_name_database='" + fc.replace(prop,"") + "'"
                   " order by B.feat_type_code_bd")
            
            #arcpy.AddMessage(sql)
            #Exécuter la SQL
            resultat = self.BDG.query(sql)
            
            #Vérifier le résultat
            if resultat:
                #Traiter tous les résultats
                for valeur in resultat:
                    #Afficher l'ajout de la valeur codée au domaine
                    arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                    #Ajouter la valeur codée
                    arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1])
                
                #Afficher l'assignation du domaine à la classe
                arcpy.AddMessage(" AssignDomainToField_management('" + fc + "', '" + subtype + "', '" + domaine + "')")
                #Assigner le domaine à la classe
                arcpy.AssignDomainToField_management(fc, subtype, domaine)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def creerSubtype(self, catalogue, workspace, classe, subtype='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de créer les SubTypes dans les classes de la Géodatabase.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        subtype     : Nom de l'attribut contenant les subtypes.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer les SubTypes dans les classes de la Géodatabase")
        
        #Définir le workspace par défaut
        arcpy.env.workspace = workspace
        
        #Extraire la description de la Géodatabase
        for fc in classe.split(","):
            #Afficher le message
            arcpy.AddMessage(" SetSubtypeField_management('" + fc + "', '" + subtype + "')")
            #Définir l'attribut qui contient le Subtype
            arcpy.SetSubtypeField_management(fc, subtype)
            
            #Définir aucun propriétaire de la classe par défaut
            prop = ""
            #Vérifier si le propriétaire est présent dans le nom de la classe
            if "." in fc:
                #Définir le propriétaire de la classe
                prop = fc.split(".")[0] + "."
            
            #Créer la SQL pour extraire les subtypes
            sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
                   "  from feat_catalogue A, feat_type B"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_name_database='" + fc.replace(prop,"") + "'"
                   " order by B.feat_type_code_bd")
            
            #arcpy.AddMessage(sql)
            #Exécuter la SQL
            resultat = self.BDG.query(sql)
            
            #Vérifier le résultat
            if resultat:
                #Traiter tous les résultats
                for valeur in resultat:
                    #Afficher le message
                    arcpy.AddMessage(" AddSubtype_management('" + fc + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                    #Ajouter un subtype à la classe
                    arcpy.AddSubtype_management(fc, valeur[0], str(valeur[0]) + ":" + valeur[1])   
                
                #Afficher le message
                arcpy.AddMessage(" SetDefaultSubtype_management('" + fc + "', " + str(resultat[0][0]) + ")")
                #Définir le Subtype par défaut
                arcpy.SetDefaultSubtype_management(fc, resultat[0][0])
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def creerDomaineAttribut(self, catalogue, workspace, classe, attribut, prefixe):
    #-------------------------------------------------------------------------------------
        """
        Permet de créer les domaines par attribut codé.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        prefixe     : Nom du préfixe utilisé pour créer les domaines d'attribut.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer les domaines par attribut codé")
        
        #Définir le workspace par défaut
        arcpy.env.workspace = workspace
        
        #Initialiser la liste des classes
        classes = ""
        #Définir la liste des classes du catalogue
        for cls in classe.split(","):
            #Définir le propriétaire par défaut
            prop = ""
            #Vérifier si le propriétaire est présent dans le nom
            if "." in (cls):
                #Extraire le propriétaire si présent
                prop = cls.split(".")[0] + "."
            #Enlever le propriétaire de la classe si présent
            classes = classes + "'" + cls.replace(prop,"").upper() + "',"
        #Enlever la dernière virgule
        classes = classes[:-1]
        
        #Initialisation de la liste des domaines
        listeDomaine = []
        
        #Extraire la description de la Géodatabase
        desc = arcpy.Describe(workspace)
        
        #Extraire tous les domaines existants de la Géodatabase
        domains = desc.domains
        
        #Traiter tous les attributs
        for att in attribut.split(","):
            #Définir le nom du domaine
            domaine = prefixe + "_" + att
            #Ajouter le domaine dans la liste
            listeDomaine.append(domaine)
            #Afficher le domaine
            arcpy.AddMessage(domaine)
            
            #Afficher la création du domaine
            arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'SHORT')")
            #Créer le domaine dans la Géodatabase
            arcpy.CreateDomain_management(workspace, domaine, domaine, "SHORT")
            
            #Créer la SQL pour définir le domaine
            sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE, E.ATTR_VALUE_LABEL_FR, E.ATTR_VALUE_LABEL_EN"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in (" + classes + ") and D.feat_attr_name_database='" + att + "'"
                   " order by E.ATTR_VALUE_INTERNAL_CODE")
            #arcpy.AddMessage(sql)
            #Exécuter la SQL
            resultat = self.BDG.query(sql)
            
            #Traiter tous les résultats
            for valeur in resultat:
                #Afficher l'ajout de la valeur codée au domaine
                arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                #Ajouter la valeur codée
                arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1] + " / " + valeur[2])
            
            #Créer la SQL pour assigner le domaine aux classes
            sql = ("select distinct B.feat_type_name_database"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in (" + classes + ") and D.feat_attr_name_database='" + att + "'"
                   " order by B.feat_type_name_database")
            #arcpy.AddMessage(sql)
            #Exécuter la SQL
            resultat = self.BDG.query(sql)
            
            #Traiter toutes les classes
            for cls in resultat:
                try:
                    #Afficher l'assignation du domaine à la classe
                    arcpy.AddMessage(" AssignDomainToField_management('" + cls[0].lower() + "', '" + att + "', '" + domaine + "')")
                    #Assigner le domaine à la classe
                    arcpy.AssignDomainToField_management(cls[0].lower(), att, domaine)
                #Gestion des erreurs
                except Exception, err:
                    #Afficher l'erreur
                    arcpy.AddWarning(err.message)
        
        #Afficher un espace
        arcpy.AddMessage(" ")
        arcpy.AddMessage(" Nombre de domaines : " + str(len(listeDomaine)))
        arcpy.AddMessage(" ")
        
        #Sortir
        return listeDomaine

    #-------------------------------------------------------------------------------------
    def creerDomaineClasseAttribut(self, catalogue, workspace, classe, attribut, prefixe):
    #-------------------------------------------------------------------------------------
        """
        Permet de créer les domaines par classe et par attribut codé.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        prefixe     : Nom du préfixe utilisé pour créer les domaines d'attribut.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer les domaines par classe et par attribut codé")
        
        #Initialisation de la liste des domaines
        listeDomaine = {}
        #Traiter tous les attributs
        for att in attribut.split(","):
            #Initialisation du compteur de domaine par attribut
            nbDomAtt = 0
            #Traiter toutes les classes
            for cls in classe.split(","):
                #Définir aucun propriétaire de la classe par défaut
                prop = ""
                #Vérifier si le propriétaire est présent dans le nom de la classe
                if "." in cls:
                    #Définir le propriétaire de la classe
                    prop = cls.split(".")[0] + "."
                
                #Initialisation de la liste des valeurs
                listeValeur = []
                
                #Créer la SQL pour définir le domaine
                sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE, E.ATTR_VALUE_LABEL_FR"
                      "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                      " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                      "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                      "   and B.feat_type_name_database='" + cls.replace(prop,"") + "' and D.feat_attr_name_database='" + att + "'"
                      " order by E.ATTR_VALUE_INTERNAL_CODE")
                
                #arcpy.AddMessage(sql)
                #Exécuter la SQL
                resultat = self.BDG.query(sql)
                
                #Vérifier le résultat
                if resultat:
                    #Traiter tous les résultats
                    for valeur in resultat:
                        #Créer la liste des valeurs d'attribut
                        listeValeur.append(str(valeur[0]) + ":" + valeur[1])
                    
                    #Vérifier si le domaine absent
                    if str(listeValeur) not in listeDomaine:
                        #Compteur de domaine par attribut
                        nbDomAtt = nbDomAtt + 1
                        #Définir le nom du domaine
                        domaine = prefixe + "_" + att + "_" + str(nbDomAtt)
                        #Ajouter le domaine dans la liste
                        listeDomaine[str(listeValeur)] = domaine
                        #Afficher le domaine
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(domaine)
                        
                        #Afficher la création du domaine
                        arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'LONG')")
                        #Créer le domaine dans la Géodatabase
                        arcpy.CreateDomain_management(workspace, domaine, domaine, "LONG")
                        
                        #Traiter toutes les valeurs
                        for val in listeValeur:
                            #Séparer le code de la description
                            valeur = val.split(":")
                            #Afficher l'ajout de la valeur codée au domaine
                            arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                            #Ajouter la valeur codée
                            arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1])
                    
                    #Si le domaine est présent
                    else:
                        #Définir le nom du domaine
                        domaine = listeDomaine[str(listeValeur)]
                    
                    try:
                        #Afficher l'assignation du domaine à la classe
                        arcpy.AddMessage(" AssignDomainToField_management('" + cls + "', '" + att + "', '" + domaine + "')")
                        #Assigner le domaine à la classe
                        arcpy.AssignDomainToField_management(cls, att, domaine)
                    #Gestion des erreurs
                    except Exception, err:
                        #Afficher l'erreur
                        arcpy.AddWarning(err.message)
        
        #Afficher un espace
        arcpy.AddMessage(" ")
        arcpy.AddMessage(" Nombre de domaines : " + str(len(listeDomaine)))
        arcpy.AddMessage(" ")
        
        #Sortir
        return listeDomaine

    #-------------------------------------------------------------------------------------
    def creerDomaineCodeAttribut(self, catalogue, workspace, classe, attribut, prefixe):
    #-------------------------------------------------------------------------------------
        """
        Permet de créer les domaines par code spécifique et par attribut codé.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        prefixe     : Nom du préfixe utilisé pour créer les domaines d'attribut.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer les domaines par code spécifique et attribut codé")
        
        #Initialisation de la liste des domaines
        listeDomaine = {}
        
        #Traiter tous les attributs
        for att in attribut.split(","):
            #Initialisation du compteur de domaines par attribut
            nbDomAtt = 0
            #Traiter toutes les classes
            for cls in classe.split(","):
                #Définir aucun propriétaire de la classe par défaut
                prop = ""
                #Vérifier si le propriétaire est présent dans le nom de la classe
                if "." in cls:
                    #Définir le propriétaire de la classe
                    prop = cls.split(".")[0] + "."
                #Initialisation de la liste des codes spécifiques par domaine
                listeCodeSpec = {}
                #Créer la SQL pour définir le domaine
                sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
                       "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                       " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                       "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                       "   and B.feat_type_name_database='" + cls.replace(prop,"") + "' and D.feat_attr_name_database='" + att + "'"
                       " order by B.feat_type_code_bd")
                
                #arcpy.AddMessage(sql)
                #Exécuter la SQL
                codes = self.BDG.query(sql)
                
                #Vérifier si la classe possède l'attribut
                if codes:
                    #Traiter tous les codes spécifiques
                    for code in codes:
                        #Initialisation de la liste des valeurs
                        listeValeur = []
                        
                        #Créer la SQL pour définir le domaine
                        sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE, E.ATTR_VALUE_LABEL_FR"
                               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                               "   and B.feat_type_code_bd=" + str(code[0]) + " and B.feat_type_name_database='" + cls.replace(prop,"") + "' and D.feat_attr_name_database='" + att + "'"
                               " order by E.ATTR_VALUE_INTERNAL_CODE")
                        
                        #arcpy.AddMessage(sql)
                        #Exécuter la SQL
                        valeurs = self.BDG.query(sql)
                        
                        #Traiter tous les résultats
                        for valeur in valeurs:                        
                            #Créer la liste des valeurs d'attribut
                            listeValeur.append(str(valeur[0]) + ": " + valeur[1])
                            
                        #Vérifier si le domaine absent
                        if str(listeValeur) not in listeDomaine:
                            #Compteur de domaine par attribut
                            nbDomAtt = nbDomAtt + 1
                            #Définir le nom du domaine
                            domaine = prefixe + "_" + att + "_" + str(nbDomAtt)
                            #Afficher le domaine
                            arcpy.AddMessage(" ")
                            arcpy.AddMessage(domaine)
                            #Ajouter le domaine dans la liste des domaines
                            listeDomaine[str(listeValeur)] = domaine
                            #Ajouter le code spécifique dans la liste des codes spécifiques
                            listeCodeSpec[domaine] = str(code[0])
                            
                            #Afficher la création du domaine
                            arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'LONG')")
                            #Créer le domaine dans la Géodatabase
                            arcpy.CreateDomain_management(workspace, domaine, domaine, "LONG")
                            
                            #Traiter toutes les valeurs
                            for val in listeValeur:
                                #Séparer le code de la description
                                valeur = val.split(":")
                                #Afficher l'ajout de la valeur codée au domaine
                                arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                                #Ajouter la valeur codée
                                arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1])
                        
                        #Si le domaine est présent
                        else:
                            #Définir le nom du domaine
                            domaine = listeDomaine[str(listeValeur)]
                            
                            #Vérifier si le domaine est absent de la liste des codes specifiques
                            if domaine not in listeCodeSpec:
                                #Ajouter le code spécifique dans la liste des codes spécifiques
                                listeCodeSpec[domaine] = str(code[0])
                            #Si le domaine est présent
                            else:
                                #Définir la liste des codes spécifiques
                                codeSpec = listeCodeSpec[domaine]
                                #Ajouter le code spécifique dans la liste des codes spécifiques
                                listeCodeSpec[domaine] = codeSpec + ";" + str(code[0])
                
                #Traiter tous les domaines de la classe 
                for domaine, codeSpec in listeCodeSpec.items():
                    try:
                        #Afficher l'assignation du domaine à la classe
                        arcpy.AddMessage(" AssignDomainToField_management('" + cls + "', '" + att + "', '" + domaine + "', '" + codeSpec + "')")
                        #Assigner le domaine à la classe
                        arcpy.AssignDomainToField_management(cls, att, domaine, codeSpec)
                    #Gestion des erreurs
                    except Exception, err:
                        #Afficher l'erreur
                        arcpy.AddWarning(err.message)
        
        #Afficher un espace
        arcpy.AddMessage(" ")
        arcpy.AddMessage(" Nombre de domaines : " + str(len(listeDomaine)))
        arcpy.AddMessage(" ")
        
        #Sortir
        return  listeDomaine
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, methode, workspace, classe, attribut, prefixe, detruire=True):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour créer les domaines d'attributs codés dans une géodatabase à partir de l'information contenue dans un catalogue.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue.
        methode     : Nom de la méthode utilisée pour créer les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        prefixe     : Nom du préfixe utilisé pour créer les domaines d'attribut.
        detruire    : Indique si tous les domaines déjà présents dans la Géodatabase seront détruits (True) ou mis à jour (False).
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requête SQL à exécuter.
        """
        
        #Vérification de la présence des paramètres obligatoires
        self.validerParamObligatoire(env, catalogue, methode, workspace, classe, attribut, prefixe)
        
        #Vérifier la connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Valider les valeurs des paramètres
        self.validerValeurParam(env, catalogue, methode, workspace)
            
        #Liste des domaines par attribut
        if methode == "DOM_ATTRIBUT":
            #Vérifier si on doit détruire tous les domaines existants
            if detruire:
                #Détruire tous les domaines existants
                self.detruireDomaineAttribut(workspace)
            #Créer les domaines des subtypes
            #self.creerDomaineSubtype(catalogue, workspace, classe, prefixe, 'CODE_SPEC')
            #Créer les domaines d'attributs codés
            self.creerDomaineAttribut(catalogue, workspace, classe, attribut, prefixe)
        
        #Liste des domaines par classe et attribut
        elif methode == "DOM_CLASSE_ATTRIBUT":
            #Vérifier si on doit détruire tous les domaines existants
            if detruire:
                #Détruire tous les domaines existants
                self.detruireDomaineAttribut(workspace)
            #Créer les domaines des subtypes
            self.creerDomaineSubtype(catalogue, workspace, classe, prefixe, 'CODE_SPEC')
            #Créer les domaines d'attributs codés
            self.creerDomaineClasseAttribut(catalogue, workspace, classe, attribut, prefixe)
        
        #Liste des domaines par code spécifique et attribut
        elif methode == "DOM_CODE_ATTRIBUT":
            #Créer les subtypes
            self.creerSubtype(catalogue, workspace, classe, 'CODE_SPEC')
            #Vérifier si on doit détruire tous les domaines existants
            if detruire:
                #Détruire tous les domaines existants
                self.detruireDomaineAttribut(workspace)
            #Créer les domaines d'attributs codés
            self.creerDomaineCodeAttribut(catalogue, workspace, classe, attribut, prefixe)
        
        #Vérifier si le type de Géodatabase est LocalDatabase 
        if arcpy.Describe(workspace).workspaceType == "LocalDatabase":
            #Afficher le message
            arcpy.AddMessage("Compact_management('" + workspace + "')")
            #Compacter la Géobase
            arcpy.Compact_management(workspace)
        
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
        methode     = ""
        workspace   = ""
        classe      = ""
        attribut    = ""
        prefixe     = "DOM"
        detruire    = True
        
        #Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            methode = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            workspace = sys.argv[4]
        
        if len(sys.argv) > 5:
            classe = sys.argv[5].upper().replace(";",",")
        
        if len(sys.argv) > 6:
            attribut = sys.argv[6].upper().replace(";",",")
        
        if len(sys.argv) > 7:
            prefixe = sys.argv[7].upper()
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                detruire = sys.argv[8].upper() == "TRUE"
        
        #Définir l'objet pour créer les domaines d'attributs codés dans une géodatabase à partir de l'information contenue dans un catalogue.
        oCreerDomaineAttributCatalogue = CreerDomaineAttributCatalogue()
        
        #Exécuter le traitement pour créer les domaines d'attributs codés dans une géodatabase à partir de l'information contenue dans un catalogue.
        oCreerDomaineAttributCatalogue.executer(env, catalogue, methode, workspace, classe, attribut, prefixe, detruire)
            
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