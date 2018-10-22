Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.Geodatabase
Imports System.Text
Imports System.IO
Imports Microsoft.VisualBasic.FileIO
Imports ESRI.ArcGIS.Carto

'**
'Nom de la composante : clsCreerStatistiques.vb
'
'''<summary>
''' Classe générique qui permet de créer l'information pour la table des statistiques des classes spatiales d'une géodatabase.
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
''' Date : 04 Octobre 2016
'''</remarks>
''' 
Public Class clsCreerStatistiques
    '''<summary>Contient le nom de la table des statistiques.</summary>
    Protected gsNomTableStatistiques As String = ""
    '''<summary>Contient le nom de la géodatabase contenant les classes à traiter.</summary>
    Protected gsNomGeodatabaseClasses As String = ""
    '''<summary>Contient la liste des classes à traiter.</summary>
    Protected gsListeClasses As String = ""
    '''<summary>Interface contenant le nom de l'attribut de découpage à traiter.</summary>
    Protected gsNomAttributDecoupage As String = ""
    '''<summary>Contient la liste des identifiants à traiter.</summary>
    Protected gsListeIdentifiants As String = ""
    '''<summary>Nom du fichier journal d'éxécution du traitement.</summary>
    Protected gsNomFichierJournal As String = ""
    '''<summary>Contient l'information de traitement.</summary>
    Protected gsInformation As String = ""

    '''<summary>Contient le code d'erreur d'exécution.</summary>
    Protected giCodeErreur As Integer = 0
    '''<summary>Contient le nombre total de classes traitées.</summary>
    Protected giNombreTotalClasses As Integer = 0
    '''<summary>Contient le nombre total d'identifiants de découpage traitées.</summary>
    Protected giNombreTotalIdentifiants As Integer = 0
    '''<summary>Contient le nombre total de sommets.</summary>
    Protected giNombreTotalSommets As Long = 0
    '''<summary>Contient le nombre total d'éléments.</summary>
    Protected giNombreTotalElements As Long = 0

    '''<summary>Interface contenant la table des statistiques.</summary>
    Protected gpTableStatistiques As ITable = Nothing
    '''<summary>Interface contenant la géodatabase des classes à traiter.</summary>
    Protected gpGeodatabaseClasses As IFeatureWorkspace = Nothing
    '''<summary>Interface contenant la géodatabase de la table des statistiques.</summary>
    Protected gpGeodatabaseStatistiques As IFeatureWorkspace = Nothing

    '''<summary>Structure contenant l'information des statistiques.</summary>
    Protected Structure Stats
        Public NbElements As Long
        Public NbSommets As Long
        Public Existe As Boolean
    End Structure

#Region "Constructeurs"
    '''<summary>
    ''' Routine qui permet d'instancier un objet qui permet l'initialisation du traitement de création des statistiques.
    '''</summary>
    ''' 
    '''<param name="sNomTableStatistiques"> Contient le nom de la table des statistiques.</param>
    '''<param name="sNomGeodatabaseClasses"> Contient le nom de la Géodatabase des classes à traiter.</param>
    '''<param name="sListeClasses"> Contient la liste des classes à traiter.</param>
    '''<param name="sNomAttributDecoupage"> Contient le nom de l'attribut de découpage à traiter.</param>
    '''<param name="sListeIdentifiants"> Contient la liste des identifiants à traiter.</param>
    '''<param name="sNomFichierJournal"> Contient le nom du fichier journal.</param>
    ''' 
    Public Sub New(ByVal sNomTableStatistiques As String, ByVal sNomGeodatabaseClasses As String, ByVal sListeClasses As String, ByVal sNomAttributDecoupage As String, _
                   Optional ByVal sListeIdentifiants As String = "", Optional ByVal sNomFichierJournal As String = "")
        'Déclarer les variables de travail

        Try
            'Définir la table des statistiques
            gsNomTableStatistiques = sNomTableStatistiques

            'Définir la Géodatabase des classes à traiter
            gsNomGeodatabaseClasses = sNomGeodatabaseClasses

            'Conserver la liste des classes à traiter
            gsListeClasses = sListeClasses

            'Conserver le nom de l'attribut de découpage à traiter
            gsNomAttributDecoupage = sNomAttributDecoupage

            'Conserver la liste des identifiants à traiter
            gsListeIdentifiants = sListeIdentifiants

            'Conserver le nom du fichier journal
            gsNomFichierJournal = sNomFichierJournal

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de vider la mémoire.
    '''</summary>
    Protected Overrides Sub Finalize()
        'Vider la mémoire
        gsNomTableStatistiques = Nothing
        gsNomGeodatabaseClasses = Nothing
        gsListeClasses = Nothing
        gsNomAttributDecoupage = Nothing
        gsListeIdentifiants = Nothing
        gsNomFichierJournal = Nothing
        gsInformation = Nothing

        giCodeErreur = Nothing
        giNombreTotalClasses = Nothing
        giNombreTotalIdentifiants = Nothing
        giNombreTotalSommets = Nothing
        giNombreTotalElements = Nothing

        gpTableStatistiques = Nothing
        gpGeodatabaseClasses = Nothing
        gpGeodatabaseStatistiques = Nothing

        'Récupération de la mémoire disponible
        GC.Collect()
        'Finaliser
        MyBase.Finalize()
    End Sub
#End Region

#Region "Propriétés"
    '''<summary>
    ''' Propriété qui permet de retourner le nom de la table des statistiques.
    '''</summary>
    ''' 
    Public ReadOnly Property NomTableStatistiques() As String
        Get
            NomTableStatistiques = gsNomTableStatistiques
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner la table des statistiques.
    '''</summary>
    ''' 
    Public ReadOnly Property TableStatistiques() As ITable
        Get
            TableStatistiques = gpTableStatistiques
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet et retourner la Géodatabase contenant la table des statistiques.
    '''</summary>
    ''' 
    Public ReadOnly Property GeodatabaseStatistiques() As IFeatureWorkspace
        Get
            GeodatabaseStatistiques = gpGeodatabaseStatistiques
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner le nom de la géodatabase contenant les classes à traiter.
    '''</summary>
    ''' 
    Public Property NomGeodatabaseClasses() As String
        Get
            NomGeodatabaseClasses = gsNomGeodatabaseClasses
        End Get
        Set(ByVal value As String)
            gsNomGeodatabaseClasses = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner la Géodatabase contenant les classes des éléments à traiter.
    '''</summary>
    ''' 
    Public Property GeodatabaseClasses() As IFeatureWorkspace
        Get
            GeodatabaseClasses = gpGeodatabaseClasses
        End Get
        Set(ByVal value As IFeatureWorkspace)
            gpGeodatabaseClasses = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner la liste des classes.
    '''</summary>
    ''' 
    Public ReadOnly Property ListeClasses() As String
        Get
            ListeClasses = gsListeClasses
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner le nom de l'attribut de découpage à traiter.
    '''</summary>
    ''' 
    Public Property NomAttributDecoupage() As String
        Get
            NomAttributDecoupage = gsNomAttributDecoupage
        End Get
        Set(ByVal value As String)
            gsNomAttributDecoupage = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner la liste des identifiants.
    '''</summary>
    ''' 
    Public ReadOnly Property ListeIdentifiants() As String
        Get
            ListeIdentifiants = gsListeIdentifiants
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner le nom du fichier journal d'éxécution du traitement.
    '''</summary>
    ''' 
    Public ReadOnly Property NomFichierJournal() As String
        Get
            NomFichierJournal = gsNomFichierJournal
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner l'information de l'exécution du traitement.
    '''</summary>
    ''' 
    Public ReadOnly Property Information() As String
        Get
            Information = gsInformation
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le code d'erreur d'exécution des contrainte.
    '''  0: Aucune erreur d'exécution.
    '''  1: Erreur d'exécution survenue dans une requête mais sans arrêt du programme.
    ''' -1: Erreur d'exécution survenue avec arrêt du programme.
    '''</summary>
    ''' 
    Public ReadOnly Property CodeErreur() As Integer
        Get
            'Retourner lecode d'erreur d'exécution.
            CodeErreur = giCodeErreur
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le nombre total de découpage traités.
    '''</summary>
    ''' 
    Public ReadOnly Property NombreTotalIdentifiants() As Integer
        Get
            'Retourner le nombre total d'identifiants de découpage traités.
            NombreTotalIdentifiants = giNombreTotalIdentifiants
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le nombre total de classes traitées.
    '''</summary>
    ''' 
    Public ReadOnly Property NombreTotalClasses() As Integer
        Get
            'Retourner le nombre total de contraintes traitées.
            NombreTotalClasses = giNombreTotalClasses
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le nombre total de sommets trouvées.
    '''</summary>
    ''' 
    Public ReadOnly Property NombreTotalSommets() As Long
        Get
            'Retourner le nombre total d'erreurs trouvées
            NombreTotalSommets = giNombreTotalSommets
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le nombre total d'éléments traités.
    '''</summary>
    ''' 
    Public ReadOnly Property NombreTotalElements() As Long
        Get
            'Retourner le nombre total d'éléments traités
            NombreTotalElements = giNombreTotalElements
        End Get
    End Property
