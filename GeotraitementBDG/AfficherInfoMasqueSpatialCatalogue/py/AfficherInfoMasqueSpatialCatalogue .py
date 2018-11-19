#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : AfficherInfoMasqueSpatialCatalogue.py
# Auteur    : Michel Pothier
# Date      : 13 avril 2015

"""
    Application qui permet d'afficher l'information sur les contraintes d'intégrité de type masque spatial pour les classes selon un catalogue. 
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue.
                            défaut = 1:BDG
    relation        OB      Liste des masques spatiaux à afficher.
                            défaut = 
    classe          OP      Nom des classes contenues dans le catalogue spécifié qui possèdent les relations.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        AfficherInfoMasqueSpatialCatalogue.py env catalogue relation [classe]
    Exemple:
        AfficherInfoMasqueSpatialCatalogue.py CATREL_PRO 1:BDG "(1*T,***,T**): CHEVAUCHE 1/1" BDG_AIRE_DESIGNEE_0;NHN_HHYD_WATERBODY_2
    
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherInfoMasqueSpatialCatalogue .py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class AfficherInfoMasqueSpatialCatalogue(object):
#*******************************************************************************************
    """
    Permet d'afficher l'information sur les contraintes d'intégrité de type masque spatial pour les classes selon un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher l'information sur les contraintes d'intégrité de type masque spatial pour les classes selon un catalogue.
        
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
    def validerParamObligatoire(self, env, catalogue, relation):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        catalogue       : Numéro du catalogue.
        relation        : Liste des masques spatiaux à afficher.
        
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
        
        #Valider la présence
        if (len(relation) == 0):
            raise Exception ('Paramètre obligatoire manquant: relation')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCatalogue(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur le catalogue
        
        Paramètres:
        -----------
        catalogue    : Numéro du catalogue.
        
        Variables:
        ----------
        sql         : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier si le catalogue est valide
        sql = "SELECT DISTINCT FEAT_CATAL_TYPE FROM FEAT_CATALOGUE WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " "
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #Afficher l'information
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Catalogue : " + catalogue)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherRelation(self, catalogue, relation, classe):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les relations.
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        relation        : Liste des masques spatiaux à afficher.
        classe          : Nom des classes contenues dans le catalogue spécifié.
        
        Variables:
        ----------
        sql             : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Initialisation de la liste des masques spatials
        masque=""
        
        #Traiter toutes les relations
        for msk in relation.split(";"):
            #Construire la liste des masques
            masque = masque + "'" + msk.split(":")[0] + "',"
        #Enlever la dernière virgule
        masque = masque[:-1]
    
        #Créer la requête SQL pour vérifier les contraintes
        sql = ("SELECT DISTINCT D.CONSTRAINT_FK, B.FEAT_TYPE_NAME_DATABASE, B.FEAT_TYPE_CODE_BD, B.FEAT_TYPE_NAME_FR"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B, CONSTRAINT C, PHYS_CONST CC, RELATION D, PARAMETER E, P_VALUE F, EGEN_MASK KK"
               " WHERE A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " "
               "   AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.PHYS_CONST_FK=CC.PHYS_CONST_ID"
               "   AND C.CONSTRAINT_ID=D.CONSTRAINT_FK AND D.RELATION_ID=E.REL_ID_FK"
               "   AND E.PARAMETER_ID=F.PARAMETER_FK AND F.EGEN_MASK_FK=KK.EGEN_MASK_ID"
               "   AND KK.EGEN_MASK_VIEW_MASK_S IN (" + masque + ")")
        #Vérifier si les classes sont spécifiées
        if len(classe) > 0:
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IN ('" + classe.replace(",","','") + "')"
        #else:
            #sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IS NOT NULL"
        #Ajouter le tri
        sql = sql + " ORDER BY B.FEAT_TYPE_CODE_BD, D.CONSTRAINT_FK"
        #Exécuter la requête SQL
        #arcpy.AddMessage(sql)
        resultat = self.BDG.query(sql)

        #Traiter tous les résultats des contraintes
        for item in resultat:
            #Créer la requête SQL pour extraire toutes les relations de la contrainte
            sql = ("select D.relation_id"
                   "  from relation D"
                   " where D.constraint_fk=" + str(item[0]) + " "
                   "   order by D.relation_id")
            #Exécuter la requête SQL
            #arcpy.AddMessage(sql)
            relResultat = self.BDG.query(sql)
            
            #Identifier qu'aucune relation n'est présente
            present = False
            
            #Traiter toutes les relations de la contraintes
            for rel in relResultat:
                #Vérifier si une relation est déjà présente
                if present:
                    #Afficher un 'ou'
                    arcpy.AddMessage("  ou")
                else:
                    #Afficher la classe
                    arcpy.AddMessage(" ")
                    arcpy.AddMessage(str(item[1]) + ": " + str(item[2]) + ": " + item[3])
                #Indiquer qu'une relation est présente
                present=True
                
                #Créer la requête SQL pour extraire toutes les relations de la contrainte
                sql = ("select F.egen_mask_fk, F.egen_cardinality, KK.egen_mask_name_fr, KK.egen_mask_view_mask_s, F.egen_expect"
                       "  from parameter E, p_value F, egen_mask KK"
                       " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=F.parameter_fk and F.egen_mask_fk=KK.egen_mask_id")
                #Exécuter la requête SQL
                #arcpy.AddMessage(sql)
                valResultat = self.BDG.query(sql)
                #Traiter tous les résultats
                for val in valResultat:
                    #Afficher l'information sur le masque spatial
                    arcpy.AddMessage("  (" + val[1] + "), " + val[2] + ", " + val[3])
                
                #Créer la requête SQL pour extraire toutes les classes en relation
                sql = ("select H.feat_list_id, H.feat_fk, B.feat_type_name_database, B.feat_type_code_bd, B.feat_type_name_fr"
                       "  from parameter E, feat_list H, feat_type B"
                       " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=H.param_feat_fk and H.feat_fk=B.feat_type_id")
                #Exécuter la requête SQL
                #arcpy.AddMessage(sql)
                clsResultat = self.BDG.query(sql)
                #Traiter tous les résultats
                for cls in clsResultat:
                    #Afficher l'information sur les classes en relation
                    arcpy.AddMessage("  " + str(cls[2]) + ": " + str(cls[3]) + ": " + cls[4])
                
                #Créer la requête SQL pour extraire tous les attributs en relation
                sql = ("select G.attr_list_id, G.attr_fk, GG.feat_attr_name_database"
                       "  from parameter E, attr_list G, feat_attr GG"
                       " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=G.param_attr_fk and G.attr_fk=GG.feat_attr_id")
                #Exécuter la requête SQL
                #arcpy.AddMessage(sql)
                attResultat = self.BDG.query(sql)
                #Traiter tous les résultats
                for att in attResultat:
                    #Afficher l'information sur les attributs en relation
                    arcpy.AddMessage("  " + att[2])
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, relation, classe):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour afficher l'information sur les contraintes d'intégrité de type masque spatial pour les classes selon un catalogue.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        catalogue       : Numéro du catalogue.
        relation        : Liste des masques spatiaux à afficher.
        classe          : Nom des classes contenues dans le catalogue spécifié.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requête SQL à exécuter.
        """
        
        #Instanciation de la classe BDG et connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Affichage de l'information
        arcpy.AddMessage("- Affichage de l'information sur les masques spatiaux")
        
        #Afficher l'information sur le catalogue
        self.afficherCatalogue(catalogue)
        
        #Afficher l'information sur les relations
        self.afficherRelation(catalogue, relation, classe)
        
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
        relation        = ""
        classe          = ""
        
        #Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]
        
        if len(sys.argv) > 3:
            relation = sys.argv[3].upper().replace("'","")
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                classe = sys.argv[4].upper().replace(";",",")
        
        #Définir l'objet pour afficher l'information sur les contraintes d'intégrité de type masque spatial pour les classes selon un catalogue.
        oAfficherInfoMasqueSpatialCatalogue = AfficherInfoMasqueSpatialCatalogue()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oAfficherInfoMasqueSpatialCatalogue.validerParamObligatoire(env, catalogue, relation)
        
        #Exécuter le traitement pour afficher l'information sur les contraintes d'intégrité de type masque spatial pour les classes selon un catalogue.
        oAfficherInfoMasqueSpatialCatalogue.executer(env, catalogue, relation, classe)
    
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