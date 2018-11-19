#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : CreerFeatureClassZtNonConforme.py
# Auteur    : Michel Pothier
# Date      : 15 décembre 2014

"""
    Application qui permet créer une FeatureClass contenant les ZT de non-conformité et le numéro de la ZT_ID.
    
    ATTENTION : Si aucun élément n'est sélectionné dans une classe, seule la classe sera identifié dans SIB
    
    Paramètres d'entrée:
    --------------------
        env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    défaut = SIB_PRO
        nomFeatureClassZT   OB      Nom de la FeatureClass des ZT de non-conformité à créer.
                                    défaut = "ZT_NON_CONFORME"
        nomAttributZT       OB      Nom de l'attribut du numéro de ZT_ID.
                                    défaut = "ZT_ID"
        nomAttributNC       OB      Nom de l'attribut du numéro de non-conformité.
                                    défaut = "NO_NC"
    
    Paramètres de sortie:
    ---------------------
        FeatureClassZT          : FeatureClass contenant les numéros de ZT_ID et les géométries des ZT.
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du résultat de l'exécution du programme.
                                  (Ex: 0=Succès, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 
    
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

#Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class CreerFeatureClassZtNonConforme:
#*******************************************************************************************
    """
    Permet de créer une FeatureClass contenant les ZT de non-conformité et le numéro de la ZT_ID.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement d'identification des éléments non-conformes.
        
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
    def validerParamObligatoire(self, env, nomFeatureClassZT, nomAttributZT, nomAttributNC):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        nomFeatureClassZT   : Nom de la FeatureClass des ZT de non-conformité à créer.
        nomAttributZT       : Nom de l'attribut du numéro de ZT_ID.
        nomAttributNC       : Nom de l'attribut du numéro de non-conformité.
        
        Retour:
        -------
        Exception s'il y a un problème
        """

        #Valider la présence de l'environnement
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')
        
        #Valider la présence du nomFeatureClassZT
        if (len(nomFeatureClassZT) == 0):
            raise Exception ('Paramètre obligatoire manquant: nomFeatureClassZT')
        
        #Valider la présence du nomAttributZT
        if (len(nomAttributZT) == 0):
            raise Exception ('Paramètre obligatoire manquant: nomAttributZT')
        
        #Valider la présence du nomAttributNC
        if (len(nomAttributNC) == 0):
            raise Exception ('Paramètre obligatoire manquant: nomAttributNC')
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, nomFeatureClassZT, nomAttributZT, nomAttributNC):
    #-------------------------------------------------------------------------------------
        """
        Permet d'exécuter le traitement de création d'une FeatureClass contenant les ZT de non-conformité et le numéro de la ZT_ID.
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        nomFeatureClassZT   : Nom de la FeatureClass des ZT de non-conformité à créer.
        nomAttributZT       : Nom de l'attribut du numéro de ZT_ID.
        nomAttributNC       : Nom de l'attribut du numéro de non-conformité.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Créer la référence spatiale pour "GCS_North_American_1983_CSRS"
        sr = arcpy.SpatialReference(4617)
        
        #Créer la FeatureClass de ZT
        arcpy.AddMessage("- Création de la FeatureClass des ZT de non-conformité")
        featureClassZT = arcpy.CreateFeatureclass_management("in_memory", nomFeatureClassZT, "POLYGON", spatial_reference=sr)
        
        #Ajouter l'attribut du numéro de ZT_ID
        arcpy.AddMessage("- Ajout de l'attribut de " + nomAttributZT + " dans la FeatureClass des ZT de non-conformité")
        arcpy.management.AddField(featureClassZT, nomAttributZT, "TEXT", field_length=64)
        
        #Ajouter l'attribut du numéro de NO_NC
        arcpy.AddMessage("- Ajout de l'attribut de " + nomAttributNC + " dans la FeatureClass des ZT de non-conformité")
        arcpy.management.AddField(featureClassZT, nomAttributNC, "TEXT", field_length=5)
        
        #Créer le curseur pour ajouter les éléments dans la FeatureClass
        cursor = arcpy.da.InsertCursor(featureClassZT, [nomAttributNC, nomAttributZT, "SHAPE@WKT"])
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Requête dans SIB afin de valider le numéro de non-conformité
        arcpy.AddMessage("- Extraction des ZT de non-conformité")
        sql = "SELECT NO_NC,ZT_ID,SHAPE_WKT FROM F710_ZT"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        
        #Traiter tous les ZT non-conformes
        for zt in resultat:
            #Extraire le ZT_ID
            no_nc = zt[0]
            
            #Extraire le ZT_ID
            zt_id = zt[1]
            
            #Extraire la géométrie en WKT
            shape_wkt = zt[2].read()
            
            #Afficher le ZT_ID à insérer
            arcpy.AddMessage("  ZT_ID=" + zt_id)
            
            #Insérer l'élément dans la FeatureClass
            cursor.insertRow([no_nc, zt_id, shape_wkt])
        
        #Accepter les ajouts en détruisant le curseur
        arcpy.AddMessage("- Accepter les modifications")
        del cursor
        
        #Sortie normale pour une exécution réussie
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB
        
        #Sortir
        return featureClassZT

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env                 = "SIB_PRO"
        nomFeatureClassZT   = ""
        nomAttributZT       = ""
        nomAttributNC       = ""
        featureClassZT      = ""
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            nomFeatureClassZT = sys.argv[2].upper()
        
        if len(sys.argv) > 3:
            nomAttributZT = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            nomAttributNC = sys.argv[4].upper()
        
        #Instanciation de la classe de création d'une FeatureClass contenant les ZT de non-conformité et le numéro de la ZT_ID.
        oCreerFeatureClassZtNonConforme = CreerFeatureClassZtNonConforme()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oCreerFeatureClassZtNonConforme.validerParamObligatoire(env, nomFeatureClassZT, nomAttributZT, nomAttributNC)
        
        #Exécuter le traitement de création d'une FeatureClass contenant les ZT de non-conformité et le numéro de la ZT_ID.
        arcpy.AddMessage("- Exécuter la création d'une FeatureClass de ZT non-conforme.")
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

    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Retourner la FeatureClass des ZT non-conformes
    arcpy.SetParameterAsText(4, featureClassZT)
    #Sortir sans code d'erreur
    sys.exit(0)