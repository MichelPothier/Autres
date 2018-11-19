#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

#####################################################################################################################################
# Nom : CompilerPython.py
# Auteur    : Michel Pothier
# Date      : 25 novembre 2014

"""
    Outil qui permet la compilation d'un programme python.    

    Paramètres:
    -----------
    programme       : Nom du programme à compiler.
     
    Paramètres de sortie:
    ---------------------
    Aucun
        
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        CompilerPython.py programme
        
    Exemple:
        CompilerPython.py S:\applications\sib\pro\py\CompteSib.py
"""
#********************************************************************************************
__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: CompilerPython.py 2057 2016-06-15 21:03:15Z mpothier $"
#********************************************************************************************

# Identification des librairies utilisees 
import os, sys, arcpy, py_compile, traceback

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Afficher la commande
        arcpy.AddMessage(sys.argv)
        
        #Vérfier si le paramètre du nom de programme est spécifié
        if len(sys.argv) > 1:
            #Compiler le programme
            py_compile.compile(sys.argv[1])
        #Si pas de nom de programme
        else:
            #Afficher la commande
            arcpy.AddError("Vous devez entrer le nom du programme à compiler")
    
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