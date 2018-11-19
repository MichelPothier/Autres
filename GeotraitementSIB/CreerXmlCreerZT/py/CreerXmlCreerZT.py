#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerXmlCreerZT.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
Application qui permet de cr�er un fichier XML pour chaque Zonede Travail (ZT) pr�sente dans un FeatureLayer de ZT.

Les zones de travail sont cr��es dans un FeatureLayer en m�moire (FeatureSet) ou s�lectionn�es dans un FeatureLayer avec des d�coupages existants.

Les �l�ments cr��s ou s�lectionn�s sont utilis�s pour ajouter l'identifiant et le polygone WKT dans un fichier XML correspondant � l'�l�ment.
    
    Param�tres d'entr�e:
    --------------------
    environnement       OB      type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                Valeur par d�faut = SIB_PRO
    featureLayerZT      OB      FeatureLayer contenant les zones de travail
                                Valeur par d�faut = FeatureSet
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
                                Valeur par d�faut = DATASET_NAME
    gabaritXml          OB      Gabarit XML contenant l'information de base de la zone de travail � cr�er
                                Valeur par d�faut = ""
    repertoireXml       OB      Nom du r�pertoire XML dans lequel les fichiers XML du service CreerZT seront cr��s.
                                Valeur par d�faut = ""
    partition           OB      Nom de la partition trait�e (Produit).
                                Valeur par d�faut = "ESSIM"
    listeNomClasse      OB      Liste des noms de classe utilis�e pour traiter la zone de travail.
                                Valeur par d�faut = <Liste des noms d'�l�ments pr�sents dans le gabarit XML>
    datePrevue          OP      Date pr�vue de fin des travaux.
                                Valeur par d�faut = ""

    Param�tres de sortie:
    ---------------------
    listeFichierXml :   Liste des noms de fichier XML cr��s dans lesquels l'information du gabaritXML est pr�sent
                        plus l'identifiant, le polygon WKT et les noms d'�l�ments.
                        (ex: 'repertoireXml'\'identifiant'_CreerZT.xml,...)

    Valeurs de retour:
    ------------------
    errorLevel :        Code du r�sultat de l'ex�cution du programme
                        (Ex: 0=Succ�s, 1=Erreur)

    Usage:
        CreerXmlCreerZT.py environnement featureLayerZT attributIdentifiant gabaritXML listeNomClasse repertoireXml listeNomClasse [datePrevue]

    Exemple: (si les �l�ments 021M07 et 021M08 sont s�lectionn�es dans le Layer DECOUPAGE.lyr)
        CreerXmlCreerZT.py TST D:\Travail\DECOUPAGE.lyr DATASET_NAME D:\Travail\CreerZT.xml D:\Travail HYDRO_TILE_2;BDG_NAMED_FEATURE_0 2014-09-24
        
        listeFichierXml = D:\Travail\021M07_fichier.xml,D:\Travail\021M08_fichier.xml
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerXmlCreerZT.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, datetime, arcpy, traceback
from xml.dom import minidom

#Importation des modules priv�s (Cits)
import util_XmlCreerZT

