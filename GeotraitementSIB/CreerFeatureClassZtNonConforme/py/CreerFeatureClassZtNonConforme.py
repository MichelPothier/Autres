#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : CreerFeatureClassZtNonConforme.py
# Auteur    : Michel Pothier
# Date      : 15 d�cembre 2014

"""
    Application qui permet cr�er une FeatureClass contenant les ZT de non-conformit� et le num�ro de la ZT_ID.
    
    ATTENTION : Si aucun �l�ment n'est s�lectionn� dans une classe, seule la classe sera identifi� dans SIB
    
    Param�tres d'entr�e:
    --------------------
        env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    d�faut = SIB_PRO
        nomFeatureClassZT   OB      Nom de la FeatureClass des ZT de non-conformit� � cr�er.
                                    d�faut = "ZT_NON_CONFORME"
        nomAttributZT       OB      Nom de l'attribut du num�ro de ZT_ID.
                                    d�faut = "ZT_ID"
        nomAttributNC       OB      Nom de l'attribut du num�ro de non-conformit�.
                                    d�faut = "NO_NC"
    
    Param�tres de sortie:
    ---------------------
        FeatureClassZT          : FeatureClass contenant les num�ros de ZT_ID et les g�om�tries des ZT.
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du r�sultat de l'ex�cution du programme.
                                  (Ex: 0=Succ�s, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 
    
    Usage:
        CreerFeatureClassZtNonConforme.py env nomFeatureClassZT nomAttributZT nomAttributNC
    
    Exemple:
        CreerFeatureClassZtNonConforme.py SIB_PRO "ZT NON-CONFORME" "ZT_ID" "NO_NC"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerFeatureClassZtNonConforme.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, traceback

#Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class CreerFeatureClassZtNonConforme:
#*******************************************************************************************
    """
    Permet de cr�er une FeatureClass contenant les ZT de non-conformit� et le num�ro de la ZT_ID.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement d'identification des �l�ments non-conformes.
        
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
    def validerParamObligatoire(self, env, nomFeatureClassZT, nomAttributZT, nomAttributNC):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        nomFeatureClassZT   : Nom de la FeatureClass des ZT de non-conformit� � cr�er.
        nomAttributZT       : Nom de l'attribut du num�ro de ZT_ID.
        nomAttributNC       : Nom de l'attribut du num�ro de non-conformit�.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """

        #Valider la pr�sence de l'environnement
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')
        
        #Valider la pr�sence du nomFeatureClassZT
        if (len(nomFeatureClassZT) == 0):
            raise Exception ('Param�tre obligatoire manquant: nomFeatureClassZT')
        
        #Valider la pr�sence du nomAttributZT
        if (len(nomAttributZT) == 0):
            raise Exception ('Param�tre obligatoire manquant: nomAttributZT')
        
        #Valider la pr�sence du nomAttributNC
        if (len(nomAttributNC) == 0):
            raise Exception ('Param�tre obligatoire manquant: nomAttributNC')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, nomFeatureClassZT, nomAttributZT, nomAttributNC):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traitement de cr�ation d'une FeatureClass contenant les ZT de non-conformit� et le num�ro de la ZT_ID.
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        nomFeatureClassZT   : Nom de la FeatureClass des ZT de non-conformit� � cr�er.
        nomAttributZT       : Nom de l'attribut du num�ro de ZT_ID.
        nomAttributNC       : Nom de l'attribut du num�ro de non-conformit�.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Cr�er la r�f�rence spatiale pour "GCS_North_American_1983_CSRS"
        sr = arcpy.SpatialReference(4617)
        
        #Cr�er la FeatureClass de ZT
        arcpy.AddMessage("- Cr�ation de la FeatureClass des ZT de non-conformit�")
        featureClassZT = arcpy.CreateFeatureclass_management("in_memory", nomFeatureClassZT, "POLYGON", spatial_reference=sr)
        
        #Ajouter l'attribut du num�ro de ZT_ID
        arcpy.AddMessage("- Ajout de l'attribut de " + nomAttributZT + " dans la FeatureClass des ZT de non-conformit�")
        arcpy.management.AddField(featureClassZT, nomAttributZT, "TEXT", field_length=64)
        
        #Ajouter l'attribut du num�ro de NO_NC
        arcpy.AddMessage("- Ajout de l'attribut de " + nomAttributNC + " dans la FeatureClass des ZT de non-conformit�")
        arcpy.management.AddField(featureClassZT, nomAttributNC, "TEXT", field_length=5)
        
        #Cr�er le curseur pour ajouter les �l�ments dans la FeatureClass
        cursor = arcpy.da.InsertCursor(featureClassZT, [nomAttributNC, nomAttributZT, "SHAPE@WKT"])
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Requ�te dans SIB afin de valider le num�ro de non-conformit�
        arcpy.AddMessage("- Extraction des ZT de non-conformit�")
        sql = "SELECT NO_NC,ZT_ID,SHAPE_WKT FROM F710_ZT"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        
        #Traiter tous les ZT non-conformes
        for zt in resultat:
            #Extraire le ZT_ID
            no_nc = zt[0]
            
            #Extraire le ZT_ID
            zt_id = zt[1]
            
            #Extraire la g�om�trie en WKT
            shape_wkt = zt[2].read()
            
            #Afficher le ZT_ID � ins�rer
            arcpy.AddMessage("  ZT_ID=" + zt_id)
            
            #Ins�rer l'�l�ment dans la FeatureClass
            cursor.insertRow([no_nc, zt_id, shape_wkt])
        
        #Accepter les ajouts en d�truisant le curseur
        arcpy.AddMessage("- Accepter les modifications")
        del cursor
        
        #Sortie normale pour une ex�cution r�ussie
        self.CompteSib.FermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB
        
        #Sortir
        return featureClassZT

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env                 = "SIB_PRO"
        nomFeatureClassZT   = ""
        nomAttributZT       = ""
        nomAttributNC       = ""
        featureClassZT      = ""
        
        #Extraction des param�tres d'ex�cution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            nomFeatureClassZT = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            nomAttributZT = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            nomAttributNC = sys.argv[4].upper()
        
        #Instanciation de la classe de cr�ation d'une FeatureClass contenant les ZT de non-conformit� et le num�ro de la ZT_ID.
        oCreerFeatureClassZtNonConforme = CreerFeatureClassZtNonConforme()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oCreerFeatureClassZtNonConforme.validerParamObligatoire(env, nomFeatureClassZT, nomAttributZT, nomAttributNC)
        
        #Ex�cuter le traitement de cr�ation d'une FeatureClass contenant les ZT de non-conformit� et le num�ro de la ZT_ID.
        arcpy.AddMessage("- Ex�cuter la cr�ation d'une FeatureClass de ZT non-conforme.")
        featureClassZT = oCreerFeatureClassZtNonConforme.executer(env, nomFeatureClassZT, nomAttributZT, nomAttributNC)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Retourner la FeatureClass des ZT non-conformes
        arcpy.SetParameterAsText(4, featureClassZT)
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Retourner la FeatureClass des ZT non-conformes
    arcpy.SetParameterAsText(4, featureClassZT)
    #Sortir sans code d'erreur
    sys.exit(0)