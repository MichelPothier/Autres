#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierLienNonConformite.py
# Auteur    : Michel Pothier
# Date      : 19 septembre 2016

"""
    Application qui permet de modifier les liens d'une non-conformit� avec d'autres non-conformit�s.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    no_nc                   Num�ro de non-conformit� � modifier.
                            d�faut = 
    lien_nc         OP      La liste des num�ros de non-conformit� en lien avec celui trait�.
                            d�faut =
                            ATTENTION : Si aucun lien n'est sp�cifi�, aucun lien ne sera pr�sent.
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierLienNonConformite.py env no_nc lien_nc

    Exemple:
        ModifierLienNonConformite.py SIB_PRO 3034 3031,3032

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierLienNonConformite.py 2127 2016-09-19 15:32:57Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierLienNonConformite(object):
#*******************************************************************************************
    """
    Permet de modifier les liens d'une non-conformit� avec d'autres non-conformit�s.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier les liens d'une non-conformit� avec d'autres non-conformit�s.
        
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
    def validerParamObligatoire(self, env, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � modifier.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(no_nc) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'no_nc')
        
        #Sortir
        return
        
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, lien_nc):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier les liens d'une non-conformit� avec d'autres non-conformit�s.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � modifier.
        lien_nc         : La liste des num�ros de non-conformit� en lien avec celui � cr�er.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #------------------------------------------------------
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'ISO-RQNC'")
        
        #------------------------------------------------------
        #Valider si la non-conformit� est absente
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si la non-conformit� est pr�sente")
        sql = "SELECT NO_NC,DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + no_nc + "' AND DATE_FERMETURE IS NULL"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception("La non-conformit� '" + no_nc + "' n'existe pas ou est ferm�e")
        #V�rifier la date de traitement
        if str(resultat[0][1]) <> "None":
            #Retourner un AVERTISSEMENT
            arcpy.AddWarning("Attention : La date de traitement est pr�sente : " + str(resultat[0][1]))
        
        #------------------------------------------------------
        #Extraire les liens entre les non-conformit�s
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire les liens entre les non-conformit�s ...")
        listeLienConserver = []
        #Extraire les liens
        sql = "SELECT NO_NC FROM F704_LI WHERE NO_ACTION='" + no_nc + "' AND TY_LIEN='NC'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Retourner un AVERTISSEMENT
        arcpy.AddWarning("Nombre de lien(s) d�j� pr�sent(s) : " + str(len(resultat)))
        arcpy.AddWarning(str(resultat))
        
        #------------------------------------------------------
        #D�truire les liens entre les non-conformit�s
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�truire les liens entre les non-conformit�s ...")
        #Initialiser le nombre de liens d�truits
        nbLienDet = 0
        #Afficher les liens
        for nc in resultat:
            #V�rifier si le lien doit �tre d�truit
            if nc[0] not in lien_nc:
                #Afficher et ex�cuter la commande
                sql = "DELETE F704_LI WHERE NO_ACTION='" + no_nc + "' AND NO_NC='" + nc[0] + "' AND TY_LIEN='NC'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
                #Compter le nombre de liens d�truits
                nbLienDet = nbLienDet + 1
            #Si le lien est � conserver
            else:
                #Cr�er la liste des liens � conserver
                listeLienConserver.append(nc[0])
        #V�rifier le nombre de liens d�truits
        if nbLienDet == 0:
            #Retourner un AVERTISSEMENT
            arcpy.AddWarning("Attention : Aucun Lien n'a �t� d�truit!")
        
        #------------------------------------------------------
        #Cr�er les liens entre les non-conformit�s
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les liens entre les non-conformit�s ...")
        #Initialiser le nombre de liens d�truits
        nbLienAdd = 0
        #V�rifier la pr�sence des liens entre les NC
        if len(lien_nc) > 0:
            #Traiter tous les liens entre les non-conformit�s
            for lien in lien_nc.split(","):
                #V�rifier si le lien doit �tre ajout�
                if lien.split(":")[0] not in listeLienConserver:
                    #Compter le nombre de liens ajout�s
                    nbLienAdd = nbLienAdd + 1
                    #Ajouter un identifiant du produit non-conforme
                    sql = "INSERT INTO F704_LI VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + lien.split(":")[0] + "',P0G03_UTL.PU_HORODATEUR,'NC')"
                    arcpy.AddMessage(sql)
                    self.Sib.execute(sql)
        #V�rifier le nombre de liens ajout�s
        if nbLienAdd == 0:
            #Retourner un AVERTISSEMENT
            arcpy.AddWarning("Attention : Aucun Lien n'a �t� ajout�!")
        
        #------------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env             = "SIB_PRO"
        no_nc           = ""
        lien_nc         = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            if sys.argv[3] <> "#":
                lien_nc = (sys.argv[3].replace(";",",")).replace("'","")
        
        #D�finir l'objet pour modifier les liens d'une non-conformit� avec d'autres non-conformit�s.
        oModifierLienNonConformite = ModifierLienNonConformite()
        
        #Valider les param�tres obligatoires
        oModifierLienNonConformite.validerParamObligatoire(env, no_nc)
        
        #Ex�cuter le traitement pour modifier les liens d'une non-conformit� avec d'autres non-conformit�s.
        oModifierLienNonConformite.executer(env, no_nc, lien_nc)   

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