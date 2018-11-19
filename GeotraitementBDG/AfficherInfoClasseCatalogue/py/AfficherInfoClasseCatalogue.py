#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom : AfficherInfoClasseCatalogue.py
# Auteur    : Michel Pothier
# Date      : 16 f�vrier 2015

"""
    Application qui permet d'afficher l'information sur les classes et attributs selon un catalogue. 
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [CATREL_PRO/CATREL_TST/CATREL_DEV]
                            d�faut = CATREL_PRO
    catalogue       OB      Num�ro du catalogue.
                            d�faut = 1:BDG
    sousCatalogue   OB      Num�ro du sous-catalogue de classes.
                            d�faut =
                            Exemple:
                              92713:BDG-Classes actives (4.0.2)
    classe          OP      Nom d'une classe contenue dans le sous-catalogue sp�cifi�.
                            d�faut = 
    codeSpec        OP      Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
                            d�faut = 
    attribut        OP      Nom d'un attribut li� au code sp�cifique.
                            d�faut = 
    listeValeur     OP      Liste des valeurs d'attributs cod�s li�es au nom d'attribut sp�cifi�.
                            Aucune valeur n'est pr�sente si l'attribut n'est pas cod�.
                            d�faut = 
    complet         OP      Indique si l'affichage doit �tre complet (True) ou partiel (False).
                            d�faut = False
    
    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        AfficherInfoClasseCatalogue.py env catalogue sousCatalogue [classe] [codeSpec] [attribut] [valeur]

    Exemple:
        AfficherInfoClasseCatalogue.py CATREL_PRO 1:BDG "92713:BDG-Classes actives (4.0.2)" NHN_HHYD_WATERBODY_2 "1480002:R�gion hydrique" WATER_DEFINITION "0:Aucun;1:Canal"

"""

__catalogue__ = "--catalogue-- : 1"
__revision__ = "--REVISION-- : $Id: AfficherInfoClasseCatalogue.py 1111 2016-06-15 19:51:31Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, cx_Oracle, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteBDG

