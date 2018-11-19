#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerLotProduction.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet de créer un lot dans SIB selon un type de produit et un type de travail.
    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    typeProduit        OB     Type de produit associé au lot.
    typeTravail        OB     Type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
    anneeFinanciere    OB     Année financière dans laquelle les coûts de production sera débitées (format : AAAA-AA).
    codeEquipe         OP     Code de l'équipe qui effectue le travail.
                              défaut = "AUTRE"
    codeExecutant      OP     Code du contractant à qui le contrat est octroyé.
                              défaut = "CITS"
    noContact          OP     Numéro de contact, chez le contractant, responsable du lot.
                              défaut = "4"
    noGroupe           OP     Permet de spécifier le groupe ou la liste de groupes (séparés par des virgules) 
                              à créer dans le lot. Il est également possible d'ajouter pour chaque groupe
                              énoncé la date de réception (01+YYYY-MM-DD) ou (01+YYYY-MM-DD, 02+YYYY-MM-DD, 03+YYYY-MM-DD).
                              Défaut = 01 (avec aucune date de réception)
    noContrat          OP     Numéro de contrat.
                              défaut = ""
    noCpc              OP     Numéro de CPC pour le contrôle des coûts.
                              défaut = ""
    noTicket           OP     Numéro de bon de commande du système E-Procurment utilisé pour les travaux à l'externe.
                              défaut = ""
    note               OP     Note explicative pour le lot.
                              défaut = ""
    
    Paramètres de sortie:
    ---------------------
    noLot   : Numéro de lot créé
    
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerLotProduction.py env typeProduit typeTravail anneeFinanciere codeEquipe codeExecutant noContact groupe
        [noContrat] [noCpc] [noTicket] [note] [fichierLog]

    Exemple:
        CreerLotProduction.py SIB_PRO BDG CORINT 2014-15 AUTRE CITS 4 01+2014-06-30 # # # "Note pour le lot"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerLotProduction.py 2140 2017-10-19 15:42:09Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerLotProduction(object):
