#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerEtapeProduction.py
# Auteur    : Michel Pothier
# Date      : 5 janvier 2015

"""
    Application qui permet de créer un fichier ".ini" contenant l'information d'un catalogue.
   
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    datePublication OB      Date de publication du catalogue.
                            défaut = 
    dateProduction  OB      Date de mise en production du catalogue.
                            défaut = 
    depot           OB      Dépôt du catalogue à créer.
                            défaut = 
    produit         OB      Produit du catalogue à créer.
                            défaut = 
    version         OB      Version du catalogue à créer.
                            défaut = 1.0.0.0
    catalogue       OB      Nom du catalogue à créer.
                            défaut = 
    emplacement     OB      Emplacement des classes physiques de données.
                            défaut = 
    listeClasses    OB      Liste des classes contenues dans le catalogue.
                            défaut = <Toutes les classes liées à l'emplacement>
    repertoire      OB      Répertoire dans lequel le fichier de catalogue sera créé.
                            défaut = S:\applications\sib\pro\ini
    
    Paramètres de sortie:
    ---------------------
    nomFichierCatalogue     Nom du fichier de catalogue.
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerEtapeProduction.py env cd_etp nom nom_an active

    Exemple:
        CreerEtapeProduction.py SIB_PRO PREP 'Préparation' 'Preparation' 1
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerFichierCatalogue.py 2057 2016-06-15 21:03:15Z mpothier $"
#********************************************************************************************

# Importation des modules publics 
import os, sys, arcpy, datetime, ConfigParser, traceback

# Importation des modules privés
#import CompteSib

#*******************************************************************************************
class CreerFichierCatalogue(object):
#*******************************************************************************************
    """
    Permet de créer un fichier contenant l'information d'un catalogue.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'un fichier de catalogue.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.Config             : Objet utilitaire pour traiter le fichier de configuration.        
        
        """
        
        #Instanciation du fichier de configuration
        self.Config = ConfigParser.ConfigParser()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def Executer(self,env,datePublication,dateProduction,depot,produit,version,catalogue,emplacement,listeClasses,repertoire):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un fichier de catalogue.
        
        Paramètres:
        -----------
        env             : Type d'environnement correspondant à une base de données.
        datePublication : Date de publication du catalogue.
        dateProduction  : Date de mise en production du catalogue.
        depot           : Dépôt du catalogue à créer.
        produit         : Produit du catalogue à créer.
        version         : Version du catalogue à créer.
        catalogue       : Nom du catalogue à créer.
        emplacement     : Emplacement des classes physiques de données.
        listeClasses    : Liste des classes contenues dans le catalogue.
        repertoire      : Répertoire dans lequel le fichier de catalogue sera créé.
               
        Variables:
        ----------
        self.Config     : Objet utilitaire pour traiter le fichier de configuration.        
               
        Retour:
        ----------
        nomFichierCatalogue    : Nom du fichier de catalogue.
        
        """
        
        #Définir le nom du fichier de catalogue
        nomFichierCatalogue = repertoire + "\\" + catalogue.replace(".","-") + ".ini"
        
        #Ajouter la section CATALOGUE
        self.Config.add_section('CATALOGUE')
        
        #Ajouter le nom du catalogue
        self.Config.set('CATALOGUE', 'Nom', catalogue)
        
        #Ajouter le dépôt du catalogue
        self.Config.set('CATALOGUE', 'Depot', depot)
        
        #Ajouter le produit du catalogue
        self.Config.set('CATALOGUE', 'Produit', produit)
        
        #Ajouter la version du catalogue
        self.Config.set('CATALOGUE', 'Version', version)
        
        #Ajouter l'emplacement des données du catalogue
        self.Config.set('CATALOGUE', 'Date_publication', datePublication)
        
        #Ajouter l'emplacement des données du catalogue
        self.Config.set('CATALOGUE', 'Date_production', dateProduction)
        
        #Ajouter l'emplacement des données du catalogue
        self.Config.set('CATALOGUE', 'Emplacement', emplacement)
        
        #Définir l'espace de travail par défaut
        arcpy.env.workspace = emplacement
        
        #Ajouter toutes les classes du catalogue
        for classe in listeClasses.split(","):
            #Extraire l'information
            desc = arcpy.Describe(classe)
            dataType = str(desc.dataType)
            #Ajouter la section du nom de la classe
            self.Config.add_section(classe)
            #Ajouter l'information de la classe
            self.Config.set(classe, 'desc_fr', classe)
            self.Config.set(classe, 'desc_an', classe)
            #Afficher la classe traitée
            arcpy.AddMessage(classe + "," + dataType)
            #Vérifier si le type de données est géométrique
            if dataType == 'FeatureClass':
                #Extraire l'information
                oidFieldName = str(desc.OIDFieldName)
                shapeFieldName = str(desc.shapeFieldName)
                shapeType = str(desc.shapeType)
                hasZ = desc.hasZ
                hasM = desc.hasM
                #Écrire l'information
                self.Config.set(classe, 'type', 'G')
                self.Config.set(classe, 'att_uid', 'FEATURE_ID')
                self.Config.set(classe, 'att_zt', 'ZT_ID')
                self.Config.set(classe, 'att_oid', oidFieldName)
                self.Config.set(classe, 'att_shp', shapeFieldName)
                if shapeType == 'Point':
                    self.Config.set(classe, 'geometrie', '0')
                elif shapeType == 'Polyline':
                    self.Config.set(classe, 'geometrie', '1')
                elif shapeType == 'Polygon':
                    self.Config.set(classe, 'geometrie', '2')
                if hasZ:
                    self.Config.set(classe, 'z', '1')
                else:
                    self.Config.set(classe, 'z', '0')
                if hasM:
                    self.Config.set(classe, 'm', '1')
                else:
                    self.Config.set(classe, 'm', '0')
            #Si le type de données est seulement attributif
            else:
                self.Config.set(classe, 'Type', 'A')
                #Vérifier la présence du OID
                if desc.hasOID:
                    #Extraire le OID
                    oidFieldName = str(desc.OIDFieldName)
                    #Écrire le OID
                    self.Config.set(classe, 'Att_oid', oidFieldName)
            
        #Écrire le fichier de catalogue
        arcpy.AddMessage("- Écriture du fichier de catalogue")
        with open(nomFichierCatalogue, 'w') as oConfigFile:
            self.Config.write(oConfigFile)
        
        #Sortir et retourner le nom du fichier de catalogue
        return nomFichierCatalogue

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env             = "SIB_PRO"
        datePublication = ""
        dateProduction  = ""
        depot           = ""
        produit         = ""
        version         = ""
        catalogue       = ""
        emplacement     = ""
        listeClasses    = ""
        repertoire      = ""
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            datePublication = sys.argv[2]
        
        if len(sys.argv) > 3:
            dateProduction = sys.argv[3]
        
        if len(sys.argv) > 4:
            depot = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            produit = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            version = sys.argv[6]
        
        if len(sys.argv) > 7:
            catalogue = sys.argv[7]
        
        if len(sys.argv) > 8:
            emplacement = sys.argv[8]
        
        if len(sys.argv) > 9:
            listeClasses = sys.argv[9].replace(";",",")
        
        if len(sys.argv) > 10:
            repertoire = sys.argv[10]
        
        #Définir l'objet de création d'un fichier de catalogue.
        oCreerFichierCatalogue = CreerFichierCatalogue()
        
        #Exécuter le traitement de création d'un fichier de catalogue.
        nomFichierCatalogue = oCreerFichierCatalogue.Executer(env,datePublication,dateProduction,depot,produit,version,catalogue,emplacement,listeClasses,repertoire)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        arcpy.SetParameterAsText(10, nomFichierCatalogue)
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("- Succès du traitement")
    arcpy.SetParameterAsText(10, nomFichierCatalogue)
    #Sortir sans code d'erreur
    sys.exit(0)