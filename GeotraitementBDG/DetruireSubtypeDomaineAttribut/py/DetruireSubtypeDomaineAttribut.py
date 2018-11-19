#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : DetruireDomaineAttribut.py
# Auteur    : Michel Pothier
# Date      : 13 juin 2016

"""
    Application qui permet de d�truire tous les domaines d'attributs cod�s dans une g�odatabase. 
    
    Param�tres d'entr�e:
    --------------------
    workspace       OB      Nom de la g�odatabase ou les domaines seront cr��s.
                            d�faut =
    classe          OB      Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
                            d�faut = <Toutes les classes pr�sentent dans la g�odatabase>
    attribut        OB      Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
                            d�faut = <Tous les attributs cod�s selon les classes s�lectionn�es>
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class DetruireDomaineAttribut(object):
#*******************************************************************************************
    """
    Permet de d�truire tous les domaines d'attributs cod�s dans une g�odatabase.
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
        Aucune
        """
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, workspace, classe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        #Valider la pr�sence
        if (len(workspace) == 0):
            raise Exception ('Param�tre obligatoire manquant: workspace')
        
        #Valider la pr�sence
        if (len(classe) == 0):
            raise Exception ('Param�tre obligatoire manquant: classe')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des param�tres.
        
        Param�tres:
        -----------
        workspace   : Nom de la g�odatabase ou les domaines seront d�truits.
        
        Variables:
        ----------
        Aucune
         
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification des valeurs des param�tres")
        
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
    def detruireDomaineAttribut(self, workspace, classe):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�truire tous les domaines existants dans la G�odatabase.
        
        Param�tres:
        -----------
        workspace   : Nom de la g�odatabase ou les domaines seront d�truits.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        
        """
        
        #D�finir le workspace par d�faut
        arcpy.env.workspace = workspace
        
        #Extraire les FeatureClass de la G�odatabase
        for fc in arcpy.ListFeatureClasses():
            #V�rifier si la classe est pr�sente dans la liste des classes
            if fc.upper() in classe:
                #Afficher le message pour d�truire les domaines de la classe trait�
                arcpy.AddMessage(" ")
                arcpy.AddMessage(u"- D�truire les subtypes de la classe : " + fc)
                #D�finir tous les Subtypes
                subtypes = arcpy.da.ListSubtypes(fc)
                #V�rifier si un Subtype est pr�sent
                if subtypes.values()[0]['SubtypeField'] <> "":
                    #Afficher le message
                    arcpy.AddMessage("SetSubtypeField_management('" + fc + "', #, True)")
                    #Enlever les subtypes d'une classe
                    arcpy.SetSubtypeField_management(fc, "#", True)
                    
                    #Afficher les subtypes
                    #for stcode, stdict in list(subtypes.items()):
                        #Afficher le message
                        #arcpy.AddMessage(" RemoveSubtype_management('" + fc + "', '" + str(stcode) + "')")
                        #D�truire un subtype d'une classe
                        #arcpy.RemoveSubtype_management(fc, stcode)
                
                #Afficher le message pour d�truire les domaines de la classe trait�
                arcpy.AddMessage(u"- D�truire le domaine et la valeur par d�faut pour chaque attribut de la classe : " + fc)
                #Traiter tous les fields
                for field in arcpy.ListFields(fc):
                    #V�rifier la pr�sence d'un domaine
                    if field.domain <> "":
                        #Afficher le message
                        arcpy.AddMessage("RemoveDomainFromField_management('" + fc + "', '" + field.name + "')")
                        #D�truire un domaine dans un attribut d'une classe
                        arcpy.RemoveDomainFromField_management(fc, field.name)
                    
                    #V�rifier si une valeur par d�faut est pr�sente
                    if field.defaultValue <> None:
                        #Afficher le message
                        arcpy.AddMessage("AssignDefaultToField_management('" + fc + "', '" + field.name + "' # # True)")
                        #D�truire la valeur par d�faut de l'attribut d'une classe
                        arcpy.AssignDefaultToField_management(fc, field.name, "#", "#", True)
                    
        #Extraire les tables de la G�odatabase
        for tbl in arcpy.ListTables():
            #V�rifier si la table est pr�sente dans la liste des classes
            if tbl.upper() in classe:
                #Afficher le message pour d�truire les domaines de la classe trait�
                arcpy.AddMessage(" ")
                arcpy.AddMessage(u"- D�truire les subtypes de la table : " + tbl)
                #D�finir tous les Subtypes
                subtypes = arcpy.da.ListSubtypes(tbl)
                #V�rifier si un Subtype est pr�sent
                if subtypes.values()[0]['SubtypeField'] <> "":
                    #Afficher le message
                    arcpy.AddMessage("SetSubtypeField_management('" + tbl + "', #, True)")
                    #Enlever les subtypes d'une classe
                    arcpy.SetSubtypeField_management(tbl, "#", True)
                    
                    #Afficher les subtypes
                    #for stcode, stdict in list(subtypes.items()):
                        #Afficher le message
                        #arcpy.AddMessage(" RemoveSubtype_management('" + tbl + "', '" + str(stcode) + "')")
                        #D�truire un subtype d'une table
                        #arcpy.RemoveSubtype_management(tbl, stcode)
                
                #Afficher le message pour d�truire les domaines de la classe trait�
                arcpy.AddMessage(u"- D�truire le domaine et la valeur par d�faut pour chaque attribut de la table : " + tbl)
                #Traiter tous les fields
                for field in arcpy.ListFields(tbl):
                    #V�rifier la pr�sence d'un domaine
                    if field.domain <> "":
                        #Afficher le message
                        arcpy.AddMessage("RemoveDomainFromField_management('" + tbl + "', '" + field.name + "')")
                        #D�truire un domaine dans un attribut d'une classe
                        arcpy.RemoveDomainFromField_management(tbl, field.name)
                    
                    #V�rifier si une valeur par d�faut est pr�sente
                    if field.defaultValue <> None:
                        #Afficher le message
                        arcpy.AddMessage("AssignDefaultToField_management('" + tbl + "', '" + field.name + "' # # True)")
                        #D�truire la valeur par d�faut de l'attribut d'une table
                        arcpy.AssignDefaultToField_management(tbl, field.name, "#", "#", True)
        
        #Envoyer un message
        arcpy.AddMessage(" ")
        arcpy.AddMessage(u"- D�truire les domaines non-utilis�s dans la G�odatabase")
        
        #Extraire la description de la G�odatabase
        desc = arcpy.Describe(workspace)
        
        #Extraire tous les domaines existants de la G�odatabase
        domains = desc.domains
        
        #Traiter tous les domaines
        for domain in domains:
            try:
                #D�truire un domaine
                arcpy.DeleteDomain_management(workspace, domain)
                #Afficher le message
                arcpy.AddMessage("DeleteDomain_management('" + workspace + "', '" + domain + "')")
            #Gestion des erreurs
            except Exception, err:
                #Afficher l'erreur
                arcpy.AddWarning(u"Le domaine est encore utilis� et ne peut �tre d�truit : " + domain)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, workspace, classe):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire les domaines d'attributs cod�s dans une g�odatabase.
        
        Param�tres:
        -----------
        workspace   : Nom de la g�odatabase ou les domaines seront cr��s.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        
        Variables:
        ----------
        Aucune
        """
        
        #V�rification de la pr�sence des param�tres obligatoires
        self.validerParamObligatoire(workspace, classe)
       
        #Valider les valeurs des param�tres
        self.validerValeurParam(workspace)

        #D�truire tous les domaines existants
        self.detruireDomaineAttribut(workspace, classe)
        
        #V�rifier si le type de G�odatabase est LocalDatabase 
        if arcpy.Describe(workspace).workspaceType == "LocalDatabase":
            #Afficher le message
            arcpy.AddMessage("Compact_management('" + workspace + "')")
            #Compacter la G�obase
            arcpy.Compact_management(workspace)
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        workspace   = ""
        classe      = ""
        
        #Lecture des param�tres  
        if len(sys.argv) > 1:
            workspace = sys.argv[1]
        
        if len(sys.argv) > 2:
            classe = sys.argv[2].upper().replace(";",",")
        
        #D�finir l'objet pour d�truire les domaines d'attributs cod�s dans une g�odatabase.
        oDetruireDomaineAttribut = DetruireDomaineAttribut()
        
        #Ex�cuter le traitement pour d�truire les domaines d'attributs cod�s dans une g�odatabase.
        oDetruireDomaineAttribut.executer(workspace, classe)
            
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