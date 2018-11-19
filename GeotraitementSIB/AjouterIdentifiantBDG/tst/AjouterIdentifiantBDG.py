#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : AjouterIdentifiantBDG.py
# Auteur    : Michel Pothier
# Date      : 21 juin 2016

"""
    Application qui permet d'ajouter un identifiant BDG de d�coupage SNRC 50000 pour la production dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    snrc            OB      Identifiant SNRC � ajouter.
                            d�faut = 
    nom             OB      Nom en fran�ais de l'identifiant SNRC.
                            d�faut = "Totalement submerge"
    nom_an          OB      Nom en anglais de l'identifiant SNRC.
                            d�faut = "Totally submerged"
    no_fu_1         OB      Premier num�ro de fuseau UTM de l'identifiant SNRC.
                            d�faut = 
    no_fu_2         OB      Deuxi�me num�ro de fuseau UTM de l'identifiant SNRC.
                            d�faut = -1
    pct_terre       OB      Pourcentage de terre de l'identifiant SNRC.
                            d�faut = 0
    cd_prov         OB      Code de province de l'identifiant SNRC.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        AjouterIdentifiantBDG.py env snrc nom nom_an no_fu_1 no_fu_2 pct_terre cd_prov

    Exemple:
        AjouterIdentifiantBDG.py SIB_PRO 021M07 MAILLARD MAILLARD 19 -1 100 QC

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AjouterIdentifiantBDG.py 2058 2016-06-21 20:43:08Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib, Snrc

#*******************************************************************************************
class AjouterIdentifiantBDG(object):
#*******************************************************************************************
    """
    Permet d'ajouter un identifiant BDG de d�coupage SNRC 50000 pour la production dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour ajouter un identifiant BDG de d�coupage SNRC 50000 pour la production dans SIB.
        
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
    def validerParamObligatoire(self, env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC � ajouter.
        nom             : Nom den fran�ais de l'identifiant SNRC.
        nom_an          : Nom en anglais de l'identifiant SNRC.
        no_fu_1         : Premier num�ro de fuseau UTM de l'identifiant SNRC.
        no_fu_2         : Deuxi�me num�ro de fuseau UTM de l'identifiant SNRC.
        pct_terre       : Pourcentage de terre de l'identifiant SNRC.
        cd_prov         : Code de province de l'identifiant SNRC.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(snrc) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'snrc')

        if (len(nom) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom')

        if (len(nom_an) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'nom_an')

        if len(no_fu_1) == 0:
            raise Exception("Param�tre obligatoire manquant: %s" %'no_fu_1')

        if len(no_fu_2) == 0:
            raise Exception("Param�tre obligatoire manquant: %s" %'no_fu_2')

        if len(pct_terre) == 0:
            raise Exception("Param�tre obligatoire manquant: %s" %'pct_terre')

        if (len(cd_prov) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'cd_prov')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self, env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour ajouter un identifiant BDG de d�coupage SNRC 50000 pour la production dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        snrc            : Identifiant SNRC � ajouter.
        nom             : Nom den fran�ais de l'identifiant SNRC.
        nom_an          : Nom en anglais de l'identifiant SNRC.
        no_fu_1         : Premier num�ro de fuseau UTM de l'identifiant SNRC.
        no_fu_2         : Deuxi�me num�ro de fuseau UTM de l'identifiant SNRC.
        pct_terre       : Pourcentage de terre de l'identifiant SNRC.
        cd_prov         : Code de province de l'identifiant SNRC.
        
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
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'PLAN'")
        
        #Valider si le num�ro SNRC est d�j� pr�sent
        arcpy.AddMessage("- Valider le num�ro Snrc ...")
        #Valider le Num�ro SNRC
        oSnrc = Snrc.Snrc(snrc)
        #V�rifier si le Snrc est valide
        if oSnrc.EstValide() and oSnrc.Echelle() == "50000":
            #D�finir le num�ro Snrc valide
            snrc = oSnrc.sNumero
            #D�finir la commande SQL
            sql = "SELECT IDENTIFIANT FROM V100_ID WHERE TY_PRODUIT = 'BDG' AND IDENTIFIANT='" + snrc + "'"
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Extraire l'identifiant de la vue
            resultat = self.Sib.requeteSib(sql)
            #V�rifier si l'identifiant est d�j� pr�sent
            if len(resultat) > 0:
                #Retourner une exception
                raise Exception("L'identifiant est d�j� pr�sent dans la vue V100_ID : " + snrc)
        #Si le Snrc est invalide
        else:
            #Retourner une exception
            raise Exception("Num�ro Snrc invalide : " + snrc)
        
        #Valider les Zones UTM
        arcpy.AddMessage("- Valider les zones UTM ...")
        #V�rifier si l'identifiant est d�j� pr�sent
        if no_fu_1 <> oSnrc.ZoneUtm():
            #Retourner une exception
            raise Exception("Zone Utm 1 invalide : " + no_fu_1 + "<>" + oSnrc.ZoneUtm())
        #V�rifier s'il y a 2 zones
        if oSnrc.DeuxZones() == "OUI":
            #V�rifier si la zone est diff�rente
            if no_fu_2 <> oSnrc.ZoneUtmOuest:
                #Retourner une exception
                raise Exception("Zone Utm 2 invalide : " + no_fu_2 + "<>" + oSnrc.ZoneUtmOuest())
        #Sinon
        else:
            #V�rifier si la zone est diff�rente
            if no_fu_2 <> "-1":
                #Retourner une exception
                raise Exception("Zone Utm 2 invalide : " + no_fu_2 + "<>-1")
        
        #Valider le poucentage de terre
        arcpy.AddMessage("- Valider le pourcentage de terre ...")
        #V�rifier si le pourcentage est num�rique
        if pct_terre.isdigit():
            #V�rifier si le pourcentage de terre est valide
            if int(pct_terre) < 0 or int(pct_terre) > 100:
                #Retourner une exception
                raise Exception("Pourcentage de terre invalide : " + pct_terre)
        #Si le pourcentage n'est pas num�rique
        else:
            #Retourner une exception
            raise Exception("Pourcentage de terre non num�rique : " + pct_terre)
        
        #Extraire l'identifiant de la table
        resultat = self.Sib.requeteSib("SELECT SNRC FROM F101_SN WHERE SNRC='" + snrc + "'")
        #V�rifier si l'identifiant est d�j� pr�sent
        if len(resultat) == 0:
            #Cr�er l'identifiant SNRC
            arcpy.AddMessage("- Ajouter l'identifiant dans la table F101_SN ...")
            sql = "INSERT INTO F101_SN VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + snrc + "',50000,'" + nom + "','" + nom_an + "'," + no_fu_1 + "," + no_fu_2 + "," + pct_terre + ")"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Extraire l'identifiant de la table
        resultat = self.Sib.requeteSib("SELECT IDENTIFIANT FROM F101_BG WHERE IDENTIFIANT='" + snrc + "' AND TY_DECOUPAGE='SNRC'")
        #V�rifier si l'identifiant est d�j� pr�sent
        if len(resultat) == 0:
            #Cr�er l'identifiant BDG
            arcpy.AddMessage("- Ajouter l'identifiant dans la table F101_BG ...")
            sql = "INSERT INTO F101_BG VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + snrc + "','SNRC')"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Extraire l'identifiant de la table
        resultat = self.Sib.requeteSib("SELECT SNRC FROM F103_PS WHERE SNRC='" + snrc + "'")
        #V�rifier si l'identifiant est d�j� pr�sent
        if len(resultat) == 0:
            #Initialiser le compteur
            cpt = 0
            #Ajouter les types de produit associ�s au type de travail
            arcpy.AddMessage("- Ajouter les codes de province dans la table F103_PS ...")
            #Traiter la liste des provinces
            for prov in cd_prov.split(","):
                #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        snrc        = ""
        nom         = "Totalement submerge"
        nom_an      = "Totally submerged"
        no_fu_1     = ""
        no_fu_2     = "-1"
        pct_terre   = "0"
        cd_prov     = ""

        #extraction des param�tres d'ex�cution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            snrc = sys.argv[2].upper()
        
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
            cd_prov = sys.argv[8].replace(";",",")
        
        #D�finir l'objet pour ajouter un identifiant BDG de d�coupage SNRC 50000 pour la production dans SIB.
        oAjouterIdentifiantBDG = AjouterIdentifiantBDG()
        
        #Valider les param�tres obligatoires
        oAjouterIdentifiantBDG.validerParamObligatoire(env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov)
        
        #Ex�cuter le traitement pour ajouter un identifiant BDG de d�coupage SNRC 50000 pour la production dans SIB.
        oAjouterIdentifiantBDG.executer(env, snrc, nom, nom_an, no_fu_1, no_fu_2, pct_terre, cd_prov)
    
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