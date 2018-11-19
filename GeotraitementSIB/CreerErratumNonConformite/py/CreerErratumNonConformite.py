#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerErratumNonConformite.py
# Auteur    : Michel Pothier
# Date      : 6 janvier 2015

"""
    Application qui permet de créer un Erratum pour un numéro de non-conformité dans SIB.

    Un seul Erratum est permis pour un numéro de non-conformité.    
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    no_nc           OB      Numéro de non-conformité pour lequel on veut ajouter un Erratum.
                            défaut = 
    desc_fr         OB      La description en français de l'Erratum pour la non-conformité.
                            défaut = 
    desc_an         OB      La description en anglais de l'Erratum pour la non-conformité.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerErratumNonConformite.py env no_nc desc_fr desc_an

    Exemple:
        CreerErratumNonConformite.py SIB_PRO 03645 'Description en français de l'erratum' 'Description en anglais de l'erratum'

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerErratumNonConformite.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerErratumNonConformite(object):
#*******************************************************************************************
    """
    Permet de créer un Erratum pour un numéro de non-conformité dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'un erratum pour un numéro de non-conformité dans SIB.
        
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
    def validerParamObligatoire(self,env,no_nc,desc_fr,desc_an):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité pour lequel on veut ajouter un Erratum.
        desc_fr         : La description en français de l'Erratum pour la non-conformité.
        desc_an         : La description en anglais de l'Erratum pour la non-conformité.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(no_nc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'no_nc')
        
        if (len(desc_fr) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'desc_fr')
        
        if (len(desc_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'desc_an')
 
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,no_nc,desc_fr,desc_an):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un erratum pour un numéro de non-conformité dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité pour lequel on veut ajouter un Erratum.
        desc_fr         : La description en français de l'Erratum pour la non-conformité.
        desc_an         : La description en anglais de l'Erratum pour la non-conformité.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        
        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #Valider le numéro de la non-conformité
        arcpy.AddMessage("- Valider le numéro de non-conformité")
        sql = "SELECT NO_NC FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le numéro de non-conformité '" + resultat[0][0] + "' est absent")
        
        #Valider si l'erratum est déjà présent
        arcpy.AddMessage("- Valider la présence du erratum")
        sql = "SELECT DESCR FROM F702_ER WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("Le erratum est déjà présent : " + resultat[0][0])
        
        #Vérifier si la longueur est respectée
        desc_fr = unicode(desc_fr, "utf-8")
        if len(desc_fr) > 4000:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'desc_fr' dépasse 4000 catactètes, longueur=" + str(len(desc_fr)))
        
        #Vérifier si la longueur est respectée
        desc_an = unicode(desc_an, "utf-8")
        if len(desc_an) > 4000:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'desc_an' dépasse 4000 catactètes, longueur=" + str(len(desc_an)))
        
        #Créer le erratum du numéro de non-conformité
        arcpy.AddMessage("- Créer un erratum pour le numéro de non-conformité")
        sql = "INSERT INTO F702_ER VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,P0G03_UTL.PU_HORODATEUR,'" + no_nc + "','" + desc_fr.replace("'", "''") + "','" + desc_an.replace("'", "''") + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env     = "SIB_PRO"
        no_nc   = ""
        desc_fr = ""
        desc_an = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            desc_fr = sys.argv[3]
         
        if len(sys.argv) > 4:
            desc_an = sys.argv[4]
        
        #Définir l'objet de création d'un erratum pour un numéro de non-conformité dans SIB.
        oCreerErratumNonConformite = CreerErratumNonConformite()
        
        #Valider les paramètres obligatoires
        oCreerErratumNonConformite.validerParamObligatoire(env,no_nc,desc_fr,desc_an)
        
        #Exécuter le traitement de création d'un erratum pour un numéro de non-conformité dans SIB.
        oCreerErratumNonConformite.executer(env,no_nc,desc_fr,desc_an)   
        
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