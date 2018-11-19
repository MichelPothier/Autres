#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : util_XmlCreerZT.py

"""
Utilitaire qui permet de g�rer un fichier XML sous le profil du service CreerZT.
"""

__revision__ = "--REVISION-- : $Id: util_XmlCreerZT.py 10061 2014-05-26 13:52:50Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, time
from xml.dom import minidom
from lxml import etree

#D�finition des constantes
NODE_SERVICE_BDRS = "bdrs:ServiceBdrs"
NODE_CREER_ZT = "bdrs:CreerZT"
NODE_TRANSACTION_ZONE = "bdrs:transactionZone"
NODE_POLYGON = "bdrs:polygon"
NODE_ZT_ID = "bdrs:zt_id"
NODE_REPOSITORY = "bdrs:repository"
NODE_PARTITION = "bdrs:partition"
NODE_FEATURE_LIST = "bdrs:featureList"
NODE_FEATURE_NAME = "bdrs:featureName"
NODE_METADATA = "bdrs:metadata"
NODE_CONTENT_INFO = "bdrs:contentInfo"
ATTR_FEATURE_CATALOGUE_ID = "featureCatalogueID"
NODE_CREATION_DATE = "bdrs:creation_date"
NODE_EXPECTED_DATE = "bdrs:expectedDate"

NOM_FICHIER_XSD = "W:\\EnvCits\\applications\\Gestion_BDRS\\pro\\ressources\\xsd\\lbd\\Par_CreerZT.xsd"
 
