#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet la validation de toutes les connexions BDG contenu dans le
   fichier de configuration.
   
   L'outil contient la classe utilitaire qui permet la gestion des BDs et des comptes BDG.
    
    Les différentes fonctionnalités de la classe utilitaire sont les suivantes:
    -OuvrirConnexionBDG
    -FermerConnexionBDG
    -ConnecterCompteBDG
    -ValiderConnexionCompteBDG
    -CreerCompteBDG
    -ModifierCompteBDG
    -DetruireCompteBDG

   Le fichier de configuration est créé dans le répertoire de l'usager qui est protégé
   en lecture et en écriture. Le nom du fichier est construit à partir de la variable
   d'environnement 'LOCALAPPDATA' qui contient le nom du répertoire de l'usager concaténé
   au nom de fichier "\BDG.ini".

   Le fichier de config contient 3 sections dans lesquels on retrouve 2 paramètres avec leurs valeurs.
   
   Les 3 sections sont les suivantes:
    BDRS_PRO: Base de données officielle des données géographique.
    BDRS_TST: Base de données utilisée seulement par l'équipe de support BDG pour effectuer ses tests.
    BDRS_DEV: Base de données utilisée seulement par les équipes de développement pour effectuer leurs tests.

   Les 2 paramètres sont les suivants:
    UsagerBd: Nom de l'usager de la base de données pour lequel on désire se connecter.
    MotPasseBd: Mot de passe de l'usager de la base de données pour lequel on désire se connecter.

   Exemple du fichier de config:   
    [BDRS_PRO]
    UsagerBd: modview
    MotPasseBd: decyukon

    [BDRS_TST]
    UsagerBd: modview
    MotPasseBd: modview

    [BDRS_DEV]
    UsagerBd: nsprod
    MotPasseBd: dev
    
   NB: Certaines sections peuvent être absentes ou d'autres présentes.
    
Nom: CompteBDG.py

Auteur: Michel Pothier         Date: 14 octobre 2014

Paramètres:
-----------
Aucun

Classe:
-------
 Nom                    Description
 ---------------------  --------------------------------------------------------------------
 CompteBDG              Permet la gestion des comptes BDG.
 
Retour:
-------
 ErrorLevel  Integer  Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CompteBDG.py 1082 2015-08-26 14:00:22Z mpothier $"
#********************************************************************************************

# Identification des librairies utilisees 
import os, sys, arcpy, datetime, util_bd, ConfigParser, cx_Oracle

