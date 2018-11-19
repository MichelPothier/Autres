#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerCompteSib.py
# Auteur    : Michel Pothier
# Date      : 24 octobre 2014

"""
    Application qui permet de créer un nouveau compte dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                            défaut = SIB_PRO
    prenom          OB      Prénom de l'usager
                            défaut = 
    nom             OB      Nom de l'usager
                            défaut = 
    cd_user         OB      Code de l'usager déterminé à partir du prénom et du nom lorsque spécifié
                            défaut = 
    langue          OB      Langue pricipale de l'usager
                            défaut = "F"
    adr_email       OB      Adresse courriel de l'usager déterminé à partir du code de l'usager
                            défaut = 
    cd_user_ab      OB      Code de l'usager abrégé déterminé à partir du prénom et du nom lorsque spécifié
                            défaut = 
    listeCdGrp      OB      Liste des groupes de privilèges accordés à l'usager 
                            Défaut = <les 3 premiers groupes>
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerCompteSib.py env prenom nom cd_user langue adr_email cd_user_ab listeCdGrp

    Exemple:
        CreerCompteSib.py SIB_PRO michel pothier mpothier mpothier@rncan.gc.ca F MPO MENU,PROD,INTERACT

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerCompteSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerCompteSib(object):
#*******************************************************************************************
    """
    Permet de créer un nouveau compte dans SIB avec ses groupes de privilèges.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'un nouveau compte dans SIB avec ses groupes de privilèges.
        
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
    def validerParamObligatoire(self, env, prenom, nom, cd_user, langue, adr_email, cd_user_ab, listeCdGrp):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        prenom          : Prénom de l'usager
        nom             : Nom de l'usager
        cd_user         : Code de l'usager déterminé à partir du prénom et du nom lorsque spécifié
        langue          : Langue pricipale de l'usager
        adr_email       : Adresse courriel de l'usager déterminé à partir du code de l'usager
        cd_user_ab      : Code de l'usager abrégé déterminé à partir du prénom et du nom lorsque spécifié
        listeCdGrp      : Liste des groupes de privilèges accordés à l'usager 

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(prenom) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'prenom')

        if (len(nom) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom')

        if (len(cd_user) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_user')

        if (len(langue) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'langue')

        if (len(adr_email) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'adr_email')

        if (len(cd_user_ab) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_user_ab')

        if (len(listeCdGrp) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'listeCdGrp')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, prenom, nom, cd_user, langue, adr_email, cd_user_ab, listeCdGrp):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un nouveau compte dans SIB avec ses groupes de privilèges.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        prenom          : Prénom de l'usager
        nom             : Nom de l'usager
        cd_user         : Code de l'usager déterminé à partir du prénom et du nom lorsque spécifié
        langue          : Langue pricipale de l'usager
        adr_email       : Adresse courriel de l'usager déterminé à partir du code de l'usager
        cd_user_ab      : Code de l'usager abrégé déterminé à partir du prénom et du nom lorsque spécifié
        listeCdGrp      : Liste des groupes de privilèges accordés à l'usager 

        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : nombre de messages d'erreur générés par le service de transaction SIB
        messageSib      : description du message reçue du service de transaction SIB

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Vérifier si le code de l'usager est déjà présent
        arcpy.AddMessage("- Valider le code du nouvel usagé")
        if self.Sib.requeteSib("SELECT CD_USER FROM F005_US WHERE CD_USER='" + cd_user + "'"):
            #Envoyer une exception
            raise Exception("Le code de l'usager est déjà utilisé : %s" %cd_user)
        
        #Vérifier si le code de l'usager abrégé est déjà présent
        arcpy.AddMessage("- Valider le code du nouvel usagé abrégé")
        if self.Sib.requeteSib("SELECT CD_USER FROM F005_US WHERE CD_USER_AB='" + cd_user_ab + "'"):
            #Envoyer une exception
            raise Exception("Le code de l'usager abrégé est déjà utilisé : %s" %cd_user_ab)

        #Extraire la liste des groupes de privilège permis
        arcpy.AddMessage("- Valider la liste des codes des groupes de privilèges du nouvel usagé")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F006_GR")
        #Initialiser le groupe
        listeGroupePermis = []
        #Construire la liste des groupes permises
        for grp in resultat:
            #Ajouter le groupe à la liste
            listeGroupePermis.append(grp[0])
        
        #Traiter la liste des groupes de privilège de l'usager
        for grpNom in listeCdGrp.split(","):
            #Extraire le groupe des noms
            grp = grpNom.split(":")[0]
            #Vérifier si le groupe de privilège de l'usager est valide
            if grp not in listeGroupePermis:
                #Envoyer une exception
                raise Exception("Le groupe de privilège de l'usager est invalide : " + grp + " " + str(listeGroupePermis))
        
        #Créer le mot de passe par défaut selon la règle du 333
        arcpy.AddMessage("- Créer le mot de passe temporaire de l'usager selon la règle du 333")
        motPasse = prenom[:3].upper() + "3" + nom[:3].upper()
        arcpy.AddWarning("  Mot de passe temporaire : " + motPasse)
        
        #Encripter le mot de passe
        arcpy.AddMessage("- Encripter le mot de passe de l'usager")
        motPasseEncrypter = self.CompteSib.EncrypterMotPasse(motPasse)
        
        #Créer le compte de l'usager
        arcpy.AddMessage("- Créer le compte SIB de l'usager")
        nb_acces = '0'
        actif = '1'
        sql = "INSERT INTO F005_US VALUES (P0G03_UTL.PU_HORODATEUR,'"+ sUsagerSib + "',SYSDATE,SYSDATE,'" + cd_user + "','" + nom + "','" + prenom + "','" + motPasseEncrypter + "'," + nb_acces + "," + actif + ",SYSDATE,'" + langue + "','" + adr_email + "','" + cd_user_ab + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Ajouter les groupes de privilège de l'usager
        arcpy.AddMessage("- Ajouter les groupes de privilège de l'usager")
        #Traiter la liste des groupes de privilège de l'usager
        for grpNom in listeCdGrp.split(","):
            #Extraire le groupe des noms
            grp = grpNom.split(":")[0]
            sql = "INSERT INTO F007_UG VALUES ('"+ sUsagerSib + "',SYSDATE,SYSDATE,'" + cd_user + "','" + grp + "',P0G03_UTL.PU_HORODATEUR)"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env         = "SIB_PRO"
        prenom      = ""
        nom         = ""
        cd_user     = ""
        langue      = "F"
        adr_email   = ""
        cd_user_ab  = ""
        listeCdGrp      = "MENU,INTERACT,PROD-OPE"

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            prenom = sys.argv[2]

        if len(sys.argv) > 3:
            nom = sys.argv[3]

        if len(sys.argv) > 4:
            cd_user = sys.argv[4].upper()

        if len(sys.argv) > 5:
            langue = sys.argv[5].upper()

        if len(sys.argv) > 6:
            adr_email = sys.argv[6].lower()
                
        if len(sys.argv) > 7:
            cd_user_ab = sys.argv[7].upper()

        if len(sys.argv) > 8:
            listeCdGrp = sys.argv[8].upper().replace(";",",").replace("'","")
        
        #Définir l'objet de création d'un nouveau compte SIB pour un usager.
        oCreerCompteSib = CreerCompteSib()
        
        #Valider les paramètres obligatoires
        oCreerCompteSib.validerParamObligatoire(env, prenom, nom, cd_user, langue, adr_email, cd_user_ab, listeCdGrp)
        
        #Exécuter le traitement de création d'un nouveau compte SIB pour un usager.
        oCreerCompteSib.executer(env, prenom, nom, cd_user, langue, adr_email, cd_user_ab, listeCdGrp)
    
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