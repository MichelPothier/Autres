#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerNonConformitePlus.py
# Auteur    : Michel Pothier
# Date      : 18 novembre 2014

"""
    Application qui permet de créer une nouvelle non-conformité dans SIB, d'ajouter des liens avec d'autres non-conformités et d'ajouter des identifiants d'un produit.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    ty_produit      OB      Type de produit qui est non-conformes.
                            défaut = 
    decoupage       OB      Classe de découpage contenant les géométries et les identifiants qui sont non-conformes.
                            défaut = <RECORDSET respectant le schéma de la classe MAP_INDEX_2 de la BDRS>
    attribut        OB      Attribut de la classe de découpage contenant les identifiants qui sont non-conformes.
                            défaut = DATASET_NAME
    titre           OB      Le titre de la non-conformité.
                            défaut = 
    titre_an        OB      Le titre anglais de la non-conformité.
                            défaut = 
    nom_source      OB      Le nom de la source de la non-conformité.
                            défaut = 
    ty_nc           OB      Le type de non-conformité.
                            OP : Observation produit
                            DM : Données modifiées dans la BD
                            PA : Plainte autre
                            PP : Plainte produit
                            Ne sont plus utilisés:
                            ND : Non-disponible
                            OA : Observation autre
                            PD : Plainte de distrubution non-active
                            SQ : Système qualité
                            défaut = PP
    origine_nc      OB      L'origine de la non-conformité.
                            AI : Audit externe
                            CL : Client
                            EC : Équipe CIT-Sherbrooke
                            OT : Équipe CIT-Ottawa
                            défaut = EC
    ty_trait_nc     OB      Type de traitement de la non-conformité.
                            N/A : Non applicable
                            AUCUN : Aucun traitement
                            CORRECTION : Correction produit
                            CORR_CAUSE : Correction cause/produit
                            DEROGATION : Produit en dérogation
                            RETRAIT : Produit retiré
                            ME : Correction métadonnées
                            ME_CAUSE : Correction cause/md
                            SM : Correction spatial/md
                            SM_CAUSE : Correction cause/spatial/md
                            SP : Correction spatial
                            SP_CAUSE : Correction cause/spatial
                            défaut = CORRECTION
    descr           OB      La description de la non-conformité.
                            défaut = 
    resp_descr      OB      Le code de l'usager responsable de la description de la non-conformité.
                            défaut = <UsagerSIB>
    date_saisie     OB      Date de saisie de la description de la non conformité.
                            défaut = <datetime.now()>
    doc_connexe     OB      Fanion indiquant s'il y a des documents connexes pour cette non-conformité.
                            défaut = 0:NON
    cause           OB      La cause de la non-conformité.
                            défaut = 
    traitement      OB      Le traitement apporté à la non-conformité.
                            défaut = 
    resp_corr       OP      Le code de l'usager responsable de la correction de la non-conformité.
                            défaut = 
    echeance_init   OP      La date d'échéance initiale pour la correction de la non-conformité.
                            défaut = 
    suivi_trait     OP      Le suivi du traitement de la non conformité.
                            défaut = 
    resp_suivi      OP      Le code de l'usager responsable du suivi de la non-conformité.
                            défaut = <UsagerSIB>
    date_traitement OP      La date de traitement de la non-conformité.
                            défaut = 
    date_fermeture  OP      La date de fermeture de la non conformité.
                            date_fermeture >= date_saisie
                            défaut =
    lien_nc         OP      La liste des numéros de non-conformité en lien avec celui à créer.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerNonConformitePlus.py env ty_produit Identifiant titre titre_an nom_source ty_nc origine_nc ty_trait_nc descr resp_descr date_saisie doc_connexe cause traitement resp_corr echeance_init suivi_trait resp_suivi date_traitement date_fermeture lien_nc

    Exemple:
        CreerNonConformitePlus.py SIB_PRO

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerNonConformitePlus.py 2118 2016-09-15 16:58:22Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerNonConformitePlus(object):
#*******************************************************************************************
    """
    Permet de créer une nouvelle non-conformité dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'une nouvelle non-conformité dans SIB.
        
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
    def validerParamObligatoire(self,env,ty_produit,decoupage,attribut,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement
        ty_produit      : Type de produit qui est non-conforme.
        decoupage       : Classe de découpage contenant les géométries et les identifiants qui sont non-conformes.
        attribut        : Attribut de la classe de découpage contenant les identifiants qui sont non-conformes.
        titre           : Le titre de la non-conformité.
        titre_an        : Le titre anglais de la non-conformité.
        nom_source      : Le nom de la source de la non-conformité.
        ty_nc           : Le type de non-conformité.
        origine_nc      : L'origine de la non-conformité.
        ty_trait_nc     : Type de traitement de la non-conformité.
        descr           : La description de la non-conformité.
        resp_descr      : Le code de l'usager responsable de la description de la non-conformité.
        date_saisie     : Date de saisie de la description de la non conformité.
        doc_connexe     : Fanion indiquant s'il y a des documents connexes pour cette non-conformité.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(ty_produit) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'ty_produit')
        
        if (len(decoupage) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'decoupage')
        
        if (len(attribut) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'attribut')
        
        if (len(titre) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'titre')
        
        if (len(titre_an) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'titre_an')
        
        if (len(nom_source) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'nom_source')
        
        if (len(ty_nc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'ty_nc')
        
        if (len(origine_nc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'origine_nc')
        
        if (len(ty_trait_nc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'ty_trait_nc')
        
        if (len(descr) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'descr')
        
        if (len(resp_descr) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'resp_descr')
        
        if (len(date_saisie) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'date_saisie')
        
        if doc_connexe <> "0" and doc_connexe <> "1":
            raise Exception("Paramètre obligatoire invalide: %s" %'doc_connexe')

        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,ty_produit,decoupage,attribut,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe,cause,traitement,resp_corr,echeance_init,suivi_trait,resp_suivi,date_traitement,date_fermeture,lien_nc):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'une nouvelle non-conformité dans SIB, d'ajouter des liens avec d'autres non-conformités et d'ajouter des identifiants d'un produit.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        ty_produit      : Type de produit qui est non-conforme.
        decoupage       : Classe de découpage contenant les géométries et les identifiants qui sont non-conformes.
        attribut        : Attribut de la classe de découpage contenant les identifiants qui sont non-conformes.
        titre           : Le titre de la non-conformité.
        titre_an        : Le titre anglais de la non-conformité.
        nom_source      : Le nom de la source de la non-conformité.
        ty_nc           : Le type de non-conformité.
        origine_nc      : L'origine de la non-conformité.
        ty_trait_nc     : Type de traitement de la non-conformité.
        descr           : La description de la non-conformité.
        resp_descr      : Le code de l'usager responsable de la description de la non-conformité.
        date_saisie     : Date de saisie de la description de la non conformité.
        doc_connexe     : Fanion indiquant s'il y a des documents connexes pour cette non-conformité.
        cause           : La cause de la non-conformité.
        traitement      : Le traitement apporté à la non-conformité.
        resp_corr       : Le code de l'usager responsable de la correction de la non-conformité.
        echeance_init   : La date d'échéance initiale pour la correction de la non-conformité.
        suivi_trait     : Le suivi du traitement de la non conformité.
        resp_suivi      : Le code de l'usager responsable du suivi de la non-conformité.
        date_traitement : La date de traitement de la non-conformité.
        date_fermeture  : La date de fermeture de la non conformité.
        lien_nc         : La liste des numéros de non-conformité en lien avec celui à créer.
        
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
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #Valider si la non-conformité est déjà présente
        arcpy.AddMessage("- Valider si la non-conformité est déjà présente")
        sql = "SELECT NO_NC FROM F702_NC WHERE TITRE='" + titre.replace("'","''") + "' AND NOM_SOURCE='" + nom_source.replace("'","''") + "' AND TY_NC='" + ty_nc + "' AND DESCR='" + descr.replace("'","''") + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("La non-conformité '" + resultat[0][0] + "' est déjà présente")
        
        #Vérifier si la longueur est respectée
        titre = unicode(titre, "utf-8")
        if len(titre) > 100:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'titre' dépasse 100 catactètes, longueur=" + str(len(titre)))
        
        #Vérifier si la longueur est respectée
        titre_an = unicode(titre_an, "utf-8")
        if len(titre_an) > 100:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'titre_an' dépasse 100 catactètes, longueur=" + str(len(titre_an)))
        
        #Vérifier si la longueur est respectée
        nom_source = unicode(nom_source, "utf-8")
        if len(nom_source) > 100:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'nom_source' dépasse 100 catactètes, longueur=" + str(len(nom_source)))
        
        #Vérifier si la longueur est respectée
        descr = unicode(descr, "utf-8")
        if len(descr) > 1000:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'descr' dépasse 1000 catactètes, longueur=" + str(len(descr)))
        
        #Vérifier si la longueur est respectée
        cause = unicode(cause, "utf-8")
        if len(cause) > 1000:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'cause' dépasse 1000 catactètes, longueur=" + str(len(cause)))
        
        #Vérifier si la longueur est respectée
        traitement = unicode(traitement, "utf-8")
        if len(traitement) > 1000:
            #Retourner une exception
            raise Exception("La longueur du paramètre 'traitement' dépasse 1000 catactètes, longueur=" + str(len(traitement)))
        
        #Vérifier si la valeur n'est pas vide
        if resp_corr <> "NULL":
            #On doit insérer les apostrophes
            resp_corr = "'" + resp_corr + "'"
        
        #Vérifier si la valeur n'est pas vide
        if echeance_init <> "NULL":
            #On doit insérer les apostrophes
            echeance_init = "'" + echeance_init + "'"
        
        #Vérifier si la valeur n'est pas vide
        if suivi_trait <> "NULL":
            #Vérifier si la longueur est respectée
            suivi_trait = unicode(suivi_trait, "utf-8")
            if len(suivi_trait) > 1000:
                #Retourner une exception
                raise Exception("La longueur du paramètre 'suivi_trait' dépasse 1000 catactètes, longueur=" + str(len(suivi_trait)))
            #On doit insérer les apostrophes
            suivi_trait = "'" + suivi_trait.replace("'", "''") + "'"
        
        #Vérifier si la valeur n'est pas vide
        if resp_suivi <> "NULL":
            #On doit insérer les apostrophes
            resp_suivi = "'" + resp_suivi + "'"
        
        #Vérifier si la valeur n'est pas vide
        if date_traitement <> "NULL":
            #On doit insérer les apostrophes
            date_traitement = "'" + date_traitement + "'"
        
        #Vérifier si la valeur n'est pas vide
        if date_fermeture <> "NULL":
            #On doit insérer les apostrophes
            date_fermeture = "'" + date_fermeture + "'"
        
        #Définir le nouveau numéro de non-conformité
        arcpy.AddMessage("- Définir le nouveau numéro de non-conformité")
        resultat = self.Sib.requeteSib("SELECT MAX(NO_NC) FROM F702_NC")
        no_nc = str(int(resultat[0][0]) + 1).zfill(5)
        
        #Créer la non-conformité
        arcpy.AddMessage("- Créer une nouvelle non-conformité")
        sql = "'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + titre.replace("'", "''") + "','" + nom_source.replace("'", "''") + "'"
        sql = sql + ",'"  + ty_nc + "','" + origine_nc + "','" + descr.replace("'", "''") + "','" + resp_descr + "','" + date_saisie + "'"
        sql = sql + ",'" + cause.replace("'", "''") + "','" + traitement.replace("'", "''") + "'," + resp_corr + "," + echeance_init + "," + resp_suivi
        sql = sql + "," + date_fermeture + "," + suivi_trait.replace("'", "''") + "," + doc_connexe + ",P0G03_UTL.PU_HORODATEUR," + date_traitement + ",'" + titre_an.replace("'", "''") + "','" + ty_trait_nc + "'"
        arcpy.AddMessage("INSERT INTO F702_NC VALUES (" + sql + ")")
        self.Sib.execute("INSERT INTO F702_NC VALUES (" + sql + ")")
        
        #Créer les identifiants du produit non-conformes
        arcpy.AddMessage("- Créer les identifiants du produit non-conformes")
        ed_fin = '99999'
        ver_fin = '99'
        nb_id = 0
        #Traiter tous les éléments sélectionnés dans la classe de découpage
        #for row in arcpy.da.SearchCursor(decoupage, [attribut, "SHAPE@WKT"]):
        for row in arcpy.da.SearchCursor(decoupage, [attribut]):
            #Compter le nombre d'identifiant
            nb_id = nb_id + 1
            
            #Extraire le numéro d'édition et version du jeu de données courant
            resultat = self.Sib.requeteSib("SELECT ED,VER FROM V200_IN WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + str(row[0]) + "' AND JEU_COUR=1")
            #Vérifier le résultat
            if len(resultat) == 0:
                #Retourner une exception
                raise Exception("Il n'y a pas de jeu de données courant pour l'identifiant : " + str(row[0]))
            
            #Définir l'édition et version de début
            ed_deb = str(resultat[0][0])
            ver_deb = str(resultat[0][1])
            
            #Ajouter un identifiant du produit non-conforme
            sql = "'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + ty_produit + "','" + str(row[0]) + "'," + ed_deb + "," + ver_deb
            sql = sql + ",P0G03_UTL.PU_HORODATEUR," + ed_fin + "," + ver_fin
            arcpy.AddMessage("INSERT INTO F705_PR VALUES (" + sql + ")")
            self.Sib.execute("INSERT INTO F705_PR VALUES (" + sql + ")")
        
        #Vérifier si aucun identifiant n'est ajouté
        if nb_id == 0:
            #Retourner une exception
            raise Exception("Vous avez sélectionné aucun identifiant dans la classe de découpage")
        #Si au moins un identifiant sélectionné
        else:
            #Afficher le nombre d'identifiant non-conformes
            arcpy.AddMessage("  Nombre d'identifiants non-conformes : " + str(nb_id))
        
        #Créer les liens entre les non-conformités
        arcpy.AddMessage("- Créer les liens entre les non-conformités")
        #Traiter tous les liens entre les non-conformités
        for lien in lien_nc.split(","):
            #Ajouter un identifiant du produit non-conforme
            sql = "'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + lien.split(":")[0] + "',P0G03_UTL.PU_HORODATEUR,'NC'"
            arcpy.AddMessage("INSERT INTO F704_LI VALUES (" + sql + ")")
            self.Sib.execute("INSERT INTO F704_LI VALUES (" + sql + ")")
        
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
        env             = "SIB_PRO"
        ty_produit      = ""
        decoupage       = ""
        attribut        = "DATASET_NAME"
        titre           = ""
        titre_an        = ""
        nom_source      = ""
        ty_nc           = "PP"
        origine_nc      = "EC"
        ty_trait_nc     = "CORRECTION"
        descr           = ""
        resp_descr      = ""
        date_saisie     = ""
        doc_connexe     = "0"
        cause           = "NULL"
        traitement      = "NULL"
        resp_corr       = "NULL"
        echeance_init   = "NULL"
        suivi_trait     = "NULL"
        resp_suivi      = "NULL"
        date_traitement = "NULL"
        date_fermeture  = "NULL"
        lien_nc         = ""

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_produit = sys.argv[2].upper().split(":")[0]
        
        if len(sys.argv) > 3:
            decoupage = sys.argv[3]
         
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                attribut = sys.argv[4]
        
        if len(sys.argv) > 5:
            titre = sys.argv[5]
        
        if len(sys.argv) > 6:
            titre_an = sys.argv[6]
        
        if len(sys.argv) > 7:
            nom_source = sys.argv[7]
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                ty_nc = sys.argv[8].split(":")[0]
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                origine_nc = sys.argv[9].split(":")[0]
        
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                ty_trait_nc = sys.argv[10].split(":")[0]
        
        if len(sys.argv) > 11:
            descr = sys.argv[11]
        
        if len(sys.argv) > 12:
            resp_descr = sys.argv[12].split(":")[0]
        
        if len(sys.argv) > 13:
            date_saisie = sys.argv[13]
        
        if len(sys.argv) > 14:
            doc_connexe = sys.argv[14].split(":")[0]
        
        if len(sys.argv) > 15:
            if sys.argv[15] <> "#":
                cause = sys.argv[15]
        
        if len(sys.argv) > 16:
            if sys.argv[16] <> "#":
                traitement = sys.argv[16]
        
        if len(sys.argv) > 17:
            if sys.argv[17] <> "#":
                resp_corr = sys.argv[17].split(":")[0]
        
        if len(sys.argv) > 18:
            if sys.argv[18] <> "#":
                echeance_init = sys.argv[18]
        
        if len(sys.argv) > 19:
            if sys.argv[19] <> "#":
                suivi_trait = sys.argv[19]
        
        if len(sys.argv) > 20:
            if sys.argv[20] <> "#":
                resp_suivi = sys.argv[20].split(":")[0]
        
        if len(sys.argv) > 21:
            if sys.argv[21] <> "#":
                date_traitement = sys.argv[21]
        
        if len(sys.argv) > 22:
            if sys.argv[22] <> "#":
                date_fermeture = sys.argv[22]
        
        if len(sys.argv) > 23:
            lien_nc = (sys.argv[23].replace(";",",")).replace("'","")
       
        #Définir l'objet de création d'une nouvelle non-conformité dans SIB.
        oCreerNonConformitePlus = CreerNonConformitePlus()
        
        #Valider les paramètres obligatoires
        oCreerNonConformitePlus.validerParamObligatoire(env,ty_produit,decoupage,attribut,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe)
        
        #Exécuter le traitement de création d'une nouvelle non-conformité dans SIB.
        oCreerNonConformitePlus.executer(env,ty_produit,decoupage,attribut,titre,titre_an,nom_source,ty_nc,origine_nc,ty_trait_nc,descr,resp_descr,date_saisie,doc_connexe,cause,traitement,resp_corr,echeance_init,suivi_trait,resp_suivi,date_traitement,date_fermeture,lien_nc)   

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