#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : IdentifierElementZtNonConforme.py
# Auteur    : Michel Pothier
# Date      : 15 décembre 2014

"""
    Application qui permet d'identifier les éléments non-conformes par classe pour un catalogue, un produit et un dépôt qui sont contenus dans des Zones de Travail (ZT).
    
    ATTENTION : Si aucun élément n'est sélectionné dans une classe, seule la classe sera identifié dans SIB
    
    Paramètres d'entrée:
    --------------------
        env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    défaut = SIB_PRO
        no_nc               OB      Numéro de non-conformité à traiter.
                                    défaut = ""
        catalogue           OB      Nom du catalogue qui permet d'indiquer le dépôt, le produit, les classes et les attributs d'identifiant de découpage, d'objet et d'élément.
                                    défaut = ""
        depot               OB      Nom du dépôt contenant les classes et les éléments.
                                    défaut = ""
        produit             OB      Nom du produit décrivant les classes et les éléments.
                                    défaut = ""
        featureLayerZT      OB      Nom du layer contenant les zones de travail (ZT).
                                    défaut = <FEATURE SET créer en mémoire et dans lequel on doit dessiner les ZT et indiquer la valeur du ZT_ID>
        attributZT          OB      Nom de l'attribut du FeatureLayerZT contenant le ZT_ID.
                                    défaut = ZT_ID
        listeFeatureLayer   OB      Liste des featureLayers non-conformes.
                                    La liste des classes permises est identifiée à partir du catalogue.
                                    défaut = <liste des FeatureLayer visible et pour lesquel les classes sont valident>
        detruire            OP      True : Indique qu'on doit détruire les éléments déjà identifiés avant d'ajouter les nouveaux.
                                    False : Indique qu'on doit seulement ajouter les nouveaux éléments identifiés sans détruire ceux existants.
                                    défaut = False
    
    Paramètres de sortie:
    ---------------------
        Aucun
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du résultat de l'exécution du programme.
                                  (Ex: 0=Succès, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 
    
    Usage:
        IdentifierElementZtNonConforme.py env no_nc catalogue depot produit featureLayerZT attributZT listeFeatureLayer detruire
    
    Exemple:
        IdentifierElementZtNonConforme.py SIB_PRO 03034 INTEGRATED_ESSIM_1.0.0.0 INTEGRATED ESSIM WATERBODY_2,WATERCOURSE_1

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: IdentifierElementZtNonConforme.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, cx_Oracle, traceback

#Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class IdentifierElementZtNonConforme:
#*******************************************************************************************
    """
    Permet d'identifier les éléments non-conformes par classe pour un catalogue, un produit et un dépôt qui sont contenus dans des Zones de Travail (ZT).
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
    def validerParamObligatoire(self, env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        catalogue           : Nom du catalogue qui permet d'indiquer le dépôt, le produit, les classes et les attributs d'identifiant de découpage, d'objet et d'élément.
        depot               : Nom du dépôt contenant les classes et les éléments.
        produit             : Nom du produit décrivant les classes et les éléments.
        featureLayerZT      : Nom du layer contenant les zones de travail (ZT).
        attributZT          : Nom de l'attribut du FeatureLayerZT contenant le ZT_ID.
        listeFeatureLayer   : Liste des featureLayers non-conformes.
        
        Retour:
        -------
        Exception s'il y a un problème
        """

        #Valider la présence de l'environnement
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')

        #Valider la présence du no_nc
        if (len(no_nc) == 0):
            raise Exception ('Paramètre obligatoire manquant: no_nc')

        #Valider la présence du catalogue
        if (len(catalogue) == 0):
            raise Exception ('Paramètre obligatoire manquant: catalogue')

        #Valider la présence du dépôt
        if (len(depot) == 0):
            raise Exception ('Paramètre obligatoire manquant: depot')

        #Valider la présence du produit
        if (len(produit) == 0):
            raise Exception ('Paramètre obligatoire manquant: produit')

        #Valider la présence du featureLayerZT
        if (len(featureLayerZT) == 0):
            raise Exception ('Paramètre obligatoire manquant: featureLayerZT')

        #Valider la présence de l'attributZT
        if (len(attributZT) == 0):
            raise Exception ('Paramètre obligatoire manquant: attributZT')

        #Valider la présence de la liste des Classes
        if (len(listeFeatureLayer) == 0):
            raise Exception ('Paramètre obligatoire manquant: listeFeatureLayer')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def extraireListeClasses(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Permet d'extraire la liste des classes présentes dans le catalogue.
        
        Paramètres:
        -----------
        catalogue       : Nom du catalogue qui permet d'indiquer le dépôt, le produit, les classes et les attributs d'identifiant de découpage, d'objet et d'élément.
        
        Retour:
        -------
        listeClasses    : Liste des noms de classes présentes dans le catalogue.
        """
        
        #Aucun FeatureLayer n'est trouvé par défaut
        listeClasses = ""
            
        #return "bs_1370009_2,lx_1000089_2"
        
        #Requête dans SIB afin d'extraire la liste des classes du catalogue
        arcpy.AddMessage("- Extraire la liste des classes du catalogue")
        sql = "SELECT CLASSE FROM F135_CL WHERE CATALOGUE='" + catalogue + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        
        #Créer la liste des classes
        for classe in resultat:
            #Ajouter la classe à la liste
            listeClasses = listeClasses + classe[0] + ","
        
        #Si au moins une classe est présente
        if len(listeClasses) > 0:
            #Enlever la dernière ","
            listeClasses = listeClasses[0:-1]
        
        #Sortir
        return listeClasses
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer, detruire):
    #-------------------------------------------------------------------------------------
        """
        Permet d'exécuter le traitement d'identifier les éléments non-conformes par classe, partition et dépôt
        qui sont contenus dans des Zones de Travail (ZT).
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        no_nc               : Numéro de non-conformité à traiter.
        catalogue           : Nom du catalogue qui permet d'indiquer le dépôt, le produit, les classes et les attributs d'identifiant de découpage, d'objet et d'élément.
        depot               : Nom du dépôt contenant les classes et les éléments.
        produit             : Nom du produit décrivant les classes et les éléments.
        featureLayerZT      : Nom du layer contenant les zones de travail (ZT).
        attributZT          : Nom de l'attribut du FeatureLayerZT contenant le ZT_ID.
        listeFeatureLayer   : Liste des featureLayers non-conformes.
        detruire            : Indique si on doit détruire les éléments déjà identifiés avant d'ajouter les nouveaux.
        
        Retour:
        -------
        Aucun
        
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Requête dans SIB afin de valider le numéro de non-conformité
        arcpy.AddMessage("- Valider le numéro de non-conformité")
        sql = "SELECT NO_NC,DATE_FERMETURE,DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Si aucun résultat retourné
        if len(resultat) == 0:
            raise Exception ("Numéro de non-conformité invalide : " + no_nc)
        #Si la date de fermeture n'est pas vide
        if resultat[0][1] <> None or resultat[0][2] <> None:
            raise Exception ("La date de fermeture n'est pas vide : " + resultat[0][1])
        #Si la date de traitement n'est pas vide
        if resultat[0][1] <> None or resultat[0][2] <> None:
            raise Exception ("La date de traitement n'est pas vide : " + resultat[0][2])
        
        #Extraire la liste des classes
        listeClasses = self.extraireListeClasses(catalogue)
        #Si la date de traitement n'est pas vide
        if len(listeClasses) == 0:
            raise Exception ("Aucune classe n'est présente dans le catalogue : " + catalogue)
        
        #Initialiser les listes
        object_id = "OBJECTID"
        bdg_id = "id"
        arcpy.AddMessage("-Traitement des Zones de travail (ZT)")
        
        #Traiter tous les éléments du FeatureLayer
        for rowZT in arcpy.SearchCursor(featureLayerZT):
            #Extraire le ZT_ID
            zt_id = str(rowZT.getValue(attributZT))
            #Afficher le ZT_ID
            arcpy.AddMessage("  ")
            arcpy.AddMessage("  " + attributZT + " : " + zt_id)
            
            #Par défaut, on suppose que le ZT_ID contient le NO_NC
            zt_id_nc = zt_id
            #Vérifier si le ZT_ID contient le NO_NC
            if no_nc not in zt_id:
                #Écrire le nouveau ZT_ID contenant le NO_NC dans le fichier XML
                zt_id_nc = zt_id + "_NC_" + no_nc
            arcpy.AddMessage("  ZT_ID_NC: %s" %zt_id_nc)
            
            #Extraire le polygon en WKT
            polygonZT = rowZT.getValue("Shape")
            
            #Ajouter l'information de la ZT
            self.Sib.cursor.setinputsizes(SHAPE_WKT = cx_Oracle.CLOB)
            sql = "INSERT INTO F710_ZT (UPDT_FLD,ETAMPE,DT_C,DT_M,NO_NC,ZT_ID,X_MIN,X_MAX,Y_MIN,Y_MAX,SHAPE_WKT) "
            sql = sql + "VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + zt_id_nc + "',"
            sql = sql + str(polygonZT.extent.XMin) + "," + str(polygonZT.extent.XMax) + "," + str(polygonZT.extent.YMin) + "," + str(polygonZT.extent.YMax) + ",:SHAPE_WKT)"
            self.Sib.cursor.execute(sql,SHAPE_WKT=polygonZT.WKT)
            #Pour lire le CLOB : wkt = resultat[0][0].read()
            arcpy.AddMessage(sql)
            
            #Traiter tous les FeatureLayer non-conformes
            for featureLayer in listeFeatureLayer.split(","):
                #Extraire la desciption du Layer
                desc = arcpy.Describe(featureLayer)
                #Extraire le nom de la classe du FeatureLayer
                classe = desc.name
                #Vérifier si la classe est contenau dans le catalogue
                if classe in listeClasses:
                    #Vérifier s'il faut détruire les entrées existantes
                    if detruire:
                        #Détruire les entrées existantes dans la table F705_EL
                        sql = "DELETE FROM F705_EL WHERE NO_NC='" + no_nc + "' AND CATALOGUE='" + catalogue + "' AND DEPOT='" + depot + "' AND PARTITION='" + produit + "' AND CLASSE='" + classe + "' AND ZT_ID_DEBUT='" + zt_id_nc + "'"
                        arcpy.AddMessage(sql)
                        self.Sib.execute(sql)
                        
                    #Initialiser le compteur d'élément
                    nb_elem = 0
                    #Vérifier si au moins un élément est sélectionné
                    if len(desc.fidSet) > 0:
                        #Traiter tous les éléments sélectionnés du FeatureLayer
                        for row in arcpy.SearchCursor(featureLayer):
                            #Extraire la géométrie de l'élément
                            geometrie = row.getValue("Shape")
                            #Vérifier si le polygon contient l'élément
                            if polygonZT.contains(geometrie):
                                #Compter les éléments ajoutés
                                nb_elem = nb_elem + 1
                                #Ajouter un élément non-conforme d'une classe
                                sql = "INSERT INTO F705_EL VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + catalogue + "','" + depot + "','" + produit + "','" + classe + "'"
                                sql = sql + "," + str(row.getValue(object_id)) + ",'" + str(row.getValue(bdg_id)) + "','" + zt_id_nc + "',NULL,NULL)"
                                arcpy.AddMessage(sql)
                                self.Sib.execute(sql)
                            
                    #Si aucun élément sélectionné
                    if nb_elem == 0:
                        #Ajouter une clase non-conforme sans élément
                        sql = "INSERT INTO F705_EL VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + catalogue + "','" + depot + "','" + produit + "','" + classe + "'"
                        sql = sql + ",0,NULL,'" + zt_id_nc + "',NULL,NULL)"
                        arcpy.AddMessage(sql)
                        self.Sib.execute(sql)
                
                #Si la classe du FeatureLayer ne fait pas partie du catalogue
                else:
                    #Afficher un avertissement
                    arcpy.AddWarning("La classe du FeatureLayer est absente du catalogue : " + classe)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:   
        #Initialisation des valeurs par défaut
        env                 = "SIB_PRO"
        no_nc               = ""
        catalogue           = ""
        depot               = ""
        produit             = ""
        featureLayerZT      = ""
        attributZT          = ""
        listeFeatureLayer   = ""
        detruire            = False
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            catalogue = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            depot = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            produit = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            featureLayerZT = sys.argv[6]
        
        if len(sys.argv) > 7:
            attributZT = sys.argv[7]
        
        if len(sys.argv) > 8:
            listeFeatureLayer = sys.argv[8].replace(";",",")
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                detruire = (sys.argv[5].upper() == "TRUE")
        
        #Instanciation de la classe d'identification des éléments non-conformes.
        oIdentifierElementZtNonConforme = IdentifierElementZtNonConforme()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oIdentifierElementZtNonConforme.validerParamObligatoire(env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer)
        
        #Exécuter le traitement d'identification des éléments non-conformes.
        arcpy.AddMessage("- Exécuter l'identification des éléments non-conformes.")
        oIdentifierElementZtNonConforme.executer(env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer, detruire)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)