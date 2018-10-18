Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.GeoDatabaseDistributed
Imports ESRI.ArcGIS.DataSourcesGDB
Imports System.Runtime.InteropServices

'**
'Nom de la composante : modBarreNonConformite.vb 
'
'''<summary>
''' Librairies de routines contenant toutes les variables, routines et fonctions globales.
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
''' Date : 16 janvier 2017
'''</remarks>
''' 
Module modBarreNonConformite
    '''<summary> Classe contenant le menu des paramètres de la barre de NonConformite. </summary>
    Public m_MenuNonConformite As dckMenuNonConformite
    ''' <summary>ComboBox utilisé pour gérer les Géodatabases-Enfant (.mdb/.gdb).</summary>
    Public m_cboGeodatabaseEnfant As cboNomGdbEnfant = Nothing
    '''<summary> Objet utilisé pour gérer l'information et les traitements d'un réplica.</summary>
    Public m_GererReplica As clsGererReplica = Nothing
    '''<summary> Objet utilisé pour gérer l'information des non-conformité.</summary>
    Public m_GererNC As clsGererNC = Nothing
    ''' <summary>Interface utilisé pour arrêter un traitement en progression.</summary>
    Public m_TrackCancel As ITrackCancel = Nothing
    ''' <summary>Interface ESRI contenant l'application ArcMap.</summary>
    Public m_Application As IApplication = Nothing
    ''' <summary>Interface ESRI contenant le document ArcMap.</summary>
    Public m_MxDocument As IMxDocument = Nothing
    ''' <summary>Contient le nombre d'identifiants de la non-conformité sélectionnés.</summary>
    Public m_NbIdentifiants As Integer = 0
    ''' <summary>Contient le nombre de classes de la non-conformité sélectionnées.</summary>
    Public m_NbClasses As Integer = 0
    ''' <summary>Contient le nombre de conflits trouvés.</summary>
    Public m_NbConflits As Integer = -1
    ''' <summary>Contient le nombre de différences trouvées.</summary>
    Public m_NbDifferences As Integer = -1

    '''<summary>Valeur initiale de la dimension en hauteur du menu.</summary>
    Public m_Height As Integer = 300
    '''<summary>Valeur initiale de la dimension en largeur du menu.</summary>
    Public m_Width As Integer = 300

    '''<summary> Interface ESRI contenant le symbol pour la texte.</summary>
    Public mpSymboleTexte As ISymbol
    '''<summary> Interface ESRI contenant le symbol pour les sommets d'une géométrie.</summary>
    Public mpSymboleSommet As ISymbol
    '''<summary> Interface ESRI contenant le symbol pour la géométrie de type point.</summary>
    Public mpSymbolePoint As ISymbol
    '''<summary> Interface ESRI contenant le symbol pour la géométrie de type ligne.</summary>
    Public mpSymboleLigne As ISymbol
    '''<summary> Interface ESRI contenant le symbol pour la géométrie de type surface.</summary>
    Public mpSymboleSurface As ISymbol

#Region "Routine et fonction publiques"
    '''<summary>
    ''' Routine qui permet de d'effectuer un Zoom selon une géométrie.
    '''</summary>
    '''
    '''<param name="pGeometry">Géométrie à afficher.</param>
    ''' 
    Public Sub ZoomToGeometry(ByVal pGeometry As IGeometry)
        'Déclarer les variables de travail
        Dim pEnvelope As IEnvelope = Nothing        'Interface ESRI contenant l'enveloppe de la géométrie.

        Try
            'Sorir si la géométrie est vide
            If pGeometry.IsEmpty Then Exit Sub

            'Vérifier si la géométrie est un point
            If pGeometry.GeometryType = esriGeometryType.esriGeometryPoint Then
                'Définir la nouvelle fenêtre de travail
                pEnvelope = m_MxDocument.ActiveView.Extent

                'Recentrer l'exveloppe selon le point
                pEnvelope.CenterAt(CType(pGeometry, IPoint))

                'Si la géométrie n'est pas un point
            Else
                'Définir l'enveloppe de l'élément en erreur qui n'est pas un point
                pEnvelope = pGeometry.Envelope

                'Agrandir l'enveloppe de 10% de l'élément en erreur
                pEnvelope.Expand(pEnvelope.Width / 10, pEnvelope.Height / 10, False)
            End If

            'Définir la nouvelle fenêtre de travail
            m_MxDocument.ActiveView.Extent = pEnvelope

            'Rafraîchier l'affichage
            m_MxDocument.ActiveView.Refresh()
            System.Windows.Forms.Application.DoEvents()

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEnvelope = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet d'extraire l'information sur les différences entre la géométrie d'un élément courant et la géométrie d'un élément d'archive.
    '''</summary>
    '''
    '''<param name="pGeometryCourant">Géométrie d'un élément courant.</param>
    '''<param name="pGeometryArchive">Géométrie d'un élément d'archive.</param>
    '''<param name="pDiffCourant">Différence de géométrie de l'élément courant.</param>
    '''<param name="pDiffArchive">Géométrie de géométrie de l'élément d'archive.</param>
    '''<param name="sMessage">Message contenant les différences de composantes et de sommets entre les géométries.</param>
    ''' 
    Public Sub ExtraireDifferencesGeometrie(ByVal pGeometryCourant As IGeometry, ByVal pGeometryArchive As IGeometry, _
                                            ByRef pDiffCourant As IGeometry, ByRef pDiffArchive As IGeometry, ByRef sMessage As String)
        'Déclarer les variables de travail
        Dim pGeomColl As IGeometryCollection = Nothing      'Interface utilisé pour extraire le nombre de composantes.
        Dim pPointColl As IPointCollection = Nothing        'Interface utilisé pour extraire le nombre de sommets.
        Dim pRelOp As IRelationalOperator = Nothing         'Interface utilisé pour vérifier une relation spatiale.
        Dim pTopoOp As ITopologicalOperator2 = Nothing      'Interface utilisé pour extraire les différences.

        Try
            'Sorir si les deux géométries sont invalides
            If pGeometryCourant Is Nothing And pGeometryArchive Is Nothing Then
                'Définir le message de différences
                sMessage = "Le type des deux géométries ne correspondent pas : " & pGeometryCourant.GeometryType.ToString & "<>" & pGeometryArchive.GeometryType.ToString
                'Définir la différence de l'élément courant
                pDiffCourant = pGeometryCourant
                'Définir la différence de l'élément d'archive
                pDiffArchive = pGeometryArchive

                'Sorir si l'élément de base est invalide
            ElseIf pGeometryCourant Is Nothing Then
                'Définir le message de différences
                sMessage = "L'élément courant est invalide."
                'Définir la différence de l'élément courant
                pDiffCourant = pGeometryCourant
                'Définir la différence de l'élément d'archive
                pDiffArchive = pGeometryArchive

                'Sorir si l'élément à comparer est invalide.
            ElseIf pGeometryArchive Is Nothing Then
                'Définir le message de différences
                sMessage = "L'élément d'archive est invalide."
                'Définir la différence de l'élément courant
                pDiffCourant = pGeometryCourant
                'Définir la différence de l'élément d'archive
                pDiffArchive = pGeometryArchive

                'Vérifier si la géométrie est un point
            ElseIf pGeometryCourant.GeometryType <> pGeometryArchive.GeometryType Then
                'Définir le message de différences
                sMessage = "Le type des deux géométries ne correspondent pas : " & pGeometryCourant.GeometryType.ToString & "<>" & pGeometryArchive.GeometryType.ToString
                'Définir la différence de l'élément courant
                pDiffCourant = pGeometryCourant
                'Définir la différence de l'élément d'archive
                pDiffArchive = pGeometryArchive

                'Vérifier si la géométrie de base est un point
            ElseIf pGeometryCourant.GeometryType = esriGeometryType.esriGeometryPoint Then
                'Interface utilisé pour vérifier une relation spatiale
                pRelOp = CType(pGeometryCourant, IRelationalOperator)
                'Vérifier si les géométries sont différentes
                If pRelOp.Equals(pGeometryArchive) Then
                    'Définir le message de différences
                    sMessage = "Les deux points sont égaux."
                    'Définir la différence de l'élément courant
                    pDiffCourant = New Point
                    'Définir la différence de l'élément d'archive
                    pDiffArchive = New Point
                Else
                    'Définir le message de différences
                    sMessage = "Les deux points ne sont pas égaux."
                    'Définir la différence de l'élément courant
                    pDiffCourant = pGeometryCourant
                    'Définir la différence de l'élément d'archive
                    pDiffArchive = pGeometryArchive
                End If

                'Si la géométrie de base n'est pas un point
            Else
                'Définir le message de différences initiale
                sMessage = "Composantes/Sommets :"

                'Interface pour extraire le nombre de composantes
                pGeomColl = CType(pGeometryCourant, IGeometryCollection)
                'Interface pour extraire le nombre de composantes
                pPointColl = CType(pGeometryCourant, IPointCollection)
                'Définir le message de différences
                sMessage = sMessage & " Courant=" & pGeomColl.GeometryCount.ToString & "/" & pPointColl.PointCount.ToString

                'Interface pour extraire le nombre de composantes
                pGeomColl = CType(pGeometryArchive, IGeometryCollection)
                'Interface pour extraire le nombre de composantes
                pPointColl = CType(pGeometryArchive, IPointCollection)
                'Définir le message de différences
                sMessage = sMessage & ", Archive=" & pGeomColl.GeometryCount.ToString & "/" & pPointColl.PointCount.ToString

                'Interface pour extraire les différences
                pTopoOp = CType(pGeometryCourant, ITopologicalOperator2)
                'Extraire et retourner les différences de l'élément courant
                pDiffCourant = pTopoOp.Difference(pGeometryArchive)

                'Interface pour extraire les différences
                pTopoOp = CType(pGeometryArchive, ITopologicalOperator2)
                'Extraire et retourner les différences de l'élément d'archive
                pDiffArchive = pTopoOp.Difference(pGeometryCourant)

                'Vérifier si aucune différence
                If pDiffCourant.IsEmpty And pDiffArchive.IsEmpty Then
                    'Transformer en Multipoint la géométrie de l'élément courant
                    pGeometryCourant = GeometrieToMultiPoint(pGeometryCourant)
                    'Transformer en Multipoint la géométrie de l'élément d'Archive
                    pGeometryArchive = GeometrieToMultiPoint(pGeometryArchive)

                    'Interface pour extraire les différences
                    pTopoOp = CType(pGeometryCourant, ITopologicalOperator2)
                    'Extraire et retourner les différences de l'élément courant
                    pDiffCourant = pTopoOp.Difference(pGeometryArchive)

                    'Interface pour extraire les différences
                    pTopoOp = CType(pGeometryArchive, ITopologicalOperator2)
                    'Extraire et retourner les différences de l'élément d'archive
                    pDiffArchive = pTopoOp.Difference(pGeometryCourant)
                End If

                'Interface pour extraire le nombre de composantes
                pGeomColl = CType(pDiffCourant, IGeometryCollection)
                'Interface pour extraire le nombre de composantes
                pPointColl = CType(pDiffCourant, IPointCollection)
                'Définir le message de différences
                sMessage = sMessage & ": Diff.Courant=" & pGeomColl.GeometryCount.ToString & "/" & pPointColl.PointCount.ToString

                'Interface pour extraire le nombre de composantes
                pGeomColl = CType(pDiffArchive, IGeometryCollection)
                'Interface pour extraire le nombre de composantes
                pPointColl = CType(pDiffArchive, IPointCollection)
                'Définir le message de différences
                sMessage = sMessage & ": Diff.Archive=" & pGeomColl.GeometryCount.ToString & "/" & pPointColl.PointCount.ToString
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pGeomColl = Nothing
            pPointColl = Nothing
            pRelOp = Nothing
            pTopoOp = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet d'indiquer si les géométries sont différentes.
    '''</summary>
    '''
    '''<param name="pGeometryCourant">Géométrie d'un élément courant.</param>
    '''<param name="pGeometryArchive">Géométrie d'un élément d'archive.</param>
    '''<returns>Boolean qui indique si les géométries sont différentes</returns>
    Public Function bDifferenceGeometrie(ByVal pGeometryCourant As IGeometry, ByVal pGeometryArchive As IGeometry) As Boolean
        'Déclarer les variables de travail
        Dim pGeomCollCourant As IGeometryCollection = Nothing   'Interface utilisé pour extraire le nombre de composantes de l'élément courant.
        Dim pGeomCollArchive As IGeometryCollection = Nothing   'Interface utilisé pour extraire le nombre de composantes de l'élément d'archive.
        Dim pPointCollCourant As IPointCollection = Nothing     'Interface utilisé pour extraire le nombre de sommets de l'élément courant.
        Dim pPointCollArchive As IPointCollection = Nothing     'Interface utilisé pour extraire le nombre de sommets de l'élément d'archive.
        Dim pRelOp As IRelationalOperator = Nothing             'Interface utilisé pour vérifier une relation spatiale.

        'Par défaut, les géométrie sont différentes
        bDifferenceGeometrie = True

        Try
            'Interface pour vérifier si les géométries sont égales
            pRelOp = CType(pGeometryCourant, IRelationalOperator)

            'Vérifier si les géométries sont égales
            If pRelOp.Equals(pGeometryArchive) Then
                'Vérifier si la Géométrie courante n'est pas un point
                If pGeometryCourant.GeometryType <> esriGeometryType.esriGeometryPoint Then
                    'Interface pour extraire le nombre de composantes
                    pGeomCollCourant = CType(pGeometryCourant, IGeometryCollection)

                    'Interface pour extraire le nombre de composantes
                    pGeomCollArchive = CType(pGeometryArchive, IGeometryCollection)

                    'Vérifier si les géométrie possède le même nombre de composantes
                    If pGeomCollCourant.GeometryCount = pGeomCollArchive.GeometryCount Then
                        'Interface pour extraire le nombre de composantes
                        pPointCollCourant = CType(pGeometryCourant, IPointCollection)

                        'Interface pour extraire le nombre de composantes
                        pPointCollArchive = CType(pGeometryArchive, IPointCollection)

                        'Vérifier si les géométrie possède le même nombre de composantes
                        If pPointCollCourant.PointCount = pPointCollArchive.PointCount Then
                            'Indiquer que les géométries sont identiques
                            bDifferenceGeometrie = False
                        End If
                    End If
                Else
                    'Indiquer que les géométries sont identiques
                    bDifferenceGeometrie = False
                End If
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pGeomCollCourant = Nothing
            pGeomCollArchive = Nothing
            pPointCollCourant = Nothing
            pPointCollArchive = Nothing
            pRelOp = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de copier un réplica enfant (Parent) dans une autre Géodatabase enfant.
    '''</summary>
    '''
    '''<param name="pEnfantGDB">Interface contenant l'information de la Géodatabase mdb ou gdb.</param>
    ''' 
    '''<remarks>Si aucun réplica n'est présent, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub CopyReplica(ByVal pParentGDB As IWorkspace, ByVal pEnfantGDB As IWorkspace)
        'Déclarer les variables de travail
        Dim pEnfantWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin = Nothing  'Interface qui permet d'enregistrer les modifications d'un réplica enfant.
        Dim pParentWorkspaceReplicas As IWorkspaceReplicas = Nothing            'Interface pour extraire les réplicas de la Géodatabase parent.
        Dim pEnfantWorkspaceReplicas As IWorkspaceReplicas = Nothing            'Interface pour extraire les réplicas de la Géodatabase enfant.
        Dim pParentReplica As IReplica3 = Nothing                               'Interface contenant le réplica de la Géodatabase parent.
        Dim pEnfantReplica As IReplica3 = Nothing                               'Interface contenant le réplica de la Géodatabase enfant.
        Dim iRepID As Integer = Nothing                                         'Contient l'identification du réplica enfant.

        Try
            'Interface pour extraire les réplicas de la Géodatabase enfant
            pParentWorkspaceReplicas = CType(pParentGDB, IWorkspaceReplicas)
            'Interface contenant le réplica de la Géodatabase enfant
            pParentReplica = CType(pParentWorkspaceReplicas.Replicas.Next, IReplica3)

            'Vérifier si un Réplica est absent
            If pParentReplica Is Nothing Then
                'Retourner un message d'erreur
                Throw New Exception("ERREUR : Aucun réplica n'est présent dans la Géodatabase parent.")
            End If

            'Interface pour extraire un réplica parent
            pEnfantWorkspaceReplicas = CType(pEnfantGDB, IWorkspaceReplicas)
            'Rafraichir les réplicas du Parent
            pEnfantWorkspaceReplicas.RefreshReplicas()

            'Interface pour extraire un réplica
            pEnfantWorkspaceReplicasAdmin = CType(pEnfantWorkspaceReplicas, IWorkspaceReplicasAdmin2)

            'Enregistrer le réplica du parent et extraire l'identifiant du réplica parent
            iRepID = pEnfantWorkspaceReplicasAdmin.RegisterReplica(pParentReplica)

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEnfantWorkspaceReplicasAdmin = Nothing
            pParentWorkspaceReplicas = Nothing
            pEnfantWorkspaceReplicas = Nothing
            pParentReplica = Nothing
            pEnfantReplica = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de réparer un réplica parent à partir d'un réplica enfant existant.
    '''</summary>
    '''
    '''<param name="pEnfantGDB">Interface contenant l'information de la Géodatabase mdb ou gdb.</param>
    ''' 
    '''<remarks>Si aucun réplica n'est présent, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub CopyInfoReplica(ByVal pParentGDB As IWorkspace, ByVal pEnfantGDB As IWorkspace)
        'Déclarer les variables de travail
        Dim pEnfantWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin = Nothing  'Interface qui permet d'enregistrer les modifications d'un réplica enfant.
        Dim pParentWorkspaceReplicas As IWorkspaceReplicas = Nothing            'Interface pour extraire les réplicas de la Géodatabase parent.
        Dim pEnfantWorkspaceReplicas As IWorkspaceReplicas = Nothing            'Interface pour extraire les réplicas de la Géodatabase enfant.
        Dim pParentReplica As IReplica3 = Nothing                               'Interface contenant le réplica de la Géodatabase parent.
        Dim pEnfantReplica As IReplica3 = Nothing                               'Interface contenant le réplica de la Géodatabase enfant.
        Dim pEnfantReplicaEdit As IReplicaEdit2 = Nothing                       'Interface qui permet de modifier l'information du répplica Enfant.

        Try
            'Interface pour extraire les réplicas de la Géodatabase enfant
            pParentWorkspaceReplicas = CType(pParentGDB, IWorkspaceReplicas)
            'Interface contenant le réplica de la Géodatabase enfant
            pParentReplica = CType(pParentWorkspaceReplicas.Replicas.Next, IReplica3)

            'Vérifier si un Réplica est absent
            If pParentReplica Is Nothing Then
                'Retourner un message d'erreur
                Throw New Exception("ERREUR : Aucun réplica n'est présent dans la Géodatabase parent.")
            End If

            'Interface pour extraire un réplica enfant
            pEnfantWorkspaceReplicas = CType(pEnfantGDB, IWorkspaceReplicas)
            'Interface contenant le réplica de la Géodatabase enfant
            pEnfantReplica = CType(pEnfantWorkspaceReplicas.ReplicaByName(pParentReplica.Name), IReplica3)

            'Vérifier si un Réplica est absent
            If pEnfantReplica Is Nothing Then
                'Retourner un message d'erreur
                Throw New Exception("ERREUR : Aucun réplica n'est présent dans la Géodatabase enfant.")
            End If

            'Ajuster le réplica de l'enfant en fonction du parent
            pEnfantReplicaEdit = CType(pEnfantReplica, IReplicaEdit2)
            pEnfantReplicaEdit.ParentID = pParentReplica.ParentID
            'pEnfantReplicaEdit.ReplicaID = pParentReplica.ReplicaID
            pEnfantReplicaEdit.ReplicaGuid = pParentReplica.ReplicaGuid
            pEnfantReplicaEdit.ReplicaDate = pParentReplica.ReplicaDate
            pEnfantReplicaEdit.Version = pParentReplica.Version
            pEnfantReplica = CType(pEnfantReplicaEdit, IReplica3)

            'Afficher l'information des réplicas Parent/Enfant
            Call AfficherInfoReplica(pParentReplica, pEnfantReplica)

            'Modifier le réplica enfant dans la Géodatabase
            pEnfantWorkspaceReplicasAdmin = CType(pEnfantWorkspaceReplicas, IWorkspaceReplicasAdmin)
            pEnfantWorkspaceReplicasAdmin.AlterReplica(pEnfantReplica)

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEnfantWorkspaceReplicasAdmin = Nothing
            pParentWorkspaceReplicas = Nothing
            pEnfantWorkspaceReplicas = Nothing
            pParentReplica = Nothing
            pEnfantReplica = Nothing
            pEnfantReplicaEdit = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de réparer un réplica parent à partir d'un réplica enfant existant.
    '''</summary>
    '''
    '''<param name="pEnfantGDB">Interface contenant l'information de la Géodatabase mdb ou gdb.</param>
    ''' 
    '''<remarks>Si aucun réplica n'est présent, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub RepairReplica(ByVal pEnfantGDB As IWorkspace)
        'Déclarer les variables de travail
        Dim pName As IName = Nothing                                    'Interface qui permet d'ouvrir la Géodatabase.
        Dim pDataset As IDataset = Nothing                              'Interface pour extraire le nom de la Géodatabase.
        Dim pParentGDB As IWorkspace = Nothing                          'Interface contenant la Géodatabase Parent.
        Dim pParentWorkspaceName As IWorkspaceName = Nothing            'Interface pour extraire le nom de la Géodatabase parent.
        Dim pEnfantWorkspaceName As IWorkspaceName = Nothing            'Interface pour extraire le nom de la Géodatabase enfant.
        Dim pParentWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin2 = Nothing 'Interface qui permet d'enregistrer les modifications du réplica Parent.
        Dim pEnfantWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin2 = Nothing 'Interface qui permet d'enregistrer les modifications du réplica Enfant.
        Dim pParentWorkspaceReplicas As IWorkspaceReplicas = Nothing    'Interface pour extraire les réplicas de la Géodatabase enfant.
        Dim pEnfantWorkspaceReplicas As IWorkspaceReplicas = Nothing    'Interface pour extraire les réplicas de la Géodatabase enfant.
        Dim pEnfantReplica As IReplica3 = Nothing                       'Interface contenant le réplica de la Géodatabase enfant.
        Dim pParentReplica As IReplica3 = Nothing                       'Interface contenant le réplica de la Géodatabase enfant.
        Dim pParentReplicaEdit As IReplicaEdit2 = Nothing               'Interface qui permet d'effectuer les modifications du réplica Parent.
        Dim pEnfantReplicaEdit As IReplicaEdit2 = Nothing               'Interface qui permet d'effectuer les modifications du réplica Enfant.
        Dim pParentVersionWorkspace As IVersionedWorkspace = Nothing    'Interface qui permet d'extraire une version de la Géodatabase Parent.
        Dim pParentVersion As IVersion = Nothing                        'Interface contenant une version de la Géodatabase Parent.
        Dim pDataChanges As IDataChanges = Nothing                      'Interface contenant les changements.
        Dim pReplicaDataChangesInit As IReplicaDataChangesInit = Nothing 'Interface pour initialiser l'identification des changements.
        Dim pPropertySet As IPropertySet = Nothing                      'Interface contenant l'instance de connexion à la Géodatabase Parent.
        Dim iRepID As Integer                                           'Identifiant du réplica Parent.

        Try
            'Interface pour extraire le nom de la Géodatabase enfant
            pDataset = CType(pEnfantGDB, IDataset)
            'Extraire le nom de la Géodatabase enfant
            pEnfantWorkspaceName = CType(pDataset.FullName, IWorkspaceName)

            'Interface pour extraire les réplicas de la Géodatabase enfant
            pEnfantWorkspaceReplicas = CType(pEnfantGDB, IWorkspaceReplicas)
            'Interface contenant le réplica de la Géodatabase enfant
            pEnfantReplica = CType(pEnfantWorkspaceReplicas.Replicas.Next, IReplica3)

            'Vérifier si un Réplica est présent
            If pEnfantReplica IsNot Nothing Then
                'Interface qui permet de définir toutes les tables de changement
                pReplicaDataChangesInit = New CheckOutDataChanges
                'Initialiser l'interface qui permet de définir toutes les tables de changement
                pReplicaDataChangesInit.Init(pEnfantReplica, pEnfantWorkspaceName)
                'Interface contenant les changements
                pDataChanges = CType(pReplicaDataChangesInit, IDataChanges)
                'Extraire le nom de la Géodatabase parent
                pParentWorkspaceName = pDataChanges.ParentWorkspaceName
                'Interface pour ouvrir la Géodatabase Parent
                pName = CType(pParentWorkspaceName, IName)
                'Définir la Géodatabase Parent
                pParentGDB = CType(pName.Open(), IWorkspace)

                'Interface pour extraire un réplica parent
                pParentWorkspaceReplicas = CType(pParentGDB, IWorkspaceReplicas)
                'Rafraichir les réplicas du Parent
                pParentWorkspaceReplicas.RefreshReplicas()

                'Extraire le réplica parent de l'enfant
                pParentReplica = CType(pParentWorkspaceReplicas.ReplicaByName(pEnfantReplica.Name), IReplica3)
                'Vérifier si le réplica parent est absent
                If pParentReplica Is Nothing Then
                    'Interface pour extraire l'usager de la GDB parent
                    pPropertySet = CType(pDataChanges.ParentWorkspaceName.ConnectionProperties, IPropertySet)

                    'Créer un nouveau réplica parent à partir du réplica enfant
                    pParentReplica = New Replica
                    pParentReplicaEdit = CType(pParentReplica, IReplicaEdit2)
                    pParentReplicaEdit.Init(pEnfantReplica)
                    pParentReplicaEdit.ParentID = -1
                    pParentReplicaEdit.ReplicaRole = esriReplicaType.esriCheckOutTypeParent
                    pParentReplicaEdit.Owner = pPropertySet.GetProperty("User").ToString.ToUpper
                    pParentReplicaEdit.Name = pParentReplica.Owner & "." & pEnfantReplica.Name
                    pParentReplicaEdit.ReplicaGuid = pEnfantReplica.ReplicaGuid

                    'Interface pour extraire la version parent selon la version de l'enfant
                    pParentVersionWorkspace = CType(pParentWorkspaceReplicas, IVersionedWorkspace)
                    Try
                        'Extraire la version parent selon la version de l'enfant
                        pParentVersion = pParentVersionWorkspace.FindVersion(pEnfantReplica.Version)
                    Catch ex As Exception
                        'On ne fait rien
                    End Try
                    'Vérifier si la version est absente
                    If pParentVersion Is Nothing Then
                        'Créer une nouvelle version parent à partir de la version de l'enfant
                        pParentVersion = pParentVersionWorkspace.DefaultVersion.CreateVersion(pEnfantReplica.Version)
                        pParentReplicaEdit.Version = pParentVersion.VersionName.Replace(pParentReplica.Owner & ".", "")
                        pParentReplica = CType(pParentReplicaEdit, IReplica3)
                    End If

                    'Interface pour extraire un réplica
                    pParentWorkspaceReplicasAdmin = CType(pParentWorkspaceReplicas, IWorkspaceReplicasAdmin2)
                    'Enregistrer le réplica du parent et extraire l'identifiant du réplica parent
                    iRepID = pParentWorkspaceReplicasAdmin.RegisterReplica(pParentReplica)

                    'Ajuster le réplica de l'enfant en fonction du parent
                    pEnfantReplicaEdit = CType(pEnfantReplica, IReplicaEdit2)
                    pEnfantReplicaEdit.ParentID = iRepID
                    'pEnfantReplicaEdit.Version = pParentReplica.Version.Replace(pParentReplica.Owner & ".", "")
                    'pEnfantReplicaEdit.ReplicaGuid = pParentReplica.ReplicaGuid
                    pEnfantReplica = CType(pEnfantReplicaEdit, IReplica3)
                    'Modifier le réplica enfant dans la Géodatabase
                    pEnfantWorkspaceReplicasAdmin = CType(pEnfantWorkspaceReplicas, IWorkspaceReplicasAdmin2)
                    pEnfantWorkspaceReplicasAdmin.AlterReplica(pEnfantReplica)
                End If

                'Afficher l'information des réplicas Parent/Enfant
                Call AfficherInfoReplica(pParentReplica, pEnfantReplica)

                'Si aucun réplica n'est présent
            Else
                'Retourner un message d'erreur
                Throw New Exception("ERREUR : Aucun réplica n'est présent dans la Géodatabase enfant.")
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            'If pDataset IsNot Nothing Then System.Runtime.InteropServices.Marshal.ReleaseComObject(pDataset)
            pDataset = Nothing
            pName = Nothing
            pParentWorkspaceName = Nothing
            pEnfantWorkspaceName = Nothing
            pParentWorkspaceReplicas = Nothing
            pEnfantWorkspaceReplicas = Nothing
            pParentGDB = Nothing
            pParentReplica = Nothing
            pEnfantReplica = Nothing
            pParentReplicaEdit = Nothing
            pEnfantReplicaEdit = Nothing
            pParentWorkspaceReplicasAdmin = Nothing
            pEnfantWorkspaceReplicasAdmin = Nothing
            pParentVersionWorkspace = Nothing
            pParentVersion = Nothing
            pDataChanges = Nothing
            pReplicaDataChangesInit = Nothing
            pPropertySet = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'afficher l'information du réplica parent et enfant.
    '''</summary>
    '''
    '''<param name="pParentReplica">Interface contenant l'information du réplica de la Géodatabase-Parent sde.</param>
    '''<param name="pEnfantReplica">Interface contenant l'information du réplica de la Géodatabase-Enfant mdb ou gdb.</param>
    ''' 
    '''<remarks>Si aucun réplica n'est présent, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub AfficherInfoReplica(ByVal pParentReplica As IReplica3, ByVal pEnfantReplica As IReplica3)
        'Déclarer les variables de travail
        Dim pRepFilterDesc As IReplicaFilterDescription = Nothing   'Interface pour modifier la méthode d'extraction du checkOut.
        Dim pEnumDataset As IEnumReplicaDataset = Nothing           'Interface contenant tous les Datasets d'un réplica.
        Dim pReplicaDataset As IReplicaDataset2 = Nothing           'Interface contenant un Dataset d'un réplica.
        Dim i As Integer = Nothing  'Compteur

        Try
            'Comparer l'information des réplicas Parent et Enfant
            Debug.Print("-----")
            Debug.Print("Name:          " & pParentReplica.Name & " / " & pEnfantReplica.Name)
            Debug.Print("Version:       " & pParentReplica.Version & " / " & pEnfantReplica.Version)
            Debug.Print("Owner:         " & pParentReplica.Owner & " / " & pEnfantReplica.Owner)
            Debug.Print("ParentID:      " & pParentReplica.ParentID & " / " & pEnfantReplica.ParentID)
            Debug.Print("ReplicaID:     " & pParentReplica.ReplicaID & " / " & pEnfantReplica.ReplicaID)
            Debug.Print("ReplicaGuid:   " & pParentReplica.ReplicaGuid & " / " & pEnfantReplica.ReplicaGuid)
            Debug.Print("ReplicaDate:   " & pParentReplica.ReplicaDate.ToString & " / " & pEnfantReplica.ReplicaDate.ToString)
            Debug.Print("ReplicaRole:   " & pParentReplica.ReplicaRole.ToString & " / " & pEnfantReplica.ReplicaRole.ToString)
            Debug.Print("ReplicaState:  " & pParentReplica.ReplicaState.ToString & " / " & pEnfantReplica.ReplicaState.ToString)
            Debug.Print("AccessType:    " & pParentReplica.AccessType.ToString & " / " & pEnfantReplica.AccessType.ToString)
            Debug.Print("HasConflicts:  " & pParentReplica.HasConflicts & " / " & pEnfantReplica.HasConflicts)
            Debug.Print("UseArchiving:  " & pParentReplica.UseArchiving & " / " & pEnfantReplica.UseArchiving)
            Debug.Print("ReconcilePolicyType:       " & pParentReplica.ReconcilePolicyType.ToString & " / " & pEnfantReplica.ReconcilePolicyType.ToString)
            Debug.Print("ReplicaReceivingVersion:   " & pParentReplica.ReplicaReceivingVersion & " / " & pEnfantReplica.ReplicaReceivingVersion)

            'Afficher les tables contenues dans le réplica Parent
            Debug.Print("----")
            Debug.Print("Datasets du réplica Parent:")
            'Interface pour modifier la méthode d'extraction du checkOut
            pRepFilterDesc = CType(pParentReplica.Description, IReplicaFilterDescription)
            'Interface pour extraire les datasets du préplica
            pEnumDataset = pParentReplica.ReplicaDatasets
            pEnumDataset.Reset()
            'Extraire le premier Dataset
            pReplicaDataset = CType(pEnumDataset.Next, IReplicaDataset2)
            i = 0
            'Traiter tous les Datasets
            Do Until pReplicaDataset Is Nothing
                Debug.Print("DatasetName:           " & pReplicaDataset.Name)
                Debug.Print("DatasetParentDatabase: " & pReplicaDataset.ParentDatabase)
                Debug.Print("DatasetParentOwner:    " & pReplicaDataset.ParentOwner)
                Debug.Print("DatasetTargetName:     " & pReplicaDataset.TargetName)
                Debug.Print("DatasetType:           " & pReplicaDataset.Type.ToString)
                Debug.Print("DatasetId:             " & pReplicaDataset.DatasetID.ToString)
                Debug.Print("DatasetReplicaId:      " & pReplicaDataset.ReplicaID.ToString)

                Debug.Print("RowsType:              " & pRepFilterDesc.RowsType(i).ToString)
                Debug.Print("TableUsesQueryGeometry:" & pRepFilterDesc.TableUsesQueryGeometry(i).ToString)
                Debug.Print("SpatialRelation:       " & pRepFilterDesc.SpatialRelation.ToString)
                Debug.Print("TableUsesDefQuery:     " & pRepFilterDesc.TableUsesDefQuery(i).ToString)
                Debug.Print("TableDefQuery:         " & pRepFilterDesc.TableDefQuery(i))
                Debug.Print("TableUsesSelection:    " & pRepFilterDesc.TableUsesSelection(i).ToString)
                If pRepFilterDesc.TableUsesSelection(i) Then Debug.Print("TableSelectionCount:   " & pRepFilterDesc.TableSelection(i).Count.ToString)

                'Extraire le prochain Dataset
                pReplicaDataset = CType(pEnumDataset.Next, IReplicaDataset2)
                i = i + 1
            Loop

            'Afficher les tables contenues dans le réplica Enfant
            Debug.Print("----")
            Debug.Print("Datasets du réplica Enfant:")
            'Interface pour modifier la méthode d'extraction du checkOut
            pRepFilterDesc = CType(pEnfantReplica.Description, IReplicaFilterDescription)
            'Interface pour extraire les datasets du préplica
            pEnumDataset = pEnfantReplica.ReplicaDatasets
            pEnumDataset.Reset()
            'Extraire le premier Dataset
            pReplicaDataset = CType(pEnumDataset.Next, IReplicaDataset2)
            i = 0
            'Traiter tous les Datasets
            Do Until pReplicaDataset Is Nothing
                Debug.Print("DatasetName:           " & pReplicaDataset.Name)
                Debug.Print("DatasetParentDatabase: " & pReplicaDataset.ParentDatabase)
                Debug.Print("DatasetParentOwner:    " & pReplicaDataset.ParentOwner)
                Debug.Print("DatasetTargetName:     " & pReplicaDataset.TargetName)
                Debug.Print("DatasetType:           " & pReplicaDataset.Type.ToString)
                Debug.Print("DatasetId:             " & pReplicaDataset.DatasetID.ToString)
                Debug.Print("DatasetReplicaId:      " & pReplicaDataset.ReplicaID.ToString)

                Debug.Print("RowsType:              " & pRepFilterDesc.RowsType(i).ToString)
                Debug.Print("TableUsesQueryGeometry:" & pRepFilterDesc.TableUsesQueryGeometry(i).ToString)
                Debug.Print("SpatialRelation:       " & pRepFilterDesc.SpatialRelation.ToString)
                Debug.Print("TableUsesDefQuery:     " & pRepFilterDesc.TableUsesDefQuery(i).ToString)
                Debug.Print("TableDefQuery:         " & pRepFilterDesc.TableDefQuery(i))
                Debug.Print("TableUsesSelection:    " & pRepFilterDesc.TableUsesSelection(i).ToString)
                If pRepFilterDesc.TableUsesSelection(i) Then Debug.Print("TableSelectionCount:   " & pRepFilterDesc.TableSelection(i).Count.ToString)

                'Extraire le prochain Dataset
                pReplicaDataset = CType(pEnumDataset.Next, IReplicaDataset2)
                i = i + 1
            Loop

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pRepFilterDesc = Nothing
            pEnumDataset = Nothing
            pReplicaDataset = Nothing
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
    Public Function InitGeoDataServerFromFile(ByVal sNomGeodatabase As String) As IGeoDataServer
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
    ''' Fonction qui permet de définir une géodatabase SDE utilisée dans un réplica à partir d'une chaine de caractères de connexion.
    '''</summary>
    '''
    '''<param name="sConnectionString">Chaine de caractères de connexion à une Base de données SDE. Ex: "SERVER=bobmk;INSTANCE=5151;VERSION=sde.DEFAULT;USER=gdb;PASSWORD=gdb"</param>
    ''' 
    ''' <returns>IGeoDataServer contenant l'information de la géodatabase utilisée pour un réplica.</returns>
    ''' 
    Public Function InitGeoDataServerFromConnectionString(ByVal sConnectionString As String) As IGeoDataServer
        'Déclarer les variables de travail
        Dim pGeoDataServer As IGeoDataServer = Nothing          'Interface contenant l'information de la géodatabase utilisée pour un réplica.
        Dim pGeoDataServerInit As IGeoDataServerInit = Nothing  'Interface pour initialiser l'information de la géodatabase utilisée pour un réplica.

        Try
            'Interface contenant l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServer = New GeoDataServer

            'Interface pour initialiser l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServerInit = CType(pGeoDataServer, IGeoDataServerInit)

            'Initialiser l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServerInit.InitFromConnectionString(sConnectionString)

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
    ''' Fonction qui permet de définir une géodatabase utilisée dans un réplica à partir d'un Workspace.
    '''</summary>
    '''
    '''<param name="pWorkspace">Interface contenant une Géodatabase.</param>
    ''' 
    ''' <returns>IGeoDataServer contenant l'information de la géodatabase utilisée pour un réplica.</returns>
    ''' 
    Public Function InitGeoDataServerFromWorkspace(ByVal pWorkspace As IWorkspace) As IGeoDataServer
        'Déclarer les variables de travail
        Dim pGeoDataServer As IGeoDataServer = Nothing          'Interface contenant l'information de la géodatabase utilisée pour un réplica.
        Dim pGeoDataServerInit As IGeoDataServerInit = Nothing  'Interface pour initialiser l'information de la géodatabase utilisée pour un réplica.

        Try
            'Interface contenant l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServer = New GeoDataServer

            'Interface pour initialiser l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServerInit = CType(pGeoDataServer, IGeoDataServerInit)

            'Initialiser l'information de la géodatabase utilisée pour un réplica.
            pGeoDataServerInit.InitWithWorkspace(pWorkspace)

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
    ''' Fonction qui permet de créer un réplica d'extraction de données dans une géodatabase .mdb ou .gdb à partir d'une géodatabase SDE.
    '''</summary>
    '''
    '''<param name="pParentGDS">Interface contenant l'information de la Géodatabase SDE.</param>
    '''<param name="pChildGDS">Interface contenant l'information de la Géodatabase mdb ou gdb.</param>
    '''<param name="sListeNomClasse">Liste des noms des classe à extraire spéparer par des virgule en incluant le nom du propriétaire.</param>
    '''<param name="sRequeteAttributive">Requête attributive à appliquer sur toutes les classes à extraire.</param>
    '''<param name="pTypeModel">Indique le type de model Simple ou complet.</param>
    '''<param name="pGeometry">Indique la géométrie utiliser pour effectuer la requête spatiale.</param>
    '''<param name="pSpatialRelation">Indique le type de requête spatiale à effecter.</param>
    ''' 
    '''<remarks>Si une des classe est déjà présente, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub ExtractDataReplica(ByVal pParentGDS As IGeoDataServer, ByVal pChildGDS As IGeoDataServer,
                                  ByVal sListeNomClasse As String, ByVal sRequeteAttributive As String,
                                  Optional ByVal pTypeModel As esriReplicaModelType = esriReplicaModelType.esriModelTypeSimple,
                                  Optional ByVal pGeometry As IGeometry = Nothing,
                                  Optional ByVal pSpatialRelation As esriSpatialRelEnum = esriSpatialRelEnum.esriSpatialRelIntersects)
        'Déclarer les variables de travail
        Dim pGPReplicaDataset As IGPReplicaDataset = Nothing        'Interface pour définir la classe à extraire de la géodatabase source.
        Dim pGPReplicaDatasets As IGPReplicaDatasets = Nothing      'Interface pour définir toutes les classes à extraire dans le IGeoDataServer parent.
        Dim pGPReplicaDatasetsExpand As IGPReplicaDatasets = Nothing 'Interface pour définir la liste des classes à extraire dans le IGeoDataServer parent
        Dim pGPReplicaDesc As IGPReplicaDescription = Nothing       'Interface pour décrire le réplica à utiliser.
        Dim pGPReplicaOptions As IGPReplicaOptions2 = Nothing       'Interface pour définir les options du réplica
        Dim pReplicationAgent As IReplicationAgent = Nothing        'Interface pour exécuter le traitement de réplication.
        Dim sNomClasse As String = Nothing      'Nom de la classe à traiter.

        Try
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
                'Ajouter la classe à extraire dans la géodatabase source
                pGPReplicaDatasets.Add(pGPReplicaDataset)
            Next
            'Définir la liste des classes à extraire dans le IGeoDataServer parent
            pGPReplicaDatasetsExpand = pParentGDS.ExpandReplicaDatasets(pGPReplicaDatasets)

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
            pGPReplicaDesc.SpatialRelation = esriSpatialRelEnum.esriSpatialRelIndexIntersects

            'Interface pour exécuter le traitement de réplication
            pReplicationAgent = New ReplicationAgent
            'Exécuter le traitement de réplication d'extraction de données
            pReplicationAgent.ExtractData("", pParentGDS, pChildGDS, pGPReplicaDesc)

        Catch comExc As COMException
            Throw New Exception(String.Format("Create replica errored: {0}, Error Code: {1}", comExc.Message, comExc.ErrorCode), comExc)
        Catch exc As Exception
            Throw New Exception(String.Format("Create replica errored: {0}", exc.Message), exc)
        Finally
            'Vider la mémoire
            pGPReplicaDataset = Nothing
            pGPReplicaDatasets = Nothing
            pGPReplicaDatasetsExpand = Nothing
            pGPReplicaDesc = Nothing
            pReplicationAgent = Nothing
            sNomClasse = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de créer un réplica de type CheckOut dans une géodatabase .mdb ou .gdb à partir d'une géodatabase SDE.
    '''</summary>
    '''
    '''<param name="pParentGDS">Interface contenant l'information de la Géodatabase SDE.</param>
    '''<param name="pChildGDS">Interface contenant l'information de la Géodatabase mdb ou gdb.</param>
    '''<param name="sListeNomClasse">Liste des noms des classe à extraire spéparer par des virgule en incluant le nom du propriétaire.</param>
    '''<param name="sRequeteAttributive">Requête attributive à appliquer sur toutes les classes à extraire.</param>
    '''<param name="pTypeModel">Indique le type de model Simple ou complet.</param>
    '''<param name="pGeometry">Indique la géométrie utiliser pour effectuer la requête spatiale.</param>
    '''<param name="pSpatialRelation">Indique le type de requête spatiale à effecter.</param>
    ''' 
    '''<remarks>Si une des classe est déjà présente, une erreur de traitement sera retournée.</remarks>
    ''' 
    Public Sub CheckOutReplica(ByVal sReplicaName As String, ByVal pParentGDS As IGeoDataServer, ByVal pChildGDS As IGeoDataServer,
                               ByVal sListeNomClasse As String, ByVal sRequeteAttributive As String,
                               Optional ByVal pTypeModel As esriReplicaModelType = esriReplicaModelType.esriModelTypeSimple,
                               Optional ByVal pGeometry As IGeometry = Nothing,
                               Optional ByVal pSpatialRelation As esriSpatialRelEnum = esriSpatialRelEnum.esriSpatialRelIntersects)
        'Déclarer les variables de travail
        Dim pGPReplicaDataset As IGPReplicaDataset = Nothing        'Interface pour définir la classe à extraire de la géodatabase source.
        Dim pGPReplicaDatasets As IGPReplicaDatasets = Nothing      'Interface pour définir toutes les classes à extraire dans le IGeoDataServer parent.
        Dim pGPReplicaDatasetsExpand As IGPReplicaDatasets = Nothing 'Interface pour définir la liste des classes à extraire dans le IGeoDataServer parent
        Dim pGPReplicaDesc As IGPReplicaDescription = Nothing       'Interface pour décrire le réplica à utiliser.
        Dim pGPReplicaOptions As IGPReplicaOptions2 = Nothing       'Interface pour définir les options du réplica
        Dim pReplicationAgent As IReplicationAgent = Nothing        'Interface pour exécuter le traitement de réplication.
        Dim sNomClasse As String = Nothing      'Nom de la classe à traiter.

        Try
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
                'Ajouter la classe à extraire dans la géodatabase source
                pGPReplicaDatasets.Add(pGPReplicaDataset)
            Next
            'Définir la liste des classes à extraire dans le IGeoDataServer parent
            pGPReplicaDatasetsExpand = pParentGDS.ExpandReplicaDatasets(pGPReplicaDatasets)

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
            pGPReplicaDesc.SpatialRelation = esriSpatialRelEnum.esriSpatialRelIndexIntersects

            'Interface pour définir les options du réplica
            pGPReplicaOptions = New GPReplicaOptions
            'Indiquer que le réplica est CheckOut
            pGPReplicaOptions.AccessType = esriReplicaAccessType.esriReplicaAccessNone
            'Indiquer qu'il n'y a pas de résolution de conflit pour la destination
            pGPReplicaOptions.ChildReconcilePolicy = esriReplicaReconcilePolicyType.esriReplicaResolveConflictsNone
            'Indiquer qu'il n'y a pas de résolution de conflit pour la source
            pGPReplicaOptions.ParentReconcilePolicy = esriReplicaReconcilePolicyType.esriReplicaResolveConflictsNone
            'Indiquer que c'est la première fois que le réplica est exécuté
            pGPReplicaOptions.IsChildFirstSender = True
            'Indiquer que le réplica n'est pas enregistrer
            pGPReplicaOptions.RegisterReplicaOnly = False
            'Indiquer que le réplica n'utilise pas l'archivage
            pGPReplicaOptions.UseArchiving = False

            'Interface pour exécuter le traitement de réplication
            pReplicationAgent = New ReplicationAgent
            'Exécuter le traitement de réplication CheckOut
            pReplicationAgent.CreateReplica("", pParentGDS, pChildGDS, sReplicaName, pGPReplicaDesc, pGPReplicaOptions)

        Catch comExc As COMException
            Throw New Exception(String.Format("Create replica errored: {0}, Error Code: {1}", comExc.Message, comExc.ErrorCode), comExc)
        Catch exc As Exception
            Throw New Exception(String.Format("Create replica errored: {0}", exc.Message), exc)
        Finally
            'Vider la mémoire
            pGPReplicaDataset = Nothing
            pGPReplicaDatasets = Nothing
            pGPReplicaDatasetsExpand = Nothing
            pGPReplicaDesc = Nothing
            pGPReplicaOptions = Nothing
            pReplicationAgent = Nothing
            sNomClasse = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de synchroniser un réplica de type CheckOut d'une géodatabase SDE à partir d'une géodatabase .mdb ou .gdb.
    '''</summary>
    '''
    '''<param name="sReplicaName">Nom du réplica à traiter.</param>
    '''<param name="pParentGDS">Interface contenant l'information de la Géodatabase SDE.</param>
    '''<param name="pChildGDS">Interface contenant l'information de la Géodatabase mdb ou gdb.</param>
    '''<param name="pConflictPolicy">Méthode de traitement des conflits.</param>
    '''<param name="bColumnLevel">Indique si les conflits sont extrait par colonne.</param>
    ''' 
    '''<remarks>Si le réplica est absent, une erreur est retournée.</remarks>
    ''' 
    Public Sub CheckInReplica(ByVal sReplicaName As String, ByVal pParentGDS As IGeoDataServer, ByVal pChildGDS As IGeoDataServer,
                              ByVal pConflictPolicy As esriReplicationAgentReconcilePolicy, ByVal bColumnLevel As Boolean)
        'Déclarer les variables de travail
        Dim pGPReplicas As IGPReplicas = Nothing                'Interface pour extraire tous les réplicas de la Géodatabase SDE.
        Dim pCurrentReplica As IGPReplica = Nothing             'Interface contenant l'information du réplica courant.
        Dim pParentReplica As IGPReplica = Nothing              'Interface contenant le réplica contenu dans la Géodatabase SDE.
        Dim pChildReplica As IGPReplica = Nothing               'Interface contenant le réplica contenu dans la Géodatabase .mdb ou .gdb.
        Dim pReplicationAgent As IReplicationAgent = Nothing    'Interface pour exécuter le traitement de synchronisation du réplication.
        Dim sCurrentReplicaName As String = Nothing     'Nom du réplica courant.
        Dim sBaseName As String = Nothing               'Nom du réplica courant sans le propriétaire.
        Dim iDotIndex As Integer = Nothing              'Position du point dans le nom du réplica.

        Try
            'Extraire tous les réplicas de la Géodatabase SDE
            pGPReplicas = pParentGDS.Replicas
            'Traiter tous les réplicas de la Géodatabase SDE
            For i As Integer = 0 To pGPReplicas.Count - 1
                'Interface contenant l'information du réplica courant
                pCurrentReplica = pGPReplicas.Element(i)
                'Extraire le nom du réplica courant
                sCurrentReplicaName = pCurrentReplica.Name
                'Extraire la position du point dans le nom du réplica
                iDotIndex = sCurrentReplicaName.LastIndexOf(".") + 1
                'Extraire le nom du réplica dans le propriétaire
                sBaseName = sCurrentReplicaName.Substring(iDotIndex, sCurrentReplicaName.Length - iDotIndex)
                'Vérifier si le réplica courant correspond au réplica à traiter
                If sBaseName.ToLower() = sReplicaName.ToLower() Then
                    'Définir le réplica contenu dans la Géodatabase SDE
                    pParentReplica = pCurrentReplica
                    'Sortir de la boucle
                    Exit For
                End If
            Next i

            'Vérifier si le réplica parent est trouvé
            If pParentReplica Is Nothing Then
                'Message d'erreur
                Throw New ArgumentException("Le nom du réplica est absent de la Géodatabase SDE.")
            End If

            'Extraire tous les réplicas de la Géodatabase .mdb ou .gdb
            pGPReplicas = pChildGDS.Replicas
            'Traiter tous les réplicas de la Géodatabase .mdb ou .gdb
            For i As Integer = 0 To pGPReplicas.Count - 1
                'Interface contenant l'information du réplica courant
                pCurrentReplica = pGPReplicas.Element(i)
                'Extraire le nom du réplica courant
                sCurrentReplicaName = pCurrentReplica.Name
                'Extraire la position du point dans le nom du réplica
                iDotIndex = sCurrentReplicaName.LastIndexOf(".") + 1
                'Extraire le nom du réplica dans le propriétaire
                sBaseName = sCurrentReplicaName.Substring(iDotIndex, sCurrentReplicaName.Length - iDotIndex)
                'Vérifier si le réplica courant correspond au réplica à traiter
                If sBaseName.ToLower() = sReplicaName.ToLower() Then
                    'Définir le réplica contenu dans la Géodatabase .mdb ou .gdb
                    pChildReplica = pCurrentReplica
                    'Sortir de la boucle
                    Exit For
                End If
            Next i

            'Vérifier si le réplica parent est trouvé
            If pChildReplica Is Nothing Then
                'Message d'erreur
                Throw New ArgumentException("Le nom du réplica est absent de la Géodatabase .mdb ou .gdb.")
            End If

            'Interface pour exécuter le traitement de synchronisation du réplication
            pReplicationAgent = New ReplicationAgent
            'Exécuter le traitement de réplication CheckIn
            pReplicationAgent.SynchronizeReplica(pParentGDS, pChildGDS, pParentReplica, pChildReplica, pConflictPolicy,
                                                 esriReplicaSynchronizeDirection.esriReplicaSynchronizeFromReplica2ToReplica1, bColumnLevel)

        Catch comExc As COMException
            Throw New Exception(String.Format("Create replica errored: {0}, Error Code: {1}", comExc.Message, comExc.ErrorCode), comExc)
        Catch exc As Exception
            Throw New Exception(String.Format("Create replica errored: {0}", exc.Message), exc)
        Finally
            'Vider la mémoire
            pGPReplicas = Nothing
            pCurrentReplica = Nothing
            pParentReplica = Nothing
            pChildReplica = Nothing
            pReplicationAgent = Nothing
            sCurrentReplicaName = Nothing
            sBaseName = Nothing
            iDotIndex = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter une classe ou une table dans un réplica existant de destination.
    '''</summary>
    '''
    '''<param name="pWorkspaceChild">Interface contenant la géodatabase de destination.</param>
    '''<param name="sReplicaName">Nom du réplica à traiter.</param>
    '''<param name="sDatasetName">Nom du dataset à ajouter dans le réplica existant.</param>
    '''<param name="sParentDatabase">Nom de la géodatabase SDE source.</param>
    '''<param name="sParentOwner">Nom du propriétaire du dataset dans la géodatabase SDE source.</param>
    '''<param name="pDatasetType">Type de dataset à ajouter.</param>
    '''<param name="pRowsType">Critère qui permet de déterminer quel colonne doit être extrait dans le dataset à ajouter.</param>
    '''<param name="bUseGeometry">Indique si on utilise une géométrie pour extraire.</param>
    '''<param name="sQueryDef">Requête attributive utilisée pour extraire les données dans le dataset à ajouter dans le réplica de destination.</param>
    ''' 
    '''<remarks>Si le réplica est absent, une erreur est retournée.</remarks>
    ''' 
    Public Sub AddDatasetToReplica(ByVal pWorkspaceChild As IWorkspace, ByVal sReplicaName As String, _
                                   ByVal sDatasetName As String, ByVal sParentDatabase As String, ByVal sParentOwner As String, _
                                   ByVal pDatasetType As esriDatasetType, ByVal pRowsType As esriRowsType, ByVal bUseGeometry As Boolean, _
                                   ByVal sQueryDef As String)
        'Déclarer les variables de travail
        Dim pWorkspaceReplicas As IWorkspaceReplicas2 = Nothing         'Interface pour trouver un réplica existant.
        Dim pReplica As IReplica = Nothing                              'Interface contenant un réplica existant.
        Dim pReplicaDataset As IReplicaDataset = Nothing                'Interface contenant le nouveau dataset à ajouter dans le réplica existant.
        Dim pReplicaDatasetEdit As IReplicaDatasetEdit = Nothing        'Interface qui permet de définir le nouveau dataset à ajouter dans le réplica existant.
        Dim pWorkspaceReplicasAdmin As IWorkspaceReplicasAdmin2 = Nothing 'Interface pour ajouter le datasetd e la géodatabase SDE dans le réplica de destination.

        Try
            'Interface pour trouver un réplica existant dans la géodatabase de destination
            pWorkspaceReplicas = CType(pWorkspaceChild, IWorkspaceReplicas2)
            'Trouver un réplica existant dans la géodatabase de destination
            pReplica = pWorkspaceReplicas.ReplicaByName(sReplicaName)

            'Interface contenant le nouveau dataset à ajouter dans le réplica existant
            pReplicaDataset = New ReplicaDataset
            'Interface qui permet de définir le nouveau dataset à ajouter dans le réplica existant.
            pReplicaDatasetEdit = CType(pReplicaDataset, IReplicaDatasetEdit)
            'Définir le type du dataset à ajouter
            pReplicaDatasetEdit.Type = pDatasetType
            'Définir le nom du dataset
            pReplicaDatasetEdit.Name = sDatasetName
            'Définir le nom de la géodatabase SDE dans laquelle le dataset doit être extrait
            pReplicaDatasetEdit.ParentDatabase = sParentDatabase
            'Définir le nom du propriétaire du dataset dans la la géodatabase SDE
            pReplicaDatasetEdit.ParentOwner = sParentOwner
            'Définir le nom du réplica de la géodatabase SDE
            pReplicaDatasetEdit.ReplicaID = pReplica.ReplicaID

            'Interface pour ajouter le datasetd e la géodatabase SDE dans le réplica de destination
            pWorkspaceReplicasAdmin = CType(pWorkspaceReplicas, IWorkspaceReplicasAdmin2)
            Try
                'Ajouter le dataset de la géodatabase SDE dans le réplica de destination
                'Attention: Le paramètre pSelID n'est pas supporté et doit toujours être Nothing
                pWorkspaceReplicasAdmin.RegisterReplicaDataset(pReplicaDataset, pRowsType, bUseGeometry, sQueryDef, Nothing, pReplica)

            Catch comExc As COMException
                ' Handle the exception appropriately for the application.
            End Try

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pWorkspaceReplicas = Nothing
            pReplica = Nothing
            pReplicaDataset = Nothing
            pReplicaDatasetEdit = Nothing
            pWorkspaceReplicasAdmin = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter l'attribut GlobalId dans une table d'une Géodatabase.
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant la table dans laquelle l'attribut GlobalId sera ajouté.</param>
    '''<param name="sGlobalIdFieldName">Nom de l'attribut GlobalId.</param>
    ''' 
    Public Sub AddGlobalID(ByVal pTable As ITable, Optional ByVal sGlobalIdFieldName As String = "GlobalId")
        'Déclarer les variables de travail
        Dim pSchemaLock As ISchemaLock = Nothing            'Interface pour bloquer/débloquer une Géodatabase.
        Dim pClassSchemaEdit As IClassSchemaEdit3 = Nothing 'Interface pour ajouter l'attribut GlobalId pour tous les éléments de la table.

        Try
            'Interface pour bloquer/débloquer une Géodatabase
            pSchemaLock = CType(pTable, ISchemaLock)
            'Bloquer une Géodatabase de façon exclusive
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            'Interface pour ajouter l'attribut GlobalId pour tous les éléments de la table
            pClassSchemaEdit = CType(pTable, IClassSchemaEdit3)
            'Ajouter l'attribut GlobalId pour tous les éléments de la table
            pClassSchemaEdit.AddGlobalID(sGlobalIdFieldName)

        Catch comExc As COMException
            'Message d'erreur
            Throw
        Finally
            'Débloquer la Géodatabase
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
            'Vider la mémoire
            pSchemaLock = Nothing
            pClassSchemaEdit = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire l'attribut GlobalId dans une table d'une Géodatabase.
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant la table dans laquelle l'attribut GlobalId sera détruit.</param>
    ''' 
    Public Sub RemoveGlobalID(ByVal pTable As ITable)
        'Déclarer les variables de travail
        Dim pSchemaLock As ISchemaLock = Nothing            'Interface pour bloquer/débloquer une Géodatabase.
        Dim pClassSchemaEdit As IClassSchemaEdit3 = Nothing 'Interface pour détruire l'attribut GlobalId pour tous les éléments de la table.

        Try
            'Interface pour bloquer/débloquer une Géodatabase
            pSchemaLock = CType(pTable, ISchemaLock)
            'Bloquer une Géodatabase de façon exclusive
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            'Interface pour détruire l'attribut GlobalId pour tous les éléments de la table
            pClassSchemaEdit = CType(pTable, IClassSchemaEdit3)
            'Détruire l'attribut GlobalId pour tous les éléments de la table
            pClassSchemaEdit.DeleteGlobalID()

        Catch comExc As COMException
            'Message d'erreur
            Throw
        Finally
            'Débloquer la Géodatabase
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
            'Vider la mémoire
            pSchemaLock = Nothing
            pClassSchemaEdit = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de dessiner dans la vue active les géométries Point, MultiPoint, 
    ''' Polyline et/ou Polygon. Ces géométries peuvent être contenu dans un GeometryBag. 
    ''' Un point est représenté par un carré, une ligne est représentée par une ligne pleine 
    ''' et la surface est représentée par une ligne pleine pour la limite et des lignes à
    ''' 45 dégrés pour l'intérieur. On peut afficher le numéro de la géométrie pour un GeometryBag.
    '''</summary>
    '''
    '''<param name="pGeometry"> Interface ESRI contenant la géométrie èa dessiner.</param>
    '''<param name="bRafraichir"> Indique si on doit rafraîchir la vue active.</param>
    '''<param name="bGeometrie"> Indique si on doit dessiner la géométrie.</param>
    '''<param name="bSommet"> Indique si on doit dessiner les sommets de la géométrie.</param>
    ''' 
    '''<return>Un booleen est retourner pour indiquer la fonction s'est bien exécutée.</return>
    ''' 
    Public Function bDessinerGeometrie(ByVal pGeometry As IGeometry,
                                       Optional ByVal bRafraichir As Boolean = False, _
                                       Optional ByVal bGeometrie As Boolean = False,
                                       Optional ByVal bSommet As Boolean = False) As Boolean
        'Déclarer les variables de travail
        Dim pScreenDisplay As IScreenDisplay = Nothing  'Interface ESRI contenant le document de ArcMap.
        Dim pGeomColl As IGeometryCollection = Nothing  'Interface ESRI contenant la fenêtre d'affichage.
        Dim pPath As IPolyline = Nothing                'Interface ESRI contenant la polyline du Path.
        Dim pGeomTexte As IGeometry = Nothing           'Interface ESRI pour la position du texte d'une surface.

        Try
            'Vérifier si la géométrie est absente
            If pGeometry Is Nothing Then Exit Function

            'Vérifier si la géométrie est vide
            If pGeometry.IsEmpty Then Exit Function

            'Initialiser les variables de travail
            pScreenDisplay = m_MxDocument.ActiveView.ScreenDisplay

            'Vérifier si on doit rafraichir l'écran
            If bRafraichir Then
                'Rafraîchier l'affichage
                m_MxDocument.ActiveView.Refresh()
                System.Windows.Forms.Application.DoEvents()
            End If

            'Vérifier si la géométrie est un GeometryBag
            If pGeometry.GeometryType = esriGeometryType.esriGeometryBag Then
                'Interface pour traiter toutes les géométries présentes dans le GeometryBag
                pGeomColl = CType(pGeometry, IGeometryCollection)

                'Dessiner toutes les géométrie présentes dans une collection de géométrie
                For i = 0 To pGeomColl.GeometryCount - 1
                    'Vérifier s'il faut dessiner la géométrie
                    If bGeometrie Then
                        'Dessiner la géométrie contenu dans un GeometrieBag
                        Call bDessinerGeometrie(pGeomColl.Geometry(i), False, bGeometrie, False)
                    End If

                    'Vérifier s'il faut dessiner les sommets de la géométrie
                    If bSommet Then
                        'Dessiner les sommets de la géométrie contenu dans un GeometrieBag
                        Call bDessinerSommet(pGeomColl.Geometry(i), False)
                    End If
                Next i

                'Vérifier si la géométrie est un point
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryPoint Then
                'Transformation du système de coordonnées selon la vue active
                pGeometry.Project(m_MxDocument.FocusMap.SpatialReference)

                'Vérifier s'il faut dessiner la géométrie
                If bGeometrie Then
                    'Afficher la géométrie avec sa symbologie dans la vue active
                    With pScreenDisplay
                        .StartDrawing(pScreenDisplay.hDC, CType(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache, Short))
                        .SetSymbol(mpSymbolePoint)
                        .DrawPoint(pGeometry)
                        .FinishDrawing()
                    End With
                End If

                'Vérifier si la géométrie est un multi-point
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryMultipoint Then
                'Transformation du système de coordonnées selon la vue active
                pGeometry.Project(m_MxDocument.FocusMap.SpatialReference)

                'Vérifier s'il faut dessiner la géométrie
                If bGeometrie Then
                    'Afficher la géométrie avec sa symbologie dans la vue active
                    With pScreenDisplay
                        .StartDrawing(pScreenDisplay.hDC, CType(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache, Short))
                        .SetSymbol(mpSymbolePoint)
                        .DrawMultipoint(pGeometry)
                        .FinishDrawing()
                    End With
                End If

                'Vérifier s'il faut dessiner les sommets de la géométrie
                If bSommet Then
                    'Dessiner les sommets de la géométrie contenu dans un GeometrieBag
                    Call bDessinerSommet(pGeometry, False)
                End If

                'Vérifier si la géométrie est une ligne
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryPolyline Then
                'Transformation du système de coordonnées selon la vue active
                pGeometry.Project(m_MxDocument.FocusMap.SpatialReference)

                'Vérifier s'il faut dessiner la géométrie
                If bGeometrie Then
                    'Afficher la géométrie avec sa symbologie dans la vue active
                    With pScreenDisplay
                        .StartDrawing(pScreenDisplay.hDC, CType(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache, Short))
                        .SetSymbol(mpSymboleLigne)
                        .DrawPolyline(pGeometry)
                        .FinishDrawing()
                    End With
                End If

                'Vérifier s'il faut dessiner les sommets de la géométrie
                If bSommet Then
                    'Dessiner les sommets de la géométrie contenu dans un GeometrieBag
                    Call bDessinerSommet(pGeometry, False)
                End If

                'Vérifier si la géométrie est une surface
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryPolygon _
            Or pGeometry.GeometryType = esriGeometryType.esriGeometryEnvelope Then
                'Transformation du système de coordonnées selon la vue active
                pGeometry.Project(m_MxDocument.FocusMap.SpatialReference)

                'Vérifier s'il faut dessiner la géométrie
                If bGeometrie Then
                    'Afficher la géométrie avec sa symbologie dans la vue active
                    With pScreenDisplay
                        .StartDrawing(pScreenDisplay.hDC, CType(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache, Short))
                        .SetSymbol(mpSymboleSurface)
                        .DrawPolygon(pGeometry)
                        .FinishDrawing()
                    End With
                End If

                'Vérifier s'il faut dessiner les sommets de la géométrie
                If bSommet Then
                    'Dessiner les sommets de la géométrie contenu dans un GeometrieBag
                    Call bDessinerSommet(pGeometry, False)
                End If
            End If

            'Retourner le résultat
            bDessinerGeometrie = True

        Catch erreur As Exception
            'Retourner l'erreur
            Throw erreur
        Finally
            pScreenDisplay = Nothing
            pGeomColl = Nothing
            pPath = Nothing
            pGeomTexte = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de dessiner dans la vue active les sommets des géométries Point, MultiPoint, Polyline et/ou Polygon.
    ''' Ces géométries peuvent être contenu dans un GeometryBag. Les sommets sont représentés par un cercle.
    '''</summary>
    '''
    '''<param name="pGeometry"> Interface ESRI contenant la géométrie utilisée pour dessiner les sommets.</param>
    '''<param name="bRafraichir"> Indique si on doit rafraîchir la vue active.</param>
    ''' 
    '''<return>Un booleen est retourner pour indiquer la fonction s'est bien exécutée.</return>
    ''' 
    Public Function bDessinerSommet(ByVal pGeometry As IGeometry, _
                                    Optional ByVal bRafraichir As Boolean = False) As Boolean
        'Déclarer les variables de travail
        Dim pScreenDisplay As IScreenDisplay = Nothing  'Interface ESRI contenant le document de ArcMap.
        Dim pGeomColl As IGeometryCollection = Nothing  'Interface ESRI contenant la fenêtre d'affichage.
        Dim pMultiPoint As IMultipoint = Nothing        'Interface contenant les sommets de la géométrie
        Dim pPointColl As IPointCollection = Nothing    'Interface utilisée pour transformer la géométrie en multipoint

        Try
            'Vérifier si la géométrie est absente
            If pGeometry Is Nothing Then Exit Function

            'Vérifier si la géométrie est vide
            If pGeometry.IsEmpty Then Exit Function

            'Initialiser les variables de travail
            pScreenDisplay = m_MxDocument.ActiveView.ScreenDisplay

            'Vérifier si on doit rafraichir l'écran
            If bRafraichir Then
                'Rafraîchier l'affichage
                m_MxDocument.ActiveView.Refresh()
                System.Windows.Forms.Application.DoEvents()
            End If

            'Transformation du système de coordonnées selon la vue active
            pGeometry.Project(m_MxDocument.FocusMap.SpatialReference)

            'Vérifier si la géométrie est un GeometryBag
            If pGeometry.GeometryType = esriGeometryType.esriGeometryBag Then
                'Interface pour traiter toutes les géométries présentes dans le GeometryBag
                pGeomColl = CType(pGeometry, IGeometryCollection)

                'Dessiner toutes les géométrie présentes dans une collection de géométrie
                For i = 0 To pGeomColl.GeometryCount - 1
                    'Dessiner les sommets de la géométrie contenu dans un GeometrieBag
                    Call bDessinerSommet(pGeomColl.Geometry(i), False)
                Next i

                'Vérifier si la géométrie est un point
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryPoint Then
                'Afficher la géométrie avec sa symbologie dans la vue active
                With pScreenDisplay
                    .StartDrawing(pScreenDisplay.hDC, CType(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache, Short))
                    .SetSymbol(mpSymboleSommet)
                    .DrawPoint(pGeometry)
                    .FinishDrawing()
                End With

                'Vérifier si la géométrie est un multi-point
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryMultipoint Then
                'Afficher la géométrie avec sa symbologie dans la vue active
                With pScreenDisplay
                    .StartDrawing(pScreenDisplay.hDC, CType(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache, Short))
                    .SetSymbol(mpSymboleSommet)
                    .DrawMultipoint(pGeometry)
                    .FinishDrawing()
                End With

                'Vérifier si la géométrie est une ligne ou une surface
            Else
                'Créer un nouveau multipoint vide
                pMultiPoint = CType(New Multipoint, IMultipoint)
                pMultiPoint.SpatialReference = pGeometry.SpatialReference

                'Transformer la géométrie en multipoint
                pPointColl = CType(pMultiPoint, IPointCollection)
                pPointColl.AddPointCollection(CType(pGeometry, IPointCollection))

                'Afficher les sommets de la géométrie avec la symbologie des sommets dans la vue active
                With pScreenDisplay
                    .StartDrawing(pScreenDisplay.hDC, CType(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache, Short))
                    .SetSymbol(mpSymboleSommet)
                    .DrawMultipoint(pMultiPoint)
                    .FinishDrawing()
                End With
            End If

            'Retourner le résultat
            bDessinerSommet = True

        Catch erreur As Exception
            'Retourner l'erreur
            Throw erreur
        Finally
            pScreenDisplay = Nothing
            pGeomColl = Nothing
            pMultiPoint = Nothing
            pPointColl = Nothing
        End Try
    End Function

    '''<summary>
    ''' Initialiser les couleurs par défaut pour le texte qui sera affiché avec les
    ''' géométries déssiné et initialiser les 3 couleurs pour les géométries de type
    ''' point, ligne et surface.
    '''</summary>
    '''
    Public Sub InitSymbole()
        'Déclarer les variables de travail
        Dim pRgbColor As IRgbColor = Nothing                'Interface ESRI contenant la couleur RGB.
        Dim pTextSymbol As ITextSymbol = Nothing            'Interface ESRI contenant un symbole de texte.
        Dim pMarkerSymbol As ISimpleMarkerSymbol = Nothing  'Interface ESRI contenant un symbole de point.
        Dim pLineSymbol As ISimpleLineSymbol = Nothing      'Interface ESRi contenant un symbole de ligne.
        Dim pFillSymbol As ISimpleFillSymbol = Nothing      'Interface ESRI contenant un symbole de surface.

        'Permet d'initialiser la symbologie
        Try
            'Vérifier si le symbole est invalide
            If mpSymboleTexte Is Nothing Then
                'Définir la couleur pour le texte
                pRgbColor = New RgbColor
                pRgbColor.RGB = 255
                'Définir la symbologie pour le texte
                pTextSymbol = New ESRI.ArcGIS.Display.TextSymbol
                pTextSymbol.Color = pRgbColor
                pTextSymbol.Font.Bold = True
                pTextSymbol.HorizontalAlignment = esriTextHorizontalAlignment.esriTHACenter
                'Conserver le symbole
                mpSymboleTexte = CType(pTextSymbol, ISymbol)
            End If

            'Vérifier si le symbole est invalide
            If mpSymboleSommet Is Nothing Then
                'Définir la couleur rouge pour le polygon
                pRgbColor = New RgbColor
                pRgbColor.Red = 255
                'Définir la symbologie pour la limite d'un polygone
                pMarkerSymbol = New SimpleMarkerSymbol
                pMarkerSymbol.Color = pRgbColor
                pMarkerSymbol.Style = esriSimpleMarkerStyle.esriSMSCircle
                pMarkerSymbol.Size = 3
                'Conserver le symbole
                mpSymboleSommet = CType(pMarkerSymbol, ISymbol)
            End If

            'Vérifier si le symbole est invalide
            If mpSymbolePoint Is Nothing Then
                'Définir la couleur rouge pour le polygon
                pRgbColor = New RgbColor
                pRgbColor.Red = 255
                'Définir la symbologie pour la limite d'un polygone
                pMarkerSymbol = New SimpleMarkerSymbol
                pMarkerSymbol.Color = pRgbColor
                pMarkerSymbol.Style = esriSimpleMarkerStyle.esriSMSSquare
                pMarkerSymbol.Size = 5
                'Conserver le symbole 
                mpSymbolePoint = CType(pMarkerSymbol, ISymbol)
            End If

            'Vérifier si le symbole est invalide
            If mpSymboleLigne Is Nothing Then
                'Définir la couleur rouge pour le polygon
                pRgbColor = New RgbColor
                pRgbColor.Red = 255
                'Définir la symbologie pour la limite d'un polygone
                pLineSymbol = New SimpleLineSymbol
                pLineSymbol.Color = pRgbColor
                pLineSymbol.Width = 1
                'Conserver le symbole en mémoire
                mpSymboleLigne = CType(pLineSymbol, ISymbol)
            End If

            'Vérifier si le symbole est invalide
            If mpSymboleSurface Is Nothing Then
                'Définir la couleur rouge pour le polygon
                pRgbColor = New RgbColor
                pRgbColor.Red = 255
                'Définir la symbologie pour la limite d'un polygone
                pLineSymbol = New SimpleLineSymbol
                pLineSymbol.Color = pRgbColor
                pLineSymbol.Width = 1
                'Définir la symbologie pour l'intérieur d'un polygone
                pFillSymbol = New SimpleFillSymbol
                pFillSymbol.Color = pRgbColor
                pFillSymbol.Outline = pLineSymbol
                pFillSymbol.Style = esriSimpleFillStyle.esriSFSBackwardDiagonal
                'Conserver le symbole 
                mpSymboleSurface = CType(pFillSymbol, ISymbol)
            End If
        Catch erreur As Exception
            'Retourner l'erreur
            Throw erreur
        Finally
            pRgbColor = Nothing
            pTextSymbol = Nothing
            pMarkerSymbol = Nothing
            pLineSymbol = Nothing
            pFillSymbol = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Initialiser les couleurs par défaut pour dessiner la symbologie des éléments courants.
    '''</summary>
    '''
    Public Sub InitSymboleCourant()
        'Déclarer les variables de travail
        Dim pRgbColor As IRgbColor = Nothing                'Interface ESRI contenant la couleur RGB.
        Dim pMarkerSymbol As ISimpleMarkerSymbol = Nothing  'Interface ESRI contenant un symbole de point.
        Dim pLineSymbol As ISimpleLineSymbol = Nothing      'Interface ESRi contenant un symbole de ligne.
        Dim pFillSymbol As ISimpleFillSymbol = Nothing      'Interface ESRI contenant un symbole de surface.

        'Permet d'initialiser la symbologie
        Try
            'Interface pour changer les paramètres du Symbole des sommets
            pMarkerSymbol = CType(mpSymboleSommet, ISimpleMarkerSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pMarkerSymbol.Color, IRgbColor)
            'Définir la couleur du sommet
            pRgbColor.Green = 0
            'Remettre la couleur du symbole
            pMarkerSymbol.Color = pRgbColor
            'Définir la grosseur du sommet
            pMarkerSymbol.Size = 3

            'Interface pour changer les paramètres du Symbole des points
            pMarkerSymbol = CType(mpSymbolePoint, ISimpleMarkerSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pMarkerSymbol.Color, IRgbColor)
            'Définir la couleur du point
            pRgbColor.Green = 0
            'Remettre la couleur du symbole
            pMarkerSymbol.Color = pRgbColor
            'Définir la grosseur du point
            pMarkerSymbol.Size = 5

            'Interface pour changer les paramètres du Symbole des lignes
            pLineSymbol = CType(mpSymboleLigne, ISimpleLineSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pLineSymbol.Color, IRgbColor)
            'Définir la couleur de la ligne
            pRgbColor.Green = 0
            'Remettre la couleur du symbole
            pLineSymbol.Color = pRgbColor
            'Définir l'épaisseur de la ligne
            pLineSymbol.Width = 1

            'Interface pour changer les paramètres du Symbole des surfaces
            pFillSymbol = CType(mpSymboleSurface, ISimpleFillSymbol)
            'Interface pour changer les paramètres du Symbole des lignes des surfaces
            pLineSymbol = CType(pFillSymbol.Outline, ISimpleLineSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pLineSymbol.Color, IRgbColor)
            'Définir la couleur de la ligne
            pRgbColor.Green = 0
            'Remettre la couleur du symbole
            pLineSymbol.Color = pRgbColor
            'Définir l'épaisseur de la ligne
            pLineSymbol.Width = 1
            'Définir la couleur du symbole de surface
            pFillSymbol.Color = pRgbColor
            'Définir la ligne des surfaces
            pFillSymbol.Outline = pLineSymbol
            'Définir le style de la ligne des surfaces
            pFillSymbol.Style = esriSimpleFillStyle.esriSFSBackwardDiagonal

        Catch erreur As Exception
            'Retourner l'erreur
            Throw erreur
        Finally
            pRgbColor = Nothing
            pMarkerSymbol = Nothing
            pLineSymbol = Nothing
            pFillSymbol = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Initialiser les couleurs par défaut pour dessiner la symbologie des éléments d'archive.
    '''</summary>
    '''
    Public Sub InitSymboleArchive()
        'Déclarer les variables de travail
        Dim pRgbColor As IRgbColor = Nothing                'Interface ESRI contenant la couleur RGB.
        Dim pMarkerSymbol As ISimpleMarkerSymbol = Nothing  'Interface ESRI contenant un symbole de point.
        Dim pLineSymbol As ISimpleLineSymbol = Nothing      'Interface ESRi contenant un symbole de ligne.
        Dim pFillSymbol As ISimpleFillSymbol = Nothing      'Interface ESRI contenant un symbole de surface.

        'Permet d'initialiser la symbologie
        Try
            'Interface pour changer les paramètres du Symbole des sommets
            pMarkerSymbol = CType(mpSymboleSommet, ISimpleMarkerSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pMarkerSymbol.Color, IRgbColor)
            'Définir la couleur du sommet
            pRgbColor.Green = 150
            'Remettre la couleur du symbole
            pMarkerSymbol.Color = pRgbColor
            'Définir la grosseur du sommet
            pMarkerSymbol.Size = 5

            'Interface pour changer les paramètres du Symbole des points
            pMarkerSymbol = CType(mpSymbolePoint, ISimpleMarkerSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pMarkerSymbol.Color, IRgbColor)
            'Définir la couleur du point
            pRgbColor.Green = 150
            'Remettre la couleur du symbole
            pMarkerSymbol.Color = pRgbColor
            'Définir la grosseur du point
            pMarkerSymbol.Size = 5

            'Interface pour changer les paramètres du Symbole des lignes
            pLineSymbol = CType(mpSymboleLigne, ISimpleLineSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pLineSymbol.Color, IRgbColor)
            'Définir la couleur de la ligne
            pRgbColor.Green = 150
            'Remettre la couleur du symbole
            pLineSymbol.Color = pRgbColor
            'Définir l'épaisseur de la ligne
            pLineSymbol.Width = 2

            'Interface pour changer les paramètres du Symbole des surfaces
            pFillSymbol = CType(mpSymboleSurface, ISimpleFillSymbol)
            'Interface pour changer les paramètres du Symbole des lignes des surfaces
            pLineSymbol = CType(pFillSymbol.Outline, ISimpleLineSymbol)
            'Interface pour changer la couleur
            pRgbColor = CType(pLineSymbol.Color, IRgbColor)
            'Définir la couleur de la ligne
            pRgbColor.Green = 150
            'Remettre la couleur du symbole
            pLineSymbol.Color = pRgbColor
            'Définir l'épaisseur de la ligne
            pLineSymbol.Width = 2
            'Définir la couleur du symbole de surface
            pFillSymbol.Color = pRgbColor
            'Définir la ligne des surfaces
            pFillSymbol.Outline = pLineSymbol
            'Définir le style de la ligne des surfaces
            pFillSymbol.Style = esriSimpleFillStyle.esriSFSForwardDiagonal

        Catch erreur As Exception
            'Retourner l'erreur
            Throw erreur
        Finally
            pRgbColor = Nothing
            pMarkerSymbol = Nothing
            pLineSymbol = Nothing
            pFillSymbol = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer un Multipoint à partir d'une géométrie.
    ''' 
    '''<param name="pGeometry"> Interface contenant la géométrie utilisée pour créer le Multipoint.</param>
    '''
    '''<return>Le Multipoint contenant les points de la géométrie spécifiée.</return>
    ''' 
    '''</summary>
    '''
    Public Function GeometrieToMultiPoint(ByVal pGeometry As IGeometry) As IMultipoint
        'Déclarer les variables de travail
        Dim pGeomColl As IPointCollection = Nothing     'Interface pour ajouter les sommets de la géométrie.
        Dim pPointColl As IPointCollection = Nothing    'Interface pour extraire les points de la géométrie.
        Dim pClone As IClone = Nothing                  'Interface pour cloner la géométrie.
        Dim pTopoOp As ITopologicalOperator2 = Nothing  'Interface ESRI utilisée pour simplifier la géométrie.

        'Définir la valeur par défaut
        GeometrieToMultiPoint = New Multipoint
        'Définir la référence spatial
        GeometrieToMultiPoint.SpatialReference = pGeometry.SpatialReference

        Try
            'Interface pour ajouter les points de la géométrie dans le multipoint
            pGeomColl = CType(GeometrieToMultiPoint, IPointCollection)

            'Interface pour clone la géométrie
            pClone = CType(pGeometry, IClone)

            'Vérifier si la géométrie est un point
            If pGeometry.GeometryType = esriGeometryType.esriGeometryPoint Then
                'Ajouter le point dans le multipoint
                pGeomColl.AddPoint(CType(pClone.Clone, IPoint))
                'Si la géométrie est un multipoint
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryMultipoint Then
                'Retourner le Multipoint
                GeometrieToMultiPoint = CType(pClone.Clone, IMultipoint)
                'Si la géométrie est un Polyline
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryPolyline Then
                'Convertir le polyline en multipoint
                pGeomColl.AddPointCollection(CType(pClone.Clone, IPointCollection))
                'Simplifier la géométrie
                pTopoOp = CType(pGeomColl, ITopologicalOperator2)
                pTopoOp.IsKnownSimple_2 = False
                pTopoOp.Simplify()
                'Si la géométrie est un Polygon
            ElseIf pGeometry.GeometryType = esriGeometryType.esriGeometryPolygon Then
                'Convertir le polygon en multipoint
                pGeomColl.AddPointCollection(CType(pClone.Clone, IPointCollection))
                'Simplifier la géométrie
                pTopoOp = CType(pGeomColl, ITopologicalOperator2)
                pTopoOp.IsKnownSimple_2 = False
                pTopoOp.Simplify()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pGeomColl = Nothing
            pPointColl = Nothing
            pClone = Nothing
            pTopoOp = Nothing
        End Try
    End Function
