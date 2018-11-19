#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEtapeTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de modifier l'information d'une �tape de production pour un type de travail et un type de produit sp�cifique dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    ty_travail      OB      Type de travail.
                            d�faut = 
    ty_produit      OB      Type de produit.
                            d�faut = 
    etape           OB      �tape de production.
                            d�faut =
    flottante       OB      Indique si l'�tape est flottante [0:NON/1:OUI].
                            d�faut = 
    retour          OB      Indique le num�ro de s�quence de retour [0 si non-interactif ou >0 et <=no_seq si interactif].
                            d�faut = 
    iterative       OB      Indique si l'�tape est it�rative [0:NON/1:OUI].
                            d�faut = 
    dt_recu_req     OB      Indique si la date re�u de l'�tape est requise [0:NON/1:OUI].
                            d�faut = 
    dt_deb_req      OB      Indique si la date de d�but de l'�tape est requise [0:NON/1:OUI].
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierEtapeTypeTravail.py env ty_travail ty_produit etape flottante retour iterative dt_recu_req dt_deb_req

    Exemple:
        ModifierEtapeTypeTravail.py SIB_PRO CHRG BDG PREP 0:NON 1 1:OUI 0:NON 0:NON

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierEtapeTypeTravail.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtapeTypeTravail(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'une �tape de production pour un type de travail et un type de produit sp�cifique dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification de l'information d'une �tape de production pour un type de travail et un type de produit sp�cifique dans SIB.
        
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
    def validerParamObligatoire(self, env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        etape           : �tape de production.
        flottante       : Indique si l'�tape est flottante [0:NON/1:OUI].
        retour          : Indique le num�ro de s�quence de retour [0 si non-interactif ou >0 et <=no_seq si interactif].
        iterative       : Indique si l'�tape est it�rative [0:NON/1:OUI].
        dt_recu_req     : Indique si la date re�u de l'�tape est requise [0:NON/1:OUI].
        dt_deb_req      : Indique si la date de d�but de l'�tape est requise [0:NON/1:OUI].

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(ty_travail) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'ty_travail')

        if (len(ty_produit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'ty_produit')

        if (len(etape) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'etape')

        if (len(flottante) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'flottante')

        if (len(retour) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'retour')

        if (len(iterative) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'iterative')

        if (len(dt_recu_req) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'dt_recu_req')

        if (len(dt_deb_req) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'dt_deb_req')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de modification de l'information d'une �tape de production pour un type de travail et un type de produit sp�cifique dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        etape           : �tape de production.
        flottante       : Indique si l'�tape est flottante [0:NON/1:OUI].
        retour          : Indique le num�ro de s�quence de retour [0 si non-interactif ou >0 et <=no_seq si interactif].
        iterative       : Indique si l'�tape est it�rative [0:NON/1:OUI].
        dt_recu_req     : Indique si la date re�u de l'�tape est requise [0:NON/1:OUI].
        dt_deb_req      : Indique si la date de d�but de l'�tape est requise [0:NON/1:OUI].
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Valider la pr�sence des �tapes de production
        arcpy.AddMessage("- Valider la pr�sence des �tapes de production")
        resultat = self.Sib.requeteSib("SELECT NO_SEQ,FLOTTANTE,ITERATIVE,RETOUR,DT_RECU_REQ,DT_DEB_REQ FROM F106_EI WHERE TY_PRODUIT='" + ty_produit + "' AND TY_TRAV='" + ty_travail + "' AND CD_ETP = '" + etape + "'")
        #V�rifier la pr�sence des �tapes de production
        if not resultat:
            #Retourner une exception
            raise Exception("L'information relative l'�tape de production est inexistante = " + etape)
        
        #Initialiser la commande SQL de modification
        sql = "UPDATE F106_EI SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE"
        
        #Valider les valeurs permises de l'attribut FLOTTANTE
        if flottante <> "0" and flottante <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut FLOTTANTE est invalide : " + flottante)
        #V�rifier si la valeur a chang�e
        if flottante <> str(resultat[0][1]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",FLOTTANTE=" + flottante
            
        #Valider les valeurs permises de l'attribut ITERATIVE
        if iterative <> "0" and iterative <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut ITERATIVE est invalide : " + iterative)
        #V�rifier si la valeur a chang�e
        if iterative <> str(resultat[0][2]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",ITERATIVE=" + iterative
        
        #V�rifier si l'�tape est it�rative
        if iterative == "1":
            #V�rifier si la valeur est un entier
            if not retour.isdigit():
                #Retourner une exception
                raise Exception("La valeur de l'attribut RETOUR doit �tre un entier : " + retour)
            #Valider les valeurs permises de l'attribut RETOUR lorsque it�ratif
            if int(retour) <= 0 or int(retour) > resultat[0][0]:
                #Retourner une exception
                raise Exception("La valeur de l'attribut RETOUR est invalide : " + retour)
        #Si l'�tape est non-it�rative
        else:
            #Valider les valeurs permises de l'attribut RETOUR lorsque non-it�ratif
            if retour <> "0":
                #Retourner une exception
                raise Exception("La valeur de l'attribut RETOUR doit �tre = 0")
        #V�rifier si la valeur a chang�e
        if retour <> str(resultat[0][3]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",RETOUR=" + retour
        
        #Valider les valeurs permises de l'attribut DT_RECU_REQ
        if dt_recu_req <> "0" and dt_recu_req <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut DT_RECU_REQ est invalide : " + dt_recu_req)
        #V�rifier si la valeur a chang�e
        if dt_recu_req <> str(resultat[0][4]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",DT_RECU_REQ=" + dt_recu_req
        
        #Valider les valeurs permises de l'attribut DT_DEB_REQ
        if dt_deb_req <> "0" and dt_deb_req <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut DT_DEB_REQ est invalide : " + dt_deb_req)
        #V�rifier si la valeur a chang�e
        if dt_deb_req <> str(resultat[0][5]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",DT_DEB_REQ=" + dt_deb_req
        
        #Modifier l'information de l'�tape de production sp�cifi�e
        arcpy.AddMessage("- Modifier l'information de l'�tape de production")
        #Modifier l'information de l'�tape de production
        sql = sql + " WHERE TY_PRODUIT='" + ty_produit + "' AND TY_TRAV='" + ty_travail + "' AND CD_ETP='" + etape + "'"
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        ty_travail  = ""
        ty_produit  = ""
        etape       = ""
        flottante   = ""
        retour      = ""
        iterative   = ""
        dt_recu_req = ""
        dt_deb_req  = ""
        
        #Extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_travail = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            ty_produit = sys.argv[3]
        
        if len(sys.argv) > 4:
            etape = sys.argv[4]
        
        if len(sys.argv) > 5:
            flottante = sys.argv[5].split(":")[0]
        
        if len(sys.argv) > 6:
            retour = sys.argv[6]
        
        if len(sys.argv) > 7:
            iterative = sys.argv[7].split(":")[0]
        
        if len(sys.argv) > 8:
            dt_recu_req = sys.argv[8].split(":")[0]
        
        if len(sys.argv) > 9:
            dt_deb_req = sys.argv[9].split(":")[0]
        
        #D�finir l'objet de modification de l'information d'une �tape de production pour un type de travail et un type de produit sp�cifique dans SIB.
        oModifierEtapeTypeTravail = ModifierEtapeTypeTravail()
        
        #Valider les param�tres obligatoires
        oModifierEtapeTypeTravail.validerParamObligatoire(env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req)
        
        #Ex�cuter le traitement de modification de l'information d'une �tape de production pour un type de travail et un type de produit sp�cifique dans SIB.
        oModifierEtapeTypeTravail.executer(env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req)
    
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