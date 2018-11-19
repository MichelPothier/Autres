#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierIdentifiantBDG.py
# Auteur    : Michel Pothier
# Date      : 22 juin 2016

"""
    Application qui permet de modifier l'information d'un identifiant BDG de découpage SNRC 50000 pour la production dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    snrc            OB      Identifiant SNRC à modifier.
                            défaut = 
    nom             OB      Nom en français de l'identifiant SNRC.
                            défaut = "Totalement submerge"
    nom_an          OB      Nom en anglais de l'identifiant SNRC.
                            défaut = "Totally submerged"
    no_fu_1         OB      Premier numéro de fuseau UTM de l'identifiant SNRC.
                            défaut = 
    no_fu_2         OB      Deuxième numéro de fuseau UTM de l'identifiant SNRC.
                            défaut = -1
    pct_terre       OB      Pourcentage de terre de l'identifiant SNRC.
                            défaut = 0
    cd_prov         OB      Code de province de l'identifiant SNRC.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierIdentifiantBDG.py env snrc nom nom_an no_fu_1 no_fu_2 pct_terre cd_prov

    Exemple:
        ModifierIdentifiantBDG.py SIB_PRO 021M07 MAILLARD MAILLARD 19 -1 100 QC

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierIdentifiantBDG.py 2062 2016-06-22 18:07:49Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib, Snrc

#*******************************************************************************************
class ModifierIdentifiantBDG(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'un identifiant BDG de découpage SNRC 50000 pour la production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour modifier l'information d'un identifiant BDG de découpage SNRC 50000 pour la production dans SIB.
        
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
    def validerParamObligatoire(self, env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC à modifier.
        nom             : Nom den français de l'identifiant SNRC.
        nom_an          : Nom en anglais de l'identifiant SNRC.
        no_fu_1         : Premier numéro de fuseau UTM de l'identifiant SNRC.
        no_fu_2         : Deuxième numéro de fuseau UTM de l'identifiant SNRC.
        pct_terre       : Pourcentage de terre de l'identifiant SNRC.
        cd_prov         : Code de province de l'identifiant SNRC.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')

        if (len(snrc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'snrc')

        if (len(nom) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom_an')

        if len(no_fu_1) == 0:
            raise Exception("Paramètre obligatoire manquant: %s" %'no_fu_1')

        if len(no_fu_2) == 0:
            raise Exception("Paramètre obligatoire manquant: %s" %'no_fu_2')

        if len(pct_terre) == 0:
            raise Exception("Paramètre obligatoire manquant: %s" %'pct_terre')

        if (len(cd_prov) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'cd_prov')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'information d'un identifiant BDG de découpage SNRC 50000 pour la production dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC à modifier.
        nom             : Nom den français de l'identifiant SNRC.
        nom_an          : Nom en anglais de l'identifiant SNRC.
        no_fu_1         : Premier numéro de fuseau UTM de l'identifiant SNRC.
        no_fu_2         : Deuxième numéro de fuseau UTM de l'identifiant SNRC.
        pct_terre       : Pourcentage de terre de l'identifiant SNRC.
        cd_prov         : Code de province de l'identifiant SNRC.
        
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
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'PLAN'")
        
        #Valider si le numéro SNRC est déjà présent
        arcpy.AddMessage("- Valider le numéro Snrc ...")
        #Valider le Numéro SNRC
        oSnrc = Snrc.Snrc(snrc)
        #Vérifier si le Snrc est valide
        if oSnrc.EstValide() and oSnrc.Echelle() == "50000":
            #Vérifier si le numéro Snrc respecte le standard
            if snrc <> oSnrc.sNumero:
                #Retourner une exception
                raise Exception("L'identifiant BDG ne correspond pas au numéro SNRC standard : " + snrc + "<>" + oSnrc.sNumero)
            #Définir la commande SQL
            sql = "SELECT IDENTIFIANT FROM V100_ID WHERE TY_PRODUIT = 'BDG' AND IDENTIFIANT='" + snrc + "'"
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Extraire l'identifiant de la vue
            resultat = self.Sib.requeteSib(sql)
            #Vérifier si l'identifiant est absent de la vue
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception("L'identifiant est absent la vue V100_ID : " + snrc)
        #Si le Snrc est invalide
        else:
            #Retourner une exception
            raise Exception("Numéro Snrc invalide : " + snrc)
        
        #Valider les Zones UTM
        arcpy.AddMessage("- Valider les zones UTM ...")
        #Vérifier si l'identifiant est déjà présent
        if no_fu_1 <> oSnrc.ZoneUtm():
            #Retourner une exception
            raise Exception("Zone Utm 1 invalide : " + no_fu_1 + "<>" + oSnrc.ZoneUtm())
        #Vérifier s'il y a 2 zones
        if oSnrc.DeuxZones() == "OUI":
            #Vérifier si la zone est différente
            if no_fu_2 <> oSnrc.ZoneUtmOuest:
                #Retourner une exception
                raise Exception("Zone Utm 2 invalide : " + no_fu_2 + "<>" + oSnrc.ZoneUtmOuest())
        #Sinon
        else:
            #Vérifier si la zone est différente
            if no_fu_2 <> "-1":
                #Retourner une exception
                raise Exception("Zone Utm 2 invalide : " + no_fu_2 + "<>-1")
        
        #Valider le poucentage de terre
        arcpy.AddMessage("- Valider le pourcentage de terre ...")
        #Vérifier si le pourcentage est numérique
        if pct_terre.isdigit():
            #Vérifier si le pourcentage de terre est valide
            if int(pct_terre) < 0 or int(pct_terre) > 100:
                #Retourner une exception
                raise Exception("Pourcentage de terre invalide : " + pct_terre)
        #Si le pourcentage n'est pas numérique
        else:
            #Retourner une exception
            raise Exception("Pourcentage de terre non numérique : " + pct_terre)
        
        #Extraire l'identifiant de la table
        resultat = self.Sib.requeteSib("SELECT SNRC FROM F101_SN WHERE SNRC='" + snrc + "'")
        #Vérifier si l'identifiant est présent
        if len(resultat) > 0:
            #Créer l'identifiant SNRC
            arcpy.AddMessage("- Modifier l'information de l'identifiant dans la table F101_SN ...")
            sql = "UPDATE F101_SN SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE"
            sql = sql + ", NOM='" + nom + "', NOM_AN='" + nom_an + "', NO_FU_1=" + no_fu_1 + ", NO_FU_2=" + no_fu_2 + ", PCT_TERRE=" + pct_terre
            sql = sql + " WHERE SNRC='" + snrc + "'"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Ajouter les types de produit associés au type de travail
        arcpy.AddMessage("- Détruire les codes de province dans la table F103_PS ...")
        #Extraire les provinces de l'identifiant
        resultat = self.Sib.requeteSib("SELECT * FROM F103_PS WHERE SNRC='" + snrc + "'")
        #Afficher toutes les provinces
        for prov in resultat:
            #Afficher les provinces
            arcpy.AddWarning(str(prov))
        #Afficher et exécuter la commande
        sql = "DELETE F103_PS WHERE SNRC='" + snrc + "'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Initialiser le compteur
        cpt = 0
        #Ajouter les types de produit associés au type de travail
        arcpy.AddMessage("- Ajouter les codes de province dans la table F103_PS ...")
        #Traiter la liste des provinces
        for prov in cd_prov.split(","):
            #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
            if prov not in "AB,BC,ET,FR,GL,MB,NB,NL,NS,NT,NU,ON,PEQC,SK,US,YT":
                #Retourner une exception
                raise Exception("Le code de province est invalide : " + prov)
            #Compteur
            cpt = cpt + 1
            #Ajouter la province
            sql = "INSERT INTO F103_PS VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + prov + "','" + snrc + "'," + str(cpt) + ",P0G03_UTL.PU_HORODATEUR)"
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
        snrc        = ""
        nom         = ""
        nom_an      = ""
        no_fu_1     = ""
        no_fu_2     = "-1"
        pct_terre   = "0"
        cd_prov     = ""

        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            snrc = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            nom = sys.argv[3]
        
        if len(sys.argv) > 4:
            nom_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            no_fu_1 = sys.argv[5]
        
        if len(sys.argv) > 6:
            no_fu_2 = sys.argv[6]
        
        if len(sys.argv) > 7:
            pct_terre = sys.argv[7]
        
        if len(sys.argv) > 8:
            cd_prov = sys.argv[8].upper().replace(";",",")
        
        #Définir l'objet pour modifier l'information d'un identifiant BDG de découpage SNRC 50000 pour la production dans SIB.
        oModifierIdentifiantBDG = ModifierIdentifiantBDG()
        
        #Valider les paramètres obligatoires
        oModifierIdentifiantBDG.validerParamObligatoire(env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov)
        
        #Exécuter le traitement pour modifier l'information d'un identifiant BDG de découpage SNRC 50000 pour la production dans SIB.
        oModifierIdentifiantBDG.executer(env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov)
    
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