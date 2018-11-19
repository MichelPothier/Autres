#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierEtatMiseProgramme.py
# Auteur    : Michel Pothier
# Date      : 11 juillet 2016

"""
    Application qui permet de modifier l'�tat d'une ou plusieurs mises au programme.
    Lorsque l'�tat est 'P', elle est chang� pour 'T' et vice versa.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    typeProduit         OB      Type de produit des mises au programme � rechercher.
                                d�faut = 'BDG'
    etatProd            OB      �tat de la production des mises au programme � rechercher.
                                d�faut = 'P : Production'
    noMap               OB      Liste des mises au programme � modifier.
                                d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtatMiseProgramme:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'�tat d'une ou plusieurs mises au programme.

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
    def validerParamObligatoire(self, env, typeProduit, etatProd, noMap):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.
        typeProduit         : Type de produit des mises au programmes recherch�es.
        etatProd            : �tat de la production : 'P' ou 'T' des mises au programmes recherch�es.
        noMap               : Liste des mises au programme � modifier.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'typeProduit')
        
        if (len(etatProd) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'etatProd')
        
        if (len(noMap) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'noMap')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, etatProd, noMap):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier l'�tat d'une ou plusieurs mises au programme.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit des mises au programmes recherch�es.
        etatProd            : �tat de la production : 'P' ou 'T' des mises au programmes recherch�es.
        noMap               : Liste des mises au programme � modifier.
        
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
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")
        
        #Valider si le type de produit est au programme
        arcpy.AddMessage("- Valider le type de produit au programme ...")
        #D�finir la commande SQL
        sql = "SELECT DISTINCT TY_PRODUIT FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "'"
        #arcpy.AddMessage(sql)
        #Ex�cuter la commande SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception("Aucun type de produit '" + typeProduit + "' n'est au programme !")
        
        #Valider si le noMap selon le type de produit est au programme
        arcpy.AddMessage("- Valider l'�tat des mises au programme ...")
        #V�rifier le r�sultat
        if etatProd not in "P,T":
            #Retourner une exception
            raise Exception("L'�tat de production est invalide : " + etatProd)
        #Si l'�tat est P
        if etatProd == "P":
            #D�finir l'�tat d�sir�
            etat = "T"
        #Si l'�tat est T
        else:
            #D�finir l'�tat d�sir�
            etat = "P"
        
        #Modifier l'information du num�ro de mise a programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'�tat des mises au programme ...")
        #Traiter toutes les mises au programme
        for map in noMap.split(","):
            #D�finir le num�ro de mise au programme
            no = map.split(" ")[0]
            
            #D�finir la commande SQL
            sql = "SELECT NO_MAP FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND NO_MAP=" + no
            #Valider la mise au programme
            resultat = self.Sib.requeteSib("SELECT NO_MAP FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND NO_MAP=" + no)
            #V�rifier le r�sultat
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
        typeProduit         = "BDG"
        etatProd            = "P : Production"
        noMap               = ""
        
        #extraction des param�tres d'ex�cution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            etatProd = sys.argv[3].upper().split(" ")[0]
        
        if len(sys.argv) > 4:
            noMap = sys.argv[4].replace(";",",").replace("'","")
        
        #D�finir l'objet pour modifier l'�tat d'une ou plusieurs mises au programme.
        oModifierEtatMiseProgramme = ModifierEtatMiseProgramme()
        
        #Valider les param�tres obligatoires
        oModifierEtatMiseProgramme.validerParamObligatoire(env, typeProduit, etatProd, noMap)
        
        #Ex�cuter le traitement pour modifier l'�tat d'une ou plusieurs mises au programme.
        oModifierEtatMiseProgramme.executer(env, typeProduit, etatProd, noMap)
    
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