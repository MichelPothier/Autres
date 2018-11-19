#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : AjouterMiseProgrammeNonConformite.py
# Auteur    : Michel Pothier
# Date      : 11 juillet 2016

"""
    Application qui permet d'ajouter une ou plusieurs mises au programme en production � une non-conformit� active.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    nonConf             OB      Num�ro de non-conformit� � ajouter aux mises au programme.
                                d�faut = 
    noMap               OB      Liste des mises au programme � ajouter � la non-conformit� sp�cifi�e.
                                d�faut = 
    detruire            OP      Indique si on doit d�truire ou non les mises au programme d�j� ajout�es � la non-conformit�.
                                d�faut = False
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class AjouterMiseProgrammeNonConformite:
#*******************************************************************************************
    """
    Classe qui permet d'ajouter une ou plusieurs mises au programme en production � une non-conformit� active.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de mise au programme.
        
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
    def validerParamObligatoire(self, env, nonConf, noMap):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        nonConf             : Num�ro de non-conformit� � ajouter aux mises au programme.
        noMap               : Liste des mises au programme � ajouter � la non-conformit� sp�cifi�e.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(nonConf) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nonConf')
        
        if (len(noMap) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'noMap')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, nonConf, noMap, detruire):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour ajouter une ou plusieurs mises au programme en production � une non-conformit� active.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        nonConf             : Num�ro de non-conformit� � ajouter aux mises au programme.
        noMap               : Liste des mises au programme � ajouter � la non-conformit� sp�cifi�e.
        detruire            : Indique si on doit d�truire ou non les mises au programme d�j� ajout�es � la non-conformit�.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS','PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        #Valider si le no_nc est valide
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le num�ro de non-conformit� ...")
        #D�finir la commande SQL pour d�truire les mises au programme li�s � la non-conformit�
        sql = "SELECT NO_NC FROM F702_NC WHERE NO_NC='" + nonConf + "' AND DATE_FERMETURE IS NULL"
        arcpy.AddMessage(sql)
        #Ex�cuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"Num�ro de non-conformit� invalide ou ferm� : " + nonConf)

        #V�rifier si on doit d�truire les mises au programme de la non-conformit�
        if detruire:
            #Valider si le no_nc est valide
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- D�truire les mises au programme li�es � la non-conformit� ...")
            #Extraire les mises au programme d�j� li�es � la non-conformit�
            resultat = self.Sib.requeteSib("SELECT NO_MAP, NO_NC FROM F502_NC WHERE NO_NC='" + nonConf + "' ORDER BY NO_MAP")
            #Traiter tous les noMap
            for map in resultat:
                #D�finir la commande SQL pour d�truire les mises au programme li�s � la non-conformit�
                sql = "DELETE FROM F502_NC WHERE NO_NC='" + nonConf + "' AND NO_MAP=" + str(map[0])
                #Ex�cuter la commande SQL
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            
        #Ajouter les mises au programme � la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les mises au programme � la non-conformit� ..." )
        #Traiter toutes les mises au programme
        for map in noMap.split(","):
            #D�finir le num�ro de mise au programme
            no = map.replace("'","").split(" ")[0]
            #D�finir la commande SQL pour v�rifier si le noMAP est valide
            sql = "SELECT NO_MAP FROM F502_PS WHERE E_PLSNRC='P' AND NO_MAP=" + no
            #Ex�cuter la commande SQL
            resultat = self.Sib.requeteSib(sql)
            #V�rifier le r�sultat
            if not resultat:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception(u"Aucun num�ro de mise au programme " + no + "n'est au programme actuellement !")
            
            #D�finir la commande SQL pour v�rifier si le noMAP est d�j� ajout� � la non-conformit�
            sql = "SELECT NO_MAP FROM F502_NC WHERE NO_NC='" + nonConf + "' AND NO_MAP=" + no
            #Ex�cuter la commande SQL
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si le r�sultat est pr�sent
            if resultat:
                #Afficher l'avertissement
                arcpy.AddWarning("ATTENTION : La mise au programme " + no + " est d�j� li�e � la non-conformit� " + nonConf)
            #Si aucun r�sultat
            else:
                #Initialiser la commande SQL pour ajouter les noMap � la nonConf
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
        
        #Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB   
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env                 = "SIB_PRO"
        nonConf             = ""
        noMap               = ""
        detruire            = False
        
        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet pour ajouter une ou plusieurs mises au programme en production � une non-conformit� active.
        oAjouterMiseProgrammeNonConformite = AjouterMiseProgrammeNonConformite()
        
        #Valider les param�tres obligatoires
        oAjouterMiseProgrammeNonConformite.validerParamObligatoire(env, nonConf, noMap)
        
        #Ex�cuter le traitement pour ajouter une ou plusieurs mises au programme en production � une non-conformit� active.
        oAjouterMiseProgrammeNonConformite.executer(env, nonConf, noMap, detruire)
    
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