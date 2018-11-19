#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerXmlCreerZT.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
Application qui permet de créer un fichier XML pour chaque Zonede Travail (ZT) présente dans un FeatureLayer de ZT.

Les zones de travail sont créées dans un FeatureLayer en mémoire (FeatureSet) ou sélectionnées dans un FeatureLayer avec des découpages existants.

Les éléments créés ou sélectionnés sont utilisés pour ajouter l'identifiant et le polygone WKT dans un fichier XML correspondant à l'élément.
    
    Paramètres d'entrée:
    --------------------
    environnement       OB      type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                Valeur par défaut = SIB_PRO
    featureLayerZT      OB      FeatureLayer contenant les zones de travail
                                Valeur par défaut = FeatureSet
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
                                Valeur par défaut = DATASET_NAME
    gabaritXml          OB      Gabarit XML contenant l'information de base de la zone de travail à créer
                                Valeur par défaut = ""
    repertoireXml       OB      Nom du répertoire XML dans lequel les fichiers XML du service CreerZT seront créés.
                                Valeur par défaut = ""
    partition           OB      Nom de la partition traitée (Produit).
                                Valeur par défaut = "ESSIM"
    listeNomClasse      OB      Liste des noms de classe utilisée pour traiter la zone de travail.
                                Valeur par défaut = <Liste des noms d'éléments présents dans le gabarit XML>
    datePrevue          OP      Date prévue de fin des travaux.
                                Valeur par défaut = ""

    Paramètres de sortie:
    ---------------------
    listeFichierXml :   Liste des noms de fichier XML créés dans lesquels l'information du gabaritXML est présent
                        plus l'identifiant, le polygon WKT et les noms d'éléments.
                        (ex: 'repertoireXml'\'identifiant'_CreerZT.xml,...)

    Valeurs de retour:
    ------------------
    errorLevel :        Code du résultat de l'exécution du programme
                        (Ex: 0=Succès, 1=Erreur)

    Usage:
        CreerXmlCreerZT.py environnement featureLayerZT attributIdentifiant gabaritXML listeNomClasse repertoireXml listeNomClasse [datePrevue]

    Exemple: (si les éléments 021M07 et 021M08 sont sélectionnées dans le Layer DECOUPAGE.lyr)
        CreerXmlCreerZT.py TST D:\Travail\DECOUPAGE.lyr DATASET_NAME D:\Travail\CreerZT.xml D:\Travail HYDRO_TILE_2;BDG_NAMED_FEATURE_0 2014-09-24
        
        listeFichierXml = D:\Travail\021M07_fichier.xml,D:\Travail\021M08_fichier.xml
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerXmlCreerZT.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, datetime, arcpy, traceback
from xml.dom import minidom

#Importation des modules privés (Cits)
import util_XmlCreerZT

