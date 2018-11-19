#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireErratumNonConformite.py
# Auteur    : Michel Pothier
# Date      : 31 août 2015

"""
    Application qui permet de détruire l'erratum d'une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.

    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    no_nc              OB     Liste des numéros de non-conformité possédant un Erratum à détruire qui sont non traitées et non fermées.
                              défaut = Aucun
                              Exemple:
                              "NO_NC:TYPE_NC:ERRATUM:TITRE"
                              "03024:PP:Pas d'outil pour corriger le fichier.:Commission de certaines occurrences d'entité Cours d'eau"
                              
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireErratumNonConformite.py env no_nc

    Exemple:
        DetruireErratumNonConformite.py SIB_PRO "03115:PA:Pas d'outil pour corriger le fichier.:Modifier l'étiquette;02748:PP:Pas d'outil pour corriger le fichier.:Erreur d'élévation"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireErratumNonConformite.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireErratumNonConformite(object):
#*******************************************************************************************
    """
    Permet de détruire l'erratum d'une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire l'erratum d'une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        
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
        no_nc           : Liste des numéros de non-conformité possédant un Erratum à détruire qui sont non traitées et non fermées.
        
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
        Exécuter le traitement pour détruire l'erratum d'une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Liste des numéros de non-conformité possédant un Erratum à détruire qui sont non traitées et non fermées.
        
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
        
        #Traiter tous les NO_NC à détruire
        for nc in no_nc.split(";"):
            #Afficher le message
            noNc = nc.split(":")[0]
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Destruction de l'Erratum du NO_NC : " + nc)
            #Valider si le NO_NC est valide
            sql = ("SELECT NC.NO_NC, NC.DATE_FERMETURE, NC.DATE_TRAITEMENT"
                   "  FROM F702_NC NC, F702_ER ER"
                   " WHERE NC.NO_NC=ER.NO_NC AND ER.NO_NC='" + noNc + "'")
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier si le NO_NC est absent
            if not resultat:
                #Retourner une exception
                raise Exception("Le NO_NC est absent de la table F702_ER : " + noNc)
            #Vérifier si le NO_NC est fermé ou traité
            if not (str(resultat[0][1]) == "None" and str(resultat[0][2]) == "None"):
                #Retourner une exception
                raise Exception("Le NO_NC est fermé ou traité : " + str(resultat))
            #Afficher les données
            arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
            
            #Détruire la NO_NC dans la table F702_ER (Erratum)
            sql = "SELECT * FROM F702_ER WHERE NO_NC='" + noNc + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
                #Détruire le NO_NC
                sql = "DELETE F702_ER WHERE NO_NC='" + noNc + "'"
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
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].replace("'","")
        
        #Définir l'objet pour détruire l'erratum d'une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireErratumNonConformite = DetruireErratumNonConformite()
        
        #Valider les paramètres obligatoires
        oDetruireErratumNonConformite.validerParamObligatoire(env, no_nc)
        
        #Exécuter le traitement pour détruire l'erratum d'une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireErratumNonConformite.executer(env, no_nc)
        
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