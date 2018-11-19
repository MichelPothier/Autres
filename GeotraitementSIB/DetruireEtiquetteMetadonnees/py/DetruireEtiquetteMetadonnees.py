#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireEtiquetteMetadonnees.py
# Auteur    : Michel Pothier
# Date      : 06 octobre 2015

"""
    Application qui permet de détruire une étiquette de métadonnées dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    ty_produit      OB      Type de produit de l'étiquette.
                            défaut = 
    cd_champ        OB      Code du champ de l'étiquette.
                            défaut =
    cd_valeur       OB      Code de valeur de l'étiquette.
                            défaut = 
    desc_fr         OB      Description française de l'étiquette.
                            défaut =
    desc_an         OB      Description anglaise de l'étiquette.
                            défaut = 
    desc_pna_fr     OP      Description PNA française de l'étiquette.
                            défaut =
    desc_pna_an     OP      Description PNA anglaise de l'étiquette.
                            défaut =
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
    	DetruireEtiquetteMetadonnees.py env ty_produit cd_champ cd_valeur
    Exemple:
        DetruireEtiquetteMetadonnees.py "SIB_PRO" "GENERAL" "address" "CITS_ADDRESS"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireEtiquetteMetadonnees.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ExceptionDetruireEtiquetteMetadonnees(Exception):
#*******************************************************************************************
    """
    Classe d'exception dérivée de la classe Exception pour gèrer un problème
    dans l'exécution du programme.
    
    Lors de l'instanciation, passez une chaîne de caractère en argument
    pour d'écrire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class DetruireEtiquetteMetadonnees(object):
#*******************************************************************************************
    """
    Permet de détruire une étiquette de métadonnées dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire une étiquette de métadonnées.
        
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
    def validerParamObligatoire(self,env,ty_produit,cd_champ,cd_valeur):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        ty_produit      : Type de produit de l'étiquette.
        cd_champ        : Code du champ de l'étiquette.
        cd_valeur       : Code de valeur de l'étiquette.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise ExceptionDetruireEtiquetteMetadonnees("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(ty_produit) == 0):
            raise ExceptionDetruireEtiquetteMetadonnees("Paramètre obligatoire manquant: %s" %'ty_produit')
        
        if (len(cd_champ) == 0):
            raise ExceptionDetruireEtiquetteMetadonnees("Paramètre obligatoire manquant: %s" %'cd_champ')
        
        if (len(cd_valeur) == 0):
            raise ExceptionDetruireEtiquetteMetadonnees("Paramètre obligatoire manquant: %s" %'cd_valeur')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,ty_produit,cd_champ,cd_valeur):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de détruire une étiquette de métadonnées dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        ty_produit      : Type de produit de l'étiquette.
        cd_champ        : Code du champ de l'étiquette.
        cd_valeur       : Code de valeur de l'étiquette.
        
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
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise ExceptionDetruireEtiquetteMetadonnees("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Vérifier si l'étiquette de métadonnéees est absente
        arcpy.AddMessage("- Vérifier si l'étiquette de métadonnéees est absente")
        sql = ("SELECT *"
               "  FROM F235_VP"
               " WHERE TY_PRODUIT='" + ty_produit + "' AND CD_CHAMP='" + cd_champ + "' AND CD_VALEUR='" + cd_valeur + "'")
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'étiquette est absente
        if not resultat:
            #Retourner une exception
            raise ExceptionDetruireEtiquetteMetadonnees("L'étiquette est absente : " + ty_produit + ", " + cd_champ + ", " + cd_valeur)
        #Afficher l'information de l'étiquette
        arcpy.AddMessage(str(resultat[0]))
        
        #Détruire l'étiquette de métadonnéees
        arcpy.AddMessage("- Détruire l'étiquette de métadonnéees")
        sql = ("DELETE F235_VP"
               " WHERE TY_PRODUIT='" + ty_produit + "' AND CD_CHAMP='" + cd_champ + "' AND CD_VALEUR='" + cd_valeur + "'")
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
        ty_produit  = ""
        cd_champ    = ""
        cd_valeur   = ""
        desc_fr     = ""
        desc_an     = ""
        desc_pna_fr = ""
        desc_pna_an = ""

        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_produit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            cd_champ = sys.argv[3]
        
        if len(sys.argv) > 4:
            cd_valeur = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            desc_fr = sys.argv[5]
        
        if len(sys.argv) > 6:
            desc_an = sys.argv[6]
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                desc_pna_fr = sys.argv[7]
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                desc_pna_an = sys.argv[8]
        
        #Définir l'objet de création pour détruire une étiquette de métadonnées dans SIB.
        oDetruireEtiquetteMetadonnees = DetruireEtiquetteMetadonnees()
        
        #Valider les paramètres obligatoires
        oDetruireEtiquetteMetadonnees.validerParamObligatoire(env,ty_produit,cd_champ,cd_valeur)
        
        #Exécuter le traitement pour détruire une étiquette de métadonnées dans SIB.
        oDetruireEtiquetteMetadonnees.executer(env,ty_produit,cd_champ,cd_valeur)
    
    #Gestion des erreurs
    except ExceptionDetruireEtiquetteMetadonnees, err:
        #Afficher l'erreur
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
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