#*******************************************************************************************
class ExceptionConnexionBDG(Exception):
#*******************************************************************************************
    """
    Classe d'exception dérivée de la classe Exception pour gèrer l'arrêt du
    programme lorsque il y a un problème dans l'exécution d'un service de
    compte BDG
    
    Lors de l'instanciation, passez une chaîne de caractère en argument
    pour d'écrire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CompteBDG(object):
#*******************************************************************************************
    """
    Permet la gestion des BDs et des comptes BDG.
    
    Les différentes fonctionnalités sont les suivantes:
    -OuvrirConnexionBDG
    -FermerConnexionBDG
    -ConnecterCompteBDG
    -ValiderConnexionCompteBDG
    -CreerCompteBDG
    -ModifierCompteBDG
    -DetruireCompteBDG
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de gestion des comptes BDG.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.NomFichierConfig   : Nom du fichier de configuration.
        self.FichierStats       : Nom du fichier des statistiques d'utilisation.
        self.FichierConfig      : Objet contenant le fichier de configuration.
        self.Config             : Objet utilitaire pour traiter le fichier de configuration.        
        
        """
        
        #Définir les variable par défaut
        self.NomFichierConf = os.environ['LOCALAPPDATA'] + "\BDG.ini"
        
        #Message de lecture du fichier de configuration
        arcpy.AddMessage("- Lecture du fichier de configuration : " + self.NomFichierConf)
        #Instanciation du fichier de configuration
        self.Config = ConfigParser.ConfigParser()
        #Lecture du fichier de configuration
        self.FichierConfig = self.Config.read(self.NomFichierConf)
        #Afficher les sections du fichier de config
        arcpy.AddMessage(self.Config.sections())
        
        #Définir le nom du fichier des statistiques d'utilisations
        self.FichierStats = "S:\\Developpement\\geo\\" + os.getenv("username") + ".txt"
        
        #initialiser le nom de l'usager de la BD
        self.nomUsagerBd = ""
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def OuvrirConnexionBDG(self, sEnv, sEnvStat=""):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement d'ouverture d'une connexion BDG à partir d'un environnement
        et du contenu du fichier de configuration.
        
        Paramètres:
        -----------
        sEnv         : Type d'environnement correspondant à une base de données.
        sEnvStat     : Type d'environnement correspondant à une base de données à écrire dans les statistiques.
               
        Variables:
        ----------
        sUsagerBd       : Nom de l'usager de la BD.
        sMotPasseBd     : Mot de passe de l'usager de la BD.
        self.Config     : Objet utilitaire pour traiter le fichier de configuration.        
               
        Retour:
        ----------
        self.BDG    : Objet utilitaire pour traiter des services BDG.
         
        """
        
        #Extraire les paramètres de connexion BD et BDG à partir du fichier de configuration
        arcpy.AddMessage("- Lecture des paramètres de connexion dans le fichier de configuration, Section:" + sEnv)
        #Vérifier si la section est présente dans le fichier de config
        if self.Config.has_section(sEnv):
            #Vérifier l'option UsagerBd
            if self.Config.has_option(sEnv,'UsagerBd'):
                sUsagerBd = self.Config.get(sEnv, 'UsagerBd')
                self.nomUsagerBd = sUsagerBd
            else:
                #Définir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:UsagerBd"]
                message.insert(1,"Vous devez absolument corriger la connexion dans la BDG via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionBDG(message)
            
            #Vérifier l'option MotPasseBd
            if self.Config.has_option(sEnv,'MotPasseBd'):
                sMotPasseBd = self.Config.get(sEnv, 'MotPasseBd')
            else:
                #Définir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:MotPasseBd"]
                message.insert(1,"Vous devez absolument corriger la connexion dans la BDG via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionBDG(message)
        else:
            #Définir l'erreur
            message = ["Section absente du fichier de configuration : " + sEnv]
            message.insert(1,"Vous devez absolument effectuer une connexion dans BDG via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionBDG(message)
        
        #Instanciation de la classe BDG et connexion à la BD BDG
        arcpy.AddMessage("- Connexion à la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.BDG = util_bd.Bd(sEnv, sUsagerBd, self.DecoderMotPasse(sMotPasseBd))
        
        #Ouverture et Validation de la connexion à la BD
        self.BDG.open()
        
        #Écrire les statistiques d'utilisation
        self.EcrireStatsUtilisation(sEnvStat)
        
        # Sortir du traitement 
        return self.BDG

    #-------------------------------------------------------------------------------------
    def EcrireStatsUtilisation(self, sEnvStat):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement d'écriture des statistiques d'utilisation des outils SIB.
        
        Paramètres:
        -----------
        sEnvStat     : Type d'environnement correspondant à une base de données à écrire dans les statistiques.
               
        Variables:
        ----------
        self.FichierStats       : Nom du fichier des statistiques d'utilisation.
        
        """
        
        #Vérifier si l'environnement de statistiques est spécifié
        if len(sEnvStat) > 0:
            #Vérifier si le fichier de statistiques existe
            if os.path.exists(self.FichierStats):
                #Ouvrir le fichier de statistiques en mode écriture à la fin
                statsFile = open(self.FichierStats, "a")
            #S'il n'existe pas
            else:
                #Créer et ouvrir le fichier de statistiques en mode écriture à la fin
                statsFile = open(self.FichierStats, "a")
                #Écrire l'entête de l'information qu'il contient
                statsFile.write("Date, \t Env, \t Usager, \t UsagerBD, \t UsagerSIB, \t Outil\n")
            
            #Écrire de l'information d'utilisation
            statsFile.write(str(datetime.datetime.now()) + ", \t" + sEnvStat + ", \t" + os.getenv("username") + ", \t" + self.nomUsagerBd + ", \tNone, \t" + sys.argv[0] + "\n")
            
            #Fermer le fichier de statistiques
            statsFile.close()
        
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def ValiderConnexionBDG(self):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de validation de toutes les connexions BDG contenu dans le
        fichier de configuration.
        
        Paramètres:
        -----------
        Aucun
               
        Variables:
        ----------
        self.Config.sections    : Liste de toutes les sections contenue dans le fichier de configuration.
        sSection                : Section à traiter dans la liste.
         
        """
        
        #Extraire les paramètres de connexion BD et BDG à partir du fichier de configuration
        arcpy.AddMessage("- Validation du fichier de configuration")
        
        #Traiter toutes les section du fichier de configuration
        for sSection in self.Config.sections():
            #Ouvrir la connexion BDG pour la section à traiter
            arcpy.AddMessage(" ")
            self.OuvrirConnexionBDG(sSection)
            
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def ConnecterCompteBDG(self, sEnv, sUsagerBd, sMotPasseBd):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création ou de correction du fichier de configuration
        afin de définir la connexion automatique par défaut dans BDG.
        
        Paramètres:
        -----------
        sEnv            : Type d'environnement correspondant à une base de données.
        sUsagerBd       : Nom de l'usager de la BD.
        sMotPasseBd     : Mot de passe de l'usager de la BD.
               
        Variables:
        ----------
        self.Config     : Objet utilitaire pour traiter le fichier de configuration.        
        oConfigFile     : Objet contenant le fichier de configuration.
        """
        
        #Afficher un message général
        arcpy.AddMessage("- Définition des paramètres de connexion dans le fichier de configuration")
        
        #Instanciation de la classe utilitaire util_bd
        arcpy.AddMessage("- Connexion à la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.BDG = util_bd.Bd(sEnv, sUsagerBd, sMotPasseBd)
        
        #Validation de la connexion à la BD       
        self.BDG.open()    
        arcpy.AddMessage("  Succès de la connexion")
        
        #Vérifier si la section est absente dans le fichier de config
        if not self.Config.has_section(sEnv):
            #Ajouter la section manquante
            arcpy.AddMessage("- Ajouter la section : " + sEnv)
            self.Config.add_section(sEnv)
        
        #Ajouter ou corriger l'option UsagerBd
        self.Config.set(sEnv, 'UsagerBd', sUsagerBd)
        
        #Ajouter ou corriger l'option MotPasseBd
        self.Config.set(sEnv, 'MotPasseBd', self.CoderMotPasse(sMotPasseBd))     
        
        #Écrire le fichier de config
        arcpy.AddMessage("- Écriture du fichier de configuration")
        with open(self.NomFichierConf, 'w') as oConfigFile:
            self.Config.write(oConfigFile)
        
        # Sortir du traitement 
        return

    #-------------------------------------------------------------------------------------
    def FermerConnexionBDG(self):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de fermeture d'une connexion BDG.
        
        Paramètres:
        -----------
        Aucun
               
        Variables:
        ----------
        Aucune
         
        """
        
        # Fermeture de la connexion de la BDG
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()   #Fermer la connexion de la base de données

        # Sortir du traitement 
        return
        
    #-------------------------------------------------------------------------------------
    def CoderMotPasse(self, motPasse):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour coder un mot de passe.
        
        Paramètres:
        -----------
        motPasse        : Mot de passe à coder 
        
        Variables:
        ----------
        ch              : Caractère à coder
        
        Valeurs de retour:
        -----------------
        motPasseCode : Mot de passe codé.
        
        """
        #Initialiser le mode de passe codé
        motPasseCode = ""
        
        #Traiter les caractères du mot de passe
        for ch in motPasse:
            #Coder le caractère
            motPasseCode = hex(ord(ch))[2:] + '~' + motPasseCode
        
        #Retourner le mot de passe codé
        return motPasseCode[:-1]
        
    #-------------------------------------------------------------------------------------
    def DecoderMotPasse(self, motPasseCode):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour décoder un mot de passe.
        
        Paramètres:
        -----------
        motPasseCode    : Mot de passe à décoder 
        
        Variables:
        ----------
        ch              : Caractère à décoder
        
        Valeurs de retour:
        -----------------
        motPasse     : Mot de passe décodé.
        
        """
        #Initialiser le mode de passe codé
        motPasse = ""
        
        #Traiter les caractères du mot de passe codé
        for ch in motPasseCode.split('~'):
            #Déoder le caractère
            motPasse = chr(int(ch,16)) + motPasse
        
        #Retourner le mot de passe
        return motPasse

    #-------------------------------------------------------------------------------------
    def UsagerBd(self):
    #-------------------------------------------------------------------------------------
        """
        Retourner le nom de l'usager de la BD.
        
        Paramètres:
        -----------
        Aucun
               
        Variables:
        ----------
        Aucune
         
        """
        
        # Sortir du traitement 
        return self.nomUsagerBd

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        # Définir l'objet de gestion des comptes BDG.
        oCompteBDG = CompteBDG()
        
        # Exécuter le traitement de validation des connexions contenue dans le fichier de configuration.
        oCompteBDG.ValiderConnexionBDG()
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("- Succès du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)