#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierCodeTopoMiseProgramme.py
# Auteur    : Michel Pothier
# Date      : 25 juillet 2016

"""
    Application qui permet de modifier l'information relative aux codes d'éléments topographique et aux collisions actives
    pour une mise au programme en production.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    typeProduit         OB      Type de produit de la mise au programme.
                                défaut = 
    noMap               OB      Numéro de la mise au programme à modifier.
                                défaut = 
    listeCodeTopo       OB      Liste des codes d'éléments topographiquea du numéro de mise au programme.
                                défaut = <Celles correspondants au numéro de mise au programme>
    listeCollActive     OP      Liste des collisions actives pour les codes d'éléments topographiquea du numéro de mise au programme.
                                défaut = <Celles correspondants au numéro de mise au programme>
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierCodeTopoMiseProgramme.py env typeProduit noMap listeCodeTopo [listeCollActive]

    Exemple:
        ModifierCodeTopoMiseProgramme.py SIB_PRO BDG 967814 "'1420001 : Filamentaire d'écoulement';'1450000 : Entité hydrographique anthropique" "'1420001 : Filamentaire d'écoulement';'1450000 : Entité hydrographique anthropique"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierCodeTopoMiseProgramme.py 2146 2017-10-19 15:43:27Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierCodeTopoMiseProgramme:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'information relative aux codes d'éléments topographique et aux collisions actives
    pour une mise au programme en production.

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
    def validerParamObligatoire(self, env, typeProduit, noMap, listeCodeTopo):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit de la mise au programme.
        noMap               : Numéro de la mise au programme à modifier.
        listeCodeTopo       : Liste des codes d'éléments topographiques.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'typeProduit')
        
        if (len(noMap) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'noMap')
        
        if (len(listeCodeTopo) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'listeCodeTopo')

        return
    
    #-------------------------------------------------------------------------------------
    def definirCodeElem(self, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de définir une liste de codes d'éléments à partir d'une liste de codes d'éléments
        contenant les descriptions sous forme de texte et retourne une vrai liste sans description.
        
        Paramètres:
        -----------
        listeCodeElem       : Liste des codes d'éléments topographique traités sous forme de texte avec description.
       
        Retour:
        -------
        listeCode           : Liste des codes d'éléments topographique traités sous forme de liste sans description.
        
        """
        
        #Initialisation de la liste des codes topographiques et des collisions actives
        listeCode = []
        
        #Traiter tous les codes ou liste des codes spécifiés        
        for codeDesc in listeCodeElem.split(","):
            #Extraire le code sans la description
            code = codeDesc.split(" ")[0]
            
            #Vérifier si le code est absent de la liste des codes
            if code not in listeCode:
                #Ajouter le code à la liste de code
                listeCode.append(code)
        
        #Retourner la liste des codes d'éléments topographiques sous forme de liste
        return listeCode
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, noMap, listeCodeTopo, listeCollActive):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'information relative aux codes d'éléments topographique et aux collisions actives
        pour une mise au programme en production.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit de la mise au programme.
        noMap               : Numéro de la mise au programme à modifier.
        listeCodeTopo       : Liste des codes d'éléments topographiques.
        listeCollActive     : Liste des collisions actives pour les codes d'éléments topographiques.
        
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
        #Vérifier si l'usager SIB possède les privilège de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")
        
        #Valider si le type de produit est au programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le type de produit au programme ...")
        sql = "SELECT DISTINCT TY_PRODUIT FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND E_PLSNRC='P'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception("Aucun type de produit '" + typeProduit + "' n'est au programme actuellement !")

        #Valider si le noMap selon le type de produit est au programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le numéro de mise au programme ...")
        sql = "SELECT IDENTIFIANT FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND E_PLSNRC='P' AND NO_MAP=" + noMap
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si le résultat est présent
        if resultat:
            #Définir l'identifiant traité
            identifiant = resultat[0][0]
        #Si le résultat est absent
        else:
            #Retourner une exception
            raise Exception("Aucun numéro de mise au programme '" + noMap + "' selon le type de produit '" + typeProduit + "' n'est au programme actuellement !")
        
        #Extraire les codes d'éléments topographiques existants
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire les codes d'éléments topographiques existants ...")
        #Extraire les codes d'éléments topographiques existants
        sql = "SELECT CD_ELEM_TOPO FROM F502_LE WHERE NO_MAP=" + noMap
        #Afficher la commande sql
        arcpy.AddMessage(sql)
        #Exécuter la commande sql
        resultat = self.Sib.requeteSib(sql)
        #initialiser la liste
        listeCodeExistant =[]
        #Traiter tous les codes
        for code in resultat:
            #Ajouter le code à la liste
            listeCodeExistant.append(code[0])
        
        #Créer la liste des codes d'éléments topographiques
        listeCodeElemTopo = self.definirCodeElem(listeCodeTopo)
        #Créer la liste des codes d'éléments en collision active
        listeCodeElemColl = self.definirCodeElem(listeCollActive)
        
        #---------------------------------------------------------------------
        #Ajouter les codes d'éléments topographiques et les collisions actives
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter ou modifier l'information relative aux codes d'éléments topographiques et aux collisions actives ...")
        #Traiter tous les codes d'éléments topographiques
        for codeElem in listeCodeElemTopo:
            #Vérifier si le code de collision est actif
            if codeElem in listeCodeElemColl:
                #Définir le code de collision active
                codeColl = "1"
                
            #Si le code de collision est inactif
            else:
                #Définir le code de collision non active
                codeColl = "0"
            
            #Vérifier si le code d'élément est existant
            if codeElem in listeCodeExistant:
                #Définir la commande pour modifier le code d'élément topographique
                sql = "UPDATE F502_LE SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, COLLISION_ACTIVE=" + codeColl + " WHERE NO_MAP=" + noMap + " AND CD_ELEM_TOPO=" + codeElem
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Exécuter la commande
                self.Sib.execute(sql)
                
            #Si le code est absent
            else:
                #Définir la commande pour insérer le code d'élément topographique
                sql = "INSERT INTO F502_LE VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, " + noMap + ", " + codeElem + ", " + codeColl + ")"
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Exécuter la commande
                self.Sib.execute(sql)
            
            #Vérifier si le code de collision est actif
            if codeColl == "1":
                #Vérifier la collision active
                sql = "SELECT A.IDENTIFIANT, A.NO_MAP, C.TY_TRAV FROM F502_PS A, F502_LE B, F503_TR C WHERE A.IDENTIFIANT='" + identifiant + "' AND B.CD_ELEM_TOPO=" + codeElem + " AND A.NO_MAP=B.NO_MAP AND A.NO_MAP=C.NO_MAP AND A.E_PLSNRC='P' AND B.COLLISION_ACTIVE=1"
                resultat = self.Sib.requeteSib(sql)
                #Vérifier le résultat
                if len(resultat) > 1:
                    #Afficher le message de collision active
                    arcpy.AddWarning("ATTENTION : Plusieurs travaux sont effectués en même temps pour le code : " + codeElem)
                    #Traiter toutes les collisions actives
                    for collActive in resultat:
                        #Avertissement de collision active
                        arcpy.AddWarning(str(collActive))
                        
        #---------------------------------------------------------------------
        #Destruction des codes d'éléments topographiques qui ne sont plus au programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Destruction des codes d'éléments topographiques qui ne sont plus au programme ...")
        #Traiter tous les codes d'éléments existants
        for codeElem in listeCodeExistant:
            #Vérifier si le code existant est absent de la liste de codes d'éléments
            if codeElem not in listeCodeElemTopo:
                #Définir la commande pour modifier le code d'élément topographique
                sql = "SELECT * FROM F502_LE WHERE NO_MAP=" + noMap + " AND CD_ELEM_TOPO=" + codeElem
                resultat = self.Sib.requeteSib(sql)
                #Définir la commande pour modifier le code d'élément topographique
                sql = "DELETE FROM F502_LE WHERE NO_MAP=" + noMap + " AND CD_ELEM_TOPO=" + codeElem
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Exécuter la commande
                self.Sib.execute(sql)
                #Afficher l'information du code détruit
                arcpy.AddWarning(str(resultat[0]))
        
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
        typeProduit         = ""
        noMap               = ""
        listeCodeTopo       = ""
        listeCollActive     = ""
        
        #extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            noMap = sys.argv[3].split(" ")[0]
        
        if len(sys.argv) > 4:
            listeCodeTopo = sys.argv[4].replace("'", "").replace(";", ",")
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                listeCollActive = sys.argv[5].replace("'", "").replace(";", ",")
        
        #Définir l'objet pour modifier l'information relative aux codes d'éléments topographique et aux collisions actives
        oModifierCodeTopoMiseProgramme = ModifierCodeTopoMiseProgramme()
        
        #Valider les paramètres obligatoires
        oModifierCodeTopoMiseProgramme.validerParamObligatoire(env, typeProduit, noMap, listeCodeTopo)
        
        #Exécuter le traitement pour modifier l'information relative aux codes d'éléments topographique et aux collisions actives
        oModifierCodeTopoMiseProgramme.executer(env, typeProduit, noMap, listeCodeTopo, listeCollActive)
    
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