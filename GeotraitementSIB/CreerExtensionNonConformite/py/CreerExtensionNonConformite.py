#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerExtensionNonConformite.py
# Auteur    : Michel Pothier
# Date      : 6 janvier 2015

"""
    Application qui permet de créer une extension pour un numéro de non-conformité dans SIB.

    Plusieurs extensions sont permises pour un numéro de non-conformité.    
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    no_nc           OB      Numéro de non-conformité pour lequel on veut créer une extension.
                            défaut = 
    date_ech        OB      La date d'échéance de l'extension de la non-conformité.
                            défaut = 
    resp_ech        OB      Nom de la personne responsable de cette extension de non-conformité.
                            défaut = <Nom de la personne ayant inscrit cette extension>
    note            OB      Note explicative pour cette extension de non-conformité.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CreerExtensionNonConformite.py env no_nc date_ech resp_ech note

    Exemple:
        CreerExtensionNonConformite.py SIB_PRO 03645 2015-01-16 MPOTHIER 'Note explication de l'extension'

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerExtensionNonConformite.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerExtensionNonConformite(object):
#*******************************************************************************************
    """
    Permet de créer une extension pour un numéro de non-conformité dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de création d'une extension pour un numéro de non-conformité dans SIB.
        
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
    def validerParamObligatoire(self,env,no_nc,date_ech,resp_ech,note):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité pour lequel on veut ajouter une extension.
        date_ech        : La date d'échéance de l'extension de la non-conformité.
        resp_ech        : Nom de la personne responsable de cette extension de non-conformité.
        note            : Note explicative pour cette extension de non-conformité.
        
        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")

        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(no_nc) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'no_nc')
        
        if (len(date_ech) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'date_ech')
        
        if (len(resp_ech) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'resp_ech')
        
        if (len(note) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'note')
 
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,no_nc,date_ech,resp_ech,note):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement de création d'une extension pour un numéro de non-conformité dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement
        no_nc           : Numéro de non-conformité pour lequel on veut ajouter une extension.
        date_ech        : La date d'échéance de l'extension de la non-conformité.
        resp_ech        : Nom de la personne responsable de cette extension de non-conformité.
        note            : Note explicative pour cette extension de non-conformité.
        
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
        
        #Définition du format de la date
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
        
        #Valider le numéro de la non-conformité
        arcpy.AddMessage("- Valider le numéro de non-conformité")
        sql = "SELECT NO_NC FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le numéro de non-conformité '" + resultat[0][0] + "' est absent")
        
        #Valider la date d'échéance initiale
        arcpy.AddMessage("- Valider la date d'échéance initiale")
        date = datetime.datetime.strptime(date_ech, '%Y-%m-%d')
        sql = "SELECT ECHEANCE_INIT FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if resultat:
            #Vérifier le résultat
            if resultat[0][0] <> None:
                #Comparer les dates d'échéance
                if date < resultat[0][0]:
                    #Retourner une exception
                    raise Exception("La date d'échéance est plus petite que celle initialement : " + date_ech + " < " + str(resultat[0][0]))
        
        #Valider la date d'échéance d'extension
        arcpy.AddMessage("- Valider la date d'échéance d'extension")
        sql = "SELECT DATE_ECH FROM F703_EX WHERE NO_ENREG='" + no_nc + "' AND TYPE_ISO='NC' ORDER BY DATE_ECH DESC"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier le résultat
        if resultat:
            #Comparer les dates d'échéance
            if date <= resultat[0][0]:
                #Retourner une exception
                raise Exception("La date d'échéance est plus petite ou égale à la dernière extension : " + date_ech + " < " + str(resultat[0][0]))
        
        #Vérifier si la longueur est respectée
        note = unicode(note, "utf-8")
        if len(note) > 500:
            #Retourner une exception
            raise Exception("La longueur de la note dépasse 500 catactètes, longueur=" + str(len(note)))
        
        #Créer une extension du numéro de non-conformité
        arcpy.AddMessage("- Créer une extension pour le numéro de non-conformité")
        sql = "INSERT INTO F703_EX VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'NC','" + no_nc + "','" + date_ech + "','" + resp_ech + "','" + note.replace("'", "''") + "',P0G03_UTL.PU_HORODATEUR)"
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
        env      = "SIB_PRO"
        no_nc    = ""
        date_ech = ""
        resp_ech = ""
        note     = ""
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            date_ech = sys.argv[3].split(" ")[0]
        
        if len(sys.argv) > 4:
            resp_ech = sys.argv[4].split(":")[0]
        
        if len(sys.argv) > 5:
            note = sys.argv[5]
        
        #Définir l'objet de création d'une extension pour un numéro de non-conformité dans SIB.
        oCreerExtensionNonConformite = CreerExtensionNonConformite()
        
        #Valider les paramètres obligatoires
        oCreerExtensionNonConformite.validerParamObligatoire(env,no_nc,date_ech,resp_ech,note)
        
        #Exécuter le traitement de création d'une extension pour un numéro de non-conformité dans SIB.
        oCreerExtensionNonConformite.executer(env,no_nc,date_ech,resp_ech,note)   
        
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