#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CreerTableauEtiquettesMetadonnees.py
# Auteur    : Michel Pothier
# Date      : 06 octobre 2015

"""
    Application qui permet de cr�er un nouveau tableau HTML des �tiquettes de m�tadonn�es dans SIB.
    
    Param�tres d'entr�e:
    --------------------
    env             OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                            d�faut = SIB_PRO
    tableau         OB      Tableau HTML des �tiquettes de m�tadonn�es.
                            d�faut = 
    
    Param�tres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
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

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class ExceptionCreerTableauEtiquettesMetadonnees(Exception):
#*******************************************************************************************
    """
    Classe d'exception d�riv�e de la classe Exception pour g�rer un probl�me
    dans l'ex�cution du programme.
    
    Lors de l'instanciation, passez une cha�ne de caract�re en argument
    pour d'�crire l'erreur survenue.
    """
    pass

#*******************************************************************************************
class CreerTableauEtiquettesMetadonnees(object):
#*******************************************************************************************
    """
    Permet de cr�er un nouveau tableau HTML des �tiquettes de m�tadonn�es dans SIB.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour cr�er un nouveau tableau HTML des �tiquettes de m�tadonn�es.
        
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
    def validerParamObligatoire(self,env,tableau):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        tableau         : Tableau HTML des �tiquettes de m�tadonn�es.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        
        if (len(env) == 0):
            raise ExceptionCreerTableauEtiquettesMetadonnees("Param�tre obligatoire manquant: %s" %'env')
        
        if (len(tableau) == 0):
            raise ExceptionCreerTableauEtiquettesMetadonnees("Param�tre obligatoire manquant: %s" %'tableau')
        
        #Sortir
        return
   
    #-------------------------------------------------------------------------------------
    def executer(self,env,tableau):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement cr�er un nouveau tableau HTML des �tiquettes de m�tadonn�es dans SIB.
        
        Param�tres:
        -----------
        env             : Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
        tableau         : Tableau HTML des �tiquettes de m�tadonn�es.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise ExceptionCreerTableauEtiquettesMetadonnees("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #V�rifier si l'�tiquette de m�tadonn�ees est d�j� pr�sente
        arcpy.AddMessage("- Extraction de toutes les �tiquettes de m�tadonn�ees")
        sql = ("SELECT TY_PRODUIT, CD_CHAMP, CD_VALEUR, DESC_FR, DESC_AN, DESC_PNA_FR, DESC_PNA_AN"
               "  FROM F235_VP ORDER BY TY_PRODUIT, CD_CHAMP, CD_VALEUR")
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        
        #Cr�er le tableau des �tiquettes
        arcpy.AddMessage("- Cr�ation du tableau des �tiquettes de m�tadonn�ees")
        file = open(tableau, 'w')
        
        #�crire l'ent�te du tableau
        file.write('<HTML>\n')
        file.write('   <BODY>\n')
        file.write('      <H1>Tableau sur les �tiquettes utilis�es par le CIT pour les m�tadonn�es dans SIB</H1>\n')
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
        
        #Traiter toutes les �tiquettes de la table
        arcpy.AddMessage("- �criture des �tiquettes de m�tadonn�ees ...")
        for etiquette in resultat:
            #�crire l'information de l'�tiquette
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
        
        #�crire la fin du tableau
        file.write('</table>')
        file.write('   </BODY>')
        file.write('</HTML>')
        
        #Fermer le tableau HTML des �tiquettes
        arcpy.AddMessage("- Fermeture du tableau des �tiquettes de m�tadonn�ees")
        file.close()
        
        #Fermeture de la connexion de la BD SIB
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return 

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env         = "SIB_PRO"
        tableau     = "W:\Equipe\Unix\sib\web\EtiquetteFGDC\etiquettes.txt"

        #extraction des param�tres d'ex�cution
        #arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            tableau = sys.argv[2]
        
        #D�finir l'objet pour cr�er un nouveau tableau HTML des �tiquettes de m�tadonn�es dans SIB.
        oCreerTableauEtiquettesMetadonnees = CreerTableauEtiquettesMetadonnees()
        
        #Valider les param�tres obligatoires
        oCreerTableauEtiquettesMetadonnees.validerParamObligatoire(env,tableau)
        
        #Ex�cuter le traitement pour cr�er un nouveau tableau HTML des �tiquettes de m�tadonn�es dans SIB.
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
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("- Succ�s du traitement")
    #Sortir sans code d'erreur
    sys.exit(0)