#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 03 ao�t 2016

"""
    Application qui permet de modifier l'information relative aux codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    codeElem            OB      Code de l'�l�ment topographique.
                                d�faut = 
    descFrancais        OB      Description fran�aise du code de l'�l�ment topographique.
                                d�faut = 
    descAnglais         OB      Description anglaise du code de l'�l�ment topographique.
                                d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierEntiteProduction.py env codeElem descFrancais descAnglais

    Exemple:
        ModifierEntiteProduction.py SIB_PRO "1000000" "Aire d�sign�e point" "Designated area point"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEntiteProduction.py 2093 2016-08-17 13:56:20Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'information relative aux codes d'�l�ment topographique
    (entit� de production) pour toutes les normes de la BDG.
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
    def validerParamObligatoire(self, env, codeElem, descFrancais, descAnglais):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        codeElem            : Code de l'�l�ment topographique.
        descFrancais        : Description fran�aise du code de l'�l�ment topographique.
        descAnglais         : Description anglaise du code de l'�l�ment topographique.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')
        
        if (len(codeElem) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'codeElem')
        
        if (len(descFrancais) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'descFrancais')
        
        if (len(descAnglais) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'descAnglais')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, codeElem, descFrancais, descAnglais):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier l'information relative aux codes d'�l�ment topographique
        (entit� de production) pour toutes les normes de la BDG.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        codeElem            : Code de l'�l�ment topographique.
        descFrancais        : Description fran�aise du code de l'�l�ment topographique.
        descAnglais         : Description anglaise du code de l'�l�ment topographique.
        
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
        
        #---------------------------------------------------------------------
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #---------------------------------------------------------------------
        #Valider si le code d'�l�ment topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le code d'�l�ment topographique ...")
        sql = "SELECT CD_ELEM_TOPO FROM F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"Le code de l'�l�ment topographique est invalide : " + codeElem)
        
        #---------------------------------------------------------------------
        #Modifier l'information relative au code de l'�l�ment topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information relative au code de l'�l�ment topographique ...")
        #Mettre la descFrancais en UTF-8
        descFrancais = unicode(descFrancais, "utf-8")
        #Mettre la descAnglais en UTF-8
        descAnglais = unicode(descAnglais, "utf-8")
        #D�finir la commande pour modifier le code d'�l�ment topographique
        sql = "UPDATE F132_EB SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, DESCR='" + descFrancais.replace("'","''") + "', DESCR_AN='" + descAnglais.replace("'","''") + "' WHERE CD_ELEM_TOPO='" + codeElem + "'"
        #Afficher la commande
        arcpy.AddMessage(sql)
        #Ex�cuter la commande
        self.Sib.execute(sql)
        
        #---------------------------------------------------------------------
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
        codeElem            = ""
        descFrancais        = ""
        descAnglais         = ""
        
        #extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            codeElem = sys.argv[2].split(" ")[0]
        
        if len(sys.argv) > 3:
            descFrancais = sys.argv[3]
        
        if len(sys.argv) > 4:
            descAnglais = sys.argv[4]
        
        #D�finir l'objet pour modifier l'information relative aux codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG.
        oModifierEntiteProduction = ModifierEntiteProduction()
        
        #Valider les param�tres obligatoires
        oModifierEntiteProduction.validerParamObligatoire(env, codeElem, descFrancais, descAnglais)
        
        #Ex�cuter le traitement pour modifier l'information relative aux codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG.
        oModifierEntiteProduction.executer(env, codeElem, descFrancais, descAnglais)
    
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