#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet la validation de toutes les connexions BDG contenu dans le
   fichier de configuration.
   
   L'outil contient la classe utilitaire qui permet la gestion des BDs et des comptes BDG.
    
    Les diff�rentes fonctionnalit�s de la classe utilitaire sont les suivantes:
    -OuvrirConnexionBDG
    -FermerConnexionBDG
    -ConnecterCompteBDG
    -ValiderConnexionCompteBDG
    -CreerCompteBDG
    -ModifierCompteBDG
    -DetruireCompteBDG

   Le fichier de configuration est cr�� dans le r�pertoire de l'usager qui est prot�g�
   en lecture et en �criture. Le nom du fichier est construit � partir de la variable
   d'environnement 'LOCALAPPDATA' qui contient le nom du r�pertoire de l'usager concat�n�
   au nom de fichier "\BDG.ini".

   Le fichier de config contient 3 sections dans lesquels on retrouve 2 param�tres avec leurs valeurs.
   
   Les 3 sections sont les suivantes:
    BDRS_PRO: Base de donn�es officielle des donn�es g�ographique.
    BDRS_TST: Base de donn�es utilis�e seulement par l'�quipe de support BDG pour effectuer ses tests.
    BDRS_DEV: Base de donn�es utilis�e seulement par les �quipes de d�veloppement pour effectuer leurs tests.

   Les 2 param�tres sont les suivants:
    UsagerBd: Nom de l'usager de la base de donn�es pour lequel on d�sire se connecter.
    MotPasseBd: Mot de passe de l'usager de la base de donn�es pour lequel on d�sire se connecter.

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
    
   NB: Certaines sections peuvent �tre absentes ou d'autres pr�sentes.
    
Nom: CompteBDG.py

Auteur: Michel Pothier         Date: 14 octobre 2014

Param�tres:
-----------
Aucun

Classe:
-------
 Nom                    Description
 ---------------------  --------------------------------------------------------------------
 CompteBDG              Permet la gestion des comptes BDG.
 
Retour:
-------
 ErrorLevel  Integer  Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
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
    Classe d'exception d�riv�e de la classe Exception pour g�rer l'arr�t du
    programme lorsque il y a un probl�me dans l'ex�cution d'un service de
    compte BDG
    
    Lors de l'instanciation, passez une cha�ne de caract�re en argument
    pour d'�crire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CompteBDG(object):
