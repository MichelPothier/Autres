#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : FermerIntervalleFinNonConformiteCourant.py
# Auteur    : Michel Pothier
# Date      : 01 avril 2015

"""
Outil qui permet de fermer les intervalles de fin d'une non-conformit� pour des identifiants avec jeux courants.

-L'intervalle d�'�dition-version est ferm�e selon le num�ro d'�dition et version maximale des identifiants non-courants. 
-Si toutes les intervalles de fin sont inscrits, alors la date de fin de traitement est inscrite pour permettre de fermer la non-conformit�.
-Au besoin, le responsable de l�'�quipe Qualit� des donn�es re�oit alors un courriel lui indiquant la fin des travaux.

Attention : Seule les non-conformit�s avec jeux courants peuvent �tre trait�es par ce programme.

Param�tres d'entr�es:
----------------------
env         OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                    D�faut = SIB_PRO
produit     OB      Type de produit des identifiants de la non-conformit� � fermer.
                    D�faut = 'RHN'
no_nc       OB      Num�ro de la non-conformit� � fermer.
                    D�faut = 
identifiant OB      Identifiants pour lesquel on veut fermer l'intervalle de fin (identifiant:ed:ver).
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
    FermerIntervalleFinNonConformiteCourant.py env produit no_nc identifiant

Exemple:
    FermerIntervalleFinNonConformiteCourant.py SIB_PRO RHN 02997 021M07:1:0:BDG;021M08:2:1:BDG

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FermerIntervalleFinNonConformiteCourant.py 2157 2018-07-12 16:19:56Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s
import EnvoyerCourriel, CompteSib

#*******************************************************************************************
class FermerIntervalleFinNonConformiteCourant(object):
#*******************************************************************************************
    """
    Permet de fermer les intervalles de fin d'une non-conformit� pour des identifiants avec jeux courants.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour fermer les intervalles de fin d'une non-conformit� pour des identifiants avec jeux courants.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

        #Initialisation du compteur de modifications
        self.nbModif = 0
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, produit, no_nc, identifiant):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        produit     : Type de produit des identifiants de la non-conformit� � fermer.
        no_nc       : Num�ro de la non-conformit� � fermer.
        identifiant : Identifiants pour lesquel on veut fermer l'intervalle de fin (identifiant:ed:ver).
        
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
        if (len(no_nc) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'no_nc')

        #V�rifier la pr�sence du param�tre
        if (len(identifiant) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'identifiant')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, produit, no_nc, identifiant, corriger):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour fermer les intervalles de fin d'une non-conformit� pour des identifiants avec jeux courants.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        produit     : Type de produit des identifiants de la non-conformit� � fermer.
        no_nc       : Num�ro de la non-conformit� � fermer.
        identifiant : Identifiants pour lesquel on veut fermer l'intervalle de fin (identifiant:ed:ver).
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
            raise Exception("Aucune non-conformit� n'est pr�sente pour ce produit : %s" %produit)
        
        #Extraction de l'information de la non-conformit�
        arcpy.AddMessage("- Validation du num�ro de la non-conformit� : " + str(no_nc))
        sql = ("SELECT DATE_FERMETURE, DATE_TRAITEMENT, TY_NC, TY_TRAIT_NC, RESP_DESCR, RESP_CORR, RESP_SUIVI"
               "  FROM F702_NC"
               " WHERE NO_NC='" + no_nc + "'")
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence du param�tre
        if (len(resultat) == 0):
            raise Exception("Num�ro de non-conformit� invalide : %s" %no_nc)
        #V�rifier si la non-conformit� est ferm�e
        if resultat[0][0] <> None:
            raise Exception("La non-conformit� est ferm�e : date_fermeture=%s" %resultat[0][0])
        #V�rifier si la non-conformit� a d�j� �t� trait�e
        if resultat[0][1] <> None:
            raise Exception("La non-conformit� a d�j� �t� trait�e : date_traitement=%s" %resultat[0][1])
        
        #Conserver l'information de la non-conformit�
        resp_descr = resultat[0][4]
        resp_corr = resultat[0][5]
        resp_suivi = resultat[0][6]
        
        #Afficher les valeurs
        arcpy.AddMessage(str(resultat))
        
        #Extraction des m�tadonn�es d'identifiants de la non-conformit�
        arcpy.AddMessage("- Fermer l'intervalle de fin des identifiants non-conformes : " + str(no_nc))
        
        #Traiter tous les identifiants
        for item in identifiant.split(","):
            #Afficher les valeurs
            arcpy.AddMessage(" ")
            arcpy.AddMessage("--" + str(item))
            #D�finir les variables
            val = item.split(":")
            id = val[0]            #identifiant
            ed_debut = val[1]      #ed_debut
            ver_debut = val[2]     #ver_debut
            
            #Construire la sql pour v�rifier si l'identifiant poss�de un jeu courant
            sql = ("SELECT IDENTIFIANT, ED, VER"
                   "  FROM V200_IN"
                   " WHERE TY_PRODUIT='" + produit + "' AND IDENTIFIANT='" + id + "' AND JEU_COUR=1")
            #Ex�cuter la requ�te
            resultat = self.Sib.requeteSib(sql)
            #V�rifier la pr�sence d'un jeu courant
            if not resultat:
                #Retourner une erreur
                arcpy.AddMessage(sql)
                raise Exception("L'dentifiant ne poss�de pas un jeu courant.")
            #D�finir l'�dition et version courante
            ed_cour=resultat[0][1]
            ver_cour=resultat[0][2]
            arcpy.AddMessage("--Ed.Ver_Cour:" + str(float(str(ed_cour) + "." + str(ver_cour))))
            
            #Construire la sql pour v�rifier si l'identifiant, �dition et version n'est pas non-conforme
            sql = ("SELECT ED_FIN, VER_FIN"
                   "  FROM F705_PR"
                   " WHERE TY_PRODUIT='" + produit + "' AND IDENTIFIANT='" + id + "' AND ED_DEBUT=" + ed_debut + " AND VER_DEBUT=" + ver_debut + " AND NO_NC='" + no_nc + "'")
            #Ex�cuter la requ�te
            arcpy.AddMessage("--" + sql)
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si l'identifiant, �dition et version n'est pas non-conforme
            if not resultat:
                #Retourner une erreur
                raise Exception("L'identifiant, �dition et version n'est pas non-conforme.")
            
            #D�finir l'�dition et version de fin
            ed_fin = resultat[0][0]        #ed_fin
            ver_fin = resultat[0][1]       #ver_fin
            arcpy.AddMessage("--Ed.Ver_Fin:" + str(float(str(ed_fin) + "." + str(ver_fin))))
            
            #V�rifier si l'intervalle de fin n'est pas trait�e
            if ed_fin == 99999:
                #Cr�er la requ�te SQL pour extraire l'�dition maximale des jeux non-courants
                sql = ("SELECT MAX(ed) FROM V200_IN WHERE TY_PRODUIT='" + produit + "' AND IDENTIFIANT='" + id + "' AND JEU_COUR=0")
                #arcpy.AddMessage(sql)
                #Ex�cuter la requ�te SQL
                resultat = self.Sib.requeteSib(sql)
                #V�rifier la pr�sence du param�tre
                if (str(resultat[0][0]) == 'None'):
                        #Red�finir l'�dition et version maximum
                        ed_max = ed_cour
                        ver_max = ver_cour
                else:
                    #Extraire la valeur de l'�dition maximale
                    ed_max = resultat[0][0]
                    
                    #Cr�er la requ�te SQL pour extraire l'�dition maximale des jeux non-courants
                    sql = ("SELECT MAX(ver)"
                           "  FROM V200_IN"
                           " WHERE TY_PRODUIT='" + produit + "' and IDENTIFIANT='" + id + "' AND ED=" + str(ed_max) + " AND JEU_COUR=0")
                    #arcpy.AddMessage(sql)
                    #Ex�cuter la requ�te SQL
                    resultat = self.Sib.requeteSib(sql)
                    #V�rifier la pr�sence du param�tre
                    if (str(resultat[0][0]) == 'None'):
                        #Retourner une erreur
                        raise Exception("La version maximum est erronn�e.")
                    #Extraire la valeur de la version maximale
                    ver_max = resultat[0][0]
                
                #V�rifier si l'�dition.version de d�but est plus �lev� ou �gale que l'�dition.version finale
                if float(str(ed_debut) + "." + str(ver_debut)) > float(str(ed_max) + "." + str(ver_max)):
                    #Afficher un avertissement
                    arcpy.AddWarning("--Ed.Ver_D�but:" + str(float(str(ed_debut) + "." + str(ver_debut))) + " > Ed.Ver_Max:" + str(float(str(ed_max) + "." + str(ver_max))))
                    #Red�finir l'�dion et version maximum
                    ed_max = ed_cour
                    ver_max = ver_cour
                
                #Cr�er la commande SQL pour modifier l'�dition et version de fin
                sql = ("UPDATE F705_PR SET ETAMPE='" + sUsagerBd + "', DT_M=SYSDATE, ED_FIN=" + str(ed_max) + ", VER_FIN=" + str(ver_max) + " "
                       " WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + produit + "' AND IDENTIFIANT='" + id + "'"
                       "   AND ED_DEBUT=" + str(ed_debut) + " AND VER_DEBUT=" + str(ver_debut))
                arcpy.AddMessage(sql + ";")
                #Ex�cuter la commande
                if corriger:
                    self.Sib.execute(sql)
                    
                #Compteur de modifications
                self.nbModif = self.nbModif + 1
            
            #si l'intervalle de fin est d�j� trait�e
            else:
                #Afficher un avertissement
                arcpy.AddWarning("L'intervalle de fin est d�ja trait�e")
                
        #Afficher le nombre de modifications effectu�es
        arcpy.AddMessage(" ")
        arcpy.AddWarning("Nombre total de modifications effectu�es : " + str(self.nbModif))
        
        #Construire la sql pour extraire les identifiants non-ferm�s
        sql = ("SELECT IDENTIFIANT"
               "  FROM F705_PR"
               " WHERE NO_NC='" + no_nc + "' AND ED_FIN=99999"
               " ORDER BY IDENTIFIANT")
        #Afficher la sql
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te
        resultat = self.Sib.requeteSib(sql)
        
        #V�rifier si toutes les intervalles de fin sont trait�es
        if len(resultat) == 0:
            #Mettre � jour la date de traitement
            arcpy.AddMessage("- Mise � jour de la date de traitement")
            sql = ("UPDATE F702_NC"
                   "   SET ETAMPE='" + sUsagerBd + "', DT_M=SYSDATE, DATE_TRAITEMENT=SYSDATE"
                   " WHERE NO_NC='" + no_nc + "'")
            arcpy.AddMessage(sql + ";")
            if corriger:
                self.Sib.execute(sql)

            arcpy.AddMessage("- Envoit d'un courriel aux responsables")
            sql = ("SELECT DISTINCT ADR_EMAIL"
                   "  FROM F005_US"
                   " WHERE CD_USER='" + str(resp_descr) + "' OR CD_USER='" + str(resp_corr) + "' OR CD_USER='" + str(resp_suivi) +  "'")
            #Ex�cuter la requ�te SQL
            resultat = self.Sib.requeteSib(sql)
            #Envoyer un courriel aux responsables
            for courriel in resultat:
                #Envoyer un courriel
                destinataire = str(courriel[0])
                sujet = unicode("Fermeture de l'intervalle de fin de la non-conformit� #" + no_nc, "utf-8")
                contenu = unicode("Bonjour,\n\nTous les jeux de donn�es associ�s � la non conformit� #" + no_nc + " sont maintenant ferm�s.\n\n" + sUsagerSib + "\n" + sUsagerBd, "utf-8")
                arcpy.AddMessage("EnvoyerCourriel('" + destinataire + "','" + sujet + "')")
                if corriger:
                    EnvoyerCourriel.EnvoyerCourriel(destinataire,contenu, sujet)
        
        #S'il reste des identifiants non ferm�s
        else:
            #Envoyer un avertissement
            arcpy.AddMessage(" ")
            arcpy.AddWarning("La non-conformit� n'est pas ferm�e.")
            arcpy.AddWarning("Nombre total d'identifiants qui n'ont pas d'intervalle de fin : " + str(len(resultat)))
            arcpy.AddWarning(str(resultat))
        
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
        produit = 'RHN'
        no_nc = ""
        identifiant = ""
        corriger = False
        
        # Lecture des param�tres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            produit = sys.argv[2].upper()

        if len(sys.argv) > 3:
            no_nc = sys.argv[3].split(":")[0]
            
        if len(sys.argv) > 4:
            identifiant = sys.argv[4].upper().replace(";",",")
            
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                corriger = sys.argv[5].upper() == "TRUE"
        
        #D�finir l'objet pour fermer les intervalles de fin d'une non-conformit� pour des identifiants avec jeux courants.
        oFermerIntervalleFinNonConformiteCourant = FermerIntervalleFinNonConformiteCourant()
        
        #Valider les param�tres obligatoires
        oFermerIntervalleFinNonConformiteCourant.validerParamObligatoire(env, produit, no_nc, identifiant)
        
        #Ex�cuter le traitement pour fermer les intervalles de fin d'une non-conformit� pour des identifiants avec jeux courants.
        oFermerIntervalleFinNonConformiteCourant.executer(env, produit, no_nc, identifiant, corriger)
    
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