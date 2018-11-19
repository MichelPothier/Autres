#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#********************************************************************************************

#####################################################################################################################################
# Nom       : FermerSelectdNonConformiteDonneesInsitu.py
# Auteur    : Michel Pothier
# Date      : 19 septembre 2016

"""
Outil qui permet de fermer une s�lection d'identifiants d'une non-conformit� sur les donn�es g�ographique apr�s avoir
effectu� une correction sur ces derni�res directement dans la BD (INSITU)
et estampiller les m�tadonn�es associ�es aux donn�es g�ographiques non-conformes.

La fermeture d'une non-conformit� est r�alis�e seulement apr�s avoir effectu� une correction INSITU dans les donn�es de la BDG.
-V�rifier si la non-conformit� existe.
-Extraire la liste des jeux de donn�es selon la no de non-conformit�.
-Pour chaque jeu de donn�es:
    -Ajouter une �tiquette de description du processus utilis�.
    -Le num�ro de version des m�tadonn�es est incr�ment�.
    -Changer la date des m�tadonn�es.
    -L'intervalle d'��dition-version est ferm�e selon le num�ro d'�dition et version du jeu courant. 
    -Si toutes les intervalles de fin sont inscrits, alors la date de fin de traitement est inscrite pour permettre de fermer la non-conformit�. 
    -Le responsable de l'��quipe Qualit� des donn�es re�oit alors un courriel lui indiquant la fin des travaux.

Attention : Seule les non-conformit�s de type DM et dont le type de traitement est SP% ou SM% peuvent �tre trait�es par ce programme.

Param�tres:
-----------
env             : Type d'environnement.
no_nc           : Num�ro de la non-conformit� � fermer.
decoupage       : FeatureLayer contenant une s�lection d'�l�ments de d�coupage repr�sentant des identifiants de la non-conformit� � fermer.
attribut        : Nom de l'attribut du FeatureLayer contenant l'identifiant de d�coupage � fermer.
no_tache        : Num�ro de la t�che Alloy qui correspond � une demande effectu�e par un usager.
procdesc        : �tiquette qui correspond � la description du processus utilis�e pour corriger la non-conformit�.

Classe:
-------
 Nom                            Description
 -----------------------------  --------------------------------------------------------------------
 FermerSelectdNonConformiteDonneesInsitu     Fermer une non-conformit� sur les donn�es g�ographique.
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: FermerSelectdNonConformiteDonneesInsitu.py 2159 2018-07-12 21:18:17Z mpothier $"
#********************************************************************************************

# Importation des modules publics
import os, sys, arcpy, datetime, traceback

# Importation des modules priv�s
import  EnvoyerCourriel, CompteSib

#*******************************************************************************************
class FermerSelectdNonConformiteDonneesInsitu(object):
#*******************************************************************************************
    """ Fermer une non-conformit� sur les donn�es g�ographique.
    
    Retour:
        ErrorLevel  Integer  Code d'erreur de retour sur le syst�me (Ex: 0=Succ�s, 1=Erreur).
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """Initialisation du traitement de fermeture d'une non-conformit�.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.CompteSib : Objet utilitaire pour la gestion des connexion � SIB.
        
        """
        
        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, no_nc, decoupage, attribut, no_tache, procdesc):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de fermeture d'une non-conformit� � partir d'une s�lection d'�l�ments de d�coupage.
        
        Param�tres:
        -----------
        env             : Type d'environnement.
        no_nc           : Num�ro de la non-conformit� � fermer.
        decoupage       : FeatureLayer contenant une s�lection d'�l�ments de d�coupage repr�sentant des identifiants de la non-conformit� � fermer.
        attribut        : Nom de l'attribut contenant l'identifiant de d�coupage � fermer.
        no_tache        : Num�ro de la t�che Alloy qui correspond � une demande effectu�e par un usager.
        procdesc        : �tiquette qui correspond � la description du processus utilis� pour corriger la non-conformit�.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        ty_produit      : Type de produit trait�.
        identifiant     : Identifiant de d�coupage trait�.
        ed_fin          : �dition de fin de la non-conformit�.
        ver_fin         : Version de fin de la non-conformit�.
        ed_cour         : �dition courante du jeu de donn�es.
        ver_cour        : Version courante du jeu de donn�es.
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)   
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        sUsagerBd = self.CompteSib.UsagerBd()
        
        #-----------------------------------
        #Extraction de l'information de la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction de l'information de la non-conformit� : " + str(no_nc))
        sql = "SELECT DATE_FERMETURE, DATE_TRAITEMENT, TY_NC, TY_TRAIT_NC, RESP_DESCR, RESP_CORR, RESP_SUIVI FROM F702_NC WHERE NO_NC='" + no_nc + "'"
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence du param�tre
        if (len(resultat) == 0):
            raise Exception("Num�ro de non-conformit� invalide : %s" %no_nc)
        #V�rifier si la non-conformit� est ferm�e
        if resultat[0][0] <> None:
            raise Exception("La non-conformit� est d�j� ferm�e : date_fermeture=" + str(resultat[0][0]))
        #V�rifier si la non-conformit� a d�j� �t� trait�e
        dateTraitement = resultat[0][1]
        if dateTraitement <> None:
            arcpy.AddWarning("La non-conformit� a d�j� �t� trait�e : date_traitement=" + str(dateTraitement))
        #V�rifier si la non-conformit� est de type DM
        if resultat[0][2] <> "DM":
            raise Exception("Le type de non-conformit� n'est pas 'DM' : TY_NC=" + str(resultat[0][2]))
        #V�rifier si la non-conformit� a le traitement SP ou SM
        if "SP" not in resultat[0][3] and "SM" not in resultat[0][3]:
            raise Exception("Le type de traitement de non-conformit� n'est pas 'SP%' ou 'SM%' : TY_TRAIT_NC=" + str(resultat[0][3]))
        #Conserver l'information de la non-conformit�
        resp_descr = resultat[0][4]
        resp_corr = resultat[0][5]
        resp_suivi = resultat[0][6]
        #Afficher les valeurs
        arcpy.AddMessage(str(resultat))
        
        #-----------------------------------
        #Extraction des identifiants s�lectionn�s
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des identifiants s�lectionn�s ...")
        #Extraire le nombre d'�l�ments s�lectionn�s
        desc = arcpy.Describe(decoupage)
        listeOid = desc.FIDSet
        #V�rifier la pr�sence du param�tre
        if len(listeOid) == 0:
            raise Exception("Aucun �l�ment n'a �t� s�lectionn� dans le Layer de d�coupage.")
        
        #Cr�er la liste  tri�e des identifiants s�lectionn�s
        listeId = list(set("{0}".format(row[0]) for row in arcpy.da.SearchCursor(decoupage, [attribut])))
        listeId.sort()
        total = len(listeId)
        #Afficher le nombre d'�l�ments s�lectionn�s
        arcpy.AddWarning("Nombre d'�l�ments s�lectionn�s : " + str(total))
        
        #-----------------------------------
        #Initialiser les compteurs
        cpt = 0
        #Traiter tous les identifiants s�lectionn�s
        for id in listeId:
            #Afficher les valeurs
            cpt = cpt + 1
            arcpy.AddMessage(" ")
            arcpy.AddMessage(str(cpt) + "/" + str(total) + " : " + str(id))
            
            #-----------------------------------
            #Extraction de l'identifiant de la non-conformit� trait�
            arcpy.AddMessage("  -Valider l'identifiant : " + id)
            sql = "SELECT TY_PRODUIT, IDENTIFIANT, ED_DEBUT, VER_DEBUT, ED_FIN, VER_FIN FROM F705_PR WHERE NO_NC='" + no_nc + "' AND IDENTIFIANT='" + id + "'"
            arcpy.AddMessage("  " + sql)
            #Ex�cuter la requ�te
            resultat = self.Sib.requeteSib(sql)
            #V�rifier la pr�sence de l'identifiant
            if resultat:
                #D�finir les variables
                ty_produit = resultat[0][0]    #ty_produit
                identifiant = resultat[0][1]   #identifiant
                ed_debut = resultat[0][2]      #ed_debut
                ver_debut = resultat[0][3]     #ver_debut
                ed_fin = resultat[0][4]        #ed_fin
                ver_fin = resultat[0][5]       #ver_fin
                
                #V�rifier si l'intervalle de fin n'est pas trait�e
                if ed_fin == 99999:
                    #Traiter l'identifiant de non-conformit�
                    self.traiterIdentifiant(no_nc, no_tache, procdesc, ty_produit, identifiant, ed_debut, ver_debut, ed_fin, ver_fin)
                
                #si l'intervalle de fin est d�j� trait�e
                else:
                    #Afficher un avertissement
                    arcpy.AddWarning("  L'intervalle de fin est d�j� trait�e")
             #Si aucun r�sultat
            else:
                #Retourner une erreur
                arcpy.AddError("  L'identifiant n'est pas associ� � la non-conformit� : " + id) 
        
        #-----------------------------------
        #V�rifier si tous les identifiants de la NC sont ferm�s        
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des identifiants non-ferm�s : " + str(no_nc))
        sql = "SELECT IDENTIFIANT FROM F705_PR WHERE NO_NC='" + no_nc + "' AND ED_FIN=99999 ORDER BY IDENTIFIANT"
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te
        resultat = self.Sib.requeteSib(sql)
        #V�rifier le r�sultat
        if resultat:
            #Afficher les identifiants non-ferm�s
            arcpy.AddWarning("Les identifiants suivants ne sont pas encore ferm�s : " + str(resultat))
            
        #Si aucun r�sultat
        else:
            #V�rifier si la non-conformit� ne poss�de d�j� pas de date de traitement
            if dateTraitement == None:
                #-----------------------------------
                #Mettre � jour la date de traitement
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Mise � jour de la date de traitement")
                sql = "UPDATE F702_NC SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, DATE_TRAITEMENT=SYSDATE WHERE NO_NC='" + no_nc + "'"
                arcpy.AddWarning(sql)
                self.Sib.execute(sql)
            
            #Envoyer les courriels aux responsables
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Envoit d'un courriel aux responsables")
            sql = "SELECT DISTINCT ADR_EMAIL FROM F005_US WHERE CD_USER='" + str(resp_descr) + "' OR CD_USER='" + str(resp_corr) + "' OR CD_USER='" + str(resp_suivi) +  "'"
            #Ex�cuter la requ�te SQL
            resultat = self.Sib.requeteSib(sql)
            #Envoyer un courriel aux responsables
            for courriel in resultat:
                #Envoyer un courriel
                destinataire = str(courriel[0])
                sujet = unicode("Fermeture de la correction INSITU de la non-conformit� #" + no_nc, "utf-8")
                contenu = unicode("Bonjour,\n\nTous les jeux de donn�es associ�s � la non conformit� #" + no_nc + " sont maitenant corrig�s.\n\n" + sUsagerSib + "\n" + sUsagerBd, "utf-8")
                arcpy.AddMessage("EnvoyerCourriel('" + destinataire + "','" + sujet + "')")
                EnvoyerCourriel.EnvoyerCourriel(destinataire,contenu, sujet)
        
        #-----------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddWarning(sql)
        self.Sib.execute(sql)
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        self.Sib.fermerConnexionSib()   
        
        # Sortir du traitement 
        return

    #-------------------------------------------------------------------------------------
    def traiterIdentifiant(self, no_nc, no_tache, procdesc, ty_produit, identifiant, ed_debut, ver_debut, ed_fin, ver_fin):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de fermeture pour un identifiant de la non-conformit�.
        
        Param�tres:
        -----------
        no_nc           : Num�ro de la non-conformit� � fermer.
        no_tache        : Num�ro de la t�che Alloy qui correspond � une demande effectu�e par un usager.
        procdesc        : �tiquette qui correspond � la description du processus utilis� pour corriger la non-conformit�.
        ty_produit      : Type de produit trait�.
        identifiant     : Identifiant de d�coupage trait�.
        ed_debut        : �dition de d�but de la non-conformit�.
        ver_debut       : Version de d�but de la non-conformit�.
        ed_fin          : �dition de fin de la non-conformit�.
        ver_fin         : Version de fin de la non-conformit�.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        self.Sib        : Objet utilitaire pour traiter des services SIB.
        resultat        : R�sultat de la requ�te SIB.
        ed_cour         : �dition courante du jeu de donn�es.
        ver_cour        : Version courante du jeu de donn�es.
        """
        
        #-----------------------------------
        #Valider le Proc/Desc
        arcpy.AddMessage("  -Valider le Proc/Desc : " + procdesc)
        sql = "SELECT * FROM F235_VP WHERE TY_PRODUIT='" + ty_produit + "' AND CD_CHAMP='procdesc' AND CD_VALEUR='" + procdesc + "'"
        arcpy.AddMessage("  " + sql)
        #Ex�cuter la requ�te
        resultat = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence du param�tre
        if (len(resultat) == 0):
            #Retourner une erreur
            raise Exception("La description de la proc�dure utilis�e pour le produit " + ty_produit + " est invalide!")

        #-----------------------------------
        #Cr�er la requ�te SQL (pour extraire l'�dition et la version du jeu courant ainsi que la version des m�tadonn�es)
        arcpy.AddMessage("  -Extraire l'�dition et la version du jeu courant ...")
        sql = "SELECT ED, VER, VER_META FROM F235_PR WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND JEU_COUR=1"
        arcpy.AddMessage("  " + sql)
        #Ex�cuter la requ�te SQL
        resultat2 = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence du param�tre
        if (len(resultat) == 0):
            raise Exception("Aucun jeu courant n'est pr�sent dans la table F235_pr")
        #Extraire la valeur de l'�dition et version courante
        ed_cour = resultat2[0][0]
        ver_cour = resultat2[0][1]
        ver_meta = resultat2[0][2]
        #V�rifier si l'�dition.version de d�but est plus �lev� que l'�dition.version courante
        if float(str(ed_debut) + "." + str(ver_debut)) > float(str(ed_cour) + "." + str(ver_cour)):
            #Retourner une erreur
            raise Exception("Ed.Ver_D�but:" + str(float(str(ed_debut) + "." + str(ver_debut))) + " > Ed.Ver_Cour:" + str(float(str(ed_cour) + "." + str(ver_cour))))
        #Afficher les valeurs
        arcpy.AddMessage("  " + str(resultat2))

        #-----------------------------------
        #Extraire le no_seq du procDesc
        arcpy.AddMessage("  -Extraire le NO_SEQ du Proc/Desc ...")
        sql = "SELECT MAX(NO_SEQ) + 1 FROM F235_PS WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed_cour) + " AND VER=" + str(ver_cour)
        arcpy.AddMessage("  " + sql)
        #Ex�cuter la requ�te SQL
        resultat3 = self.Sib.requeteSib(sql)
        #D�finir le NO_SEQ
        no_seq = str(resultat3[0][0])
        
        #-----------------------------------
        #Cr�er l'�tiquette du Proc/Desc
        arcpy.AddMessage("  -Cr�er l'�tiquette du Proc/Desc dans les m�tadonn�es ...")
        sql = "INSERT INTO F235_PS Values (P0G03_UTL.PU_HORODATEUR, '" + no_tache + "', SYSDATE, SYSDATE, '" + ty_produit + "', '" + identifiant + "', " + str(ed_cour) + ", " + str(ver_cour) + ", " + no_seq + ", '{$PS$" + procdesc + "}', TO_CHAR(SYSDATE, 'YYYYMMDD'), 0)"
        arcpy.AddWarning("  " + sql)
        #Ex�cuter la commande
        self.Sib.execute(sql)
        
        #-----------------------------------
        #Modifier la date des m�tadonn�es
        arcpy.AddMessage("  -Modifier la date des m�tadonn�es ...")
        sql = "UPDATE F235_MR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, DT_METADATA=TO_CHAR(SYSDATE, 'YYYYMMDD') WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND ED=" + str(ed_cour) + " AND VER=" + str(ver_cour)
        arcpy.AddWarning("  " + sql)
        #Ex�cuter la commande
        self.Sib.execute(sql)
        
        #-----------------------------------
        #Incr�menter la version des m�tadonn�es
        ver_meta = ver_meta + 1
        #Cr�er la commande SQL pour modifier la version des m�tadonn�es
        arcpy.AddMessage("  -Modifier la version des m�tadonn�es ...")
        sql = "UPDATE F235_PR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, VER_META=" + str(ver_meta) + " WHERE TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "' AND JEU_COUR=1"
        arcpy.AddWarning("  " + sql)
        #Ex�cuter la commande
        self.Sib.execute(sql)
        
        #-----------------------------------
        #Modifier l'�dition et version de fin
        arcpy.AddMessage("  -Modifier l'�dition et version de fin de non-conformit� ...")
        sql = "UPDATE F705_PR SET ETAMPE='" + no_tache + "', DT_M=SYSDATE, ED_FIN=" + str(ed_cour) + ", VER_FIN=" + str(ver_cour) + " WHERE NO_NC='" + no_nc + "' AND TY_PRODUIT='" + ty_produit + "' AND IDENTIFIANT='" + identifiant + "'"
        arcpy.AddWarning("  " + sql)
        #Ex�cuter la commande
        self.Sib.execute(sql)
        
        # Sortir du traitement 
        return

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Valeur par d�faut
        env = "SIB_PRO"
        no_nc = ""
        decoupage = ""
        attribut = "DATASET_NAME"
        no_tache = ""
        procdesc = ""
        
        # Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            no_nc = sys.argv[2].split(":")[0]
        
        if len(sys.argv) > 3:
            decoupage = sys.argv[3]
        
        if len(sys.argv) > 4:
            attribut = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            no_tache = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            procdesc = sys.argv[6].upper()
        
        # D�finir l'objet de fermeture d'une non-conformit� de correction des donn�es g�ographique
        oFermerSelectdNonConformiteDonneesInsitu = FermerSelectdNonConformiteDonneesInsitu()
        
        # Ex�cuter le traitement de fermeture d'une non-conformit� de correction des donn�es g�ographique
        oFermerSelectdNonConformiteDonneesInsitu.executer(env, no_nc, decoupage, attribut, no_tache, procdesc)
    
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