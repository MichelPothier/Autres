#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierListeEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 09 ao�t 2016

"""
    Application qui permet de modifier l'information relative aux listes de codes d'�l�ment topographique pour toutes les normes de la BDG.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    nom                 OB      Nom de la liste des codes de l'�l�ment topographique.
                                d�faut = 
    descFrancais        OB      Description fran�aise du nom de la liste des codes d'�l�ment topographique.
                                d�faut = 
    descAnglais         OB      Description anglaise du nom de la liste des codes d'�l�ment topographique.
                                d�faut =
    collActive          OB      Indique si la collision est active ou non pour les codes d'�l�ment topographique.
                                d�faut = 1:Oui
    listeCodes          OB      Liste des codes d'�l�ment topographique.
                                d�faut =
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierListeEntiteProduction.py env nom descFrancais descAnglais collActive listeCodes

    Exemple:
        ModifierListeEntiteProduction.py SIB_PRO "FORTMCMURRAY" "Liste des codes pour la mise � jour du secteur Fort McMurray" "List of codes for update FortMcMurray sector" "1:Oui" 10000001;10000002
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierListeEntiteProduction.py 2091 2016-08-17 13:54:27Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierListeEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'information relative aux listes de codes d'�l�ment topographique
    pour toutes les normes de la BDG.
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
    def validerParamObligatoire(self, env, nom, descFrancais, descAnglais, collActive, listeCodes):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        nom                 : Nom de la liste des codes de l'�l�ment topographique.
        descFrancais        : Description fran�aise du nom de la liste des codes d'�l�ment topographique.
        descAnglais         : Description anglaise du nom de la liste des codes d'�l�ment topographique.
        collActive          : Indique si la collision est active ou non pour les codes d'�l�ment topographique.
        listeCodes          : Liste des codes d'�l�ment topographique.
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')
        
        if (len(nom) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'nom')
        
        if (len(descFrancais) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'descFrancais')
        
        if (len(descAnglais) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'descAnglais')
        
        if (len(collActive) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'collActive')
        
        if (len(listeCodes) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'listeCodes')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, nom, descFrancais, descAnglais, collActive, listeCodes):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier une liste de codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG
        afin de facilit� la mise au programme d'un travail.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        nom                 : Nom de la liste des codes de l'�l�ment topographique.
        descFrancais        : Description fran�aise du nom de la liste des codes d'�l�ment topographique.
        descAnglais         : Description anglaise du nom de la liste des codes d'�l�ment topographique.
        collActive          : Indique si la collision est active ou non pour les codes d'�l�ment topographique.
        listeCodes          : Liste des codes d'�l�ment topographique.
        
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
        #Valider le nom de la liste des codes d'�l�ment topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le nom de la liste des codes d'�l�ment topographique ...")
        sql = "SELECT NOM_LISTE, DESCR, DESCR_AN FROM F134_NL WHERE NOM_LISTE='" + nom + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception(u"Le nom de la liste des codes d'�l�ment topographique est invalide : " + nom)
        
        #---------------------------------------------------------------------
        #Modifier l'information de la liste des codes d'�l�ment topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information de la liste des codes d'�l�ment topographique ...")
        #Mettre la descFrancais en UTF-8
        descFrancais = unicode(descFrancais, "utf-8")
        #Mettre la descAnglais en UTF-8
        descAnglais = unicode(descAnglais, "utf-8")
        #D�finir la commande pour modifier l'information de la liste
        sql = "UPDATE F134_NL SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, DESCR='" + descFrancais.replace("'","''") + "', DESCR_AN='" + descAnglais.replace("'","''") + "' WHERE NOM_LISTE='" + nom + "'"
        #Afficher la commande
        arcpy.AddMessage(sql)
        #Ex�cuter la commande
        self.Sib.execute(sql)
        
        #---------------------------------------------------------------------
        #Modifier la liste des codes d'�l�ment topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier la liste des codes d'�l�ment topographique ...")
        #Traiter tous les codes d'�l�ment topographique
        for code in listeCodes.split(","):
            #D�finir le code sans la description
            codeElem = code.replace("'","").split(" ")[0]
            
            #D�finir la commande pour modifier le code d'�l�ment topographique � la liste
            sql = "UPDATE F134_LE SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, COLLISION_ACTIVE=" + collActive + " WHERE NOM_LISTE='" + nom + "' AND CD_ELEM_TOPO='" + codeElem + "'"
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
        nom                 = ""
        descFrancais        = ""
        descAnglais         = ""
        collActive          = "1:Oui"
        listeCodes          = ""
        
        #Extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            nom = sys.argv[2].replace("'","").split(" ")[0].upper()
        
        if len(sys.argv) > 3:
            descFrancais = sys.argv[3]
        
        if len(sys.argv) > 4:
            descAnglais = sys.argv[4]
        
        if len(sys.argv) > 5:
            collActive = sys.argv[5].split(":")[0]
        
        if len(sys.argv) > 6:
            listeCodes = sys.argv[6].replace(";",",")
        
        #D�finir l'objet pour modifier une liste de codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG.
        oModifierListeEntiteProduction = ModifierListeEntiteProduction()
        
        #Valider les param�tres obligatoires
        oModifierListeEntiteProduction.validerParamObligatoire(env, nom, descFrancais, descAnglais, collActive, listeCodes)
        
        #Ex�cuter le traitement pour modifier une liste de codes d'�l�ment topographique (entit� de production) pour toutes les normes de la BDG.
        oModifierListeEntiteProduction.executer(env, nom, descFrancais, descAnglais, collActive, listeCodes)
    
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