#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : AfficherInfoContrainteCatalogue.py
# Auteur    : Michel Pothier
# Date      : 05 mars 2015

"""
    Application qui permet d'afficher l'information sur les contraintes d'intégrité pour les classes selon un catalogue. 
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue.
                            défaut = 1:BDG
    sousCatalogue   OB      Numéro du sous-catalogue de classes.
                            défaut =
    classe          OP      Nom d'une classe contenue dans le catalogue spécifié.
                            défaut = 
    codeSpec        OP      Numéro d'un code spécifique contenue dans la classe spécifiée.
                            défaut = 
    contrainte      OP      Nom des containtes recherchées.
                            défaut = <Toutes les contraintes contenues dans le catalogue>
                            Attention : La contrainte est choisie en fonction de son identifiant.
                            identifiant:Nom de la contrainte
                            16904:Valider un masque spatial
                            116088:Valider le domaine d'attribut
                            30718640:Proximité
                            131019:Filtrage  
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        AfficherInfoContrainteCatalogue.py env catalogue sousCatalogue [classe] [codeSpec] [contrainte]
    
    Exemple:
        AfficherInfoContrainteCatalogue.py CATREL_PRO 1:BDG 92711:BDG-RHN NHN_HHYD_WATERBODY_2 "1480002:Région hydrique" #
    
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherInfoContrainteCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class AfficherInfoContrainteCatalogue(object):
#*******************************************************************************************
    """
    Permet d'afficher l'information sur les contraintes d'intégrité pour les classes selon un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher l'information sur les contraintes d'intégrité pour les classes selon un catalogue.
        
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
    def validerParamObligatoire(self, env, catalogue, sousCatalogue):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        
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
        if (len(sousCatalogue) == 0):
            raise Exception ('Paramètre obligatoire manquant: sousCatalogue')
        
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
        sql             : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier si le sous-catalogue est valide
        sql = ("SELECT FEAT_CATAL_ID, FEAT_CATAL_NAME_FR, FEAT_CATAL_NAME_EN"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND FEAT_CATAL_ID=" + sousCatalogue.split(":")[0] + " ")
        
        #Exécuter la requête SQL
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Numéro du sous-catalogue invalide : " + sousCatalogue)
        
        #Afficher l'information
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Sous-catalogue : " + str(resultat[0][0]) + ":" + resultat[0][1])
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherClasse(self, catalogue, sousCatalogue, classe, codeSpec, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les classes pour un catalogue.
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        contrainte      : Nom d'une containte liée au code spécifique.
        
        Variables:
        ----------
        sql             : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier si la classe est valide
        sql = ("SELECT DISTINCT B.FEAT_TYPE_NAME_DATABASE"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND FEAT_CATAL_ID=" + sousCatalogue.split(":")[0] + " ")
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
            #Afficher l'information
            arcpy.AddMessage(" ")
            arcpy.AddMessage("Classe : " + item[0])
            
            #Afficher l'information selon le code spécifique
            self.afficherCodeSpec(catalogue, sousCatalogue, item[0], codeSpec, contrainte)
            
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCodeSpec(self, catalogue, sousCatalogue, classe, codeSpec, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les codes spécifiques pour une ou plusieurs classes.
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        contrainte      : Nom d'une containte liée au code spécifique.
        
        Variables:
        ----------
        sql             : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier si le codeSpec est valide
        sql = ("SELECT DISTINCT B.FEAT_TYPE_CODE_BD, upper(B.FEAT_TYPE_NAME_FR)"
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
        #arcpy.AddMessage(sql)
        resultat = self.BDG.query(sql)
        
        #Vérifier le résultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Code spécifique invalide : " + codeSpec)
        
        #Afficher l'information
        codeGenerique = str(((resultat[0][0]/10000)*10000) + 9)
        arcpy.AddMessage("  CodeGen : " + str(codeGenerique)) 
        #Afficher l'information du code générique selon la contrainte
        self.afficherContrainte(catalogue, sousCatalogue, classe, codeGenerique, contrainte, "    Aucune contrainte générique")
        
       #Traiter tous les résultats
        for item in resultat:
            #Afficher l'information
            arcpy.AddMessage("  CodeSpec : " + str(item[0]) + ":" + str(item[1])) 
            #Afficher l'information selon la contrainte
            self.afficherContrainte(catalogue, sousCatalogue, classe, str(item[0]), contrainte, "    Aucune contrainte spécifique")
            
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def afficherContrainte(self, catalogue, sousCatalogue, classe, codeSpec, contraite, message=""):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information pour toutes les contraintes d'un code spécifique
        
        Paramètres:
        -----------
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        contrainte      : Nom d'une containte liée au code spécifique.
        message         : Message associé à la contrainte.
        
        Variables:
        ----------
        sql             : Requête SQL à exécuter.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Créer la requête SQL pour vérifier les contraintes
        sql = ("select C.constraint_id, CC.phys_const_id, CC.phys_const_name_fr"
               "  from feat_catalogue A, feat_type B, constraint C, phys_const CC"
               " where A.feat_catal_id=B.feat_catal_fk"
               "   and A.feat_catal_type=" + catalogue.split(":")[0] + " and B.feat_type_code_bd=" + codeSpec + " "
               "   and B.feat_type_id=C.feat_type_fk" 
               "   and C.phys_const_fk=CC.phys_const_id")
        
        #Vérifier si les contraintes sont présentes
        if len(contraite) > 0:
            #Créer la liste SQL des contraintes
            listeId = ""
            for item in contrainte.split(","):
                id = item.split(":")[0]
                if listeId == "":
                    listeId = listeId + id
                else:
                    listeId = listeId + "," + id
            #Ajouter les contraintes à rechercher
            sql = sql + " and CC.phys_const_id in (" + listeId + ")"
            
        #Ajouter le tri à la SQL
        sql = sql + " order by C.constraint_id, CC.phys_const_id"
        
        #Exécuter la requête SQL
        #arcpy.AddMessage(sql)
        resultat = self.BDG.query(sql)
        #arcpy.AddMessage(str(resultat))
        
        #Vérifier le résultat
        if resultat:
            #Traiter tous les résultats des contraintes
            for item in resultat:
                #Afficher l'information
                arcpy.AddMessage("    " + str(item[1]) + ":" + item[2] + " (ID Contrainte:" + str(item[0]) + ")")
                
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
                    #Vérifier si la contrainte est : Valider le domaine d'attribut=116088
                    if item[1] == 116088:
                        #Créer la requête SQL pour extraire le nom de l'attribut et l'expression régulière
                        sql = ("select EE.const_param_name_fr, F.p_value"
                               "  from parameter E, p_value F, const_param EE"
                               " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=F.parameter_fk and E.const_param_fk=EE.const_param_id")
                        #Exécuter la requête SQL
                        #arcpy.AddMessage(sql)
                        valResultat = self.BDG.query(sql)
                        #Traiter tous les résultats
                        for val in valResultat:
                            #Afficher l'information sur le masque spatial
                            arcpy.AddMessage("      " + val[0] + "=" + val[1])
                    
                    #Vérifier si la contrainte est : Valider un masque spatial=16904
                    elif item[1] == 16904:
                        #Vérifier si une relation est déjà présente
                        if present:
                            #Afficher un 'ou'
                            arcpy.AddMessage("                  ou")
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
                            arcpy.AddMessage("      (" + val[1] + "), " + val[2] + ", " + val[3])
                        
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
                            arcpy.AddMessage("      " + str(cls[2]) + ": " + str(cls[3]) + ": " + cls[4])
                        
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
                            arcpy.AddMessage("      " + att[2])
                    
                    #Vérifier si la contrainte est :
                    #Fltrage=131019, Proximité=30718640, Tolérances de changement=, Dimensions minimales externes, Dimensions minimales internes, etc
                    else:
                        #Créer la requête SQL pour extraire la largeur et la longueur
                        sql = ("select EE.const_param_name_fr, F.p_value"
                               "  from parameter E, p_value F, const_param EE"
                               " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=F.parameter_fk and E.const_param_fk=EE.const_param_id")
                        #Exécuter la requête SQL
                        #arcpy.AddMessage(sql)
                        valResultat = self.BDG.query(sql)
                        #Traiter tous les résultats
                        for val in valResultat:
                            #Afficher l'information sur le masque spatial
                            arcpy.AddMessage("      " + val[0] + "=" + val[1])
                        
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
                            arcpy.AddMessage("      " + str(cls[2]) + ": " + str(cls[3]) + ": " + cls[4])
                        
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
                            arcpy.AddMessage("      " + att[2])

                #Afficher l'information sur le masque spatial
                arcpy.AddMessage(" ")
                        
        #Si aucune contrainte
        else:
            #Envoyer un message d'avertissement
            arcpy.AddWarning(message)
            arcpy.AddMessage(" ")
            
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, sousCatalogue, classe, codeSpec, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour afficher l'information sur les contraintes d'intégrité pour les classes selon un catalogue.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        catalogue       : Numéro du catalogue.
        sousCatalogue   : Numéro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue spécifié.
        codeSpec        : Numéro d'un code spécifique contenue dans la classe spécifiée.
        contrainte      : Nom d'une containte liée au code spécifique.
               
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
        arcpy.AddMessage("- Affichage de l'information sur les contraintes")
        
        #Afficher l'information
        self.afficherCatalogue(catalogue)
        
        #Afficher l'information
        self.afficherSousCatalogue(catalogue, sousCatalogue)
        
        #Afficher l'information
        self.afficherClasse(catalogue, sousCatalogue, classe, codeSpec, contrainte)
        
        #Fermeture de la connexion de la BD BDG
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
        contrainte      = ""
        
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
                contrainte = sys.argv[6].replace(";",",").replace("'","")
        
        #Définir l'objet pour afficher l'information sur les contraintes d'intégrité pour les classes selon un catalogue.
        oAfficherInfoContrainteCatalogue = AfficherInfoContrainteCatalogue()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oAfficherInfoContrainteCatalogue.validerParamObligatoire(env, catalogue, sousCatalogue)
        
        #Exécuter le traitement pour afficher l'information sur les contraintes d'intégrité pour les classes selon un catalogue.
        oAfficherInfoContrainteCatalogue.executer(env, catalogue, sousCatalogue, classe, codeSpec, contrainte)
    
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