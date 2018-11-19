#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : MettreProgrammeXmlCreerZT.py
# Auteur    : Michel Pothier
# Date      : 22 octobre 2014

"""
    Application qui permet de mettre au programme dans SIB une ou plusieurs zone de travail (ZT)
    à partir de l'information contenue dans des fichiers XML.
    
    Paramètres d'entrée:
    --------------------
        env                 OP      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    défaut = SIB_PRO
        listeFichierXml     OB      Liste des fichiers XML contenant l'information de chaque zone de travail à mettre au programme.
                                    défaut = ""
        noLot               OB      Numéro de lot associé à un type de produit et un type de travail.
                                    défaut = ""
        noGroupe            OB      Numéro de groupe qui subdivise un lot.
                                    défaut = "01"
        typeProduction      OB      Type de production associé au travail.
                                    défaut = "A"
        listeNonConf        OP      Liste des numéros de non-conformité traités.
                                    défaut = ""
        note                OP      note explicative associée aux identifiants traités.
                                    défaut = ""
    
    Paramètres de sortie:
    ---------------------
        listeFichierXmlSortie   : Liste des noms de fichier XML corrigés
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du résultat de l'exécution du programme.
                                  (Ex: 0=Succès, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de données doivent être opérationnelles. 
    
    Usage:
        MettreProgrammeXmlCreerZT.py env listeFichierXml noLot noGroupe typeProduction [listeNonConf] [note]
    
    Exemple:
        MettreProgrammeXmlCreerZT.py SIB_PRO d:\021M07.xml,d:\021M08.xml, 170766 01 C # "Ceci est une note"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: MettreProgrammeXmlCreerZT.py 2145 2017-10-19 15:43:17Z mpothier $"

#####################################################################################################################################

#Importation des modules publics
import os, sys, cx_Oracle, arcpy, traceback

#Importation des modules privés (Cits)
import CompteSib, util_XmlCreerZT

#*******************************************************************************************
class MettreProgrammeXmlCreerZT:
#*******************************************************************************************
    """
    Permet de mettre au programme dans SIB une ou plusieurs zone de travail (ZT)
    à partir de l'information contenue dans des fichiers XML.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de mise au programme.
        
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
    def validerParamObligatoire(self, env, listeFichierXml, noLot, noGroupe, typeProduction):
    #-------------------------------------------------------------------------------------
        """
        Validation de la présence des paramètres obligatoires
        
        Paramètres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML à traiter
        noLot           : Numéro de lot dans SIB
        noGroupe        : Numéro de groupe dans SIB
        typeProduction  : Type de production dans SIB
        
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

        #Valider la présence du noLot
        if (len(noLot) == 0):
            raise Exception ('Paramètre obligatoire manquant: noLot')
        
        #Valider que le groupe est composé de 2 chiffres
        if len(noGroupe)<> 2:
            raise Exception("La valeur de GROUPE fournie est invalide : %s. "
                            "Cette valeur doit être composée de 2 chiffres." % noGroupe)

        #Valider la présence du typeProduction
        if (len(typeProduction) == 0):
            raise Exception ('Paramètre obligatoire manquant: typeProduction')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def mapSansEdVer(self, typeProduit):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant d'indiquer si la mise au programme se fait avec ou sans édition et version.
        
        Paramètres:
        -----------
        typeProduit     : Type de produit vérifié.
       
        Retour:
        -------
        sansEdVer       : Indique si la mise au programme est avec ou sans édition et version.getvalue
        
        """
        
        #Vérifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE CD_PARAMETRE='MAP-SANS-ED-VER' AND TY_PRODUIT='" + typeProduit + "'")

        #Définir le résultat de la requête
        if resultat:
            sansEdVer = True
        else:
            sansEdVer = False
        
        #Sortir et retourner le résultat
        return sansEdVer

    #-------------------------------------------------------------------------------------
    def miseAuProgrammeZt(self, typeProduit, identifiant, datePrevue, normes, typeTravail, noLot, noGroupe, 
                          typeProduction, note="", listeNonConf="", validerIdentifiant=False, catalogue=""):
    #-------------------------------------------------------------------------------------
        """
        Cette méthode effectue une mise au programme des zones de travail (ZT) et ajoute les travaux associés à la 
        production d'un jeu de données pour un lot donné dans SIB. Elle est utilisable seulement pour les produits
        dans SIB qui ne requierent pas de liste d'éléments topo. 
        (SELECT TY_PRODUIT FROM F008_PP WHERE CD_PARAMETRE = 'MAP-LISTE-ENTITE' AND VALEUR = 0)
        
        Par défaut, la méthode ne valide pas l'identifiant selon un dictionnaire (validerIdentifiant=False)
       
        Paramètres:
        ----------
        typeProduit             : Nom du produit
        identifiant             : Identifiant du produit
        datePrevue              : Date à laquelle tous les travaux cédulés seront terminés
        normes                  : Normes selon laquelle le fichier sera produit
        typeTravail             : Type de travail à effectuer
        noLot                   : Numéro de lot
        noGroupe                : Numéro de groupe
        typeProduction          : Indique le type de production : 'A', 'C' et 'E'
        note                    : Information complémentaire : 3 lignes de 80 caractères maximum (optionnel)
                                  (défaut NULL)
        listeNonConf            : Liste des numéros de non conformités qui seront réglés par cette mise au programme (défaut NULL) (optionnel)
        validerIdentifiant      : Fanion indiquant si on veut valider ou non l'identifiant selon la table dictionnaires F101 (défaut=False) (optionnel)
        catalogue               : Numéro du catalogue (défaut NULL) (optionnel)
        
        Valeurs de retour:
        -----------------
        infoMap                 : Dictionnaire python contenant les clés suivantes :
                  "identifiant" : Identifiant résultant de la mise au programme
                  "noMap"       : Numéro de mise au programme correspondant à l'identifiant
                  "edition"     : Édition associée à l'identifiant. -1 lorsque le produit n'a pas d'édition
                  "version"     : Version associée à l'identifiant. -1 lorsque le produit n'a pas de version
        """

        #instanciation du logger
        fanion_validerIdentifiant = {True:1, False:0}.get(validerIdentifiant)
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()

        #Définition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")  # Définition du format de la date
        
        #Appel du service de transaction Sib qui initialise l'ajout d'une nouvelle instance de produit au programme
        code_retour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Mise_au_programme", cx_Oracle.STRING, 
                                          [sUsagerSib, typeProduit, identifiant, datePrevue, normes, typeProduction, 
                                           note, "", listeNonConf, "", "", "", fanion_validerIdentifiant])
        #Vérifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Mise_au_programme]")
            raise Exception(message)
        
        #Appel du service de transaction qui ajoute un travail à la mise au programme préalablement initialisée
        code_retour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Travail", cx_Oracle.STRING, [typeTravail, 1, catalogue])
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        #Vérifier le code de retour
        if code_succes <>1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Travail]")
            raise Exception(message)
        
        #Définir la zone-mémoire où est emmagasinée la valeur de la variable noMap
        noMap = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #Définir la zone-mémoire où est emmagasinée la valeur de la variable edition
        edition = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #Définir la zone-mémoire où est emmagasinée la valeur de la variable version
        version = self.Sib.cursor.var(cx_Oracle.NUMBER)
        
        #Appel du service de transaction qui termine l'ajout d'un travail
        code_retour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Termine", cx_Oracle.STRING, [noMap, edition, version]) 
        #Vérifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Termine]")
            raise Exception(message)
        
        #Appel du service de transaction qui ajoute une instance de produit au contenu d'un lot
        code_retour = self.Sib.cursor.callfunc("P0607_CONT.pu_Ajouter_contenu_lot", cx_Oracle.STRING, [sUsagerSib, noLot, noGroupe, noMap])
        #Vérifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0607_CONT.pu_Ajouter_contenu_lot]")
            raise Exception(message)
            
        #Définir le numéro de mise au programme
        noMap = int(noMap.getvalue())
        #Vérifier si la mise au programme se fait avec édition et version
        if self.mapSansEdVer(typeProduit):
            #Définir l'édition et la version à None
            edition = -1
            version = -1
        else:
            #Extraire l'édition et la version résultante
            edition = int(edition.getvalue())
            version = int(version.getvalue())

        # Extraction de l'identifiant mis au programme
        requete = "SELECT IDENTIFIANT FROM F502_PS WHERE NO_MAP='%s'" % noMap
        self.Sib.cursor.execute(requete)
        identifiant = self.Sib.cursor.fetchone()[0]

        # Définir l'information à retourner sur la mise au programme
        infoMap = {"noMap":noMap, "identifiant":identifiant,"edition":edition, "version":version}

        return infoMap

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeFichierXml, noLot, noGroupe, typeProduction, listeNonConf, note):
    #-------------------------------------------------------------------------------------
        """
        Permet de mettre au programme tous les identifiants de Zone de travail (ZT)
        contenus dans chaque fichier XML de la liste.
        
        Paramètres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML à traiter
        noLot           : Numéro de lot dans SIB
        noGroupe        : Numéro de groupe dans SIB
        typeProduction  : Type de production dans SIB
        listeNonConf    : Liste des non-conformités dans SIB
        note            : Note explicative reliéeà la mise au programme
        
        Retour:
        -------
        listeFichierXmlSortie : Liste des noms de fichier XML de sortie corrigés
        
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
        #Vérifier si l'usager SIB possède les privilège de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne possède pas le groupe de privilèges : 'G-SYS','PLAN'")

        #Définir les valeurs par défaut        
        validerIdentifiant = 0
        typeProduit      = ""
        typeTravail      = ""
        normes           = ""
        catalogue        = ""
          
        #Requête dans SIB afin d'extraire le type de produit et le type de travail en fonction du numéro de lot
        arcpy.AddMessage("- Extraction du type de produit et du type de travail dans SIB")
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT,TY_TRAV FROM F601_LO WHERE NO_LOT='" + noLot + "'")
        
        #Extraire le type de produit dans SIB en fonction du noLot
        typeProduit = resultat[0][0]
        arcpy.AddMessage("  Type de produit: %s" %typeProduit)
        
        #Extraire le type de travail dans SIB en fonction du noLot
        typeTravail = resultat[0][1]
        arcpy.AddMessage("  Type de travail: %s" %typeTravail)
        
        #Initialiser les listes
        listeFichierXmlSortie = []
        listeMap = []
        listeEd = []
        listeVer = []
        listeId = []
        
        #Créer la liste des fichierXML
        listeFichierXml = listeFichierXml.split(",")
        #Traiter tous les fichiers XML de la liste
        for fichierXml in listeFichierXml:
            #Instanciation de la classe XmlCreerZT pour lire et ecrire dans le fichier XML selon le profil du service CreerZT
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Lecture du fichier XML: %s" %fichierXml)
            oXmlCreerZT = util_XmlCreerZT.XmlCreerZT(fichierXml)
            
            #Extraire l'identifiant
            identifiant = oXmlCreerZT.obtenirZtId()
            arcpy.AddMessage("  Identifiant: %s" %identifiant)
            
            #Extraire la date prévue
            datePrevue = oXmlCreerZT.obtenirDatePrevue()
            arcpy.AddMessage("  Date prévue: %s" %datePrevue)
            
            #Extraire le catalogue et la normes
            catalogue = oXmlCreerZT.obtenirCatalogue()
            arcpy.AddMessage("  Nom du catalogue: %s" %catalogue)
            normes = catalogue.split('_')[2]
            arcpy.AddMessage("  Normes: %s" %normes)
            catalogue = ""
            arcpy.AddMessage("  Catalogue: %s" %catalogue)
            
            #Mettre au programme une ZT
            arcpy.AddMessage("- Mettre au programme une ZT dans SIB : %s ..." %identifiant)
            infoMap = self.miseAuProgrammeZt( typeProduit, 
                                              identifiant, 
                                              datePrevue,
                                              normes, 
                                              typeTravail, 
                                              noLot, 
                                              noGroupe, 
                                              typeProduction, 
                                              note, 
                                              listeNonConf,  
                                              validerIdentifiant,
                                              catalogue
                                              )
            
            #Extraire le nouvel identifiant avec le noMap
            idNoMap = infoMap["identifiant"]
            
            #Affichage des informations de la MAP
            arcpy.AddMessage("  infoMap=%s" %str(infoMap))
            listeMap.append(infoMap["noMap"])
            listeEd.append(infoMap["edition"])
            listeVer.append(infoMap["version"])
            listeId.append(idNoMap)
            
            #Écrire le nouvel identifiant avec le noMap dans le fichier XML
            oXmlCreerZT.definirZtId(idNoMap)
            
            #Changer le nom du fichier XML selon le nouvel identifiant contenant le noMap
            fichierXmlSortie = fichierXml.replace(identifiant, idNoMap)
            
            #Écrire dans le même fichier le nouvel identifiant
            arcpy.AddMessage("- Écriture du fichier XML %s:" %fichierXmlSortie)
            oXmlCreerZT.ecrire(fichierXmlSortie)
            
            #Ajouter le fichier XML de sortie à la liste
            listeFichierXmlSortie.append(fichierXmlSortie)
        
        # Sortie normale pour une exécution réussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #exécution de la méthode pour la fermeture de la connexion de la BD SIB
        
        #Afficher les listes
        arcpy.AddMessage("  listeMap=%s" %str(listeMap))
        arcpy.AddMessage("  listeEd=%s" %str(listeEd))
        arcpy.AddMessage("  listeVer=%s" %str(listeVer))
        arcpy.AddMessage("  listeId=%s" %str(listeId))
        
        #Sortir et retourner la liste des fichiers XML de sortie
        return listeFichierXmlSortie

#-------------------------------------------------------------------------------------
# Exécution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par défaut
        env                     = "SIB_PRO"
        listeFichierXml         = ""
        noLot                   = ""
        noGroupe                = "01"
        typeProduction          = "A"
        listeNonConf            = ""
        note                    = ""
        listeFichierXmlSortie   = []

        #Extraction des paramètres d'exécution
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
        
        if len(sys.argv) > 2:
            listeFichierXml = sys.argv[2].replace(";",",")
        
        if len(sys.argv) > 3:
            noLot = sys.argv[3].split(" ")[0]
        
        if len(sys.argv) > 4:
            noGroupe = str(sys.argv[4])
        
        if len(sys.argv) > 5:
            typeProduction = sys.argv[5].upper()
        
        if len(sys.argv) > 6:
            if sys.argv[6] <> "#":
                listeNonConf = sys.argv[6].upper().replace(";",",")
        
        if len(sys.argv) > 7:
            if sys.argv[7] <> "#":
                note = sys.argv[7]
        
        #Instanciation de la classe MiseAuProgramme
        oMettreProgrammeXmlCreerZT = MettreProgrammeXmlCreerZT()
        
        #Vérification de la présence des paramètres obligatoires
        arcpy.AddMessage("- Vérification de la présence des paramètres obligatoires")
        oMettreProgrammeXmlCreerZT.validerParamObligatoire(env, listeFichierXml, noLot, noGroupe, typeProduction)
        
        #Exécuter la mise au programme à partir de la liste des fichiers XML
        arcpy.AddMessage("- Exécuter la mise au programme à partir de la liste des fichiers XML")
        listeFichierXmlSortie = oMettreProgrammeXmlCreerZT.executer(env, listeFichierXml, noLot, noGroupe, typeProduction, listeNonConf, note)
        
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Afficher la liste des fichierXml
        arcpy.AddMessage("  listeFichierXmlSortie=%s" %listeFichierXmlSortie)
        arcpy.SetParameterAsText(7, listeFichierXmlSortie)
        #Sortir avec un code d'erreur
        sys.exit(1)

    #Sortie normale pour une exécution réussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Afficher la liste des fichierXml
    arcpy.AddMessage("  listeFichierXmlSortie=%s" %listeFichierXmlSortie)
    arcpy.SetParameterAsText(7, listeFichierXmlSortie)
    #Sortir sans code d'erreur
    sys.exit(0)