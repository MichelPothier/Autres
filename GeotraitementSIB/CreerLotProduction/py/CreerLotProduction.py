#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerLotProduction.py
# Auteur    : Michel Pothier
# Date      : 23 septembre 2014

"""
    Application qui permet de cr�er un lot dans SIB selon un type de produit et un type de travail.
    
    Param�tres d'entr�e:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              d�faut = SIB_PRO
    typeProduit        OB     Type de produit associ� au lot.
    typeTravail        OB     Type de travail � effetuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
    anneeFinanciere    OB     Ann�e financi�re dans laquelle les co�ts de production sera d�bit�es (format : AAAA-AA).
    codeEquipe         OP     Code de l'�quipe qui effectue le travail.
                              d�faut = "AUTRE"
    codeExecutant      OP     Code du contractant � qui le contrat est octroy�.
                              d�faut = "CITS"
    noContact          OP     Num�ro de contact, chez le contractant, responsable du lot.
                              d�faut = "4"
    noGroupe           OP     Permet de sp�cifier le groupe ou la liste de groupes (s�par�s par des virgules) 
                              � cr�er dans le lot. Il est �galement possible d'ajouter pour chaque groupe
                              �nonc� la date de r�ception (01+YYYY-MM-DD) ou (01+YYYY-MM-DD, 02+YYYY-MM-DD, 03+YYYY-MM-DD).
                              D�faut = 01 (avec aucune date de r�ception)
    noContrat          OP     Num�ro de contrat.
                              d�faut = ""
    noCpc              OP     Num�ro de CPC pour le contr�le des co�ts.
                              d�faut = ""
    noTicket           OP     Num�ro de bon de commande du syst�me E-Procurment utilis� pour les travaux � l'externe.
                              d�faut = ""
    note               OP     Note explicative pour le lot.
                              d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    noLot   : Num�ro de lot cr��
    
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerLotProduction(object):
#*******************************************************************************************
    """
    Permet de cr�er un lot dans SIB selon un type de produit et un type de travail.
    
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
        
        # D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, typeProduit, typeTravail, anneeFinanciere):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit associ� au lot.
        typeTravail         : Type de travail � effetuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
        anneeFinanciere     : Ann�e financi�re dans laquelle les co�ts de production sera d�bit�es (format : AAAA-AA).
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """
        
        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'typeProduit')
        
        if (len(typeTravail) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'typeTravail')
        
        if (len(anneeFinanciere) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'anneeFinanciere')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, typeTravail, anneeFinanciere, codeEquipe, etatLot, noGroupe, noCpc, codeExecutant, noContrat, noContact, noTicket, note):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'un lot pour un produit donn�.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        typeProduit     : Type de produit associ� au lot.
        typeTravail     : Type de travail � effetuer sur tous les identifiants du lot. Doit �tre pr�d�fini pr�alablement dans SIB.
        anneeFinanciere : Ann�e financi�re o� la production a commenc�e (format : AAAA-AA).
        codeEquipe      : Code de l'�quipe qui effectue le travail.
        etatLot         : �tat du lot [A:en pr�paration /C:pr�t pour la production /T:termin�].
        noGroupe        : Num�ro de groupe associ� au num�ro de lot. Il est possible de sp�cifier plusieurs groupes 
                          s�par�s par des virgules (01, 02, 03). Il est �galement possible d'ajouter pour chaque groupe
                          �nonc� la date de r�ception (01+YYYY-MM-DD) ou (01+YYYY-MM-DD, 02+YYYY-MM-DD, 03+YYYY-MM-DD).
        noCpc           : Num�ro de CPC pour le contr�le des co�ts.
        codeExecutant   : Code du contractant � qui le contrat a �t� octroy�.
        noContrat       : Num�ro de contrat.
        noContact       : Num�ro de contact, chez le contractant, responsable du lot.
        noTicket        : Num�ro de ticket.
        note            : Note attach�e au lot � cr�er.
        
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
        noLot           : Num�ro de lot cr��.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD'")  
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS','PLAN'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        #Appel du service de transaction SIB qui initialise l'ajout d'un lot
        arcpy.AddMessage("- Appel du service SIB : P0608_LOT.pu_Ajouter_Lot")
        codeRetour = oSib.cursor.callfunc("P0608_LOT.pu_Ajouter_Lot", cx_Oracle.STRING, [sUsagerSib, typeProduit, typeTravail, anneeFinanciere, codeEquipe, noCpc, codeExecutant, noContrat, noContact, noTicket, note])
        
        #V�rifier le succ�s du service SIB 
        if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
            #Traiter tous les num�ros de groupe dans le lot pr�alablement initialis�
            for record_groupe in noGroupe.split(","):
                list_item_record_groupe = record_groupe.split("+")
                dt_recep = None
                groupe = list_item_record_groupe[0]
                if len(list_item_record_groupe) > 1:
                    dt_recep = list_item_record_groupe[1]
                #Appel du service de transaction SIB qui ajoute un num�ro de groupe dans le lot pr�alablement initialis�
                arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Ajouter_Groupe : [" + groupe + ", " + str(dt_recep) + "]")
                codeRetour = oSib.cursor.callfunc('P0608_lot.pu_Ajouter_Groupe', cx_Oracle.STRING, [groupe, dt_recep])
            
            #V�rifier le succ�s du service SIB 
            if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                #appel du service de transaction SIB qui finalise l'ajout du lot et retour du num�ro de lot cr��
                noLot = oSib.cursor.var(cx_Oracle.STRING)  #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable noLot
                codeRetour = oSib.cursor.callfunc('P0608_lot.pu_Ajouter_Termine', cx_Oracle.STRING, [noLot])
                
                #V�rifier le succ�s du service SIB 
                if oSib.cursor.callfunc('P0008_err.pu_succes', cx_Oracle.NUMBER, [codeRetour]) == 1:
                    #r�cup�ration de l'�tampe temporelle du lot pr�alablement cr��e
                    requete = "select updt_fld from f601_lo where no_lot ='%s'" % (noLot.getvalue())
                    arcpy.AddMessage("  " + requete)
                    oSib.cursor.execute(requete)
                    etampe = oSib.cursor.fetchone() [0]
                    arcpy.AddMessage("  �tampe temporelle : %s" %etampe)
                    
                    #appel du service de transaction SIB qui modifie l'�tat du lot pr�alablement cr��
                    arcpy.AddMessage("- Appel du service SIB : P0608_lot.pu_Modifier_Etat_Lot")
                    codeRetour = oSib.cursor.callfunc('P0608_lot.pu_Modifier_Etat_Lot', cx_Oracle.STRING, [sUsagerSib, noLot, etatLot, etampe])
                    
                    #V�rifier le succ�s du service SIB 
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
                
                #la finalisation de l'ajout du lot n'a pas r�ussie
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
                
            #l'ajout du groupe n'a pas r�ussie
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
        
        #l'initialisation de l'ajout d'un lot n'a pas r�ussi
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
        
        #Sortir et retourner le num�ro de lot
        return noLot.getvalue()

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
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

        #extraction des param�tres d'ex�cution
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
        
        # D�finir l'objet de cr�ation d'un num�ro de lot.
        oCreerLotProduction = CreerLotProduction()
        
        #Valider les param�tres obligatoires
        oCreerLotProduction.validerParamObligatoire(env, typeProduit, typeTravail, anneeFinanciere)
        
        # Ex�cuter le traitement d'un num�ro de lot.
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
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("- Succ�s du traitement")
    #Afficher le noLot
    arcpy.AddMessage("  noLOT=%s" %noLot)
    arcpy.SetParameterAsText(12, noLot)
    #Sortir sans code d'erreur
    sys.exit(0)