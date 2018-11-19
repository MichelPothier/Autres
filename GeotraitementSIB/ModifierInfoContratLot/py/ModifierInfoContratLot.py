#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierInfoContratLot.py
# Auteur    : Michel Pothier
# Date      : 23 juin 2016

"""
    Application qui permet de modifier l'information de lots et de groupe à partir d'un numéro de contrat.
    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    typeTravail        OB     Type de travail à effectuer sur tous les identifiants du lot, préalablement défini dans SIB.
                              défaut = ""
    noSecteur          OB     Liste des numéros de secteur correspondant à un numéro de contrat temporaire en production.
                              défaut = ""
    noContrat          OB     Numéro de contrat.
                              défaut = ""
    executant          OB     Code du contractant à qui le contrat est octroyé.
                              défaut = ""
    contact            OB     Numéro de contact, chez le contractant, responsable du lot.
                              défaut = ""
    noTicket           OB     Numéro de bon de commande du système E-Procurment utilisé pour les travaux à l'externe.
                              défaut = ""
    dateDebut          OB     Date de début de traitement du lot.
                              défaut = ""
    dateFin            OB     Date de fin de traitement du lot.
                              défaut = ""
    infoLot            OB     Information sur le prix du contrat et la date de réception pour chaque lot du contrat.
                              défaut = ""
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierInfoContratLot.py env typeTravail 

    Exemple:
        ModifierInfoContratLot.py SIB_PRO 

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierInfoContratLot.py 2074 2016-07-19 16:01:20Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback
from datetime import datetime

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierInfoContratLot(object):
#*******************************************************************************************
    """
    Permet de modifier l'information de lot et de groupe à partir d'un numéro de contrat.
    
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
    def validerParamObligatoire(self, env, typeTravail, noSecteur, noContrat, executant, contact, noTicket, dateDebut, dateFin, infoLot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        typeTravail     : Type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
        noSecteur       : Liste des numéros de secteur correspondant au numéro de contrat temporaire.
        noContrat       : Numéro de contrat.
        executant       : Code du contractant à qui le contrat a été octroyé.
        contact         : Numéro de contact, chez le contractant, responsable du lot.
        noTicket        : Numéro de ticket.
        dateDebut       : Date de début de traitement du lot.
        dateFin         : Date de fin de traitement du lot.
        infoLot         : Information sur le prix du contrat et la date de réception pour chaque lot du contrat.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(typeTravail) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'typeTravail')
        
        if (len(noSecteur) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noSecteur')
        
        if (len(codeExecutant) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'codeExecutant')
        
        if (len(noContact) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noContact')
        
        if (len(noTicket) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'noTicket')
        
        if (len(dateDebut) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'dateDebut')
        
        if (len(dateFin) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'dateFin')
        
        if (len(infoLot) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'infoLot')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self,env, typeTravail, noSecteur, noContrat, codeExecutant, noContact, noTicket, dateDebut, dateFin, infoLot):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'information de lot et de groupe à partir d'un numéro de contrat.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        typeTravail     : Type de travail à effetuer sur tous les identifiants du lot, préalablement défini dans SIB.
        noSecteur       : Liste des numéros de secteur correspondant au numéro de contrat temporaire.
        noContrat       : Numéro de contrat.
        executant       : Code du contractant à qui le contrat a été octroyé.
        contact         : Numéro de contact, chez le contractant, responsable du lot.
        noTicket        : Numéro de ticket.
        dateDebut       : Date de début de traitement du lot.
        dateFin         : Date de fin de traitement du lot.
        infoLot         : Information sur le prix du contrat et la date de réception pour chaque lot du contrat.
        
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
        #-------------------------------------------
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #Vérifier si l'usager SIB possède les privilège de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'PLAN' ou 'G-SYS'")
        
        #Valider le type de travail et les numéros de secteur en production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le type de travail et les numéros de secteur en production")
        sql = "SELECT DISTINCT NO_CONTRAT FROM F601_LO WHERE TY_TRAV='" + typeTravail + "' AND NO_CONTRAT IN ('" + noSecteur.replace(",", "','") + "') AND E_LOT <> 'T'"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier si le nombre de secteur correspond
        if len(resultat) <> len(noSecteur.split(",")):
            #Retourner une exception
            raise Exception(u"Les numéros de secteur sont invalides : " + str(resultat))
        
        #Valider la date de début
        dateDebut = dateDebut.split(" ")[0]
        if dateDebut != datetime.strptime(dateDebut, "%Y-%m-%d").strftime('%Y-%m-%d'):
            #Retourner une exception
            raise Exception(u"La date de début est invalide : " + dateDebut)
        #Valider la date de fin
        dateFin = dateFin.split(" ")[0]
        if dateFin != datetime.strptime(dateFin, "%Y-%m-%d").strftime('%Y-%m-%d'):
            #Retourner une exception
            raise Exception(u"La date de fin est invalide : " + dateFin)
        #Vérifier si la date de début est plus grande que la date de fin
        if dateDebut >= dateFin:
            #Retourner une exception
            raise Exception(u"La date de début est plus grande que la date de fin : " + dateDebut + ">=" + dateFin)
        
        #-------------------------------------------
        #Modifier l'information du lot de production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information pour le contrat en cours de production")
        #Définir la commande SQL de modification
        sql = "UPDATE F601_LO SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE"
        sql = sql + ", NO_CONTRAT='" + noContrat + "', CD_EXECU='" + codeExecutant + "', NO_CONTACT=" + noContact
        sql = sql + ", NO_TICKET='" + noTicket + "', DT_DEBUT=TO_DATE('" + dateDebut + "'), DT_FIN=TO_DATE('" + dateFin + "')"
        sql= sql + " WHERE NO_CONTRAT IN ('" + noSecteur.replace(",", "','") + "')"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #-------------------------------------------
        #Iniialiser la liste des lots entrés
        lotsEntres = []
        #afficher l'identifiant de l'élément
        arcpy.AddMessage("  ")
        arcpy.AddMessage("- Modifier l'information pour chaque lot en cours de production")
        #Traiter tous les éléments du RecorsSet
        for row in arcpy.da.SearchCursor(infoLot, ["NO_LOT", "PRIX_CONTRAT", "DT_RECEP"]):
            #afficher l'identifiant de l'élément
            arcpy.AddMessage("#" + str(row[0]) + " " + str(row[1]) + " '" + str(row[2]) + "'")
            
            #Conserver les lots entrés
            noLot = str(row[0])
            lotsEntres.append(noLot)
            
            #Valider le prix du contrat
            try:
                prixContrat = int(row[1])
            except:
                #Retourner une exception
                raise Exception(u"Le prix du contrat est invalide : " + str(row[1]))
            
            #Valider la date de réception
            dateRecep = str(row[2]).split(" ")[0]
            if dateRecep != datetime.strptime(dateRecep, "%Y-%m-%d").strftime('%Y-%m-%d'):
                #Retourner une exception
                raise Exception(u"La date de réception est invalide : " + dateRecep)
            
            #Valider le numéro de lot
            resultat = oSib.requeteSib("SELECT NO_LOT FROM F601_LO WHERE NO_LOT='" + noLot + "' AND NO_CONTRAT='" + noContrat + "'")
            #Vérifier si le numéro de lot est invalide
            if not resultat:
                #Retourner une exception
                raise Exception(u"Le numéro de lot est invalide : " + noLot)
            
            #Définir la commande SQL de modification
            sql = "UPDATE F601_LO SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, PRIX_CONTRAT=" + str(prixContrat)
            sql= sql + " WHERE NO_LOT='" + noLot + "'"
            arcpy.AddMessage(sql)
            oSib.execute(sql)
            
            #Définir la commande SQL de modification pour changer la date de réception
            sql = "UPDATE F601_GR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, DT_RECEP=TO_DATE('" + dateRecep + "')"
            sql= sql + " WHERE NO_LOT='" + noLot + "'"
            arcpy.AddMessage(sql)
            oSib.execute(sql)
            arcpy.AddMessage(" ")

        #Vérifier si aucun lot entré
        if len(lotsEntres) == 0:
            #Retourner une exception
            arcpy.AddWarning(u"ATTENTION : Aucun lot n'a été spécifié.")
            arcpy.AddMessage(" ")
            
        #-------------------------------------------
        #Initialiser la liste des lots absents
        arcpy.AddMessage("- Vérifier l'information pour tous les lots présents : " + str(lotsEntres))
        lotsAbsents = []
        sql = "SELECT NO_LOT FROM F601_LO WHERE NO_CONTRAT='" + noContrat + "'"
        arcpy.AddMessage(sql)
        #Définir la liste des types de travail
        resultat = oSib.requeteSib(sql)
        #Traiter tous les no_lot
        for noLot in resultat:
            #Vérifier si le noLot est absent la liste des lots entres
            if noLot[0] not in lotsEntres:
                #Conserver les lots absents
                lotsAbsents.append(noLot[0])
        
        #Vérifier si le noLot est présent dans la liste
        if len(lotsAbsents) > 0:
            #Retourner une exception
            arcpy.AddWarning(u"ATTENTION : Information absente pour les lots suivants : " + str(lotsAbsents))
        
        #-------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage(" ")
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
        typeTravail      = ""
        noSecteur        = ""
        noContrat        = ""
        codeExecutant    = ""
        noContact        = ""
        noTicket         = ""
        dateDebut        = ""
        dateFin          = ""
        infoLot          = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeTravail = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            noSecteur = sys.argv[3].replace(";",",")
        
        if len(sys.argv) > 4:
            noContrat = sys.argv[4]
        
        if len(sys.argv) > 5:
            codeExecutant = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            noContact = sys.argv[6].split(":")[0]
        
        if len(sys.argv) > 7:
            noTicket = sys.argv[7]
        
        if len(sys.argv) > 8:
            dateDebut = sys.argv[8]
        
        if len(sys.argv) > 9:
            dateFin = sys.argv[9]
        
        if len(sys.argv) > 10:
            infoLot = sys.argv[10]
        
        #Définir l'objet pour modifier l'information de lot et de groupe à partir d'un numéro de contrat.
        oModifierInfoContratLot = ModifierInfoContratLot()
        
        #Valider les paramètres obligatoires
        oModifierInfoContratLot.validerParamObligatoire(env, typeTravail, noSecteur, noContrat, codeExecutant, noContact, noTicket, dateDebut, dateFin, infoLot)
        
        #Exécuter le traitement modifier l'information de lot et de groupe à partir d'un numéro de contrat.
        oModifierInfoContratLot.executer(env, typeTravail, noSecteur, noContrat, codeExecutant, noContact, noTicket, dateDebut, dateFin, infoLot)
    
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