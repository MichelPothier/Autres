#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : AfficherInfoContrainteCatalogue.py
# Auteur    : Michel Pothier
# Date      : 05 mars 2015

"""
    Application qui permet d'afficher l'information sur les contraintes d'int�grit� pour les classes selon un catalogue. 
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue.
                            d�faut = 1:BDG
    sousCatalogue   OB      Num�ro du sous-catalogue de classes.
                            d�faut =
    classe          OP      Nom d'une classe contenue dans le catalogue sp�cifi�.
                            d�faut = 
    codeSpec        OP      Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
                            d�faut = 
    contrainte      OP      Nom des containtes recherch�es.
                            d�faut = <Toutes les contraintes contenues dans le catalogue>
                            Attention : La contrainte est choisie en fonction de son identifiant.
                            identifiant:Nom de la contrainte
                            16904:Valider un masque spatial
                            116088:Valider le domaine d'attribut
                            30718640:Proximit�
                            131019:Filtrage  
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        AfficherInfoContrainteCatalogue.py env catalogue sousCatalogue [classe] [codeSpec] [contrainte]
    
    Exemple:
        AfficherInfoContrainteCatalogue.py CATREL_PRO 1:BDG 92711:BDG-RHN NHN_HHYD_WATERBODY_2 "1480002:R�gion hydrique" #
    
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherInfoContrainteCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class AfficherInfoContrainteCatalogue(object):
#*******************************************************************************************
    """
    Permet d'afficher l'information sur les contraintes d'int�grit� pour les classes selon un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher l'information sur les contraintes d'int�grit� pour les classes selon un catalogue.
        
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
    def validerParamObligatoire(self, env, catalogue, sousCatalogue):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        
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
        if (len(sousCatalogue) == 0):
            raise Exception ('Param�tre obligatoire manquant: sousCatalogue')
        
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
    def afficherSousCatalogue(self, catalogue, sousCatalogue):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les sous-catalogues
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier si le sous-catalogue est valide
        sql = ("SELECT FEAT_CATAL_ID, FEAT_CATAL_NAME_FR, FEAT_CATAL_NAME_EN"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND FEAT_CATAL_ID=" + sousCatalogue.split(":")[0] + " ")
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Num�ro du sous-catalogue invalide : " + sousCatalogue)
        
        #Afficher l'information
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Sous-catalogue : " + str(resultat[0][0]) + ":" + resultat[0][1])
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherClasse(self, catalogue, sousCatalogue, classe, codeSpec, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les classes pour un catalogue.
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        contrainte      : Nom d'une containte li�e au code sp�cifique.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier si la classe est valide
        sql = ("SELECT DISTINCT B.FEAT_TYPE_NAME_DATABASE"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND FEAT_CATAL_ID=" + sousCatalogue.split(":")[0] + " ")
        #V�rifier si la classe est pr�sente
        if len(classe) > 0:
            #Ajouter le nom de la classe � rechercher
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE='" + classe + "'"
        #Si la classe est absente
        else:
            #Ajouter le nom de la classe � rechercher
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IS NOT NULL"
        #Ajouter le tri � la SQL
        sql =sql + " ORDER BY B.FEAT_TYPE_NAME_DATABASE"
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Nom de la classe invalide : " + classe)
        
        #Traiter tous les r�sultats
        for item in resultat:
            #Afficher l'information
            arcpy.AddMessage(" ")
            arcpy.AddMessage("Classe : " + item[0])
            
            #Afficher l'information selon le code sp�cifique
            self.afficherCodeSpec(catalogue, sousCatalogue, item[0], codeSpec, contrainte)
            
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCodeSpec(self, catalogue, sousCatalogue, classe, codeSpec, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les codes sp�cifiques pour une ou plusieurs classes.
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        contrainte      : Nom d'une containte li�e au code sp�cifique.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier si le codeSpec est valide
        sql = ("SELECT DISTINCT B.FEAT_TYPE_CODE_BD, upper(B.FEAT_TYPE_NAME_FR)"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK")
        #V�rifier si la classe est pr�sente
        if classe <> None:
            #Ajouter le nom du code sp�cifique � rechercher
            sql = sql +  " AND B.FEAT_TYPE_NAME_DATABASE='" + classe + "'"       
        #Si la classe est absente
        else:
            #Ajouter le nom du code sp�cifique � rechercher
            sql = sql + " AND B.FEAT_TYPE_NAME_DATABASE IS NULL"
        #V�rifier si le codeSpec est pr�sent
        if len(codeSpec) > 0:
            #Ajouter le nom du code sp�cifique � rechercher
            sql = sql + " AND B.FEAT_TYPE_CODE_BD=" + codeSpec
        #Ajouter le tri � la SQL
        sql =sql + " ORDER BY B.FEAT_TYPE_CODE_BD"
        
        #Ex�cuter la requ�te SQL
        #arcpy.AddMessage(sql)
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Code sp�cifique invalide : " + codeSpec)
        
        #Afficher l'information
        codeGenerique = str(((resultat[0][0]/10000)*10000) + 9)
        arcpy.AddMessage("  CodeGen : " + str(codeGenerique)) 
        #Afficher l'information du code g�n�rique selon la contrainte
        self.afficherContrainte(catalogue, sousCatalogue, classe, codeGenerique, contrainte, "    Aucune contrainte g�n�rique")
        
       #Traiter tous les r�sultats
        for item in resultat:
            #Afficher l'information
            arcpy.AddMessage("  CodeSpec : " + str(item[0]) + ":" + str(item[1])) 
            #Afficher l'information selon la contrainte
            self.afficherContrainte(catalogue, sousCatalogue, classe, str(item[0]), contrainte, "    Aucune contrainte sp�cifique")
            
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def afficherContrainte(self, catalogue, sousCatalogue, classe, codeSpec, contraite, message=""):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information pour toutes les contraintes d'un code sp�cifique
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        contrainte      : Nom d'une containte li�e au code sp�cifique.
        message         : Message associ� � la contrainte.
        
        Variables:
        ----------
        sql             : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier les contraintes
        sql = ("select C.constraint_id, CC.phys_const_id, CC.phys_const_name_fr"
               "  from feat_catalogue A, feat_type B, constraint C, phys_const CC"
               " where A.feat_catal_id=B.feat_catal_fk"
               "   and A.feat_catal_type=" + catalogue.split(":")[0] + " and B.feat_type_code_bd=" + codeSpec + " "
               "   and B.feat_type_id=C.feat_type_fk" 
               "   and C.phys_const_fk=CC.phys_const_id")
        
        #V�rifier si les contraintes sont pr�sentes
        if len(contraite) > 0:
            #Cr�er la liste SQL des contraintes
            listeId = ""
            for item in contrainte.split(","):
                id = item.split(":")[0]
                if listeId == "":
                    listeId = listeId + id
                else:
                    listeId = listeId + "," + id
            #Ajouter les contraintes � rechercher
            sql = sql + " and CC.phys_const_id in (" + listeId + ")"
            
        #Ajouter le tri � la SQL
        sql = sql + " order by C.constraint_id, CC.phys_const_id"
        
        #Ex�cuter la requ�te SQL
        #arcpy.AddMessage(sql)
        resultat = self.BDG.query(sql)
        #arcpy.AddMessage(str(resultat))
        
        #V�rifier le r�sultat
        if resultat:
            #Traiter tous les r�sultats des contraintes
            for item in resultat:
                #Afficher l'information
                arcpy.AddMessage("    " + str(item[1]) + ":" + item[2] + " (ID Contrainte:" + str(item[0]) + ")")
                
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
                    #V�rifier si la contrainte est : Valider le domaine d'attribut=116088
                    if item[1] == 116088:
                        #Cr�er la requ�te SQL pour extraire le nom de l'attribut et l'expression r�guli�re
                        sql = ("select EE.const_param_name_fr, F.p_value"
                               "  from parameter E, p_value F, const_param EE"
                               " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=F.parameter_fk and E.const_param_fk=EE.const_param_id")
                        #Ex�cuter la requ�te SQL
                        #arcpy.AddMessage(sql)
                        valResultat = self.BDG.query(sql)
                        #Traiter tous les r�sultats
                        for val in valResultat:
                            #Afficher l'information sur le masque spatial
                            arcpy.AddMessage("      " + val[0] + "=" + val[1])
                    
                    #V�rifier si la contrainte est : Valider un masque spatial=16904
                    elif item[1] == 16904:
                        #V�rifier si une relation est d�j� pr�sente
                        if present:
                            #Afficher un 'ou'
                            arcpy.AddMessage("                  ou")
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
                            arcpy.AddMessage("      (" + val[1] + "), " + val[2] + ", " + val[3])
                        
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
                            arcpy.AddMessage("      " + str(cls[2]) + ": " + str(cls[3]) + ": " + cls[4])
                        
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
                            arcpy.AddMessage("      " + att[2])
                    
                    #V�rifier si la contrainte est :
                    #Fltrage=131019, Proximit�=30718640, Tol�rances de changement=, Dimensions minimales externes, Dimensions minimales internes, etc
                    else:
                        #Cr�er la requ�te SQL pour extraire la largeur et la longueur
                        sql = ("select EE.const_param_name_fr, F.p_value"
                               "  from parameter E, p_value F, const_param EE"
                               " where E.rel_id_fk=" + str(rel[0]) + " and E.parameter_id=F.parameter_fk and E.const_param_fk=EE.const_param_id")
                        #Ex�cuter la requ�te SQL
                        #arcpy.AddMessage(sql)
                        valResultat = self.BDG.query(sql)
                        #Traiter tous les r�sultats
                        for val in valResultat:
                            #Afficher l'information sur le masque spatial
                            arcpy.AddMessage("      " + val[0] + "=" + val[1])
                        
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
                            arcpy.AddMessage("      " + str(cls[2]) + ": " + str(cls[3]) + ": " + cls[4])
                        
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
                            arcpy.AddMessage("      " + att[2])

                #Afficher l'information sur le masque spatial
                arcpy.AddMessage(" ")
                        
        #Si aucune contrainte
        else:
            #Envoyer un message d'avertissement
            arcpy.AddWarning(message)
            arcpy.AddMessage(" ")
            
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, sousCatalogue, classe, codeSpec, contrainte):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour afficher l'information sur les contraintes d'int�grit� pour les classes selon un catalogue.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        contrainte      : Nom d'une containte li�e au code sp�cifique.
               
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
        arcpy.AddMessage("- Affichage de l'information sur les contraintes")
        
        #Afficher l'information
        self.afficherCatalogue(catalogue)
        
        #Afficher l'information
        self.afficherSousCatalogue(catalogue, sousCatalogue)
        
        #Afficher l'information
        self.afficherClasse(catalogue, sousCatalogue, classe, codeSpec, contrainte)
        
        #Fermeture de la connexion de la BD BDG
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
        sousCatalogue   = ""
        classe          = ""
        codeSpec        = ""
        contrainte      = ""
        
        #Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]
        
        if len(sys.argv) > 3:
            sousCatalogue = sys.argv[3]
        
        if len(sys.argv) > 4:
            if sys.argv[4] <> "#":
                classe = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            if sys.argv[5] <> "#":
                codeSpec = sys.argv[5].split(":")[0]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                contrainte = sys.argv[6].replace(";",",").replace("'","")
        
        #D�finir l'objet pour afficher l'information sur les contraintes d'int�grit� pour les classes selon un catalogue.
        oAfficherInfoContrainteCatalogue = AfficherInfoContrainteCatalogue()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oAfficherInfoContrainteCatalogue.validerParamObligatoire(env, catalogue, sousCatalogue)
        
        #Ex�cuter le traitement pour afficher l'information sur les contraintes d'int�grit� pour les classes selon un catalogue.
        oAfficherInfoContrainteCatalogue.executer(env, catalogue, sousCatalogue, classe, codeSpec, contrainte)
    
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