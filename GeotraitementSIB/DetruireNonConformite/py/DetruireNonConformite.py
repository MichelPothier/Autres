#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : DetruireNonConformite.py
# Auteur    : Michel Pothier
# Date      : 17 juin 2015

"""
    Application qui permet de détruire une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.

    
    Paramètres d'entrée:
    --------------------
    env                OB     Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                              défaut = SIB_PRO
    ty_produit         OB     Liste des types de produits contenant des non-conformités non traitées et non fermées.
                              défaut = <Tous>
                              Exemple:
                              "DNEC:#2:#5" indique qu'il y a 2 numéros de non-conformité non-fermés et 5 identifiants pour le type de produit DNEC.
                              "None:#1:#0" indique qu'il y a 1 numéro de non-conformité non-fermés et 0 identifiant de type de produit inconnu.
    no_nc              OB     Liste des numéros de non-conformité à détruire selon les types de produits spécifiés qui sont non traitées et non fermées.
                              défaut = 
                              Exemple:
                              "NO_NC:TYPE_NC:TY_PRODUIT:#COUNT(IDENTIFIANT):TITRE"
                              "03024:PP:TOPORAMA:#1:Commission de certaines occurrences d'entité Cours d'eau"
                              
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        DetruireNonConformite.py env ty_produit no_nc

    Exemple:
        DetruireNonConformite.py SIB_PRO "DNEC:#2;None:#1"  "03115:PA:None:#1Modifier l'étiquette;02818:PP:DNEC:#45:Erreur de précision;02748:PP:DNEC:#23:Erreur d'élévation"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: DetruireNonConformite.py 10242 2014-07-04 13:54:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class DetruireNonConformite(object):
#*******************************************************************************************
    """
    Permet de détruire une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
    
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour détruire une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        
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
    def validerParamObligatoire(self, env, ty_produit, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement.    
        ty_produit      : Liste des types de produits contenant des non-conformités non traitées et non fermées.
        no_nc           : Liste des numéros de non-conformité à détruire selon les types de produits spécifiés qui sont non traitées et non fermées.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'env')
        
        if (len(ty_produit) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'ty_produit')
        
        if (len(no_nc) == 0):
            raise Exception("- Paramètre obligatoire manquant: %s" %'no_nc')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, ty_produit, no_nc):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour détruire une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        
        Paramètres:
        -----------
        env             : Type d'environnement.    
        ty_produit      : Liste des types de produits contenant des non-conformités non traitées et non fermées.
        no_nc           : Liste des numéros de non-conformité à détruire selon les types de produits spécifiés qui sont non traitées et non fermées.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS' ou 'ISO-RQNC'")
        
        #Traiter tous les types de produit
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider tous les types de produits.")
        for produit in ty_produit.split(";"):
            #Extraire le produit
            produit = produit.split(":")[0]
            #Extraire le type de produit
            sql = ("SELECT TY_PRODUIT"
                   "  FROM (SELECT DISTINCT NVL(PR.TY_PRODUIT,'None') AS TY_PRODUIT"
                   "          FROM F702_NC NC, F705_PR PR"
                   "         WHERE NC.NO_NC=PR.NO_NC(+) AND NC.DATE_FERMETURE IS NULL AND NC.DATE_TRAITEMENT IS NULL)"
                   " WHERE TY_PRODUIT='" + produit + "'")
            resultat = oSib.requeteSib(sql)
            #Vérifier si le ty_produit est absent
            if not resultat:
                #Retourner une exception
                arcpy.AddMessage(sql)
                raise Exception("Le TY_PRODUIT est absent de la table F705_PR : " + produit)
        #Afficher les types de produits
        arcpy.AddMessage(ty_produit)
        
        #Traiter tous les NO_NC à détruire
        for nc in no_nc.split(";"):
            #Afficher le message
            noNc = nc.split(":")[0]
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Destruction du NO_NC : " + nc)
            #Valider si le NO_NC est valide
            sql = "SELECT NO_NC, DATE_FERMETURE, DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + noNc + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier si le NO_NC est absent
            if not resultat:
                #Retourner une exception
                raise Exception("Le NO_NC est absent de la table F702_NC : " + noNc)
            #Vérifier si le NO_NC est fermé ou traité
            if not (str(resultat[0][1]) == "None" and str(resultat[0][2]) == "None"):
                #Retourner une exception
                raise Exception("Le NO_NC est fermé ou traité : " + str(resultat))
            #Afficher les données
            arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
           
            #Détruire la NO_NC dans la table F702_NC
            sql = "SELECT * FROM F702_NC WHERE NO_NC='" + noNc + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
                #Détruire le NO_NC
                sql = "DELETE F702_NC WHERE NO_NC='" + noNc + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            
            #Détruire les identifiants du NO_NC dans la table F705_PR
            sql = "SELECT IDENTIFIANT,TY_PRODUIT,ED_DEBUT,VER_DEBUT,ED_FIN,VER_FIN FROM F705_PR WHERE NO_NC='" + noNc + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données
                #arcpy.AddMessage(str(resultat).replace("), (", "),\n ("))
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
                #Détruire le NO_NC
                sql = "DELETE F705_PR WHERE NO_NC='" + noNc + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            #Si le NO_NC est absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning(" Aucun identifiant n'est présent dans la table F705_PR")
            
            #Détruire la NO_NC dans la table F702_ER (Erratum)
            sql = "SELECT * FROM F702_ER WHERE NO_NC='" + noNc + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
                #Détruire le NO_NC
                sql = "DELETE F702_ER WHERE NO_NC='" + noNc + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            #Si le NO_NC est absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning(" Aucun NO_NC n'est présent dans la table F702_ER")
            
            #Détruire la NO_NC dans la table F703_EX (Extension)
            sql = "SELECT * FROM F703_EX WHERE TYPE_ISO='NC' AND NO_ENREG='" + noNc + "'"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
                #Détruire le NO_NC
                sql = "DELETE F703_EX WHERE TYPE_ISO='NC' AND NO_ENREG='" + noNc + "'"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            #Si le NO_NC est absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning(" Aucun NO_NC n'est présent dans la table F703_EX")
            
            #Détruire la NO_NC dans la table F704_LI (Liaison)
            sql = "SELECT * FROM F704_LI WHERE NO_NC='" + noNc + "' OR (TY_LIEN='NC' and NO_ACTION='" + noNc + "')"
            arcpy.AddMessage(sql)
            resultat = oSib.requeteSib(sql)
            #Vérifier le résultat
            if resultat:
                #Afficher les données
                arcpy.AddWarning(" " + "\n ".join(", ".join(map(lambda x: unicode(x),l)) for l in resultat))
                #Détruire le NO_NC
                sql = "DELETE F704_LI WHERE NO_NC='" + noNc + "' OR (TY_LIEN='NC' and NO_ACTION='" + noNc + "')"
                arcpy.AddMessage(sql)
                oSib.execute(sql)
            #Si le NO_NC est absent
            else:
                #Afficher un message d'absence
                arcpy.AddWarning(" Aucun NO_NC n'est présent dans la table F704_LI")
         
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env              = "SIB_PRO"
        ty_produit       = ""
        no_nc            = ""
        
        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            ty_produit = sys.argv[2]
        
        if len(sys.argv) > 3:
            no_nc = sys.argv[3].replace("'","")
        
        #Définir l'objet pour détruire une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireNonConformite = DetruireNonConformite()
        
        #Valider les paramètres obligatoires
        oDetruireNonConformite.validerParamObligatoire(env, ty_produit, no_nc)
        
        #Exécuter le traitement pour détruire une ou plusieurs non-conformités qui ne possèdent pas de date de traitement et de date de fermeture.
        oDetruireNonConformite.executer(env, ty_produit, no_nc)
        
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