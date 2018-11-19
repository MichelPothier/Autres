#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : IdentifierElementXmlCreerZtNonConforme.py
# Auteur    : Michel Pothier
# Date      : 15 décembre 2014

"""
    Application qui permet d'identifier les éléments non-conformes par classe, partition et dépôt qui sont contenus dans des Zones de Travail (ZT).
    
    Les ZT, les dépots, les partitions et les classes traités sont présents dans les fichiers XML de type CreerZT.
    
    ATTENTION : Si aucun élément n'est sélectionné dans une classe, seule la classe sera identifié dans SIB
    
    Paramètres d'entrée:
    --------------------
        env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    défaut = SIB_PRO
        no_nc               OB      Numéro de non-conformité à traiter.
                                    défaut = ""
        listeFichierXml     OB      Liste des fichiers XML contenant l'information de chaque zone de travail à traiter.
                                    défaut = ""
        listeFeatureLayer   OB      Liste des "FeatureLayer" contenant les éléments sélectionnés et qui correspondent aux classes, partitions et dépôts des fichiers XML.
                                    défaut = ""
        detruire            OP      True : Indique qu'on doit détruire les éléments déjà identifiés avant d'ajouter les nouveaux.
                                    False : Indique qu'on doit seulement ajouter les nouveaux éléments identifiés sans détruire ceux existants.
                                    défaut = False
    
    Paramètres de sortie:
    ---------------------
        listeFichierXmlSortie   : Liste des noms de fichier XML corrigés
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du résultat de l'exécution du programme.
                                  (Ex: 0=Succès, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 
    
    Usage:
        IdentifierElementXmlCreerZtNonConforme.py env no_nc listeFichierXml listeFeatureLayer ajouter
    
    Exemple:
        IdentifierElementXmlCreerZtNonConforme.py SIB_PRO 03034 d:\021M07.xml,d:\021M08.xml WATERBODY_2,WATERCOURSE_1

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: IdentifierElementXmlCreerZtNonConforme.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, arcpy, traceback

#Importation des modules privés (Cits)
import CompteSib, util_XmlCreerZT

#*******************************************************************************************
class IdentifierElementXmlCreerZtNonConforme:
#*******************************************************************************************
    """
    Permet d'identifier les éléments non-conformes par classe, partition et dépôt qui sont contenus dans des Zones de Travail (ZT).
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
    def validerParamObligatoire(self, env, no_nc, listeFichierXml, listeFeatureLayer):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        listeFichierXml     : Liste des fichiers XML à traiter
        listeFichierXml     : Liste des fichiers XML contenant l'information de chaque zone de travail à traiter.
        listeFeatureLayer   : Liste des "FeatureLayer" contenant les éléments sélectionnés et qui correspondent aux classes, partitions et dépôts des fichiers XML.
        
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

        #Valider la présence de la liste du fichier XML
        if (len(listeFichierXml) == 0):
            raise Exception ('Paramètre obligatoire manquant: listeFichierXml')

        #Valider la présence de la liste des FeatureLayer
        if (len(listeFeatureLayer) == 0):
            raise Exception ('Paramètre obligatoire manquant: listeFeatureLayer')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def extraireFeatureLayer(self, classe, listeFeatureLayer):
    #-------------------------------------------------------------------------------------
        """
        Permet d'extraire le FeatureLayer de la liste correspondant à la classe désirée.
        Si aucun n'élémnt n'est sélectionné dans le FeatureLayer, il n'est pas extrait même si la classe correspond.
        
        Paramètres:
        -----------
        classe              : Nom de la classe à trouver.
        listeFeatureLayer   : Liste des "FeatureLayer" contenant les éléments sélectionnés et qui correspondent aux classes, partitions et dépôts des fichiers XML.
        
        Retour:
        -------
        featureLayer        : Nom du FeatureLayer trouvé.
        """
        
        #Aucun FeatureLayer n'est trouvé par défaut
        featureLayer = ""
        
        #Traiter tous les Layer
        for layer in listeFeatureLayer.split(","):
            #Extraire la desciption du Layer
            desc = arcpy.Describe(layer)
            #Vérifier si le nom de la classe correspond
            if classe.upper() in desc.name.upper():
                #Vérifier si le layer est un FeatureLayer
                if desc.dataType == u'FeatureLayer':
                    #Vérifier si au moins un élément est sélectionné
                    if len(desc.fidSet) > 0:
                        #Retourner le nom du Layer
                        return layer
        
        #Sortir
        return featureLayer
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, listeFichierXml, listeFeatureLayer, detruire):
    #-------------------------------------------------------------------------------------
        """
        Permet d'exécuter le traitement d'identifier les éléments non-conformes par classe, partition et dépôt
        qui sont contenus dans des Zones de Travail (ZT).
        
        Paramètres:
        -----------
        env                 : Environnement de travail
        no_nc               : Numéro de non-conformité à traiter.
        listeFichierXml     : Liste des fichiers XML contenant l'information de chaque zone de travail à traiter.
        listeFeatureLayer   : Liste des "FeatureLayer" contenant les éléments sélectionnés et qui correspondent aux classes, partitions et dépôts des fichiers XML.
        detruire            : True : Indique qu'on doit détruire les éléments déjà identifiés avant d'ajouter les nouveaux.
                              False : Indique qu'on doit seulement ajouter les nouveaux éléments identifiés sans détruire ceux existants.
        
        Retour:
        -------
        listeFichierXmlSortie : Liste des noms de fichier XML de sortie corrigés
        
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
        
        #Initialiser les listes
        listeFichierXmlSortie = []
        object_id = "OBJECTID"
        bdg_id = "BDG_ID"
        #Traiter tous les fichiers XML de la liste
        for fichierXml in listeFichierXml.split(","):
            #Instanciation de la classe XmlCreerZT pour lire et écrire dans le fichier XML selon le profil du service CreerZT
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Lecture du fichier XML: %s" %fichierXml)
            oXmlCreerZT = util_XmlCreerZT.XmlCreerZT(fichierXml)
            
            #Extraire le dépôt
            depot = oXmlCreerZT.obtenirDepot()
            arcpy.AddMessage("  Dépôt: %s" %depot)
            
            #Extraire la ZT_ID
            zt_id = oXmlCreerZT.obtenirZtId()
            arcpy.AddMessage("  ZT_ID: %s" %zt_id)
            
            #Par défaut, on suppose que le ZT_ID contient le NO_NC
            zt_id_nc = zt_id
            #Vérifier si le ZT_ID contient le NO_NC
            if no_nc not in zt_id:
                #Écrire le nouveau ZT_ID contenant le NO_NC dans le fichier XML
                zt_id_nc = zt_id + "_NC_" + no_nc
                oXmlCreerZT.definirZtId(zt_id_nc)
            arcpy.AddMessage("  ZT_ID_NC: %s" %zt_id_nc)
            
            #
            #Extraire le catalogue
            catalogue = oXmlCreerZT.obtenirCatalogue()
            arcpy.AddMessage("  Catalogue: %s" %catalogue)
            
            #Extraire la partition
            partition = oXmlCreerZT.obtenirPartition()
            arcpy.AddMessage("  Partition: %s" %partition)
            
            #Extraire la liste des classes
            listeClasse = oXmlCreerZT.obtenirListeNomElement()
            arcpy.AddMessage("  ListeClasse: %s" %listeClasse)
            
            #Extraire le polygonWKT
            mxd = arcpy.mapping.MapDocument("CURRENT")
            polygonWKT = oXmlCreerZT.obtenirPolygone()
            arcpy.AddMessage("  PolygonWKT: %s" %polygonWKT)
            polygon = arcpy.FromWKT(polygonWKT.replace("POLYGON (","MULTIPOLYGON ((") + ")", mxd.activeDataFrame.spatialReference)
            
            #Vérifier s'il faut détruire les entrées existantes
            #if detruire:
                #Détruire les entrées existantes dans la table F705_PR
                #sql = "DELETE FROM F705_PR WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + partition + "' AND IDENTIFIANT='" + zt_id_nc + "'"
                #arcpy.AddMessage(sql)
                #self.Sib.execute(sql)
            
            #Traiter toutes les classes non-conformes
            for classe in listeClasse.split(","):
                #Vérifier s'il faut détruire les entrées existantes
                if detruire:
                    #Détruire les entrées existantes dans la table F705_EL
                    sql = "DELETE FROM F705_EL WHERE NO_NC='" + no_nc + "' AND CATALOGUE='" + catalogue + "' AND DEPOT='" + depot + "' AND PARTITION='" + partition + "' AND CLASSE='" + classe + "' AND ZT_ID_DEBUT='" + zt_id_nc + "'"
                    arcpy.AddMessage(sql)
                    self.Sib.execute(sql)
                    
                #Initialiser le compteur d'élément
                nb_elem = 0
                #Trouver le FeatureLayer de la classe
                featureLayer = self.extraireFeatureLayer(classe, listeFeatureLayer)
                #Vérifier si des éléments sont sélectionnés
                if len(featureLayer) > 0:
                    #Traiter tous les éléments sélectionnés du FeatureLayer
                    for row in arcpy.SearchCursor(featureLayer):
                        #Extraire l'élément
                        element = row.getValue("Shape")
                        #Vérifier si le polygon contient l'élément
                        if polygon.contains(element):
                            #Compter les éléments ajoutés
                            nb_elem = nb_elem + 1
                            #Ajouter un élément non-conforme d'une classe
                            sql = "P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + catalogue + "','" + depot + "','" + partition + "','" + classe + "'"
                            sql = sql + "," + str(row.getValue(object_id)) + ",'" + str(row.getValue(bdg_id)) + "','" + zt_id_nc + "',NULL,NULL"
                            arcpy.AddMessage("INSERT INTO F705_EL VALUES (" + sql + ")")
                            self.Sib.execute("INSERT INTO F705_EL VALUES (" + sql + ")")
                        
                #Si aucun élément sélectionnée
                if nb_elem == 0:
                    #Ajouter une clase non-conforme sans élément
                    sql = "P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + catalogue + "','" + depot + "','" + partition + "','" + classe + "'"
                    sql = sql + ",0,NULL,'" + zt_id_nc + "',NULL,NULL"
                    arcpy.AddMessage("INSERT INTO F705_EL VALUES (" + sql + ")")
                    self.Sib.execute("INSERT INTO F705_EL VALUES (" + sql + ")")
            
            #Ajouter un identifiant du produit non-conforme
            #sql = "INSERT INTO F705_PR VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + partition + "','" + zt_id_nc + "',1,0,P0G03_UTL.PU_HORODATEUR,99999,99)"
            #arcpy.AddMessage(sql)
            #self.Sib.execute(sql)
            
            #Changer le nom du fichier XML selon le nouvel identifiant contenant le no_nc
            fichierXmlSortie = fichierXml.replace(zt_id, zt_id_nc)
            
            #Écrire dans le même fichier le nouvel identifiant
            arcpy.AddMessage("- Écriture du fichier XML %s:" %fichierXmlSortie)
            oXmlCreerZT.ecrire(fichierXmlSortie)
            
            #Ajouter le fichier XML de sortie à la liste
            listeFichierXmlSortie.append(fichierXmlSortie)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB
        
        #Sortir et retourner la liste des fichiers XML de sortie
        return listeFichierXmlSortie

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:   
        #Initialisation des valeurs par défaut
        env                     = "SIB_PRO"
        no_nc                   = ""
        listeFichierXml         = ""
        listeFeatureLayer       = ""
        detruire                = False
        listeFichierXmlSortie   = []
        
        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            listeFichierXml = sys.argv[3].replace(";",",")
        
        if len(sys.argv) > 4:
            listeFeatureLayer = sys.argv[4].replace(";",",")
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                detruire = (sys.argv[5].upper() == "TRUE")
        
        #Instanciation de la classe d'identification des éléments non-conformes.
        oIdentifierElementXmlCreerZtNonConforme = IdentifierElementXmlCreerZtNonConforme()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oIdentifierElementXmlCreerZtNonConforme.validerParamObligatoire(env, no_nc, listeFichierXml, listeFeatureLayer)
        
        #Exécuter le traitement d'identification des éléments non-conformes.
        arcpy.AddMessage("- Exécuter l'identification des éléments non-conformes.")
        listeFichierXmlSortie = oIdentifierElementXmlCreerZtNonConforme.executer(env, no_nc, listeFichierXml, listeFeatureLayer, detruire)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Afficher la liste des fichierXml
        arcpy.AddMessage("  listeFichierXmlSortie=%s" %listeFichierXmlSortie)
        arcpy.SetParameterAsText(5, listeFichierXmlSortie)
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Afficher la liste des fichierXml
    arcpy.AddMessage("  listeFichierXmlSortie=%s" %listeFichierXmlSortie)
    arcpy.SetParameterAsText(5, listeFichierXmlSortie)
    #Sortir sans code d'erreur
    sys.exit(0)