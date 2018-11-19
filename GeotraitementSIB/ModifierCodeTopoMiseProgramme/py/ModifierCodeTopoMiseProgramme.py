#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierCodeTopoMiseProgramme.py
# Auteur    : Michel Pothier
# Date      : 25 juillet 2016

"""
    Application qui permet de modifier l'information relative aux codes d'�l�ments topographique et aux collisions actives
    pour une mise au programme en production.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    typeProduit         OB      Type de produit de la mise au programme.
                                d�faut = 
    noMap               OB      Num�ro de la mise au programme � modifier.
                                d�faut = 
    listeCodeTopo       OB      Liste des codes d'�l�ments topographiquea du num�ro de mise au programme.
                                d�faut = <Celles correspondants au num�ro de mise au programme>
    listeCollActive     OP      Liste des collisions actives pour les codes d'�l�ments topographiquea du num�ro de mise au programme.
                                d�faut = <Celles correspondants au num�ro de mise au programme>
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierCodeTopoMiseProgramme.py env typeProduit noMap listeCodeTopo [listeCollActive]

    Exemple:
        ModifierCodeTopoMiseProgramme.py SIB_PRO BDG 967814 "'1420001 : Filamentaire d'�coulement';'1450000 : Entit� hydrographique anthropique" "'1420001 : Filamentaire d'�coulement';'1450000 : Entit� hydrographique anthropique"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierCodeTopoMiseProgramme.py 2146 2017-10-19 15:43:27Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierCodeTopoMiseProgramme:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'information relative aux codes d'�l�ments topographique et aux collisions actives
    pour une mise au programme en production.

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
    def validerParamObligatoire(self, env, typeProduit, noMap, listeCodeTopo):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit de la mise au programme.
        noMap               : Num�ro de la mise au programme � modifier.
        listeCodeTopo       : Liste des codes d'�l�ments topographiques.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'typeProduit')
        
        if (len(noMap) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'noMap')
        
        if (len(listeCodeTopo) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'listeCodeTopo')

        return
    
    #-------------------------------------------------------------------------------------
    def definirCodeElem(self, listeCodeElem):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de d�finir une liste de codes d'�l�ments � partir d'une liste de codes d'�l�ments
        contenant les descriptions sous forme de texte et retourne une vrai liste sans description.
        
        Param�tres:
        -----------
        listeCodeElem       : Liste des codes d'�l�ments topographique trait�s sous forme de texte avec description.
       
        Retour:
        -------
        listeCode           : Liste des codes d'�l�ments topographique trait�s sous forme de liste sans description.
        
        """
        
        #Initialisation de la liste des codes topographiques et des collisions actives
        listeCode = []
        
        #Traiter tous les codes ou liste des codes sp�cifi�s        
        for codeDesc in listeCodeElem.split(","):
            #Extraire le code sans la description
            code = codeDesc.split(" ")[0]
            
            #V�rifier si le code est absent de la liste des codes
            if code not in listeCode:
                #Ajouter le code � la liste de code
                listeCode.append(code)
        
        #Retourner la liste des codes d'�l�ments topographiques sous forme de liste
        return listeCode
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, noMap, listeCodeTopo, listeCollActive):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier l'information relative aux codes d'�l�ments topographique et aux collisions actives
        pour une mise au programme en production.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit de la mise au programme.
        noMap               : Num�ro de la mise au programme � modifier.
        listeCodeTopo       : Liste des codes d'�l�ments topographiques.
        listeCollActive     : Liste des collisions actives pour les codes d'�l�ments topographiques.
        
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
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        #Valider si le type de produit est au programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le type de produit au programme ...")
        sql = "SELECT DISTINCT TY_PRODUIT FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND E_PLSNRC='P'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception("Aucun type de produit '" + typeProduit + "' n'est au programme actuellement !")

        #Valider si le noMap selon le type de produit est au programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le num�ro de mise au programme ...")
        sql = "SELECT IDENTIFIANT FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND E_PLSNRC='P' AND NO_MAP=" + noMap
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si le r�sultat est pr�sent
        if resultat:
            #D�finir l'identifiant trait�
            identifiant = resultat[0][0]
        #Si le r�sultat est absent
        else:
            #Retourner une exception
            raise Exception("Aucun num�ro de mise au programme '" + noMap + "' selon le type de produit '" + typeProduit + "' n'est au programme actuellement !")
        
        #Extraire les codes d'�l�ments topographiques existants
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraire les codes d'�l�ments topographiques existants ...")
        #Extraire les codes d'�l�ments topographiques existants
        sql = "SELECT CD_ELEM_TOPO FROM F502_LE WHERE NO_MAP=" + noMap
        #Afficher la commande sql
        arcpy.AddMessage(sql)
        #Ex�cuter la commande sql
        resultat = self.Sib.requeteSib(sql)
        #initialiser la liste
        listeCodeExistant =[]
        #Traiter tous les codes
        for code in resultat:
            #Ajouter le code � la liste
            listeCodeExistant.append(code[0])
        
        #Cr�er la liste des codes d'�l�ments topographiques
        listeCodeElemTopo = self.definirCodeElem(listeCodeTopo)
        #Cr�er la liste des codes d'�l�ments en collision active
        listeCodeElemColl = self.definirCodeElem(listeCollActive)
        
        #---------------------------------------------------------------------
        #Ajouter les codes d'�l�ments topographiques et les collisions actives
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter ou modifier l'information relative aux codes d'�l�ments topographiques et aux collisions actives ...")
        #Traiter tous les codes d'�l�ments topographiques
        for codeElem in listeCodeElemTopo:
            #V�rifier si le code de collision est actif
            if codeElem in listeCodeElemColl:
                #D�finir le code de collision active
                codeColl = "1"
                
            #Si le code de collision est inactif
            else:
                #D�finir le code de collision non active
                codeColl = "0"
            
            #V�rifier si le code d'�l�ment est existant
            if codeElem in listeCodeExistant:
                #D�finir la commande pour modifier le code d'�l�ment topographique
                sql = "UPDATE F502_LE SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, COLLISION_ACTIVE=" + codeColl + " WHERE NO_MAP=" + noMap + " AND CD_ELEM_TOPO=" + codeElem
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
                
            #Si le code est absent
            else:
                #D�finir la commande pour ins�rer le code d'�l�ment topographique
                sql = "INSERT INTO F502_LE VALUES (P0G03_UTL.PU_HORODATEUR, '" + sUsagerSib + "', SYSDATE, SYSDATE, " + noMap + ", " + codeElem + ", " + codeColl + ")"
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
            
            #V�rifier si le code de collision est actif
            if codeColl == "1":
                #V�rifier la collision active
                sql = "SELECT A.IDENTIFIANT, A.NO_MAP, C.TY_TRAV FROM F502_PS A, F502_LE B, F503_TR C WHERE A.IDENTIFIANT='" + identifiant + "' AND B.CD_ELEM_TOPO=" + codeElem + " AND A.NO_MAP=B.NO_MAP AND A.NO_MAP=C.NO_MAP AND A.E_PLSNRC='P' AND B.COLLISION_ACTIVE=1"
                resultat = self.Sib.requeteSib(sql)
                #V�rifier le r�sultat
                if len(resultat) > 1:
                    #Afficher le message de collision active
                    arcpy.AddWarning("ATTENTION : Plusieurs travaux sont effectu�s en m�me temps pour le code : " + codeElem)
                    #Traiter toutes les collisions actives
                    for collActive in resultat:
                        #Avertissement de collision active
                        arcpy.AddWarning(str(collActive))
                        
        #---------------------------------------------------------------------
        #Destruction des codes d'�l�ments topographiques qui ne sont plus au programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Destruction des codes d'�l�ments topographiques qui ne sont plus au programme ...")
        #Traiter tous les codes d'�l�ments existants
        for codeElem in listeCodeExistant:
            #V�rifier si le code existant est absent de la liste de codes d'�l�ments
            if codeElem not in listeCodeElemTopo:
                #D�finir la commande pour modifier le code d'�l�ment topographique
                sql = "SELECT * FROM F502_LE WHERE NO_MAP=" + noMap + " AND CD_ELEM_TOPO=" + codeElem
                resultat = self.Sib.requeteSib(sql)
                #D�finir la commande pour modifier le code d'�l�ment topographique
                sql = "DELETE FROM F502_LE WHERE NO_MAP=" + noMap + " AND CD_ELEM_TOPO=" + codeElem
                #Afficher la commande
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
                #Afficher l'information du code d�truit
                arcpy.AddWarning(str(resultat[0]))
        
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
        typeProduit         = ""
        noMap               = ""
        listeCodeTopo       = ""
        listeCollActive     = ""
        
        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet pour modifier l'information relative aux codes d'�l�ments topographique et aux collisions actives
        oModifierCodeTopoMiseProgramme = ModifierCodeTopoMiseProgramme()
        
        #Valider les param�tres obligatoires
        oModifierCodeTopoMiseProgramme.validerParamObligatoire(env, typeProduit, noMap, listeCodeTopo)
        
        #Ex�cuter le traitement pour modifier l'information relative aux codes d'�l�ments topographique et aux collisions actives
        oModifierCodeTopoMiseProgramme.executer(env, typeProduit, noMap, listeCodeTopo, listeCollActive)
    
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