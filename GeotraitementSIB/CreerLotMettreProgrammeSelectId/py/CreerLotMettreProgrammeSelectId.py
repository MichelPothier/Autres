#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : CreerLotMettreProgrammeSelectId.py
# Auteur    : Michel Pothier
# Date      : 26 janvier 2015

"""
    Application qui permet de cr�er un lot et mettre au programme l'identifiant de d�coupage pr�sent dans un attribut
    pour chaque �l�ment s�lectionn� dans un FeatureLayer de d�coupage.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                                d�faut = SIB_PRO
    featureLayer        OB      FeatureLayer contenant les identifiants s�lectionn�s.
                                d�faut = ""
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail.
                                d�faut = DATASET_NAME
    typeProduit         OB      type de produit associ� au lot.
                                d�faut = ""
    typeTravail         OB      type de travail � effetuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
                                d�faut = ""
    anneeFinanciere     OB      Ann�e financi�re dans laquelle les co�ts de production sera d�bit�es (format : AAAA-AA).
                                d�faut = ""
    codeEquipe          OB      Code de l'�quipe qui effectue le travail.
                                d�faut = "AUTRE"
    codeExecutant       OB      Code du contractant � qui le contrat est octroy�.
                                d�faut = "CITS"
    noContact           OB      Num�ro de contact, chez le contractant, responsable du lot.
                                d�faut = "4"
    typeProduction      OB      Indique le type de production : 'A:Autre', 'C:Client' et 'E:Entente'.
                                d�faut = A
    normes              OB      Num�ro de la normes selon laquelle le fichier sera produit.
                                d�faut = ""
    catalogue           OP      Num�ro de catalogue selon laquelle le fichier sera produit. 
                                d�faut = ""
    fanionCollision     OB      Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme.
                                0 : la mise au programme n'est pas inscrite.
                                1 : la mise au programme est inscrite m�me s'il y a collision.
                                D�faut = 0
    listeCodeTopo       OB      Liste des codes d'�l�ments topographique trait�s.
                                d�faut = ""
    listeCollActive     OP      Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
                                d�faut = ""
    noContrat           OP      Num�ro de contrat.
                                d�faut = ""
    noTicket            OP      Num�ro de bon de commande du syst�me E-Procurment utilis� pour les travaux � l'externe.
                                d�faut = ""
    datePrevue          OP      Date pr�vue de la fin des travaux.
                                d�faut = ""
    nbJoursDelai        OP      Nombre de jours de d�lai accord�s � la date pr�vue.
                                d�faut = ""
    listeNonConf        OP      Liste des num�ros de non-conformit� trait�s.
                                d�faut = ""
    noteLot             OP      Note explicative pour le lot.
                                d�faut = ""
    noteMAP             OP      Note explicative associ�e aux identifiants trait�s.
                                d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    listeNoMap   : Liste des num�ros de mise au programme.
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerLotMettreProgrammeSelectId(object):
#*******************************************************************************************
    """
    Classe qui permet de mettre au programme les �l�ments s�lectionn�s dans un FeatureLayer
    selon l'information contenue dans un num�ro de lot.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'un lot.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, featureLayer, attributIdentifiant, typeProduit, typeTravail, anneeFinanciere,
                                codeEquipe, codeExecutant, noContact, typeProduction, normes, fanionCollision, listeCodeTopo):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        featureLayer        : FeatureLayer contenant les �l�ments des identifiants s�lectionn�s.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'�l�ment.
        typeProduit         : Type de produit associ� au lot.
        typeTravail         : Type de travail � effetuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
        anneeFinanciere     : Ann�e financi�re dans laquelle les co�ts de production sera d�bit�es (format : AAAA-AA).
        codeEquipe          : Code de l'�quipe qui effectue le travail.
        codeExecutant       : Code du contractant � qui le contrat a �t� octroy� (d�faut = null).
        noContact           : Num�ro de contact, chez le contractant, responsable du lot.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'.
        normes              : Num�ro de la normes selon laquelle le fichier sera produit.
        fanionCollision     : Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme.
        listeCodeTopo       : Liste des codes d'�l�ments topographique trait�s.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """
        
        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(featureLayer) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'featureLayer')
        
        if (len(attributIdentifiant) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'attributIdentifiant')
        
        if (len(typeProduit) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'typeProduit')
        
        if (len(typeTravail) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'typeTravail')
        
        if (len(anneeFinanciere) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'anneeFinanciere')
        
        if (len(codeEquipe) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'codeEquipe')
        
        if (len(codeExecutant) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'codeExecutant')
        
        if (len(noContact) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'noContact')
        
        if (len(typeProduction) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'typeProduction')
        
        if (len(normes) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'normes')
        
        if (len(fanionCollision) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'fanionCollision')
        
        if (len(listeCodeTopo) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'listeCodeTopo')
        
        return
    
    #-------------------------------------------------------------------------------------
    def definirDate(self, date, delai):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de d�finir la date pr�vue en fonction du d�lais fourni.
        Si on founi un d�lais, il est additionn� � la date du jour pour calculer la date de fin pr�vue.
        
        Param�tres:
        -----------
        date         : Date pr�vue de la fin des travaux.
        delai        : Nombre de jours de d�lai accord�s � la date pr�vue.
       
        Retour:
        -------
        datePrevue  : Date pr�vue de la fin des travaux incluant les jours de d�lai.
        
        """
        #V�rifier la pr�sence d'un d�lai
        if delai == "":
            #D�finir la date pr�vue sans d�lai
            datePrevue = date
        #Si aucun d�lai
        else:
            #D�finir la date pr�vue avec d�lai
            delaiSec = int(delai) * 60 * 60 * 24    # nombre de jours en secondes
            datePrevue = time.strftime("%Y/%m/%d", time.localtime(time.time() + delaiSec))
        
        return datePrevue
    
    #-------------------------------------------------------------------------------------
    def definirCodeCollision(self, listeCodeTopo, listeCollActive):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de d�finir la liste des codes topographiques et de leurs codes de collision actives.
        
        Param�tres:
        -----------
        listeCodeTopo       : Liste des codes d'�l�ments topographique trait�s.
        listeCollActive     : Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
       
        Retour:
        -------
        listeCodeTopo       : Liste des codes d'�l�ments topographique trait�s.
        listeCollActive     : Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
        
        """
       
        #Initialisation de la liste des codes topographiques et des collisions actives
        listeCode = ""
        listeCollision = ""

        #Traiter tous les codes ou liste de codes sp�cifi�s        
        listeCodeDesc = listeCodeTopo.split(",")
        for _codeDesc in listeCodeDesc:
            #Extraire le code de la description
            _code = (_codeDesc.replace("'","")).split(" :")

            #V�rifier si le code est absent de la liste des codes
            if _code[0] not in listeCode:
                #Ajouter le code � la liste de code
                listeCode = listeCode + _code[0] + ","
                
                #V�rifier si le code est pr�sent dans la liste des collisions actives
                if _code[0] in listeCollActive:
                    #On d�sactive la collision pour le code trait�
                    listeCollision = listeCollision + "1,"
                
                #Si le code est absent dans la liste des collisions actives
                else:
                    #On active la collision pour le code trait�
                    listeCollision = listeCollision + "0,"
        
        #D�finir la liste des codes et des collisions
        listeCodeTopo = listeCode.replace("'","")[:-1]
        listeCollActive = listeCollision[:-1]

        return listeCodeTopo, listeCollActive

    #-------------------------------------------------------------------------------------
    def validerIdentifiant(self, typeProduit):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de retourner le fanion pour indiquer si on doit valider l'identitifiant.
        
        Param�tres:
        -----------
        typeProduit     : Type de produit v�rifi�.
       
        Retour:
        -------
        fanionValiderIdentifiant    : Fanion pour indiquer si on doit valider l'identitifiant.
                                      0 : "SANS-DECOUPAGE"
                                      1 : "AVEC-DECOUPAGE"
        """
        
        #V�rifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE CD_PARAMETRE='DECOUPAGE' AND TY_PRODUIT='" + typeProduit + "'")

        #Indiquer s'il s'agit d'un d�coupage pr�-d�finit
        if (not resultat) or (resultat[0][0] == "SANS-DECOUPAGE"):
            fanionValiderIdentifiant=0
        else:
            fanionValiderIdentifiant=1
        
        #Sortir et retourner le r�sultat
        return fanionValiderIdentifiant
    
    #-------------------------------------------------------------------------------------
    def mapSansEdVer(self, typeProduit):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant d'indiquer si la mise au programme se fait avec ou sans �dition et version.
        
        Param�tres:
        -----------
        typeProduit     : Type de produit v�rifi�.
       
        Retour:
        -------
        sansEdVer       : Indique si la mise au programme est avec ou sans �dition et version.getvalue
        
        """
        
        #V�rifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE CD_PARAMETRE='MAP-SANS-ED-VER' AND TY_PRODUIT='" + typeProduit + "'")

        #D�finir le r�sultat de la requ�te
        if resultat:
            sansEdVer = True
        else:
            sansEdVer = False
        
        #Sortir et retourner le r�sultat
        return sansEdVer
    
    #-------------------------------------------------------------------------------------
    def miseAuProgramme(self, typeProduit, identifiant, datePrevue, normes, typeTravail, noLot, noGroupe, typeProduction, note, 
                        gabaritMeta, listeNosNonConf, listeElemTopo, listeCollActive, fanionCollision, 
                        fanionValiderIdentifiant, catalogue=""):
    #-------------------------------------------------------------------------------------
        """
        Cette m�thode effectue une mise au programme et ajoute les travaux associ�s � la production d'un jeu de donn�es pour un lot donn� dans SIB.

        Param�tres:
        ---------
        typeProduit             : Nom du produit
        identifiant             : Identifiant du produit
        datePrevue              : Date � laquelle tous les travaux c�dul�s seront termin�s
        normes                  : Normes selon laquelle le fichier sera produit
        typeProduction          : Indique le type de production : 'A', 'C' et 'E'
        note                    : Information compl�mentaire : 3 lignes de 80 caract�res maximum
        gabaritMeta             : Code indiquant le gabarit de m�tadonn�es � utiliser
        listeNosNonConf         : Liste des num�ros de non conformit�s qui seront r�gl�s par cette mise au programme (d�faut NULL) (optionnel) 
        listeElemTopo           : Liste des codes d��l�ments topographiques associ�s � cette mise au programme (d�faut NULL)(optionnel) 
        typeTravail             : Type de travail � effectuer
        noLot                   : Num�ro de lot associ� � la mise au programme
        noGroupe                : Num�ro de groupe
        listeCollActive         : Liste des valeurs � appliquer � chacun des codes d'entit�s topographiques pour la gestion des collisions
        fanionCollision         : Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme
        fanionValiderIdentifiant: Fanion indiquant si on veut valider ou non l'identifiant selon la table dictionnaires F101
        catalogue               : Num�ro du catalogue
        
        Valeurs de retour:
        -----------------
        infoMap     : Contient l'information sur la mise au programme effectu�e {"noMap":noMap, "edition":edition, "version":version}

        """
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS','PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        # Appel du service de transaction Sib qui initialise l'ajout d'une nouvelle instance de produit au programme
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Mise_au_programme : " + sUsagerSib + "," + typeProduit + "," + identifiant + ",DT:" + datePrevue + ",N:" + normes + ",TP:" + typeProduction + ",Nt:" + note + ",GM:" + gabaritMeta + ",NC:" + listeNosNonConf + ",ET:" + listeElemTopo + ",CA:" + listeCollActive)
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Mise_au_programme : " + sUsagerSib + "," + typeProduit + "," + identifiant + "," + datePrevue + "," + normes + "," + typeProduction + "," + note + "," + gabaritMeta + "," + listeNosNonConf + "," + listeElemTopo + "," + listeCollActive + "," + fanionCollision + "," + fanionValiderIdentifiant)
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Mise_au_programme", cx_Oracle.STRING, [sUsagerSib, typeProduit, identifiant, datePrevue, normes, typeProduction, note, gabaritMeta, listeNosNonConf, listeElemTopo, listeCollActive, fanionCollision, fanionValiderIdentifiant])
        # V�rifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Mise_au_programme]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute un travail � la mise au programme pr�alablement initialis�e
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Travail")
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Travail", cx_Oracle.STRING, [typeTravail, 1, catalogue])
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        # V�rifier le code de retour
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Travail]")
            raise Exception(message)
        
        #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable noMap
        noMap = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable edition
        edition = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable version 
        version = self.Sib.cursor.var(cx_Oracle.NUMBER)
        
        # Appel du service de transaction qui termine l'ajout d'un travail
        #arcpy.AddMessage("- P0502_PR.pu_Ajouter_Termine")
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Termine", cx_Oracle.STRING, [noMap, edition, version])
        # V�rifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Termine]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute une instance de produit au contenu d'un lot
        #arcpy.AddMessage("- P0607_CONT.pu_Ajouter_contenu_lot")
        codeRetour = self.Sib.cursor.callfunc("P0607_CONT.pu_Ajouter_contenu_lot", cx_Oracle.STRING, [sUsagerSib, noLot, noGroupe, noMap])
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        # V�rifier le code de retour
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0607_CONT.pu_Ajouter_contenu_lot]")
            raise Exception(message)
        
        #D�finir le num�ro de mise au programme
        noMap = int(noMap.getvalue())
        #V�rifier si la mise au programme se fait avec �dition et version
        if self.mapSansEdVer(typeProduit):
            #D�finir l'�dition et la version � None
            edition = -1
            version = -1
        else:
            #Extraire l'�dition et la version r�sultante
            edition = int(edition.getvalue())
            version = int(version.getvalue())
        
        # D�finir l'information � retourner sur la mise au programme
        infoMap = {"noMap":noMap, "edition":edition, "version":version}
        
        #Sortir et retourner l'information sur la mise au programme        
        return infoMap
    
    #-------------------------------------------------------------------------------------
    def CreerLot(self, typeProduit, typeTravail, anneeFinanciere, codeEquipe, etatLot, noGroupe, noCpc, codeExecutant, noContrat, noContact, noTicket, note):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'un lot pour un produit donn�.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        typeProduit     : type de produit associ� au lot
        typeTravail     : type de travail � effetuer sur tous les identifiants du lot. Doit �tre pr�d�fini pr�alablement dans SIB.
        anneeFinanciere : ann�e financi�re o� la production a commenc�e (format : AAAA-AA)
        codeEquipe      : code de l'�quipe qui effectue le travail
        etatLot         : �tat du lot [A:en pr�paration /C:pr�t pour la production /T:termin�] 
        noGroupe        : num�ro de groupe associ� au num�ro de lot. Il est possible de sp�cifier plusieurs groupes 
                          s�par�s par des virgules (01, 02, 03). Il est �galement possible d'ajouter pour chaque groupe
                          �nonc� la date de r�ception (01+YYYY-MM-DD) ou (01+YYYY-MM-DD, 02+YYYY-MM-DD, 03+YYYY-MM-DD)
        noCpc           : (optionnel) num�ro de CPC pour le contr�le des co�ts (d�faut = null)
        codeExecutant   : (optionnel) code du contractant � qui le contrat a �t� octroy� (d�faut = null)
        noContrat       : (optionnel) num�ro de contrat (d�faut = null)
        noContact       : (optionnel) num�ro de contact, chez le contractant, responsable du lot
        noTicket        : (optionnel) num�ro de ticket (d�faut = null)
        note            : (optionnel) note attach�e au lot cr�er (d�faut = null)
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : nombre de messages d'erreur g�n�r�s par le service de transaction SIB
        messageSib      : description du message re�ue du service de transaction SIB

        Valeurs de retour:
        -----------------
        noLot           -- num�ro de lot cr��
        """

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")  
        
        #Appel du service de transaction SIB qui initialise l'ajout d'un lot
        #arcpy.AddMessage("- Appel du service SIB : P0608_LOT.pu_Ajouter_Lot")
        codeRetour = self.Sib.cursor.callfunc("P0608_LOT.pu_Ajouter_Lot", cx_Oracle.STRING, [sUsagerSib, typeProduit, typeTravail, anneeFinanciere, codeEquipe, noCpc, codeExecutant, noContrat, noContact, noTicket, note])

        #V�rifier le succ�s du service SIB 
        if self.Sib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
            #Traiter tous les num�ros de groupe dans le lot pr�alablement initialis�
            for record_groupe in noGroupe.split(","):
                list_item_record_groupe = record_groupe.split("+")
                dt_recep = None
                groupe = list_item_record_groupe[0]
                if len(list_item_record_groupe) > 1:
                    dt_recep = list_item_record_groupe[1]
                #Appel du service de transaction SIB qui ajoute un num�ro de groupe dans le lot pr�alablement initialis�
                #arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Ajouter_Groupe")
                codeRetour = self.Sib.cursor.callfunc('P0608_lot.pu_Ajouter_Groupe', cx_Oracle.STRING, [groupe, dt_recep])

            #V�rifier le succ�s du service SIB 
            if self.Sib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                #appel du service de transaction SIB qui finalise l'ajout du lot et retour du num�ro de lot cr��
                noLot = self.Sib.cursor.var(cx_Oracle.STRING)  #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable noLot
                codeRetour = self.Sib.cursor.callfunc('P0608_lot.pu_Ajouter_Termine', cx_Oracle.STRING, [noLot])

                #V�rifier le succ�s du service SIB 
                if self.Sib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                    #r�cup�ration de l'�tampe temporelle du lot pr�alablement cr��e
                    requete = "select updt_fld from f601_lo where no_lot ='%s'" % (noLot.getvalue())
                    #arcpy.AddMessage("  " + requete)
                    self.Sib.cursor.execute(requete)
                    etampe = self.Sib.cursor.fetchone() [0]
                    #arcpy.AddMessage("  �tampe temporelle : %s" %etampe)
                    
                    #appel du service de transaction SIB qui modifie l'�tat du lot pr�alablement cr��
                    #arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Modifier_Etat_Lot")
                    codeRetour = self.Sib.cursor.callfunc('P0608_lot.pu_Modifier_Etat_Lot', cx_Oracle.STRING, [sUsagerSib, noLot, etatLot, etampe])
                    
                    #V�rifier le succ�s du service SIB 
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
                
                #la finalisation de l'ajout du lot n'a pas r�ussie
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
                
            #l'ajout du groupe n'a pas r�ussie
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
        
        #l'initialisation de l'ajout d'un lot n'a pas r�ussi
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
        
        #Sortir et retourner le num�ro de lot
        return noLot.getvalue()

    #-------------------------------------------------------------------------------------
    def executer(self, env, featureLayer, attributIdentifiant, typeProduit, typeTravail, anneeFinanciere, codeEquipe, codeExecutant, noContact, typeProduction,
                 normes, catalogue, fanionCollision, listeCodeTopo, listeCollActive, noContrat, noTicket,
                 datePrevue, nbJoursDelai, listeNonConf, noteLot, noteMAP):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de mise au programme des �l�ments d'identifiant de d�coupage s�lectionn�s.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        featureLayer        : FeatureLayer contenant les �l�ments des identifiants s�lectionn�s.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'�l�ment.
        typeProduit         : Type de produit associ� au lot.
        typeTravail         : Type de travail � effetuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
        anneeFinanciere     : Ann�e financi�re dans laquelle les co�ts de production sera d�bit�es (format : AAAA-AA).
        codeEquipe          : Code de l'�quipe qui effectue le travail.
        codeExecutant       : Code du contractant � qui le contrat a �t� octroy� (d�faut = null).
        noContact           : Num�ro de contact, chez le contractant, responsable du lot.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'.
        normes              : Num�ro de la normes selon laquelle le fichier sera produit.
        catalogue           : Num�ro de catalogue selon laquelle le fichier sera produit. 
        fanionCollision     : Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme.
        listeCodeTopo       : Liste des codes d'�l�ments topographique trait�s.
        listeCollActive     : Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
        noContrat           : Num�ro de contrat.
        noTicket            : Num�ro de bon de commande du syst�me E-Procurment utilis� pour les travaux � l'externe.
        datePrevue          : Date pr�vue de la fin des travaux.
        nbJoursDelai        : Nombre de jours de d�lai accord�s � la date pr�vue.
        listeNonConf        : Liste des num�ros de non-conformit� trait�s.
        noteLot             : Note explicative associ�e aux lots.
        noteMAP             : Note explicative associ�e aux identifiants mise au programme.
        
        Variables:
        ----------
        self.CompteSib      : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib                : Objet utilitaire pour traiter des services SIB.
        sUsagerSib          : Nom de l'usager SIB.
        code_retour         : Code de retour d'un service SIB.
        nbMessSib           : Nombre de messages d'erreur g�n�r�s par le service de transaction SIB
        messageSib          : Description du message re�ue du service de transaction SIB
        noLot               : Numr�ro de lot dans lequel la mise au programme doit �tre ajout�.
        noGroupe            : Numr�ro de groupe dans lequel la mise au programme doit �tre ajout�.

        Valeurs de retour:
        -----------------
        listeMap        : Liste des num�ros des mises au programme.
        listeEd         : Liste des num�ros d'�dition.
        listeVer        : Liste des num�ros de version.
        listeId         : Liste des identifiants de d�coupage.
        
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #D�finir les valeurs par d�faut
        gabaritMeta = ""
        etatLot     = "C"
        noGroupe    = "01"
        noCpc       = ""
        
        #D�finir la date pr�vue en fonction du d�lai        
        arcpy.AddMessage("- D�finir la date pr�vue en fonction du d�lai")
        datePrevue = self.definirDate(datePrevue, nbJoursDelai)
        arcpy.AddMessage("  datePrevue=" + datePrevue)
        
        #Extraction de la liste des codes topographiques et des collisions actives
        arcpy.AddMessage("- D�finir les codes de collisions")
        listeCodeTopo, listeCollActive = self.definirCodeCollision(listeCodeTopo, listeCollActive)
        arcpy.AddMessage("  listeCodeTopo=" + listeCodeTopo)
        arcpy.AddMessage("  listeCollActive=" + listeCollActive)
        
        #V�rifier si l'identifiant doit �tre valid�
        arcpy.AddMessage("- V�rifier si l'identifiant de d�coupage doit �tre valid�")
        fanionValiderIdentifiant = self.validerIdentifiant(typeProduit)
        arcpy.AddMessage("  fanionValiderIdentifiant=" + str(fanionValiderIdentifiant))
        
        #Initialiser les listes
        listeNoLot = []
        listeMap = []
        listeEd = []
        listeVer = []
        listeId = []
        
        #Traiter tous les �l�ments d'identifiant de d�coupage s�lectionn�s
        arcpy.AddMessage("- Traiter tous les �l�ments du FeatureLayer : " + featureLayer)
        #Cr�er le curseur pour la recherche
        cursor = arcpy.SearchCursor(featureLayer)
        #Extraire le premier �l�ment
        row = cursor.next()
        #traiter tant qu'il y aura des �l�ments
        while row:
            #D�finir l'identifiant trait�
            identifiant = str(row.getValue(attributIdentifiant))
            
            #Ajouter l'identifiant dans la liste
            listeId.append(identifiant)
            
            #Ex�cuter le traitement de cr�ation d'un num�ro de lot.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Cr�ation d'un lot dans SIB ...")
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
            
            #extraire le prochain �l�ment
            row = cursor.next()
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir et retourner la liste des num�ro de lot, de mise au programme, des �ditions, des versions et des identifiants.
        return listeNoLot, listeMap, listeEd, listeVer, listeId

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
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
        
        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet de cr�ation de lot et de mise au programme.
        oCreerLotMettreProgrammeSelectId = CreerLotMettreProgrammeSelectId()
        
        #Valider les param�tres obligatoires
        oCreerLotMettreProgrammeSelectId.validerParamObligatoire(env, featureLayer, attributIdentifiant, typeProduit, typeTravail, anneeFinanciere,
                                         codeEquipe, codeExecutant, noContact, typeProduction, normes, fanionCollision, listeCodeTopo)
        
        #Ex�cuter le traitement de cr�ation de lot et de mise au programme.
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
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("- Succ�s du traitement")
    #Afficher les num�ros de mise au programme
    arcpy.AddMessage("  listeNoLot=%s" %str(listeNoLot))
    arcpy.AddMessage("  listeMap=%s" %str(listeMap))
    arcpy.AddMessage("  listeEd=%s" %str(listeEd))
    arcpy.AddMessage("  listeVer=%s" %str(listeVer))
    arcpy.AddMessage("  listeId=%s" %str(listeId))
    arcpy.SetParameterAsText(22, listeNoLot)
    arcpy.SetParameterAsText(23, listeMap)
    #Sortir sans code d'erreur
    sys.exit(0)