#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : ValiderInfoMetaNonConforme.py
# Auteur    : Michel Pothier
# Date      : 21 octobre 2014

"""
Outil qui permet de valider les valeurs minimum et maximum de date de validit� et de pr�cision altim�trique et planim�trique
dans les m�tadonn�es par rapport aux informations sur les donn�es pour tous les identifiants d'une non-conformit�.

Les dates minimum et maximum sont pr�sentes dans la table F235_PR sous l'attribut DT_CONTENT_BEG et DT_CONTENT_END.

Les pr�cisions altim�trique minimum (EXPLANATION = '{$PS$VERT_EXPL_BDG_MIN}') et maximum (EXPLANATION = '{$PS$VERT_EXPL_BDG_MAX}')
sont pr�sentes dans la table F235_AV sous l'atrribut VALUE.
   
Les pr�cisions planim�trique minimum (EXPLANATION = '{$PS$HORIZ_EXPL_BDG_MIN}') et maximum (EXPLANATION = '{$PS$HORIZ_EXPL_BDG_MAX}')
sont pr�sentes dans la table F235_AH sous l'atrribut VALUE.

ATTENTION : Les corrections ne sont pas effectu�es mais les commandes pour le faire sont affich�es au fur et � mesure et � la fin du traitement.

Param�tres d'entr�es:
----------------------
env         : Type d'environnement.
no_nc       : Num�ro de la non-conformit� � fermer.
no_tache    : Num�ro de ticket Alloy.

Param�tres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du r�sultat de l'ex�cution du programme.
              (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ValiderInfoMetaNonConforme(object):
#*******************************************************************************************
    """
    Valider les valeurs minimum et maximum de date de validit� et de pr�cision altim�trique
    et planim�trique dans les m�tadonn�es.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les valeurs minimum et maximum de date de validit�
        et de pr�cision altim�trique et planim�trique dans les m�tadonn�es.
        
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
    def executer(self, env, no_nc, no_tache):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider les valeurs minimum et maximum de date de validit�
        et de pr�cision altim�trique et planim�trique dans les m�tadonn�es.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        no_nc       : Num�ro de la non-conformit� � fermer.
        no_tache    : Num�ro de t�che Alloy.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib            : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        listeItem       : Liste des items (jeu de donn�es) contenus dans la non-conformit�.
        listeCorrection : Liste des corrections � effectuer dans SIB.
        corrections     : Liste des corrections pour un item.
        correction      : Correction � effectuer.
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
        
        #Cr�er la requ�te SQL ('{$PS$HORIZ_EXPL_BDG_MIN}' et '{$PS$HORIZ_EXPL_BDG_MAX}')
        arcpy.AddMessage("- Extraction des m�tadonn�es d'identifiants de la non-conformit� : " + str(no_nc))
        sSql = "SELECT TY_PRODUIT,IDENTIFIANT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC=" + no_nc + " ORDER BY IDENTIFIANT"
        arcpy.AddMessage(sSql)
        #Ex�cuter la requ�te SQL pour extraire les m�tadonn�es de pr�cision planim�trique associ�es aux identifiant de la non-conformit�
        resultat = self.Sib.requeteSib(sSql)
        
        #Initialisation du traitement
        listeItem = []
        listeCorrection = []
        #Traiter toutes les lignes
        for ligne in resultat:
            #D�finir les variables
            ty_produit = ligne[0]   #ty_produit
            identifiant = ligne[1]  #identifiant
            ed_fin = ligne[2]       #ed_fin
            ver_fin = ligne[3]      #ver_fin
            
            #Remplir les valeurs de l'item � traiter
            Item = []   #initialisation
            Item.append(ty_produit)
            Item.append(identifiant)
            Item.append(ed_fin)
            Item.append(ver_fin)
            
            #Ajouter l'item trait� dans la liste
            listeItem.append(Item)
            
            #Afficher l'item trait�
            arcpy.AddMessage(" ")
            arcpy.AddMessage(str(len(listeItem)) + ':' + str(Item))
            
            #Valider l'�dition et version courante du jeu de donn�es 
            ed_cour,ver_cour = self.validerEdVerFin(ty_produit, identifiant, ed_fin, ver_fin)
            
            #Extraire l'information sur les donn�es pour l'identifiant trait�
            info = self.extraireInfoDonnees(identifiant)
        
            #Extraire l'information sur les m�tadonn�es pour le jeu de donn�es courant
            meta = self.extraireInfoMetadonnees(ty_produit, identifiant, ed_cour, ver_cour)
            
            #Valider l'information des donn�es par rapport aux m�tadonn�es 
            corrections = self.validerInfoMeta(no_tache, ty_produit, identifiant, ed_cour, ver_cour, info, meta)
            
            #Ajouter les corrections � la liste des corrections
            for correction in corrections:
                #Ajouter une correction � la liste des corrections
                arcpy.AddMessage(correction)
                listeCorrection.append(correction)
            
        #Afficher le nombre d'identifiants trait�s
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Nombre d'identifiants : " + str(len(listeItem)))

        #Afficher le nombre de correction � effectuer
        arcpy.AddMessage("Nombre de correction(s) : " + str(len(listeCorrection)))
        #Afficher toutes les corrections � effectuer
        arcpy.AddMessage(" ")
        for correction in listeCorrection:
            #Afficher une correction � effectuer
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
        Valider si l'�dition et la version de fin de la non conformit� correspond � celui du jeu courant.
        
        Param�tres:
        -----------
        ty_produit  : Type de produit trait�.
        identifiant : Identifiant de d�coupage trait�.
        ed          : �dition de fin de la non-conformit�.
        ver         : Version de fin de la non-conformit�.
        
        Variables:
        ----------
        resultat    : R�sultat de la requ�te SIB.

        Valeurs de retour:
        ------------------
        ed_cour     : �dition courante du jeu de donn�es.
        ver_cour    : Version courante du jeu de donn�es.
        
        """

        #Cr�er la requ�te SQL (pour extraire l'�dition et version du jeu courant)
        sSql = "select ed,ver from f235_pr where ty_produit='" + ty_produit + "' and identifiant='" + identifiant + "' and jeu_cour=1"
        arcpy.AddMessage(" " + sSql)
        
        #Ex�cuter la requ�te SQL pour extraire les m�tadonn�es de pr�cision planim�trique associ�es � l'identifiant de la non-conformit� trait�
        resultat = self.Sib.requeteSib(sSql)
        
        #Extraire la valeur de l'�dition et version courante
        ed_cour = resultat[0][0]
        ver_cour = resultat[0][1]
        
        #Valider l'�dition courante
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
        Extraire l'information sur le jeu de donn�es courant de la BDG pour un identifiant.
        
        Param�tres:
        -----------
        identifiant : Identifiant de d�coupage trait�.
        
        Variables:
        ----------
        resultat    : R�sultat de la requ�te SIB.
        val_min     : Date de validit� minimum du jeu de donn�es courant.
        val_max     : Date de validit� maximum du jeu de donn�es courant.
        alti_min    : Pr�cision altim�trique minimum du jeu de donn�es courant.
        alti_max    : Pr�cision altim�trique maximum du jeu de donn�es courant.
        plani_min   : Pr�cision planim�trique minimum du jeu de donn�es courant.
        plani_max   : Pr�cision planim�trique maximum du jeu de donn�es courant.

        Valeurs de retour:
        ------------------
        info : Information sur les donn�es
        """
        
        #Initialisation de la liste de retour
        info = []
        
        #Cr�er la requ�te SQL pour extraire les statistiques des donn�es de la BDG pour l'identifiant trait�
        sSql = "select val_min,val_max,alti_min,alti_max,plani_min,plani_max from vinfo_bdg_min_max@BDG_DBA where dataset_name='" + identifiant + "'"
        arcpy.AddMessage(" " + sSql)
        
        #Ex�cuter la requ�te SQL pour extraire les m�tadonn�es de pr�cision planim�trique associ�es � l'identifiant de la non-conformit� trait�
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        
        #Extraire la valeur minimum et maximum de date de validit�
        val_min = resultat[0][0]
        val_max = resultat[0][1]
        info.append(val_min)
        info.append(val_max)
        
        #Extraire la valeur minimum et maximum de la pr�cision altim�trique
        alti_min = resultat[0][2]
        alti_max = resultat[0][3]
        info.append(alti_min)
        info.append(alti_max)
        
        #Extraire la valeur minimum et maximum de la pr�cision planim�trique
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
        Extraire l'information sur les m�tadonn�es du jeu courant dans SIB.
        
        Param�tres:
        -----------
        ty_produit  : Type de produit trait�.
        identifiant : Identifiant de d�coupage trait�.
        ed          : �dition du jeu courant.
        ver         : Version du jeu courant.
        
        Variables:
        ----------
        resultat    : R�sultat de la requ�te SIB.
        val_min     : Date de validit� minimum du jeu de donn�es courant.
        val_max     : Date de validit� maximum du jeu de donn�es courant.
        alti_min    : Pr�cision altim�trique minimum du jeu de donn�es courant.
        alti_max    : Pr�cision altim�trique maximum du jeu de donn�es courant.
        plani_min   : Pr�cision planim�trique minimum du jeu de donn�es courant.
        plani_max   : Pr�cision planim�trique maximum du jeu de donn�es courant.

        Valeurs de retour:
        ------------------
        meta        : M�tadonn�es du jeu de donn�es courant dans SIB.
        """
        
        #Initialisation de la liste de retour
        meta = []
        
        #Cr�er la requ�te SQL pour extraire la pr�cision planim�trique minimum et maximum pour l'identifiant trait�
        sSql = "SELECT DT_CONTENT_BEG,DT_CONTENT_END FROM F235_PR WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed) + " AND VER="+ str(ver)
        arcpy.AddMessage(" " + sSql)
        #Ex�cuter la requ�te SQL pour extraire les m�tadonn�es de pr�cision planim�trique associ�es � l'identifiant de la non-conformit� trait�
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        #Extraire la valeur minimum et maximum de date de validit�
        val_min = resultat[0][0]
        val_max = resultat[0][1]
        meta.append(val_min)
        meta.append(val_max)
        
        #Cr�er la requ�te SQL pour extraire la pr�cision planim�trique minimum et maximum pour l'identifiant trait�
        sSql = "SELECT VALUE,EXPLANATION FROM F235_AV WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed) + " AND VER=" + str(ver) + " ORDER BY VALUE"
        arcpy.AddMessage(" " + sSql)
        #Ex�cuter la requ�te SQL pour extraire les m�tadonn�es de pr�cision planim�trique associ�es � l'identifiant de la non-conformit� trait�
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        #Extraire la valeur minimum et maximum de la pr�cision altim�trique
        if resultat:
            alti_min = int(resultat[0][0])
            alti_max = int(resultat[1][0])
        else:
            alti_min = None
            alti_max = None
        meta.append(alti_min)
        meta.append(alti_max)
        
        #Cr�er la requ�te SQL pour extraire la pr�cision planim�trique minimum et maximum pour l'identifiant trait�
        sSql = "SELECT VALUE,EXPLANATION FROM F235_AH WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed) + " AND VER=" + str(ver) + " ORDER BY VALUE"
        arcpy.AddMessage(" " + sSql)
        #Ex�cuter la requ�te SQL pour extraire les m�tadonn�es de pr�cision planim�trique associ�es � l'identifiant de la non-conformit� trait�
        resultat = self.Sib.requeteSib(sSql)
        arcpy.AddMessage(" " + str(resultat))
        #Extraire la valeur minimum et maximum de la pr�cision planim�trique
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
        Valider si l'information sur les donn�es correspond aux m�tadonn�es du jeu courant.
        
        Param�tres:
        -----------
        no_tache    : Num�ro de t�che Alloy.
        ty_produit  : Type de produit trait�.
        identifiant : Identifiant de d�coupage trait�.
        ed          : �dition du jeu courant.
        ver         : Version du jeu courant.
        info        : Valeur minimum et maximum sur les donn�es de date de validit� et de pr�cision altim�trique et planim�trique.
        meta        : Valeur minimum et maximum sur les m�tadonn�es de date de validit� et de pr�cision altim�trique et planim�trique.
        
        Variables:
        ----------
        resultat    : R�sultat de la requ�te SIB.

        Valeurs de retour:
        ------------------
        correction  : Commande correcpondant aux corrections � effectuer.
        
        """
        
        #Initialisation des corrections � effectuer
        correction = []

        #Afficher l'information sur les donn�es
        arcpy.AddMessage("  info:" + str(info))
        
        #Afficher l'information sur les donn�es
        arcpy.AddMessage("  meta:" + str(meta))
        
        #----------------
        #date de validit�
        #----------------
        #Valider la valeur minimum
        if info[0] <> meta[0]:
            arcpy.AddWarning("  Val_min, Info:" + str(info[0]) + " <> Meta:" + str(meta[0]))
            #DT_CONTENT_BEG
            correction.append("UPDATE F235_PR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',DT_CONTENT_BEG=" + str(info[0]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + ";")
        #Valider la valeur maximum de la date de validit�
        if info[1] <> meta[1]:
            arcpy.AddWarning("  Val_max, Info:" + str(info[1]) + ' <> Meta:' + str(meta[1]))
            #DT_CONTENT_END
            correction.append("UPDATE F235_PR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DT_M=SYSDATE,ETAMPE='" + no_tache + "',DT_CONTENT_END=" + str(info[1]) + " WHERE TY_PRODUIT='" + ty_produit + "' and IDENTIFIANT='" + identifiant + "' and ED=" + str(ed) + " and VER=" + str(ver) + ";")

        #----------------------
        #Pr�cision altim�trique
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
        #Pr�cision planim�trique
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "SIB_PRO"
        no_nc = ""
        
        # Lecture des param�tres
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper()
            
        if len(sys.argv) > 3:
            no_tache = sys.argv[3].upper()
        
        # D�finir l'objet de validation des m�tadonn�es.
        ValiderInfoMetaNonConforme = ValiderInfoMetaNonConforme()
        
        # Ex�cuter le traitement de validation des m�tadonn�es.
        ValiderInfoMetaNonConforme.executer(env, no_nc, no_tache)
    
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