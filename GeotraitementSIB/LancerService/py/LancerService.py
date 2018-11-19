#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : LancerService.py
# Auteur    : Michel Pothier
# Date      : 23 octobre 2014

"""
    Application qui permet de lancer un ou plusieurs services BDRS selon la liste des fichiers XML et leur contenus.
    
    Paramètres d'entrée:
    --------------------
        env                 OB      Type d'environnement [PRO/TST]
                                    Défaut = "PRO"
        listeFichierXML     OB      Liste des noms des fichiers XML contenant l'information du service BDRS à lancer.
                                    Défaut = ""
        
    Paramètres de sortie:
    ---------------------
        listeFihierLog      Liste des noms des fichiers log créés.
        
    Valeurs de retour:
        errorLevel          Code du résultat de l'exécution du programme.
                            (Ex: 0=Succès, 1=Erreur)

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

# Importation des modules privés
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
        
        Paramètres:
        -----------
        Aucun
        
        Variables:
        ----------
        self.lanceurBDRS : Programme qui permet de lancer un service BDRS.
        
        """
        
        # Définir l'objet de gestion des comptes BDG.
        self.CompteBDG = CompteBDG.CompteBDG()
        
        # Définir l'objet de gestion des comptes Sib.
        self.lanceurBDRS = "S:\\applications\\Gestion_BDRS\\pro\\py\\bdrs\\services\\lbd\\clients\\LancerService.py"
        
        # Sortir
        return

    #-------------------------------------------------------------------------------------
    def validerParamObligatoire(self, env, listeFichierXml):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML à traiter
        
        Retour:
        -------
        Exception s'il y a un problème
        """

        #Valider la présence de l'environnement
        if (len(env) == 0):
            raise Exception ('Paramètre obligatoire manquant: env')

        #Valider la présence de la liste du fichier XML
        if (len(listeFichierXml) == 0):
            raise Exception ('Paramètre obligatoire manquant: listeFichierXml')
 
        #Sortir
        return

    #-------------------------------------------------------------------------------------
    def verifierServiceTermine(self, env, listeZtId, secAttente=10, cptMax=20):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env             : Environnement de travail
        listeZtId       : Liste des fichiers XML à traiter
        secAttente      : Nombre de secondes d'attente entre les vérifications des status
        cptMax          : Compteur maximum de vérification des status             
        
        Retour:
        -------
        Exception s'il y a un problème
        """
        
        #Instanciation de la classe BDG et connexion à la BDG
        arcpy.AddMessage("- Connexion à la BDG")
        oBDG = self.CompteBDG.OuvrirConnexionBDG("BDRS_" + env)   
        
        #Initialiser la boucle de vérification
        cont = True
        cpt = 0
        
        #Boucler tant que toutes les ZtId ne sont pas terminées ou qu'il y a plus de 20 vérificatons
        while cont and cpt < cptMax:
            #Initialiser la boucle pour arreter
            cont = False
            cpt = cpt + 1
            
            #Vérification du STATUT des ZT_ID dans la BDRS
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- " + str(cpt) + ":Vérification du STATUT des ZT_ID ...")
            
            #Attendre X secondes entre chaque vérification
            time.sleep(secAttente)
            
            #Traiter toutes les ZT_ID de la liste
            for ZtId in listeZtId:
                #Construire la requete
                sSql = "  SELECT ZT_ID,STATUS FROM VUE_GESTION_TRANSACTIONS WHERE ZT_ID LIKE '%" + ZtId + "%'"
                arcpy.AddMessage(sSql)
                
                #Exécuter la requête SQL
                resultat = oBDG.query(sSql)
                #Traiter tous les résultats
                for item in resultat:
                    #Afficher le résultat
                    arcpy.AddMessage("  ZT_ID='" + item[0] + "'=" + item[1])

                    #Vérifier si on doit continuer la vérification
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
        Permet d'exécuter le traiter pour lancer un ou plusieurs services BDRS
        selon la liste des fichiers XML et leur contenus.
        
        Paramètres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML à traiter.
        
        Retour:
        -------
        listeFichierLog : Liste des noms des fichiers LOG.
        
        """
        
        #Initialiser les listes
        listeFichierLog = []
        listeZtId = []
        
        #Créer la liste des fichierXML
        listeFichierXml = listeFichierXml.split(",")
        
        #Traiter tous les fichiers XML de la liste
        for fichierXml in listeFichierXml:
            #Extraire le nomet l'extension du fichier XML
            nom, ext = os.path.splitext(os.path.basename(fichierXml))

            #Créer le nom du fichier LOG à partir du nom du fichier XML
            fichierLog = fichierXml.replace(ext, ".log")

            #Ajouter le fichier LOG dans la liste            
            listeFichierLog.append(fichierLog)
            
            #Ajouter et ajouter le ZtId dans la liste correspondant au nom du fichier XML
            listeZtId.append(nom.replace("_CreerZT",""))
            
            #Définir la commande pour le lanceur de service de la BDRS
            commande = "%python27% " + self.lanceurBDRS + " --env " + env + " --xml " + fichierXml  + " --log " + fichierLog
            
            #Exécuter le lanceur de service de la BDRS
            arcpy.AddMessage(" ")
            arcpy.AddMessage(commande)
            #err = os.system(commande)
            #err = subprocess.check_output(commande, shell=True)
            
            message = subprocess.check_output(commande, shell=True)
            arcpy.AddMessage(message)
            
            #Vérifier le résultat de l'exécution de la commande
            #if err <> 0:
                #Lancer une erreur d'exécution
                #raise Exception("Erreur dans l'exécution du lanceur de la BDRS (voir le fichierLog)")
        
        #Vérifier si les services sont terminés
        self.verifierServiceTermine(env, listeZtId)
        
        #Sortir
        return listeFichierLog

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par défaut
        env                 = "PRO"
        listeFichierXml     = []
        listeFichierLog     = []

        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeFichierXml = sys.argv[2].replace(";",",")
        
        #Instanciation de la classe LancerService
        oLancerService = LancerService()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oLancerService.validerParamObligatoire(env, listeFichierXml)
        
        #Exécuter le lanceur de service
        arcpy.AddMessage("- Exécuter le lancement des services BDRS")
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
    
    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Afficher la liste des fichierXml
    arcpy.AddMessage("  listeFichierLog=%s" %listeFichierLog)
    arcpy.SetParameterAsText(2, listeFichierLog)
    #Sortir sans code d'erreur
    sys.exit(0)