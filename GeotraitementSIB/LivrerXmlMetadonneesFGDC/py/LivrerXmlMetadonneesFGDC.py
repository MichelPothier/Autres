#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : LivrerXmlMetadonneesFGDC.py
# Auteur    : Michel Pothier
# Date      : 19 octobre 2017

"""
    Application qui permet de livrer les m�tadonn�es FGDC d'un identifiant de produit dans SIB � partir d'un fichier XML.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                                d�faut = SIB_PRO
    typeProduit         OB      Type de produit de l'identifiant.
                                d�faut = "BDG"
    identifiant         OB      Identifiant du produit � traiter.
                                d�faut = ""
    noMap               OB      Num�ro de mise au programme de l'identifiant du produit.
                                d�faut = ""
    fichierXml          OB      Nom complet du fichier XML contenant les m�tadonn�es FGDC compl�tes.
                                ATTENTION : Le nom du fichier est transform� pour �tre utilis� sous Linux.
                                (\\dfscitsh est enlev� et "\" est remplac� par "/")
                                d�faut = "\\dfscitsh\cits\Travail\Gestion_BDSpatiales\transactionsBdg\pro\livraison\id_meta_fgdc.xml"
    fichierXsd          OB      Nom complet du fichier Xsd pour valider les m�tadonn�es FGDC.
                                d�faut = "\\dfscitsh\cits\EnvCits\applications\gestion_bdg\tst\Gestion_BDSpatiales\xsd\fusion.xsd"
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        LivrerXmlMetadonneesFGDC.py env typeProduit identifiant noMap fichierXml fichierXsd

    Exemple:
        LivrerXmlMetadonneesFGDC.py SIB_PRO BDG 021M07 981244
           \\dfscitsh\cits\Travail\Gestion_BDSpatiales\transactionsBdg\pro\livraison\001M09_meta_fgdc.xml
           \\dfscitsh\cits\EnvCits\applications\gestion_bdg\tst\Gestion_BDSpatiales\xsd\fusion.xsd

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: LivrerXmlMetadonneesFGDC.py 2152 2017-12-19 19:55:06Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class LivrerXmlMetadonneesFGDC(object):
#*******************************************************************************************
    """
    Permet de livrer les m�tadonn�es FGDC d'un identifiant de produit dans SIB � partir d'un fichier XML.   
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de destruction de m�tadonn�es FGDC.
        
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
    def validerParamObligatoire(self, env, typeProduit, identifiant, noMap, fichierXml, FichierXsd):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit d'un identifiant.
        identifiant         : Identifiant du produit � traiter.
        noMap               : Num�ro de mise au programme de l'identifiant du produit.
        fichierXml          : Nom complet du fichier XML contenant les m�tadonn�es FGDC compl�tes.
        fichierXsd          : Nom complet du fichier Xsd pour valider les m�tadonn�es FGDC.
        
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
        
        if (len(noMap) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'noMap')
        
        if (len(fichierXml) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'fichierXml')
        
        if (len(fichierXsd) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'fichierXsd')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, identifiant, noMap, fichierXml, FichierXsd):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de destruction des m�tadonn�es FGDC d'un identifiant de produit dans SIB.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit d'un identifiant.
        identifiant         : Identifiant du produit � traiter.
        noMap               : Num�ro de mise au programme de l'identifiant du produit.
        fichierXml          : Nom complet du fichier XML contenant les m�tadonn�es FGDC compl�tes.
        fichierXsd          : Nom complet du fichier Xsd pour valider les m�tadonn�es FGDC.
        
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
        
        #Valider le num�ro de mise au programme
        arcpy.AddMessage("- Valider le num�ro de mise au programme '" + noMap + "' de l'identifiant '" + identifiant + "' du produit '" + typeProduit + "'")
        #Extraire l'identifiant
        id = identifiant.split(" ")[0]
        #Ex�cuter la requ�te dans SIB
        sql = "SELECT NO_MAP FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND IDENTIFIANT='" + identifiant + "' AND NO_MAP=" + noMap + " AND E_PLSNRC='P'"
        resultat = oSib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            arcpy.AddMessage(sql)
            raise Exception("L'identifiant '" + id + "' du produit '" + typeProduit + "' de SIB est invalide, n'est pas en production ou n'est pas au programme : no_map=" + noMap + "!")
        
        #Appel du service de transaction SIB qui effectue la mise en place FGDC dans SIB.
        fichierXml = fichierXml.replace("\\dfscitsh","").replace("\\","/")
        fichierXsd = fichierXsd.replace("\\dfscitsh","").replace("\\","/")
        arcpy.AddMessage("- Appel du service SIB : P0201_XML.pu_mettre_en_place_fgdc_fich (" + sUsagerSib + ", " + fichierXml + ", " + FichierXsd + ", " + noMap + ")")
        codeRetour = oSib.cursor.callfunc("P0201_XML.pu_mettre_en_place_fgdc_fich", cx_Oracle.STRING, [sUsagerSib, fichierXml, FichierXsd, noMap])
        
        #V�rifier le succ�s du service SIB 
        if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
            #Afficher le message de succ�s du traitraitement
            arcpy.AddMessage("- Succ�s d'ex�cution du service SIB : P0201_XML.pu_mettre_en_place_fgdc_fich")
        
        #l'initialisation de l'ajout d'un lot n'a pas r�ussi
        else:
            #Extraire le nombre de message
            nbMessSib = oSib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
            count = 1
            #Extraire tous les messages
            message = []
            while nbMessSib >= count:
                messageSib = oSib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                message.append(messageSib)
                count += 1
            raise Exception(message)
        
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
        noMap            = ""
        fichierXml       = ""
        fichierXsd       = ""
        
        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            identifiant = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            noMap = sys.argv[4]
        
        if len(sys.argv) > 5:
            fichierXml = sys.argv[5]
        
        if len(sys.argv) > 6:
            fichierXsd = sys.argv[6]
        
        #D�finir l'objet de livraison des m�tadonn�es FGDC.
        oLivrerXmlMetadonneesFGDC = LivrerXmlMetadonneesFGDC()
        
        #Valider les param�tres obligatoires
        oLivrerXmlMetadonneesFGDC.validerParamObligatoire(env, typeProduit, identifiant, noMap, fichierXml, FichierXsd)
        
        #Ex�cuter le traitement de livraison des m�tadonn�es FGDC.
        oLivrerXmlMetadonneesFGDC.executer(env, typeProduit, identifiant, noMap, fichierXml, FichierXsd)
    
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