#*******************************************************************************************
class CreerXmlCreerZT(object):
#*******************************************************************************************
    """
    Classe qui permet de créer un fichier XML pour chaque zone de travail (ZT) créée ou sélectionnée
    dans un FeatureLayer selon le profil du service de transaction CreerZT.
    
    L'identifiant de la ZT doit être inscrit dans l'attribut d'identifiant du FeatureLayer spécifié.
    
    L'identifiant de la ZT est ajouté au début du nom des fichiers XML créés.
    
    """

    #-------------------------------------------------------------------------------------
    def __init__(self, gabaritXml):
    #-------------------------------------------------------------------------------------
        """
        Initialisation et lecture du fichier XML du service CreerZT.
        
        Paramètres:
        -----------
        gabaritXml :  Contient le nom du gabarit XML du service CreerZT à traiter.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Conserver le nom du GABARIT xml
        self.gabaritXml = gabaritXml
        
        #instanciation de la classe XmlCreerZT
        self.XmlCreerZT = util_XmlCreerZT.XmlCreerZT(gabaritXml)

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, featureLayerZT, attributIdentifiant, gabaritXml, repertoireXml, partition, listeNomClasse):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires

        Paramètres:
        -----------
        featureLayerZT         FeatureLayer contenant les zones de travail
        attributIdentifiant    Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
        gabaritXML             Gabarit XML contenant l'information de base de la zone de travail à créer
        repertoireXml          Nom du répertoire XML dans lequel les fichiers XML du service CreerZT seront créés.
        partition              Nom de la partition traitée (Produit).
        listeNomClasse         Liste des noms de classe.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        if (len(featureLayerZT) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'featureLayerZT')

        if (len(attributIdentifiant) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'attributIdentifiant')

        if (len(gabaritXml) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'gabaritXml')

        if (len(repertoireXml) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'repertoireXml')

        if (len(partition) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'partition')
        
        if (len(listeNomClasse) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'listeNomClasse')

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def creerFichierXml(self, featureLayer, attributIdentifiant, repertoireXml, partition, listeNomClasse, datePrevue):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de créer un fichier XML par élément présent dans le featureLayerZT
        et selon l'identifiant présent dans un attribut du featureLayer.
        
        Paramètres:
        -----------
        featureLayerZT         FeatureLayer contenant les zones de travail
        attributIdentifiant    Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
        repertoireXml          Nom du répertoire XML dans lequel les fichiers XML du service CreerZT seront créés.
        partition              Nom de la partition traitée (Produit).
        listeNomClasse         Liste des noms de classe.
        datePrevue             Date prévue de livraison des données de la zone de travail
        
        Retour:
        -------
        listeFichierXml        Liste des noms de fichiers XML créés (ex: D:\test\021M07.xml,D:\test\021M08.xml)
        """
        
        #remplacer la liste des noms d'éléments dans le fichier XML
        arcpy.AddMessage("  listeNomClasse: " + listeNomClasse)
        self.XmlCreerZT.definirListeNomElement(listeNomClasse)
        
        #remplacer le nom de la partition dans le fichier XML
        arcpy.AddMessage("  partition: " + partition)
        self.XmlCreerZT.definirPartition(partition)
        
        #afficher la date de création
        dateCreation = datetime.datetime.now().strftime("%Y-%m-%d")
        arcpy.AddMessage("  dateCreation: " + dateCreation)
        #définir la date de création
        self.XmlCreerZT.definirDateCreation(dateCreation)
        
        #afficher la date prévue
        arcpy.AddMessage("  datePrevue: " + datePrevue)
        #définir la date prévue
        self.XmlCreerZT.definirDatePrevue(datePrevue)
        
        #initialiser la liste des noms de fichiers XML     
        listeFichierXml = ""

        arcpy.AddMessage("-Lecture des identifiants")
        
        #traiter tous les éléments du FeatureLayer
        for row in arcpy.da.SearchCursor(featureLayer, [attributIdentifiant, "SHAPE@WKT"]):
            #afficher l'identifiant de l'élément
            arcpy.AddMessage("  ")
            arcpy.AddMessage("  " + attributIdentifiant + ": " + str(row[0]))
            #definir le ZT_ID
            self.XmlCreerZT.definirZtId(str(row[0]))
            
            #transformer le WKT de type MULTIPOLYGON en POLYGON 
            wkt = row[1].replace("MULTIPOLYGON","POLYGON")
            wkt = wkt.replace("(((","((")
            wkt = wkt.replace(")))","))")
            #afficher le polygone en WKT
            arcpy.AddMessage("  WKT:" + wkt)
            #definir le polygone dans le fichier XML
            self.XmlCreerZT.definirPolygone(wkt)
            
            #définir le nom du fichier XML selon le répertoire XML, l'identifiant et le nom du service à remplir
            nomIdentifiantFichierXml = repertoireXml + "\\" + str(row[0]) + "_CreerZT.xml"
            #afficher le nom du fichierXML
            arcpy.AddMessage("  fichierXML: " + nomIdentifiantFichierXml)
            #écrire le fichier XML
            self.XmlCreerZT.ecrire(nomIdentifiantFichierXml)
            #remplir la liste des noms de fichiers XML
            listeFichierXml = listeFichierXml + nomIdentifiantFichierXml + ";"
        
        #retirer le dernier ","
        if len(listeFichierXml) > 0:
            arcpy.AddMessage("  ")
            listeFichierXml = listeFichierXml[:-1]
        #Si aucun élément créé ou sélectionné
        else:
            #Lancer une erreur : Aucune zone de travail sélectionnée ou créée
            raise Exception("ERREUR : Aucune zone de travail selectionnee ou creee")
        
        #sortir
        return listeFichierXml

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        arcpy.AddMessage(sys.argv)
        env                 = "SIB_PRO"
        featureLayerZT      = ""
        attributIdentifiant = "DATASET_NAME"
        gabaritXml          = "S:\\applications\\sib\\pro\\xml\\gabarit_creerZT_RHN_OPP.xml"
        repertoireXml       = ""
        partition           = "ESSIM"
        listeNomClasse      = ""
        datePrevue          = ""
        listeFichierXml     = ""
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            featureLayerZT = sys.argv[2].upper()

        if len(sys.argv) > 3:
            attributIdentifiant = sys.argv[3].upper()

        if len(sys.argv) > 4:
            gabaritXml = sys.argv[4].upper()

        if len(sys.argv) > 5:
            repertoireXml = sys.argv[5].upper()

        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                partition = sys.argv[6].upper()
                
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                listeNomClasse = sys.argv[7].replace(";",",")

        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                datePrevue = sys.argv[8].split(" ")[0]
        
        #Affichage des paramètres
        arcpy.AddMessage("- env : " + env)
        arcpy.AddMessage("- featureLayerZT : " + featureLayerZT)
        arcpy.AddMessage("- attributIdentifiant : " + attributIdentifiant)
        arcpy.AddMessage("- gabaritXml : " + gabaritXml)
        arcpy.AddMessage("- repertoireXml : " + repertoireXml)
        arcpy.AddMessage("- partition : " + partition)
        arcpy.AddMessage("- listeNomClasse : " + listeNomClasse)
        arcpy.AddMessage("- datePrevue : " + datePrevue)
        
        #instanciation de la classe CreerZT
        oCreerXmlCreerZT = CreerXmlCreerZT(gabaritXml)
        
        #appel de la méthode validerParamObligatoire        
        arcpy.AddMessage("- Vérifier la présence des paramètres obligatoires")
        oCreerXmlCreerZT.validerParamObligatoire(featureLayerZT, attributIdentifiant, gabaritXml, repertoireXml, partition, listeNomClasse)
        
        #création des fichiers XML pour chaque élément présent dans le FeatureLayerZT
        arcpy.AddMessage("- Création des fichiers XML ...")
        listeFichierXml = oCreerXmlCreerZT.creerFichierXml(featureLayerZT, attributIdentifiant, repertoireXml, partition, listeNomClasse, datePrevue)
        
    except Exception, err:
        #afficher le message d'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #retourner la valeur de la liste des fichiers XML créés
        arcpy.SetParameterAsText(8, listeFichierXml)
        arcpy.AddMessage("  listeFichierXml : " + listeFichierXml)
        #sortir avec une erreur
        sys.exit(1)
    
    #affichier le message de succès
    arcpy.AddMessage("- Succès du traitement")
    #retourner la valeur de la liste des fichiers XML créés
    arcpy.SetParameterAsText(8, listeFichierXml)
    arcpy.AddMessage("  listeFichierXml : " + listeFichierXml)
    #Sortir sans code d'erreur
    sys.exit(0)