#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierMiseProgramme.py
# Auteur    : Michel Pothier
# Date      : 28 juin 2016

"""
    Application qui permet de modifier l'information d'une mise au programme en production.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    typeProduit         OB      Type de produit de la mise au programme.
                                d�faut = 
    noMap               OB      Num�ro de la mise au programme � modifier.
                                d�faut = 
    typeProd            OB      Type de production du num�ro de mise au programme.
                                d�faut = 
    etatProd            OB      �tat de la production du num�ro de mise au programme.
                                d�faut = 
    normes              OB      Norme selon laquelle la production sera effectu�e.
                                d�faut = 
    gabaritMD           OP      Gabarit de m�tadonn�es utilis�. 
                                d�faut = 
    datePrevue          OP      Date pr�vue de la fin des travaux
                                d�faut = 
    note                OP      Note explicative associ�e aux identifiants trait�s.
                                d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierMiseProgramme.py env typeProduit noMap typeProd etatProd normes [gabaritMD] [datePrevue]  [note]

    Exemple:
        ModifierMiseProgramme.py SIB_PRO BDG 0123456 A P 4.0.2  # # # "Note pour le lot"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierMiseProgramme.py 2147 2017-10-19 15:43:44Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierMiseProgramme:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'information d'une mise au programme en production.

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
    def validerParamObligatoire(self, env, typeProduit, noMap, typeProd, etatProd, normes):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit de la mise au programme.
        noMap               : Num�ro de la mise au programme � modifier.
        typeProd            : Indique le type de production : 'A', 'C' ou 'E'
        etatProd            : Indique l'�tat de la production : 'P' ou 'T'
        normes              : Num�ro de la normes selon laquelle le fichier sera produit.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(typeProduit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'typeProduit')
        
        if (len(noMap) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'noMap')
        
        if (len(typeProd) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'typeProd')
        
        if (len(etatProd) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'etatProd')
        
        if (len(normes) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'normes')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, typeProduit, noMap, typeProd, etatProd, normes, gabaritMD, datePrevue, note):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour modifier l'information d'une mise au programme en production.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        typeProduit         : Type de produit de la mise au programme.
        noMap               : Num�ro de la mise au programme � modifier.
        typeProd            : Indique le type de production : 'A', 'C' ou 'E'
        etatProd            : Indique l'�tat de la production : 'P' ou 'T'
        normes              : Num�ro de la normes selon laquelle le fichier sera produit.
        gabaritMD           : Gabarit de m�tadonn�es utilis�. 
        datePrevue          : Date pr�vue de la fin des travaux.
        note                : Note explicative associ�e aux identifiants trait�s.
        
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
        arcpy.AddMessage("- Valider le type de produit au programme ...")
        resultat = self.Sib.requeteSib("SELECT DISTINCT TY_PRODUIT FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND E_PLSNRC='P'")
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception("Aucun type de produit '" + typeProduit + "' n'est au programme actuellement !")

        #Valider si le noMap selon le type de produit est au programme
        arcpy.AddMessage("- Valider le num�ro de mise au programme ...")
        resultat = self.Sib.requeteSib("SELECT NO_MAP FROM F502_PS WHERE TY_PRODUIT='" + typeProduit + "' AND E_PLSNRC='P' AND NO_MAP=" + noMap)
        #V�rifier le r�sultat
        if not resultat:
            #Retourner une exception
            raise Exception("Aucun num�ro de mise au programme '" + noMap + "' selon le type de produit '" + typeProduit + "' n'est au programme actuellement !")
        
        #V�rifier si le gabaritMD est vide
        if gabaritMD == "":
            #Ajouter la valeur NULL
            gabaritMD = "NULL"
        #si le gabarit n'est pas vide
        else:
            #Ajouter les apostrophes
            gabaritMD = "'" + gabaritMD.replace("'","''") + "'"
        
        #V�rifier si la date pr�vue est vide
        if datePrevue == "":
            #Ajouter la valeur NULL
            datePrevue = "NULL"
        #si la date n'est pas vide
        else:
            #Ajouter les apostrophes
            datePrevue = "'" + datePrevue + "'"
        
        #V�rifier si la note est vide
        if note == "":
            #Ajouter la valeur NULL
            note = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            note = "'" + note.replace("'","''") + "'"
        
        #Modifier l'information du num�ro de mise a programme
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information du num�ro de mise a programme ...")
        #Initialiser la commande SQL de modifification
        sql = "UPDATE F502_PS SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE"
        sql = sql + ",TYPE='" + typeProd + "',E_PLSNRC='" + etatProd + "',NORMES='" + normes + "'"
        sql= sql + ",GABARIT_MD=" + gabaritMD + ",DT_PREVUE=TO_DATE(" + datePrevue + "),NOTE=" + note + " WHERE NO_MAP=" + noMap
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
        
        #Sortir et retourner la liste des num�ro de mise au programme, des �ditions, des versions et des identifiants.
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
        typeProd            = ""
        etatProd            = ""
        normes              = ""
        gabaritMD           = ""
        datePrevue          = ""
        note                = ""
        
        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            typeProduit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            noMap = sys.argv[3].split(" ")[0]
        
        if len(sys.argv) > 4:
            typeProd = sys.argv[4].upper().split(" ")[0]
        
        if len(sys.argv) > 5:
            etatProd = sys.argv[5].upper().split(" ")[0]
        
        if len(sys.argv) > 6:
            normes = sys.argv[6]
            
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                gabaritMD = sys.argv[7]
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                datePrevue = sys.argv[8].split(" ")[0]
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                note = sys.argv[9]
        
        #D�finir l'objet pour modifier l'information d'une mise au programme en production.
        oModifierMiseProgramme = ModifierMiseProgramme()
        
        #Valider les param�tres obligatoires
        oModifierMiseProgramme.validerParamObligatoire(env, typeProduit, noMap, typeProd, etatProd, normes)
        
        #Ex�cuter le traitement pour modifier l'information d'une mise au programme en production.
        oModifierMiseProgramme.executer(env, typeProduit, noMap, typeProd, etatProd, normes, gabaritMD, datePrevue, note)
    
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