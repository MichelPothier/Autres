#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : CreerListeEntiteProduction.py
# Auteur    : Michel Pothier
# Date      : 09 août 2016

"""
    Application qui permet de créer une nouvelle liste de codes d'élément topographique (entité de production) pour toutes les normes de la BDG
    afin de facilité la mise au programme d'un travail.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    nom                 OB      Nom de la liste des codes de l'élément topographique.
                                défaut = 
    descFrancais        OB      Description française du nom de la liste des codes d'élément topographique.
                                défaut = 
    descAnglais         OB      Description anglaise du nom de la liste des codes d'élément topographique.
                                défaut =
    collActive          OB      Indique si la collision est active ou non pour les codes d'élément topographique.
                                défaut = 1:Oui
    listeCodes          OB      Liste des codes d'élément topographique.
                                défaut =
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerListeEntiteProduction.py env nom descFrancais descAnglais collActive listeCodes

    Exemple:
        CreerListeEntiteProduction.py SIB_PRO "FORTMCMURRAY" "Liste des codes pour la mise à jour du secteur Fort McMurray" "List of codes for update FortMcMurray sector" "1:Oui" 10000001;10000002
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerListeEntiteProduction.py 2089 2016-08-17 13:50:25Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerListeEntiteProduction:
#*******************************************************************************************
    """
    Classe qui permet de créer une nouvelle liste de codes d'élément topographique (entité de production) pour toutes les normes de la BDG
    afin de facilité la mise au programme d'un travail.
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
    def validerParamObligatoire(self, env, nom, descFrancais, descAnglais, collActive, listeCodes):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        nom                 : Nom de la liste des codes de l'élément topographique.
        descFrancais        : Description française du nom de la liste des codes d'élément topographique.
        descAnglais         : Description anglaise du nom de la liste des codes d'élément topographique.
        collActive          : Indique si la collision est active ou non pour les codes d'élément topographique.
        listeCodes          : Liste des codes d'élément topographique.
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'env')
        
        if (len(nom) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'nom')
        
        if (len(descFrancais) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'descFrancais')
        
        if (len(descAnglais) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'descAnglais')
        
        if (len(collActive) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'collActive')
        
        if (len(listeCodes) == 0):
            raise Exception(u"Paramètre obligatoire manquant: %s" %'listeCodes')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, nom, descFrancais, descAnglais, collActive, listeCodes):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour créer une nouvelle liste de codes d'élément topographique (entité de production) pour toutes les normes de la BDG
        afin de facilité la mise au programme d'un travail.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        nom                 : Nom de la liste des codes de l'élément topographique.
        descFrancais        : Description française du nom de la liste des codes d'élément topographique.
        descAnglais         : Description anglaise du nom de la liste des codes d'élément topographique.
        collActive          : Indique si la collision est active ou non pour les codes d'élément topographique.
        listeCodes          : Liste des codes d'élément topographique.
        
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
        #Valider le nom de la liste des codes d'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le nom de la liste des codes d'élément topographique ...")
        sql = "SELECT NOM_LISTE, DESCR, DESCR_AN FROM F134_NL WHERE NOM_LISTE='" + nom + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if resultat:
            #Retourner une exception
            raise Exception(u"Le nom de la liste des codes d'élément topographique est déjà présent : " + nom + " : " + resultat[0][1] + " : " + resultat[0][2])
        
        #---------------------------------------------------------------------
        #Créer la nouvelle liste des codes d'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Créer la nouvelle liste des codes d'élément topographique ...")
        #Mettre la descFrancais en UTF-8
        descFrancais = unicode(descFrancais, "utf-8")
        #Mettre la descAnglais en UTF-8
        descAnglais = unicode(descAnglais, "utf-8")
        #Définir la commande pour créer le nouveau code d'élément topographique
        sql = "INSERT INTO F134_NL VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, '" + nom + "', '" + descFrancais.replace("'","''") + "', '" + descAnglais.replace("'","''") + "')"
        #Afficher la commande
        arcpy.AddMessage(sql)
        #Exécuter la commande
        self.Sib.execute(sql)
        
        #---------------------------------------------------------------------
        #Créer la nouvelle liste des codes d'élément topographique
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter les codes d'élément topographique à la liste ...")
        #Traiter tous les codes d'élément topographique
        for code in listeCodes.split(","):
            #Définir le code sans la description
            codeElem = code.replace("'","").split(" ")[0]
            
            #Définir la commande pour ajouter le code d'élément topographique à la liste
            sql = "INSERT INTO F134_LE VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, '" + nom + "', '" + codeElem + "', " + collActive + ")"
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
        nom                 = ""
        descFrancais        = ""
        descAnglais         = ""
        collActive          = "1:Oui"
        listeCodes          = ""
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            nom = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            descFrancais = sys.argv[3]
        
        if len(sys.argv) > 4:
            descAnglais = sys.argv[4]
        
        if len(sys.argv) > 5:
            collActive = sys.argv[5].split(":")[0]
        
        if len(sys.argv) > 6:
            listeCodes = sys.argv[6].replace(";",",")
        
        #Définir l'objet pour créer une nouvelle liste de codes d'élément topographique (entité de production) pour toutes les normes de la BDG.
        oCreerListeEntiteProduction = CreerListeEntiteProduction()
        
        #Valider les paramètres obligatoires
        oCreerListeEntiteProduction.validerParamObligatoire(env, nom, descFrancais, descAnglais, collActive, listeCodes)
        
        #Exécuter le traitement pour créer une nouvelle liste de codes d'élément topographique (entité de production) pour toutes les normes de la BDG.
        oCreerListeEntiteProduction.executer(env, nom, descFrancais, descAnglais, collActive, listeCodes)
    
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