Imports System.Windows.Forms
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports System.Drawing
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.Geometry

''' <summary>
''' Designer class of the dockable window add-in. It contains user interfaces that
''' make up the dockable window.
''' </summary>
Public Class dckMenuIdentification
    'Déclarer les variables de travail
    Private m_hook As Object    'Object contenant l'application parent
    Private m_DescCodeSpecifique As New Dictionary(Of String, String)   'Contient la description des codes spcifiques d'un catalogue
    Private m_DescValeurAttribut As New Dictionary(Of String, String)   'Contient la description des valeurs d'attributs d'un catalogue

    ''' <summary>
    ''' Host object of the dockable window
    ''' </summary> 
    Public Property Hook() As Object
        Get
            Return m_hook
        End Get
        Set(ByVal value As Object)
            m_hook = value
        End Set
    End Property

    ''' <summary>
    ''' Implementation class of the dockable window add-in. It is responsible for
    ''' creating and disposing the user interface class for the dockable window.
    ''' </summary>
    Public Class AddinImpl
        Inherits ESRI.ArcGIS.Desktop.AddIns.DockableWindow

        Private m_windowUI As dckMenuIdentification

        Protected Overrides Function OnCreateChild() As System.IntPtr
            m_windowUI = New dckMenuIdentification(Me.Hook)
            Return m_windowUI.Handle
        End Function

        Protected Overrides Sub Dispose(ByVal Param As Boolean)
            If m_windowUI IsNot Nothing Then
                m_windowUI.Dispose(Param)
            End If

            MyBase.Dispose(Param)
        End Sub
    End Class

    '''<summary>
    ''' Routine qui permet d'initialiser le menu lors de la création du menu.
    '''</summary>
    '''
    Public Sub New(ByVal hook As Object)
        ' This call is required by the Windows Form Designer.
        InitializeComponent()

        ' Add any initialization after the InitializeComponent() call.
        Me.Hook = hook

        Try
            'Définir l'application
            m_Application = CType(hook, IApplication)

            'Définir le document
            m_MxDocument = CType(m_Application.Document, IMxDocument)

            'Définir le menu d'identification
            m_MenuIdentification = Me

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'afficher le menu.
    '''</summary>
    '''
    Public Overloads Sub Show(ByVal Show As Boolean)
        'Déclarer les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver un DockableWindow
        Dim pDockWindow As IDockableWindow 'Interface contenant le DockableWindow

        Try
            'Trouver le Dockable Window
            windowID.Value = "MPO_BarreSIB_dckMenuIdentification"
            pDockWindow = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
            pDockWindow.Show(Show)

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            windowID = Nothing
            pDockWindow = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'indiquer si le menu est affiché.
    '''</summary>
    '''
    Public Overloads Function IsVisible() As Boolean
        'Déclarer les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver un DockableWindow
        Dim pDockWindow As IDockableWindow 'Interface contenant le DockableWindow

        Try
            'Trouver le Dockable Window
            windowID.Value = "MPO_BarreSIB_dckMenuIdentification"
            pDockWindow = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
            Return pDockWindow.IsVisible

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            windowID = Nothing
            pDockWindow = Nothing
        End Try
    End Function

#Region "Routines et fonctions publiques"
    '''<summary>
    ''' Routine qui permet d'initialiser le menu d'identification.
    '''</summary>
    '''
    Public Sub Initialiser()
        Try
            'Initialiser les nodes
            treIdentification.Nodes.Clear()
            'Initialiser le tri
            btnRafraichir.Text = "Ascendant"
            'Initialiser le nombre maximum d'items
            txtMaxItem.Text = "1000"

            'Vider le contenu du DataGridView en ajoutant un nouveau Dataset vide
            dgvIdentification.DataSource = New DataSet("DataSet")

        Catch erreur As Exception
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les éléments sélectionnés de tous les FeatureLayers visibles dans la Map.
    '''</summary>
    ''' 
    '''<param name="pMap"> Interface ESRI contenant tous les FeatureLayers et leurs éléments sélectionnés à ajouter dans le menu.</param>
    '''
    Public Sub IdentifierMap(ByVal pMap As IMap)
        'Déclarer la variables de travail
        Dim qFeatureLayerColl As Collection = Nothing   'Contient la liste des FeatureLayer visibles
        Dim pFeatureLayer As IFeatureLayer = Nothing    'Interface contenant une classe de données
        Dim i As Integer = Nothing                      'Compteur

        Try
            'Initialiser les nodes
            treIdentification.Nodes.Clear()

            'Vider le contenu du DataGridView en ajoutant un nouveau Dataset vide
            dgvIdentification.DataSource = New DataSet("DataSet")

            'Définir le MapLayer et tous les FeatureLayer visibles
            m_MapLayer = New clsGererMapLayer(pMap, True)

            'Définir la liste des FeatureLayer
            qFeatureLayerColl = m_MapLayer.FeatureLayerCollection

            'vérifier si les FeatureLayers sont présents
            If qFeatureLayerColl IsNot Nothing Then
                'Traiter tous les FeatureLayer
                For i = 1 To qFeatureLayerColl.Count
                    'Définir le FeatureLayer
                    pFeatureLayer = CType(qFeatureLayerColl.Item(i), IFeatureLayer)

                    'Identifier les éléments sélectionnés dans le FeatureLayer.
                    Call IdentifierFeatureLayer(pFeatureLayer, False)
                Next
            End If

            'Définir l'information sur le nombre de Layers visibles et le nombre d'éléments sélectionnés
            lblInformation.Text = qFeatureLayerColl.Count.ToString & " Layer(s), " & pMap.SelectionCount.ToString & " Élément(s)"

        Catch erreur As Exception
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qFeatureLayerColl = Nothing
            pFeatureLayer = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les éléments sélectionnés dans le FeatureLayer.
    '''</summary>
    ''' 
    '''<param name="pFeatureLayer"> Interface ESRI contenant les éléments sélectionnés d'un FeatureLayer à ajouter dans le menu.</param>
    '''<param name="bInitialiser"> Inidique si on doit initialiser le menu avant d'ajouter les éléments sélectionnés.</param>
    '''
    Public Sub IdentifierFeatureLayer(ByVal pFeatureLayer As IFeatureLayer, ByVal bInitialiser As Boolean)
        'Déclarer les variables de travail
        Dim qNodeLayer As TreeNode = Nothing                'TreeNode correspondant au Layer
        Dim pFeatureSelection As IFeatureSelection = Nothing 'Interface qui permet de traiter la sélection
        Dim pSelectionSet As ISelectionSet = Nothing        'Interface contenant les éléments sélectionnés
        Dim pCursor As ICursor = Nothing                    'Interface qui permet d'extraire les éléments
        Dim pFeature As IFeature = Nothing                  'Interface contenant un élément
        Dim pDisplayString As IDisplayString = Nothing      'Interface qui permet d'interpréter l'affichage de l'élément
        Dim qNodeFeature As TreeNode = Nothing              'TreeNode correspondant à un élément

        Try
            'Vérifier si le FeatureLayer est valide
            If pFeatureLayer Is Nothing Then Return

            'Interface pour traiter les éléments sélectionnés
            pFeatureSelection = CType(pFeatureLayer, IFeatureSelection)

            'Initialiser les nodes si spécifié
            If bInitialiser Then treIdentification.Nodes.Clear()

            'Définir et ajouter le node du FeatureLayer
            qNodeLayer = treIdentification.Nodes.Add(pFeatureLayer.Name, pFeatureLayer.Name)
            qNodeLayer.Checked = True

            'Interface pour extraire l'affichage de l'élément
            pDisplayString = CType(pFeatureLayer, IDisplayString)

            'Interface pour traiter les éléments sélectionnés
            pFeatureSelection = CType(pFeatureLayer, IFeatureSelection)

            'Définir le curseur d'extraction des éléments
            pSelectionSet = pFeatureSelection.SelectionSet

            'Définir le curseur d'extraction des éléments
            pSelectionSet.Search(Nothing, False, pCursor)

            'Extraire le premier élément
            pFeature = CType(pCursor.NextRow, IFeature)

            'Débuter la mise à jour
            treIdentification.BeginUpdate()

            'Traiter tous les éléments sélectionnés
            Do Until pFeature Is Nothing
                Try
                    'Définir et ajouter le node de l'élément sélectionné
                    qNodeFeature = qNodeLayer.Nodes.Add(pFeature.OID.ToString, pDisplayString.FindDisplayString(pFeature))
                    qNodeFeature.Nodes.Add("", "")
                Catch
                    'Définir et ajouter le node de l'élément sélectionné
                    qNodeFeature = qNodeLayer.Nodes.Add(pFeature.OID.ToString, pFeature.OID.ToString)
                    qNodeFeature.Nodes.Add("", "")
                End Try

                'Vérifier si le nombre de noeud dépasse la limite
                If qNodeLayer.Nodes.Count > m_MaxItems Then Exit Do

                'Extraire le prochain élément
                pFeature = CType(pCursor.NextRow, IFeature)
            Loop

            'Ouvrir tous les nodes au premier niveau
            qNodeLayer.Expand()

            'Trier tous les nodes
            treIdentification.Sort()

            'Sélectionner le premier node
            qNodeLayer = qNodeLayer.FirstNode
            treIdentification.SelectedNode = qNodeLayer

            'Terminer la mise à jour
            treIdentification.EndUpdate()

            'Définir l'information sur le nombre de Layers visibles et le nombre d'éléments sélectionnés
            lblInformation.Text = "1 Layer, " & pFeatureSelection.SelectionSet.Count.ToString & " Élément(s)"

        Catch erreur As Exception
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qNodeLayer = Nothing
            qNodeFeature = Nothing
            pFeatureSelection = Nothing
            pSelectionSet = Nothing
            pCursor = Nothing
            pFeature = Nothing
            pDisplayString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les éléments sélectionnés dans un StandaloneTable.
    '''</summary>
    ''' 
    '''<param name="pStandaloneTable"> Interface ESRI contenant les éléments sélectionnés d'un StandaloneTable à ajouter dans le menu.</param>
    '''<param name="bInitialiser"> Inidique si on doit initialiser le menu avant d'ajouter les éléments sélectionnés.</param>
    '''
    Public Sub IdentifierTable(ByVal pStandaloneTable As IStandaloneTable, ByVal bInitialiser As Boolean)
        'Déclarer les variables de travail
        Dim qNodeLayer As TreeNode = Nothing                'TreeNode correspondant au Layer.
        Dim pTableSelection As ITableSelection = Nothing    'Interface qui permet de traiter la sélection.
        Dim pSelectionSet As ISelectionSet = Nothing        'Interface contenant les éléments sélectionnés.
        Dim pCursor As ICursor = Nothing                    'Interface qui permet d'extraire les éléments.
        Dim pRow As IRow = Nothing                          'Interface contenant un élément.
        Dim pDisplayString As IDisplayString = Nothing      'Interface qui permet d'interpréter l'affichage de l'élément.
        Dim qNodeFeature As TreeNode = Nothing              'TreeNode correspondant à un élément.
        Dim pDataset As IDataset = Nothing              'Interface pour vérifier s'il s'agit d'une vue.

        Try
            'Vérifier si le FeatureLayer est valide
            If pStandaloneTable Is Nothing Then Return
            'Interface pour traiter les éléments sélectionnés
            pTableSelection = CType(pStandaloneTable, ITableSelection)

            'Dim pQueryDesc As IQueryDescription = Nothing
            'Dim pQueryTableName As IQueryTableName = Nothing
            'pQueryTableName = CType(pDataset.FullName, IQueryTableName)
            'pQueryDesc = pQueryTableName.QueryDescription
            'pQueryTableName.Query = pQueryDesc.Query

            'Initialiser les nodes si spécifié
            If bInitialiser Then treIdentification.Nodes.Clear()

            'Définir et ajouter le node du FeatureLayer
            qNodeLayer = treIdentification.Nodes.Add(pStandaloneTable.Name, pStandaloneTable.Name)
            qNodeLayer.Checked = True

            'Interface pour extraire l'affichage de l'élément
            pDisplayString = CType(pStandaloneTable, IDisplayString)

            'Interface pour traiter les éléments sélectionnés
            pTableSelection = CType(pStandaloneTable, ITableSelection)

            'Définir le SelectionSet
            pSelectionSet = pTableSelection.SelectionSet

            Try
                'Définir le curseur d'extraction des éléments
                pSelectionSet.Search(Nothing, True, pCursor)
            Catch ex As Exception
                'Interface pour vérifier s'il s'agit d'une vue.
                pDataset = CType(pStandaloneTable, IDataset)
                'Vérifier si les ids doivent être assignés
                If TypeOf pDataset.FullName Is IQueryTableName Then
                    'Assigner les ids à la vue
                    pCursor = pStandaloneTable.Table.Search(Nothing, False)
                    pRow = pCursor.NextRow
                    Do Until pRow Is Nothing
                        pRow = pCursor.NextRow
                    Loop
                End If
                'Définir le curseur d'extraction des éléments
                pSelectionSet.Search(Nothing, True, pCursor)
            End Try

            'Extraire le premier élément
            pRow = pCursor.NextRow

            'Débuter la mise à jour
            treIdentification.BeginUpdate()

            'Traiter tous les éléments sélectionnés
            Do Until pRow Is Nothing
                Try
                    'Définir et ajouter le node de l'élément sélectionné
                    qNodeFeature = qNodeLayer.Nodes.Add(pRow.OID.ToString, pDisplayString.FindDisplayString(CType(pRow, IObject)))
                    qNodeFeature.Nodes.Add("", "")
                Catch
                    'Définir et ajouter le node de l'élément sélectionné
                    qNodeFeature = qNodeLayer.Nodes.Add(pRow.OID.ToString, pRow.OID.ToString)
                    qNodeFeature.Nodes.Add("", "")
                End Try

                'Vérifier si le nombre de noeud dépasse la limite
                If qNodeLayer.Nodes.Count > m_MaxItems Then Exit Do

                'Extraire le prochain élément
                pRow = pCursor.NextRow
            Loop

            'Ouvrir tous les nodes au premier niveau
            qNodeLayer.Expand()

            'Trier tous les nodes
            treIdentification.Sort()

            'Terminer la mise à jour
            treIdentification.EndUpdate()

            'Sélectionner le premier node
            qNodeLayer = qNodeLayer.FirstNode
            treIdentification.SelectedNode = qNodeLayer

            'Définir l'information sur le nombre de Layers visibles et le nombre d'éléments sélectionnés
            lblInformation.Text = "1 Table(s), " & pTableSelection.SelectionSet.Count.ToString & " Élément(s)"

        Catch erreur As Exception
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qNodeLayer = Nothing
            qNodeFeature = Nothing
            pTableSelection = Nothing
            pSelectionSet = Nothing
            pCursor = Nothing
            pRow = Nothing
            pDisplayString = Nothing
            pDataset = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier les éléments sélectionnés dans un StandaloneTable.
    '''</summary>
    ''' 
    '''<param name="pStandaloneTable"> Interface ESRI contenant les éléments sélectionnés d'un StandaloneTable à ajouter dans le menu.</param>
    '''<param name="bInitialiser"> Inidique si on doit initialiser le menu avant d'ajouter les éléments sélectionnés.</param>
    '''
    Public Sub IdentifierTable2(ByVal pStandaloneTable As IStandaloneTable, ByVal bInitialiser As Boolean)
        'Déclarer les variables de travail
        Dim qNodeLayer As TreeNode = Nothing                'TreeNode correspondant au Layer
        Dim pTableSelection As ITableSelection = Nothing    'Interface qui permet de traiter la sélection
        Dim pSelectionSet As ISelectionSet = Nothing        'Interface contenant les éléments sélectionnés.
        Dim pDataset As IDataset = Nothing              'Interface pour vérifier s'il s'agit d'une vue.
        Dim pCursor As ICursor = Nothing                    'Interface qui permet d'extraire les éléments
        Dim pRow As IRow = Nothing                          'Interface contenant un élément
        Dim pDisplayString As IDisplayString = Nothing      'Interface qui permet d'interpréter l'affichage de l'élément
        Dim qNodeFeature As TreeNode = Nothing              'TreeNode correspondant à un élément
        Dim pEnumIds As IEnumIDs = Nothing                  'Interface pour extraire tous les Ids sélectionnés
        Dim nId As Integer = Nothing                        'Identifiant d'un élément

        Try
            'Vérifier si le FeatureLayer est valide
            If pStandaloneTable Is Nothing Then Return

            'Interface pour traiter les éléments sélectionnés
            pTableSelection = CType(pStandaloneTable, ITableSelection)

            'Initialiser les nodes si spécifié
            If bInitialiser Then treIdentification.Nodes.Clear()

            'Définir et ajouter le node du FeatureLayer
            qNodeLayer = treIdentification.Nodes.Add(pStandaloneTable.Name, pStandaloneTable.Name)
            qNodeLayer.Checked = True

            'Interface pour extraire l'affichage de l'élément
            pDisplayString = CType(pStandaloneTable, IDisplayString)

            'Interface pour traiter les éléments sélectionnés
            pTableSelection = CType(pStandaloneTable, ITableSelection)

            'Définir le SelectionSet
            pSelectionSet = pTableSelection.SelectionSet

            Try
                'Définir le curseur d'extraction des éléments
                pSelectionSet.Search(Nothing, True, pCursor)
            Catch ex As Exception
                'Interface pour vérifier s'il s'agit d'une vue.
                pDataset = CType(pStandaloneTable, IDataset)
                'Vérifier si les ids doivent être assignés
                If TypeOf pDataset.FullName Is IQueryTableName Then
                    'Assigner les ids à la vue
                    pCursor = pStandaloneTable.Table.Search(Nothing, False)
                    pRow = pCursor.NextRow
                    Do Until pRow Is Nothing
                        pRow = pCursor.NextRow
                    Loop
                End If
                'Définir le curseur d'extraction des éléments
                pSelectionSet.Search(Nothing, True, pCursor)
            End Try

            'Interface pour extraire les éléments sélectionnés
            pEnumIds = pSelectionSet.IDs
            pEnumIds.Reset()

            'Extraire le premier Id des éléments sélectionnés
            nId = pEnumIds.Next

            'Débuter la mise à jour
            treIdentification.BeginUpdate()

            'Traiter tant qu'il y a des éléments
            Do Until nId = -1
                'Extraire l'élément de la table
                pRow = pStandaloneTable.Table.GetRow(nId)

                'Vérifier si l'élément a été trouvé
                If pRow IsNot Nothing Then
                    Try
                        'Définir et ajouter le node de l'élément sélectionné
                        qNodeFeature = qNodeLayer.Nodes.Add(pRow.OID.ToString, pDisplayString.FindDisplayString(CType(pRow, IObject)))
                        qNodeFeature.Nodes.Add("", "")
                    Catch
                        'Définir et ajouter le node de l'élément sélectionné
                        qNodeFeature = qNodeLayer.Nodes.Add(pRow.OID.ToString, pRow.OID.ToString)
                        qNodeFeature.Nodes.Add("", "")
                    End Try
                End If

                'Trouver le prochain ID des éléments sélectionnés
                nId = pEnumIds.Next
            Loop

            'Ouvrir tous les nodes au premier niveau
            qNodeLayer.Expand()

            'Trier tous les nodes
            treIdentification.Sort()

            'Terminer la mise à jour
            treIdentification.EndUpdate()

            'Sélectionner le premier node
            qNodeLayer = qNodeLayer.FirstNode
            treIdentification.SelectedNode = qNodeLayer

            'Définir l'information sur le nombre de Layers visibles et le nombre d'éléments sélectionnés
            lblInformation.Text = "1 Table(s), " & pTableSelection.SelectionSet.Count.ToString & " Élément(s)"

        Catch erreur As Exception
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qNodeLayer = Nothing
            qNodeFeature = Nothing
            pTableSelection = Nothing
            pDataset = Nothing
            pSelectionSet = Nothing
            pEnumIds = Nothing
            pCursor = Nothing
            pRow = Nothing
            pDisplayString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier un seul élément sélectionné dans un FeatureLayer.
    '''</summary>
    ''' 
    '''<param name="pFeatureLayer"> Interface ESRI représentant le FeatureLayer de l'élément à ajouter dans le menu.</param>
    '''<param name="pFeature"> Interface ESRI représentant l'élément à ajouter dans le menu.</param>
    '''<param name="bInitialiser"> Inidique si on doit initialiser le menu avant d'ajouter l'élément spécifié.</param>
    '''
    Public Sub IdentifierFeature(ByVal pFeatureLayer As IFeatureLayer, ByVal pFeature As IFeature, ByVal bInitialiser As Boolean)
        'Déclarer les variables de travail
        Dim qNodeLayer As TreeNode = Nothing            'TreeNode correspondant au Layer
        Dim pDisplayString As IDisplayString = Nothing  'Interface qui permet d'interpréter l'affichage de l'élément
        Dim qNodeFeature As TreeNode = Nothing          'TreNode correspondant à un élément

        Try
            'Initialiser les nodes si spécifié
            If bInitialiser Then treIdentification.Nodes.Clear()

            'Vérifier si le FeatureLayer est valide
            If pFeatureLayer Is Nothing Then Return

            'Débuter la mise à jour
            treIdentification.BeginUpdate()

            'Interface pour extraire l'affichage de l'élément
            pDisplayString = CType(pFeatureLayer, IDisplayString)

            'Ajouter le node du FeatureLayer
            qNodeLayer = treIdentification.Nodes.Add(pFeatureLayer.Name, pFeatureLayer.Name)

            'Vérifier si le Feature est valide
            If pFeature Is Nothing Then Return

            Try
                'Définir et ajouter le node de l'élément sélectionné
                qNodeFeature = qNodeLayer.Nodes.Add(pFeature.OID.ToString, pDisplayString.FindDisplayString(pFeature))
                qNodeFeature.Nodes.Add("", "")
            Finally
                'Définir et ajouter le node de l'élément sélectionné
                qNodeFeature = qNodeLayer.Nodes.Add(pFeature.OID.ToString, pFeature.OID.ToString)
                qNodeFeature.Nodes.Add("", "")
            End Try

            'Ouvrir tous les nodes au premier niveau
            qNodeLayer.Expand()

            'Trier tous les nodes
            treIdentification.Sort()

            'Terminer la mise à jour
            treIdentification.EndUpdate()

            'Sélectionner le premier node
            qNodeLayer = qNodeLayer.FirstNode
            treIdentification.SelectedNode = qNodeLayer

            'Définir l'information sur le nombre de Layers visibles et le nombre d'éléments sélectionnés
            lblInformation.Text = "1 Layer, 1 Élément"

        Catch erreur As Exception
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qNodeLayer = Nothing
            qNodeFeature = Nothing
            pDisplayString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Classe qui permet d'inverser la comparaison pour simuler le tri descendant.
    '''</summary>
    Public Class Descendant
        Implements IComparer

        '''<summary>
        ''' Fonction qui permet d'inverser la comparaison pour simuler le tri descendant.
        '''</summary>
        Public Function Compare(ByVal x As Object, ByVal y As Object) As Integer Implements IComparer.Compare
            'Déclarer les variables de travail
            Dim tx As TreeNode = CType(x, TreeNode)
            Dim ty As TreeNode = CType(y, TreeNode)

            'Retourner le résultat du tri
            Return String.Compare(ty.Text, tx.Text)

        End Function
    End Class

    '''<summary>Flash geometry on the display. The geometry type could be polygon, polyline, point, or multipoint.</summary>
    '''
    '''<param name="geometry"> An IGeometry interface</param>
    '''<param name="color">An IRgbColor interface</param>
    '''<param name="display">An IDisplay interface</param>
    '''<param name="delay">A System.Int32 that is the time im milliseconds to wait.</param>
    ''' 
    '''<remarks></remarks>
    Public Sub FlashGeometry(ByVal geometry As ESRI.ArcGIS.Geometry.IGeometry, ByVal color As ESRI.ArcGIS.Display.IRgbColor, ByVal display As ESRI.ArcGIS.Display.IDisplay, ByVal delay As System.Int32)

        If geometry Is Nothing OrElse color Is Nothing OrElse display Is Nothing Then
            Return
        End If

        display.StartDrawing(display.hDC, CShort(ESRI.ArcGIS.Display.esriScreenCache.esriNoScreenCache))

        Select Case geometry.GeometryType
            Case ESRI.ArcGIS.Geometry.esriGeometryType.esriGeometryPolygon

                'Set the flash geometry's symbol.
                Dim simpleFillSymbol As ESRI.ArcGIS.Display.ISimpleFillSymbol = New ESRI.ArcGIS.Display.SimpleFillSymbolClass
                simpleFillSymbol.Color = color
                Dim symbol As ESRI.ArcGIS.Display.ISymbol = TryCast(simpleFillSymbol, ESRI.ArcGIS.Display.ISymbol) ' Dynamic Cast
                symbol.ROP2 = ESRI.ArcGIS.Display.esriRasterOpCode.esriROPNotXOrPen

                'Flash the input polygon geometry.
                display.SetSymbol(symbol)
                display.DrawPolygon(geometry)
                System.Threading.Thread.Sleep(delay)
                display.DrawPolygon(geometry)
                Exit Select

            Case ESRI.ArcGIS.Geometry.esriGeometryType.esriGeometryPolyline

                'Set the flash geometry's symbol.
                Dim simpleLineSymbol As ESRI.ArcGIS.Display.ISimpleLineSymbol = New ESRI.ArcGIS.Display.SimpleLineSymbolClass
                simpleLineSymbol.Width = 4
                simpleLineSymbol.Color = color
                Dim symbol As ESRI.ArcGIS.Display.ISymbol = TryCast(simpleLineSymbol, ESRI.ArcGIS.Display.ISymbol) ' Dynamic Cast
                symbol.ROP2 = ESRI.ArcGIS.Display.esriRasterOpCode.esriROPNotXOrPen

                'Flash the input polyline geometry.
                display.SetSymbol(symbol)
                display.DrawPolyline(geometry)
                System.Threading.Thread.Sleep(delay)
                display.DrawPolyline(geometry)
                Exit Select

            Case ESRI.ArcGIS.Geometry.esriGeometryType.esriGeometryPoint

                'Set the flash geometry's symbol.
                Dim simpleMarkerSymbol As ESRI.ArcGIS.Display.ISimpleMarkerSymbol = New ESRI.ArcGIS.Display.SimpleMarkerSymbolClass
                simpleMarkerSymbol.Style = ESRI.ArcGIS.Display.esriSimpleMarkerStyle.esriSMSCircle
                simpleMarkerSymbol.Size = 12
                simpleMarkerSymbol.Color = color
                Dim symbol As ESRI.ArcGIS.Display.ISymbol = TryCast(simpleMarkerSymbol, ESRI.ArcGIS.Display.ISymbol) ' Dynamic Cast
                symbol.ROP2 = ESRI.ArcGIS.Display.esriRasterOpCode.esriROPNotXOrPen

                'Flash the input point geometry.
                display.SetSymbol(symbol)
                display.DrawPoint(geometry)
                System.Threading.Thread.Sleep(delay)
                display.DrawPoint(geometry)
                Exit Select

            Case ESRI.ArcGIS.Geometry.esriGeometryType.esriGeometryMultipoint

                'Set the flash geometry's symbol.
                Dim simpleMarkerSymbol As ESRI.ArcGIS.Display.ISimpleMarkerSymbol = New ESRI.ArcGIS.Display.SimpleMarkerSymbolClass
                simpleMarkerSymbol.Style = ESRI.ArcGIS.Display.esriSimpleMarkerStyle.esriSMSCircle
                simpleMarkerSymbol.Size = 12
                simpleMarkerSymbol.Color = color
                Dim symbol As ESRI.ArcGIS.Display.ISymbol = TryCast(simpleMarkerSymbol, ESRI.ArcGIS.Display.ISymbol) ' Dynamic Cast
                symbol.ROP2 = ESRI.ArcGIS.Display.esriRasterOpCode.esriROPNotXOrPen

                'Flash the input multipoint geometry.
                display.SetSymbol(symbol)
                display.DrawMultipoint(geometry)
                System.Threading.Thread.Sleep(delay)
                display.DrawMultipoint(geometry)
                Exit Select

        End Select

        display.FinishDrawing()

    End Sub
