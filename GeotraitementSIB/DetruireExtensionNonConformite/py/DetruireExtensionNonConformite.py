#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireExtensionNonConformite.py
# Auteur    : Michel Pothier
# Date      : 01 septembre 2015

"""
    Application qui permet de d�truire une ou plusieurs extensions d'une non-conformit� qui ne poss�dent pas de date de traitement et de date de fermeture.

    
    Param�tres d'entr�e:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              d�faut = SIB_PRO
    no_nc              OB     Num�ro de non-conformit� poss�dant une ou plusieurs Extensions � d�truire qui sont non trait�es et non ferm�es.
                              d�faut = Aucun
                              Exemple:
                              "NO_NC:TYPE_NC:TITRE"
                              "03024:PP:Commission de certaines occurrences d'entit� Cours d'eau"
    date_ech           OB     Dates d'�ch�ance de l'extension � d�truire pour une non-conformit�.
                              d�faut = Aucun
                              Exemple:
                              "DATE_ECH:RESP_ECH:NOTE"
                              "2016-03-15: OTROTTIE: Non prioritaire"
                              
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireExtensionNonConformite.py env no_nc

    Exemple:
        DetruireExtensionNonConformite.py SIB_PRO "03024:PP:Commission de certaines occurrences d'entit� Cours d'eau" "2016-03-15:OTROTTIE:Non prioritaire;2016-05-15:OTROTTIE:Non prioritaire"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireExtensionNonConformite.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireExtensionNonConformite(object):
#*******************************************************************************************
    """
    Permet de d�truire une ou plusieurs extensions d'une non-conformit� qui ne poss�dent pas de date de traitement et de date de fermeture.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire une ou plusieurs extensions d'une non-conformit� qui ne poss�dent pas de date de traitement et de date de fermeture.
        
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
    def validerParamObligatoire(self, env, no_nc, date_ech):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Num�ro de non-conformit� poss�dant une ou plusieurs Extensions � d�truire qui sont non trait�es et non ferm�es.
        date_ech        : Dates d'�ch�ance de l'extension � d�truire pour une non-conformit�.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')
        
        if (len(no_nc) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'no_nc')
        
        if (len(date_ech) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'date_ech')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, date_ech):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire une ou plusieurs extensions d'une non-conformit� qui ne poss�dent pas de date de traitement et de date de fermeture.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Num�ro de non-conformit� poss�dant une ou plusieurs Extensions � d�truire qui sont non trait�es et non ferm�es.
        date_ech        : Dates d'�ch�ance de l'extension � d�truire pour une non-conformit�.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'ISO-RQNC'")
        
        #V�rification du num�ro de non-conformit�
        arcpy.AddMessage("- V�rification de la non-conformit� : " + no_nc)
        noNc = no_nc.split(":")[0]
        #Valider si le NO_NC est valide
        sql = ("SELECT DISTINCT NC.NO_NC, NC.DATE_FERMETURE, NC.DATE_TRAITEMENT"
               "  FROM F702_NC NC, F703_EX EX"
               " WHERE EX.TYPE_ISO='NC' AND NC.NO_NC=EX.NO_ENREG AND EX.NO_ENREG='" + noNc + "'")
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #V�rifier si le NO_NC est absent
        if not resultat:
            #Retourner une exception
            raise Exception("Le NO_NC est absent de la table F703_EX : " + noNc)
        #V�rifier si le NO_NC est ferm� ou trait�
        if not (str(resultat[0][1]) == "None" and str(resultat[0][2]) == "None"):
            #Retourner une exception
            raise Exception("Le NO_NC est ferm� ou trait� : " + str(resultat))
        #Afficher les donn�es
        arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
        
        #Traiter toutes les extensions � d�truire
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
            #V�rifier si le NO_NC est absent
            if not resultat:
                #Retourner une exception
                raise Exception("L'extension est absente de la table F703_EX : " + str(ech))

            #Afficher les donn�es
            arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
            #D�truire l'extension du NO_NC
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env              = "SIB_PRO"
        no_nc            = ""
        date_ech         = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].replace("'","")
        
        if len(sys.argv) > 3:
            date_ech = sys.argv[3].replace("'","")
        
        #D�finir l'objet pour d�truire une ou plusieurs extensions d'une non-conformit� qui ne poss�dent pas de date de traitement et de date de fermeture.
        oDetruireExtensionNonConformite = DetruireExtensionNonConformite()
        
        #Valider les param�tres obligatoires
        oDetruireExtensionNonConformite.validerParamObligatoire(env, no_nc, date_ech)
        
        #Ex�cuter le traitement pour d�truire une ou plusieurs extensions d'une non-conformit� qui ne poss�dent pas de date de traitement et de date de fermeture.
        oDetruireExtensionNonConformite.executer(env, no_nc, date_ech)
        
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