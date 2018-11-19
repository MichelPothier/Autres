#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 03 août 2016

"""
    Application qui permet de modifier l'information relative aux codes d'élément topographique (entité de production) pour toutes les normes de la BDG.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    codeElem            OB      Code de l'élément topographique.
                                défaut = 
    descFrancais        OB      Description française du code de l'élément topographique.
                                défaut = 
    descAnglais         OB      Description anglaise du code de l'élément topographique.
                                défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierEntiteProduction.py env codeElem descFrancais descAnglais

    Exemple:
        ModifierEntiteProduction.py SIB_PRO "1000000" "Aire désignée point" "Designated area point"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEntiteProduction.py 2093 2016-08-17 13:56:20Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'information relative aux codes d'élément topographique
    (entité de production) pour toutes les normes de la BDG.
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
    def validerParamObligatoire(self, env, codeElem, descFrancais, descAnglais):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        codeElem            : Code de l'élément topographique.
        descFrancais        : Description française du code de l'élément topographique.
        descAnglais         : Description anglaise du code de l'élément topographique.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(codeElem) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'codeElem')
        
        if (len(descFrancais) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'descFrancais')
        
        if (len(descAnglais) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'descAnglais')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, codeElem, descFrancais, descAnglais):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'information relative aux codes d'élément topographique
        (entité de production) pour toutes les normes de la BDG.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        codeElem            : Code de l'élément topographique.
        descFrancais        : Description française du code de l'élément topographique.
        descAnglais         : Description anglaise du code de l'élément topographique.
        
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
        
        #---------------------------------------------------------------------
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #---------------------------------------------------------------------
        #Valider si le code d'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le code d'élément topographique ...")
        sql = "SELECT CD_ELEM_TOPO FROM F132_EB WHERE CD_ELEM_TOPO='" + codeElem + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"Le code de l'élément topographique est invalide : " + codeElem)
        
        #---------------------------------------------------------------------
        #Modifier l'information relative au code de l'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information relative au code de l'élément topographique ...")
        #Mettre la descFrancais en UTF-8
        descFrancais = unicode(descFrancais, "utf-8")
        #Mettre la descAnglais en UTF-8
        descAnglais = unicode(descAnglais, "utf-8")
        #Définir la commande pour modifier le code d'élément topographique
        sql = "UPDATE F132_EB SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, DESCR='" + descFrancais.replace("'","''") + "', DESCR_AN='" + descAnglais.replace("'","''") + "' WHERE CD_ELEM_TOPO='" + codeElem + "'"
        #Afficher la commande
        arcpy.AddMessage(sql)
        #Exécuter la commande
        self.Sib.execute(sql)
        
        #---------------------------------------------------------------------
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
        codeElem            = ""
        descFrancais        = ""
        descAnglais         = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            codeElem = sys.argv[2].split(" ")[0]
        
        if len(sys.argv) > 3:
            descFrancais = sys.argv[3]
        
        if len(sys.argv) > 4:
            descAnglais = sys.argv[4]
        
        #Définir l'objet pour modifier l'information relative aux codes d'élément topographique (entité de production) pour toutes les normes de la BDG.
        oModifierEntiteProduction = ModifierEntiteProduction()
        
        #Valider les paramètres obligatoires
        oModifierEntiteProduction.validerParamObligatoire(env, codeElem, descFrancais, descAnglais)
        
        #Exécuter le traitement pour modifier l'information relative aux codes d'élément topographique (entité de production) pour toutes les normes de la BDG.
        oModifierEntiteProduction.executer(env, codeElem, descFrancais, descAnglais)
    
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