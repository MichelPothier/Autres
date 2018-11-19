#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderInfoMetaNonConforme.py
# Auteur    : Michel Pothier
# Date      : 21 octobre 2014

"""
Outil qui permet de valider les valeurs minimum et maximum de date de validité et de précision altimétrique et planimétrique
dans les métadonnées par rapport aux informations sur les données pour tous les identifiants d'une non-conformité.

Les dates minimum et maximum sont présentes dans la table F235_PR sous l'attribut DT_CONTENT_BEG et DT_CONTENT_END.

Les précisions altimétrique minimum (EXPLANATION = '{$PS$VERT_EXPL_BDG_MIN}') et maximum (EXPLANATION = '{$PS$VERT_EXPL_BDG_MAX}')
sont présentes dans la table F235_AV sous l'atrribut VALUE.
   
Les précisions planimétrique minimum (EXPLANATION = '{$PS$HORIZ_EXPL_BDG_MIN}') et maximum (EXPLANATION = '{$PS$HORIZ_EXPL_BDG_MAX}')
sont présentes dans la table F235_AH sous l'atrribut VALUE.

ATTENTION : Les corrections ne sont pas effectuées mais les commandes pour le faire sont affichées au fur et à mesure et à la fin du traitement.

Paramètres d'entrées:
----------------------
env         : Type d'environnement.
no_nc       : Numéro de la non-conformité à fermer.
no_tache    : Numéro de ticket Alloy.

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    ValiderInfoMetaNonConforme.py env no_nc no_tache

Exemple:
    ValiderInfoMetaNonConforme.py SIB_PRO 02997 T011107

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderInfoMetaNonConforme.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ValiderInfoMetaNonConforme(object):
#*******************************************************************************************
    """
    Valider les valeurs minimum et maximum de date de validité et de précision altimétrique
    et planimétrique dans les métadonnées.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les valeurs minimum et maximum de date de validité
        et de précision altimétrique et planimétrique dans les métadonnées.
        
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
    def executer(self, env, no_nc, no_tache):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour valider les valeurs minimum et maximum de date de validité
        et de précision altimétrique et planimétrique dans les métadonnées.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        no_nc       : Numéro de la non-conformité à fermer.
        no_tache    : Numéro de tâche Alloy.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib            : Objet utilitaire pour traiter des services SIB.
        resultat        : Résultat de la requête SIB.
        listeItem       : Liste des items (jeu de données) contenus dans la non-conformité.
        listeCorrection : Liste des corrections à effectuer dans SIB.
        corrections     : Liste des corrections pour un item.
        correction      : Correction à effectuer.
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
        
        #Créer la requête SQL ('{$PS$HORIZ_EXPL_BDG_MIN}' et '{$PS$HORIZ_EXPL_BDG_MAX}')
        arcpy.AddMessage("- Extraction des métadonnées d'identifiants de la non-conformité : " + str(no_nc))
        sSql = "SELECT TY_PRODUIT,IDENTIFIANT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC=" + no_nc + " ORDER BY IDENTIFIANT"
        arcpy.AddMessage(sSql)
        #Exécuter la requête SQL pour extraire les métadonnées de précision planimétrique associées aux identifiant de la non-conformité
        resultat = self.Sib.requeteSib(sSql)
        
        #Initialisation du traitement
        listeItem = []
        listeCorrection = []
        #Traiter toutes les lignes
        for ligne in resultat:
            #Définir les variables
            ty_produit = ligne[0]   #ty_produit
            identifiant = ligne[1]  #identifiant
            ed_fin = ligne[2]       #ed_fin
            ver_fin = ligne[3]      #ver_fin
            
            #Remplir les valeurs de l'item à traiter
            Item = []   #initialisation
            Item.append(ty_produit)
            Item.append(identifiant)
            Item.append(ed_fin)
            Item.append(ver_fin)
            
            #Ajouter l'item traité dans la liste
            listeItem.append(Item)
            
            #Afficher l'item traité
            arcpy.AddMessage(" ")
            arcpy.AddMessage(str(len(listeItem)) + ':' + str(Item))
            
            #Valider l'édition et version courante du jeu de données 
            ed_cour,ver_cour = self.validerEdVerFin(ty_produit, identifiant, ed_fin, ver_fin)
            
            #Extraire l'information sur les données pour l'identifiant traité
            info = self.extraireInfoDonnees(identifiant)
        
            #Extraire l'information sur les métadonnées pour le jeu de données courant
            meta = self.extraireInfoMetadonnees(ty_produit, identifiant, ed_cour, ver_cour)
            
            #Valider l'information des données par rapport aux métadonnées 
            corrections = self.validerInfoMeta(no_tache, ty_produit, identifiant, ed_cour, ver_cour, info, meta)
            
            #Ajouter les corrections à la liste des corrections
            for correction in corrections:
                #Ajouter une correction à la liste des corrections
                arcpy.AddMessage(correction)
                listeCorrection.append(correction)
            
        #Afficher le nombre d'identifiants traités
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Nombre d'identifiants : " + str(len(listeItem)))

        #Afficher le nombre de correction à effectuer
        arcpy.AddMessage("Nombre de correction(s) : " + str(len(listeCorrection)))
        #Afficher toutes les corrections à effectuer
        arcpy.AddMessage(" ")
        for correction in listeCorrection:
            #Afficher une correction à effectuer
            arcpy.AddMessage(correction)
      
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        self.Sib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

    #-------------------------------------------------------------------------------------
    def validerEdVerFin(self, ty_produit, identifiant, ed, ver):
    #-------------------------------------------------------------------------------------
        """
        Valider si l'édition et la version de fin de la non conformité correspond à celui du jeu courant.
        
        Paramètres:
        -----------
        ty_produit  : Type de produit traité.
        identifiant : Identifiant de découpage traité.
        ed          : Édition de fin de la non-conformité.
        ver         : Version de fin de la non-conformité.
        
        Variables:
        ----------
        resultat    : Résultat de la requête SIB.

        Valeurs de retour:
        ------------------
        ed_cour     : Édition courante du jeu de données.
        ver_cour    : Version courante du jeu de données.
        
        """

        #Créer la requête SQL (pour extraire l'édition et version du jeu courant)
        sSql = "select ed,ver from f235_pr where ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "' and jeu_cour=1"
        arcpy.AddMessage(" " + sSql)
        
        #Exécuter la requête SQL pour extraire les métadonnées de précision planimétrique associées à l'identifiant de la non-conformité traité
        resultat = self.Sib.requeteSib(sSql)
        
        #Extraire la valeur de l'édition et version courante
        ed_cour = resultat[0][0]
        ver_cour = resultat[0][1]
        
        #Valider l'édition courante
        if ed_cour <> ed:
            #Afficher un message d'avertissement
            arcpy.AddWarning("  ed_cour:" + str(ed_cour) + " <> ed_fin:" + str(ed))
        else:
            #Afficher un message OK
            arcpy.AddMessage("  ed_cour:" + str(ed_cour) + " = ed_fin:" + str(ed))
        
        #Valider la version courante
        if ver_cour <> ver:
            #Afficher un message d'avertissement
            arcpy.AddWarning("  ver_cour:" + str(ver_cour) + " <> ver_fin:" + str(ver))
        else:
            #Afficher un message OK
            arcpy.AddMessage("  ver_cour:" + str(ver_cour) + " = ver_fin:" + str(ver))
        
        # Sortir du traitement 
        return ed_cour, ver_cour

    #-------------------------------------------------------------------------------------
    def extraireInfoDonnees(self, identifiant):
    #-------------------------------------------------------------------------------------
        """
        Extraire l'information sur le jeu de données courant de la BDG pour un identifiant.
        
        Paramètres:
        -----------
        identifiant : Identifiant de découpage traité.
        
        Variables:
        ----------
        resultat    : Résultat de la requête SIB.
        val_min     : Date de validité minimum du jeu de données courant.
        val_max     : Date de validité maximum du jeu de données courant.
        alti_min    : Précision altimétrique minimum du jeu de données courant.
        alti_max    : Précision altimétrique maximum du jeu de données courant.
        plani_min   : Précision planimétrique minimum du jeu de données courant.
        plani_max   : Précision planimétrique maximum du jeu de données courant.

        Valeurs de retour:
        ------------------
        info : Information sur les données
        """
        
        #Initialisation de la liste de retour
        info = []
        
        #Créer la requête SQL pour extraire les statistiques des données de la BDG pour l'identifiant traité
        sSql = "select val_min,val_max,alti_min,alti_max,plani_min,plani_max from vinfo_bdg_min_max@BDG_DBA where dataset_name='" + identifiant + "'"
        arcpy.AddMessage(" " + sSql)
        
        #Exécuter la requête SQL pour extraire les métadonnées de précision planimétrique associées à l'identifiant de la non-conformité traité
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        
        #Extraire la valeur minimum et maximum de date de validité
        val_min = resultat[0][0]
        val_max = resultat[0][1]
        info.append(val_min)
        info.append(val_max)
        
        #Extraire la valeur minimum et maximum de la précision altimétrique
        alti_min = resultat[0][2]
        alti_max = resultat[0][3]
        info.append(alti_min)
        info.append(alti_max)
        
        #Extraire la valeur minimum et maximum de la précision planimétrique
        plani_min = resultat[0][4]
        plani_max = resultat[0][5]
        info.append(plani_min)
        info.append(plani_max)
        
        # Sortir du traitement 
        return info

    #-------------------------------------------------------------------------------------
    def extraireInfoMetadonnees(self, ty_produit, identifiant, ed, ver):
    #-------------------------------------------------------------------------------------
        """
        Extraire l'information sur les métadonnées du jeu courant dans SIB.
        
        Paramètres:
        -----------
        ty_produit  : Type de produit traité.
        identifiant : Identifiant de découpage traité.
        ed          : Édition du jeu courant.
        ver         : Version du jeu courant.
        
        Variables:
        ----------
        resultat    : Résultat de la requête SIB.
        val_min     : Date de validité minimum du jeu de données courant.
        val_max     : Date de validité maximum du jeu de données courant.
        alti_min    : Précision altimétrique minimum du jeu de données courant.
        alti_max    : Précision altimétrique maximum du jeu de données courant.
        plani_min   : Précision planimétrique minimum du jeu de données courant.
        plani_max   : Précision planimétrique maximum du jeu de données courant.

        Valeurs de retour:
        ------------------
        meta        : Métadonnées du jeu de données courant dans SIB.
        """
        
        #Initialisation de la liste de retour
        meta = []
        
        #Créer la requête SQL pour extraire la précision planimétrique minimum et maximum pour l'identifiant traité
        sSql = "SELECT DT_CONTENT_BEG,DT_CONTENT_END FROM F235_PR WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed) + " AND VER="+ str(ver)
        arcpy.AddMessage(" " + sSql)
        #Exécuter la requête SQL pour extraire les métadonnées de précision planimétrique associées à l'identifiant de la non-conformité traité
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        #Extraire la valeur minimum et maximum de date de validité
        val_min = resultat[0][0]
        val_max = resultat[0][1]
        meta.append(val_min)
        meta.append(val_max)
        
        #Créer la requête SQL pour extraire la précision planimétrique minimum et maximum pour l'identifiant traité
        sSql = "SELECT VALUE,EXPLANATION FROM F235_AV WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed) + " AND VER=" + str(ver) + " ORDER BY VALUE"
        arcpy.AddMessage(" " + sSql)
        #Exécuter la requête SQL pour extraire les métadonnées de précision planimétrique associées à l'identifiant de la non-conformité traité
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        #Extraire la valeur minimum et maximum de la précision altimétrique
        if resultat:
            alti_min = int(resultat[0][0])
            alti_max = int(resultat[1][0])
        else:
            alti_min = None
            alti_max = None
        meta.append(alti_min)
        meta.append(alti_max)
        
        #Créer la requête SQL pour extraire la précision planimétrique minimum et maximum pour l'identifiant traité
        sSql = "SELECT VALUE,EXPLANATION FROM F235_AH WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed) + " AND VER=" + str(ver) + " ORDER BY VALUE"
        arcpy.AddMessage(" " + sSql)
        #Exécuter la requête SQL pour extraire les métadonnées de précision planimétrique associées à l'identifiant de la non-conformité traité
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        #Extraire la valeur minimum et maximum de la précision planimétrique
        plani_min = int(resultat[0][0])
        plani_max = int(resultat[1][0])
        meta.append(plani_min)
        meta.append(plani_max)
        
        # Sortir du traitement 
        return meta

    #-------------------------------------------------------------------------------------
    def validerInfoMeta(self, no_tache, ty_produit, identifiant, ed, ver, info, meta):
    #-------------------------------------------------------------------------------------
        """
        Valider si l'information sur les données correspond aux métadonnées du jeu courant.
        
        Paramètres:
        -----------
        no_tache    : Numéro de tâche Alloy.
        ty_produit  : Type de produit traité.
        identifiant : Identifiant de découpage traité.
        ed          : Édition du jeu courant.
        ver         : Version du jeu courant.
        info        : Valeur minimum et maximum sur les données de date de validité et de précision altimétrique et planimétrique.
        meta        : Valeur minimum et maximum sur les métadonnées de date de validité et de précision altimétrique et planimétrique.
        
        Variables:
        ----------
        resultat    : Résultat de la requête SIB.

        Valeurs de retour:
        ------------------
        correction  : Commande correcpondant aux corrections à effectuer.
        
        """
        
        #Initialisation des corrections à effectuer
        correction = []

        #Afficher l'information sur les données
        arcpy.AddMessage("  info:" + str(info))
        
        #Afficher l'information sur les données
        arcpy.AddMessage("  meta:" + str(meta))
        
        #----------------
        #date de validité
        #----------------
        #Valider la valeur minimum
        if info[0] <> meta[0]:
            arcpy.AddWarning("  Val_min, Info:" + str(info[0]) + " <> Meta:" + str(meta[0]))
            #DT_CONTENT_BEG
            correction.append("UPDATE F235_PR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',DT_CONTENT_BEG=" + str(info[0]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + ";")
        #Valider la valeur maximum de la date de validité
        if info[1] <> meta[1]:
            arcpy.AddWarning("  Val_max, Info:" + str(info[1]) + ' <> Meta:' + str(meta[1]))
            #DT_CONTENT_END
            correction.append("UPDATE F235_PR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',DT_CONTENT_END=" + str(info[1]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + ";")

        #----------------------
        #Précision altimétrique
        #----------------------
        #Valider la valeur minimum
        if info[2] <> meta[2]:
            arcpy.AddWarning("  Alti_min, Info:" + str(info[2]) + " <> Meta:" + str(meta[2]))
            #'{$PS$VERT_EXPL_BDG_MIN}'
            correction.append("UPDATE F235_AV SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',VALUE=" + str(info[2]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + " and EXPLANATION='{$PS$VERT_EXPL_BDG_MIN}';")
        #Valider la valeur maximum
        if info[3] <> meta[3]:
            arcpy.AddWarning("  Alti_max, Info:" + str(info[3]) + ' <> Meta:' + str(meta[3]))
            #'{$PS$VERT_EXPL_BDG_MAX}'
            correction.append("UPDATE F235_AV SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',VALUE=" + str(info[3]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + " and EXPLANATION='{$PS$VERT_EXPL_BDG_MAX}';")

        #-----------------------
        #Précision planimétrique
        #-----------------------
        #Valider la valeur minimum
        if info[4] <> meta[4]:
            arcpy.AddWarning("  Plani_min, Info:" + str(info[4]) + " <> Meta:" + str(meta[4]))
            #'{$PS$HORIZ_EXPL_BDG_MIN}'
            correction.append("UPDATE F235_AH SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',VALUE=" + str(info[4]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + " and EXPLANATION='{$PS$HORIZ_EXPL_BDG_MIN}';")
        #Valider la valeur maximum
        if info[5] <> meta[5]:
            arcpy.AddWarning("  Plani_max, Info:" + str(info[5]) + ' <> Meta:' + str(meta[5]))
            #'{$PS$HORIZ_EXPL_BDG_MAX}'
            correction.append("UPDATE F235_AH SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',VALUE=" + str(info[5]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + " and EXPLANATION='{$PS$HORIZ_EXPL_BDG_MAX}';")
        
        # Sortir du traitement 
        return correction

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par défaut
        env = "SIB_PRO"
        no_nc = ""
        
        # Lecture des paramètres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper()
            
        if len(sys.argv) > 3:
            no_tache = sys.argv[3].upper()
        
        # Définir l'objet de validation des métadonnées.
        ValiderInfoMetaNonConforme = ValiderInfoMetaNonConforme()
        
        # Exécuter le traitement de validation des métadonnées.
        ValiderInfoMetaNonConforme.executer(env, no_nc, no_tache)
    
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