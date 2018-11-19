#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierExecutantProduction.py
# Auteur    : Michel Pothier
# Date      : 17 novembre 2014

"""
    Application qui permet de modifier un ex�cutant de production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    cd_execu        OB      Code de l'ex�cutant de production � modifier.
                            d�faut = 
    actif           OB      Indique si l'ex�cutant de production est actif ou non [0:Non/1:Oui].
                            d�faut = 
    firme           OB      Nom de l'ex�cutant (firme) de production.
                            d�faut = 
    adr_no          OB      Num�ro civique de l'adresse ou est situ� l'ex�cutant de production.
                            d�faut =
    adr_rue         OB      Nom de la rue de l'adresse ou est situ� l'ex�cutant de production.
                            d�faut = 
    ville           OB      Nom de la ville de l'adresse ou est situ� l'ex�cutant de production.
                            d�faut =
    cd_prov         OB      Code la province de l'adresse ou est situ� l'ex�cutant de production.
                            ['AB:Alberta','BC:Colombie Britanique','MB:Manitoba','NB:Nouveau Brunswick','NL:Territoire du Nord','NS:Nouvelle �cosse','ON:Ontario','PE:�le du Prince �douard','QC:Qu�bec','SK:Saskatchewan'].
                            d�faut = 
    cd_postal       OB      Code postal de l'adresse ou est situ� l'ex�cutant de production sous la forme C#C #C#.
                            d�faut =
    cd_pays         OB      Code du pays de l'adresse ou est situ� l'ex�cutant de production [CA:Canada].
                            d�faut = 
    tel             OB      Num�ro de t�l�phone de l'ex�cutant de production sous la forme ###-###-####.
                            d�faut =
    fax             OB      Num�ro de fax de l'ex�cutant de production sous la forme ###-###-####.
                            d�faut =
    adr_email       OB      Courriel de l'ex�cutant de production.
                            d�faut =
    site_ftp        OB      Site_ftp de l'ex�cutant de production.
                            d�faut = 
    cd_acces        OB      Code d'acc�s du site_ftp de l'ex�cutant de production.
                            d�faut = 
    cd_comp         OB      Code de compression des fichiers utilis�s par l'ex�cutant de production [gzip/winzip].
                            d�faut = 
    cd_decomp       OB      Code de d�compression des fichiers utilis�s par l'ex�cutant de production [gunzip/winzip].
                            d�faut = 
    format_image    OB      Format des images utilis� par l'ex�cutant de production [PIX/TIF].
                            d�faut = 
    no_tps          OB      Num�ro de TPS de l'ex�cutant de production.
                            d�faut =
    no_contact      OB      Num�ro du contact de l'ex�cutant de production.
                            d�faut =
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierExecutantProduction.py env cd_execu actif firme adr_no adr_rue ville cd_prov cd_postal cd_pays tel fax adr_email site_ftp cd_acces cd_comp cd_decomp format_image no_tps no_contact

    Exemple:
        ModifierExecutantProduction.py SIB_PRO TEST 1:OUI "Firme Test" 200 Principale Sherbrooke QC:Qu�bec "J0B 2P0" CA:Canada 819-823-6668 819-823-6669 test@rncan.gc.ca test bjk_123 gzip gunzip TIF R1234567 "45:Frank Zappa"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierExecutantProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierExecutantProduction(object):
#*******************************************************************************************
    """
    Permet de modifier un ex�cutant de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification d'un ex�cutant de production dans SIB.
        
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
    def validerParamObligatoire(self,env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'�quipe de production � modifier.
        actif           : Indique si l'ex�cutant de production est actif ou non [0:Non/1:Oui].
        firme           : Nom de l'ex�cutant (firme) de production.
        adr_no          : Num�ro civique de l'adresse ou est situ� l'ex�cutant de production.
        adr_rue         : Nom de la rue de l'adresse ou est situ� l'ex�cutant de production.
        ville           : Nom de la ville de l'adresse ou est situ� l'ex�cutant de production.
        cd_prov         : Code la province de l'adresse ou est situ� l'ex�cutant de production.
        cd_postal       : Code postal de l'adresse ou est situ� l'ex�cutant de production sous la forme C#C #C#.
        cd_pays         : Code du pays de l'adresse ou est situ� l'ex�cutant de production.
        tel             : Num�ro de t�l�phone de l'ex�cutant de production sous la forme ###-###-####.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(cd_execu) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_execu')

        if actif <> "0" and actif <> "1":
            raise Exception("Param�tre obligatoire manquant: %s" %'actif')

        if (len(firme) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'firme')

        if (len(adr_no) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'adr_no')

        if (len(adr_rue) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'adr_rue')

        if (len(ville) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'ville')

        if (len(cd_prov) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_prov')

        if (len(cd_postal) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_postal')

        if (len(cd_pays) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_pays')

        if (len(tel) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'tel')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel,fax,adr_email,site_ftp,cd_acces,cd_comp,cd_decomp,format_image,no_tps,no_contact):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de modification d'un ex�cutant de production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'�quipe de production � modifier.
        actif           : Indique si l'ex�cutant de production est actif ou non [0:Non/1:Oui].
        firme           : Nom de l'ex�cutant (firme) de production.
        adr_no          : Num�ro civique de l'adresse ou est situ� l'ex�cutant de production.
        adr_rue         : Nom de la rue de l'adresse ou est situ� l'ex�cutant de production.
        ville           : Nom de la ville de l'adresse ou est situ� l'ex�cutant de production.
        cd_prov         : Code la province de l'adresse ou est situ� l'ex�cutant de production.
        cd_postal       : Code postal de l'adresse ou est situ� l'ex�cutant de production sous la forme C#C #C#.
        cd_pays         : Code du pays de l'adresse ou est situ� l'ex�cutant de production.
        tel             : Num�ro de t�l�phone de l'ex�cutant de production sous la forme ###-###-####.
        fax             : Num�ro de fax de l'ex�cutant de production sous la forme ###-###-####.
        adr_email       : Courriel de l'ex�cutant de production.
        site_ftp        : Site_ftp de l'ex�cutant de production.
        cd_acces        : Code d'acc�s du site_ftp de l'ex�cutant de production. 
        cd_comp         : Code de compression des fichiers utilis�s par l'ex�cutant de production.
        cd_decomp       : Code de d�compression des fichiers utilis�s par l'ex�cutant de production.
        format_image    : Format des images utilis� par l'ex�cutant de production.
        no_tps          : Num�ro de TPS de l'ex�cutant de production.
        no_contact      : Num�ro du contact de l'ex�cutant de production.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Valider si l'ex�cutant de production est absent
        arcpy.AddMessage("- Valider le code de l'ex�cutant de production")
        resultat = self.Sib.requeteSib("SELECT CD_EXECU FROM F604_EX WHERE CD_EXECU='" + cd_execu + "'")
        #V�rifier si l'ex�cutant de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le code de l'ex�cutant de production '" + cd_execu + "' est absent")
        
        #V�rifier si le num�ro de fax est vide
        if fax == "":
            #Ajouter la valeur NULL
            fax = "NULL"
        #si le num�ro de fax n'est pas vide
        else:
            #Ajouter les apostrophes
            fax = "'" + fax + "'"
        
        #V�rifier si le courriel est vide
        if adr_email == "":
            #Ajouter la valeur NULL
            adr_email = "NULL"
        #si le courriel n'est pas vide
        else:
            #Ajouter les apostrophes
            adr_email = "'" + adr_email + "'"
        
        #V�rifier si le site ftp est vide
        if site_ftp == "":
            #Ajouter la valeur NULL
            site_ftp = "NULL"
        #si le site ftp n'est pas vide
        else:
            #Ajouter les apostrophes
            site_ftp = "'" + site_ftp + "'"
        
        #V�rifier si le code d'acces est vide
        if cd_acces == "":
            #Ajouter la valeur NULL
            cd_acces = "NULL"
        #si le code d'acces n'est pas vide
        else:
            #Ajouter les apostrophes
            cd_acces = "'" + cd_acces + "'"
        
        #V�rifier si le code de compression est vide
        if cd_comp == "":
            #Ajouter la valeur NULL
            cd_comp = "NULL"
        #si le code de compression n'est pas vide
        else:
            #Ajouter les apostrophes
            cd_comp = "'" + cd_comp + "'"
        
        #V�rifier si le code de d�compression est vide
        if cd_decomp == "":
            #Ajouter la valeur NULL
            cd_decomp = "NULL"
        #si le code de d�compression n'est pas vide
        else:
            #Ajouter les apostrophes
            cd_decomp = "'" + cd_decomp + "'"
        
        #V�rifier si le format d'image est vide
        if format_image == "":
            #Ajouter la valeur NULL
            format_image = "NULL"
        #si le format d'image n'est pas vide
        else:
            #Ajouter les apostrophes
            format_image = "'" + format_image + "'"
        
        #V�rifier si le num�ro de TPS est vide
        if no_tps == "":
            #Ajouter la valeur NULL
            no_tps = "NULL"
        #si le num�ro de TPS n'est pas vide
        else:
            #Ajouter les apostrophes
            no_tps = "'" + no_tps + "'"
        
        #V�rifier si le num�ro de contact est vide
        if no_contact == "":
            #Ajouter la valeur NULL
            no_contact = "NULL"
        
        #Modifier l'ex�cutant de production
        arcpy.AddMessage("- Modifier l'information de l'ex�cutant de production")
        #Initialiser la commande SQL de modifification
        sql = "UPDATE F604_EX SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,UPDT_FLD=P0G03_UTL.PU_HORODATEUR"
        sql = sql + ",ACTIF=" + actif + ",TEL='" + tel + "',FAX=" + fax + ",FIRME='" + firme.replace("'","''") + "',ADR_NO='" + adr_no + "',ADR_RUE='" + adr_rue.replace("'","''") + "',VILLE='" + ville  + "'"
        sql = sql + ",CD_PROV='" + cd_prov + "',CD_POSTAL='" + cd_postal + "',CD_PAYS='" + cd_pays + "',ADR_EMAIL=" + adr_email + ",SITE_FTP=" + site_ftp + ",CD_ACCES=" + cd_acces + ",CD_COMP=" + cd_comp + ",CD_DECOMP=" + cd_decomp + ",FORMAT_IMAGE=" + format_image + ",NO_TPS=" + no_tps + ",NO_CONTACT=" + no_contact
        sql= sql + " WHERE CD_EXECU='" + cd_execu + "'"
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        cd_execu    = ""
        actif       = ""
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

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_execu = sys.argv[2].split(":")[0].upper()
        
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
                no_contact = sys.argv[20].split(':')[0]
        
        #D�finir l'objet de modification d'un ex�cutant de production dans SIB.
        oModifierExecutantProduction = ModifierExecutantProduction()
        
        #Valider les param�tres obligatoires
        oModifierExecutantProduction.validerParamObligatoire(env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel)
        
        #Ex�cuter le traitement de modification d'un ex�cutant de production dans SIB.
        oModifierExecutantProduction.executer(env,cd_execu,actif,firme,adr_no,adr_rue,ville,cd_prov,cd_postal,cd_pays,tel,fax,adr_email,site_ftp,cd_acces,cd_comp,cd_decomp,format_image,no_tps,no_contact)
    
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