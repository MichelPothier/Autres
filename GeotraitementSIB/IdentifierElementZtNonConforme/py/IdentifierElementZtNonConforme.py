#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : IdentifierElementZtNonConforme.py
# Auteur    : Michel Pothier
# Date      : 15 d�cembre 2014

"""
    Application qui permet d'identifier les �l�ments non-conformes par classe pour un catalogue, un produit et un d�p�t qui sont contenus dans des Zones de Travail (ZT).
    
    ATTENTION : Si aucun �l�ment n'est s�lectionn� dans une classe, seule la classe sera identifi� dans SIB
    
    Param�tres d'entr�e:
    --------------------
        env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    d�faut = SIB_PRO
        no_nc               OB      Num�ro de non-conformit� � traiter.
                                    d�faut = ""
        catalogue           OB      Nom du catalogue qui permet d'indiquer le d�p�t, le produit, les classes et les attributs d'identifiant de d�coupage, d'objet et d'�l�ment.
                                    d�faut = ""
        depot               OB      Nom du d�p�t contenant les classes et les �l�ments.
                                    d�faut = ""
        produit             OB      Nom du produit d�crivant les classes et les �l�ments.
                                    d�faut = ""
        featureLayerZT      OB      Nom du layer contenant les zones de travail (ZT).
                                    d�faut = <FEATURE SET cr�er en m�moire et dans lequel on doit dessiner les ZT et indiquer la valeur du ZT_ID>
        attributZT          OB      Nom de l'attribut du FeatureLayerZT contenant le ZT_ID.
                                    d�faut = ZT_ID
        listeFeatureLayer   OB      Liste des featureLayers non-conformes.
                                    La liste des classes permises est identifi�e � partir du catalogue.
                                    d�faut = <liste des FeatureLayer visible et pour lesquel les classes sont valident>
        detruire            OP      True : Indique qu'on doit d�truire les �l�ments d�j� identifi�s avant d'ajouter les nouveaux.
                                    False : Indique qu'on doit seulement ajouter les nouveaux �l�ments identifi�s sans d�truire ceux existants.
                                    d�faut = False
    
    Param�tres de sortie:
    ---------------------
        Aucun
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du r�sultat de l'ex�cution du programme.
                                  (Ex: 0=Succ�s, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 
    
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

#Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class IdentifierElementZtNonConforme:
#*******************************************************************************************
    """
    Permet d'identifier les �l�ments non-conformes par classe pour un catalogue, un produit et un d�p�t qui sont contenus dans des Zones de Travail (ZT).
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
    def validerParamObligatoire(self, env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        catalogue           : Nom du catalogue qui permet d'indiquer le d�p�t, le produit, les classes et les attributs d'identifiant de d�coupage, d'objet et d'�l�ment.
        depot               : Nom du d�p�t contenant les classes et les �l�ments.
        produit             : Nom du produit d�crivant les classes et les �l�ments.
        featureLayerZT      : Nom du layer contenant les zones de travail (ZT).
        attributZT          : Nom de l'attribut du FeatureLayerZT contenant le ZT_ID.
        listeFeatureLayer   : Liste des featureLayers non-conformes.
        
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

        #Valider la pr�sence du catalogue
        if (len(catalogue) == 0):
            raise Exception ('Param�tre obligatoire manquant: catalogue')

        #Valider la pr�sence du d�p�t
        if (len(depot) == 0):
            raise Exception ('Param�tre obligatoire manquant: depot')

        #Valider la pr�sence du produit
        if (len(produit) == 0):
            raise Exception ('Param�tre obligatoire manquant: produit')

        #Valider la pr�sence du featureLayerZT
        if (len(featureLayerZT) == 0):
            raise Exception ('Param�tre obligatoire manquant: featureLayerZT')

        #Valider la pr�sence de l'attributZT
        if (len(attributZT) == 0):
            raise Exception ('Param�tre obligatoire manquant: attributZT')

        #Valider la pr�sence de la liste des Classes
        if (len(listeFeatureLayer) == 0):
            raise Exception ('Param�tre obligatoire manquant: listeFeatureLayer')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def extraireListeClasses(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Permet d'extraire la liste des classes pr�sentes dans le catalogue.
        
        Param�tres:
        -----------
        catalogue       : Nom du catalogue qui permet d'indiquer le d�p�t, le produit, les classes et les attributs d'identifiant de d�coupage, d'objet et d'�l�ment.
        
        Retour:
        -------
        listeClasses    : Liste des noms de classes pr�sentes dans le catalogue.
        """
        
        #Aucun FeatureLayer n'est trouv� par d�faut
        listeClasses = ""
            
        #return "bs_1370009_2,lx_1000089_2"
        
        #Requ�te dans SIB afin d'extraire la liste des classes du catalogue
        arcpy.AddMessage("- Extraire la liste des classes du catalogue")
        sql = "SELECT CLASSE FROM F135_CL WHERE CATALOGUE='" + catalogue + "'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        
        #Cr�er la liste des classes
        for classe in resultat:
            #Ajouter la classe � la liste
            listeClasses = listeClasses + classe[0] + ","
        
        #Si au moins une classe est pr�sente
        if len(listeClasses) > 0:
            #Enlever la derni�re ","
            listeClasses = listeClasses[0:-1]
        
        #Sortir
        return listeClasses
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer, detruire):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traitement d'identifier les �l�ments non-conformes par classe, partition et d�p�t
        qui sont contenus dans des Zones de Travail (ZT).
        
        Param�tres:
        -----------
        env                 : Environnement de travail
        no_nc               : Num�ro de non-conformit� � traiter.
        catalogue           : Nom du catalogue qui permet d'indiquer le d�p�t, le produit, les classes et les attributs d'identifiant de d�coupage, d'objet et d'�l�ment.
        depot               : Nom du d�p�t contenant les classes et les �l�ments.
        produit             : Nom du produit d�crivant les classes et les �l�ments.
        featureLayerZT      : Nom du layer contenant les zones de travail (ZT).
        attributZT          : Nom de l'attribut du FeatureLayerZT contenant le ZT_ID.
        listeFeatureLayer   : Liste des featureLayers non-conformes.
        detruire            : Indique si on doit d�truire les �l�ments d�j� identifi�s avant d'ajouter les nouveaux.
        
        Retour:
        -------
        Aucun
        
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
        
        #Extraire la liste des classes
        listeClasses = self.extraireListeClasses(catalogue)
        #Si la date de traitement n'est pas vide
        if len(listeClasses) == 0:
            raise Exception ("Aucune classe n'est pr�sente dans le catalogue : " + catalogue)
        
        #Initialiser les listes
        object_id = "OBJECTID"
        bdg_id = "id"
        arcpy.AddMessage("-Traitement des Zones de travail (ZT)")
        
        #Traiter tous les �l�ments du FeatureLayer
        for rowZT in arcpy.SearchCursor(featureLayerZT):
            #Extraire le ZT_ID
            zt_id = str(rowZT.getValue(attributZT))
            #Afficher le ZT_ID
            arcpy.AddMessage("  ")
            arcpy.AddMessage("  " + attributZT + " : " + zt_id)
            
            #Par d�faut, on suppose que le ZT_ID contient le NO_NC
            zt_id_nc = zt_id
            #V�rifier si le ZT_ID contient le NO_NC
            if no_nc not in zt_id:
                #�crire le nouveau ZT_ID contenant le NO_NC dans le fichier XML
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
                #V�rifier si la classe est contenau dans le catalogue
                if classe in listeClasses:
                    #V�rifier s'il faut d�truire les entr�es existantes
                    if detruire:
                        #D�truire les entr�es existantes dans la table F705_EL
                        sql = "DELETE FROM F705_EL WHERE NO_NC='" + no_nc + "' AND CATALOGUE='" + catalogue + "' AND DEPOT='" + depot + "' AND PARTITION='" + produit + "' AND CLASSE='" + classe + "' AND ZT_ID_DEBUT='" + zt_id_nc + "'"
                        arcpy.AddMessage(sql)
                        self.Sib.execute(sql)
                        
                    #Initialiser le compteur d'�l�ment
                    nb_elem = 0
                    #V�rifier si au moins un �l�ment est s�lectionn�
                    if len(desc.fidSet) > 0:
                        #Traiter tous les �l�ments s�lectionn�s du FeatureLayer
                        for row in arcpy.SearchCursor(featureLayer):
                            #Extraire la g�om�trie de l'�l�ment
                            geometrie = row.getValue("Shape")
                            #V�rifier si le polygon contient l'�l�ment
                            if polygonZT.contains(geometrie):
                                #Compter les �l�ments ajout�s
                                nb_elem = nb_elem + 1
                                #Ajouter un �l�ment non-conforme d'une classe
                                sql = "INSERT INTO F705_EL VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + no_nc + "','" + catalogue + "','" + depot + "','" + produit + "','" + classe + "'"
                                sql = sql + "," + str(row.getValue(object_id)) + ",'" + str(row.getValue(bdg_id)) + "','" + zt_id_nc + "',NULL,NULL)"
                                arcpy.AddMessage(sql)
                                self.Sib.execute(sql)
                            
                    #Si aucun �l�ment s�lectionn�
                    if nb_elem == 0:
                        #Ajouter une clase non-conforme sans �l�ment
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
        
        #Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    #Gestion des erreurs
    try:   
        #Initialisation des valeurs par d�faut
        env                 = "SIB_PRO"
        no_nc               = ""
        catalogue           = ""
        depot               = ""
        produit             = ""
        featureLayerZT      = ""
        attributZT          = ""
        listeFeatureLayer   = ""
        detruire            = False
        
        #Extraction des param�tres d'ex�cution
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
        
        #Instanciation de la classe d'identification des �l�ments non-conformes.
        oIdentifierElementZtNonConforme = IdentifierElementZtNonConforme()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oIdentifierElementZtNonConforme.validerParamObligatoire(env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer)
        
        #Ex�cuter le traitement d'identification des �l�ments non-conformes.
        arcpy.AddMessage("- Ex�cuter l'identification des �l�ments non-conformes.")
        oIdentifierElementZtNonConforme.executer(env, no_nc, catalogue, depot, produit, featureLayerZT, attributZT, listeFeatureLayer, detruire)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)