import arcpy, datetime, EnvoyerCourriel, CompteSib

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "SIB-Production-Python"
        self.alias = "SIB-Production-Python"

        # List of tool classes associated with this toolbox
        self.tools = [ModifierIdentifiantsNonConformite, ModifierEtapesTypeTravail, ModifierInfoContratLot]
        
class ModifierIdentifiantsNonConformite(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ModifierIdentifiantsNonConformite"
        self.description = "Outil qui permet de modifier l'information des identifiants de production pour un num�ro de non-conformit� et un type de produit sp�cifique dans SIB."
        self.canRunInBackground = False
        self.category = "Identifiants par non-conformit�"

        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

    def getParameterInfo(self):
        """Define parameter definitions"""
        #Env
        param0 = arcpy.Parameter(
            displayName="env",
            name="env",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param0.filter.type = "GPString"
        param0.filter.list = ["SIB_PRO", "SIB_TST", "SIB_DEV", "BDG_SIB_TST"]
        param0.value = "SIB_PRO"
        #D�finir et conserver la connexion SIB    
        self.Sib = self.CompteSib.OuvrirConnexionSib(param0.value)
        
        #Num�ros de non-conformit�
        param1 = arcpy.Parameter(
            displayName="no_nc",
            name="no_nc",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.filter.type = "GPString"
        #D�finir la liste des num�ros de non-conformit�
        resultat = self.Sib.requeteSib("SELECT NO_NC,TITRE FROM F702_NC WHERE DATE_FERMETURE IS NULL ORDER BY NO_NC DESC")
        listeNoNC = []
        for no_nc in resultat:
            listeNoNC.append(no_nc[0] + ": " + no_nc[1])
        param1.filter.list = listeNoNC
        
        #typeProduit
        param2 = arcpy.Parameter(
            displayName="typeProduit",
            name="typeProduit",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param2.filter.type = "GPString"        
        #D�finir la liste des types de produits
        resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F000_PR WHERE ISO=1 ORDER BY TY_PRODUIT")
        listeTypeProduit = []
        for typeProduit in resultat:
            listeTypeProduit.append(typeProduit[0])
        param2.filter.list = listeTypeProduit
        
        #infoIndentifiants
        param3 = arcpy.Parameter(
            displayName='IdentifiantsNonConformite',
            name='IdentifiantsNonConformite',
            datatype='GPValueTable',
            parameterType='Required',
            direction='Input')
        param3.columns = [['GPString', 'IDENTIFIANT'], ['GPString', 'ED_VER_DEBUT'], ['GPString', 'ED_VER_FIN']]
        
        #Define the result parameter
        params = [param0, param1, param2, param3]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        #V�rifier si l'environnement est sp�cifi�
        if parameters[0].value:
            #D�finir et conserver la connexion SIB    
            self.Sib = self.CompteSib.OuvrirConnexionSib(parameters[0].value)
            
            #V�rifier si l'environnement a chang�
            if parameters[0].altered and not parameters[0].hasBeenValidated:        
                #Obtenir la liste des num�ros de non-conformit�
                resultat = self.Sib.requeteSib("SELECT NO_NC,TITRE FROM F702_NC WHERE DATE_FERMETURE IS NULL ORDER BY NO_NC DESC")
                listeNoNC = []
                for no_nc in resultat:
                    listeNoNC.append(no_nc[0] + ": " + no_nc[1])
                #D�finir la liste des num�ros de non-conformit�
                parameters[1].filter.list = listeNoNC
            
            #V�rifier si le no_nc a chang�
            if parameters[1].value and ((parameters[0].altered and not parameters[0].hasBeenValidated) or (parameters[1].altered and not parameters[1].hasBeenValidated)):
                #D�finir la liste des types de produit pour le no_nc
                resultat = self.Sib.requeteSib("SELECT DISTINCT TY_PRODUIT FROM F705_PR WHERE NO_NC='" + parameters[1].value.split(":")[0] + "'")
                #V�rifier le r�sultat
                if not resultat:
                    #D�finir la liste des types de produits
                    resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F000_PR WHERE ISO=1 ORDER BY TY_PRODUIT")
                #Construire la liste des types de produit
                listeTypeProduit = []
                for typeProduit in resultat:
                    listeTypeProduit.append(typeProduit[0])
                #D�finir la liste des types de produits
                parameters[2].filter.list = listeTypeProduit
                #V�rifier si au moins un typeProduit
                if len(listeTypeProduit) > 0:
                    #D�finir la valeur par d�faut
                    parameters[2].value = listeTypeProduit[0]
            
            #V�rifier si le typeProduit a chang�
            if parameters[2].value and ((parameters[0].altered and not parameters[0].hasBeenValidated) or (parameters[1].altered and not parameters[1].hasBeenValidated) or (parameters[2].altered and not parameters[2].hasBeenValidated)):
                #Extraire les identifiants de la non-conformit� existantes
                resultat = self.Sib.requeteSib("SELECT IDENTIFIANT,ED_DEBUT||'.'||VER_DEBUT,ED_FIN||'.'||VER_FIN FROM F705_PR WHERE TY_PRODUIT='" + parameters[2].value + "' AND NO_NC='" + parameters[1].value.split(":")[0] + "' ORDER BY IDENTIFIANT")
                #V�rifier si un r�sultat est pr�sent
                if resultat:
                    #Remplir la table des valeurs
                    parameters[3].values = resultat
                
                #Obtenir la liste des identifiants permis par type de produit
                resultat = self.Sib.requeteSib("SELECT IDENTIFIANT FROM V100_ID WHERE TY_PRODUIT = '" + parameters[2].value + "' ORDER BY IDENTIFIANT")
                listeIdentifiants = []
                for identifiant in resultat:
                    listeIdentifiants.append(identifiant[0])
                #D�finir la liste des identifiants permis par type de produit
                parameters[3].filters[0].list = listeIdentifiants
       
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        #V�rifier si l'environnement est sp�cifi�
        if parameters[0].value:
            #V�rifier si le type de travail est sp�cifi�
            if parameters[1].value:
                #V�rifier si le type de produit est sp�cifi�
                if parameters[2].value:
                    #D�finir et conserver la connexion SIB    
                    self.Sib = self.CompteSib.OuvrirConnexionSib(parameters[0].value)
                    
                    #Extraire les �tapes de production existantes
                    resultat = self.Sib.requeteSib("SELECT IDENTIFIANT,ED_DEBUT||'.'||VER_DEBUT,ED_FIN||'.'||VER_FIN FROM F705_PR WHERE TY_PRODUIT='" + parameters[2].value + "' AND NO_NC='" + parameters[1].value.split(":")[0] + "' ORDER BY IDENTIFIANT")
                    #V�rifier la pr�sence des identifiants existants
                    if resultat:
                        #V�rifier si aucune modification
                        if str(map(list, resultat)) == str(parameters[3].values).replace("u'","'"):
                            #Retourner un message d'erreur
                            parameters[3].setWarningMessage("Aucune modification n'a encore �t� effectu�e !")
                
                #V�rifier si les identifiants sont sp�cifi�es
                if parameters[3].value:
                    #Traiter tous les identifiants
                    for identifiant in parameters[3].values:
                        #Obtenir la liste des �ditions et versions permises par identifiant
                        sql = "SELECT ED||'.'||VER AS ED_VER FROM F235_PR WHERE TY_PRODUIT='" + parameters[2].value + "' AND IDENTIFIANT='" + identifiant[0] + "'"
                        resultat = self.Sib.requeteSib(sql)
                        #Construire la liste des �ditions et versions permises par identifiant
                        listeEdVer = ['99999.99']
                        for edVer in resultat:
                            listeEdVer.append(edVer[0])
                        #Valider l'�dition et version de d�but
                        if identifiant[1] not in listeEdVer:
                            #Retourner un message d'erreur
                            parameters[3].setErrorMessage(u"L'�dition et version de d�but est invalide pour l'identifiant : " + identifiant[0] + "\n" + str(listeEdVer))
                        #Valider l'�dition et version de fin
                        if identifiant[2] not in listeEdVer:
                            #Retourner un message d'erreur
                            parameters[3].setErrorMessage(u"L'�dition et version de fin est invalide pour l'identifiant : " + identifiant[0] + "\n" + str(listeEdVer))
                        #V�rifier si l'�dition et version de d�but est plus grand que celui de fin
                        if float(identifiant[1]) > float(identifiant[2]):
                            #Retourner un message d'erreur
                            parameters[3].setErrorMessage(u"L'�dition et version de d�but est plus grand que celui de fin : " + identifiant[1] + ">" + identifiant[2])
                
                #Si aucun identifiant sp�cifi�
                else:
                    #Retourner un message d'erreur
                    parameters[3].setErrorMessage("Au moins un identifiant est n�cessaire!")
                
        return

    def execute(self, parameters, messages):
        """
        Ex�cuter le traitement pour modifier l'information des identifiants pour un num�ro de non-conformit� de produit.
        
        Param�tres:
        -----------  
        env                 : Type d'environnement
        noNC                : Num�ro de non-conformit�.
        typeProduit         : Type de produit.
        infoIndentifiants   : Liste des identifiants de production et de ses param�tres de traitement.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur g�n�r�s par le service de transaction SIB.
        messageSib      : Description du message re�ue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        #D�finir les variables des param�tres
        env = parameters[0].value.upper()
        noNC = parameters[1].value.split(":")[0]
        typeProduit = parameters[2].value.upper()
        infoIndentifiants = parameters[3].values
        
        #-------------------------------------------
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  
  
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        sUsagerBd = self.CompteSib.UsagerBd()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #--------------------------------------------
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #--------------------------------------------
        #Validation du num�ro de la non-conformit�
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Validation du num�ro de la non-conformit� : " + noNC)
        sql = ("SELECT DATE_FERMETURE, DATE_TRAITEMENT, TY_NC, TY_TRAIT_NC, RESP_DESCR, RESP_CORR, RESP_SUIVI FROM F702_NC WHERE NO_NC='" + noNC + "'")
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te SQL
        resultat = self.Sib.requeteSib(sql)
        #V�rifier la pr�sence du param�tre
        if (len(resultat) == 0):
            raise Exception("Num�ro de non-conformit� invalide : " + noNC)
        #V�rifier si la non-conformit� est ferm�e
        if resultat[0][0] <> None:
            raise Exception("La non-conformit� est ferm�e : date_fermeture=" + resultat[0][0])
        #V�rifier si la non-conformit� a d�j� �t� trait�e
        if resultat[0][1] <> None:
            raise Exception("La non-conformit� a d�j� �t� trait�e : date_traitement="  + resultat[0][1])   
        #Conserver l'information de la non-conformit�
        resp_descr = resultat[0][4]
        resp_corr = resultat[0][5]
        resp_suivi = resultat[0][6]
        
        #--------------------------------------------
        #D�finir la liste des identifiants permis
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�finir la liste des identifiants permis")
        sql = "SELECT IDENTIFIANT FROM V100_ID WHERE TY_PRODUIT = '" + typeProduit + "' ORDER BY IDENTIFIANT"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Initialiser la liste des identifiants permis
        listeIdentifiants = []
        #Construire la liste des identifiants permis
        for id in resultat:
            listeIdentifiants.append(id[0])
        #Afficher la liste des identifiants permis
        #arcpy.AddMessage(str(listeIdentifiants))
        
        #--------------------------------------------
        #Valider la pr�sence des identifiants de production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�truire les identifiants de la non-conformit�")
        resultat = self.Sib.requeteSib("SELECT IDENTIFIANT,ED_DEBUT||'.'||VER_DEBUT,ED_FIN||'.'||VER_FIN FROM F705_PR WHERE TY_PRODUIT='" + typeProduit + "' AND NO_NC='" + noNC + "' ORDER BY IDENTIFIANT")
        #V�rifier la pr�sence des �tapes de production
        if resultat:
            #Afficher la commande pour d�truire les identifiants de la non-conformit�
            sql = "DELETE F705_PR WHERE TY_PRODUIT='" + typeProduit + "' AND NO_NC='" + noNC + "'"
            arcpy.AddMessage(sql)
            #Afficher les �tapes existantes
            for row in resultat:
                arcpy.AddMessage(str(row))
            #D�truire les �tapes de production existantes
            self.Sib.execute(sql)
        
        #--------------------------------------------
        #Valider la liste des identifiants de la non-conformit� et leurs param�tres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider la liste des identifiants de la non-conformit� et leurs param�tres")
        #Afficher les valeurs d'attributs
        attributs = ["IDENTIFIANT", "ED_VER_DEBUT", "ED_VER_FIN"]
        arcpy.AddMessage(str(attributs))
        #Traiter tous les �l�ments du tableValue
        for row in infoIndentifiants:
            #Afficher l'information
            arcpy.AddMessage("['" + str(row[0]) + "', " + str(row[1]) + ", " + str(row[2]) + "]")
            
            #V�rifier si l'identifiant est valide
            if str(row[0]) not in listeIdentifiants:
                #Retourner un message d'erreur
                raise Exception(u"L'identifiant est invalide : " + str(row[0]))
            
            #D�finir la liste des �ditions et versions permises
            sql = "SELECT ED||'.'||VER AS ED_VER FROM F235_PR WHERE TY_PRODUIT='" + typeProduit + "' AND IDENTIFIANT='" + row[0] + "'"
            #arcpy.AddMessage(sql)
            resultat = self.Sib.requeteSib(sql)
            listeEdVer = ['99999.99']
            for edVer in resultat:
                listeEdVer.append(edVer[0])
            
            #V�rifier si l'�dition et version de d�but est valide
            if row[1] not in listeEdVer:
                #Retourner un message d'erreur
                arcpy.AddMessage(str(listeEdVer))
                raise Exception(u"L'�dition et version de d�but est invalide : " + row[1])
            
            #V�rifier si l'�dition et version de fin est valide
            if row[2] not in listeEdVer:
                #Retourner un message d'erreur
                arcpy.AddMessage(str(listeEdVer))
                raise Exception(u"L'�dition et version de fin est invalide : " + row[2])
            
            #V�rifier si l'�dition et version de d�but est plus grand que celui de fin
            if float(row[1]) > float(row[2]):
                #Retourner un message d'erreur
                raise Exception(u"L'�dition et version de d�but est plus grand que celui de fin : " + row[1] + ">" + row[2])
        
        #--------------------------------------------
        #Ajouter la liste des �tapes de production et leurs param�tres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter la liste des identifiants de la non-conformit� et leurs param�tres")
        #Traiter tous les �l�ments du tableValue
        for row in infoIndentifiants:
            #D�finir l'�dition et version de d�but
            edDebut,verDebut = row[1].split(".")
            #D�finir l'�dition et version de fin
            edFin,verFin = row[2].split(".")
            #Ajouter un identifiant du produit non-conforme
            sql = "INSERT INTO F705_PR VALUES ('" + sUsagerSib + "',SYSDATE,SYSDATE,'" + noNC + "','" + typeProduit + "','" + row[0] + "'," + edDebut + "," + verDebut + ",P0G03_UTL.PU_HORODATEUR," + edFin + "," + verFin + ")"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #--------------------------------------------
        #V�rifier si tous les intervalles de fin sont sp�cifi�s
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- V�rifier si toutes les intervalles de fin sont sp�cifi�es")
        #Construire la sql pour extraire les identifiants non-ferm�s
        sql = ("SELECT IDENTIFIANT FROM F705_PR WHERE NO_NC='" + noNC + "' AND ED_FIN=99999 ORDER BY IDENTIFIANT")
        #Afficher la sql
        arcpy.AddMessage(sql)
        #Ex�cuter la requ�te
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si toutes les intervalles de fin sont trait�es
        if not resultat:
            #Mettre � jour la date de traitement
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Mise � jour de la date de traitement")
            sql = ("UPDATE F702_NC SET ETAMPE='" + sUsagerBd + "', DT_M=SYSDATE, DATE_TRAITEMENT=SYSDATE WHERE NO_NC='" + noNC + "'")
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
            
            #Envoyer un courriel aux responsables
            arcpy.AddMessage(" ")
            arcpy.AddMessage("- Envoit d'un courriel aux responsables")
            sql = ("SELECT DISTINCT ADR_EMAIL FROM F005_US WHERE CD_USER='" + str(resp_descr) + "' OR CD_USER='" + str(resp_corr) + "' OR CD_USER='" + str(resp_suivi) +  "'")
            #Ex�cuter la requ�te SQL
            resultat = self.Sib.requeteSib(sql)
            #Traiter tous les courriels � envoyer
            for courriel in resultat:
                #D�finir l'information du courriel � envoyer
                destinataire = str(courriel[0])
                sujet = u"Fermeture de l'intervalle de fin de la non-conformit� #" + noNC
                contenu = u"Bonjour,\n\nTous les jeux de donn�es associ�s � la non conformit� #" + noNC + u" sont maintenant ferm�s.\n\n" + sUsagerSib + "\n" + sUsagerBd
                #Message d'envoit du courriel
                arcpy.AddMessage("EnvoyerCourriel('" + destinataire + "','" + sujet + "')")
                #Envoyer un courriel
                EnvoyerCourriel.EnvoyerCourriel(destinataire, contenu, sujet)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return
        
class ModifierEtapesTypeTravail(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ModifierEtapesTypeTravail"
        self.description = "Outil qui permet de modifier la liste des �tapes de production pour un type de travail et un type de produit sp�cifique dans SIB."
        self.canRunInBackground = False
        self.category = "�tapes par type de travail"

        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

    def getParameterInfo(self):
        """Define parameter definitions"""
        #Env
        param0 = arcpy.Parameter(
            displayName="env",
            name="env",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param0.filter.type = "GPString"
        param0.filter.list = ["SIB_PRO", "SIB_TST", "SIB_DEV", "BDG_SIB_TST"]
        param0.value = "SIB_PRO"
        #D�finir et conserver la connexion SIB    
        self.Sib = self.CompteSib.OuvrirConnexionSib(param0.value)

        #typeTravail
        param1 = arcpy.Parameter(
            displayName="typeTravail",
            name="typeTravail",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.filter.type = "GPString"
        #D�finir la liste des types de travail
        resultat = self.Sib.requeteSib("SELECT TY_TRAV FROM F104_TT ORDER BY TY_TRAV")
        listeTypeTravail = []
        for typeTravail in resultat:
            listeTypeTravail.append(typeTravail[0])
        param1.filter.list = listeTypeTravail

        #typeProduit
        param2 = arcpy.Parameter(
            displayName="typeProduit",
            name="typeProduit",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param2.filter.type = "GPString"

        #infoEtapes
        param3 = arcpy.Parameter(
            displayName='EtapesTypeTravail',
            name='EtapesTypeTravail',
            datatype='GPValueTable',
            parameterType='Required',
            direction='Input')
        param3.columns = [['GPString', 'CD_ETP'], ['GPLong', 'FLOTTANTE'], ['GPLong', 'RETOUR'], ['GPLong', 'ITERATIVE'], ['GPLong', 'DT_RECU_REQ'], ['GPLong', 'DT_DEB_REQ']]
        #D�finir la liste des �tapes permises
        resultat = self.Sib.requeteSib("SELECT CD_ETP FROM F117_ET WHERE ACTIVE=1 ORDER BY CD_ETP")
        listeEtapes = []
        for etape in resultat:
            listeEtapes.append(etape[0])
        param3.filters[0].list = listeEtapes
        #D�finir les valeurs permises pour les fanions Oui ou Non
        param3.filters[1].list = [0, 1]
        param3.filters[3].list = [0, 1]
        param3.filters[4].list = [0, 1]
        param3.filters[5].list = [0, 1]
        
        #Define the result parameter
        params = [param0, param1, param2, param3]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        #V�rifier si l'environnement est sp�cifi�
        if parameters[0].value:
            #D�finir et conserver la connexion SIB    
            self.Sib = self.CompteSib.OuvrirConnexionSib(parameters[0].value)
            
            #V�rifier si l'environnement a chang�
            if parameters[0].altered and not parameters[0].hasBeenValidated:        
                #D�finir la liste des types de travail
                resultat = self.Sib.requeteSib("SELECT TY_TRAV FROM F104_TT ORDER BY TY_TRAV")
                listeTypeTravail = []
                for typeTravail in resultat:
                    listeTypeTravail.append(typeTravail[0])
                parameters[1].filter.list = listeTypeTravail
                
            #V�rifier si le typeTravail a chang�
            if parameters[1].value and ((parameters[0].altered and not parameters[0].hasBeenValidated) or (parameters[1].altered and not parameters[1].hasBeenValidated)):
                #D�finir la liste des types de produit
                resultat = self.Sib.requeteSib("SELECT TY_PRODUIT FROM F105_ET WHERE TY_TRAV='" + parameters[1].value + "' AND ACTIF = 1")
                listeTypeProduit = []
                for typeProduit in resultat:
                    listeTypeProduit.append(typeProduit[0])
                #D�finir les types de produits par d�faut
                parameters[2].filter.list = listeTypeProduit
                #V�rifier si un seul typeProduit
                if len(listeTypeProduit) == 1:
                    #D�finir la valeur par d�faut
                    parameters[2].value = listeTypeProduit[0]
            
            #V�rifier si le typeProduit a chang�
            if parameters[2].value and ((parameters[0].altered and not parameters[0].hasBeenValidated) or (parameters[1].altered and not parameters[1].hasBeenValidated) or (parameters[2].altered and not parameters[2].hasBeenValidated)):
                #Extraire les �tapes de production existantes
                resultat = self.Sib.requeteSib("SELECT CD_ETP,FLOTTANTE,RETOUR,ITERATIVE,DT_RECU_REQ,DT_DEB_REQ FROM F106_EI WHERE TY_PRODUIT='" + parameters[2].value + "' AND TY_TRAV='" + parameters[1].value + "' ORDER BY NO_SEQ")
                #V�rifier si un r�sultat est pr�sent
                if resultat:
                    #Remplir la table des valeurs
                    parameters[3].values = resultat
       
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        #V�rifier si l'environnement est sp�cifi�
        if parameters[0].value:
            #V�rifier si le type de travail est sp�cifi�
            if parameters[1].value:
                #V�rifier si le type de produit est sp�cifi�
                if parameters[2].value:
                    #D�finir et conserver la connexion SIB    
                    self.Sib = self.CompteSib.OuvrirConnexionSib(parameters[0].value)
                    
                    #Extraire les �tapes de production existantes
                    resultat = self.Sib.requeteSib("SELECT CD_ETP,FLOTTANTE,RETOUR,ITERATIVE,DT_RECU_REQ,DT_DEB_REQ FROM F106_EI WHERE TY_PRODUIT='" + parameters[2].value + "' AND TY_TRAV='" + parameters[1].value + "' ORDER BY NO_SEQ")
                    #V�rifier la pr�sence des �tapes existantes
                    if resultat:
                        #V�rifier si aucune modification
                        if str(map(list, resultat)) == str(parameters[3].values).replace("u'","'"):
                            #Retourner un message d'erreur
                            parameters[3].setWarningMessage("Aucune modification n'a encore �t� effectu�e!")
                            
                #V�rifier si les �tapes sont sp�cifi�es
                if not parameters[3].value:
                    #Retourner un message d'erreur
                    parameters[3].setErrorMessage("Au moins une �tape est n�cessaire!")
                
        return

    def execute(self, parameters, messages):
        """
        Ex�cuter le traitement pour modifier l'information de lot et de groupe � partir d'un num�ro de contrat.
        
        Param�tres:
        -----------  
        env                 : Type d'environnement
        typeTravail         : Type de travail.
        typeProduit         : Type de produit.
        EtapesTypeTravail   : Liste des �tapes de production et de ses param�tres de traitement.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur g�n�r�s par le service de transaction SIB.
        messageSib      : Description du message re�ue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        #D�finir les variables des param�tres
        env = parameters[0].value.upper()
        typeTravail = parameters[1].value.upper()
        typeProduit = parameters[2].value.upper()
        etapesTypeTravail = parameters[3].values
        
        #-------------------------------------------
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Instanciation de la classe Sib et connexion � la BD Sib
        self.Sib = self.CompteSib.OuvrirConnexionSib(env, env)  

        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        # D�finition du format de la date
        self.Sib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY/MM/DD'")
        
        #--------------------------------------------
        #Valider la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'G-SYS'")
        sql = "SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND CD_GRP='G-SYS'"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe G-SYS pour ajouter un nouvel usager SIB
        if not resultat:
            #Retourner une exception
            raise Exception("L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'G-SYS'")
        
        #--------------------------------------------
        #D�finir la liste des �tapes permises
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�finir la liste des �tapes permises")
        sql = "SELECT CD_ETP FROM F117_ET WHERE ACTIVE=1 ORDER BY CD_ETP"
        arcpy.AddMessage(sql)
        resultat = self.Sib.requeteSib(sql)
        #Initialiser la liste des �tapes permises
        listeEtapes = []
        #Construire la liste des �tapes permises
        for etape in resultat:
            listeEtapes.append(etape[0])
        #Afficher la liste des codes d'�tape
        arcpy.AddMessage(str(listeEtapes))
        
        #--------------------------------------------
        #Valider la pr�sence des �tapes de production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- D�truire les �tapes de production existantes")
        resultat = self.Sib.requeteSib("SELECT NO_SEQ,CD_ETP,FLOTTANTE,RETOUR,ITERATIVE,DT_RECU_REQ,DT_DEB_REQ FROM F106_EI WHERE TY_PRODUIT='" + typeProduit + "' AND TY_TRAV='" + typeTravail + "' ORDER BY NO_SEQ")
        #V�rifier la pr�sence des �tapes de production
        if resultat:
            #Afficher la commande pour d�truire les �tapes de production existantes
            sql = "DELETE F106_EI WHERE TY_PRODUIT='" + typeProduit + "' AND TY_TRAV='" + typeTravail + "'"
            arcpy.AddMessage(sql)
            #Afficher les �tapes existantes
            for row in resultat:
                arcpy.AddMessage(str(row))
            #D�truire les �tapes de production existantes
            self.Sib.execute(sql)
        
        #--------------------------------------------
        #Valider la liste des �tapes de production et leurs param�tres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider la liste des �tapes de production et leurs param�tres")
        #Initialiser le num�ro de s�quence
        no_seq = 0
        #Afficher les valeurs d'attributs
        attributs = ["NO_SEQ", "CD_ETP", "FLOTTANTE", "RETOUR", "ITERATIVE", "DT_RECU_REQ", "DT_DEB_REQ"]
        arcpy.AddMessage(str(attributs))
        #Traiter tous les �l�ments du tableValue
        for row in etapesTypeTravail:
            #D�finir le no_seq
            no_seq = no_seq + 1
            
            #Afficher l'information
            arcpy.AddMessage("[" + str(no_seq) + ", '" + str(row[0]) + "', " + str(row[1]) + ", " + str(row[2]) + ", " + str(row[3]) + ", " + str(row[4]) + ", " + str(row[5]) + "]")
            
            #V�rifier si l'�tape est valide
            if str(row[0]) not in listeEtapes:
                #Retourner un message d'erreur
                raise Exception(u"Le code d'�tape est invalide : " + str(row[0]))
            
            #V�rifier si le fanion de l'�tape flottante est valide
            if str(row[1]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de l'�tape flottante est invalide : " + str(row[1]))
            
            #V�rifier si le fanion de l'�tape flottante est valide
            if str(row[3]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de l'�tape it�rative est invalide : " + str(row[3]))
            
            #V�rifier si l'�tape est non-it�rative
            if str(row[3]) == '0':
                #V�rifier si la valeur de l'attribut RETOUR <> 0
                if str(row[2]) <> '0':
                    #Retourner un message d'erreur
                    raise Exception(u"La valeur de l'attribut RETOUR doit �tre 0 lorsque l'�tape est non-it�rative!")
            #V�rifier si l'�tape est it�rative
            else:
                #V�rifier si la valeur de l'attribut RETOUR = 0 et > no_seq
                if row[2] == 0 or row[2] > no_seq:
                    #Retourner un message d'erreur
                    raise Exception(u"La valeur de l'attribut RETOUR doit �tre plus grand que 0 et inf�rieure au NO_SEQ lorsque l'�tape est it�rative!")
            
            #V�rifier si le fanion de la date re�u est valide
            if str(row[4]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de la date re�u est invalide : " + str(row[4]))
            
            #V�rifier si le fanion de la date de d�but est valide
            if str(row[5]) not in ['0', '1']:
                #Retourner un message d'erreur
                raise Exception(u"Le fanion de la date de d�but est invalide : " + str(row[5]))
       
        #--------------------------------------------
        #Ajouter la liste des �tapes de production et leurs param�tres
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Ajouter la liste des �tapes de production et leurs param�tres")
        #Initialiser le num�ro de s�quence
        no_seq = 0
        #Traiter tous les �l�ments du tableValue
        for row in etapesTypeTravail:
            #D�finir le no_seq
            no_seq = no_seq + 1
            
            #Ajouter une �tapes de production
            sql = "INSERT INTO F106_EI VALUES (P0G03_UTL.PU_HORODATEUR,'" + sUsagerSib + "',SYSDATE,SYSDATE,'" + typeProduit + "','" + typeTravail + "'," + str(no_seq) + ",'" + row[0] + "'," + str(row[1]) + "," + str(row[2]) + "," + str(row[3]) + "," + str(row[4]) + "," + str(row[5]) + ")"
            arcpy.AddMessage(sql)
            self.Sib.execute(sql)
        
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        self.Sib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB
        arcpy.AddMessage(" ")
        self.CompteSib.FermerConnexionSib()  
        
        #Sortir
        return

class ModifierInfoContratLot(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ModifierInfoContratLot"
        self.description = "Application qui permet de modifier l'information de lot et de groupe � partir d'un num�ro de contrat."
        self.canRunInBackground = False
        self.category = "Lots par contrat de production"

        #D�finir l'objet de gestion des comptes Sib.
        self.CompteSib = CompteSib.CompteSib()

    def getParameterInfo(self):
        """Define parameter definitions"""
        #Env
        param0 = arcpy.Parameter(
            displayName="env",
            name="env",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param0.filter.type = "GPString"
        param0.filter.list = ["SIB_PRO", "SIB_TST", "SIB_DEV", "BDG_SIB_TST"]
        param0.value = "SIB_PRO"
        #D�finir et conserver la connexion SIB    
        self.Sib = self.CompteSib.OuvrirConnexionSib(param0.value)

        #typeTravail
        param1 = arcpy.Parameter(
            displayName="typeTravail",
            name="typeTravail",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param1.filter.type = "GPString"
        #D�finir la liste des types de travail
        resultat = self.Sib.requeteSib("SELECT DISTINCT TY_TRAV FROM F601_LO WHERE NO_CONTRAT IS NOT NULL AND E_LOT <> 'T' ORDER BY TY_TRAV")
        listeTypeTravail = []
        for typeTravail in resultat:
            listeTypeTravail.append(typeTravail[0])
        param1.filter.list = listeTypeTravail

        #noSecteur
        param2 = arcpy.Parameter(
            displayName="noSecteur",
            name="noSecteur",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        param2.filter.type = "GPString"

        #noContrat
        param3 = arcpy.Parameter(
            displayName="noContrat",
            name="noContrat",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param3.filter.type = "GPString"

        #executant
        param4 = arcpy.Parameter(
            displayName="executant",
            name="executant",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param4.filter.type = "GPString"
        #D�finir la liste des codes d'ex�cutant
        resultat = self.Sib.requeteSib("SELECT CD_EXECU FROM F604_EX")
        listeCodeExecutant = []
        for CodeExecutant in resultat:
            listeCodeExecutant.append(CodeExecutant[0])
        param4.filter.list = listeCodeExecutant

        #contact
        param5 = arcpy.Parameter(
            displayName="contact",
            name="contact",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param5.filter.type = "GPString"

        #noTicket
        param6 = arcpy.Parameter(
            displayName="noTicket",
            name="noTicket",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        param6.filter.type = "GPString"

        #dateDebut
        param7 = arcpy.Parameter(
            displayName="dateDebut",
            name="dateDebut",
            datatype="GPDate",
            parameterType="Required",
            direction="Input")

        #dateFin
        param8 = arcpy.Parameter(
            displayName="dateFin",
            name="dateFin",
            datatype="GPDate",
            parameterType="Required",
            direction="Input")
        #D�finir la date de fin par d�faut
        param8.value = str(datetime.date.today())

        #infoLots
        param9 = arcpy.Parameter(
            displayName='infoLots',
            name='infoLots',
            datatype='GPValueTable',
            parameterType='Required',
            direction='Input')
        param9.columns = [['GPString', 'NO_LOT'], ['GPDouble', 'PRIX_CONTRAT'], ['GPDate', 'DT_RECEP']]
        
        #Define the result parameter
        params = [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        #V�rifier si l'environnement est sp�cifi�
        if parameters[0].value:
            #D�finir et conserver la connexion SIB    
            self.Sib = self.CompteSib.OuvrirConnexionSib(parameters[0].value)
            
            #V�rifier si l'environnement a chang�
            if parameters[0].altered and not parameters[0].hasBeenValidated:        
                #D�finir la liste des types de travail
                resultat = self.Sib.requeteSib("SELECT DISTINCT TY_TRAV FROM F601_LO WHERE NO_CONTRAT IS NOT NULL AND E_LOT <> 'T' ORDER BY TY_TRAV")
                listeTypeTravail = []
                for typeTravail in resultat:
                    listeTypeTravail.append(typeTravail[0])
                parameters[1].filter.list = listeTypeTravail
                
            #V�rifier si le ty_travail a chang�
            if parameters[1].value and ((parameters[0].altered and not parameters[0].hasBeenValidated) or (parameters[1].altered and not parameters[1].hasBeenValidated)):
                #D�finir la liste des num�ros de contrat en cours
                resultat = self.Sib.requeteSib("SELECT DISTINCT NO_CONTRAT,TY_PRODUIT FROM F601_LO WHERE TY_TRAV='" + parameters[1].value + "' AND NO_CONTRAT IS NOT NULL AND E_LOT <> 'T' ORDER BY NO_CONTRAT DESC")
                listeNoContrat = []
                for noContrat in resultat:
                    listeNoContrat.append(noContrat[0])
                parameters[2].filter.list = listeNoContrat
                            
            #V�rifier si le no_contrat a chang�
            if parameters[2].value and ((parameters[0].altered and not parameters[0].hasBeenValidated) or (parameters[2].altered and not parameters[2].hasBeenValidated)):
                #D�finir les noSecteur
                listeSecteur = ""
                for secteur in parameters[2].values:
                    #Ajouter le secteur
                    listeSecteur = listeSecteur + "'" + secteur + "'"
                listeSecteur = listeSecteur.replace("''", "','")
                
                #Extraire l'information du num�ro de lot
                parameters[3].value = str(parameters[2].values)
                resultat = self.Sib.requeteSib("SELECT DISTINCT NO_CONTRAT,CD_EXECU,NO_CONTACT,DT_DEBUT,DT_FIN,NO_TICKET,PRIX_CONTRAT FROM F601_LO WHERE NO_CONTRAT IN (" + listeSecteur + ") ORDER BY NO_CONTRAT")
                #V�rifier si un r�sultat est pr�sent
                if len(resultat) > 0:
                    #D�finir le NO_CONTRAT
                    parameters[3].value = resultat[0][0]
                    #D�finir le CD_EXECU
                    parameters[4].value = resultat[0][1]
                    #D�finir le NO_CONTACT
                    parameters[5].value = resultat[0][2]
                    #D�finir le NO_TICKET
                    parameters[6].value = resultat[0][5]
                    #D�finir la DT_DEBUT
                    parameters[7].value = resultat[0][3]
                    #D�finir la DT_FIN
                    parameters[8].value = resultat[0][4]

                #Extraire les �tapes de production existantes
                resultat = self.Sib.requeteSib("SELECT A.NO_LOT,A.PRIX_CONTRAT,B.DT_RECEP FROM F601_LO A, F601_GR B WHERE A.NO_LOT=B.NO_LOT AND NO_CONTRAT IN (" + listeSecteur + ") ORDER BY A.NO_LOT")
                #V�rifier si un r�sultat est pr�sent
                if len(resultat) > 0:
                    #Remplir la table des valeurs
                    parameters[9].values = resultat
            
            #V�rifier si le code d'ex�cutant est sp�cifi�
            if parameters[4].value and ((parameters[0].altered and not parameters[0].hasBeenValidated) or (parameters[4].altered and not parameters[4].hasBeenValidated)):
                #D�finir la liste des num�ros de contact selon le code d'ex�cutant
                resultat = self.Sib.requeteSib("SELECT NO_CONTACT,NOM FROM F607_CO WHERE CD_EXECU = '" + parameters[4].value + "'")
                #Initialiser la liste des contacts
                listeNoContact = []
                #Traiter tous les contacts
                for noContact in resultat:
                    #Ajouter le contact
                    listeNoContact.append(str(noContact[0]) + ":" + noContact[1])
                    #V�rifier si le no de contact correspond
                    if parameters[5].value == str(noContact[0]):
                        parameters[5].value = str(noContact[0]) + ":" + noContact[1]
                #D�finir la liste des contacts
                parameters[5].filter.list = listeNoContact
                #V�rifier si un seul contact est pr�sent
                if len(listeNoContact) == 1:
                    #Red�finir le contact
                    parameters[5].value = listeNoContact[0]

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        #V�rifier la pr�sence de la valeur
        if parameters[7].value and parameters[8].value:
            #V�rifier si la date de d�butest plus grande que la date de fin
            if parameters[7].value > parameters[8].value:
                #Retourner un message d'erreur
                parameters[8].setErrorMessage(u"La date de fin est inf�rieure � la date de d�but")
        
        #V�rifier si l'environnement et le secteur sont sp�cifi�s
        if parameters[0].value and parameters[2].value:
            #D�finir et conserver la connexion SIB    
            self.Sib = self.CompteSib.OuvrirConnexionSib(parameters[0].value)
            
            #D�finir les noSecteur
            listeSecteur = ""
            for secteur in parameters[2].values:
                #Ajouter le secteur
                listeSecteur = listeSecteur + "'" + secteur + "'"
            listeSecteur = listeSecteur.replace("''", "','")
            
            #Iniialiser la liste des lots
            lots = []
            #D�finir la liste des types de travail
            resultat = self.Sib.requeteSib("SELECT NO_LOT FROM F601_LO WHERE NO_CONTRAT IN (" + listeSecteur + ")")
            #Traiter tous les no_lot
            for noLot in resultat:
                #Conserver les lots
                lots.append(str(noLot[0]))
            
            #Retourner un message d'erreur
            parameters[9].setWarningMessage("Remplir l'information pour les lots suivants : " + str(lots))

        return

    def execute(self, parameters, messages):
        """
        Ex�cuter le traitement pour modifier l'information de lot et de groupe � partir d'un num�ro de contrat.
        
        Param�tres:
        -----------
        env             : Type d'environnement.    
        typeTravail     : Type de travail � effetuer sur tous les identifiants du lot, pr�alablement d�fini dans SIB.
        noSecteur       : Liste des num�ros de secteur correspondant au num�ro de contrat temporaire.
        noContrat       : Num�ro de contrat.
        executant       : Code du contractant � qui le contrat a �t� octroy�.
        contact         : Num�ro de contact, chez le contractant, responsable du lot.
        noTicket        : Num�ro de ticket.
        dateDebut       : Date de d�but de traitement du lot.
        dateFin         : Date de fin de traitement du lot.
        infoLot         : Information sur le prix du contrat et la date de r�ception pour chaque lot du contrat.
        
        Variables:
        ----------
        self.CompteSib  : Objet utilitaire pour la gestion des connexion � SIB.       
        oSib            : Objet utilitaire pour traiter des services SIB.
        sUsagerSib      : Nom de l'usager SIB.
        code_retour     : Code de retour d'un service SIB.
        nbMessSib       : Nombre de messages d'erreur g�n�r�s par le service de transaction SIB.
        messageSib      : Description du message re�ue du service de transaction SIB.

        Valeurs de retour:
        -----------------
        Aucun
        """
        #D�finir les variables des param�tres
        env = parameters[0].value.upper()
        typeTravail = parameters[1].value.upper()
        noSecteur = ""
        for secteur in parameters[2].values:
            noSecteur = noSecteur + "'" + secteur + "'"
        noSecteur = noSecteur.replace("''", "','")
        noContrat = parameters[3].value
        codeExecutant = parameters[4].value.upper()
        noContact = parameters[5].value.split(":")[0]
        noTicket = parameters[6].value
        dateDebut = str(parameters[7].value).split(" ")[0]
        dateFin = str(parameters[8].value).split(" ")[0]
        infoLot = parameters[9].values
        
        #-------------------------------------------
        #Instanciation de la classe Sib et connexion � la BD Sib
        oSib = self.CompteSib.OuvrirConnexionSib(env, env)  
        
        #Extraire le nom de l'usager SIB
        sUsagerSib = self.CompteSib.UsagerSib()
        
        #D�finition du format de la date
        oSib.cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'YYYY-MM-DD hh24:mi:ss'")
        
        #Extraire la liste des groupes de privil�ge de l'usager
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider si l'usager poss�de le groupe de privil�ges 'PLAN' ou 'G-SYS'")
        resultat = oSib.requeteSib("SELECT CD_GRP FROM F007_UG WHERE CD_USER='" + sUsagerSib + "' AND (CD_GRP='PLAN' OR CD_GRP='G-SYS')")
        #V�rifier si l'usager SIB poss�de les privil�ge de groupe 'PLAN' ou 'G-SYS'
        if not resultat:
            #Retourner une exception
            raise Exception(u"L'usager SIB '" + sUsagerSib + "' ne poss�de pas le groupe de privil�ges : 'PLAN' ou 'G-SYS'")
        
        #Valider le type de travail et les num�ros de secteur en production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Valider le type de travail et les num�ros de secteur en production")
        sql = "SELECT DISTINCT NO_CONTRAT FROM F601_LO WHERE TY_TRAV='" + typeTravail + "' AND NO_CONTRAT IN (" + noSecteur + ") AND E_LOT <> 'T'"
        arcpy.AddMessage(sql)
        resultat = oSib.requeteSib(sql)
        #V�rifier si le nombre de secteur correspond
        if len(resultat) <> len(noSecteur.split(",")):
            #Retourner une exception
            raise Exception(u"Les num�ros de secteur sont invalides : " + str(resultat))

        #V�rifier si la date de d�but est plus grande que la date de fin
        if dateDebut >= dateFin:
            #Retourner une exception
            raise Exception(u"La date de d�but est plus grande que la date de fin : " + dateDebut + ">=" + dateFin)
        
        #-------------------------------------------
        #Modifier l'information du lot de production
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Modifier l'information pour le contrat en cours de production")
        #D�finir la commande SQL de modification
        sql = "UPDATE F601_LO SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE"
        sql = sql + ", NO_CONTRAT='" + noContrat + "', CD_EXECU='" + codeExecutant + "', NO_CONTACT=" + noContact
        sql = sql + ", NO_TICKET='" + noTicket + "', DT_DEBUT=TO_DATE('" + dateDebut + "'), DT_FIN=TO_DATE('" + dateFin + "')"
        sql= sql + " WHERE NO_CONTRAT IN (" + noSecteur + ")"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #-------------------------------------------
        #Iniialiser la liste des lots entr�s
        lotsEntres = []
        #afficher l'identifiant de l'�l�ment
        arcpy.AddMessage("  ")
        arcpy.AddMessage("- Modifier l'information pour chaque lot en cours de production")
        #Traiter tous les �l�ments du tableValue
        for row in infoLot:
            #Afficher l'identifiant de l'�l�ment
            arcpy.AddMessage("#" + str(row[0]) + " " + str(row[1]) + " '" + str(row[2]) + "'")
            
            #Conserver les lots entr�s
            noLot = str(row[0])
            lotsEntres.append(noLot)
            
            #Valider le prix du contrat
            try:
                prixContrat = int(row[1])
            except:
                #Retourner une exception
                raise Exception(u"Le prix du contrat est invalide : " + str(row[1]))
            
            #Valider la date de r�ception
            dateRecep = str(row[2]).split(" ")[0]
            
            #Valider le num�ro de lot
            resultat = oSib.requeteSib("SELECT NO_LOT FROM F601_LO WHERE NO_LOT='" + noLot + "' AND NO_CONTRAT='" + noContrat + "'")
            #V�rifier si le num�ro de lot est invalide
            if not resultat:
                #Retourner une exception
                raise Exception(u"Le num�ro de lot est invalide : " + noLot)
            
            #D�finir la commande SQL de modification
            sql = "UPDATE F601_LO SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, PRIX_CONTRAT=" + str(prixContrat)
            sql= sql + " WHERE NO_LOT='" + noLot + "'"
            arcpy.AddMessage(sql)
            oSib.execute(sql)
            
            #D�finir la commande SQL de modification pour changer la date de r�ception
            sql = "UPDATE F601_GR SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" + sUsagerSib + "', DT_M=SYSDATE, DT_RECEP=TO_DATE('" + dateRecep + "')"
            sql= sql + " WHERE NO_LOT='" + noLot + "'"
            arcpy.AddMessage(sql)
            oSib.execute(sql)
            arcpy.AddMessage(" ")

        #V�rifier si aucun lot entr�
        if len(lotsEntres) == 0:
            #Retourner une exception
            arcpy.AddWarning(u"ATTENTION : Aucun lot n'a �t� sp�cifi�.")
            arcpy.AddMessage(" ")
            
        #-------------------------------------------
        #Initialiser la liste des lots absents
        arcpy.AddMessage("- Valider l'information pour tous les lots pr�sents : " + str(lotsEntres))
        lotsAbsents = []
        sql = "SELECT NO_LOT FROM F601_LO WHERE NO_CONTRAT='" + noContrat + "'"
        arcpy.AddMessage(sql)
        #D�finir la liste des types de travail
        resultat = oSib.requeteSib(sql)
        #Traiter tous les no_lot
        for noLot in resultat:
            #V�rifier si le noLot est absent la liste des lots entres
            if noLot[0] not in lotsEntres:
                #Conserver les lots absents
                lotsAbsents.append(noLot[0])
        
        #V�rifier si le noLot est pr�sent dans la liste
        if len(lotsAbsents) > 0:
            #Retourner une exception
            arcpy.AddWarning(u"ATTENTION : Information absente pour les lots suivants : " + str(lotsAbsents))
        
        #-------------------------------------------
        #Accepter les modifications
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Accepter les modifications")
        sql = "COMMIT"
        arcpy.AddMessage(sql)
        oSib.execute(sql)
        
        #Fermeture de la connexion de la BD SIB 
        arcpy.AddMessage(" ")
        arcpy.AddMessage("- Fermeture de la connexion SIB")
        oSib.fermerConnexionSib()

        #messages.addMessage("Success of process")
        
        #Sortir
        return
