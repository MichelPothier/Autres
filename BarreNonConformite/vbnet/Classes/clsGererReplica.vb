Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.GeoDatabaseDistributed
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.Server
Imports System.Windows.Forms
Imports System.Runtime.InteropServices
Imports ESRI.ArcGIS.Editor

'**
'Nom de la composante : clsGererReplica.vb
'
'''<summary>
''' Classe qui permet de gérer un réplica d'une Géodatabase locale afin de pouvoir définir ou extraire l'information liées aux divers changements effectués aux données.
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
'''</remarks>
''' 
Public Class clsGererReplica
    '''<summary> Géodatabase parent dans laquelle les données d'origines ont été retirées et les changements doivent être déposés.</summary>
    Protected gpGdbParent As IWorkspace = Nothing
    '''<summary> Géodatabase enfant contenant les changements, les données ajoutées, détruites et modifiées.</summary>
    Protected gpGdbEnfant As IWorkspace = Nothing
    '''<summary> Géodatabase d'archive dans laquelle les données originales ont été retirés.</summary>
    Protected gpGdbArchive As IWorkspace = Nothing
    '''<summary> Interface contenant l'information du réplica contenu dans la Géodatabase parent.</summary>
    Protected gpReplicaParent As IReplica3 = Nothing
    '''<summary> Interface contenant l'information du réplica contenu dans la Géodatabase enfant.</summary>
    Protected gpReplicaEnfant As IReplica3 = Nothing
    '''<summary> Interface contenant les changements dans les données de la Géodatabase enfant.</summary>
    Protected gpDataChanges As IDataChanges = Nothing
    '''<summary> Interface pour annuler le traitement et afficher l'information.</summary>
    Protected gpTrackCancel As ITrackCancel = Nothing
    '''<summary> Contient le nombre de conflits trouvés.</summary>
    Protected giNbConflits As Integer = -1
    '''<summary> Contient le nombre de différences trouvés.</summary>
    Protected giNbDifferences As Integer = -1

#Region "Propriétés"
    '''<summary>
    ''' Propriété qui permet de définir et retourner la Géodatabase parent.
    '''</summary>
    ''' 
    Public Property GdbParent() As IWorkspace
        Get
            GdbParent = gpGdbParent
        End Get
        Set(ByVal value As IWorkspace)
            gpGdbParent = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner la Géodatabase enfant.
    '''</summary>
    ''' 
    Public ReadOnly Property GdbEnfant() As IWorkspace
        Get
            GdbEnfant = gpGdbEnfant
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner la Géodatabase d'archive.
    '''</summary>
    ''' 
    Public Property GdbArchive() As IWorkspace
        Get
            GdbArchive = gpGdbArchive
        End Get
        Set(ByVal value As IWorkspace)
            gpGdbArchive = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le réplica de la Géodatabase parent.
    '''</summary>
    ''' 
    Public ReadOnly Property ReplicaParent() As IReplica3
        Get
            ReplicaParent = gpReplicaParent
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le réplica de la Géodatabase enfant.
    '''</summary>
    ''' 
    Public ReadOnly Property ReplicaEnfant() As IReplica3
        Get
            ReplicaEnfant = gpReplicaEnfant
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner les changements de la Géodatabase enfant qui contient un réplica valide.
    '''</summary>
    ''' 
    Public ReadOnly Property DataChanges() As IDataChanges
        Get
            DataChanges = gpDataChanges
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner l'interface pour annuler le traitement et afficher l'information.
    '''</summary>
    ''' 
    Public Property TrackCancel() As ITrackCancel
        Get
            TrackCancel = gpTrackCancel
        End Get
        Set(ByVal value As ITrackCancel)
            gpTrackCancel = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le nombre de conflits trouvées entre la Géodatabase parent et l'archive interne ou externe de la Géodatabase enfant.
    '''</summary>
    ''' 
    Public ReadOnly Property NbConflits() As Integer
        Get
            NbConflits = giNbConflits
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le nombre de différences trouvées entre la Géodatabase enfant et son archive interne ou externe.
    '''</summary>
    ''' 
    Public ReadOnly Property NbDifferences() As Integer
        Get
            NbDifferences = giNbDifferences
        End Get
    End Property
#End Region

#Region "Routines et fonctions d'initialisation"
    '''<summary>
    ''' Routine qui permet de créer un réplica de type CheckOut à partir d'une géodatabase SDE en copiant les classes et identifiants spécifiées de la BDG
    ''' dans une géodatabase locale (.mdb ou .gdb).
    '''</summary>
    '''
    '''<param name="sNomReplica">Nom du réplica.</param>
    '''<param name="sNomGdbParent">Nom de la Géodatabase Parent .sde.</param>
    '''<param name="sNomGdbEnfant">Nom de la Géodatabase enfant .mdb ou .gdb.</param>
    '''<param name="sListeNomClasse">Liste des noms des classe à extraire de la BDG spéparés par des virgules en incluant le nom du propriétaire.</param>
    '''<param name="sListeIdentifiants">Liste des identifiants à extraire de la BDG spéparés par des virgules et apostrophes.</param>
    '''<param name="sNomAttributId">Nom de l'attribut des identifiants de la BDG.</param>
    '''<param name="pTypeModel">Indique le type de model Simple ou complet.</param>
    '''<param name="pEsriDataExtractionType">Indique le type d'extraction à effectuer (esriDataCheckOut ou esriDataExtraction).</param>
    '''<param name="pGeometry">Indique la géométrie utiliser pour effectuer la requête spatiale.</param>
    '''<param name="pSpatialRelation">Indique le type de requête spatiale à effecter.</param>
    ''' 
    Public Sub CreerReplicaBDG(ByVal sNomReplica As String, ByRef sNomGdbParent As String, ByRef sNomGdbEnfant As String,
                               ByVal sListeNomClasse As String, ByVal sListeIdentifiants As String, ByVal sNomAttributId As String,
                               Optional ByVal pTypeModel As esriReplicaModelType = esriReplicaModelType.esriModelTypeSimple,
                               Optional ByVal pEsriDataExtractionType As esriDataExtractionType = esriDataExtractionType.esriDataCheckOut,
                               Optional ByVal pGeometry As IGeometry = Nothing,
                               Optional ByVal pSpatialRelation As esriSpatialRelEnum = esriSpatialRelEnum.esriSpatialRelIntersects)
        'Déclarer les variables de travail
        Dim pWorkspaceReplicas As IWorkspaceReplicas2 = Nothing 'Interface pour vérifier si le réplica est déjà présent.
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface pour extraire les classes à traiter.
        Dim pEnumNameEdit As IEnumNameEdit = Nothing            'Interface contenant la liste des classes à extraire.
        Dim pDataset As IDataset = Nothing                      'Interface pour définir la classe à extraire de la géodatabase.
        Dim pRepDescription As IReplicaDescription4 = Nothing   'Interface contenant la description du CheckOut.
        Dim pRepFilterDescEdit As IReplicaFilterDescriptionEdit = Nothing   'Interface pour modifier la méthode d'extraction du checkOut.
        Dim pDataExtraction As IDataExtraction = Nothing        'Interface pour exécuter le DataExtraction
        Dim pCheckOut As ICheckOut = Nothing                    'Interface pour exécuter le CheckOut.
        Dim sExtGdbEnfant As String = Nothing                   'Extension du nom de la Géodatabase enfant.
        Dim sRequeteAttributive As String = ""                  'Contient la requête attributive pour extraire la liste des identifiants par classe de la BDG.
        Dim dDateDebut As DateTime = Nothing                    'Contient la date de début du traitement.
        Dim sTempsTraitement As String = ""                     'Temps de traitement.
        Dim pFeatureProgress As IFeatureProgress = Nothing

        Try
            'Initialiser les compteurs
            giNbConflits = -1
            giNbDifferences = -1

            'Définir la date de début
            dDateDebut = System.DateTime.Now
            'Afficher l'information du début du tratement de Réplica
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Début du traitement de Réplica ..."

            'Définir la Géodatabase parent
            gpGdbParent = DefinirGeodatabase(sNomGdbParent)

            'Interface pour vérifier si le réplica est déjà présent.
            pWorkspaceReplicas = CType(gpGdbParent, IWorkspaceReplicas2)

            'Rafraichir les réplicas
            pWorkspaceReplicas.RefreshReplicas()

            Try
                'Définir le réplica parent
                gpReplicaParent = CType(pWorkspaceReplicas.ReplicaByName(sNomReplica), IReplica3)
            Catch ex As Exception
                'On ne fait rien
            End Try

            'Vérifier si le réplica est absent
            If gpReplicaParent Is Nothing Then
                'Vérifier si la géodatabase est présente
                If System.IO.Directory.Exists(sNomGdbEnfant) Then
                    'Définir la Géodatabase enfant
                    gpGdbEnfant = DefinirGeodatabase(sNomGdbEnfant)

                    'Si la géodatabase est absente
                Else
                    'Définir l'extension de la géodatabase
                    sExtGdbEnfant = IO.Path.GetExtension(sNomGdbEnfant)

                    'Vérifier si l'extension est .mdb ou .gdb
                    If sExtGdbEnfant = ".mdb" Or sExtGdbEnfant = ".gdb" Then
                        'Créer la géodatabase .mdb ou .gdb
                        gpGdbEnfant = CreerGeodatabaseLocale(sNomGdbEnfant)
                    End If
                End If

                'Interface pour extraire les classes à traiter
                pFeatureWorkspace = CType(gpGdbParent, IFeatureWorkspace)

                'Interface contenant la liste des classes à extraire
                pEnumNameEdit = New NamesEnumerator

                'Traiter toutes les classes à extraire dans le IGeoDataServer parent
                For Each sNomClasse In Split(sListeNomClasse, ",")
                    'Interface pour définir la classe à extraire de la géodatabase source
                    pDataset = CType(pFeatureWorkspace.OpenTable(sNomClasse), IDataset)

                    'Ajouter la classe à extraire dans la géodatabase source
                    pEnumNameEdit.Add(pDataset.FullName)
                Next

                'Interface pour extraire le WorkspaceName de la Géodatabase enfant
                pDataset = CType(gpGdbEnfant, IDataset)

                'Interface contenant la description du CheckOut
                pRepDescription = New ReplicaDescription

                'Initialiser la description du CheckOut
                pRepDescription.Init(CType(pEnumNameEdit, IEnumName), CType(pDataset.FullName, IWorkspaceName), False, pEsriDataExtractionType)

                'Définir le type de model de checkOut
                pRepDescription.ReplicaModelType = pTypeModel

                'Interface pour modifier la méthode d'extraction du checkOut
                pRepFilterDescEdit = CType(pRepDescription, IReplicaFilterDescriptionEdit)
                'Définir la géométrie de la relation spatiale
                pRepFilterDescEdit.Geometry = pGeometry
                'Définir la relation spatiale
                pRepFilterDescEdit.SpatialRelation = pSpatialRelation

                'vérifier si des identifiants sont spécifiés
                If sListeIdentifiants.Length > 0 Then
                    'Définir la requête attributive à partir de la liste des identifiants
                    sRequeteAttributive = sNomAttributId & " IN (" & sListeIdentifiants & ")"
                End If

                'Traiter tous les dataset à extraire
                For i = 0 To pRepDescription.TableNameCount - 1
                    'Appliquer les filtres d'extraction pour chaque classe à extaire
                    With pRepFilterDescEdit
                        .RowsType(i) = esriRowsType.esriRowsTypeFilter
                        .TableUsesQueryGeometry(i) = Not (pGeometry Is Nothing)
                        .TableUsesDefQuery(i) = Not (sRequeteAttributive = "")
                        .TableDefQuery(i) = sRequeteAttributive
                        .TableUsesSelection(i) = False
                        .TableSelection(i) = Nothing
                    End With
                Next

                'Vérifier si le type d'extraction est CheckOut
                If pEsriDataExtractionType = esriDataExtractionType.esriDataCheckOut Then
                    'Afficher l'information de la création de la GéodatabaseEnfant
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Créer la Géodatabase Enfant - Checkout: " & sNomReplica & " ..."
                    'Interface pour exécuter le CheckOut
                    pCheckOut = New CheckOut
                    'Exécuter le CheckOut sans les objets reliés
                    pCheckOut.CheckOutData(pRepDescription, False, sNomReplica)

                    'Si le type d'extraction est DataExtraction
                ElseIf pEsriDataExtractionType = esriDataExtractionType.esriDataExtraction Then
                    'Afficher l'information de la création de la GéodatabaseEnfant
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Créer la Géodatabase Enfant - Extraction: " & sNomReplica & " ..."
                    'Interface pour exécuter le CheckOut
                    pDataExtraction = New DataExtraction
                    'Exécuter le CheckOut sans les objets reliés
                    pDataExtraction.Extract(pRepDescription, False)
                End If

                'Afficher l'information de la création de la Géodatabase d'archive
                If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Créer la Géodatabase d'archive ..."
                'Créer la Géodatabase d'archive externe à partir de la Géodatabase enfant
                Call CreerGdbArchiveExterne()

                'Initialiser le réplica de la Géodatabase enfant
                Call DefinirReplicaEnfant()

                'Définir l'interface des changements de la Géodatabase enfant
                Call DefinirDataChanges()

                'Initialiser le réplica de la Géodatabase parent
                Call DefinirReplicaParent()

                'Si le réplica est déja présent
            Else
                'Retourner l'erreur
                Throw New Exception("ERREUR : Le réplica est déjà présent dans la Géodatabase parent : " & sNomReplica)
            End If

            'Définir le temps d'exécution
            sTempsTraitement = System.DateTime.Now.Subtract(dDateDebut).Add(New TimeSpan(5000000)).ToString.Substring(0, 8)
            'Afficher la fin et le temps du traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement de Réplica (Temps d'exécution: " & sTempsTraitement & ") !"

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            'If pDataset IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(pDataset)
            pWorkspaceReplicas = Nothing
            pFeatureWorkspace = Nothing
            pEnumNameEdit = Nothing
            pDataset = Nothing
            pRepDescription = Nothing
            pRepFilterDescEdit = Nothing
            pCheckOut = Nothing
            pDataExtraction = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer une description de réplica d'une Géodatabase enfant avec une Géodatabase d'archive externe.
    '''</summary>
    '''
    '''<param name="sNomReplica">Nom du réplica.</param>
    '''<param name="sNomGdbParent">Nom de la Géodatabase Parent .sde.</param>
    '''<param name="sNomGdbArchiveCopier">Nom de la Géodatabase d'Archive .mdb ou .gdb. à copier</param>
    '''<param name="sListeNomClasse">Liste des noms des classe à extraire spéparer par des virgule en incluant le nom du propriétaire.</param>
    '''<param name="sRequeteAttributive">Requête attributive à appliquer sur toutes les classes à extraire.</param>
    '''<param name="pTypeModel">Indique le type de model Simple ou complet.</param>
    '''<param name="pEsriDataExtractionType">Indique le type d'extraction à effectuer (esriDataCheckOut ou esriDataExtraction).</param>
    '''<param name="pGeometry">Indique la géométrie utiliser pour effectuer la requête spatiale.</param>
    '''<param name="pSpatialRelation">Indique le type de requête spatiale à effecter.</param>
    ''' 
    ''' <remarks>
    ''' La description du réplica est ajouter dans la Géodatabase enfant mais pas dans la Geodatabase parent.
    ''' La Géodatabase d'archive sera créée à partir du nom de la Géodatabase à copier.
    ''' </remarks>
    ''' 
    Public Sub CreerDescriptionReplicaEnfant(ByVal sNomReplica As String, ByVal sNomGdbParent As String, ByVal sNomGdbArchiveCopier As String,
                        ByVal sListeNomClasse As String, ByVal sRequeteAttributive As String,
                        Optional ByVal pEsriDataExtractionType As esriDataExtractionType = esriDataExtractionType.esriDataCheckOut,
                        Optional ByVal pTypeModel As esriReplicaModelType = esriReplicaModelType.esriModelTypeSimple,
                        Optional ByVal pGeometry As IGeometry = Nothing,
                        Optional ByVal pSpatialRelation As esriSpatialRelEnum = esriSpatialRelEnum.esriSpatialRelIntersects)
        'Déclarer les variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface pour extraire les classes à traiter.
        Dim pEnumNameEdit As IEnumNameEdit = Nothing            'Interface contenant la liste des classes à extraire.
        Dim pDataset As IDataset = Nothing                      'Interface pour définir la classe à extraire de la géodatabase.
        Dim pRepDescription As IReplicaDescription4 = Nothing   'Interface contenant la description du CheckOut.
        Dim pRepFilterDescEdit As IReplicaFilterDescriptionEdit = Nothing   'Interface pour modifier la méthode d'extraction du checkOut.
        Dim sExtGdbEnfant As String = Nothing                   'Extension du nom de la Géodatabase enfant.
        Dim sNomGdbArchive As String = Nothing                  'Nom de la Géodatabase d'archive.

        Try
            'Définir la Géodatabase parent
            gpGdbParent = DefinirGeodatabase(sNomGdbParent)

            'Définir le nom de la Géodatabase d'archive
            sNomGdbArchive = gpGdbEnfant.PathName.Replace(".", "_archive.")

            'Vérifier si la géodatabase d'archive est absente
            If Not System.IO.File.Exists(sNomGdbArchive) And Not System.IO.Directory.Exists(sNomGdbArchive) Then
                'Vérifier si la géodatabase d'archive à copier est présente
                If System.IO.File.Exists(sNomGdbArchiveCopier) Or System.IO.Directory.Exists(sNomGdbArchiveCopier) Then
                    'Copier la Géodatabase d'archive à copier avec le nom de la Géodatabase d'archive
                    System.IO.File.Copy(sNomGdbArchiveCopier, sNomGdbArchive, True)
                    'Définir le nom de la Géodatabase d'archive à partir du nom de la Géodatabase enfant
                    gpGdbArchive = DefinirGeodatabase(sNomGdbArchive)

                    'Si la géodatabase est absente
                Else
                    'Retourner une erreur
                    Throw New Exception("ERREUR : Le nom de la Géodatabase d'Archive à copier est absente : " & sNomGdbArchiveCopier)
                End If
            End If

            'Interface pour extraire les classes à traiter
            pFeatureWorkspace = CType(gpGdbEnfant, IFeatureWorkspace)

            'Interface contenant la liste des classes à extraire
            pEnumNameEdit = New NamesEnumerator

            'Traiter toutes les classes à extraire dans le IGeoDataServer parent
            For Each sNomClasse In Split(sListeNomClasse, ",")
                'Interface pour définir la classe à extraire de la géodatabase source
                pDataset = CType(pFeatureWorkspace.OpenTable(sNomClasse), IDataset)

                'Ajouter la classe à extraire dans la géodatabase source
                pEnumNameEdit.Add(pDataset.FullName)
            Next

            'Interface pour extraire le WorkspaceName de la Géodatabase enfant
            pDataset = CType(gpGdbEnfant, IDataset)

            'Interface contenant la description du CheckOut
            pRepDescription = New ReplicaDescription

            'Initialiser la description du CheckOut
            pRepDescription.Init(CType(pEnumNameEdit, IEnumName), CType(pDataset.FullName, IWorkspaceName), False, pEsriDataExtractionType)

            'Définir le type de model de checkOut
            pRepDescription.ReplicaModelType = pTypeModel

            'Interface pour modifier la méthode d'extraction du checkOut
            pRepFilterDescEdit = CType(pRepDescription, IReplicaFilterDescriptionEdit)
            'Définir la géométrie de la relation spatiale
            pRepFilterDescEdit.Geometry = pGeometry
            'Définir la relation spatiale
            pRepFilterDescEdit.SpatialRelation = pSpatialRelation

            'Traiter tous les dataset à extraire
            For i = 0 To pRepDescription.TableNameCount - 1
                'Appliquer les filtres d'extraction pour chaque classe à extaire
                With pRepFilterDescEdit
                    .RowsType(i) = esriRowsType.esriRowsTypeFilter
                    .TableUsesQueryGeometry(i) = Not (pGeometry Is Nothing)
                    .TableUsesDefQuery(i) = Not (sRequeteAttributive = "")
                    .TableDefQuery(i) = sRequeteAttributive
                    .TableUsesSelection(i) = False
                    .TableSelection(i) = Nothing
                End With
            Next

            'Ajouter la description du réplica dans la Géodatabase enfant
            Call AjouterDescriptionReplicaEnfant(sNomReplica, pRepDescription, gpGdbEnfant)

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            'If pDataset IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(pDataset)
            pFeatureWorkspace = Nothing
            pEnumNameEdit = Nothing
            pDataset = Nothing
            pRepDescription = Nothing
            pRepFilterDescEdit = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter toutes les classes spatiales et non spatiales d'une Géodatabase enfant dans la Map spécifiée.
    '''</summary>
    ''' 
    '''<param name="pMap"> Map dans laquelle les classes seront ajoutés.</param>
    '''
    Public Sub AjouterClassesGdbEnfantMap(ByRef pMap As IMap)
        'Déclarer les variables de travail
        Dim pEnumDataset As IEnumDataset = Nothing          'Interface pour extraire toutes les classe de la Géodtabase enfant.
        Dim pDataset As IDataset = Nothing                  'Interface contenant une classe de la Géodtabase enfant.
        Dim pTable As ITable = Nothing                      'Interface contenant une table non spatiale.
        Dim pFeatureClass As IFeatureClass = Nothing        'Interface contenant une classe spatiale.
        Dim pFeatureLayer As IFeatureLayer = Nothing        'Interface contenant une classe spatiale à ajouter dans la Map.
        Dim pGroupLayer As IGroupLayer = Nothing            'Interface contenant les FeatureLayer du réplica
        Dim pStandaloneTable As IStandaloneTable = Nothing  'Interface contenant une table à ajouter dans la Map.
        Dim pTableCollection As IStandaloneTableCollection = Nothing    'Interface pour ajouter une table non spatiale.

        Try
            'Vérifier si la Géodatabase enfant est valide
            If gpGdbEnfant IsNot Nothing Then
                'Créer un nouveau GroupLayer
                pGroupLayer = New GroupLayer
                pGroupLayer.Name = gpReplicaEnfant.Name

                'Extraire toutes les classes spatiales et non spatiales de la Géodatabase enfant
                pEnumDataset = gpGdbEnfant.Datasets(esriDatasetType.esriDTAny)

                'Initialiser l'extraction
                pEnumDataset.Reset()

                'Extraire le premier dataset
                pDataset = pEnumDataset.Next

                'Traiter toutes les classes
                Do Until pDataset Is Nothing
                    'Vérifer si c'est une classe spatiale
                    If pDataset.Type = esriDatasetType.esriDTFeatureClass Then
                        'Interface contenant la classe pour ajouter dans la Map
                        pFeatureLayer = New FeatureLayer
                        'Définir la classe spatiale
                        pFeatureClass = CType(pDataset.FullName.Open, IFeatureClass)
                        'Définir la classe du FeatureLayer
                        pFeatureLayer.FeatureClass = pFeatureClass
                        'Définir le nom du FeatureLayer
                        pFeatureLayer.Name = pFeatureClass.AliasName
                        'Ajouter le FeatureLayer dans le GroupLayer
                        pGroupLayer.Add(pFeatureLayer)

                        'Si c'est une table non spatiale
                    ElseIf pDataset.Type = esriDatasetType.esriDTTable Then
                        'Interface contenant la table pour ajouter dans la Map
                        pStandaloneTable = New StandaloneTable
                        'Définir la table non spatiale
                        pTable = CType(pDataset.FullName.Open, ITable)
                        'Définir la table duStandalone
                        pStandaloneTable.Table = CType(pDataset.FullName.Open, ITable)
                        'Interface pour ajouter la classe dans la Map
                        pTableCollection = CType(pMap, IStandaloneTableCollection)
                        'Ajouter la table dans la Map
                        pTableCollection.AddStandaloneTable(pStandaloneTable)
                    End If

                    'Extraire le premier dataset
                    pDataset = pEnumDataset.Next
                Loop

                'Ajouter le GroupLayer dans la Map
                pMap.AddLayer(pGroupLayer)

            Else
                'Retourner une erreur
                Throw New Exception("ERREUR : La Géodatabase enfant est invalide !")
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEnumDataset = Nothing
            pDataset = Nothing
            pFeatureClass = Nothing
            pTable = Nothing
            pGroupLayer = Nothing
            pFeatureLayer = Nothing
            pStandaloneTable = Nothing
            pTableCollection = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter une description de réplica dans une Géodatabase enfant.
    '''</summary>
    ''' 
    '''<param name="sNomReplica"> Nom du réplica à ajouter.</param>
    '''<param name="pReplicaDescription"> Interface contenant la description des Datasets ajoutés dans la Géodatabase.</param>
    '''<param name="pGeodatabase"> Interface contenant la Géodatabase enfant dans laquelle le réplica sera ajouté.</param>
    ''' 
    Private Sub AjouterDescriptionReplicaEnfant(ByVal sNomReplica As String, ByRef pReplicaDescription As IReplicaDescription4, ByRef pGeodatabase As IWorkspace)
        'Déclarer les variable de travail
        Dim pWorkspaceReplicas As IWorkspaceReplicas = Nothing              'Interface utilisé pour extraire les réplicas.
        Dim pReplica As IReplica3 = Nothing                                 'Interface contenant l'information d'un réplica.
        Dim pReplicaEdit As IReplicaEdit2 = Nothing                         'Interface qui permet de modifier l'information d'un réplica.
        Dim pWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin = Nothing    'Interface qui permet d'ajouter un réplica dans une Géodatabase.

        Try
            'Vérifier si la géodatabase est une Géodatabase enfant
            If pGeodatabase.Type = esriWorkspaceType.esriLocalDatabaseWorkspace Then
                'Créer un nouveau réplica
                pReplica = New Replica

                'Interface pour modifier l'information du réplica
                pReplicaEdit = CType(pReplica, IReplicaEdit2)

                'Modifier l'information du réplica
                pReplicaEdit.Name = sNomReplica
                pReplicaEdit.Description = pReplicaDescription
                pReplicaEdit.ParentID = -1
                pReplicaEdit.ReplicaID = -1
                pReplicaEdit.ReplicaGuid = "-1"
                pReplicaEdit.ReplicaRole = esriReplicaType.esriCheckOutTypeChild
                pReplicaEdit.AccessType = esriReplicaAccessType.esriReplicaAccessNone

                'Interface pour l'information du réplica
                pReplica = CType(pReplicaEdit, IReplica3)

                'Interface pour extraire les réplicas de la Géodatabase enfant
                pWorkspaceReplicas = CType(pGeodatabase, IWorkspaceReplicas)
                'Rafraichir les réplicas
                pWorkspaceReplicas.RefreshReplicas()

                'Interface pour ajouter un réplica dans une géodatabase un réplica
                'pWorkspaceReplicasAdmin = CType(pWorkspaceReplicas, IWorkspaceReplicasAdmin2)
                'Enregistrer le réplica dans la Géodatabase
                'pWorkspaceReplicasAdmin.RegisterReplica(pReplica)

                'Définir le réplica de la Géodatabase enfant
                gpReplicaEnfant = pReplica

                'Si la géodatabase n'est pas une Géodatabase enfant .mdb ou .Gdb
            Else
                'Retourner une erreur
                Throw New Exception("ERREUR : La géodatabase n'est pas de type .mdb ou .Gdb")
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pWorkspaceReplicas = Nothing
            pReplica = Nothing
            pReplicaEdit = Nothing
            pWorkspaceReplicasAdmin = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'annuler le réplica dans une Géodatabase Parent et Enfant.
    '''</summary>
    ''' 
    Public Sub AnnulerReplica()
        'Déclarer les variable de travail
        Dim pWorkspaceReplicas As IWorkspaceReplicas = Nothing              'Interface utilisé pour extraire les réplicas.
        Dim pWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin = Nothing    'Interface qui permet d'ajouter un réplica dans une Géodatabase.

        Try
            'Vérifier si la géodatabase Parent est valide
            If gpGdbParent IsNot Nothing Then
                'Afficher l'information pour annuler le réplica de la Géodatabase Parent
                If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Annuler le réplica de la Géodatabase Parent !"

                'Interface pour extraire les réplicas de la Géodatabase Parent
                pWorkspaceReplicas = CType(gpGdbParent, IWorkspaceReplicas)
                'Rafraichir les réplicas
                pWorkspaceReplicas.RefreshReplicas()

                'Vérifier si le réplica de la Géodatabase Parent est valide
                If gpReplicaParent IsNot Nothing Then
                    'Interface pour détruire un réplica dans une géodatabase
                    pWorkspaceReplicasAdmin = CType(pWorkspaceReplicas, IWorkspaceReplicasAdmin2)
                    'Détruire le réplica dans la Géodatabase Parent
                    pWorkspaceReplicasAdmin.UnregisterReplica(gpReplicaParent, True)
                    'Désassigner la géodatabase Parent
                    gpGdbParent = Nothing

                    'Si le réplica de la géodatabase Parent est invalide
                Else
                    'Retourner une erreur
                    Throw New AnnulerExecutionException("ERREUR : Le réplica de la géodatabase Parent est invalide")
                End If

                'Si la géodatabase Parent est invalide
            Else
                'Retourner une erreur
                Throw New AnnulerExecutionException("ERREUR : La géodatabase Parent est invalide")
            End If

            'Vérifier si la géodatabase Enfant est valide
            If gpGdbEnfant IsNot Nothing Then
                'Afficher l'information pour annuler le réplica de la Géodatabase Parent
                If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Annuler le réplica de la Géodatabase Parent !"

                'Interface pour extraire les réplicas de la Géodatabase Enfant
                pWorkspaceReplicas = CType(gpGdbEnfant, IWorkspaceReplicas)
                'Rafraichir les réplicas
                pWorkspaceReplicas.RefreshReplicas()

                'Vérifier si le réplica de la Géodatabase Enfant est valide
                If gpReplicaEnfant IsNot Nothing Then
                    'Interface pour ajouter un réplica dans une géodatabase un réplica
                    pWorkspaceReplicasAdmin = CType(pWorkspaceReplicas, IWorkspaceReplicasAdmin2)
                    'Détruire le réplica dans la Géodatabase Enfant
                    pWorkspaceReplicasAdmin.UnregisterReplica(gpReplicaEnfant, True)

                    'Si le réplica de la géodatabase Enfant est invalide
                Else
                    'Retourner une erreur
                    Throw New AnnulerExecutionException("ERREUR : Le réplica de la géodatabase Enfant est invalide")
                End If

                'Si la géodatabase Enfant est invalide
            Else
                'Retourner une erreur
                Throw New AnnulerExecutionException("ERREUR : La géodatabase Parent est invalide")
            End If

            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement d'annulation de réplica !"

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pWorkspaceReplicas = Nothing
            pWorkspaceReplicasAdmin = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'initialiser la classe à partir de la géodatabase enfant.
    '''</summary>
    ''' 
    '''<param name="pGdbEnfant"> Interface contenant la Géodatabase enfant.</param>
    ''' 
    Public Sub Init(Optional ByVal pGdbEnfant As IWorkspace = Nothing)
        Try
            'Initialiser les compteurs
            giNbConflits = -1
            giNbDifferences = -1
            gpTrackCancel = New CancelTracker

            'Définir la Géodatabase enfant
            If pGdbEnfant IsNot Nothing Then gpGdbEnfant = pGdbEnfant

            'Initialiser le réplica de la Géodatabase enfant
            Call DefinirReplicaEnfant()

            'Définir l'interface des changements de la Géodatabase enfant
            Call DefinirDataChanges()

            'Définir le réplica de la Géodatabase parent
            Call DefinirReplicaParent()

            'Définir la géodatabase d'archive à partir du nom de la Géodatabase enfant
            Call DefinirGdbArchive()

        Catch ex As Exception
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'initialiser la classe à partir des noms de la géodatabase enfant.
    '''</summary>
    ''' 
    '''<param name="sGdbEnfant"> Nom de la Géodatabase enfant.</param>
    ''' 
    Public Sub Init(ByVal sGdbEnfant As String)
        Try
            'Initialiser les compteurs
            giNbConflits = -1
            giNbDifferences = -1
            gpTrackCancel = New CancelTracker

            'Définir la Géodatabase enfant
            gpGdbEnfant = DefinirGeodatabase(sGdbEnfant)

            'Initialiser le réplica de la Géodatabase enfant
            Call DefinirReplicaEnfant()

            'Définir l'interface des changements de la Géodatabase enfant
            Call DefinirDataChanges()

            'Définir le réplica de la Géodatabase parent
            Call DefinirReplicaParent()

            'Définir la géodatabase d'archive à partir du nom de la Géodatabase enfant
            Call DefinirGdbArchive()

        Catch ex As Exception
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de valider le traitement de gestion du réplica.
    '''</summary>
    '''
    '''<param name="sMessage"> Message qui indique pourquoi le traitement est valide ou invalide.</param>
    ''' 
    '''<remarks>
    ''' Par défaut, les différences seront identifiées à partir de l'information du réplica de la Géodatabase enfant dans laquelle l'archive interne est présente.
    ''' Si le réplica de la Géodatabase enfant est invalide, les différences seront identifiées à partir de la Géodatabase d'archive externe.
    ''' La Géodatabase d'archive externe correspond à la copie initiale de la Géodatabase enfant.
    ''' </remarks>
    ''' 
    Public Function EstValide(Optional ByRef sMessage As String = "Le traitement de gestion du réplica est valide.") As Boolean
        'Par défaut, la classe est valide
        EstValide = True

        Try
            'Vérifier si la géodabase enfant est invalide
            If gpGdbEnfant Is Nothing Then
                'Retourner un message
                sMessage = "ERREUR : La géodatabase enfant est invalide"
                'Le traitement de gestion du réplica est invalide
                Return False
            End If

            'Vérifier si la géodabase enfant est de type .mdb ou .gdb
            If Not gpGdbEnfant.Type = esriWorkspaceType.esriLocalDatabaseWorkspace Then
                'Retourner un message
                sMessage = "ERREUR : La géodatabase enfant n'est pas de type .mdb ou .gdb."
                'Le traitement de gestion du réplica est invalide
                Return False
            End If

            'Vérifier si le réplica de la géodabase enfant est invalide
            If gpReplicaEnfant Is Nothing Then
                'Vérifier si la Géodatabase parent est invalide
                If gpGdbParent Is Nothing Then
                    'Retourner un message
                    sMessage = "ERREUR : La géodatabase parent est invalide"
                    'Le traitement de gestion du réplica est invalide
                    Return False
                End If

                'Vérifier si la géodabase parent est de type .sde
                If Not gpGdbParent.Type = esriWorkspaceType.esriRemoteDatabaseWorkspace Then
                    'Retourner un message
                    sMessage = "ERREUR : La géodatabase parent n'est pas de type .sde"
                    'Le traitement de gestion du réplica est invalide
                    Return False
                End If

                'Vérifier si la Géodatabase d'archive est invalide
                If gpGdbArchive Is Nothing Then
                    'Retourner un message
                    sMessage = "ERREUR : La géodatabase d'archive est invalide"
                    'Le traitement de gestion du réplica est invalide
                    Return False
                End If

                'Vérifier si la géodabase d'archive est de type .mdb ou .gdb
                If Not gpGdbArchive.Type = esriWorkspaceType.esriLocalDatabaseWorkspace Then
                    'Retourner un message
                    sMessage = "ERREUR : La géodatabase d'archive n'est pas de type .mdb ou .gdb."
                    'Le traitement de gestion du réplica est invalide
                    Return False
                End If

                'Si le réplica enfant est présent
            Else
                'Vérifier si le réplica enfant est de type checkOut
                If gpReplicaEnfant.AccessType <> esriReplicaAccessType.esriReplicaAccessNone Then
                    'Retourner un message
                    sMessage = "ERREUR : Le réplica enfant n'est pas de type CheckOut."
                    'Le traitement de gestion du réplica est invalide
                    Return False
                End If
            End If

        Catch ex As Exception
            Throw
        End Try
    End Function

    '''<summary>
    '''Fonction qui permet de définir une Géodatabase de type .sde, .mdb ou .gdb à partir d'un nom de Géodatabase.
    '''</summary>
    '''
    '''<param name="sNomGeodatabase">Nom complet la Géodatabase.</param>
    ''' 
    '''<returns>"IWorkspace" correspondants à une Géodatabase , Nothing sinon.</returns>
    '''
    Private Function DefinirGeodatabase(ByVal sNomGeodatabase As String) As IWorkspace
        'Déclaration des variables de travail
        Dim pFactoryType As Type = Nothing                      'Interface utilisé pour définir le type de Géodatabase.
        Dim pWorkspaceFactory As IWorkspaceFactory2 = Nothing   'Interface utilise pour créer une Géodatabase.
        Dim sNomGeodatabaseSDE As String = Nothing              'Nom de la Géodatabase SDE.
        Dim sRepArcCatalog As String = ""                       'Nom du répertoire contenant les connexions des Géodatabase .sde.

        'Par défaut, aucune géodatabase n'est créée
        DefinirGeodatabase = Nothing

        Try
            'Vérifier si le nom de la géodatabase est valide
            If sNomGeodatabase IsNot Nothing Then
                'Vérifier si le nom de la géodatabase est spécifié
                If sNomGeodatabase.Length > 0 Then
                    'Extraire le nom du répertoire contenant les connexions des Géodatabase .sde.
                    sRepArcCatalog = IO.Directory.GetDirectories(Environment.GetEnvironmentVariable("APPDATA"), "ArcCatalog", IO.SearchOption.AllDirectories)(0)

                    'Redéfinir le nom complet de la Géodatabase .sde
                    sNomGeodatabaseSDE = sNomGeodatabase.ToLower.Replace("database connections", sRepArcCatalog)

                    'Vérifier si le nom est une geodatabase SDE PRO prédéfinie
                    If sNomGeodatabaseSDE = "bdrs_pro_bdg_dba" Then
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory

                        'Ouvrir la géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory
                        DefinirGeodatabase = pWorkspaceFactory.OpenFromString("INSTANCE=sde:oracle11g:bdrs_pro;USER=BDG_DBA;PASSWORD=123bdg_dba;VERSION=sde.DEFAULT", 0)

                        'Vérifier si le nom est une geodatabase SDE TST prédéfinie
                    ElseIf sNomGeodatabaseSDE = "bdrs_tst_bdg_dba" Then
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory

                        'Ouvrir la géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory
                        DefinirGeodatabase = pWorkspaceFactory.OpenFromString("INSTANCE=sde:oracle11g:bdrs_tst;USER=BDG_DBA;PASSWORD=tst;VERSION=sde.DEFAULT", 0)

                        'Vérifier si le nom est une geodatabase SDE PRO prédéfinie
                    ElseIf sNomGeodatabaseSDE = "geo_pro_geobase_dba" Then
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory

                        'Ouvrir la géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory
                        DefinirGeodatabase = pWorkspaceFactory.OpenFromString("INSTANCE=sde:oracle11g:geo_pro;USER=GEOBASE_DBA;PASSWORD=123geobase_dba;VERSION=sde.DEFAULT", 0)

                        'Vérifier si le nom est une geodatabase SDE TST prédéfinie
                    ElseIf sNomGeodatabaseSDE = "geo_tst_geobase_dba" Then
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory

                        'Ouvrir la géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory
                        DefinirGeodatabase = pWorkspaceFactory.OpenFromString("INSTANCE=sde:oracle11g:geo_tst;USER=GEOBASE_DBA;PASSWORD=tst;VERSION=sde.DEFAULT", 0)

                        'Vérifier si le nom est une geodatabase SDE
                    ElseIf IO.Path.GetExtension(sNomGeodatabaseSDE) = ".sde" Then
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = New ESRI.ArcGIS.DataSourcesGDB.SdeWorkspaceFactory

                        'Ouvrir la géodatabase
                        DefinirGeodatabase = pWorkspaceFactory.OpenFromFile(sNomGeodatabaseSDE, 0)

                        'Vérifier si le nom est une personnel geodatabase
                    ElseIf IO.Path.GetExtension(sNomGeodatabase) = ".mdb" Then
                        'Définir le type de workspace : MDB
                        pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.AccessWorkspaceFactory")
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = CType(Activator.CreateInstance(pFactoryType), IWorkspaceFactory2)

                        'Ouvrir la géodatabase
                        DefinirGeodatabase = pWorkspaceFactory.OpenFromFile(sNomGeodatabase, 0)

                        'Si le nom est une file geodatabase
                    ElseIf IO.Path.GetExtension(sNomGeodatabase) = ".gdb" Then
                        'Définir le type de workspace : GDB
                        pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.FileGDBWorkspaceFactory")
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = CType(Activator.CreateInstance(pFactoryType), IWorkspaceFactory2)

                        'Ouvrir la géodatabase
                        DefinirGeodatabase = pWorkspaceFactory.OpenFromFile(sNomGeodatabase, 0)

                    Else
                        'Retourner une erreur
                        Throw New Exception("Erreur : L'extension du nom de la Géodatabase n'est pas .sde, .mdb ou .gdb : " & sNomGeodatabase)
                    End If
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pFactoryType = Nothing
            pWorkspaceFactory = Nothing
        End Try
    End Function

    '''<summary>
    '''Fonction qui permet de créer une Géodatabase locale de type .mdb ou .gdb.
    '''</summary>
    '''
    '''<param name="sNomGeodatabase">Nom complet la Géodatabase locale à créer.</param>
    ''' 
    '''<returns>"IWorkspace" correspondants à une Géodatabase locale , Nothing sinon.</returns>
    ''' 
    ''' <remarks>
    ''' Une Géodatabase est créée seulement si le nom contient .mdb ou .gdb, sinon une erreur est retournée.
    '''</remarks>
    '''
    Private Function CreerGeodatabaseLocale(ByVal sNomGeodatabase As String) As IWorkspace
        'Déclaration des variables de travail
        Dim pFactoryType As Type = Nothing                      'Interface utilisé pour définir le type de Géodatabase.
        Dim pWorkspaceFactory As IWorkspaceFactory = Nothing    'Interface utilise pour créer une Géodatabase.

        'Par défaut, aucune géodatabase n'est créée
        CreerGeodatabaseLocale = Nothing

        Try
            'Vérifier si le nom de la géodatabase est valide
            If sNomGeodatabase IsNot Nothing Then
                'Vérifier si le nom de la géodatabase est spécifié
                If sNomGeodatabase.Length > 0 Then
                    'Vérifier si le nom est une personnel geodatabase
                    If IO.Path.GetExtension(sNomGeodatabase) = ".mdb" Then
                        'Définir le type de workspace : MDB
                        pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.AccessWorkspaceFactory")
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = CType(Activator.CreateInstance(pFactoryType), IWorkspaceFactory)

                        'Vérifier si la Géodatabase n'existe pas
                        If Not IO.File.Exists(sNomGeodatabase) Then
                            'Créer la géodatabase
                            pWorkspaceFactory.Create(IO.Path.GetDirectoryName(sNomGeodatabase), IO.Path.GetFileName(sNomGeodatabase), Nothing, 0)
                        End If

                        'Ouvrir la géodatabase
                        CreerGeodatabaseLocale = pWorkspaceFactory.OpenFromFile(sNomGeodatabase, 0)

                        'Si le nom est une file geodatabase
                    ElseIf IO.Path.GetExtension(sNomGeodatabase) = ".gdb" Then
                        'Définir le type de workspace : GDB
                        pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.FileGDBWorkspaceFactory")
                        'Interface pour ouvrir la Géodatabase
                        pWorkspaceFactory = CType(Activator.CreateInstance(pFactoryType), IWorkspaceFactory)

                        'Vérifier si la Géodatabase n'existe pas
                        If Not IO.Directory.Exists(sNomGeodatabase) Then
                            'Créer la Géodatabase
                            pWorkspaceFactory.Create(IO.Path.GetDirectoryName(sNomGeodatabase), IO.Path.GetFileName(sNomGeodatabase), Nothing, 0)
                        End If

                        'Ouvrir la géodatabase
                        CreerGeodatabaseLocale = pWorkspaceFactory.OpenFromFile(sNomGeodatabase, 0)

                    Else
                        'Retourner une erreur
                        Throw New Exception("Erreur : L'extension du nom de la Géodatabase n'est pas .mdb ou .gdb : " & sNomGeodatabase)
                    End If
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pFactoryType = Nothing
            pWorkspaceFactory = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de définir le réplica de la Géodatabase enfant.
    '''</summary>
    ''' 
    Private Sub DefinirReplicaEnfant()
        'Déclarer les variables de travail
        Dim pEnfantWorkspaceReplicas As IWorkspaceReplicas = Nothing        'Interface pour extraire les réplicas de la Géodatabase enfant.
        Dim pEnumReplica As IEnumReplica = Nothing                          'Interface utilisé pour extraire les réplicas.

        Try
            'Interface contenant le réplica enfant
            gpReplicaEnfant = Nothing

            'Vérifier si la géodatabase enfant est valide
            If gpGdbEnfant IsNot Nothing Then
                'Interface pour extraire les réplicas de la Géodatabase enfant
                pEnfantWorkspaceReplicas = CType(gpGdbEnfant, IWorkspaceReplicas)

                'Interface utilisé pour extraire les réplicas.
                pEnumReplica = pEnfantWorkspaceReplicas.Replicas
                pEnumReplica.Reset()

                'Interface contenant le réplica de la Géodatabase enfant
                gpReplicaEnfant = CType(pEnumReplica.Next, IReplica3)
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEnfantWorkspaceReplicas = Nothing
            pEnumReplica = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de définir l'interface des changements de la Géodatabase enfant.
    '''</summary>
    ''' 
    Private Sub DefinirDataChanges()
        'Déclarer les variables de travail
        Dim pReplicaDataChangesInit As IReplicaDataChangesInit = Nothing    'Interface pour initialiser l'identification des changements.
        Dim pEnfantWorkspaceName As IWorkspaceName = Nothing                'Interface pour extraire le nom de la Géodatabase enfant.
        Dim pDataset As IDataset = Nothing                                  'Interface pour extraire le nom de la Géodatabase.

        Try
            'Interface contenant les changements du réplica est invalide
            gpDataChanges = Nothing

            'Vérifier si un Réplica est présent
            If gpReplicaEnfant IsNot Nothing Then
                'Vérifier si le réplica est de type CheckOut
                If gpReplicaEnfant.AccessType = esriReplicaAccessType.esriReplicaAccessNone Then
                    'Interface pour extraire le nom de la Géodatabase enfant
                    pDataset = CType(gpGdbEnfant, IDataset)

                    'Extraire le nom de la Géodatabase enfant
                    pEnfantWorkspaceName = CType(pDataset.FullName, IWorkspaceName)

                    'Interface qui permet de définir toutes les tables de changement
                    pReplicaDataChangesInit = New CheckOutDataChanges

                    'Initialiser l'interface qui permet de définir toutes les tables de changement
                    pReplicaDataChangesInit.Init(gpReplicaEnfant, pEnfantWorkspaceName)

                    'Interface contenant les changements
                    gpDataChanges = CType(pReplicaDataChangesInit, IDataChanges)
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            'If pDataset IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(pDataset)
            pReplicaDataChangesInit = Nothing
            pEnfantWorkspaceName = Nothing
            pDataset = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de définir la Géodatabase parent à partir de l'interface de changements.
    '''</summary>
    ''' 
    Private Sub DefinirGdbParent()
        'Déclarer les variables de travail
        Dim pName As IName = Nothing                            'Interface utilisé pour ouvrir une Géodatabase.

        Try
            'Interface contenant la géodatabase parent invalide
            gpGdbParent = Nothing

            'Vérifier si l'interface de changement est valide
            If gpDataChanges IsNot Nothing Then
                'Interface pour ouvrir la Géodatabase Parent
                pName = CType(gpDataChanges.ParentWorkspaceName, IName)

                'Définir la Géodatabase Parent
                gpGdbParent = CType(pName.Open(), IWorkspace)
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pName = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de définir le réplica de la Géodatabase parent à partir de l'interface de changements.
    '''</summary>
    ''' 
    Private Sub DefinirReplicaParent()
        'Déclarer les variables de travail
        Dim pWorkspaceReplicas As IWorkspaceReplicas2 = Nothing 'Interface utilisé pour extraire un réplica existant.

        Try
            'Interface contenant le réplica parent invalide
            gpReplicaParent = Nothing

            'Vérifier si la géodabase parent est invalide
            If gpGdbParent Is Nothing Then
                'Définir la Géodatabase Parent à partir de l'interface de changement
                Call DefinirGdbParent()
            End If

            'Vérifier si la géodabase parent est valide
            If gpGdbParent IsNot Nothing Then
                'Interface pour ouvrir la Géodatabase Parent
                pWorkspaceReplicas = CType(gpGdbParent, IWorkspaceReplicas2)

                'Rafraichir les réplicas
                pWorkspaceReplicas.RefreshReplicas()

                Try
                    'Définir le réplica de la Géodatabase Parent
                    gpReplicaParent = CType(pWorkspaceReplicas.ReplicaByName(gpReplicaEnfant.Name), IReplica3)

                Catch ex As Exception
                    'On ne fait rien
                End Try
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pWorkspaceReplicas = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de définir la Géodatabase d'archive à partir du nom de la Géodatabase enfant.
    '''</summary>
    ''' 
    '''<remarks>Le nom de la géodatabase d'archive est le même que celui de l'enfant mais contient le suffixe "_archive" à la fin du nom sans l'extension.</remarks>
    ''' 
    Private Sub DefinirGdbArchive()
        Try
            'Interface contenant la géodatabase parent invalide
            gpGdbArchive = Nothing

            'Vérifier si la Géodatabase enfant est valide
            If gpGdbEnfant IsNot Nothing Then
                'Définir le nom de la Géodatabase d'archive à partir du nom de la Géodatabase enfant
                gpGdbArchive = DefinirGeodatabase(gpGdbEnfant.PathName.Replace(".", "_archive."))
            End If

        Catch ex As Exception
            'On ne fait rien
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer la Géodatabase d'archive à partir de la Géodatabase enfant.
    '''</summary>
    ''' 
    '''<remarks>Le nom de la géodatabase d'archive est le même que celui de l'enfant mais contient le suffixe "_archive" à la fin du nom sans l'extension.</remarks>
    ''' 
    Private Sub CreerGdbArchiveExterne()
        Try
            'Interface contenant la géodatabase parent invalide
            gpGdbArchive = Nothing

            'Vérifier si la Géodatabase enfant est valide
            If gpGdbEnfant IsNot Nothing Then
                'Vérifier si la GdbEnfant est un '.mdb'
                If gpGdbEnfant.PathName.Contains(".mdb") Then
                    'Copier la Géodatabase enfant avec le nom de la Géodatabase d'archive
                    System.IO.File.Copy(gpGdbEnfant.PathName, gpGdbEnfant.PathName.Replace(".", "_archive."), True)

                    'Si la GdbEnfant est un '.gdb'
                Else
                    'Copier la Géodatabase enfant avec le nom de la Géodatabase d'archive
                    My.Computer.FileSystem.CopyDirectory(gpGdbEnfant.PathName, gpGdbEnfant.PathName.Replace(".", "_archive."), True)
                End If

                'Définir le nom de la Géodatabase d'archive à partir du nom de la Géodatabase enfant
                gpGdbArchive = DefinirGeodatabase(gpGdbEnfant.PathName.Replace(".", "_archive."))
            End If

        Catch ex As Exception
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de retourner la description complète d'un réplica dans un noeud de TreeView.
    '''</summary>
    '''
    '''<param name="pReplica">Interface contenant l'information d'un réplica de Géodatabase.</param>
    '''<param name="pNodeGdb">Noeud d'un TreeView dans lequel la description du réplica de la Géodatabase sera inscrite.</param>
    ''' 
    Private Sub DescriptionReplica(ByVal pReplica As IReplica3, ByRef pNodeGdb As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeReplica As TreeNode = Nothing                      'Noeud du réplica de réplica d'un TreeView.
        Dim pNodeDataset As TreeNode = Nothing                      'Noeud de Dataset de réplica d'un TreeView.
        Dim pNodeFilter As TreeNode = Nothing                       'Noeud du filtre de Dataset de réplica d'un TreeView.
        Dim pRepFilterDesc As IReplicaFilterDescription = Nothing   'Interface contenant le filtre utilisé pour extraire un Dataset.
        Dim pEnumDataset As IEnumReplicaDataset = Nothing           'Interface utilisé pour extraire tous les Datasets d'un réplica.
        Dim pReplicaDataset As IReplicaDataset2 = Nothing           'Interface contenant l'information d'un Dataset contenu dans un réplica.
        Dim i As Integer = Nothing                                  'Compteur de Dataset.

        Try
            'Vérifier si le réplica est présent
            If pReplica IsNot Nothing Then
                'Définir l'information du réplica
                pNodeReplica = pNodeGdb.Nodes.Add("Replica=" & pReplica.Name)
                pNodeReplica.Nodes.Add("Name=" & pReplica.Name)
                pNodeReplica.Nodes.Add("Version=" & pReplica.Version)
                pNodeReplica.Nodes.Add("Owner=" & pReplica.Owner)
                pNodeReplica.Nodes.Add("ParentID=" & pReplica.ParentID)
                pNodeReplica.Nodes.Add("ReplicaID=" & pReplica.ReplicaID)
                pNodeReplica.Nodes.Add("ReplicaGuid=" & pReplica.ReplicaGuid)
                pNodeReplica.Nodes.Add("ReplicaDate=" & pReplica.ReplicaDate.ToString)
                pNodeReplica.Nodes.Add("ReplicaRole=" & pReplica.ReplicaRole.ToString)
                pNodeReplica.Nodes.Add("ReplicaState=" & pReplica.ReplicaState.ToString)
                pNodeReplica.Nodes.Add("AccessType=" & pReplica.AccessType.ToString)
                pNodeReplica.Nodes.Add("HasConflicts=" & pReplica.HasConflicts)
                pNodeReplica.Nodes.Add("UseArchiving=" & pReplica.UseArchiving)
                pNodeReplica.Nodes.Add("ReconcilePolicyType=" & pReplica.ReconcilePolicyType.ToString)
                pNodeReplica.Nodes.Add("ReplicaReceivingVersion=" & pReplica.ReplicaReceivingVersion)

                'Interface pour modifier la méthode d'extraction du checkOut
                pRepFilterDesc = CType(pReplica.Description, IReplicaFilterDescription)

                'vérifier la présence des Datasets dans le réplica
                If pReplica.ReplicaDatasets IsNot Nothing Then
                    'Interface pour extraire les datasets du préplica
                    pEnumDataset = pReplica.ReplicaDatasets
                    pEnumDataset.Reset()

                    'Extraire le premier Dataset
                    pReplicaDataset = CType(pEnumDataset.Next, IReplicaDataset2)
                    i = 0

                    'Traiter tous les Datasets
                    Do Until pReplicaDataset Is Nothing
                        'Définir l'information du Dataset
                        pNodeDataset = pNodeGdb.Nodes.Add((i + 1).ToString & "-ReplicaDataset=" & pReplicaDataset.Name)
                        pNodeDataset.Nodes.Add("Name=" & pReplicaDataset.Name)
                        pNodeDataset.Nodes.Add("ParentDatabase=" & pReplicaDataset.ParentDatabase)
                        pNodeDataset.Nodes.Add("ParentOwner=" & pReplicaDataset.ParentOwner)
                        pNodeDataset.Nodes.Add("TargetName=" & pReplicaDataset.TargetName)
                        pNodeDataset.Nodes.Add("Type=" & pReplicaDataset.Type.ToString)
                        pNodeDataset.Nodes.Add("Id=" & pReplicaDataset.DatasetID.ToString)
                        pNodeDataset.Nodes.Add("ReplicaId=" & pReplicaDataset.ReplicaID.ToString)

                        'Définir l'information des filtres utilisés pour créer le Dataset
                        pNodeFilter = pNodeDataset.Nodes.Add("ReplicaFilterDescription=" & pRepFilterDesc.RowsType(i).ToString)
                        pNodeFilter.Nodes.Add("RowsType=" & pRepFilterDesc.RowsType(i).ToString)
                        pNodeFilter.Nodes.Add("TableUsesQueryGeometry=" & pRepFilterDesc.TableUsesQueryGeometry(i).ToString)
                        pNodeFilter.Nodes.Add("SpatialRelation=" & pRepFilterDesc.SpatialRelation.ToString)
                        pNodeFilter.Nodes.Add("TableUsesDefQuery=" & pRepFilterDesc.TableUsesDefQuery(i).ToString)
                        pNodeFilter.Nodes.Add("TableDefQuery=" & pRepFilterDesc.TableDefQuery(i))
                        pNodeFilter.Nodes.Add("TableUsesSelection=" & pRepFilterDesc.TableUsesSelection(i).ToString)
                        If pRepFilterDesc.TableUsesSelection(i) Then
                            pNodeFilter.Nodes.Add("TableSelectionCount=" & pRepFilterDesc.TableSelection(i).Count.ToString)
                        End If

                        'Extraire le prochain Dataset
                        pReplicaDataset = CType(pEnumDataset.Next, IReplicaDataset2)
                        i = i + 1
                    Loop
                Else
                    'Définir l'information du réplica
                    pNodeReplica = pNodeGdb.Nodes.Add("Aucun Dataset de réplica n'est présent !")
                End If
            Else
                'Définir l'information du réplica
                pNodeReplica = pNodeGdb.Nodes.Add("Aucune description de réplica n'est présent !")
            End If

            'Ouvrir tous les noeuds de la Géodatabase
            pNodeGdb.Expand()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeReplica = Nothing
            pNodeDataset = Nothing
            pNodeFilter = Nothing
            pRepFilterDesc = Nothing
            pEnumDataset = Nothing
            pReplicaDataset = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de créer un réplica d'extraction de données dans une géodatabase .mdb ou .gdb à partir d'une géodatabase SDE.
    '''</summary>
    '''
    '''<param name="sNomGdbParent">Nom de la Géodatabase parent .sde.</param>
    '''<param name="sNomGdbEnfant">Nom de la Géodatabase enfant .mdb ou .gdb.</param>
    '''<param name="sListeNomClasse">Liste des noms des classe à extraire spéparer par des virgule en incluant le nom du propriétaire.</param>
    '''<param name="sRequeteAttributive">Requête attributive à appliquer sur toutes les classes à extraire.</param>
    '''<param name="pTypeModel">Indique le type de model Simple ou complet.</param>
    '''<param name="pGeometry">Indique la géométrie utiliser pour effectuer la requête spatiale.</param>
    '''<param name="pSpatialRelation">Indique le type de requête spatiale à effecter.</param>
    ''' 
    '''<remarks>Si une des classe est déjà présente, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub CreerReplicaExtraction(ByVal sNomGdbParent As String, ByVal sNomGdbEnfant As String,
                                      ByVal sListeNomClasse As String, ByVal sRequeteAttributive As String,
                                      Optional ByVal pTypeModel As esriReplicaModelType = esriReplicaModelType.esriModelTypeSimple,
                                      Optional ByVal pGeometry As IGeometry = Nothing,
                                      Optional ByVal pSpatialRelation As esriSpatialRelEnum = esriSpatialRelEnum.esriSpatialRelIntersects)
        'Déclarer les variables de travail
        Dim pGdsParent As IGeoDataServer = Nothing                  'Interface contenant l'information de la Géodatabase parent.
        Dim pGdsEnfant As IGeoDataServer = Nothing                  'Interface contenant l'information de la Géodatabase enfant.
        Dim pGPReplicaDataset As IGPReplicaDataset = Nothing        'Interface pour définir la classe à extraire de la géodatabase source.
        Dim pGPReplicaDatasets As IGPReplicaDatasets = Nothing      'Interface pour définir toutes les classes à extraire dans le IGeoDataServer parent.
        Dim pGPReplicaDatasetsExpand As IGPReplicaDatasets = Nothing 'Interface pour définir la liste des classes à extraire dans le IGeoDataServer parent
        Dim pGPReplicaDesc As IGPReplicaDescription = Nothing       'Interface pour décrire le réplica à utiliser.
        Dim pGPReplicaOptions As IGPReplicaOptions2 = Nothing       'Interface pour définir les options du réplica
        Dim pReplicationAgent As IReplicationAgent = Nothing        'Interface pour exécuter le traitement de réplication.
        Dim sNomClasse As String = Nothing                          'Nom de la classe à traiter.
        Dim sExtGdbEnfant As String = Nothing                       'Extension du nom de la Géodatabase enfant.

        Try
            'Définir la Géodatabase serveur parent
            pGdsParent = InitGeoDataServerFromFile(sNomGdbParent)

            'Définir la Géodatabase serveur enfant
            pGdsEnfant = InitGeoDataServerFromFile(sNomGdbEnfant)

            'Vérifier si la géodatabase est présente
            If System.IO.Directory.Exists(sNomGdbEnfant) Then
                'Définir la Géodatabase enfant
                gpGdbEnfant = DefinirGeodatabase(sNomGdbEnfant)

                'Si la géodatabase est absente
            Else
                'Définir l'extension de la géodatabase
                sExtGdbEnfant = IO.Path.GetExtension(sNomGdbEnfant)

                'Vérifier si l'extension est .mdb ou .gdb
                If sExtGdbEnfant = ".mdb" Or sExtGdbEnfant = ".gdb" Then
                    'Créer la géodatabase .mdb ou .gdb
                    gpGdbEnfant = CreerGeodatabaseLocale(sNomGdbEnfant)
                End If
            End If

            'Interface pour définir toutes les classes à extraire dans le IGeoDataServer parent
            pGPReplicaDatasets = New GPReplicaDatasets
            'Traiter toutes les classes à extraire dans le IGeoDataServer parent
            For Each sNomClasse In Split(sListeNomClasse, ",")
                'Interface pour définir la classe à extraire de la géodatabase source
                pGPReplicaDataset = New GPReplicaDataset
                'Inidiquer que le Dataset est une classe
                pGPReplicaDataset.DatasetType = esriDatasetType.esriDTFeatureClass
                'Définir le nom de la classe (Doit contenir le nom du propriétaire ex:'BDG_DBA.')
                pGPReplicaDataset.Name = sNomClasse
                'Définir la requête attributive
                pGPReplicaDataset.DefQuery = sRequeteAttributive
                'Définir si la requête spatiale doit être utilisée
                pGPReplicaDataset.UseGeometry = pGeometry IsNot Nothing
                'Ajouter la classe à extraire dans la géodatabase source
                pGPReplicaDatasets.Add(pGPReplicaDataset)
            Next
            'Définir la liste des classes à extraire dans le IGeoDataServer parent
            pGPReplicaDatasetsExpand = pGdsParent.ExpandReplicaDatasets(pGPReplicaDatasets)

            'Interface pour décrire le réplica à utiliser
            pGPReplicaDesc = New GPReplicaDescription
            'Définir dans le réplica les classes à extraire dans le IGeoDataServer parent
            pGPReplicaDesc.ReplicaDatasets = pGPReplicaDatasetsExpand
            'Définir dans le réplica le type de model à utiliser (simple ou complet)
            pGPReplicaDesc.ModelType = pTypeModel
            'Indiquer si c'est la première génération du réplica
            pGPReplicaDesc.SingleGeneration = True
            'Définir au besoin la géométrie d'extraction
            pGPReplicaDesc.QueryGeometry = pGeometry
            'Définir au besoin le type de relation entre les éléments et la géométrie d'extraction
            pGPReplicaDesc.SpatialRelation = pSpatialRelation

            'Interface pour exécuter le traitement de réplication
            pReplicationAgent = New ReplicationAgent
            'Exécuter le traitement de réplication d'extraction de données
            pReplicationAgent.ExtractData("", pGdsParent, pGdsEnfant, pGPReplicaDesc)

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pGdsParent = Nothing
            pGdsEnfant = Nothing
            pGPReplicaDataset = Nothing
            pGPReplicaDatasets = Nothing
            pGPReplicaDatasetsExpand = Nothing
            pGPReplicaDesc = Nothing
            pReplicationAgent = Nothing
            sNomClasse = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de définir une géodatabase utilisée dans un réplica à partir d'un nom de géodatabase.
    ''' 
    ''' Exemple: sNomGeodatabase = "C:\arcgis\ArcTutor\DatabaseServers\buildings.mdb".
    '''          sNomGeodatabase = "C:\arcgis\ArcTutor\DatabaseServers\hazards.gdb".
    '''</summary>
    '''
    '''<param name="sNomGeodatabase">Nom complet d'une Géodatabase.</param>
    ''' 
    ''' <returns>IGeoDataServer contenant l'information de la géodatabase utilisée pour un réplica.</returns>
    ''' 
    Private Function InitGeoDataServerFromFile(ByVal sNomGeodatabase As String) As IGeoDataServer
        'Déclarer les variables de travail
        Dim pGeoDataServer As IGeoDataServer = Nothing          'Interface contenant l'information de la géodatabase utilisée pour un réplica.
        Dim pGeoDataServerInit As IGeoDataServerInit = Nothing  'Interface pour initialiser l'information de la géodatabase utilisée pour un réplica.

        Try
            'Interface contenant l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServer = New GeoDataServer

            'Interface pour initialiser l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServerInit = CType(pGeoDataServer, IGeoDataServerInit)

            'Initialiser l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServerInit.InitFromFile(sNomGeodatabase)

            Return pGeoDataServer

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pGeoDataServer = Nothing
            pGeoDataServerInit = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire un élément d'archive interne ou externe à partir d'un OBJECTID et d'un nom de classe.
    '''</summary>
    '''
    '''<param name="iOid">ObjectId de l'élément.</param>
    '''<param name="sNomClasse">Nom de la classe de l'élément.</param>
    ''' 
    ''' <returns>IRow contenant l'élément demandé, sinon nothing</returns>
    ''' 
    Public Function ExtraireElementArchive(ByVal iOid As Integer, ByVal sNomClasse As String) As IRow
        'Par défaut, aucun élément n'es extrait
        ExtraireElementArchive = Nothing

        Try
            'Vérifier si l'archive externe est absente
            If gpGdbArchive Is Nothing Then
                'vérifier si l'archive interne est présente
                If gpDataChanges IsNot Nothing Then
                    'Extraire l'élément de l'archive externe
                    ExtraireElementArchive = ExtraireElementArchiveInterne(iOid, sNomClasse)
                End If

                'Si l'archive externe est présente
            Else
                'Extraire l'élément de l'archive externe
                ExtraireElementArchive = ExtraireElementArchiveExterne(iOid, sNomClasse)
            End If

        Catch ex As Exception
            Throw
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire un élément de la Géodatabase d'archive interne à la Géodatabase enfant à partir d'un OBJECTID et d'un nom de classe.
    '''</summary>
    '''
    '''<param name="iOid">ObjectId de l'élément.</param>
    '''<param name="sNomClasse">Nom de la classe de l'élément.</param>
    ''' 
    ''' <returns>IRow contenant l'élément demandé, sinon nothing</returns>
    ''' 
    Public Function ExtraireElementArchiveInterne(ByVal iOid As Integer, ByVal sNomClasse As String) As IRow
        'Déclarer les variables de travail
        Dim pDataChangesExt As IDataChangesExt = Nothing    'Interface qui permet d'extraire les éléments d'archive d'un CheckOut.
        Dim pCursor As ICursor = Nothing                    'Interface contenant les éléments d'archive d'un CheckOut à extraire.
        Dim pFidSet As IFIDSet = Nothing                    'Interface contenant la liste des OID d'éléments d'archive d'un CheckOut à extraire.

        Try
            'Interface pour ajouter les OID des éléments originaux à extraire
            pFidSet = New FIDSet

            'Ajouter le OID à extraire
            pFidSet.Add(iOid)

            'Interface pour contenant les éléments d'archive d'un CheckOut
            pDataChangesExt = CType(gpDataChanges, IDataChangesExt)

            'Interface pour extraire les éléments d'archive d'un CheckOut
            pCursor = pDataChangesExt.ExtractOriginalRows(sNomClasse, pFidSet)

            'Extraire l'élément de l'archive
            ExtraireElementArchiveInterne = pCursor.NextRow()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pDataChangesExt = Nothing
            pCursor = Nothing
            pFidSet = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire un élément de la Géodatabase d'archive externe à partir d'un OBJECTID et d'un nom de classe.
    '''</summary>
    '''
    '''<param name="iOid">ObjectId de l'élément.</param>
    '''<param name="sNomClasse">Nom de la classe de l'élément.</param>
    ''' 
    ''' <returns>IRow contenant l'élément demandé, sinon nothing</returns>
    ''' 
    Public Function ExtraireElementArchiveExterne(ByVal iOid As Integer, ByVal sNomClasse As String) As IRow
        'Déclarer les variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface qui permet d'extraire les classes d'une Géodatabase d'archive externe.
        Dim pTable As ITable = Nothing                          'Interface qui permet d'extraire un élément d'une Géodatabase d'archive externe.

        Try
            'Interface qui permet d'extraire les classes d'une Géodatabase d'archive externe
            pFeatureWorkspace = CType(gpGdbArchive, IFeatureWorkspace)

            'Interface pour extraire l'élément d'archive externe
            pTable = pFeatureWorkspace.OpenTable(sNomClasse)

            'Extraire l'élément de l'archive
            ExtraireElementArchiveExterne = pTable.GetRow(iOid)

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatureWorkspace = Nothing
            pTable = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire un élément de la Géodatabase enfant à partir d'un OBJECTID, d'un nom de classe.
    '''</summary>
    '''
    '''<param name="iOid">ObjectId de l'élément.</param>
    '''<param name="sNomClasse">Nom de la classe de l'élément.</param>
    ''' 
    ''' <returns>IRow contenant l'élément demandé, sinon nothing</returns>
    ''' 
    Public Function ExtraireElementEnfant(ByVal iOid As Integer, ByVal sNomClasse As String) As IRow
        'Déclarer les variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface contenant des classes d'éléments.
        Dim pTable As ITable = Nothing                          'Interface contenant une classe d'éléments.

        'Par défaut, aucun élément n'est retourné
        ExtraireElementEnfant = Nothing

        Try
            'Interface contenant des classes d'éléments.
            pFeatureWorkspace = CType(gpGdbEnfant, IFeatureWorkspace)

            'Extraire la classe d'élément
            pTable = pFeatureWorkspace.OpenTable(sNomClasse)

            'Extraire l'élément de la Géodatabase enfant
            ExtraireElementEnfant = pTable.GetRow(iOid)

        Catch ex As Exception
            'On ne fait rien
        Finally
            'Vider la mémoire
            pFeatureWorkspace = Nothing
            pTable = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire un élément de la Géodatabase parent à partir d'un OBJECTID, d'un nom de classe.
    '''</summary>
    '''
    '''<param name="iOid">ObjectId de l'élément.</param>
    '''<param name="sNomClasse">Nom de la classe de l'élément.</param>
    ''' 
    ''' <returns>IRow contenant l'élément demandé, sinon nothing</returns>
    ''' 
    Public Function ExtraireElementParent(ByVal iOid As Integer, ByVal sNomClasse As String) As IRow
        'Déclarer les variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface contenant des classes d'éléments.
        Dim pTable As ITable = Nothing                          'Interface contenant une classe d'éléments.

        'Par défaut, aucun élément n'est retourné
        ExtraireElementParent = Nothing

        Try
            'Interface contenant des classes d'éléments.
            pFeatureWorkspace = CType(gpGdbParent, IFeatureWorkspace)

            'Extraire la classe d'élément
            pTable = pFeatureWorkspace.OpenTable(sNomClasse)

            'Extraire l'élément de la Géodatabase parent
            ExtraireElementParent = pTable.GetRow(iOid)

        Catch ex As Exception
            'On ne fait rien
        Finally
            'Vider la mémoire
            pFeatureWorkspace = Nothing
            pTable = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de remplir la description du réplica de la Géodatabase enfant et parent dans le TreewView.
    '''</summary>
    '''
    '''<param name="treReplica">TreeView dans lequel la description du réplica de la Géodatabase enfant et parent seront inscrite.</param>
    ''' 
    Public Sub DescriptionReplica(ByRef treReplica As TreeView)
        'Déclarer les variables de travail
        Dim pNodeGdb As TreeNode = Nothing                                  'Noeud d'un TreeView dans lequel la description du réplica de la Géodatabase sera inscrite.

        Try
            'Vider les noeuds du replica
            treReplica.Nodes.Clear()

            'Définir le noeud contenant le nombre de conflits
            treReplica.Nodes.Add("Nombre de conflits= " & giNbConflits.ToString)

            'Définir le noeud contenant le nombre de différences
            treReplica.Nodes.Add("Nombre de différences= " & giNbDifferences.ToString)

            'Vérifier si la Géodatabase enfant est valide
            If gpGdbEnfant IsNot Nothing Then
                'Définir le noeud de la Géodatabase Enfant
                pNodeGdb = treReplica.Nodes.Add("GDB Enfant=" & gpGdbEnfant.PathName)

                'Remplir la description du réplica de la Géodatabase enfant dans le TreeView
                DescriptionReplica(ReplicaEnfant, pNodeGdb)
            End If

            'Vérifier si la Géodatabase parent est valide
            If gpGdbParent IsNot Nothing Then
                'Définir le noeud de la Géodatabase Parent
                pNodeGdb = treReplica.Nodes.Add("GDB Parent=" & gpGdbParent.ConnectionProperties.GetProperty("Instance").ToString.ToUpper)

                'Remplir la description du réplica de la Géodatabase parent dans le TreeView
                DescriptionReplica(ReplicaParent, pNodeGdb)
            End If

            'Afficher l'information du début du tratement de Réplica
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Affichage de la description du réplica !"

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeGdb = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de calculer le nombre de différences à partir d'un noeud de Réplica'un TreewView.
    '''</summary>
    '''
    '''<param name="pNodeReplica">TreeNode contenant les différences d'un Réplica et son archive.</param>
    ''' 
    Private Function CalculerDifferences(ByVal pNodeReplica As TreeNode) As Integer
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing  'Noued d'un TreeView utilisé pour le calcul

        'Par défaut, le nombre de différences est inconnu
        CalculerDifferences = -1

        Try
            'Si le noeud est REPLICA
            If pNodeReplica.Tag.ToString = "REPLICA" Then
                'Par défaut, le nombre de différences est inconnu
                CalculerDifferences = 0

                'Traiter toutes les classes
                For i = 0 To pNodeReplica.Nodes.Count - 1
                    'Définir le noeud à traiter
                    pNode = pNodeReplica.Nodes.Item(i)

                    'Traiter tous les types de différences (Détruits/Ajoutés/Modifiés)
                    For j = 0 To pNode.Nodes.Count - 1
                        'Compter le nombre de différences
                        CalculerDifferences = CalculerDifferences + pNode.Nodes.Item(j).Nodes.Count
                    Next
                Next
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeReplica = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de calculer le nombre d'éléments et d'attributs différents contenu dans un noeud de TreewView d'attributs d'éléments.
    '''</summary>
    '''
    '''<param name="pNodeDepart">TreeNode de départ contenant les attributs d'éléments différents.</param>
    '''<param name="iNbElements">Nombre d'éléments différents.</param>
    '''<param name="iNbAttributs">Nombre d'attributs d'éléments différents.</param>
    ''' 
    Public Sub CalculerDifferences(ByVal pNodeDepart As TreeNode, ByRef iNbElements As Integer, ByRef iNbAttributs As Integer)
        Try
            'Si le noeud est REPLICA
            If pNodeDepart.Tag.ToString = "ELEMENT" Then
                'Compter le nombre d'éléments
                iNbElements = iNbElements + 1
                'Compter le nombre d'attributs
                iNbAttributs = iNbAttributs + pNodeDepart.Nodes.Count

            Else
                'Traiter toutes les classes
                For i = 0 To pNodeDepart.Nodes.Count - 1
                    'Définir le noeud à traiter
                    Call CalculerDifferences(pNodeDepart.Nodes.Item(i), iNbElements, iNbAttributs)
                Next
            End If

        Catch ex As Exception
            Throw
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de vider la mémoire des objets de la classe.
    '''</summary>
    '''
    Protected Overrides Sub finalize()
        'Libérer les Géodatabase
        If gpGdbEnfant IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(gpGdbEnfant)
        If gpGdbArchive IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(gpGdbArchive)
        'Vider la mémoire
        gpGdbParent = Nothing
        gpGdbEnfant = Nothing
        gpGdbArchive = Nothing
        gpReplicaParent = Nothing
        gpReplicaEnfant = Nothing
        gpDataChanges = Nothing
        gpTrackCancel = Nothing
        'Récupération de la mémoire disponible
        GC.Collect()
    End Sub
