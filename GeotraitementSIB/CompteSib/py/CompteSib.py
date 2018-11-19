#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************
"""Outil qui permet la validation de toutes les connexions SIB contenu dans le
   fichier de configuration.
   
   L'outil contient la classe utilitaire qui permet la gestion des BDs et des comptes SIB.
    
    Les diff�rentes fonctionnalit�s de la classe utilitaire sont les suivantes:
    -OuvrirConnexionSib
    -FermerConnexionSib
    -ConnecterCompteSib
    -ValiderConnexionCompteSib
    -CreerCompteSib
    -ModifierCompteSib
    -DetruireCompteSib

   Le fichier de configuration est cr�� dans le r�pertoire de l'usager qui est prot�g�
   en lecture et en �criture. Le nom du fichier est construit � partir de la variable
   d'environnement 'LOCALAPPDATA' qui contient le nom du r�pertoire de l'usager concat�n�
   au nom de fichier "\sib.ini".

   Le fichier de config contient 4 sections dans lesquels on retrouve 4 param�tres avec leurs valeurs.
   
   Les 4 sections sont les suivantes:
    SIB_PRO: Base de donn�es officielle de production des donn�es.
    SIB_TST: Base de donn�es utilis�e seulement par l'�quipe de support SIB pour effectuer ses tests.
    SIB_DEV: Base de donn�es utilis�e seulement par les �quipes de d�veloppement pour effectuer leurs tests.
    BDG_SIB_TST: Base de donn�es utilis�e par les �quipes de production pour effectuer leurs tests.

   Les 4 param�tres sont les suivants:
    UsagerBd: Nom de l'usager de la base de donn�es pour lequel on d�sire se connecter.
    MotPasseBd: Mot de passe de l'usager de la base de donn�es pour lequel on d�sire se connecter.
    UsagerSib: Nom de l'usager SIB pour lequel on d�sire se connecter.
    MotPasseSib: Mot de passe de l'usager SIB pour lequel on d�sire se connecter.

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
    
   NB: Certaines sections peuvent �tre absentes ou d'autres pr�sentes.
    
Nom: CompteSIB.py

Auteur: Michel Pothier         Date: 6 octobre 2014

Param�tres:
-----------
Aucun

Classe:
-------
 Nom                    Description
 ---------------------  --------------------------------------------------------------------
 CompteSib              Permet la gestion des comptes SIB.
 
Retour:
-------
 ErrorLevel  Integer  Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
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
    Classe d'exception d�riv�e de la classe Exception pour g�rer l'arr�t du
    programme lorsque il y a un probl�me dans l'ex�cution d'un service de
    compte SIB
    
    Lors de l'instanciation, passez une cha�ne de caract�re en argument
    pour d'�crire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CompteSib(object):
#*******************************************************************************************
    """
    Permet la gestion des BDs et des comptes SIB.
    
    Les diff�rentes fonctionnalit�s sont les suivantes:
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
        
        #D�finir le nom du fichier des statistiques d'utilisations
        self.FichierStats = "S:\\Developpement\\geo\\" + os.getenv("username") + ".txt"
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def OuvrirConnexionSib(self, sEnv, sEnvStat=""):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement d'ouverture d'une connexion SIB � partir d'un environnement
        et du contenu du fichier de configuration.
        
        Param�tres:
        -----------
        sEnv         : Type d'environnement correspondant � une base de donn�es.
        sEnvStat     : Type d'environnement correspondant � une base de donn�es � �crire dans les statistiques.
               
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
        
        #Extraire les param�tres de connexion BD et SIB � partir du fichier de configuration
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
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
            
            #V�rifier l'option MotPasseBd
            if self.Config.has_option(sEnv,'MotPasseBd'):
                sMotPasseBd = self.Config.get(sEnv, 'MotPasseBd')
            else:
                #D�finir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:MotPasseBd"]
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
                
            #V�rifier l'option UsagerSib
            if self.Config.has_option(sEnv,'UsagerSib'):
                sUsagerSib = self.Config.get(sEnv, 'UsagerSib')
                self.nomUsagerSib = sUsagerSib
            else:
                #D�finir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:UsagerSib"]
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
            
            #V�rifier l'option MotPasseSib
            if self.Config.has_option(sEnv,'MotPasseSib'):
                sMotPasseSib = self.Config.get(sEnv, 'MotPasseSib')
            else:
                #D�finir l'erreur
                message = ["Option absente du fichier de configuration : Section:" + sEnv + ", Option:MotPasseSib"]
                message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
                #Retourner l'erreur
                raise ExceptionConnexionSib(message)
        else:
            #D�finir l'erreur
            message = ["Section absente du fichier de configuration : " + sEnv]
            message.insert(1,"Vous devez absolument effectuer une connexion dans SIB via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionSib(message)
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.Sib = util_sib.Sib(sEnv, sUsagerBd, self.DecoderMotPasse(sMotPasseBd))

        #Validation de la connexion � la BD de SIB      
        self.Sib.ouvrirConnexionSib()    
        arcpy.AddMessage("  Succ�s de la connexion")

        #Validation de la connexion SIB
        arcpy.AddMessage("- Connexion � SIB : " + sEnv)
        arcpy.AddMessage("  UsagerSib: " + sUsagerSib)
        arcpy.AddMessage("  MotPasseSib: " + ''.rjust(len(sMotPasseSib),'*'))
        code_retour = self.Sib.cursor.callfunc('ACCES_SQL.pu_entree', cx_Oracle.NUMBER, [sUsagerSib, self.DecoderMotPasse(sMotPasseSib)])
        code_succes = int(code_retour)
        if code_succes <> 1:
            #D�finir l'erreur
            message = ["Usager ou Mot de passe invalide : " + sEnv]
            message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionSib(message)
        arcpy.AddMessage("  Succ�s de la connexion")
        
        #�crire les statistiques d'utilisation
        self.EcrireStatsUtilisation(sEnvStat)
        
        # Sortir du traitement 
        return self.Sib

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
            statsFile.write(str(datetime.datetime.now()) + ", \t" + sEnvStat + ", \t" + os.getenv("username") + ", \t" + self.nomUsagerBd + ", \t" + self.nomUsagerSib + ", \t" + sys.argv[0] + "\n")
            
            #Fermer le fichier de statistiques
            statsFile.close()
        
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def ValiderConnexionSib(self):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de validation de toutes les connexions SIB contenu dans le
        fichier de configuration.
        
        Param�tres:
        -----------
        Aucun
               
        Variables:
        ----------
        self.Config.sections    : Liste de toutes les sections contenue dans le fichier de configuration.
        sSection                : Section � traiter dans la liste.
         
        """
        
        #Extraire les param�tres de connexion BD et SIB � partir du fichier de configuration
        arcpy.AddMessage("- Validation du fichier de configuration")
        
        #Traiter toutes les section du fichier de configuration
        for sSection in self.Config.sections():
            #Ouvrir la connexion SIB pour la section � traiter
            arcpy.AddMessage(" ")
            self.OuvrirConnexionSib(sSection)
            
        # Sortir du traitement 
        return 

    #-------------------------------------------------------------------------------------
    def FermerConnexionSib(self):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de fermeture d'une connexion SIB.
        
        Param�tres:
        -----------
        Aucun
               
        Variables:
        ----------
        Aucune
         
        """
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        self.Sib.cursor.callproc('ACCES_SQL.pu_logout')   #termine la session SIB en d�truisant le "jeton"
        self.Sib.fermerConnexionSib()   #Fermer la connexion de la base de donn�es

        # Sortir du traitement 
        return
        
    #-------------------------------------------------------------------------------------
    def EncrypterMotPasse(self, motPasse):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement d'encryption d'un mot de passe.
        
        Param�tres:
        -----------
        motPasse        : Mot de passe � encrypter 
        
        Variables:
        ----------
        iKey        : Cl� de chiffrement
        ac          : Caract�re ascii
        acData      : Liste des caract�res ascii
        cr          : Caract�re crypt�
        crData      : Liste des caract�res crypt�s
        hx          : Caract�re hexad�cimal
        
        Valeurs de retour:
        -----------------
        motPasseEncrypter : Mot de passe crypt�.
        
        """
        
        #Initialisation des variables de travail
        iKey = 999
        acData = []
        crData = []
        motPasseEncrypter = ""
        
        #Transformer en liste le maximum de 8 caract�res du mor de passe
        chrData = list(motPasse[:8])
        
        #Traiter tous les caract�res du mot de passe
        for chr in chrData:
            #Initialisation de la cl� de chiffrement
            iKey = iKey & 0xFFFF
            
            #Transformer le caract�re en code ascii
            ac = ord(chr)
            acData.append(ac)
            
            #Chiffrer le caract�re ascii � partir de la cl� de chiffrement
            cr = ac ^ (iKey >> 8)
            crData.append(cr)
            
            #Transformer le caract�re chiffr� en hexad�cimal en ajoutant '~'
            hx = hex(cr)[-2:].upper() + '~'
            motPasseEncrypter = motPasseEncrypter + hx
            
            #calcul de la nouvelle cl� de chiffrement
            iKey = ((cr + iKey) * 12345 + 34521) & 0xFFFF
        
        #Retourner le mot de passe encrypt�
        return motPasseEncrypter
        
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
        
        #Traiter les caract�res du mot de passe (maximum 8)
        for ch in motPasse[:8]:
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
    def UsagerSib(self):
    #-------------------------------------------------------------------------------------
        """
        Retourner le nom de l'usager SIB.
        
        Param�tres:
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
        Ex�cuter le traitement de cr�ation ou de correction du fichier de configuration
        afin de d�finir la connexion automatique par d�faut dans SIB.
        
        Param�tres:
        -----------
        sEnv            : Type d'environnement correspondant � une base de donn�es.
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
        
        #Afficher un message g�n�ral
        arcpy.AddMessage("- D�finition des param�tres de connexion dans le fichier de configuration")

        #Forcer la mise en majuscule de l'usager et mot de passe SIB        
        sUsagerSib=sUsagerSib.upper()
        sMotPasseSib=sMotPasseSib.upper()[:8]
        
        #Instanciation de la classe utilitaire Sib
        arcpy.AddMessage("- Connexion � la BD : " + sEnv)
        arcpy.AddMessage("  UsagerBd: " + sUsagerBd)
        arcpy.AddMessage("  MotPasseBd: " + ''.rjust(len(sMotPasseBd),'*'))
        self.Sib = util_sib.Sib(sEnv, sUsagerBd, sMotPasseBd)
        
        #Validation de la connexion � la BD de SIB        
        self.Sib.ouvrirConnexionSib()    
        arcpy.AddMessage("  Succ�s de la connexion")
        
        #Validation de la connexion SIB
        arcpy.AddMessage("- Connexion � SIB : " + sEnv)
        arcpy.AddMessage("  UsagerSib: " + sUsagerSib)
        arcpy.AddMessage("  MotPasseSib: " + ''.rjust(len(sMotPasseSib),'*'))
        code_retour = self.Sib.cursor.callfunc('ACCES_SQL.pu_entree', cx_Oracle.NUMBER, [sUsagerSib, sMotPasseSib])
        code_succes = int(code_retour)
        if code_succes <> 1:
            #D�finir l'erreur
            message = ["Usager ou Mot de passe invalide : " + sEnv]
            message.insert(1,"Vous devez absolument corriger la connexion dans SIB via le Geotraitement")
            #Retourner l'erreur
            raise ExceptionConnexionSib(message)
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
        
        #Ajouter ou corriger l'option UsagerSib en majuscule
        self.Config.set(sEnv, 'UsagerSib', sUsagerSib)
        
        #Ajouter ou corriger l'option MotPasseSib en majuscule
        self.Config.set(sEnv, 'MotPasseSib', self.CoderMotPasse(sMotPasseSib))       

        #�crire le fichier de config
        arcpy.AddMessage("- �criture du fichier de configuration")
        with open(self.NomFichierConf, 'w') as oConfigFile:
            self.Config.write(oConfigFile)
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        # D�finir l'objet de gestion des comptes Sib.
        oCompteSib = CompteSib()
        
        # Ex�cuter le traitement de validation des connexions contenue dans le fichier de configuration.
        oCompteSib.ValiderConnexionSib()
    
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