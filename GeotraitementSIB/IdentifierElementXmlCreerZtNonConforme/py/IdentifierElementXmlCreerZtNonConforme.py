#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : IdentifierElementXmlCreerZtNonConforme.py
# Auteur    : Michel Pothier
# Date      : 15 d�cembre 2014

"""
    Application qui permet d'identifier les �l�ments non-conformes par classe, partition et d�p�t qui sont contenus dans des Zones de Travail (ZT).
    
    Les ZT, les d�pots, les partitions et les classes trait�s sont pr�sents dans les fichiers XML de type CreerZT.
    
    ATTENTION : Si aucun �l�ment n'est s�lectionn� dans une classe, seule la classe sera identifi� dans SIB
    
    Param�tres d'entr�e:
    --------------------
        env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    d�faut = SIB_PRO
        no_nc               OB      Num�ro de non-conformit� � traiter.
                                    d�faut = ""
        listeFichierXml     OB      Liste des fichiers XML contenant l'information de chaque zone de travail � traiter.
                                    d�faut = ""
        listeFeatureLayer   OB      Liste des "FeatureLayer" contenant les �l�ments s�lectionn�s et qui correspondent aux classes, partitions et d�p�ts des fichiers XML.
                                    d�faut = ""
        detruire            OP      True : Indique qu'on doit d�truire les �l�ments d�j� identifi�s avant d'ajouter les nouveaux.
                                    False : Indique qu'on doit seulement ajouter les nouveaux �l�ments identifi�s sans d�truire ceux existants.
                                    d�faut = False
    
    Param�tres de sortie:
    ---------------------
        listeFichierXmlSortie   : Liste des noms de fichier XML corrig�s
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du r�sultat de l'ex�cution du programme.
                                  (Ex: 0=Succ�s, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 
    
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

#Importation des modules priv�s (Cits)
import CompteSib, util_XmlCreerZT

#*******************************************************************************************
class IdentifierElementXmlCreerZtNonConforme:
#*******************************************************************************************
    """
    Permet d'identifier les �l�ments non-conformes par classe, partition et d�p�t qui sont contenus dans des Zones de Travail (ZT).
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
    def validerParamObligatoire(self, env, no_nc, listeFichierXml, listeFeatureLayer):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        listeFichierXml     : Liste des fichiers XML � traiter
        listeFichierXml     : Liste des fichiers XML contenant l'information de chaque zone de travail � traiter.
        listeFeatureLayer   : Liste des "FeatureLayer" contenant les �l�ments s�lectionn�s et qui correspondent aux classes, partitions et d�p�ts des fichiers XML.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """

        #Valider la pr�sence de l'environnement
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')

        #Valider la pr�sence du no_nc
        if (len(no_nc) == 0):
            raise Exception ('Param�tre obligatoire manquant: no_nc')

        #Valider la pr�sence de la liste du fichier XML
        if (len(listeFichierXml) == 0):
            raise Exception ('Param�tre obligatoire manquant: listeFichierXml')

        #Valider la pr�sence de la liste des FeatureLayer
        if (len(listeFeatureLayer) == 0):
            raise Exception ('Param�tre obligatoire manquant: listeFeatureLayer')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def extraireFeatureLayer(self, classe, listeFeatureLayer):
    #-------------------------------------------------------------------------------------
        """
        Permet d'extraire le FeatureLayer de la liste correspondant � la classe d�sir�e.
        Si aucun n'�l�mnt n'est s�lectionn� dans le FeatureLayer, il n'est pas extrait m�me si la classe correspond.
        
        Param�tres:
        -----------
        classe              : Nom de la classe � trouver.
        listeFeatureLayer   : Liste des "FeatureLayer" contenant les �l�ments s�lectionn�s et qui correspondent aux classes, partitions et d�p�ts des fichiers XML.
        
        Retour:
        -------
        featureLayer        : Nom du FeatureLayer trouv�.
        """
        
        #Aucun FeatureLayer n'est trouv� par d�faut
        featureLayer = ""
        
        #Traiter tous les Layer
        for layer in listeFeatureLayer.split(","):
            #Extraire la desciption du Layer
            desc = arcpy.Describe(layer)
            #V�rifier si le nom de la classe correspond
            if classe.upper() in desc.name.upper():
                #V�rifier si le layer est un FeatureLayer
                if desc.dataType == u'FeatureLayer':
                    #V�rifier si au moins un �l�ment est s�lectionn�
                    if len(desc.fidSet) > 0:
                        #Retourner le nom du Layer
                        return layer
        
        #Sortir
        return featureLayer
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, listeFichierXml, listeFeatureLayer, detruire):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traitement d'identifier les �l�ments non-conformes par classe, partition et d�p�t
        qui sont contenus dans des Zones de Travail (ZT).
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        no_nc               : Num�ro de non-conformit� � traiter.
        listeFichierXml     : Liste des fichiers XML contenant l'information de chaque zone de travail � traiter.
        listeFeatureLayer   : Liste des "FeatureLayer" contenant les �l�ments s�lectionn�s et qui correspondent aux classes, partitions et d�p�ts des fichiers XML.
        detruire            : True : Indique qu'on doit d�truire les �l�ments d�j� identifi�s avant d'ajouter les nouveaux.
                              False : Indique qu'on doit seulement ajouter les nouveaux �l�ments identifi�s sans d�truire ceux existants.
        
        Retour:
        -------
        listeFichierXmlSortie : Liste des noms de fichier XML de sortie corrig�s
        
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #Requ�te dans SIB afin de valider le num�ro de non-conformit�
        arcpy.AddMessage("- Valider le num�ro de non-conformit�")
        sql = "SELECT NO_NC,DATE_FERMETURE,DATE_TRAITEMENT FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Si aucun r�sultat retourn�
        if len(resultat) == 0:
            raise Exception ("Num�ro de non-conformit� invalide : " + no_nc)
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
            #Instanciation de la classe XmlCreerZT pour lire et �crire dans le fichier XML selon le profil du service CreerZT
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Lecture du fichier XML: %s" %fichierXml)
            oXmlCreerZT = util_XmlCreerZT.XmlCreerZT(fichierXml)
            
            #Extraire le d�p�t
            depot = oXmlCreerZT.obtenirDepot()
            arcpy.AddMessage("  D�p�t: %s" %depot)
            
            #Extraire la ZT_ID
            zt_id = oXmlCreerZT.obtenirZtId()
            arcpy.AddMessage("  ZT_ID: %s" %zt_id)
            
            #Par d�faut, on suppose que le ZT_ID contient le NO_NC
            zt_id_nc = zt_id
            #V�rifier si le ZT_ID contient le NO_NC
            if no_nc not in zt_id:
                #�crire le nouveau ZT_ID contenant le NO_NC dans le fichier XML
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
            
            #V�rifier s'il faut d�truire les entr�es existantes
            #if detruire:
                #D�truire les entr�es existantes dans la table F705_PR
                #sql = "DELETE FROM F705_PR WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + partition + "' AND IDENTIFIANT='" + zt_id_nc + "'"
                #arcpy.AddMessage(sql)
                #self.Sib.execute(sql)
            
            #Traiter toutes les classes non-conformes
            for classe in listeClasse.split(","):
                #V�rifier s'il faut d�truire les entr�es existantes
                if detruire:
                    #D�truire les entr�es existantes dans la table F705_EL
                    sql = "DELETE FROM F705_EL WHERE NO_NC='" + no_nc + "' AND CATALOGUE='" + catalogue + "' AND DEPOT='" + depot + "' AND PARTITION='" + partition + "' AND CLASSE='" + classe + "' AND ZT_ID_DEBUT='" + zt_id_nc + "'"
                    arcpy.AddMessage(sql)
                    self.Sib.execute(sql)
                    
                #Initialiser le compteur d'�l�ment
                nb_elem = 0
                #Trouver le FeatureLayer de la classe
                featureLayer = self.extraireFeatureLayer(classe, listeFeatureLayer)
                #V�rifier si des �l�ments sont s�lectionn�s
                if len(featureLayer) > 0:
                    #Traiter tous les �l�ments s�lectionn�s du FeatureLayer
                    for row in arcpy.SearchCursor(featureLayer):
                        #Extraire l'�l�ment
                        element = row.getValue("Shape")
                        #V�rifier si le polygon contient l'�l�ment
                        if polygon.contains(element):
                            #Compter les �l�ments ajout�s
                            nb_elem = nb_elem + 1
                            #Ajouter un �l�ment non-conforme d'une classe
                            sql = "P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + catalogue + "','" + depot + "','" + partition + "','" + classe + "'"
                            sql = sql + "," + str(row.getValue(object_id)) + ",'" + str(row.getValue(bdg_id)) + "','" + zt_id_nc + "',NULL,NULL"
                            arcpy.AddMessage("INSERT INTO F705_EL VALUES (" + sql + ")")
                            self.Sib.execute("INSERT INTO F705_EL VALUES (" + sql + ")")
                        
                #Si aucun �l�ment s�lectionn�e
                if nb_elem == 0:
                    #Ajouter une clase non-conforme sans �l�ment
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
            
            #�crire dans le m�me fichier le nouvel identifiant
            arcpy.AddMessage("- �criture du fichier XML %s:" %fichierXmlSortie)
            oXmlCreerZT.ecrire(fichierXmlSortie)
            
            #Ajouter le fichier XML de sortie � la liste
            listeFichierXmlSortie.append(fichierXmlSortie)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB
        
        #Sortir et retourner la liste des fichiers XML de sortie
        return listeFichierXmlSortie

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:   
        #Initialisation des valeurs par d�faut
        env                     = "SIB_PRO"
        no_nc                   = ""
        listeFichierXml         = ""
        listeFeatureLayer       = ""
        detruire                = False
        listeFichierXmlSortie   = []
        
        #Extraction des param�tres d'ex�cution
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
        
        #Instanciation de la classe d'identification des �l�ments non-conformes.
        oIdentifierElementXmlCreerZtNonConforme = IdentifierElementXmlCreerZtNonConforme()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oIdentifierElementXmlCreerZtNonConforme.validerParamObligatoire(env, no_nc, listeFichierXml, listeFeatureLayer)
        
        #Ex�cuter le traitement d'identification des �l�ments non-conformes.
        arcpy.AddMessage("- Ex�cuter l'identification des �l�ments non-conformes.")
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

    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Afficher la liste des fichierXml
    arcpy.AddMessage("  listeFichierXmlSortie=%s" %listeFichierXmlSortie)
    arcpy.SetParameterAsText(5, listeFichierXmlSortie)
    #Sortir sans code d'erreur
    sys.exit(0)