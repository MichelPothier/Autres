#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : FermerIntervalleFinNonConformiteInvalide.py
# Auteur    : Michel Pothier
# Date      : 22 août 2017

"""
Outil qui permet de fermer les intervalles de fin pour les non-conformités qui possèdent une date de fermeture et pour lesquels aucune édition et version de fin sont présente.

-L'intervalle d?'édition-version d'un identifiant est fermée selon le numéro d'édition et version de début. 

Attention : Seules les non-conformités avec une date de fermeture peuvent être traitées par ce programme.

Paramètres d'entrées:
----------------------
env         OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                    Défaut = SIB_PRO
produit     OB      Type de produit des identifiants de non-conformité à fermer.
                    Défaut = 'BDG'
ty_nc       OB      Liste des types de non-conformité à fermer.
                    Le type de non-conformité.
                    •OP : Observation produit
                    •DM : Données modifiées dans la BD
                    •PA : Plainte autre
                    •PP : Plainte produit
                     Ne sont plus utilisés:
                    •ND : Non-disponible
                    •OA : Observation autre
                    •PD : Plainte de distrubution non-active
                    •SQ : Système qualité
                    Défaut = <Selon les non-conformités dont l'intervalle de fin est invalide>
no_nc       OB      Liste des numéros de non-conformité à fermer.
                    Défaut = 
corriger    OP      Indique si on doit corriger.
                    Défaut = false

Paramètres de sortie:
---------------------
Aucun

Valeurs de retour:
------------------
errorLevel  : Code du résultat de l'exécution du programme.
              (Ex: 0=Succès, 1=Erreur)
Usage:
    FermerIntervalleFinNonConformiteInvalide.py env produit no_nc

Exemple:
    FermerIntervalleFinNonConformiteInvalide.py SIB_PRO BDG DM,OP,PP 02997;02888

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FermerIntervalleFinNonConformiteInvalide.py 2135 2017-08-23 13:31:54Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés
import EnvoyerCourriel, CompteSib

#*******************************************************************************************
class FermerIntervalleFinNonConformiteInvalide(object):
#*******************************************************************************************
    """
    Permet de fermer les intervalles de fin pour les non-conformités qui possèdent une date de fermeture
    et pour lesquels aucune édition et version de fin sont présente.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour fermer les intervalles de fin pour les non-conformités qui possèdent une date de fermeture
        et pour lesquels aucune édition et version de fin sont présente.
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion à SIB.
        
        """
        
        #Définir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

        #Initialisation du compteur d'identifiants
        self.nbId = 0
        
        #Initialisation du compteur de modifications
        self.nbModif = 0
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, produit, ty_nc, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        produit     : Type de produit des identifiants de non-conformité à fermer.
        no_nc       : Liste des types de non-conformité à fermer.
        no_nc       : Liste des numéros de non-conformité à fermer.
        
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
        if (len(produit) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'produit')

        #Vérifier la présence du paramètre
        if (len(ty_nc) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'ty_nc')

        #Vérifier la présence du paramètre
        if (len(no_nc) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'no_nc')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, produit, ty_nc, no_nc, corriger):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour fermer les intervalles de fin d'une non-conformité pour des identifiants avec jeux courants.
        
        Paramètres:
        -----------
        env         : Type d'environnement.
        produit     : Type de produit des identifiants de la non-conformité à fermer.
        no_nc       : Liste des types de non-conformité à fermer.
        no_nc       : Liste des numéros de non-conformité à fermer.
        corriger    : Indique si on doit corriger.

        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : Résultat de la requête SIB.
        ed_debut        : Édition de début de la non-conformité.
        ver_debut       : Version de début de la non-conformité.
        ed_max          : Édition maximum de l'identifiant.
        ver_max         : Version maximum de l'identifiant.
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        arcpy.AddMessage("- Connexion à la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        sUsagerBd = self.CompteSib.UsagerBd()
        
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

        #Extraction de l'information de la non-conformité
        arcpy.AddMessage("- Validation du type de produit de la non-conformité : " + produit)
        sql = ("SELECT DISTINCT TY_PRODUIT"
               "  FROM F705_PR"
               " WHERE TY_PRODUIT='" + produit + "' AND ED_FIN=99999")
        arcpy.AddMessage(sql)
        #Exécuter la requête SQL
        resultat = self.Sib.requeteSib(sql)
        #Vérifier la présence du paramètre
        if (len(resultat) == 0):
            arcpy.AddMessage(sql)
            raise Exception("Aucune non-conformité n'est présente pour ce produit : %s" %produit)
        
        #Traiter tous les non-conformités
        for item in no_nc.split(","):
            #Définir le numéro de non-conformité
            nc = item.split(" ")[0]
            
            #Traiter la non-conformité
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Traitement de la non-conformité : " + nc + " ...")
            sql = ("SELECT PR.IDENTIFIANT, PR.ED_DEBUT, PR.VER_DEBUT"
                   "  FROM F702_NC NC, F705_PR PR"
                   " WHERE PR.TY_PRODUIT='" + produit + "' AND NC.NO_NC='" + nc + "' AND NC.NO_NC=PR.NO_NC"
                   "   AND PR.ED_FIN=99999 AND NC.DATE_TRAITEMENT IS NOT NULL")
            arcpy.AddMessage(sql)
            #Exécuter la requête SQL
            resultat = self.Sib.requeteSib(sql)

            #Traiter tous les identifiants
            for identifiant in resultat:
                #Compter les identifiants
                self.nbId = self.nbId + 1

                #Définir les valeurs
                id = identifiant[0]
                ed_debut = str(identifiant[1])
                ver_debut = str(identifiant[2])
                
                #Créer la commande SQL pour modifier l'édition et version de fin
                sql = ("UPDATE F705_PR"
                       "   SET ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, ED_FIN=" + ed_debut + ", VER_FIN=" + ver_debut + " "
                       " WHERE NO_NC='" + nc + "' AND TY_PRODUIT='" + produit + "' AND IDENTIFIANT='" + id + "'")
                arcpy.AddMessage(sql + ";")
                
                #Vérifier s'il faut corriger
                if corriger:
                    #Exécuter la commande
                    self.Sib.execute(sql)
                    #Compter les modifications
                    self.nbModif = self.nbModif + 1
            
            #Afficher le nombre d'identifiant
            arcpy.AddWarning("Nombre d'identifiants : " + str(len(resultat)))
                
        #Afficher le nombre de modifications effectuées
        arcpy.AddMessage(" ")
        arcpy.AddWarning("Nombre total d'identifiants : " + str(self.nbId))
        arcpy.AddWarning("Nombre total de modifications effectuées : " + str(self.nbModif))
        
        #Accepter les modifications si on corrige
        if corriger:
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Accepter les modifications")
            sql = "COMMIT"
            arcpy.AddMessage(sql + ";")
            self.Sib.execute(sql)
        
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
        produit = 'BDG'
        ty_nc = ""
        no_nc = ""
        corriger = False
        
        # Lecture des paramètres
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()

        if len(sys.argv) > 2:
            produit = sys.argv[2].upper()

        if len(sys.argv) > 3:
            ty_nc = sys.argv[3].upper().replace(";",",").replace("'","")

        if len(sys.argv) > 4:
            no_nc = sys.argv[4].replace(";",",").replace("'","")
            
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                corriger = sys.argv[5].upper() == "TRUE"
        
        #Définir l'objet pour fermer les intervalles de fin pour les non-conformités qui possèdent une date de fermeture
        oFermerIntervalleFinNonConformiteInvalide = FermerIntervalleFinNonConformiteInvalide()
        
        #Valider les paramètres obligatoires
        oFermerIntervalleFinNonConformiteInvalide.validerParamObligatoire(env, produit, ty_nc, no_nc)
        
        #Exécuter le traitement pour fermer les intervalles pour les non-conformités qui possèdent une date de fermeture
        oFermerIntervalleFinNonConformiteInvalide.executer(env, produit, ty_nc, no_nc, corriger)
    
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