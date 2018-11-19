#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : AfficherInfoMasqueSpatialCatalogue.py
# Auteur    : Michel Pothier
# Date      : 13 avril 2015

"""
    Application qui permet d'afficher l'information sur les contraintes d'int�grit� de type masque spatial pour les classes selon un catalogue. 
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue.
                            d�faut = 1:BDG
    relation        OB      Liste des masques spatiaux � afficher.
                            d�faut = 
    classe          OP      Nom des classes contenues dans le catalogue sp�cifi� qui poss�dent les relations.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        AfficherInfoMasqueSpatialCatalogue.py env catalogue relation [classe]
    Exemple:
        AfficherInfoMasqueSpatialCatalogue.py CATREL_PRO 1:BDG "(1*T,***,T**): CHEVAUCHE 1/1" BDG_AIRE_DESIGNEE_0;NHN_HHYD_WATERBODY_2
    
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherInfoMasqueSpatialCatalogue .py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class AfficherInfoMasqueSpatialCatalogue(object):
#*******************************************************************************************
    """
    Permet d'afficher l'information sur les contraintes d'int�grit� de type masque spatial pour les classes selon un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher l'information sur les contraintes d'int�grit� de type masque spatial pour les classes selon un catalogue.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteBDG : Objet utilitaire pour la gestion des connexion � BDG.
        
        """
        
        #D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, catalogue, relation):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        catalogue       : Num�ro du catalogue.
        relation        : Liste des masques spatiaux � afficher.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Valider la pr�sence
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')
        
        #Valider la pr�sence
        if (len(catalogue) == 0):
            raise Exception ('Param�tre obligatoire manquant: catalogue')
        
        #Valider la pr�sence
        if (len(relation) == 0):
            raise Exception ('Param�tre obligatoire manquant: relation')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCatalogue(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur le catalogue
        
        Param�tres:
        -----------
        catalogue    : Num�ro du catalogue.
        
        Variables:
        ----------
        sql         : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier si le catalogue est valide
        sql = "SELECT DISTINCT FEAT_CATAL_TYPE FROM FEAT_CATALOGUE WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " "
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #Afficher l'information
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Catalogue : " + catalogue)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherRelation(self, catalogue, relation, classe):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les relations.
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        relation        : Liste des masques spatiaux � afficher.
        classe          : Nom des classes contenues dans le catalogue sp�cifi�.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Initialisation de la liste des masques spatials
        masque=""
        
        #Traiter toutes les relations
        for msk in relation.split(";"):
            #Construire la liste des masques
            masque = masque + "'" + msk.split(":")[0] + "',"
        #Enlever la derni�re virgule
        masque = masque[:-1]
    
        #Cr�er la requ�te SQL pour v�rifier les contraintes
        sql = ("SELECT DISTINCT D.CONSTRAINT_FK, B.FEAT_TYPE_NAME_DATABASE, B.FEAT_TYPE_CODE_BD, B.FEAT_TYPE_NAME_FR"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B, CONSTRAINT C, PHYS_CONST CC, RELATION D, PARAMETER E, P_VALUE F, EGEN_MASK KK"
               " WHERE A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " "
               "   AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.PHYS_CONST_FK=CC.PHYS_CONST_ID"
               "   AND C.CONSTRAINT_ID=D.CONSTRAINT_FK AND D.RELATION_ID=E.REL_ID_FK"
               "   AND E.PARAMETER_ID=F.PARAMETER_FK AND F.EGEN_MASK_FK=KK.EGEN_MASK_ID"
               "   AND KK.EGEN_MASK_VIEW_MASK_S IN (" + masque + ")")
        #V�rifier si les classes sont sp�cifi�es
        if len(classe) > 0:
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IN ('" + classe.replace(",","','") + "')"
        #else:
            #sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IS NOT NULL"
        #Ajouter le tri
        sql = sql + " ORDER BY B.FEAT_TYPE_CODE_BD, D.CONSTRAINT_FK"
        #Ex�cuter la requ�te SQL
        #arcpy.AddMessage(sql)
        resultat = self.BDG.query(sql)

        #Traiter tous les r�sultats des contraintes
        for item in resultat:
            #Cr�er la requ�te SQL pour extraire toutes les relations de la contrainte
            sql = ("select D.relation_id"
                   "  from relation D"
                   " where D.constraint_fk=" + str(item[0]) + " "
                   "   order by D.relation_id")
            #Ex�cuter la requ�te SQL
            #arcpy.AddMessage(sql)
            relResultat = self.BDG.query(sql)
            
            #Identifier qu'aucune relation n'est pr�sente
            present = False
            
            #Traiter toutes les relations de la contraintes
            for rel in relResultat:
                #V�rifier si une relation est d�j� pr�sente
                if present:
                    #Afficher un 'ou'
                    arcpy.AddMessage("  ou")
                else:
                    #Afficher la classe
                    arcpy.AddMessage(" ")
                    arcpy.AddMessage(str(item[1]) + ": " + str(item[2]) + ": " + item[3])
                #Indiquer qu'une relation est pr�sente
                present=True
                
                #Cr�er la requ�te SQL pour extraire toutes les relations de la contrainte
                sql = ("select F.egen_mask_fk, F.egen_cardinality, KK.egen_mask_name_fr, KK.egen_mask_view_mask_s, F.egen_expect"
                       "  from parameter E, p_value F, egen_mask KK"
                       " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=F.parameter_fk and F.egen_mask_fk=KK.egen_mask_id")
                #Ex�cuter la requ�te SQL
                #arcpy.AddMessage(sql)
                valResultat = self.BDG.query(sql)
                #Traiter tous les r�sultats
                for val in valResultat:
                    #Afficher l'information sur le masque spatial
                    arcpy.AddMessage("  (" + val[1] + "), " + val[2] + ", " + val[3])
                
                #Cr�er la requ�te SQL pour extraire toutes les classes en relation
                sql = ("select H.feat_list_id, H.feat_fk, B.feat_type_name_database, B.feat_type_code_bd, B.feat_type_name_fr"
                       "  from parameter E, feat_list H, feat_type B"
                       " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=H.param_feat_fk and H.feat_fk=B.feat_type_id")
                #Ex�cuter la requ�te SQL
                #arcpy.AddMessage(sql)
                clsResultat = self.BDG.query(sql)
                #Traiter tous les r�sultats
                for cls in clsResultat:
                    #Afficher l'information sur les classes en relation
                    arcpy.AddMessage("  " + str(cls[2]) + ": " + str(cls[3]) + ": " + cls[4])
                
                #Cr�er la requ�te SQL pour extraire tous les attributs en relation
                sql = ("select G.attr_list_id, G.attr_fk, GG.feat_attr_name_database"
                       "  from parameter E, attr_list G, feat_attr GG"
                       " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=G.param_attr_fk and G.attr_fk=GG.feat_attr_id")
                #Ex�cuter la requ�te SQL
                #arcpy.AddMessage(sql)
                attResultat = self.BDG.query(sql)
                #Traiter tous les r�sultats
                for att in attResultat:
                    #Afficher l'information sur les attributs en relation
                    arcpy.AddMessage("  " + att[2])
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, relation, classe):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour afficher l'information sur les contraintes d'int�grit� de type masque spatial pour les classes selon un catalogue.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        catalogue       : Num�ro du catalogue.
        relation        : Liste des masques spatiaux � afficher.
        classe          : Nom des classes contenues dans le catalogue sp�cifi�.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requ�te SQL � ex�cuter.
        """
        
        #Instanciation de la classe BDG et connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Affichage de l'information
        arcpy.AddMessage("- Affichage de l'information sur les masques spatiaux")
        
        #Afficher l'information sur le catalogue
        self.afficherCatalogue(catalogue)
        
        #Afficher l'information sur les relations
        self.afficherRelation(catalogue, relation, classe)
        
        #Fermeture de la connexion de la BD BDG
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion BDG")
        self.BDG.close()
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env             = "CATREL_PRO"
        catalogue       = "1:BDG"
        relation        = ""
        classe          = ""
        
        #Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]
        
        if len(sys.argv) > 3:
            relation = sys.argv[3].upper().replace("'","")
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                classe = sys.argv[4].upper().replace(";",",")
        
        #D�finir l'objet pour afficher l'information sur les contraintes d'int�grit� de type masque spatial pour les classes selon un catalogue.
        oAfficherInfoMasqueSpatialCatalogue = AfficherInfoMasqueSpatialCatalogue()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oAfficherInfoMasqueSpatialCatalogue.validerParamObligatoire(env, catalogue, relation)
        
        #Ex�cuter le traitement pour afficher l'information sur les contraintes d'int�grit� de type masque spatial pour les classes selon un catalogue.
        oAfficherInfoMasqueSpatialCatalogue.executer(env, catalogue, relation, classe)
    
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