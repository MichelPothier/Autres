#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom : MettreProgrammeXmlCreerZT.py
# Auteur    : Michel Pothier
# Date      : 22 octobre 2014

"""
    Application qui permet de mettre au programme dans SIB une ou plusieurs zone de travail (ZT)
    � partir de l'information contenue dans des fichiers XML.
    
    Param�tres d'entr�e:
    --------------------
        env                 OP      Type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                    d�faut = SIB_PRO
        listeFichierXml     OB      Liste des fichiers XML contenant l'information de chaque zone de travail � mettre au programme.
                                    d�faut = ""
        noLot               OB      Num�ro de lot associ� � un type de produit et un type de travail.
                                    d�faut = ""
        noGroupe            OB      Num�ro de groupe qui subdivise un lot.
                                    d�faut = "01"
        typeProduction      OB      Type de production associ� au travail.
                                    d�faut = "A"
        listeNonConf        OP      Liste des num�ros de non-conformit� trait�s.
                                    d�faut = ""
        note                OP      note explicative associ�e aux identifiants trait�s.
                                    d�faut = ""
    
    Param�tres de sortie:
    ---------------------
        listeFichierXmlSortie   : Liste des noms de fichier XML corrig�s
    
    Valeurs de retour:
    ------------------
        errorLevel              : Code du r�sultat de l'ex�cution du programme.
                                  (Ex: 0=Succ�s, 1=Erreur)
    
    Limite(s) et contrainte(s) d'utilisation:
        Les bases de donn�es doivent �tre op�rationnelles. 
    
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

#Importation des modules priv�s (Cits)
import CompteSib, util_XmlCreerZT

#*******************************************************************************************
class MettreProgrammeXmlCreerZT:
#*******************************************************************************************
    """
    Permet de mettre au programme dans SIB une ou plusieurs zone de travail (ZT)
    � partir de l'information contenue dans des fichiers XML.
    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de mise au programme.
        
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
    def validerParamObligatoire(self, env, listeFichierXml, noLot, noGroupe, typeProduction):
    #-------------------------------------------------------------------------------------
        """
        Validation de la pr�sence des param�tres obligatoires
        
        Param�tres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML � traiter
        noLot           : Num�ro de lot dans SIB
        noGroupe        : Num�ro de groupe dans SIB
        typeProduction  : Type de production dans SIB
        
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

        #Valider la pr�sence du noLot
        if (len(noLot) == 0):
            raise Exception ('Param�tre obligatoire manquant: noLot')
        
        #Valider que le groupe est compos� de 2 chiffres
        if len(noGroupe)<> 2:
            raise Exception("La valeur de GROUPE fournie est invalide : %s. "
                            "Cette valeur doit �tre compos�e de 2 chiffres." % noGroupe)

        #Valider la pr�sence du typeProduction
        if (len(typeProduction) == 0):
            raise Exception ('Param�tre obligatoire manquant: typeProduction')
 
        #Sortir
        return
    
    #-------------------------------------------------------------------------------------
    def mapSansEdVer(self, typeProduit):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant d'indiquer si la mise au programme se fait avec ou sans �dition et version.
        
        Param�tres:
        -----------
        typeProduit     : Type de produit v�rifi�.
       
        Retour:
        -------
        sansEdVer       : Indique si la mise au programme est avec ou sans �dition et version.getvalue
        
        """
        
        #V�rifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE CD_PARAMETRE='MAP-SANS-ED-VER' AND TY_PRODUIT='" + typeProduit + "'")

        #D�finir le r�sultat de la requ�te
        if resultat:
            sansEdVer = True
        else:
            sansEdVer = False
        
        #Sortir et retourner le r�sultat
        return sansEdVer

    #-------------------------------------------------------------------------------------
    def miseAuProgrammeZt(self, typeProduit, identifiant, datePrevue, normes, typeTravail, noLot, noGroupe, 
                          typeProduction, note="", listeNonConf="", validerIdentifiant=False, catalogue=""):
    #-------------------------------------------------------------------------------------
        """
        Cette m�thode effectue une mise au programme des zones de travail (ZT) et ajoute les travaux associ�s � la 
        production d'un jeu de donn�es pour un lot donn� dans SIB. Elle est utilisable seulement pour les produits
        dans SIB qui ne requierent pas de liste d'�l�ments topo. 
        (SELECT TY_PRODUIT FROM F008_PP WHERE CD_PARAMETRE = 'MAP-LISTE-ENTITE' AND VALEUR = 0)
        
        Par d�faut, la m�thode ne valide pas l'identifiant selon un dictionnaire (validerIdentifiant=False)
       
        Param�tres:
        ----------
        typeProduit             : Nom du produit
        identifiant             : Identifiant du produit
        datePrevue              : Date � laquelle tous les travaux c�dul�s seront termin�s
        normes                  : Normes selon laquelle le fichier sera produit
        typeTravail             : Type de travail � effectuer
        noLot                   : Num�ro de lot
        noGroupe                : Num�ro de groupe
        typeProduction          : Indique le type de production : 'A', 'C' et 'E'
        note                    : Information compl�mentaire : 3 lignes de 80 caract�res maximum (optionnel)
                                  (d�faut NULL)
        listeNonConf            : Liste des num�ros de non conformit�s qui seront r�gl�s par cette mise au programme (d�faut NULL) (optionnel)
        validerIdentifiant      : Fanion indiquant si on veut valider ou non l'identifiant selon la table dictionnaires F101 (d�faut=False) (optionnel)
        catalogue               : Num�ro du catalogue (d�faut NULL) (optionnel)
        
        Valeurs de retour:
        -----------------
        infoMap                 : Dictionnaire python contenant les cl�s suivantes :
                  "identifiant" : Identifiant r�sultant de la mise au programme
                  "noMap"       : Num�ro de mise au programme correspondant � l'identifiant
                  "edition"     : �dition associ�e � l'identifiant. -1 lorsque le produit n'a pas d'�dition
                  "version"     : Version associ�e � l'identifiant. -1 lorsque le produit n'a pas de version
        """

        #instanciation du logger
        fanion_validerIdentifiant = {True:1, False:0}.get(validerIdentifiant)
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()

        #D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")  # D�finition du format de la date
        
        #Appel du service de transaction Sib qui initialise l'ajout d'une nouvelle instance de produit au programme
        code_retour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Mise_au_programme", cx_Oracle.STRING, 
                                          [sUsagerSib, typeProduit, identifiant, datePrevue, normes, typeProduction, 
                                           note, "", listeNonConf, "", "", "", fanion_validerIdentifiant])
        #V�rifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Mise_au_programme]")
            raise Exception(message)
        
        #Appel du service de transaction qui ajoute un travail � la mise au programme pr�alablement initialis�e
        code_retour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Travail", cx_Oracle.STRING, [typeTravail, 1, catalogue])
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        #V�rifier le code de retour
        if code_succes <>1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Travail]")
            raise Exception(message)
        
        #D�finir la zone-m�moire o� est emmagasin�e la valeur de la variable noMap
        noMap = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #D�finir la zone-m�moire o� est emmagasin�e la valeur de la variable edition
        edition = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #D�finir la zone-m�moire o� est emmagasin�e la valeur de la variable version
        version = self.Sib.cursor.var(cx_Oracle.NUMBER)
        
        #Appel du service de transaction qui termine l'ajout d'un travail
        code_retour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Termine", cx_Oracle.STRING, [noMap, edition, version]) 
        #V�rifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Termine]")
            raise Exception(message)
        
        #Appel du service de transaction qui ajoute une instance de produit au contenu d'un lot
        code_retour = self.Sib.cursor.callfunc("P0607_CONT.pu_Ajouter_contenu_lot", cx_Oracle.STRING, [sUsagerSib, noLot, noGroupe, noMap])
        #V�rifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(code_retour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0607_CONT.pu_Ajouter_contenu_lot]")
            raise Exception(message)
            
        #D�finir le num�ro de mise au programme
        noMap = int(noMap.getvalue())
        #V�rifier si la mise au programme se fait avec �dition et version
        if self.mapSansEdVer(typeProduit):
            #D�finir l'�dition et la version � None
            edition = -1
            version = -1
        else:
            #Extraire l'�dition et la version r�sultante
            edition = int(edition.getvalue())
            version = int(version.getvalue())

        # Extraction de l'identifiant mis au programme
        requete = "SELECT IDENTIFIANT FROM F502_PS WHERE NO_MAP='%s'" % noMap
        self.Sib.cursor.execute(requete)
        identifiant = self.Sib.cursor.fetchone()[0]

        # D�finir l'information � retourner sur la mise au programme
        infoMap = {"noMap":noMap, "identifiant":identifiant,"edition":edition, "version":version}

        return infoMap

    #-------------------------------------------------------------------------------------
    def executer(self, env, listeFichierXml, noLot, noGroupe, typeProduction, listeNonConf, note):
    #-------------------------------------------------------------------------------------
        """
        Permet de mettre au programme tous les identifiants de Zone de travail (ZT)
        contenus dans chaque fichier XML de la liste.
        
        Param�tres:
        -----------
        env             : Environnement de travail
        listeFichierXml : Liste des fichiers XML � traiter
        noLot           : Num�ro de lot dans SIB
        noGroupe        : Num�ro de groupe dans SIB
        typeProduction  : Type de production dans SIB
        listeNonConf    : Liste des non-conformit�s dans SIB
        note            : Note explicative reli�e� la mise au programme
        
        Retour:
        -------
        listeFichierXmlSortie : Liste des noms de fichier XML de sortie corrig�s
        
        """
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS','PLAN'")
        resultat = self.Sib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP IN ('G-SYS','PLAN')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'G-SYS','PLAN' pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS','PLAN'")

        #D�finir les valeurs par d�faut        
        validerIdentifiant = 0
        typeProduit      = ""
        typeTravail      = ""
        normes           = ""
        catalogue        = ""
          
        #Requ�te dans SIB afin d'extraire le type de produit et le type de travail en fonction du num�ro de lot
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
        
        #Cr�er la liste des fichierXML
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
            
            #Extraire la date pr�vue
            datePrevue = oXmlCreerZT.obtenirDatePrevue()
            arcpy.AddMessage("  Date pr�vue: %s" %datePrevue)
            
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
            
            #�crire le nouvel identifiant avec le noMap dans le fichier XML
            oXmlCreerZT.definirZtId(idNoMap)
            
            #Changer le nom du fichier XML selon le nouvel identifiant contenant le noMap
            fichierXmlSortie = fichierXml.replace(identifiant, idNoMap)
            
            #�crire dans le m�me fichier le nouvel identifiant
            arcpy.AddMessage("- �criture du fichier XML %s:" %fichierXmlSortie)
            oXmlCreerZT.ecrire(fichierXmlSortie)
            
            #Ajouter le fichier XML de sortie � la liste
            listeFichierXmlSortie.append(fichierXmlSortie)
        
        # Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB
        
        #Afficher les listes
        arcpy.AddMessage("  listeMap=%s" %str(listeMap))
        arcpy.AddMessage("  listeEd=%s" %str(listeEd))
        arcpy.AddMessage("  listeVer=%s" %str(listeVer))
        arcpy.AddMessage("  listeId=%s" %str(listeId))
        
        #Sortir et retourner la liste des fichiers XML de sortie
        return listeFichierXmlSortie

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:   
        #Initialisation des valeurs par d�faut
        env                     = "SIB_PRO"
        listeFichierXml         = ""
        noLot                   = ""
        noGroupe                = "01"
        typeProduction          = "A"
        listeNonConf            = ""
        note                    = ""
        listeFichierXmlSortie   = []

        #Extraction des param�tres d'ex�cution
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
        
        #V�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")
        oMettreProgrammeXmlCreerZT.validerParamObligatoire(env, listeFichierXml, noLot, noGroupe, typeProduction)
        
        #Ex�cuter la mise au programme � partir de la liste des fichiers XML
        arcpy.AddMessage("- Ex�cuter la mise au programme � partir de la liste des fichiers XML")
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

    #Sortie normale pour une ex�cution r�ussie
    arcpy.AddMessage("- Fin normale de l'application")
    #Afficher la liste des fichierXml
    arcpy.AddMessage("  listeFichierXmlSortie=%s" %listeFichierXmlSortie)
    arcpy.SetParameterAsText(7, listeFichierXmlSortie)
    #Sortir sans code d'erreur
    sys.exit(0)