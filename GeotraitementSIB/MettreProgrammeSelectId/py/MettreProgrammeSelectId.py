#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : MettreProgrammeSelectId.py
# Auteur    : Michel Pothier
# Date      : 21 octobre 2014

"""
    Application qui permet de mettre au programme les éléments sélectionnés dans un FeatureLayer.
    Le nom de l'identifiant est présent dans l'attribut d'identifiant spécifié du FeatureLayer.
    Le numéro de lot contient plusieurs informations comme le type de produit et le type de travail.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    featureLayer        OB      FeatureLayer contenant les identifiants sélectionnés
                                défaut = ""
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
                                défaut = DATASET_NAME
    noLot               OB      Numéro du lot dans lequel on doit ajouter la mise au programme.
                                défaut = aucun
    noGroupe            OB      Numéro de groupe dans lequel on doit ajouter la mise au programme.
                                défaut = 1
    typeProduction      OB      Indique le type de production : 'A:Autre', 'C:Contrat' et 'E:Entente'.
                                défaut = A
    normes              OB      Numéro de la normes selon laquelle le fichier sera produit
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
    datePrevue          OP      Date prévue de la fin des travaux
                                défaut = ""
    nbJoursDelai        OP      Nombre de jours de délai accordés à la date prévue
                                défaut = ""
    listeNonConf        OP      Liste des numéros de non-conformité traités.
                                défaut = ""
    note                OP      Note explicative associée aux identifiants traités.
                                défaut = ""
    
    Paramètres de sortie:
    ---------------------
    listeNoMap   : Liste des numéros de mise au programme.
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        MettreProgrammeSelectId.py env featureLayer attributIdentifiant noLot noGroupe typeProduction normes
        [catalogue] fanionCollision listeCodeTopo [listeCollActive] [datePrevue] [nbJoursDelai] [listeNonConf] [note]

    Exemple:
        MettreProgrammeSelectId.py SIB_PRO DECOUPAGE DATASET_NAME 088566 01 A 4.02 4.02.1 1 10001,10002,10003 0,1,1 # # # "Note pour le lot"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: MettreProgrammeSelectId.py 2144 2017-10-19 15:43:08Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class MettreProgrammeSelectId:
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
        
        # Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, featureLayer, attributIdentifiant, noLot, noGroupe,
                                typeProduction, fanionCollision, normes):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        featureLayer        : FeatureLayer contenant les éléments des identifiants sélectionnés.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'élément.
        noLot               : Numréro de lot dans lequel la mise au programme doit être ajouté.
        noGroupe            : Numréro de groupe dans lequel la mise au programme doit être ajouté.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'
        fanionCollision     : Fanion indiquant l'action à prendre s'il y a collision entre les mises au programme.
        normes              : Numéro de la normes selon laquelle le fichier sera produit.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(featureLayer) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'featureLayer')
        
        if (len(attributIdentifiant) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'attributIdentifiant')
        
        if (len(noLot) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'noLot')
        
        if (len(noGroupe) <> 2):
            raise Exception("La valeur de GROUPE fournie est invalide : %s. Cette valeur doit être composée de 2 chiffres." %'noGroupe')
        
        if (len(typeProduction) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'typeProduction')
        
        if (len(fanionCollision) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'fanionCollision')
        
        if (len(normes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'normes')

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
    def extraireInfoLot(self, noLot):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant d'extraire l'information d'un lot.
        
        Paramètres:
        -----------
        noLot               : Numéro de lot dans lequel la mise au programme doit être ajouté.
       
        Retour:
        -------
        typeProduit         : Nom du produit
        typeTravail         : Type de travail à effectuer

        """
        
        #Vérifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT  TY_PRODUIT, TY_TRAV FROM F601_LO WHERE NO_LOT='" + noLot + "'")

        #Si un résultat est présent
        if resultat:
            #Définir le type de produit
            typeProduit = resultat[0][0]
            #Définir le type de travail
            typeTravail = resultat[0][1]
        #Si aucun résultat
        else:
            #Retourner une exception
            raise Exception("Numéro de lot invalide : " + noLot)
        
        #Sortir et retourner le résultat
        return typeProduit, typeTravail
    
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
    def validerIdentifiantLot(self, featureLayer, attributIdentifiant, noLot):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de retourner les identifiants déjà présent dans le lot.
        
        Paramètres:
        -----------
        featureLayer        : FeatureLayer contenant les éléments des identifiants sélectionnés.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'élément.
        noLot               : Numréro de lot dans lequel la mise au programme doit être ajouté.
       
        Retour:
        -------
        listeIdentifiant    : Liste des identifiants déjà présents dans le lot.

        """
        
        #Initialiser la liste des identifiants déjà présents dans le lot.
        listeIdentifiant = ""

        #Traiter tous les éléments d'identifiant de découpage sélectionnés
        arcpy.AddMessage("- Valider la présence des identifiants dans le lot ")
        #Créer le curseur pour la recherche
        cursor = arcpy.SearchCursor(featureLayer)
        #Extraire le premier élément
        row = cursor.next()
        #traiter tant qu'il y aura des éléments
        while row:
            #Définir l'identifiant traité
            identifiant = str(row.getValue(attributIdentifiant))
        
            #Vérifier si l'identifiant est déjà dans le lot
            sql = "SELECT F502_PS.IDENTIFIANT,F502_PS.NO_MAP FROM F502_PS, F503_TR WHERE IDENTIFIANT='" + identifiant + "' AND NO_LOT='" + noLot + "' AND F502_PS.NO_MAP=F503_TR.NO_MAP"
            resultat = self.Sib.requeteSib(sql)
            if resultat:
                listeIdentifiant = listeIdentifiant + "/" + identifiant
            
            #extraire le prochain élément
            row = cursor.next()
        
        #Vérifier si des identifiants sont déjà présents dans le lot
        if len(listeIdentifiant) > 0:
            #Retourner une exception
            raise Exception("Les identifiants suivants sont déja dans le lot : " + listeIdentifiant)

        #Sortir et retourner le résultat
        return 
    
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
        
        # Appel du service de transaction Sib qui initialise l'ajout d'une nouvelle instance de produit au programme
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Mise_au_programme", cx_Oracle.STRING, [sUsagerSib, typeProduit, identifiant, datePrevue, normes, typeProduction, note, gabaritMeta, listeNosNonConf, listeElemTopo, listeCollActive, fanionCollision, fanionValiderIdentifiant])
        # Vérifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Mise_au_programme]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute un travail à la mise au programme préalablement initialisée
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
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Termine", cx_Oracle.STRING, [noMap, edition, version])
        # Vérifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Termine]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute une instance de produit au contenu d'un lot
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
    def executer(self, env, featureLayer, attributIdentifiant, noLot, noGroupe, typeProduction, normes, catalogue,
                 fanionCollision, listeCodeTopo, listeCollActive,datePrevue, nbJoursDelai, listeNonConf, note):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de mise au programme des éléments d'identifiant de découpage sélectionnés.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        featureLayer        : FeatureLayer contenant les éléments des identifiants sélectionnés.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'élément.
        noLot               : Numréro de lot dans lequel la mise au programme doit être ajouté.
        noGroupe            : Numréro de groupe dans lequel la mise au programme doit être ajouté.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'
        normes              : Numéro de la normes selon laquelle le fichier sera produit
        catalogue           : Numéro de catalogue selon laquelle le fichier sera produit. 
        fanionCollision     : Fanion indiquant l'action à prendre s'il y a collision entre les mises au programme.
        listeCodeTopo       : Liste des codes d'éléments topographique traités.
        listeCollActive     : Liste des codes de collisions active associés à chaque code d'élément topographique spécifié.
        datePrevue          : Date prévue de la fin des travaux
        nbJoursDelai        : Nombre de jours de délai accordés à la date prévue
        listeNonConf        : Liste des numéros de non-conformité traités.
        note                : Note explicative associée aux identifiants traités.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : nombre de messages d'erreur générés par le service de transaction SIB
        messageSib      : description du message reçue du service de transaction SIB

        Valeurs de retour:
        -----------------
        listeMap        : Liste des numéros des mises au programme.
        listeEd         : Liste des numéros d'édition.
        listeVer        : Liste des numéros de version.
        listeId         : Liste des identifiants de découpage.
        
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
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
        
        #Valider si les identifiants sont déjà présents dans le lot
        self.validerIdentifiantLot(featureLayer, attributIdentifiant, noLot)
        
        #Définir la date prévue en fonction du délai        
        arcpy.AddMessage("- Définir la date prévue en fonction du délai")
        datePrevue = self.definirDate(datePrevue, nbJoursDelai)
        arcpy.AddMessage("  datePrevue=" + datePrevue)
        
        #Définir le gabarit de métadonnées à vide car ilo n'est plus utilisé
        gabaritMeta = ""
        
        #Extraction de la liste des codes topographiques et des collisions actives
        arcpy.AddMessage("- Définir les codes de collisions")
        listeCodeTopo, listeCollActive = self.definirCodeCollision(listeCodeTopo, listeCollActive)
        arcpy.AddMessage("  listeCodeTopo=" + listeCodeTopo)
        arcpy.AddMessage("  listeCollActive=" + listeCollActive)
        
        #Extraire le type de produit et le type de travail à partir du numéro de lot        
        arcpy.AddMessage("- Extraire les information du lot")
        typeProduit, typeTravail = self.extraireInfoLot(noLot)
        arcpy.AddMessage("  typeProduit=" + typeProduit)
        arcpy.AddMessage("  typeTravail=" + typeTravail)
        
        #Vérifier si l'identifiant doit être validé
        arcpy.AddMessage("- Vérifier si l'identifiant de découpage doit être validé")
        fanionValiderIdentifiant = self.validerIdentifiant(typeProduit)
        arcpy.AddMessage("  fanionValiderIdentifiant=" + str(fanionValiderIdentifiant))
        
        #Initialiser les listes
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
            
            #Mettre au programme un identifiant
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Mise au programme dans SIB : %s ..." %identifiant)
            infoMap = self.miseAuProgramme( typeProduit, 
                                            identifiant, 
                                            datePrevue,
                                            normes, 
                                            typeTravail, 
                                            noLot, 
                                            noGroupe, 
                                            typeProduction, 
                                            note, 
                                            gabaritMeta, 
                                            listeNonConf, 
                                            listeCodeTopo,
                                            listeCollActive, 
                                            fanionCollision, 
                                            fanionValiderIdentifiant,
                                            catalogue
                                            )
            
            #Affichage des informations de la MAP
            arcpy.AddMessage("  infoMap=%s" %str(infoMap))
            listeMap.append(infoMap["noMap"])
            listeEd.append(infoMap["edition"])
            listeVer.append(infoMap["version"])
            
            #extraire le prochain élément
            row = cursor.next()
        
        # Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB   
        
        #Sortir et retourner la liste des numéro de mise au programme, des éditions, des versions et des identifiants.
        return listeMap, listeEd, listeVer, listeId

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
        noLot               = ""
        noGroupe            = "01"
        typeProduction      = "A"
        normes              = "4.0.2"
        catalogue           = ""
        fanionCollision     = "0"
        listeCodeTopo       = ""
        listeCollActive     = ""
        datePrevue          = ""
        nbJoursDelai        = ""
        listeNonConf        = ""
        note                = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
            
        if len(sys.argv) > 2:
            featureLayer = sys.argv[2].upper()
            
        if len(sys.argv) > 3:
            attributIdentifiant = sys.argv[3].upper()
            
        if len(sys.argv) > 4:
            noLot = sys.argv[4].split(" ")[0]
            
        if len(sys.argv) > 5:
            noGroupe = sys.argv[5]
            
        if len(sys.argv) > 6:
            typeProduction = sys.argv[6].split(" ")[0]
            
        if len(sys.argv) > 7:
            normes = sys.argv[7]
            
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                catalogue = sys.argv[8]
                
        if len(sys.argv) > 9:
            fanionCollision = sys.argv[9]
            
        if len(sys.argv) > 10:
            listeCodeTopo = sys.argv[10].replace(";",",")
            
        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                listeCollActive = sys.argv[11].replace(";",",")
                
        if len(sys.argv) > 12:
            if sys.argv[12] <> "#":
                datePrevue = sys.argv[12]
                
        if len(sys.argv) > 13:
            if sys.argv[13] <> "#":
                nbJoursDelai = sys.argv[13]
                
        if len(sys.argv) > 14:
            if sys.argv[14] <> "#":
                listeNonConf = sys.argv[14].replace(";",",")
                
        if len(sys.argv) > 15:
            if sys.argv[15] <> "#":
                note = sys.argv[15]
        
        # Définir l'objet de mise au programme.
        oMettreProgrammeSelectId = MettreProgrammeSelectId()
        
        #Valider les paramètres obligatoires
        oMettreProgrammeSelectId.validerParamObligatoire(featureLayer, attributIdentifiant, noLot, noGroupe, typeProduction, fanionCollision, normes)
        
        # Exécuter le traitement de mise au programme.
        listeMap, listeEd, listeVer, listeId = oMettreProgrammeSelectId.executer(env, featureLayer, attributIdentifiant, noLot, noGroupe, typeProduction,
                                               normes, catalogue,fanionCollision, listeCodeTopo, listeCollActive,
                                               datePrevue, nbJoursDelai, listeNonConf, note)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Afficher les listes
        arcpy.AddMessage("  listeMap=")
        arcpy.AddMessage("  listeEd=")
        arcpy.AddMessage("  listeVer=")
        arcpy.AddMessage("  listeId=")
        arcpy.SetParameterAsText(15, "")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("- Succès du traitement")
    #Afficher les numéros de mise au programme
    arcpy.AddMessage("  listeMap=%s" %str(listeMap))
    arcpy.AddMessage("  listeEd=%s" %str(listeEd))
    arcpy.AddMessage("  listeVer=%s" %str(listeVer))
    arcpy.AddMessage("  listeId=%s" %str(listeId))
    arcpy.SetParameterAsText(15, listeMap)
    #Sortir sans code d'erreur
    sys.exit(0)