#*******************************************************************************************
    """
    Permet la gestion des BDs et des comptes BDG.
    
    Les diff�rentes fonctionnalit�s sont les suivantes:
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
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.NomFichierConfig   : Nom du fichier de configuration.
        self.FichierStats       : Nom du fichier des statistiques d'utilisation.
        self.FichierConfig      : Objet contenant le fichier de configuration.
        self.Config             : Objet utilitaire pour traiter le fichier de configuration.        
        
        """
        
        #D�finir les variable par d�faut
        self.NomFichierConf = os.environ['LOCALAPPDATA'] + "\BDG.ini"
        
        #Message de lecture du fichier de configuration
        arcpy.AddMessage("- Lecture du fichier de configuration : " + self.NomFichierConf)
        #Instanciation du fichier de configuration
        self.Config = ConfigParser.ConfigParser()
        #Lecture du fichier de configuration
        self.FichierConfig = self.Config.read(self.NomFichierConf)
        #Afficher les sections du fichier de config
        arcpy.AddMessage(self.Config.sections())
        
        #D�finir le nom du fichier des statistiques d'utilisations
        self.FichierStats = "S:\\Developpement\\geo\\" + os.getenv("username") + ".txt"
        
        #initialiser le nom de l'usager de la BD
        self.nomUsagerBd = ""
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def OuvrirConnexionBDG(self, sEnv, sEnvStat=""):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement d'ouverture d'une connexion BDG � partir d'un environnement
        et du contenu du fichier de configuration.
        
        Param�tres:
        -----------
        sEnv         : Type d'environnement correspondant � une base de donn�es.
        sEnvStat     : Type d'environnement correspondant � une base de donn�es � �crire dans les statistiques.
               
        Variables:
        ----------
        sUsagerBd       : Nom de l'usager de la BD.
        sMotPasseBd     : Mot de passe de l'usager de la BD.
        self.Config     : Objet utilitaire pour traiter le fichier de configuration.        
               
        Retour:
        ----------
        self.BDG    : Objet utilitaire pour traiter des services BDG.
         
        """
        
        #Extraire les param�tres de connexion BD et BDG � partir du fichier de configuration
        arcpy.AddMessage("- Lecture des param�tres de connexion dans le fichier de configuration, Section:" + sEnv)
        #V�rifier si la section est pr�sente dans le fichier de config
        if self.Config.has_section(sEnv):
            #V�rifier l'option UsagerBd
            if self.Config.has_option(sEnv,'UsagerBd'):
                sUsagerBd = self.Config.get(sEnv, 'UsagerBd')
                self.nomUsagerBd = sUsagerBd
            else:
                #D�finir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:UsagerBd"]
                message.insert(1,"Vous devez absolument corriger la connexion dans la BDG via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionBDG(message)
            
            #V�rifier l'option MotPasseBd
            if self.Config.has_option(sEnv,'MotPasseBd'):
                sMotPasseBd = self.Config.get(sEnv, 'MotPasseBd')
            else:
                #D�finir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:MotPasseBd"]
                message.insert(1,"Vous devez absolument corriger la connexion dans la BDG via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionBDG(message)
        else:
            #D�finir l'erreur
            message = ["Section absente du fichier de configuration : " + sEnv]
            message.insert(1,"Vous devez absolument effectuer une connexion dans BDG via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionBDG(message)
        
        #Instanciation de la classe BDG et connexion � la BD BDG
        arcpy.AddMessage("- Connexion � la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.BDG = util_bd.Bd(sEnv, sUsagerBd, self.DecoderMotPasse(sMotPasseBd))
        
        #Ouverture et Validation de la connexion � la BD
        self.BDG.open()
        
        #�crire les statistiques d'utilisation
        self.EcrireStatsUtilisation(sEnvStat)
        
        # Sortir du traitement 
        return self.BDG

    #-------------------------------------------------------------------------------------
    def EcrireStatsUtilisation(self, sEnvStat):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement d'�criture des statistiques d'utilisation des outils SIB.
        
        Param�tres:
        -----------
        sEnvStat     : Type d'environnement correspondant � une base de donn�es � �crire dans les statistiques.
               
        Variables:
        ----------
        self.FichierStats       : Nom du fichier des statistiques d'utilisation.
        
        """
        
        #V�rifier si l'environnement de statistiques est sp�cifi�
        if len(sEnvStat) > 0:
            #V�rifier si le fichier de statistiques existe
            if os.path.exists(self.FichierStats):
                #Ouvrir le fichier de statistiques en mode �criture � la fin
                statsFile = open(self.FichierStats, "a")
            #S'il n'existe pas
            else:
                #Cr�er et ouvrir le fichier de statistiques en mode �criture � la fin
                statsFile = open(self.FichierStats, "a")
                #�crire l'ent�te de l'information qu'il contient
                statsFile.write("Date, \t Env, \t Usager, \t UsagerBD, \t UsagerSIB, \t Outil\n")
            
            #�crire de l'information d'utilisation
            statsFile.write(str(datetime.datetime.now()) + ", \t" + sEnvStat + ", \t" + os.getenv("username") + ", \t" + self.nomUsagerBd + ", \tNone, \t" + sys.argv[0] + "\n")
            
            #Fermer le fichier de statistiques
            statsFile.close()
        
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def ValiderConnexionBDG(self):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de validation de toutes les connexions BDG contenu dans le
        fichier de configuration.
        
        Param�tres:
        -----------
        Aucun
               
        Variables:
        ----------
        self.Config.sections    : Liste de toutes les sections contenue dans le fichier de configuration.
        sSection                : Section � traiter dans la liste.
         
        """
        
        #Extraire les param�tres de connexion BD et BDG � partir du fichier de configuration
        arcpy.AddMessage("- Validation du fichier de configuration")
        
        #Traiter toutes les section du fichier de configuration
        for sSection in self.Config.sections():
            #Ouvrir la connexion BDG pour la section � traiter
            arcpy.AddMessage(" ")
            self.OuvrirConnexionBDG(sSection)
            
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def ConnecterCompteBDG(self, sEnv, sUsagerBd, sMotPasseBd):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation ou de correction du fichier de configuration
        afin de d�finir la connexion automatique par d�faut dans BDG.
        
        Param�tres:
        -----------
        sEnv            : Type d'environnement correspondant � une base de donn�es.
        sUsagerBd       : Nom de l'usager de la BD.
        sMotPasseBd     : Mot de passe de l'usager de la BD.
               
        Variables:
        ----------
        self.Config     : Objet utilitaire pour traiter le fichier de configuration.        
        oConfigFile     : Objet contenant le fichier de configuration.
        """
        
        #Afficher un message g�n�ral
        arcpy.AddMessage("- D�finition des param�tres de connexion dans le fichier de configuration")
        
        #Instanciation de la classe utilitaire util_bd
        arcpy.AddMessage("- Connexion � la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.BDG = util_bd.Bd(sEnv, sUsagerBd, sMotPasseBd)
        
        #Validation de la connexion � la BD       
        self.BDG.open()    
        arcpy.AddMessage("  Succ�s de la connexion")
        
        #V�rifier si la section est absente dans le fichier de config
        if not self.Config.has_section(sEnv):
            #Ajouter la section manquante
            arcpy.AddMessage("- Ajouter la section : " + sEnv)
            self.Config.add_section(sEnv)
        
        #Ajouter ou corriger l'option UsagerBd
        self.Config.set(sEnv, 'UsagerBd', sUsagerBd)
        
        #Ajouter ou corriger l'option MotPasseBd
        self.Config.set(sEnv, 'MotPasseBd', self.CoderMotPasse(sMotPasseBd))     
        
        #�crire le fichier de config
        arcpy.AddMessage("- �criture du fichier de configuration")
        with open(self.NomFichierConf, 'w') as oConfigFile:
            self.Config.write(oConfigFile)
        
        # Sortir du traitement 
        return

    #-------------------------------------------------------------------------------------
    def FermerConnexionBDG(self):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de fermeture d'une connexion BDG.
        
        Param�tres:
        -----------
        Aucun
               
        Variables:
        ----------
        Aucune
         
        """
        
        # Fermeture de la connexion de la BDG
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()   #Fermer la connexion de la base de donn�es

        # Sortir du traitement 
        return
        
    #-------------------------------------------------------------------------------------
    def CoderMotPasse(self, motPasse):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour coder un mot de passe.
        
        Param�tres:
        -----------
        motPasse        : Mot de passe � coder 
        
        Variables:
        ----------
        ch              : Caract�re � coder
        
        Valeurs de retour:
        -----------------
        motPasseCode : Mot de passe cod�.
        
        """
        #Initialiser le mode de passe cod�
        motPasseCode = ""
        
        #Traiter les caract�res du mot de passe
        for ch in motPasse:
            #Coder le caract�re
            motPasseCode = hex(ord(ch))[2:] + '~' + motPasseCode
        
        #Retourner le mot de passe cod�
        return motPasseCode[:-1]
        
    #-------------------------------------------------------------------------------------
    def DecoderMotPasse(self, motPasseCode):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�coder un mot de passe.
        
        Param�tres:
        -----------
        motPasseCode    : Mot de passe � d�coder 
        
        Variables:
        ----------
        ch              : Caract�re � d�coder
        
        Valeurs de retour:
        -----------------
        motPasse     : Mot de passe d�cod�.
        
        """
        #Initialiser le mode de passe cod�
        motPasse = ""
        
        #Traiter les caract�res du mot de passe cod�
        for ch in motPasseCode.split('~'):
            #D�oder le caract�re
            motPasse = chr(int(ch,16)) + motPasse
        
        #Retourner le mot de passe
        return motPasse

    #-------------------------------------------------------------------------------------
    def UsagerBd(self):
    #-------------------------------------------------------------------------------------
        """
        Retourner le nom de l'usager de la BD.
        
        Param�tres:
        -----------
        Aucun
               
        Variables:
        ----------
        Aucune
         
        """
        
        # Sortir du traitement 
        return self.nomUsagerBd

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        # D�finir l'objet de gestion des comptes BDG.
        oCompteBDG = CompteBDG()
        
        # Ex�cuter le traitement de validation des connexions contenue dans le fichier de configuration.
        oCompteBDG.ValiderConnexionBDG()
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("- Succ�s du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)