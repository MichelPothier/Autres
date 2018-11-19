#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : ModifierMiseProgrammeLot.py
# Auteur    : Michel Pothier
# Date      : 29 juin 2016

"""
    Application qui permet de modifier l'information pour toutes les mises au programme d'un lot en production.
    
    Paramètres d'entrée:
    --------------------
    env                 OB      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                défaut = SIB_PRO
    noLot               OB      Numéro de lot en production.
                                défaut = 
    typeProd            OB      Type de production du numéro de mise au programme.
                                défaut = 
    etatProd            OB      État de la production du numéro de mise au programme.
                                défaut = 
    normes              OB      Norme selon laquelle la production sera effectuée.
                                défaut = 
    catalogue           OP      Numéro de catalogue selon laquelle la production sera effectuée.
                                défaut = 
    gabaritMD           OP      Gabarit de métadonnées utilisé.
                                défaut = 
    datePrevue          OP      Date prévue de la fin des travaux.
                                défaut = 
    nbJrsExt            OP      Nombre de jours d'extension.
                                défaut = 
    note                OP      Note explicative associée aux identifiants traités.
                                défaut = 
    
    Paramètres de sortie:
    ---------------------
    Aucun
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du résultat de l'exécution du programme.
                      (Ex: 0=Succès, 1=Erreur)
    Usage:
        ModifierMiseProgrammeLot.py env noLot typeProd etatProd normes [catalogue] [gabaritMD] [datePrevue] [nbJrsExt] [note]

    Exemple:
        ModifierMiseProgrammeLot.py SIB_PRO 456789 A P 4.0.2 # # # # "Note pour le lot"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: ModifierMiseProgrammeLot.py 2148 2017-10-19 15:43:54Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules privés (Cits)
import CompteSib

#*******************************************************************************************
class ModifierMiseProgrammeLot:
#*******************************************************************************************
    """
    Classe qui permet de modifier l'information pour toutes les mises au programme d'un lot en production.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement.
        
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
    def validerParamObligatoire(self, env, noLot, typeProd, etatProd, normes):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la présence des paramètres obligatoires.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        noLot               : Numéro de lot en production.
        typeProd            : Indique le type de production : 'A', 'C' ou 'E'
        etatProd            : Indique l'état de la production : 'P' ou 'T'
        normes              : Numéro de la normes selon laquelle le fichier sera produit.
        
        """

        #Message de vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        
        if (len(env) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'env')
        
        if (len(noLot) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'noLot')
        
        if (len(typeProd) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'typeProd')
        
        if (len(etatProd) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'etatProd')
        
        if (len(normes) == 0):
            raise Exception("Paramètre obligatoire manquant: %s" %'normes')

        return
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, noLot, typeProd, etatProd, normes, catalogue, gabaritMD, datePrevue, nbJrsExt, note):
    #-------------------------------------------------------------------------------------
        """
        Exécuter le traitement pour modifier l'information d'une mise au programme en production.
        
        Paramètres:
        -----------
        env                 : Type d'environnement.    
        noLot               : Numéro de lot en production.
        typeProd            : Indique le type de production : 'A', 'C' ou 'E'
        etatProd            : Indique l'état de la production : 'P' ou 'T'
        normes              : Numéro de la normes selon laquelle le fichier sera produit.
        catalogue           : Numéro de catalogue selon laquelle la production sera effectuée.
        gabaritMD           : Gabarit de métadonnées utilisé.
        datePrevue          : Date prévue de la fin des travaux.
        nbJrsExt            : Nombre de jours d'extension.        
        note                : Note explicative associée aux identifiants traités.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion à SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.

        Valeurs de retour:
        -----------------
        
        """
        
        #Instanciation de la classe Sib et connexion à la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Valider la liste des groupes de privilège de l'usager
        arcpy.AddMessage("- Valider si l'usager possède le groupe de privilèges 'G-SYS','PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #Vérifier si l'usager SIB possède les privilège de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")

        #Vérifier si le type de production est valide
        if typeProd not in "A,C,E":
            #Retourner une exception
            raise Exception("Le type de production est invalide : " + typeProd + "<> (A,C,E)")

        #Vérifier si l'état de production est valide
        if etatProd not in "P,T":
            #Retourner une exception
            raise Exception("L'état de la production est invalide : " + etatProd + "<> (P,T)")
        
        #Vérifier si le gabaritMD est vide
        if gabaritMD == "":
            #Ajouter la valeur NULL
            gabaritMD = "NULL"
        #si le gabarit n'est pas vide
        else:
            #Ajouter les apostrophes
            gabaritMD = "'" + gabaritMD.replace("'","''") + "'"
        
        #Vérifier si la date prévue est vide
        if datePrevue == "":
            #Ajouter la valeur NULL
            datePrevue = "NULL"
        #si la date n'est pas vide
        else:
            #Ajouter les apostrophes
            datePrevue = "'" + datePrevue + "'"
        
        #Vérifier si le nombre de jours d'extension est vide
        if nbJrsExt == "":
            #Ajouter la valeur NULL
            nbJrsExt = "NULL"
        #si la note n'est pas vide
        elif not nbJrsExt.isdigit():
            #Retourner une exception
            raise Exception("Le nombre de jours d'extension n'est pas numérique : " + nbJrsExt)
        
        #Vérifier si la note est vide
        if note == "":
            #Ajouter la valeur NULL
            note = "NULL"
        #si la note n'est pas vide
        else:
            #Ajouter les apostrophes
            note = "'" + note.replace("'","''") + "'"

        #Construire la liste des normes valident selon le type de produit du noLot
        resultat = self.Sib.requeteSib("SELECT CD_VALEUR FROM F002_VP A, F601_LO B WHERE A.TY_PRODUIT=B.TY_PRODUIT and NO_LOT='" + noLot + "' AND CD_CHAMP='normes' ORDER BY CD_VALEUR DESC")
        listeNormes = []
        for norme in resultat:
            listeNormes.append(norme[0])
        #Vérifier si la norme est valide normes selon le type de produit du noLot
        if normes not in listeNormes:
            #Retourner une exception
            raise Exception("La norme est invalide : " + normes)
        #Ajouter les apostrophes
        normes = "'" + normes + "'"
        
        #Vérifier si aucun catalogue n'est présent
        if catalogue == "":
            #Ajouter la valeur NULL
            catalogue = "NULL"
        #Vérifier la valeur du catalogue
        else:
            #Construire la liste des catalogues valident selon le type de produit du noLot
            resultat = self.Sib.requeteSib("SELECT CD_VALEUR FROM F002_VP A, F601_LO B WHERE A.TY_PRODUIT=B.TY_PRODUIT and NO_LOT='" + noLot + "' AND CD_CHAMP='no_catalogue' ORDER BY CD_VALEUR DESC")
            listeNoCatalogue = []
            for noCatalogue in resultat:
                listeNoCatalogue.append(noCatalogue[0])
            #Vérifier si le catalogue est valide selon le type de produit du noLot
            if catalogue not in listeNoCatalogue:
                #Retourner une exception
                raise Exception("Le catalogue est invalide : " + catalogue)
            #Ajouter les apostrophes
            catalogue = "'" + catalogue + "'"
        
        #Valider si le noMap selon le type de produit est au programme
        arcpy.AddMessage("- Valider le numéro de lot ...")
        resultat = self.Sib.requeteSib("SELECT B.NO_MAP FROM F502_PS A, F503_TR B WHERE NO_LOT='" + noLot + "' AND A.NO_MAP=B.NO_MAP")
        #Vérifier le résultat
        if not resultat:
            #Retourner une exception
            raise Exception("Aucun numéro de lot '" + noLot + "' n'est au programme actuellement !")

        #-------------------------------------------------------
        #Modifier l'information pour la mise a programme du lot
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information pour la mise a programme du lot ...")
        #Traiter tous les NO_MAP
        for noMap in resultat:
            #Initialiser la commande SQL de modifification
            sql = "UPDATE F502_PS SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE"
            sql = sql + ",TYPE='" + typeProd + "',E_PLSNRC='" + etatProd + "',NORMES=" + normes
            sql= sql + ",GABARIT_MD=" + gabaritMD + ",DT_PREVUE=TO_DATE(" + datePrevue + "),NOTE=" + note + " WHERE NO_MAP=" + str(noMap[0])
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Modifier l'information pour le type de travail du lot
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information pour le type de travail du lot ...")
        #Initialiser la commande SQL de modifification
        sql = "UPDATE F503_TR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR,ETAMPE='" + sUsagerSib + "',DT_M=SYSDATE"
        sql= sql + ",NO_CATALOGUE=" + catalogue + ",NB_JRS_EXT=" + nbJrsExt + " WHERE NO_LOT='" + noLot + "'"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB   
        
        #Sortir
        return

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par défaut
        env                 = "SIB_PRO"
        noLot               = ""
        typeProd            = ""
        etatProd            = ""
        normes              = ""
        catalogue           = ""
        gabaritMD           = ""
        datePrevue          = ""
        nbJrsExt            = ""
        note                = ""
        
        #extraction des paramètres d'exécution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            noLot = sys.argv[2].split(" ")[0]
        
        if len(sys.argv) > 3:
            typeProd = sys.argv[3].upper().split(" ")[0]
        
        if len(sys.argv) > 4:
            etatProd = sys.argv[4].upper().split(" ")[0]
        
        if len(sys.argv) > 5:
            normes = sys.argv[5]
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                catalogue = sys.argv[6]
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                gabaritMD = sys.argv[7].upper()
        
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                datePrevue = sys.argv[8].split(" ")[0]
        
        if len(sys.argv) > 9:
            if sys.argv[9] <> "#":
                nbJrsExt = sys.argv[9]
        
        if len(sys.argv) > 10:
            if sys.argv[10] <> "#":
                note = sys.argv[10]
        
        #Définir l'objet pour modifier l'information pour toutes les mises au programme d'un lot en production.
        oModifierMiseProgrammeLot = ModifierMiseProgrammeLot()
        
        #Valider les paramètres obligatoires
        oModifierMiseProgrammeLot.validerParamObligatoire(env, noLot, typeProd, etatProd, normes)
        
        #Exécuter le traitement pour modifier l'information pour toutes les mises au programme d'un lot en production.
        oModifierMiseProgrammeLot.executer(env, noLot, typeProd, etatProd, normes, catalogue, gabaritMD, datePrevue, nbJrsExt, note)
    
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