#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerEtapesTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de créer la liste des étapes de production pour un type de travail et un type de produit spécifique dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    ty_travail      OB      Type de travail.
                            défaut = 
    ty_produit      OB      Type de produit.
                            défaut = 
    tableEtapes     OB      Liste des étapes de production et de ses paramètres de traitement.
                            défaut =
                            Attention : Si les étapes de production existe déjà, le traitement ne se fera pas à moins de forcer à les détruire.
    detruire        OB      Indique si on doit détruire les étapes de production existantes [True/False].
                            défaut = False
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerEtapesTypeTravail.py env ty_travail ty_produit tableEtapes detruire

    Exemple:
        CreerEtapesTypeTravail.py SIB_PRO CHRG BDG RECORDSET False

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerEtapesTypeTravail.py 2107 2016-08-23 17:50:51Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerEtapesTypeTravail(object):
#*******************************************************************************************
    """
    Permet de créer la liste des étapes de production pour un type de travail et un type de produit spécifique dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'une liste des étapes de production pour un type de travail et un type de produit spécifique.
        
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
    def validerParamObligatoire(self, env, ty_travail, ty_produit, tableEtapes):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        tableEtapes     : Liste des étapes de production et de ses paramètres de traitement.

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

        if (len(tableEtapes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'tableEtapes')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, ty_produit, tableEtapes, detruire):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'une liste des étapes de production pour un type de travail et un type de produit spécifique dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        tableEtapes     : Liste des étapes de production et de ses paramètres de traitement.
        detruire        : Indique si on doit détruire les étapes de production existantes [True/False].
        
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
        
        #-----------------------------------------------------
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #--------------------------------------------
        #Définir la liste des étapes permises
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Définir la liste des étapes permises")
        sql = "SELECT CD_ETP FROM F117_ET WHERE ACTIVE=1 ORDER BY CD_ETP"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Initialiser la liste des étapes permises
        listeEtapes = []
        #Construire la liste des étapes permises
        for etape in resultat:
            listeEtapes.append(etape[0])
        #Afficher la liste des codes d'étape
        arcpy.AddMessage(str(listeEtapes))
        
        #-----------------------------------------------------
        #Valider la présence des étapes de production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider la présence des étapes de production existantes")
        sql = "SELECT NO_SEQ,CD_ETP,FLOTTANTE,RETOUR,ITERATIVE,DT_RECU_REQ,DT_DEB_REQ FROM F106_EI WHERE TY_PRODUIT='" + ty_produit + "' AND TY_TRAV='" + ty_travail + "' ORDER BY NO_SEQ"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier la présence des étapes de production
        if resultat:
            #Vérifier si on doit détruire les étapes existantes
            if detruire:
                #Afficher les étapes existantes
                for row in resultat:
                    arcpy.AddMessage(str(row))
                #Détruire les étapes de production existantes
                sql = "DELETE F106_EI WHERE TY_PRODUIT='" + ty_produit + "' AND TY_TRAV='" + ty_travail + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            
            #Si on ne doit pas détruire les étapes existantes
            else:
                #Retourner une exception
                raise Exception(u"La liste des étapes de production est déjà présente, nombre d'étapes = " + str(len(resultat)))
        
        #-----------------------------------------------------
        #Valider la liste des étapes de production et leurs paramètres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider la liste des étapes de production et leurs paramètres")
        #Initialiser le numéro de séquence
        no_seq = 0
        #Afficher les valeurs d'attributs
        attributs = ["CD_ETP", "FLOTTANTE", "RETOUR", "ITERATIVE", "DT_RECU_REQ", "DT_DEB_REQ"]
        arcpy.AddMessage(str(attributs))
        #Traiter tous les éléments de la table
        for row in arcpy.da.SearchCursor(tableEtapes, attributs):
            #Définir le numéro de séquence
            no_seq = no_seq + 1
            #Afficher les valeurs d'attributs
            arcpy.AddMessage(str(no_seq) + " : " + str(row))
            
            #Vérifier si l'étape est valide
            if str(row[0]) not in listeEtapes:
                #Retourner un message d'erreur
                raise Exception(u"Le code d'étape est invalide : " + str(row[0]))
            
            #Vérifier si le fanion de l'étape flottante est valide
            if str(row[1]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de l'étape flottante est invalide : " + str(row[1]))
            
            #Vérifier si le fanion de l'étape flottante est valide
            if str(row[3]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de l'étape itérative est invalide : " + str(row[3]))
            
            #Vérifier si l'étape est non-itérative
            if row[3] == 0:
                #Vérifier si la valeur de l'attribut RETOUR <> 0
                if row[2] <> 0:
                    #Retourner un message d'erreur
                    raise Exception(u"La valeur de l'attribut RETOUR doit etre 0 lorsque l'etape est non-iterative")
            #Vérifier si l'étape est itérative
            else:
                #Vérifier si la valeur de l'attribut RETOUR = 0 et > no_seq
                if row[2] == 0 or row[2] > no_seq:
                    #Retourner un message d'erreur
                    raise Exception(u"La valeur de l'attribut RETOUR doit plus grand que 0 et inferieure au NO_SEQ lorsque l'etape est iterative")

            #Vérifier si le fanion de la date reçu est valide
            if str(row[4]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de la date reçu est invalide : " + str(row[4]))
            
            #Vérifier si le fanion de la date de début est valide
            if str(row[5]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de la date de début est invalide : " + str(row[5]))
        
        #-----------------------------------------------------
        #Ajouter la liste des étapes de production et leurs paramètres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter la liste des étapes de production et leurs paramètres")
        #Initialiser le numéro de séquence
        no_seq = 0
        #Traiter tous les éléments de la table
        for row in arcpy.da.SearchCursor(tableEtapes, attributs):
            #Définir le numéro de séquence
            no_seq = no_seq + 1
            #Ajouter une étapes de production
            sql = "INSERT INTO F106_EI VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + ty_produit + "','" + ty_travail + "'," + str(no_seq) + ",'" + row[0] + "'," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "," + str(row[4]) + "," + str(row[5]) + ")"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #-----------------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
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
        tableEtapes = ""
        detruire    = False
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_travail = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            ty_produit = sys.argv[3]
        
        if len(sys.argv) > 4:
            tableEtapes = sys.argv[4]
            
        if len(sys.argv) > 5:
            if sys.argv[5] <> '#':
                detruire = sys.argv[5].upper()=='TRUE'
        
        #Définir l'objet de création d'une liste des étapes de production pour un type de travail et un type de produit spécifique dans SIB.
        oCreerEtapesTypeTravail = CreerEtapesTypeTravail()
        
        #Valider les paramètres obligatoires
        oCreerEtapesTypeTravail.validerParamObligatoire(env, ty_travail, ty_produit, tableEtapes)
        
        #Exécuter le traitement de création d'une liste des étapes de production pour un type de travail et un type de produit spécifique dans SIB.
        oCreerEtapesTypeTravail.executer(env, ty_travail, ty_produit, tableEtapes, detruire)
    
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