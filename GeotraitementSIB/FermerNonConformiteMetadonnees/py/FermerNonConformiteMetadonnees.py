#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : FermerNonConformiteMetadonnees.py
# Auteur    : Michel Pothier
# Date      : 01 d�cembre 2014

"""
Outil qui permet de fermer une non-conformit� de m�tadonn�es.

La fermeture d'une non-conformit� est r�alis�e seulement apr�s avoir effectu� une correction INSITU dans les m�tadonn�es de SIB.
-Le num�ro de version des m�tadonn�es est incr�ment�.
-L'intervalle d��dition-version est ferm�e selon le num�ro d'�dition et version du jeu courant. 
-Si toutes les intervalles de fin sont inscrits, alors la date de fin de traitement est inscrite pour permettre de fermer la non-conformit�. 
-Le responsable de l��quipe Qualit� des donn�es re�oit alors un courriel lui indiquant la fin des travaux.

Attention : Seule les non-conformit�s de type DM et dont le type de traitement est ME% peuvent �tre trait�es par ce programme.

Param�tres d'entr�es:
----------------------
env         OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                    D�faut = SIB_PRO
no_nc       OB      Num�ro de la non-conformit� � fermer.
                    D�faut = 
no_tache    OB      Num�ro de ticket Alloy (Exemple : T011343).
                    D�faut = 

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
Usage:
    FermerNonConformiteMetadonnees.py env no_nc no_tache

Exemple:
    FermerNonConformiteMetadonnees.py SIB_PRO 02997 T011107

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FermerNonConformiteMetadonnees.py 2124 2016-09-19 13:52:18Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s
import EnvoyerCourriel, CompteSib

#*******************************************************************************************
class FermerNonConformiteMetadonnees(object):
#*******************************************************************************************
    """
    Permet de fermer une non-conformit� de m�tadonn�es.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour fermer une non-conformit� de m�tadonn�es.
        
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
    def validerParamObligatoire(self, env, no_nc, no_tache):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        no_nc       : Num�ro de la non-conformit� � fermer.
        no_tache    : Num�ro de t�che Alloy.
        
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
        if (len(no_nc) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'no_nc')

        #V�rifier la pr�sence du param�tre
        if (len(no_tache) == 0):
            raise Exception("- Param�tre obligatoire manquant: %s" %'no_tache')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, no_tache):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour fermer une non-conformit� de m�tadonn�es.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        no_nc       : Num�ro de la non-conformit� � fermer.
        no_tache    : Num�ro de t�che Alloy.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        ty_produit      : Type de produit trait�.
        identifiant     : Identifiant de d�coupage trait�.
        ed_fin          : �dition de fin de la non-conformit�.
        ver_fin         : Version de fin de la non-conformit�.
        ed_cour         : �dition courante du jeu de donn�es.
        ver_cour        : Version courante du jeu de donn�es.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        sUsagerBd = self.CompteSib.UsagerBd()
        
        #Extraction de l'information de la non-conformit�
        arcpy.AddMessage("- Extraction de l'information de la non-conformit� : " + str(no_nc))
        sql = "SELECT DATE_FERMETURE,DATE_TRAITEMENT,TY_NC,TY_TRAIT_NC,RESP_DESCR,RESP_CORR,RESP_SUIVI FROM F702_NC WHERE NO_NC='" + no_nc + "'"
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
        #V�rifier si la non-conformit� a d�j� �t� trait�e
        if resultat[0][2] <> "DM":
            raise Exception("Le type de non-conformit� n'est pas 'DM' : TY_NC=%s" %resultat[0][2])
        #V�rifier si la non-conformit� a d�j� �t� trait�e
        if "ME" not in resultat[0][3]:
            raise Exception("Le type de traitement de non-conformit� n'est pas 'ME%' : TY_TRAIT_NC=%s" %resultat[0][3])
        #Conserver l'information de la non-conformit�
        resp_descr = resultat[0][4]
        resp_corr = resultat[0][5]
        resp_suivi = resultat[0][6]
        #Afficher les valeurs
        arcpy.AddMessage(str(resultat))
        
        #Extraction des m�tadonn�es d'identifiants de la non-conformit�
        arcpy.AddMessage("- Extraction des identifiants non-conformes : " + str(no_nc))
        sql = "SELECT TY_PRODUIT,IDENTIFIANT,ED_DEBUT,VER_DEBUT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' ORDER BY IDENTIFIANT"
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te
        resultat = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence du param�tre
        if (len(resultat) == 0):
            #Retourner une erreur
            raise Exception("Aucun identifiant n'est associ� � la non-conformit�")
        
        #Traiter toutes les items
        for item in resultat:
            #Afficher les valeurs
            arcpy.AddMessage(str(item))
            #D�finir les variables
            ty_produit = item[0]    #ty_produit
            identifiant = item[1]   #identifiant
            ed_debut = item[2]      #ed_debut
            ver_debut = item[3]     #ver_debut
            ed_fin = item[4]        #ed_fin
            ver_fin = item[5]       #ver_fin
            
            #V�rifier si l'intervalle de fin n'est pas trait�e
            if ed_fin == 99999:
                #Cr�er la requ�te SQL (pour extraire l'�dition et la version du jeu courant ainsi que la version des m�tadonn�es)
                sql = "SELECT ed,ver,ver_meta FROM F235_PR WHERE ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "' and jeu_cour=1"
                arcpy.AddMessage(sql)
                #Ex�cuter la requ�te SQL
                resultat2 = self.Sib.requeteSib(sql)
                #V�rifier la pr�sence du param�tre
                if (len(resultat) == 0):
                    raise Exception("Aucun jeu courant n'est pr�sent dans la table F235_pr")
                #Extraire la valeur de l'�dition et version courante
                ed_cour = resultat2[0][0]
                ver_cour = resultat2[0][1]
                ver_meta = resultat2[0][2]
                #V�rifier si l'�dition.version de d�but est plus �lev� que l'�dition.version courante
                if float(str(ed_debut) + "." + str(ver_debut)) > float(str(ed_cour) + "." + str(ver_cour)):
                    #Retourner une erreur
                    raise Exception("Ed.Ver_D�but:" + str(float(str(ed_debut) + "." + str(ver_debut))) + " > Ed.Ver_Cour:" + str(float(str(ed_cour) + "." + str(ver_cour))))
                #Afficher les valeurs
                arcpy.AddMessage(str(resultat2))
                
                #Cr�er la commande SQL pour modifier l'�dition et version de fin
                sql = "UPDATE F705_PR SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,ed_fin=" + str(ed_cour) + ",ver_fin=" + str(ver_cour) + " WHERE no_nc='" + no_nc + "' AND ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "'"
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
                
                #-----------------------------------
                #Modifier la date des m�tadonn�es
                arcpy.AddMessage("  -Modifier la date des m�tadonn�es ...")
                sql = "UPDATE F235_MR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, DT_METADATA=TO_CHAR(SYSDATE, 'YYYYMMDD') WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed_cour) + " AND VER=" + str(ver_cour)
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
                
                #Incr�menter la version des m�tadonn�es
                ver_meta = ver_meta + 1
                #Cr�er la commande SQL pour modifier la version des m�tadonn�es
                sql = "UPDATE F235_PR SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,ver_meta=" + str(ver_meta) + " WHERE ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "' and jeu_cour=1"
                arcpy.AddMessage(sql)
                #Ex�cuter la commande
                self.Sib.execute(sql)
            
            #si l'intervalle de fin est d�j� trait�e
            else:
                #Afficher un avertissement
                arcpy.AddWarning("L'intervalle de fin est d�ja trait�e")
        
        #Mettre � jour la date de traitement
        arcpy.AddMessage("- Mise � jour de la date de traitement")
        sql = "UPDATE F702_NC SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,DATE_TRAITEMENT=SYSDATE WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        arcpy.AddMessage("- Envoit d'un courriel aux responsables")
        sql = "SELECT DISTINCT ADR_EMAIL FROM F005_US WHERE CD_USER='" + str(resp_descr) + "' OR CD_USER='" + str(resp_corr) + "' OR CD_USER='" + str(resp_suivi) +  "'"
        #Ex�cuter la requ�te SQL
        resultat = self.Sib.requeteSib(sql)
        #Envoyer un courriel aux responsables
        for courriel in resultat:
            #Envoyer un courriel
            destinataire = str(courriel[0])
            sujet = unicode("Fermeture de la correction INSITU de la non-conformit� #" + no_nc, "utf-8")
            contenu = unicode("Bonjour,\n\nTous les jeux de donn�es associ�s � la non conformit� #" + no_nc + " sont maitenant corrig�s.\n\n" + sUsagerSib + "\n" + sUsagerBd, "utf-8")
            arcpy.AddMessage("EnvoyerCourriel('" + destinataire + "','" + sujet + "')")
            EnvoyerCourriel.EnvoyerCourriel(destinataire,contenu, sujet)
        
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
        no_nc = ""
        no_tache = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
            
        if len(sys.argv) > 3:
            no_tache = sys.argv[3].upper()
        
        #D�finir l'objet pour fermer une non-conformit� de m�tadonn�es.
        oFermerNonConformiteMetadonnees = FermerNonConformiteMetadonnees()
        
        #Valider les param�tres obligatoires
        oFermerNonConformiteMetadonnees.validerParamObligatoire(env,no_nc,no_tache)
        
        #Ex�cuter le traitement pour fermer une non-conformit� de m�tadonn�es.
        oFermerNonConformiteMetadonnees.executer(env, no_nc, no_tache)
    
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