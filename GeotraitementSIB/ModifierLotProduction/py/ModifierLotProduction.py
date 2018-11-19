#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierLotProduction.py
# Auteur    : Michel Pothier
# Date      : 03 février 2015

"""
    Application qui permet de modifier toute l'information d'un lot de production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    noLot              OB     Numéro du lot de production à modifier.
                              défaut = ""
    typeProduit        OB     Type de produit associé au lot.
                              défaut = ""
    typeTravail        OB     Type de travail à effectuer sur tous les identifiants du lot, préalablement défini dans SIB.
                              défaut = ""
    anneeFinanciere    OB     Année financière dans laquelle les coûts de production sera débitées (format : AAAA-AA).
                              défaut = ""
    codeEquipe         OB     Code de l'équipe qui effectue le travail.
                              défaut = ""
    codeExecutant      OB     Code du contractant à qui le contrat est octroyé.
                              défaut = ""
    noContact          OB     Numéro de contact, chez le contractant, responsable du lot.
                              défaut = ""
    etatLot            OB     État du lot [A:en préparation /C:prêt pour la production /T:terminé].
                              Défaut = ""
    noContrat          OP     Numéro de contrat.
                              défaut = ""
    noCpc              OP     Numéro de CPC pour le contrôle des coûts.
                              défaut = ""
    noTicket           OP     Numéro de bon de commande du système E-Procurment utilisé pour les travaux à l'externe.
                              défaut = ""
    note               OP     Note explicative pour le lot.
                              défaut = ""
    noteTableauBord    OP     Note pour le tableau de bord.
                              défaut = ""
    dateDebut          OP     Date de début de traitement du lot.
                              défaut = ""
    dateFin            OP     Date de fin de traitement du lot.
                              défaut = ""
    prixKm             OP     Prix associé à chaque kilomètre.
                              défaut = ""
    prixContrat        OP     Prix associé associé au contrat.
                              défaut = ""
    fermetureAuto      OP     Code de fermeture automatique du lot [0:NON/1:OUI].
                              défaut = ""
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierLotProduction.py env noLot typeProduit typeTravail anneeFinanciere codeEquipe codeExecutant noContact etatLot
        [noContrat] [noCpc] [noTicket] [note] [noteTableauBord] [dateDebut] [dateFin] [prixKm] [prixContrat] [fermetureAuto]

    Exemple:
        ModifierLotProduction.py SIB_PRO 35444 BDG CORINT 2014-15 AUTRE CITS 4 A # # # "Note pour le lot"
                                "Note pour le tableau de bord" 2015-02-03 2016-02-03 0 0 1

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierLotProduction.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierLotProduction(object):
#*******************************************************************************************
    """
    Permet de modifier toute l'information d'un lot de production dans SIB.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier toute l'information d'un lot de production dans SIB.
        
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
    def validerParamObligatoire(self, env, noLot, typeProduit, typeTravail, anneeFinanciere, codeEquipe, codeExecutant, noContact, etatLot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        noLot           : Numéro du lot de production à modifier.
        typeProduit     : Type de produit associé au lot.
        typeTravail     : Type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
        anneeFinanciere : Année financière dans laquelle les coûts de production sera débitées (format : AAAA-AA).
        codeEquipe      : Code de l'équipe qui effectue le travail.
        codeExecutant   : Code du contractant à qui le contrat a été octroyé.
        noContact       : Numéro de contact, chez le contractant, responsable du lot.
        etatLot         : État du lot [A:en préparation /C:prêt pour la production /T:terminé].
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(noLot) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noLot')
        
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
        
        if (len(etatLot) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'etatLot')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self,env,noLot,typeProduit,typeTravail,anneeFinanciere,codeEquipe,codeExecutant,noContact,etatLot,noContrat,noCpc,noTicket,note,noteTableauBord,dateDebut,dateFin,prixKm,prixContrat,fermetureAuto):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier toute l'information d'un lot de production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        noLot           : Numéro du lot de production à modifier.
        typeProduit     : Type de produit associé au lot.
        typeTravail     : Type de travail à effetuer sur tous les identifiants du lot. Doit être prédéfini préalablement dans SIB.
        anneeFinanciere : Année financière où la production a commencée (format : AAAA-AA).
        codeEquipe      : Code de l'équipe qui effectue le travail.
        codeExecutant   : Code du contractant à qui le contrat a été octroyé.
        noContact       : Numéro de contact, chez le contractant, responsable du lot.
        etatLot         : État du lot [A:en préparation /C:prêt pour la production /T:terminé].
        noContrat       : Numéro de contrat.
        noCpc           : Numéro de CPC pour le contrôle des coûts.
        noTicket        : Numéro de ticket.
        note            : Note attachée au lot.
        noteTableauBord : Note pour le tableau de bord.
        dateDebut       : Date de début de traitement du lot.
        dateFin         : Date de fin de traitement du lot.
        prixKm          : Prix associé à chaque kilomètre.
        prixContrat     : Prix associé associé au contrat.
        fermetureAuto   : Code de fermeture automatique du lot [0:NON/1:OUI].
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur générés par le service de transaction SIB.
        messageSib      : Description du message reçue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #Vérifier si l'usager SIB possède les privilège de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'PLAN' ou 'G-SYS'")
        
        #Valider si le lot de production est absent
        arcpy.AddMessage("- Valider le numéro du lot de production")
        resultat = oSib.requeteSib("SELECT NO_LOT FROM F601_LO WHERE NO_LOT='" + noLot + "'")
        #Vérifier si le lot de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le lot de production '" + noLot + "' est absent")
        
        #Vérifier si le numéro de contrat est vide
        if noContrat == "":
            #Ajouter la valeur NULL
            noContrat = "NULL"
        #si le numéro de contrat n'est pas vide
        else:
            #Ajouter les apostrophes
            noContrat = "'" + noContrat + "'"
        
        #Vérifier si le numéro de CPC est vide
        if noCpc == "":
            #Ajouter la valeur NULL
            noCpc = "NULL"
        #si le numéro de CPC n'est pas vide
        else:
            #Ajouter les apostrophes
            noCpc = "'" + noCpc + "'"
        
        #Vérifier si le numéro de ticket est vide
        if noTicket == "":
            #Ajouter la valeur NULL
            noTicket = "NULL"
        #si le numéro de ticket n'est pas vide
        else:
            #Ajouter les apostrophes
            noTicket = "'" + noTicket + "'"
        
        #Vérifier si la note est vide
        if note == "":
            #Ajouter la valeur NULL
            note = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            note = "'" + note.replace("'","''") + "'"
        
        #Vérifier si la note du tableau de bord est vide
        if noteTableauBord == "":
            #Ajouter la valeur NULL
            noteTableauBord = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            noteTableauBord = "'" + noteTableauBord.replace("'","''") + "'"
        
        #Vérifier si la date de début est vide
        if dateDebut == "":
            #Ajouter la valeur NULL
            dateDebut = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            dateDebut = "'" + dateDebut + "'"
        
        #Vérifier si la date de fin est vide
        if dateFin == "":
            #Ajouter la valeur NULL
            dateFin = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            dateFin = "'" + dateFin + "'"
        
        #Vérifier si le prix du KM est vide
        if prixKm == "":
            #Ajouter la valeur NULL
            prixKm = "NULL"
        
        #Vérifier si le prix du contrat est vide
        if prixContrat == "":
            #Ajouter la valeur NULL
            prixContrat = "NULL"
        
        #Vérifier si la fermeture automatique est vide
        if fermetureAuto == "":
            #Ajouter la valeur NULL
            fermetureAuto = "NULL"
        
        #Modifier l'information du lot de production
        arcpy.AddMessage("- Modifier l'information du lot de production")
        #Initialiser la commande SQL de modifification
        sql = "UPDATE F601_LO SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE"
        sql = sql + ",TY_PRODUIT='" + typeProduit + "',TY_TRAV='" + typeTravail + "',ANNEE='" + anneeFinanciere + "',CD_EQUIPE='" + codeEquipe + "',E_LOT='" + etatLot + "',CD_EXECU='" + codeExecutant + "',NO_CONTACT=" + noContact
        sql = sql + ",NO_CONTRAT=" + noContrat + ",NO_CPC=" + noCpc + ",NO_TICKET=" + noTicket + ",NOTE=" + note
        sql = sql + ",NOTE_TAB_BORD=" + noteTableauBord + ",DT_DEBUT=TO_DATE(" + dateDebut + "),DT_FIN=TO_DATE(" + dateFin + "),PRIX_KM=" + prixKm + ",PRIX_CONTRAT=" + prixContrat + ",FERMETURE_AUTO=" + fermetureAuto
        sql= sql + " WHERE NO_LOT='" + noLot + "'"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env              = "SIB_PRO"
        noLot            = ""
        typeProduit      = ""
        typeTravail      = ""
        anneeFinanciere  = ""
        codeEquipe       = ""
        codeExecutant    = ""
        noContact        = ""
        etatLot          = ""
        noContrat        = ""
        noCpc            = ""
        noTicket         = ""
        note             = ""
        noteTableauBord  = ""
        dateDebut        = ""
        dateFin          = ""
        prixKm           = ""
        prixContrat      = ""
        fermetureAuto    = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            noLot = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            typeProduit = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            typeTravail = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            anneeFinanciere = sys.argv[5]
        
        if len(sys.argv) > 6:
            codeEquipe = sys.argv[6].upper()
        
        if len(sys.argv) > 7:
            codeExecutant = sys.argv[7].upper()
        
        if len(sys.argv) > 8:
            noContact = sys.argv[8].split(":")[0]
        
        if len(sys.argv) > 9:
            etatLot = str(sys.argv[9])
        
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                noContrat = sys.argv[10]
        
        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                noCpc = sys.argv[11]
        
        if len(sys.argv) > 12:
            if sys.argv[12] <> "#":
                noTicket = sys.argv[12]
        
        if len(sys.argv) > 13:
            if sys.argv[13] <> "#":
                note = sys.argv[13]
        
        if len(sys.argv) > 14:
            if sys.argv[14] <> "#":
                noteTableauBord = sys.argv[14]
        
        if len(sys.argv) > 15:
            if sys.argv[15] <> "#":
                dateDebut = sys.argv[15]
        
        if len(sys.argv) > 16:
            if sys.argv[16] <> "#":
                dateFin = sys.argv[16]
        
        if len(sys.argv) > 17:
            if sys.argv[17] <> "#":
                prixKm = sys.argv[17]
        
        if len(sys.argv) > 18:
            if sys.argv[18] <> "#":
                prixContrat = sys.argv[18]
        
        if len(sys.argv) > 19:
            if sys.argv[19] <> "#":
                fermetureAuto = sys.argv[19].split(":")[0]
        
        #Définir l'objet pour modifier l'information d'un numéro de lot de production.
        oModifierLotProduction = ModifierLotProduction()
        
        #Valider les paramètres obligatoires
        oModifierLotProduction.validerParamObligatoire(env, noLot, typeProduit, typeTravail, anneeFinanciere, codeEquipe, codeExecutant, noContact, etatLot)
        
        #Exécuter le traitement modifier l'information d'un numéro de lot de production.
        oModifierLotProduction.executer(env,noLot,typeProduit,typeTravail,anneeFinanciere,codeEquipe,codeExecutant,noContact,etatLot,noContrat,noCpc,noTicket,note,noteTableauBord,dateDebut,dateFin,prixKm,prixContrat,fermetureAuto)
    
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