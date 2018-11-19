#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerXmlMetadonneesFGDC.py
# Auteur    : Michel Pothier
# Date      : 14 décembre 2017

"""
    Application qui permet de créer le fichier XML des métadonnées FGDC d'un identifiant de produit dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                                défaut = SIB_PRO
    typeProduit         OB      Type de produit de l'identifiant.
                                défaut = "BDG"
    identifiant         OB      Identifiant avec ou sans édition.version courante du produit à traiter.
                                défaut = ""
    nomXsd              OB      Nom du fichier XSD pour valider le fichier XML.
                                défaut = "/cits/Envcits/xml\pro\sib\XSD_FGDC_CITS/cits-fgdc-std-001-1998-ann.xsd"
    nomXml              OB      Nom du fichier XML des métadonnées FGDC d'un identifiant.
                                défaut = "/cits/travail/Gestion_BDSpatiales/transactionsBdg/pro/livraison/METADONNEES_FGDC.xml"
  
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerXmlMetadonneesFGDC.py env typeProduit identifiant nomXsd nomXml

    Exemple:
        CreerXmlMetadonneesFGDC.py SIB_PRO BDG 021M07 12.0
        CreerXmlMetadonneesFGDC.py SIB_PRO BDG 021M07 12.0 "/cits/Envcits/xml\pro\sib\XSD_FGDC_CITS/cits-fgdc-std-001-1998-ann.xsd" "/cits/travail/Gestion_BDSpatiales/transactionsBdg/pro/livraison/METADONNEES_FGDC.xml"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerXmlMetadonneesFGDC.py 2151 2017-12-19 19:53:54Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, subprocess, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerXmlMetadonneesFGDC(object):
#*******************************************************************************************
    """
    Permet de créer le fichier XML des métadonnées FGDC d'un identifiant de produit dans SIB.   
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement la création du fichier XML de métadonnées FGDC.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        # Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, typeProduit, identifiant, nomXsd, nomXml):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit d'un identifiant.
        identifiant         : Identifiant avec ou sans édition.version courante du produit à traiter.
        nomXsd              : Nom du fichier XSD pour valider le fichier XML.
        nomXml              : Nom du fichier XML des métadonnées FGDC d'un identifiant.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """
        
        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'typeProduit')
        
        if (len(identifiant) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'identifiant')
        
        if (len(nomXsd) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'nomXsd')
        
        if (len(nomXml) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'nomXml')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, identifiant, nomXsd, nomXml):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création du fichier XML des métadonnées FGDC d'un identifiant de produit dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        typeProduit     : Type de produit d'un identifiant.
        identifiant     : Identifiant avec ou sans édition.version courante du produit à traiter.
        nomXsd          : Nom du fichier XSD pour valider le fichier XML.
        nomXml          : Nom du fichier XML des métadonnées FGDC d'un identifiant.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur générés par le service de transaction SIB.
        messageSib      : Description du message reçue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucune
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")  
        
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS','PLAN'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')"
        resultat = oSib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")
        
        #Valider le numéro d'édition et version de l'identifiant courant
        arcpy.AddMessage("- Valider le numéro courant d'édition et version de l'identifiant '" + identifiant + "' du produit '" + typeProduit + "'")
        #Extraire l'identifiant
        id = identifiant.split(" ")[0]
        #Exécuter la requête dans SIB
        sql = "SELECT ED, VER FROM F235_PR WHERE TY_PRODUIT='" + typeProduit + "' AND IDENTIFIANT='" + id + "' AND JEU_COUR=1"
        resultat = oSib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            arcpy.AddMessage(sql)
            raise Exception("L'identifiant '" + id + "' du produit '" + typeProduit + "' de SIB est invalide ou ne possède pas de jeu courant!")

        #Définir le numéro d'édition et version du jeu de données courant
        ed = resultat[0][0]
        ver = resultat[0][1]
        
        #Exécution du programme pour créer le fichier XML des métadonnées FGDC dans SIB.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer le fichier XML des métadonnées FGDC")
        cmd = "java -jar  S:\java\pro\cits\sib\JSib121c\GenererXmlFgdc_SIB_PRO.jar " + typeProduit + " " + id + " " + str(ed) + " " + str(ver) + " " + nomXml + " " + nomXsd + " 1 FR"
        arcpy.AddMessage(cmd)   
        message = subprocess.check_output(cmd, shell=True)
        arcpy.AddMessage(message)
        
        #Fermeture de la connexion de la BD SIB  
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env              = "SIB_PRO"
        typeProduit      = "BDG"
        identifiant      = ""
        nomXsd           = "/cits/Envcits/xml\pro\sib\XSD_FGDC_CITS/cits-fgdc-std-001-1998-ann.xsd"
        nomXml           = "/cits/travail/Gestion_BDSpatiales/transactionsBdg/pro/livraison/METADONNEES_FGDC.xml"
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            identifiant = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            nomXsd = sys.argv[4]
        
        if len(sys.argv) > 5:
            nomXml = sys.argv[5]
        
        # Définir l'objet de création du fichier XML des métadonnées FGDC.
        oCreerXmlMetadonneesFGDC = CreerXmlMetadonneesFGDC()
        
        #Valider les paramètres obligatoires
        oCreerXmlMetadonneesFGDC.validerParamObligatoire(env, typeProduit, identifiant, nomXsd, nomXml)
        
        # Exécuter le traitement création du fichier XML des métadonnées FGDC.
        oCreerXmlMetadonneesFGDC.executer(env, typeProduit, identifiant, nomXsd, nomXml)
    
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