#*******************************************************************************************
class CreerXmlCreerZT(object):
#*******************************************************************************************
    """
    Classe qui permet de cr�er un fichier XML pour chaque zone de travail (ZT) cr��e ou s�lectionn�e
    dans un FeatureLayer selon le profil du service de transaction CreerZT.
    
    L'identifiant de la ZT doit �tre inscrit dans l'attribut d'identifiant du FeatureLayer sp�cifi�.
    
    L'identifiant de la ZT est ajout� au d�but du nom des fichiers XML cr��s.
    
    """

    #-------------------------------------------------------------------------------------
    def __init__(self, gabaritXml):
    #-------------------------------------------------------------------------------------
        """
        Initialisation et lecture du fichier XML du service CreerZT.
        
        Param�tres:
        -----------
        gabaritXml :  Contient le nom du gabarit XML du service CreerZT � traiter.
        
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
        Validation de la pr�sence des param�tres obligatoires

        Param�tres:
        -----------
        featureLayerZT         FeatureLayer contenant les zones de travail
        attributIdentifiant    Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
        gabaritXML             Gabarit XML contenant l'information de base de la zone de travail � cr�er
        repertoireXml          Nom du r�pertoire XML dans lequel les fichiers XML du service CreerZT seront cr��s.
        partition              Nom de la partition trait�e (Produit).
        listeNomClasse         Liste des noms de classe.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        if (len(featureLayerZT) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'featureLayerZT')

        if (len(attributIdentifiant) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'attributIdentifiant')

        if (len(gabaritXml) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'gabaritXml')

        if (len(repertoireXml) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'repertoireXml')

        if (len(partition) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'partition')
        
        if (len(listeNomClasse) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'listeNomClasse')

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def creerFichierXml(self, featureLayer, attributIdentifiant, repertoireXml, partition, listeNomClasse, datePrevue):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de cr�er un fichier XML par �l�ment pr�sent dans le featureLayerZT
        et selon l'identifiant pr�sent dans un attribut du featureLayer.
        
        Param�tres:
        -----------
        featureLayerZT         FeatureLayer contenant les zones de travail
        attributIdentifiant    Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
        repertoireXml          Nom du r�pertoire XML dans lequel les fichiers XML du service CreerZT seront cr��s.
        partition              Nom de la partition trait�e (Produit).
        listeNomClasse         Liste des noms de classe.
        datePrevue             Date pr�vue de livraison des donn�es de la zone de travail
        
        Retour:
        -------
        listeFichierXml        Liste des noms de fichiers XML cr��s (ex: D:\test\021M07.xml,D:\test\021M08.xml)
        """
        
        #remplacer la liste des noms d'�l�ments dans le fichier XML
        arcpy.AddMessage("  listeNomClasse: " + listeNomClasse)
        self.XmlCreerZT.definirListeNomElement(listeNomClasse)
        
        #remplacer le nom de la partition dans le fichier XML
        arcpy.AddMessage("  partition: " + partition)
        self.XmlCreerZT.definirPartition(partition)
        
        #afficher la date de cr�ation
        dateCreation = datetime.datetime.now().strftime("%Y-%m-%d")
        arcpy.AddMessage("  dateCreation: " + dateCreation)
        #d�finir la date de cr�ation
        self.XmlCreerZT.definirDateCreation(dateCreation)
        
        #afficher la date pr�vue
        arcpy.AddMessage("  datePrevue: " + datePrevue)
        #d�finir la date pr�vue
        self.XmlCreerZT.definirDatePrevue(datePrevue)
        
        #initialiser la liste des noms de fichiers XML     
        listeFichierXml = ""

        arcpy.AddMessage("-Lecture des identifiants")
        
        #traiter tous les �l�ments du FeatureLayer
        for row in arcpy.da.SearchCursor(featureLayer, [attributIdentifiant, "SHAPE@WKT"]):
            #afficher l'identifiant de l'�l�ment
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
            
            #d�finir le nom du fichier XML selon le r�pertoire XML, l'identifiant et le nom du service � remplir
            nomIdentifiantFichierXml = repertoireXml + "\\" + str(row[0]) + "_CreerZT.xml"
            #afficher le nom du fichierXML
            arcpy.AddMessage("  fichierXML: " + nomIdentifiantFichierXml)
            #�crire le fichier XML
            self.XmlCreerZT.ecrire(nomIdentifiantFichierXml)
            #remplir la liste des noms de fichiers XML
            listeFichierXml = listeFichierXml + nomIdentifiantFichierXml + ";"
        
        #retirer le dernier ","
        if len(listeFichierXml) > 0:
            arcpy.AddMessage("  ")
            listeFichierXml = listeFichierXml[:-1]
        #Si aucun �l�ment cr�� ou s�lectionn�
        else:
            #Lancer une erreur : Aucune zone de travail s�lectionn�e ou cr��e
            raise Exception("ERREUR : Aucune zone de travail selectionnee ou creee")
        
        #sortir
        return listeFichierXml

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
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
        
        #extraction des param�tres d'ex�cution
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
        
        #Affichage des param�tres
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
        
        #appel de la m�thode validerParamObligatoire        
        arcpy.AddMessage("- V�rifier la pr�sence des param�tres obligatoires")
        oCreerXmlCreerZT.validerParamObligatoire(featureLayerZT, attributIdentifiant, gabaritXml, repertoireXml, partition, listeNomClasse)
        
        #cr�ation des fichiers XML pour chaque �l�ment pr�sent dans le FeatureLayerZT
        arcpy.AddMessage("- Cr�ation des fichiers XML ...")
        listeFichierXml = oCreerXmlCreerZT.creerFichierXml(featureLayerZT, attributIdentifiant, repertoireXml, partition, listeNomClasse, datePrevue)
        
    except Exception, err:
        #afficher le message d'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #retourner la valeur de la liste des fichiers XML cr��s
        arcpy.SetParameterAsText(8, listeFichierXml)
        arcpy.AddMessage("  listeFichierXml : " + listeFichierXml)
        #sortir avec une erreur
        sys.exit(1)
    
    #affichier le message de succ�s
    arcpy.AddMessage("- Succ�s du traitement")
    #retourner la valeur de la liste des fichiers XML cr��s
    arcpy.SetParameterAsText(8, listeFichierXml)
    arcpy.AddMessage("  listeFichierXml : " + listeFichierXml)
    #Sortir sans code d'erreur
    sys.exit(0)