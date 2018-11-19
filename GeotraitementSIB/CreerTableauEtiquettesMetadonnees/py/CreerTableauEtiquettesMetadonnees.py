#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerTableauEtiquettesMetadonnees.py
# Auteur    : Michel Pothier
# Date      : 06 octobre 2015

"""
    Application qui permet de créer un nouveau tableau HTML des étiquettes de métadonnées dans SIB.
    
    Paramètres d'entrée:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            défaut = SIB_PRO
    tableau         OB      Tableau HTML des étiquettes de métadonnées.
                            défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
    	CreerTableauEtiquettesMetadonnees.py env ty_produit cd_champ cd_valeur desc_fr desc_an desc_pna_fr desc_pna_an
    Exemple:
        CreerTableauEtiquettesMetadonnees.py "SIB_PRO" "GENERAL" "address" "CITS_ADDRESS" "2144, rue King Ouest, bureau 010" "2144, King Street West, Suite 010" "physique; 2144; King Ouest; ; 010" "physical; 2144; King West; ; 010"
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CreerTableauEtiquettesMetadonnees.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, datetime, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ExceptionCreerTableauEtiquettesMetadonnees(Exception):
#*******************************************************************************************
    """
    Classe d'exception dérivée de la classe Exception pour gèrer un problème
    dans l'exécution du programme.
    
    Lors de l'instanciation, passez une chaîne de caractère en argument
    pour d'écrire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CreerTableauEtiquettesMetadonnees(object):
#*******************************************************************************************
    """
    Permet de créer un nouveau tableau HTML des étiquettes de métadonnées dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour créer un nouveau tableau HTML des étiquettes de métadonnées.
        
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
    def validerParamObligatoire(self,env,tableau):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires.

        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        tableau         : Tableau HTML des étiquettes de métadonnées.

        Retour:
        -------
        Exception s'il y a une erreur de paramètre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise ExceptionCreerTableauEtiquettesMetadonnees("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(tableau) == 0):
            raise ExceptionCreerTableauEtiquettesMetadonnees("Paramètre obligatoire manquant: %s" %'tableau')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,tableau):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement créer un nouveau tableau HTML des étiquettes de métadonnées dans SIB.
        
        Paramètres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        tableau         : Tableau HTML des étiquettes de métadonnées.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise ExceptionCreerTableauEtiquettesMetadonnees("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS'")
        
        #Vérifier si l'étiquette de métadonnéees est déjà présente
        arcpy.AddMessage("- Extraction de toutes les étiquettes de métadonnéees")
        sql = ("SELECT TY_PRODUIT, CD_CHAMP, CD_VALEUR, DESC_FR, DESC_AN, DESC_PNA_FR, DESC_PNA_AN"
               "  FROM F235_VP ORDER BY TY_PRODUIT, CD_CHAMP, CD_VALEUR")
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        
        #Créer le tableau des étiquettes
        arcpy.AddMessage("- Création du tableau des étiquettes de métadonnéees")
        file = open(tableau, 'w')
        
        #Écrire l'entête du tableau
        file.write('<HTML>\n')
        file.write('   <BODY>\n')
        file.write('      <H1>Tableau sur les étiquettes utilisées par le CIT pour les métadonnées dans SIB</H1>\n')
        file.write('      <H2>Version: ' + str(datetime.date.today()) + '</H2>\n')
        file.write('<table border=1 cellspacing=1 cellpadding=1 width="100%">\n')
        file.write('  <tr>\n')
        file.write('  <th align="left" bgcolor="#C0C0C0" bordercolor="#FFFFFF">TY_PRODUIT</th>\n')
        file.write('  <th align="left" bgcolor="#C0C0C0" bordercolor="#FFFFFF">CD_CHAMP</th>\n')
        file.write('  <th align="left" bgcolor="#C0C0C0" bordercolor="#FFFFFF">CD_VALEUR</th>\n')
        file.write('  <th align="left" bgcolor="#C0C0C0" bordercolor="#FFFFFF">DESC_FR</th>\n')
        file.write('  <th align="left" bgcolor="#C0C0C0" bordercolor="#FFFFFF">DESC_AN</th>\n')
        file.write('  <th align="left" bgcolor="#C0C0C0" bordercolor="#FFFFFF">DESC_PNA_FR</th>\n')
        file.write('  <th align="left" bgcolor="#C0C0C0" bordercolor="#FFFFFF">DESC_PNA_AN</th>\n')
        file.write('  </tr>\n')
        
        #Traiter toutes les étiquettes de la table
        arcpy.AddMessage("- Écriture des étiquettes de métadonnéees ...")
        for etiquette in resultat:
            #Écrire l'information de l'étiquette
            file.write('   <tr>\n')
            file.write('    <td>' + etiquette[0] + '</td>\n')
            file.write('    <td>' + etiquette[1] + '</td>\n')
            file.write('    <td>' + etiquette[2] + '</td>\n')
            file.write('    <td>' + etiquette[3].encode('utf8').replace("'","&#39;").replace("(","&#40;").replace("(","&#41;").replace("\n","&#10;") + '</td>\n')
            file.write('    <td>' + etiquette[4].encode('utf8').replace("'","&#39;").replace("(","&#40;").replace("(","&#41;").replace("\n","&#10;") + '</td>\n')
            if etiquette[5] == None:
                file.write('    <td>&nbsp;</td>\n')
            else:
                file.write('    <td>' + str(etiquette[5]).encode('utf8').replace("'","&#39;").replace("(","&#40;").replace("(","&#41;").replace("\n","&#10;") + '</td>\n')
            if etiquette[6] == None:
                file.write('    <td>&nbsp;</td>\n')
            else:
                file.write('    <td>' + str(etiquette[6]).encode('utf8').replace("'","&#39;").replace("(","&#40;").replace("(","&#41;").replace("\n","&#10;") + '</td>\n')
            file.write('   </tr>\n')
        
        #Écrire la fin du tableau
        file.write('</table>')
        file.write('   </BODY>')
        file.write('</HTML>')
        
        #Fermer le tableau HTML des étiquettes
        arcpy.AddMessage("- Fermeture du tableau des étiquettes de métadonnéees")
        file.close()
        
        #Fermeture de la connexion de la BD SIB
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env         = "SIB_PRO"
        tableau     = "W:\Equipe\Unix\sib\web\EtiquetteFGDC\etiquettes.txt"

        #extraction des paramètres d'exécution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            tableau = sys.argv[2]
        
        #Définir l'objet pour créer un nouveau tableau HTML des étiquettes de métadonnées dans SIB.
        oCreerTableauEtiquettesMetadonnees = CreerTableauEtiquettesMetadonnees()
        
        #Valider les paramètres obligatoires
        oCreerTableauEtiquettesMetadonnees.validerParamObligatoire(env,tableau)
        
        #Exécuter le traitement pour créer un nouveau tableau HTML des étiquettes de métadonnées dans SIB.
        oCreerTableauEtiquettesMetadonnees.executer(env,tableau)
    
    #Gestion des erreurs
    except ExceptionCreerTableauEtiquettesMetadonnees, err:
        #Afficher l'erreur
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succès du traitement
    arcpy.AddMessage("- Succès du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)