#!/usr/bin/env python
# -*- coding: Latin-1 -*-

####################################################################################################################################
# Nom       : MettreProgrammeSelectId.py
# Auteur    : Michel Pothier
# Date      : 21 octobre 2014

"""
    Application qui permet de mettre au programme les �l�ments s�lectionn�s dans un FeatureLayer.
    Le nom de l'identifiant est pr�sent dans l'attribut d'identifiant sp�cifi� du FeatureLayer.
    Le num�ro de lot contient plusieurs informations comme le type de produit et le type de travail.
    
    Param�tres d'entr�e:
    --------------------
    env                 OB      type d'environnement [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST]
                                d�faut = SIB_PRO
    featureLayer        OB      FeatureLayer contenant les identifiants s�lectionn�s
                                d�faut = ""
    attributIdentifiant OB      Nom de l'attribut du FeatureLayer contenant l'identifiant de la zone de travail
                                d�faut = DATASET_NAME
    noLot               OB      Num�ro du lot dans lequel on doit ajouter la mise au programme.
                                d�faut = aucun
    noGroupe            OB      Num�ro de groupe dans lequel on doit ajouter la mise au programme.
                                d�faut = 1
    typeProduction      OB      Indique le type de production : 'A:Autre', 'C:Contrat' et 'E:Entente'.
                                d�faut = A
    normes              OB      Num�ro de la normes selon laquelle le fichier sera produit
                                d�faut = ""
    catalogue           OP      Num�ro de catalogue selon laquelle le fichier sera produit. 
                                d�faut = ""
    fanionCollision     OB      Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme.
                                0 : la mise au programme n'est pas inscrite.
                                1 : la mise au programme est inscrite m�me s'il y a collision.
                                D�faut = 0
    listeCodeTopo       OB      Liste des codes d'�l�ments topographique trait�s.
                                d�faut = ""
    listeCollActive     OP      Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
                                d�faut = ""
    datePrevue          OP      Date pr�vue de la fin des travaux
                                d�faut = ""
    nbJoursDelai        OP      Nombre de jours de d�lai accord�s � la date pr�vue
                                d�faut = ""
    listeNonConf        OP      Liste des num�ros de non-conformit� trait�s.
                                d�faut = ""
    note                OP      Note explicative associ�e aux identifiants trait�s.
                                d�faut = ""
    
    Param�tres de sortie:
    ---------------------
    listeNoMap   : Liste des num�ros de mise au programme.
    
    Valeurs de retour:
    ------------------
    errorLevel      : Code du r�sultat de l'ex�cution du programme.
                      (Ex: 0=Succ�s, 1=Erreur)
    Usage:
        MettreProgrammeSelectId.py env featureLayer attributIdentifiant noLot noGroupe typeProduction normes
        [catalogue] fanionCollision listeCodeTopo [listeCollActive] [datePrevue] [nbJoursDelai] [listeNonConf] [note]

    Exemple:
        MettreProgrammeSelectId.py SIB_PRO DECOUPAGE DATASET_NAME 088566 01 A 4.02 4.02.1 1 10001,10002,10003 0,1,1 # # # "Note pour le lot"

"""

__version__ = "--VERSION-- : 1"
__revision__ = "--REVISION-- : $Id: MettreProgrammeSelectId.py 2144 2017-10-19 15:43:08Z mpothier $"

#####################################################################################################################################

# Importation des modules publics
import os, sys, cx_Oracle, time, arcpy, traceback

# Importation des modules priv�s (Cits)
import CompteSib

