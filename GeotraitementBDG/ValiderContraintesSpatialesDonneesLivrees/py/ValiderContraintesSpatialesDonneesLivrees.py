#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : ValiderContrainteSpatialesDonneesLivrees.py
# Auteur    : Michel Pothier
# Date      : 15 juin 2016

""" Outil qui permet de valider les contraintes spatiales des donn�es livr�es dans la BDG selon une table de contraintes spatiales.

    Les actions suivantes sont effectu�es pour chaque type de travail � traiter :
    -Cr�er un layer de d�coupage dont les �l�ments s�lectionn�s sont ceux livr�s dans la BDG pour le type de travail trait�.
    -Extraire toutes les classes li�es au type de travail trait�.
    -Lancer l'ex�cution de la validation des contraintes spatiales selon le layer de d�coupage et les classes li�s au type de travail.

    Param�tres d'entr�es:
    ---------------------
    envSib              : Environnement de travail SIB [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].
                          d�faut=SIB_PRO
    geodatabase         : Nom de la g�odatabase contenant les tables spatiales.
                          d�faut="\\DFSCITSH\CITS\Travail\Gestion_BDSpatiales\validation\BDRS_PRO_BDG.sde"
    tableContraintes    : Nom de la table contenant les contraintes spatiales.
                          d�faut=CONTRAINTE_INTEGRITE_SPATIALE
    classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de d�coupage.
                          d�faut=GES_DECOUPAGE_SNRC50K_2
    attributDecoupage   : Nom de l'attribut de la classe de d�coupage contenant les identifiants de d�coupage.
                          d�faut=DATASET_NAME
    repTravail          : Nom du r�pertoire de travail.
                          d�faut=\\DFSCITSH\CITS\Travail\Gestion_BDSpatiales\validation
    dateFin             : Date de fin du traitement de livraison des donn�es BDG (ex:2015-12-15 16:21:54).
                          d�faut=<24 heures avant la date et l'heure courante>
    typeTravail         : Liste des types de travaux pr�sents dans la table SER_RECONCILE_LOG et
                          dont les identifiants ont �t� livr�s apr�s la date de fin sp�cifi�e.
                          exemple: CORINT:2
                                   RHN_ANOM_2:33
                          d�faut=<typeTravail:nombre de livraison>
    courriel            : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
                          d�faut = michel.pothier@canada.ca;odette.trottier@canada.ca
    serveur             : Nom du serveur de batch LSF.
                          d�faut = s-she-fermat

    Param�tres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel  : Code du r�sultat de l'ex�cution du programme.
                  Ex: 0=Succ�s, 1=Erreur)

    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 

    Usage:
        ValiderContrainteSpatialesDonneesLivrees.py env geodatabase tableContraintes classeDecoupage attributDecoupage repTravail dateFin typeTravail courriel

    Exemple:
        ValiderContrainteSpatialesDonneesLivrees.py SIB_PRO
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ValiderContrainteSpatialesDonneesLivrees.py 1833 2014-10-02 14:53:38Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, datetime, arcpy, subprocess, traceback

# Importation des modules priv�s
import CompteSib

#*******************************************************************************************
class ValiderContrainteSpatialesDonneesLivrees(object):
#*******************************************************************************************
    """ Valider l'int�grit� des donn�es spatiales livr�es dans la BDG selon une table de contraintes spatiales.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour valider l'int�grit� des donn�es spatiales livr�es dans la BDG selon une table de contraintes spatiales.
        
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
    def validerParamObligatoire(self, env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, courriel, serveur):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires.

        Param�tres:
        -----------
        env                 : Type d'environnement
        geodatabase         : Nom de la g�odatabase contenant les tables spatiales.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de d�coupage.
        attributDecoupage   : Nom de l'attribut de la classe de d�coupage contenant les identifiants de d�coupage.
        repTravail          : Nom du r�pertoire de travail.
        dateFin             : Date de fin du traitement de livraison des donn�es BDG (ex:2015-12-15 16:21:54).
        courriel            : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
        serveur             : Nom du serveur de batch LSF.

        Retour:
        -------
        Exception s'il y a une erreur de param�tre obligatoire
        """

        #Affichage du message
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(env) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'env')

        if (len(geodatabase) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'geodatabase')

        if (len(tableContraintes) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'tableContraintes')

        if (len(classeDecoupage) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'classeDecoupage')

        if (len(attributDecoupage) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'attributDecoupage')

        if (len(repTravail) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'repTravail')

        if (len(dateFin) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'dateFin')

        if (len(courriel) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'courriel')

        if (len(serveur) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'serveur')

        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def executer(self, env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, typeTravail, courriel, serveur):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement pour valider l'int�grit� des donn�es spatiales livr�es dans la BDG selon une table de contraintes spatiales.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.
        geodatabase         : Nom de la g�odatabase contenant les tables spatiales.
        tableContraintes    : Nom de la table contenant les contraintes spatiales.
        classeDecoupage     : Nom de la classe contenant les polygones et les identifiants de d�coupage.
        attributDecoupage   : Nom de l'attribut de la classe de d�coupage contenant les identifiants de d�coupage.
        repTravail          : Nom du r�pertoire de travail.
        dateFin             : Date de fin du traitement de livraison des donn�es BDG (ex:2015-12-15 16:21:54).
        typeTravail         : Liste des types de travaux pr�sents dans la table SER_RECONCILE_LOG et
                              dont les identifiants ont �t� livr�s apr�s la date de fin sp�cifi�e.
        courriel            : Adresse courriel utilis�e pour envoyer le rapport d'ex�cution.
        serveur             : Nom du serveur de batch LSF.
               
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        """
        
        #Permet de remplacer les fichier existants
        arcpy.env.overwriteOutput = True
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        arcpy.AddMessage("- Connexion � la BD SIB")
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)   

        #----------------------------------------------------------        
        #Cr�er la requ�te SQL pour extraire les types de travail livr�s.
        #----------------------------------------------------------
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Extraction des travaux effectu�s sur le nombre d'identifiants livr�s")
        sSql = ("SELECT TY_TRAV, COUNT(*)"
                " FROM SER_RECONCILE_LOG@BDG_DBA"
                " WHERE STATUT=9 AND DATE_FIN>TO_DATE('" + dateFin + "','yyyy-mm-dd HH24:MI:SS')")
        #V�rifier si on sp�cifier les types de travail dans la requ�te
        if len(typeTravail) > 0:
            #Initialiser la liste des travaux
            listeTrav = ""
            #Extraire les types de travaux
            for trav in typeTravail.split(";"):
                #Ajouter le travail � la liste
                listeTrav = listeTrav + trav.split(":")[0] + ","
                #Afficher le travail et le nombre d'identifiants
                arcpy.AddMessage(str(trav))
            #Ajouter la liste des travaux � la requ�te SQL
            sSql = sSql + " AND TY_TRAV IN ('" + listeTrav[:-1].replace(",","','") + "')"
        #Ajouter le regroupement et le tri dans la requ�te sql
        sSql = sSql + " GROUP BY TY_TRAV ORDER BY TY_TRAV"
        
        #Ex�cuter la requ�te SQL
        arcpy.AddMessage(sSql)
        resultatTrav = oSib.requeteSib(sSql)
        
        #Traiter tous les types de travail livr�s
        for trav in resultatTrav:
            #Cr�er la requ�te SQL.
            arcpy.AddMessage(" ")
            arcpy.AddMessage("-Type de travail: " + str(trav[0]) + ", Nombre d'identifiants: " + str(trav[1]))
            
            #D�finir la date et l'heure de traitement
            dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            #----------------------------------------------------------
            #Cr�er la requ�te SQL pour extraire les identifiants livr�s
            #----------------------------------------------------------
            sSql = (" SELECT DISTINCT B.FEAT_TYPE_NAME_DATABASE"
                    " FROM FEAT_CATALOGUE@BDG_VIEW A, FEAT_TYPE@BDG_VIEW B"
                    " WHERE A.FEAT_CATAL_TYPE=1"
                    "   AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK" 
                    "   AND B.FEAT_TYPE_CODE_BD IN "
                    "   ("
                    "       SELECT DISTINCT LE.CD_ELEM_TOPO"
                    "      FROM F502_PS PS, F502_LE LE, F503_TR TR, F601_LO LO"
                    "     WHERE TR.TY_TRAV='" + trav[0] + "'"
                    "       AND PS.NO_MAP=TR.NO_MAP AND PS.NO_MAP=LE.NO_MAP AND TR.NO_LOT=LO.NO_LOT" 
                    "   )"
                    " ORDER BY B.FEAT_TYPE_NAME_DATABASE")
            
            #Ex�cuter la requ�te SQL
            resultatClasse = oSib.requeteSib(sSql)
            
            #V�rifier si aucune classe
            if len(resultatClasse) == 0:
                #Cr�er la liste des identifiants � traiter            
                arcpy.AddMessage(sSql)
                raise Exception("ERREUR : Aucune classe � traiter")
            
            #Initialisation de la liste des classes � traiter
            listeClasse = ""
            #Traiter toutes les classes
            for cls in resultatClasse:
                #Ajouter la classe � la liste
                listeClasse = listeClasse + "'" + cls[0] + "',"                
            #D�finir la requete des identifiants
            listeClasse = listeClasse[:-1]
            
            #----------------------------------------------------------
            #Cr�er la requ�te SQL pour extraire les identifiants livr�s
            #----------------------------------------------------------
            sSql = ("SELECT IDENTIFIANT"
                    "  FROM SER_RECONCILE_LOG@BDG_DBA"
                    " WHERE STATUT=9 AND DATE_FIN>TO_DATE('" + dateFin + "','yyyy-mm-dd HH24:MI:SS')"
                    "   AND TY_TRAV='" + trav[0] + "'"
                    " ORDER BY IDENTIFIANT")
            #Ex�cuter la requ�te SQL
            resultatId = oSib.requeteSib(sSql)

            #Traiter tous les identifiants correspondant au type de travail
            for id in resultatId:
                #D�finir la date et l'heure de traitement
                dateHeure = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                #D�finir le nom du fichier batch
                nomBatch = repTravail + "\\" + id[0] + "_Batch_" + trav[0] + "_" + dateHeure + ".bat"
                #Cr�er le fichier batch
                batch = open(nomBatch, 'a')
                
                #----------------------------------------------------------
                #Afficher le message d'ex�cution du traitement de validation pour le travail
                #----------------------------------------------------------
                arcpy.AddMessage(" ")
                arcpy.AddMessage("- Ex�cution du traitement de validation spatiale ...")
                #D�finir le nom du rapport d'ex�cution
                nomRapport = repTravail + "\\" + id[0] + "_Rapport_" + trav[0] + "_[DATE_TIME].txt"
                #D�finir le nom du journal d'ex�cution
                nomJournal = repTravail + "\\" + id[0] + "_Journal_" + trav[0] + "_[DATE_TIME].log"
                #D�finir le nom de la Geodatabase d'erreurs
                nomErreur = repTravail + "\\" + id[0] + "_Erreurs_" + trav[0] + "_[DATE_TIME].mdb"
                nomErreur = ""
                #D�finir la commande de validation
                cmd = (repTravail + "\\ValiderContrainte.exe"
                       ' "' + geodatabase + '"'
                       ' "' + tableContraintes + '"'
                       ' "NOM_TABLE IN (' + listeClasse + ')"'
                       ' "' + classeDecoupage + ":" + attributDecoupage + "='" + id[0] + "'" + '"'
                       ' "' + attributDecoupage + '"'
                       ' "' + nomErreur + '"'
                       ' "' + nomRapport + '"'
                       ' "' + nomJournal + '"'
                       ' "' + courriel + '"'
                       ' "TBL_STATISTIQUE_ELEMENT_ERREUR"')
                
                #Afficher la commande
                arcpy.AddMessage(cmd)
                #�criture du fichier batch
                batch.write("\n" + cmd + "\n")
            
                #Fermer le fichier batch
                batch.close()
            
                #Ex�cuter le fichier batch
                arcpy.AddMessage(" ")
                #arcpy.AddMessage(nomBatch)
                #process = subprocess.Popen(nomBatch, shell=False)
            
                #D�finir la Job � lancer
                job = 'plink lsf bsub -q qTest -m ' + serveur + ' -oo "' + nomBatch.replace("\\","\\\\").replace(".bat","_lsf.log") + '" "' + nomBatch.replace("\\","\\\\") + '"'
                #Afficher la job � lancer
                arcpy.AddMessage('  ' + job)
                #Ex�cuter la job � lancer
                process = subprocess.Popen(job, shell=False)
        
        # Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()   
        
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
        geodatabase = "\\\\DFSCITSH\\CITS\\Travail\\Gestion_BDSpatiales\\validation\\BDRS_PRO_BDG.sde"
        tableContraintes = "CONTRAINTE_INTEGRITE_SPATIALE"
        classeDecoupage = "GES_DECOUPAGE_SNRC50K_2"
        attributDecoupage = "DATASET_NAME"
        repTravail = "\\\\DFSCITSH\\CITS\\Travail\\Gestion_BDSpatiales\\validation"
        dateFin = str(datetime.datetime.now().replace(microsecond=0) - datetime.timedelta(days=1))
        typeTravail = ""
        courriel = "michel.pothier@canada.ca;odette.trottier@canada.ca"
        serveur = "s-she-fermat"
        
        # Lecture des param�tres
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            geodatabase = sys.argv[2]
        
        if len(sys.argv) > 3:
            tableContraintes = sys.argv[3].upper()
        
        if len(sys.argv) > 4:
            classeDecoupage = sys.argv[4].upper()
        
        if len(sys.argv) > 5:
            attributDecoupage = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            repTravail = sys.argv[6]
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                dateFin = sys.argv[7]
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                typeTravail = sys.argv[8]
        
        if len(sys.argv) > 9:
            courriel = sys.argv[9]
        
        if len(sys.argv) > 10:
            serveur = sys.argv[10]
        
        #D�finir l'objet pour valider l'int�grit� des donn�es spatiales livr�es dans la BDG selon une table de contraintes spatiales.
        oValiderContrainteSpatialesDonneesLivrees = ValiderContrainteSpatialesDonneesLivrees()
        
        #Valider les param�tres obligatoires
        oValiderContrainteSpatialesDonneesLivrees.validerParamObligatoire(env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, courriel, serveur)
        
        #Ex�cuter le traitement pour valider l'int�grit� des donn�es spatiales livr�es dans la BDG selon une table de contraintes spatiales.
        oValiderContrainteSpatialesDonneesLivrees.executer(env, geodatabase, tableContraintes, classeDecoupage, attributDecoupage, repTravail, dateFin, typeTravail, courriel, serveur)
    
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