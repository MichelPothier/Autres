#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerExecutantProduction.py
# Auteur    : Michel Pothier
# Date      : 17 novembre 2014

"""
    Application qui permet de créer un nouvel exécutant de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_execu        OB      Code de l'exécutant de production à créer.
                            défaut = 
    actif           OB      Indique si l'exécutant de production est actif ou non [0:Non/1:Oui].
                            défaut = 1
    firme           OB      Nom de l'exécutant (firme) de production.
                            défaut = 
    adr_no          OB      Numéro civique de l'adresse ou est situé l'exécutant de production.
                            défaut =
    adr_rue         OB      Nom de la rue de l'adresse ou est situé l'exécutant de production.
                            défaut = 
    ville           OB      Nom de la ville de l'adresse ou est situé l'exécutant de production.
                            défaut =
    cd_prov         OB      Code la province de l'adresse ou est situé l'exécutant de production.
                            défaut = QC
    cd_postal       OB      Code postal de l'adresse ou est situé l'exécutant de production sous la forme C#C #C#.
                            défaut =
    cd_pays         OB      Code du pays de l'adresse ou est situé l'exécutant de production.
                            défaut = CA
    tel             OB      Numéro de téléphone de l'exécutant de production sous la forme ###-###-####.
                            défaut =
    fax             OB      Numéro de fax de l'exécutant de production sous la forme ###-###-####.
                            défaut =
    adr_email       OB      Courriel de l'exécutant de production.
                            défaut =
    site_ftp        OB      Site_ftp de l'exécutant de production.
                            défaut = 
    cd_acces        OB      Code d'accès du site_ftp de l'exécutant de production.
                            défaut = 
    cd_comp         OB      Code de compression des fichiers utilisés par l'exécutant de production [GZIP/WINZIP].
                            défaut = 
    cd_decomp       OB      Code de décompression des fichiers utilisés par l'exécutant de production [GUNZIP/WUNZIP].
                            défaut = 
    format_image    OB      Format des images utilisé par l'exécutant de production [PIX/TIF].
                            défaut = 
    no_tps          OB      Numéro de TPS de l'exécutant de production.
                            défaut =
    no_contact      OB      Numéro du contact de l'exécutant de production.
                            défaut =
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerExecutantProduction.py env cd_execu actif firme adr_no adr_rue ville cd_prov cd_postal cd_pays tel fax adr_email site_ftp cd_acces cd_comp cd_decomp format_image no_tps no_contact

    Exemple:
        CreerExecutantProduction.py SIB_PRO TEST 1:OUI "Firme Test" 200 Principale Sherbrooke QC:Québec "J0B 2P0" CA:Canada 819-823-6668 819-823-6669 test@rncan.gc.ca test bjk_123 gzip gunzip TIF R1234567 #

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerExecutantProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerExecutantProduction(object):
#*******************************************************************************************
    """
    Permet de créer un nouvel executant de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'un nouvel exécutant de production dans SIB.
        
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
    def validerParamObligatoire(self,env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'équipe de production à créer.
        actif           : Indique si l'exécutant de production est actif ou non [0:Non/1:Oui].
        firme           : Nom de l'exécutant (firme) de production.
        adr_no          : Numéro civique de l'adresse ou est situé l'exécutant de production.
        adr_rue         : Nom de la rue de l'adresse ou est situé l'exécutant de production.
        ville           : Nom de la ville de l'adresse ou est situé l'exécutant de production.
        cd_prov         : Code la province de l'adresse ou est situé l'exécutant de production.
        cd_postal       : Code postal de l'adresse ou est situé l'exécutant de production sous la forme C#C #C#.
        cd_pays         : Code du pays de l'adresse ou est situé l'exécutant de production.
        tel             : Numéro de téléphone de l'exécutant de production sous la forme ###-###-####.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(cd_execu) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_execu')

        if actif <> "0" and actif <> "1":
            raise Exception("Paramètre obligatoire manquant: %s" %'actif')

        if (len(firme) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'firme')

        if (len(adr_no) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'adr_no')

        if (len(adr_rue) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'adr_rue')

        if (len(ville) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'ville')

        if (len(cd_prov) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_prov')

        if (len(cd_postal) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_postal')

        if (len(cd_pays) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_pays')

        if (len(tel) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tel')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel,fax,adr_email,site_ftp,cd_acces,cd_comp,cd_decomp,format_image,no_tps,no_contact):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un nouvel exécutant de production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'équipe de production à créer.
        actif           : Indique si l'exécutant de production est actif ou non [0:Non/1:Oui].
        firme           : Nom de l'exécutant (firme) de production.
        adr_no          : Numéro civique de l'adresse ou est situé l'exécutant de production.
        adr_rue         : Nom de la rue de l'adresse ou est situé l'exécutant de production.
        ville           : Nom de la ville de l'adresse ou est situé l'exécutant de production.
        cd_prov         : Code la province de l'adresse ou est situé l'exécutant de production.
        cd_postal       : Code postal de l'adresse ou est situé l'exécutant de production sous la forme C#C #C#.
        cd_pays         : Code du pays de l'adresse ou est situé l'exécutant de production.
        tel             : Numéro de téléphone de l'exécutant de production sous la forme ###-###-####.
        fax             : Numéro de fax de l'exécutant de production sous la forme ###-###-####.
        adr_email       : Courriel de l'exécutant de production.
        site_ftp        : Site_ftp de l'exécutant de production.
        cd_acces        : Code d'accès du site_ftp de l'exécutant de production. 
        cd_comp         : Code de compression des fichiers utilisés par l'exécutant de production.
        cd_decomp       : Code de décompression des fichiers utilisés par l'exécutant de production.
        format_image    : Format des images utilisé par l'exécutant de production.
        no_tps          : Numéro de TPS de l'exécutant de production.
        no_contact      : Numéro du contact de l'exécutant de production.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

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
        
        #Valider si l'exécutant de production est déjà présent
        arcpy.AddMessage("- Valider le code de l'exécutant de production")
        resultat = self.Sib.requeteSib("SELECT CD_EXECU FROM F604_EX WHERE CD_EXECU='" + cd_execu + "'")
        #Vérifier si l'exécutant de production est présent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("Le code de l'exécutant de production '" + cd_execu + "' est déjà présent")

        #Vérifier si le numéro de fax est vide
        if fax == "":
            #Ajouter la valeur NULL
            fax = "NULL"
        #si le numéro de fax n'est pas vide
        else:
            #Ajouter les apostrophes
            fax = "'" + fax + "'"

        #Vérifier si le courriel est vide
        if adr_email == "":
            #Ajouter la valeur NULL
            adr_email = "NULL"
        #si le courriel n'est pas vide
        else:
            #Ajouter les apostrophes
            adr_email = "'" + adr_email + "'"

        #Vérifier si le site ftp est vide
        if site_ftp == "":
            #Ajouter la valeur NULL
            site_ftp = "NULL"
        #si le site ftp n'est pas vide
        else:
            #Ajouter les apostrophes
            site_ftp = "'" + site_ftp + "'"

        #Vérifier si le code d'acces est vide
        if cd_acces == "":
            #Ajouter la valeur NULL
            cd_acces = "NULL"
        #si le code d'acces n'est pas vide
        else:
            #Ajouter les apostrophes
            cd_acces = "'" + cd_acces + "'"

        #Vérifier si le code de compression est vide
        if cd_comp == "":
            #Ajouter la valeur NULL
            cd_comp = "NULL"
        #si le code de compression n'est pas vide
        else:
            #Ajouter les apostrophes
            cd_comp = "'" + cd_comp + "'"

        #Vérifier si le code de décompression est vide
        if cd_decomp == "":
            #Ajouter la valeur NULL
            cd_decomp = "NULL"
        #si le code de décompression n'est pas vide
        else:
            #Ajouter les apostrophes
            cd_decomp = "'" + cd_decomp + "'"

        #Vérifier si le format d'image est vide
        if format_image == "":
            #Ajouter la valeur NULL
            format_image = "NULL"
        #si le format d'image n'est pas vide
        else:
            #Ajouter les apostrophes
            format_image = "'" + format_image + "'"

        #Vérifier si le numéro de TPS est vide
        if no_tps == "":
            #Ajouter la valeur NULL
            no_tps = "NULL"
        #si le numéro de TPS n'est pas vide
        else:
            #Ajouter les apostrophes
            no_tps = "'" + no_tps + "'"

        #Vérifier si le numéro de contact est vide
        if no_contact == "":
            #Ajouter la valeur NULL
            no_contact = "NULL"

        #Créer l'exécutant de production
        arcpy.AddMessage("- Créer l'exécutant de production")
        sql = "INSERT INTO F604_EX VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + cd_execu + "'," + actif + ",'" + tel + "'," + fax + ",'" + firme + "','" + adr_no + "','" + adr_rue + "','" + ville  + "'"
        sql = sql + ",'" + cd_prov + "','" + cd_postal + "','" + cd_pays + "'," + adr_email + "," + site_ftp + "," + cd_acces + "," + cd_comp + "," + cd_decomp + "," + format_image + "," + no_tps + "," + no_contact + ")"
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
        cd_execu    = ""
        actif       = "1"
        firme       = ""
        adr_no      = ""
        adr_rue     = ""
        ville       = ""
        cd_prov     = ""
        cd_postal   = ""
        cd_pays     = ""
        tel         = ""
        fax         = ""
        adr_email   = ""
        site_ftp    = ""
        cd_acces    = ""
        cd_comp     = ""
        cd_decomp   = ""
        format_image = ""
        no_tps      = ""
        no_contact  = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_execu = sys.argv[2].upper()
        
        if len(sys.argv) >3:
            if sys.argv[3] <> "#":
                actif = sys.argv[3].split(':')[0]
        
        if len(sys.argv) > 4:
            firme = sys.argv[4]
        
        if len(sys.argv) > 5:
            adr_no = sys.argv[5]
        
        if len(sys.argv) > 6:
            adr_rue = sys.argv[6]
        
        if len(sys.argv) > 7:
            ville = sys.argv[7]
        
        if len(sys.argv) > 8:
            cd_prov = sys.argv[8].upper().split(':')[0]
        
        if len(sys.argv) > 9:
            cd_postal = sys.argv[9].upper()
        
        if len(sys.argv) > 10:
            cd_pays = sys.argv[10].upper().split(':')[0]
        
        if len(sys.argv) > 11:
            tel = sys.argv[11]
        
        if len(sys.argv) > 12:
            if sys.argv[12] <> "#":
                fax = sys.argv[12]
        
        if len(sys.argv) > 13:
            if sys.argv[13] <> "#":
                adr_email = sys.argv[13].lower()
        
        if len(sys.argv) > 14:
            if sys.argv[14] <> "#":
                site_ftp = sys.argv[14].lower()
        
        if len(sys.argv) > 15:
            if sys.argv[15] <> "#":
                cd_acces = sys.argv[15].lower()
        
        if len(sys.argv) > 16:
            if sys.argv[16] <> "#":
                cd_comp = sys.argv[16].lower()
        
        if len(sys.argv) > 17:
            if sys.argv[17] <> "#":
                cd_decomp = sys.argv[17].lower()
        
        if len(sys.argv) > 18:
            if sys.argv[18] <> "#":
                format_image = sys.argv[18].upper()
        
        if len(sys.argv) > 19:
            if sys.argv[19] <> "#":
                no_tps = sys.argv[19].upper()
        
        if len(sys.argv) > 20:
            if sys.argv[20] <> "#":
                no_contact = sys.argv[20]
        
        #Définir l'objet de création d'un nouvel exécutant de production dans SIB.
        oCreerExecutantProduction = CreerExecutantProduction()
        
        #Valider les paramètres obligatoires
        oCreerExecutantProduction.validerParamObligatoire(env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel)
        
        #Exécuter le traitement de création d'un nouvel exécutant de production dans SIB.
        oCreerExecutantProduction.executer(env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel,fax,adr_email,site_ftp,cd_acces,cd_comp,cd_decomp,format_image,no_tps,no_contact)
    
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