#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : CreerCartesPdfStatistiquesErreurs.py
# Auteur    : Michel Pothier
# Date      : 18 Janvier 2018

"""
Outil qui permet de créer un fichier PDF contenant les cartes des statistiques d'erreurs par classe et contrainte.

Paramètres d'entrées:
----------------------
env         OB  Type d'environnement [BDRS_PRO/BDRS_TST/BDRS_DEV].
                défaut = BDRS_PRO
mxd         OB  Nom d'un fichier de projet ArcMap.
                défaut : S:\applications\gestion_bdg\pro\Gestion_BDSpatiales\mxd\StatistiqueErreursDecoupage50k.mxd
classes     OB  Liste des classes présentent dans la table des statistiques d'erreurs.
                La table des statistiques d'erreurs est inclut dans le fichier .mxd sous le nom TBL_STATISTIQUE_ELEMENT_ERREUR.
                défaut : 
contraintes OB  Liste des contraintes présentent dans la table des statistiques d'erreurs.
                La table des statistiques d'erreurs est inclut dans le fichier .mxd sous le nom TBL_STATISTIQUE_ELEMENT_ERREUR.
                défaut :

Paramètres de sortie:
---------------------
pdf         OB  Nom du fichier PDF contenant les cartes des statistiques d'erreurs.
                défaut : S:\Erreurs\StatistiquesErreurs.pdf

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    CreerCartesPdfStatistiquesErreurs.py env mxd classes contraintes pdf

Exemple:
    CreerCartesPdfStatistiquesErreurs.py BDG_PRO S:\applications\gestion_bdg\pro\Gestion_BDSpatiales\mxd\StatistiqueErreursDecoupage50k.mxd NHN_HHYD_WATERBODY_2 AjustementDecoupage_DATASET_NAME S:\Erreurs\StatistiquesErreurs.pdf

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerCartesPdfStatistiquesErreurs.py 1163 2018-03-05 16:58:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteBDG

#*******************************************************************************************
class CreerCartesPdfStatistiquesErreurs(object):
#*******************************************************************************************
    """
    Application qui permet de créer un fichier PDF contenant les cartes des statistiques d'erreurs par classe et contrainte.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer un fichier PDF contenant les cartes des statistiques d'erreurs par classe et contrainte.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion à BDG.
        
        """
        
        #Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Définir la date de début
        self.dateDebut = datetime.datetime.now().replace(microsecond=0)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, mxd, classes, contraintes, pdf):
    #-------------------------------------------------------------------------------------
        """
        Valider les paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        mxd         : Nom d'un fichier de projet ArcMap.
        classes     : Liste des classes présentent dans la table des statistiques d'erreurs.
        contraintes : Liste des contraintes présentent dans la table des statistiques d'erreurs.
        pdf         : Nom du fichier PDF contenant les cartes des statistiques d'erreurs.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(mxd) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'mxd')
        
        if (len(classes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'classes')
        
        if (len(contraintes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'contraintes')
        
        if (len(pdf) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'pdf')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, mxd, classes, contraintes, pdf):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour créer un fichier PDF contenant les cartes des statistiques d'erreurs par classe et contrainte.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        mxd         : Nom d'un fichier de projet ArcMap.
        classes     : Liste des classes présentent dans la table des statistiques d'erreurs.
        contraintes : Liste des contraintes présentent dans la table des statistiques d'erreurs.
        pdf         : Nom du fichier PDF contenant les cartes des statistiques d'erreurs.
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion à BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        resultat        : Résultat de la requête BDG.
        """
        
        #Connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Extraire l'usager de la BD
        sUsagerBd = self.CompteBDG.UsagerBd()
        
        #Définir le projet ArcMap
        prj = arcpy.mapping.MapDocument(mxd)
        
        #Définir le FeatureLayer de découpage
        lyr = arcpy.mapping.ListLayers(prj,"*GES_DECOUPAGE_SNRC50K_2*")[0]
        
        #Définir la table des statistiques
        tbl = arcpy.mapping.ListTableViews(prj,"*TBL_STATISTIQUE_ELEMENT_ERREUR*")[0]
        
        #Extraire tous les TextElement
        textElement = arcpy.mapping.ListLayoutElements(prj,"TEXT_ELEMENT")
        #Traiter tous les TextElement
        for te in textElement:
            #Vérifier si c'est le titre de la carte
            if te.name == "CLASSE":
                #Extraitre le titre de la carte
                titre = te
            #Vérifier si c'est le sous-titre de la carte
            if te.name == "CONTRAINTE":
                #Extraitre le sous-titre de la carte
                soustitre = te
        
        #Extraire la légende dans le projet
        legende = arcpy.mapping.ListLayoutElements(prj,"LEGEND_ELEMENT")[0]
        
        #Définir la date et le temps
        dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        
        #Définir le nom du fichier PDF
        pdf = pdf.replace("[DATE_TIME]",dt)
        #Créer le fichier PDF contenant les cartes des statistiques d'erreurs pour toutes les classes et toutes les contraintes.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer le fichier PDF vide des cartes des statistiques d'erreurs : " + pdf + " ...")
        PDFdoc = arcpy.mapping.PDFDocumentCreate(pdf)
        
        #Traiter toutes les classes
        for classe in classes.split(','):
            #Traiter toutes les contraintes
            for contrainte in contraintes.split(','):
                #Afficher le message
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Traitement de la classe : " + classe + " et de la contraite : " + contrainte + " ...")
                
                #Modifier le titre et le sous-titre de la carte
                #legende.title = contrainte
                titre.text = classe
                soustitre.text = contrainte
                
                #Modifier la requête attributive dans la table des statistiques d'erreurs
                tbl.definitionQuery = u"CONTRAINTE = '" + contrainte + "' AND NOM_TABLE = '" + classe + "'"
                
                #Modifier la requête attributive dans le FeatureLayer
                #lyr.name = classe
                #lyr.definitionQuery = u"NB_ERREUR > 0 AND CONTRAINTE = '" + contrainte + "' AND NOM_TABLE = '" + classe + "'"
                lyr.definitionQuery = u"CONTRAINTE = '" + contrainte + "' AND NOM_TABLE = '" + classe + "'"
                
                #Reclassifier la symbologie du FeatureLayer
                arcpy.AddMessage("  Reclassification de la symbologie : (" + str(lyr.symbology.numClasses) + ") ...")
                #lyr.symbology.numClasses = 5
                lyr.symbology.reclassify()
                
                #Rafraichir le projet ArcMap
                #arcpy.RefreshTOC()
                #arcpy.RefreshActiveView()
                
                #Définir le fichier PDF temporaire
                tmp = os.path.dirname(pdf) + "\\" + dt + "_" + classe + "_" + contrainte + ".pdf"
                #Exporter la carte dans un fichier PDF temporaire
                arcpy.AddMessage("  Créer le fichier PDF temporaire : " + tmp + " ...")
                arcpy.mapping.ExportToPDF(prj, tmp)
                #Ajouter le fichier PDF temporaire dans le final
                arcpy.AddMessage("  Ajouter le fichier PDF temporaire ...")
                PDFdoc.appendPages(tmp)
        
        #Sauver le fichier PDF final
        arcpy.AddMessage("  Sauver le fichier PDF final ...")
        PDFdoc.saveAndClose()

        #Fermeture de la connexion de la BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir du traitement
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "BDRS_PRO"
        mxd = "S:\applications\gestion_bdg\pro\Gestion_BDSpatiales\mxd\StatistiqueErreursDecoupage50k.mxd"
        classes = ""
        contraintes = ""
        pdf = "S:\Erreurs\StatistiquesErreurs_[DATE_TIME].pdf"
        
        # Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            mxd = sys.argv[2]
        
        if len(sys.argv) > 3:
            if sys.argv[3] <> '#':
                classes = sys.argv[3].replace(";",",")
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> '#':
                contraintes = sys.argv[4].replace(";",",")
        
        if len(sys.argv) > 5:
            pdf = sys.argv[5]
        
        #Définir l'objet pour créer un fichier PDF contenant les cartes des statistiques d'erreurs par classe et contrainte.
        oCreerCartesPdfStatistiquesErreurs = CreerCartesPdfStatistiquesErreurs()
        
        #Valider les paramètres obligatoires
        oCreerCartesPdfStatistiquesErreurs.validerParamObligatoire(env, mxd, classes, contraintes, pdf)
        
        #Exécuter le traitement pour créer un fichier PDF contenant les cartes des statistiques d'erreurs par classe et contrainte.
        oCreerCartesPdfStatistiquesErreurs.executer(env, mxd, classes, contraintes, pdf)
        
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