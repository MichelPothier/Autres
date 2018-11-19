#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : FermerSelectdNonConformiteDonneesInsitu.py
# Auteur    : Michel Pothier
# Date      : 19 septembre 2016

"""
Outil qui permet de fermer une sélection d'identifiants d'une non-conformité sur les données géographique après avoir
effectué une correction sur ces dernières directement dans la BD (INSITU)
et estampiller les métadonnées associées aux données géographiques non-conformes.

La fermeture d'une non-conformité est réalisée seulement après avoir effectué une correction INSITU dans les données de la BDG.
-Vérifier si la non-conformité existe.
-Extraire la liste des jeux de données selon la no de non-conformité.
-Pour chaque jeu de données:
    -Ajouter une étiquette de description du processus utilisé.
    -Le numéro de version des métadonnées est incrémenté.
    -Changer la date des métadonnées.
    -L'intervalle d'’édition-version est fermée selon le numéro d'édition et version du jeu courant. 
    -Si toutes les intervalles de fin sont inscrits, alors la date de fin de traitement est inscrite pour permettre de fermer la non-conformité. 
    -Le responsable de l'’équipe Qualité des données reçoit alors un courriel lui indiquant la fin des travaux.

Attention : Seule les non-conformités de type DM et dont le type de traitement est SP% ou SM% peuvent être traitées par ce programme.

Paramètres:
-----------
env             : Type d'environnement.
no_nc           : Numéro de la non-conformité à fermer.
decoupage       : FeatureLayer contenant une sélection d'éléments de découpage représentant des identifiants de la non-conformité à fermer.
attribut        : Nom de l'attribut du FeatureLayer contenant l'identifiant de découpage à fermer.
no_tache        : Numéro de la tâche Alloy qui correspond à une demande effectuée par un usager.
procdesc        : Étiquette qui correspond à la description du processus utilisée pour corriger la non-conformité.

Classe:
-------
 Nom                            Description
 -----------------------------  --------------------------------------------------------------------
 FermerSelectdNonConformiteDonneesInsitu     Fermer une non-conformité sur les données géographique.
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FermerSelectdNonConformiteDonneesInsitu.py 2159 2018-07-12 21:18:17Z mpothier $"
#********************************************************************************************

# Importation des modules publics
import os, sys, arcpy, datetime, traceback

# Importation des modules privés
import  EnvoyerCourriel, CompteSib

#*******************************************************************************************
class FermerSelectdNonConformiteDonneesInsitu(object):
#*******************************************************************************************
    """ Fermer une non-conformité sur les données géographique.
    
    Retour:
        ErrorLevel  Integer  Code d'erreur de retour sur le système (Ex: 0=Succès, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """Initialisation du traitement de fermeture d'une non-conformité.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        #Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, decoupage, attribut, no_tache, procdesc):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de fermeture d'une non-conformité à partir d'une sélection d'éléments de découpage.
        
        Paramètres:
        -----------
        env             : Type d'environnement.
        no_nc           : Numéro de la non-conformité à fermer.
        decoupage       : FeatureLayer contenant une sélection d'éléments de découpage représentant des identifiants de la non-conformité à fermer.
        attribut        : Nom de l'attribut contenant l'identifiant de découpage à fermer.
        no_tache        : Numéro de la tâche Alloy qui correspond à une demande effectuée par un usager.
        procdesc        : Étiquette qui correspond à la description du processus utilisé pour corriger la non-conformité.
        
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
        
        #-----------------------------------
        #Extraction de l'information de la non-conformité
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction de l'information de la non-conformité : " + str(no_nc))
        sql = "SELECT DATE_FERMETURE, DATE_TRAITEMENT, TY_NC, TY_TRAIT_NC, RESP_DESCR, RESP_CORR, RESP_SUIVI FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        #Exécuter la requête SQL
        resultat = self.Sib.requeteSib(sql)
        #Vérifier la présence du paramètre
        if (len(resultat) == 0):
            raise Exception("Numéro de non-conformité invalide : %s" %no_nc)
        #Vérifier si la non-conformité est fermée
        if resultat[0][0] <> None:
            raise Exception("La non-conformité est déjà fermée : date_fermeture=" + str(resultat[0][0]))
        #Vérifier si la non-conformité a déjà été traitée
        dateTraitement = resultat[0][1]
        if dateTraitement <> None:
            arcpy.AddWarning("La non-conformité a déjà été traitée : date_traitement=" + str(dateTraitement))
        #Vérifier si la non-conformité est de type DM
        if resultat[0][2] <> "DM":
            raise Exception("Le type de non-conformité n'est pas 'DM' : TY_NC=" + str(resultat[0][2]))
        #Vérifier si la non-conformité a le traitement SP ou SM
        if "SP" not in resultat[0][3] and "SM" not in resultat[0][3]:
            raise Exception("Le type de traitement de non-conformité n'est pas 'SP%' ou 'SM%' : TY_TRAIT_NC=" + str(resultat[0][3]))
        #Conserver l'information de la non-conformité
        resp_descr = resultat[0][4]
        resp_corr = resultat[0][5]
        resp_suivi = resultat[0][6]
        #Afficher les valeurs
        arcpy.AddMessage(str(resultat))
        
        #-----------------------------------
        #Extraction des identifiants sélectionnés
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des identifiants sélectionnés ...")
        #Extraire le nombre d'éléments sélectionnés
        desc = arcpy.Describe(decoupage)
        listeOid = desc.FIDSet
        #Vérifier la présence du paramètre
        if len(listeOid) == 0:
            raise Exception("Aucun élément n'a été sélectionné dans le Layer de découpage.")
        
        #Créer la liste  triée des identifiants sélectionnés
        listeId = list(set("{0}".format(row[0]) for row in arcpy.da.SearchCursor(decoupage, [attribut])))
        listeId.sort()
        total = len(listeId)
        #Afficher le nombre d'éléments sélectionnés
        arcpy.AddWarning("Nombre d'éléments sélectionnés : " + str(total))
        
        #-----------------------------------
        #Initialiser les compteurs
        cpt = 0
        #Traiter tous les identifiants sélectionnés
        for id in listeId:
            #Afficher les valeurs
            cpt = cpt + 1
            arcpy.AddMessage(" ")
            arcpy.AddMessage(str(cpt) + "/" + str(total) + " : " + str(id))
            
            #-----------------------------------
            #Extraction de l'identifiant de la non-conformité traité
            arcpy.AddMessage("  -Valider l'identifiant : " + id)
            sql = "SELECT TY_PRODUIT, IDENTIFIANT, ED_DEBUT, VER_DEBUT, ED_FIN, VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' AND IDENTIFIANT='" + id + "'"
            arcpy.AddMessage("  " + sql)
            #Exécuter la requête
            resultat = self.Sib.requeteSib(sql)
            #Vérifier la présence de l'identifiant
            if resultat:
                #Définir les variables
                ty_produit = resultat[0][0]    #ty_produit
                identifiant = resultat[0][1]   #identifiant
                ed_debut = resultat[0][2]      #ed_debut
                ver_debut = resultat[0][3]     #ver_debut
                ed_fin = resultat[0][4]        #ed_fin
                ver_fin = resultat[0][5]       #ver_fin
                
                #Vérifier si l'intervalle de fin n'est pas traitée
                if ed_fin == 99999:
                    #Traiter l'identifiant de non-conformité
                    self.traiterIdentifiant(no_nc, no_tache, procdesc, ty_produit, identifiant, ed_debut, ver_debut, ed_fin, ver_fin)
                
                #si l'intervalle de fin est déjà traitée
                else:
                    #Afficher un avertissement
                    arcpy.AddWarning("  L'intervalle de fin est déjà traitée")
             #Si aucun résultat
            else:
                #Retourner une erreur
                arcpy.AddError("  L'identifiant n'est pas associé à la non-conformité : " + id) 
        
        #-----------------------------------
        #Vérifier si tous les identifiants de la NC sont fermés        
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des identifiants non-fermés : " + str(no_nc))
        sql = "SELECT IDENTIFIANT FROM F705_PR WHERE NO_NC='" + no_nc + "' AND ED_FIN=99999 ORDER BY IDENTIFIANT"
        arcpy.AddMessage(sql)
        #Exécuter la requête
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if resultat:
            #Afficher les identifiants non-fermés
            arcpy.AddWarning("Les identifiants suivants ne sont pas encore fermés : " + str(resultat))
            
        #Si aucun résultat
        else:
            #Vérifier si la non-conformité ne possède déjà pas de date de traitement
            if dateTraitement == None:
                #-----------------------------------
                #Mettre à jour la date de traitement
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Mise à jour de la date de traitement")
                sql = "UPDATE F702_NC SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, DATE_TRAITEMENT=SYSDATE WHERE NO_NC='" + no_nc + "'"
                arcpy.AddWarning(sql)
                self.Sib.execute(sql)
            
            #Envoyer les courriels aux responsables
            arcpy.AddMessage(" ")
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
        
        #-----------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddWarning(sql)
        self.Sib.execute(sql)
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        self.Sib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

    #-------------------------------------------------------------------------------------
    def traiterIdentifiant(self, no_nc, no_tache, procdesc, ty_produit, identifiant, ed_debut, ver_debut, ed_fin, ver_fin):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de fermeture pour un identifiant de la non-conformité.
        
        Paramètres:
        -----------
        no_nc           : Numéro de la non-conformité à fermer.
        no_tache        : Numéro de la tâche Alloy qui correspond à une demande effectuée par un usager.
        procdesc        : Étiquette qui correspond à la description du processus utilisé pour corriger la non-conformité.
        ty_produit      : Type de produit traité.
        identifiant     : Identifiant de découpage traité.
        ed_debut        : Édition de début de la non-conformité.
        ver_debut       : Version de début de la non-conformité.
        ed_fin          : Édition de fin de la non-conformité.
        ver_fin         : Version de fin de la non-conformité.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : Résultat de la requête SIB.
        ed_cour         : Édition courante du jeu de données.
        ver_cour        : Version courante du jeu de données.
        """
        
        #-----------------------------------
        #Valider le Proc/Desc
        arcpy.AddMessage("  -Valider le Proc/Desc : " + procdesc)
        sql = "SELECT * FROM F235_VP WHERE TY_PRODUIT='" + ty_produit + "' AND CD_CHAMP='procdesc' AND CD_VALEUR='" + procdesc + "'"
        arcpy.AddMessage("  " + sql)
        #Exécuter la requête
        resultat = self.Sib.requeteSib(sql)
        #Vérifier la présence du paramètre
        if (len(resultat) == 0):
            #Retourner une erreur
            raise Exception("La description de la procédure utilisée pour le produit " + ty_produit + " est invalide!")

        #-----------------------------------
        #Créer la requête SQL (pour extraire l'édition et la version du jeu courant ainsi que la version des métadonnées)
        arcpy.AddMessage("  -Extraire l'édition et la version du jeu courant ...")
        sql = "SELECT ED, VER, VER_META FROM F235_PR WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND JEU_COUR=1"
        arcpy.AddMessage("  " + sql)
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
        arcpy.AddMessage("  " + str(resultat2))

        #-----------------------------------
        #Extraire le no_seq du procDesc
        arcpy.AddMessage("  -Extraire le NO_SEQ du Proc/Desc ...")
        sql = "SELECT MAX(NO_SEQ) + 1 FROM F235_PS WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed_cour) + " AND VER=" + str(ver_cour)
        arcpy.AddMessage("  " + sql)
        #Exécuter la requête SQL
        resultat3 = self.Sib.requeteSib(sql)
        #Définir le NO_SEQ
        no_seq = str(resultat3[0][0])
        
        #-----------------------------------
        #Créer l'étiquette du Proc/Desc
        arcpy.AddMessage("  -Créer l'étiquette du Proc/Desc dans les métadonnées ...")
        sql = "INSERT INTO F235_PS Values (P0G03_UTL.PU_HORODATEUR, '" + no_tache + "', SYSDATE, SYSDATE, '" + ty_produit + "', '" + identifiant + "', " + str(ed_cour) + ", " + str(ver_cour) + ", " + no_seq + ", '{$PS$" + procdesc + "}', TO_CHAR(SYSDATE, 'YYYYMMDD'), 0)"
        arcpy.AddWarning("  " + sql)
        #Exécuter la commande
        self.Sib.execute(sql)
        
        #-----------------------------------
        #Modifier la date des métadonnées
        arcpy.AddMessage("  -Modifier la date des métadonnées ...")
        sql = "UPDATE F235_MR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, DT_METADATA=TO_CHAR(SYSDATE, 'YYYYMMDD') WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed_cour) + " AND VER=" + str(ver_cour)
        arcpy.AddWarning("  " + sql)
        #Exécuter la commande
        self.Sib.execute(sql)
        
        #-----------------------------------
        #Incrémenter la version des métadonnées
        ver_meta = ver_meta + 1
        #Créer la commande SQL pour modifier la version des métadonnées
        arcpy.AddMessage("  -Modifier la version des métadonnées ...")
        sql = "UPDATE F235_PR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, VER_META=" + str(ver_meta) + " WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND JEU_COUR=1"
        arcpy.AddWarning("  " + sql)
        #Exécuter la commande
        self.Sib.execute(sql)
        
        #-----------------------------------
        #Modifier l'édition et version de fin
        arcpy.AddMessage("  -Modifier l'édition et version de fin de non-conformité ...")
        sql = "UPDATE F705_PR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, ED_FIN=" + str(ed_cour) + ", VER_FIN=" + str(ver_cour) + " WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
        arcpy.AddWarning("  " + sql)
        #Exécuter la commande
        self.Sib.execute(sql)
        
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
        decoupage = ""
        attribut = "DATASET_NAME"
        no_tache = ""
        procdesc = ""
        
        # Lecture des paramètres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            decoupage = sys.argv[3]
        
        if len(sys.argv) > 4:
            attribut = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            no_tache = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            procdesc = sys.argv[6].upper()
        
        # Définir l'objet de fermeture d'une non-conformité de correction des données géographique
        oFermerSelectdNonConformiteDonneesInsitu = FermerSelectdNonConformiteDonneesInsitu()
        
        # Exécuter le traitement de fermeture d'une non-conformité de correction des données géographique
        oFermerSelectdNonConformiteDonneesInsitu.executer(env, no_nc, decoupage, attribut, no_tache, procdesc)
    
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