#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : LancerService.py
# Auteur    : Michel Pothier
# Date      : 23 octobre 2014

"""
    Application qui permet de lancer un ou plusieurs services BDRS selon la liste des fichiers XML et leur contenus.
    
    Param�tres d'entr�e:
    --------------------
        env                 OB      Type d'environnement [PRO/TST]
                                    D�faut = "PRO"
        listeFichierXML     OB      Liste des noms des fichiers XML contenant l'information du service BDRS � lancer.
                                    D�faut = ""
        
    Param�tres de sortie:
    ---------------------
        listeFihierLog      Liste des noms des fichiers log cr��s.
        
    Valeurs de retour:
        errorLevel          Code du r�sultat de l'ex�cution du programme.
                            (Ex: 0=Succ�s, 1=Erreur)

    Usage:
        LancerService.py env listeFichierXml
        
    Exemple:
        LancerService.py TST D:\Travail\053I05_849453_CreerZT.xml,D:\Travail\053I06_849454_CreerZT.xml
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: LancerService.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, time, arcpy, subprocess, traceback

# Importation des modules priv�s
import CompteBDG

#*******************************************************************************************
class LancerService:
#*******************************************************************************************
    """
    Permet de lancer un ou plusieurs services BDRS selon la liste des fichiers XML et leur contenus.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement pour lancer un ou plusieurs services BDRS.
        
        Param�tres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.lanceurBDRS : Programme qui permet de lancer un service BDRS.
        
        """
        
        # D�finir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # D�finir l'objet de gestion des comptes Sib.
        self.lanceurBDRS = "S:\\applications\\Gestion_BDRS\\pro\\py\\bdrs\\services\\lbd\\clients\\LancerService.py"
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, listeFichierXml):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML � traiter
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """

        #Valider la pr�sence de l'environnement
        if (len(env) == 0):
            raise Exception ('Param�tre obligatoire manquant: env')

        #Valider la pr�sence de la liste du fichier XML
        if (len(listeFichierXml) == 0):
            raise Exception ('Param�tre obligatoire manquant: listeFichierXml')
 
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def verifierServiceTermine(self, env, listeZtId, secAttente=10, cptMax=20):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env             : Environnement de travail
        listeZtId       : Liste des fichiers XML � traiter
        secAttente      : Nombre de secondes d'attente entre les v�rifications des status
        cptMax          : Compteur maximum de v�rification des status             
        
        Retour:
        -------
        Exception s'il y a un probl�me
        """
        
        #Instanciation de la classe BDG et connexion � la BDG
        arcpy.AddMessage("- Connexion � la BDG")
        oBDG = self.CompteBDG.OuvrirConnexionBDG("BDRS_" + env)   
        
        #Initialiser la boucle de v�rification
        cont = True
        cpt = 0
        
        #Boucler tant que toutes les ZtId ne sont pas termin�es ou qu'il y a plus de 20 v�rificatons
        while cont and cpt < cptMax:
            #Initialiser la boucle pour arreter
            cont = False
            cpt = cpt + 1
            
            #V�rification du STATUT des ZT_ID dans la BDRS
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- " + str(cpt) + ":V�rification du STATUT des ZT_ID ...")
            
            #Attendre X secondes entre chaque v�rification
            time.sleep(secAttente)
            
            #Traiter toutes les ZT_ID de la liste
            for ZtId in listeZtId:
                #Construire la requete
                sSql = "  SELECT ZT_ID,STATUS FROM VUE_GESTION_TRANSACTIONS WHERE ZT_ID LIKE '%" + ZtId + "%'"
                arcpy.AddMessage(sSql)
                
                #Ex�cuter la requ�te SQL
                resultat = oBDG.query(sSql)
                #Traiter tous les r�sultats
                for item in resultat:
                    #Afficher le r�sultat
                    arcpy.AddMessage("  ZT_ID='" + item[0] + "'=" + item[1])

                    #V�rifier si on doit continuer la v�rification
                    if item[1] in ['pending','processing']:
                        #Initialiser la boucle pour continuer
                        cont = True
        
        #Fermer la connexion BDG
        arcpy.AddMessage(" ")
        self.CompteBDG.FermerConnexionBDG()
        
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def executer(self, env, listeFichierXml):
    #-------------------------------------------------------------------------------------
        """
        Permet d'ex�cuter le traiter pour lancer un ou plusieurs services BDRS
        selon la liste des fichiers XML et leur contenus.
        
        Param�tres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML � traiter.
        
        Retour:
        -------
        listeFichierLog : Liste des noms des fichiers LOG.
        
        """
        
        #Initialiser les listes
        listeFichierLog = []
        listeZtId = []
        
        #Cr�er la liste des fichierXML
        listeFichierXml = listeFichierXml.split(",")
        
        #Traiter tous les fichiers XML de la liste
        for fichierXml in listeFichierXml:
            #Extraire le nomet l'extension du fichier XML
            nom, ext = os.path.splitext(os.path.basename(fichierXml))

            #Cr�er le nom du fichier LOG � partir du nom du fichier XML
            fichierLog = fichierXml.replace(ext, ".log")

            #Ajouter le fichier LOG dans la liste            
            listeFichierLog.append(fichierLog)
            
            #Ajouter et ajouter le ZtId dans la liste correspondant au nom du fichier XML
            listeZtId.append(nom.replace("_CreerZT",""))
            
            #D�finir la commande pour le lanceur de service de la BDRS
            commande = "%python27% " + self.lanceurBDRS + " --env " + env + " --xml " + fichierXml  + " --log " + fichierLog
            
            #Ex�cuter le lanceur de service de la BDRS
            arcpy.AddMessage(" ")
            arcpy.AddMessage(commande)
            #err = os.system(commande)
            #err = subprocess.check_output(commande, shell=True)
            
            message = subprocess.check_output(commande, shell=True)
            arcpy.AddMessage(message)
            
            #V�rifier le r�sultat de l'ex�cution de la commande
            #if err <> 0:
                #Lancer une erreur d'ex�cution
                #raise Exception("Erreur dans l'ex�cution du lanceur de la BDRS (voir le fichierLog)")
        
        #V�rifier si les services sont termin�s
        self.verifierServiceTermine(env, listeZtId)
        
        #Sortir
        return listeFichierLog

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par d�faut
        env                 = "PRO"
        listeFichierXml     = []
        listeFichierLog     = []

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeFichierXml = sys.argv[2].replace(";",",")
        
        #Instanciation de la classe LancerService
        oLancerService = LancerService()
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oLancerService.validerParamObligatoire(env, listeFichierXml)
        
        #Ex�cuter le lanceur de service
        arcpy.AddMessage("- Ex�cuter le lancement des services BDRS")
        listeFichierLog = oLancerService.executer(env, listeFichierXml)
        
    except Exception, err:
        #gestion de l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Afficher la liste des fichierXml
        arcpy.AddMessage("  listeFichierLog=%s" %listeFichierLog)
        arcpy.SetParameterAsText(2, listeFichierLog)
        #sortir avec une erreur
        sys.exit(1)
    
    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Afficher la liste des fichierXml
    arcpy.AddMessage("  listeFichierLog=%s" %listeFichierLog)
    arcpy.SetParameterAsText(2, listeFichierLog)
    #Sortir sans code d'erreur
    sys.exit(0)