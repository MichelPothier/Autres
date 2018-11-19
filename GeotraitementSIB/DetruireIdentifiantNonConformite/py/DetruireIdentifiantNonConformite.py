#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireIdentifiantNonConformite.py
# Auteur    : Michel Pothier
# Date      : 13 septembre 2016

"""
    Application qui permet de détruire un ou plusieurs identifiants d'une non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.

    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    no_nc              OB     Liste des numéros de non-conformité à détruire selon les types de produits spécifiés qui sont non traitées et non fermées.
                              défaut = 
                              Exemple:
                              "NO_NC:TYPE_NC:TY_PRODUIT:#COUNT(IDENTIFIANT):TITRE"
                              "03024:PP:TOPORAMA:#1:Commission de certaines occurrences d'entité Cours d'eau"
    identifiants       OB     Liste des identifiants de la non-conformité à détruire.
                              défaut = 
                              Exemple:
                              "IDENTIFIANT: TY_PRODUIT, ED.VER_DEBUT, ED.VER_FIN"
                              "021M07: BDG, 10.0, 99999.99"
                              
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireIdentifiantNonConformite.py env ty_produit no_nc

    Exemple:
        DetruireIdentifiantNonConformite.py SIB_PRO "DNEC:#2;None:#1"  "03115:PA:None:#1Modifier l'étiquette;02818:PP:DNEC:#45:Erreur de précision;02748:PP:DNEC:#23:Erreur d'élévation"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireIdentifiantNonConformite.py 2116 2016-09-15 16:52:46Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireIdentifiantNonConformite(object):
#*******************************************************************************************
    """
    Permet de détruire un ou plusieurs identifiants d'une non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire un ou plusieurs identifiants d'une non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        
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
    def validerParamObligatoire(self, env, no_nc, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Liste des numéros de non-conformité à détruire selon les types de produits spécifiés qui sont non traitées et non fermées.
        identifiants    : Liste des identifiants de la non-conformité à détruire.
        
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
        
        if (len(identifiants) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'identifiants')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire un ou plusieurs identifiants d'une non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Liste des numéros de non-conformité à détruire selon les types de produits spécifiés qui sont non traitées et non fermées.
        identifiants    : Liste des identifiants de la non-conformité à détruire.
        
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
        
        #-----------------------------------------------------------------
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #-----------------------------------------------------------------
        #Afficher le message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation du numéro de non-conformité ...")
        #Définir le no_nc
        noNc = no_nc.split(":")[0]
        #Valider si le NO_NC est valide
        sql = "SELECT NO_NC, DATE_FERMETURE, DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + noNc + "'"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier si le NO_NC est absent
        if not resultat:
            #Retourner une exception
            raise Exception("Le NO_NC est absent de la table F702_NC : " + noNc)
        #Vérifier si le NO_NC est fermé ou traité
        if not (str(resultat[0][1]) == "None" and str(resultat[0][2]) == "None"):
            #Retourner une exception
            raise Exception("Le NO_NC est fermé ou traité : " + str(resultat))

        #-----------------------------------------------------------------
        #Afficher le message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Détruire les identifiants de la non-conformité ...")
        #Traiter tous les identifiants de la non-conformité
        for id in identifiants.split(","):
            #Définir l'identifiant
            identifiant = id.split(":")[0]
            #Détruire les identifiants du NO_NC dans la table F705_PR
            sql = "SELECT * FROM F705_PR WHERE NO_NC='" + noNc + "' AND IDENTIFIANT='" + identifiant + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Détruire le NO_NC
                sql = "DELETE F705_PR WHERE NO_NC='" + noNc + "' AND IDENTIFIANT='" + identifiant + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
                #Afficher les données
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
            #Si le NO_NC est absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning(" Aucun identifiant n'est présent dans la table F705_PR")
            #Message de séparation
            arcpy.AddMessage(" ")
         
        #-----------------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #-----------------------------------------------------------------
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
        identifiants     = ""
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2]
        
        if len(sys.argv) > 3:
            identifiants = sys.argv[3].replace(";",",").replace("'","")
        
        #Définir l'objet pour détruire un ou plusieurs identifiants d'une non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireIdentifiantNonConformite = DetruireIdentifiantNonConformite()
        
        #Valider les paramètres obligatoires
        oDetruireIdentifiantNonConformite.validerParamObligatoire(env, no_nc, identifiants)
        
        #Exécuter le traitement pour détruire un ou plusieurs identifiants d'une non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireIdentifiantNonConformite.executer(env, no_nc, identifiants)
        
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