#*******************************************************************************************
class MettreProgrammeSelectId:
#*******************************************************************************************
    """
    Classe qui permet de mettre au programme les �l�ments s�lectionn�s dans un FeatureLayer
    selon l'information contenue dans un num�ro de lot.

    """

    #-------------------------------------------------------------------------------------
    def  __init__(self):
    #-------------------------------------------------------------------------------------
        """
        Initialisation du traitement de cr�ation d'un lot.
        
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
    def validerParamObligatoire(self, featureLayer, attributIdentifiant, noLot, noGroupe,
                                typeProduction, fanionCollision, normes):
    #-------------------------------------------------------------------------------------
        """
        Permet de valider la pr�sence des param�tres obligatoires.
        
        Param�tres:
        -----------
        featureLayer        : FeatureLayer contenant les �l�ments des identifiants s�lectionn�s.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'�l�ment.
        noLot               : Numr�ro de lot dans lequel la mise au programme doit �tre ajout�.
        noGroupe            : Numr�ro de groupe dans lequel la mise au programme doit �tre ajout�.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'
        fanionCollision     : Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme.
        normes              : Num�ro de la normes selon laquelle le fichier sera produit.
        
        """

        #Message de v�rification de la pr�sence des param�tres obligatoires
        arcpy.AddMessage("- V�rification de la pr�sence des param�tres obligatoires")

        if (len(featureLayer) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'featureLayer')
        
        if (len(attributIdentifiant) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'attributIdentifiant')
        
        if (len(noLot) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'noLot')
        
        if (len(noGroupe) <> 2):
            raise Exception("La valeur de GROUPE fournie est invalide : %s. Cette valeur doit �tre compos�e de 2 chiffres." %'noGroupe')
        
        if (len(typeProduction) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'typeProduction')
        
        if (len(fanionCollision) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'fanionCollision')
        
        if (len(normes) == 0):
            raise Exception("Param�tre obligatoire manquant: %s" %'normes')

        return
    
    #-------------------------------------------------------------------------------------
    def definirDate(self, date, delai):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de d�finir la date pr�vue en fonction du d�lais fourni.
        Si on founi un d�lais, il est additionn� � la date du jour pour calculer la date de fin pr�vue.
        
        Param�tres:
        -----------
        date         : Date pr�vue de la fin des travaux.
        delai        : Nombre de jours de d�lai accord�s � la date pr�vue.
       
        Retour:
        -------
        datePrevue  : Date pr�vue de la fin des travaux incluant les jours de d�lai.
        
        """
        #V�rifier la pr�sence d'un d�lai
        if delai == "":
            #D�finir la date pr�vue sans d�lai
            datePrevue = date
        #Si aucun d�lai
        else:
            #D�finir la date pr�vue avec d�lai
            delaiSec = int(delai) * 60 * 60 * 24    # nombre de jours en secondes
            datePrevue = time.strftime("%Y/%m/%d", time.localtime(time.time() + delaiSec))
        
        return datePrevue
    
    #-------------------------------------------------------------------------------------
    def extraireInfoLot(self, noLot):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant d'extraire l'information d'un lot.
        
        Param�tres:
        -----------
        noLot               : Num�ro de lot dans lequel la mise au programme doit �tre ajout�.
       
        Retour:
        -------
        typeProduit         : Nom du produit
        typeTravail         : Type de travail � effectuer

        """
        
        #V�rifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT  TY_PRODUIT, TY_TRAV FROM F601_LO WHERE NO_LOT='" + noLot + "'")

        #Si un r�sultat est pr�sent
        if resultat:
            #D�finir le type de produit
            typeProduit = resultat[0][0]
            #D�finir le type de travail
            typeTravail = resultat[0][1]
        #Si aucun r�sultat
        else:
            #Retourner une exception
            raise Exception("Num�ro de lot invalide : " + noLot)
        
        #Sortir et retourner le r�sultat
        return typeProduit, typeTravail
    
    #-------------------------------------------------------------------------------------
    def definirCodeCollision(self, listeCodeTopo, listeCollActive):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de d�finir la liste des codes topographiques et de leurs codes de collision actives.
        
        Param�tres:
        -----------
        listeCodeTopo       : Liste des codes d'�l�ments topographique trait�s.
        listeCollActive     : Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
       
        Retour:
        -------
        listeCodeTopo       : Liste des codes d'�l�ments topographique trait�s.
        listeCollActive     : Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
        
        """
       
        #Initialisation de la liste des codes topographiques et des collisions actives
        listeCode = ""
        listeCollision = ""

        #Traiter tous les codes ou liste de codes sp�cifi�s        
        listeCodeDesc = listeCodeTopo.split(",")
        for _codeDesc in listeCodeDesc:
            #Extraire le code de la description
            _code = (_codeDesc.replace("'","")).split(" :")

            #V�rifier si le code est absent de la liste des codes
            if _code[0] not in listeCode:
                #Ajouter le code � la liste de code
                listeCode = listeCode + _code[0] + ","
                
                #V�rifier si le code est pr�sent dans la liste des collisions actives
                if _code[0] in listeCollActive:
                    #On d�sactive la collision pour le code trait�
                    listeCollision = listeCollision + "1,"
                
                #Si le code est absent dans la liste des collisions actives
                else:
                    #On active la collision pour le code trait�
                    listeCollision = listeCollision + "0,"
        
        #D�finir la liste des codes et des collisions
        listeCodeTopo = listeCode.replace("'","")[:-1]
        listeCollActive = listeCollision[:-1]

        return listeCodeTopo, listeCollActive
    
    #-------------------------------------------------------------------------------------
    def validerIdentifiantLot(self, featureLayer, attributIdentifiant, noLot):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de retourner les identifiants d�j� pr�sent dans le lot.
        
        Param�tres:
        -----------
        featureLayer        : FeatureLayer contenant les �l�ments des identifiants s�lectionn�s.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'�l�ment.
        noLot               : Numr�ro de lot dans lequel la mise au programme doit �tre ajout�.
       
        Retour:
        -------
        listeIdentifiant    : Liste des identifiants d�j� pr�sents dans le lot.

        """
        
        #Initialiser la liste des identifiants d�j� pr�sents dans le lot.
        listeIdentifiant = ""

        #Traiter tous les �l�ments d'identifiant de d�coupage s�lectionn�s
        arcpy.AddMessage("- Valider la pr�sence des identifiants dans le lot ")
        #Cr�er le curseur pour la recherche
        cursor = arcpy.SearchCursor(featureLayer)
        #Extraire le premier �l�ment
        row = cursor.next()
        #traiter tant qu'il y aura des �l�ments
        while row:
            #D�finir l'identifiant trait�
            identifiant = str(row.getValue(attributIdentifiant))
        
            #V�rifier si l'identifiant est d�j� dans le lot
            sql = "SELECT F502_PS.IDENTIFIANT,F502_PS.NO_MAP FROM F502_PS, F503_TR WHERE IDENTIFIANT='" + identifiant + "' AND NO_LOT='" + noLot + "' AND F502_PS.NO_MAP=F503_TR.NO_MAP"
            resultat = self.Sib.requeteSib(sql)
            if resultat:
                listeIdentifiant = listeIdentifiant + "/" + identifiant
            
            #extraire le prochain �l�ment
            row = cursor.next()
        
        #V�rifier si des identifiants sont d�j� pr�sents dans le lot
        if len(listeIdentifiant) > 0:
            #Retourner une exception
            raise Exception("Les identifiants suivants sont d�ja dans le lot : " + listeIdentifiant)

        #Sortir et retourner le r�sultat
        return 
    
    #-------------------------------------------------------------------------------------
    def validerIdentifiant(self, typeProduit):
    #-------------------------------------------------------------------------------------
        """
        Fonction permettant de retourner le fanion pour indiquer si on doit valider l'identitifiant.
        
        Param�tres:
        -----------
        typeProduit     : Type de produit v�rifi�.
       
        Retour:
        -------
        fanionValiderIdentifiant    : Fanion pour indiquer si on doit valider l'identitifiant.
                                      0 : "SANS-DECOUPAGE"
                                      1 : "AVEC-DECOUPAGE"
        """
        
        #V�rifier si on valide l'identifiant en fonction du type de produit
        resultat = self.Sib.requeteSib("SELECT VALEUR FROM F008_PP WHERE CD_PARAMETRE='DECOUPAGE' AND TY_PRODUIT='" + typeProduit + "'")

        #Indiquer s'il s'agit d'un d�coupage pr�-d�finit
        if (not resultat) or (resultat[0][0] == "SANS-DECOUPAGE"):
            fanionValiderIdentifiant=0
        else:
            fanionValiderIdentifiant=1
        
        #Sortir et retourner le r�sultat
        return fanionValiderIdentifiant
    
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
    def miseAuProgramme(self, typeProduit, identifiant, datePrevue, normes, typeTravail, noLot, noGroupe, typeProduction, note, 
                        gabaritMeta, listeNosNonConf, listeElemTopo, listeCollActive, fanionCollision, 
                        fanionValiderIdentifiant, catalogue=""):
    #-------------------------------------------------------------------------------------
        """
        Cette m�thode effectue une mise au programme et ajoute les travaux associ�s � la production d'un jeu de donn�es pour un lot donn� dans SIB.

        Param�tres:
        ---------
        typeProduit             : Nom du produit
        identifiant             : Identifiant du produit
        datePrevue              : Date � laquelle tous les travaux c�dul�s seront termin�s
        normes                  : Normes selon laquelle le fichier sera produit
        typeProduction          : Indique le type de production : 'A', 'C' et 'E'
        note                    : Information compl�mentaire : 3 lignes de 80 caract�res maximum
        gabaritMeta             : Code indiquant le gabarit de m�tadonn�es � utiliser
        listeNosNonConf         : Liste des num�ros de non conformit�s qui seront r�gl�s par cette mise au programme (d�faut NULL) (optionnel) 
        listeElemTopo           : Liste des codes d��l�ments topographiques associ�s � cette mise au programme (d�faut NULL)(optionnel) 
        typeTravail             : Type de travail � effectuer
        noLot                   : Num�ro de lot associ� � la mise au programme
        noGroupe                : Num�ro de groupe
        listeCollActive         : Liste des valeurs � appliquer � chacun des codes d'entit�s topographiques pour la gestion des collisions
        fanionCollision         : Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme
        fanionValiderIdentifiant: Fanion indiquant si on veut valider ou non l'identifiant selon la table dictionnaires F101
        catalogue               : Num�ro du catalogue
        
        Valeurs de retour:
        -----------------
        infoMap     : Contient l'information sur la mise au programme effectu�e {"noMap":noMap, "edition":edition, "version":version}

        """
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        # Appel du service de transaction Sib qui initialise l'ajout d'une nouvelle instance de produit au programme
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Mise_au_programme", cx_Oracle.STRING, [sUsagerSib, typeProduit, identifiant, datePrevue, normes, typeProduction, note, gabaritMeta, listeNosNonConf, listeElemTopo, listeCollActive, fanionCollision, fanionValiderIdentifiant])
        # V�rifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Mise_au_programme]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute un travail � la mise au programme pr�alablement initialis�e
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Travail", cx_Oracle.STRING, [typeTravail, 1, catalogue])
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        # V�rifier le code de retour
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Travail]")
            raise Exception(message)
        
        #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable noMap
        noMap = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable edition
        edition = self.Sib.cursor.var(cx_Oracle.NUMBER)
        #d�finir la zone-m�moire o� est emmagasin�e la valeur de la variable version 
        version = self.Sib.cursor.var(cx_Oracle.NUMBER)
        
        # Appel du service de transaction qui termine l'ajout d'un travail
        codeRetour = self.Sib.cursor.callfunc("P0502_PR.pu_Ajouter_Termine", cx_Oracle.STRING, [noMap, edition, version])
        # V�rifier le code de retour
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        if code_succes <> 1:
            message.insert(0, "Erreur dans le service de transaction [P0502_PR.pu_Ajouter_Termine]")
            raise Exception(message)
        
        # Appel du service de transaction qui ajoute une instance de produit au contenu d'un lot
        codeRetour = self.Sib.cursor.callfunc("P0607_CONT.pu_Ajouter_contenu_lot", cx_Oracle.STRING, [sUsagerSib, noLot, noGroupe, noMap])
        code_succes, message =  self.Sib.callVerifierReussite(codeRetour)
        # V�rifier le code de retour
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
        
        # D�finir l'information � retourner sur la mise au programme
        infoMap = {"noMap":noMap, "edition":edition, "version":version}
        
        #Sortir et retourner l'information sur la mise au programme        
        return infoMap
 
    #-------------------------------------------------------------------------------------
    def executer(self, env, featureLayer, attributIdentifiant, noLot, noGroupe, typeProduction, normes, catalogue,
                 fanionCollision, listeCodeTopo, listeCollActive,datePrevue, nbJoursDelai, listeNonConf, note):
    #-------------------------------------------------------------------------------------
        """
        Ex�cuter le traitement de mise au programme des �l�ments d'identifiant de d�coupage s�lectionn�s.
        
        Param�tres:
        -----------
        env                 : Type d'environnement.    
        featureLayer        : FeatureLayer contenant les �l�ments des identifiants s�lectionn�s.
        attributIdentifiant : Nom de l'attribut du FeatureLayer contenant l'identifiant de l'�l�ment.
        noLot               : Numr�ro de lot dans lequel la mise au programme doit �tre ajout�.
        noGroupe            : Numr�ro de groupe dans lequel la mise au programme doit �tre ajout�.
        typeProduction      : Indique le type de production : 'A', 'C' et 'E'
        normes              : Num�ro de la normes selon laquelle le fichier sera produit
        catalogue           : Num�ro de catalogue selon laquelle le fichier sera produit. 
        fanionCollision     : Fanion indiquant l'action � prendre s'il y a collision entre les mises au programme.
        listeCodeTopo       : Liste des codes d'�l�ments topographique trait�s.
        listeCollActive     : Liste des codes de collisions active associ�s � chaque code d'�l�ment topographique sp�cifi�.
        datePrevue          : Date pr�vue de la fin des travaux
        nbJoursDelai        : Nombre de jours de d�lai accord�s � la date pr�vue
        listeNonConf        : Liste des num�ros de non-conformit� trait�s.
        note                : Note explicative associ�e aux identifiants trait�s.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : nombre de messages d'erreur g�n�r�s par le service de transaction SIB
        messageSib      : description du message re�ue du service de transaction SIB

        Valeurs de retour:
        -----------------
        listeMap        : Liste des num�ros des mises au programme.
        listeEd         : Liste des num�ros d'�dition.
        listeVer        : Liste des num�ros de version.
        listeId         : Liste des identifiants de d�coupage.
        
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
        
        #Valider si les identifiants sont d�j� pr�sents dans le lot
        self.validerIdentifiantLot(featureLayer, attributIdentifiant, noLot)
        
        #D�finir la date pr�vue en fonction du d�lai        
        arcpy.AddMessage("- D�finir la date pr�vue en fonction du d�lai")
        datePrevue = self.definirDate(datePrevue, nbJoursDelai)
        arcpy.AddMessage("  datePrevue=" + datePrevue)
        
        #D�finir le gabarit de m�tadonn�es � vide car ilo n'est plus utilis�
        gabaritMeta = ""
        
        #Extraction de la liste des codes topographiques et des collisions actives
        arcpy.AddMessage("- D�finir les codes de collisions")
        listeCodeTopo, listeCollActive = self.definirCodeCollision(listeCodeTopo, listeCollActive)
        arcpy.AddMessage("  listeCodeTopo=" + listeCodeTopo)
        arcpy.AddMessage("  listeCollActive=" + listeCollActive)
        
        #Extraire le type de produit et le type de travail � partir du num�ro de lot        
        arcpy.AddMessage("- Extraire les information du lot")
        typeProduit, typeTravail = self.extraireInfoLot(noLot)
        arcpy.AddMessage("  typeProduit=" + typeProduit)
        arcpy.AddMessage("  typeTravail=" + typeTravail)
        
        #V�rifier si l'identifiant doit �tre valid�
        arcpy.AddMessage("- V�rifier si l'identifiant de d�coupage doit �tre valid�")
        fanionValiderIdentifiant = self.validerIdentifiant(typeProduit)
        arcpy.AddMessage("  fanionValiderIdentifiant=" + str(fanionValiderIdentifiant))
        
        #Initialiser les listes
        listeMap = []
        listeEd = []
        listeVer = []
        listeId = []
        
        #Traiter tous les �l�ments d'identifiant de d�coupage s�lectionn�s
        arcpy.AddMessage("- Traiter tous les �l�ments du FeatureLayer : " + featureLayer)
        #Cr�er le curseur pour la recherche
        cursor = arcpy.SearchCursor(featureLayer)
        #Extraire le premier �l�ment
        row = cursor.next()
        #traiter tant qu'il y aura des �l�ments
        while row:
            #D�finir l'identifiant trait�
            identifiant = str(row.getValue(attributIdentifiant))
            
            #Ajouter l'identifiant dans la liste
            listeId.append(identifiant)
            
            #Mettre au programme un identifiant
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Mise au programme dans SIB : %s ..." %identifiant)
            infoMap = self.miseAuProgramme( typeProduit, 
                                            identifiant, 
                                            datePrevue,
                                            normes, 
                                            typeTravail, 
                                            noLot, 
                                            noGroupe, 
                                            typeProduction, 
                                            note, 
                                            gabaritMeta, 
                                            listeNonConf, 
                                            listeCodeTopo,
                                            listeCollActive, 
                                            fanionCollision, 
                                            fanionValiderIdentifiant,
                                            catalogue
                                            )
            
            #Affichage des informations de la MAP
            arcpy.AddMessage("  infoMap=%s" %str(infoMap))
            listeMap.append(infoMap["noMap"])
            listeEd.append(infoMap["edition"])
            listeVer.append(infoMap["version"])
            
            #extraire le prochain �l�ment
            row = cursor.next()
        
        # Sortie normale pour une ex�cution r�ussie
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        self.CompteSib.FermerConnexionSib()   #ex�cution de la m�thode pour la fermeture de la connexion de la BD SIB   
        
        #Sortir et retourner la liste des num�ro de mise au programme, des �ditions, des versions et des identifiants.
        return listeMap, listeEd, listeVer, listeId

