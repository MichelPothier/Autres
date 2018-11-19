#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerErratumNonConformite.py
# Auteur    : Michel Pothier
# Date      : 6 janvier 2015

"""
    Application qui permet de cr�er un Erratum pour un num�ro de non-conformit� dans SIB.

    Un seul Erratum est permis pour un num�ro de non-conformit�.    
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    no_nc           OB      Num�ro de non-conformit� pour lequel on veut ajouter un Erratum.
                            d�faut = 
    desc_fr         OB      La description en fran�ais de l'Erratum pour la non-conformit�.
                            d�faut = 
    desc_an         OB      La description en anglais de l'Erratum pour la non-conformit�.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        CreerErratumNonConformite.py env no_nc desc_fr desc_an

    Exemple:
        CreerErratumNonConformite.py SIB_PRO 03645 'Description en fran�ais de l'erratum' 'Description en anglais de l'erratum'

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerErratumNonConformite.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerErratumNonConformite(object):
#*******************************************************************************************
    """
    Permet de cr�er un Erratum pour un num�ro de non-conformit� dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'un erratum pour un num�ro de non-conformit� dans SIB.
        
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
    def validerParamObligatoire(self,env,no_nc,desc_fr,desc_an):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� pour lequel on veut ajouter un Erratum.
        desc_fr         : La description en fran�ais de l'Erratum pour la non-conformit�.
        desc_an         : La description en anglais de l'Erratum pour la non-conformit�.
        
        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(no_nc) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'no_nc')
        
        if (len(desc_fr) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'desc_fr')
        
        if (len(desc_an) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'desc_an')
 
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,no_nc,desc_fr,desc_an):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'un erratum pour un num�ro de non-conformit� dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� pour lequel on veut ajouter un Erratum.
        desc_fr         : La description en fran�ais de l'Erratum pour la non-conformit�.
        desc_an         : La description en anglais de l'Erratum pour la non-conformit�.
        
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
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS' ou 'ISO-RQNC'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='G-SYS' OR CD_GRP='ISO-RQNC')"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS ou ISO-RQNC
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS' ou 'ISO-RQNC'")
        
        #Valider le num�ro de la non-conformit�
        arcpy.AddMessage("- Valider le num�ro de non-conformit�")
        sql = "SELECT NO_NC FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if len(resultat) == 0:
            #Retourner une exception
            raise Exception("Le num�ro de non-conformit� '" + resultat[0][0] + "' est absent")
        
        #Valider si l'erratum est d�j� pr�sent
        arcpy.AddMessage("- Valider la pr�sence du erratum")
        sql = "SELECT DESCR FROM F702_ER WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if len(resultat) > 0:
            #Retourner une exception
            raise Exception("Le erratum est d�j� pr�sent : " + resultat[0][0])
        
        #V�rifier si la longueur est respect�e
        desc_fr = unicode(desc_fr, "utf-8")
        if len(desc_fr) > 4000:
            #Retourner une exception
            raise Exception("La longueur du param�tre 'desc_fr' d�passe 4000 catact�tes, longueur=" + str(len(desc_fr)))
        
        #V�rifier si la longueur est respect�e
        desc_an = unicode(desc_an, "utf-8")
        if len(desc_an) > 4000:
            #Retourner une exception
            raise Exception("La longueur du param�tre 'desc_an' d�passe 4000 catact�tes, longueur=" + str(len(desc_an)))
        
        #Cr�er le erratum du num�ro de non-conformit�
        arcpy.AddMessage("- Cr�er un erratum pour le num�ro de non-conformit�")
        sql = "INSERT INTO F702_ER VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,P0G03_UTL.PU_HORODATEUR,'" + no_nc + "','" + desc_fr.replace("'", "''") + "','" + desc_an.replace("'", "''") + "')"
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
        env     = "SIB_PRO"
        no_nc   = ""
        desc_fr = ""
        desc_an = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            desc_fr = sys.argv[3]
         
        if len(sys.argv) > 4:
            desc_an = sys.argv[4]
        
        #D�finir l'objet de cr�ation d'un erratum pour un num�ro de non-conformit� dans SIB.
        oCreerErratumNonConformite = CreerErratumNonConformite()
        
        #Valider les param�tres obligatoires
        oCreerErratumNonConformite.validerParamObligatoire(env,no_nc,desc_fr,desc_an)
        
        #Ex�cuter le traitement de cr�ation d'un erratum pour un num�ro de non-conformit� dans SIB.
        oCreerErratumNonConformite.executer(env,no_nc,desc_fr,desc_an)   
        
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