#End Region

#Region "Routine et fonction publiques originales - /DataExtraction/CheckOut/CheckIn"
    'The following shows how to use the OutputSpatialReference parameter when extracting schema.
    Public Sub DataExtract_to_utm13(pRepDSetDesc As IReplicaDescription)
        ' Generate the spatial reference for UTM 13N, NAD83
        Dim pSRFact As ISpatialReferenceFactory
        Dim pPrjCoordSys As IProjectedCoordinateSystem
        Dim pSpRef As ISpatialReference
        pSRFact = New SpatialReferenceEnvironment
        pPrjCoordSys = pSRFact.CreateProjectedCoordinateSystem(esriSRProjCSType.esriSRProjCS_NAD1983UTM_13N)
        pSpRef = pPrjCoordSys
        With pSpRef
            .SetDomain(2212182, 2220772, 386656, 395246)
            .SetFalseOriginAndUnits(500000, 0, 1)
            .SetMDomain(0, 1)
            .SetMFalseOriginAndUnits(1, 1)
            .SetZDomain(0, 1)
            .SetZFalseOriginAndUnits(1, 1)
        End With
        Dim pDataExtraction As IDataExtraction
        pDataExtraction = New DataExtraction
        pDataExtraction.ExtractSchema(pRepDSetDesc, pPrjCoordSys)
    End Sub

    'Run the CO_Layer routine in ArcMap to checkout the feature class associated with the selected layer in the table of contents. 
    'Features that are selected, satisfy the layer definiton query and intersect the geometry of a selected graphic are checked out. 
    'The CreateRepDescription function, which is called by CO_Layer, uses the IReplicaDescription and IReplicaFilterDescriptionEdit interfaces to apply these conditions. 
    Public Sub FirstLayerCheckOut()
        Dim pFeatureLayer As IFeatureLayer
        Dim pParentWorkSpaceName As IWorkspaceName
        Dim pDataset As IDataset
        Dim pFeatureClassName As IFeatureClassName
        Dim pRepDescription As IReplicaDescription
        Dim pWorkSpace As IWorkspace
        Dim pSelectionSet As ISelectionSet
        Dim pDisplayTable As IDisplayTable
        Dim pCheckOut As ICheckOut
        Dim pChildWorkspaceFactory As IWorkspaceFactory
        Dim pChildWorkspaceName As IWorkspaceName
        Dim pTableDef As ITableDefinition
        Dim strFilter As String

        ' Get the first layer
        pFeatureLayer = CType(m_MxDocument.FocusMap.Layer(0), IFeatureLayer)

        ' Make sure the layer is from SDE and get the parent workspace
        pDataset = CType(pFeatureLayer.FeatureClass, IDataset)
        pFeatureClassName = CType(pDataset.FullName, IFeatureClassName)
        pWorkSpace = pDataset.Workspace
        If Not pWorkSpace.Type = esriWorkspaceType.esriRemoteDatabaseWorkspace Then
            MsgBox("Not an SDE feature class")
            Exit Sub
        End If
        pDataset = CType(pWorkSpace, IDataset)
        pParentWorkSpaceName = CType(pDataset.FullName, IWorkspaceName)

        ' Get the selected graphic, if there is one
        Dim pMap As IMap
        Dim pElement As IElement
        Dim pGraphicsConSelect As IGraphicsContainerSelect
        Dim pGeometry As IGeometry = Nothing
        pMap = m_MxDocument.FocusMap
        pGraphicsConSelect = CType(pMap, IGraphicsContainerSelect)
        If pGraphicsConSelect.ElementSelectionCount = 1 Then
            pElement = pGraphicsConSelect.SelectedElement(0)
            pGeometry = pElement.Geometry
        End If
        ' Get the selection set and query def (If there is one)
        pDisplayTable = CType(pFeatureLayer, IDisplayTable)
        pSelectionSet = pDisplayTable.DisplaySelectionSet
        If pSelectionSet.Count = 0 Then pSelectionSet = Nothing
        pTableDef = CType(pFeatureLayer, ITableDefinition)
        strFilter = pTableDef.DefinitionExpression
        ' Create the checkout database
        pChildWorkspaceFactory = New AccessWorkspaceFactory
        pChildWorkspaceName = pChildWorkspaceFactory.Create("D:\VersionTravail", "test", Nothing, 0)
        pRepDescription = CreateRepDescription(pFeatureClassName, pChildWorkspaceName, False, _
                                               pGeometry, pSelectionSet, strFilter)

        ' Checkout
        pCheckOut = New CheckOut
        pCheckOut.CheckOutData(pRepDescription, True, "test_" & pFeatureLayer.Name)
    End Sub

    ' Create a Replica Dataset descrpiton for a single feature class checkout
    Public Function CreateRepDescription(pFeatureClassName As IFeatureClassName, pChildWorkspaceName As IWorkspaceName, _
      bolReuseSchema As Boolean, pGeometry As IGeometry, pSelectionSet As ISelectionSet, _
      strFilter As String) As IReplicaDescription
        Dim pName As IName
        Dim pEnumNameEdit As IEnumNameEdit
        Dim intIndex As Integer
        Dim intDSet As Integer
        Dim pRepDescription As IReplicaDescription
        Dim pRepFilterDescEdit As IReplicaFilterDescriptionEdit

        ' Use the featuredataset if the featureclass is in a featuredataset
        If pFeatureClassName.FeatureDatasetName Is Nothing Then
            pName = CType(pFeatureClassName, IName)
        Else
            pName = CType(pFeatureClassName.FeatureDatasetName, IName)
        End If
        pEnumNameEdit = New NamesEnumerator
        pEnumNameEdit.Add(pName)

        ' Initialize the ReplicaDatasetDescription for the layer
        pRepDescription = New ReplicaDescription
        pRepDescription.Init(CType(pEnumNameEdit, IEnumName), pChildWorkspaceName, bolReuseSchema, esriDataExtractionType.esriDataCheckOut)
        pRepDescription.ReplicaModelType = esriReplicaModelType.esriModelTypeSimple

        ' Apply the selection and geometry filters
        intIndex = pRepDescription.FindTable(CType(pFeatureClassName, IName))
        pRepFilterDescEdit = CType(pRepDescription, IReplicaFilterDescriptionEdit)
        With pRepFilterDescEdit
            .RowsType(intIndex) = esriRowsType.esriRowsTypeFilter
            .TableUsesQueryGeometry(intIndex) = Not (pGeometry Is Nothing)
            .Geometry = pGeometry
            .SpatialRelation = esriSpatialRelEnum.esriSpatialRelIntersects
            .TableUsesDefQuery(intIndex) = Not (strFilter = "")
            .TableDefQuery(intIndex) = strFilter
            .TableUsesSelection(intIndex) = Not (pSelectionSet Is Nothing)
            .TableSelection(intIndex) = pSelectionSet
        End With
        ' If the feature class is part of a feature dataset, all class in the
        ' dataset are included by default. We need to set exclude = true
        ' for all other data in the feature dataset. The check-out may contain dependant classes
        ' such as related tables or the complete geometric network.
        If TypeOf pName Is IFeatureDatasetName Then
            ' initially, exclude all
            For intDSet = 0 To pRepDescription.TableNameCount - 1
                pRepDescription.TableExcluded(intDSet) = True
            Next intDSet
            ' Find the feature class and reset to include it
            pRepDescription.TableExcluded(intIndex) = False
        End If
        CreateRepDescription = pRepDescription
    End Function

    'Select which ever routine is appropriate for your application to check in the changes from a check-out geodatabase or a delta file, 
    'and copy and paste the code into your VB application.
    'The following samples do not reconcile and post the changes to the parent version once the check in has completed 
    'and they do not create the <check-out name>_OM and<check-out name>_RC tables. To enable both these features, set the appropriate parameters for the check in method to TRUE.
    '(The <check-out name>_OM table records the pre- and post- check-in ObjectID valuesfor new features/rows that have been added to feature classes, tables 
    'or attributedrelationship classes in the check-out geodatabase and checked into the mastergeodatabase. 
    'The <check-out name>_RC table records all the changes made to the checked out data - these changes are recorded as inserts (0), updates (1) and deletes (2).)
    Public Sub CheckIn_GDB()
        '++ Checks in changes from a check-out personal geodatabase
        '++ Modify the check-out geodatabase name, master geodatabase connection 
        '++ properties and check-out name as required.
        Dim pMasterWorkspaceName As IWorkspaceName
        Dim pMasterWorkspace As IWorkspace
        Dim pCheckOutWorkspaceName As IWorkspaceName
        Dim pCheckOutWorkspace As IWorkspace
        Dim pCheckOutWorkspaceReplicas As IWorkspaceReplicas
        Dim pCheckOutReplica As IReplica
        Dim pFact As IWorkspaceFactory2
        Dim pMasterPropSet As IPropertySet2, pCheckOutPropSet As IPropertySet2
        Dim pDataset As IDataset
        Dim pCheckIn As ICheckIn

        '++ Open the check-out geodatabase
        pCheckOutPropSet = New PropertySet
        pCheckOutPropSet.SetProperty("Database", "d:\MyCheckOut.mdb")
        pFact = CType((New AccessWorkspaceFactory), IWorkspaceFactory2)
        pCheckOutWorkspace = pFact.Open(pCheckOutPropSet, 0)
        pDataset = CType(pCheckOutWorkspace, IDataset)
        pCheckOutWorkspaceName = CType(pDataset.FullName, IWorkspaceName)

        '++ get the check-out it contains
        pCheckOutWorkspaceReplicas = CType(pCheckOutWorkspace, IWorkspaceReplicas)
        pCheckOutReplica = pCheckOutWorkspaceReplicas.Replicas.Next

        '++ Open the master geodatabase
        pMasterPropSet = New PropertySet
        With pMasterPropSet
            .SetProperty("Server", "")
            .SetProperty("Instance", "")
            .SetProperty("DATABASE", "")
            .SetProperty("user", "")
            .SetProperty("password", "")
            .SetProperty("version", "")
        End With
        pFact = CType((New SdeWorkspaceFactory), IWorkspaceFactory2)
        pMasterWorkspace = pFact.Open(pMasterPropSet, 0)
        pDataset = CType(pMasterWorkspace, IDataset)
        pMasterWorkspaceName = CType(pDataset.FullName, IWorkspaceName)

        pCheckIn = New CheckIn
        pCheckIn.CheckInFromGDB(pMasterWorkspaceName, pCheckOutReplica.Name, pCheckOutWorkspaceName, False, False)
    End Sub

    Public Sub CheckIn_Delta()
        '++ Checks in changes from a delta database.
        '++ Modify the delta geodatabase name, master geodatabase connection 
        '++ properties and check-out name as required.
        Dim pMasterWorkspaceName As IWorkspaceName
        Dim pMasterWorkspace As IWorkspace
        Dim pFact As IWorkspaceFactory2
        Dim pMasterPropSet As IPropertySet2
        Dim pDataset As IDataset
        Dim pCheckIN As ICheckIn
        Dim SFileName As String

        '++ Open the master geodatabase
        pMasterPropSet = New PropertySet
        With pMasterPropSet
            .SetProperty("Server", "")
            .SetProperty("Instance", "")
            .SetProperty("DATABASE", "")
            .SetProperty("user", "")
            .SetProperty("password", "")
            .SetProperty("version", "sde.DEFAULT")
        End With
        pFact = CType((New SdeWorkspaceFactory), IWorkspaceFactory2)
        pMasterWorkspace = pFact.Open(pMasterPropSet, 0)
        pDataset = CType(pMasterWorkspace, IDataset)
        pMasterWorkspaceName = CType(pDataset.FullName, IWorkspaceName)
        pCheckIN = New CheckIn

        '++ set the path to and name of the delta file
        '++ '1' represents the esriExportDataChangesOption constant(1=Access).
        SFileName = "d:\MyDeltaDatabase.mdb"
        pCheckIN.CheckInFromDeltaFile(pMasterWorkspaceName, "MyCheckOut_new", SFileName, esriExportDataChangesOption.esriExportToAccess, False, False)
    End Sub


    ' Converts a GlobalID field to a GUID field.
    Public Sub ConvertGlobalIdToGuid(ByVal workspace As IWorkspace, ByVal datasetName As String)
        ' Open the table.
        Dim featureWorkspace As IFeatureWorkspace = CType(workspace, IFeatureWorkspace)
        Dim table As ITable = featureWorkspace.OpenTable(datasetName)

        ' Get the GlobalID field.
        Dim classEx As IClassEx = CType(table, IClassEx)
        If Not classEx.HasGlobalID Then
            Throw New Exception(String.Format("No GlobalID column in table: {0}.", datasetName))
        End If
        Dim globalIDFieldName As String = classEx.GlobalIDFieldName

        ' Convert the GlobalID column to a GUID column.
        Dim classSchemaEditEx As IClassSchemaEditEx = CType(table, IClassSchemaEditEx)
        classSchemaEditEx.UnregisterGlobalIDColumn(globalIDFieldName)
    End Sub

    ' Converts a GUID field to a GlobalID field.
    Public Sub ConvertGuidToGlobalId(ByVal workspace As IWorkspace, ByVal datasetName As String, ByVal guidFieldName As String)
        ' Open the table.
        Dim featureWorkspace As IFeatureWorkspace = CType(workspace, IFeatureWorkspace)
        Dim table As ITable = featureWorkspace.OpenTable(datasetName)

        ' Get the GUID field to convert.
        Dim fields As IFields = table.Fields
        Dim guidFieldIndex As Integer = fields.FindField(guidFieldName)
        Dim guidField As IField = fields.Field(guidFieldIndex)
        If guidField.Type <> esriFieldType.esriFieldTypeGUID Then
            Throw New Exception(String.Format("Field {0} is not a GUID field.", guidFieldName))
        End If

        ' Convert the GUID column to a GlobalID column.
        Dim classSchemaEditEx As IClassSchemaEditEx = CType(table, IClassSchemaEditEx)
        classSchemaEditEx.RegisterGlobalIDColumn(guidField.Name)
    End Sub

    ' Import data while preserving GlobalID values.
    Public Sub ImportDataChangesWithGlobalIDs(ByVal sourceWorkspace As IWorkspace, ByVal sourceDatasetName As String, _
                                          ByVal targetWorkspace As IWorkspace, ByVal targetDatasetName As String)

        ' Open the source dataset.
        Dim sourceFeatureWorkspace As IFeatureWorkspace = CType(sourceWorkspace, IFeatureWorkspace)
        Dim sourceTable As ITable = sourceFeatureWorkspace.OpenTable(sourceDatasetName)

        ' Create a name object for the target workspace.
        Dim dataset As IDataset = CType(targetWorkspace, IDataset)
        Dim targetWorkspaceName As IWorkspaceName = CType(dataset.FullName, IWorkspaceName)

        ' Initialize a TableDataChanges object with inserts.
        Dim tableDataChangesInfo As ITableDataChangesInfo = New TableDataChangesInfo
        tableDataChangesInfo.Init(targetDatasetName, sourceTable, Nothing, Nothing)
        Dim tablesDataChanges As ITablesDataChanges = New TablesDataChanges
        tablesDataChanges.Init(esriReplicaModelType.esriModelTypeFullGeodatabase)
        tablesDataChanges.Add(tableDataChangesInfo)
        Dim dataChanges As IDataChanges = CType(tablesDataChanges, IDataChanges)

        ' Use the TablesDataChanges to generate an updategram.
        Dim tempDirectory As String = Environment.GetEnvironmentVariable("TEMP")
        Dim deltaFile As String = IO.Path.Combine(tempDirectory, "tmp_import_with_GlobalIDs.xml")
        Dim dataChangesExporter As IExportDataChanges = New DataChangesExporter
        dataChangesExporter.ExportDataChanges(deltaFile, esriExportDataChangesOption.esriExportToXML, dataChanges, True)

        ' Import the updategram into the target workspace.
        Dim deltaDataChanges As IDeltaDataChanges = New DeltaDataChanges
        Dim deltaDataChangesInit2 As IDeltaDataChangesInit2 = CType(deltaDataChanges, IDeltaDataChangesInit2)
        deltaDataChangesInit2.Init2(deltaFile, esriExportDataChangesOption.esriExportToXML, False)
        Dim importDataChanges As IImportDataChanges = New DataChangesImporter
        importDataChanges.ImportDataChanges(targetWorkspaceName, deltaDataChanges, False, True)
    End Sub