#-------------------------------------------------------------------------------------
# Ex�cution de la fonction principale
#-------------------------------------------------------------------------------------
if __name__ == '__main__':
    # Gestion des erreurs
    try:
        #Initialisation des valeurs par d�faut
        env                 = "SIB_PRO"
        featureLayer        = ""
        attributIdentifiant = "DATASET_NAME"
        noLot               = ""
        noGroupe            = "01"
        typeProduction      = "A"
        normes              = "4.0.2"
        catalogue           = ""
        fanionCollision     = "0"
        listeCodeTopo       = ""
        listeCollActive     = ""
        datePrevue          = ""
        nbJoursDelai        = ""
        listeNonConf        = ""
        note                = ""

        #extraction des param�tres d'ex�cution
        arcpy.AddMessage(sys.argv)
        if len(sys.argv) > 1:
            env = sys.argv[1].upper()
            
        if len(sys.argv) > 2:
            featureLayer = sys.argv[2].upper()
            
        if len(sys.argv) > 3:
            attributIdentifiant = sys.argv[3].upper()
            
        if len(sys.argv) > 4:
            noLot = sys.argv[4].split(" ")[0]
            
        if len(sys.argv) > 5:
            noGroupe = sys.argv[5]
            
        if len(sys.argv) > 6:
            typeProduction = sys.argv[6].split(" ")[0]
            
        if len(sys.argv) > 7:
            normes = sys.argv[7]
            
        if len(sys.argv) > 8:
            if sys.argv[8] <> "#":
                catalogue = sys.argv[8]
                
        if len(sys.argv) > 9:
            fanionCollision = sys.argv[9]
            
        if len(sys.argv) > 10:
            listeCodeTopo = sys.argv[10].replace(";",",")
            
        if len(sys.argv) > 11:
            if sys.argv[11] <> "#":
                listeCollActive = sys.argv[11].replace(";",",")
                
        if len(sys.argv) > 12:
            if sys.argv[12] <> "#":
                datePrevue = sys.argv[12]
                
        if len(sys.argv) > 13:
            if sys.argv[13] <> "#":
                nbJoursDelai = sys.argv[13]
                
        if len(sys.argv) > 14:
            if sys.argv[14] <> "#":
                listeNonConf = sys.argv[14].replace(";",",")
                
        if len(sys.argv) > 15:
            if sys.argv[15] <> "#":
                note = sys.argv[15]
        
        # D�finir l'objet de mise au programme.
        oMettreProgrammeSelectId = MettreProgrammeSelectId()
        
        #Valider les param�tres obligatoires
        oMettreProgrammeSelectId.validerParamObligatoire(featureLayer, attributIdentifiant, noLot, noGroupe, typeProduction, fanionCollision, normes)
        
        # Ex�cuter le traitement de mise au programme.
        listeMap, listeEd, listeVer, listeId = oMettreProgrammeSelectId.executer(env, featureLayer, attributIdentifiant, noLot, noGroupe, typeProduction,
                                               normes, catalogue,fanionCollision, listeCodeTopo, listeCollActive,
                                               datePrevue, nbJoursDelai, listeNonConf, note)
    
    #Gestion des erreurs
    except Exception, err:
        #Afficher l'erreur
        arcpy.AddError(traceback.format_exc())
        arcpy.AddError(err.message)
        arcpy.AddError("- Fin anormale de l'application")
        #Afficher les listes
        arcpy.AddMessage("  listeMap=")
        arcpy.AddMessage("  listeEd=")
        arcpy.AddMessage("  listeVer=")
        arcpy.AddMessage("  listeId=")
        arcpy.SetParameterAsText(15, "")
        #Sortir avec un code d'erreur
        sys.exit(1)
    
    #Afficher le message de succ�s du traitement
    arcpy.AddMessage("- Succ�s du traitement")
    #Afficher les num�ros de mise au programme
    arcpy.AddMessage("  listeMap=%s" %str(listeMap))
    arcpy.AddMessage("  listeEd=%s" %str(listeEd))
    arcpy.AddMessage("  listeVer=%s" %str(listeVer))
    arcpy.AddMessage("  listeId=%s" %str(listeId))
    arcpy.SetParameterAsText(15, listeMap)
    #Sortir sans code d'erreur
    sys.exit(0)