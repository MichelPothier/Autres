#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerEtapesTypeTravail.py
# Auteur    : Michel Pothier
# Date      : 12 novembre 2014

"""
    Application qui permet de cr�er la liste des �tapes de production pour un type de travail et un type de produit sp�cifique dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    ty_travail      OB      Type de travail.
                            d�faut = 
    ty_produit      OB      Type de produit.
                            d�faut = 
    tableEtapes     OB      Liste des �tapes de production et de ses param�tres de traitement.
                            d�faut =
                            Attention : Si les �tapes de production existe d�j�, le traitement ne se fera pas � moins de forcer � les d�truire.
    detruire        OB      Indique si on doit d�truire les �tapes de production existantes [True/False].
                            d�faut = False
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerEtapesTypeTravail(object):
#*******************************************************************************************
    """
    Permet de cr�er la liste des �tapes de production pour un type de travail et un type de produit sp�cifique dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'une liste des �tapes de production pour un type de travail et un type de produit sp�cifique.
        
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
    def validerParamObligatoire(self, env, ty_travail, ty_produit, tableEtapes):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        tableEtapes     : Liste des �tapes de production et de ses param�tres de traitement.

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

        if (len(tableEtapes) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'tableEtapes')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_travail, ty_produit, tableEtapes, detruire):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'une liste des �tapes de production pour un type de travail et un type de produit sp�cifique dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        ty_travail      : Type de travail.
        ty_produit      : Type de produit.
        tableEtapes     : Liste des �tapes de production et de ses param�tres de traitement.
        detruire        : Indique si on doit d�truire les �tapes de production existantes [True/False].
        
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
        
        #-----------------------------------------------------
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #--------------------------------------------
        #D�finir la liste des �tapes permises
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�finir la liste des �tapes permises")
        sql = "SELECT CD_ETP FROM F117_ET WHERE ACTIVE=1 ORDER BY CD_ETP"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Initialiser la liste des �tapes permises
        listeEtapes = []
        #Construire la liste des �tapes permises
        for etape in resultat:
            listeEtapes.append(etape[0])
        #Afficher la liste des codes d'�tape
        arcpy.AddMessage(str(listeEtapes))
        
        #-----------------------------------------------------
        #Valider la pr�sence des �tapes de production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider la pr�sence des �tapes de production existantes")
        sql = "SELECT NO_SEQ,CD_ETP,FLOTTANTE,RETOUR,ITERATIVE,DT_RECU_REQ,DT_DEB_REQ FROM F106_EI WHERE TY_PRODUIT='" + ty_produit + "' AND TY_TRAV='" + ty_travail + "' ORDER BY NO_SEQ"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence des �tapes de production
        if resultat:
            #V�rifier si on doit d�truire les �tapes existantes
            if detruire:
                #Afficher les �tapes existantes
                for row in resultat:
                    arcpy.AddMessage(str(row))
                #D�truire les �tapes de production existantes
                sql = "DELETE F106_EI WHERE TY_PRODUIT='" + ty_produit + "' AND TY_TRAV='" + ty_travail + "'"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
            
            #Si on ne doit pas d�truire les �tapes existantes
            else:
                #Retourner une exception
                raise Exception(u"La liste des �tapes de production est d�j� pr�sente, nombre d'�tapes = " + str(len(resultat)))
        
        #-----------------------------------------------------
        #Valider la liste des �tapes de production et leurs param�tres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider la liste des �tapes de production et leurs param�tres")
        #Initialiser le num�ro de s�quence
        no_seq = 0
        #Afficher les valeurs d'attributs
        attributs = ["CD_ETP", "FLOTTANTE", "RETOUR", "ITERATIVE", "DT_RECU_REQ", "DT_DEB_REQ"]
        arcpy.AddMessage(str(attributs))
        #Traiter tous les �l�ments de la table
        for row in arcpy.da.SearchCursor(tableEtapes, attributs):
            #D�finir le num�ro de s�quence
            no_seq = no_seq + 1
            #Afficher les valeurs d'attributs
            arcpy.AddMessage(str(no_seq) + " : " + str(row))
            
            #V�rifier si l'�tape est valide
            if str(row[0]) not in listeEtapes:
                #Retourner un message d'erreur
                raise Exception(u"Le code d'�tape est invalide : " + str(row[0]))
            
            #V�rifier si le fanion de l'�tape flottante est valide
            if str(row[1]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de l'�tape flottante est invalide : " + str(row[1]))
            
            #V�rifier si le fanion de l'�tape flottante est valide
            if str(row[3]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de l'�tape it�rative est invalide : " + str(row[3]))
            
            #V�rifier si l'�tape est non-it�rative
            if row[3] == 0:
                #V�rifier si la valeur de l'attribut RETOUR <> 0
                if row[2] <> 0:
                    #Retourner un message d'erreur
                    raise Exception(u"La valeur de l'attribut RETOUR doit etre 0 lorsque l'etape est non-iterative")
            #V�rifier si l'�tape est it�rative
            else:
                #V�rifier si la valeur de l'attribut RETOUR = 0 et > no_seq
                if row[2] == 0 or row[2] > no_seq:
                    #Retourner un message d'erreur
                    raise Exception(u"La valeur de l'attribut RETOUR doit plus grand que 0 et inferieure au NO_SEQ lorsque l'etape est iterative")

            #V�rifier si le fanion de la date re�u est valide
            if str(row[4]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de la date re�u est invalide : " + str(row[4]))
            
            #V�rifier si le fanion de la date de d�but est valide
            if str(row[5]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de la date de d�but est invalide : " + str(row[5]))
        
        #-----------------------------------------------------
        #Ajouter la liste des �tapes de production et leurs param�tres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter la liste des �tapes de production et leurs param�tres")
        #Initialiser le num�ro de s�quence
        no_seq = 0
        #Traiter tous les �l�ments de la table
        for row in arcpy.da.SearchCursor(tableEtapes, attributs):
            #D�finir le num�ro de s�quence
            no_seq = no_seq + 1
            #Ajouter une �tapes de production
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        ty_travail  = ""
        ty_produit  = ""
        tableEtapes = ""
        detruire    = False
        
        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet de cr�ation d'une liste des �tapes de production pour un type de travail et un type de produit sp�cifique dans SIB.
        oCreerEtapesTypeTravail = CreerEtapesTypeTravail()
        
        #Valider les param�tres obligatoires
        oCreerEtapesTypeTravail.validerParamObligatoire(env, ty_travail, ty_produit, tableEtapes)
        
        #Ex�cuter le traitement de cr�ation d'une liste des �tapes de production pour un type de travail et un type de produit sp�cifique dans SIB.
        oCreerEtapesTypeTravail.executer(env, ty_travail, ty_produit, tableEtapes, detruire)
    
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