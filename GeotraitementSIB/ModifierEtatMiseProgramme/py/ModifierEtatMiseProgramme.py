#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierEtatMiseProgramme.py
# Auteur    : Michel Pothier
# Date      : 11 juillet 2016

"""
    Application qui permet de modifier l'état d'une ou plusieurs mises au programme.
    Lorsque l'état est 'P', elle est changé pour 'T' et vice versa.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    typeProduit         OB      Type de produit des mises au programme à rechercher.
                                défaut = 'BDG'
    etatProd            OB      État de la production des mises au programme à rechercher.
                                défaut = 'P : Production'
    noMap               OB      Liste des mises au programme à modifier.
                                défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierEtatMiseProgramme.py env typeProduit etatProd noMap

    Exemple:
        ModifierEtatMiseProgramme.py SIB_PRO BDG T 0123456,7890345

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEtatMiseProgramme.py 10242 1 2014-07-04 13:54:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtatMiseProgramme:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'état d'une ou plusieurs mises au programme.

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
    def validerParamObligatoire(self, env, typeProduit, etatProd, noMap):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.
        typeProduit         : Type de produit des mises au programmes recherchées.
        etatProd            : État de la production : 'P' ou 'T' des mises au programmes recherchées.
        noMap               : Liste des mises au programme à modifier.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'typeProduit')
        
        if (len(etatProd) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'etatProd')
        
        if (len(noMap) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'noMap')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, etatProd, noMap):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'état d'une ou plusieurs mises au programme.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit des mises au programmes recherchées.
        etatProd            : État de la production : 'P' ou 'T' des mises au programmes recherchées.
        noMap               : Liste des mises au programme à modifier.
        
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
        
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS','PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")
        
        #Valider si le type de produit est au programme
        arcpy.AddMessage("- Valider le type de produit au programme ...")
        #Définir la commande SQL
        sql = "SELECT DISTINCT TY_PRODUIT FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "'"
        #arcpy.AddMessage(sql)
        #Exécuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception("Aucun type de produit '" + typeProduit + "' n'est au programme !")
        
        #Valider si le noMap selon le type de produit est au programme
        arcpy.AddMessage("- Valider l'état des mises au programme ...")
        #Vérifier le résultat
        if etatProd not in "P,T":
            #Retourner une exception
            raise Exception("L'état de production est invalide : " + etatProd)
        #Si l'état est P
        if etatProd == "P":
            #Définir l'état désiré
            etat = "T"
        #Si l'état est T
        else:
            #Définir l'état désiré
            etat = "P"
        
        #Modifier l'information du numéro de mise a programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'état des mises au programme ...")
        #Traiter toutes les mises au programme
        for map in noMap.split(","):
            #Définir le numéro de mise au programme
            no = map.split(" ")[0]
            
            #Définir la commande SQL
            sql = "SELECT NO_MAP FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND NO_MAP=" + no
            #Valider la mise au programme
            resultat = self.Sib.requeteSib("SELECT NO_MAP FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND NO_MAP=" + no)
            #Vérifier le résultat
            if not resultat:
                #Retourner une exception
                arcpy.AddWarning(sql)
                raise Exception("La mise au programme est invalide : " + no)
            
            #Initialiser la commande SQL de modification
            sql = "UPDATE F502_PS SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, E_PLSNRC='" + etat + "' WHERE TY_PRODUIT='" + typeProduit + "' AND NO_MAP=" + no
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
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
        typeProduit         = "BDG"
        etatProd            = "P : Production"
        noMap               = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            etatProd = sys.argv[3].upper().split(" ")[0]
        
        if len(sys.argv) > 4:
            noMap = sys.argv[4].replace(";",",").replace("'","")
        
        #Définir l'objet pour modifier l'état d'une ou plusieurs mises au programme.
        oModifierEtatMiseProgramme = ModifierEtatMiseProgramme()
        
        #Valider les paramètres obligatoires
        oModifierEtatMiseProgramme.validerParamObligatoire(env, typeProduit, etatProd, noMap)
        
        #Exécuter le traitement pour modifier l'état d'une ou plusieurs mises au programme.
        oModifierEtatMiseProgramme.executer(env, typeProduit, etatProd, noMap)
    
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