#End Region

#Region "Routines et fonctions pour gérer les conflits et les différences contenus dans un TreeView"
    '''<summary>
    ''' Routine qui permet d'accepter l'action effectuée pour un ou plusieurs éléments de la Géodatabase enfant à partir d'un noeud de TreeView.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Noeud d'un TreeView dans lequel l'identification d'un ou plusieurs attributs d'éléments à traiter sont présents.</param>
    '''<param name="pNodeReplica"> Noeud d'un TreeView dans lequel l'identification complète du réplica est présente.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    ''' 
    '''<remarks>
    ''' L'état de l'élément, le nom de la table, l'identifiant de l'élément et le nom de l'attribut est présent dans le noeud du TreeView.
    ''' Si l'état de l'élément enfant est AJOUTER, l'élément enfant ajouté sera aussi ajouté dans le parent et l'archive.
    ''' Si l'état de l'élément enfant est DETRUIRE, l'élément enfant détruit sera aussi détruit dans le parent et l'archive.
    ''' Si l'état de l'élément enfant est MODIFIER, l'élément enfant modifié sera aussi modifié dans le parent et l'archive.
    '''</remarks>
    ''' 
    Public Sub AccepterActionEnfant(ByRef pNodeTraiter As TreeNode, ByRef pNodeReplica As TreeNode, Optional ByRef pTableEnfant As ITable = Nothing, _
                                    Optional ByRef pTableArchive As ITable = Nothing, Optional ByRef pTableParent As ITable = Nothing)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud enfant d'un autre noeud.
        Dim sEtatElement As String = Nothing    'Contient l'état de l'élément.
        Dim sNomTable As String = Nothing       'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing    'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                'Contient l'identifiant de l'élément.

        Try
            'Vérifier si le noeud de recherche est valide et si le texte de recherche est spécifié
            If pNodeTraiter IsNot Nothing Then
                'Vérifier si le noeud est un élément
                If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                    'Définir l'état
                    sEtatElement = pNodeTraiter.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Accepter l'élément ajouté de la GdbEnfant
                        Call AccepterAjouterElementEnfant(sNomTable, iOid, pTableEnfant, pTableArchive, pTableParent)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Accepter l'élément détruit de la GdbEnfant
                        Call AccepterDetruireElementEnfant(sNomTable, iOid, pTableEnfant, pTableArchive)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Accepter l'élément modifié de la GdbEnfant
                        Call AccepterModifierElementEnfant(pNodeTraiter, pTableEnfant, pTableArchive, pTableParent)
                    End If

                    'Détruire tous les noeuds vides parents du noeud à traiter.
                    Call DetruireNoeudsParentsVides(pNodeTraiter)

                    'Vérifier si le noeud est une geométrie
                ElseIf pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                    'Définir l'état
                    sEtatElement = pNodeTraiter.Parent.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Parent.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Accepter l'action effectué dans l'élément de la GdbEnfant
                        Call AccepterAjouterElementEnfant(sNomTable, iOid, pTableEnfant, pTableArchive, pTableParent)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Accepter l'action effectué dans l'élément de la GdbEnfant
                        Call AccepterDetruireElementEnfant(sNomTable, iOid, pTableEnfant, pTableArchive)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Accepter l'action effectué dans l'élément de la GdbEnfant
                        Call AccepterModifierAttributEnfant(pNodeTraiter, pTableEnfant, pTableArchive, pTableParent)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter)
                    End If

                    'Si le noeud est trouver
                ElseIf pNodeTraiter.Tag.ToString = "TROUVER" Then
                    'Traiter tous les noeud
                    For Each pNode In pNodeReplica.Nodes.Find(pNodeTraiter.Name, True)
                        'Traiter le noeud
                        Call AccepterActionEnfant(pNode, pNodeReplica, pTableEnfant, pTableArchive, pTableParent)
                    Next

                    'Détruire le noeud
                    pNodeTraiter.Remove()

                    'Sinon, c'est un noeud de groupe
                Else
                    'Traiter tous les noeuds du noeud à traiter
                    For i = pNodeTraiter.Nodes.Count - 1 To 0 Step -1
                        'Définir le noeud à traiter
                        pNode = pNodeTraiter.Nodes.Item(i)

                        'Traiter le noeud
                        Call AccepterActionEnfant(pNode, pNodeReplica, pTableEnfant, pTableArchive, pTableParent)
                    Next

                    'Vérifier si le noeud n'est pas un réplica ou un résultat
                    If pNodeTraiter.Tag.ToString <> "REPLICA" Then
                        'Vérifier si le noeud est vide
                        If pNodeTraiter.Nodes.Count = 0 Then
                            'Détruire le noeud
                            pNodeTraiter.Remove()
                        End If
                    End If
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour ajouter un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    ''' 
    Private Sub AccepterAjouterElementEnfant(ByVal sNomTable As String, ByVal iOid As Integer, _
                                             ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable, ByRef pTableParent As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing     'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing    'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing     'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pDataset As IDataset = Nothing              'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing                'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing               'Interface contenant un élément de la table d'archive.
        Dim pRowParent As IRow = Nothing                'Interface contenant un élément de la table parent.
        Dim pFeatureEnfant As IFeature = Nothing        'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing       'Interface contenant un élément de la table d'archive.
        Dim pFeatureParent As IFeature = Nothing        'Interface contenant un élément de la table parent.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableEnfant, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.CreateRow
                'Définir l'élément parent
                pRowParent = pTableParent.CreateRow

                'Traiter tous les attributs
                For i = 0 To pTableEnfant.Fields.FieldCount - 1
                    'Vérifier si l'attribut est editable
                    If pTableEnfant.Fields.Field(i).Editable Then
                        'Vérifier si l'attribut est une géométrie
                        If pTableArchive.Fields.Field(i).Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour traiter la géométrie
                            pFeatureEnfant = CType(pRowEnfant, IFeature)
                            pFeatureArchive = CType(pRowArchive, IFeature)
                            pFeatureParent = CType(pRowParent, IFeature)

                            'Copier la géométrie
                            pFeatureParent.Shape = pFeatureEnfant.Shape
                            'Copier la géométrie
                            pFeatureArchive.Shape = pFeatureEnfant.Shape

                            'Si l'attribut n'est pas une géométrie
                        Else
                            'Copier la valeur de l'attribut
                            pRowParent.Value(i) = pRowEnfant.Value(i)
                            'Copier la valeur de l'attribut
                            pRowArchive.Value(i) = pRowEnfant.Value(i)
                        End If
                    End If
                Next

                'Sauver l'élément parent ajouté
                pRowParent.Store()

                'Sauver l'élément d'archive ajouté
                pRowArchive.Store()

            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pFeatWorkspaceParent = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pRowParent = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
            pFeatureParent = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour détruire un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    ''' 
    Private Sub AccepterDetruireElementEnfant(ByVal sNomTable As String, ByVal iOid As Integer, ByRef pTableArchive As ITable, ByRef pTableParent As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing    'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing     'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pDataset As IDataset = Nothing              'Interface contenant l'information de la classe.
        Dim pRowArchive As IRow = Nothing               'Interface contenant un élément de la table d'archive.
        Dim pRowParent As IRow = Nothing                'Interface contenant un élément de la table parent.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableArchive, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
            End If

            'Interface pour ouvrir les tables
            pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableParent, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table parent
                pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table parent
                pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)
                'Détruire l'élément parent
                pRowParent.Delete()
            Catch ex As Exception
                'On ne fait rien
            End Try

            Try
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)
                'Détruire l'élément d'archive
                pRowArchive.Delete()
            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceArchive = Nothing
            pFeatWorkspaceParent = Nothing
            pDataset = Nothing
            pRowArchive = Nothing
            pRowParent = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour modifier un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    ''' 
    Private Sub AccepterModifierElementEnfant(ByVal pNodeTraiter As TreeNode, ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable, ByRef pTableParent As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing     'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing    'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing     'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pDataset As IDataset = Nothing              'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing                'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing               'Interface contenant un élément de la table d'archive.
        Dim pRowParent As IRow = Nothing                'Interface contenant un élément de la table parent.
        Dim pFeatureEnfant As IFeature = Nothing        'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing       'Interface contenant un élément de la table d'archive.
        Dim pFeatureParent As IFeature = Nothing        'Interface contenant un élément de la table parent.
        Dim pNode As TreeNode = Nothing             'Contient un noeud d'attribut.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableEnfant, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableParent, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Name)
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)

                'Traiter tous les noeuds du noeud à traiter
                For Each pNode In pNodeTraiter.Nodes
                    'Définir le nom de l'attribut
                    sNomAttribut = pNode.Name.Split(CChar("/"))(2)

                    'Définir la position de l'attribut
                    iPosAtt = pTableEnfant.FindField(sNomAttribut)

                    'Vérifier si l'attribut est une géométrie
                    If pTableEnfant.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                        'Interface pour traiter la géométrie
                        pFeatureEnfant = CType(pRowEnfant, IFeature)
                        pFeatureArchive = CType(pRowArchive, IFeature)
                        pFeatureParent = CType(pRowParent, IFeature)

                        'Copier la géométrie enfant dans le parent
                        pFeatureParent.Shape = pFeatureEnfant.Shape

                        'Copier la géométrie enfant dans l'archive
                        pFeatureArchive.Shape = pFeatureEnfant.Shape

                        'Si l'attribut n'est pas une géométrie
                    Else
                        'Copier la valeur de l'attribut enfant dans le parent
                        pRowParent.Value(iPosAtt) = pRowEnfant.Value(iPosAtt)

                        'Copier la valeur de l'attribut enfant dans l'archive
                        pRowArchive.Value(iPosAtt) = pRowEnfant.Value(iPosAtt)
                    End If
                Next

                'Sauver la modification du parent
                pRowParent.Store()

                'Sauver la modification de l'archive
                pRowParent.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pFeatWorkspaceParent = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pRowParent = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
            pFeatureParent = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour modifier un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    ''' 
    Private Sub AccepterModifierAttributEnfant(ByVal pNodeTraiter As TreeNode, ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable, ByRef pTableParent As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing     'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing    'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing     'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing           'Interface contenant un élément de la table d'archive.
        Dim pRowParent As IRow = Nothing            'Interface contenant un élément de la table parent.
        Dim pFeatureEnfant As IFeature = Nothing    'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing   'Interface contenant un élément de la table d'archive.
        Dim pFeatureParent As IFeature = Nothing    'Interface contenant un élément de la table parent.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableEnfant, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableParent, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Parent.Name)
                'Définir l'élément parent
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)

                'Définir le nom de l'attribut
                sNomAttribut = pNodeTraiter.Name.Split(CChar("/"))(2)

                'Définir la position de l'attribut
                iPosAtt = pTableArchive.FindField(sNomAttribut)

                'Vérifier si l'attribut est une géométrie
                If pTableArchive.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                    'Interface pour traiter la géométrie
                    pFeatureEnfant = CType(pRowEnfant, IFeature)
                    pFeatureArchive = CType(pRowArchive, IFeature)
                    pFeatureParent = CType(pRowParent, IFeature)

                    'Copier la géométrie enfant dans le parent
                    pFeatureParent.Shape = pFeatureEnfant.Shape

                    'Copier la géométrie enfant dans l'archive
                    pFeatureArchive.Shape = pFeatureEnfant.Shape

                    'Si l'attribut n'est pas une géométrie
                Else
                    'Copier la valeur de l'attribut enfant dans le parent
                    pRowParent.Value(iPosAtt) = pRowEnfant.Value(iPosAtt)

                    'Copier la valeur de l'attribut enfant dans l'archive
                    pRowArchive.Value(iPosAtt) = pRowEnfant.Value(iPosAtt)
                End If

                'Sauver la modification du parent
                pRowParent.Store()

                'Sauver la modification de l'archive
                pRowParent.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pFeatWorkspaceParent = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pRowParent = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
            pFeatureParent = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action effectuée pour un ou plusieurs éléments de la Géodatabase enfant à partir d'un noeud de TreeView.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Noeud d'un TreeView dans lequel l'identification d'un ou plusieurs attributs d'éléments à traiter sont présents.</param>
    '''<param name="pNodeReplica"> Noeud d'un TreeView dans lequel l'identification complète du réplica est présente.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    '''<remarks>
    ''' L'état de l'élément, le nom de la table, l'identifiant de l'élément et le nom de l'attribut est présent dans le noeud du TreeView.
    ''' Si l'état de l'élément enfant est AJOUTER, l'élément du parent sera détruit.
    ''' Si l'état de l'élément enfant est DETRUIRE, l'élément d'archive sera détruit.
    ''' Si l'état de l'élément enfant est MODIFIER, les valeurs des attributs d'archive à traiter seront copiées dans les valeurs des attributs parent.
    '''</remarks>
    ''' 
    Public Sub RefuserActionEnfant(ByRef pNodeTraiter As TreeNode, ByRef pNodeReplica As TreeNode, _
                                   Optional ByRef pTableEnfant As ITable = Nothing, Optional ByRef pTableArchive As ITable = Nothing)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud enfant d'un autre noeud.
        Dim sEtatElement As String = Nothing    'Contient l'état de l'élément.
        Dim sNomTable As String = Nothing       'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing    'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                'Contient l'identifiant de l'élément.

        Try
            'Vérifier si le noeud de recherche est valide et si le texte de recherche est spécifié
            If pNodeTraiter IsNot Nothing Then
                'Vérifier si le noeud est un élément
                If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                    'Définir l'état
                    sEtatElement = pNodeTraiter.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Refuser l'élément ajouté de la GdbEnfant
                        Call RefuserAjouterElementEnfant(sNomTable, iOid, pTableEnfant)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Refuser l'élément détruit de la GdbEnfant
                        Call RefuserDetruireElementEnfant(sNomTable, iOid, pTableEnfant, pTableArchive)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Refuser l'élément modifié de la GdbEnfant
                        Call RefuserModifierElementEnfant(pNodeTraiter, pTableEnfant, pTableArchive)
                    End If

                    'Détruire tous les noeuds vides parents du noeud à traiter.
                    Call DetruireNoeudsParentsVides(pNodeTraiter)

                    'Vérifier si le noeud est une geométrie
                ElseIf pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                    'Définir l'état
                    sEtatElement = pNodeTraiter.Parent.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Parent.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Refuser l'action effectué dans l'élément de la GdbEnfant
                        Call RefuserAjouterElementEnfant(sNomTable, iOid, pTableEnfant)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Refuser l'action effectué dans l'élément de la GdbEnfant
                        Call RefuserDetruireElementEnfant(sNomTable, iOid, pTableEnfant, pTableArchive)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Refuser l'action effectué dans l'élément de la GdbEnfant
                        Call RefuserModifierAttributEnfant(pNodeTraiter, pTableEnfant, pTableArchive)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter)
                    End If

                    'Si le noeud est trouver
                ElseIf pNodeTraiter.Tag.ToString = "TROUVER" Then
                    'Traiter tous les noeud
                    For Each pNode In pNodeReplica.Nodes.Find(pNodeTraiter.Name, True)
                        'Traiter le noeud
                        Call RefuserActionEnfant(pNode, pNodeReplica, pTableEnfant, pTableArchive)
                    Next

                    'Détruire le noeud
                    pNodeTraiter.Remove()

                    'Sinon, c'est un noeud de groupe
                Else
                    'Traiter tous les noeuds du noeud à traiter
                    For i = pNodeTraiter.Nodes.Count - 1 To 0 Step -1
                        'Définir le noeud à traiter
                        pNode = pNodeTraiter.Nodes.Item(i)

                        'Traiter le noeud
                        Call RefuserActionEnfant(pNode, pNodeReplica, pTableEnfant, pTableArchive)
                    Next

                    'Vérifier si le noeud n'est pas un réplica ou un résultat
                    If pNodeTraiter.Tag.ToString <> "REPLICA" Then
                        'Vérifier si le noeud est vide
                        If pNodeTraiter.Nodes.Count = 0 Then
                            'Détruire le noeud
                            pNodeTraiter.Remove()
                        End If
                    End If
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour ajouter un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    ''' 
    Private Sub RefuserAjouterElementEnfant(ByVal sNomTable As String, ByVal iOid As Integer, ByRef pTableEnfant As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableEnfant, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Détruire l'élément enfant
                pRowEnfant.Delete()
            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour détruire un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub RefuserDetruireElementEnfant(ByVal sNomTable As String, ByVal iOid As Integer, ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing              'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing                'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing               'Interface contenant un élément de la table d'archive.
        Dim pFeatureEnfant As IFeature = Nothing        'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing       'Interface contenant un élément de la table d'archive.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)

            'Interface pour extraire le nom de la table
            pDataset = CType(pTableArchive, IDataset)

            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
            End If

            'Interface pour ouvrir les tables
            pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableEnfant, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.CreateRow

                'Traiter tous les attributs
                For i = 0 To pTableArchive.Fields.FieldCount - 1
                    'Vérifier si l'attribut est editable
                    If pTableArchive.Fields.Field(i).Editable Then
                        'Vérifier si l'attribut est une géométrie
                        If pTableArchive.Fields.Field(i).Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour traiter la géométrie
                            pFeatureArchive = CType(pRowArchive, IFeature)
                            pFeatureEnfant = CType(pRowEnfant, IFeature)

                            'Copier la géométrie
                            pFeatureEnfant.Shape = pFeatureArchive.Shape

                            'Si l'attribut n'est pas une géométrie
                        Else
                            'Copier la valeur de l'attribut
                            pRowEnfant.Value(i) = pRowArchive.Value(i)
                        End If
                    End If
                Next

                'Sauver l'élément enfant ajouté
                pRowEnfant.Store()

                'Détruire l'élément
                pRowArchive.Delete()

            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour modifier un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub RefuserModifierElementEnfant(ByVal pNodeTraiter As TreeNode, ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing  'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing           'Interface contenant un élément de la table d'archive.
        Dim pFeatureEnfant As IFeature = Nothing    'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing   'Interface contenant un élément de la table d'archive.
        Dim pNode As TreeNode = Nothing             'Contient un noeud d'attribut.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableEnfant, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Name)
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)

                'Traiter tous les noeuds du noeud à traiter
                For Each pNode In pNodeTraiter.Nodes
                    'Définir le nom de l'attribut
                    sNomAttribut = pNode.Name.Split(CChar("/"))(2)

                    'Définir la position de l'attribut
                    iPosAtt = pTableArchive.FindField(sNomAttribut)

                    'Vérifier si l'attribut est une géométrie
                    If pTableArchive.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                        'Interface pour traiter la géométrie
                        pFeatureEnfant = CType(pRowEnfant, IFeature)
                        pFeatureArchive = CType(pRowArchive, IFeature)

                        'Copier la géométrie d'archive dans l'enfant
                        pFeatureEnfant.Shape = pFeatureArchive.Shape

                        'Si l'attribut n'est pas une géométrie
                    Else
                        'Copier la valeur de l'attribut d'archive dans l'enfant
                        pRowEnfant.Value(iPosAtt) = pRowArchive.Value(iPosAtt)
                    End If
                Next

                'Sauver la modification de l'enfant
                pRowEnfant.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
            pNode = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour modifier un élément de la Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub RefuserModifierAttributEnfant(ByVal pNodeTraiter As TreeNode, ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing  'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing           'Interface contenant un élément de la table d'archive.
        Dim pFeatureEnfant As IFeature = Nothing    'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing   'Interface contenant un élément de la table d'archive.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableEnfant, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Parent.Name)
                'Définir l'élément parent
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)

                'Définir le nom de l'attribut
                sNomAttribut = pNodeTraiter.Name.Split(CChar("/"))(2)

                'Définir la position de l'attribut
                iPosAtt = pTableArchive.FindField(sNomAttribut)

                'Vérifier si l'attribut est une géométrie
                If pTableArchive.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                    'Interface pour traiter la géométrie
                    pFeatureEnfant = CType(pRowEnfant, IFeature)
                    pFeatureArchive = CType(pRowArchive, IFeature)

                    'Copier la géométrie d'archive dans le parent
                    pFeatureEnfant.Shape = pFeatureArchive.Shape

                    'Si l'attribut n'est pas une géométrie
                Else
                    'Copier la valeur de l'attribut d'archive dans le parent
                    pRowEnfant.Value(iPosAtt) = pRowArchive.Value(iPosAtt)
                End If

                'Sauver la modification du parent
                pRowEnfant.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action effectuée pour un ou plusieurs éléments de la Géodatabase parent à partir d'un noeud de TreeView.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Noeud d'un TreeView dans lequel l'identification d'un ou plusieurs attributs d'éléments à traiter sont présents.</param>
    '''<param name="pNodeReplica"> Noeud d'un TreeView dans lequel l'identification complète du réplica est présente.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    '''<remarks>
    ''' L'état de l'élément, le nom de la table, l'identifiant de l'élément et le nom de l'attribut est présent dans le noeud du TreeView.
    ''' Si l'état de l'élément parent est AJOUTER, un nouvel élément enfant sera créé à partir de l'élément parent et l'élément parent sera détruit.
    ''' Si l'état de l'élément parent est DETRUIRE, l'élément enfant sera détruit.
    ''' Si l'état de l'élément parent est MODIFIER, les valeurs des attributs parent à traiter seront copiées dans l'élément enfant et
    '''                                             les valeurs des attributs d'archive à traiter seront copiées dans l'élément parent.
    '''</remarks>
    ''' 
    Public Sub AccepterActionParent(ByRef pNodeTraiter As TreeNode, ByRef pNodeReplica As TreeNode, Optional ByRef pTableParent As ITable = Nothing, _
                                    Optional ByRef pTableEnfant As ITable = Nothing, Optional ByRef pTableArchive As ITable = Nothing)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud enfant d'un autre noeud.
        Dim sValeurs As String() = Nothing      'Contient les valeurs du noeud trouvé.
        Dim sEtatElement As String = Nothing    'Contient l'état de l'élément.
        Dim sNomTable As String = Nothing       'Contient le nom de la table.
        Dim iOid As Integer = -1                'Contient l'identifiant de l'élément.

        Try
            'Vérifier si le noeud de recherche est valide et si le texte de recherche est spécifié
            If pNodeTraiter IsNot Nothing Then
                'Vérifier si le noeud est un élément
                If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                    'Définir l'état de l'élément
                    sEtatElement = pNodeTraiter.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Accepter l'élément ajouté de la GdbParent
                        Call AccepterAjouterElementParent(sNomTable, iOid, pTableParent, pTableEnfant)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Accepter l'élément détruit de la GdbParent
                        Call AccepterDetruireElementParent(sNomTable, iOid, pTableEnfant)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Accepter l'élément modifié de la GdbParent
                        Call AccepterModifierElementParent(pNodeTraiter, pTableParent, pTableEnfant, pTableArchive)
                    End If

                    'Détruire tous les noeuds vides parents du noeud à traiter.
                    Call DetruireNoeudsParentsVides(pNodeTraiter)

                    'Vérifier si le noeud est une geométrie
                ElseIf pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                    'Définir l'état de l'élément
                    sEtatElement = pNodeTraiter.Parent.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Parent.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Accepter l'action effectué dans l'élément de la GdbParent
                        Call AccepterAjouterElementParent(sNomTable, iOid, pTableParent, pTableEnfant)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Accepter l'action effectué dans l'élément de la GdbParent
                        Call AccepterDetruireElementParent(sNomTable, iOid, pTableEnfant)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Accepter l'action effectué dans l'élément de la GdbParent
                        Call AccepterModifierAttributParent(pNodeTraiter, pTableParent, pTableEnfant, pTableArchive)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter)
                    End If

                    'Si le noeud est trouver
                ElseIf pNodeTraiter.Tag.ToString = "TROUVER" Then
                    'Traiter tous les noeud
                    For Each pNode In pNodeReplica.Nodes.Find(pNodeTraiter.Name, True)
                        'Traiter le noeud
                        Call AccepterActionParent(pNode, pNodeReplica, pTableEnfant, pTableArchive)

                        'Détruire le noeud
                        pNode.Remove()
                    Next

                    'Sinon, c'est un noeud de groupe
                Else
                    'Traiter tous les noeuds du noeud à traiter
                    For i = pNodeTraiter.Nodes.Count - 1 To 0 Step -1
                        'Définir le noeud à traiter
                        pNode = pNodeTraiter.Nodes.Item(i)

                        'Traiter le noeud
                        Call AccepterActionParent(pNode, pNodeReplica, pTableParent, pTableEnfant, pTableArchive)
                    Next

                    'Vérifier si le noeud n'est pas un réplica ou un résultat
                    If pNodeTraiter.Tag.ToString <> "REPLICA" Then
                        'Vérifier si le noeud est vide
                        If pNodeTraiter.Nodes.Count = 0 Then
                            'Détruire le noeud
                            pNodeTraiter.Remove()
                        End If
                    End If
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
            sValeurs = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour ajouter un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    ''' 
    Private Sub AccepterAjouterElementParent(ByVal sNomTable As String, ByVal iOid As Integer, ByRef pTableParent As ITable, ByRef pTableEnfant As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowParent As IRow = Nothing            'Interface contenant un élément de la table parent.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.
        Dim pFeatureParent As IFeature = Nothing    'Interface contenant un élément de la table parent.
        Dim pFeatureEnfant As IFeature = Nothing    'Interface contenant un élément de la table enfant.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableParent, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table parent
                pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table parent
                pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
            End If

            'Interface pour ouvrir les tables
            pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableEnfant, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.CreateRow

                'Traiter tous les attributs
                For i = 0 To pTableParent.Fields.FieldCount - 1
                    'Vérifier si l'attribut est editable
                    If pTableParent.Fields.Field(i).Editable Then
                        'Vérifier si l'attribut est une géométrie
                        If pTableParent.Fields.Field(i).Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour traiter la géométrie
                            pFeatureParent = CType(pRowParent, IFeature)
                            pFeatureEnfant = CType(pRowEnfant, IFeature)

                            'Copier la géométrie
                            pFeatureEnfant.Shape = pFeatureParent.Shape

                            'Si l'attribut n'est pas une géométrie
                        Else
                            'Copier la valeur de l'attribut
                            pRowEnfant.Value(i) = pRowParent.Value(i)
                        End If
                    End If
                Next

                'Sauver l'élément enfant ajouté
                pRowEnfant.Store()

                'Détruire l'élément parent
                pRowParent.Delete()

            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceParent = Nothing
            pFeatWorkspaceEnfant = Nothing
            pDataset = Nothing
            pRowParent = Nothing
            pRowEnfant = Nothing
            pFeatureParent = Nothing
            pFeatureEnfant = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour détruire un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    ''' 
    Private Sub AccepterDetruireElementParent(ByVal sNomTable As String, ByVal iOid As Integer, ByRef pTableEnfant As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.
        Dim pFeatureEnfant As IFeature = Nothing    'Interface contenant un élément de la table enfant.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)

            'Interface pour extraire le nom de la table
            pDataset = CType(pTableEnfant, IDataset)

            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.GetRow(iOid)

                'Détruire l'élément
                pRowEnfant.Delete()

            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceEnfant = Nothing
            pDataset = Nothing
            pRowEnfant = Nothing
            pFeatureEnfant = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour modifier un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub AccepterModifierElementParent(ByVal pNodeTraiter As TreeNode, ByRef pTableParent As ITable, ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing  'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowParent As IRow = Nothing            'Interface contenant un élément de la table parent.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing           'Interface contenant un élément de la table d'archive.
        Dim pFeatureParent As IFeature = Nothing    'Interface contenant un élément de la table parent.
        Dim pFeatureEnfant As IFeature = Nothing    'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing   'Interface contenant un élément de la table d'archive.
        Dim pNode As TreeNode = Nothing             'Contient un noeud d'attribut.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableParent, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableEnfant, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Name)
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)

                'Traiter tous les noeuds du noeud à traiter
                For Each pNode In pNodeTraiter.Nodes
                    'Définir le nom de l'attribut
                    sNomAttribut = pNode.Name.Split(CChar("/"))(2)

                    'Définir la position de l'attribut
                    iPosAtt = pTableEnfant.FindField(sNomAttribut)

                    'Vérifier si l'attribut est une géométrie
                    If pTableEnfant.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                        'Interface pour traiter la géométrie
                        pFeatureParent = CType(pRowParent, IFeature)
                        pFeatureEnfant = CType(pRowEnfant, IFeature)
                        pFeatureArchive = CType(pRowArchive, IFeature)

                        'Copier la géométrie parent dans l'enfant
                        pFeatureEnfant.Shape = pFeatureParent.Shape

                        'Copier la géométrie d'archive dans le parent
                        pFeatureParent.Shape = pFeatureArchive.Shape

                        'Si l'attribut n'est pas une géométrie
                    Else
                        'Copier la valeur de l'attribut parent dans l'enfant
                        pRowEnfant.Value(iPosAtt) = pRowParent.Value(iPosAtt)

                        'Copier la valeur de l'attribut d'archive dans le parent
                        pRowParent.Value(iPosAtt) = pRowArchive.Value(iPosAtt)
                    End If
                Next

                'Sauver la modification de l'enfant
                pRowEnfant.Store()

                'Sauver la modification du parent
                pRowParent.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceParent = Nothing
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowParent = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pFeatureParent = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
            pNode = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'accepter l'action pour modifier un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub AccepterModifierAttributParent(ByVal pNodeTraiter As TreeNode, ByRef pTableParent As ITable, ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pFeatWorkspaceEnfant As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase enfant.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing  'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowParent As IRow = Nothing            'Interface contenant un élément de la table parent.
        Dim pRowEnfant As IRow = Nothing            'Interface contenant un élément de la table enfant.
        Dim pRowArchive As IRow = Nothing           'Interface contenant un élément de la table d'archive.
        Dim pFeatureParent As IFeature = Nothing    'Interface contenant un élément de la table parent.
        Dim pFeatureEnfant As IFeature = Nothing    'Interface contenant un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing   'Interface contenant un élément de la table d'archive.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableParent, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableEnfant, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableEnfant = pFeatWorkspaceEnfant.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Name)
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)
                'Définir l'élément enfant
                pRowEnfant = pTableEnfant.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)

                'Définir le nom de l'attribut
                sNomAttribut = pNodeTraiter.Name.Split(CChar("/"))(2)

                'Définir la position de l'attribut
                iPosAtt = pTableEnfant.FindField(sNomAttribut)

                'Vérifier si l'attribut est une géométrie
                If pTableEnfant.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                    'Interface pour traiter la géométrie
                    pFeatureParent = CType(pRowParent, IFeature)
                    pFeatureEnfant = CType(pRowEnfant, IFeature)
                    pFeatureArchive = CType(pRowArchive, IFeature)

                    'Copier la géométrie parent dans l'enfant
                    pFeatureEnfant.Shape = pFeatureParent.Shape

                    'Copier la géométrie d'archive dans le parent
                    pFeatureParent.Shape = pFeatureArchive.Shape

                    'Si l'attribut n'est pas une géométrie
                Else
                    'Copier la valeur de l'attribut parent dans l'enfant
                    pRowEnfant.Value(iPosAtt) = pRowParent.Value(iPosAtt)

                    'Copier la valeur de l'attribut d'archive dans le parent
                    pRowParent.Value(iPosAtt) = pRowArchive.Value(iPosAtt)
                End If

                'Sauver la modification de l'enfant
                pRowEnfant.Store()

                'Sauver la modification du parent
                pRowParent.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceParent = Nothing
            pFeatWorkspaceEnfant = Nothing
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowParent = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pFeatureParent = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action effectuée pour un ou plusieurs éléments de la Géodatabase parent à partir d'un noeud de TreeView.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Noeud d'un TreeView dans lequel l'identification d'un ou plusieurs attributs d'éléments à traiter sont présents.</param>
    '''<param name="pNodeReplica"> Noeud d'un TreeView dans lequel l'identification complète du réplica est présente.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    '''<param name="pTableEnfant"> Interface contenant les éléments de la table enfant.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    '''<remarks>
    ''' L'état de l'élément, le nom de la table, l'identifiant de l'élément et le nom de l'attribut est présent dans le noeud du TreeView.
    ''' Si l'état de l'élément parent est AJOUTER, l'élément du parent sera détruit.
    ''' Si l'état de l'élément parent est DETRUIRE, l'élément d'archive sera détruit.
    ''' Si l'état de l'élément parent est MODIFIER, les valeurs des attributs d'archive à traiter seront copiées dans les valeurs des attributs parent.
    '''</remarks>
    ''' 
    Public Sub RefuserActionParent(ByRef pNodeTraiter As TreeNode, ByRef pNodeReplica As TreeNode, Optional ByRef pTableParent As ITable = Nothing, _
                                   Optional ByRef pTableEnfant As ITable = Nothing, Optional ByRef pTableArchive As ITable = Nothing)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud enfant d'un autre noeud.
        Dim sValeurs As String() = Nothing      'Contient les valeurs du noeud trouvé.
        Dim sEtatElement As String = Nothing    'Contient l'état de l'élément.
        Dim sNomTable As String = Nothing       'Contient le nom de la table.
        Dim iOid As Integer = -1                'Contient l'identifiant de l'élément.

        Try
            'Vérifier si le noeud de recherche est valide et si le texte de recherche est spécifié
            If pNodeTraiter IsNot Nothing Then
                'Vérifier si le noeud est un élément
                If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                    'Définir l'état
                    sEtatElement = pNodeTraiter.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Accepter l'élément ajouté de la GdbParent
                        Call RefuserAjouterElementParent(sNomTable, iOid, pTableParent)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Accepter l'élément détruit de la GdbParent
                        Call RefuserDetruireElementParent(sNomTable, iOid, pTableArchive)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Accepter l'élément modifié de la GdbParent
                        Call RefuserModifierElementParent(pNodeTraiter, pTableParent, pTableArchive)
                    End If

                    'Détruire tous les noeuds vides parents du noeud à traiter.
                    Call DetruireNoeudsParentsVides(pNodeTraiter)

                    'Vérifier si le noeud est une geométrie
                ElseIf pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                    'Définir l'état
                    sEtatElement = pNodeTraiter.Parent.Parent.Name
                    'Définir le nom de la table
                    sNomTable = pNodeTraiter.Parent.Parent.Parent.Name
                    'Définir l'identifiant de l'élément
                    iOid = CInt(pNodeTraiter.Parent.Name)

                    'Si l'état est AJOUTER
                    If sEtatElement = "AJOUTER" Then
                        'Accepter l'action effectué dans l'élément de la GdbParent
                        Call RefuserAjouterElementParent(sNomTable, iOid, pTableParent)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est DETRUIRE
                    ElseIf sEtatElement = "DETRUIRE" Then
                        'Accepter l'action effectué dans l'élément de la GdbParent
                        Call RefuserDetruireElementParent(sNomTable, iOid, pTableArchive)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter.Parent)

                        'Si l'état est MODIFIER
                    ElseIf sEtatElement = "MODIFIER" Then
                        'Accepter l'action effectué dans l'élément de la GdbParent
                        Call RefuserModifierAttributParent(pNodeTraiter, pTableParent, pTableArchive)

                        'Détruire tous les noeuds vides parents du noeud à traiter.
                        Call DetruireNoeudsParentsVides(pNodeTraiter)
                    End If

                    'Si le noeud est trouver
                ElseIf pNodeTraiter.Tag.ToString = "TROUVER" Then
                    'Traiter tous les noeud
                    For Each pNode In pNodeReplica.Nodes.Find(pNodeTraiter.Name, True)
                        'Traiter le noeud
                        Call RefuserActionParent(pNode, pNodeReplica, pTableEnfant, pTableArchive)

                        'Détruire le noeud
                        pNode.Remove()
                    Next

                    'Sinon, c'est un noeud de groupe
                Else
                    'Traiter tous les noeuds du noeud à traiter
                    For i = pNodeTraiter.Nodes.Count - 1 To 0 Step -1
                        'Définir le noeud à traiter
                        pNode = pNodeTraiter.Nodes.Item(i)

                        'Traiter le noeud
                        Call RefuserActionParent(pNode, pNodeReplica, pTableParent, pTableEnfant, pTableArchive)
                    Next

                    'Vérifier si le noeud n'est pas un réplica ou un résultat
                    If pNodeTraiter.Tag.ToString <> "REPLICA" Then
                        'Vérifier si le noeud est vide
                        If pNodeTraiter.Nodes.Count = 0 Then
                            'Détruire le noeud
                            pNodeTraiter.Remove()
                        End If
                    End If
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
            sValeurs = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour ajouter un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    ''' 
    Private Sub RefuserAjouterElementParent(ByVal sNomTable As String, ByVal iOid As Integer, ByRef pTableParent As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowParent As IRow = Nothing            'Interface contenant un élément de la table parent.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableParent, IDataset)
            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table parent
                pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table parent
                pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)
                'Détruire l'élément parent
                pRowParent.Delete()
            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceParent = Nothing
            pDataset = Nothing
            pRowParent = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour détruire un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub RefuserDetruireElementParent(ByVal sNomTable As String, ByVal iOid As Integer, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing              'Interface contenant l'information de la classe.
        Dim pRowArchive As IRow = Nothing               'Interface contenant un élément de la table enfant.

        Try
            'Interface pour ouvrir les tables
            pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)

            'Interface pour extraire le nom de la table
            pDataset = CType(pTableArchive, IDataset)

            'Vérifier si la table est inconnue
            If pDataset Is Nothing Then
                'Définir la table enfant
                pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                'Vérifier si la table est inconnue
            ElseIf sNomTable <> pDataset.BrowseName Then
                'Définir la table enfant
                pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
            End If

            Try
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)
                'Détruire l'élément
                pRowArchive.Delete()

            Catch ex As Exception
                'On ne fait rien
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour modifier un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub RefuserModifierElementParent(ByVal pNodeTraiter As TreeNode, ByRef pTableParent As ITable, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing  'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowParent As IRow = Nothing            'Interface contenant un élément de la table parent.
        Dim pRowArchive As IRow = Nothing           'Interface contenant un élément de la table d'archive.
        Dim pFeatureParent As IFeature = Nothing    'Interface contenant un élément de la table parent.
        Dim pFeatureArchive As IFeature = Nothing   'Interface contenant un élément de la table d'archive.
        Dim pNode As TreeNode = Nothing             'Contient un noeud d'attribut.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "ELEMENT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableParent, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Name)
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)

                'Traiter tous les noeuds du noeud à traiter
                For Each pNode In pNodeTraiter.Nodes
                    'Définir le nom de l'attribut
                    sNomAttribut = pNode.Name.Split(CChar("/"))(2)

                    'Définir la position de l'attribut
                    iPosAtt = pTableArchive.FindField(sNomAttribut)

                    'Vérifier si l'attribut est une géométrie
                    If pTableArchive.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                        'Interface pour traiter la géométrie
                        pFeatureParent = CType(pRowParent, IFeature)
                        pFeatureArchive = CType(pRowArchive, IFeature)

                        'Copier la géométrie d'archive dans le parent
                        pFeatureParent.Shape = pFeatureArchive.Shape

                        'Si l'attribut n'est pas une géométrie
                    Else
                        'Copier la valeur de l'attribut d'archive dans le parent
                        pRowParent.Value(iPosAtt) = pRowArchive.Value(iPosAtt)
                    End If
                Next

                'Sauver la modification du parent
                pRowParent.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceParent = Nothing
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowParent = Nothing
            pRowArchive = Nothing
            pFeatureParent = Nothing
            pFeatureArchive = Nothing
            pNode = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de refuser l'action pour modifier un élément de la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Contient le noeud du TreeView à traiter.</param>
    '''<param name="pTableParent"> Interface contenant les éléments de la table parent.</param>
    '''<param name="pTableArchive"> Interface contenant les éléments de la table d'archive.</param>
    ''' 
    Private Sub RefuserModifierAttributParent(ByVal pNodeTraiter As TreeNode, ByRef pTableParent As ITable, ByRef pTableArchive As ITable)
        'Déclarer les variables de travail
        Dim pFeatWorkspaceParent As IFeatureWorkspace = Nothing   'Interface contenant toutes les tables de la Géodatabase parent.
        Dim pFeatWorkspaceArchive As IFeatureWorkspace = Nothing  'Interface contenant toutes les tables de la Géodatabase d'archive.
        Dim pDataset As IDataset = Nothing          'Interface contenant l'information de la classe.
        Dim pRowParent As IRow = Nothing            'Interface contenant un élément de la table parent.
        Dim pRowArchive As IRow = Nothing           'Interface contenant un élément de la table d'archive.
        Dim pFeatureParent As IFeature = Nothing    'Interface contenant un élément de la table parent.
        Dim pFeatureArchive As IFeature = Nothing   'Interface contenant un élément de la table d'archive.
        Dim sNomTable As String = Nothing           'Contient le nom de la table.
        Dim sNomAttribut As String = Nothing        'Contient le nom de l'attribut.
        Dim iOid As Integer = -1                    'Contient l'identifiant de l'élément
        Dim iPosAtt As Integer = -1                 'Contient la position de l'attribut.

        Try
            'Vérifier si le noeud est un élément
            If pNodeTraiter.Tag.ToString = "GEOMETRIE" Or pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                'Définir le nom de la table
                sNomTable = pNodeTraiter.Parent.Parent.Parent.Name

                'Interface pour ouvrir les tables
                pFeatWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableParent, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table parent
                    pTableParent = pFeatWorkspaceParent.OpenTable(sNomTable)
                End If

                'Interface pour ouvrir les tables
                pFeatWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableArchive, IDataset)
                'Vérifier si la table est inconnue
                If pDataset Is Nothing Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)

                    'Vérifier si la table est inconnue
                ElseIf sNomTable <> pDataset.BrowseName Then
                    'Définir la table enfant
                    pTableArchive = pFeatWorkspaceArchive.OpenTable(sNomTable)
                End If

                'Définir l'identifiant de l'élément
                iOid = CInt(pNodeTraiter.Parent.Name)
                'Définir l'élément parent
                pRowParent = pTableParent.GetRow(iOid)
                'Définir l'élément d'archive
                pRowArchive = pTableArchive.GetRow(iOid)

                'Définir le nom de l'attribut
                sNomAttribut = pNodeTraiter.Name.Split(CChar("/"))(2)

                'Définir la position de l'attribut
                iPosAtt = pTableArchive.FindField(sNomAttribut)

                'Vérifier si l'attribut est une géométrie
                If pTableArchive.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                    'Interface pour traiter la géométrie
                    pFeatureParent = CType(pRowParent, IFeature)
                    pFeatureArchive = CType(pRowArchive, IFeature)

                    'Copier la géométrie d'archive dans le parent
                    pFeatureParent.Shape = pFeatureArchive.Shape

                    'Si l'attribut n'est pas une géométrie
                Else
                    'Copier la valeur de l'attribut d'archive dans le parent
                    pRowParent.Value(iPosAtt) = pRowArchive.Value(iPosAtt)
                End If

                'Sauver la modification du parent
                pRowParent.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatWorkspaceParent = Nothing
            pFeatWorkspaceArchive = Nothing
            pDataset = Nothing
            pRowParent = Nothing
            pRowArchive = Nothing
            pFeatureParent = Nothing
            pFeatureArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire tous les noeuds vides parents du noeud à traiter.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Noeud d'un TreeView à traiter.</param>
    ''' 
    Private Sub DetruireNoeudsParentsVides(ByRef pNodeTraiter As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeParent As TreeNode = Nothing       'Contient le noeud parent du noeud à traiter.

        Try
            'Vérifier si le noeud à traiter est valide
            If pNodeTraiter IsNot Nothing Then
                'Vérifier si le noeud n'est pas un réplica
                If pNodeTraiter.Tag.ToString <> "REPLICA" Then
                    'Définir le noeud parent
                    pNodeParent = pNodeTraiter.Parent

                    'Détruire le noeud
                    pNodeTraiter.Remove()

                    'Traiter tous les noeuds parent
                    Do Until pNodeParent Is Nothing
                        'Définir le noeud à traiter
                        pNodeTraiter = pNodeParent

                        'Définir le noeud parent du noeud à traiter
                        pNodeParent = pNodeTraiter.Parent

                        'Vérifier si le noeud parent n'est pas un réplica
                        If pNodeTraiter.Tag.ToString <> "REPLICA" Then
                            'Vérifier si le noeud est vide
                            If pNodeTraiter.Nodes.Count = 0 Then
                                'Détruire le noeud
                                pNodeTraiter.Remove()

                                'Si le noeud n'est pas vide
                            Else
                                'Sortir de la boucle
                                Exit Do
                            End If
                        End If
                    Loop
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeParent = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de rechercher tous les éléments contenus dans le TreeView qui contient le texte spécifié.
    '''</summary>
    '''
    '''<param name="pTreeView"> TreeView dans lequel l'identification d'éléments sont présents.</param>
    '''<param name="sTexte">Contient le texte utilisé pour rechercher les éléments à traiter.</param>
    '''<param name="bPresent">Indique si la recherche du texte doit être présent ou non.</param>
    ''' 
    '''<remarks>
    ''' Un nouveau noeud de recherche contenant les éléments trouvés sera créé.
    '''</remarks>
    ''' 
    Public Sub RechercherElements(ByRef pTreeView As TreeView, ByVal sTexte As String, Optional ByVal bPresent As Boolean = True)
        'Déclarer les variables de travail
        Dim pNodeResultat As TreeNode = Nothing         'Noeud d'un TreeView contenant le résultat de la recheche.
        Dim pNodeResultatAncien As TreeNode = Nothing   'Ancien noeud de recherche à détruire.

        Try
            'Vérifier si un texte est spécifié
            If sTexte.Length > 0 And pTreeView.SelectedNode IsNot Nothing Then
                'Vérifier si le noeud de recherche est déjà présent
                If pTreeView.Nodes.Count = 2 Then
                    'Définir l'ancien résultat
                    pNodeResultatAncien = pTreeView.Nodes.Item(1)
                End If

                'Créer le nouvequ noeud contenant le résultat de la recherche
                pNodeResultat = pTreeView.Nodes.Add(sTexte, "Résultat de la recherche : '" & sTexte _
                                                    & "' pour le noeud : '" & pTreeView.SelectedNode.Tag.ToString & "=" & pTreeView.SelectedNode.Name & "'")
                'Définir le type de noeud
                pNodeResultat.Tag = "RESULTAT"

                'Rechercher tous les éléments à partir d'un noeud de TreeView selon le texte spécifié 
                Call RechercherElementsNoeud(pNodeResultat, pTreeView.SelectedNode, sTexte, bPresent)

                'Si un résultat est trouvé
                If pNodeResultat.Nodes.Count > 0 Then
                    'Ouvrir le noeud du résultat de la recheche
                    pNodeResultat.ExpandAll()
                End If

                'Vérifier si le noeud de recherche est déjà présent
                If pNodeResultatAncien IsNot Nothing Then
                    'Détruire le noeud contenant le résultat de la recherche
                    pTreeView.Nodes.Remove(pNodeResultatAncien)
                End If

                'Sélectionner le noeud du résultat de la recherche
                pTreeView.SelectedNode = pNodeResultat
                pTreeView.Focus()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vide la mémoire
            pNodeResultat = Nothing
            pNodeResultatAncien = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de rechercher tous les éléments contenus dans le TreeView qui contient le texte spécifié.
    '''</summary>
    '''
    '''<param name="pNodeResultat">Noeud d'un TreeView contenant le résultat de la recherche.</param>
    '''<param name="pNodeRecherche">Noeud d'un TreeView utilisé pour la recherche.</param>
    '''<param name="sTexte">Contient le texte utilisé pour rechercher les éléments à traiter.</param>
    '''<param name="bPresent">Indique si la recherche du texte doit être présent ou non.</param>
    ''' 
    '''<remarks>
    ''' Un nouveau noeud de recherche contenant les éléments trouvés sera créé.
    '''</remarks>
    ''' 
    Private Sub RechercherElementsNoeud(ByRef pNodeResultat As TreeNode, ByVal pNodeRecherche As TreeNode, _
                                        ByVal sTexte As String, Optional ByVal bPresent As Boolean = True)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud d'un TreeView utilisé pour la recherche.
        Dim pNodeTrouver As TreeNode = Nothing  'Noeud d'un TreeView trouvé.

        Try
            'Vérifier si le noeud de recherche est valide et si le texte de recherche est spécifié
            If pNodeRecherche IsNot Nothing And sTexte.Length > 0 Then
                'Traiter tous les Nodes
                For Each pNode In pNodeRecherche.Nodes
                    'Vérifier si le noeud est une geométrie ou un attribut
                    If pNode.Tag.ToString = "GEOMETRIE" Or pNode.Tag.ToString = "ATTRIBUT" Then
                        'Vérifier si le noeud contient le texte recherché
                        If pNode.Text.Contains(sTexte) = bPresent Then
                            'Ajouter le noeud trouvé
                            pNodeTrouver = pNodeResultat.Nodes.Add(pNode.Name, pNode.Parent.Parent.Text & "/" & pNode.Parent.Parent.Parent.Text & "/" & pNode.Parent.Text & "/" & pNode.Text)
                            'Définir le type de noeud
                            pNodeTrouver.Tag = "TROUVER"
                        End If

                        'Vérifier si le noeud un attribut trouvé
                    ElseIf pNode.Tag.ToString = "TROUVER" Then
                        'Vérifier si le noeud contient le texte recherché
                        If pNode.Text.Contains(sTexte) = bPresent Then
                            'Ajouter le noeud trouvé
                            pNodeTrouver = pNodeResultat.Nodes.Add(pNode.Name, pNode.Text)
                            'Définir le type de noeud
                            pNodeTrouver.Tag = "TROUVER"
                        End If

                        'Sinon
                    Else
                        'Rechercher tous les éléments à partir d'un noeud de TreeView selon le texte spécifié 
                        Call RechercherElementsNoeud(pNodeResultat, pNode, sTexte, bPresent)
                    End If
                Next
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vide la mémoire
            pNode = Nothing
            pNodeTrouver = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de rechercher tous les attributs d'éléments d'un TreeView d'attributs d'éléments contenus dans un autre TreeView d'attributs d'éléments.
    '''</summary>
    '''
    '''<param name="sDescription">Description de la recherche à effectuer.</param>
    '''<param name="pTreeViewResultat"> TreeView dans lequel le résultat des éléments sont présents.</param>
    '''<param name="pTreeViewRecherche">TreeView utilisé pour rechercher les éléments dans lequel les éléments du TreeView de résultat sont présents.</param>
    '''<param name="bPresent">Indique si la recherche des éléments doivent être présents ou non.</param>
    ''' 
    '''<remarks>
    ''' Un nouveau noeud de recherche contenant les attributs d'éléments trouvés sera créé.
    '''</remarks>
    ''' 
    Public Sub RechercherElementsTreeView(ByVal sDescription As String, ByRef pTreeViewResultat As TreeView, ByRef pTreeViewRecherche As TreeView, Optional ByVal bPresent As Boolean = True)
        'Déclarer les variables de travail
        Dim pNodeResultat As TreeNode = Nothing             'Noeud d'un TreeView contenant le résultat de la recheche.
        Dim pNodeResultatAncien As TreeNode = Nothing       'Ancien noeud de recherche à détruire.
        Dim pNodeResultatDepart As TreeNode = Nothing       'Noeud de départ du TreeView de résultat.
        Dim pNodeRechercheDepart As TreeNode = Nothing      'Noeud de départ du TreeView de recherche.
        Dim pDictAttributs As Dictionary(Of String, String) 'Dictionnaire contenant les éléments à rechercher.

        Try
            'Vérifier la présence de noeuds dans le TreeView de résultat
            If pTreeViewResultat.Nodes.Count > 0 Then
                'Vérifier si le noeud de recherche est déjà présent
                If pTreeViewResultat.Nodes.Count = 2 Then
                    'Définir l'ancien résultat
                    pNodeResultatAncien = pTreeViewResultat.Nodes.Item(1)
                End If

                'Créer un nouveau dictionaire vide
                pDictAttributs = New Dictionary(Of String, String)

                'Vérifier la présence de noeuds dans le TreeView de recheche
                If pTreeViewRecherche.Nodes.Count > 0 Then
                    'Définir le noeud de départ
                    pNodeRechercheDepart = pTreeViewRecherche.Nodes.Item(0)

                    'Définir les éléments présents dans le TreeView de recherche
                    Call DictionnaireAttributsElements(pNodeRechercheDepart, pDictAttributs)
                End If

                'Définir le noeud de départ
                pNodeResultatDepart = pTreeViewResultat.Nodes.Item(0)

                'Créer le nouvequ noeud contenant le résultat de la recherche
                pNodeResultat = pTreeViewResultat.Nodes.Add(sDescription, "Résultat de la recherche : '" & sDescription _
                                                            & "' pour le noeud : '" & pNodeResultatDepart.Tag.ToString & "=" & pNodeResultatDepart.Name & "'")
                'Définir le type de noeud
                pNodeResultat.Tag = "RESULTAT"

                'Rechercher tous les attributs d'éléments d'un TreeView à partir d'un dictionnaire d'attributs d'éléments
                Call RechercherElementsTreeViewNoeud(pNodeResultat, pNodeResultatDepart, pDictAttributs, bPresent)

                'Si un résultat est trouvé
                If pNodeResultat.Nodes.Count > 0 Then
                    'Ouvrir le noeud du résultat de la recheche
                    pNodeResultat.ExpandAll()
                End If

                'Vérifier si le noeud de recherche est déjà présent
                If pNodeResultatAncien IsNot Nothing Then
                    'Détruire le noeud contenant le résultat de la recherche
                    pTreeViewResultat.Nodes.Remove(pNodeResultatAncien)
                End If

                'Sélectionner le noeud du résultat de la recherche
                pTreeViewResultat.SelectedNode = pNodeResultat
                pTreeViewResultat.Focus()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vide la mémoire
            pNodeResultat = Nothing
            pNodeResultatAncien = Nothing
            pNodeResultatDepart = Nothing
            pNodeRechercheDepart = Nothing
            pDictAttributs = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de rechercher tous les attributs d'éléments contenus dans le TreeView qui sont présents dans le dictionnaire d'attributs d'éléments.
    '''</summary>
    '''
    '''<param name="pNodeResultat">Noeud d'un TreeView contenant le résultat de la recherche.</param>
    '''<param name="pNodeRecherche">Noeud d'un TreeView utilisé pour la recherche.</param>
    '''<param name="pDictAttributs">Dictionnaire contenant les éléments à rechercher..</param>
    '''<param name="bPresent">Indique si la recherche du texte doit être présent ou non.</param>
    ''' 
    '''<remarks>
    ''' Un nouveau noeud de recherche contenant les éléments trouvés sera créé.
    '''</remarks>
    ''' 
    Private Sub RechercherElementsTreeViewNoeud(ByRef pNodeResultat As TreeNode, ByVal pNodeRecherche As TreeNode, _
                                                ByVal pDictAttributs As Dictionary(Of String, String), Optional ByVal bPresent As Boolean = True)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud d'un TreeView utilisé pour la recherche.
        Dim pNodeTrouver As TreeNode = Nothing  'Noeud d'un TreeView trouvé.

        Try
            'Vérifier si le noeud de recherche est valide et si le texte de recherche est spécifié
            If pNodeRecherche IsNot Nothing Then
                'Traiter tous les Nodes
                For Each pNode In pNodeRecherche.Nodes
                    'Vérifier si le noeud est une geométrie ou un attribut
                    If pNode.Tag.ToString = "GEOMETRIE" Or pNode.Tag.ToString = "ATTRIBUT" Then
                        'Vérifier si le noeud contient l'attribut recherché
                        If pDictAttributs.ContainsKey(pNode.Name) = bPresent Then
                            'Ajouter le noeud trouvé
                            pNodeTrouver = pNodeResultat.Nodes.Add(pNode.Name, pNode.Parent.Parent.Text & "/" & pNode.Parent.Parent.Parent.Text & "/" & pNode.Parent.Text & "/" & pNode.Text)
                            'Définir le type de noeud
                            pNodeTrouver.Tag = "TROUVER"
                        End If

                        ''Vérifier si le noeud contient l'attribut recherché
                        'If pDictAttributs.ContainsKey(pNode.Name & "/" & pNode.Parent.Name & "/" & pNode.Parent.Parent.Parent.Name) = bPresent Then
                        '    'Ajouter le noeud trouvé
                        '    pNodeTrouver = pNodeResultat.Nodes.Add(pNode.Name & "/" & pNode.Parent.Name & "/" & pNode.Parent.Parent.Parent.Name, _
                        '                                           pNode.Parent.Parent.Text & "/" & pNode.Parent.Parent.Parent.Text & "/" & pNode.Parent.Text & "/" & pNode.Text)
                        '    'Définir le type de noeud
                        '    pNodeTrouver.Tag = "TROUVER"
                        'End If

                        'Sinon
                    Else
                        'Rechercher tous les éléments à partir d'un noeud de TreeView
                        Call RechercherElementsTreeViewNoeud(pNodeResultat, pNode, pDictAttributs, bPresent)
                    End If
                Next
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vide la mémoire
            pNode = Nothing
            pNodeTrouver = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de remplir un dictionnaire d'attributs d'éléments à partir d'un noeud de TreeView de différences ou de conflits.
    '''</summary>
    '''
    '''<param name="pNodeRecherche">Noeud d'un TreeView utilisé pour la recherche.</param>
    '''<param name="pDictAttributs">Contient le dictionnaire d'attributs pour tous les éléments d'un Noeud de TreeView.</param>
    ''' 
    '''<remarks>
    ''' Le dictionnaire contient l'attribut, le OID et la classe d'un élément.
    '''</remarks>
    ''' 
    Private Sub DictionnaireAttributsElements(ByVal pNodeRecherche As TreeNode, ByRef pDictAttributs As Dictionary(Of String, String))
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud d'un TreeView utilisé pour la recherche.

        Try
            'Vérifier si le noeud de recherche est valide
            If pNodeRecherche IsNot Nothing Then
                'Traiter tous les Nodes
                For Each pNode In pNodeRecherche.Nodes
                    'Vérifier si le noeud est une geométrie ou un attribut
                    If pNode.Tag.ToString = "GEOMETRIE" Or pNode.Tag.ToString = "ATTRIBUT" Then
                        'Ajouter l'attribut de l'élément au dictionaire
                        pDictAttributs.Add(pNode.Name, pNode.Text & "/" & pNode.Parent.Text & "/" & pNode.Parent.Parent.Parent.Text & "/" & pNode.Parent.Parent.Text)

                        'Sinon
                    Else
                        'Remplir le dictionnaire de tous les autres éléments
                        Call DictionnaireAttributsElements(pNode, pDictAttributs)
                    End If
                Next
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vide la mémoire
            pNode = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de copier tous les attributs d'éléments d'une Géodatabase source dans les éléments d'une Géodatabase de destination correspondants à partir d'un noeud de TreeView.
    '''</summary>
    '''
    '''<param name="pNodeTraiter"> Noeud d'un TreeView dans lequel l'identification d'un ou plusieurs attributs d'éléments à traiter sont présents.</param>
    '''<param name="pFeatWorkspaceA"> Interface contenant toutes les tables de la Géodatabase source.</param>
    '''<param name="pFeatWorkspaceB"> Interface contenant toutes les tables de la Géodatabase de destination.</param>
    '''<param name="pTableA"> Interface contenant les éléments de la table source.</param>
    '''<param name="pTableB"> Interface contenant les éléments de la table de destination.</param>
    '''<param name="pRowA"> Interface contenant un élément de la table source.</param>
    '''<param name="pRowB"> Interface contenant un élément de la table de destination.</param>
    ''' 
    '''<remarks>
    ''' L'état de l'élément, le nom de la table, l'identifiant de l'élément et le nom de l'attribut est présent dans le noeud du TreeView.
    ''' Si l'état de l'élément parent est DETRUIRE, l'élément d'archive sera détruit.
    ''' Si l'état de l'élément parent est AJOUTER, un nouvel élément d'archive sera créé et la valeur de l'attribut sera copiée.
    ''' Si l'état de l'élément parent est MODIFIER, la valeur de l'attribut sera copiée.
    '''</remarks>
    ''' 
    Public Sub CopierSourceDestination(ByVal pNodeTraiter As TreeNode, ByVal pFeatWorkspaceA As IFeatureWorkspace, ByVal pFeatWorkspaceB As IFeatureWorkspace,
                                       Optional ByRef pTableA As ITable = Nothing, Optional ByRef pTableB As ITable = Nothing, _
                                       Optional ByRef pRowA As IRow = Nothing, Optional ByRef pRowB As IRow = Nothing)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing     'Noeud enfant d'un autre noeud.
        Dim sValeurs As String() = Nothing  'Contient les valeurs du noeud trouvé.
        Dim sEtatElement As String = Nothing 'Contient l'état de l'élément.

        Try
            'Vérifier si le noeud de recherche est valide et si le texte de recherche est spécifié
            If pNodeTraiter IsNot Nothing Then
                'Vérifier si le noeud est une geométrie
                If pNodeTraiter.Tag.ToString = "GEOMETRIE" Then
                    'Traiter l'élément de destination selon l'état de l'élément source
                    Call TraiterElementEtatAttribut(pNodeTraiter.Parent.Parent.Name, pNodeTraiter.Parent.Parent.Parent.Name, CInt(pNodeTraiter.Parent.Name), pNodeTraiter.Name, _
                                                    pFeatWorkspaceA, pFeatWorkspaceB, pTableA, pTableB, pRowA, pRowB)

                    'Si le noeud est un attribut
                ElseIf pNodeTraiter.Tag.ToString = "ATTRIBUT" Then
                    'Traiter l'élément de destination selon l'état de l'élément source
                    Call TraiterElementEtatAttribut(pNodeTraiter.Parent.Parent.Name, pNodeTraiter.Parent.Parent.Parent.Name, CInt(pNodeTraiter.Parent.Name), pNodeTraiter.Name, _
                                                    pFeatWorkspaceA, pFeatWorkspaceB, pTableA, pTableB, pRowA, pRowB)

                    'Si le noeud est trouver
                ElseIf pNodeTraiter.Tag.ToString = "TROUVER" Then
                    'Séparer les valeurs (EtatElement/NomTable/Oid/NomAttribut)
                    sValeurs = pNodeTraiter.Name.Split(CChar("/"))
                    'Définir l'état de l'élément
                    sEtatElement = pNodeTraiter.Text.Split(CChar("/"))(0).Replace("ETAT=", "")
                    'Traiter l'élément de destination selon l'état de l'élément source
                    Call TraiterElementEtatAttribut(sEtatElement, sValeurs(2), CInt(sValeurs(1)), sValeurs(0), _
                                                    pFeatWorkspaceA, pFeatWorkspaceB, pTableA, pTableB, pRowA, pRowB)

                    'Sinon
                Else
                    'Traiter tous les noeuds du noeud à traiter
                    For Each pNode In pNodeTraiter.Nodes
                        'Traiter le noeud du noeud à traiter
                        Call CopierSourceDestination(pNode, pFeatWorkspaceA, pFeatWorkspaceB, pTableA, pTableB, pRowA, pRowB)
                    Next
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
            sValeurs = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de traiter un élément de destination selon l'état d'un élément source en utilisant l'information d'un attribut en paramètres.
    '''</summary>
    '''
    '''<param name="sEtatElement"> Contient l'état de l'élément (DETRUIRE/AJOUTER/MODIFIER).</param>
    '''<param name="sNomTable"> Contient le nom de la table.</param>
    '''<param name="iOid"> Contient l'identifiant de l'élément.</param>
    '''<param name="sNomAttribut"> Contient le nom de l'attribut de l'élément.</param>
    '''<param name="pFeatWorkspaceA"> Interface contenant toutes les tables de la Géodatabase source.</param>
    '''<param name="pFeatWorkspaceB"> Interface contenant toutes les tables de la Géodatabase de destination.</param>
    '''<param name="pTableA"> Interface contenant les éléments de la table source.</param>
    '''<param name="pTableB"> Interface contenant les éléments de la table de destination.</param>
    '''<param name="pRowA"> Interface contenant un élément de la table source.</param>
    '''<param name="pRowB"> Interface contenant un élément de la table de destination.</param>
    Private Sub TraiterElementEtatAttribut(ByVal sEtatElement As String, ByVal sNomTable As String, ByVal iOid As Integer, ByVal sNomAttribut As String, _
                                           ByVal pFeatWorkspaceA As IFeatureWorkspace, ByVal pFeatWorkspaceB As IFeatureWorkspace, _
                                           ByRef pTableA As ITable, ByRef pTableB As ITable, ByRef pRowA As IRow, ByRef pRowB As IRow)
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing  'Interface contenant l'information de la classe.
        Dim pFeatureA As IFeature = Nothing 'Interface contenant un élément de la table A.
        Dim pFeatureB As IFeature = Nothing 'Interface contenant un élément de la table B.
        Dim iPosAtt As Integer = -1         'Contient la position de l'attribut.

        Try
            'Vérifier si la table est inconnue
            If pTableB Is Nothing Then
                'Définir la table A
                pTableA = pFeatWorkspaceA.OpenTable(sNomTable)
                'Définir la table B
                pTableB = pFeatWorkspaceB.OpenTable(sNomTable)

                'Si la table est connue
            Else
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableB, IDataset)

                'Vérifier si la table est la même
                If sNomTable <> pDataset.BrowseName Then
                    'Définir la table A
                    pTableA = pFeatWorkspaceA.OpenTable(sNomTable)
                    'Définir la table B
                    pTableB = pFeatWorkspaceB.OpenTable(sNomTable)
                End If
            End If

            'Vérifier si l'état est DETRUIRE
            If sEtatElement = "DETRUIRE" Then
                'Vérifier si l'élément B n'a pas été traité
                If pRowB Is Nothing Then
                    Try
                        'Définir l'élément B
                        pRowB = pTableB.GetRow(iOid)
                        'Détruire l'élément
                        pRowB.Delete()
                    Catch ex As Exception
                        'On ne fait rien
                    End Try
                End If

                'Si l'état est AJOUTER
            ElseIf sEtatElement = "AJOUTER" Then
                'Vérifier si l'élément B n'a pas été traité
                If pRowB Is Nothing Then
                    'Définir l'élément A
                    pRowA = pTableA.GetRow(iOid)
                    'Définir l'élément B
                    pRowB = pTableB.CreateRow
                End If

                'Définir la position de l'attribut
                iPosAtt = pTableB.FindField(sNomAttribut)

                'Vérifier si l'attribut est une géométrie
                If pTableB.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                    'Interface pour traiter la géométrie
                    pFeatureA = CType(pRowA, IFeature)
                    pFeatureB = CType(pRowB, IFeature)
                    'Copier la géométrie
                    pFeatureB.Shape = pFeatureA.Shape

                    'Si l'attribut n'est pas une géométrie
                Else
                    'Copier la valeur de l'attribut
                    pRowB.Value(iPosAtt) = pRowA.Value(iPosAtt)
                End If

                'Sauver la copie
                pRowB.Store()

                'Si l'état est MODIFIER
            ElseIf sEtatElement = "MODIFIER" Then
                'Vérifier si l'élément B n'a pas été traité
                If pRowB Is Nothing Then
                    'Définir l'élément A
                    pRowA = pTableA.GetRow(iOid)
                    'Définir l'élément B
                    pRowB = pTableB.GetRow(iOid)
                End If

                'Définir la position de l'attribut
                iPosAtt = pTableB.FindField(sNomAttribut)

                'Vérifier si l'attribut est une géométrie
                If pTableB.Fields.Field(iPosAtt).Type = esriFieldType.esriFieldTypeGeometry Then
                    'Interface pour traiter la géométrie
                    pFeatureA = CType(pRowA, IFeature)
                    pFeatureB = CType(pRowB, IFeature)
                    'Copier la géométrie
                    pFeatureB.Shape = pFeatureA.Shape

                    'Si l'attribut n'est pas une géométrie
                Else
                    'Copier la valeur de l'attribut
                    pRowB.Value(iPosAtt) = pRowA.Value(iPosAtt)
                End If

                'Sauver la modification
                pRowB.Store()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pFeatureA = Nothing
            pFeatureB = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions pour identifier les conflits dans un TreeView"
    '''<summary>
    ''' Routine qui permet d'identifier les conflits dans un TreeView entre la Géodatabase parent (.sde) et l'archive interne ou externe de la Géodatabase enfant (.mdb ou .gdb).
    '''</summary>
    '''
    '''<param name="treConflits"> TreeView dans lequel les conflits seront identifiées.</param>
    '''<param name="bExterne">Indique si l'archive externe est utilisée pour identifier les conflits.</param>
    ''' 
    '''<remarks>
    ''' Par défaut, les conflits seront identifiées à partir de l'information du réplica de la Géodatabase enfant dans laquelle l'archive interne est présente.
    ''' La Géodatabase d'archive externe correspond à la copie initiale de la Géodatabase enfant.
    '''</remarks>
    ''' 
    Public Sub IdentifierConflits(ByRef treConflits As TreeView, Optional bExterne As Boolean = False)
        'Déclarer les variables de travail
        Dim pEditor As IEditor = Nothing    'Interface qui permet de vérifier et sauver les modification.
        Dim pUID As New UID                 'Interface contenant l'identifiant d'une classe.

        Try
            'Définir l'identifiant de la classe d'édition
            pUID.Value = "esriEditor.Editor"
            'Interface pour vérifier et sauver les modifications
            pEditor = CType(m_Application.FindExtensionByCLSID(pUID), IEditor)
            'vérifier la présence de modifications
            If pEditor.HasEdits Then
                'Fermer et sauver les modifications
                pEditor.StopEditing(True)
            End If

            'Initialiser le compteur
            giNbConflits = -1

            'Vérifier si les conflits sont identifier à partir de l'archive externe
            If bExterne Then
                'Identifier tous les conflits entre la Géodatabase parent et l'archive externe de la Géodatabase enfant
                Call IdentifierConflitsArchiveExterne(treConflits)

                'Si les conflits sont identifiés à partir de l'archive interne
            Else
                'Identifier les conflits entre la Géodatabase parent et l'archive interne de la Géodatabase enfant
                Call IdentifierConflitsArchiveInterne(treConflits)
            End If

            'Donner le focus au TreeView
            treConflits.Focus()

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pEditor = Nothing
            pUID = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les conflits dans un TreeView entre la Géodatabase parent (.sde) et l'archive externe de la Géodatabase enfant (.mdb ou .gdb).
    '''</summary>
    '''
    '''<param name="treConflits">TreeView dans lequel les conflits seront identifiées.</param>
    ''' 
    '''<remarks>L'archive des données est externe à la Géodatabase enfant. Elle est donc présente dans une autre Géodatabase .mdb ou .gdb.</remarks>
    ''' 
    Private Sub IdentifierConflitsArchiveExterne(ByRef treConflits As TreeView)
        'Déclarer les variables de travail
        Dim pNodeReplica As TreeNode = Nothing                      'Noeud du TreeView pour un réplica.
        Dim pParentFeatureWorkspace As IFeatureWorkspace = Nothing  'Interface pour ouvrir la table parent.
        Dim pArchiveFeatureWorkspace As IFeatureWorkspace = Nothing 'Interface pour ouvrir la table d'archive.
        Dim pEnfantFeatureWorkspace As IFeatureWorkspace = Nothing  'Interface pour ouvrir la table enfant.
        Dim pRepFilterDesc As IReplicaFilterDescription = Nothing   'Interface pour modifier la méthode d'extraction du checkOut.
        Dim pDatasetName As IDatasetName = Nothing                  'Interface contenant un Dataset d'un réplica.
        Dim pTableParent As ITable = Nothing                        'Interface contenant la table de la Géodatabase parent.
        Dim pTableArchive As ITable = Nothing                       'Interface contenant la table de la Géodatabase d'archive.
        Dim pTableEnfant As ITable = Nothing                        'Interface contenant la table de la Géodatabase enfant.
        Dim dDateDebut As DateTime = Nothing                        'Contient la date de début du traitement.
        Dim sTempsTraitement As String = ""                         'Temps de traitement.
        Dim sNomClasse As String = ""                               'Contient le nom de la classe à traiter.

        Try
            'Débuter les ajouts dans le treeview
            treConflits.BeginUpdate()

            'Initialiser le TreeView des conflits
            treConflits.Nodes.Clear()

            'Vérifier si la Géodatabase parent est présente
            If gpGdbParent IsNot Nothing Then
                'Vérifier si la description du réplica enfant est présente
                If gpReplicaEnfant IsNot Nothing Then
                    'Définir la date de début
                    dDateDebut = System.DateTime.Now

                    'Afficher le nom du réplica
                    pNodeReplica = treConflits.Nodes.Add(gpReplicaEnfant.Name, "REPLICA=" & gpReplicaEnfant.Name _
                                                         & ", GdbParent=" & gpGdbParent.ConnectionProperties.GetProperty("Instance").ToString.ToUpper _
                                                         & ", GdbArchive=" & gpGdbArchive.PathName & ":<ArchiveExterne>" & ", GdbEnfant=" & gpGdbEnfant.PathName)
                    'Définir le type de noeud
                    pNodeReplica.Tag = "REPLICA"

                    'Interface pour extraire les tables de la Géodatabase parent
                    pParentFeatureWorkspace = CType(gpGdbParent, IFeatureWorkspace)

                    'Interface pour extraire les tables de la Géodatabase d'archive
                    pArchiveFeatureWorkspace = CType(gpGdbArchive, IFeatureWorkspace)

                    'Interface pour extraire les tables de la Géodatabase enfant
                    pEnfantFeatureWorkspace = CType(gpGdbEnfant, IFeatureWorkspace)

                    'Interface pour modifier la méthode d'extraction du checkOut
                    pRepFilterDesc = CType(gpReplicaEnfant.Description, IReplicaFilterDescription)

                    'Traiter toutes les tables
                    For i = 0 To gpReplicaEnfant.Description.TableNameCount - 1
                        'Interface pour extraire le nom de la classe
                        pDatasetName = CType(gpReplicaEnfant.Description.TableName(i), IDatasetName)

                        'Définir le nom de la classe
                        sNomClasse = pDatasetName.Name.Replace(gpReplicaParent.Owner & ".", "")

                        'Afficher le nom de la classe traitée
                        If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = sNomClasse & " ..."

                        'Définir la table de la Géodatabase parent
                        pTableParent = pParentFeatureWorkspace.OpenTable(sNomClasse)
                        'Définir la table de sélection de la Géodatabase parent
                        pTableParent = Table2TableSelection(pTableParent, pRepFilterDesc, i)

                        'Définir la table de la Géodatabase d'archive
                        pTableArchive = pArchiveFeatureWorkspace.OpenTable(sNomClasse)
                        'Définir la table de sélection de la Géodatabase d'archive
                        pTableArchive = Table2TableSelection(pTableArchive, pRepFilterDesc, i)

                        'Définir la table de la Géodatabase enfant
                        pTableEnfant = pEnfantFeatureWorkspace.OpenTable(sNomClasse)

                        'Traiter tous les conflits d'un Dataset de réplica CheckOut
                        Call IdentifierConflitsArchiveExterneDataset(pTableParent, pTableArchive, pTableEnfant, pNodeReplica)
                    Next

                    'Trier les conflits
                    treConflits.Sort()

                    'Ouvrir le noeud du réplica
                    'pNodeReplica.ExpandAll()
                    pNodeReplica.Expand()

                    'Définir le nombre de conflits trouvés
                    giNbConflits = CalculerDifferences(pNodeReplica)

                    'Sélectionner le noeud du réplica
                    treConflits.SelectedNode = pNodeReplica

                    'Définir le temps d'exécution
                    sTempsTraitement = System.DateTime.Now.Subtract(dDateDebut).Add(New TimeSpan(5000000)).ToString.Substring(0, 8)
                    'Afficher la fin et le temps du traitement
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement (Temps d'exécution: " & sTempsTraitement & ") !"

                Else
                    'Retourner une erreur
                    Throw New AnnulerExecutionException("ERREUR : La description du réplica de la Géodatabase enfant est absente !")
                End If

            Else
                'Retourner une erreur
                Throw New AnnulerExecutionException("ERREUR : La Géodatabase parent est absente !")
            End If

            'Terminer les ajouts dans le treeview
            treConflits.EndUpdate()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeReplica = Nothing
            pParentFeatureWorkspace = Nothing
            pArchiveFeatureWorkspace = Nothing
            pEnfantFeatureWorkspace = Nothing
            pRepFilterDesc = Nothing
            pDatasetName = Nothing
            pTableParent = Nothing
            pTableArchive = Nothing
            pTableEnfant = Nothing
            dDateDebut = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les conflits dans un TreerView entre une table d'une Géodatabase parent et une table d'une Géodatabase d'archive externe.
    ''' L'archive des données est externe à la Géodatabase enfant. Elle est donc présente dans une autre Géodatabase .mdb ou .gdb.
    '''</summary>
    ''' 
    '''<param name="pTableParent">Interface contenant la table de la Géodatabase enfant.</param>
    '''<param name="pTableArchive">Interface contenant la table de la Géodatabase d'archive.</param>
    '''<param name="pTableEnfant">Interface contenant la table de la Géodatabase enfant.</param>
    '''<param name="pNodeReplica">Noeud d'un Treeview contenant l'inforemation du réplica.</param>
    '''
    Private Sub IdentifierConflitsArchiveExterneDataset(ByVal pTableParent As ITable, ByVal pTableArchive As ITable, ByVal pTableEnfant As ITable, ByRef pNodeReplica As TreeNode)
        'Déclarer les variables de travail
        Dim pArchiveFeatDict As Dictionary(Of Integer, IRow) = Nothing  'Interface contenant les éléments de la table d'archive à traiter.
        Dim pDataset As IDataset = Nothing                              'Interface qui permet d'extraire le nom de la table.
        Dim pNodeClasse As TreeNode = Nothing                           'Noeud du TreeView pour une classe.
        Dim pNodeAjouter As TreeNode = Nothing                          'Noeud du TreeView pour tous les éléments ajoutés d'une classe.
        Dim pNodeDetruire As TreeNode = Nothing                         'Noeud du TreeView pour tous les éléments détruits d'une classe.
        Dim pNodeModifier As TreeNode = Nothing                         'Noeud du TreeView pour tous les éléments modifiés d'une classe.
        Dim pTableSelection As ITableSelection = Nothing                'Interface pour extraire les éléments sélectionnés.
        Dim pCursor As ICursor = Nothing                                'Interface utilisé pour lire les éléments.
        Dim pRowParent As IRow = Nothing                                'Interface contenant l'élément parent.
        Dim pRowArchive As IRow = Nothing                               'Interface contenant l'élément d'archive.
        Dim iOid As Integer = Nothing                                   'Contient la valeur du lien.

        Try
            'Interface pour extraire le nom de la table
            pDataset = CType(pTableArchive, IDataset)

            'Afficher le nom de la classe modifiée
            pNodeClasse = pNodeReplica.Nodes.Add(pDataset.BrowseName, "CLASSE=" & pDataset.BrowseName)
            'Définir le type de noeud
            pNodeClasse.Tag = "CLASSE"

            'Initialiser les noeuds de la classe
            pNodeAjouter = Nothing
            pNodeDetruire = Nothing
            pNodeModifier = Nothing

            'Lire les éléments de la table d'archive 
            pArchiveFeatDict = LireElementsDict(pTableArchive)

            'Interface pour extraire les éléments sélectionnés de la table enfant
            pTableSelection = CType(pTableParent, ITableSelection)

            'Interfaces pour extraire les éléments sélectionnés
            pTableSelection.SelectionSet.Search(Nothing, False, pCursor)

            'Extraire le premier élément
            pRowParent = pCursor.NextRow

            'Traiter tous les éléments sélectionnés du FeatureLayer
            Do Until pRowParent Is Nothing
                'Vérifier si le lien est présent dans les éléments de la table d'archive
                If pArchiveFeatDict.ContainsKey(pRowParent.OID) Then
                    'Définir l'élément d'archive
                    pRowArchive = pArchiveFeatDict.Item(pRowParent.OID)

                    'Retirer l'élément du dictionaire d'Archive
                    pArchiveFeatDict.Remove(pRowParent.OID)

                    'Si le lien est absent dans les éléments de la table d'archive
                Else
                    'Aucun élément d'archive
                    pRowArchive = Nothing
                End If

                'Identifier les conflits entre l'élément de la table parent et l'élément de la table d'archive
                ConflitsElementNoeud(pRowParent, pRowArchive, pTableEnfant, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)

                'Extraire le prochain élément à traiter
                pRowParent = pCursor.NextRow
            Loop

            'Traiter tous les éléments restants du dictionnaire de la table d'archive
            For Each iOid In pArchiveFeatDict.Keys
                'Définir l'élément d'archive
                pRowArchive = pArchiveFeatDict.Item(iOid)

                'Identifier les différences entre l'élément de la table parent et l'élément de la table d'archive
                ConflitsElementNoeud(Nothing, pRowArchive, pTableEnfant, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)
            Next

            'Ouvrir le noeud
            pNodeClasse.Expand()

            'Vérifier si aucune différences dans le noeud de la classe
            If pNodeClasse.Nodes.Count = 0 Then pNodeClasse.Remove()

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pArchiveFeatDict = Nothing
            pDataset = Nothing
            pNodeClasse = Nothing
            pNodeAjouter = Nothing
            pNodeDetruire = Nothing
            pNodeModifier = Nothing
            pTableSelection = Nothing
            pCursor = Nothing
            pRowParent = Nothing
            pRowArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet d'extraire le SelectionSet correspondant au réplica du dataset à traiter.
    '''</summary>
    '''
    '''<param name="pGeodatabase">Interface contenant la Géodatabase.</param>
    '''<param name="pTable">Interface contenant la table.</param>
    '''<param name="pRepFilterDesc">Interface contenant un Dataset d'un réplica.</param>
    '''<param name="pReplicaDataset">Interface contenant un Dataset d'un réplica.</param>
    '''<param name="iIndexDataset">Contient le numéro d'indexe du Dataset.</param>
    ''' 
    '''<remarks>Si aucun réplica n'est présent dans la géodatabase enfant, une erreur de traitement sera retournée.</remarks>
    ''' 
    Private Function ReplicaTable2SelectionSet(ByVal pGeodatabase As IWorkspace, ByVal pTable As ITable, ByVal pRepFilterDesc As IReplicaFilterDescription, _
                                              ByVal pReplicaDataset As IReplicaDataset2, ByVal iIndexDataset As Integer) As ISelectionSet
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing                          'Interface pour extraire le nom de la Géodatabase.
        Dim pParentLayer As ITable = Nothing                        'Interface utilisé pour extraire la sélection d'une FeatureClass ou une Table.
        Dim pFeatureLayer As IFeatureLayer = Nothing                'Interface utilisé pour extraire la sélection d'une FeatureClass.
        Dim pStandaloneTable As IStandaloneTable = Nothing          'Interface utilisé pour extraire la sélection d'une Table.
        Dim pQueryfilter As IQueryFilter = Nothing                  'Interface contenant une requête attributive.
        Dim pSpatialfilter As ISpatialFilter = Nothing              'Interface contenant une requête spatiale et attributive.
        Dim pSelectionSet As ISelectionSet = Nothing                'Interface contenant une sélection d'éléments à traiter.

        'Par défaut le SelectionSet est invalide
        ReplicaTable2SelectionSet = Nothing

        Try
            'Interface pour vérifier le type de table
            pDataset = CType(pTable, IDataset)

            'Si la table est une Featureclass
            If pDataset.Type = esriDatasetType.esriDTFeatureClass Then
                'Creer un nouveau FeatureLayer vide pour extraire la sélection
                pFeatureLayer = New FeatureLayer
                'Définir la classe du FeatureLayer
                pFeatureLayer.FeatureClass = CType(pTable, IFeatureClass)
                'Interface pour extraire la sélection
                pParentLayer = CType(pFeatureLayer, ITable)

                'Si la table est une Table
            ElseIf pDataset.Type = esriDatasetType.esriDTTable Then
                'Creer un nouveau StandaloneTable vide pour extraire la sélection
                pStandaloneTable = New StandaloneTable
                'Définir la table du StandaloneTable
                pStandaloneTable.Table = CType(pTable, ITable)
                'Interface pour extraire la sélection
                pParentLayer = CType(pStandaloneTable, ITable)

            Else
                'Retourner un message d'erreur
                Throw New Exception("ERREUR : La table n'est par un type valide.")
            End If

            'Vérifier si un filtre a été effectué sur la table parent
            If pRepFilterDesc.RowsType(iIndexDataset) = esriRowsType.esriRowsTypeFilter Then
                'Vérifier si une sélection a été effectué sur la table parent
                If pRepFilterDesc.TableUsesSelection(iIndexDataset) = True Then
                    'Définir les éléments sélectionnés
                    pSelectionSet = pRepFilterDesc.TableSelection(iIndexDataset)

                    'Si une requête spatiale a été effectué sur la table parent
                ElseIf pRepFilterDesc.TableUsesQueryGeometry(iIndexDataset) = True Then
                    'Créer un nouveau filtre spatiale
                    pSpatialfilter = New SpatialFilter
                    'Définir la relation spatiale
                    pSpatialfilter.SpatialRel = pRepFilterDesc.SpatialRelation
                    'Définir la géométrie de la relation spatiale
                    pSpatialfilter.Geometry = pRepFilterDesc.Geometry
                    'Définir la requête attributive
                    pSpatialfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                    'Extraire les éléments sélectionnés selon la requête attributive et spatiale
                    pSelectionSet = pParentLayer.Select(pSpatialfilter, esriSelectionType.esriSelectionTypeIDSet, _
                                                        esriSelectionOption.esriSelectionOptionNormal, pGeodatabase)

                    'Si une requête attributive a été effectué sur la table parent
                ElseIf pRepFilterDesc.TableUsesDefQuery(iIndexDataset) = True Then
                    'Créer un nouveau filtre spatiale
                    pQueryfilter = New QueryFilter
                    'Définir la requête attributive
                    pQueryfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                    'Extraire les éléments sélectionnés selon la requête attributive et spatiale
                    pSelectionSet = pParentLayer.Select(pQueryfilter, esriSelectionType.esriSelectionTypeIDSet, _
                                                        esriSelectionOption.esriSelectionOptionNormal, pGeodatabase)

                    'Si toute la table doit être sélectionnée
                Else
                    'Extraire les éléments sélectionnés selon la requête attributive et spatiale
                    pSelectionSet = pParentLayer.Select(Nothing, esriSelectionType.esriSelectionTypeIDSet, _
                                                        esriSelectionOption.esriSelectionOptionNormal, pGeodatabase)
                End If

                'Si toute la table doit être sélectionnée
            Else
                'Extraire les éléments sélectionnés selon la requête attributive et spatiale
                pSelectionSet = pParentLayer.Select(Nothing, esriSelectionType.esriSelectionTypeIDSet, _
                                                    esriSelectionOption.esriSelectionOptionNormal, pGeodatabase)
            End If

            'Retourner la sélection de la table
            ReplicaTable2SelectionSet = pSelectionSet

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pParentLayer = Nothing
            pFeatureLayer = Nothing
            pStandaloneTable = Nothing
            pQueryfilter = Nothing
            pSpatialfilter = Nothing
            pSelectionSet = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'identifier les conflits dans un TreeView entre la Géodatabase parent (.sde) et l'archive interne de la Géodatabase enfant (.mdb ou .gdb).
    ''' L'archive est présente directement dans la Géodatabase enfant (.mdb ou .gdb) via l'information d'un réplica de type checkOut.
    '''</summary>
    '''
    '''<param name="treConflits">TreeView dans lequel les conflits seront identifiés.</param>
    ''' 
    '''<remarks>Si aucun réplica n'est présent dans la géodatabase enfant, une erreur de traitement sera retournée.</remarks>
    ''' 
    Private Sub IdentifierConflitsArchiveInterne(ByRef treConflits As TreeView)
        'Déclarer les variables de travail
        Dim pNodeReplica As TreeNode = Nothing                          'Noeud du TreeView pour un réplica.
        Dim pNodeClasse As TreeNode = Nothing                           'Noeud du TreeView pour une classe.
        Dim pNodeAjouter As TreeNode = Nothing                          'Noeud du TreeView pour tous les éléments ajoutés d'une classe.
        Dim pNodeDetruire As TreeNode = Nothing                         'Noeud du TreeView pour tous les éléments détruits d'une classe.
        Dim pNodeModifier As TreeNode = Nothing                         'Noeud du TreeView pour tous les éléments modifiés d'une classe.
        Dim pEnumModifiedClassInfo As IEnumModifiedClassInfo = Nothing  'Interface contenant les classes modifiées.
        Dim pModifiedClassInfo As IModifiedClassInfo = Nothing          'Interface contenant une classe modifiée.
        Dim pParentGdb As IWorkspace = Nothing                          'Interface contenant la Géodatabase Parent.
        Dim pPropertySet As IPropertySet = Nothing                      'Interface contenant l'instance de connexion à la Géodatabase Parent.
        Dim pParentFeatureWorkspace As IFeatureWorkspace = Nothing      'Interface pour ouvrir la table parent.
        Dim pParentTable As ITable = Nothing                            'Interface contenant les éléments de la table parent.
        Dim pEnfantFeatureWorkspace As IFeatureWorkspace = Nothing      'Interface pour ouvrir la table enfant.
        Dim pEnfantTable As ITable = Nothing                            'Interface contenant les éléments de la table enfant.
        Dim pName As IName = Nothing                                    'Interface qui permet d'ouvrir la Géodatabase Parent.
        Dim pFidSet As IFIDSet = Nothing                                'Interface contenant les OIDs à traiter.

        Try
            'Débuter les ajouts dans le treeview
            treConflits.BeginUpdate()

            'Initialiser le TreeView des conflits
            treConflits.Nodes.Clear()

            'Vérifier si l'archive interne est présente
            If gpDataChanges IsNot Nothing Then
                'Interface pour extraire l'instance de la GDB parent
                pPropertySet = CType(gpDataChanges.ParentWorkspaceName.ConnectionProperties, IPropertySet)

                'Interface pour ouvrir la Géodatabase Parent
                pName = CType(gpDataChanges.ParentWorkspaceName, IName)

                'Définir la Géodatabase Parent
                pParentGdb = CType(pName.Open(), IWorkspace)

                'Afficher le nom du réplica
                pNodeReplica = treConflits.Nodes.Add(gpReplicaEnfant.Name, "REPLICA=" & gpReplicaEnfant.Name _
                                                     & ", GdbParent=" & pPropertySet.GetProperty("Instance").ToString _
                                                     & ", GdbArchive=" & gpGdbEnfant.PathName & ":<ArchiveInterne>" & ", GdbEnfant=" & gpGdbEnfant.PathName)
                'Définir le type de noeud
                pNodeReplica.Tag = "REPLICA"

                'Interface pour extraire les tables de la Géodatabase parent
                pParentFeatureWorkspace = CType(pParentGdb, IFeatureWorkspace)

                'Interface pour extraire les tables de la Géodatabase enfant
                pEnfantFeatureWorkspace = CType(gpGdbEnfant, IFeatureWorkspace)

                'Interface contenant les classes modifiées
                pEnumModifiedClassInfo = gpDataChanges.GetModifiedClassesInfo

                'Extraire la première classe modifiée.
                pModifiedClassInfo = pEnumModifiedClassInfo.Next

                'Traiter toutes les classes modifiées
                Do Until pModifiedClassInfo Is Nothing
                    'Afficher le nom de la classe modifiée
                    pNodeClasse = pNodeReplica.Nodes.Add(pModifiedClassInfo.ChildClassName, "CLASSE=" & pModifiedClassInfo.ChildClassName)
                    'Définir le type de noeud
                    pNodeClasse.Tag = "CLASSE"

                    'Initialiser les noeuds de la classe
                    pNodeAjouter = Nothing
                    pNodeDetruire = Nothing
                    pNodeModifier = Nothing

                    'Définir la classe de la Géodatabase Parent
                    pParentTable = pParentFeatureWorkspace.OpenTable(pModifiedClassInfo.ParentClassName)

                    'Définir la classe de la Géodatabase enfant
                    pEnfantTable = pEnfantFeatureWorkspace.OpenTable(pModifiedClassInfo.ParentClassName)

                    'Interface contenant les OIDs des éléments détruits à traiter
                    pFidSet = DataChangesOids(gpDataChanges, pModifiedClassInfo.ChildClassName, esriDataChangeType.esriDataChangeTypeDelete)

                    'Afficher les conflits entre les éléments Parent et Enfant-Archive pour les OIDs des éléments détruits
                    Call ConflitsElementsArchive(pFidSet, gpDataChanges, pModifiedClassInfo.ChildClassName, pParentTable, pEnfantTable, _
                                                 pNodeReplica, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)

                    'Interface contenant les OIDs des éléments modifiés à traiter
                    pFidSet = DataChangesOids(gpDataChanges, pModifiedClassInfo.ChildClassName, esriDataChangeType.esriDataChangeTypeUpdate)

                    'Afficher les conflits entre les éléments Parent et Enfant-Archive pour les OIDs des éléments modifiés
                    Call ConflitsElementsArchive(pFidSet, gpDataChanges, pModifiedClassInfo.ChildClassName, pParentTable, pEnfantTable, _
                                                 pNodeReplica, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)

                    'Ouvrir le noeud
                    pNodeClasse.Expand()

                    'Extraire la prochaine classe modifiée.
                    pModifiedClassInfo = pEnumModifiedClassInfo.Next
                Loop

                'Trier les conflits
                treConflits.Sort()

                'Ouvrir le noeud
                'pNodeReplica.ExpandAll()
                pNodeReplica.Expand()

                'Définir le nombre de conflits trouvés
                giNbConflits = CalculerDifferences(pNodeReplica)

                'Sélectionner le noeud du réplica
                treConflits.SelectedNode = pNodeReplica

                'Si l'archive interne est absente
            Else
                'Retourner l'erreur
                Throw New AnnulerExecutionException("ERREUR : L'archive interne est absente !")
            End If

            'Terminer les ajouts dans le treeview
            treConflits.EndUpdate()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeReplica = Nothing
            pNodeClasse = Nothing
            pNodeAjouter = Nothing
            pNodeDetruire = Nothing
            pNodeModifier = Nothing
            pEnumModifiedClassInfo = Nothing
            pModifiedClassInfo = Nothing
            pParentGdb = Nothing
            pPropertySet = Nothing
            pParentFeatureWorkspace = Nothing
            pParentTable = Nothing
            pName = Nothing
            pFidSet = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les conflits d'attributs dans un noeud de TreeView pour un ensemble de OID d'éléments Parent/Enfant-Archive.
    ''' L'archive est présente directement dans la Géodatabase enfant (.mdb ou .gdb) via l'information d'un réplica de type checkOut.
    '''</summary>
    '''
    '''<param name="pFidSet">Interface contenant l'ensemble des OIDs à traiter.</param>
    '''<param name="pDataChanges">Interface contenant les changements.</param>
    '''<param name="sNomClasse">Nom de la classe à traiter.</param>
    '''<param name="pTableParent">Interface contenant tous les éléments de la table parent.</param>
    '''<param name="pTableEnfant">Interface contenant tous les éléments de la table enfant.</param>
    '''<param name="pNodeReplica">Noeud du TreeView pour un Réplica de Géodatabase.</param>
    '''<param name="pNodeClasse">Noeud du TreeView pour une classe.</param>
    '''<param name="pNodeAjouter">Noeud du TreeView pour tous les éléments ajouter d'une classe.</param>
    '''<param name="pNodeDetruire">Noeud du TreeView pour tous les éléments détruits d'une classe.</param>
    '''<param name="pNodeModifier">Noeud du TreeView pour tous les éléments modifiés d'une classe.</param>
    ''' 
    Private Sub ConflitsElementsArchive(ByVal pFidSet As IFIDSet, ByVal pDataChanges As IDataChanges, ByVal sNomClasse As String, _
                                        ByVal pTableParent As ITable, ByVal pTableEnfant As ITable, _
                                        ByRef pNodeReplica As TreeNode, ByRef pNodeClasse As TreeNode, _
                                        ByRef pNodeAjouter As TreeNode, ByRef pNodeDetruire As TreeNode, ByRef pNodeModifier As TreeNode)
        'Déclarer les variables de travail
        Dim pDataChangesExt As IDataChangesExt = Nothing    'Interface qui permet d'extraire les éléments originaux.
        Dim pCursorArchive As ICursor = Nothing             'Interface contenant les éléments d'archive à extraire.
        Dim pRowParent As IRow = Nothing                    'Interface contenant un élément de la table Parent.
        Dim pRowArchive As IRow = Nothing                   'Interface contenant un élément de la table Enfant-Archive.

        Try
            'Vérifier si des OIDs sont présents
            If pFidSet.Count > 0 Then
                'Interface pour extraire les éléments Enfant-Archive
                pDataChangesExt = CType(pDataChanges, IDataChangesExt)

                'Extraire les éléments Enfant-Archive
                pCursorArchive = pDataChangesExt.ExtractOriginalRows(sNomClasse, pFidSet)

                'Extraire le premier élément Enfant-Archive
                pRowArchive = pCursorArchive.NextRow()

                'Traiter tous les éléments Enfant-Archive
                Do Until pRowArchive Is Nothing
                    'Définir l'élément de la géodatabase parent
                    pRowParent = pTableParent.GetRow(pRowArchive.OID)

                    'Remplir les noeuds de TreeView contenant les conflits entre les éléments Parent/Enfant-Archive
                    Call ConflitsElementNoeud(pRowParent, pRowArchive, pTableEnfant, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)

                    'Extraire le prochain élément Enfant-Archive
                    pRowArchive = pCursorArchive.NextRow()
                Loop
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pDataChangesExt = Nothing
            pCursorArchive = Nothing
            pFidSet = Nothing
            pRowParent = Nothing
            pRowArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les conflits d'attributs dans un noeud de TreeView pour un ensemble de OID d'éléments Parent/Enfant.
    '''</summary>
    '''
    '''<param name="pFidSet">Interface contenant l'ensemble des OIDs à traiter.</param>
    '''<param name="pTableParent">Interface contenant la table des éléments Parent.</param>
    '''<param name="pTableEnfant">Interface contenant la table des éléments Enfant.</param>
    '''<param name="pNodeReplica">Noeud du TreeView pour un Réplica de Géodatabase .</param>
    '''<param name="pNodeClasse">Noeud du TreeView pour une classe.</param>
    '''<param name="pNodeAjouter">Noeud du TreeView pour tous les éléments ajoutés d'une classe.</param>
    '''<param name="pNodeDetruire">Noeud du TreeView pour tous les éléments détruits d'une classe.</param>
    '''<param name="pNodeModifier">Noeud du TreeView pour tous les éléments modifiés d'une classe.</param>
    ''' 
    Private Sub ConflitsElementsCourant(ByVal pFidSet As IFIDSet, ByVal pTableParent As ITable, ByVal pTableEnfant As ITable, ByRef pNodeReplica As TreeNode, _
                                        ByRef pNodeClasse As TreeNode, ByRef pNodeAjouter As TreeNode, ByRef pNodeDetruire As TreeNode, ByRef pNodeModifier As TreeNode)
        'Déclarer les variables de travail
        Dim pRowParent As IRow = Nothing                    'Interface contenant un élément de la table Parent.
        Dim pRowEnfant As IRow = Nothing                    'Interface contenant un élément de la table Enfant.
        Dim iOid As Integer = -1

        Try
            'Vérifier si des OIDs sont présents
            If pFidSet.Count > 0 Then
                'Initialiser l'extraction des OIDs
                pFidSet.Reset()

                'Extraire le premier OID à traiter
                pFidSet.Next(iOid)

                'Traiter tous les éléments
                Do Until iOid = -1
                    'Définir l'élément de la géodatabase parent
                    pRowParent = pTableParent.GetRow(iOid)

                    Try
                        'Définir l'élément de la géodatabase parent
                        pRowEnfant = pTableEnfant.GetRow(iOid)

                    Catch ex As Exception
                        'On ne fait rien
                        pRowEnfant = Nothing
                    End Try

                    'Remplir les noeuds de TreeView contenant les conflits entre les éléments Parent/Enfant
                    Call ConflitsElementNoeud(pRowParent, pRowEnfant, pTableEnfant, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)
                Loop
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pRowParent = Nothing
            pRowEnfant = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les conflits d'attributs dans un noeud de TreeView entre deux éléments Parent/Archive.
    '''</summary>
    '''
    '''<param name="pRowParent">Interface contenant un élément de la table parent.</param>
    '''<param name="pRowArchive">Interface contenant un élément de la table d'archive.</param>
    '''<param name="pTableEnfant">Interface contenant tous les éléments de la table enfant.</param>
    '''<param name="pNodeClasse">Noeud d'un TreeView pour tous les éléments d'une classe.</param>
    '''<param name="pNodeAjouter">Noeud du TreeView pour les éléments ajoutés d'une classe.</param>
    '''<param name="pNodeDetruire">Noeud du TreeView pour les éléments détruits d'une classe.</param>
    '''<param name="pNodeModifier">Noeud du TreeView pour les éléments modifiés d'une classe.</param>
    ''' 
    Private Sub ConflitsElementNoeud(ByVal pRowParent As IRow, ByVal pRowArchive As IRow, ByVal pTableEnfant As ITable, _
                                     ByRef pNodeClasse As TreeNode, ByRef pNodeAjouter As TreeNode, ByRef pNodeDetruire As TreeNode, ByRef pNodeModifier As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeElement As TreeNode = Nothing              'Objet contenant un noeud du TreeView pour un élément.
        Dim pNodeAttribut As TreeNode = Nothing             'Objet contenant un noeud du TreeView pour un attribut d'élément.
        Dim pFeatureParent As IFeature = Nothing            'Interface contenant la géométrie d'un élément de la table parent.
        Dim pFeatureArchive As IFeature = Nothing           'Interface contenant la géométrie d'un élément de la table d'archive.
        Dim pFeatureEnfant As IFeature = Nothing            'Interface contenant la géométrie d'un élément de la table enfant.
        Dim pRowEnfant As IRow = Nothing                    'Interface contenant la géométrie d'un élément de la table enfant.
        Dim pField As IField = Nothing                      'Interface contenant un attribut d'élément.
        Dim iOid As Integer = 0                             'Compteur

        Try
            'Vérifier si l'élément est absent de la table d'archive
            If pRowArchive Is Nothing Then
                'Si le noeud ajouter est absent
                If pNodeAjouter Is Nothing Then
                    'Créer le noeud contenant les éléments ajoutés
                    pNodeAjouter = pNodeClasse.Nodes.Add("AJOUTER", "ETAT=AJOUTER")
                    'Définir le type de noeud
                    pNodeAjouter.Tag = "ETAT"
                End If

                'Afficher l'information de l'élément
                pNodeElement = pNodeAjouter.Nodes.Add(pRowParent.OID.ToString, "OBJECTID=" & pRowParent.OID.ToString)
                'Définir le type de noeud
                pNodeElement.Tag = "ELEMENT"

                'Vérifier tous les attributs
                For i = 0 To pRowParent.Fields.FieldCount - 1
                    'Interface contenant un attribut d'élément
                    pField = pRowParent.Fields.Field(i)

                    'Vérifier si l'attribut est modifiable
                    If pField.Editable = True Then
                        'Vérifier si l'attribut est une géométrie
                        If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour extraire la Géométrie
                            pFeatureParent = CType(pRowParent, IFeature)
                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pFeatureParent.Shape.GeometryType.ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "GEOMETRIE"

                            'Si l'attribut n'est pas une géométrie
                        Else
                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pRowParent.Value(i).ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "ATTRIBUT"
                        End If
                    End If
                Next

                'Vérifier si l'élément est absent de la table parent
            ElseIf pRowParent Is Nothing Then
                Try
                    'Définir l'élément enfant
                    pRowEnfant = pTableEnfant.GetRow(pRowArchive.OID)
                Catch ex As Exception
                    'Aucun élément enfant
                    pRowEnfant = Nothing
                End Try

                'Vérifier si l'élément est absent aussi dans l'enfant
                If pRowEnfant IsNot Nothing Then
                    'Si le noeud detruire est absent
                    If pNodeDetruire Is Nothing Then
                        'Créer le noeud contenant les éléments détruits
                        pNodeDetruire = pNodeClasse.Nodes.Add("DETRUIRE", "ETAT=DETRUIRE")
                        'Définir le type de noeud
                        pNodeDetruire.Tag = "ETAT"
                    End If

                    'Afficher l'information de l'élément
                    pNodeElement = pNodeDetruire.Nodes.Add(pRowArchive.OID.ToString, "OBJECTID=" & pRowArchive.OID.ToString)
                    'Définir le type de noeud
                    pNodeElement.Tag = "ELEMENT"

                    'Vérifier tous les attributs
                    For i = 0 To pRowArchive.Fields.FieldCount - 1
                        'Interface contenant un attribut d'élément
                        pField = pRowArchive.Fields.Field(i)

                        'Vérifier si l'attribut est modifiable
                        If pField.Editable = True Then
                            'Vérifier si l'attribut est une géométrie
                            If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                'Interface pour extraire la Géométrie
                                pFeatureArchive = CType(pRowArchive, IFeature)
                                'Ajouter un noeud pour l'attribut différent
                                pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                       pField.Name & "=" & pFeatureArchive.Shape.GeometryType.ToString)
                                'Définir le type de noeud
                                pNodeAttribut.Tag = "GEOMETRIE"

                                'Si l'attribut n'est pas une géométrie
                            Else
                                'Ajouter un noeud pour l'attribut différent
                                pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                       pField.Name & "=" & pRowArchive.Value(i).ToString)
                                'Définir le type de noeud
                                pNodeAttribut.Tag = "ATTRIBUT"
                            End If
                        End If
                    Next
                End If

                'Si l'élément est présent dans la table parent et archive
            Else
                'Vérifier tous les attributs
                For i = 0 To pRowParent.Fields.FieldCount - 1
                    'Interface contenant un attribut d'élément
                    pField = pRowParent.Fields.Field(i)

                    'Vérifier si l'attribut est modifiable
                    If pField.Editable = True Then
                        'Vérifier si l'attribut est une géométrie
                        If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour extraire la Géométrie de la table parent
                            pFeatureParent = CType(pRowParent, IFeature)
                            'Interface pour extraire la Géométrie de latable d'archive
                            pFeatureArchive = CType(pRowArchive, IFeature)
                            'Vérifier si les géométries des éléments sont différentes
                            If bDifferenceGeometrie(pFeatureParent.Shape, pFeatureArchive.Shape) Then
                                'Vérifier si le noeud de l'élément est invalide
                                If pNodeElement Is Nothing Then
                                    'Si le noeud modifier est absent
                                    If pNodeModifier Is Nothing Then
                                        'Créer le noeud contenant les éléments modifiés
                                        pNodeModifier = pNodeClasse.Nodes.Add("MODIFIER", "ETAT=MODIFIER")
                                        'Définir le type de noeud
                                        pNodeModifier.Tag = "ETAT"
                                    End If

                                    'Afficher l'information de l'élément
                                    pNodeElement = pNodeModifier.Nodes.Add(pFeatureParent.OID.ToString, "OBJECTID=" & pFeatureParent.OID.ToString)
                                    'Définir le type de noeud
                                    pNodeElement.Tag = "ELEMENT"
                                End If

                                'Ajouter un noeud pour l'attribut différent
                                pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                       pField.Name & "=" & pFeatureParent.Shape.GeometryType.ToString)
                                'Définir le type de noeud
                                pNodeAttribut.Tag = "GEOMETRIE"
                            End If

                            'Si la valeur d'attribut Parent est différente de l'Enfant
                        ElseIf Not pRowParent.Value(i).Equals(pRowArchive.Value(i)) Then
                            'Vérifier si le noeud de l'élément est invalide
                            If pNodeElement Is Nothing Then
                                'Si le noeud modifier est absent
                                If pNodeModifier Is Nothing Then
                                    'Créer le noeud contenant les éléments modifiés
                                    pNodeModifier = pNodeClasse.Nodes.Add("MODIFIER", "ETAT=MODIFIER")
                                    'Définir le type de noeud
                                    pNodeModifier.Tag = "ETAT"
                                End If
                                'Afficher l'information de l'élément
                                pNodeElement = pNodeModifier.Nodes.Add(pRowParent.OID.ToString, "OBJECTID=" & pRowParent.OID.ToString)
                                'Définir le type de noeud
                                pNodeElement.Tag = "ELEMENT"
                            End If

                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pRowParent.Value(i).ToString & "<>" & pRowArchive.Value(i).ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "ATTRIBUT"
                        End If
                    End If
                Next
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeElement = Nothing
            pNodeAttribut = Nothing
            pFeatureParent = Nothing
            pFeatureArchive = Nothing
            pRowParent = Nothing
            pRowArchive = Nothing
            pFeatureEnfant = Nothing
            pRowEnfant = Nothing
            pField = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de transformer les OIDs contenus dans une sélection d'éléments et de les retourner dans un ensemble de OIDs..
    '''</summary>
    '''
    '''<param name="pSelectionSet">Interface contenant les OIDs à traiter.</param>
    ''' 
    '''<return>IFIDSet contenant la liste des OIDs d'éléments à traiter.</return>
    ''' 
    Private Function SelectionSet2FidSet(ByVal pSelectionSet As ISelectionSet) As IFIDSet
        'Déclarer les variables de travail
        Dim pEnumIDs As IEnumIDs = Nothing                  'Interface pour extraire les OIDs du SelectionSet.
        Dim iOid As Integer = 0                             'ObjectId d'un élément.

        'Par déafaut, on retourne l'ensemble des OIDs vide
        SelectionSet2FidSet = New FIDSet

        Try
            'Interface pour extraire les éléments détruits
            pEnumIDs = pSelectionSet.IDs

            'Extraire le premier élément détruit
            pEnumIDs.Reset()
            iOid = pEnumIDs.Next()

            'Vérifier si au moins un élément est détruit
            If iOid > -1 Then
                'Traiter tous les éléments détruits
                Do Until iOid = -1
                    'Ajouter le OID à extraire
                    SelectionSet2FidSet.Add(iOid)

                    'Extraire le prochain OID
                    iOid = pEnumIDs.Next()
                Loop
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEnumIDs = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire les OIDs dans un ensemble de OIDs selon un type de changement désiré d'un réplica.
    '''</summary>
    '''
    '''<param name="pDataChanges">Interface contenant les changements.</param>
    '''<param name="sNomClasse">Nom de la classe à traiter.</param>
    '''<param name="pEsriDataChangeType">Indique le type de changement désiré.</param>
    ''' 
    '''<return>IFIDSet contenant la liste des OIDs d'éléments à traiter.</return>
    ''' 
    Private Function DataChangesOids(ByVal pDataChanges As IDataChanges, ByVal sNomClasse As String, ByVal pEsriDataChangeType As esriDataChangeType) As IFIDSet
        'Déclarer les variables de travail
        Dim pDiffCursor As IDifferenceCursor = Nothing      'Interface pour extraire les différences.
        Dim pRow As IRow = Nothing                          'Interface contenant un élément modifié.
        Dim iOid As Integer = Nothing                       'ObjectId d'un élément.

        'Par déafaut, on retourne l'ensemble des OIDs vide
        DataChangesOids = New FIDSet

        Try
            'Interface pour extraire les éléments détruits
            pDiffCursor = pDataChanges.Extract(sNomClasse, pEsriDataChangeType)

            'Créer un nouveau Row vide
            pRow = New Row

            'Extraire le premier élément détruit
            pDiffCursor.Next(iOid, pRow)

            'Vérifier si au moins un élément est détruit
            If iOid > -1 Then
                'Traiter tous les éléments détruits
                Do Until iOid = -1
                    'Ajouter le OID à extraire
                    DataChangesOids.Add(iOid)

                    'Extraire le prochain élément détruit
                    pDiffCursor.Next(iOid, pRow)
                Loop
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pDiffCursor = Nothing
            pRow = Nothing
        End Try
    End Function
