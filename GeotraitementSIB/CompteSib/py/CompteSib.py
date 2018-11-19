#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet la validation de toutes les connexions SIB contenu dans le
   fichier de configuration.
   
   L'outil contient la classe utilitaire qui permet la gestion des BDs et des comptes SIB.
    
    Les différentes fonctionnalités de la classe utilitaire sont les suivantes:
    -OuvrirConnexionSib
    -FermerConnexionSib
    -ConnecterCompteSib
    -ValiderConnexionCompteSib
    -CreerCompteSib
    -ModifierCompteSib
    -DetruireCompteSib

   Le fichier de configuration est créé dans le répertoire de l'usager qui est protégé
   en lecture et en écriture. Le nom du fichier est construit à partir de la variable
   d'environnement 'LOCALAPPDATA' qui contient le nom du répertoire de l'usager concaténé
   au nom de fichier "\sib.ini".

   Le fichier de config contient 4 sections dans lesquels on retrouve 4 paramètres avec leurs valeurs.
   
   Les 4 sections sont les suivantes:
    SIB_PRO: Base de données officielle de production des données.
    SIB_TST: Base de données utilisée seulement par l'équipe de support SIB pour effectuer ses tests.
    SIB_DEV: Base de données utilisée seulement par les équipes de développement pour effectuer leurs tests.
    BDG_SIB_TST: Base de données utilisée par les équipes de production pour effectuer leurs tests.

   Les 4 paramètres sont les suivants:
    UsagerBd: Nom de l'usager de la base de données pour lequel on désire se connecter.
    MotPasseBd: Mot de passe de l'usager de la base de données pour lequel on désire se connecter.
    UsagerSib: Nom de l'usager SIB pour lequel on désire se connecter.
    MotPasseSib: Mot de passe de l'usager SIB pour lequel on désire se connecter.

   Exemple du fichier de config:   
    [SIB_PRO]
    UsagerBd: modview
    MotPasseBd: decyukon
    UsagerSib: demon_prod
    MotPasseSib: dem3pro

    [SIB_TST]
    UsagerBd: modview
    MotPasseBd: modview
    UsagerSib: demon_prod
    MotPasseSib: dem3pro

    [SIB_DEV]
    UsagerBd: nsprod
    MotPasseBd: dev
    UsagerSib: demon_prod
    MotPasseSib: dem3pro

    [BDG_SIB_TST]
    UsagerBd: modview
    MotPasseBd: modview
    UsagerSib: demon_prod
    MotPasseSib: dem3pro
    
   NB: Certaines sections peuvent être absentes ou d'autres présentes.
    
Nom: CompteSIB.py

Auteur: Michel Pothier         Date: 6 octobre 2014

Paramètres:
-----------
Aucun

Classe:
-------
 Nom                    Description
 ---------------------  --------------------------------------------------------------------
 CompteSib              Permet la gestion des comptes SIB.
 
Retour:
-------
 ErrorLevel  Integer  Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CompteSib.py 1994 2015-08-26 13:21:06Z mpothier $"
#********************************************************************************************

# Identification des librairies utilisees 
import os, sys, arcpy, datetime, util_sib, ConfigParser, cx_Oracle

