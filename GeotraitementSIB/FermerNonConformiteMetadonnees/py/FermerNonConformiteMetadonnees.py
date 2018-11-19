#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : FermerNonConformiteMetadonnees.py
# Auteur    : Michel Pothier
# Date      : 01 décembre 2014

"""
Outil qui permet de fermer une non-conformité de métadonnées.

La fermeture d'une non-conformité est réalisée seulement après avoir effectué une correction INSITU dans les métadonnées de SIB.
-Le numéro de version des métadonnées est incrémenté.
-L'intervalle d’édition-version est fermée selon le numéro d'édition et version du jeu courant. 
-Si toutes les intervalles de fin sont inscrits, alors la date de fin de traitement est inscrite pour permettre de fermer la non-conformité. 
-Le responsable de l’équipe Qualité des données reçoit alors un courriel lui indiquant la fin des travaux.

Attention : Seule les non-conformités de type DM et dont le type de traitement est ME% peuvent être traitées par ce programme.

Paramètres d'entrées:
----------------------
env         OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                    Défaut = SIB_PRO
no_nc       OB      Numéro de la non-conformité à fermer.
                    Défaut = 
no_tache    OB      Numéro de ticket Alloy (Exemple : T011343).
                    Défaut = 

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
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

# Importation des modules privés
import EnvoyerCourriel, CompteSib

#*******************************************************************************************
class FermerNonConformiteMetadonnees(object):
#*******************************************************************************************
    """
    Permet de fermer une non-conformité de métadonnées.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour fermer une non-conformité de métadonnées.
        
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
    def validerParamObligatoire(self, env, no_nc, no_tache):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        no_nc       : Numéro de la non-conformité à fermer.
        no_tache    : Numéro de tâche Alloy.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire.
        
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        #Vérifier la présence du paramètre
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')

        #Vérifier la présence du paramètre
        if (len(no_nc) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'no_nc')

        #Vérifier la présence du paramètre
        if (len(no_tache) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'no_tache')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, no_tache):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour fermer une non-conformité de métadonnées.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        no_nc       : Numéro de la non-conformité à fermer.
        no_tache    : Numéro de tâche Alloy.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : Résultat de la requête SIB.
        ty_produit      : Type de produit traité.
        identifiant     : Identifiant de découpage traité.
        ed_fin          : Édition de fin de la non-conformité.
        ver_fin         : Version de fin de la non-conformité.
        ed_cour         : Édition courante du jeu de données.
        ver_cour        : Version courante du jeu de données.
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        sUsagerBd = self.CompteSib.UsagerBd()
        
        #Extraction de l'information de la non-conformité
        arcpy.AddMessage("- Extraction de l'information de la non-conformité : " + str(no_nc))
        sql = "SELECT DATE_FERMETURE,DATE_TRAITEMENT,TY_NC,TY_TRAIT_NC,RESP_DESCR,RESP_CORR,RESP_SUIVI FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        #Exécuter la requête SQL
        resultat = self.Sib.requeteSib(sql)
        #Vérifier la présence du paramètre
        if (len(resultat) == 0):
            raise Exception("Numéro de non-conformité invalide : %s" %no_nc)
        #Vérifier si la non-conformité est fermée
        if resultat[0][0] <> None:
            raise Exception("La non-conformité est fermée : date_fermeture=%s" %resultat[0][0])
        #Vérifier si la non-conformité a déjà été traitée
        if resultat[0][1] <> None:
            raise Exception("La non-conformité a déjà été traitée : date_traitement=%s" %resultat[0][1])
        #Vérifier si la non-conformité a déjà été traitée
        if resultat[0][2] <> "DM":
            raise Exception("Le type de non-conformité n'est pas 'DM' : TY_NC=%s" %resultat[0][2])
        #Vérifier si la non-conformité a déjà été traitée
        if "ME" not in resultat[0][3]:
            raise Exception("Le type de traitement de non-conformité n'est pas 'ME%' : TY_TRAIT_NC=%s" %resultat[0][3])
        #Conserver l'information de la non-conformité
        resp_descr = resultat[0][4]
        resp_corr = resultat[0][5]
        resp_suivi = resultat[0][6]
        #Afficher les valeurs
        arcpy.AddMessage(str(resultat))
        
        #Extraction des métadonnées d'identifiants de la non-conformité
        arcpy.AddMessage("- Extraction des identifiants non-conformes : " + str(no_nc))
        sql = "SELECT TY_PRODUIT,IDENTIFIANT,ED_DEBUT,VER_DEBUT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' ORDER BY IDENTIFIANT"
        arcpy.AddMessage(sql)
        #Exécuter la requête
        resultat = self.Sib.requeteSib(sql)
        #Vérifier la présence du paramètre
        if (len(resultat) == 0):
            #Retourner une erreur
            raise Exception("Aucun identifiant n'est associé à la non-conformité")
        
        #Traiter toutes les items
        for item in resultat:
            #Afficher les valeurs
            arcpy.AddMessage(str(item))
            #Définir les variables
            ty_produit = item[0]    #ty_produit
            identifiant = item[1]   #identifiant
            ed_debut = item[2]      #ed_debut
            ver_debut = item[3]     #ver_debut
            ed_fin = item[4]        #ed_fin
            ver_fin = item[5]       #ver_fin
            
            #Vérifier si l'intervalle de fin n'est pas traitée
            if ed_fin == 99999:
                #Créer la requête SQL (pour extraire l'édition et la version du jeu courant ainsi que la version des métadonnées)
                sql = "SELECT ed,ver,ver_meta FROM F235_PR WHERE ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "' and jeu_cour=1"
                arcpy.AddMessage(sql)
                #Exécuter la requête SQL
                resultat2 = self.Sib.requeteSib(sql)
                #Vérifier la présence du paramètre
                if (len(resultat) == 0):
                    raise Exception("Aucun jeu courant n'est présent dans la table F235_pr")
                #Extraire la valeur de l'édition et version courante
                ed_cour = resultat2[0][0]
                ver_cour = resultat2[0][1]
                ver_meta = resultat2[0][2]
                #Vérifier si l'édition.version de début est plus élevé que l'édition.version courante
                if float(str(ed_debut) + "." + str(ver_debut)) > float(str(ed_cour) + "." + str(ver_cour)):
                    #Retourner une erreur
                    raise Exception("Ed.Ver_Début:" + str(float(str(ed_debut) + "." + str(ver_debut))) + " > Ed.Ver_Cour:" + str(float(str(ed_cour) + "." + str(ver_cour))))
                #Afficher les valeurs
                arcpy.AddMessage(str(resultat2))
                
                #Créer la commande SQL pour modifier l'édition et version de fin
                sql = "UPDATE F705_PR SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,ed_fin=" + str(ed_cour) + ",ver_fin=" + str(ver_cour) + " WHERE no_nc='" + no_nc + "' AND ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "'"
                arcpy.AddMessage(sql)
                #Exécuter la commande
                self.Sib.execute(sql)
                
                #-----------------------------------
                #Modifier la date des métadonnées
                arcpy.AddMessage("  -Modifier la date des métadonnées ...")
                sql = "UPDATE F235_MR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, DT_METADATA=TO_CHAR(SYSDATE, 'YYYYMMDD') WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed_cour) + " AND VER=" + str(ver_cour)
                arcpy.AddMessage(sql)
                #Exécuter la commande
                self.Sib.execute(sql)
                
                #Incrémenter la version des métadonnées
                ver_meta = ver_meta + 1
                #Créer la commande SQL pour modifier la version des métadonnées
                sql = "UPDATE F235_PR SET ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,ver_meta=" + str(ver_meta) + " WHERE ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "' and jeu_cour=1"
                arcpy.AddMessage(sql)
                #Exécuter la commande
                self.Sib.execute(sql)
            
            #si l'intervalle de fin est déjà traitée
            else:
                #Afficher un avertissement
                arcpy.AddWarning("L'intervalle de fin est déja traitée")
        
        #Mettre à jour la date de traitement
        arcpy.AddMessage("- Mise à jour de la date de traitement")
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
        #Exécuter la requête SQL
        resultat = self.Sib.requeteSib(sql)
        #Envoyer un courriel aux responsables
        for courriel in resultat:
            #Envoyer un courriel
            destinataire = str(courriel[0])
            sujet = unicode("Fermeture de la correction INSITU de la non-conformité #" + no_nc, "utf-8")
            contenu = unicode("Bonjour,\n\nTous les jeux de données associés à la non conformité #" + no_nc + " sont maitenant corrigés.\n\n" + sUsagerSib + "\n" + sUsagerBd, "utf-8")
            arcpy.AddMessage("EnvoyerCourriel('" + destinataire + "','" + sujet + "')")
            EnvoyerCourriel.EnvoyerCourriel(destinataire,contenu, sujet)
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        self.Sib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "SIB_PRO"
        no_nc = ""
        no_tache = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
            
        if len(sys.argv) > 3:
            no_tache = sys.argv[3].upper()
        
        #Définir l'objet pour fermer une non-conformité de métadonnées.
        oFermerNonConformiteMetadonnees = FermerNonConformiteMetadonnees()
        
        #Valider les paramètres obligatoires
        oFermerNonConformiteMetadonnees.validerParamObligatoire(env,no_nc,no_tache)
        
        #Exécuter le traitement pour fermer une non-conformité de métadonnées.
        oFermerNonConformiteMetadonnees.executer(env, no_nc, no_tache)
    
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