#End Region

#Region "Routines et fonctions pour identifier les différences dans un TreeView"
    '''<summary>
    ''' Routine qui permet d'identifier les différences dans un TreeView entre la Géodatabase enfant (.mdb ou .gdb) et son archive interne ou externe.
    '''</summary>
    '''
    '''<param name="treDifferences"> TreeView dans lequel les différences seront identifiées.</param>
    '''<param name="bExterne">Indique si l'archive externe est utilisée pour identifier les différences.</param>
    ''' 
    '''<remarks>
    ''' Par défaut, les différences seront identifiées à partir de l'information du réplica de la Géodatabase enfant dans laquelle l'archive interne est présente.
    ''' La Géodatabase d'archive externe correspond à la copie initiale de la Géodatabase enfant.
    ''' </remarks>
    ''' 
    Public Sub IdentifierDifferences(ByRef treDifferences As TreeView, Optional bExterne As Boolean = False)
        'Déclarer les variables de travail
        Dim pEditor As IEditor = Nothing    'Interface qui permet de vérifier et sauver les modification.
        Dim pUID As New UID                 'Interface contenant l'identifiant d'une classe.

        Try
            'Définir l'identifiant de la classe d'édition
            pUID.Value = "esriEditor.Editor"
            'Interface pour vérifier et sauver les modifications
            pEditor = CType(m_Application.FindExtensionByCLSID(pUID), IEditor)
            'vérifier la présence de modifications
            If pEditor.HasEdits Then
                'Fermer et sauver les modifications
                pEditor.StopEditing(True)
            End If

            'Initialiser le compteur
            giNbDifferences = -1

            'Vérifier si les différences sont identifiées à partir de l'archive externe
            If bExterne Then
                'Identifier les différences entre la Géodatabase enfant et l'archive externe de la Géodatabase enfant
                Call IdentifierDifferencesArchiveExterne(treDifferences)

                'Si les différences sont identifiées à partir de l'archive interne
            Else
                'Identifier les différences entre la Géodatabase enfant et l'archive interne de la Géodatabase enfant
                Call IdentifierDifferencesArchiveInterne(treDifferences)
            End If

            'Donner le focus au TreeView
            treDifferences.Focus()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEditor = Nothing
            pUID = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'extraire les différences entre la géodatabase enfant (.mdb ou .gdb) et la géodatabase d'archive externe.
    '''</summary>
    '''
    '''<param name="treDifferences">TreeView dans lequel les différences seront identifiées.</param>
    '''
    '''<remarks>L'archive des données est externe à la Géodatabase enfant. Elle est donc présente dans une autre Géodatabase .mdb ou .gdb.</remarks>
    '''
    Private Sub IdentifierDifferencesArchiveExterne(ByRef treDifferences As TreeView)
        'Déclarer les variables de travail
        Dim pNodeReplica As TreeNode = Nothing                      'Noeud du TreeView pour un réplica.
        Dim pArchiveFeatureWorkspace As IFeatureWorkspace = Nothing 'Interface pour ouvrir la table parent.
        Dim pEnfantFeatureWorkspace As IFeatureWorkspace = Nothing  'Interface pour ouvrir la table enfant.
        Dim pDatasetName As IDatasetName = Nothing                  'Interface contenant un Dataset d'un réplica.
        Dim pRepFilterDesc As IReplicaFilterDescription = Nothing   'Interface pour modifier la méthode d'extraction du checkOut.
        Dim pTableEnfant As ITable = Nothing                        'Interface contenant la table de la Géodatabase enfant.
        Dim pTableArchive As ITable = Nothing                       'Interface contenant la table de la Géodatabase d'archive.
        Dim dDateDebut As DateTime = Nothing                        'Contient la date de début du traitement.
        Dim sTempsTraitement As String = ""                         'Temps de traitement.
        Dim sNomClasse As String = ""                               'Contient le nom de la classe à traiter.

        Try
            'Débuter les ajouts dans le treeview
            treDifferences.BeginUpdate()

            'Initialiser le TreeView des conflits
            treDifferences.Nodes.Clear()

            'Vérifier si la Géodatabase d'archive externe est présente
            If gpGdbArchive IsNot Nothing Then
                'Vérifier si la description du réplica enfant est présente
                If gpReplicaEnfant IsNot Nothing Then
                    'Définir la date de début
                    dDateDebut = System.DateTime.Now

                    'Afficher le nom du réplica
                    pNodeReplica = treDifferences.Nodes.Add(gpReplicaEnfant.Name, "REPLICA=" & gpReplicaEnfant.Name & _
                                                            ", GdbEnfant=" & gpGdbEnfant.PathName & ", GdbArchive=" & gpGdbArchive.PathName & ":<ArchiveExterne>")
                    'Définir le type de noeud
                    pNodeReplica.Tag = "REPLICA"

                    'Interface pour extraire les tables de la Géodatabase enfant
                    pEnfantFeatureWorkspace = CType(gpGdbEnfant, IFeatureWorkspace)

                    'Interface pour extraire les tables de la Géodatabase d'archive
                    pArchiveFeatureWorkspace = CType(gpGdbArchive, IFeatureWorkspace)

                    'Interface pour modifier la méthode d'extraction du checkOut
                    pRepFilterDesc = CType(gpReplicaEnfant.Description, IReplicaFilterDescription)

                    'Traiter toutes les tables
                    For i = 0 To gpReplicaEnfant.Description.TableNameCount - 1
                        'Interface pour extraire le nom de la classe
                        pDatasetName = CType(gpReplicaEnfant.Description.TableName(i), IDatasetName)

                        'Définir le nom de la classe
                        sNomClasse = pDatasetName.Name
                        If gpReplicaParent IsNot Nothing Then sNomClasse = sNomClasse.Replace(gpReplicaParent.Owner & ".", "")

                        'Afficher le nom de la classe traitée
                        If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = sNomClasse & " ..."

                        'Définir la table de la Géodatabase enfant
                        pTableEnfant = pEnfantFeatureWorkspace.OpenTable(sNomClasse)
                        'Définir la table de sélection de la Géodatabase enfant
                        'pTableEnfant = Table2TableSelection(pTableEnfant, pRepFilterDesc, i)
                        pTableEnfant = Table2TableSelection(pTableEnfant, Nothing, i)

                        'Définir la table de la Géodatabase d'archive
                        pTableArchive = pArchiveFeatureWorkspace.OpenTable(sNomClasse)
                        'Définir la table de sélection de la Géodatabase d'archive
                        'pTableArchive = Table2TableSelection(pTableArchive, pRepFilterDesc, i)
                        pTableArchive = Table2TableSelection(pTableArchive, Nothing, i)

                        'Traiter toutes les différences entre la table enfant et son archive externe
                        Call IdentifierDifferencesArchiveExterneDataset(pTableEnfant, pTableArchive, pNodeReplica)
                    Next

                    'Trier les différences
                    treDifferences.Sort()

                    'Ouvrir le noeud du réplica
                    'pNodeReplica.ExpandAll()
                    pNodeReplica.Expand()

                    'Définir le nombre de différences trouvées
                    giNbDifferences = CalculerDifferences(pNodeReplica)

                    'Sélectionner le noeud du réplica
                    treDifferences.SelectedNode = pNodeReplica

                    'Définir le temps d'exécution
                    sTempsTraitement = System.DateTime.Now.Subtract(dDateDebut).Add(New TimeSpan(5000000)).ToString.Substring(0, 8)

                    'Afficher la fin et le temps du traitement
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement (Temps d'exécution: " & sTempsTraitement & ") !"

                Else
                    'Retourner une erreur
                    Throw New AnnulerExecutionException("ERREUR : La description du réplica de la Géodatabase enfant est absente !")
                End If

            Else
                'Retourner une erreur
                Throw New AnnulerExecutionException("ERREUR : La Géodatabase d'archive externe est absente !")
            End If

            'Terminer les ajouts dans le treeview
            treDifferences.EndUpdate()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeReplica = Nothing
            pEnfantFeatureWorkspace = Nothing
            pArchiveFeatureWorkspace = Nothing
            pRepFilterDesc = Nothing
            pDatasetName = Nothing
            pTableEnfant = Nothing
            pTableArchive = Nothing
            dDateDebut = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les différences dans un TreerView entre une table d'une Géodatabase enfant et une table d'une Géodatabase d'archive externe.
    '''</summary>
    ''' 
    '''<param name="pTableEnfant">Interface contenant la table de la Géodatabase enfant.</param>
    '''<param name="pTableArchive">Interface contenant la table de la Géodatabase d'archive.</param>
    '''
    Private Sub IdentifierDifferencesArchiveExterneDataset(ByVal pTableEnfant As ITable, ByVal pTableArchive As ITable, ByRef pNodeReplica As TreeNode)
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing                              'Interface qui permet d'extraire le nom de la table.
        Dim pNodeClasse As TreeNode = Nothing                           'Noeud du TreeView pour une classe.
        Dim pNodeAjouter As TreeNode = Nothing                          'Noeud du TreeView pour tous les éléments ajoutés d'une classe.
        Dim pNodeDetruire As TreeNode = Nothing                         'Noeud du TreeView pour tous les éléments détruits d'une classe.
        Dim pNodeModifier As TreeNode = Nothing                         'Noeud du TreeView pour tous les éléments modifiés d'une classe.
        Dim pArchiveFeatDict As Dictionary(Of Integer, IRow) = Nothing  'Interface contenant les éléments à traiter.
        Dim pTableSelection As ITableSelection = Nothing                'Interface pour extraire les éléments sélectionnés.
        Dim pCursor As ICursor = Nothing                                'Interface utilisé pour lire les éléments.
        Dim pRowEnfant As IRow = Nothing                                'Interface contenant l'élément enfant.
        Dim pRowArchive As IRow = Nothing                               'Interface contenant l'élément d'archive.
        Dim iOid As Integer = Nothing                                   'Contient la valeur du lien.

        Try
            'Interface pour extyraire le nom de la table
            pDataset = CType(pTableEnfant, IDataset)

            'Afficher le nom de la classe modifiée
            pNodeClasse = pNodeReplica.Nodes.Add(pDataset.BrowseName, "CLASSE=" & pDataset.BrowseName)
            'Définir le type de noeud
            pNodeClasse.Tag = "CLASSE"

            'Lire les éléments de la table parent 
            pArchiveFeatDict = LireElementsDict(pTableArchive)

            'Interface pour extraire les éléments sélectionnés de la table enfant
            pTableSelection = CType(pTableEnfant, ITableSelection)

            'Interfaces pour extraire les éléments sélectionnés
            pTableSelection.SelectionSet.Search(Nothing, False, pCursor)

            'Extraire le premier élément
            pRowEnfant = pCursor.NextRow

            'Traiter tous les éléments sélectionnés du FeatureLayer
            Do Until pRowEnfant Is Nothing
                'Vérifier si le lien est présent dans les éléments de la table d'archive
                If pArchiveFeatDict.ContainsKey(pRowEnfant.OID) Then
                    'Définir l'élément d'archive
                    pRowArchive = pArchiveFeatDict.Item(pRowEnfant.OID)
                    'Retirer l'élément du dictionaire d'Archive
                    pArchiveFeatDict.Remove(pRowEnfant.OID)
                Else
                    'Aucun élément d'archive
                    pRowArchive = Nothing
                End If

                'Identifier les différences entre l'élément de la table enfant et l'élément de la table d'archive
                DifferenceElementNoeud(pRowEnfant, pRowArchive, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)

                'Extraire le prochain élément à traiter
                pRowEnfant = pCursor.NextRow
            Loop

            'Traiter tous les éléments restants du dictionnaire de la table d'archive
            For Each iOid In pArchiveFeatDict.Keys
                'Définir l'élément d'archive
                pRowArchive = pArchiveFeatDict.Item(iOid)
                'Identifier les différences entre l'élément de la table enfant et l'élément de la table d'archive
                DifferenceElementNoeud(Nothing, pRowArchive, pNodeClasse, pNodeAjouter, pNodeDetruire, pNodeModifier)
            Next

            'Ouvrir le noeud
            pNodeClasse.Expand()

            'Vérifier si aucune différences dans le noeud de la classe
            If pNodeClasse.Nodes.Count = 0 Then pNodeClasse.Remove()

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            'If pDataset IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(pDataset)
            pDataset = Nothing
            pNodeClasse = Nothing
            pNodeAjouter = Nothing
            pNodeDetruire = Nothing
            pNodeModifier = Nothing
            pArchiveFeatDict = Nothing
            pTableSelection = Nothing
            pCursor = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de sélectionner les éléments correspondant à la description du réplica dataset à traiter.
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant la table à traiter</param>
    '''<param name="pRepFilterDesc">Interface contenant un Dataset d'un réplica.</param>
    '''<param name="iIndexDataset">Contient le numéro d'indexe du Dataset.</param>
    ''' 
    '''<returns>ITable contenant la sélection des éléments de la table à traiter</returns>
    ''' 
    Private Function Table2TableSelection(ByVal pTable As ITable, ByVal pRepFilterDesc As IReplicaFilterDescription, ByVal iIndexDataset As Integer) As ITable
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing                  'Interface pour extraire le nom de la Géodatabase.
        Dim pFeatureLayer As IFeatureLayer = Nothing        'Interface utilisé pour extraire la sélection d'une FeatureClass.
        Dim pStandaloneTable As IStandaloneTable = Nothing  'Interface utilisé pour extraire la sélection d'une Table.
        Dim pQueryfilter As IQueryFilter = Nothing          'Interface contenant une requête attributive.
        Dim pSpatialfilter As ISpatialFilter = Nothing      'Interface contenant une requête spatiale et attributive.
        Dim pFeatureSelection As IFeatureSelection = Nothing 'Interface utilisé pour sélectionner les éléments.
        Dim pTableSelection As ITableSelection = Nothing    'Interface utilisé pour sélectionner les éléments.

        'Par défaut la table est invalide
        Table2TableSelection = Nothing

        Try
            'Interface pour vérifier le type de table
            pDataset = CType(pTable, IDataset)

            'Si la table est une Featureclass
            If pDataset.Type = esriDatasetType.esriDTFeatureClass Then
                'Creer un nouveau FeatureLayer vide pour extraire la sélection
                pFeatureLayer = New FeatureLayer
                'Définir la classe du FeatureLayer
                pFeatureLayer.FeatureClass = CType(pTable, IFeatureClass)
                'Interface pour sélectionner les éléments
                pFeatureSelection = CType(pFeatureLayer, IFeatureSelection)

                'Vérifier si un filtre est présent
                If pRepFilterDesc IsNot Nothing Then
                    'Vérifier si un filtre a été effectué sur la table 
                    If pRepFilterDesc.RowsType(iIndexDataset) = esriRowsType.esriRowsTypeFilter Then
                        'Vérifier si une sélection a été effectué sur la table parent
                        If pRepFilterDesc.TableUsesSelection(iIndexDataset) = True Then
                            'Définir les éléments sélectionnés
                            pFeatureSelection.SelectionSet = pRepFilterDesc.TableSelection(iIndexDataset)

                            'Si une requête spatiale a été effectué sur la table parent
                        ElseIf pRepFilterDesc.TableUsesQueryGeometry(iIndexDataset) = True Then
                            'Créer un nouveau filtre spatiale
                            pSpatialfilter = New SpatialFilter
                            'Définir la relation spatiale
                            'pSpatialfilter.SpatialRel = pRepFilterDesc.SpatialRelation
                            'Définir la géométrie de la relation spatiale
                            'pSpatialfilter.Geometry = pRepFilterDesc.Geometry
                            'Définir la requête attributive
                            pSpatialfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                            'Sélectionner les éléments selon la requête attributive et spatiale
                            pFeatureSelection.SelectFeatures(pSpatialfilter, esriSelectionResultEnum.esriSelectionResultNew, False)

                            'Si une requête attributive a été effectué sur la table parent
                        ElseIf pRepFilterDesc.TableUsesDefQuery(iIndexDataset) = True Then
                            'Créer un nouveau filtre spatiale
                            pQueryfilter = New QueryFilter
                            'Définir la requête attributive
                            pQueryfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                            'Sélectionner les éléments selon la requête attributive
                            pFeatureSelection.SelectFeatures(pQueryfilter, esriSelectionResultEnum.esriSelectionResultNew, False)

                            'Si toute la table doit être sélectionnée
                        Else
                            'Sélectionner tous les éléments de la table
                            pFeatureSelection.SelectFeatures(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                        End If

                        'Si toute la table doit être sélectionnée
                    Else
                        'Sélectionner tous les éléments de la table
                        pFeatureSelection.SelectFeatures(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                    End If

                    'Si toute la table doit être sélectionnée
                Else
                    'Sélectionner tous les éléments de la table
                    pFeatureSelection.SelectFeatures(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                End If

                'Définir la table de sélection
                Table2TableSelection = CType(pFeatureSelection, ITable)

                'Si la table est une Table attributive
            ElseIf pDataset.Type = esriDatasetType.esriDTTable Then
                'Creer un nouveau StandaloneTable vide pour extraire la sélection
                pStandaloneTable = New StandaloneTable
                'Définir la table du StandaloneTable
                pStandaloneTable.Table = CType(pTable, ITable)
                'Interface contenant le Layer de la table
                pTableSelection = CType(pStandaloneTable, ITableSelection)

                'Vérifier si un filtre est présent
                If pRepFilterDesc IsNot Nothing Then
                    'Vérifier si un filtre a été effectué sur la table parent
                    If pRepFilterDesc.RowsType(iIndexDataset) = esriRowsType.esriRowsTypeFilter Then
                        'Vérifier si une sélection a été effectué sur la table parent
                        If pRepFilterDesc.TableUsesSelection(iIndexDataset) = True Then
                            'Définir les éléments sélectionnés
                            pTableSelection.SelectionSet = pRepFilterDesc.TableSelection(iIndexDataset)

                            'Si une requête spatiale a été effectué sur la table parent
                        ElseIf pRepFilterDesc.TableUsesQueryGeometry(iIndexDataset) = True Then
                            'Créer un nouveau filtre spatiale
                            pSpatialfilter = New SpatialFilter
                            'Définir la relation spatiale
                            'pSpatialfilter.SpatialRel = pRepFilterDesc.SpatialRelation
                            'Définir la géométrie de la relation spatiale
                            'pSpatialfilter.Geometry = pRepFilterDesc.Geometry
                            'Définir la requête attributive
                            pSpatialfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                            'Sélectionner les éléments selon la requête attributive et spatiale
                            pTableSelection.SelectRows(pSpatialfilter, esriSelectionResultEnum.esriSelectionResultNew, False)

                            'Si une requête attributive a été effectué sur la table parent
                        ElseIf pRepFilterDesc.TableUsesDefQuery(iIndexDataset) = True Then
                            'Créer un nouveau filtre spatiale
                            pQueryfilter = New QueryFilter
                            'Définir la requête attributive
                            pQueryfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                            'Sélectionner les éléments selon la requête attributive
                            pTableSelection.SelectRows(pQueryfilter, esriSelectionResultEnum.esriSelectionResultNew, False)

                            'Si toute la table doit être sélectionnée
                        Else
                            'Sélectionner tous les éléments de la table
                            pTableSelection.SelectRows(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                        End If

                        'Si toute la table doit être sélectionnée
                    Else
                        'Sélectionner tous les éléments de la table
                        pTableSelection.SelectRows(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                    End If
                    'Si toute la table doit être sélectionnée
                Else
                    'Sélectionner tous les éléments de la table
                    pTableSelection.SelectRows(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                End If

                'Définir la table de sélection
                Table2TableSelection = CType(pTableSelection, ITable)

            Else
                'Retourner un message d'erreur
                Throw New Exception("ERREUR : La table n'est par un type valide.")
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            'If pDataset IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(pDataset)
            pDataset = Nothing
            pFeatureLayer = Nothing
            pStandaloneTable = Nothing
            pQueryfilter = Nothing
            pSpatialfilter = Nothing
            pFeatureSelection = Nothing
            pTableSelection = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de créer un filtre pour extraire les éléments correspondant à la description du réplica dataset à traiter.
    '''</summary>
    '''
    '''<param name="pRepFilterDesc">Interface contenant un Dataset d'un réplica.</param>
    '''<param name="iIndexDataset">Contient le numéro d'indexe du Dataset.</param>
    ''' 
    '''<returns>IQueryFilter contenant le filtre des éléments de la table à traiter</returns>
    ''' 
    Private Function ReplicaFilter2QueryFilter(ByVal pRepFilterDesc As IReplicaFilterDescription, ByVal iIndexDataset As Integer) As IQueryFilter
        'Déclarer les variables de travail
        Dim pQueryfilter As IQueryFilter = Nothing          'Interface contenant une requête attributive.
        Dim pSpatialfilter As ISpatialFilter = Nothing      'Interface contenant une requête spatiale et attributive.

        'Par défaut, il n'y a pas de filtre
        ReplicaFilter2QueryFilter = Nothing

        Try
            'Vérifier si un filtre a été effectué sur la table parent
            If pRepFilterDesc.RowsType(iIndexDataset) = esriRowsType.esriRowsTypeFilter Then
                'Vérifier si une sélection a été effectué sur la table parent
                If pRepFilterDesc.TableUsesSelection(iIndexDataset) = True Then
                    'Il n'y a pas de filtre
                    ReplicaFilter2QueryFilter = Nothing

                    'Si une requête spatiale a été effectué sur la table parent
                ElseIf pRepFilterDesc.TableUsesQueryGeometry(iIndexDataset) = True Then
                    'Créer un nouveau filtre spatiale
                    pSpatialfilter = New SpatialFilter
                    'Définir la relation spatiale
                    pSpatialfilter.SpatialRel = pRepFilterDesc.SpatialRelation
                    'Définir la géométrie de la relation spatiale
                    pSpatialfilter.Geometry = pRepFilterDesc.Geometry
                    'Définir la requête attributive
                    pSpatialfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                    'Définir le filtre
                    ReplicaFilter2QueryFilter = pSpatialfilter

                    'Si une requête attributive a été effectué sur la table parent
                ElseIf pRepFilterDesc.TableUsesDefQuery(iIndexDataset) = True Then
                    'Créer un nouveau filtre spatiale
                    pQueryfilter = New QueryFilter
                    'Définir la requête attributive
                    pQueryfilter.WhereClause = pRepFilterDesc.TableDefQuery(iIndexDataset)
                    'Définir le filtre
                    ReplicaFilter2QueryFilter = pQueryfilter
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pQueryfilter = Nothing
            pSpatialfilter = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de lire les éléments d'une table et de les conserver par un lien de OID.
    '''</summary>
    ''' 
    '''<param name="pTable"> Interface contenant la table des éléments à lire.</param>
    ''' 
    '''<return> Dictionary(Of Integer, IRow) contenant les éléments identifiés par un lien de OID.</return>
    '''
    Private Function LireElementsDict(ByRef pTable As ITable) As Dictionary(Of Integer, IRow)
        'Déclarer les variables de travail
        Dim pTableSelection As ITableSelection = Nothing    'Interface pour extraire les éléments sélectionnés.
        Dim pCursor As ICursor = Nothing                    'Interface utilisé pour lire les éléments.
        Dim pRow As IRow = Nothing                          'Interface contenant l'élément lu.

        'Définir la valeur par défaut
        LireElementsDict = New Dictionary(Of Integer, IRow)

        Try
            'Interface pour extraire les éléments sélectionnés
            pTableSelection = CType(pTable, ITableSelection)

            'Interfaces pour extraire les éléments sélectionnés
            pTableSelection.SelectionSet.Search(Nothing, False, pCursor)

            'Extraire le premier élément
            pRow = pCursor.NextRow

            'Traiter tous les éléments sélectionnés du FeatureLayer
            Do Until pRow Is Nothing
                'Conserver l'élément par le lien d'un OID
                LireElementsDict.Add(pRow.OID, pRow)

                'Extraire le prochain élément à traiter
                pRow = pCursor.NextRow
            Loop

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pTableSelection = Nothing
            pCursor = Nothing
            pRow = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de lire les éléments d'une table et de les conserver par un lien de OID.
    '''</summary>
    ''' 
    '''<param name="pTable"> Interface contenant la table des éléments à lire.</param>
    '''<param name="pQueryFilter"> Interface contenant le filtre des éléments à lire.</param>
    ''' 
    '''<return> Dictionary(Of Integer, IRow) contenant les éléments identifiés par un lien de OID.</return>
    '''
    Private Function LireElementsDict(ByRef pTable As ITable, ByVal pQueryFilter As IQueryFilter) As Dictionary(Of Integer, IRow)
        'Déclarer les variables de travail
        Dim pCursor As ICursor = Nothing                    'Interface utilisé pour lire les éléments.
        Dim pRow As IRow = Nothing                          'Interface contenant l'élément lu.

        'Définir la valeur par défaut
        LireElementsDict = New Dictionary(Of Integer, IRow)

        Try
            'Interfaces pour extraire les éléments
            pCursor = pTable.Search(pQueryFilter, False)

            'Extraire le premier élément
            pRow = pCursor.NextRow

            'Traiter tous les éléments sélectionnés du FeatureLayer
            Do Until pRow Is Nothing
                'Conserver l'élément par le lien d'un OID
                LireElementsDict.Add(pRow.OID, pRow)

                'Extraire le prochain élément à traiter
                pRow = pCursor.NextRow
            Loop

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pCursor = Nothing
            pRow = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'identifier les différences d'attributs dans un noeud de TreeView entre deux éléments Enfant/Archive.
    '''</summary>
    '''
    '''<param name="pRowEnfant">Interface contenant un élément de la table enfant.</param>
    '''<param name="pRowArchive">Interface contenant un élément de la table d'archive.</param>
    '''<param name="pNodeClasse">Noeud d'un TreeView pour tous les éléments d'une classe.</param>
    '''<param name="pNodeAjouter">Noeud du TreeView pour les éléments ajoutés d'une classe.</param>
    '''<param name="pNodeDetruire">Noeud du TreeView pour les éléments détruits d'une classe.</param>
    '''<param name="pNodeModifier">Noeud du TreeView pour les éléments modifiés d'une classe.</param>
    ''' 
    Private Sub DifferenceElementNoeud(ByVal pRowEnfant As IRow, ByVal pRowArchive As IRow, ByRef pNodeClasse As TreeNode, _
                                      ByRef pNodeAjouter As TreeNode, ByRef pNodeDetruire As TreeNode, ByRef pNodeModifier As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeElement As TreeNode = Nothing              'Objet contenant un noeud du TreeView pour un élément.
        Dim pNodeAttribut As TreeNode = Nothing             'Objet contenant un noeud du TreeView pour un attribut d'élément.
        Dim pFeatureEnfant As IFeature = Nothing            'Interface contenant la géométrie d'un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing           'Interface contenant la géométrie d'un élément de la table d'archive.
        Dim pField As IField = Nothing                      'Interface contenant un attribut d'élément.
        Dim iOid As Integer = 0                             'Compteur

        Try
            'Vérifier si l'élément est absent de la table enfant
            If pRowEnfant Is Nothing Then
                'Si le noeud DETRUIRE n'existe pas
                If pNodeDetruire Is Nothing Then
                    'Créer le noeud contenant les éléments détruits
                    pNodeDetruire = pNodeClasse.Nodes.Add("DETRUIRE", "ETAT=DETRUIRE")
                    'Définir le type de noeud
                    pNodeDetruire.Tag = "ETAT"
                End If

                'Afficher l'information de l'élément
                pNodeElement = pNodeDetruire.Nodes.Add(pRowArchive.OID.ToString, "OBJECTID=" & pRowArchive.OID.ToString)
                'Définir le type de noeud
                pNodeElement.Tag = "ELEMENT"

                'Vérifier tous les attributs
                For i = 0 To pRowArchive.Fields.FieldCount - 1
                    'Interface contenant un attribut d'élément
                    pField = pRowArchive.Fields.Field(i)

                    'Vérifier si l'attribut est modifiable
                    If pField.Editable = True Then
                        'Vérifier si l'attribut est une géométrie
                        If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour extraire la Géométrie
                            pFeatureArchive = CType(pRowArchive, IFeature)
                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pFeatureArchive.Shape.GeometryType.ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "GEOMETRIE"

                            'Si l'attribut n'est pas une géométrie
                        Else
                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pRowArchive.Value(i).ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "ATTRIBUT"
                        End If
                    End If
                Next

                'Vérifier si l'élément est absent de la table d'archive
            ElseIf pRowArchive Is Nothing Then
                'Si le noeud Ajouter n'existe pas
                If pNodeAjouter Is Nothing Then
                    'Créer le noeud contenant les éléments à Ajouter
                    pNodeAjouter = pNodeClasse.Nodes.Add("AJOUTER", "ETAT=AJOUTER")
                    'Définir le type de noeud
                    pNodeAjouter.Tag = "ETAT"
                End If

                'Afficher l'information de l'élément
                pNodeElement = pNodeAjouter.Nodes.Add(pRowEnfant.OID.ToString, "OBJECTID=" & pRowEnfant.OID.ToString)
                'Définir le type de noeud
                pNodeElement.Tag = "ELEMENT"

                'Vérifier tous les attributs
                For i = 0 To pRowEnfant.Fields.FieldCount - 1
                    'Interface contenant un attribut d'élément
                    pField = pRowEnfant.Fields.Field(i)

                    'Vérifier si l'attribut est modifiable
                    If pField.Editable = True Then
                        'Vérifier si l'attribut est une géométrie
                        If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour extraire la Géométrie
                            pFeatureEnfant = CType(pRowEnfant, IFeature)
                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pFeatureEnfant.Shape.GeometryType.ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "GEOMETRIE"

                            'Si l'attribut n'est pas une géométrie
                        Else
                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pRowEnfant.Value(i).ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "ATTRIBUT"
                        End If
                    End If
                Next

                'Si l'élément est présent dand la table parent
            Else
                'Vérifier tous les attributs
                For i = 0 To pRowArchive.Fields.FieldCount - 1
                    'Interface contenant un attribut d'élément
                    pField = pRowArchive.Fields.Field(i)

                    'Vérifier si l'attribut est modifiable
                    If pField.Editable = True Then
                        'Vérifier si l'attribut est une géométrie
                        If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                            'Interface pour extraire la Géométrie
                            pFeatureEnfant = CType(pRowEnfant, IFeature)
                            'Interface pour extraire la Géométrie originale
                            pFeatureArchive = CType(pRowArchive, IFeature)
                            'Vérifier si les géométries des éléments sont différentes
                            If bDifferenceGeometrie(pFeatureEnfant.Shape, pFeatureArchive.Shape) Then
                                'Vérifier si le noeud de l'élément est invalide
                                If pNodeElement Is Nothing Then
                                    'Si le noeud modifier est absent
                                    If pNodeModifier Is Nothing Then
                                        'Créer le noeud contenant les éléments modifiés
                                        pNodeModifier = pNodeClasse.Nodes.Add("MODIFIER", "ETAT=MODIFIER")
                                        'Définir le type de noeud
                                        pNodeModifier.Tag = "ETAT"
                                    End If

                                    'Afficher l'information de l'élément
                                    pNodeElement = pNodeModifier.Nodes.Add(pRowEnfant.OID.ToString, "OBJECTID=" & pRowEnfant.OID.ToString)
                                    'Définir le type de noeud
                                    pNodeElement.Tag = "ELEMENT"
                                End If

                                'Ajouter un noeud pour l'attribut différent
                                pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                       pField.Name & "=" & pFeatureEnfant.Shape.GeometryType.ToString)
                                'Définir le type de noeud
                                pNodeAttribut.Tag = "GEOMETRIE"
                            End If

                            'Si la valeur d'attribut Parent est différente de l'Enfant
                        ElseIf Not pRowArchive.Value(i).Equals(pRowEnfant.Value(i)) Then
                            'Vérifier si le noeud de l'élément est invalide
                            If pNodeElement Is Nothing Then
                                'Si le noeud modifier est absent
                                If pNodeModifier Is Nothing Then
                                    'Créer le noeud contenant les éléments modifiés
                                    pNodeModifier = pNodeClasse.Nodes.Add("MODIFIER", "ETAT=MODIFIER")
                                    'Définir le type de noeud
                                    pNodeModifier.Tag = "ETAT"
                                End If

                                'Afficher l'information de l'élément
                                pNodeElement = pNodeModifier.Nodes.Add(pRowEnfant.OID.ToString, "OBJECTID=" & pRowEnfant.OID.ToString)
                                'Définir le type de noeud
                                pNodeElement.Tag = "ELEMENT"
                            End If

                            'Ajouter un noeud pour l'attribut différent
                            pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                   pField.Name & "=" & pRowEnfant.Value(i).ToString & "<>" & pRowArchive.Value(i).ToString)
                            'Définir le type de noeud
                            pNodeAttribut.Tag = "ATTRIBUT"
                        End If
                    End If
                Next
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeElement = Nothing
            pNodeAttribut = Nothing
            pFeatureArchive = Nothing
            pFeatureEnfant = Nothing
            pRowEnfant = Nothing
            pRowArchive = Nothing
            pField = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les différences entre la géodatabase enfant (.mdb ou .gdb) et son archive interne via un réplica de CheckOut.
    '''</summary>
    '''
    '''<param name="treDifferences">TreeView dans lequel les différences seront identifiées.</param>
    ''' 
    '''<remarks>Si aucun réplica n'est présent dans la géodatabase enfant, une erreur de traitement sera retournée.</remarks>
    ''' 
    Private Sub IdentifierDifferencesArchiveInterne(ByRef treDifferences As TreeView)
        'Déclarer les variables de travail
        Dim pNodeReplica As TreeNode = Nothing                          'Objet contenant un noeud du TreeView pour un réplica.
        Dim pNodeClasse As TreeNode = Nothing                           'Objet contenant un noeud du TreeView pour une classe.
        Dim pEnumModifiedClassInfo As IEnumModifiedClassInfo = Nothing  'Interface contenant les classes modifiées.
        Dim pModifiedClassInfo As IModifiedClassInfo = Nothing          'Interface contenant une classe modifiée.

        Try
            'Débuter les ajouts dans le treeview
            treDifferences.BeginUpdate()

            'Initialiser le TreeView des différences
            treDifferences.Nodes.Clear()

            'Vérifier si l'archive interne est présente
            If gpDataChanges IsNot Nothing Then
                'Afficher le nom du réplica
                pNodeReplica = treDifferences.Nodes.Add(gpReplicaEnfant.Name, "REPLICA=" & gpReplicaEnfant.Name _
                                                        & ", GdbEnfant=" & gpGdbEnfant.PathName & ", GdbArchive=" & gpGdbEnfant.PathName & ":<ArchiveInterne>")
                'Définir le type de noeud
                pNodeReplica.Tag = "REPLICA"

                'Interface contenant les classes modifiées
                pEnumModifiedClassInfo = gpDataChanges.GetModifiedClassesInfo

                'Extraire la première classe modifiée.
                pModifiedClassInfo = pEnumModifiedClassInfo.Next

                'Traiter toutes les classes modifiées
                Do Until pModifiedClassInfo Is Nothing
                    'Afficher le nom de la classe modifiée
                    pNodeClasse = pNodeReplica.Nodes.Add(pModifiedClassInfo.ChildClassName, "CLASSE=" & pModifiedClassInfo.ChildClassName)
                    'Définir le type de noeud
                    pNodeClasse.Tag = "CLASSE"

                    'Afficher les éléments détruits
                    Call DifferencesElementsDetruire(gpDataChanges, pModifiedClassInfo, pNodeClasse)

                    'Interface pour extraire les éléments ajoutés
                    Call DifferencesElementsAjouter(gpDataChanges, pModifiedClassInfo, pNodeClasse)

                    'Interface pour extraire les éléments modifiés
                    Call DifferencesElementsModifier(gpDataChanges, pModifiedClassInfo, pNodeClasse)

                    'Ouvrir le noeud
                    pNodeClasse.Expand()

                    'Extraire la prochaine classe modifiée.
                    pModifiedClassInfo = pEnumModifiedClassInfo.Next
                Loop

                'Trier les différences
                treDifferences.Sort()

                'Ouvrir le noeud du réplica
                'pNodeReplica.ExpandAll()
                pNodeReplica.Expand()

                'Définir le nombre de différences trouvées
                giNbDifferences = CalculerDifferences(pNodeReplica)

                'Sélectionner le noeud du réplica
                treDifferences.SelectedNode = pNodeReplica

                'Si l'archive interne est absente
            Else
                'Retourner l'erreur
                Throw New AnnulerExecutionException("ERREUR : L'archive interne est absente !")
            End If

            'Terminer les ajouts dans le treeview
            treDifferences.EndUpdate()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeReplica = Nothing
            pNodeClasse = Nothing
            pEnumModifiedClassInfo = Nothing
            pModifiedClassInfo = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les différences d'attributs dans un noeud de TreeView pour tous les éléments à détruire.
    '''</summary>
    '''
    '''<param name="pDataChanges">Interface contenant les changements.</param>
    '''<param name="pModifiedClassInfo">Interface contenant une classe modifiée.</param>
    '''<param name="pNodeClasse">Noeud d'un TreeView dans lequel les éléments détruits seront inscrits.</param>
    ''' 
    Private Sub DifferencesElementsDetruire(ByVal pDataChanges As IDataChanges, ByVal pModifiedClassInfo As IModifiedClassInfo, ByRef pNodeClasse As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeDetruire As TreeNode = Nothing         'Objet contenant un noeud du TreeView pour les éléments détruits.
        Dim pNodeElement As TreeNode = Nothing          'Objet contenant un noeud du TreeView pour un élément.
        Dim pNodeAttribut As TreeNode = Nothing         'Objet contenant un noeud du TreeView pour un attribut d'élément.
        Dim pDataChangesExt As IDataChangesExt = Nothing 'Interface qui permet d'extraire les éléments originaux.
        Dim pDiffCursor As IDifferenceCursor = Nothing  'Interface pour extraire les différences.
        Dim pCursorArchive As ICursor = Nothing         'Interface contenant les éléments d'archive à extraire.
        Dim pFidSet As IFIDSet = Nothing                'Interface contenant la liste des OIDs d'éléments d'archive à extraire.
        Dim pFeature As IFeature = Nothing              'Interface contenant la géométrie d'un élément.
        Dim pRowArchive As IRow = Nothing               'Interface contenant l'élément d'archive de l'élément détruit.
        Dim pRow As IRow = Nothing                      'Interface contenant un élément modifié.
        Dim pField As IField = Nothing                  'Interface contenant un attribut d'élément.
        Dim iOid As Integer = 0                         'ObjectId d'un élément.

        Try
            'Interface pour ajouter les OID des éléments originaux à extraire
            pFidSet = New FIDSet

            'Interface pour extraire les éléments détruits
            pDiffCursor = pDataChanges.Extract(pModifiedClassInfo.ChildClassName, esriDataChangeType.esriDataChangeTypeDelete)

            'Créer un nouveau Row vide
            pRow = New Row
            'Extraire le premier élément détruit
            pDiffCursor.Next(iOid, pRow)

            'Vérifier si au moins un élément est détruit
            If iOid > -1 Then
                'Traiter tous les éléments détruits
                Do Until iOid = -1
                    'Ajouter le OID à extraire
                    pFidSet.Add(iOid)

                    'Extraire le prochain élément détruit
                    pDiffCursor.Next(iOid, pRow)
                Loop

                'Interface pour contenant les éléments originaux
                pDataChangesExt = CType(pDataChanges, IDataChangesExt)

                'Interface pour extraire les éléments d'archive
                pCursorArchive = pDataChangesExt.ExtractOriginalRows(pModifiedClassInfo.ChildClassName, pFidSet)

                'Extraire le premier élément original
                pRowArchive = pCursorArchive.NextRow()

                'Si au moins un élément est détruit
                If pRowArchive IsNot Nothing Then
                    'Créer le noeud contenant les éléments détruits
                    pNodeDetruire = pNodeClasse.Nodes.Add("DETRUIRE", "ETAT=DETRUIRE")
                    'Définir le type de noeud
                    pNodeDetruire.Tag = "ETAT"

                    'Traiter tous les éléments détruits
                    Do Until pRowArchive Is Nothing
                        'Afficher l'information de l'élément détruit
                        pNodeElement = pNodeDetruire.Nodes.Add(pRowArchive.OID.ToString, "OBJECTID=" & pRowArchive.OID.ToString)
                        'Définir le type de noeud
                        pNodeElement.Tag = "ELEMENT"

                        'Vérifier tous les attributs
                        For i = 0 To pRowArchive.Fields.FieldCount - 1
                            'Interface contenant un attribut d'élément
                            pField = pRowArchive.Fields.Field(i)

                            'Vérifier si l'attribut est modifiable
                            If pField.Editable = True Then
                                'Vérifier si l'attribut est une géométrie
                                If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                    'Interface pour extraire la Géométrie
                                    pFeature = CType(pRowArchive, IFeature)
                                    'Ajouter un noeud pour l'attribut différent
                                    pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                           pField.Name & "=" & pFeature.Shape.GeometryType.ToString)
                                    'Définir le type de noeud
                                    pNodeAttribut.Tag = "GEOMETRIE"

                                    'Si l'attribut n'est pas une géométrie
                                Else
                                    'Ajouter un noeud pour l'attribut différent
                                    pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                           pField.Name & "=" & pRowArchive.Value(i).ToString)
                                    'Définir le type de noeud
                                    pNodeAttribut.Tag = "ATTRIBUT"
                                End If
                            End If
                        Next

                        'Extraire le prochain élément détruit
                        pRowArchive = pCursorArchive.NextRow()
                    Loop

                    'Ouvrir le noeud
                    pNodeDetruire.Expand()
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeDetruire = Nothing
            pNodeElement = Nothing
            pNodeAttribut = Nothing
            pDataChangesExt = Nothing
            pDiffCursor = Nothing
            pCursorArchive = Nothing
            pFidSet = Nothing
            pFeature = Nothing
            pRowArchive = Nothing
            pRow = Nothing
            pField = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les différences d'attributs dans un noeud de TreeView pour tous les éléments à ajouter.
    '''</summary>
    '''
    '''<param name="pDataChanges">Interface contenant les changements.</param>
    '''<param name="pModifiedClassInfo">Interface contenant une classe modifiée.</param>
    '''<param name="pNodeClasse">Noeud d'un TreeView dans lequel les éléments ajoutés seront inscrits.</param>
    ''' 
    Private Sub DifferencesElementsAjouter(ByVal pDataChanges As IDataChanges, ByVal pModifiedClassInfo As IModifiedClassInfo, ByRef pNodeClasse As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeAjouter As TreeNode = Nothing          'Objet contenant un noeud du TreeView pour les éléments ajoutés.
        Dim pNodeElement As TreeNode = Nothing          'Objet contenant un noeud du TreeView pour un élément.
        Dim pNodeAttribut As TreeNode = Nothing         'Objet contenant un noeud du TreeView pour un attribut d'élément.
        Dim pDiffCursor As IDifferenceCursor = Nothing  'Interface pour extraire les différences.
        Dim pFeature As IFeature = Nothing              'Interface contenant la géométrie d'un élément enfant.
        Dim pRow As IRow = New Row                      'Interface contenant un élément enfant.
        Dim pField As IField = Nothing                  'Interface contenant un attribut d'élément.
        Dim iOid As Integer = 0                         'Compteur

        Try
            'Interface pour extraire les éléments ajoutés
            pDiffCursor = pDataChanges.Extract(pModifiedClassInfo.ChildClassName, esriDataChangeType.esriDataChangeTypeInsert)

            'Extraire le premier élément ajouté
            pDiffCursor.Next(iOid, pRow)

            'Si au moins un élément est ajouté
            If iOid > -1 Then
                'Créer le noeud contenant les éléments ajoutés
                pNodeAjouter = pNodeClasse.Nodes.Add("AJOUTER", "ETAT=AJOUTER")
                'Définir le type de noeud
                pNodeAjouter.Tag = "ETAT"

                'Traiter tous les éléments ajoutés
                Do Until iOid = -1
                    'Afficher l'information de l'élément ajouté
                    pNodeElement = pNodeAjouter.Nodes.Add(iOid.ToString, "OBJECTID=" & iOid.ToString)
                    'Définir le type de noeud
                    pNodeElement.Tag = "ELEMENT"

                    'Vérifier tous les attributs
                    For i = 0 To pRow.Fields.FieldCount - 1
                        'Interface contenant un attribut d'élément
                        pField = pRow.Fields.Field(i)

                        'Vérifier si l'attribut est modifiable
                        If pField.Editable = True Then
                            'Vérifier si l'attribut est une géométrie
                            If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                'Interface pour extraire la Géométrie
                                pFeature = CType(pRow, IFeature)
                                'Ajouter un noeud pour l'attribut différent
                                pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                       pField.Name & "=" & pFeature.Shape.GeometryType.ToString)
                                'Définir le type de noeud
                                pNodeAttribut.Tag = "GEOMETRIE"

                                'Si l'attribut n'est pas une géométrie
                            Else
                                'Ajouter un noeud pour l'attribut différent
                                pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                       pField.Name & "=" & pRow.Value(i).ToString)
                                'Définir le type de noeud
                                pNodeAttribut.Tag = "ATTRIBUT"
                            End If
                        End If
                    Next

                    'Extraire le prochain élément ajouté
                    pDiffCursor.Next(iOid, pRow)
                Loop

                'Ouvrir le noeud
                pNodeAjouter.Expand()
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeAjouter = Nothing
            pNodeElement = Nothing
            pNodeAttribut = Nothing
            pDiffCursor = Nothing
            pFeature = Nothing
            pRow = Nothing
            pField = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les différences d'attributs dans un noeud de TreeView pour tous les éléments à modifier.
    '''</summary>
    '''
    '''<param name="pDataChanges">Interface contenant les changements.</param>
    '''<param name="pModifiedClassInfo">Interface contenant une classe modifiée.</param>
    '''<param name="pNodeClasse">Noeud d'un TreeView dans lequel les éléments modifiés seront inscrits.</param>
    ''' 
    Private Sub DifferencesElementsModifier(ByVal pDataChanges As IDataChanges, ByVal pModifiedClassInfo As IModifiedClassInfo, ByRef pNodeClasse As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeModifier As TreeNode = Nothing         'Objet contenant un noeud du TreeView pour les éléments modifiés.
        Dim pNodeElement As TreeNode = Nothing          'Objet contenant un noeud du TreeView pour un élément.
        Dim pNodeAttribut As TreeNode = Nothing         'Objet contenant un noeud du TreeView pour un attribut d'élément.
        Dim pDataChangesExt As IDataChangesExt = Nothing 'Interface qui permet d'extraire les éléments originaux.
        Dim pRowColl As Collection = Nothing            'Collection des éléments modifiés.
        Dim pDiffCursor As IDifferenceCursor = Nothing  'Interface pour extraire les différences.
        Dim pOriCursor As ICursor = Nothing             'Interface contenant les éléments originaux à extraire.
        Dim pFidSet As IFIDSet = Nothing                'Interface contenant la liste des OID d'éléments originaux à extraire.
        Dim pFeatureEnfant As IFeature = Nothing        'Interface contenant la géométrie d'un élément enfant.
        Dim pFeatureArchive As IFeature = Nothing       'Interface contenant la géométrie d'un élément d'archive.
        Dim pRowEnfant As IRow = Nothing                'Interface contenant un élément enfant.
        Dim pRowArchive As IRow = Nothing               'Interface contenant l'élément d'archive.
        Dim pField As IField = Nothing                  'Interface contenant un attribut d'élément.
        Dim iOid As Integer = 0                         'Compteur

        Try
            'Objet contenant les éléments modifiés.
            pRowColl = New Collection

            'Interface pour ajouter les OID des éléments originaux à extraire
            pFidSet = New FIDSet

            'Interface pour extraire les éléments modifiés
            pDiffCursor = pDataChanges.Extract(pModifiedClassInfo.ChildClassName, esriDataChangeType.esriDataChangeTypeUpdate)

            'Créer un nouveau Row vide
            pRowEnfant = New Row
            'Extraire le premier élément
            pDiffCursor.Next(iOid, pRowEnfant)

            'Vérifier si au moins un élément 
            If iOid > -1 Then
                'Traiter tous les éléments détruits
                Do Until iOid = -1
                    'Ajouter le OID à extraire
                    pFidSet.Add(iOid)

                    'Conserver l'élément modifié
                    pRowColl.Add(pRowEnfant, iOid.ToString)

                    'Créer un nouveau Row vide
                    pRowEnfant = New Row
                    'Extraire le prochain élément
                    pDiffCursor.Next(iOid, pRowEnfant)
                Loop

                'Interface pour contenant les éléments d'Archive
                pDataChangesExt = CType(pDataChanges, IDataChangesExt)

                'Interface pour extraire les éléments originaux
                pOriCursor = pDataChangesExt.ExtractOriginalRows(pModifiedClassInfo.ChildClassName, pFidSet)

                'Extraire le premier élément d'archive
                pRowArchive = pOriCursor.NextRow()

                'Si au moins un élément
                If pRowArchive IsNot Nothing Then
                    'Créer le noeud contenant les éléments modifiés
                    pNodeModifier = pNodeClasse.Nodes.Add("MODIFIER", "ETAT=MODIFIER")
                    'Définir le type de noeud
                    pNodeModifier.Tag = "ETAT"

                    'Traiter tous les éléments détruits
                    Do Until pRowArchive Is Nothing
                        'Afficher l'information de l'élément détruit
                        pNodeElement = pNodeModifier.Nodes.Add(pRowArchive.OID.ToString, "OBJECTID=" & pRowArchive.OID.ToString)
                        'Définir le type de noeud
                        pNodeElement.Tag = "ELEMENT"

                        'Extraire l'élément modifié
                        pRowEnfant = CType(pRowColl.Item(pRowArchive.OID.ToString), IRow)

                        'Vérifier tous les attributs
                        For i = 0 To pRowEnfant.Fields.FieldCount - 1
                            'Interface contenant un attribut d'élément
                            pField = pRowEnfant.Fields.Field(i)

                            'Vérifier si l'attribut est modifiable
                            If pField.Editable = True Then
                                'Vérifier si l'attribut est une géométrie
                                If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                    'Interface pour extraire la Géométrie de l'élément enfant
                                    pFeatureEnfant = CType(pRowEnfant, IFeature)
                                    'Interface pour extraire la Géométrie de l'élément d'archive
                                    pFeatureArchive = CType(pRowArchive, IFeature)
                                    'Vérifier si les géométries des éléments sont différentes
                                    If bDifferenceGeometrie(pFeatureEnfant.Shape, pFeatureArchive.Shape) Then
                                        'Ajouter un noeud pour l'attribut différent
                                        pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                               pField.Name & "=" & pFeatureEnfant.Shape.GeometryType.ToString)
                                        'Définir le type de noeud
                                        pNodeAttribut.Tag = "GEOMETRIE"
                                    End If

                                    'Si la valeur d'attribut est différente de l'archive
                                ElseIf Not pRowEnfant.Value(i).Equals(pRowArchive.Value(i)) Then
                                    'Ajouter un noeud pour l'attribut différent
                                    pNodeAttribut = pNodeElement.Nodes.Add(pNodeClasse.Name & "/" & pNodeElement.Name & "/" & pField.Name, _
                                                                           pField.Name & "=" & pRowEnfant.Value(i).ToString & "<>" & pRowArchive.Value(i).ToString)
                                    'Définir le type de noeud
                                    pNodeAttribut.Tag = "ATTRIBUT"
                                End If
                            End If
                        Next

                        'Extraire le prochain élément détruit
                        pRowArchive = pOriCursor.NextRow()
                    Loop

                    'Ouvrir le noeud
                    pNodeModifier.Expand()
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeModifier = Nothing
            pNodeElement = Nothing
            pNodeAttribut = Nothing
            pDataChangesExt = Nothing
            pDiffCursor = Nothing
            pOriCursor = Nothing
            pFidSet = Nothing
            pFeatureArchive = Nothing
            pFeatureEnfant = Nothing
            pRowArchive = Nothing
            pRowEnfant = Nothing
            pField = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions pour déposer les différences dans la Géodatabase Parent"
    '''<summary>
    ''' Routine qui permet de déposer les différences dans la Géodatabase Parent en utilisant l'archive interne ou externe.
    '''</summary>
    ''' 
    '''<param name="bExterne">Indique si l'archive externe est utilisée pour identifier les différences.</param>
    ''' 
    '''<remarks>
    ''' Par défaut, les différences seront déposées à partir de l'information du réplica de la Géodatabase enfant dans laquelle l'archive interne est présente.
    ''' La Géodatabase d'archive externe correspond à la copie initiale de la Géodatabase enfant.
    ''' </remarks>
    ''' 
    Public Sub DeposerDifferences(Optional bExterne As Boolean = False)
        Try
            'Vérifier si les différences sont identifiées à partir de l'archive externe
            If bExterne Then
                'Déposer les différences entre la Géodatabase enfant et l'archive externe de la Géodatabase enfant
                Call DeposerDifferencesArchiveExterne()

                'Si les différences sont déposées à partir de l'archive interne
            Else
                'Déposer les différences entre la Géodatabase enfant et l'archive interne de la Géodatabase enfant
                Call DeposerDifferencesArchiveInterne()
            End If

        Catch ex As Exception
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de déposer les différences entre une Géodatabase enfant (.mdb ou .gdb) et son archive interne dans la Géodatabase parent (.sde)
    ''' en utilisant le CheckIn ESRI.
    '''</summary>
    ''' 
    '''<param name="bReconcile">Indique si une réconciliation doit être effectuée.</param>
    ''' 
    '''<remarks>Si aucun réplica ou archive interne n'est présent, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub DeposerDifferencesArchiveInterne(Optional bReconcile As Boolean = True)
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing                                  'Interface pour extraire le nom de la Géodatabase.
        Dim pParentWorkspaceName As IWorkspaceName = Nothing                'Interface pour extraire le nom de la Géodatabase parent.
        Dim pEnfantWorkspaceName As IWorkspaceName = Nothing                'Interface pour extraire le nom de la Géodatabase enfant.
        Dim pCheckIn As ICheckIn2 = Nothing                                 'Interface pour exécuter un checkIn.
        Dim pWorkspaceReplicas As IWorkspaceReplicas = Nothing              'Interface utilisé pour extraire les réplicas.
        Dim pWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin = Nothing    'Interface qui permet d'ajouter un réplica dans une Géodatabase.

        Try
            'Vérifier si la description du réplica enfant est présente
            If gpReplicaEnfant IsNot Nothing Then
                'Vérifier si l'archive interne est valide
                If gpDataChanges IsNot Nothing Then
                    'Interface pour extraire le nom de la Géodatabase enfant
                    pDataset = CType(gpGdbEnfant, IDataset)

                    'Extraire le nom de la Géodatabase enfant
                    pEnfantWorkspaceName = CType(pDataset.FullName, IWorkspaceName)

                    'Extraire le nom de la Géodatabase parent
                    pParentWorkspaceName = gpDataChanges.ParentWorkspaceName

                    'Interface pour exécuter un checkIn
                    pCheckIn = New CheckIn

                    'Exécuter un CheckIn qui enlèce la description des réplicas
                    If pCheckIn.CheckInFromGDB2(pParentWorkspaceName, gpReplicaEnfant.Name, pEnfantWorkspaceName, bReconcile, _
                                                 esriReplicaReconcilePolicyType.esriReplicaResolveConflictsInFavorOfDatabaseChanges, False, False) Then
                        'Retourner un message d'erreur
                        Throw New AnnulerExecutionException("ERREUR : Des conflits sont présents entre la Géodatabase parent et l'archive interne de la Géodatabase enfant.")
                    End If

                    'Désassigner la géodatabase Parent
                    gpGdbParent = Nothing

                    'Si l'archive interne est invalide
                Else
                    'Retourner un message d'erreur
                    Throw New AnnulerExecutionException("ERREUR : L'archive interne est invalide.")
                End If

                'Si aucun réplica n'est présent
            Else
                'Retourner un message d'erreur
                Throw New AnnulerExecutionException("ERREUR : Aucun réplica n'est présent dans la Géodatabase enfant.")
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pParentWorkspaceName = Nothing
            pEnfantWorkspaceName = Nothing
            pDataset = Nothing
            pCheckIn = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'extraire les différences entre la géodatabase enfant (.mdb ou .gdb) et la géodatabase d'archive externe.
    '''</summary>
    '''
    '''<remarks>L'archive des données est externe à la Géodatabase enfant. Elle est donc présente dans une autre Géodatabase .mdb ou .gdb.</remarks>
    '''
    Private Sub DeposerDifferencesArchiveExterne()
        'Déclarer les variables de travail
        Dim pFeatureWorkspaceParent As IFeatureWorkspace = Nothing  'Interface pour ouvrir la table parent.
        Dim pFeatureWorkspaceEnfant As IFeatureWorkspace = Nothing  'Interface pour ouvrir la table enfant.
        Dim pFeatureWorkspaceArchive As IFeatureWorkspace = Nothing 'Interface pour ouvrir la table d'archive.
        Dim pDatasetName As IDatasetName = Nothing                  'Interface contenant un Dataset d'un réplica.
        Dim pRepFilterDesc As IReplicaFilterDescription = Nothing   'Interface contenant le filtre d'un dataset de réplica.
        Dim pQueryFilter As IQueryFilter = Nothing                  'Interface contenant le filtre des éléments à traiter.
        Dim pTableParent As ITable = Nothing                        'Interface contenant la table de la Géodatabase parent.
        Dim pTableEnfant As ITable = Nothing                        'Interface contenant la table de la Géodatabase enfant.
        Dim pTableArchive As ITable = Nothing                       'Interface contenant la table de la Géodatabase d'archive.
        Dim sNomClasse As String = ""                               'Contient le nom de la classe à traiter.
        Dim dDateDebut As DateTime = Nothing                        'Contient la date de début du traitement.
        Dim sTempsTraitement As String = ""                         'Contient le temps de traitement.

        Try
            'Vérifier si la Géodatabase d'archive externe est présente
            If gpGdbArchive IsNot Nothing Then
                'Vérifier si la description du réplica enfant est présente
                If gpReplicaEnfant IsNot Nothing Then
                    'Définir la date de début
                    dDateDebut = System.DateTime.Now
                    'Afficher la fin et le temps du traitement
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Début du traitement pour déposer les différences !"

                    'Interface pour extraire les tables de la Géodatabase parent
                    pFeatureWorkspaceParent = CType(gpGdbParent, IFeatureWorkspace)

                    'Interface pour extraire les tables de la Géodatabase enfant
                    pFeatureWorkspaceEnfant = CType(gpGdbEnfant, IFeatureWorkspace)

                    'Interface pour extraire les tables de la Géodatabase d'archive
                    pFeatureWorkspaceArchive = CType(gpGdbArchive, IFeatureWorkspace)

                    'Interface pour modifier la méthode d'extraction du checkOut
                    pRepFilterDesc = CType(gpReplicaEnfant.Description, IReplicaFilterDescription)

                    'Traiter toutes les tables
                    For i = 0 To gpReplicaEnfant.Description.TableNameCount - 1
                        'Interface pour extraire le nom de la classe
                        pDatasetName = CType(gpReplicaEnfant.Description.TableName(i), IDatasetName)

                        'Définir le nom de la classe
                        sNomClasse = pDatasetName.Name.Replace(gpReplicaParent.Owner & ".", "")

                        'Afficher le nom de la classe traitée
                        If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = sNomClasse & " ..."

                        'Définir le filter des éléments à traiter
                        pQueryFilter = ReplicaFilter2QueryFilter(pRepFilterDesc, i)

                        'Définir la table de la Géodatabase parent
                        pTableParent = pFeatureWorkspaceParent.OpenTable(sNomClasse)

                        'Définir la table de la Géodatabase enfant
                        pTableEnfant = pFeatureWorkspaceEnfant.OpenTable(sNomClasse)

                        'Définir la table de la Géodatabase d'archive
                        pTableArchive = pFeatureWorkspaceArchive.OpenTable(sNomClasse)

                        'Vérifier si la table est spatiale
                        If pDatasetName.Type = esriDatasetType.esriDTFeatureClass Then
                            'Déposer toutes les différences d'une table attributive de la géodatabase parent
                            Call DeposerDifferencesArchiveExterneTable(pTableEnfant, pTableArchive, pTableParent, pQueryFilter)

                            'Si la table est attributive
                        ElseIf pDatasetName.Type = esriDatasetType.esriDTTable Then
                            'Déposer toutes les différences d'une table attributive de la géodatabase parent
                            Call DeposerDifferencesArchiveExterneTable(pTableEnfant, pTableArchive, pTableParent, pQueryFilter)
                        End If
                    Next

                    'Afficher la fin et le temps du traitement
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement pour déposer les différences (Temps d'exécution: " & sTempsTraitement & ") !"

                Else
                    'Retourner une erreur
                    Throw New AnnulerExecutionException("ERREUR : La description du réplica de la Géodatabase enfant est absente !")
                End If

            Else
                'Retourner une erreur
                Throw New AnnulerExecutionException("ERREUR : La Géodatabase d'archive externe est absente !")
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatureWorkspaceParent = Nothing
            pFeatureWorkspaceEnfant = Nothing
            pFeatureWorkspaceArchive = Nothing
            pRepFilterDesc = Nothing
            pQueryFilter = Nothing
            pDatasetName = Nothing
            pTableEnfant = Nothing
            pTableArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet déposer les différences entre une table d'une Géodatabase enfant et une table d'une Géodatabase d'archive externe dans la Géodatabase parent (.sde).
    '''</summary>
    ''' 
    '''<param name="pTableEnfant">Interface contenant la table de la Géodatabase enfant.</param>
    '''<param name="pTableArchive">Interface contenant la table de la Géodatabase d'archive.</param>
    '''<param name="pTableParent">Interface contenant la table de la Géodatabase parent.</param>
    '''<param name="pQueryfilter">Interface contenant le filtre utilisé pour extraire les éléments de la table parent.</param>
    '''
    Private Sub DeposerDifferencesArchiveExterneTable(ByRef pTableEnfant As ITable, ByRef pTableArchive As ITable, ByRef pTableParent As ITable, ByVal pQueryfilter As IQueryFilter)
        'Déclarer les variables de travail
        Dim pDictElementEnfant As Dictionary(Of Integer, IRow) = Nothing    'Dictionaire contenant les éléments de la table enfant.
        Dim pDictElementArchive As Dictionary(Of Integer, IRow) = Nothing   'Dictionaire contenant les éléments de la table d'archive.
        Dim pCursor As ICursor = Nothing                                    'Interface utilisé pour lire les éléments de la table parent.
        Dim pRowParent As IRow = Nothing                                    'Interface contenant un élément de la table parent.
        Dim iOid As Integer = Nothing                                       'Contient la valeur du OID.

        Try
            'Lire les éléments de la table d'enfant
            pDictElementEnfant = LireElementsDict(pTableEnfant, Nothing)

            'Lire les éléments de la table d'archive 
            pDictElementArchive = LireElementsDict(pTableArchive, Nothing)

            'Interface pour extraire les éléments de la table parent
            pCursor = pTableParent.Update(pQueryfilter, False)

            'Extraire le premier élément de la table parent
            pRowParent = pCursor.NextRow

            'Traiter tous les éléments sélectionnés du FeatureLayer
            Do Until pRowParent Is Nothing
                'Déposer les différences entre l'élément de la table enfant et l'élément de la table d'archive dans la table parent
                DeposerDifferencesArchiveExterneElement(pDictElementEnfant.Item(pRowParent.OID), pDictElementArchive.Item(pRowParent.OID), pRowParent, pTableParent, pCursor)

                'Vérifier si le lien est présent dans les éléments de la table d'enfant
                If pDictElementArchive.ContainsKey(pRowParent.OID) Then
                    'Retirer l'élément du dictionaire d'enfant
                    pDictElementEnfant.Remove(pRowParent.OID)
                End If

                'Vérifier si le lien est présent dans les éléments de la table d'archive
                If pDictElementArchive.ContainsKey(pRowParent.OID) Then
                    'Retirer l'élément du dictionaire d'Archive
                    pDictElementArchive.Remove(pRowParent.OID)
                End If

                'Extraire le prochain élément de la table parent
                pRowParent = pCursor.NextRow
            Loop

            'Traiter tous les éléments restants du dictionnaire de la table d'enfant restants - AJOUTER
            For Each iOid In pDictElementEnfant.Keys
                'Déposer les différences entre l'élément de la table enfant et l'élément de la table d'archive dans la table parent
                DeposerDifferencesArchiveExterneElement(pDictElementEnfant.Item(iOid), pDictElementArchive.Item(iOid), Nothing, pTableParent, pCursor)

                'Vérifier si le lien est présent dans les éléments de la table d'archive
                If pDictElementArchive.ContainsKey(iOid) Then
                    'Retirer l'élément du dictionaire d'Archive
                    pDictElementArchive.Remove(iOid)
                End If
            Next

            'Traiter tous les éléments restants du dictionnaire de la table d'archive restants - DETRUIT
            For Each iOid In pDictElementArchive.Keys
                'Déposer les différences entre l'élément de la table enfant et l'élément de la table d'archive dans la table parent
                DeposerDifferencesArchiveExterneElement(pDictElementEnfant.Item(iOid), pDictElementArchive.Item(iOid), pRowParent, pTableParent, pCursor)
            Next

            'Finaliser le dépôt des éléments dans la table parent
            pCursor.Flush()

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pDictElementEnfant = Nothing
            pDictElementArchive = Nothing
            pCursor = Nothing
            pRowParent = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de déposer les différences d'attributs entre deux éléments spatiales Enfant/Archive dans la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="pRowEnfant">Interface contenant un élément de la table enfant.</param>
    '''<param name="pRowArchive">Interface contenant un élément de la table d'archive.</param>
    '''<param name="pRowParent">Interface contenant un élément de la table parent.</param>
    '''<param name="pTableParent">Interface contenant tous les éléments de la table parent.</param>
    '''<param name="pCursorParent">Interface utilisé pour modifier les éléments de la table parent.</param>
    ''' 
    Private Sub DeposerDifferencesArchiveExterneElement(ByVal pRowEnfant As IRow, ByVal pRowArchive As IRow, ByRef pRowParent As IRow, _
                                                        ByRef pTableParent As ITable, ByRef pCursorParent As ICursor)
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing              'Interface pour extraire le nom de la table.
        Dim pRowBufferParent As IRowBuffer = Nothing    'Interface contenant la géométrie d'un élément de la table enfant.
        Dim pFeatureParent As IFeature = Nothing        'Interface contenant la géométrie d'un élément de la table parent.
        Dim pFeatureEnfant As IFeature = Nothing        'Interface contenant la géométrie d'un élément de la table enfant.
        Dim pFeatureArchive As IFeature = Nothing       'Interface contenant la géométrie d'un élément de la table d'archive.
        Dim pField As IField = Nothing                  'Interface contenant un attribut d'élément.
        Dim iOid As Integer = 0                         'Compteur

        Try
            'Interface pour extraire le nom de la table.
            pDataset = CType(pTableParent, IDataset)

            'Vérifier si l'élément est absent de la table enfant
            If pRowEnfant Is Nothing Then
                'Vérifier si l'élément de la table parent est présent
                If pRowParent IsNot Nothing Then
                    'Détruire l'élément de la table parent
                    pCursorParent.DeleteRow()

                    'Si l'élément de la table parent est détruit
                Else
                    'Retourner un message de conflit
                    Throw New Exception("CONFLIT : L'élément parent est détruit : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pRowEnfant.OID.ToString)
                End If

                'Vérifier si l'élément est absent de la table d'archive
            ElseIf pRowArchive Is Nothing Then
                'Vérifier si l'élément de la table parent est absent
                If pRowParent Is Nothing Then
                    'Créer un nouvel élément pour la table parent
                    pRowBufferParent = pTableParent.CreateRowBuffer

                    'Vérifier tous les attributs
                    For i = 0 To pRowEnfant.Fields.FieldCount - 1
                        'Interface contenant un attribut d'élément
                        pField = pRowEnfant.Fields.Field(i)

                        'Vérifier si l'attribut est modifiable
                        If pField.Editable = True Then
                            'Vérifier si l'attribut est une géométrie
                            If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                'Interface pour extraire la Géométrie
                                pFeatureParent = CType(pRowBufferParent, IFeature)

                                'Modifier la géométrie de l'élément de la Géodatabase parent
                                pFeatureParent.Shape = pFeatureEnfant.Shape

                                'Si l'attribut n'est pas une géométrie
                            Else
                                'Modifier la valeur de l'attribut de l'élément de la Géodatabase parent
                                pRowBufferParent.Value(i) = pRowEnfant.Value(i)
                            End If
                        End If
                    Next

                    'Ajouter un nouvel élément dans la Géodatabase parent
                    pCursorParent.InsertRow(pRowBufferParent)

                    'Si l'élément de la table parent est ajouté
                Else
                    'Retourner un message de conflit
                    Throw New Exception("CONFLIT : L'élément parent est ajouté : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pRowEnfant.OID.ToString)
                End If

                'Si l'élément doit être modifier dans la table parent
            Else
                'Vérifier si l'élément de la table parent est présent
                If pRowParent IsNot Nothing Then
                    'Vérifier tous les attributs
                    For i = 0 To pRowArchive.Fields.FieldCount - 1
                        'Interface contenant un attribut d'élément
                        pField = pRowArchive.Fields.Field(i)

                        'Vérifier si l'attribut est modifiable
                        If pField.Editable = True Then
                            'Vérifier si l'attribut est une géométrie
                            If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                'Interface pour extraire la Géométrie
                                pFeatureParent = CType(pRowParent, IFeature)

                                'Interface pour extraire la Géométrie
                                pFeatureEnfant = CType(pRowEnfant, IFeature)

                                'Interface pour extraire la Géométrie originale
                                pFeatureArchive = CType(pRowArchive, IFeature)

                                'Vérifier si les géométries des éléments sont différentes
                                If Not bDifferenceGeometrie(pFeatureParent.Shape, pFeatureArchive.Shape) Then
                                    'Vérifier si les géométries des éléments sont différentes
                                    If bDifferenceGeometrie(pFeatureEnfant.Shape, pFeatureArchive.Shape) Then
                                        'Modifier la géométrie de l'élément de la Géodatabase parent
                                        pFeatureParent.Shape = pFeatureEnfant.Shape
                                    End If

                                    'Si les géométries sont différentes
                                Else
                                    'Retourner un message de conflit
                                    Throw New Exception("CONFLIT : La géométrie de l'élément parent est modifiée : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pRowEnfant.OID.ToString)
                                End If

                                'Si l'attribut n'est pas une géométrie
                            Else
                                'Si la valeur d'attribut parent est différente de l'archive
                                If pRowParent.Value(i).Equals(pRowArchive.Value(i)) Then
                                    'Si la valeur d'attribut enfant est différente de l'archive
                                    If Not pRowArchive.Value(i).Equals(pRowEnfant.Value(i)) Then
                                        'Modifier la valeur de l'attribut de l'élément de la Géodatabase parent
                                        pRowParent.Value(i) = pRowEnfant.Value(i)
                                    End If

                                    'Si les valeurs d'attributs sont différents
                                Else
                                    'Retourner un message de conflit
                                    Throw New Exception("CONFLIT : L'attribut " & pField.Name & "de l'élément parent est modifiée : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pRowEnfant.OID.ToString)
                                End If
                            End If
                        End If
                    Next

                    'Modifier l' élément de la Géodatabase parent
                    pCursorParent.UpdateRow(pRowParent)

                    'Si l'élément de la table parent est détruit
                Else
                    'Retourner un message de conflit
                    Throw New Exception("CONFLIT : L'élément parent est détruit : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pFeatureEnfant.OID.ToString)
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pRowBufferParent = Nothing
            pFeatureParent = Nothing
            pFeatureEnfant = Nothing
            pFeatureArchive = Nothing
            pField = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de déposer les différences d'attributs entre deux éléments spatiales Enfant/Archive dans la Géodatabase parent.
    '''</summary>
    '''
    '''<param name="pFeatureEnfant">Interface contenant un élément de la table enfant.</param>
    '''<param name="pFeatureArchive">Interface contenant un élément de la table d'archive.</param>
    '''<param name="pFeatureParent">Interface contenant un élément de la table parent.</param>
    '''<param name="pFeatureClassParent">Interface contenant tous les éléments de la table parent.</param>
    '''<param name="pFeatureCursorParent">Interface utilisé pour modifier les éléments de la table parent.</param>
    ''' 
    Private Sub DeposerDifferencesArchiveExterneElement(ByVal pFeatureEnfant As IFeature, ByVal pFeatureArchive As IFeature, ByRef pFeatureParent As IFeature, _
                                                        ByRef pFeatureClassParent As IFeatureClass, ByRef pFeatureCursorParent As IFeatureCursor)
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing                      'Interface pour extraire le nom de la table.
        Dim pFeatureBufferParent As IFeatureBuffer = Nothing    'Interface contenant la géométrie d'un élément de la table enfant.
        Dim pField As IField = Nothing                          'Interface contenant un attribut d'élément.
        Dim iOid As Integer = 0                                 'Compteur

        Try
            'Vérifier si l'élément est absent de la table enfant
            If pFeatureEnfant Is Nothing Then
                'Vérifier si l'élément de la table parent est présent
                If pFeatureParent IsNot Nothing Then
                    'Détruire l'élément de la table parent
                    pFeatureCursorParent.DeleteFeature()

                    'Si l'élément de la table parent est détruit
                Else
                    'Retourner un message de conflit
                    Throw New Exception("CONFLIT : L'élément parent est détruit : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pFeatureEnfant.OID.ToString)
                End If

                'Vérifier si l'élément est absent de la table d'archive
            ElseIf pFeatureArchive Is Nothing Then
                'Vérifier si l'élément de la table parent est absent
                If pFeatureParent Is Nothing Then
                    'Ajouter un nouvel élément dans la table parent
                    pFeatureBufferParent = pFeatureClassParent.CreateFeatureBuffer

                    'Vérifier tous les attributs
                    For i = 0 To pFeatureEnfant.Fields.FieldCount - 1
                        'Interface contenant un attribut d'élément
                        pField = pFeatureEnfant.Fields.Field(i)

                        'Vérifier si l'attribut est modifiable
                        If pField.Editable = True Then
                            'Vérifier si l'attribut est une géométrie
                            If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                'Interface pour extraire la Géométrie
                                pFeatureEnfant = CType(pFeatureEnfant, IFeature)

                                'Modifier la géométrie de l'élément de la Géodatabase parent
                                pFeatureParent.Shape = pFeatureEnfant.Shape

                                'Si l'attribut n'est pas une géométrie
                            Else
                                'Modifier la valeur de l'attribut de l'élément de la Géodatabase parent
                                pFeatureParent.Value(i) = pFeatureEnfant.Value(i)
                            End If
                        End If
                    Next

                    'Ajouter un nouvel élément dans la Géodatabase parent
                    pFeatureCursorParent.InsertFeature(pFeatureBufferParent)

                    'Si l'élément de la table parent est ajouté
                Else
                    'Retourner un message de conflit
                    Throw New Exception("CONFLIT : L'élément parent est ajouté : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pFeatureEnfant.OID.ToString)
                End If

                'Si l'élément doit être modifier dans la table parent
            Else
                'Vérifier si l'élément de la table parent est présent
                If pFeatureParent IsNot Nothing Then
                    'Vérifier tous les attributs
                    For i = 0 To pFeatureArchive.Fields.FieldCount - 1
                        'Interface contenant un attribut d'élément
                        pField = pFeatureArchive.Fields.Field(i)

                        'Vérifier si l'attribut est modifiable
                        If pField.Editable = True Then
                            'Vérifier si l'attribut est une géométrie
                            If pField.Type = esriFieldType.esriFieldTypeGeometry Then
                                'Vérifier si les géométries des éléments sont différentes
                                If Not bDifferenceGeometrie(pFeatureParent.Shape, pFeatureArchive.Shape) Then
                                    'Vérifier si les géométries des éléments sont différentes
                                    If bDifferenceGeometrie(pFeatureEnfant.Shape, pFeatureArchive.Shape) Then
                                        'Modifier la géométrie de l'élément de la Géodatabase parent
                                        pFeatureParent.Shape = pFeatureEnfant.Shape
                                    End If

                                    'Si les géométries sont différentes
                                Else
                                    'Retourner un message de conflit
                                    Throw New Exception("CONFLIT : La géométrie de l'élément parent est modifiée : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pFeatureEnfant.OID.ToString)
                                End If

                                'Si l'attribut n'est pas une géométrie
                            Else
                                'Si la valeur d'attribut parent est égale à l'archive
                                If pFeatureParent.Value(i).Equals(pFeatureArchive.Value(i)) Then
                                    'Si la valeur d'attribut enfant est différente de l'archive
                                    If Not pFeatureArchive.Value(i).Equals(pFeatureEnfant.Value(i)) Then
                                        'Modifier la valeur de l'attribut de l'élément de la Géodatabase parent
                                        pFeatureParent.Value(i) = pFeatureEnfant.Value(i)
                                    End If

                                    'Si les valeurs d'attributs sont différents
                                Else
                                    'Retourner un message de conflit
                                    Throw New Exception("CONFLIT : L'attribut " & pField.Name & "de l'élément parent est modifiée : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pFeatureEnfant.OID.ToString)
                                End If
                            End If
                        End If
                    Next

                    'Modifier l' élément de la Géodatabase parent
                    pFeatureCursorParent.UpdateFeature(pFeatureParent)

                    'Si l'élément de la table parent est détruit
                Else
                    'Retourner un message de conflit
                    Throw New Exception("CONFLIT : L'élément parent est détruit : GDB=" & pDataset.BrowseName & ", OBJECTID=" & pFeatureEnfant.OID.ToString)
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pFeatureBufferParent = Nothing
            pField = Nothing
        End Try
    End Sub
#End Region
End Class
