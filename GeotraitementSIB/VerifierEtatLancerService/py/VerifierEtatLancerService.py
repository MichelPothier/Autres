#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : VerifierEtatLancerService.py
# Auteur    : Michel Pothier
# Date      : 27 novembre 2014

"""
    Application qui permet de vérifier et afficher l'état de l'exécution des services BDRS.
    
    Paramètres d'entrée:
    --------------------
        env             OB      Type d'environnement [PRO/TST]
                                Défaut = "PRO"
        listeZtId       OB      Liste des zones de traitement à vérifier.
                                Attention : La liste des ZtId doit être séparées par une virgule.
                                Le numéro de la ZtId peut être incomplet, il affichera toutes les ZtId qui le contient.
                                Défaut = ""
        seconde         OB      Nombre de secondes de délai entre chaque vérification d'état.
                                Défaut = 10
        maximum         OB      Nombre maximum de fois que la vérification de l'état est effectué.
                                Défaut = 20
        
    Paramètres de sortie:
    ---------------------
        Aucun
        
    Valeurs de retour:
        errorLevel          Code du résultat de l'exécution du programme.
                            (Ex: 0=Succès, 1=Erreur)

    Usage:
        VerifierEtatLancerService.py env listeZtId seconde maximum
        
    Exemple:
        VerifierEtatLancerService.py TST 053I05_849453,053I06_849454 5 10
"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: VerifierEtatLancerService.py 2057 2016-06-15 21:03:15Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import traceback

#Importation des modules privés
import LancerService

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par défaut
        env         = "PRO"
        listeZtId   = ""
        seconde     = 10
        maximum     = 20
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeZtId = sys.argv[2].replace(";",",")
        
        if len(sys.argv) > 3:
            seconde = int(sys.argv[3])
        
        if len(sys.argv) > 4:
            maximum = int(sys.argv[4])
        
        #Instanciation de la classe LancerService
        oLancerService = LancerService.LancerService()
        
        #Exécuter le lanceur de service
        arcpy.AddMessage("- Exécuter la vérification des services BDRS")
        oLancerService.verifierServiceTermine(env, listeZtId.split(","), seconde, maximum)
        
    except Exception, err:
        #gestion de l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #sortir avec une erreur
        sys.exit(1)
    
    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)