#End Region

#Region "Routine et fonction publiques originales"
    ' Creates a replica of all data in a feature dataset.
    Public Sub CreateFeatureDatasetReplica(ByVal parentGDS As IGeoDataServer, ByVal childGDS As IGeoDataServer, _
                                           ByVal replicaName As String, ByVal accessType As esriReplicaAccessType, _
                                           ByVal featureDataset As String, ByVal geometry As IGeometry, _
                                           ByVal registerOnly As Boolean, ByVal useArchiving As Boolean)
        Try
            'Définir une FeatureClass à extraire de la géodatabase source
            Dim gpReplicaDataset As IGPReplicaDataset = New GPReplicaDataset
            gpReplicaDataset.DatasetType = esriDatasetType.esriDTFeatureClass
            gpReplicaDataset.Name = featureDataset
            gpReplicaDataset.DefQuery = "DATASET_NAME='031G01'"
            'Ajouter la classe à extraire dans la géodatabase source
            Dim gpReplicaDatasets As IGPReplicaDatasets = New GPReplicaDatasets
            gpReplicaDatasets.Add(gpReplicaDataset)
            Dim gpReplicaDatasetsExpand As IGPReplicaDatasets = parentGDS.ExpandReplicaDatasets(gpReplicaDatasets)

            'Définir le type de réplica à exécuter
            Dim gpReplicaDesc As IGPReplicaDescription = New GPReplicaDescription
            gpReplicaDesc.ReplicaDatasets = gpReplicaDatasetsExpand
            gpReplicaDesc.ModelType = esriReplicaModelType.esriModelTypeSimple
            Dim singleGeneration As Boolean
            If accessType = esriReplicaAccessType.esriReplicaAccessNone Then
                singleGeneration = True
            Else
                singleGeneration = False
            End If
            gpReplicaDesc.SingleGeneration = singleGeneration
            gpReplicaDesc.QueryGeometry = geometry
            gpReplicaDesc.SpatialRelation = esriSpatialRelEnum.esriSpatialRelIndexIntersects

            'Définir les options du réplica
            'esriReplicaAccessNone = 0    - The child replica is a check-out replica. 
            'esriReplicaChildReadOnly = 1 - The child replica is read only.  Data changes may only be synchronized from the parent replica to the child replica.  
            '                               Conflicts are not detected, so if there happens to be conflictings edits on the child database, 
            '                               the parent replicas edits will over-write the edits on synchronize.
            'esriReplicaParentReadOnly = 2 -The parent replica is read only.  Data changes may only be synchronized from the child replica to the parent replica.  
            '                               Conflicts are not detected, so if there happens to be conflictings edits on the parent database, 
            '                               the child replicas edits will over-write the edits on synchronize.  
            'esriReplicaBothReadWrite = 3 - Both the parent and child replicas can synchronize data changes with their relative replica.
            'esriReplicaParentOrChildReadOnly = 4 - Used to retrieve whether the parent or child replica is read only. 
            '                                       Can be useful in cases where you would otherwise use both esriReplicaChildReadOnly and 
            '                                       esriReplicaParentReadOnly to find out whether the replica is a one-way replica.
            Dim replicaOptions As IGPReplicaOptions2 = New GPReplicaOptions
            replicaOptions.AccessType = accessType
            replicaOptions.ChildReconcilePolicy = esriReplicaReconcilePolicyType.esriReplicaResolveConflictsNone
            replicaOptions.ParentReconcilePolicy = esriReplicaReconcilePolicyType.esriReplicaResolveConflictsNone
            replicaOptions.IsChildFirstSender = True
            replicaOptions.RegisterReplicaOnly = registerOnly
            replicaOptions.UseArchiving = useArchiving

            'Exécuter le traitement de réplica
            Dim replicationAgent As IReplicationAgent = New ReplicationAgent
            'replicationAgent.CreateReplica("", parentGDS, childGDS, replicaName, gpReplicaDesc, replicaOptions)
            replicationAgent.ExtractData("", parentGDS, childGDS, gpReplicaDesc)

        Catch comExc As COMException
            Throw New Exception(String.Format("Create replica errored: {0}, Error Code: {1}", comExc.Message, comExc.ErrorCode), comExc)
        Catch exc As Exception
            Throw New Exception(String.Format("Create replica errored: {0}", exc.Message), exc)
        End Try
    End Sub

    ' This method adds a feature class or table to a replica.
    Public Sub AddDatasetToReplicaOri(ByVal workspace As IWorkspace, ByVal replicaName As String, _
                                   ByVal datasetName As String, ByVal parentDatabase As String, ByVal parentOwner As String, _
                                   ByVal datasetType As esriDatasetType, ByVal rowsType As esriRowsType, ByVal useGeometry As Boolean, _
                                   ByVal queryDef As String)
        Try
            ' Find the replica.
            Dim workspaceReplicas2 As IWorkspaceReplicas2 = CType(workspace, IWorkspaceReplicas2)
            Dim replica As IReplica = workspaceReplicas2.ReplicaByName(replicaName)

            ' Create a replica dataset for the new feature class or table.
            Dim replicaDataset As IReplicaDataset = New ReplicaDataset
            Dim replicaDatasetEdit As IReplicaDatasetEdit = CType(replicaDataset, IReplicaDatasetEdit)
            replicaDatasetEdit.Type = datasetType
            replicaDatasetEdit.Name = datasetName
            replicaDatasetEdit.ParentDatabase = parentDatabase
            replicaDatasetEdit.ParentOwner = parentOwner
            replicaDatasetEdit.ReplicaID = replica.ReplicaID

            ' Add the dataset. Note that the pSelID parameter is not currently supported
            ' and should always be Nothing.
            Dim workspaceReplicasAdmin2 As IWorkspaceReplicasAdmin2 = CType(workspaceReplicas2, IWorkspaceReplicasAdmin2)
            Try
                workspaceReplicasAdmin2.RegisterReplicaDataset(replicaDataset, rowsType, useGeometry, _
                                                               queryDef, Nothing, replica)
            Catch comExc As COMException
                ' Handle the exception appropriately for the application.
            End Try

        Catch ex As Exception
            Throw
        End Try
    End Sub

    ' Synchronizes a replica in a connected environment.
    Public Sub SynchronizeReplica(ByVal parentGDS As IGeoDataServer, ByVal childGDS As IGeoDataServer, _
                                  ByVal replicaName As String, ByVal conflictPolicy As esriReplicationAgentReconcilePolicy, _
                                  ByVal syncDirection As esriReplicaSynchronizeDirection, ByVal columnLevel As Boolean)
        Try
            ' Iterate through the replicas of the parent GeoDataServer.
            Dim gpReplicas As IGPReplicas = parentGDS.Replicas
            Dim parentReplica As IGPReplica = Nothing
            For i As Integer = 0 To gpReplicas.Count - 1
                ' See if the unqualified replica name matches the replicaName parameter.
                Dim currentReplica As IGPReplica = gpReplicas.Element(i)
                Dim currentReplicaName As String = currentReplica.Name
                Dim dotIndex As Integer = currentReplicaName.LastIndexOf(".") + 1
                Dim baseName As String = currentReplicaName.Substring(dotIndex, currentReplicaName.Length - dotIndex)
                If baseName.ToLower() = replicaName.ToLower() Then
                    parentReplica = currentReplica
                    Exit For
                End If
            Next i

            ' Check to see if the parent replica was found.
            If parentReplica Is Nothing Then
                Throw New ArgumentException("The requested replica could not be found on the parent GDS.")
            End If

            ' Iterate through the replica of the child GeoDataServer.
            gpReplicas = childGDS.Replicas
            Dim childReplica As IGPReplica = Nothing
            For i As Integer = 0 To gpReplicas.Count - 1
                ' See if the unqualified replica name matches the replicaName parameter.
                Dim currentReplica As IGPReplica = gpReplicas.Element(i)
                Dim currentReplicaName As String = currentReplica.Name
                Dim dotIndex As Integer = currentReplicaName.LastIndexOf(".") + 1
                Dim baseName As String = currentReplicaName.Substring(dotIndex, currentReplicaName.Length - dotIndex)
                If baseName.ToLower() = replicaName.ToLower() Then
                    childReplica = currentReplica
                    Exit For
                End If
            Next i

            ' Check to see if the child replica was found.
            If childReplica Is Nothing Then
                Throw New ArgumentException("The requested replica could not be found on the child GDS.")
            End If

            ' Synchronize the replica.
            Dim replicationAgent As IReplicationAgent = New ReplicationAgent
            replicationAgent.SynchronizeReplica(parentGDS, childGDS, parentReplica, childReplica, conflictPolicy, syncDirection, columnLevel)

        Catch comExc As COMException
            Throw New Exception(String.Format("Create replica errored: {0}, Error Code: {1}", comExc.Message, comExc.ErrorCode), comExc)
        Catch exc As Exception
            Throw New Exception(String.Format("Create replica errored: {0}", exc.Message), exc)
        End Try
    End Sub

    'The following code example uses IClassSchemaEdit3 to add a field of type GlobalID to an existing feature class or table. 
    'Use any valid string name for the GlobalID field, for example, GlobalID. As when making any type of schema change, '
    'an exclusive schema lock should be acquired for the feature class or dataset before adding or removing a GlobalID field.
    Public Sub AddGlobalIDOri(ByVal table As ITable, ByVal globalIdFieldName As String)
        ' Try to acquire an exclusive schema lock.
        Dim schemaLock As ISchemaLock = CType(table, ISchemaLock)
        Try
            schemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            ' Add the GlobalID field.
            Dim classSchemaEdit3 As IClassSchemaEdit3 = CType(table, IClassSchemaEdit3)
            classSchemaEdit3.AddGlobalID(globalIdFieldName)
        Catch comExc As COMException
            ' Handle the exception appropriately for the application.
        Finally
            ' Demote the exclusive lock to a shared lock.
            schemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
        End Try
    End Sub

    'The following code example uses IClassSchemaEdit3 to delete the GlobalID from an existing feature class or table. 
    'ArcGIS prevents deleting the GlobalID field from a feature class or table that is participating in a replica, 
    'as replication requires the GlobalID field. In this case, unregister the replica before deleting the GlobalID field. 
    Public Sub RemoveGlobalIDOri(ByVal table As ITable)
        ' Try to acquire an exclusive schema lock.
        Dim schemaLock As ISchemaLock = CType(table, ISchemaLock)
        Try
            schemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            ' Remove the GlobalID field.
            Dim classSchemaEdit3 As IClassSchemaEdit3 = CType(table, IClassSchemaEdit3)
            classSchemaEdit3.DeleteGlobalID()
        Catch comExc As COMException
            ' Handle the exception appropriately for the application.
        Finally
            ' Demote the exclusive lock to a shared lock.
            schemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
        End Try
    End Sub

    ' This function takes the two SDE workspaces and replica, and gets the schema changes.
    Public Sub ListSchemaChanges(ByVal targetWorkspace As IWorkspace, ByVal sourceWorkspace As IWorkspace, ByVal replicaName As String)
        Try
            ' Get the replica from the source and the workspace name object for the target.
            Dim workspaceReplicas As IWorkspaceReplicas = CType(sourceWorkspace, IWorkspaceReplicas)
            Dim replica As IReplica = workspaceReplicas.ReplicaByName(replicaName)
            Dim dataset As IDataset = CType(targetWorkspace, IDataset)
            Dim Name As IName = dataset.FullName
            Dim workspaceName As IWorkspaceName = CType(Name, IWorkspaceName)

            ' Initialize the schema changes object.
            Dim schemaChanges As ISchemaChanges = New SchemaChanges
            Dim schemaChangesInit As ISchemaChangesInit = CType(schemaChanges, ISchemaChangesInit)
            schemaChangesInit.Init(replica, workspaceName)

            ' Print the changes.
            PrintSchemaChanges(schemaChanges.GetChanges(), "")

        Catch ex As Exception
            Throw
        End Try
    End Sub

    ' This function takes the target workspaces and either the schema file
    ' for the relative replica or a schema changes file, and gets the schema changes.
    ' Set the isSchemaChangeFile to true if it is a schema changes file.
    Public Sub ListSchemaChanges(ByVal targetWorkspace As IWorkspace, ByVal schemaFile As String, ByVal isSchemaChangeFile As Boolean)
        Try
            ' Workspace name object for the target.
            Dim dataset As IDataset = CType(targetWorkspace, IDataset)
            Dim Name As IName = dataset.FullName
            Dim workspaceName As IWorkspaceName = CType(Name, IWorkspaceName)

            ' Initialize the schema changes object.
            Dim schemaChangesInit As ISchemaChangesInit = New SchemaChanges
            If isSchemaChangeFile Then
                schemaChangesInit.InitFromSchemaDifferencesDocument(schemaFile, workspaceName)
            Else
                schemaChangesInit.InitFromSchemaDocument(schemaFile, workspaceName)
            End If

            Dim schemaChanges As ISchemaChanges = CType(schemaChangesInit, ISchemaChanges)

            ' Print the changes.
            Dim enumSchemaChange As IEnumSchemaChange = schemaChanges.GetChanges()
            PrintSchemaChanges(enumSchemaChange, "")

        Catch ex As Exception
            Throw
        End Try
    End Sub

    ' Recursive function that steps through the schema changes info.
    Public Sub PrintSchemaChanges(ByVal enumSchemaChanges As IEnumSchemaChange, ByVal schemaChange As String)
        Try
            enumSchemaChanges.Reset()
            Dim schemaChangesInfo As ISchemaChangeInfo = Nothing
            Dim dataName As String = ""

            ' Step through the schema changes.
            Do While Not (schemaChangesInfo) Is Nothing

                ' Get the name of the feature class, feature dataset, and so on, that has changed.
                If schemaChangesInfo.SchemaChangeType <> esriSchemaChangeType.esriSchemaChangeTypeNoChange Then
                    Dim toObject As Object = schemaChangesInfo.ToObject
                    Dim fromObject As Object = schemaChangesInfo.FromObject
                    If Not toObject Is Nothing Then
                        dataName = GetDataName(toObject)
                    ElseIf Not fromObject Is Nothing Then
                        dataName = GetDataName(fromObject)
                    End If
                End If

                ' If at the end of the list for the schema change, print the schema change.
                ' Otherwise, continue through the list.
                If Not schemaChangesInfo.GetChanges() Is Nothing Then
                    Dim nextSchemaChange As String = String.Format("{0}{1}/", schemaChange, dataName)
                    PrintSchemaChanges(schemaChangesInfo.GetChanges(), nextSchemaChange)
                    Return
                Else
                    ' Convert the schema change type to a string and print the change.
                    Dim changeType As String = System.Enum.GetName(GetType(esriSchemaChangeType), schemaChangesInfo.SchemaChangeType)
                    Console.WriteLine("{0}{1}: {2}", schemaChange, dataName, changeType)
                End If

                schemaChangesInfo = enumSchemaChanges.Next()

            Loop

        Catch ex As Exception
            Throw
        End Try
    End Sub

    ' Gets the name of the object returned from the schemachangesinfo class.
    Public Function GetDataName(ByVal data As Object) As String
        Try
            If TypeOf data Is IDataElement Then
                Dim dataElement As IDataElement = CType(data, IDataElement)
                Dim dataElementName As String = dataElement.Name
                Return dataElementName
            ElseIf TypeOf data Is IFields Then
                Return "Field Changes"
            ElseIf TypeOf data Is IField Then
                Dim field As IField = CType(data, IField)
                Dim fieldName As String = field.Name
                Return fieldName
            ElseIf TypeOf data Is IDomain Then
                Dim domain As IDomain = CType(data, IDomain)
                Dim domainName As String = domain.Name
                Return domainName
            Else
                Return "Unknown type"
            End If

        Catch ex As Exception
            Throw
        End Try
    End Function
#End Region
End Module
