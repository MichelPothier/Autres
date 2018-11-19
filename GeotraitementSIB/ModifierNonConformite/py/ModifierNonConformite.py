#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : ModifierNonConformite.py
# Auteur    : Michel Pothier
# Date      : 24 novembre 2014

"""
    Application qui permet de modifier l'information d'une non-conformit� dans SIB.
    Aucune modification n'est permise lorsque la date de fermeture est pr�sente.
    Aucun identifiant ne peut �tre d�truit lorsque l'intervalle de fin (ed_fin,ver_fin) est pr�sente.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    no_nc                   Num�ro de non-conformit� � modifier.
                            d�faut = 
    titre           OB      Le titre de la non-conformit�.
                            d�faut = 
    titre_an        OB      Le titre anglais de la non-conformit�.
                            d�faut = 
    nom_source      OB      Le nom de la source de la non-conformit�.
                            d�faut = 
    ty_nc           OB      Le type de non-conformit�.
                            OP : Observation produit
                            DM : Donn�es modifi�es dans la BD
                            PA : Plainte autre
                            PP : Plainte produit
                            Ne sont plus utilis�s:
                            ND : Non-disponible
                            OA : Observation autre
                            PD : Plainte de distrubution non-active
                            SQ : Syst�me qualit�
                            d�faut = PP
    origine_nc      OB      L'origine de la non-conformit�.
                            AI : Audit externe
                            CL : Client
                            EC : �quipe CIT-Sherbrooke
                            OT : �quipe CIT-Ottawa
                            d�faut = EC
    ty_trait_nc     OB      Type de traitement de la non-conformit�.
                            N/A : Non applicable
                            AUCUN : Aucun traitement
                            CORRECTION : Correction produit
                            CORR_CAUSE : Correction cause/produit
                            DEROGATION : Produit en d�rogation
                            RETRAIT : Produit retir�
                            ME : Correction m�tadonn�es
                            ME_CAUSE : Correction cause/md
                            SM : Correction spatial/md
                            SM_CAUSE : Correction cause/spatial/md
                            SP : Correction spatial
                            SP_CAUSE : Correction cause/spatial
                            d�faut = CORRECTION
    descr           OB      La description de la non-conformit�.
                            d�faut = 
    resp_descr      OB      Le code de l'usager responsable de la description de la non-conformit�.
                            d�faut = <UsagerSIB>
    date_saisie     OB      Date de saisie de la description de la non conformit�.
                            d�faut = <datetime.now()>
    doc_connexe     OB      Fanion indiquant s'il y a des documents connexes pour cette non-conformit�.
                            d�faut = 0:NON
    cause           OB      La cause de la non-conformit�.
                            d�faut = 
    traitement      OB      Le traitement apport� � la non-conformit�.
                            d�faut = 
    resp_corr       OP      Le code de l'usager responsable de la correction de la non-conformit�.
                            d�faut = 
    echeance_init   OP      La date d'�ch�ance initiale pour la correction de la non-conformit�.
                            d�faut = 
    suivi_trait     OP      Le suivi du traitement de la non conformit�.
                            d�faut = 
    resp_suivi      OP      Le code de l'usager responsable du suivi de la non-conformit�.
                            d�faut = <UsagerSIB>
    date_traitement OP      La date de traitement de la non-conformit�.
                            d�faut = 
    date_fermeture  OP      La date de fermeture de la non conformit�.
                            date_fermeture >= date_saisie
                            d�faut =
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ModifierNonConformite.py env no_nc titre titre_an nom_source ty_nc origine_nc ty_trait_nc descr resp_descr date_saisie doc_connexe cause traitement resp_corr echeance_init suivi_trait resp_suivi date_traitement date_fermeture

    Exemple:
        ModifierNonConformite.py SIB_PRO 3034

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierNonConformite.py 2120 2016-09-15 17:01:33Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ModifierNonConformite(object):
#*******************************************************************************************
    """
    Permet de modifier l'information d'une non-conformit� dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de modification d'une non-conformit� dans SIB.
        
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
    def validerParamObligatoire(self,env,no_nc,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � modifier.
        titre           : Le titre de la non-conformit�.
        titre_an        : Le titre anglais de la non-conformit�.
        nom_source      : Le nom de la source de la non-conformit�.
        ty_nc           : Le type de non-conformit�.
        origine_nc      : L'origine de la non-conformit�.
        ty_trait_nc     : Type de traitement de la non-conformit�.
        descr           : La description de la non-conformit�.
        resp_descr      : Le code de l'usager responsable de la description de la non-conformit�.
        date_saisie     : Date de saisie de la description de la non conformit�.
        doc_connexe     : Fanion indiquant s'il y a des documents connexes pour cette non-conformit�.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')

        if (len(no_nc) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'env')
                
        if (len(titre) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'titre')
        
        if (len(titre_an) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'titre_an')
        
        if (len(nom_source) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'nom_source')
        
        if (len(ty_nc) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'ty_nc')
        
        if (len(origine_nc) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'origine_nc')
        
        if (len(ty_trait_nc) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'ty_trait_nc')
        
        if (len(descr) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'descr')
        
        if (len(resp_descr) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'resp_descr')
        
        if (len(date_saisie) == 0):
            raise Exception(u"Param�tre obligatoire manquant: %s" %'date_saisie')
        
        if doc_connexe <> "0" and doc_connexe <> "1":
            raise Exception(u"Param�tre obligatoire invalide: %s" %'doc_connexe')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,no_nc,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe,cause,traitement,resp_corr,echeance_init,suivi_trait,resp_suivi,date_traitement,date_fermeture):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de modification d'une non-conformit� dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� � modifier.
        titre           : Le titre de la non-conformit�.
        titre_an        : Le titre anglais de la non-conformit�.
        nom_source      : Le nom de la source de la non-conformit�.
        ty_nc           : Le type de non-conformit�.
        origine_nc      : L'origine de la non-conformit�.
        ty_trait_nc     : Type de traitement de la non-conformit�.
        descr           : La description de la non-conformit�.
        resp_descr      : Le code de l'usager responsable de la description de la non-conformit�.
        date_saisie     : Date de saisie de la description de la non conformit�.
        doc_connexe     : Fanion indiquant s'il y a des documents connexes pour cette non-conformit�.
        cause           : La cause de la non-conformit�.
        traitement      : Le traitement apport� � la non-conformit�.
        resp_corr       : Le code de l'usager responsable de la correction de la non-conformit�.
        echeance_init   : La date d'�ch�ance initiale pour la correction de la non-conformit�.
        suivi_trait     : Le suivi du traitement de la non conformit�.
        resp_suivi      : Le code de l'usager responsable du suivi de la non-conformit�.
        date_traitement : La date de traitement de la non-conformit�.
        date_fermeture  : La date de fermeture de la non conformit�.
        
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
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #------------------------------------------------------
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'ISO-RQNC'")
        
        #------------------------------------------------------
        #Valider l'information de la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider l'information de la non-conformit� ...")
        sql = "SELECT NO_NC,DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + no_nc + "' AND DATE_FERMETURE IS NULL"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception(u"La non-conformit� '" + no_nc + "' n'existe pas ou est ferm�e")
        #V�rifier la date de traitement
        if str(resultat[0][1]) <> "None":
            #Retourner un AVERTISSEMENT
            arcpy.AddWarning(u"Attention : La date de traitement est pr�sente : " + str(resultat[0][1]))
        
        #V�rifier si la longueur est respect�e
        titre = unicode(titre, "utf-8")
        if len(titre) > 100:
            #Retourner une exception
            raise Exception(u"La longueur du param�tre 'titre' d�passe 100 catact�tes, longueur=" + str(len(titre)))
        
        #V�rifier si la longueur est respect�e
        titre_an = unicode(titre_an, "utf-8")
        if len(titre_an) > 100:
            #Retourner une exception
            raise Exception(u"La longueur du param�tre 'titre_an' d�passe 100 catact�tes, longueur=" + str(len(titre_an)))
        
        #V�rifier si la longueur est respect�e
        nom_source = unicode(nom_source, "utf-8")
        if len(nom_source) > 100:
            #Retourner une exception
            raise Exception(u"La longueur du param�tre 'nom_source' d�passe 100 catact�tes, longueur=" + str(len(nom_source)))
        
        #V�rifier si la longueur est respect�e
        descr = unicode(descr, "utf-8")
        if len(descr) > 1000:
            #Retourner une exception
            raise Exception(u"La longueur du param�tre 'descr' d�passe 1000 catact�tes, longueur=" + str(len(descr)))
        
        #V�rifier si la longueur est respect�e
        cause = unicode(cause, "utf-8")
        if len(cause) > 1000:
            #Retourner une exception
            raise Exception(u"La longueur du param�tre 'cause' d�passe 1000 catact�tes, longueur=" + str(len(cause)))
        
        #V�rifier si la longueur est respect�e
        traitement = unicode(traitement, "utf-8")
        if len(traitement) > 1000:
            #Retourner une exception
            raise Exception(u"La longueur du param�tre 'traitement' d�passe 1000 catact�tes, longueur=" + str(len(traitement)))
        
        #V�rifier si la valeur n'est pas vide
        if resp_corr <> "NULL":
            #On doit ins�rer les apostrophes
            resp_corr = "'" + resp_corr + "'"
        
        #V�rifier si la valeur n'est pas vide
        if echeance_init <> "NULL":
            #On doit ins�rer les apostrophes
            echeance_init = "'" + echeance_init + "'"
        
        #V�rifier si la valeur n'est pas vide
        if suivi_trait <> "NULL":
            #V�rifier si la longueur est respect�e
            suivi_trait = unicode(suivi_trait, "utf-8")
            if len(suivi_trait) > 1000:
                #Retourner une exception
                raise Exception(u"La longueur du param�tre 'suivi_trait' d�passe 1000 catact�tes, longueur=" + str(len(suivi_trait)))
            #On doit ins�rer les apostrophes
            suivi_trait = "'" + suivi_trait.replace("'", "''") + "'"
        
        #V�rifier si la valeur n'est pas vide
        if resp_suivi <> "NULL":
            #On doit ins�rer les apostrophes
            resp_suivi = "'" + resp_suivi + "'"
        
        #V�rifier si la valeur n'est pas vide
        if date_traitement <> "NULL":
            #On doit ins�rer les apostrophes
            date_traitement = "'" + date_traitement + "'"
        
        #V�rifier si la valeur n'est pas vide
        if date_fermeture <> "NULL":
            #On doit ins�rer les apostrophes
            date_fermeture = "'" + date_fermeture + "'"
        
        #------------------------------------------------------
        #Modifier l'information de la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information d'une non-conformit� ...")
        sql = "ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE,TITRE='" + titre.replace("'", "''") + "',NOM_SOURCE='" + nom_source.replace("'", "''") + "'"
        sql = sql + ",TY_NC='"  + ty_nc + "',ORIGINE_NC='" + origine_nc + "',DESCR='" + descr.replace("'", "''") + "',RESP_DESCR='" + resp_descr + "',DATE_SAISIE='" + date_saisie + "'"
        sql = sql + ",CAUSE='" + cause.replace("'", "''") + "',TRAITEMENT='" + traitement.replace("'", "''") + "',RESP_CORR=" + resp_corr + ",ECHEANCE_INIT=" + echeance_init + ",RESP_SUIVI=" + resp_suivi
        sql = sql + ",DATE_FERMETURE=" + date_fermeture + ",SUIVI_TRAIT=" + suivi_trait + ",DOC_CONNEXE=" + doc_connexe + ",UPDT_FLD=P0G03_UTL.PU_HORODATEUR,DATE_TRAITEMENT=" + date_traitement + ",TITRE_AN='" + titre_an.replace("'", "''") + "',TY_TRAIT_NC='" + ty_trait_nc + "'"
        arcpy.AddMessage("UPDATE F702_NC SET " + sql + " WHERE NO_NC='" + no_nc + "'")
        self.Sib.execute("UPDATE F702_NC SET " + sql + " WHERE NO_NC='" + no_nc + "'")
        
        #------------------------------------------------------
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
        env             = "SIB_PRO"
        no_nc           = ""
        titre           = ""
        titre_an        = ""
        nom_source      = ""
        ty_nc           = ""
        origine_nc      = ""
        ty_trait_nc     = ""
        descr           = ""
        resp_descr      = ""
        date_saisie     = ""
        doc_connexe     = ""
        cause           = ""
        traitement      = ""
        resp_corr       = "NULL"
        echeance_init   = "NULL"
        suivi_trait     = "NULL"
        resp_suivi      = "NULL"
        date_traitement = "NULL"
        date_fermeture  = "NULL"

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            titre = sys.argv[3]
        
        if len(sys.argv) > 4:
            titre_an = sys.argv[4]
        
        if len(sys.argv) > 5:
            nom_source = sys.argv[5]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                ty_nc = sys.argv[6].split(":")[0]
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                origine_nc = sys.argv[7].split(":")[0]
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                ty_trait_nc = sys.argv[8].split(":")[0]
        
        if len(sys.argv) > 9:
            descr = sys.argv[9]
        
        if len(sys.argv) > 10:
            resp_descr = sys.argv[10].split(":")[0]
        
        if len(sys.argv) > 11:
            date_saisie = sys.argv[11]
        
        if len(sys.argv) > 12:
            doc_connexe = sys.argv[12].split(":")[0]
        
        if len(sys.argv) > 13:
            if sys.argv[13] <> "#":
                cause = sys.argv[13]
        
        if len(sys.argv) > 14:
            if sys.argv[14] <> "#":
                traitement = sys.argv[14]
        
        if len(sys.argv) > 15:
            if sys.argv[15] <> "#":
                resp_corr = sys.argv[15].split(":")[0]
        
        if len(sys.argv) > 16:
            if sys.argv[16] <> "#":
                echeance_init = sys.argv[16]
        
        if len(sys.argv) > 17:
            if sys.argv[17] <> "#":
                suivi_trait = sys.argv[17]
        
        if len(sys.argv) > 18:
            if sys.argv[18] <> "#":
                resp_suivi = sys.argv[18].split(":")[0]
        
        if len(sys.argv) > 19:
            if sys.argv[19] <> "#":
                date_traitement = sys.argv[19]
        
        if len(sys.argv) > 20:
            if sys.argv[20] <> "#":
                date_fermeture = sys.argv[20]
        
        #D�finir l'objet de modification d'une non-conformit� dans SIB.
        oModifierNonConformite = ModifierNonConformite()
        
        #Valider les param�tres obligatoires
        oModifierNonConformite.validerParamObligatoire(env,no_nc,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe)
        
        #Ex�cuter le traitement de modification d'une non-conformit� dans SIB.
        oModifierNonConformite.executer(env,no_nc,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe,cause,traitement,resp_corr,echeance_init,suivi_trait,resp_suivi,date_traitement,date_fermeture)   

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