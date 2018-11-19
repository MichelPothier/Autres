#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : util_XmlCreerZT.py

"""
Utilitaire qui permet de gérer un fichier XML sous le profil du service CreerZT.
"""

__revision__ = "--REVISION-- : $Id: util_XmlCreerZT.py 10061 2014-05-26 13:52:50Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, time
from xml.dom import minidom
from lxml import etree

#Définition des constantes
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
        ErrorLevel      Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def __init__(self, nomFichierXML, nomFichierXSD=NOM_FICHIER_XSD):
    #-------------------------------------------------------------------------------------
        """
        Initialisation et lecture du fichier XML du service CreerZT.
        
        Paramètres:
        -----------
        nomFichierXML   Contient le nom du fichier XML du service CreerZT à traiter.
        nomFichierXSD   Contient le nom du fichier XML du service CreerZT à traiter.
        
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
        
        Paramètres:
        -----------
        nomFichierXML   Contient le nom du fichier XML du service CreerZT à traiter.
        
        Retour:
        -------
        Aucun

        """
        
        #Vérifier si le fichier XML est absent
        if not os.path.exists(nomFichierXML):
            #Envoyer une erreur d'exécution
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
        Écriture sur disque du fichier XML pour le service CreerZT.
        
        Paramètres:
        -----------
        nomFichierXML   Contient le nom du fichier XML du service CreerZT à écrire sur disque.
        [remplacer]     Indiquer si on doit remplacer le fichier XML s'il est existant (Déf:True).
         
        Retour:
        -------
        Aucun
       
        """
        
        #Vérifier si le fichier XML est déjà présent et qu'on ne veut pas le remplacer
        if os.path.exists(nomFichierXML) and remplacer == False:
            #Envoyer une erreur d'exécution
            raise Exception("Fichier XML déjà présent : %s" %nomFichierXML)
        
        #Ouvrir le fichier XML en écriture        
        fichierXML = open(nomFichierXML,"wb")
        
        #Écrire le contenu du XML dans le fichier
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
        
        Paramètres:
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
        Valider le fichier XML selon le fichier XSD spécifié.
        Si le fichier est valide aucune exception n'est retournée.
        Si le fichier est invalide, une exception est retournée.
        
        Paramètres:
        -----------
        nomFichierXSD   Contient le nom du fichier XSD utiliser pour valider le fichier XML.
        
        Retour:
        -------
        Exception       Exception retournée contenant le message d'erreur.
        
        """
        
        #Vérifier si le nom du fichier XSD est spécifié
        if len(nomFichierXSD) > 0:
            #Conserver le nom du fichier XSD
            self.nomFichierXSD = nomFichierXSD

        #Lire le fichier XSD
        self.documentXSD = etree.parse(self.nomFichierXSD)

        #Créer un schéma de validation à partir du document XSD         
        self.schemaXSD = etree.XMLSchema(self.documentXSD)

        #Envoyer une exception si le fichier XML est invalide à partir du schéma XSD
        self.schemaXSD.assertValid(self.documentXML)

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def estValide(self, nomFichierXSD=""):
    #-------------------------------------------------------------------------------------
        """
        Permet d'indiquer si le fichier XML est valide (True) ou non (False).
        
        Paramètres:
        -----------
        nomFichierXSD   Contient le nom du fichier XML du service CreerZT à écrire sur disque.
        
        Retour:
        -------
        valide          Indique si le fichier XML est valide (True) ou non (False).
        
        """
        
        #Vérifier si le nom du fichier XSD est spécifié
        if len(nomFichierXSD) > 0:
            #Conserver le nom du fichier XSD
            self.nomFichierXSD = nomFichierXSD

        #Lire le fichier XSD
        self.documentXSD = etree.parse(self.nomFichierXSD)

        #Créer un schéma de validation à partir du document XSD         
        self.schemaXSD = etree.XMLSchema(self.documentXSD)

        #Définir si le fichier XML est valide ou non à partir du schéma XSD
        valide = self.schemaXSD.validate(self.documentXML)
        
        #Sortir
        return valide

    #-------------------------------------------------------------------------------------
    def obtenirDepot(self):
    #-------------------------------------------------------------------------------------
        """
        Permet d'obtenir le dépôt de la zone de travail (ZtId).
        
        Paramètres:
        -----------
        Aucun
        
        Retour:
        -------
        depot        Dépôt de la zone de travail.
        
        """

        #Sortir
        return self.obtenirNoeudTexte(NODE_REPOSITORY)

    #-------------------------------------------------------------------------------------
    def definirDepot(self, depot):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir le dépôt de la zone de travail (ZtId).
        
        Paramètres:
        -----------
        depot        Dépôt de la zone de travail.
        
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
        
        Paramètres:
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
        Permet de définir l'identifiant de la zone de travail (ZtId).
        
        Paramètres:
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
        Permet d'obtenir la partition (Type de produit) reliée à l'identifiant de la zone de travail.
        
        Paramètres:
        -----------
        Aucun
        
        Retour:
        -------
        partition        Partition reliée à l'identifiant de la zone de travail.
        
        """
        
        #Sortir
        return self.obtenirNoeudTexte(NODE_PARTITION)

    #-------------------------------------------------------------------------------------
    def definirPartition(self, partition):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir la partition (Type de produit) reliée à l'identifiant de la zone de travail.
        
        Paramètres:
        -----------
        partition        Partition reliée à l'identifiant de la zone de travail.
        
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
        Permet d'obtenir la date de création de la zone de travail.
        
        Paramètres:
        -----------
        Aucun
        
        Retour:
        -------
        dateCreation        Date de création de la zone de travail.
        
        """
        
        #Sortir
        return self.obtenirNoeudTexte(NODE_CREATION_DATE)

    #-------------------------------------------------------------------------------------
    def definirDateCreation(self, dateCreation):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir la date de création de la zone de travail.
        
        Paramètres:
        -----------
        dateCreation        Date de création de la zone de travail.
        
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
        Permet d'obtenir la date prévue de livraison reliée à l'identifiant de la zone de travail.
        
        Paramètres:
        -----------
        Aucun
        
        Retour:
        -------
        datePrevue        Date prévue de livraison de la zone de travail.
        
        """
        
        #Sortir
        return self.obtenirNoeudTexte(NODE_EXPECTED_DATE)

    #-------------------------------------------------------------------------------------
    def definirDatePrevue(self, datePrevue):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir la date prévue de livraison reliée à l'identifiant de la zone de travail.
        
        Paramètres:
        -----------
        datePrevue        Date prévue de livraison de la zone de travail.
        
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
        Permet d'obtenir le nom du catalogue reliée à l'identifiant de la zone de travail.
        Le nom du catalogue contient le numéro du catalogue et de la norme.
        Le nom du catalogue est contenu sous un attribut dans un node.
        
        Paramètres:
        -----------
        Aucun
        
        Retour:
        -------
        catalogue        Nom du catalogue de la zone de travail.
        
        """
        
        #Le nom du catalogue est vide par défaut
        catalogue = ''
        
        #Extraire le node FEATURE_LIST
        listNodeFeatureList = self.documentXML.getElementsByTagName(NODE_FEATURE_LIST)
        
        #Vérifier la présence du node FEATURE_LIST
        if len(listNodeFeatureList) > 0:
            #Définir le node FEATURE_LIST
            nodeFeatureList = listNodeFeatureList[0]
            
            #Vérifier si l'attribut du catalogue est présent
            if nodeFeatureList.hasAttribute(ATTR_FEATURE_CATALOGUE_ID):
                #Définir le nom du catalogue
                catalogue = str(nodeFeatureList.getAttribute(ATTR_FEATURE_CATALOGUE_ID))
        
        #Sortir
        return catalogue

    #-------------------------------------------------------------------------------------
    def definirCatalogue(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir le nom du catalogue reliée à l'identifiant de la zone de travail.
        Le nom du catalogue contient le numéro du catalogue et de la norme.
        Le nom du catalogue est contenu sous un attribut dans un node.
        
        Paramètres:
        -----------
        catalogue        Nom du catalogue de la zone de travail.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Extraire le node FEATURE_LIST
        listNodeFeatureList = self.documentXML.getElementsByTagName(NODE_FEATURE_LIST)
        
        #Vérifier la présence du node FEATURE_LIST
        if len(listNodeFeatureList) > 0:
            #Définir le node FEATURE_LIST
            nodeFeatureList = listNodeFeatureList[0]
            
            #Vérifier si l'attribut du catalogue est présent
            if nodeFeatureList.hasAttribute(ATTR_FEATURE_CATALOGUE_ID):
                #Véfinir le nom du catalogue
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
        
        Paramètres:
        -----------
        Aucun
        
        Retour:
        -------
        polygonWKT      Coordonnées du polygone sous forme de Well Known Text.
        
        """

        #Sortir
        return self.obtenirNoeudTexte(NODE_POLYGON)

    #-------------------------------------------------------------------------------------
    def definirPolygone(self, polygonWKT):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir le polygone sous forme de Well Known Text.
        
        Paramètres:
        -----------
        polygonWKT      Coordonnées du polygone sous forme de Well Known Text.
        
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
        Permet d'obtenir la liste des noms d'éléments
        (ex: BDG_CHEMIN_FER_1,BDG_COURBE_NIVEAU_1,BDG_LIGNE_TRANSPORT_ENERGIE_1).
        
        Paramètres:
        -----------
        Aucun
        
        Retour:
        -------
        listeNomElement        Liste des noms d'éléments séparés par une virgule.
        
        """

        #Initialiser la liste liste des noms d'élémente.
        listeNomElement = ''
        
        #Extraire le node FEATURE_NAME
        listNodeFeatureName = self.documentXML.getElementsByTagName(NODE_FEATURE_NAME)
        
        #Vérifier la présence du node FEATURE_NAME
        for featureName in listNodeFeatureName:
            #Définir la liste des noms d'éléments
            listeNomElement = listeNomElement + str(featureName.childNodes[0].data) + ','
            
        #Vérifier la présence de noms d'éléments
        if len(listeNomElement) > 0:
            #Enlever le dernier ','
            listeNomElement = listeNomElement[:-1]
        
        #Sortir
        return listeNomElement

    #-------------------------------------------------------------------------------------
    def definirListeNomElement(self, listeNomElement):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir la liste des noms d'éléments.
        (ex: BDG_CHEMIN_FER_1,BDG_COURBE_NIVEAU_1,BDG_LIGNE_TRANSPORT_ENERGIE_1).

        Paramètres:
        -----------
        listeNomElement        Liste des noms d'éléments séparé par une virgule.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Extraire le node FEATURE_LIST
        listNodeFeatureList = self.documentXML.getElementsByTagName(NODE_FEATURE_LIST)
        
        #Vérifier la présence du node FEATURE_LIST
        if len(listNodeFeatureList) > 0:
            #Définir le node FEATURE_LIST
            nodeFeatureList = listNodeFeatureList[0]

            #Détruire tous les nodes
            while len(nodeFeatureList.childNodes) > 0:
                #Détruire le dernier node
                nodeFeatureList.removeChild(nodeFeatureList.childNodes[len(nodeFeatureList.childNodes)-1])
                
            #Traiter tous les noms d'éléments présents dans la liste de noms
            for nomElement in listeNomElement.split(','):
                #Créer le node TEXT contenant l'indentation
                nodeIndent = self.documentXML.createTextNode("\n        ")
                #Ajouter le node nodeIndent dans le node FEATURE_LIST
                nodeFeatureList.appendChild(nodeIndent)
                
                #Créer le node TEXT contenant le nom de l'élément
                nodeText = self.documentXML.createTextNode(nomElement)
                #Créer le node FEATURE_NAME
                nodeFeatureName = self.documentXML.createElement(NODE_FEATURE_NAME)
                #Ajouter le nom de l'élément dans le node FEATURE_NAME
                nodeFeatureName.appendChild(nodeText)
                #Ajouter le node FEATURE_NAME dans le node FEATURE_LIST
                nodeFeatureList.appendChild(nodeFeatureName)
                
            #Créer le node TEXT contenant l'indentation
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
        
        Paramètres:
        -----------
        nomNoeud        Nom du noeud traité.
        
        Retour:
        -------
        valeurNoeud     Valeur texte du noeud traité.
        
        """
        
        #La valeur du noeud est vide par défaut
        valeurNoeud = ''
        
        #Extraire la liste des noeuds à traiter
        listNoeudTraiter = self.documentXML.getElementsByTagName(nomNoeud)
        
        #Vérifier la présence du noeud
        if len(listNoeudTraiter) > 0:
            #Définir le noeud traité
            noeudTraiter = listNoeudTraiter[0]
            
            #Vérifier si le noeud a des enfants
            if noeudTraiter.hasChildNodes(): 
                #Extraire la valeur du noeud
                valeurNoeud = str(noeudTraiter.childNodes[0].data)
        
        #Sortir
        return valeurNoeud

    #-------------------------------------------------------------------------------------
    def definirNoeudTexte(self, nomNoeud, valeurNoeud):
    #-------------------------------------------------------------------------------------
        """
        Permet de définir la valeur d'un noeud de type texte.
        
        Paramètres:
        -----------
        nomNoeud        Nom du noeud traité.
        valeurNoeud     Valeur texte du noeud traité.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Extraire les noeuds à traiter
        listNoeudTraiter = self.documentXML.getElementsByTagName(nomNoeud)
        
        #Vérifier la présence d'un noeud
        if len(listNoeudTraiter) > 0:
            #Définir le noeud traité
            noeudTraiter = listNoeudTraiter[0]
            
            #Vérifier si le noeud a des enfants
            if noeudTraiter.hasChildNodes(): 
                #Définir la valeur du noeud
                noeudTraiter.childNodes[0].data = valeurNoeud
            #Si le node n'a pas d'enfant
            else:
                #Créer un TEXT NODE
                noeudText = self.documentXML.createTextNode(valeurNoeud)
                #Ajouter le TEXT NODE
                noeudTraiter.appendChild(noeudText)
                
        #Si le noeud est absent
        else:
            #Erreur, le node traité est absent du fichier XML
            raise Exception('Le noeud %s est absent du fichier XML' %nomNoeud)
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par défaut
        gabaritXml          = ""
        fichierXml          = ""
        listeNomElement     = ""
        
        #Instanciation de la classe XmlCreerZT
        oXmlCreerZT = XmlCreerZT(gabaritXml)
        
        #Remplacer la liste des noms d'éléments dans le fichier XML
        oXmlCreerZT.definirListeNomElement(listeNomElement)
        
    except Exception, err:
        #Sortir avec une erreur
        sys.exit(1)

    #Sortir sans erreur
    sys.exit(0)