#*******************************************************************************************
class ExceptionConnexionSib(Exception):
#*******************************************************************************************
    """
    Classe d'exception dérivée de la classe Exception pour gèrer l'arrêt du
    programme lorsque il y a un problème dans l'exécution d'un service de
    compte SIB
    
    Lors de l'instanciation, passez une chaîne de caractère en argument
    pour d'écrire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CompteSib(object):
#*******************************************************************************************
    """
    Permet la gestion des BDs et des comptes SIB.
    
    Les différentes fonctionnalités sont les suivantes:
    -OuvrirConnexionSib
    -FermerConnexionSib
    -ConnecterCompteSib
    -ValiderConnexionCompteSib
    -CreerCompteSib
    -ModifierCompteSib
    -DetruireCompteSib
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de gestion des comptes SIB.
        
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
        self.NomFichierConf = os.environ['LOCALAPPDATA'] + "\sib.ini"
        
        #Message de lecture du fichier de configuration
        arcpy.AddMessage("- Lecture du fichier de configuration : " + self.NomFichierConf)
        #Instanciation du fichier de configuration
        self.Config = ConfigParser.ConfigParser()
        #Lecture du fichier de configuration
        self.FichierConfig = self.Config.read(self.NomFichierConf)
        #Afficher les sections du fichier de config
        arcpy.AddMessage(self.Config.sections())
        
        #initialiser le nom de l'usager de la BD et SIB
        self.nomUsagerBd = ""
        self.nomUsagerSib = ""
        
        #Définir le nom du fichier des statistiques d'utilisations
        self.FichierStats = "S:\\Developpement\\geo\\" + os.getenv("username") + ".txt"
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def OuvrirConnexionSib(self, sEnv, sEnvStat=""):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement d'ouverture d'une connexion SIB à partir d'un environnement
        et du contenu du fichier de configuration.
        
        Paramètres:
        -----------
        sEnv         : Type d'environnement correspondant à une base de données.
        sEnvStat     : Type d'environnement correspondant à une base de données à écrire dans les statistiques.
               
        Variables:
        ----------
        sUsagerBd       : Nom de l'usager de la BD.
        sMotPasseBd     : Mot de passe de l'usager de la BD.
        sUsagerSib      : Nom de l'usager de Sib.
        sMotPasseSib    : Mot de passe de l'usager Sib.
        self.Config     : Objet utilitaire pour traiter le fichier de configuration.        
               
        Retour:
        ----------
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerBd       : Nom de l'usager de la BD.
        sUsagerSib      : Nom de l'usager de Sib.
        """
        
        #Extraire les paramètres de connexion BD et SIB à partir du fichier de configuration
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
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
            
            #Vérifier l'option MotPasseBd
            if self.Config.has_option(sEnv,'MotPasseBd'):
                sMotPasseBd = self.Config.get(sEnv, 'MotPasseBd')
            else:
                #Définir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:MotPasseBd"]
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
                
            #Vérifier l'option UsagerSib
            if self.Config.has_option(sEnv,'UsagerSib'):
                sUsagerSib = self.Config.get(sEnv, 'UsagerSib')
                self.nomUsagerSib = sUsagerSib
            else:
                #Définir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:UsagerSib"]
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
            
            #Vérifier l'option MotPasseSib
            if self.Config.has_option(sEnv,'MotPasseSib'):
                sMotPasseSib = self.Config.get(sEnv, 'MotPasseSib')
            else:
                #Définir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:MotPasseSib"]
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
        else:
            #Définir l'erreur
            message = ["Section absente du fichier de configuration : " + sEnv]
            message.insert(1,"Vous devez absolument effectuer une connexion dans SIB via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionSib(message)
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.Sib = util_sib.Sib(sEnv, sUsagerBd, self.DecoderMotPasse(sMotPasseBd))

        #Validation de la connexion à la BD de SIB      
        self.Sib.ouvrirConnexionSib()    
        arcpy.AddMessage("  Succès de la connexion")

        #Validation de la connexion SIB
        arcpy.AddMessage("- Connexion à SIB : " + sEnv)
        arcpy.AddMessage("  UsagerSib: " + sUsagerSib)
        arcpy.AddMessage("  MotPasseSib: " + ''.rjust(len(sMotPasseSib),'*'))
        code_retour = self.Sib.cursor.callfunc('ACCES_SQL.pu_entree', cx_Oracle.NUMBER, [sUsagerSib, self.DecoderMotPasse(sMotPasseSib)])
        code_succes = int(code_retour)
        if code_succes <> 1:
            #Définir l'erreur
            message = ["Usager ou Mot de passe invalide : " + sEnv]
            message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionSib(message)
        arcpy.AddMessage("  Succès de la connexion")
        
        #Écrire les statistiques d'utilisation
        self.EcrireStatsUtilisation(sEnvStat)
        
        # Sortir du traitement 
        return self.Sib

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
            statsFile.write(str(datetime.datetime.now()) + ", \t" + sEnvStat + ", \t" + os.getenv("username") + ", \t" + self.nomUsagerBd + ", \t" + self.nomUsagerSib + ", \t" + sys.argv[0] + "\n")
            
            #Fermer le fichier de statistiques
            statsFile.close()
        
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def ValiderConnexionSib(self):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de validation de toutes les connexions SIB contenu dans le
        fichier de configuration.
        
        Paramètres:
        -----------
        Aucun
               
        Variables:
        ----------
        self.Config.sections    : Liste de toutes les sections contenue dans le fichier de configuration.
        sSection                : Section à traiter dans la liste.
         
        """
        
        #Extraire les paramètres de connexion BD et SIB à partir du fichier de configuration
        arcpy.AddMessage("- Validation du fichier de configuration")
        
        #Traiter toutes les section du fichier de configuration
        for sSection in self.Config.sections():
            #Ouvrir la connexion SIB pour la section à traiter
            arcpy.AddMessage(" ")
            self.OuvrirConnexionSib(sSection)
            
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def FermerConnexionSib(self):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de fermeture d'une connexion SIB.
        
        Paramètres:
        -----------
        Aucun
               
        Variables:
        ----------
        Aucune
         
        """
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        self.Sib.cursor.callproc('ACCES_SQL.pu_logout')   #termine la session SIB en détruisant le "jeton"
        self.Sib.fermerConnexionSib()   #Fermer la connexion de la base de données

        # Sortir du traitement 
        return
        
    #-------------------------------------------------------------------------------------
    def EncrypterMotPasse(self, motPasse):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement d'encryption d'un mot de passe.
        
        Paramètres:
        -----------
        motPasse        : Mot de passe à encrypter 
        
        Variables:
        ----------
        iKey        : Clé de chiffrement
        ac          : Caractère ascii
        acData      : Liste des caractères ascii
        cr          : Caractère crypté
        crData      : Liste des caractères cryptés
        hx          : Caractère hexadécimal
        
        Valeurs de retour:
        -----------------
        motPasseEncrypter : Mot de passe crypté.
        
        """
        
        #Initialisation des variables de travail
        iKey = 999
        acData = []
        crData = []
        motPasseEncrypter = ""
        
        #Transformer en liste le maximum de 8 caractères du mor de passe
        chrData = list(motPasse[:8])
        
        #Traiter tous les caractères du mot de passe
        for chr in chrData:
            #Initialisation de la clé de chiffrement
            iKey = iKey & 0xFFFF
            
            #Transformer le caractère en code ascii
            ac = ord(chr)
            acData.append(ac)
            
            #Chiffrer le caractère ascii à partir de la clé de chiffrement
            cr = ac ^ (iKey >> 8)
            crData.append(cr)
            
            #Transformer le caractère chiffré en hexadécimal en ajoutant '~'
            hx = hex(cr)[-2:].upper() + '~'
            motPasseEncrypter = motPasseEncrypter + hx
            
            #calcul de la nouvelle clé de chiffrement
            iKey = ((cr + iKey) * 12345 + 34521) & 0xFFFF
        
        #Retourner le mot de passe encrypté
        return motPasseEncrypter
        
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
        
        #Traiter les caractères du mot de passe (maximum 8)
        for ch in motPasse[:8]:
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
    def UsagerSib(self):
    #-------------------------------------------------------------------------------------
        """
        Retourner le nom de l'usager SIB.
        
        Paramètres:
        -----------
        Aucun
               
        Variables:
        ----------
        Aucune
         
        """
        
        # Sortir du traitement 
        return self.nomUsagerSib
    
    #-------------------------------------------------------------------------------------
    def ConnecterCompteSib(self, sEnv, sUsagerBd, sMotPasseBd, sUsagerSib, sMotPasseSib):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création ou de correction du fichier de configuration
        afin de définir la connexion automatique par défaut dans SIB.
        
        Paramètres:
        -----------
        sEnv            : Type d'environnement correspondant à une base de données.
        sUsagerBd       : Nom de l'usager de la BD.
        sMotPasseBd     : Mot de passe de l'usager de la BD.
        sUsagerSib      : Nom de l'usager de Sib.
        sMotPasseSib    : Mot de passe de l'usager Sib.
               
        Variables:
        ----------
        oSib            : Objet utilitaire pour traiter des services SIB.
        self.Config     : Objet utilitaire pour traiter le fichier de configuration.        
        oConfigFile     : Objet contenant le fichier de configuration.
        """
        
        #Afficher un message général
        arcpy.AddMessage("- Définition des paramètres de connexion dans le fichier de configuration")

        #Forcer la mise en majuscule de l'usager et mot de passe SIB        
        sUsagerSib=sUsagerSib.upper()
        sMotPasseSib=sMotPasseSib.upper()[:8]
        
        #Instanciation de la classe utilitaire Sib
        arcpy.AddMessage("- Connexion à la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.Sib = util_sib.Sib(sEnv, sUsagerBd, sMotPasseBd)
        
        #Validation de la connexion à la BD de SIB        
        self.Sib.ouvrirConnexionSib()    
        arcpy.AddMessage("  Succès de la connexion")
        
        #Validation de la connexion SIB
        arcpy.AddMessage("- Connexion à SIB : " + sEnv)
        arcpy.AddMessage("  UsagerSib: " + sUsagerSib)
        arcpy.AddMessage("  MotPasseSib: " + ''.rjust(len(sMotPasseSib),'*'))
        code_retour = self.Sib.cursor.callfunc('ACCES_SQL.pu_entree', cx_Oracle.NUMBER, [sUsagerSib, sMotPasseSib])
        code_succes = int(code_retour)
        if code_succes <> 1:
            #Définir l'erreur
            message = ["Usager ou Mot de passe invalide : " + sEnv]
            message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionSib(message)
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
        
        #Ajouter ou corriger l'option UsagerSib en majuscule
        self.Config.set(sEnv, 'UsagerSib', sUsagerSib)
        
        #Ajouter ou corriger l'option MotPasseSib en majuscule
        self.Config.set(sEnv, 'MotPasseSib', self.CoderMotPasse(sMotPasseSib))       

        #Écrire le fichier de config
        arcpy.AddMessage("- Écriture du fichier de configuration")
        with open(self.NomFichierConf, 'w') as oConfigFile:
            self.Config.write(oConfigFile)
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        # Définir l'objet de gestion des comptes Sib.
        oCompteSib = CompteSib()
        
        # Exécuter le traitement de validation des connexions contenue dans le fichier de configuration.
        oCompteSib.ValiderConnexionSib()
    
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