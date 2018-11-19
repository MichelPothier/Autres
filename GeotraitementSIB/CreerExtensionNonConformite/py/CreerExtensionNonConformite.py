#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerExtensionNonConformite.py
# Auteur    : Michel Pothier
# Date      : 6 janvier 2015

"""
    Application qui permet de cr�er une extension pour un num�ro de non-conformit� dans SIB.

    Plusieurs extensions sont permises pour un num�ro de non-conformit�.    
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    no_nc           OB      Num�ro de non-conformit� pour lequel on veut cr�er une extension.
                            d�faut = 
    date_ech        OB      La date d'�ch�ance de l'extension de la non-conformit�.
                            d�faut = 
    resp_ech        OB      Nom de la personne responsable de cette extension de non-conformit�.
                            d�faut = <Nom de la personne ayant inscrit cette extension>
    note            OB      Note explicative pour cette extension de non-conformit�.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerExtensionNonConformite(object):
#*******************************************************************************************
    """
    Permet de cr�er une extension pour un num�ro de non-conformit� dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'une extension pour un num�ro de non-conformit� dans SIB.
        
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
    def validerParamObligatoire(self,env,no_nc,date_ech,resp_ech,note):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� pour lequel on veut ajouter une extension.
        date_ech        : La date d'�ch�ance de l'extension de la non-conformit�.
        resp_ech        : Nom de la personne responsable de cette extension de non-conformit�.
        note            : Note explicative pour cette extension de non-conformit�.
        
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
        
        if (len(date_ech) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'date_ech')
        
        if (len(resp_ech) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'resp_ech')
        
        if (len(note) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'note')
 
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,no_nc,date_ech,resp_ech,note):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de cr�ation d'une extension pour un num�ro de non-conformit� dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement
        no_nc           : Num�ro de non-conformit� pour lequel on veut ajouter une extension.
        date_ech        : La date d'�ch�ance de l'extension de la non-conformit�.
        resp_ech        : Nom de la personne responsable de cette extension de non-conformit�.
        note            : Note explicative pour cette extension de non-conformit�.
        
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
        
        #D�finition du format de la date
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
        
        #Valider la date d'�ch�ance initiale
        arcpy.AddMessage("- Valider la date d'�ch�ance initiale")
        date = datetime.datetime.strptime(date_ech, '%Y-%m-%d')
        sql = "SELECT ECHEANCE_INIT FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if resultat:
            #V�rifier le r�sultat
            if resultat[0][0] <> None:
                #Comparer les dates d'�ch�ance
                if date < resultat[0][0]:
                    #Retourner une exception
                    raise Exception("La date d'�ch�ance est plus petite que celle initialement : " + date_ech + " < " + str(resultat[0][0]))
        
        #Valider la date d'�ch�ance d'extension
        arcpy.AddMessage("- Valider la date d'�ch�ance d'extension")
        sql = "SELECT DATE_ECH FROM F703_EX WHERE NO_ENREG='" + no_nc + "' AND TYPE_ISO='NC' ORDER BY DATE_ECH DESC"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if resultat:
            #Comparer les dates d'�ch�ance
            if date <= resultat[0][0]:
                #Retourner une exception
                raise Exception("La date d'�ch�ance est plus petite ou �gale � la derni�re extension : " + date_ech + " < " + str(resultat[0][0]))
        
        #V�rifier si la longueur est respect�e
        note = unicode(note, "utf-8")
        if len(note) > 500:
            #Retourner une exception
            raise Exception("La longueur de la note d�passe 500 catact�tes, longueur=" + str(len(note)))
        
        #Cr�er une extension du num�ro de non-conformit�
        arcpy.AddMessage("- Cr�er une extension pour le num�ro de non-conformit�")
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
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env      = "SIB_PRO"
        no_nc    = ""
        date_ech = ""
        resp_ech = ""
        note     = ""
        
        #extraction des param�tres d'ex�cution
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
        
        #D�finir l'objet de cr�ation d'une extension pour un num�ro de non-conformit� dans SIB.
        oCreerExtensionNonConformite = CreerExtensionNonConformite()
        
        #Valider les param�tres obligatoires
        oCreerExtensionNonConformite.validerParamObligatoire(env,no_nc,date_ech,resp_ech,note)
        
        #Ex�cuter le traitement de cr�ation d'une extension pour un num�ro de non-conformit� dans SIB.
        oCreerExtensionNonConformite.executer(env,no_nc,date_ech,resp_ech,note)   
        
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