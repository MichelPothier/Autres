#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : FermerIntervalleFinNonConformiteInvalide.py
# Auteur    : Michel Pothier
# Date      : 22 ao�t 2017

"""
Outil qui permet de fermer les intervalles de fin pour les non-conformit�s qui poss�dent une date de fermeture et pour lesquels aucune �dition et version de fin sont pr�sente.

-L'intervalle d?'�dition-version d'un identifiant est ferm�e selon le num�ro d'�dition et version de d�but. 

Attention : Seules les non-conformit�s avec une date de fermeture peuvent �tre trait�es par ce programme.

Param�tres d'entr�es:
----------------------
env         OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                    D�faut = SIB_PRO
produit     OB      Type de produit des identifiants de non-conformit� � fermer.
                    D�faut = 'BDG'
ty_nc       OB      Liste des types de non-conformit� � fermer.
                    Le type de non-conformit�.
                    �OP : Observation produit
                    �DM : Donn�es modifi�es dans la BD
                    �PA : Plainte autre
                    �PP : Plainte produit
                     Ne sont plus utilis�s:
                    �ND : Non-disponible
                    �OA : Observation autre
                    �PD : Plainte de distrubution non-active
                    �SQ : Syst�me qualit�
                    D�faut = <Selon les non-conformit�s dont l'intervalle de fin est invalide>
no_nc       OB      Liste des num�ros de non-conformit� � fermer.
                    D�faut = 
corriger    OP      Indique si on doit corriger.
                    D�faut = false

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
Usage:
    FermerIntervalleFinNonConformiteInvalide.py env produit no_nc

Exemple:
    FermerIntervalleFinNonConformiteInvalide.py SIB_PRO BDG DM,OP,PP 02997;02888

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FermerIntervalleFinNonConformiteInvalide.py 2135 2017-08-23 13:31:54Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s
import EnvoyerCourriel, CompteSib

#*******************************************************************************************
class FermerIntervalleFinNonConformiteInvalide(object):
#*******************************************************************************************
    """
    Permet de fermer les intervalles de fin pour les non-conformit�s qui poss�dent une date de fermeture
    et pour lesquels aucune �dition et version de fin sont pr�sente.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour fermer les intervalles de fin pour les non-conformit�s qui poss�dent une date de fermeture
        et pour lesquels aucune �dition et version de fin sont pr�sente.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

        #Initialisation du compteur d'identifiants
        self.nbId = 0
        
        #Initialisation du compteur de modifications
        self.nbModif = 0
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, produit, ty_nc, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        produit     : Type de produit des identifiants de non-conformit� � fermer.
        no_nc       : Liste des types de non-conformit� � fermer.
        no_nc       : Liste des num�ros de non-conformit� � fermer.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire.
        
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        #V�rifier la pr�sence du param�tre
        if (len(env) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'env')

        #V�rifier la pr�sence du param�tre
        if (len(produit) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'produit')

        #V�rifier la pr�sence du param�tre
        if (len(ty_nc) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'ty_nc')

        #V�rifier la pr�sence du param�tre
        if (len(no_nc) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'no_nc')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, produit, ty_nc, no_nc, corriger):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour fermer les intervalles de fin d'une non-conformit� pour des identifiants avec jeux courants.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        produit     : Type de produit des identifiants de la non-conformit� � fermer.
        no_nc       : Liste des types de non-conformit� � fermer.
        no_nc       : Liste des num�ros de non-conformit� � fermer.
        corriger    : Indique si on doit corriger.

        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        ed_debut        : �dition de d�but de la non-conformit�.
        ver_debut       : Version de d�but de la non-conformit�.
        ed_max          : �dition maximum de l'identifiant.
        ver_max         : Version maximum de l'identifiant.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        sUsagerBd = self.CompteSib.UsagerBd()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'ISO-RQNC'")

        #Extraction de l'information de la non-conformit�
        arcpy.AddMessage("- Validation du type de produit de la non-conformit� : " + produit)
        sql = ("SELECT DISTINCT TY_PRODUIT"
               "  FROM F705_PR"
               " WHERE TY_PRODUIT='" + produit + "' AND ED_FIN=99999")
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence du param�tre
        if (len(resultat) == 0):
            arcpy.AddMessage(sql)
            raise Exception("Aucune non-conformit� n'est pr�sente pour ce produit : %s" %produit)
        
        #Traiter tous les non-conformit�s
        for item in no_nc.split(","):
            #D�finir le num�ro de non-conformit�
            nc = item.split(" ")[0]
            
            #Traiter la non-conformit�
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Traitement de la non-conformit� : " + nc + " ...")
            sql = ("SELECT PR.IDENTIFIANT, PR.ED_DEBUT, PR.VER_DEBUT"
                   "  FROM F702_NC NC, F705_PR PR"
                   " WHERE PR.TY_PRODUIT='" + produit + "' AND NC.NO_NC='" + nc + "' AND NC.NO_NC=PR.NO_NC"
                   "   AND PR.ED_FIN=99999 AND NC.DATE_TRAITEMENT IS NOT NULL")
            arcpy.AddMessage(sql)
            #Ex�cuter la requ�te SQL
            resultat = self.Sib.requeteSib(sql)

            #Traiter tous les identifiants
            for identifiant in resultat:
                #Compter les identifiants
                self.nbId = self.nbId + 1

                #D�finir les valeurs
                id = identifiant[0]
                ed_debut = str(identifiant[1])
                ver_debut = str(identifiant[2])
                
                #Cr�er la commande SQL pour modifier l'�dition et version de fin
                sql = ("UPDATE F705_PR"
                       "   SET ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, ED_FIN=" + ed_debut + ", VER_FIN=" + ver_debut + " "
                       " WHERE NO_NC='" + nc + "' AND TY_PRODUIT='" + produit + "' AND IDENTIFIANT='" + id + "'")
                arcpy.AddMessage(sql + ";")
                
                #V�rifier s'il faut corriger
                if corriger:
                    #Ex�cuter la commande
                    self.Sib.execute(sql)
                    #Compter les modifications
                    self.nbModif = self.nbModif + 1
            
            #Afficher le nombre d'identifiant
            arcpy.AddWarning("Nombre d'identifiants : " + str(len(resultat)))
                
        #Afficher le nombre de modifications effectu�es
        arcpy.AddMessage(" ")
        arcpy.AddWarning("Nombre total d'identifiants : " + str(self.nbId))
        arcpy.AddWarning("Nombre total de modifications effectu�es : " + str(self.nbModif))
        
        #Accepter les modifications si on corrige
        if corriger:
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Accepter les modifications")
            sql = "COMMIT"
            arcpy.AddMessage(sql + ";")
            self.Sib.execute(sql)
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        self.Sib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "SIB_PRO"
        produit = 'BDG'
        ty_nc = ""
        no_nc = ""
        corriger = False
        
        # Lecture des param�tres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            produit = sys.argv[2].upper()

        if len(sys.argv) > 3:
            ty_nc = sys.argv[3].upper().replace(";",",").replace("'","")

        if len(sys.argv) > 4:
            no_nc = sys.argv[4].replace(";",",").replace("'","")
            
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                corriger = sys.argv[5].upper() == "TRUE"
        
        #D�finir l'objet pour fermer les intervalles de fin pour les non-conformit�s qui poss�dent une date de fermeture
        oFermerIntervalleFinNonConformiteInvalide = FermerIntervalleFinNonConformiteInvalide()
        
        #Valider les param�tres obligatoires
        oFermerIntervalleFinNonConformiteInvalide.validerParamObligatoire(env, produit, ty_nc, no_nc)
        
        #Ex�cuter le traitement pour fermer les intervalles pour les non-conformit�s qui poss�dent une date de fermeture
        oFermerIntervalleFinNonConformiteInvalide.executer(env, produit, ty_nc, no_nc, corriger)
    
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