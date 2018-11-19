#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : CreerLotMettreProgrammeSelectId.py
# Auteur    : Michel Pothier
# Date      : 26 janvier 2015

"""
    Application qui permet de créer un lot et mettre au programme l'identifiant de découpage présent dans un attribut
    pour chaque élément sélectionné dans un FeatureLayer de découpage.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                                défaut = SIB_PRO
    featureLayer        OB      FeatureLayer contenant les identifiants sélectionnés.
                                défaut = ""
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail.
                                défaut = DATASET_NAME
    typeProduit         OB      type de produit associé au lot.
                                défaut = ""
    typeTravail         OB      type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
                                défaut = ""
    anneeFinanciere     OB      Année financière dans laquelle les coûts de production sera débitées (format : AAAA-AA).
                                défaut = ""
    codeEquipe          OB      Code de l'équipe qui effectue le travail.
                                défaut = "AUTRE"
    codeExecutant       OB      Code du contractant à qui le contrat est octroyé.
                                défaut = "CITS"
    noContact           OB      Numéro de contact, chez le contractant, responsable du lot.
                                défaut = "4"
    typeProduction      OB      Indique le type de production : 'A:Autre', 'C:Client' et 'E:Entente'.
                                défaut = A
    normes              OB      Numéro de la normes selon laquelle le fichier sera produit.
                                défaut = ""
    catalogue           OP      Numéro de catalogue selon laquelle le fichier sera produit. 
                                défaut = ""
    fanionCollision     OB      Fanion indiquant l'action à prendre s'il y a collision entre les mises au programme.
                                0 : la mise au programme n'est pas inscrite.
                                1 : la mise au programme est inscrite même s'il y a collision.
                                Défaut = 0
    listeCodeTopo       OB      Liste des codes d'éléments topographique traités.
                                défaut = ""
    listeCollActive     OP      Liste des codes de collisions active associés à chaque code d'élément topographique spécifié.
                                défaut = ""
    noContrat           OP      Numéro de contrat.
                                défaut = ""
    noTicket            OP      Numéro de bon de commande du système E-Procurment utilisé pour les travaux à l'externe.
                                défaut = ""
    datePrevue          OP      Date prévue de la fin des travaux.
                                défaut = ""
    nbJoursDelai        OP      Nombre de jours de délai accordés à la date prévue.
                                défaut = ""
    listeNonConf        OP      Liste des numéros de non-conformité traités.
                                défaut = ""
    noteLot             OP      Note explicative pour le lot.
                                défaut = ""
    noteMAP             OP      Note explicative associée aux identifiants traités.
                                défaut = ""
    
    Paramètres de sortie:
    ---------------------
    listeNoMap   : Liste des numéros de mise au programme.
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerLotMettreProgrammeSelectId.py env featureLayer attributIdentifiant typeProduit typeTravail anneeFinanciere codeEquipe codeExecutant noContact typeProduction normes
        [catalogue] fanionCollision listeCodeTopo [listeCollActive] [datePrevue] [nbJoursDelai] [listeNonConf] [noteLot] [noteMAP]

    Exemple:
        CreerLotMettreProgrammeSelectId.py SIB_PRO DECOUPAGE DATASET_NAME BDG CORINT 2014-15 AUTRE CITS 4 A 4.02 4.02.1 1 10001,10002,10003 10001,10002,10003 # # #
        "Note pour le lot" "Note pour la MAP"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerLotMettreProgrammeSelectId.py 2139 2017-10-19 15:41:54Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerLotMettreProgrammeSelectId(object):
#*******************************************************************************************
    """
    Classe qui permet de mettre au programme les éléments sélectionnés dans un FeatureLayer
    selon l'information contenue dans un numéro de lot.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'un lot.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        #Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, featureLayer, attributIdentifiant, typeProduit, typeTravail, anneeFinanciere,
                                codeEquipe, codeExecutant, noContact, typeProduction, normes, fanionCollision, listeCodeTopo):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        featureLayer        : FeatureLayer contenant les éléments des identifiants sélectionnés.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'élément.
        typeProduit         : Type de produit associé au lot.
        typeTravail         : Type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
        anneeFinanciere     : Année financière dans laquelle les coûts de production sera débitées (format : AAAA-AA).
        codeEquipe          : Code de l'équipe qui effectue le travail.
        codeExecutant       : Code du contractant à qui le contrat a été octroyé (défaut = null).
        noContact           : Numéro de contact, chez le contractant, responsable du lot.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'.
        normes              : Numéro de la normes selon laquelle le fichier sera produit.
        fanionCollision     : Fanion indiquant l'action à prendre s'il y a collision entre les mises au programme.
        listeCodeTopo       : Liste des codes d'éléments topographique traités.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """
        
        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(featureLayer) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'featureLayer')
        
        if (len(attributIdentifiant) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'attributIdentifiant')
        
        if (len(typeProduit) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'typeProduit')
        
        if (len(typeTravail) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'typeTravail')
        
        if (len(anneeFinanciere) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'anneeFinanciere')
        
        if (len(codeEquipe) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'codeEquipe')
        
        if (len(codeExecutant) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'codeExecutant')
        
        if (len(noContact) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noContact')
        
        if (len(typeProduction) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'typeProduction')
        
        if (len(normes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'normes')
        
        if (len(fanionCollision) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'fanionCollision')
        
        if (len(listeCodeTopo) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'listeCodeTopo')
        
        return
    
    #-------------------------------------------------------------------------------------
    def definirDate(self, date, delai):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de définir la date prévue en fonction du délais fourni.
        Si on founi un délais, il est additionné à la date du jour pour calculer la date de fin prévue.
        
        Paramètres:
        -----------
        date         : Date prévue de la fin des travaux.
        delai        : Nombre de jours de délai accordés à la date prévue.
       
        Retour:
        -------
        datePrevue  : Date prévue de la fin des travaux incluant les jours de délai.
        
        """
        #Vérifier la présence d'un délai
        if delai == "":
            #Définir la date prévue sans délai
            datePrevue = date
        #Si aucun délai
        else:
            #Définir la date prévue avec délai
            delaiSec = int(delai) * 60 * 60 * 24    # nombre de jours en secondes
            datePrevue = time.strftime("%Y/%m/%d", time.localtime(time.time() + delaiSec))
        
        return datePrevue
    
    #-------------------------------------------------------------------------------------
    def definirCodeCollision(self, listeCodeTopo, listeCollActive):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de définir la liste des codes topographiques et de leurs codes de collision actives.
        
        Paramètres:
        -----------
        listeCodeTopo       : Liste des codes d'éléments topographique traités.
        listeCollActive     : Liste des codes de collisions active associés à chaque code d'élément topographique spécifié.
       
        Retour:
        -------
        listeCodeTopo       : Liste des codes d'éléments topographique traités.
        listeCollActive     : Liste des codes de collisions active associés à chaque code d'élément topographique spécifié.
        
        """
       
        #Initialisation de la liste des codes topographiques et des collisions actives
        listeCode = ""
        listeCollision = ""

        #Traiter tous les codes ou liste de codes spécifiés        
        listeCodeDesc = listeCodeTopo.split(",")
        for _codeDesc in listeCodeDesc:
            #Extraire le code de la description
            _code = (_codeDesc.replace("'","")).split(" :")

            #Vérifier si le code est absent de la liste des codes
            if _code[0] not in listeCode:
                #Ajouter le code à la liste de code
                listeCode = listeCode + _code[0] + ","
                
                #Vérifier si le code est présent dans la liste des collisions actives
                if _code[0] in listeCollActive:
                    #On désactive la collision pour le code traité
                    listeCollision = listeCollision + "1,"
                
                #Si le code est absent dans la liste des collisions actives
                else:
                    #On active la collision pour le code traité
                    listeCollision = listeCollision + "0,"
        
        #Définir la liste des codes et des collisions
        listeCodeTopo = listeCode.replace("'","")[:-1]
        listeCollActive = listeCollision[:-1]

        return listeCodeTopo, listeCollActive

    #-------------------------------------------------------------------------------------
    def validerIdentifiant(self, typeProduit):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de retourner le fanion pour indiquer si on doit valider l'identitifiant.
        
        Paramètres:
        -----------
        typeProduit     : Type de produit vérifié.
       
        Retour:
        -------
        fanionValiderIdentifiant    : Fanion pour indiquer si on doit valider l'identitifiant.
                                      0 : "SANS-DECOUPAGE"
                                      1 : "AVEC-DECOUPAGE"
        """
        
        #Vérifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE CD_PARAMETRE='DECOUPAGE' AND TY_PRODUIT='" + typeProduit + "'")

        #Indiquer s'il s'agit d'un découpage pré-définit
        if (not resultat) or (resultat[0][0] == "SANS-DECOUPAGE"):
            fanionValiderIdentifiant=0
        else:
            fanionValiderIdentifiant=1
        
        #Sortir et retourner le résultat
        return fanionValiderIdentifiant
    
    #-------------------------------------------------------------------------------------
    def mapSansEdVer(self, typeProduit):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant d'indiquer si la mise au programme se fait avec ou sans édition et version.
        
        Paramètres:
        -----------
        typeProduit     : Type de produit vérifié.
       
        Retour:
        -------
        sansEdVer       : Indique si la mise au programme est avec ou sans édition et version.getvalue
        
        """
        
        #Vérifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE CD_PARAMETRE='MAP-SANS-ED-VER' AND TY_PRODUIT='" + typeProduit + "'")

        #Définir le résultat de la requête
        if resultat:
            sansEdVer = True
        else:
            sansEdVer = False
        
        #Sortir et retourner le résultat
        return sansEdVer
    
    #-------------------------------------------------------------------------------------
    def miseAuProgramme(self, typeProduit, identifiant, datePrevue, normes, typeTravail, noLot, noGroupe, typeProduction, note, 
                        gabaritMeta, listeNosNonConf, listeElemTopo, listeCollActive, fanionCollision, 
                        fanionValiderIdentifiant, catalogue=""):
    #-------------------------------------------------------------------------------------
        """
        Cette méthode effectue une mise au programme et ajoute les travaux associés à la production d'un jeu de données pour un lot donné dans SIB.

        Paramètres:
        ---------
        typeProduit             : Nom du produit
        identifiant             : Identifiant du produit
        datePrevue              : Date à laquelle tous les travaux cédulés seront terminés
        normes                  : Normes selon laquelle le fichier sera produit
        typeProduction          : Indique le type de production : 'A', 'C' et 'E'
        note                    : Information complémentaire : 3 lignes de 80 caractères maximum
        gabaritMeta             : Code indiquant le gabarit de métadonnées à utiliser
        listeNosNonConf         : Liste des numéros de non conformités qui seront réglés par cette mise au programme (défaut NULL) (optionnel) 
        listeElemTopo           : Liste des codes d’éléments topographiques associés à cette mise au programme (défaut NULL)(optionnel) 
        typeTravail             : Type de travail à effectuer
        noLot                   : Numéro de lot associé à la mise au programme
        noGroupe                : Numéro de groupe
        listeCollActive         : Liste des valeurs à appliquer à chacun des codes d'entités topographiques pour la gestion des collisions
        fanionCollision         : Fanion indiquant l'action à prendre s'il y a collision entre les mises au programme
        fanionValiderIdentifiant: Fanion indiquant si on veut valider ou non l'identifiant selon la table dictionnaires F101
        catalogue               : Numéro du catalogue
        
        Valeurs de retour:
        -----------------
        infoMap     : Contient l'information sur la mise au programme effectuée {"noMap":noMap, "edition":edition, "version":version}

        """
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS','PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")
        
        # Appel du service de transaction Sib qui initialise l'ajout d'une nouvelle instance de produit au programme
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Mise_au_programme : " + sUsagerSib + "," + typeProduit + "," + identifiant + ",DT:" + datePrevue + ",N:" + normes + ",TP:" + typeProduction + ",Nt:" + note + ",GM:" + gabaritMeta + ",NC:" + listeNosNonConf + ",ET:" + listeElemTopo + ",CA:" + listeCollActive)
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Mise_au_programme : " + sUsagerSib + "," + typeProduit + "," + identifiant + "," + datePrevue + "," + normes + "," + typeProduction + "," + note + "," + gabaritMeta + "," + listeNosNonConf + "," + listeElemTopo + "," + listeCollActive + "," + fanionCollision + "," + fanionValiderIdentifiant)
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Mise_au_programme", cx_Oracle.STRING, [sUsagerSib, typeProduit, identifiant, datePrevue, normes, typeProduction, note, gabaritMeta, listeNosNonConf, listeElemTopo, listeCollActive, fanionCollision, fanionValiderIdentifiant])
        # Vérifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Mise_au_programme]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute un travail à la mise au programme préalablement initialisée
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Travail")
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Travail", cx_Oracle.STRING, [typeTravail, 1, catalogue])
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        # Vérifier le code de retour
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Travail]")
            raise Exception(message)
        
        #définir la zone-mémoire où est emmagasinée la valeur de la variable noMap
        noMap = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #définir la zone-mémoire où est emmagasinée la valeur de la variable edition
        edition = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #définir la zone-mémoire où est emmagasinée la valeur de la variable version 
        version = self.Sib.cursor.var(cx_Oracle.NUMBER)
        
        # Appel du service de transaction qui termine l'ajout d'un travail
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Termine")
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Termine", cx_Oracle.STRING, [noMap, edition, version])
        # Vérifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Termine]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute une instance de produit au contenu d'un lot
        #arcpy.AddMessage("- P0607_CONT.pu_Ajouter_contenu_lot")
        codeRetour = self.Sib.cursor.callfunc("P0607_CONT.pu_Ajouter_contenu_lot", cx_Oracle.STRING, [sUsagerSib, noLot, noGroupe, noMap])
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        # Vérifier le code de retour
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0607_CONT.pu_Ajouter_contenu_lot]")
            raise Exception(message)
        
        #Définir le numéro de mise au programme
        noMap = int(noMap.getvalue())
        #Vérifier si la mise au programme se fait avec édition et version
        if self.mapSansEdVer(typeProduit):
            #Définir l'édition et la version à None
            edition = -1
            version = -1
        else:
            #Extraire l'édition et la version résultante
            edition = int(edition.getvalue())
            version = int(version.getvalue())
        
        # Définir l'information à retourner sur la mise au programme
        infoMap = {"noMap":noMap, "edition":edition, "version":version}
        
        #Sortir et retourner l'information sur la mise au programme        
        return infoMap
    
    #-------------------------------------------------------------------------------------
    def CreerLot(self, typeProduit, typeTravail, anneeFinanciere, codeEquipe, etatLot, noGroupe, noCpc, codeExecutant, noContrat, noContact, noTicket, note):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un lot pour un produit donné.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        typeProduit     : type de produit associé au lot
        typeTravail     : type de travail à effetuer sur tous les identifiants du lot. Doit être prédéfini préalablement dans SIB.
        anneeFinanciere : année financière où la production a commencée (format : AAAA-AA)
        codeEquipe      : code de l'équipe qui effectue le travail
        etatLot         : état du lot [A:en préparation /C:prêt pour la production /T:terminé] 
        noGroupe        : numéro de groupe associé au numéro de lot. Il est possible de spécifier plusieurs groupes 
                          séparés par des virgules (01, 02, 03). Il est également possible d'ajouter pour chaque groupe
                          énoncé la date de réception (01+YYYY-MM-DD) ou (01+YYYY-MM-DD, 02+YYYY-MM-DD, 03+YYYY-MM-DD)
        noCpc           : (optionnel) numéro de CPC pour le contrôle des coûts (défaut = null)
        codeExecutant   : (optionnel) code du contractant à qui le contrat a été octroyé (défaut = null)
        noContrat       : (optionnel) numéro de contrat (défaut = null)
        noContact       : (optionnel) numéro de contact, chez le contractant, responsable du lot
        noTicket        : (optionnel) numéro de ticket (défaut = null)
        note            : (optionnel) note attachée au lot créer (défaut = null)
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : nombre de messages d'erreur générés par le service de transaction SIB
        messageSib      : description du message reçue du service de transaction SIB

        Valeurs de retour:
        -----------------
        noLot           -- numéro de lot créé
        """

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")  
        
        #Appel du service de transaction SIB qui initialise l'ajout d'un lot
        #arcpy.AddMessage("- Appel du service SIB : P0608_LOT.pu_Ajouter_Lot")
        codeRetour = self.Sib.cursor.callfunc("P0608_LOT.pu_Ajouter_Lot", cx_Oracle.STRING, [sUsagerSib, typeProduit, typeTravail, anneeFinanciere, codeEquipe, noCpc, codeExecutant, noContrat, noContact, noTicket, note])

        #Vérifier le succès du service SIB 
        if self.Sib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
            #Traiter tous les numéros de groupe dans le lot préalablement initialisé
            for record_groupe in noGroupe.split(","):
                list_item_record_groupe = record_groupe.split("+")
                dt_recep = None
                groupe = list_item_record_groupe[0]
                if len(list_item_record_groupe) > 1:
                    dt_recep = list_item_record_groupe[1]
                #Appel du service de transaction SIB qui ajoute un numéro de groupe dans le lot préalablement initialisé
                #arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Ajouter_Groupe")
                codeRetour = self.Sib.cursor.callfunc('P0608_lot.pu_Ajouter_Groupe', cx_Oracle.STRING, [groupe, dt_recep])

            #Vérifier le succès du service SIB 
            if self.Sib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                #appel du service de transaction SIB qui finalise l'ajout du lot et retour du numéro de lot créé
                noLot = self.Sib.cursor.var(cx_Oracle.STRING)  #définir la zone-mémoire où est emmagasinée la valeur de la variable noLot
                codeRetour = self.Sib.cursor.callfunc('P0608_lot.pu_Ajouter_Termine', cx_Oracle.STRING, [noLot])

                #Vérifier le succès du service SIB 
                if self.Sib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                    #récupération de l'étampe temporelle du lot préalablement créée
                    requete = "select updt_fld from f601_lo where no_lot ='%s'" % (noLot.getvalue())
                    #arcpy.AddMessage("  " + requete)
                    self.Sib.cursor.execute(requete)
                    etampe = self.Sib.cursor.fetchone() [0]
                    #arcpy.AddMessage("  Étampe temporelle : %s" %etampe)
                    
                    #appel du service de transaction SIB qui modifie l'état du lot préalablement créé
                    #arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Modifier_Etat_Lot")
                    codeRetour = self.Sib.cursor.callfunc('P0608_lot.pu_Modifier_Etat_Lot', cx_Oracle.STRING, [sUsagerSib, noLot, etatLot, etampe])
                    
                    #Vérifier le succès du service SIB 
                    if self.Sib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) <> 1:
                        #Extraire le nombre de message
                        nbMessSib = self.Sib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
                        count = 1
                        #Extraire tous les messages
                        message = []
                        while nbMessSib >= count:
                            #Extraire un message
                            messageSib = self.Sib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                            message.append(messageSib)
                            count += 1
                        #Retourner le message d'erreur
                        raise Exception(message)
                
                #la finalisation de l'ajout du lot n'a pas réussie
                else:
                    #Extraire le nombre de message
                    nbMessSib = self.Sib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
                    count = 1
                    #Extraire tous les messages
                    message = []
                    while nbMessSib >= count:
                        messageSib = self.Sib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                        message.append(messageSib)
                        count += 1
                    #Retourner le message d'erreur
                    raise Exception(message)
                
            #l'ajout du groupe n'a pas réussie
            else:
                #Extraire le nombre de message
                nbMessSib = self.Sib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
                count = 1
                #Extraire tous les messages
                message = []
                while nbMessSib >= count:
                    messageSib = self.Sib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                    message.append(messageSib)
                    count += 1
                #Retourner le message d'erreur
                raise Exception(message)
        
        #l'initialisation de l'ajout d'un lot n'a pas réussi
        else:
            #Extraire le nombre de message
            nbMessSib = self.Sib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
            count = 1
            #Extraire tous les messages
            message = []
            while nbMessSib >= count:
                messageSib = self.Sib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                message.append(messageSib)
                count += 1
            raise Exception(message)  
        
        #Sortir et retourner le numéro de lot
        return noLot.getvalue()

    #-------------------------------------------------------------------------------------
    def executer(self, env, featureLayer, attributIdentifiant, typeProduit, typeTravail, anneeFinanciere, codeEquipe, codeExecutant, noContact, typeProduction,
                 normes, catalogue, fanionCollision, listeCodeTopo, listeCollActive, noContrat, noTicket,
                 datePrevue, nbJoursDelai, listeNonConf, noteLot, noteMAP):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de mise au programme des éléments d'identifiant de découpage sélectionnés.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        featureLayer        : FeatureLayer contenant les éléments des identifiants sélectionnés.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'élément.
        typeProduit         : Type de produit associé au lot.
        typeTravail         : Type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
        anneeFinanciere     : Année financière dans laquelle les coûts de production sera débitées (format : AAAA-AA).
        codeEquipe          : Code de l'équipe qui effectue le travail.
        codeExecutant       : Code du contractant à qui le contrat a été octroyé (défaut = null).
        noContact           : Numéro de contact, chez le contractant, responsable du lot.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'.
        normes              : Numéro de la normes selon laquelle le fichier sera produit.
        catalogue           : Numéro de catalogue selon laquelle le fichier sera produit. 
        fanionCollision     : Fanion indiquant l'action à prendre s'il y a collision entre les mises au programme.
        listeCodeTopo       : Liste des codes d'éléments topographique traités.
        listeCollActive     : Liste des codes de collisions active associés à chaque code d'élément topographique spécifié.
        noContrat           : Numéro de contrat.
        noTicket            : Numéro de bon de commande du système E-Procurment utilisé pour les travaux à l'externe.
        datePrevue          : Date prévue de la fin des travaux.
        nbJoursDelai        : Nombre de jours de délai accordés à la date prévue.
        listeNonConf        : Liste des numéros de non-conformité traités.
        noteLot             : Note explicative associée aux lots.
        noteMAP             : Note explicative associée aux identifiants mise au programme.
        
        Variables:
        ----------
        self.CompteSib      : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib                : Objet utilitaire pour traiter des services SIB.
        sUsagerSib          : Nom de l'usager SIB.
        code_retour         : Code de retour d'un service SIB.
        nbMessSib           : Nombre de messages d'erreur générés par le service de transaction SIB
        messageSib          : Description du message reçue du service de transaction SIB
        noLot               : Numréro de lot dans lequel la mise au programme doit être ajouté.
        noGroupe            : Numréro de groupe dans lequel la mise au programme doit être ajouté.

        Valeurs de retour:
        -----------------
        listeMap        : Liste des numéros des mises au programme.
        listeEd         : Liste des numéros d'édition.
        listeVer        : Liste des numéros de version.
        listeId         : Liste des identifiants de découpage.
        
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Définir les valeurs par défaut
        gabaritMeta = ""
        etatLot     = "C"
        noGroupe    = "01"
        noCpc       = ""
        
        #Définir la date prévue en fonction du délai        
        arcpy.AddMessage("- Définir la date prévue en fonction du délai")
        datePrevue = self.definirDate(datePrevue, nbJoursDelai)
        arcpy.AddMessage("  datePrevue=" + datePrevue)
        
        #Extraction de la liste des codes topographiques et des collisions actives
        arcpy.AddMessage("- Définir les codes de collisions")
        listeCodeTopo, listeCollActive = self.definirCodeCollision(listeCodeTopo, listeCollActive)
        arcpy.AddMessage("  listeCodeTopo=" + listeCodeTopo)
        arcpy.AddMessage("  listeCollActive=" + listeCollActive)
        
        #Vérifier si l'identifiant doit être validé
        arcpy.AddMessage("- Vérifier si l'identifiant de découpage doit être validé")
        fanionValiderIdentifiant = self.validerIdentifiant(typeProduit)
        arcpy.AddMessage("  fanionValiderIdentifiant=" + str(fanionValiderIdentifiant))
        
        #Initialiser les listes
        listeNoLot = []
        listeMap = []
        listeEd = []
        listeVer = []
        listeId = []
        
        #Traiter tous les éléments d'identifiant de découpage sélectionnés
        arcpy.AddMessage("- Traiter tous les éléments du FeatureLayer : " + featureLayer)
        #Créer le curseur pour la recherche
        cursor = arcpy.SearchCursor(featureLayer)
        #Extraire le premier élément
        row = cursor.next()
        #traiter tant qu'il y aura des éléments
        while row:
            #Définir l'identifiant traité
            identifiant = str(row.getValue(attributIdentifiant))
            
            #Ajouter l'identifiant dans la liste
            listeId.append(identifiant)
            
            #Exécuter le traitement de création d'un numéro de lot.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Création d'un lot dans SIB ...")
            noLot = self.CreerLot(typeProduit, typeTravail, anneeFinanciere, codeEquipe, etatLot, noGroupe, noCpc, codeExecutant,
                                  noContrat, noContact, noTicket, noteLot)
            
            #Affichage des informations du lot
            arcpy.AddMessage("  noLot=%s" %str(noLot))
            listeNoLot.append(noLot)
            
            #Mettre au programme un identifiant
            arcpy.AddMessage("- Mise au programme dans SIB : %s ..." %identifiant)
            infoMap = self.miseAuProgramme(typeProduit, identifiant, datePrevue, normes, typeTravail, noLot, noGroupe, typeProduction, noteMAP,
                                           gabaritMeta, listeNonConf, listeCodeTopo, listeCollActive, fanionCollision, fanionValiderIdentifiant, catalogue)
            
            #Affichage des informations de la MAP
            arcpy.AddMessage("  infoMap=%s" %str(infoMap))
            listeMap.append(infoMap["noMap"])
            listeEd.append(infoMap["edition"])
            listeVer.append(infoMap["version"])
            
            #extraire le prochain élément
            row = cursor.next()
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir et retourner la liste des numéro de lot, de mise au programme, des éditions, des versions et des identifiants.
        return listeNoLot, listeMap, listeEd, listeVer, listeId

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env                 = "SIB_PRO"
        featureLayer        = ""
        attributIdentifiant = "DATASET_NAME"
        typeProduit         = ""
        typeTravail         = ""
        anneeFinanciere     = ""
        codeEquipe          = "AUTRE"
        codeExecutant       = "CITS"
        noContact           = "4"
        typeProduction      = "A"
        normes              = ""
        catalogue           = ""
        fanionCollision     = "0"
        listeCodeTopo       = ""
        listeCollActive     = ""
        noContrat           = ""
        noTicket            = ""
        datePrevue          = ""
        nbJoursDelai        = ""
        listeNonConf        = ""
        noteLot             = ""
        noteMAP             = ""
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            featureLayer = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            attributIdentifiant = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            typeProduit = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            typeTravail = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            anneeFinanciere = sys.argv[6]
        
        if len(sys.argv) > 7:
            codeEquipe = sys.argv[7].upper()
         
        if len(sys.argv) > 8:
            codeExecutant = sys.argv[8].upper()
        
        if len(sys.argv) > 9:
            noContact = sys.argv[9].split(":")[0]
        
        if len(sys.argv) > 10:
            typeProduction = sys.argv[10].split(" ")[0]
        
        if len(sys.argv) > 11:
            normes = sys.argv[11]
        
        if len(sys.argv) > 12:
            if sys.argv[12] <> "#":
                catalogue = sys.argv[12]
        
        if len(sys.argv) > 13:
            fanionCollision = sys.argv[13]
        
        if len(sys.argv) > 14:
            listeCodeTopo = sys.argv[14].replace(";",",")
        
        if len(sys.argv) > 15:
            if sys.argv[15] <> "#":
                listeCollActive = sys.argv[15].replace(";",",")
        
        if len(sys.argv) > 16:
            if sys.argv[16] <> "#":
                noContrat = sys.argv[16]
        
        if len(sys.argv) > 17:
            if sys.argv[17] <> "#":
                noTicket = sys.argv[17]
        
        if len(sys.argv) > 18:
            if sys.argv[18] <> "#":
                datePrevue = sys.argv[18]
        
        if len(sys.argv) > 19:
            if sys.argv[19] <> "#":
                nbJoursDelai = sys.argv[19]
        
        if len(sys.argv) > 20:
            if sys.argv[20] <> "#":
                listeNonConf = sys.argv[20].replace(";",",")
        
        if len(sys.argv) > 21:
            if sys.argv[21] <> "#":
                noteLot = sys.argv[21]
        
        if len(sys.argv) > 22:
            if sys.argv[22] <> "#":
                noteMAP = sys.argv[22]
        
        #Définir l'objet de création de lot et de mise au programme.
        oCreerLotMettreProgrammeSelectId = CreerLotMettreProgrammeSelectId()
        
        #Valider les paramètres obligatoires
        oCreerLotMettreProgrammeSelectId.validerParamObligatoire(env, featureLayer, attributIdentifiant, typeProduit, typeTravail, anneeFinanciere,
                                         codeEquipe, codeExecutant, noContact, typeProduction, normes, fanionCollision, listeCodeTopo)
        
        #Exécuter le traitement de création de lot et de mise au programme.
        listeNoLot, listeMap, listeEd, listeVer, listeId = oCreerLotMettreProgrammeSelectId.executer(env, featureLayer, attributIdentifiant,
                                               typeProduit,typeTravail,anneeFinanciere,codeEquipe,codeExecutant,noContact,typeProduction,
                                               normes,catalogue,fanionCollision,listeCodeTopo,listeCollActive,noContrat,noTicket,
                                               datePrevue, nbJoursDelai, listeNonConf, noteLot, noteMAP)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Afficher les listes
        arcpy.AddMessage("  listeNoLot=")
        arcpy.AddMessage("  listeMap=")
        arcpy.AddMessage("  listeEd=")
        arcpy.AddMessage("  listeVer=")
        arcpy.AddMessage("  listeId=")
        arcpy.SetParameterAsText(22, "")
        arcpy.SetParameterAsText(23, "")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("- Succès du traitement")
    #Afficher les numéros de mise au programme
    arcpy.AddMessage("  listeNoLot=%s" %str(listeNoLot))
    arcpy.AddMessage("  listeMap=%s" %str(listeMap))
    arcpy.AddMessage("  listeEd=%s" %str(listeEd))
    arcpy.AddMessage("  listeVer=%s" %str(listeVer))
    arcpy.AddMessage("  listeId=%s" %str(listeId))
    arcpy.SetParameterAsText(22, listeNoLot)
    arcpy.SetParameterAsText(23, listeMap)
    #Sortir sans code d'erreur
    sys.exit(0)