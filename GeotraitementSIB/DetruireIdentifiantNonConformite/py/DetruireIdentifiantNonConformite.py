#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireIdentifiantNonConformite.py
# Auteur    : Michel Pothier
# Date      : 13 septembre 2016

"""
    Application qui permet de d�truire un ou plusieurs identifiants d'une non-conformit�s qui ne poss�dent pas de date de traitement et de date de fermeture.

    
    Param�tres d'entr�e:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              d�faut = SIB_PRO
    no_nc              OB     Liste des num�ros de non-conformit� � d�truire selon les types de produits sp�cifi�s qui sont non trait�es et non ferm�es.
                              d�faut = 
                              Exemple:
                              "NO_NC:TYPE_NC:TY_PRODUIT:#COUNT(IDENTIFIANT):TITRE"
                              "03024:PP:TOPORAMA:#1:Commission de certaines occurrences d'entit� Cours d'eau"
    identifiants       OB     Liste des identifiants de la non-conformit� � d�truire.
                              d�faut = 
                              Exemple:
                              "IDENTIFIANT: TY_PRODUIT, ED.VER_DEBUT, ED.VER_FIN"
                              "021M07: BDG, 10.0, 99999.99"
                              
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        DetruireIdentifiantNonConformite.py env ty_produit no_nc

    Exemple:
        DetruireIdentifiantNonConformite.py SIB_PRO "DNEC:#2;None:#1"  "03115:PA:None:#1Modifier l'�tiquette;02818:PP:DNEC:#45:Erreur de pr�cision;02748:PP:DNEC:#23:Erreur d'�l�vation"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireIdentifiantNonConformite.py 2116 2016-09-15 16:52:46Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class DetruireIdentifiantNonConformite(object):
#*******************************************************************************************
    """
    Permet de d�truire un ou plusieurs identifiants d'une non-conformit�s qui ne poss�dent pas de date de traitement et de date de fermeture.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour d�truire un ou plusieurs identifiants d'une non-conformit�s qui ne poss�dent pas de date de traitement et de date de fermeture.
        
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
    def validerParamObligatoire(self, env, no_nc, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Liste des num�ros de non-conformit� � d�truire selon les types de produits sp�cifi�s qui sont non trait�es et non ferm�es.
        identifiants    : Liste des identifiants de la non-conformit� � d�truire.
        
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
        
        if (len(identifiants) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'identifiants')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, identifiants):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour d�truire un ou plusieurs identifiants d'une non-conformit�s qui ne poss�dent pas de date de traitement et de date de fermeture.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        no_nc           : Liste des num�ros de non-conformit� � d�truire selon les types de produits sp�cifi�s qui sont non trait�es et non ferm�es.
        identifiants    : Liste des identifiants de la non-conformit� � d�truire.
        
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
        
        #-----------------------------------------------------------------
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'ISO-RQNC'")
        
        #-----------------------------------------------------------------
        #Afficher le message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation du num�ro de non-conformit� ...")
        #D�finir le no_nc
        noNc = no_nc.split(":")[0]
        #Valider si le NO_NC est valide
        sql = "SELECT NO_NC, DATE_FERMETURE, DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + noNc + "'"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #V�rifier si le NO_NC est absent
        if not resultat:
            #Retourner une exception
            raise Exception("Le NO_NC est absent de la table F702_NC : " + noNc)
        #V�rifier si le NO_NC est ferm� ou trait�
        if not (str(resultat[0][1]) == "None" and str(resultat[0][2]) == "None"):
            #Retourner une exception
            raise Exception("Le NO_NC est ferm� ou trait� : " + str(resultat))

        #-----------------------------------------------------------------
        #Afficher le message
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�truire les identifiants de la non-conformit� ...")
        #Traiter tous les identifiants de la non-conformit�
        for id in identifiants.split(","):
            #D�finir l'identifiant
            identifiant = id.split(":")[0]
            #D�truire les identifiants du NO_NC dans la table F705_PR
            sql = "SELECT * FROM F705_PR WHERE NO_NC='" + noNc + "' AND IDENTIFIANT='" + identifiant + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #V�rifier le r�sultat
            if resultat:
                #D�truire le NO_NC
                sql = "DELETE F705_PR WHERE NO_NC='" + noNc + "' AND IDENTIFIANT='" + identifiant + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
                #Afficher les donn�es
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
            #Si le NO_NC est absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning(" Aucun identifiant n'est pr�sent dans la table F705_PR")
            #Message de s�paration
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env              = "SIB_PRO"
        no_nc            = ""
        identifiants     = ""
        
        #Extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2]
        
        if len(sys.argv) > 3:
            identifiants = sys.argv[3].replace(";",",").replace("'","")
        
        #D�finir l'objet pour d�truire un ou plusieurs identifiants d'une non-conformit�s qui ne poss�dent pas de date de traitement et de date de fermeture.
        oDetruireIdentifiantNonConformite = DetruireIdentifiantNonConformite()
        
        #Valider les param�tres obligatoires
        oDetruireIdentifiantNonConformite.validerParamObligatoire(env, no_nc, identifiants)
        
        #Ex�cuter le traitement pour d�truire un ou plusieurs identifiants d'une non-conformit�s qui ne poss�dent pas de date de traitement et de date de fermeture.
        oDetruireIdentifiantNonConformite.executer(env, no_nc, identifiants)
        
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