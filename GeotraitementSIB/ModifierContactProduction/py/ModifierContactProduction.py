#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierContactProduction.py
# Auteur    : Michel Pothier
# Date      : 13 janvier 2015

"""
    Application qui permet de modifier d'un contact pour un exécutant de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    cd_execu        OB      Code de l'exécutant de production du contact.
                            défaut = 
    no_contact      OB      Numéro du contact de production.
                            défaut = 
    nom             OB      Nom complet (prénom et nom) du contact de production.
                            défaut = 
    langue          OB      Langue parlée du contact de production [A:Anglais/F:Français].
                            défaut = A:Anglais
    sexe            OB      Sexe du contact de production [M:Masculin/F:Féminin].
                            défaut = M:Masculin
    adr_email       OB      Courriel du contact de production.
                            défaut =
    tel             OB      Numéro de téléphone du contact de production sous la forme ###-###-####.
                            défaut =
    poste           OP      Numéro de poste du contact de production.
                            défaut =
    fax             OP      Numéro de fax du contact de production sous la forme ###-###-####.
                            défaut =
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierContactProduction.py env cd_execu no_contact nom langue sexe adr_email tel poste fax

    Exemple:
        ModifierContactProduction.py SIB_PRO CIT 1386 "Michel Pothier" F:Féminin M:Masculin mpothier@rncan.gc.ca 819-564-5600 281 819-823-6669

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierContactProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierContactProduction(object):
#*******************************************************************************************
    """
    Permet de modifier d'un contact pour un exécutant de production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification d'un contact pour un exécutant de production dans SIB.
        
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
    def validerParamObligatoire(self,env,cd_execu,no_contact,nom,langue,sexe,adr_email,tel):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'exécutant de production.
        no_contact      : Numéro du contact de production.
        nom             : Nom complet (prénom et nom) du contact de production.
        langue          : Langue parlée du contact de production [A:Anglais/F:Français].
        sexe            : Sexe du contact de production [M:Masculin/F:Féminin].
        adr_email       : Courriel du contact de production.
        tel             : Numéro de téléphone du contact de production sous la forme ###-###-####.

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

        if (len(no_contact) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'no_contact')

        if (len(nom) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom')

        if (len(langue) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'langue')

        if (len(sexe) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'sexe')

        if (len(adr_email) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'adr_email')

        if (len(tel) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tel')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,cd_execu,no_contact,nom,langue,sexe,adr_email,tel,poste,fax):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de modification d'un contact pour un exécutant de production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        cd_execu        : Code d'exécutant de production.
        no_contact      : Numéro du contact de production.
        nom             : Nom complet (prénom et nom) du contact de production.
        langue          : Langue parlée du contact de production [A:Anglais/F:Français].
        sexe            : Sexe du contact de production [M:Masculin/F:Féminin].
        adr_email       : Courriel du contact de production.
        tel             : Numéro de téléphone du contact de production sous la forme ###-###-####.
        poste           : Numéro de poste du contact de production.
        fax             : Numéro de fax du contact de production sous la forme ###-###-####.
        
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
        
        #Valider si l'exécutant de production est absent
        arcpy.AddMessage("- Valider le code de l'exécutant de production")
        resultat = self.Sib.requeteSib("SELECT CD_EXECU FROM F604_EX WHERE CD_EXECU='" + cd_execu + "'")
        #Vérifier si l'exécutant de production est présent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le code de l'exécutant de production '" + cd_execu + "' est absent")
        
        #Vérifier si le numéro de contact est numérique
        if not no_contact.isdigit():
            #Retourner une exception
            raise Exception("Le numéro de contact de production '" + no_contact + "' n'est pas numérique")
        
        #Valider si numéro de contact de production est absent
        arcpy.AddMessage("- Valider le numéro de contact de production")
        resultat = self.Sib.requeteSib("SELECT NO_CONTACT FROM F607_CO WHERE NO_CONTACT=" + no_contact + " AND CD_EXECU='" + cd_execu + "'")
        #Vérifier si l'exécutant de production est présent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le numéro de contact de production '" + no_contact + "' est absent pour l'exécutant '" + cd_execu + "'")
        
        #Valider la structure du numéro de fax
        if len(tel) <> 12 or len(tel.split("-")) <> 3:
            #Retourner une exception
            raise Exception("Le numéro de téléphone doit être sous la forme ###-###-####")
        
        #Vérifier si le numéro de poste est vide
        if poste == "":
            #Ajouter la valeur NULL
            poste = "NULL"
        #Vérifier si le numéro de poste est numérique
        else:
            #si le numéro de poste n'est pas vide
            if not poste.isdigit():
                #Retourner une exception
                raise Exception("Le numéro de poste '" + poste + "' n'est pas numérique")
            #Ajouter les apostrophes
            poste = "'" + poste + "'"
        
        #Vérifier si le numéro de fax est vide
        if fax == "":
            #Ajouter la valeur NULL
            fax = "NULL"
        #si le numéro de fax n'est pas vide
        else:
            #Valider la structure du numéro de fax
            if len(fax) <> 12 or len(fax.split("-")) <> 3:
                #Retourner une exception
                raise Exception("Le numéro de fax doit être sous la forme ###-###-####")
            #Ajouter les apostrophes
            fax = "'" + fax + "'"
        
        #Modifier le contact de production
        arcpy.AddMessage("- Modifier le contact de production")
        sql = "UPDATE F607_CO SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,NOM='" + nom + "',LANGUE='" + langue + "',SEXE='" + sexe + "',ADR_EMAIL='" + adr_email  + "',TEL='"  + tel + "'"
        sql = sql + ",POSTE=" + poste + ",FAX=" + fax + " WHERE CD_EXECU='" + cd_execu + "' AND NO_CONTACT=" + no_contact
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
        no_contact  = ""
        nom         = ""
        langue      = ""
        sexe        = ""
        adr_email   = ""
        tel         = ""
        poste       = ""
        fax         = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            cd_execu = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            no_contact = sys.argv[3].split(":")[0]
        
        if len(sys.argv) > 4:
            nom = sys.argv[4]
        
        if len(sys.argv) > 5:
            langue = sys.argv[5].upper().split(":")[0]
        
        if len(sys.argv) > 6:
            sexe = sys.argv[6].upper().split(":")[0]
        
        if len(sys.argv) > 7:
            adr_email = sys.argv[7].lower()
        
        if len(sys.argv) > 8:
            tel = sys.argv[8]
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                poste = sys.argv[9]
        
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                fax = sys.argv[10]
        
        #Définir l'objet de modification d'un contact pour un exécutant de production dans SIB.
        oModifierContactProduction = ModifierContactProduction()
        
        #Valider les paramètres obligatoires
        oModifierContactProduction.validerParamObligatoire(env,cd_execu,no_contact,nom,langue,sexe,adr_email,tel)
        
        #Exécuter le traitement de modification d'un contact pour un exécutant de production dans SIB.
        oModifierContactProduction.executer(env,cd_execu,no_contact,nom,langue,sexe,adr_email,tel,poste,fax)
    
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