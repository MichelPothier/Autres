#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireExtensionNonConformite.py
# Auteur    : Michel Pothier
# Date      : 01 septembre 2015

"""
    Application qui permet de détruire une ou plusieurs extensions d'une non-conformité qui ne possèdent pas de date de traitement et de date de fermeture.

    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    no_nc              OB     Numéro de non-conformité possédant une ou plusieurs Extensions à détruire qui sont non traitées et non fermées.
                              défaut = Aucun
                              Exemple:
                              "NO_NC:TYPE_NC:TITRE"
                              "03024:PP:Commission de certaines occurrences d'entité Cours d'eau"
    date_ech           OB     Dates d'échéance de l'extension à détruire pour une non-conformité.
                              défaut = Aucun
                              Exemple:
                              "DATE_ECH:RESP_ECH:NOTE"
                              "2016-03-15: OTROTTIE: Non prioritaire"
                              
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireExtensionNonConformite.py env no_nc

    Exemple:
        DetruireExtensionNonConformite.py SIB_PRO "03024:PP:Commission de certaines occurrences d'entité Cours d'eau" "2016-03-15:OTROTTIE:Non prioritaire;2016-05-15:OTROTTIE:Non prioritaire"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireExtensionNonConformite.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireExtensionNonConformite(object):
#*******************************************************************************************
    """
    Permet de détruire une ou plusieurs extensions d'une non-conformité qui ne possèdent pas de date de traitement et de date de fermeture.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire une ou plusieurs extensions d'une non-conformité qui ne possèdent pas de date de traitement et de date de fermeture.
        
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
    def validerParamObligatoire(self, env, no_nc, date_ech):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Numéro de non-conformité possédant une ou plusieurs Extensions à détruire qui sont non traitées et non fermées.
        date_ech        : Dates d'échéance de l'extension à détruire pour une non-conformité.
        
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
        
        if (len(date_ech) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'date_ech')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, date_ech):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire une ou plusieurs extensions d'une non-conformité qui ne possèdent pas de date de traitement et de date de fermeture.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Numéro de non-conformité possédant une ou plusieurs Extensions à détruire qui sont non traitées et non fermées.
        date_ech        : Dates d'échéance de l'extension à détruire pour une non-conformité.
        
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
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #Vérification du numéro de non-conformité
        arcpy.AddMessage("- Vérification de la non-conformité : " + no_nc)
        noNc = no_nc.split(":")[0]
        #Valider si le NO_NC est valide
        sql = ("SELECT DISTINCT NC.NO_NC, NC.DATE_FERMETURE, NC.DATE_TRAITEMENT"
               "  FROM F702_NC NC, F703_EX EX"
               " WHERE EX.TYPE_ISO='NC' AND NC.NO_NC=EX.NO_ENREG AND EX.NO_ENREG='" + noNc + "'")
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier si le NO_NC est absent
        if not resultat:
            #Retourner une exception
            raise Exception("Le NO_NC est absent de la table F703_EX : " + noNc)
        #Vérifier si le NO_NC est fermé ou traité
        if not (str(resultat[0][1]) == "None" and str(resultat[0][2]) == "None"):
            #Retourner une exception
            raise Exception("Le NO_NC est fermé ou traité : " + str(resultat))
        #Afficher les données
        arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
        
        #Traiter toutes les extensions à détruire
        for ech in date_ech.split(";"):
            #Afficher le message
            date = ech.split(":")[0]
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Destruction de l'Extension : str(ech)")
            #Valider si le NO_NC est valide
            sql = ("SELECT *"
                   "  FROM F703_EX"
                   " WHERE TYPE_ISO='NC' AND NO_ENREG='" + noNc + "' AND DATE_ECH='" + date + "'")
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier si le NO_NC est absent
            if not resultat:
                #Retourner une exception
                raise Exception("L'extension est absente de la table F703_EX : " + str(ech))

            #Afficher les données
            arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
            #Détruire l'extension du NO_NC
            sql = ("DELETE F703_EX"
                   " WHERE TYPE_ISO='NC' AND NO_ENREG='" + noNc + "' AND DATE_ECH='" + date + "'")
            arcpy.AddMessage(sql)
            oSib.execute(sql)
         
        #Accepter les modifications
        arcpy.AddMessage(" ")
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
        no_nc            = ""
        date_ech         = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].replace("'","")
        
        if len(sys.argv) > 3:
            date_ech = sys.argv[3].replace("'","")
        
        #Définir l'objet pour détruire une ou plusieurs extensions d'une non-conformité qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireExtensionNonConformite = DetruireExtensionNonConformite()
        
        #Valider les paramètres obligatoires
        oDetruireExtensionNonConformite.validerParamObligatoire(env, no_nc, date_ech)
        
        #Exécuter le traitement pour détruire une ou plusieurs extensions d'une non-conformité qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireExtensionNonConformite.executer(env, no_nc, date_ech)
        
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