#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerTypeProduit.py
# Auteur    : Michel Pothier
# Date      : 5 janvier 2015

"""
    Application qui permet de créer un nouveau type de produit dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    produit         OB      Type de produit à créer.
                            défaut = 
    desc_fr         OB      Description en français du type de produit.
                            défaut = 
    desc_an         OB      Description en anglais du type de produit.
                            défaut =
    acronyme_fr     OB      Acronyme en français du type de produit.
                            défaut = 
    acronyme_an     OB      Acronyme en anglais du type de produit.
                            défaut =
    utilisation     OB      Type d'utilisation lié au produit.
                            défaut = ISO;PRODUCTION
    parametre       OB      Paramètres associés au produit.
                            défaut = MAP-LISTE-ENTITE;MAP-SANS-ED-VER
    catalogue       OB      Nom du catalogue présentement utilisé pour définir le produit, les classes et les éléments.
                            défaut = 
    decoupage       OB      Découpage utilisé pour segmenter les éléments du produit.
                            défaut = SANS-DECOUPAGE
    depot           OB      Nom du dépôt dans lequel le type de produit est situé.
                            défaut = INTEGRATED
    action          OP      Action à effectuer sur d'autres type de produit.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerTypeProduit.py env produit desc_fr desc_an acronyme_fr acronyme_an utilisation parametre catalogue decoupage depot action

    Exemple:
        CreerTypeProduit.py SIB_PRO ESSIM 'Modèle Intégré du Secteur des Sciences de la Terre' 'Earth Science Sector- Integrated Model' ESSIM ESSIM ISO;PRODUCTION MAP-SANS-ED-VER 1.0.0 SANS-DECOUPAGE INTEGRATED BNDT

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerTypeProduit.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerTypeProduit(object):
#*******************************************************************************************
    """
    Permet de créer un nouveau type de produit dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'un nouveau type de produit dans SIB.
        
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
    def validerParamObligatoire(self,env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        produit         : Type de produit à créer.
        desc_fr         : Description en français du type de produit.
        desc_an         : Description en anglais du type de produit.
        acronyme_fr     : Acronyme en français du type de produit.
        acronyme_an     : Acronyme en anglais du type de produit.
        utilisation     : Type d'utilisation lié au produit.
        parametre       : Paramètres associés au produit.
        catalogue       : Nom du catalogue présentement utilisé pour définir le produit, les classes et les éléments.
        decoupage       : Découpage utilisé pour segmenter les éléments du produit.
        depot           : Nom du dépôt dans lequel le type de produit est situé.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(produit) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'produit')

        if (len(desc_fr) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'desc_fr')

        if (len(desc_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'desc_an')

        if (len(acronyme_fr) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'acronyme_fr')

        if (len(acronyme_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'acronyme_an')

        if (len(utilisation) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'utilisation')

        if (len(parametre) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'parametre')

        if (len(catalogue) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'catalogue')

        if (len(decoupage) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'decoupage')

        if (len(depot) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'depot')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot,action):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'un nouveau type de produit dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        produit         : Type de produit à créer.
        desc_fr         : Description en français du type de produit.
        desc_an         : Description en anglais du type de produit.
        acronyme_fr     : Acronyme en français du type de produit.
        acronyme_an     : Acronyme en anglais du type de produit.
        utilisation     : Type d'utilisation lié au produit.
        parametre       : Paramètres associés au produit.
        catalogue       : Nom du catalogue présentement utilisé pour définir le produit, les classes et les éléments.
        decoupage       : Découpage utilisé pour segmenter les éléments du produit.
        depot           : Nom du dépôt dans lequel le type de produit est situé.
        action          : Action à effectuer sur d'autres type de produit.
        
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
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Valider si le type de produit est déjà présent
        arcpy.AddMessage("- Valider le type de produit")
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F000_PR WHERE TY_PRODUIT='" + produit + "'")
        #Vérifier si le type de produit est présent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("Le type de produit '" + produit + "' est déjà présent")
        
        #Valider si l'acronyme français est déjà présent
        arcpy.AddMessage("- Valider l'acronyme français")
        resultat = self.Sib.requeteSib("SELECT ACRONYME FROM F000_PR WHERE ACRONYME='" + acronyme_fr + "'")
        #Vérifier si l'acronyme français est présent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("L'acronyme français '" + acronyme_fr + "' est déjà présent")
        
        #Valider si l'acronyme anglais est déjà présent
        arcpy.AddMessage("- Valider l'acronyme anglais")
        resultat = self.Sib.requeteSib("SELECT ACRONYME_AN FROM F000_PR WHERE ACRONYME_AN='" + acronyme_an + "'")
        #Vérifier si l'acronyme anglais est présent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("L'acronyme anglais '" + acronyme_an + "' est déjà présent")        
        
        #Traiter le champ DIFFUSION
        if "DIFFUSION" in utilisation:
            diffusion = "1"
        else:
            diffusion = "0"
        #Traiter le champ ISO
        if "ISO" in utilisation:
            iso = "1"
        else:
            iso = "0"
        #Traiter le champ PRODUCTION
        if "PRODUCTION" in utilisation:
            production = "1"
        else:
            production = "0"
        #Traiter le champ STRATEGIE
        if "STRATEGIE" in utilisation:
            strategie = "1"
        else:
            strategie = "0"
        
        #Créer le type de produit
        arcpy.AddMessage("- Créer le type de produit")
        sql = "INSERT INTO F000_PR VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','" + desc_fr.replace("'", "''") + "','" + desc_an.replace("'", "''") + "'"
        sql = sql + "," + diffusion + "," + iso + "," + production + "," + strategie + ",'" + acronyme_fr + "','" + acronyme_an + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre MAP-LISTE-ENTITE
        if "MAP-LISTE-ENTITE" in parametre:
            valeur = "1"
        else:
            valeur = "0"
        sql = "INSERT INTO F008_PP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','MAP-LISTE-ENTITE','" +  valeur + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre MAP-SANS-ED-VER
        if "MAP-SANS-ED-VER" in parametre:
            valeur = "1"
        else:
            valeur = "0"
        sql = "INSERT INTO F008_PP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','MAP-SANS-ED-VER','" +  valeur + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre PRODUIT-OBLIGATOIRE-INVENTAIRE
        if "PRODUIT-OBLIGATOIRE-INVENTAIRE" in parametre:
            valeur = "1"
        else:
            valeur = "0"
        sql = "INSERT INTO F008_PP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','PRODUIT-OBLIGATOIRE-INVENTAIRE','" +  valeur + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre DECOUPAGE
        sql = "INSERT INTO F008_PP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','DECOUPAGE','" +  decoupage + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre DEPOT
        sql = "INSERT INTO F008_PP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','DEPOT','" +  depot + "')"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre ACTION
        if len(action) > 0:
            sql = "INSERT INTO F008_PP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','ACTION','" +  action + "')"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Traiter le parametre catalogue
        sql = "INSERT INTO F010_DP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','v200_in','normes',NULL,NULL,'" + catalogue + "',NULL,NULL,'C')"
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
        env         = "SIB_PRO"
        produit     = ""
        desc_fr     = ""
        desc_an     = ""
        acronyme_fr = ""
        acronyme_an = ""
        utilisation = "ISO;PRODUCTION"
        parametre   = "MAP-LISTE-ENTITE;MAP-SANS-ED-VER"
        catalogue   = ""
        decoupage   = "SANS-DECOUPAGE"
        depot       = "INTEGRATED"
        action      = ""
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            produit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            desc_fr = sys.argv[3]
        
        if len(sys.argv) > 4:
            desc_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            acronyme_fr = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            acronyme_an = sys.argv[6].upper()
                
        if len(sys.argv) > 7:
            utilisation = sys.argv[7].upper()
        
        if len(sys.argv) > 8:
            parametre = sys.argv[8].upper()
        
        if len(sys.argv) > 9:
            catalogue = sys.argv[9].upper()
        
        if len(sys.argv) > 10:
            decoupage = sys.argv[10].upper()
        
        if len(sys.argv) > 11:
            depot = sys.argv[11].upper()
        
        if len(sys.argv) > 12:
            if sys.argv[12] <> '#':
                action = sys.argv[12].upper()
        
        #Définir l'objet de création d'un nouveau type de produit dans SIB.
        oCreerTypeProduit = CreerTypeProduit()
        
        #Valider les paramètres obligatoires
        oCreerTypeProduit.validerParamObligatoire(env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot)
        
        #Exécuter le traitement de création d'un nouveau type de produit dans SIB.
        oCreerTypeProduit.executer(env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot,action)
    
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