#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierEtapeTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de modifier l'information d'une étape de production pour un type de travail et un type de produit spécifique dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    ty_travail      OB      Type de travail.
                            défaut = 
    ty_produit      OB      Type de produit.
                            défaut = 
    etape           OB      Étape de production.
                            défaut =
    flottante       OB      Indique si l'étape est flottante [0:NON/1:OUI].
                            défaut = 
    retour          OB      Indique le numéro de séquence de retour [0 si non-interactif ou >0 et <=no_seq si interactif].
                            défaut = 
    iterative       OB      Indique si l'étape est itérative [0:NON/1:OUI].
                            défaut = 
    dt_recu_req     OB      Indique si la date reçu de l'étape est requise [0:NON/1:OUI].
                            défaut = 
    dt_deb_req      OB      Indique si la date de début de l'étape est requise [0:NON/1:OUI].
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierEtapeTypeTravail(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'une étape de production pour un type de travail et un type de produit spécifique dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification de l'information d'une étape de production pour un type de travail et un type de produit spécifique dans SIB.
        
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
    def validerParamObligatoire(self, env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        etape           : Étape de production.
        flottante       : Indique si l'étape est flottante [0:NON/1:OUI].
        retour          : Indique le numéro de séquence de retour [0 si non-interactif ou >0 et <=no_seq si interactif].
        iterative       : Indique si l'étape est itérative [0:NON/1:OUI].
        dt_recu_req     : Indique si la date reçu de l'étape est requise [0:NON/1:OUI].
        dt_deb_req      : Indique si la date de début de l'étape est requise [0:NON/1:OUI].

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(ty_travail) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'ty_travail')

        if (len(ty_produit) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'ty_produit')

        if (len(etape) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'etape')

        if (len(flottante) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'flottante')

        if (len(retour) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'retour')

        if (len(iterative) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'iterative')

        if (len(dt_recu_req) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'dt_recu_req')

        if (len(dt_deb_req) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'dt_deb_req')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de modification de l'information d'une étape de production pour un type de travail et un type de produit spécifique dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        etape           : Étape de production.
        flottante       : Indique si l'étape est flottante [0:NON/1:OUI].
        retour          : Indique le numéro de séquence de retour [0 si non-interactif ou >0 et <=no_seq si interactif].
        iterative       : Indique si l'étape est itérative [0:NON/1:OUI].
        dt_recu_req     : Indique si la date reçu de l'étape est requise [0:NON/1:OUI].
        dt_deb_req      : Indique si la date de début de l'étape est requise [0:NON/1:OUI].
        
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
        
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Valider la présence des étapes de production
        arcpy.AddMessage("- Valider la présence des étapes de production")
        resultat = self.Sib.requeteSib("SELECT NO_SEQ,FLOTTANTE,ITERATIVE,RETOUR,DT_RECU_REQ,DT_DEB_REQ FROM F106_EI WHERE TY_PRODUIT='" + ty_produit + "' AND TY_TRAV='" + ty_travail + "' AND CD_ETP = '" + etape + "'")
        #Vérifier la présence des étapes de production
        if not resultat:
            #Retourner une exception
            raise Exception("L'information relative l'étape de production est inexistante = " + etape)
        
        #Initialiser la commande SQL de modification
        sql = "UPDATE F106_EI SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE"
        
        #Valider les valeurs permises de l'attribut FLOTTANTE
        if flottante <> "0" and flottante <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut FLOTTANTE est invalide : " + flottante)
        #Vérifier si la valeur a changée
        if flottante <> str(resultat[0][1]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",FLOTTANTE=" + flottante
            
        #Valider les valeurs permises de l'attribut ITERATIVE
        if iterative <> "0" and iterative <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut ITERATIVE est invalide : " + iterative)
        #Vérifier si la valeur a changée
        if iterative <> str(resultat[0][2]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",ITERATIVE=" + iterative
        
        #Vérifier si l'étape est itérative
        if iterative == "1":
            #Vérifier si la valeur est un entier
            if not retour.isdigit():
                #Retourner une exception
                raise Exception("La valeur de l'attribut RETOUR doit être un entier : " + retour)
            #Valider les valeurs permises de l'attribut RETOUR lorsque itératif
            if int(retour) <= 0 or int(retour) > resultat[0][0]:
                #Retourner une exception
                raise Exception("La valeur de l'attribut RETOUR est invalide : " + retour)
        #Si l'étape est non-itérative
        else:
            #Valider les valeurs permises de l'attribut RETOUR lorsque non-itératif
            if retour <> "0":
                #Retourner une exception
                raise Exception("La valeur de l'attribut RETOUR doit être = 0")
        #Vérifier si la valeur a changée
        if retour <> str(resultat[0][3]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",RETOUR=" + retour
        
        #Valider les valeurs permises de l'attribut DT_RECU_REQ
        if dt_recu_req <> "0" and dt_recu_req <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut DT_RECU_REQ est invalide : " + dt_recu_req)
        #Vérifier si la valeur a changée
        if dt_recu_req <> str(resultat[0][4]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",DT_RECU_REQ=" + dt_recu_req
        
        #Valider les valeurs permises de l'attribut DT_DEB_REQ
        if dt_deb_req <> "0" and dt_deb_req <> "1":
            #Retourner une exception
            raise Exception("La valeur de l'attribut DT_DEB_REQ est invalide : " + dt_deb_req)
        #Vérifier si la valeur a changée
        if dt_deb_req <> str(resultat[0][5]):
            #Ajouter la commande pour modifier la valeur
            sql = sql + ",DT_DEB_REQ=" + dt_deb_req
        
        #Modifier l'information de l'étape de production spécifiée
        arcpy.AddMessage("- Modifier l'information de l'étape de production")
        #Modifier l'information de l'étape de production
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
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env         = "SIB_PRO"
        ty_travail  = ""
        ty_produit  = ""
        etape       = ""
        flottante   = ""
        retour      = ""
        iterative   = ""
        dt_recu_req = ""
        dt_deb_req  = ""
        
        #Extraction des paramètres d'exécution
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
        
        #Définir l'objet de modification de l'information d'une étape de production pour un type de travail et un type de produit spécifique dans SIB.
        oModifierEtapeTypeTravail = ModifierEtapeTypeTravail()
        
        #Valider les paramètres obligatoires
        oModifierEtapeTypeTravail.validerParamObligatoire(env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req)
        
        #Exécuter le traitement de modification de l'information d'une étape de production pour un type de travail et un type de produit spécifique dans SIB.
        oModifierEtapeTypeTravail.executer(env, ty_travail, ty_produit, etape, flottante, retour, iterative, dt_recu_req, dt_deb_req)
    
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