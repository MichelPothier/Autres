#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerXmlMetadonneesFGDC.py
# Auteur    : Michel Pothier
# Date      : 14 d�cembre 2017

"""
    Application qui permet de cr�er le fichier XML des m�tadonn�es FGDC d'un identifiant de produit dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                                d�faut = SIB_PRO
    typeProduit         OB      Type de produit de l'identifiant.
                                d�faut = "BDG"
    identifiant         OB      Identifiant avec ou sans �dition.version courante du produit � traiter.
                                d�faut = ""
    nomXsd              OB      Nom du fichier XSD pour valider le fichier XML.
                                d�faut = "/cits/Envcits/xml\pro\sib\XSD_FGDC_CITS/cits-fgdc-std-001-1998-ann.xsd"
    nomXml              OB      Nom du fichier XML des m�tadonn�es FGDC d'un identifiant.
                                d�faut = "/cits/travail/Gestion_BDSpatiales/transactionsBdg/pro/livraison/METADONNEES_FGDC.xml"
  
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerXmlMetadonneesFGDC(object):
#*******************************************************************************************
    """
    Permet de cr�er le fichier XML des m�tadonn�es FGDC d'un identifiant de produit dans SIB.   
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement la cr�ation du fichier XML de m�tadonn�es FGDC.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        # D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, typeProduit, identifiant, nomXsd, nomXml):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit d'un identifiant.
        identifiant         : Identifiant avec ou sans �dition.version courante du produit � traiter.
        nomXsd              : Nom du fichier XSD pour valider le fichier XML.
        nomXml              : Nom du fichier XML des m�tadonn�es FGDC d'un identifiant.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """
        
        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'typeProduit')
        
        if (len(identifiant) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'identifiant')
        
        if (len(nomXsd) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'nomXsd')
        
        if (len(nomXml) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'nomXml')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, identifiant, nomXsd, nomXml):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation du fichier XML des m�tadonn�es FGDC d'un identifiant de produit dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        typeProduit     : Type de produit d'un identifiant.
        identifiant     : Identifiant avec ou sans �dition.version courante du produit � traiter.
        nomXsd          : Nom du fichier XSD pour valider le fichier XML.
        nomXml          : Nom du fichier XML des m�tadonn�es FGDC d'un identifiant.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur g�n�r�s par le service de transaction SIB.
        messageSib      : Description du message re�ue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucune
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")  
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS','PLAN'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')"
        resultat = oSib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        #Valider le num�ro d'�dition et version de l'identifiant courant
        arcpy.AddMessage("- Valider le num�ro courant d'�dition et version de l'identifiant '" + identifiant + "' du produit '" + typeProduit + "'")
        #Extraire l'identifiant
        id = identifiant.split(" ")[0]
        #Ex�cuter la requ�te dans SIB
        sql = "SELECT ED, VER FROM F235_PR WHERE TY_PRODUIT='" + typeProduit + "' AND IDENTIFIANT='" + id + "' AND JEU_COUR=1"
        resultat = oSib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            arcpy.AddMessage(sql)
            raise Exception("L'identifiant '" + id + "' du produit '" + typeProduit + "' de SIB est invalide ou ne poss�de pas de jeu courant!")

        #D�finir le num�ro d'�dition et version du jeu de donn�es courant
        ed = resultat[0][0]
        ver = resultat[0][1]
        
        #Ex�cution du programme pour cr�er le fichier XML des m�tadonn�es FGDC dans SIB.
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Cr�er le fichier XML des m�tadonn�es FGDC")
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env              = "SIB_PRO"
        typeProduit      = "BDG"
        identifiant      = ""
        nomXsd           = "/cits/Envcits/xml\pro\sib\XSD_FGDC_CITS/cits-fgdc-std-001-1998-ann.xsd"
        nomXml           = "/cits/travail/Gestion_BDSpatiales/transactionsBdg/pro/livraison/METADONNEES_FGDC.xml"
        
        #extraction des param�tres d'ex�cution
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
        
        # D�finir l'objet de cr�ation du fichier XML des m�tadonn�es FGDC.
        oCreerXmlMetadonneesFGDC = CreerXmlMetadonneesFGDC()
        
        #Valider les param�tres obligatoires
        oCreerXmlMetadonneesFGDC.validerParamObligatoire(env, typeProduit, identifiant, nomXsd, nomXml)
        
        # Ex�cuter le traitement cr�ation du fichier XML des m�tadonn�es FGDC.
        oCreerXmlMetadonneesFGDC.executer(env, typeProduit, identifiant, nomXsd, nomXml)
    
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