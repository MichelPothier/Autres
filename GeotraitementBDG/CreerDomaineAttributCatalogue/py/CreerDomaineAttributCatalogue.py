#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : CreerDomaineAttributCatalogue.py
# Auteur    : Michel Pothier
# Date      : 18 f�vrier 2015

"""
    Application qui permet de cr�er les domaines d'attributs cod�s dans une g�odatabase � partir de l'information contenue dans un catalogue. 
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue.
                            d�faut = 1:BDG
    methode         OB      Nom de la m�thode utilis�e pour cr�er les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
                            DOM_ATTRIBUT : Les domaines sont cr��s � partir seulement du nom des attributs cod�s pour les classes s�lectionn�es.
                            DOM_CLASSE_ATTRIBUT : Les domaines sont cr��s � partir des noms de classe et des attributs cod�s pour les classes s�lectionn�es.
                            DOM_CODE_ATTRIBUT : Les domaines sont cr��s � partir des codes sp�cifiques et des attributs cod�s pour les classes s�lectionn�es.
                            d�faut = DOM_ATTRIBUT
    workspace       OB      Nom de la g�odatabase ou les domaines seront cr��s.
                            d�faut =
    classe          OB      Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
                            d�faut = <Toutes les classes pr�sentent dans la g�odatabase>
    attribut        OB      Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
                            d�faut = <Tous les attributs cod�s selon les classes s�lectionn�es>
    prefixe         OB      Nom du pr�fixe utilis� pour cr�er les domaines d'attribut.
                            Exemple : Si l'attribut est "PROVIDER", le domaine sera DOM_PROVIDER ou DOM_PROVIDER_X si plusieurs domaines par attribut sont pr�sents.
                            d�faut = "DOM"
    detruire        OP      Indique si tous les domaines d�j� pr�sents dans la G�odatabase seront d�truits (True) ou mis � jour (False).
                            d�faut = True
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class CreerDomaineAttributCatalogue(object):
#*******************************************************************************************
    """
    Permet de cr�er les domaines d'attributs cod�s dans une g�odatabase � partir de l'information contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour cr�er les domaines d'attributs cod�s dans une g�odatabase � partir de l'information contenue dans un catalogue.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        #D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def definirListeDomaine(self, catalogue, methode, classe, prefixe):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir la liste des domaines d'attributs cod�s.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        methode     : Nom de la m�thode utilis�e pour cr�er les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Cr�er la liste des domaines d'attributs cod�s")
        
        #Formatter la liste des classes pour la SQL
        listeClasse = "'" + classe.replace(",","','") + "'"
        
        #Liste des domaines par attribut
        if methode == "DOM_ATTRIBUT":
            #Cr�er la SQL
            sql = ("select distinct D.feat_attr_name_database"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in ('" + listeClasse + "')"
                   " order by D.feat_attr_name_database")
        
        #Liste des domaines par classe et attribut
        elif methode == "DOM_CLASSE_ATTRIBUT":
            #Cr�er la SQL
            sql = ("select distinct B.feat_type_name_database,D.feat_attr_name_database"
                  "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
                  " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                  "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id and D.feat_attr_domain_type=-1"
                  "   and B.feat_type_name_database in ('" + listeClasse + "')"
                  " order by B.feat_type_name_database,D.feat_attr_name_database")
        
        #Liste des domaines par code sp�cifique et attribut
        elif methode == "DOM_CODE_ATTRIBUT":
            #Cr�er la SQL
            sql = ("select distinct B.feat_type_code_bd,D.feat_attr_name_database"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in ('" + listeClasse + "')"
                   " order by D.feat_attr_name_database,B.feat_type_code_bd")
        
        #D�finir la liste des domaines d'attributs cod�s
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
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        methode     : Nom de la m�thode utilis�e pour cr�er les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
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
        if (len(methode) == 0):
            raise Exception ('Param�tre obligatoire manquant: methode')
        
        #Valider la pr�sence
        if (len(workspace) == 0):
            raise Exception ('Param�tre obligatoire manquant: workspace')
        
        #Valider la pr�sence
        if (len(classe) == 0):
            raise Exception ('Param�tre obligatoire manquant: classe')
        
        #Valider la pr�sence
        if (len(attribut) == 0):
            raise Exception ('Param�tre obligatoire manquant: attribut')
        
        #Valider la pr�sence
        if (len(prefixe) == 0):
            raise Exception ('Param�tre obligatoire manquant: prefixe')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, env, catalogue, methode, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des param�tres.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        methode     : Nom de la m�thode utilis�e pour cr�er les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        
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
        
        #V�rifier si la m�thode est valide
        arcpy.AddMessage("- V�rifier si la m�thode est valide")
        #D�finir la liste des m�thodes
        listeMethode = ['DOM_ATTRIBUT','DOM_CLASSE_ATTRIBUT','DOM_CODE_ATTRIBUT']
        #V�rifier si le Workspace est absent
        if methode not in (listeMethode):
            #Envoyer une exception
            raise Exception("M�thode invalide : " + methode)
        
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
    def detruireDomaineAttribut(self, workspace):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�truire tous les domaines existants dans la G�odatabase.
        
        Param�tres:
        -----------
        workspace   : Nom de la g�odatabase ou les domaines seront d�truits.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�truire tous les domaines existants dans les classes de la G�odatabase")
        
        #D�finir le workspace par d�faut
        arcpy.env.workspace = workspace
        
        #Extraire la description de la G�odatabase
        #for fc in classe.split(","):
        for fc in arcpy.ListFeatureClasses():
            #Extraire les fields
            fields = arcpy.ListFields(fc)
            
            #Traiter tous les fields
            for field in fields:
                #V�rifier la pr�sence d'un domaine
                if len(field.domain) > 0:
                    #V�rifier si l'attribut est pr�sent dans la liste des attribut
                    #if field.name in attribut:
                    
                    #Afficher le message
                    arcpy.AddMessage(" RemoveDomainFromField_management('" + fc + "', '" + field.name + "')")
                    
                    #D�truire un domaine dans un attribut d'une classe
                    arcpy.RemoveDomainFromField_management(fc, field.name)
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�truire tous les domaines existants dans la G�odatabase")
        
        #Extraire la description de la G�odatabase
        desc = arcpy.Describe(workspace)
        
        #Extraire tous les domaines existants de la G�odatabase
        domains = desc.domains
        
        #Traiter tous les domaines
        for domain in domains:
            #V�rifier si c'est un domaine
            #if "DOM_" in domain:
            
            #Afficher le message
            arcpy.AddMessage(" DeleteDomain_management('" + workspace + "', '" + domain + "')")
            
            try:
                #D�truire un domaine
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
        Permet de cr�er les domaines des SubTypes dans les classes de la G�odatabase.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        prefixe     : Nom du pr�fixe utilis� pour cr�er les domaines d'attribut.
        subtype     : Nom de l'attribut contenant les subtypes.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Cr�er les domaines de SubTypes dans les classes de la G�odatabase")
        
        #D�finir le workspace par d�faut
        arcpy.env.workspace = workspace
        
        #Extraire la description de la G�odatabase
        for fc in classe.split(","):
            #D�finir le nom du domaine
            domaine = prefixe + "_" + subtype + "_" + fc
            
            #Afficher la cr�ation du domaine
            arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'LONG')")
            #Cr�er le domaine dans la G�odatabase
            arcpy.CreateDomain_management(workspace, domaine, domaine, "LONG")
            
            #D�finir aucun propri�taire de la classe par d�faut
            prop = ""
            #V�rifier si le propri�taire est pr�sent dans le nom de la classe
            if "." in fc:
                #D�finir le propri�taire de la classe
                prop = fc.split(".")[0] + "."
            
            #Cr�er la SQL pour extraire les subtypes
            sql = ("select distinct B.feat_type_code_bd, B.feat_type_NAME_FR"
                   "  from feat_catalogue A, feat_type B"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_name_database='" + fc.replace(prop,"") + "'"
                   " order by B.feat_type_code_bd")
            
            #arcpy.AddMessage(sql)
            #Ex�cuter la SQL
            resultat = self.BDG.query(sql)
            
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les r�sultats
                for valeur in resultat:
                    #Afficher l'ajout de la valeur cod�e au domaine
                    arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                    #Ajouter la valeur cod�e
                    arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1])
                
                #Afficher l'assignation du domaine � la classe
                arcpy.AddMessage(" AssignDomainToField_management('" + fc + "', '" + subtype + "', '" + domaine + "')")
                #Assigner le domaine � la classe
                arcpy.AssignDomainToField_management(fc, subtype, domaine)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def creerSubtype(self, catalogue, workspace, classe, subtype='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de cr�er les SubTypes dans les classes de la G�odatabase.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        subtype     : Nom de l'attribut contenant les subtypes.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Cr�er les SubTypes dans les classes de la G�odatabase")
        
        #D�finir le workspace par d�faut
        arcpy.env.workspace = workspace
        
        #Extraire la description de la G�odatabase
        for fc in classe.split(","):
            #Afficher le message
            arcpy.AddMessage(" SetSubtypeField_management('" + fc + "', '" + subtype + "')")
            #D�finir l'attribut qui contient le Subtype
            arcpy.SetSubtypeField_management(fc, subtype)
            
            #D�finir aucun propri�taire de la classe par d�faut
            prop = ""
            #V�rifier si le propri�taire est pr�sent dans le nom de la classe
            if "." in fc:
                #D�finir le propri�taire de la classe
                prop = fc.split(".")[0] + "."
            
            #Cr�er la SQL pour extraire les subtypes
            sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
                   "  from feat_catalogue A, feat_type B"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_name_database='" + fc.replace(prop,"") + "'"
                   " order by B.feat_type_code_bd")
            
            #arcpy.AddMessage(sql)
            #Ex�cuter la SQL
            resultat = self.BDG.query(sql)
            
            #V�rifier le r�sultat
            if resultat:
                #Traiter tous les r�sultats
                for valeur in resultat:
                    #Afficher le message
                    arcpy.AddMessage(" AddSubtype_management('" + fc + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                    #Ajouter un subtype � la classe
                    arcpy.AddSubtype_management(fc, valeur[0], str(valeur[0]) + ":" + valeur[1])   
                
                #Afficher le message
                arcpy.AddMessage(" SetDefaultSubtype_management('" + fc + "', " + str(resultat[0][0]) + ")")
                #D�finir le Subtype par d�faut
                arcpy.SetDefaultSubtype_management(fc, resultat[0][0])
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def creerDomaineAttribut(self, catalogue, workspace, classe, attribut, prefixe):
    #-------------------------------------------------------------------------------------
        """
        Permet de cr�er les domaines par attribut cod�.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        prefixe     : Nom du pr�fixe utilis� pour cr�er les domaines d'attribut.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Cr�er les domaines par attribut cod�")
        
        #D�finir le workspace par d�faut
        arcpy.env.workspace = workspace
        
        #Initialiser la liste des classes
        classes = ""
        #D�finir la liste des classes du catalogue
        for cls in classe.split(","):
            #D�finir le propri�taire par d�faut
            prop = ""
            #V�rifier si le propri�taire est pr�sent dans le nom
            if "." in (cls):
                #Extraire le propri�taire si pr�sent
                prop = cls.split(".")[0] + "."
            #Enlever le propri�taire de la classe si pr�sent
            classes = classes + "'" + cls.replace(prop,"").upper() + "',"
        #Enlever la derni�re virgule
        classes = classes[:-1]
        
        #Initialisation de la liste des domaines
        listeDomaine = []
        
        #Extraire la description de la G�odatabase
        desc = arcpy.Describe(workspace)
        
        #Extraire tous les domaines existants de la G�odatabase
        domains = desc.domains
        
        #Traiter tous les attributs
        for att in attribut.split(","):
            #D�finir le nom du domaine
            domaine = prefixe + "_" + att
            #Ajouter le domaine dans la liste
            listeDomaine.append(domaine)
            #Afficher le domaine
            arcpy.AddMessage(domaine)
            
            #Afficher la cr�ation du domaine
            arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'SHORT')")
            #Cr�er le domaine dans la G�odatabase
            arcpy.CreateDomain_management(workspace, domaine, domaine, "SHORT")
            
            #Cr�er la SQL pour d�finir le domaine
            sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE, E.ATTR_VALUE_LABEL_FR, E.ATTR_VALUE_LABEL_EN"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in (" + classes + ") and D.feat_attr_name_database='" + att + "'"
                   " order by E.ATTR_VALUE_INTERNAL_CODE")
            #arcpy.AddMessage(sql)
            #Ex�cuter la SQL
            resultat = self.BDG.query(sql)
            
            #Traiter tous les r�sultats
            for valeur in resultat:
                #Afficher l'ajout de la valeur cod�e au domaine
                arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                #Ajouter la valeur cod�e
                arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1] + " / " + valeur[2])
            
            #Cr�er la SQL pour assigner le domaine aux classes
            sql = ("select distinct B.feat_type_name_database"
                   "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                   " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                   "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                   "   and B.feat_type_name_database in (" + classes + ") and D.feat_attr_name_database='" + att + "'"
                   " order by B.feat_type_name_database")
            #arcpy.AddMessage(sql)
            #Ex�cuter la SQL
            resultat = self.BDG.query(sql)
            
            #Traiter toutes les classes
            for cls in resultat:
                try:
                    #Afficher l'assignation du domaine � la classe
                    arcpy.AddMessage(" AssignDomainToField_management('" + cls[0].lower() + "', '" + att + "', '" + domaine + "')")
                    #Assigner le domaine � la classe
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
        Permet de cr�er les domaines par classe et par attribut cod�.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        prefixe     : Nom du pr�fixe utilis� pour cr�er les domaines d'attribut.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Cr�er les domaines par classe et par attribut cod�")
        
        #Initialisation de la liste des domaines
        listeDomaine = {}
        #Traiter tous les attributs
        for att in attribut.split(","):
            #Initialisation du compteur de domaine par attribut
            nbDomAtt = 0
            #Traiter toutes les classes
            for cls in classe.split(","):
                #D�finir aucun propri�taire de la classe par d�faut
                prop = ""
                #V�rifier si le propri�taire est pr�sent dans le nom de la classe
                if "." in cls:
                    #D�finir le propri�taire de la classe
                    prop = cls.split(".")[0] + "."
                
                #Initialisation de la liste des valeurs
                listeValeur = []
                
                #Cr�er la SQL pour d�finir le domaine
                sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE, E.ATTR_VALUE_LABEL_FR"
                      "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                      " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                      "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                      "   and B.feat_type_name_database='" + cls.replace(prop,"") + "' and D.feat_attr_name_database='" + att + "'"
                      " order by E.ATTR_VALUE_INTERNAL_CODE")
                
                #arcpy.AddMessage(sql)
                #Ex�cuter la SQL
                resultat = self.BDG.query(sql)
                
                #V�rifier le r�sultat
                if resultat:
                    #Traiter tous les r�sultats
                    for valeur in resultat:
                        #Cr�er la liste des valeurs d'attribut
                        listeValeur.append(str(valeur[0]) + ":" + valeur[1])
                    
                    #V�rifier si le domaine absent
                    if str(listeValeur) not in listeDomaine:
                        #Compteur de domaine par attribut
                        nbDomAtt = nbDomAtt + 1
                        #D�finir le nom du domaine
                        domaine = prefixe + "_" + att + "_" + str(nbDomAtt)
                        #Ajouter le domaine dans la liste
                        listeDomaine[str(listeValeur)] = domaine
                        #Afficher le domaine
                        arcpy.AddMessage(" ")
                        arcpy.AddMessage(domaine)
                        
                        #Afficher la cr�ation du domaine
                        arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'LONG')")
                        #Cr�er le domaine dans la G�odatabase
                        arcpy.CreateDomain_management(workspace, domaine, domaine, "LONG")
                        
                        #Traiter toutes les valeurs
                        for val in listeValeur:
                            #S�parer le code de la description
                            valeur = val.split(":")
                            #Afficher l'ajout de la valeur cod�e au domaine
                            arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                            #Ajouter la valeur cod�e
                            arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1])
                    
                    #Si le domaine est pr�sent
                    else:
                        #D�finir le nom du domaine
                        domaine = listeDomaine[str(listeValeur)]
                    
                    try:
                        #Afficher l'assignation du domaine � la classe
                        arcpy.AddMessage(" AssignDomainToField_management('" + cls + "', '" + att + "', '" + domaine + "')")
                        #Assigner le domaine � la classe
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
        Permet de cr�er les domaines par code sp�cifique et par attribut cod�.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        prefixe     : Nom du pr�fixe utilis� pour cr�er les domaines d'attribut.
        
        """
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Cr�er les domaines par code sp�cifique et attribut cod�")
        
        #Initialisation de la liste des domaines
        listeDomaine = {}
        
        #Traiter tous les attributs
        for att in attribut.split(","):
            #Initialisation du compteur de domaines par attribut
            nbDomAtt = 0
            #Traiter toutes les classes
            for cls in classe.split(","):
                #D�finir aucun propri�taire de la classe par d�faut
                prop = ""
                #V�rifier si le propri�taire est pr�sent dans le nom de la classe
                if "." in cls:
                    #D�finir le propri�taire de la classe
                    prop = cls.split(".")[0] + "."
                #Initialisation de la liste des codes sp�cifiques par domaine
                listeCodeSpec = {}
                #Cr�er la SQL pour d�finir le domaine
                sql = ("select distinct B.feat_type_code_bd, B.feat_type_name_fr"
                       "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                       " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                       "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                       "   and B.feat_type_name_database='" + cls.replace(prop,"") + "' and D.feat_attr_name_database='" + att + "'"
                       " order by B.feat_type_code_bd")
                
                #arcpy.AddMessage(sql)
                #Ex�cuter la SQL
                codes = self.BDG.query(sql)
                
                #V�rifier si la classe poss�de l'attribut
                if codes:
                    #Traiter tous les codes sp�cifiques
                    for code in codes:
                        #Initialisation de la liste des valeurs
                        listeValeur = []
                        
                        #Cr�er la SQL pour d�finir le domaine
                        sql = ("select distinct E.ATTR_VALUE_INTERNAL_CODE, E.ATTR_VALUE_LABEL_FR"
                               "  from feat_catalogue A, feat_type B, relation_feat_attr C, feat_attr D, FEAT_ATTR_VALUE E"
                               " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                               "   and B.feat_type_id=C.feat_type_fk and C.feat_attr_fk=D.feat_attr_id AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK and D.feat_attr_domain_type=-1"
                               "   and B.feat_type_code_bd=" + str(code[0]) + " and B.feat_type_name_database='" + cls.replace(prop,"") + "' and D.feat_attr_name_database='" + att + "'"
                               " order by E.ATTR_VALUE_INTERNAL_CODE")
                        
                        #arcpy.AddMessage(sql)
                        #Ex�cuter la SQL
                        valeurs = self.BDG.query(sql)
                        
                        #Traiter tous les r�sultats
                        for valeur in valeurs:                        
                            #Cr�er la liste des valeurs d'attribut
                            listeValeur.append(str(valeur[0]) + ": " + valeur[1])
                            
                        #V�rifier si le domaine absent
                        if str(listeValeur) not in listeDomaine:
                            #Compteur de domaine par attribut
                            nbDomAtt = nbDomAtt + 1
                            #D�finir le nom du domaine
                            domaine = prefixe + "_" + att + "_" + str(nbDomAtt)
                            #Afficher le domaine
                            arcpy.AddMessage(" ")
                            arcpy.AddMessage(domaine)
                            #Ajouter le domaine dans la liste des domaines
                            listeDomaine[str(listeValeur)] = domaine
                            #Ajouter le code sp�cifique dans la liste des codes sp�cifiques
                            listeCodeSpec[domaine] = str(code[0])
                            
                            #Afficher la cr�ation du domaine
                            arcpy.AddMessage(" CreateDomain_management('" + workspace + "', '" + domaine + "', '" + domaine + "', 'LONG')")
                            #Cr�er le domaine dans la G�odatabase
                            arcpy.CreateDomain_management(workspace, domaine, domaine, "LONG")
                            
                            #Traiter toutes les valeurs
                            for val in listeValeur:
                                #S�parer le code de la description
                                valeur = val.split(":")
                                #Afficher l'ajout de la valeur cod�e au domaine
                                arcpy.AddMessage(" AddCodedValueToDomain_management('" + workspace + "', '" + domaine + "', " + str(valeur[0]) + ", '" + str(valeur[0]) + ":" + valeur[1] + "')")
                                #Ajouter la valeur cod�e
                                arcpy.AddCodedValueToDomain_management(workspace, domaine, valeur[0], str(valeur[0]) + ":" + valeur[1])
                        
                        #Si le domaine est pr�sent
                        else:
                            #D�finir le nom du domaine
                            domaine = listeDomaine[str(listeValeur)]
                            
                            #V�rifier si le domaine est absent de la liste des codes specifiques
                            if domaine not in listeCodeSpec:
                                #Ajouter le code sp�cifique dans la liste des codes sp�cifiques
                                listeCodeSpec[domaine] = str(code[0])
                            #Si le domaine est pr�sent
                            else:
                                #D�finir la liste des codes sp�cifiques
                                codeSpec = listeCodeSpec[domaine]
                                #Ajouter le code sp�cifique dans la liste des codes sp�cifiques
                                listeCodeSpec[domaine] = codeSpec + ";" + str(code[0])
                
                #Traiter tous les domaines de la classe 
                for domaine, codeSpec in listeCodeSpec.items():
                    try:
                        #Afficher l'assignation du domaine � la classe
                        arcpy.AddMessage(" AssignDomainToField_management('" + cls + "', '" + att + "', '" + domaine + "', '" + codeSpec + "')")
                        #Assigner le domaine � la classe
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
        Ex�cuter le traitement pour cr�er les domaines d'attributs cod�s dans une g�odatabase � partir de l'information contenue dans un catalogue.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        methode     : Nom de la m�thode utilis�e pour cr�er les domaines d'attributs [DOM_ATTRIBUT/DOM_CLASSE_ATTRIBUT/DOM_CODE_ATTRIBUT].
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        prefixe     : Nom du pr�fixe utilis� pour cr�er les domaines d'attribut.
        detruire    : Indique si tous les domaines d�j� pr�sents dans la G�odatabase seront d�truits (True) ou mis � jour (False).
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requ�te SQL � ex�cuter.
        """
        
        #V�rification de la pr�sence des param�tres obligatoires
        self.validerParamObligatoire(env, catalogue, methode, workspace, classe, attribut, prefixe)
        
        #V�rifier la connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Valider les valeurs des param�tres
        self.validerValeurParam(env, catalogue, methode, workspace)
            
        #Liste des domaines par attribut
        if methode == "DOM_ATTRIBUT":
            #V�rifier si on doit d�truire tous les domaines existants
            if detruire:
                #D�truire tous les domaines existants
                self.detruireDomaineAttribut(workspace)
            #Cr�er les domaines des subtypes
            #self.creerDomaineSubtype(catalogue, workspace, classe, prefixe, 'CODE_SPEC')
            #Cr�er les domaines d'attributs cod�s
            self.creerDomaineAttribut(catalogue, workspace, classe, attribut, prefixe)
        
        #Liste des domaines par classe et attribut
        elif methode == "DOM_CLASSE_ATTRIBUT":
            #V�rifier si on doit d�truire tous les domaines existants
            if detruire:
                #D�truire tous les domaines existants
                self.detruireDomaineAttribut(workspace)
            #Cr�er les domaines des subtypes
            self.creerDomaineSubtype(catalogue, workspace, classe, prefixe, 'CODE_SPEC')
            #Cr�er les domaines d'attributs cod�s
            self.creerDomaineClasseAttribut(catalogue, workspace, classe, attribut, prefixe)
        
        #Liste des domaines par code sp�cifique et attribut
        elif methode == "DOM_CODE_ATTRIBUT":
            #Cr�er les subtypes
            self.creerSubtype(catalogue, workspace, classe, 'CODE_SPEC')
            #V�rifier si on doit d�truire tous les domaines existants
            if detruire:
                #D�truire tous les domaines existants
                self.detruireDomaineAttribut(workspace)
            #Cr�er les domaines d'attributs cod�s
            self.creerDomaineCodeAttribut(catalogue, workspace, classe, attribut, prefixe)
        
        #V�rifier si le type de G�odatabase est LocalDatabase 
        if arcpy.Describe(workspace).workspaceType == "LocalDatabase":
            #Afficher le message
            arcpy.AddMessage("Compact_management('" + workspace + "')")
            #Compacter la G�obase
            arcpy.Compact_management(workspace)
        
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
        methode     = ""
        workspace   = ""
        classe      = ""
        attribut    = ""
        prefixe     = "DOM"
        detruire    = True
        
        #Lecture des param�tres
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
        
        #D�finir l'objet pour cr�er les domaines d'attributs cod�s dans une g�odatabase � partir de l'information contenue dans un catalogue.
        oCreerDomaineAttributCatalogue = CreerDomaineAttributCatalogue()
        
        #Ex�cuter le traitement pour cr�er les domaines d'attributs cod�s dans une g�odatabase � partir de l'information contenue dans un catalogue.
        oCreerDomaineAttributCatalogue.executer(env, catalogue, methode, workspace, classe, attribut, prefixe, detruire)
            
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