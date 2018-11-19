#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : ValiderDomaineValeurGeodatabaseCatalogue.py
# Auteur    : Michel Pothier
# Date      : 09 mars 2015

"""
    Application qui permet de valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.

    Le catalogue contient des expressions r�guli�res de validation pour chaque attribut (variable ou cod�) d'un code sp�cifique.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue.
                            d�faut = 1:BDG
    classe          OB      Liste des noms de classe du catalogue � valider.
                            d�faut = <Toutes les classes pr�sentes dans le catalogue>
    attribut        OB      Liste des noms d'attribut du catalogue � valider.
                            d�faut = <Tous les attributs pr�sents dans le catalogue>
    workspace       OB      Nom de la g�odatabase contenant les donn�es � valider.
                            d�faut = "Database Connections\BDRS_PRO.sde"
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        ValiderDomaineValeurGeodatabaseCatalogue.py env catalogue classe attribut workspace

    Exemple:
        ValiderDomaineValeurGeodatabaseCatalogue.py CATREL_PRO 1:BDG NHN_HHYD_WATERBODY_2,NHN_HNET_NETWORK_LINEAR_FLOW_1 WATER_DEFINITION,PERMANENCY "Database Connections\BDRS_PRO.sde"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderDomaineValeurGeodatabaseCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, re, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class ValiderDomaineValeurGeodatabaseCatalogue(object):
#*******************************************************************************************
    """
    Permet de valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        
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
    def validerParamObligatoire(self, env, catalogue, workspace, classe, attribut):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        #Valider la pr�sence
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')
        
        #Valider la pr�sence
        if (len(catalogue) == 0):
            raise Exception ('Param�tre obligatoire manquant: catalogue')
        
        #Valider la pr�sence
        if (len(classe) == 0):
            raise Exception ('Param�tre obligatoire manquant: classe')
        
        #Valider la pr�sence
        if (len(attribut) == 0):
            raise Exception ('Param�tre obligatoire manquant: attribut')
        
        #Valider la pr�sence
        if (len(workspace) == 0):
            raise Exception ('Param�tre obligatoire manquant: workspace')
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerValeurParam(self, catalogue, workspace):
    #-------------------------------------------------------------------------------------
        """
        Validation des valeurs des param�tres.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
         
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Envoyer un message
        arcpy.AddMessage("- V�rification des valeurs des param�tres")
        
        #Cr�er la requ�te SQL pour v�rifier si le catalogue est valide
        arcpy.AddMessage("- V�rifier si le catalogue est valide")
        sql = ("SELECT DISTINCT FEAT_CATAL_TYPE FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " ")
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #V�rifier si le Workspace est valide
        arcpy.AddMessage("- V�rifier si le Workspace est valide")
        #V�rifier si le Workspace est absent
        if not arcpy.Exists(workspace):
            #Envoyer une exception
            raise Exception("Workspace absent : " + workspace)
        #V�rifier si le Workspace est invalide
        if arcpy.Describe(workspace).DataType <> "Workspace":
            #Envoyer une exception
            raise Exception("Workspace invalide : " + workspace)
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def validerDomaineAttributClasse(self, catalogue, cls, codeGen, attribut, workspace, codeSpec='CODE_SPEC'):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider les valeurs d'un attribut cod� pour une classe de la G�odatabase en fonction du domaine contenu dans le catalogue.
        
        Param�tres:
        -----------
        catalogue   : Num�ro du catalogue.
        cls         : Nom de la classe du catalogue � valider.
        codeGen     : Code g�n�rique de la classe du catalogue � valider.
        attribut    : Liste des noms d'attribut du catalogue � valider.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
        codeSpec    : Nom de l'attribut de la G�odatabase contenant le code sp�cifique.
        
        Variables:
        ----------
        sql                 : Requ�te SQL � ex�cuter.
        att                 : Nom de l'attribut et du code sp�cifique � traiter.
        attResultat         : Liste des attributs et codes sp�cifiques � traiter.
        valCatalogue        : Ensemble des valeurs d'attributs du catalogue � traiter.
        attCatalogueErr     : Ensemble des valeurs attributs du catalogue en erreur.
        valGeodatabase      : Ensemble des valeurs d'attributs du catalogue � traiter.
        attGeodatabaseErr   : Ensemble des valeurs d'attributs du catalogue en erreur.
        """
        
        #Cr�er la SQL pour d�finir la liste des attributs � valider avec des expressions r�guli�res
        sql =  (" select distinct F.p_value"
                "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk and E.const_param_fk=116089"
                "   and (B.feat_type_name_database='" + cls + "' or B.feat_type_code_bd=" + codeGen + ") and F.p_value in ('" + attribut.replace(",","','") + "')"
                " order by F.p_value")
        #arcpy.AddMessage(sql)
        #Ex�cuter la SQL
        attResultat = self.BDG.query(sql)
        
        #Traiter tous les attributs qui poss�dent une expression r�guli�re � valider
        for att in attResultat:
            #Afficher l'attribut � valider
            arcpy.AddMessage("  " + att[0])
            
            #Cr�er la SQL pour d�finir l'ensemble des valeurs de la G�odatabase
            sql = "select distinct " + codeSpec + "," + att[0] + " from BDG_DBA." + cls + " order by " + codeSpec + "," + att[0]
            #arcpy.AddMessage(sql)
            try:
                #Ex�cuter la SQL
                valResultat = self.SDE.execute(sql)
            #Gestion des erreurs
            except Exception, err:
                #Afficher l'erreur
                arcpy.AddMessage(sql)
                arcpy.AddError(err.message)
                valResultat = False
            
            #V�rifier la pr�sence d'un r�sultat
            if valResultat and type(valResultat) == list:
                #Traiter tous les r�sultats des valeurs de la G�odatabase
                for val in valResultat:
                    #Afficher la valeurl'attribut � valider
                    #arcpy.AddMessage("    " + str(val[0]) + ", valeur=" + str(val[1]))
                    
                    #Cr�er la SQL pour extraire le nom du code sp�cifique et le num�ro de relation
                    sql =  (" select D.relation_id, B.feat_type_code_bd, B.feat_type_name_fr"
                            "  from feat_catalogue A, feat_type B, constraint C, relation D, parameter E, p_value F"
                            " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                            "   and B.feat_type_id=C.feat_type_fk and C.constraint_id=D.constraint_fk and C.phys_const_fk=116088"
                            "   and D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk"
                            "   and (B.feat_type_code_bd=" + str(val[0]) + "or B.feat_type_code_bd=" + codeGen + ") AND F.p_value='" + att[0] + "'")
                    #arcpy.AddMessage(sql)
                    #Ex�cuter la SQL
                    relResultat = self.BDG.query(sql)
                    #V�rifier le r�sultat
                    if relResultat:
                        #Afficher la valeur de l'attribut � valider
                        #arcpy.AddMessage("      " + str(relResultat[0][1]) + ":" + relResultat[0][2] + " (rel=" + str(relResultat[0][0]) + ")")
                        
                        #Cr�er la SQL pour extraire l'expression r�guli�re du code sp�cifique
                        sql =  (" select F.p_value"
                                "  from relation D, parameter E, p_value F"
                                " where D.relation_id=E.rel_id_fk and E.parameter_id=F.parameter_fk and E.const_param_fk=116090 and D.relation_id=" + str(relResultat[0][0]))
                        #arcpy.AddMessage(sql)
                        #Ex�cuter la SQL
                        expResultat = self.BDG.query(sql)
                        #V�rifier le r�sultat
                        if expResultat:
                            #Afficher la valeurl'attribut � valider
                            #arcpy.AddMessage("      Expression=" + expResultat[0][0])
                            try:
                                #V�rifier si la valeur respecte l'expression r�guli�re
                                if not re.match(expResultat[0][0], str(val[1])):
                                    #Afficher la valeur de l'attribut � valider
                                    arcpy.AddMessage("      " + str(relResultat[0][1]) + ":" + relResultat[0][2] + " (rel=" + str(relResultat[0][0]) + ")")
                                    #Afficher un message d'erreur
                                    arcpy.AddWarning("      Valeur invalide : " + str(val[1]) + ", " + expResultat[0][0])
                            #Gestion des erreurs
                            except Exception, err:
                                #Afficher la valeur de l'attribut � valider
                                arcpy.AddMessage("      " + str(relResultat[0][1]) + ":" + relResultat[0][2] + " (rel=" + str(relResultat[0][0]) + ")")
                                #Afficher un message d'erreur
                                arcpy.AddError("      Expression r�guli�re invalide : " + str(val[1]) + ", " + expResultat[0][0])
                        else:
                            #Afficher un message d'erreur
                            arcpy.AddError("Aucune expression r�guli�re : " + str(val[1]))
                    else:
                        #Afficher un message d'erreur
                        arcpy.AddError("Aucune relation : " + att[0])
                        
        #Sortir
        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, classe, attribut, workspace):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du catalogue.
        classe      : Liste des noms de classe contenus dans la g�odatabase utilis�s pour cr�er les domaines.
        attribut    : Liste des noms d'attribut cod�s � traiter selon les classes s�lectionn�es.
        workspace   : Nom de la g�odatabase contenant les valeurs d'attribut � valider.
        
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requ�te SQL � ex�cuter.
        """
        
        #V�rification de la pr�sence des param�tres obligatoires
        self.validerParamObligatoire(env, catalogue, classe, attribut, workspace)
        
        #V�rifier la connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #V�rifier la connexion � SDE
        arcpy.AddMessage("- Connexion � SDE")
        self.SDE = arcpy.ArcSDESQLExecute(workspace)
        
        #Valider les valeurs des param�tres
        self.validerValeurParam(catalogue, workspace)
        
        #Envoyer un message
        arcpy.AddMessage("- Valider les valeurs des attributs de chaque classe entre le catalogue et la G�odatabase")
        
        #Cr�er la SQL pour extraire le code g�n�rique de chaque classe � valider
        sql =  (" select distinct B.feat_type_name_database, substr(to_char(B.feat_type_code_bd),1,3)||'0009'"
                "  from feat_catalogue A, feat_type B"
                " where A.feat_catal_type=" + catalogue.split(":")[0] + " and A.feat_catal_id=B.feat_catal_fk"
                "   and B.feat_type_name_database in ('" + classe.replace(",","','") + "')"
                " order by B.feat_type_name_database")
        #arcpy.AddMessage(sql)
        #Ex�cuter la SQL
        resultat = self.BDG.query(sql)
        
        #Traiter toutes les classes � valider
        for cls in resultat:
            #Afficher un s�parateur
            arcpy.AddMessage(" ")
        
            #Afficher le nom de la classe avec son code g�n�rique
            arcpy.AddMessage(cls[0] + ":"+ cls[1])
        
            #Valider les valeurs des attributs pour une classe en fonction des expressions r�guli�res du catalogue
            self.validerDomaineAttributClasse(catalogue, cls[0], cls[1], attribut, workspace)
            
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
        env         = "CATREL_PRO"
        catalogue   = "1:BDG"
        classe      = ""
        attribut    = ""
        workspace   = "Database Connections\BDRS_PRO.sde"
        
        #Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            catalogue = sys.argv[2]

        if len(sys.argv) > 3:
            classe = sys.argv[3].upper().replace(";",",")
        
        if len(sys.argv) > 4:
            attribut = sys.argv[4].upper().replace(";",",").replace("'","")
        
        if len(sys.argv) > 5:
            workspace = sys.argv[5]
        
        #D�finir l'objet pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oValiderDomaineValeurGeodatabaseCatalogue = ValiderDomaineValeurGeodatabaseCatalogue()
        
        #Ex�cuter le traitement pour valider les domaines des valeurs d'attributs d'une g�odatabase en fonction de l'information contenue dans un catalogue.
        oValiderDomaineValeurGeodatabaseCatalogue.executer(env, catalogue, classe, attribut, workspace)
            
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