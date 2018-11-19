#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireDateFermetureNonConformite.py
# Auteur    : Michel Pothier
# Date      : 15 septembre 2016

"""
    Application qui permet de détruire la date de fermeture pour une ou plusieurs non-conformités fermées.
    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    no_nc              OB     Liste des numéros de non-conformité fermées.
                              défaut = 
                              Exemple:
                              "NO_NC:TYPE_NC:TY_PRODUIT:#COUNT(IDENTIFIANT):TITRE"
                              "03024:PP:TOPORAMA:#1:Commission de certaines occurrences d'entité Cours d'eau"
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireDateFermetureNonConformite.py env no_nc

    Exemple:
        DetruireDateFermetureNonConformite.py SIB_PRO "03115:PA:None:#1:Modifier l'étiquette;02818:PP:DNEC:#45:Erreur de précision;02748:PP:DNEC:#23:Erreur d'élévation"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireDateFermetureNonConformite.py 2122 2016-09-15 17:07:29Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireDateFermetureNonConformite(object):
#*******************************************************************************************
    """
    Permet de détruire la date de fermeture pour une ou plusieurs non-conformités fermées.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire la date de fermeture pour une ou plusieurs non-conformités fermées.
        
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
    def validerParamObligatoire(self, env, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Liste des numéros de non-conformité fermées.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(no_nc) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'no_nc')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire la date de fermeture pour une ou plusieurs non-conformités fermées.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Liste des numéros de non-conformité fermées.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #------------------------------------------------------
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #------------------------------------------------------
        #Traiter tous les NO_NC
        for nc in no_nc.split(";"):
            #Afficher le message
            noNC = nc.split(":")[0]
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Destruction de la date de fermeture pour la NO_NC : " + noNC)
            
            #Extraire la date de fermeture de la NC
            sql = "SELECT DATE_FERMETURE FROM F702_NC WHERE NO_NC='" + noNC + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier si le NO_NC est absent
            if not resultat:
                #Retourner une exception
                raise Exception(u"Le NO_NC est absent de la table F702_NC : " + noNC)
            
            #Vérifier si le NO_NC est non fermé
            if str(resultat[0][0]) == "None":
                #Afficher le message
                arcpy.AddWarning("La date de fermeture est déjà détruite!")
            #Si la date de fermeture est présente
            else:
                #Afficher la date de fermeture
                arcpy.AddWarning("Date de fermeture : " + str(resultat[0][0]))
                #Mettre la valeur NULL pour la date de fermeture de la non-conformité
                sql = "UPDATE F702_NC SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DATE_FERMETURE=NULL WHERE NO_NC='" + noNC + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
        
        #------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #------------------------------------------------------
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
        no_nc            = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].replace("'","")
        
        #Définir l'objet pour détruire la date de fermeture pour une ou plusieurs non-conformités fermées.
        oDetruireDateFermetureNonConformite = DetruireDateFermetureNonConformite()
        
        #Valider les paramètres obligatoires
        oDetruireDateFermetureNonConformite.validerParamObligatoire(env, no_nc)
        
        #Exécuter le traitement pour détruire la date de fermeture pour une ou plusieurs non-conformités fermées.
        oDetruireDateFermetureNonConformite.executer(env, no_nc)
        
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