#*******************************************************************************************
class XmlCreerZT(object):
#*******************************************************************************************
    """
    Classe qui permet de traiter un document XML pour le service de transaction CreerZT.
    
    Variables:
        Aucune
    
    Retour:
        ErrorLevel      Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def __init__(self, nomFichierXML, nomFichierXSD=NOM_FICHIER_XSD):
    #-------------------------------------------------------------------------------------
        """
        Initialisation et lecture du fichier XML du service CreerZT.
        
        Param�tres:
        -----------
        nomFichierXML   Contient le nom du fichier XML du service CreerZT � traiter.
        nomFichierXSD   Contient le nom du fichier XML du service CreerZT � traiter.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Conserver le nom du fichier XSD
        self.nomFichierXSD = nomFichierXSD

        #Lire le fichier XML et conserver le nom et le contenu du document
        self.lire(nomFichierXML)

        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def lire(self, nomFichierXML):
    #-------------------------------------------------------------------------------------
        """
        Lecture du fichier XML du service CreerZT.
        On conserve le nom et le contenu du fichier XML pour le traitement.
        
        Param�tres:
        -----------
        nomFichierXML   Contient le nom du fichier XML du service CreerZT � traiter.
        
        Retour:
        -------
        Aucun

        """
        
        #V�rifier si le fichier XML est absent
        if not os.path.exists(nomFichierXML):
            #Envoyer une erreur d'ex�cution
            raise Exception("Fichier XML absent : %s" %nomFichierXML)
            
        #Conserver le nom du fichier XML
        self.nomFichierXML = nomFichierXML
        
        #Lire le fichier XML et conserver le contenu
        self.documentXML = minidom.parse(nomFichierXML)

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def ecrire(self, nomFichierXML, remplacer=True):
    #-------------------------------------------------------------------------------------
        """
        �criture sur disque du fichier XML pour le service CreerZT.
        
        Param�tres:
        -----------
        nomFichierXML   Contient le nom du fichier XML du service CreerZT � �crire sur disque.
        [remplacer]     Indiquer si on doit remplacer le fichier XML s'il est existant (D�f:True).
         
        Retour:
        -------
        Aucun
       
        """
        
        #V�rifier si le fichier XML est d�j� pr�sent et qu'on ne veut pas le remplacer
        if os.path.exists(nomFichierXML) and remplacer == False:
            #Envoyer une erreur d'ex�cution
            raise Exception("Fichier XML d�j� pr�sent : %s" %nomFichierXML)
        
        #Ouvrir le fichier XML en �criture        
        fichierXML = open(nomFichierXML,"wb")
        
        #�crire le contenu du XML dans le fichier
        self.documentXML.writexml(fichierXML)
        
        #Fermer le fichier XML        
        fichierXML.close()
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def obtenirNomFichierXML(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir le nom du fichier XML.
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        self.nomFichierXML        Nom du fichier XML.
        
        """
        
        #Sortir
        return self.nomFichierXML

    #-------------------------------------------------------------------------------------
    def valider(self, nomFichierXSD=""):
    #-------------------------------------------------------------------------------------
        """
        Valider le fichier XML selon le fichier XSD sp�cifi�.
        Si le fichier est valide aucune exception n'est retourn�e.
        Si le fichier est invalide, une exception est retourn�e.
        
        Param�tres:
        -----------
        nomFichierXSD   Contient le nom du fichier XSD utiliser pour valider le fichier XML.
        
        Retour:
        -------
        Exception       Exception retourn�e contenant le message d'erreur.
        
        """
        
        #V�rifier si le nom du fichier XSD est sp�cifi�
        if len(nomFichierXSD) > 0:
            #Conserver le nom du fichier XSD
            self.nomFichierXSD = nomFichierXSD

        #Lire le fichier XSD
        self.documentXSD = etree.parse(self.nomFichierXSD)

        #Cr�er un sch�ma de validation � partir du document XSD         
        self.schemaXSD = etree.XMLSchema(self.documentXSD)

        #Envoyer une exception si le fichier XML est invalide � partir du sch�ma XSD
        self.schemaXSD.assertValid(self.documentXML)

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def estValide(self, nomFichierXSD=""):
    #-------------------------------------------------------------------------------------
        """
        Permet d'indiquer si le fichier XML est valide (True) ou non (False).
        
        Param�tres:
        -----------
        nomFichierXSD   Contient le nom du fichier XML du service CreerZT � �crire sur disque.
        
        Retour:
        -------
        valide          Indique si le fichier XML est valide (True) ou non (False).
        
        """
        
        #V�rifier si le nom du fichier XSD est sp�cifi�
        if len(nomFichierXSD) > 0:
            #Conserver le nom du fichier XSD
            self.nomFichierXSD = nomFichierXSD

        #Lire le fichier XSD
        self.documentXSD = etree.parse(self.nomFichierXSD)

        #Cr�er un sch�ma de validation � partir du document XSD         
        self.schemaXSD = etree.XMLSchema(self.documentXSD)

        #D�finir si le fichier XML est valide ou non � partir du sch�ma XSD
        valide = self.schemaXSD.validate(self.documentXML)
        
        #Sortir
        return valide

    #-------------------------------------------------------------------------------------
    def obtenirDepot(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir le d�p�t de la zone de travail (ZtId).
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        depot        D�p�t de la zone de travail.
        
        """

        #Sortir
        return self.obtenirNoeudTexte(NODE_REPOSITORY)

    #-------------------------------------------------------------------------------------
    def definirDepot(self, depot):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir le d�p�t de la zone de travail (ZtId).
        
        Param�tres:
        -----------
        depot        D�p�t de la zone de travail.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Sortir
        return self.definirNoeudTexte(NODE_REPOSITORY, depot)

    #-------------------------------------------------------------------------------------
    def obtenirZtId(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir l'identifiant de la zone de travail (ZtId).
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        ztId        Identifiant de la zone de travail.
        
        """

        #Sortir
        return self.obtenirNoeudTexte(NODE_ZT_ID)

    #-------------------------------------------------------------------------------------
    def definirZtId(self, ztId):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir l'identifiant de la zone de travail (ZtId).
        
        Param�tres:
        -----------
        ztId        Identifiant de la zone de travail.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Sortir
        return self.definirNoeudTexte(NODE_ZT_ID, ztId)

    #-------------------------------------------------------------------------------------
    def obtenirPartition(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir la partition (Type de produit) reli�e � l'identifiant de la zone de travail.
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        partition        Partition reli�e � l'identifiant de la zone de travail.
        
        """
        
        #Sortir
        return self.obtenirNoeudTexte(NODE_PARTITION)

    #-------------------------------------------------------------------------------------
    def definirPartition(self, partition):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir la partition (Type de produit) reli�e � l'identifiant de la zone de travail.
        
        Param�tres:
        -----------
        partition        Partition reli�e � l'identifiant de la zone de travail.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Sortir
        return self.definirNoeudTexte(NODE_PARTITION, partition)

    #-------------------------------------------------------------------------------------
    def obtenirDateCreation(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir la date de cr�ation de la zone de travail.
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        dateCreation        Date de cr�ation de la zone de travail.
        
        """
        
        #Sortir
        return self.obtenirNoeudTexte(NODE_CREATION_DATE)

    #-------------------------------------------------------------------------------------
    def definirDateCreation(self, dateCreation):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir la date de cr�ation de la zone de travail.
        
        Param�tres:
        -----------
        dateCreation        Date de cr�ation de la zone de travail.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Sortir
        return self.definirNoeudTexte(NODE_CREATION_DATE, dateCreation)

    #-------------------------------------------------------------------------------------
    def obtenirDatePrevue(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir la date pr�vue de livraison reli�e � l'identifiant de la zone de travail.
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        datePrevue        Date pr�vue de livraison de la zone de travail.
        
        """
        
        #Sortir
        return self.obtenirNoeudTexte(NODE_EXPECTED_DATE)

    #-------------------------------------------------------------------------------------
    def definirDatePrevue(self, datePrevue):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir la date pr�vue de livraison reli�e � l'identifiant de la zone de travail.
        
        Param�tres:
        -----------
        datePrevue        Date pr�vue de livraison de la zone de travail.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Sortir
        return self.definirNoeudTexte(NODE_EXPECTED_DATE, datePrevue)

    #-------------------------------------------------------------------------------------
    def obtenirCatalogue(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir le nom du catalogue reli�e � l'identifiant de la zone de travail.
        Le nom du catalogue contient le num�ro du catalogue et de la norme.
        Le nom du catalogue est contenu sous un attribut dans un node.
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        catalogue        Nom du catalogue de la zone de travail.
        
        """
        
        #Le nom du catalogue est vide par d�faut
        catalogue = ''
        
        #Extraire le node FEATURE_LIST
        listNodeFeatureList = self.documentXML.getElementsByTagName(NODE_FEATURE_LIST)
        
        #V�rifier la pr�sence du node FEATURE_LIST
        if len(listNodeFeatureList) > 0:
            #D�finir le node FEATURE_LIST
            nodeFeatureList = listNodeFeatureList[0]
            
            #V�rifier si l'attribut du catalogue est pr�sent
            if nodeFeatureList.hasAttribute(ATTR_FEATURE_CATALOGUE_ID):
                #D�finir le nom du catalogue
                catalogue = str(nodeFeatureList.getAttribute(ATTR_FEATURE_CATALOGUE_ID))
        
        #Sortir
        return catalogue

    #-------------------------------------------------------------------------------------
    def definirCatalogue(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir le nom du catalogue reli�e � l'identifiant de la zone de travail.
        Le nom du catalogue contient le num�ro du catalogue et de la norme.
        Le nom du catalogue est contenu sous un attribut dans un node.
        
        Param�tres:
        -----------
        catalogue        Nom du catalogue de la zone de travail.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Extraire le node FEATURE_LIST
        listNodeFeatureList = self.documentXML.getElementsByTagName(NODE_FEATURE_LIST)
        
        #V�rifier la pr�sence du node FEATURE_LIST
        if len(listNodeFeatureList) > 0:
            #D�finir le node FEATURE_LIST
            nodeFeatureList = listNodeFeatureList[0]
            
            #V�rifier si l'attribut du catalogue est pr�sent
            if nodeFeatureList.hasAttribute(ATTR_FEATURE_CATALOGUE_ID):
                #V�finir le nom du catalogue
                nodeFeatureList.setAttribute(ATTR_FEATURE_CATALOGUE_ID, catalogue)
            
            #Si l'attribut ATTR_FEATURE_CATALOGUE_ID est absent
            else:
                #Erreur, l'attribut ATTR_FEATURE_CATALOGUE_ID est absent du fichier XML
                raise Exception("L'attribut %s est absent du fichier XML" %ATTR_FEATURE_CATALOGUE_ID)

        #Si le node FEATURE_LIST est absent
        else:
            #Erreur, le node FEATURE_LIST est absent du fichier XML
            raise Exception('Le noeud %s est absent du fichier XML' %NODE_FEATURE_LIST)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def obtenirPolygone(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir le polygone sous forme de Well Known Text.
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        polygonWKT      Coordonn�es du polygone sous forme de Well Known Text.
        
        """

        #Sortir
        return self.obtenirNoeudTexte(NODE_POLYGON)

    #-------------------------------------------------------------------------------------
    def definirPolygone(self, polygonWKT):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir le polygone sous forme de Well Known Text.
        
        Param�tres:
        -----------
        polygonWKT      Coordonn�es du polygone sous forme de Well Known Text.
        
        Retour:
        -------
        Aucun
        
        """

        #Sortir
        return self.definirNoeudTexte(NODE_POLYGON, polygonWKT)

    #-------------------------------------------------------------------------------------
    def obtenirListeNomElement(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir la liste des noms d'�l�ments
        (ex: BDG_CHEMIN_FER_1,BDG_COURBE_NIVEAU_1,BDG_LIGNE_TRANSPORT_ENERGIE_1).
        
        Param�tres:
        -----------
        Aucun
        
        Retour:
        -------
        listeNomElement        Liste des noms d'�l�ments s�par�s par une virgule.
        
        """

        #Initialiser la liste liste des noms d'�l�mente.
        listeNomElement = ''
        
        #Extraire le node FEATURE_NAME
        listNodeFeatureName = self.documentXML.getElementsByTagName(NODE_FEATURE_NAME)
        
        #V�rifier la pr�sence du node FEATURE_NAME
        for featureName in listNodeFeatureName:
            #D�finir la liste des noms d'�l�ments
            listeNomElement = listeNomElement + str(featureName.childNodes[0].data) + ','
            
        #V�rifier la pr�sence de noms d'�l�ments
        if len(listeNomElement) > 0:
            #Enlever le dernier ','
            listeNomElement = listeNomElement[:-1]
        
        #Sortir
        return listeNomElement

    #-------------------------------------------------------------------------------------
    def definirListeNomElement(self, listeNomElement):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir la liste des noms d'�l�ments.
        (ex: BDG_CHEMIN_FER_1,BDG_COURBE_NIVEAU_1,BDG_LIGNE_TRANSPORT_ENERGIE_1).

        Param�tres:
        -----------
        listeNomElement        Liste des noms d'�l�ments s�par� par une virgule.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Extraire le node FEATURE_LIST
        listNodeFeatureList = self.documentXML.getElementsByTagName(NODE_FEATURE_LIST)
        
        #V�rifier la pr�sence du node FEATURE_LIST
        if len(listNodeFeatureList) > 0:
            #D�finir le node FEATURE_LIST
            nodeFeatureList = listNodeFeatureList[0]

            #D�truire tous les nodes
            while len(nodeFeatureList.childNodes) > 0:
                #D�truire le dernier node
                nodeFeatureList.removeChild(nodeFeatureList.childNodes[len(nodeFeatureList.childNodes)-1])
                
            #Traiter tous les noms d'�l�ments pr�sents dans la liste de noms
            for nomElement in listeNomElement.split(','):
                #Cr�er le node TEXT contenant l'indentation
                nodeIndent = self.documentXML.createTextNode("\n        ")
                #Ajouter le node nodeIndent dans le node FEATURE_LIST
                nodeFeatureList.appendChild(nodeIndent)
                
                #Cr�er le node TEXT contenant le nom de l'�l�ment
                nodeText = self.documentXML.createTextNode(nomElement)
                #Cr�er le node FEATURE_NAME
                nodeFeatureName = self.documentXML.createElement(NODE_FEATURE_NAME)
                #Ajouter le nom de l'�l�ment dans le node FEATURE_NAME
                nodeFeatureName.appendChild(nodeText)
                #Ajouter le node FEATURE_NAME dans le node FEATURE_LIST
                nodeFeatureList.appendChild(nodeFeatureName)
                
            #Cr�er le node TEXT contenant l'indentation
            nodeIndent = self.documentXML.createTextNode("\n      ")
            #Ajouter le node nodeIndent dans le node FEATURE_LIST
            nodeFeatureList.appendChild(nodeIndent)
            
        #Si le node FEATURE_LIST est absent
        else:
            #Erreur, le node FEATURE_LIST est absent du fichier XML
            raise Exception('Le noeud %s est absent du fichier XML' %NODE_FEATURE_LIST)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def obtenirNoeudTexte(self, nomNoeud):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir la valeur d'un noeud de type texte.
        
        Param�tres:
        -----------
        nomNoeud        Nom du noeud trait�.
        
        Retour:
        -------
        valeurNoeud     Valeur texte du noeud trait�.
        
        """
        
        #La valeur du noeud est vide par d�faut
        valeurNoeud = ''
        
        #Extraire la liste des noeuds � traiter
        listNoeudTraiter = self.documentXML.getElementsByTagName(nomNoeud)
        
        #V�rifier la pr�sence du noeud
        if len(listNoeudTraiter) > 0:
            #D�finir le noeud trait�
            noeudTraiter = listNoeudTraiter[0]
            
            #V�rifier si le noeud a des enfants
            if noeudTraiter.hasChildNodes(): 
                #Extraire la valeur du noeud
                valeurNoeud = str(noeudTraiter.childNodes[0].data)
        
        #Sortir
        return valeurNoeud

    #-------------------------------------------------------------------------------------
    def definirNoeudTexte(self, nomNoeud, valeurNoeud):
    #-------------------------------------------------------------------------------------
        """
        Permet de d�finir la valeur d'un noeud de type texte.
        
        Param�tres:
        -----------
        nomNoeud        Nom du noeud trait�.
        valeurNoeud     Valeur texte du noeud trait�.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Extraire les noeuds � traiter
        listNoeudTraiter = self.documentXML.getElementsByTagName(nomNoeud)
        
        #V�rifier la pr�sence d'un noeud
        if len(listNoeudTraiter) > 0:
            #D�finir le noeud trait�
            noeudTraiter = listNoeudTraiter[0]
            
            #V�rifier si le noeud a des enfants
            if noeudTraiter.hasChildNodes(): 
                #D�finir la valeur du noeud
                noeudTraiter.childNodes[0].data = valeurNoeud
            #Si le node n'a pas d'enfant
            else:
                #Cr�er un TEXT NODE
                noeudText = self.documentXML.createTextNode(valeurNoeud)
                #Ajouter le TEXT NODE
                noeudTraiter.appendChild(noeudText)
                
        #Si le noeud est absent
        else:
            #Erreur, le node trait� est absent du fichier XML
            raise Exception('Le noeud %s est absent du fichier XML' %nomNoeud)
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par d�faut
        gabaritXml          = ""
        fichierXml          = ""
        listeNomElement     = ""
        
        #Instanciation de la classe XmlCreerZT
        oXmlCreerZT = XmlCreerZT(gabaritXml)
        
        #Remplacer la liste des noms d'�l�ments dans le fichier XML
        oXmlCreerZT.definirListeNomElement(listeNomElement)
        
    except Exception, err:
        #Sortir avec une erreur
        sys.exit(1)

    #Sortir sans erreur
    sys.exit(0)