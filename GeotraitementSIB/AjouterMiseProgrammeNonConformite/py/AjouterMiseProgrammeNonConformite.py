#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : AjouterMiseProgrammeNonConformite.py
# Auteur    : Michel Pothier
# Date      : 11 juillet 2016

"""
    Application qui permet d'ajouter une ou plusieurs mises au programme en production à une non-conformité active.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    nonConf             OB      Numéro de non-conformité à ajouter aux mises au programme.
                                défaut = 
    noMap               OB      Liste des mises au programme à ajouter à la non-conformité spécifiée.
                                défaut = 
    detruire            OP      Indique si on doit détruire ou non les mises au programme déjà ajoutées à la non-conformité.
                                défaut = False
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        AjouterMiseProgrammeNonConformite.py env nonConf noMap [detruire]

    Exemple:
        AjouterMiseProgrammeNonConformite.py SIB_PRO 03354 966721;966722;966723

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AjouterMiseProgrammeNonConformite.py 2138 2017-10-19 15:41:35Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class AjouterMiseProgrammeNonConformite:
#*******************************************************************************************
    """
    Classe qui permet d'ajouter une ou plusieurs mises au programme en production à une non-conformité active.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de mise au programme.
        
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
    def validerParamObligatoire(self, env, nonConf, noMap):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        nonConf             : Numéro de non-conformité à ajouter aux mises au programme.
        noMap               : Liste des mises au programme à ajouter à la non-conformité spécifiée.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(nonConf) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nonConf')
        
        if (len(noMap) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'noMap')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, nonConf, noMap, detruire):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour ajouter une ou plusieurs mises au programme en production à une non-conformité active.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        nonConf             : Numéro de non-conformité à ajouter aux mises au programme.
        noMap               : Liste des mises au programme à ajouter à la non-conformité spécifiée.
        detruire            : Indique si on doit détruire ou non les mises au programme déjà ajoutées à la non-conformité.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        
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
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")
        
        #Valider si le no_nc est valide
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le numéro de non-conformité ...")
        #Définir la commande SQL pour détruire les mises au programme liés à la non-conformité
        sql = "SELECT NO_NC FROM F702_NC WHERE NO_NC='" + nonConf + "' AND DATE_FERMETURE IS NULL"
        arcpy.AddMessage(sql)
        #Exécuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"Numéro de non-conformité invalide ou fermé : " + nonConf)

        #Vérifier si on doit détruire les mises au programme de la non-conformité
        if detruire:
            #Valider si le no_nc est valide
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Détruire les mises au programme liées à la non-conformité ...")
            #Extraire les mises au programme déjà liées à la non-conformité
            resultat = self.Sib.requeteSib("SELECT NO_MAP, NO_NC FROM F502_NC WHERE NO_NC='" + nonConf + "' ORDER BY NO_MAP")
            #Traiter tous les noMap
            for map in resultat:
                #Définir la commande SQL pour détruire les mises au programme liés à la non-conformité
                sql = "DELETE FROM F502_NC WHERE NO_NC='" + nonConf + "' AND NO_MAP=" + str(map[0])
                #Exécuter la commande SQL
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            
        #Ajouter les mises au programme à la non-conformité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les mises au programme à la non-conformité ..." )
        #Traiter toutes les mises au programme
        for map in noMap.split(","):
            #Définir le numéro de mise au programme
            no = map.replace("'","").split(" ")[0]
            #Définir la commande SQL pour vérifier si le noMAP est valide
            sql = "SELECT NO_MAP FROM F502_PS WHERE E_PLSNRC='P' AND NO_MAP=" + no
            #Exécuter la commande SQL
            resultat = self.Sib.requeteSib(sql)
            #Vérifier le résultat
            if not resultat:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception(u"Aucun numéro de mise au programme " + no + "n'est au programme actuellement !")
            
            #Définir la commande SQL pour vérifier si le noMAP est déjà ajouté à la non-conformité
            sql = "SELECT NO_MAP FROM F502_NC WHERE NO_NC='" + nonConf + "' AND NO_MAP=" + no
            #Exécuter la commande SQL
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si le résultat est présent
            if resultat:
                #Afficher l'avertissement
                arcpy.AddWarning("ATTENTION : La mise au programme " + no + " est déjà liée à la non-conformité " + nonConf)
            #Si aucun résultat
            else:
                #Initialiser la commande SQL pour ajouter les noMap à la nonConf
                sql = "INSERT INTO F502_NC (UPDT_FLD, ETAMPE, DT_C, DT_M, NO_MAP, NO_NC) "
                sql = sql + "VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, " + no + ", '" + nonConf + "')"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB   
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env                 = "SIB_PRO"
        nonConf             = ""
        noMap               = ""
        detruire            = False
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            nonConf = sys.argv[2].split(" ")[0]
        
        if len(sys.argv) > 3:
            noMap = sys.argv[3].replace(";",",")
            
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                detruire = sys.argv[4].upper() == "TRUE" 
        
        #Définir l'objet pour ajouter une ou plusieurs mises au programme en production à une non-conformité active.
        oAjouterMiseProgrammeNonConformite = AjouterMiseProgrammeNonConformite()
        
        #Valider les paramètres obligatoires
        oAjouterMiseProgrammeNonConformite.validerParamObligatoire(env, nonConf, noMap)
        
        #Exécuter le traitement pour ajouter une ou plusieurs mises au programme en production à une non-conformité active.
        oAjouterMiseProgrammeNonConformite.executer(env, nonConf, noMap, detruire)
    
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