#*******************************************************************************************
class AfficherInfoClasseCatalogue(object):
#*******************************************************************************************
    """
    Permet d'afficher l'information sur les classes d'un cataloguee.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour afficher l'information sur les classes d'un catalogue.
        
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
    def validerParamObligatoire(self, env, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env         : Type d'environnement.
        catalogue   : Num�ro du sous-catalogue.
        
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
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCatalogue(self, catalogue):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les catalogues
        
        Param�tres:
        -----------
        catalogue     : Num�ro de la catalogue du sousCatalogue.
        
        Variables:
        ----------
        sql         : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Afficher l'information
        arcpy.AddMessage(" ")
        arcpy.AddMessage("Catalogue")
        
        #Cr�er la requ�te SQL pour v�rifier si la catalogue est valide
        #arcpy.AddMessage("- V�rifier si la catalogue est valide : " + catalogue)
        sql = "SELECT DISTINCT FEAT_CATAL_TYPE FROM FEAT_CATALOGUE WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " "
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Catalogue invalide : " + catalogue)
        
        #Traiter tous les r�sultats
        for item in resultat:
            #Afficher l'information compl�te
            if complet:
                #Afficher l'information
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_TYPE = " + str(item[0]))
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage(" " + catalogue)
        
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
        sql         : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Afficher l'information
        arcpy.AddMessage("Sous-catalogue")
        
        #Cr�er la requ�te SQL pour v�rifier si le nom du sousCatalogue est valide
        #arcpy.AddMessage("- V�rifier si le nom du sousCatalogue est valide : " + sousCatalogue)
        sql = ("SELECT FEAT_CATAL_ID,FEAT_CATAL_NAME_FR,FEAT_CATAL_NAME_EN,FEAT_CATAL_BDG_VER_NUM,FEAT_CATAL_VERSION_DATE"
               "  FROM FEAT_CATALOGUE"
               " WHERE FEAT_CATAL_TYPE=" + catalogue.split(":")[0])
        #V�rifier si le sousCatalogue est pr�sent
        if len(sousCatalogue) > 0:
            #Ajouter le nom du sousCatalogue � rechercher
            sql = sql + " AND FEAT_CATAL_ID='" + sousCatalogue.split(":")[0] + "'"
        #Ajouter le tri � la SQL
        sql =sql + " ORDER BY FEAT_CATAL_NAME_FR"
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Num�ro du sous-catalogue invalide : " + sousCatalogue)
        
        #Traiter tous les r�sultats
        for item in resultat:
            #Afficher l'information compl�te
            if complet:
                #Afficher l'information
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_ID = " + str(item[0]))
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_NAME_FR = '" + item[1] + "'")
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_NAME_EN = '" + item[2] + "'")
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_BDG_VER_NUM = '" + str(item[3]) + "'")
                arcpy.AddMessage(" FEAT_CATALOGUE.FEAT_CATAL_VERSION_DATE = '" + str(item[3]) + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage(" " + str(item[0]) + " : " + item[1] + " / " + item[2] + " (" + str(item[3]) + ")")
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherClasse(self, catalogue, sousCatalogue, classe):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les classes
        
        Param�tres:
        -----------
        catalogue       : Num�ro de la catalogue du sousCatalogue.
        sousCatalogue   : Num�ro du sous-catalogue pour un groupe de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        attribut        : Nom d'un attribut li� au code sp�cifique.
        listeValeur     : Liste des valeurs d'attributs cod�s li�es au nom d'attribut sp�cifi�.
        complet         : Indique si l'affichage doit �tre complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier si la classe est valide
        sql = ("SELECT DISTINCT B.FEAT_TYPE_NAME_DATABASE"
               "  FROM FEAT_CATALOGUE A, FEAT_TYPE B"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND FEAT_CATAL_ID='" + sousCatalogue.split(":")[0] + "'")
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
            #Afficher l'information compl�te
            if complet:
                #Afficher l'information
                arcpy.AddMessage("   FEAT_TYPE.FEAT_TYPE_NAME_DATABASE = '" + item[0] + "'")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("   " + item[0])
            
            #Afficher l'information
            self.afficherCodeSpec(catalogue, sousCatalogue, item[0], codeSpec)
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherCodeSpec(self, catalogue, sousCatalogue, classe, codeSpec):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les codes sp�cifiques
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        attribut        : Nom d'un attribut li� au code sp�cifique.
        listeValeur     : Liste des valeurs d'attributs cod�s li�es au nom d'attribut sp�cifi�.
        complet         : Indique si l'affichage doit �tre complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier si le codeSpec est valide
        sql = ("SELECT B.FEAT_TYPE_ID, B.FEAT_TYPE_CODE_BD, B.FEAT_TYPE_NAME_FR, B.FEAT_TYPE_DEFINITION_FR, B.FEAT_TYPE_NAME_EN, B.FEAT_TYPE_DEFINITION_EN"
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
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Code sp�cifique invalide : " + codeSpec)
        
        #Traiter tous les r�sultats
        for item in resultat:
            #Afficher l'information compl�te
            if complet:
                #Afficher l'information
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_ID = " + str(item[0]))
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_CODE_BD = " + str(item[1]))
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_NAME_FR = '" + item[2] + "'")
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_DEFINITION_FR = '" + item[3] + "'")
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_NAME_EN = '" + item[4] + "'")
                arcpy.AddMessage("     FEAT_TYPE.FEAT_TYPE_DEFINITION_EN = '" + item[5] + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("     " + str(item[1]) + " : " + item[2] + " / " + item[4])
            
            #Afficher l'information
            self.afficherAttribut(catalogue, sousCatalogue, classe, str(item[1]), attribut)
            arcpy.AddMessage(" ")
        
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherAttribut(self, catalogue, sousCatalogue, classe, codeSpec, attribut):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les attributs
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        attribut        : Nom d'un attribut li� au code sp�cifique.
        listeValeur     : Liste des valeurs d'attributs cod�s li�es au nom d'attribut sp�cifi�.
        complet         : Indique si l'affichage doit �tre complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier si l'attribut est valide
        #arcpy.AddMessage("- V�rifier si l'attribut est valide : " + attribut)
        sql = ("SELECT D.FEAT_ATTR_ID,D.FEAT_ATTR_NAME_DATABASE,D.FEAT_ATTR_DATA_TYPE,D.FEAT_ATTR_NAME_FR,D.FEAT_ATTR_DEFINITION_FR,D.FEAT_ATTR_NAME_EN,D.FEAT_ATTR_DEFINITION_EN"
               "  FROM FEAT_CATALOGUE A,FEAT_TYPE B,RELATION_FEAT_ATTR C,FEAT_ATTR D"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"
               "   AND B.FEAT_TYPE_CODE_BD=" + codeSpec + " AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID")
        #V�rifier si l'attribut est pr�sent
        if len(attribut) > 0:
            #Ajouter le nom de l'attribut � rechercher
            sql = sql + " AND D.FEAT_ATTR_NAME_DATABASE='" + attribut + "'"
        #Ajouter le tri � la SQL
        sql =sql + " ORDER BY D.FEAT_ATTR_NAME_DATABASE"
        
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #Afficher la commande SQL
            arcpy.AddMessage(sql)
            #Envoyer une exception
            raise Exception("Attribut invalide : " + attribut)
        
        #Traiter tous les r�sultats
        for item in resultat:
            #Afficher l'information compl�te
            if complet:
                #Afficher l'information
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_ID = " + str(item[0]))
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_NAME_DATABASE = '" + item[1] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_DATA_TYPE = '" + str(item[2]) + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_NAME_FR = '" + item[3] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_DEFINITION_FR = '" + item[4] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_NAME_EN = '" + item[5] + "'")
                arcpy.AddMessage("       FEAT_ATTR.FEAT_ATTR_DEFINITION_EN = '" + item[6] + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("       " + item[1].ljust(25," ") + " : " + str(item[2]).ljust(20," ") + " : " + item[3] + " / " + item[5])
            
            #Afficher l'information
            self.afficherValeurAttribut(catalogue, sousCatalogue, classe, codeSpec, item[1], listeValeur)
            
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def afficherValeurAttribut(self, catalogue, sousCatalogue, classe, codeSpec, attribut, listeValeur):
    #-------------------------------------------------------------------------------------
        """
        Afficher l'information sur les valeurs d'attributs.
        
        Param�tres:
        -----------
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        attribut        : Nom d'un attribut li� au code sp�cifique.
        listeValeur     : Liste des valeurs d'attributs cod�s li�es au nom d'attribut sp�cifi�.
        complet         : Indique si l'affichage doit �tre complet (True) ou partiel (False).
        
        Variables:
        ----------
        sql         : Requ�te SQL � ex�cuter.
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Cr�er la requ�te SQL pour v�rifier la valeur d'attribut
        #arcpy.AddMessage("- V�rifier la liste des valeurs d'attribut : " + listeValeur)
        sql = ("SELECT E.ATTR_VALUE_ID,E.ATTR_VALUE_INTERNAL_CODE,E.ATTR_VALUE_LABEL_FR,E.ATTR_VALUE_DEFINITION_FR,E.ATTR_VALUE_LABEL_EN,E.ATTR_VALUE_DEFINITION_EN"
               "  FROM FEAT_CATALOGUE A,FEAT_TYPE B,RELATION_FEAT_ATTR C,FEAT_ATTR D,FEAT_ATTR_VALUE E"
               " WHERE A.FEAT_CATAL_TYPE=" + catalogue.split(":")[0] + " AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"
               " AND B.FEAT_TYPE_CODE_BD=" + codeSpec + " AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID"
               " AND D.FEAT_ATTR_NAME_DATABASE='" + attribut + "' AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK")
        #V�rifier si la liste des valeurs d'attribut est pr�sente
        if len(listeValeur) > 0:
            #Initialiser les valeurs d'attribut � rechercher
            valeurs = ""
            #Traiter toutes les valeurs de la liste
            for valeur in listeValeur.split(","):
                #Ajouter les valeurs d'attributs � rechercher
                valeurs = valeurs + valeur.split(":")[0] + ","
            #Ajouter les valeurs d'attribut � rechercher dans la SQL
            sql = sql + " AND E.ATTR_VALUE_INTERNAL_CODE IN (" + valeurs[:-1] + ")"
        #Ajouter le tri � la SQL
        sql =sql + " ORDER BY E.ATTR_VALUE_INTERNAL_CODE"
            
        #Ex�cuter la requ�te SQL
        resultat = self.BDG.query(sql)
        
        #V�rifier le r�sultat
        if not resultat:
            #V�rifier une valeur est sp�cifi�e
            if len(listeValeur) > 0:
                #Afficher la commande SQL
                arcpy.AddMessage(sql)
                #Envoyer une exception
                arcpy.AddWarning("Valeur d'attribut invalide : " + listeValeur)
        
        #Traiter tous les r�sultats
        for item in resultat:
            #Afficher l'information compl�te
            if complet:
                #Afficher l'information
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_ID = " + str(item[0]))
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_INTERNAL_CODE = " + str(item[1]))
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_LABEL_FR = '" + item[2] + "'")
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_DEFINITION_FR = '" + item[3] + "'")
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_LABEL_EN = '" + item[4] + "'")
                arcpy.AddMessage("         FEAT_ATTR_VALUE.ATTR_VALUE_DEFINITION_EN = '" + item[5] + "'")
                arcpy.AddMessage(" ")
                
            #Afficher l'information miniamle
            else:
                #Afficher l'information
                arcpy.AddMessage("         " + str(item[1]).rjust(3," ") + " : " + item[2] + " / " + item[4])
            
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, catalogue, sousCatalogue, classe, codeSpec, attribut, listeValeur, complet=False):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour afficher l'information sur les classes d'un catalogue.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        catalogue       : Num�ro du catalogue.
        sousCatalogue   : Num�ro du sous-catalogue de classes.
        classe          : Nom d'une classe contenue dans le sous-catalogue sp�cifi�.
        codeSpec        : Num�ro d'un code sp�cifique contenue dans la classe sp�cifi�e.
        attribut        : Nom d'un attribut li� au code sp�cifique.
        listeValeur     : Liste des valeurs d'attributs cod�s li�es au nom d'attribut sp�cifi�.
        complet         : Indique si l'affichage doit �tre complet (True) ou partiel (False).
               
        Variables:
        ----------
        self.CompteBDG  : Objet utilitaire pour la gestion des connexion � BDG.       
        self.BDG        : Objet utilitaire pour traiter des services BDG.
        sql             : Requ�te SQL � ex�cuter.
        """
        
        #Instanciation de la classe BDG et connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        self.BDG = self.CompteBDG.OuvrirConnexionBDG(env, env)
        
        #Afficher l'information
        self.afficherCatalogue(catalogue)
        
        #Afficher l'information
        self.afficherSousCatalogue(catalogue, sousCatalogue)
        
        #Afficher l'information
        self.afficherClasse(catalogue, sousCatalogue, classe)
        
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
        sousCatalogue   = ""
        classe          = ""
        codeSpec        = ""
        attribut        = ""
        listeValeur     = ""
        complet         = False
        
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
                attribut = sys.argv[6].upper()

        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                listeValeur = sys.argv[7].replace(";",",").replace("'","")

        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                complet = sys.argv[8].upper() == "TRUE"
        
        #D�finir l'objet pour afficher l'information sur les classes d'un catalogue.
        oAfficherInfoClasseCatalogue = AfficherInfoClasseCatalogue()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oAfficherInfoClasseCatalogue.validerParamObligatoire(env, catalogue)
        
        #Ex�cuter le traitement pour afficher l'information sur les classes d'un catalogue.
        oAfficherInfoClasseCatalogue.executer(env, catalogue, sousCatalogue, classe, codeSpec, attribut, listeValeur, complet)
    
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