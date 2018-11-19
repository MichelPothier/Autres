#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierLotProduction.py
# Auteur    : Michel Pothier
# Date      : 03 f�vrier 2015

"""
    Application qui permet de modifier toute l'information d'un lot de production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              d�faut = SIB_PRO
    noLot              OB     Num�ro du lot de production � modifier.
                              d�faut = ""
    typeProduit        OB     Type de produit associ� au lot.
                              d�faut = ""
    typeTravail        OB     Type de travail � effectuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
                              d�faut = ""
    anneeFinanciere    OB     Ann�e financi�re dans laquelle les co�ts de production sera d�bit�es (format : AAAA-AA).
                              d�faut = ""
    codeEquipe         OB     Code de l'�quipe qui effectue le travail.
                              d�faut = ""
    codeExecutant      OB     Code du contractant � qui le contrat est octroy�.
                              d�faut = ""
    noContact          OB     Num�ro de contact, chez le contractant, responsable du lot.
                              d�faut = ""
    etatLot            OB     �tat du lot [A:en pr�paration /C:pr�t pour la production /T:termin�].
                              D�faut = ""
    noContrat          OP     Num�ro de contrat.
                              d�faut = ""
    noCpc              OP     Num�ro de CPC pour le contr�le des co�ts.
                              d�faut = ""
    noTicket           OP     Num�ro de bon de commande du syst�me E-Procurment utilis� pour les travaux � l'externe.
                              d�faut = ""
    note               OP     Note explicative pour le lot.
                              d�faut = ""
    noteTableauBord    OP     Note pour le tableau de bord.
                              d�faut = ""
    dateDebut          OP     Date de d�but de traitement du lot.
                              d�faut = ""
    dateFin            OP     Date de fin de traitement du lot.
                              d�faut = ""
    prixKm             OP     Prix associ� � chaque kilom�tre.
                              d�faut = ""
    prixContrat        OP     Prix associ� associ� au contrat.
                              d�faut = ""
    fermetureAuto      OP     Code de fermeture automatique du lot [0:NON/1:OUI].
                              d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
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
    def validerParamObligatoire(self, env, noLot, typeProduit, typeTravail, anneeFinanciere, codeEquipe, codeExecutant, noContact, etatLot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement.    
        noLot           : Num�ro du lot de production � modifier.
        typeProduit     : Type de produit associ� au lot.
        typeTravail     : Type de travail � effetuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
        anneeFinanciere : Ann�e financi�re dans laquelle les co�ts de production sera d�bit�es (format : AAAA-AA).
        codeEquipe      : Code de l'�quipe qui effectue le travail.
        codeExecutant   : Code du contractant � qui le contrat a �t� octroy�.
        noContact       : Num�ro de contact, chez le contractant, responsable du lot.
        etatLot         : �tat du lot [A:en pr�paration /C:pr�t pour la production /T:termin�].
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')
        
        if (len(noLot) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'noLot')
        
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
        
        if (len(etatLot) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'etatLot')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self,env,noLot,typeProduit,typeTravail,anneeFinanciere,codeEquipe,codeExecutant,noContact,etatLot,noContrat,noCpc,noTicket,note,noteTableauBord,dateDebut,dateFin,prixKm,prixContrat,fermetureAuto):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier toute l'information d'un lot de production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        noLot           : Num�ro du lot de production � modifier.
        typeProduit     : Type de produit associ� au lot.
        typeTravail     : Type de travail � effetuer sur tous les identifiants du lot. Doit �tre pr�d�fini pr�alablement dans SIB.
        anneeFinanciere : Ann�e financi�re o� la production a commenc�e (format : AAAA-AA).
        codeEquipe      : Code de l'�quipe qui effectue le travail.
        codeExecutant   : Code du contractant � qui le contrat a �t� octroy�.
        noContact       : Num�ro de contact, chez le contractant, responsable du lot.
        etatLot         : �tat du lot [A:en pr�paration /C:pr�t pour la production /T:termin�].
        noContrat       : Num�ro de contrat.
        noCpc           : Num�ro de CPC pour le contr�le des co�ts.
        noTicket        : Num�ro de ticket.
        note            : Note attach�e au lot.
        noteTableauBord : Note pour le tableau de bord.
        dateDebut       : Date de d�but de traitement du lot.
        dateFin         : Date de fin de traitement du lot.
        prixKm          : Prix associ� � chaque kilom�tre.
        prixContrat     : Prix associ� associ� au contrat.
        fermetureAuto   : Code de fermeture automatique du lot [0:NON/1:OUI].
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur g�n�r�s par le service de transaction SIB.
        messageSib      : Description du message re�ue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'PLAN' ou 'G-SYS'")
        
        #Valider si le lot de production est absent
        arcpy.AddMessage("- Valider le num�ro du lot de production")
        resultat = oSib.requeteSib("SELECT NO_LOT FROM F601_LO WHERE NO_LOT='" + noLot + "'")
        #V�rifier si le lot de production est absent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le lot de production '" + noLot + "' est absent")
        
        #V�rifier si le num�ro de contrat est vide
        if noContrat == "":
            #Ajouter la valeur NULL
            noContrat = "NULL"
        #si le num�ro de contrat n'est pas vide
        else:
            #Ajouter les apostrophes
            noContrat = "'" + noContrat + "'"
        
        #V�rifier si le num�ro de CPC est vide
        if noCpc == "":
            #Ajouter la valeur NULL
            noCpc = "NULL"
        #si le num�ro de CPC n'est pas vide
        else:
            #Ajouter les apostrophes
            noCpc = "'" + noCpc + "'"
        
        #V�rifier si le num�ro de ticket est vide
        if noTicket == "":
            #Ajouter la valeur NULL
            noTicket = "NULL"
        #si le num�ro de ticket n'est pas vide
        else:
            #Ajouter les apostrophes
            noTicket = "'" + noTicket + "'"
        
        #V�rifier si la note est vide
        if note == "":
            #Ajouter la valeur NULL
            note = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            note = "'" + note.replace("'","''") + "'"
        
        #V�rifier si la note du tableau de bord est vide
        if noteTableauBord == "":
            #Ajouter la valeur NULL
            noteTableauBord = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            noteTableauBord = "'" + noteTableauBord.replace("'","''") + "'"
        
        #V�rifier si la date de d�but est vide
        if dateDebut == "":
            #Ajouter la valeur NULL
            dateDebut = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            dateDebut = "'" + dateDebut + "'"
        
        #V�rifier si la date de fin est vide
        if dateFin == "":
            #Ajouter la valeur NULL
            dateFin = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            dateFin = "'" + dateFin + "'"
        
        #V�rifier si le prix du KM est vide
        if prixKm == "":
            #Ajouter la valeur NULL
            prixKm = "NULL"
        
        #V�rifier si le prix du contrat est vide
        if prixContrat == "":
            #Ajouter la valeur NULL
            prixContrat = "NULL"
        
        #V�rifier si la fermeture automatique est vide
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
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
        
        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet pour modifier l'information d'un num�ro de lot de production.
        oModifierLotProduction = ModifierLotProduction()
        
        #Valider les param�tres obligatoires
        oModifierLotProduction.validerParamObligatoire(env, noLot, typeProduit, typeTravail, anneeFinanciere, codeEquipe, codeExecutant, noContact, etatLot)
        
        #Ex�cuter le traitement modifier l'information d'un num�ro de lot de production.
        oModifierLotProduction.executer(env,noLot,typeProduit,typeTravail,anneeFinanciere,codeEquipe,codeExecutant,noContact,etatLot,noContrat,noCpc,noTicket,note,noteTableauBord,dateDebut,dateFin,prixKm,prixContrat,fermetureAuto)
    
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