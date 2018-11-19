#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom       : VerifierEtatLancerService.py
# Auteur    : Michel Pothier
# Date      : 27 novembre 2014

"""
    Application qui permet de v�rifier et afficher l'�tat de l'ex�cution des services BDRS.
    
    Param�tres d'entr�e:
    --------------------
        env             OB      Type d'environnement [PRO/TST]
                                D�faut = "PRO"
        listeZtId       OB      Liste des zones de traitement � v�rifier.
                                Attention : La liste des ZtId doit �tre s�par�es par une virgule.
                                Le num�ro de la ZtId peut �tre incomplet, il affichera toutes les ZtId qui le contient.
                                D�faut = ""
        seconde         OB      Nombre de secondes de d�lai entre chaque v�rification d'�tat.
                                D�faut = 10
        maximum         OB      Nombre maximum de fois que la v�rification de l'�tat est effectu�.
                                D�faut = 20
        
    Param�tres de sortie:
    ---------------------
        Aucun
        
    Valeurs de retour:
        errorLevel          Code du r�sultat de l'ex�cution du programme.
                            (Ex: 0=Succ�s, 1=Erreur)

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

#Importation des modules priv�s
import LancerService

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par d�faut
        env         = "PRO"
        listeZtId   = ""
        seconde     = 10
        maximum     = 20
        
        #extraction des param�tres d'ex�cution
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
        
        #Ex�cuter le lanceur de service
        arcpy.AddMessage("- Ex�cuter la v�rification des services BDRS")
        oLancerService.verifierServiceTermine(env, listeZtId.split(","), seconde, maximum)
        
    except Exception, err:
        #gestion de l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #sortir avec une erreur
        sys.exit(1)
    
    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Sortir sans code d'erreur
    sys.exit(0)