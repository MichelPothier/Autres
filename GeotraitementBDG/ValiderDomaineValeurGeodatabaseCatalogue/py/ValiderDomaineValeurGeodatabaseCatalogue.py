#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ValiderDomaineValeurGeodatabaseCatalogue.py
# Auteur    : Michel Pothier
# Date      : 09 mars 2015

"""
    Application qui permet de valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.

    Le catalogue contient des expressions régulières de validation pour chaque attribut (variable ou codé) d'un code spécifique.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            défaut = CATREL_PRO
    catalogue       OB      Numéro du catalogue.
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
        ValiderDomaineValeurGeodatabaseCatalogue.py env catalogue classe attribut workspace

    Exemple:
        ValiderDomaineValeurGeodatabaseCatalogue.py CATREL_PRO 1:BDG NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 WATER_DEFINITION,PERMANENCY "Database Connections\BDRS_PRO.sde"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderDomaineValeurGeodatabaseCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, re, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderDomaineValeurGeodatabaseCatalogue(object):
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
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
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
        catalogue   : Numéro du catalogue.
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
        env         : Type d'environnement.
        catalogue   : Numéro du catalogue.
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
        sql = ("SELECT DISTINCT FEAT_CATAL_TYPE FROM FEAT_CATALOGUE"
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
    def validerDomaineAttributClasse(self, catalogue, cls, codeGen, attribut, workspace, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut codé pour une classe de la Géodatabase en fonction du domaine contenu dans le catalogue.
        
        Paramètres:
        -----------
        catalogue   : Numéro du catalogue.
        cls         : Nom de la classe du catalogue à valider.
        codeGen     : Code générique de la classe du catalogue à valider.
        attribut    : Liste des noms d'attribut du catalogue à valider.
        workspace   : Nom de la géodatabase contenant les valeurs d'attribut à valider.
        codeSpec    : Nom de l'attribut de la Géodatabase contenant le code spécifique.
        
        Variables:
        ----------
        sql                 : Requête SQL à exécuter.
        att                 : Nom de l'attribut et du code spécifique à traiter.
        attResultat         : Liste des attributs et codes spécifiques à traiter.
        valCatalogue        : Ensemble des valeurs d'attributs du catalogue à traiter.
        attCatalogueErr     : Ensemble des valeurs attributs du catalogue en erreur.
        valGeodatabase      : Ensemble des valeurs d'attributs du catalogue à traiter.
        attGeodatabaseErr   : Ensemble des valeurs d'attributs du catalogue en erreur.
        """
        
        #Créer la SQL pour définir la liste des attributs à valider avec des expressions régulières
        sql =  (" select distinct F.p_value"
                "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk and E.const_param_fk=116089"
                "   and (B.feat_type_name_database='" + cls + "' or B.feat_type_code_bd=" + codeGen + ") and F.p_value in ('" + attribut.replace(",","','") + "')"
                " order by F.p_value")
        #arcpy.AddMessage(sql)
        #Exécuter la SQL
        attResultat = self.BDG.query(sql)
        
        #Traiter tous les attributs qui possèdent une expression régulière à valider
        for att in attResultat:
            #Afficher l'attribut à valider
            arcpy.AddMessage("  " + att[0])
            
            #Créer la SQL pour définir l'ensemble des valeurs de la Géodatabase
            sql = "select distinct " + codeSpec + "," + att[0] + " from BDG_DBA." + cls + " order by " + codeSpec + "," + att[0]
            #arcpy.AddMessage(sql)
            try:
                #Exécuter la SQL
                valResultat = self.SDE.execute(sql)
            #Gestion des erreurs
            except Exception, err:
                #Afficher l'erreur
                arcpy.AddMessage(sql)
                arcpy.AddError(err.message)
                valResultat = False
            
            #Vérifier la présence d'un résultat
            if valResultat and type(valResultat) == list:
                #Traiter tous les résultats des valeurs de la Géodatabase
                for val in valResultat:
                    #Afficher la valeurl'attribut à valider
                    #arcpy.AddMessage("    " + str(val[0]) + ", valeur=" + str(val[1]))
                    
                    #Créer la SQL pour extraire le nom du code spécifique et le numéro de relation
                    sql =  (" select D.relation_id, B.feat_type_code_bd, B.feat_type_name_fr"
                            "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                            " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                            "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                            "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk"
                            "   and (B.feat_type_code_bd=" + str(val[0]) + "or B.feat_type_code_bd=" + codeGen + ") AND F.p_value='" + att[0] + "'")
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
                            #Afficher la valeurl'attribut à valider
                            #arcpy.AddMessage("      Expression=" + expResultat[0][0])
                            try:
                                #Vérifier si la valeur respecte l'expression régulière
                                if not re.match(expResultat[0][0], str(val[1])):
                                    #Afficher la valeur de l'attribut à valider
                                    arcpy.AddMessage("      " + str(relResultat[0][1]) + ":" + relResultat[0][2] + " (rel=" + str(relResultat[0][0]) + ")")
                                    #Afficher un message d'erreur
                                    arcpy.AddWarning("      Valeur invalide : " + str(val[1]) + ", " + expResultat[0][0])
                            #Gestion des erreurs
                            except Exception, err:
                                #Afficher la valeur de l'attribut à valider
                                arcpy.AddMessage("      " + str(relResultat[0][1]) + ":" + relResultat[0][2] + " (rel=" + str(relResultat[0][0]) + ")")
                                #Afficher un message d'erreur
                                arcpy.AddError("      Expression régulière invalide : " + str(val[1]) + ", " + expResultat[0][0])
                        else:
                            #Afficher un message d'erreur
                            arcpy.AddError("Aucune expression régulière : " + str(val[1]))
                    else:
                        #Afficher un message d'erreur
                        arcpy.AddError("Aucune relation : " + att[0])
                        
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
        catalogue   : Numéro du catalogue.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        attribut    : Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
        workspace   : Nom de la géodatabase contenant les valeurs d'attribut à valider.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requête SQL à exécuter.
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
        arcpy.AddMessage("- Valider les valeurs des attributs de chaque classe entre le catalogue et la Géodatabase")
        
        #Créer la SQL pour extraire le code générique de chaque classe à valider
        sql =  (" select distinct B.feat_type_name_database, substr(to_char(B.feat_type_code_bd),1,3)||'0009'"
                "  from feat_catalogue A, feat_type B"
                " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_name_database in ('" + classe.replace(",","','") + "')"
                " order by B.feat_type_name_database")
        #arcpy.AddMessage(sql)
        #Exécuter la SQL
        resultat = self.BDG.query(sql)
        
        #Traiter toutes les classes à valider
        for cls in resultat:
            #Afficher un séparateur
            arcpy.AddMessage(" ")
        
            #Afficher le nom de la classe avec son code générique
            arcpy.AddMessage(cls[0] + ":"+ cls[1])
        
            #Valider les valeurs des attributs pour une classe en fonction des expressions régulières du catalogue
            self.validerDomaineAttributClasse(catalogue, cls[0], cls[1], attribut, workspace)
            
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
        oValiderDomaineValeurGeodatabaseCatalogue = ValiderDomaineValeurGeodatabaseCatalogue()
        
        #Exécuter le traitement pour valider les domaines des valeurs d'attributs d'une géodatabase en fonction de l'information contenue dans un catalogue.
        oValiderDomaineValeurGeodatabaseCatalogue.executer(env, catalogue, classe, attribut, workspace)
            
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