#End Region

#Region "Routine et fonction publiques"
    '''<summary>
    ''' Routine qui permet de vérifier si on peut exécuter le traitement de création des statistiques.
    '''</summary>
    ''' 
    '''<returns>True si le traitement est valide, False sinon.</returns>
    ''' 
    Public Function EstValide() As Boolean
        'Déclaration des variables de travail

        'Par défaut, la contrainte est valide
        EstValide = True
        gsInformation = "Le traitement de création des statistiques est valide !"

        Try
            'Vérifier si la géodatabase des classes à traiter est invalide
            If gpGeodatabaseClasses Is Nothing Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La géodatabase est invalide : " & gsNomGeodatabaseClasses

                'Vérifier si la Table des statistiques est invalide
            ElseIf gpTableStatistiques Is Nothing Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques est invalide : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas de OID
            ElseIf Not gpTableStatistiques.HasOID Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas de OID : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas d'attribut ETAMPE
            ElseIf gpTableStatistiques.FindField("ETAMPE") = -1 Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas l'attribut ETAMPE : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas d'attribut DT_C
            ElseIf gpTableStatistiques.FindField("DT_C") = -1 Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas l'attribut DT_C : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas d'attribut DT_M
            ElseIf gpTableStatistiques.FindField("DT_M") = -1 Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas l'attribut DT_M : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas d'attribut IDENTIFIANT
            ElseIf gpTableStatistiques.FindField("IDENTIFIANT") = -1 Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas l'attribut IDENTIFIANT : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas d'attribut NOM_TABLE
            ElseIf gpTableStatistiques.FindField("NOM_TABLE") = -1 Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas l'attribut NOM_TABLE : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas d'attribut NB_ELEMENT
            ElseIf gpTableStatistiques.FindField("NB_ELEMENT") = -1 Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas l'attribut NB_ELEMENT : " & gsNomTableStatistiques

                'Vérifier si la Table des statistiques ne contient pas d'attribut NB_SOMMET
            ElseIf gpTableStatistiques.FindField("NB_SOMMET") = -1 Then
                'Définir le message d'erreur
                EstValide = False
                giCodeErreur = 2
                gsInformation = "ERREUR : La table des statistiques ne contient pas l'attribut NB_SOMMET : " & gsNomTableStatistiques
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'exécuter le traitement de création des statistiques sur les classes spatiales contenues dans une Géodatabase.
    ''' 
    ''' Les statistiques sont écrites dans une table d'attributs d'une Géodatabase et correspondent au nombre d'éléments et de sommets 
    ''' par classe spatiale et par identifiant de découpage. 
    '''</summary>
    '''
    '''<returns>Boolean qui indique si le traitement a été exécuté avec succès.</returns>
    ''' 
    Public Function Executer() As Boolean
        'Déclaration des variables de travail
        Dim pFeatureClass As IFeatureClass = Nothing    'Interface contenant la classe spatiale à traiter.
        Dim pFeatureCursor As IFeatureCursor = Nothing  'Interface utilisé pour extraire les éléments.
        Dim pFeature As IFeature = Nothing              'Interface contenant un élément.
        Dim pPointColl As IPointCollection = Nothing    'Interface utilisé pour extraire le nombre de sommets.
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface utiliser pour définir une requête attributive.
        Dim sIdentifiant As String = ""                 'Contient le nom de l'identifiant traité.
        Dim dDateDebut As DateTime = Nothing            'Contient la date de début du traitement.
        Dim iPosAtt As Integer = 0                      'Position de l'attribut de découpage.
        Dim iNbElements As Long = 0                     'Contient le nombre d'éléments par classe et identifiant.
        Dim iNbSommets As Long = 0                      'Contient le nombre de sommets par classe et identifiant.
        Dim iNombreElements As Long = 0                 'Contient le nombre d'éléments par classe.
        Dim iNombreSommets As Long = 0                  'Contient le nombre de sommets par classe.
        Dim oStatsDict As Dictionary(Of String, Stats)  'Contient le dictionaire des statistiques.
        Dim oStats As Stats = Nothing                   'Contient l'information de statistique.
        Dim sUsager As String = ""                      'Contient le nom de l'usager.

        'Par défaut, le traitement ne s'est pas exécuté avec succès
        Executer = False

        Try
            'Définir la date de début
            dDateDebut = System.DateTime.Now

            'Définir le nom de l'usager
            sUsager = System.Environment.GetEnvironmentVariable("USERNAME")

            'Vérifier si le nom du fichier journal est présent
            If gsNomFichierJournal.Length > 0 Then
                'Redéfinir les noms de fichier contenant le mot %DATE_TIME%
                gsNomFichierJournal = gsNomFichierJournal.Replace("[DATE_TIME]", dDateDebut.ToString("yyyyMMdd_HHmmss"))
                'Vérifier si les répertoires existent
                If Not IO.Directory.Exists(IO.Path.GetDirectoryName(gsNomFichierJournal)) Then
                    'Créer le répertoire
                    IO.Directory.CreateDirectory(IO.Path.GetDirectoryName(gsNomFichierJournal))
                End If
            End If

            'Afficher les paramètres d'exécution du traitement
            EcrireMessage("")
            EcrireMessage("--------------------------------------------------------------------------------")
            EcrireMessage("-Version : " & IO.File.GetLastWriteTime(System.Reflection.Assembly.GetExecutingAssembly().Location).ToString)
            EcrireMessage("-Usager  : " & sUsager)
            EcrireMessage("-Date    : " & dDateDebut.ToString)
            EcrireMessage("")
            EcrireMessage("-Paramètres :")
            EcrireMessage(" --------------------------")
            EcrireMessage(" Table des statistiques    : " & gsNomTableStatistiques)
            EcrireMessage(" Géodatabase des classes   : " & gsNomGeodatabaseClasses)
            EcrireMessage(" Liste des classes         : " & gsListeClasses)
            EcrireMessage(" Attribut des identifiants : " & gsNomAttributDecoupage)
            EcrireMessage(" Liste des identifiants    : " & gsListeIdentifiants)
            EcrireMessage(" Journal d'exécution       : " & gsNomFichierJournal)
            EcrireMessage("--------------------------------------------------------------------------------")
            EcrireMessage("")

            'Écrire les statistiques d'utilisation
            Call EcrireStatistiqueUtilisation("clsCreerStatistiques.Executer " & Me.NomGeodatabaseClasses)

            'Définir la Géodatabase des classes à traiter
            gpGeodatabaseClasses = CType(DefinirGeodatabase(gsNomGeodatabaseClasses), IFeatureWorkspace)

            'Définir la table des statistiques
            gpTableStatistiques = DefinirTableStatistiques(gsNomTableStatistiques)

            'Définir la liste des classes si aucune n'est spécifiée
            Call DefinirListeClasses(gpGeodatabaseClasses, gsListeClasses)

            'Vérifier si la contrainte est valide
            If EstValide() Then
                'Traiter toutes les classes de la liste
                For Each sNomClasse In gsListeClasses.Split(CChar(","))
                    'Afficher le message
                    EcrireMessage("-Calcul des statistiques pour la classe : " & sNomClasse)

                    'Inbitialiser le dictionaire des statistiques
                    oStatsDict = New Dictionary(Of String, Stats)

                    'Compter les classes
                    giNombreTotalClasses = giNombreTotalClasses + 1

                    Try
                        'Définir la classe à traiter
                        pFeatureClass = gpGeodatabaseClasses.OpenFeatureClass(sNomClasse)
                    Catch ex As Exception
                        'Retourner l'erreur
                        Err.Raise(-1, , "ERREUR : Incapable d'ouvrir la classe spatiale : " & sNomClasse)
                    End Try

                    'Définir la position de l'attribut de découpage
                    iPosAtt = pFeatureClass.FindField(gsNomAttributDecoupage)

                    'Vérifier si l'attribut d'identifiant de découpage est présent
                    If iPosAtt = -1 Then
                        'Retourner l'erreur
                        Err.Raise(-1, , "ERREUR : L'attribut d'identifiant de découpage est absent !")
                    End If

                    'Initialiser les compteurs
                    iNombreElements = 0
                    iNombreSommets = 0

                    'Créer une nouvelle requête vide
                    pQueryFilter = New QueryFilter
                    'Vérifier si une liste d'identifiant est présent
                    If gsListeIdentifiants.Length > 0 Then
                        'Définir la requête des identifiants
                        pQueryFilter.WhereClause = gsNomAttributDecoupage & " IN ('" & gsListeIdentifiants.Replace(",", "','") & "')"
                    End If

                    'Interface contenant les éléments à traiter
                    pFeatureCursor = pFeatureClass.Search(pQueryFilter, False)

                    'Extraire le premier élément
                    pFeature = pFeatureCursor.NextFeature()

                    'Traiter tous les éléments
                    Do Until pFeature Is Nothing
                        'Définir l'identifiant
                        sIdentifiant = pFeature.Value(iPosAtt).ToString

                        'Vérifier si la géométrie est un point
                        If pFeature.Shape.GeometryType = esriGeometryType.esriGeometryPoint Then
                            'Compter les sommets
                            iNbSommets = 1

                            'Si la géométrie n'est pas un point
                        Else
                            'Interface pour extraire le nombre de sommets
                            pPointColl = CType(pFeature.Shape, IPointCollection)
                            'Compter les sommets
                            iNbSommets = pPointColl.PointCount
                        End If

                        'Vérifier si l'information est présente dans le dictionnaire
                        If oStatsDict.ContainsKey(sIdentifiant) Then
                            'Modifier l'information
                            oStats = oStatsDict.Item(sIdentifiant)

                            'Si l'information est présente dans le dictionnaire
                        Else
                            'Ajouter l'information
                            oStats = New Stats
                            oStatsDict.Add(sIdentifiant, oStats)
                        End If

                        'Définir l'information
                        giNombreTotalElements = giNombreTotalElements + 1
                        giNombreTotalSommets = giNombreTotalSommets + iNbSommets
                        iNombreElements = iNombreElements + 1
                        iNombreSommets = iNombreSommets + iNbSommets
                        oStats.NbElements = oStats.NbElements + 1
                        oStats.NbSommets = oStats.NbSommets + iNbSommets
                        oStatsDict.Item(sIdentifiant) = oStats

                        'Extraire le prochain élément
                        pFeature = pFeatureCursor.NextFeature()
                    Loop

                    'Vérifier si on doit traiter le CANADA
                    If gsListeIdentifiants.Length = 0 Then
                        'Ajouter l'information pour le CANADA
                        oStats = New Stats
                        oStats.NbElements = iNombreElements
                        oStats.NbSommets = iNombreSommets
                        oStatsDict.Add("CANADA", oStats)
                    End If

                    'Afficher le résultat pour la classe
                    EcrireMessage(" ---------------------------------------------------")
                    EcrireMessage(" Nombre total d'identifiants traités : " & oStatsDict.Count.ToString)
                    EcrireMessage(" Nombre total d'éléments trouvées    : " & iNombreElements.ToString)
                    EcrireMessage(" Nombre total de sommets trouvées    : " & iNombreSommets.ToString)
                    EcrireMessage("")

                    'Écrire les statistiques dans la table
                    Call EcrireTableStatistiques(gpTableStatistiques, oStatsDict, sNomClasse, sUsager, iNombreElements, iNombreSommets)

                    'Compter les identifiants
                    giNombreTotalIdentifiants = giNombreTotalIdentifiants + oStatsDict.Count

                    'Vider la mémoire
                    oStatsDict = Nothing
                    oStats = Nothing
                    GC.Collect()
                Next
            End If

            'Afficher le résultat pour l'ensemble de toutes les classes
            EcrireMessage("")
            EcrireMessage("-Statistiques pour l'ensemble de toutes les classes :")
            EcrireMessage(" ---------------------------------------------------")
            EcrireMessage(" Nombre total de classes traitées    : " & giNombreTotalClasses.ToString)
            EcrireMessage(" Nombre total d'identifiants traités : " & giNombreTotalIdentifiants.ToString)
            EcrireMessage(" Nombre total d'éléments trouvées    : " & giNombreTotalElements.ToString)
            EcrireMessage(" Nombre total de sommets trouvées    : " & giNombreTotalSommets.ToString)
            EcrireMessage("")
            EcrireMessage("-Temps total d'exécution : " & System.DateTime.Now.Subtract(dDateDebut).ToString)

            'Indique le succès du traitement
            Executer = True

        Catch ex As Exception
            'Écrire l'erreur
            EcrireMessage("[clsCreerStatistiques.Executer] " & ex.Message)
        Finally
            'Vider la mémoire
            pFeatureClass = Nothing
            pFeatureCursor = Nothing
            pFeature = Nothing
            pPointColl = Nothing
            sIdentifiant = Nothing
            dDateDebut = Nothing
            iPosAtt = Nothing
            pQueryFilter = Nothing
            iPosAtt = Nothing
            iNombreElements = Nothing
            iNombreSommets = Nothing
            oStatsDict = Nothing
            oStats = Nothing
            GC.Collect()
        End Try
    End Function
#End Region

#Region "Routine et fonction privées"
    '''<summary>
    ''' Routine qui permet d'écrire et afficher le nombre d'éléments et de sommets d'une classe spatiale dans la table des statistiques.
    '''</summary>
    ''' 
    '''<param name="pTableStatistiques"> Tables contenant les statistiques.</param>
    '''<param name="oStatsDict"> Contient le dictionaire des statistiques.</param>
    '''<param name="sNomClasse"> Contient le nom de la classe spatiale.</param>
    '''<param name="sUsager"> Contient le nom de l'usager.</param>
    '''<param name="iNombreElements"> Contient le nombre d'éléments par classe.</param>
    '''<param name="iNombreSommets"> Contient le nombre de sommets par classe.</param>
    ''' 
    Private Sub EcrireTableStatistiques(ByRef pTableStatistiques As ITable, ByRef oStatsDict As Dictionary(Of String, Stats), ByVal sNomClasse As String, _
                                        ByVal sUsager As String, ByVal iNombreElements As Long, ByVal iNombreSommets As Long)
        'Déclaration des variables de travail
        Dim pUpdateCursor As ICursor = Nothing      'Interface utilisé pour modifier les statistiques dans la table.
        Dim pInsertCursor As ICursor = Nothing      'Interface utilisé pour ajouter les statistiques dans la table.
        Dim pRow As IRow = Nothing                  'Interface ESRI contenant un item de la table des statistiques à modifier.
        Dim pRowBuffer As IRowBuffer = Nothing      'Interface ESRI contenant un item de la table des statistiques à créer.
        Dim pQueryFilter As IQueryFilter = Nothing  'Interface utilisé pour effectuer une requête attributive.
        Dim oStats As Stats = Nothing               'Contient l'information de statistique.
        Dim oIds As List(Of String) = Nothing       'Contient la liste des identifiants.
        Dim sIdentifiant As String = ""             'Contient le nom de l'identifiant traité.
        Dim iNombreIdentifiants As Long = 0         'Contient le nombre d'identifiants par classe.

        Try
            'Vérifier si le propriétaire de la classe est inclut dans le nom
            If sNomClasse.Contains(".") Then
                'Enlever le propriétaire de la classe du nom
                sNomClasse = sNomClasse.Split(CChar("."))(1)
            End If

            'Interface pour effectuer une requête
            pQueryFilter = New QueryFilter
            'Créer la requête pour extraire seulement les statistiques de la classe traitée
            pQueryFilter.WhereClause = "NOM_TABLE = '" & sNomClasse & "'"
            'Vérifier si des identifiants sont spécifiés
            If gsListeIdentifiants.Length > 0 Then
                'Ajouter la requête pour les identifiants à traiter
                pQueryFilter.WhereClause = pQueryFilter.WhereClause & " AND IDENTIFIANT IN ('" & gsListeIdentifiants.Replace(",", "','") & "')"
            End If
            'Interface pour créer les erreurs
            pUpdateCursor = pTableStatistiques.Update(pQueryFilter, True)
            'Extraire la première statistiques
            pRow = pUpdateCursor.NextRow()
            'Traiter toutes les statistiques existantes
            Do Until pRow Is Nothing
                'Définir l'identifiant
                sIdentifiant = pRow.Value(4).ToString
                'Vérifier si l'information est présente dans le dictionnaire
                If oStatsDict.ContainsKey(sIdentifiant) Then
                    'Modifier l'information
                    oStats = oStatsDict.Item(sIdentifiant)

                    'Si l'information est présente dans le dictionnaire
                Else
                    'Ajouter l'information
                    oStats = New Stats
                    oStatsDict.Add(sIdentifiant, oStats)
                End If
                'Indiquer que l'élément a été traité
                oStats.Existe = True
                'Mettre à jour l'information
                oStatsDict.Item(sIdentifiant) = oStats

                'Définir la statistique
                pRow.Value(1) = sUsager
                pRow.Value(3) = System.DateTime.Now
                pRow.Value(6) = oStats.NbElements
                Try
                    'Écrire le nombre de sommets
                    pRow.Value(7) = oStats.NbSommets
                Catch ex As Exception
                    'Afficher l'erreur
                    EcrireMessage(ex.Message)
                    'Définir le maximum de sommets
                    pRow.Value(7) = 2147483647
                End Try
                'Ajouter la statistique dans la table des statistiques
                pUpdateCursor.UpdateRow(pRow)

                'Extraire la prochaine statistiques
                pRow = pUpdateCursor.NextRow()
            Loop

            'Interface pour ajouter les statistiques
            pInsertCursor = pTableStatistiques.Insert(True)

            'Construire la liste des identifiants
            oIds = oStatsDict.Keys.ToList
            'Trier la liste des identifiants
            oIds.Sort()

            'Afficher les statistiques
            iNombreIdentifiants = 0
            For Each sIdentifiant In oIds
                'Définir l'information
                iNombreIdentifiants = iNombreIdentifiants + 1
                'Définir l'objet contenant les statistiques
                oStats = oStatsDict.Item(sIdentifiant)
                'Afficher l'information des statistiques total pour la classe et l'identifiant
                EcrireMessage(" " & (iNombreIdentifiants).ToString & "-" & sNomClasse & ", " & sIdentifiant & ", " & oStats.NbElements.ToString & ", " & oStats.NbSommets.ToString)
                'Vérifier si l'élément dans la table existe
                If oStats.Existe = False Then
                    'Créer une nouvelle statistique
                    pRowBuffer = gpTableStatistiques.CreateRowBuffer
                    'Définir la statistique
                    pRowBuffer.Value(1) = sUsager
                    pRowBuffer.Value(2) = System.DateTime.Now
                    pRowBuffer.Value(3) = System.DateTime.Now
                    pRowBuffer.Value(4) = sIdentifiant
                    pRowBuffer.Value(5) = sNomClasse
                    pRowBuffer.Value(6) = oStats.NbElements
                    Try
                        'Écrire le nombre de sommets
                        pRowBuffer.Value(7) = oStats.NbSommets
                    Catch ex As Exception
                        'Afficher l'erreur
                        EcrireMessage(ex.Message)
                        'Définir le maximum de sommets
                        pRowBuffer.Value(7) = 2147483647
                    End Try
                    'Ajouter la statistique dans la table des statistiques
                    pInsertCursor.InsertRow(pRowBuffer)
                End If
            Next

            'Accepter l'ajout des statistiques
            pInsertCursor.Flush()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pInsertCursor = Nothing
            pUpdateCursor = Nothing
            pRow = Nothing
            pRowBuffer = Nothing
            pQueryFilter = Nothing
            oStats = Nothing
            oIds = Nothing
            sIdentifiant = Nothing
            iNombreIdentifiants = Nothing
            GC.Collect()
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de définir la liste des classes spatiales contenues dans une géodatabase.
    ''' La liste est contruite seulement si aucune classe n'est spécifiée.
    '''</summary>
    ''' 
    '''<param name="pGeodatabaseClasses"> Géodatabase contenant les classes spatiales à traiter.</param>
    '''<param name="sListeClasses"> Liste des classes spatiales à traiter.</param>
    ''' 
    Private Sub DefinirListeClasses(ByVal pGeodatabaseClasses As IFeatureWorkspace, ByRef sListeClasses As String)
        'Déclaration des variables de travail
        Dim pDataset As IDataset = Nothing          'Contient le nom de la classe ou de la Geodatabase.
        Dim pEnumDataset As IEnumDataset = Nothing  'Interface contenant la table des contraintes.
        Dim pPropertySet As IPropertySet = Nothing  'Interface utilisée pour extraire l'usager de la BD SDE.
        Dim pWorkspace As IWorkspace = Nothing      'Interface utilisé pour vérifier s'il s'agit d'une Géodatabase SDE.
        Dim sNomClasse As String = ""               'Contient le nom de la classe.
        Dim sUser As String = ""                    'Contient le nom de l'usager de la BD SDE.

        Try
            'Vérifier si aucune classe n'est spécifiée
            If sListeClasses.Length = 0 Then
                'Interface pour extraire la liste des classes
                pDataset = CType(pGeodatabaseClasses, IDataset)

                'Interface pour vérifier s'il s'agit d'une Geédatabase SDE
                pWorkspace = CType(pGeodatabaseClasses, IWorkspace)
                'Vérifier s'il s'agit d'une Geédatabase SDE
                If pWorkspace.WorkspaceFactory.WorkspaceType = esriWorkspaceType.esriRemoteDatabaseWorkspace Then
                    'Interface pour extraire les propriétés de la Géodatabase SDE
                    pPropertySet = pWorkspace.ConnectionProperties
                    'Extraire le nom de l'usager de la BD
                    sUser = CStr(pPropertySet.GetProperty("USER")).ToUpper
                End If

                'Extraire les classes spatiales
                pEnumDataset = pDataset.Subsets

                'Extraire la première classe
                pDataset = pEnumDataset.Next

                'Traiter toutes les classes spatiales
                Do Until pDataset Is Nothing
                    'Vérifier si le Dataset est une FeatureClass
                    If pDataset.Type = esriDatasetType.esriDTFeatureClass Then
                        'Définir le nom de la classe
                        sNomClasse = pDataset.Name.ToUpper

                        'Vérifier s'il n'y a pas d'usager ou si le nom de la classe contient le nom de l'usager
                        If sUser.Length = 0 Or sNomClasse.Contains(sUser) Then
                            'Si c'est la première classe
                            If sListeClasses.Length = 0 Then
                                'Ajouter le nom de la classe
                                sListeClasses = sNomClasse

                                'Si ce n'est pas la première classe
                            Else
                                'Ajouter le nom de la classe
                                sListeClasses = sListeClasses & "," & sNomClasse
                            End If
                        End If
                    End If

                    'Extraire la prochaine classe
                    pDataset = pEnumDataset.Next
                Loop
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pEnumDataset = Nothing
            pPropertySet = Nothing
            pWorkspace = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de définir la table contenant les statistiques des classes spatiales.
    '''</summary>
    ''' 
    '''<param name="sNomTableStatistiques"> Nom de la tables contenant les statistiques.</param>
    ''' 
    Private Function DefinirTableStatistiques(ByVal sNomTableStatistiques As String) As ITable
        'Déclaration des variables de travail
        Dim pWorkspace As IWorkspace = Nothing      'Interface contenant une Géodatabase.
        Dim pTable As ITable = Nothing              'Interface contenant la table des contraintes.
        Dim sNomTable As String = ""                'Contient le nom de la table des contraintes.
        Dim sNomGeodatabase As String = ""          'Contient le nom de la Géodatabase.
        Dim sRepArcCatalog As String = ""           'Nom du répertoire contenant les connexions des Géodatabase .sde.

        'Par défaut, la table est invalide
        DefinirTableStatistiques = Nothing

        Try
            'Extraire le nom du répertoire contenant les connexions des Géodatabase .sde.
            sRepArcCatalog = IO.Directory.GetDirectories(Environment.GetEnvironmentVariable("APPDATA"), "ArcCatalog", IO.SearchOption.AllDirectories)(0)

            'Redéfinir le nom complet de la Géodatabase .sde
            sNomTableStatistiques = sNomTableStatistiques.ToLower.Replace("database connections", sRepArcCatalog)

            'Définir le nom de la table des statistiques sans le nom de la Géodatabase
            sNomTable = System.IO.Path.GetFileName(sNomTableStatistiques)

            'Définir le nom de la géodatabase sans celui du nom de la table
            sNomGeodatabase = sNomTableStatistiques.Replace("\" & sNomTable, "")
            sNomGeodatabase = sNomGeodatabase.Replace(sNomTable, "")

            'Vérifier si le nom de la Géodatabase de la table est absent
            If sNomGeodatabase.Length = 0 Then
                'Définir la Géodatabase de la table des contraintes à partir de celle des classes
                gpGeodatabaseStatistiques = gpGeodatabaseClasses
                'Interface pour extraire le nom de la Géodatabase
                pWorkspace = CType(gpGeodatabaseStatistiques, IWorkspace)
                'Définir le nom de la Géodatabase
                sNomGeodatabase = pWorkspace.PathName

                'Si le nom de la Géodatabase est présent
            Else
                'Ouvrir la géodatabase de la table des contraintes
                gpGeodatabaseStatistiques = CType(DefinirGeodatabase(sNomGeodatabase), IFeatureWorkspace)

                'Vérifier si la Géodatabase est valide
                If gpGeodatabaseStatistiques Is Nothing Then
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Le nom de la Géodatabase est invalide : " & sNomGeodatabase)
                End If
            End If

            Try
                'Ouvrir la table des contraintes
                pTable = gpGeodatabaseStatistiques.OpenTable(sNomTable)
            Catch ex As Exception
                'Retourner l'erreur
                Err.Raise(-1, , "ERREUR : Incapable d'ouvrir la table des statistiques : " & sNomTable)
            End Try

            'Définir le nom complet de la table des statistiques
            gsNomTableStatistiques = sNomGeodatabase & "\" & sNomTable

            'Retourner la table des statistiques
            DefinirTableStatistiques = pTable

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pWorkspace = Nothing
            pTable = Nothing
            sNomTable = Nothing
            sNomGeodatabase = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'ouvrir et retourner la Geodatabase à partir d'un nom de Géodatabase.
    '''</summary>
    '''
    '''<param name="sNomGeodatabase"> Nom de la géodatabase à ouvrir.</param>
    ''' 
    Private Function DefinirGeodatabase(ByRef sNomGeodatabase As String) As IWorkspace
        'Déclaration des variables de travail
        Dim pFactoryType As Type = Nothing                      'Interface utilisé pour définir le type de géodatabase.
        Dim pWorkspaceFactory As IWorkspaceFactory = Nothing    'Interface utilisé pour ouvrir la géodatabase.
        Dim sRepArcCatalog As String = ""                       'Nom du répertoire contenant les connexions des Géodatabase .sde.

        'Par défaut, aucune géodatabase n'est créée
        DefinirGeodatabase = Nothing

        Try
            'Valider le paramètre de la Geodatabase
            If sNomGeodatabase.Length > 0 Then
                'Extraire le nom du répertoire contenant les connexions des Géodatabase .sde.
                sRepArcCatalog = IO.Directory.GetDirectories(Environment.GetEnvironmentVariable("APPDATA"), "ArcCatalog", IO.SearchOption.AllDirectories)(0)

                'Redéfinir le nom complet de la Géodatabase .sde
                sNomGeodatabase = sNomGeodatabase.ToLower.Replace("database connections", sRepArcCatalog)

                'Vérifier si la Geodatabase est SDE
                If sNomGeodatabase.Contains(".sde") Then
                    'Définir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.SdeWorkspaceFactory")

                    'Si la Geodatabse est une File Geodatabase
                ElseIf sNomGeodatabase.Contains(".gdb") Then
                    'Définir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.FileGDBWorkspaceFactory")

                    'Si la Geodatabse est une personnelle Geodatabase
                ElseIf sNomGeodatabase.Contains(".mdb") Then
                    'Définir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.AccessWorkspaceFactory")

                    'Sinon
                Else
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Le nom de la Géodatabase ne correspond pas à une Geodatabase !")
                End If

                'Interface pour ouvrir le Workspace
                pWorkspaceFactory = CType(Activator.CreateInstance(pFactoryType), IWorkspaceFactory)

                Try
                    'Ouvrir le workspace de la Géodatabase
                    DefinirGeodatabase = pWorkspaceFactory.OpenFromFile(sNomGeodatabase, 0)
                Catch ex As Exception
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Incapable d'ouvrir la Géodatabase : " & sNomGeodatabase)
                End Try
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFactoryType = Nothing
            pWorkspaceFactory = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'écrire les statistiques d'utilisation d'un usager.
    ''' 
    '''<param name="sCommande"> Commande à écrire dans le fichier de statistique d'utilisation.</param>
    '''<param name="sNomRepertoire"> Nom du répertoire dans lequel le fichier de statistique est présent.</param>
    ''' 
    '''</summary>
    '''
    Protected Sub EcrireStatistiqueUtilisation(ByVal sCommande As String, Optional ByVal sNomRepertoire As String = "S:\Developpement\geo\")
        'Déclarer les variables de travail
        Dim oStreamWriter As StreamWriter = Nothing     'Objet utilisé pour écrire dans un fichier text.
        Dim sNomFichier As String = ""                  'Nom complet du fichier de statistique d'utilisation.
        Dim sNomUsager As String = ""                   'Nom de l'usager.

        Try
            'Définir le nom de l'usager
            sNomUsager = Environment.GetEnvironmentVariable("USERNAME")

            'Définir le nom complet du fichier
            sNomFichier = sNomRepertoire & sNomUsager & ".txt"

            'Vérifier si le fichier existe
            If File.Exists(sNomFichier) Then
                'Définir l'objet pour écrire à la fin du fichier
                oStreamWriter = File.AppendText(sNomFichier)

                'Si le fichier n'existe pas
            Else
                'Définir l'objet pour écrire dans un nouveau fichier créé
                oStreamWriter = File.CreateText(sNomFichier)

                'Écrire l'entête du fichier
                oStreamWriter.WriteLine("Date, 	 Env, 	 Usager, 	 UsagerBD, 	 UsagerSIB, 	 Outil")
            End If

            'Écrire la commande utilisée
            oStreamWriter.WriteLine(DateTime.Now.ToString & "," & vbTab & System.IO.Path.GetFileName(System.Environment.GetCommandLineArgs()(0)) & "," & vbTab & sNomUsager & "," & vbTab & "NONE," & vbTab & "NONE," & vbTab & sCommande)

            'Fermer le fichier
            oStreamWriter.Close()

        Catch ex As Exception
            'Retourner l'erreur
            'Throw ex
        Finally
            'Vider la mémoire
            oStreamWriter = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'écrire le message d'exécution dans la console et dans un fichier journal.
    '''</summary>
    ''' 
    '''<param name="sMessage"> Message à écrire dans un RichTextBox, un fichier journal et/ou dans la console.</param>
    '''
    Private Sub EcrireMessage(ByVal sMessage As String)
        Try
            'Écrire dans la console
            Console.WriteLine(sMessage)

            'Vérifier si le nom du fichier journal est présent
            If gsNomFichierJournal.Length > 0 Then
                'Écrire le message dans le RichTextBox
                File.AppendAllText(gsNomFichierJournal, sMessage & vbCrLf)
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub
#End Region
End Class