#*******************************************************************************************
    """
    Permet de créer un lot dans SIB selon un type de produit et un type de travail.
    
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
    def validerParamObligatoire(self, env, typeProduit, typeTravail, anneeFinanciere):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit associé au lot.
        typeTravail         : Type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
        anneeFinanciere     : Année financière dans laquelle les coûts de production sera débitées (format : AAAA-AA).
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """
        
        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'typeProduit')
        
        if (len(typeTravail) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'typeTravail')
        
        if (len(anneeFinanciere) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'anneeFinanciere')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, typeTravail, anneeFinanciere, codeEquipe, etatLot, noGroupe, noCpc, codeExecutant, noContrat, noContact, noTicket, note):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un lot pour un produit donné.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        typeProduit     : Type de produit associé au lot.
        typeTravail     : Type de travail à effetuer sur tous les identifiants du lot. Doit être prédéfini préalablement dans SIB.
        anneeFinanciere : Année financière où la production a commencée (format : AAAA-AA).
        codeEquipe      : Code de l'équipe qui effectue le travail.
        etatLot         : État du lot [A:en préparation /C:prêt pour la production /T:terminé].
        noGroupe        : Numéro de groupe associé au numéro de lot. Il est possible de spécifier plusieurs groupes 
                          séparés par des virgules (01, 02, 03). Il est également possible d'ajouter pour chaque groupe
                          énoncé la date de réception (01+YYYY-MM-DD) ou (01+YYYY-MM-DD, 02+YYYY-MM-DD, 03+YYYY-MM-DD).
        noCpc           : Numéro de CPC pour le contrôle des coûts.
        codeExecutant   : Code du contractant à qui le contrat a été octroyé.
        noContrat       : Numéro de contrat.
        noContact       : Numéro de contact, chez le contractant, responsable du lot.
        noTicket        : Numéro de ticket.
        note            : Note attachée au lot à créer.
        
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
        noLot           : Numéro de lot créé.
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")  
        
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS','PLAN'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")
        
        #Appel du service de transaction SIB qui initialise l'ajout d'un lot
        arcpy.AddMessage("- Appel du service SIB : P0608_LOT.pu_Ajouter_Lot")
        codeRetour = oSib.cursor.callfunc("P0608_LOT.pu_Ajouter_Lot", cx_Oracle.STRING, [sUsagerSib, typeProduit, typeTravail, anneeFinanciere, codeEquipe, noCpc, codeExecutant, noContrat, noContact, noTicket, note])
        
        #Vérifier le succès du service SIB 
        if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
            #Traiter tous les numéros de groupe dans le lot préalablement initialisé
            for record_groupe in noGroupe.split(","):
                list_item_record_groupe = record_groupe.split("+")
                dt_recep = None
                groupe = list_item_record_groupe[0]
                if len(list_item_record_groupe) > 1:
                    dt_recep = list_item_record_groupe[1]
                #Appel du service de transaction SIB qui ajoute un numéro de groupe dans le lot préalablement initialisé
                arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Ajouter_Groupe : [" + groupe + ", " + str(dt_recep) + "]")
                codeRetour = oSib.cursor.callfunc('P0608_lot.pu_Ajouter_Groupe', cx_Oracle.STRING, [groupe, dt_recep])
            
            #Vérifier le succès du service SIB 
            if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                #appel du service de transaction SIB qui finalise l'ajout du lot et retour du numéro de lot créé
                noLot = oSib.cursor.var(cx_Oracle.STRING)  #définir la zone-mémoire où est emmagasinée la valeur de la variable noLot
                codeRetour = oSib.cursor.callfunc('P0608_lot.pu_Ajouter_Termine', cx_Oracle.STRING, [noLot])
                
                #Vérifier le succès du service SIB 
                if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                    #récupération de l'étampe temporelle du lot préalablement créée
                    requete = "select updt_fld from f601_lo where no_lot ='%s'" % (noLot.getvalue())
                    arcpy.AddMessage("  " + requete)
                    oSib.cursor.execute(requete)
                    etampe = oSib.cursor.fetchone() [0]
                    arcpy.AddMessage("  Étampe temporelle : %s" %etampe)
                    
                    #appel du service de transaction SIB qui modifie l'état du lot préalablement créé
                    arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Modifier_Etat_Lot")
                    codeRetour = oSib.cursor.callfunc('P0608_lot.pu_Modifier_Etat_Lot', cx_Oracle.STRING, [sUsagerSib, noLot, etatLot, etampe])
                    
                    #Vérifier le succès du service SIB 
                    if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) <> 1:
                        #Extraire le nombre de message
                        nbMessSib = oSib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
                        count = 1
                        #Extraire tous les messages
                        message = []
                        while nbMessSib >= count:
                            #Extraire un message
                            messageSib = oSib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                            message.append(messageSib)
                            count += 1
                        #Retourner le message d'erreur
                        raise Exception(message)
                
                #la finalisation de l'ajout du lot n'a pas réussie
                else:
                    #Extraire le nombre de message
                    nbMessSib = oSib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
                    count = 1
                    #Extraire tous les messages
                    message = []
                    while nbMessSib >= count:
                        messageSib = oSib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                        message.append(messageSib)
                        count += 1
                    #Retourner le message d'erreur
                    raise Exception(message)
                
            #l'ajout du groupe n'a pas réussie
            else:
                #Extraire le nombre de message
                nbMessSib = oSib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
                count = 1
                #Extraire tous les messages
                message = []
                while nbMessSib >= count:
                    messageSib = oSib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                    message.append(messageSib)
                    count += 1
                #Retourner le message d'erreur
                raise Exception(message)
        
        #l'initialisation de l'ajout d'un lot n'a pas réussi
        else:
            #Extraire le nombre de message
            nbMessSib = oSib.cursor.callfunc('P0008_err.pu_nombre_messages', cx_Oracle.NUMBER, [codeRetour])
            count = 1
            #Extraire tous les messages
            message = []
            while nbMessSib >= count:
                messageSib = oSib.cursor.callfunc('P0008_ERR.pu_extraire_message', cx_Oracle.STRING, [codeRetour, count, 'F'])
                message.append(messageSib)
                count += 1
            raise Exception(message)
         
        #Fermeture de la connexion de la BD SIB  
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()
        
        #Sortir et retourner le numéro de lot
        return noLot.getvalue()

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env              = "SIB_PRO"
        typeProduit      = ""
        typeTravail      = ""
        anneeFinanciere  = ""
        codeEquipe       = "AUTRE"
        codeExecutant    = "CITS"
        noContact        = "4"
        noGroupe         = "01"
        etatLot          = "C"
        noContrat        = ""
        noCpc            = ""
        noTicket         = ""
        note             = ""
        fichierLog       = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            typeTravail = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            anneeFinanciere = sys.argv[4]
        
        if len(sys.argv) > 5:
            codeEquipe = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            codeExecutant = sys.argv[6].upper()
        
        if len(sys.argv) > 7:
            noContact = sys.argv[7].split(":")[0]
        
        if len(sys.argv) > 8:
            noGroupe = str(sys.argv[8])
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                noContrat = sys.argv[9]
        
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                noCpc = sys.argv[10]
        
        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                noTicket = sys.argv[11]
        
        if len(sys.argv) > 12:
            if sys.argv[12] <> "#":
                note = sys.argv[12]
        
        # Définir l'objet de création d'un numéro de lot.
        oCreerLotProduction = CreerLotProduction()
        
        #Valider les paramètres obligatoires
        oCreerLotProduction.validerParamObligatoire(env, typeProduit, typeTravail, anneeFinanciere)
        
        # Exécuter le traitement d'un numéro de lot.
        noLot = oCreerLotProduction.executer(env, typeProduit, typeTravail, anneeFinanciere, codeEquipe, etatLot, noGroupe, noCpc, codeExecutant, noContrat, noContact, noTicket, note)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Afficher le noLot=
        arcpy.AddMessage("  noLOT=")
        arcpy.SetParameterAsText(12, "")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("- Succès du traitement")
    #Afficher le noLot
    arcpy.AddMessage("  noLOT=%s" %noLot)
    arcpy.SetParameterAsText(12, noLot)
    #Sortir sans code d'erreur
    sys.exit(0)