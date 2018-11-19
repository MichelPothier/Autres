#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : DetruireDomaineAttribut.py
# Auteur    : Michel Pothier
# Date      : 13 juin 2016

"""
    Application qui permet de détruire tous les domaines d'attributs codés dans une géodatabase. 
    
    Paramètres d'entrée:
    --------------------
    workspace       OB      Nom de la géodatabase ou les domaines seront créés.
                            défaut =
    classe          OB      Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
                            défaut = <Toutes les classes présentent dans la géodatabase>
    attribut        OB      Liste des noms d'attribut codés à traiter selon les classes sélectionnées.
                            défaut = <Tous les attributs codés selon les classes sélectionnées>
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireDomaineAttribut.py env catalogue methode workspace classe attribut prefixe [detruire]

    Exemple:
        DetruireDomaineAttribu.py "Database Connections\BDRS_PRO.sde" NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 WATER_DEFINITION,PERMANENCY

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireSubtypeDomaineAttribut.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class DetruireDomaineAttribut(object):
#*******************************************************************************************
    """
    Permet de détruire tous les domaines d'attributs codés dans une géodatabase.
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
        Aucune
        """
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, workspace, classe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        #Valider la présence
        if (len(workspace) == 0):
            raise Exception ('Paramètre obligatoire manquant: workspace')
        
        #Valider la présence
        if (len(classe) == 0):
            raise Exception ('Paramètre obligatoire manquant: classe')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des paramètres.
        
        Paramètres:
        -----------
        workspace   : Nom de la géodatabase ou les domaines seront détruits.
        
        Variables:
        ----------
        Aucune
         
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Envoyer un message
        arcpy.AddMessage("- Vérification des valeurs des paramètres")
        
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
    def detruireDomaineAttribut(self, workspace, classe):
    #-------------------------------------------------------------------------------------
        """
        Permet de détruire tous les domaines existants dans la Géodatabase.
        
        Paramètres:
        -----------
        workspace   : Nom de la géodatabase ou les domaines seront détruits.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        
        """
        
        #Définir le workspace par défaut
        arcpy.env.workspace = workspace
        
        #Extraire les FeatureClass de la Géodatabase
        for fc in arcpy.ListFeatureClasses():
            #Vérifier si la classe est présente dans la liste des classes
            if fc.upper() in classe:
                #Afficher le message pour détruire les domaines de la classe traité
                arcpy.AddMessage(" ")
                arcpy.AddMessage(u"- Détruire les subtypes de la classe : " + fc)
                #Définir tous les Subtypes
                subtypes = arcpy.da.ListSubtypes(fc)
                #Vérifier si un Subtype est présent
                if subtypes.values()[0]['SubtypeField'] <> "":
                    #Afficher le message
                    arcpy.AddMessage("SetSubtypeField_management('" + fc + "', #, True)")
                    #Enlever les subtypes d'une classe
                    arcpy.SetSubtypeField_management(fc, "#", True)
                    
                    #Afficher les subtypes
                    #for stcode, stdict in list(subtypes.items()):
                        #Afficher le message
                        #arcpy.AddMessage(" RemoveSubtype_management('" + fc + "', '" + str(stcode) + "')")
                        #Détruire un subtype d'une classe
                        #arcpy.RemoveSubtype_management(fc, stcode)
                
                #Afficher le message pour détruire les domaines de la classe traité
                arcpy.AddMessage(u"- Détruire le domaine et la valeur par défaut pour chaque attribut de la classe : " + fc)
                #Traiter tous les fields
                for field in arcpy.ListFields(fc):
                    #Vérifier la présence d'un domaine
                    if field.domain <> "":
                        #Afficher le message
                        arcpy.AddMessage("RemoveDomainFromField_management('" + fc + "', '" + field.name + "')")
                        #Détruire un domaine dans un attribut d'une classe
                        arcpy.RemoveDomainFromField_management(fc, field.name)
                    
                    #Vérifier si une valeur par défaut est présente
                    if field.defaultValue <> None:
                        #Afficher le message
                        arcpy.AddMessage("AssignDefaultToField_management('" + fc + "', '" + field.name + "' # # True)")
                        #Détruire la valeur par défaut de l'attribut d'une classe
                        arcpy.AssignDefaultToField_management(fc, field.name, "#", "#", True)
                    
        #Extraire les tables de la Géodatabase
        for tbl in arcpy.ListTables():
            #Vérifier si la table est présente dans la liste des classes
            if tbl.upper() in classe:
                #Afficher le message pour détruire les domaines de la classe traité
                arcpy.AddMessage(" ")
                arcpy.AddMessage(u"- Détruire les subtypes de la table : " + tbl)
                #Définir tous les Subtypes
                subtypes = arcpy.da.ListSubtypes(tbl)
                #Vérifier si un Subtype est présent
                if subtypes.values()[0]['SubtypeField'] <> "":
                    #Afficher le message
                    arcpy.AddMessage("SetSubtypeField_management('" + tbl + "', #, True)")
                    #Enlever les subtypes d'une classe
                    arcpy.SetSubtypeField_management(tbl, "#", True)
                    
                    #Afficher les subtypes
                    #for stcode, stdict in list(subtypes.items()):
                        #Afficher le message
                        #arcpy.AddMessage(" RemoveSubtype_management('" + tbl + "', '" + str(stcode) + "')")
                        #Détruire un subtype d'une table
                        #arcpy.RemoveSubtype_management(tbl, stcode)
                
                #Afficher le message pour détruire les domaines de la classe traité
                arcpy.AddMessage(u"- Détruire le domaine et la valeur par défaut pour chaque attribut de la table : " + tbl)
                #Traiter tous les fields
                for field in arcpy.ListFields(tbl):
                    #Vérifier la présence d'un domaine
                    if field.domain <> "":
                        #Afficher le message
                        arcpy.AddMessage("RemoveDomainFromField_management('" + tbl + "', '" + field.name + "')")
                        #Détruire un domaine dans un attribut d'une classe
                        arcpy.RemoveDomainFromField_management(tbl, field.name)
                    
                    #Vérifier si une valeur par défaut est présente
                    if field.defaultValue <> None:
                        #Afficher le message
                        arcpy.AddMessage("AssignDefaultToField_management('" + tbl + "', '" + field.name + "' # # True)")
                        #Détruire la valeur par défaut de l'attribut d'une table
                        arcpy.AssignDefaultToField_management(tbl, field.name, "#", "#", True)
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage(u"- Détruire les domaines non-utilisés dans la Géodatabase")
        
        #Extraire la description de la Géodatabase
        desc = arcpy.Describe(workspace)
        
        #Extraire tous les domaines existants de la Géodatabase
        domains = desc.domains
        
        #Traiter tous les domaines
        for domain in domains:
            try:
                #Détruire un domaine
                arcpy.DeleteDomain_management(workspace, domain)
                #Afficher le message
                arcpy.AddMessage("DeleteDomain_management('" + workspace + "', '" + domain + "')")
            #Gestion des erreurs
            except Exception, err:
                #Afficher l'erreur
                arcpy.AddWarning(u"Le domaine est encore utilisé et ne peut être détruit : " + domain)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, workspace, classe):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire les domaines d'attributs codés dans une géodatabase.
        
        Paramètres:
        -----------
        workspace   : Nom de la géodatabase ou les domaines seront créés.
        classe      : Liste des noms de classe contenus dans la géodatabase utilisés pour créer les domaines.
        
        Variables:
        ----------
        Aucune
        """
        
        #Vérification de la présence des paramètres obligatoires
        self.validerParamObligatoire(workspace, classe)
       
        #Valider les valeurs des paramètres
        self.validerValeurParam(workspace)

        #Détruire tous les domaines existants
        self.detruireDomaineAttribut(workspace, classe)
        
        #Vérifier si le type de Géodatabase est LocalDatabase 
        if arcpy.Describe(workspace).workspaceType == "LocalDatabase":
            #Afficher le message
            arcpy.AddMessage("Compact_management('" + workspace + "')")
            #Compacter la Géobase
            arcpy.Compact_management(workspace)
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        workspace   = ""
        classe      = ""
        
        #Lecture des paramètres  
        if len(sys.argv) > 1:
            workspace = sys.argv[1]
        
        if len(sys.argv) > 2:
            classe = sys.argv[2].upper().replace(";",",")
        
        #Définir l'objet pour détruire les domaines d'attributs codés dans une géodatabase.
        oDetruireDomaineAttribut = DetruireDomaineAttribut()
        
        #Exécuter le traitement pour détruire les domaines d'attributs codés dans une géodatabase.
        oDetruireDomaineAttribut.executer(workspace, classe)
            
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