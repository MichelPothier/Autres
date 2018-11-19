#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierTypeProduit.py
# Auteur    : Michel Pothier
# Date      : 5 janvier 2015

"""
    Application qui permet de modifier l'information d'un type de produit dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    produit         OB      Type de produit � modifier.
                            d�faut = 
    desc_fr         OB      Description en fran�ais du type de produit.
                            d�faut = 
    desc_an         OB      Description en anglais du type de produit.
                            d�faut =
    acronyme_fr     OB      Acronyme en fran�ais du type de produit.
                            d�faut = 
    acronyme_an     OB      Acronyme en anglais du type de produit.
                            d�faut =
    utilisation     OB      Type d'utilisation li� au produit.
                            d�faut = 
    parametre       OB      Param�tres associ�s au produit.
                            d�faut = 
    catalogue       OB      Nom du catalogue pr�sentement utilis� pour d�finir le produit, les classes et les �l�ments.
                            d�faut = 
    decoupage       OB      D�coupage utilis� pour segmenter les �l�ments du produit.
                            d�faut = 
    depot           OB      Nom du d�p�t dans lequel le type de produit est situ�.
                            d�faut = 
    action          OP      Action � effectuer sur d'autres type de produit.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierTypeProduit.py env produit desc_fr desc_an acronyme_fr acronyme_an utilisation parametre catalogue decoupage depot action

    Exemple:
        ModifierTypeProduit.py SIB_PRO ESSIM 'Mod�le Int�gr� du Secteur des Sciences de la Terre' 'Earth Science Sector- Integrated Model' ESSIM ESSIM ISO;PRODUCTION MAP-SANS-ED-VER 1.0.0 SANS-DECOUPAGE INTEGRATED BNDT

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierTypeProduit.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierTypeProduit(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'un type de produit dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification de l'information d'un type de produit dans SIB.
        
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
    def validerParamObligatoire(self,env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        produit         : Type de produit � modifier.
        desc_fr         : Description en fran�ais du type de produit.
        desc_an         : Description en anglais du type de produit.
        acronyme_fr     : Acronyme en fran�ais du type de produit.
        acronyme_an     : Acronyme en anglais du type de produit.
        utilisation     : Type d'utilisation li� au produit.
        parametre       : Param�tres associ�s au produit.
        catalogue       : Nom du catalogue pr�sentement utilis� pour d�finir le produit, les classes et les �l�ments.
        decoupage       : D�coupage utilis� pour segmenter les �l�ments du produit.
        depot           : Nom du d�p�t dans lequel le type de produit est situ�.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(produit) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'produit')

        if (len(desc_fr) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'desc_fr')

        if (len(desc_an) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'desc_an')

        if (len(acronyme_fr) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'acronyme_fr')

        if (len(acronyme_an) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'acronyme_an')

        if (len(utilisation) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'utilisation')

        if (len(parametre) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'parametre')

        if (len(catalogue) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'catalogue')

        if (len(decoupage) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'decoupage')

        if (len(depot) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'depot')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot,action):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de modification de l'information d'un type de produit dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        produit         : Type de produit � modifier.
        desc_fr         : Description en fran�ais du type de produit.
        desc_an         : Description en anglais du type de produit.
        acronyme_fr     : Acronyme en fran�ais du type de produit.
        acronyme_an     : Acronyme en anglais du type de produit.
        utilisation     : Type d'utilisation li� au produit.
        parametre       : Param�tres associ�s au produit.
        catalogue       : Nom du catalogue pr�sentement utilis� pour d�finir le produit, les classes et les �l�ments.
        decoupage       : D�coupage utilis� pour segmenter les �l�ments du produit.
        depot           : Nom du d�p�t dans lequel le type de produit est situ�.
        action          : Action � effectuer sur d'autres type de produit.
        
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
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #Valider si le type de produit est d�j� pr�sent
        arcpy.AddMessage("- Valider le type de produit")
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F000_PR WHERE TY_PRODUIT='" + produit + "'")
        #V�rifier si le type de produit est pr�sent
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le type de produit '" + produit + "' est absent")
        
        #Valider si l'acronyme fran�ais est d�j� pr�sent
        arcpy.AddMessage("- Valider l'acronyme fran�ais")
        resultat = self.Sib.requeteSib("SELECT ACRONYME FROM F000_PR WHERE ACRONYME='" + acronyme_fr + "' AND TY_PRODUIT<>'" + produit + "'")
        #V�rifier si l'acronyme fran�ais est pr�sent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("L'acronyme fran�ais '" + acronyme_fr + "' est d�j� pr�sent")
        
        #Valider si l'acronyme anglais est d�j� pr�sent
        arcpy.AddMessage("- Valider l'acronyme anglais")
        resultat = self.Sib.requeteSib("SELECT ACRONYME_AN FROM F000_PR WHERE ACRONYME_AN='" + acronyme_an + "' AND TY_PRODUIT<>'" + produit + "'")
        #V�rifier si l'acronyme anglais est pr�sent
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("L'acronyme anglais '" + acronyme_an + "' est d�j� pr�sent")        
        
        #Traiter le champ DIFFUSION
        if "DIFFUSION" in utilisation:
            diffusion = "1"
        else:
            diffusion = "0"
        #Traiter le champ ISO
        if "ISO" in utilisation:
            iso = "1"
        else:
            iso = "0"
        #Traiter le champ PRODUCTION
        if "PRODUCTION" in utilisation:
            production = "1"
        else:
            production = "0"
        #Traiter le champ STRATEGIE
        if "STRATEGIE" in utilisation:
            strategie = "1"
        else:
            strategie = "0"
        
        #Cr�er le type de produit
        arcpy.AddMessage("- Modifier le type de produit")
        sql = "UPDATE F000_PR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,DESCR='" + desc_fr.replace("'", "''") + "',DESCR_AN='" + desc_an.replace("'", "''") + "'"
        sql = sql + ",DIFFUSION=" + diffusion + ",ISO=" + iso + ",PRODUCTION=" + production + ",STRATEGIE=" + strategie + ",ACRONYME='" + acronyme_fr + "',ACRONYME_AN='" + acronyme_an + "' WHERE TY_PRODUIT='" + produit + "'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre MAP-LISTE-ENTITE
        if "MAP-LISTE-ENTITE" in parametre:
            valeur = "1"
        else:
            valeur = "0"
        sql = "UPDATE F008_PP SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,VALEUR='" + valeur + "' WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='MAP-LISTE-ENTITE'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre MAP-SANS-ED-VER
        if "MAP-SANS-ED-VER" in parametre:
            valeur = "1"
        else:
            valeur = "0"
        sql = "UPDATE F008_PP SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,VALEUR='" + valeur + "' WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='MAP-SANS-ED-VER'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre PRODUIT-OBLIGATOIRE-INVENTAIRE
        if "PRODUIT-OBLIGATOIRE-INVENTAIRE" in parametre:
            valeur = "1"
        else:
            valeur = "0"
        sql = "UPDATE F008_PP SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,VALEUR='" + valeur + "' WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='PRODUIT-OBLIGATOIRE-INVENTAIRE'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre DECOUPAGE
        sql = "UPDATE F008_PP SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,VALEUR='" + decoupage + "' WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='DECOUPAGE'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre DEPOT
        sql = "UPDATE F008_PP SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,VALEUR='" + depot + "' WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='DEPOT'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Traiter le parametre ACTION
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='ACTION'")
        #Si le param�tre ACTION est pr�sent dans SIB
        if len(resultat) > 0:
            #Si la valeur du param�tre ACTION est pr�sente
            if len(action) > 0:
                #On modifie la valeur
                sql = "UPDATE F008_PP SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,VALEUR='" + action + "' WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='ACTION'"
            #Si la valeur du param�tre ACTION est absente
            else:
                #On d�truit la valeur
                sql = "DELETE FROM F008_PP WHERE TY_PRODUIT='" + produit + "' AND CD_PARAMETRE='ACTION'"
        #Si le param�tre ACTION est absent dans SIB
        else:
            #Si la valeur du param�tre ACTION est pr�sente
            if len(action) > 0:
                #On ajoute la valeur
                sql = "INSERT INTO F008_PP VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + produit + "','ACTION','" +  action + "')"
                arcpy.AddMessage(sql)
                self.Sib.execute(sql)
        
        #Traiter le parametre catalogue
        sql = "UPDATE F010_DP SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,DF_STRING='" + catalogue + "' WHERE TY_PRODUIT='" + produit + "'"
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
        produit     = ""
        desc_fr     = ""
        desc_an     = ""
        acronyme_fr = ""
        acronyme_an = ""
        utilisation = ""
        parametre   = ""
        catalogue   = ""
        decoupage   = ""
        depot       = ""
        action      = ""
        
        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            produit = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            desc_fr = sys.argv[3]
        
        if len(sys.argv) > 4:
            desc_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            acronyme_fr = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            acronyme_an = sys.argv[6].upper()
                
        if len(sys.argv) > 7:
            utilisation = sys.argv[7].upper()
        
        if len(sys.argv) > 8:
            parametre = sys.argv[8].upper()
        
        if len(sys.argv) > 9:
            catalogue = sys.argv[9].upper()
        
        if len(sys.argv) > 10:
            decoupage = sys.argv[10].upper()
        
        if len(sys.argv) > 11:
            depot = sys.argv[11].upper()
        
        if len(sys.argv) > 12:
            action = sys.argv[12].upper()
        
        #D�finir l'objet de modification d'un type de produit dans SIB.
        oModifierTypeProduit = ModifierTypeProduit()
        
        #Valider les param�tres obligatoires
        oModifierTypeProduit.validerParamObligatoire(env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot)
        
        #Ex�cuter le traitement de modification d'un type de produit dans SIB.
        oModifierTypeProduit.executer(env,produit,desc_fr,desc_an,acronyme_fr,acronyme_an,utilisation,parametre,catalogue,decoupage,depot,action)
    
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