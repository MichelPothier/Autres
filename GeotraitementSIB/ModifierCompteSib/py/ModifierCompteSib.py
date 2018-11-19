#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierCompteSib.py
# Auteur    : Michel Pothier
# Date      : 24 octobre 2014

"""
    Application qui permet de modifier toute l'information d'un compte existant dans SIB avec ses groupes de privilèges.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                            défaut = SIB_PRO
    cd_user         OB      Code de l'usager SIB
                            défaut = <Valeur contenue dans la variable d'environnement USERNAME>
    motPasse        OP      Mot de passe de l'usager SIB
                            défaut = 
    prenom          OP      Prénom de l'usager SIB
                            défaut = <Valeur contenue dans SIB>
    nom             OP      Nom de l'usager SIB
                            défaut = <Valeur contenue dans SIB>
    actif           OP      Indique si le compte est actif [1:Vrai, 0:Faux]
                            défaut = <Valeur contenue dans SIB>
    langue          OP      Langue pricipale de l'usager SIB [F:Français,A:Anglais]
                            défaut = <Valeur contenue dans SIB>
    adr_email       OP      Adresse courriel de l'usager SIB
                            défaut = <Valeur contenue dans SIB>
    cd_user_ab      OP      Code de l'usager abrégé SIB
                            défaut = <Valeur contenue dans SIB>
    cd_user_grp     OP      Code de l'usager SIB utilisé pour extraire les groupes de privilèges
                            défaut = <Valeur contenue dans la variable d'environnement USERNAME>
    listeCdGrp      OP      Liste des groupes de privilèges accordés à l'usager SIB
                            Défaut = <Valeurs contenues dans SIB pour l'usager spécifié dans 'cd_user_grp'>
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierCompteSib.py env cd_user motPasse prenom nom actif langue adr_email cd_user_ab cd_user_grp listeCdGrp

    Exemple:
        ModifierCompteSib.py SIB_PRO MPOTHIER MIC3POT Michel Pothier 1 F mpothier@rncan.gc.ca F MPO LOUELLET MENU,PROD,INTERACT

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierCompteSib.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierCompteSib(object):
#*******************************************************************************************
    """
    Permet de modifier un compte existant dans SIB avec ses groupes de privilèges.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification d'un compte existant dans SIB avec ses groupes de privilèges.
        
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
    def validerParamObligatoire(self, env, cd_user):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        cd_user         : Code de l'usager déterminé à partir du prénom et du nom lorsque spécifié

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(cd_user) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_user')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, cd_user, motPasse, prenom, nom, actif, langue, adr_email, cd_user_ab, cd_user_grp, listeCdGrp):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de modification de l'information d'un compte existant dans SIB avec ses groupes de privilèges.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        cd_user         : Code de l'usager déterminé à partir du prénom et du nom lorsque spécifié
        motPasse        : Mot de passe de l'usager
        prenom          : Prénom de l'usager
        nom             : Nom de l'usager
        actif           : Indique si le compte est actif (1:Vrai, 0:Faux)
        langue          : Langue pricipale de l'usager
        adr_email       : Adresse courriel de l'usager déterminé à partir du code de l'usager
        cd_user_ab      : Code de l'usager abrégé déterminé à partir du prénom et du nom lorsque spécifié
        cd_user_grp     : Code de l'usager SIB utilisé pour extraire les groupes de privilèges
        listeCdGrp      : Liste des groupes de privilèges accordés à l'usager 
        
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
        
        #Vérifier si le code de l'usager est présent
        arcpy.AddMessage("- Valider le code de l'usagé")
        if len(self.Sib.requeteSib("SELECT CD_USER FROM F005_US WHERE CD_USER='" + cd_user + "'")) == 0:
            #Envoyer une exception
            raise Exception("Le code de l'usager n'existe pas : %s" %cd_user)
        
        #Vérifier le mot de passe
        update = False
        sql_motPasse = ""
        if len(motPasse) > 0:
            #Encripter le mot de passe
            arcpy.AddMessage("- Encripter le mot de passe de l'usager")
            motPasseEncrypter = self.CompteSib.EncrypterMotPasse(motPasse.upper())
            sql_motPasse = ",M_PASSE='" + motPasseEncrypter + "'"
            arcpy.AddMessage("  Mot de passe encrypté : " + motPasseEncrypter)
            update = True
        
        #Vérifier le prénom de l'usager
        sql_prenom = ""
        if len(prenom) > 0:
            sql_prenom = ",PRENOM='" + prenom + "'"
            update = True
        
        #Vérifier le nom de l'usager
        sql_nom = ""
        if len(nom) > 0:
            sql_nom = ",NOM='" + nom + "'"
            update = True
        
        #Vérifier si l'état du compte est valide
        sql_actif = ""
        if len(actif) > 0:
            arcpy.AddMessage("- Valider l'état (ACTIF) du compte")
            if actif not in ['1','0']:
                #Envoyer une exception
                raise Exception("L'état du compte est invalide : %s" %actif)
            sql_actif = ",ACTIF=" + actif
            update = True
        
        #Vérifier si la langue parlée est valide
        sql_langue = ""
        if len(langue) > 0:
            arcpy.AddMessage("- Valider la langue parlée")
            if langue not in ['F','A']:
                #Envoyer une exception
                raise Exception("La langue parlée est invalide : %s" %langue)
            sql_langue= ",LANGUE='" + langue + "'"
            update = True
        
        #Vérifier l'adresse courriel
        sql_adr_email = ""
        if len(adr_email) > 0:
            sql_adr_email = ",ADR_EMAIL='" + adr_email + "'"
            update = True
        
        #Vérifier si le code de l'usager abrégé est déjà présent
        sql_cd_user_ab = ""
        if len(cd_user_ab) > 0:
            arcpy.AddMessage("- Valider le code de l'usagé abrégé")
            if self.Sib.requeteSib("SELECT CD_USER FROM F005_US WHERE CD_USER_AB='" + cd_user_ab + "' AND CD_USER <> '" + cd_user + "'"):
                #Envoyer une exception
                raise Exception("Le code de l'usager abrégé est déjà utilisé : %s" %cd_user_ab)
            sql_cd_user_ab = ",CD_USER_AB='" + cd_user_ab + "'"
            update = True
        
        #Vérifier si une modification a eu lieu
        if update:
            #Modifier l'information du compte de l'usager
            arcpy.AddMessage("- Modifier l'information du compte SIB de l'usager")
            sql = "UPDATE F005_US SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='"+ sUsagerSib + "',DT_M=SYSDATE" + sql_motPasse + sql_prenom + sql_nom + sql_actif + sql_langue + sql_adr_email + sql_cd_user_ab + " WHERE CD_USER='" + cd_user + "'"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Vérifier si le code de l'usager de groupe est présent et qu'il n'y a pas de groupes de privil`ges spécifiés
        if (cd_user_grp) > 0 and len(listeCdGrp) == 0:
            #Extraire les groupes de privilèges de l'usager de groupe
            arcpy.AddMessage("- Extraire les groupes de privilèges de l'usager spécifié : " + cd_user_grp)
            resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + cd_user_grp + "'")
            listeGroupeActuel = []
            #Construire la liste des groupes actuels de l'usager
            for grp in resultat:
                #Ajouter le groupe à la liste
                listeGroupeActuel.append(grp[0])
            listeCdGrp = str(listeGroupeActuel)[1:-1].replace("'","").replace(" ","")
            arcpy.AddMessage("  listeCdGrp=" + listeCdGrp)
            
        #Extraire la liste des groupes de privilège permis
        if len(listeCdGrp) > 0:
            arcpy.AddMessage("- Extraire la liste des codes des groupes de privilèges permis")
            resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F006_GR")
            #Initialiser le groupe
            listeGroupePermis = []
            #Construire la liste des groupes permis
            for grp in resultat:
                #Ajouter le groupe à la liste
                listeGroupePermis.append(grp[0])

            arcpy.AddMessage("- Extraire la liste des codes des groupes de privilèges actuels de l'usager")
            resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + cd_user + "'")
            #Initialiser le groupe
            listeGroupeActuel = []
            arcpy.AddMessage("- Détruire les groupes de privilège de l'usager en trop")
            #Construire la liste des groupes actuels de l'usager et Détruire les groupes de privilège de l'usager en trop
            for grp in resultat:
                #Ajouter le groupe à la liste
                listeGroupeActuel.append(grp[0])
                #Vérifier si le groupe de privilège de l'usager doit être détruit
                if grp[0] not in listeCdGrp:
                    #Détruire un groupe de privilège à l'usager
                    sql = "DELETE FROM F007_UG WHERE CD_USER='" + cd_user + "' AND CD_GRP='" + grp[0] + "'" 
                    arcpy.AddMessage(sql)
                    self.Sib.execute(sql)
                    update = True

            #Ajouter les groupes de privilège de l'usager manquant
            arcpy.AddMessage("- Ajouter les groupes de privilège de l'usager manquants")
            #Traiter la liste des groupes de privilège de l'usager
            for grpNom in listeCdGrp.split(","):
                #Extraire le groupe des noms
                grp = grpNom.split(":")[0]
                #Vérifier si le groupe de privilège de l'usager est valide
                if grp not in listeGroupePermis:
                    #Envoyer une exception
                    raise Exception("Le groupe de privilège de l'usager est invalide : " + grp + " " + str(listeGroupePermis))
                #Vérifier si le groupe de privilège de l'usager est valide
                if grp not in listeGroupeActuel:
                    #Ajouter un groupe de privilège à l'usager
                    sql = "INSERT INTO F007_UG VALUES ('"+ sUsagerSib + "',SYSDATE,SYSDATE,'" + cd_user + "','" + grp + "',P0G03_UTL.PU_HORODATEUR)"
                    arcpy.AddMessage(sql)
                    self.Sib.execute(sql)
                    update = True
        
        #Vérifier si une modification a eu lieu
        if update:
            #Accepter les modifications
            arcpy.AddMessage("- Accepter les modifications")
            sql = "COMMIT"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        else:
            #Accepter les modifications
            arcpy.AddWarning("- Acune modification effectuée")
        
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
        cd_user     = ""
        motPasse    = ""
        prenom      = ""
        nom         = ""
        actif       = ""
        langue      = ""
        adr_email   = ""
        cd_user_ab  = ""
        cd_user_grp = ""
        listeCdGrp  = ""

        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            cd_user = sys.argv[2].upper()

        if len(sys.argv) > 3:
            if sys.argv[3] <> "#":
                motPasse = sys.argv[3]

        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                prenom = sys.argv[4]

        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                nom = sys.argv[5]

        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                actif = sys.argv[6].upper()

        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                langue = sys.argv[7].upper()

        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                adr_email = sys.argv[8].lower()
                
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                cd_user_ab = sys.argv[9].upper()
                
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                cd_user_grp = sys.argv[10].upper()

        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                listeCdGrp = sys.argv[11].upper().replace(";",",").replace("'","")
        
        #Définir l'objet de modification d'un compte existant dans SIB pour un usager.
        oModifierCompteSib = ModifierCompteSib()
        
        #Valider les paramètres obligatoires
        oModifierCompteSib.validerParamObligatoire(env, cd_user)
        
        #Exécuter le traitement de modification de l'information d'un compte existant dans SIB pour un usager.
        oModifierCompteSib.executer(env, cd_user, motPasse, prenom, nom, actif, langue, adr_email, cd_user_ab, cd_user_grp, listeCdGrp)
    
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