#End Region

#Region "Routines et fonctions d'événements"
    Private Sub btnRafraichir_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnRafraichir.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris.
        Dim pFeatureLayer As IFeatureLayer = Nothing        'Interface qui contient la FeatureLayer à traiter.
        Dim pStandaloneTable As IStandaloneTable = Nothing  'Interface qui contient la StandaloneTable à traiter.
        Dim qNode As TreeNode = Nothing                     'Objet contenant le noeud traité.
        Dim qNomTable As Collection = Nothing               'Object contenant les noms des tables.
        Dim bInitialiser As Boolean = True                  'Indique si on doit initialiser

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Initialiser les noms de tables
            qNomTable = New Collection

            'Traiter tous les nodes du TreeView
            For Each qNode In treIdentification.Nodes()
                'Ajouter le nom de la table
                qNomTable.Add(qNode.Name)
            Next

            'Traiter tous les noms de tables
            For i = 1 To qNomTable.Count
                'Définir le FeatureLayer
                pFeatureLayer = m_MapLayer.ExtraireFeatureLayerByName(CStr(qNomTable.Item(i)))

                'Vérifier si le FeatureLayer est valide
                If pFeatureLayer IsNot Nothing Then
                    'Afficher le contenu du FeatureLayer sélectionné
                    Call IdentifierFeatureLayer(pFeatureLayer, bInitialiser)

                Else
                    'Définir le FeatureLayer
                    pStandaloneTable = m_MapLayer.ExtraireStandaloneTableByName(CStr(qNomTable.Item(i)))

                    'Vérifier si le StandaloneTable est valide
                    If pStandaloneTable IsNot Nothing Then
                        'Afficher le contenu de la table sélectionnée
                        Call IdentifierTable2(pStandaloneTable, bInitialiser)

                    Else
                        'Vider les Nodes du Node traité
                        qNode.Nodes.Clear()
                    End If
                End If

                'On ne doit plus initialiser
                bInitialiser = False
            Next

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pFeatureLayer = Nothing
            pStandaloneTable = Nothing
            qNode = Nothing
            qNomTable = Nothing
        End Try
    End Sub

    Private Sub cboTrier_TextChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles cboTrier.TextChanged
        'Vérifier si le tri doit être descendant
        If cboTrier.Text = "Descendant" Then
            'Changer le type de tri
            treIdentification.TreeViewNodeSorter = New Descendant()

            'Si le tri doit être ascendant
        Else
            'Changer le type de tri
            treIdentification.TreeViewNodeSorter = Nothing
            treIdentification.Sort()
        End If
    End Sub

    Private Sub txtMaxItem_TextChanged(ByVal sender As Object, ByVal e As System.EventArgs) Handles txtMaxItem.TextChanged
        Try
            'Vérifier si la valeur est numérique
            If IsNumeric(txtMaxItem.Text) Then
                'Rédéfinir la nouvelle valeur
                m_MaxItems = CInt(txtMaxItem.Text)
            Else
                'Remettre l'ancienne valeur
                txtMaxItem.Text = m_MaxItems.ToString
            End If

        Catch ex As Exception
            Throw
        End Try
    End Sub

    Private Sub treIdentification_NodeMouseDoubleClick(sender As Object, e As TreeNodeMouseClickEventArgs) Handles treIdentification.NodeMouseDoubleClick
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris.
        Dim pFeatureLayer As IFeatureLayer = Nothing        'Contient le FeatureLayer du Noeud sélectionné.
        Dim qNode As TreeNode = Nothing                     'Contient le noeud sélectionné.
        Dim pFeature As IFeature = Nothing                  'Contient l'élément du noeud poour une FeatureClass.
        Dim pEnvelope As IEnvelope = Nothing                'Contient l'enveloppe de la fenêtre graphique.
        Dim pGeometry As IGeometry = Nothing                'Contient la géométrie de l'élément.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Définir le noeud sélectionné
            qNode = treIdentification.SelectedNode

            'Vérifier si le Node est numérique, c'est donc un élément sélectionné
            If IsNumeric(qNode.Name) Then
                'Définir le FeatureLayer du noeud sélectionné
                pFeatureLayer = m_MapLayer.ExtraireFeatureLayerByName(qNode.Parent.Name)

                'Vérifier si la FeatureLayer est valide
                If pFeatureLayer IsNot Nothing Then
                    'Définir l'élément du noeud sélectionné
                    pFeature = pFeatureLayer.FeatureClass.GetFeature(CInt(qNode.Name))
                    'Vérifier si l'élément est valide
                    If pFeature IsNot Nothing Then
                        'Définir la géométrie
                        pGeometry = pFeature.ShapeCopy
                        'Projeter la géométrie
                        pGeometry.Project(m_MxDocument.FocusMap.SpatialReference)
                        'Vérifier si la géométrie est un point
                        If pGeometry.GeometryType = ESRI.ArcGIS.Geometry.esriGeometryType.esriGeometryPoint Then
                            'Définir l'enveloppe de la fenêtre graphique
                            pEnvelope = m_MxDocument.ActiveView.Extent
                            'Définir la nouvelle fenêtre de travail selon le point
                            pEnvelope.CenterAt(CType(pGeometry, ESRI.ArcGIS.Geometry.IPoint))
                        Else
                            'Définir l'enveloppe de la fenêtre graphique
                            pEnvelope = pGeometry.Envelope
                            'Définir la nouvelle fenêtre de travail selon l'enveloppe de la géométrie
                            pEnvelope.Expand(pEnvelope.Width / 10, pEnvelope.Height / 10, False)
                        End If

                        'Définir la nouvelle fenêtre de travail
                        m_MxDocument.ActiveView.Extent = pEnvelope
                        'Rafraîchier l'affichage
                        m_MxDocument.ActiveView.Refresh()
                        'Permet de vider la mémoire sur les évènements
                        System.Windows.Forms.Application.DoEvents()
                    End If
                End If
            End If

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pFeatureLayer = Nothing
            qNode = Nothing
            pFeature = Nothing
            pEnvelope = Nothing
            pGeometry = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine permet de remplir le DataGridView si un élément est sélectionné. 
    '''</summary>
    Private Sub treIdentification_AfterSelect(ByVal sender As Object, ByVal e As System.Windows.Forms.TreeViewEventArgs) Handles treIdentification.AfterSelect
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris.
        Dim pStandaloneTable As IStandaloneTable = Nothing  'Contient le StandaloneTable du Noeud sélectionné.
        Dim pFeatureLayer As IFeatureLayer = Nothing        'Contient le FeatureLayer du Noeud sélectionné.
        Dim qNode As TreeNode = Nothing                     'Contient le noeud sélectionné.
        Dim pRow As IRow = Nothing                          'Contient l'élément du noeud pour une table.
        Dim pFeature As IFeature = Nothing                  'Contient l'élément du noeud poour une FeatureClass.
        Dim pGeometry As IGeometry = Nothing                'Contient la géométrie de l'élément.
        Dim pRgbColor As IRgbColor = Nothing                'Couleur d'affichage pour le Flash d'une géométrie.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Définir le noeud sélectionné
            qNode = treIdentification.SelectedNode

            'Vérifier si le Node est numérique, c'est donc un élément sélectionné
            If IsNumeric(qNode.Name) Then
                'Définir la table du noeud sélectionné
                pStandaloneTable = m_MapLayer.ExtraireStandaloneTableByName(qNode.Parent.Name)

                'Vérifier si la table est valide
                If pStandaloneTable IsNot Nothing Then
                    'Définir l'élément du noeud sélectionné
                    pRow = pStandaloneTable.Table.GetRow(CInt(qNode.Name))

                    'Vérifier si l'élément est valide
                    If pRow IsNot Nothing Then
                        'Définir les attributs de l'élément
                        DataGridAttributElement(pRow, dgvIdentification)
                    End If

                Else
                    'Définir le FeatureLayer du noeud sélectionné
                    pFeatureLayer = m_MapLayer.ExtraireFeatureLayerByName(qNode.Parent.Name)

                    'Vérifier si la FeatureLayer est valide
                    If pFeatureLayer IsNot Nothing Then
                        'Définir l'élément du noeud sélectionné
                        pFeature = pFeatureLayer.FeatureClass.GetFeature(CInt(qNode.Name))
                        'Vérifier si l'élément est valide
                        If pFeature IsNot Nothing Then
                            'Vérifier si il est visible
                            If treIdentification.Focused Then
                                'Définir la couleur
                                pRgbColor = New RgbColor
                                pRgbColor.Red = 255

                                'Définir la géométrie
                                pGeometry = pFeature.ShapeCopy

                                'Projeter la géométrie
                                pGeometry.Project(m_MxDocument.FocusMap.SpatialReference)

                                'Afficher la géométrie sous forme de flash
                                FlashGeometry(pGeometry, pRgbColor, m_MxDocument.ActiveView.ScreenDisplay, 100)
                            End If

                            'Définir les attributs de l'élément
                            DataGridAttributElement(pFeature, dgvIdentification)
                        End If
                    End If
                End If
            End If

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pStandaloneTable = Nothing
            pFeatureLayer = Nothing
            qNode = Nothing
            pRow = Nothing
            pFeature = Nothing
            pGeometry = Nothing
            pRgbColor = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine permet de remplir le Node d'un TreeView lorsqu'un Node doit être ouvert. 
    '''</summary>
    Private Sub treIdentification_BeforeExpand(ByVal sender As Object, ByVal e As System.Windows.Forms.TreeViewCancelEventArgs) Handles treIdentification.BeforeExpand
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris
        Dim pRelClass As IRelationshipClass = Nothing       'Interface qui contient la relation entre les tables
        Dim pTable As ITable = Nothing                      'Interface qui contient la table de base
        Dim pTableRel As ITable = Nothing                   'Interface qui contient la table en relation
        Dim pRow As IRow = Nothing                          'Contient l'élément du noeud

        Try
            'Vérifier si le node est déjà traité
            If e.Node.Checked Then Return

            'Indiquer que le noeud est traité
            e.Node.Checked = True

            'Détruire les Nodes enfants du Node sélectionné
            e.Node.Nodes.Clear()

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si le Node est numérique, c'est donc un élément à ouvrir
            If IsNumeric(e.Node.Name) Then
                'Définir la table de base à partir du Node parent
                pTable = CType(m_MapLayer.ExtraireTableByName(e.Node.Parent.Name), ITable)

                'Vérifier si la table de base est valide
                If pTable IsNot Nothing Then
                    'Définir l'élément de la table de base à partir du noeud sélectionné
                    pRow = pTable.GetRow(CInt(e.Node.Name))

                    'Ajouter les noeuds correspondant aux tables en relation pour un élément
                    AjouterNoeudTable(e.Node, CType(pTable, IRelationshipClassCollection))
                End If

                'Le Node n'est pas numérique, c'est donc une table à ouvrir
            Else
                'Définir la table en relation à partir du noeud sélectionné
                pTableRel = CType(m_MapLayer.ExtraireTableByName(e.Node.Name), ITable)

                'Vérifier si la table en relation est valide
                If pTableRel IsNot Nothing Then
                    'Définir la table de base à partir du parent du noeud parent sélectionné
                    pTable = CType(m_MapLayer.ExtraireTableByName(e.Node.Parent.Parent.Name), ITable)

                    'Vérifier si la table de base est valide
                    If pTable IsNot Nothing Then
                        'Définir l'élément de base à partir du noeud parent sélectionné
                        pRow = pTable.GetRow(CInt(e.Node.Parent.Name))

                        'Extraire la relation
                        pRelClass = ExtraireRelation(pTable, pTableRel)

                        'Ajouter les noeuds d'élément pour une table
                        AjouterNoeudElement2(e.Node, pTable, pRow, pRelClass.OriginPrimaryKey, pTableRel, pRelClass.OriginForeignKey)
                    End If
                End If
            End If

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pRelClass = Nothing
            pTable = Nothing
            pTableRel = Nothing
            pRow = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions privées"
    '''<summary>
    ''' Routine permet d'ajouter tous les nodes de tables (FeatureLayer ou StandAloneTable). 
    '''</summary>
    '''
    '''<param name="qNode">Interface contenant le Node d'affichage.</param>
    '''<param name="pRelClassColl">Interface contenant les classes en relation avec le FeatureLayer traité.</param>
    '''
    ''' <remarks>
    ''' Si aucune relation n'est présente, le Node est vide.
    '''</remarks>
    Private Sub AjouterNoeudTable(ByRef qNode As TreeNode, ByVal pRelClassColl As IRelationshipClassCollection)
        'Déclarer les variables de travail
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing   'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing           'Interface contenant la classe en relation et ses paramètres
        Dim pStandaloneTable As IStandaloneTable = Nothing      'Interface contenant le StandaloneTable
        Dim pFeatureLayer As IFeatureLayer = Nothing            'Interface contenant le FeatureLayer
        Dim pDataset As IDataset = Nothing                      'Interface qui contient le nom du Dataset
        Dim qNodeRel As TreeNode = Nothing                      'Interface contenant le node en relation

        Try
            'Interface pour énumérer les Relates de la classe de découpage
            pEnumRelClass = pRelClassColl.RelationshipClasses

            'Initialiser la recherche des Relates de la classe de découpage
            pEnumRelClass.Reset()

            'Trouver la première classe en relation
            pRelClass = pEnumRelClass.Next

            'Traiter toutes les classes en relation
            Do Until pRelClass Is Nothing
                'Interface pour déterminer le nom et le type de classe
                pDataset = CType(pRelClass.DestinationClass, IDataset)

                'Vérifier si la classe de destination est de type StandaloneTable
                If pDataset.Type = esriDatasetType.esriDTTable Then
                    'Extraire le StandaloneTable par le nom du DatasetName
                    pStandaloneTable = m_MapLayer.ExtraireStandaloneTableByDatasetName(pDataset.Name)

                    'Vérifier si le StandaloneTable est trouvé
                    If pStandaloneTable IsNot Nothing Then
                        'Ajouter le node du StandaloneTable en relation
                        qNodeRel = qNode.Nodes.Add(pStandaloneTable.Name, pStandaloneTable.Name)
                        'Ajouter un node vide
                        qNodeRel = qNodeRel.Nodes.Add(" ", " ")
                    End If

                    'Vérifier si la classe de destination est de type FeatureClass
                ElseIf pDataset.Type = esriDatasetType.esriDTFeatureClass Then
                    'Extraire le FeatureLayer par le nom du DatasetName
                    pFeatureLayer = m_MapLayer.ExtraireFeatureLayerByDatasetName(pDataset.Name)

                    'Vérifier si le FeatureLayer est trouvé
                    If pFeatureLayer IsNot Nothing Then
                        'Ajouter le node du FeatureLayer en relation
                        qNodeRel = qNode.Nodes.Add(pFeatureLayer.Name, pFeatureLayer.Name)
                        'Ajouter un node vide
                        qNodeRel = qNodeRel.Nodes.Add(" ", " ")
                    End If
                End If

                'Trouver la prochaine classe en relation 
                pRelClass = pEnumRelClass.Next
            Loop

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pEnumRelClass = Nothing
            pRelClass = Nothing
            pStandaloneTable = Nothing
            pFeatureLayer = Nothing
            pDataset = Nothing
            qNodeRel = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter tous les noeuds d'éléments de la table de relation liés avec l'élément de base.
    '''</summary>
    '''
    '''<param name="qNode">Contient le noeud traité.</param>
    '''<param name="pTable">Nom de la table contenant l'élément de base.</param>
    '''<param name="pRow">Élément de base pour lequel on recherche ses relations dans la table en relation.</param>
    '''<param name="sAttribut">Nom de l'attribut de l'élément de base.</param>
    '''<param name="pTableRel">Nom de la table contenant les éléments en relation avec l'élément de base.</param>
    '''<param name="sAttributRel">Nom de l'attribut de la table de relation.</param>
    ''' 
    ''' <remarks>
    ''' Si l'élément de base ou les attributs sont invalides, rien n'est effectué.
    '''</remarks>
    Private Sub AjouterNoeudElement2(ByRef qNode As TreeNode, ByVal pTable As ITable, ByVal pRow As IRow, ByVal sAttribut As String, ByVal pTableRel As ITable, ByVal sAttributRel As String)
        'Déclarer les variables de travail
        Dim pCursor As ICursor = Nothing                'Interface qui contient le résultat de la recherche
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface qui contient la requête pour la recherche
        Dim pRowRel As IRow = Nothing                   'Interface qui contient un élément en relation
        Dim pDisplayString As IDisplayString = Nothing  'Interface qui permet d'interpréter l'affichage de l'élément
        Dim qNodeRel As TreeNode = Nothing              'Contient un nouveau Node créé
        Dim nPos As Integer = Nothing                   'Index de l'attribut d'origine ou de destination
        Dim sValeur As String = Nothing                 'Valeur de l'attribut d'origine

        Try
            'Trouver la position de l'attribut d'origine
            nPos = pRow.Fields.FindField(sAttribut)

            'Vérifier si la position est invalide
            If nPos < 0 Then Exit Sub

            'Définir la valeur d'attribut d'origine
            sValeur = pRow.Value(nPos).ToString

            'Créer une nouvelle requête
            pQueryFilter = New QueryFilter

            'Trouver la position de l'attribut en relation
            nPos = pTableRel.FindField(sAttributRel)

            'Vérifier si la position est invalide
            If nPos < 0 Then Exit Sub

            'Interface pour interpréter l'affichage d'un élément
            pDisplayString = CType(pTableRel, IDisplayString)

            'Vérifier si le type de l'attribut est un String
            If pTableRel.Fields.Field(nPos).Type = esriFieldType.esriFieldTypeString Then
                'Définir la requête de recherche avec une valeur de texte
                pQueryFilter.WhereClause = sAttributRel & " = '" & sValeur & "'"
            Else
                'Définir la requête de recherche
                pQueryFilter.WhereClause = sAttributRel & " = " & sValeur
            End If

            'Rechercher les éléments en relation
            pCursor = pTableRel.Search(pQueryFilter, False)

            'Trouver le premier élément
            pRowRel = pCursor.NextRow()

            'Débuter la mise à jour
            treIdentification.BeginUpdate()

            'Traiter tant qu'il y a des éléments
            Do Until pRowRel Is Nothing
                Try
                    'Ajouter le nouveau noeud en relation correspondant à l'affichage de la table
                    qNodeRel = qNode.Nodes.Add(pRowRel.OID.ToString, pDisplayString.FindDisplayString(CType(pRowRel, IObject)))
                Catch
                    'Ajouter le nouveau noeud en relation correspondant à l'affichage de la table
                    qNodeRel = qNode.Nodes.Add(pRowRel.OID.ToString, pRow.OID.ToString)
                End Try

                'Ajouter un Node vide au nouveau Node créé
                qNodeRel.Nodes.Add("", "")

                'Vérifier si le nombre de noeud dépasse la limite
                If qNode.Nodes.Count > m_MaxItems Then Exit Do

                'Trouver le prochain élément
                pRowRel = pCursor.NextRow()
            Loop

            'Terminer la mise à jour
            treIdentification.EndUpdate()

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pCursor = Nothing
            pQueryFilter = Nothing
            pRowRel = Nothing
            pDisplayString = Nothing
            qNodeRel = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter tous les noeuds d'éléments de la table de relation liés avec l'élément de base.
    '''</summary>
    '''
    '''<param name="qNode">Contient le noeud traité.</param>
    '''<param name="pTable">Nom de la table contenant l'élément de base.</param>
    '''<param name="pRow">Élément de base pour lequel on recherche ses relations dans la table en relation.</param>
    '''<param name="sAttribut">Nom de l'attribut de l'élément de base.</param>
    '''<param name="pTableRel">Nom de la table contenant les éléments en relation avec l'élément de base.</param>
    '''<param name="sAttributRel">Nom de l'attribut de la table de relation.</param>
    ''' 
    ''' <remarks>
    ''' Si l'élément de base ou les attributs sont invalides, rien n'est effectué.
    '''</remarks>
    Private Sub AjouterNoeudElement(ByRef qNode As TreeNode, ByVal pTable As ITable, ByVal pRow As IRow, ByVal sAttribut As String, ByVal pTableRel As ITable, ByVal sAttributRel As String)
        'Déclarer les variables de travail
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface qui contient la requête pour la recherche
        Dim pRowRel As IRow = Nothing                   'Interface qui contient un élément en relation
        Dim pDisplayString As IDisplayString = Nothing  'Interface qui permet d'interpréter l'affichage de l'élément
        Dim qNodeRel As TreeNode = Nothing              'Contient un nouveau Node créé
        Dim nPos As Integer = Nothing                   'Index de l'attribut d'origine ou de destination
        Dim sValeur As String = Nothing                 'Valeur de l'attribut d'origine
        Dim pSelectionSet As ISelectionSet = Nothing    'Interface contenant les éléments sélectionnés
        Dim pTableSel As ITableSelection = Nothing      'Interface pour traiter la sélection d'éléments
        Dim pEnumIDs As IEnumIDs = Nothing              'Interface pour extraire les éléments sélectionnés
        Dim nId As Integer = Nothing                    'Identifiant d'un élément

        Try
            'Trouver la position de l'attribut d'origine
            nPos = pRow.Fields.FindField(sAttribut)

            'Vérifier si la position est invalide
            If nPos < 0 Then Exit Sub

            'Définir la valeur d'attribut d'origine
            sValeur = pRow.Value(nPos).ToString

            'Créer une nouvelle requête
            pQueryFilter = New QueryFilter

            'Trouver la position de l'attribut en relation
            nPos = pTableRel.FindField(sAttributRel)

            'Vérifier si la position est invalide
            If nPos < 0 Then Exit Sub

            'Interface pour interpréter l'affichage d'un élément
            pDisplayString = CType(pTableRel, IDisplayString)

            'Vérifier si le type de l'attribut est un String
            If pTableRel.Fields.Field(nPos).Type = esriFieldType.esriFieldTypeString Then
                'Définir la requête de recherche avec une valeur de texte
                pQueryFilter.WhereClause = sAttributRel & " = '" & sValeur & "'"
            Else
                'Définir la requête de recherche
                pQueryFilter.WhereClause = sAttributRel & " = " & sValeur
            End If

            'Ajouter le nouveau noeud en relation correspondant à l'affichage de la table
            'qNode.Nodes.Add(pDisplayString.ExpressionProperties.Expression)

            'Interface pour vérifier la sélection d'éléments
            pTableSel = CType(pTableRel, ITableSelection)

            'Conserver la sélection de la table
            pSelectionSet = pTableSel.SelectionSet

            'Vérifier si aucun élément n'est sélectionné
            If pTableSel.SelectionSet.Count = 0 Then
                'sélectionné seulement les éléments en relation avec les éléments déjà sélectionnés
                pTableSel.SelectRows(pQueryFilter, esriSelectionResultEnum.esriSelectionResultNew, False)

                'Si des éléments sont sélectionnés
            Else
                'sélectionné seulement les éléments en relation avec les éléments déjà sélectionnés
                pTableSel.SelectRows(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAnd, False)
            End If

            'Interface pour extraire les éléments sélectionnés
            pEnumIDs = pTableSel.SelectionSet.IDs
            pEnumIDs.Reset()

            'Extraire le premier Id des éléments sélectionnés
            nId = pEnumIDs.Next

            'Traiter tant qu'il y a des éléments
            Do Until nId = -1
                'Extraire l'élément de la table
                pRowRel = pTableRel.GetRow(nId)

                'Vérifier si l'élément a été trouvé
                If pRowRel IsNot Nothing Then
                    Try
                        'Ajouter le nouveau noeud en relation correspondant à l'affichage de la table
                        qNodeRel = qNode.Nodes.Add(pRowRel.OID.ToString, pDisplayString.FindDisplayString(CType(pRowRel, IObject)))
                        'Ajouter un Node vide au nouveau Node créé
                        qNodeRel.Nodes.Add("", "")

                    Catch
                        'Ajouter le nouveau noeud en relation correspondant à l'affichage de la table
                        qNodeRel = qNode.Nodes.Add(pRowRel.OID.ToString, pRowRel.OID.ToString)
                        'Ajouter un Node vide au nouveau Node créé
                        qNodeRel.Nodes.Add("", "")
                    End Try
                End If


                'Trouver le prochain ID des éléments sélectionnés
                nId = pEnumIDs.Next
            Loop

            'Remettre l'ancienne sélection
            pTableSel.SelectionSet = pSelectionSet

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pQueryFilter = Nothing
            pRowRel = Nothing
            pDisplayString = Nothing
            qNodeRel = Nothing
            pSelectionSet = Nothing
            pTableSel = Nothing
            pEnumIDs = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet d'extraire une relation d'une table à partir d'un nom de table en relation.
    '''</summary>
    '''
    '''<param name="pTable">Interface qui contient la table pour laquelle on veut extraire ses relations.</param>
    '''<param name="pTableRel">Interface qui contient la table en relation.</param>
    '''
    '''<returns>"IRelationshipClass" contenant l'information de la relation.</returns>
    '''
    ''' <remarks>
    ''' Si aucune relation n'est présente, Nothing est retourné.
    '''</remarks>
    Private Function ExtraireRelation(ByVal pTable As ITable, ByVal pTableRel As ITable) As IRelationshipClass
        'Déclarer les variables de travail
        Dim pRelClassColl As IRelationshipClassCollection = Nothing 'Interface contenant toutes les relations d'une table
        Dim pRelClass As IRelationshipClass = Nothing               'Interface contenant une relation d'une table
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing       'Interface qui permet d'extraire une relation
        Dim pDataset As IDataset = Nothing                          'Interface qui contient le nom d'une table

        'Initialiser la valeur par défaut
        ExtraireRelation = Nothing

        Try
            'Interface pour extraire toutes les relations d'une table
            pRelClassColl = CType(pTable, IRelationshipClassCollection)

            'Extraire toutes les relations d'une table
            pEnumRelClass = pRelClassColl.RelationshipClasses

            'Initialiser la recherche des Relations
            pEnumRelClass.Reset()

            'Trouver la première relation
            pRelClass = pEnumRelClass.Next

            'Traiter toutes les relations
            Do Until pRelClass Is Nothing
                'Interface pour extraire le nom de la table en relation
                pDataset = CType(pTableRel, IDataset)

                'Vérifier si le nom de la table en relation correspond avec celle spécifiée
                If pRelClass.DestinationClass.AliasName = pDataset.BrowseName Then
                    'Définir la relation trouvée
                    ExtraireRelation = pRelClass
                    'Sortir de la boucle
                    Exit Do
                End If

                'Trouver la prochaine relation
                pRelClass = pEnumRelClass.Next
            Loop

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pRelClassColl = Nothing
            pRelClass = Nothing
            pEnumRelClass = Nothing
            pDataset = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine permet de remplir le DataGridView à partir des attributs d'un élément spécifié. 
    '''</summary>
    '''
    '''<param name="pRow">Contient l'élément à traiter.</param>
    '''<param name="qDataGridView">DataGridView à remplir.</param>
    '''
    ''' <remarks>
    ''' Si l'élément est invalide, le DataGridView est vide.
    '''</remarks>
    Private Sub DataGridAttributElement(ByVal pRow As IRow, ByRef qDataGridView As DataGridView)
        'Déclarer les variables de travail
        Dim qBindingSource As BindingSource     'BindingSource utilisé pour lié le DataGridView et le DataSet
        Dim qDataTable As DataTable = Nothing   'DataTable utilisé pour contenir les colonnes et les lignes
        Dim qDataSet As DataSet = Nothing       'DataSet utilisé pour présenter et lié les données au DataGridView.
        Dim qDataRow As DataRow = Nothing       'DataRow utilisé pour définir les noms et valeurs d'Atrributs
        Dim pFields As IFields = Nothing        'Interface contenant les attributs de l'élément
        Dim qDataColNom As DataColumn = Nothing     'DataColumn utilisé pour définir la colonne Nom
        Dim qDataColValeur As DataColumn = Nothing  'DataColumn utilisé pour définir la colonne Valeur
        Dim sNomClasse As String = Nothing      'Contient le nom de la classe
        Dim i As Integer = Nothing              'Compteur

        Try
            'Vérifier si le catalogue n'est pas spécifié
            If m_Catalogue Is Nothing Then
                'Définir la liste des codes spécifiques vide
                m_DescCodeSpecifique = New Dictionary(Of String, String)
                'Définir la listes des valeurs d'attributs vide
                m_DescValeurAttribut = New Dictionary(Of String, String)

                'Si le catalogue est spécifié
            Else
                'Interface pour extraire le nom de la table
                Dim pDataset As IDataset = CType(pRow.Table, IDataset)
                'Vérifier si le nom de la classe contient le propriétaire
                If pDataset.BrowseName.Contains(".") Then
                    'Définir le nom de la classe sans le propiétaire de la classe
                    sNomClasse = pDataset.BrowseName.Split(CChar("."))(1)
                Else
                    'Définir le nom de la classe
                    sNomClasse = pDataset.BrowseName
                End If
                'Définir la liste des codes spécifiques
                m_DescCodeSpecifique = m_Catalogue.ExtraireListeCodeSpecifique(sNomClasse)
                'Définir la listes des valeurs d'attributs
                m_DescValeurAttribut = m_Catalogue.ExtraireListeValeurAttribut(sNomClasse)
                'Vider la mémoire
                pDataset = Nothing
            End If

            'Créer un nouveau DataTable
            qDataTable = New DataTable("DataTable")

            'Créer un nouveau DataSet. 
            qDataSet = New DataSet("DataSet")

            'Définir la colonne Nom
            qDataColNom = New DataColumn
            With qDataColNom
                .DataType = System.Type.GetType("System.String")
                .ColumnName = "Nom"
                .Caption = "Nom"
            End With
            'Ajouter la colonne Nom à la table
            qDataTable.Columns.Add(qDataColNom)

            'Définir la colonne Valeur
            qDataColValeur = New DataColumn
            With qDataColValeur
                .DataType = System.Type.GetType("System.String")
                .ColumnName = "Valeur"
                .Caption = "Valeur"
            End With
            'Ajouter la colonne Valeur à la table
            qDataTable.Columns.Add(qDataColValeur)

            'Ajouter la table contenant les colonnes au dataset
            qDataSet.Tables.Add(qDataTable)

            'Vérifier si l'élément est invalide
            If pRow Is Nothing Then Return

            'Définir l'interface des attributs
            pFields = pRow.Fields

            'Traiter tous les attributs de l'élément
            For i = 0 To pFields.FieldCount - 1
                'Créer une nouvelle ligne dans la table
                qDataRow = qDataTable.NewRow()

                'Définir le nom de l'attribut
                qDataRow("Nom") = pFields.Field(i).Name

                'Vérifier si le type d'attribut est une géométrie
                If pFields.Field(i).Type = ESRI.ArcGIS.Geodatabase.esriFieldType.esriFieldTypeGeometry Then
                    'Définir la valeur de l'attribut
                    qDataRow("Valeur") = pFields.Field(i).GeometryDef.GeometryType.ToString

                    'Vérifier si le type est un entier
                ElseIf pFields.Field(i).Type = ESRI.ArcGIS.Geodatabase.esriFieldType.esriFieldTypeInteger Then
                    'Vérifier si l'attribut est un code spécifique
                    If pFields.Field(i).Name = "CODE_SPEC" Then
                        'Vérifier si la description est disponible
                        If m_DescCodeSpecifique.ContainsKey(pRow.Value(i).ToString) Then
                            'Définir la valeur et sa description
                            qDataRow("Valeur") = pRow.Value(i).ToString & ":" & m_DescCodeSpecifique.Item(pRow.Value(i).ToString)
                        Else
                            'Vérifier si la valeur est nulle
                            If IsDBNull(pRow.Value(i)) Then
                                'Définir la valeur de l'attribut
                                qDataRow("Valeur") = "<null>"
                            Else
                                'Définir la valeur de l'attribut
                                qDataRow("Valeur") = pRow.Value(i).ToString
                            End If
                        End If

                        'Si l'attribut n'est pas un code spécifique
                    Else
                        'Vérifier si la description est disponible
                        If m_DescValeurAttribut.ContainsKey(pFields.Field(i).Name & "_" & pRow.Value(i).ToString) Then
                            'Définir la valeur et sa description
                            qDataRow("Valeur") = pRow.Value(i).ToString & ":" & m_DescValeurAttribut.Item(pFields.Field(i).Name & "_" & pRow.Value(i).ToString)
                        Else
                            'Vérifier si la valeur est nulle
                            If IsDBNull(pRow.Value(i)) Then
                                'Définir la valeur de l'attribut
                                qDataRow("Valeur") = "<null>"
                            Else
                                'Définir la valeur de l'attribut
                                qDataRow("Valeur") = pRow.Value(i).ToString
                            End If
                        End If
                    End If

                    'Si le type d'attribut n'est pas une géométrie ni un entier
                Else
                    'Vérifier si la valeur est nulle
                    If IsDBNull(pRow.Value(i)) Then
                        'Définir la valeur de l'attribut
                        qDataRow("Valeur") = "<null>"
                    Else
                        'Définir la valeur de l'attribut
                        qDataRow("Valeur") = pRow.Value(i).ToString
                    End If
                End If

                'Définir les attributs dans le DataGridView
                qDataTable.Rows.Add(qDataRow)
            Next

            'Creer un BindingSource pour effectuer le lien entre le dataset et le DataGridView
            qBindingSource = New BindingSource

            'Lié le DataTable au DataSet via le BindingSource
            qBindingSource.DataSource = qDataSet.Tables.Item("DataTable")

            'Lié le DataSet au DataGridview via le BindingSource
            qDataGridView.DataSource = qBindingSource

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pFields = Nothing
            qBindingSource = Nothing
            qDataTable = Nothing
            qDataSet = Nothing
            qDataRow = Nothing
            qDataColNom = Nothing
            qDataColValeur = Nothing
            sNomClasse = Nothing
            i = Nothing
        End Try
    End Sub
#End Region
End Class