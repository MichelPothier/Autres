Imports System.Windows.Forms
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports System.Drawing
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.GeoDatabaseUI
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS

''' <summary>
''' Designer class of the dockable window add-in. It contains user interfaces that
''' make up the dockable window.
''' </summary>
Public Class dckMenuRelations
    'Déclarer les variables de travail
    Private m_hook As Object                                        'Application par lequel le menu a été appelée
    Private m_NodeRel As TreeNode = Nothing                         'Contient la copie du Noeud
    Private m_RelationshipClass As IRelationshipClass = Nothing     'Contient la copie d'une relation
    Private m_ListeValeur As New Collection                         'Collections des listes de valeur
    Private m_Click As Integer = 0                                  'Nombre de click effectué

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

        Private m_windowUI As dckMenuRelations

        Protected Overrides Function OnCreateChild() As System.IntPtr
            m_windowUI = New dckMenuRelations(Me.Hook)
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

            'Définir le menu
            m_MenuRelations = Me

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
            windowID.Value = "MPO_BarreSIB_dckMenuRelations"
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
            windowID.Value = "MPO_BarreSIB_dckMenuRelations"
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
    ''' Routine qui permet d'identifier toutes les relations pour tous les FeatureLayer et toutes les tables dans la Map.
    '''</summary>
    ''' 
    '''<param name="pMap"> Interface ESRI contenant tous les FeatureLayers et tous les StandaloneTables.</param>
    '''
    Public Sub IdentifierMap(ByVal pMap As IMap)
        'Déclarer la variables de travail
        Dim qFeatureLayerColl As Collection = Nothing           'Contient la liste des FeatureLayer visibles
        Dim pFeatureLayer As IFeatureLayer = Nothing            'Interface contenant une classe de données
        Dim pStandaloneTableColl As IStandaloneTableCollection  'Interface qui permet d'extraire les StandaloneTable de la Map
        Dim pStandaloneTable As IStandaloneTable = Nothing      'Interface contenant le StandaloneTable
        Dim pTableDef As ITableDefinition = Nothing             'Interface contenant la requête associée à la table
        Dim qNode As TreeNode = Nothing                         'Interface contenant le node traité
        Dim qRelColl As Collection = Nothing                    'Objet qui permet de contenir toutes les relations déjà traitées.
        Dim pCursor As ICursor = Nothing                        'Interface qui permet d'extraire les éléments.
        Dim pRow As IRow = Nothing                              'Interface contenant un élément.

        Try
            'Définir une liste d'images pour afficher les Noeuds avec ou sans requête
            treRelations.StateImageList = New ImageList()
            treRelations.StateImageList.Images.Add(CType(My.Resources.ResourceManager.GetObject("Requete"), System.Drawing.Image))
            'treRelations.StateImageList.Images.Add(SystemIcons.Question)

            'Initialiser les relations traitées
            qRelColl = New Collection

            'Initialiser les nodes
            treRelations.Nodes.Clear()

            'Vider le contenu du DataGridView en ajoutant un nouveau Dataset vide
            dgvListesAttributs.DataSource = New DataSet("DataSet")

            'Vider le contenu du RichTextBox contenant une requête
            rtxRequete.Text = ""

            'Définir le MapLayer et tous les FeatureLayer visibles ou non
            m_MapLayer = New clsGererMapLayer(pMap, False)

            'Définir la liste des FeatureLayer
            qFeatureLayerColl = m_MapLayer.FeatureLayerCollection

            'vérifier si les FeatureLayers sont présents
            If qFeatureLayerColl IsNot Nothing Then
                'Traiter tous les FeatureLayer
                For i = 1 To qFeatureLayerColl.Count
                    'Définir le FeatureLayer
                    pFeatureLayer = CType(qFeatureLayerColl.Item(i), IFeatureLayer)

                    'Vérifier si le FeatureLayer est absent
                    If Not qRelColl.Contains(pFeatureLayer.Name) Then
                        'Vérifier si la classe contient des OIDs
                        If pFeatureLayer.FeatureClass.HasOID = True Then
                            'Ajouter le Node du FeatureLayer
                            qNode = treRelations.Nodes.Add(pFeatureLayer.Name, pFeatureLayer.Name)
                            qNode.Tag = pFeatureLayer.FeatureClass.AliasName
                            qRelColl.Add(qNode, qNode.Text)

                            'Interface pour vérifier la présence de la requête attributive
                            pTableDef = CType(pFeatureLayer, ITableDefinition)
                            'Vérifier la présence de la requête attributive
                            If pTableDef.DefinitionExpression.Length > 0 Then
                                'Changer la couleur du texte pour rouge
                                'qNode.ForeColor = Color.Red
                                qNode.StateImageIndex = 0
                                'Si pas de requête attributive
                            Else
                                'Changer la couleur du texte pour noir
                                'qNode.ForeColor = Color.Black
                                qNode.StateImageIndex = -1
                            End If

                            'Identifier toutes les relations du Node traité
                            Call IdentifierRelations(CType(pFeatureLayer, IRelationshipClassCollection), qNode, qRelColl)

                            'Ouvrir seulement le premier niveau de l'arbre
                            qNode.Expand()
                        End If
                    End If
                Next
            End If

            'Définir la liste des StandaloneTable
            pStandaloneTableColl = CType(pMap, IStandaloneTableCollection)

            'Traiter tous les StandaloneTable
            For i = 0 To pStandaloneTableColl.StandaloneTableCount - 1
                'Définir le StandaloneTable
                pStandaloneTable = pStandaloneTableColl.StandaloneTable(i)

                'Vérifier si le StandaloneTable est absent
                If Not qRelColl.Contains(pStandaloneTable.Name) Then
                    'Vérifier si la table contient des OIDs
                    If pStandaloneTable.Table.HasOID = True Then
                        'Ajouter le Node du FeatureLayer
                        qNode = treRelations.Nodes.Add(pStandaloneTable.Name, pStandaloneTable.Name)
                        qRelColl.Add(qNode, qNode.Text)

                        'Interface pour vérifier la présence de la requête attributive
                        pTableDef = CType(pStandaloneTable, ITableDefinition)
                        'Vérifier la présence de la requête attributive
                        If pTableDef.DefinitionExpression.Length > 0 Then
                            'Changer la couleur du texte pour rouge
                            'qNode.ForeColor = Color.Red
                            qNode.StateImageIndex = 0
                            'Si pas de requête attributive
                        Else
                            'Changer la couleur du texte pour noir
                            'qNode.ForeColor = Color.Black
                            qNode.StateImageIndex = -1
                        End If

                        'Identifier toutes les relations du Node traité
                        Call IdentifierRelations(CType(pStandaloneTable, IRelationshipClassCollection), qNode, qRelColl)

                        'Ouvrir seulement le premier niveau de l'arbre
                        qNode.Expand()
                    End If
                End If
            Next

            'Trier tous les nodes
            treRelations.Sort()

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qFeatureLayerColl = Nothing
            pFeatureLayer = Nothing
            pStandaloneTableColl = Nothing
            pStandaloneTable = Nothing
            pTableDef = Nothing
            qNode = Nothing
            pCursor = Nothing
            pRow = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'identifier toutes les relations liées à une table et de les ajouter dans le Node de la table.
    '''</summary>
    ''' 
    '''<param name="pRelClassColl"> Interface ESRI contenant toutes les relations d'une table.</param>
    '''<param name="qNode"> Interface ESRI contenant le node de la table traitée.</param>
    '''<param name="qRelColl"> Objet contenant les relations traitées.</param>
    '''
    Public Sub IdentifierRelations(ByVal pRelClassColl As IRelationshipClassCollection, ByRef qNode As TreeNode, ByRef qRelColl As Collection)
        'Déclarer la variables de travail
        Dim pFeatureLayer As IFeatureLayer = Nothing            'Interface contenant une classe de données
        Dim pStandaloneTable As IStandaloneTable = Nothing      'Interface contenant le StandaloneTable
        Dim pTableDef As ITableDefinition = Nothing             'Interface contenant la requête associée à la table
        Dim pDataset As IDataset = Nothing                      'Interface qui contient le nom du Dataset
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing   'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing           'Interface contenant la classe en relation et ses paramètres
        Dim qRelNode As TreeNode = Nothing                      'Interface contenant le node en relation

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
                        qRelNode = qNode.Nodes.Add(pStandaloneTable.Name, pStandaloneTable.Name)
                        qRelNode.Tag = pDataset.Name
                        If Not qRelColl.Contains(qRelNode.Text) Then qRelColl.Add(qRelNode, qRelNode.Text)

                        'Interface pour vérifier la présence de la requête attributive
                        pTableDef = CType(pStandaloneTable, ITableDefinition)
                        'Vérifier la présence de la requête attributive
                        If pTableDef.DefinitionExpression.Length > 0 Then
                            'Changer la couleur du texte pour rouge
                            'qRelNode.ForeColor = Color.Red
                            qRelNode.StateImageIndex = 0
                            'Si pas de requête attributive
                        Else
                            'Changer la couleur du texte pour noir
                            'qRelNode.ForeColor = Color.Black
                            qRelNode.StateImageIndex = -1
                        End If

                        'Identifier toutes les relations du Node traité
                        Call IdentifierRelations(CType(pStandaloneTable, IRelationshipClassCollection), qRelNode, qRelColl)
                    End If

                    'Vérifier si la classe de destination est de type FeatureClass
                ElseIf pDataset.Type = esriDatasetType.esriDTFeatureClass Then
                    'Extraire le FeatureLayer par le nom du DatasetName
                    pFeatureLayer = m_MapLayer.ExtraireFeatureLayerByDatasetName(pDataset.Name)

                    'Vérifier si le FeatureLayer est trouvé
                    If pFeatureLayer IsNot Nothing Then
                        'Ajouter le node du FeatureLayer en relation
                        qRelNode = qNode.Nodes.Add(pFeatureLayer.Name, pFeatureLayer.Name)
                        qRelNode.Tag = pDataset.Name
                        If Not qRelColl.Contains(qRelNode.Text) Then qRelColl.Add(qRelNode, qRelNode.Text)

                        'Interface pour vérifier la présence de la requête attributive
                        pTableDef = CType(pFeatureLayer, ITableDefinition)
                        'Vérifier la présence de la requête attributive
                        If pTableDef.DefinitionExpression.Length > 0 Then
                            'Changer la couleur du texte pour rouge
                            'qRelNode.ForeColor = Color.Red
                            qRelNode.StateImageIndex = 0
                            'Si pas de requête attributive
                        Else
                            'Changer la couleur du texte pour noir
                            'qRelNode.ForeColor = Color.Black
                            qRelNode.StateImageIndex = -1
                        End If

                        'Identifier toutes les relations du Node traité
                        Call IdentifierRelations(CType(pFeatureLayer, IRelationshipClassCollection), qRelNode, qRelColl)
                    End If
                End If

                'Trouver la prochaine classe en relation 
                pRelClass = pEnumRelClass.Next
            Loop

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pFeatureLayer = Nothing
            pStandaloneTable = Nothing
            pTableDef = Nothing
            pDataset = Nothing
            pEnumRelClass = Nothing
            pRelClass = Nothing
            qRelNode = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions d'événement"
    '''<summary>
    ''' Routine qui permet de rafraichir la structure des relations.
    '''</summary>
    ''' 
    Private Sub btnRafraichirRelations_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnRafraichirRelations.Click
        Try
            'Identifier toutes les relations pour toutes les tables de la Map active
            m_MenuRelations.IdentifierMap(m_MxDocument.FocusMap)

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de copier en mémoire la relation entre la table sélectionnée et la table parent.
    '''</summary>
    ''' 
    Private Sub btnCopierRelation_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCopierRelation.Click
        'Déclarer les variables de travail 
        Dim pTableOrigine As IDataset = Nothing         'Table d'origine
        Dim pTableDestination As IDataset = Nothing     'Table de destination
        Dim pRelClass As IRelationshipClass = Nothing   'Interface contenant la nouvelle relation

        Try
            'Sortir si un noeud n'est pas sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Sortir si le noeud sélectionné ne possède pas de parent
            If treRelations.SelectedNode.Parent Is Nothing Then Exit Sub

            'Extraire la table d'origine par le text du node parent
            pTableOrigine = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Parent.Text), IDataset)

            'Extraire la table de destination par le text du node
            pTableDestination = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), IDataset)

            'Trouver la relation à partir du nom de la table en relation
            pRelClass = TrouverRelationShipTable(pTableOrigine, pTableDestination.BrowseName)

            'Vérifier si la relation a été trouvée
            If pRelClass IsNot Nothing Then
                'Conserver en mémoire la relation
                m_RelationshipClass = pRelClass
                'Conserver en mémoire le noeud de la relation
                m_NodeRel = treRelations.SelectedNode
                'Activer le bouton pour coller la relation
                btnCollerRelation.Enabled = True
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTableOrigine = Nothing
            pTableDestination = Nothing
            pRelClass = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de coller la relation présente en mémoire dans la table sélectionnée,
    ''' mais seulement si c'est la même classe que celle du parent.
    '''</summary>
    ''' 
    Private Sub btnCollerRelation_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnCollerRelation.Click
        'Déclarer les variables de travail 
        Dim pTableOrigine As IDataset = Nothing         'Table d'origine

        Try
            'Sortir si un noeud n'est pas sélectionné ou s'il n'y a pas de relation en mémoire
            If treRelations.SelectedNode Is Nothing Or m_RelationshipClass Is Nothing Then Exit Sub

            'Extraire la table par le text du node
            pTableOrigine = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), IDataset)

            'Vérifier si la relation a été ajoutée. doit être la même classe
            If AjouterRelationShipTable(pTableOrigine, m_RelationshipClass) Then
                'Coller le nouveau Node en relation
                treRelations.SelectedNode.Nodes.Add(CType(m_NodeRel.Clone(), TreeNode))
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTableOrigine = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire la relation entre la table sélectionnée et la table parent.
    '''</summary>
    ''' 
    Private Sub btnDetruireRelation_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDetruireRelation.Click
        'Déclarer les variables de travail 
        Dim pTableOrigine As IDataset = Nothing             'Table d'origine
        Dim pTableDestination As IDataset = Nothing         'Table de destination
        Dim qResultat As DialogResult = Nothing             'Contient le résultat d'une question

        Try
            'Sortir si un noeud n'est pas sélectionné
            If treRelations.SelectedNode Is Nothing Or treRelations.SelectedNode.Parent Is Nothing Then Exit Sub

            'Extraire la table d'origine par le text du node parent
            pTableOrigine = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Parent.Text), IDataset)

            'Extraire la table de destination par le text du node
            pTableDestination = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), IDataset)

            'Afficher la boîte de dialogue pour vérifier si on veut vraiment détruire la relation
            qResultat = MessageBox.Show("Voulez-vous vraiement détruire la relation ?", treRelations.SelectedNode.Text, MessageBoxButtons.YesNo)

            'Vérifier si la réponse est Oui
            If qResultat = DialogResult.Yes Then
                'Vérifier si la relation a été détruite
                DetruireRelationShipTable(pTableOrigine, CStr(treRelations.SelectedNode.Tag))

                'Détruire le node
                treRelations.SelectedNode.Remove()
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTableOrigine = Nothing
            pTableDestination = Nothing
            qResultat = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter une relation entre la table sélectionnée et une nouvelle table à partir du menu de construction.
    '''</summary>
    ''' 
    Private Sub btnAjouterRelation_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnAjouterRelation.Click
        'Déclarer les variables de travail 
        Dim qNodeRel As TreeNode = Nothing                  'Node traité en relation
        Dim pTableOrigine As IDataset = Nothing             'Table d'origine
        Dim pTableDestination As IDataset = Nothing         'Table de destination
        Dim pRelateData As IRelateData2 = Nothing           'Interface qui permet d'afficher le menu pour créer une relation
        Dim pDataset As IDataset = Nothing                  'Interface contenant le nom de la nouvelle relation
        Dim pRelClass As IRelationshipClass = Nothing       'Interface contenant la nouvelle relation

        Try
            'Sortir si un noeud n'est pas sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Extraire la table par le text du node
            pTableOrigine = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), IDataset)

            'Créer un nouveau menu pour créer une relation
            pRelateData = CType(New RelateData, IRelateData2)

            'Définir les paramètres du menu
            pRelateData.Application = m_Application
            pRelateData.RelateOrigin = pTableOrigine

            'Afficher le menu et retourner la nouvelle relation
            pRelClass = pRelateData.DoModal(m_Application.hWnd)

            'Sortir si la relation n'a pas été créée
            If pRelClass Is Nothing Then Exit Sub

            'Interface pour obtenir le nom de la relation
            pDataset = CType(pRelClass, IDataset)

            'Vérifier le nom de la relation
            If pDataset.Name = "Relate1" Then pDataset.Rename(pRelClass.ForwardPathLabel)

            'Vérifier si la relation a été ajoutée
            If AjouterRelationShipTable(pTableOrigine, pRelClass) Then
                'Extraire le nom de la table en relation
                pTableDestination = CType(m_MapLayer.ExtraireTableByDatasetName(pRelClass.DestinationClass.AliasName), IDataset)

                'Créer le nouveau Node en relation
                qNodeRel = treRelations.SelectedNode.Nodes.Add(pTableDestination.Name, pTableDestination.Name)
                qNodeRel.Tag = pRelClass.DestinationClass.AliasName

                'Ajouter toutes les autres relation de la table en relation
                Call IdentifierRelations(CType(pTableDestination, IRelationshipClassCollection), qNodeRel, New Collection)
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qNodeRel = Nothing
            pTableOrigine = Nothing
            pTableDestination = Nothing
            pRelateData = Nothing
            pDataset = Nothing
            pRelClass = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ouvrir la table sélectionnée.
    '''</summary>
    ''' 
    Private Sub btnOuvrirTable_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnOuvrirTable.Click
        'Déclarer les variables de travail
        Dim pTableWindow2 As ITableWindow2 = Nothing    'Interface qui permet de verifier la présence du menu des tables d'attributs et de les manipuler
        Dim pExistTableWindow As ITableWindow = Nothing 'Interface contenant le menu de la table d'attributs existente
        Dim pTable As ITable = Nothing                  'Interface contenant la table à ouvrir dans le menu des tables d'attributs

        Try
            'Sortir si un noeud n'est pas sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Interface pour vérifier la présence du menu des tables d'attributs
            pTableWindow2 = CType(New TableWindow, ITableWindow2)

            'Extraire la table correspondant au noeud sélectionné
            pTable = m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text)

            'Vérifier si la table est valide
            If pTable IsNot Nothing Then
                'Vérifier si le type de table est un FeatureLayer
                If TypeOf pTable Is FeatureLayer Then
                    'Définir le menu de la table d'attribut de la table s'il est présent
                    pExistTableWindow = pTableWindow2.FindViaLayer(CType(pTable, ILayer))
                    'Vérifier si le menu de la table d'attribut est absent
                    If pExistTableWindow Is Nothing Then
                        'Définir le FeatureLayer à afficher
                        pTableWindow2.Layer = CType(pTable, ILayer)
                    End If

                    'Si le type de table est un StandaloneTable
                ElseIf TypeOf pTable Is StandaloneTable Then
                    'Extraire la table correspondant au noeud sélectionné
                    pExistTableWindow = pTableWindow2.FindViaStandaloneTable(CType(pTable, IStandaloneTable))
                    'Vérifier si le menu de la table d'attribut est absent
                    If pExistTableWindow Is Nothing Then
                        'Définir le StandaloneTable à afficher
                        pTableWindow2.StandaloneTable = CType(pTable, IStandaloneTable)
                    End If
                End If

                'Vérifier le menu de la table d'attribut est absent
                If pExistTableWindow Is Nothing Then
                    'Définir les paramètre d'affichage du menu des tables d'attributs
                    pTableWindow2.TableSelectionAction = esriTableSelectionActions.esriSelectFeatures
                    pTableWindow2.ShowSelected = False
                    pTableWindow2.ShowAliasNamesInColumnHeadings = True
                    pTableWindow2.Application = m_Application

                    'Si le menu de la table d'attribut est présent
                Else
                    'Redéfinir le menu des tables d'attributs pour celui existant
                    pTableWindow2 = CType(pExistTableWindow, ITableWindow2)
                End If

                'Afficher le menu des tables d'attributs s'il n'est pas affiché
                If Not pTableWindow2.IsVisible Then pTableWindow2.Show(True)
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTableWindow2 = Nothing
            pExistTableWindow = Nothing
            pTable = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de remplir le menu d'identification à partir des éléments sélectionnés de la table sélectionnée
    '''</summary>
    ''' 
    Private Sub btnIdentifier_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnIdentifier.Click
        'Déclarer les variables de travail
        Dim pTable As ITable = Nothing                  'Interface contenant la table à ouvrir dans le menu des tables d'attributs
        Dim pMouseCursor As IMouseCursor = Nothing      'Interface qui permet de changer le curseur de la souris

        Try
            'Sortir si un noeud n'est pas sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Extraire la table correspondant au noeud sélectionné
            pTable = m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text)

            'Vérifier si la table est valide
            If pTable IsNot Nothing Then
                'Vérifier si le type de table est un FeatureLayer
                If TypeOf pTable Is FeatureLayer Then
                    'Identifier les éléments sélectionnés via le menu d'identification
                    m_MenuIdentification.IdentifierFeatureLayer(CType(pTable, IFeatureLayer), True)

                    'Si le type de table est un StandaloneTable
                ElseIf TypeOf pTable Is StandaloneTable Then
                    'Identifier les éléments sélectionnés via le menu d'identification
                    m_MenuIdentification.IdentifierTable2(CType(pTable, IStandaloneTable), True)
                End If
            End If

            'Afficher le menu d'identification
            m_MenuIdentification.Show(True)

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTable = Nothing
            pMouseCursor = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'un DragAndDrop est terminé.
    ''' La relation est déplacée ou copiée à condition que le lien de la relation soit valide avec celui de la cible.
    ''' Si la cible ne correspond pas à un Node du TreeView, la relation est détruite.
    '''</summary>
    ''' 
    Private Sub treRelations_DragDrop(ByVal sender As Object, ByVal e As System.Windows.Forms.DragEventArgs) Handles treRelations.DragDrop
        'Déclarer les variables de travail 
        Dim qDraggedNode As TreeNode = Nothing              'Node traité
        Dim qTargetPoint As System.Drawing.Point = Nothing  'Coordonnées correspondant au Node cible
        Dim qTargetNode As TreeNode = Nothing               'Node cible
        Dim pTableOrigine As IDataset = Nothing             'Table d'origine
        Dim pTableDestination As IDataset = Nothing         'Table de destination
        Dim pRelateData As IRelateData2 = Nothing           'Interface qui permet d'afficher le menu pour créer une relation
        Dim pRelClass As IDataset = Nothing                 'Interface contenant une nouvelle relation
        Dim qResultat As DialogResult = Nothing             'Contient le résultat d'une question

        Try
            'Extraire le Node à détruire, à déplacer ou à copier
            qDraggedNode = CType(e.Data.GetData(GetType(TreeNode)), TreeNode)

            'Extraire les coordonnées correspondant au Node cible
            qTargetPoint = treRelations.PointToClient(New System.Drawing.Point(e.X, e.Y))
            'Extraire le Node cible
            qTargetNode = treRelations.GetNodeAt(qTargetPoint)

            'Vérifier si le Node parent du DraggedNode est invalide
            If qDraggedNode.Parent Is Nothing Then
                'Vérifer si le Node cible est valide
                If qTargetNode IsNot Nothing Then
                    'Extraire la table par le text du node
                    pTableOrigine = CType(m_MapLayer.ExtraireTableByName(qTargetNode.Text), IDataset)
                    'Extraire le FeatureLayer par le text du node
                    pTableDestination = CType(m_MapLayer.ExtraireTableByName(qDraggedNode.Text), IDataset)

                    'Créer un nouveau menu pour créer une relation
                    pRelateData = CType(New RelateData, IRelateData2)
                    'Définir les paramètre du menu
                    pRelateData.Application = m_Application
                    pRelateData.RelateOrigin = pTableOrigine
                    pRelateData.StandaloneTable = CType(pTableDestination, IStandaloneTable)
                    'Afficher le menu et retourner la nouvelle relation
                    pRelClass = CType(pRelateData.DoModal(m_Application.hWnd), IDataset)
                    'Vérifier le nom de la relation
                    If pRelClass.Name = "Relate1" Then pRelClass.Rename(pTableDestination.Name)
                    'Vérifier si la relation a été ajoutée
                    If AjouterRelationShipTable(pTableOrigine, CType(pRelClass, IRelationshipClass)) Then
                        'Ajouter le node
                        qTargetNode.Nodes.Add(CType(qDraggedNode.Clone(), TreeNode))
                        'Détruire le node
                        qDraggedNode.Remove()
                    End If
                End If

                'Vérifier si le Node de la cible est invalide
            ElseIf qTargetNode Is Nothing Then
                'Extraire le FeatureLayer par le text du node
                pTableOrigine = CType(m_MapLayer.ExtraireTableByName(qDraggedNode.Parent.Text), IDataset)

                'Afficher la boîte de dialogue pour vérifier si on veut vraiment détruire la relation
                qResultat = MessageBox.Show("Voulez-vous vraiement détruire la relation ?", qDraggedNode.Text, MessageBoxButtons.YesNo)
                'Vérifier si la réponse est Oui
                If qResultat = DialogResult.Yes Then
                    'Vérifier si la relation a été détruite
                    DetruireRelationShipTable(pTableOrigine, CStr(qDraggedNode.Tag))
                    'Détruire le node
                    qDraggedNode.Remove()
                End If

                'Vérifier si le node de la cible n'est pas le même Node
            ElseIf Not qDraggedNode.Equals(qTargetNode) Then
                'Extraire le FeatureLayer par le text du node
                pTableOrigine = CType(m_MapLayer.ExtraireTableByName(qDraggedNode.Parent.Text), IDataset)
                'Extraire la table par le text du node
                pTableDestination = CType(m_MapLayer.ExtraireTableByName(qTargetNode.Text), IDataset)

                'Vérifier si la copie de la relation a réussie
                If CopierRelationShipTable(pTableOrigine, pTableDestination, CStr(qDraggedNode.Tag)) Then
                    'Vérifier si l'effect est un déplacement 
                    If e.Effect = DragDropEffects.Move Then
                        'Ajouter le node
                        qTargetNode.Nodes.Add(CType(qDraggedNode.Clone(), TreeNode))
                        'Détruire le node
                        qDraggedNode.Remove()

                        'Vérifier si l'effect est une copie
                    ElseIf e.Effect = DragDropEffects.Copy Then
                        'Copier le Node dans la cible
                        qTargetNode.Nodes.Add(CType(qDraggedNode.Clone(), TreeNode))
                    End If
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qTargetPoint = Nothing
            qTargetNode = Nothing
            qDraggedNode = Nothing
            pTableOrigine = Nothing
            pTableDestination = Nothing
            pRelateData = Nothing
            pRelClass = Nothing
            qResultat = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'un DragAndDrop est débuté pour donnéer l'effect visuel.
    '''</summary>
    ''' 
    Private Sub treRelations_DragEnter(ByVal sender As Object, ByVal e As System.Windows.Forms.DragEventArgs) Handles treRelations.DragEnter
        'Initier l'effet visuel du traitement de DragAndDrop
        e.Effect = e.AllowedEffect
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'un DragAndDrop est initié.
    ''' La souris de gauche permet de déplacer une relation.
    ''' Le bouton de droite permet de copier une relation.
    '''</summary>
    ''' 
    Private Sub treRelations_ItemDrag(ByVal sender As Object, ByVal e As System.Windows.Forms.ItemDragEventArgs) Handles treRelations.ItemDrag
        'Vérifier si le bouton est celui de droite 
        If e.Button = MouseButtons.Right Then
            'Initier un déplacement de relation
            DoDragDrop(e.Item, DragDropEffects.Move)

            'Vérifier si le bouton est celui de gauche
        ElseIf e.Button = MouseButtons.Left Then
            'Initier une copie de relation
            DoDragDrop(e.Item, DragDropEffects.Copy)
        End If
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'une touche du clavier est enfoncée avec un objet du menu des relations.
    ''' On ouvre tous les Noeuds si la touche Shift est enfoncée.
    '''</summary>
    ''' 
    Private Sub treRelations_KeyDown(ByVal sender As Object, ByVal e As System.Windows.Forms.KeyEventArgs) Handles treRelations.KeyDown
        'Déclarer les variables de travail
        Dim qTreeView As TreeView = Nothing    'Contient le TeeView

        Try
            'Vérifier si la touche Shift est enfoncée
            If e.Shift Then
                'Vérifier si le type d'objet est un TreeView
                If TypeOf sender Is TreeView Then
                    'Définir le TreeView
                    qTreeView = CType(sender, TreeView)
                    'Vérifier si un Node est sélectionné
                    If qTreeView.SelectedNode IsNot Nothing Then
                        'Vérifier si le Node est ouvert
                        If qTreeView.SelectedNode.IsExpanded Then
                            'Ouvrir tous les Nodes
                            qTreeView.SelectedNode.ExpandAll()
                        End If
                    End If
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qTreeView = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'un noeud doit être ouvert.
    ''' On n'ouvre pas le noeud s'il s'agit d'un double-click.
    '''</summary>
    ''' 
    Private Sub treRelations_BeforeExpand(ByVal sender As Object, ByVal e As System.Windows.Forms.TreeViewCancelEventArgs) Handles treRelations.BeforeExpand
        'Vérifier si c'est un Double-Click
        If m_Click = 2 Then
            'Annuler l'ouverture du Node
            e.Cancel = True
        End If
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'un noeud doit être fermé.
    ''' On ne ferme pas le noeud s'il s'agit d'un double-click.
    '''</summary>
    ''' 
    Private Sub treRelations_BeforeCollapse(ByVal sender As Object, ByVal e As System.Windows.Forms.TreeViewCancelEventArgs) Handles treRelations.BeforeCollapse
        'Vérifier si c'est un Double-Click
        If m_Click = 2 Then
            'Annuler l'ouverture du Node
            e.Cancel = True
        End If
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'un click de souris est effectué.
    ''' On conserve le nombre de clicks afin de savoir si c'est un double-click qui est effectué.
    '''</summary>
    ''' 
    Private Sub treRelations_MouseDown(ByVal sender As Object, ByVal e As System.Windows.Forms.MouseEventArgs) Handles treRelations.MouseDown
        'Conserver le nombre de click
        m_Click = e.Clicks
    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'un click de souris est effectué sur un Node du TreeView de relations.
    ''' Elle permet d'afficher la requête attributive dans le Rich Text Box du même menu.
    ''' Elle permet également d'afficher le nombre d'éléments sélectionnés dans le Label de message
    '''</summary>
    ''' 
    Private Sub treRelations_NodeMouseClick(ByVal sender As Object, ByVal e As System.Windows.Forms.TreeNodeMouseClickEventArgs) Handles treRelations.NodeMouseClick
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing                  'Interface pour connaitre le nom de la table
        Dim pTableDef As ITableDefinition = Nothing         'Interface qui permet d'extraire et définir la requête attributive
        Dim pTableSelection As ITableSelection = Nothing    'Interface pour indiquer le nombre d'éléments sélectionnés

        Try
            'Activer les boutons liés à un Node de sélectionné
            btnModifierRequete.Enabled = True
            btnRechercherRelation.Enabled = True

            'Afficher la requête vide
            rtxRequete.Text = ""

            'Sélectionner le Node du TreeVieew
            treRelations.SelectedNode = e.Node

            'Extraire la table par le text du node
            pTableDef = CType(m_MapLayer.ExtraireTableByName(e.Node.Text), ITableDefinition)

            'Vérifier si le StandaloneTable a été trouvé
            If pTableDef IsNot Nothing Then
                'Afficher la requête contenue dans le TableDefinition
                rtxRequete.Text = pTableDef.DefinitionExpression
                'Interface pour connaitre le nombre d'éléments sélectionnés
                pTableSelection = CType(pTableDef, ITableSelection)
                'Interface pour extraire le nom de la table
                pDataset = CType(pTableDef, IDataset)
                'Afficher le nombre d'éléments sélectionnés
                txtMessage.Text = pTableSelection.SelectionSet.Count.ToString & " élément(s) sélectionné(s) : " & pDataset.Name
            End If

            'Définir les attributs de la table
            DataGridAttributElement(CType(pTableDef, ITable), dgvListesAttributs)

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pTableDef = Nothing
            pTableSelection = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine appelé lorsqu'un double-click de souris est effectué sur un node du TreeView de relations.
    ''' Avec le double-clic gauche, elle permet d'ouvrir ou fermer tous les nodes sous celui sélectionné.
    ''' Avec le double-clic droit, elle permet d'ouvrir le menu des tables d'attributs correspondant au Noeud sélectionné.
    '''</summary>
    ''' 
    Private Sub treRelations_NodeMouseDoubleClick(ByVal sender As Object, ByVal e As System.Windows.Forms.TreeNodeMouseClickEventArgs) Handles treRelations.NodeMouseDoubleClick
        'Déclarer les variables de travail
        Dim pTableWindow2 As ITableWindow2 = Nothing    'Interface qui permet de verifier la présence du menu des tables d'attributs et de les manipuler
        Dim pExistTableWindow As ITableWindow = Nothing 'Interface contenant le menu de la table d'attributs existente
        Dim pTable As ITable = Nothing                  'Interface contenant la table à ouvrir dans le menu des tables d'attributs

        Try
            'Interface pour vérifier la présence du menu des tables d'attributs
            pTableWindow2 = CType(New TableWindow, ITableWindow2)
            'Extraire la table correspondant au noeud sélectionné
            pTable = m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text)

            'Vérifier si la table est valide
            If pTable IsNot Nothing Then
                'Vérifier si le type de table est un FeatureLayer
                If TypeOf pTable Is FeatureLayer Then
                    'Définir le menu de la table d'attribut de la table s'il est présent
                    pExistTableWindow = pTableWindow2.FindViaLayer(CType(pTable, ILayer))
                    'Vérifier si le menu de la table d'attribut est absent
                    If pExistTableWindow Is Nothing Then
                        'Définir le FeatureLayer à afficher
                        pTableWindow2.Layer = CType(pTable, ILayer)
                    End If

                    'Si le type de table est un StandaloneTable
                ElseIf TypeOf pTable Is StandaloneTable Then
                    'Extraire la table correspondant au noeud sélectionné
                    pExistTableWindow = pTableWindow2.FindViaStandaloneTable(CType(pTable, IStandaloneTable))
                    'Vérifier si le menu de la table d'attribut est absent
                    If pExistTableWindow Is Nothing Then
                        'Définir le StandaloneTable à afficher
                        pTableWindow2.StandaloneTable = CType(pTable, IStandaloneTable)
                    End If
                End If

                'Vérifier le menu de la table d'attribut est absent
                If pExistTableWindow Is Nothing Then
                    'Définir les paramètre d'affichage du menu des tables d'attributs
                    pTableWindow2.TableSelectionAction = esriTableSelectionActions.esriSelectFeatures
                    pTableWindow2.ShowSelected = False
                    pTableWindow2.ShowAliasNamesInColumnHeadings = True
                    pTableWindow2.Application = m_Application

                    'Si le menu de la table d'attribut est présent
                Else
                    'Redéfinir le menu des tables d'attributs pour celui existant
                    pTableWindow2 = CType(pExistTableWindow, ITableWindow2)
                End If

                'Afficher le menu des tables d'attributs s'il n'est pas affiché
                If Not pTableWindow2.IsVisible Then pTableWindow2.Show(True)
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTableWindow2 = Nothing
            pExistTableWindow = Nothing
            pTable = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de construire et transférer la requête attributive (DefinitionQuery) pour chaque liste d'attributs
    ''' dans la table sélectionnée.
    '''</summary>
    ''' 
    Private Sub btnTransfererListes_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTransfererListes.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing      'Interface qui permet de changer le curseur de la souris
        Dim pTable As ITable = Nothing                  'Interface contenant l'information de la table traitée
        Dim pTableDef As ITableDefinition = Nothing     'Interface contenant la requête attributive
        Dim pTableSel As ITableSelection = Nothing      'Interface utilisé pour traiter la sélection des éléments
        Dim i As Integer = 0                            'Compteur

        Try
            'Sortir si aucun noeud n'est sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Extraire la table par le text du node
            pTable = m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text)

            'Vérifier si la Table a été trouvée
            If pTable IsNot Nothing Then
                'Terminer l'édition des listes de valeurs
                dgvListesAttributs.EndEdit()

                'Interface ppour déselectionner les éléments
                pTableSel = CType(pTable, ITableSelection)

                'Désélectionner les éléments car très lent sinon
                pTableSel.Clear()

                'Interface ppour changer la requête
                pTableDef = CType(pTable, ITableDefinition)

                'Initialiser la requête attributive
                pTableDef.DefinitionExpression = ""

                'Traiter tous les attributs
                For i = 0 To dgvListesAttributs.Rows.Count - 2
                    'Vérifier la présence d'une liste de valeurs
                    If dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Length > 0 Then
                        'Vérifier la présence de la liste
                        If m_ListeValeur.Contains(dgvListesAttributs.Rows(i).Cells(0).Value.ToString) Then
                            'Détruire la liste valeur
                            m_ListeValeur.Remove(dgvListesAttributs.Rows(i).Cells(0).Value.ToString)
                        End If
                        'Conserver la liste des valeurs
                        m_ListeValeur.Add(dgvListesAttributs.Rows(i).Cells(1).Value.ToString, _
                                          dgvListesAttributs.Rows(i).Cells(0).Value.ToString)
                        'Vérifier si l'attribut est un String
                        If pTable.Fields.Field(i).Type = esriFieldType.esriFieldTypeString Then
                            'Vérifier la présence d'une requête
                            If pTableDef.DefinitionExpression.Length > 0 Then
                                'Définir la requête selon la liste des valeurs de type String
                                pTableDef.DefinitionExpression = pTableDef.DefinitionExpression & " AND " _
                                    & dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN ('" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Replace(",", "','") & "')"
                                'Si aucune requête présente
                            Else
                                'Définir la requête selon la liste des valeurs de type String
                                pTableDef.DefinitionExpression = dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN ('" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Replace(",", "','") & "')"
                            End If

                            'Si le type n'Est pas un String
                        Else
                            'Vérifier la présence d'une requête
                            If pTableDef.DefinitionExpression.Length > 0 Then
                                'Définir la requête selon la liste des valeurs
                                pTableDef.DefinitionExpression = pTableDef.DefinitionExpression & " AND " _
                                    & dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN (" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString & ")"
                                'Si aucune requête présente
                            Else
                                'Définir la requête selon la liste des valeurs
                                pTableDef.DefinitionExpression = dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN (" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString & ")"
                            End If
                        End If
                        'Si pas de liste de valeur
                    Else
                        'Vérifier la présence de la liste
                        If m_ListeValeur.Contains(dgvListesAttributs.Rows(i).Cells(0).Value.ToString) Then
                            'Détruire la liste valeur
                            m_ListeValeur.Remove(dgvListesAttributs.Rows(i).Cells(0).Value.ToString)
                        End If
                    End If
                Next

                'Vérifier la présence d'une requête
                If pTableDef.DefinitionExpression.Length > 0 Then
                    'Changer la couleur du texte pour rouge
                    'treRelations.SelectedNode.ForeColor = Color.Red
                    treRelations.SelectedNode.StateImageIndex = 0
                    'Si pas de liste de valeurs
                Else
                    'Changer la couleur du texte pour noir
                    'treRelations.SelectedNode.ForeColor = Color.Black
                    treRelations.SelectedNode.StateImageIndex = -1
                End If

                'Mettre à jour le text du menu
                rtxRequete.Text = pTableDef.DefinitionExpression
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTable = Nothing
            pTableDef = Nothing
            pTableSel = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de construire et transférer la requête attributive (DefinitionQuery) pour chaque liste d'attributs
    ''' dans toutes les tables en relation avec la table sélectionnée.
    '''</summary>
    ''' 
    Private Sub btnTransfererListesTables_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTransfererListesTables.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing      'Interface qui permet de changer le curseur de la souris
        Dim qNode As TreeNode = Nothing                 'Contient le noeud traité
        Dim pTable As ITable = Nothing                  'Interface contenant l'information de la table traitée
        Dim pTableDef As ITableDefinition = Nothing     'Interface contenant la requête attributive
        Dim qTableColl As New Collection                'Contient la collection de toutes les tables en relation 
        Dim nPos As Integer = 0                         'Contient la position de l'attribut
        Dim i As Integer = 0                            'Compteur
        Dim j As Integer = 0                            'Compteur

        Try
            'Sortir si aucun noeud n'est sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Terminer l'édition des listes de valeurs
            dgvListesAttributs.EndEdit()

            'Enlever toutes la sélection dans toutes les tables car très lent sinon 
            m_MxDocument.FocusMap.ClearSelection()

            'Extraire le dernier noeud parent
            qNode = treRelations.SelectedNode

            'Traiter tant qu'il y a un noeud parent
            Do Until qNode.Parent Is Nothing
                'Définir le noeud parent
                qNode = qNode.Parent
            Loop

            'Extraire toutes les tables en relation avec le Noeud de départ
            Call ExtraireTableNoeudEnfant(qTableColl, qNode)

            'Conserver les listes des valeurs en mémoire
            Call ConserverListesValeurs()

            'Traiter toutes les tables en relation
            For j = 1 To qTableColl.Count
                'Extraire la table en relation
                pTable = CType(qTableColl.Item(j), ITable)

                'Interface pour traiter la requête attributive
                pTableDef = CType(pTable, ITableDefinition)

                'Initialiser la requête attributive
                pTableDef.DefinitionExpression = ""

                'Traiter tous les attributs
                For i = 0 To dgvListesAttributs.Rows.Count - 2
                    'Vérifier la présence d'une liste de valeurs
                    If dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Length > 0 Then
                        'Extraire la position de l'attribut dans la table
                        nPos = pTable.FindField(dgvListesAttributs.Rows(i).Cells(0).Value.ToString)

                        'Vérifier si la table possède l'attribut
                        If nPos <> -1 Then
                            'Vérifier si l'attribut est un String
                            If pTable.Fields.Field(nPos).Type = esriFieldType.esriFieldTypeString Then
                                'Vérifier la présence d'une requête
                                If pTableDef.DefinitionExpression.Length > 0 Then
                                    'Définir la requête selon la liste des valeurs de type String
                                    pTableDef.DefinitionExpression = pTableDef.DefinitionExpression & " AND " _
                                        & dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                        & " IN ('" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Replace(",", "','") & "')"
                                    'Si aucune requête présente
                                Else
                                    'Définir la requête selon la liste des valeurs de type String
                                    pTableDef.DefinitionExpression = dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                        & " IN ('" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Replace(",", "','") & "')"
                                End If

                                'Si le type n'est pas un String
                            Else
                                'Vérifier la présence d'une requête
                                If pTableDef.DefinitionExpression.Length > 0 Then
                                    'Définir la requête selon la liste des valeurs
                                    pTableDef.DefinitionExpression = pTableDef.DefinitionExpression & " AND " _
                                        & dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                        & " IN (" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString & ")"
                                    'Si aucune requête présente
                                Else
                                    'Définir la requête selon la liste des valeurs
                                    pTableDef.DefinitionExpression = dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                        & " IN (" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString & ")"
                                End If
                            End If
                        End If
                    End If
                Next
            Next

            'Identifier toutes les relations pour toutes les tables de la Map active
            m_MenuRelations.IdentifierMap(m_MxDocument.FocusMap)

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qNode = Nothing
            pTable = Nothing
            pTableDef = Nothing
            qTableColl = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de vider les requêtes attributive de toutes les tables en relation avec celle sélectionnée.
    '''</summary>
    ''' 
    Private Sub btnTransfererListesVides_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnTransfererListesVides.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing      'Interface qui permet de changer le curseur de la souris
        Dim qNode As TreeNode = Nothing                 'Contient le noeud traité
        Dim pTable As ITable = Nothing                  'Interface contenant l'information de la table traitée
        Dim pTableDef As ITableDefinition = Nothing     'Interface contenant la requête attributive
        Dim qTableColl As New Collection                'Contient la collection de toutes les tables en relation 

        Try
            'Sortir si aucun noeud n'est sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Enlever toutes la sélection dans toutes les tables car très lent sinon 
            m_MxDocument.FocusMap.ClearSelection()

            'Terminer l'édition des listes de valeurs
            dgvListesAttributs.EndEdit()

            'Extraire le dernier noeud parent
            qNode = treRelations.SelectedNode

            'Traiter tant qu'il y a un noeud parent
            Do Until qNode.Parent Is Nothing
                'Définir le noeud parent
                qNode = qNode.Parent
            Loop

            'Extraire toutes les tables en relation avec le Noeud de départ
            Call ExtraireTableNoeudEnfant(qTableColl, qNode)

            'Traiter toutes les tables en relation
            For j = 1 To qTableColl.Count
                'Extraire la table en relation
                pTable = CType(qTableColl.Item(j), ITable)

                'Interface pour traiter la requête attributive
                pTableDef = CType(pTable, ITableDefinition)

                'Initialiser la requête attributive
                pTableDef.DefinitionExpression = ""
            Next

            'Identifier toutes les relations pour toutes les tables de la Map active
            m_MenuRelations.IdentifierMap(m_MxDocument.FocusMap)

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qNode = Nothing
            pTable = Nothing
            pTableDef = Nothing
            qTableColl = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'ajouter des valeurs d'attributs dans la liste conservé en mémoire.
    '''</summary>
    ''' 
    Private Sub btnAjouterListeAttributs_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnAjouterListeAttributs.Click
        Try
            'Conserver les listes des valeurs en mémoire
            Call ConserverListesValeurs()

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire la liste des valeurs d'attributs conservés en mémoire.
    '''</summary>
    ''' 
    Private Sub btnDetruireListeAttributs_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDetruireListeAttributs.Click
        'Déclarer les variables de travail
        Dim pTable As ITable = Nothing  'Interface contenant la table sélectionnée

        Try
            'Détruire la liste des valeurs d'attributs en mémoire
            m_ListeValeur.Clear()

            'Extraire la table par le text du node
            pTable = m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text)

            'Vérifier si la table est trouvée
            If pTable IsNot Nothing Then
                'Définir les attributs de la table
                DataGridAttributElement(pTable, dgvListesAttributs)
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    ' '''<summary>
    ' ''' Routine appelé lorsqu'un double-clic est effectué sur le Cell.
    ' ''' La requête de la liste des valeurs est ajoutée dans le Layer
    ' '''</summary>
    ' ''' 
    'Private Sub dgvListesAttributs_CellDoubleClick(ByVal sender As Object, ByVal e As System.Windows.Forms.DataGridViewCellEventArgs) Handles dgvListesAttributs.CellDoubleClick
    '    'Déclarer les variables de travail
    '    Dim pTable As ITable = Nothing
    '    Dim pTableDef As ITableDefinition = Nothing

    '    Try
    '        'Extraire la table par le text du node
    '        pTable = m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text)

    '        'Vérifier si la Table a été trouvée
    '        If pTable IsNot Nothing Then
    '            'Extraire la table par le text du node
    '            pTableDef = CType(pTable, ITableDefinition)
    '            'Vérifier la présence d'une liste de valeurs
    '            If dgvListesAttributs.Rows(e.RowIndex).Cells(1).Value.ToString.Length > 0 Then
    '                'Vérifier si l'attribut est un String
    '                If pTable.Fields.Field(e.RowIndex).Type = esriFieldType.esriFieldTypeString Then
    '                    'Vérifier la présence d'une requête
    '                    If pTableDef.DefinitionExpression.Length > 0 Then
    '                        'Définir la requête selon la liste des valeurs de type String
    '                        pTableDef.DefinitionExpression = pTableDef.DefinitionExpression & " AND " _
    '                            & dgvListesAttributs.Rows(e.RowIndex).Cells(0).Value.ToString _
    '                            & " IN ('" & dgvListesAttributs.Rows(e.RowIndex).Cells(1).Value.ToString.Replace(",", "',") & "')"
    '                        'Si aucune requête présente
    '                    Else
    '                        'Définir la requête selon la liste des valeurs de type String
    '                        pTableDef.DefinitionExpression = dgvListesAttributs.Rows(e.RowIndex).Cells(0).Value.ToString _
    '                            & " IN ('" & dgvListesAttributs.Rows(e.RowIndex).Cells(1).Value.ToString.Replace(",", "',") & "')"
    '                    End If

    '                    'Si le type n'Est pas un String
    '                Else
    '                    'Vérifier la présence d'une requête
    '                    If pTableDef.DefinitionExpression.Length > 0 Then
    '                        'Définir la requête selon la liste des valeurs
    '                        pTableDef.DefinitionExpression = pTableDef.DefinitionExpression & " AND " _
    '                            & dgvListesAttributs.Rows(e.RowIndex).Cells(0).Value.ToString _
    '                            & " IN (" & dgvListesAttributs.Rows(e.RowIndex).Cells(1).Value.ToString & ")"
    '                        'Si aucune requête présente
    '                    Else
    '                        'Définir la requête selon la liste des valeurs
    '                        pTableDef.DefinitionExpression = dgvListesAttributs.Rows(e.RowIndex).Cells(0).Value.ToString _
    '                            & " IN (" & dgvListesAttributs.Rows(e.RowIndex).Cells(1).Value.ToString & ")"
    '                    End If
    '                End If
    '            End If

    '            'Vérifier la présence d'une requête
    '            If pTableDef.DefinitionExpression.Length > 0 Then
    '                'Changer la couleur du texte pour rouge
    '                'treRelations.SelectedNode.ForeColor = Color.Red
    '                treRelations.SelectedNode.StateImageIndex = 0
    '                'Si pas de liste de valeurs
    '            Else
    '                'Changer la couleur du texte pour noir
    '                'treRelations.SelectedNode.ForeColor = Color.Black
    '                treRelations.SelectedNode.StateImageIndex = -1
    '            End If

    '            'Mettre à jour le text du menu
    '            rtxRequete.Text = pTableDef.DefinitionExpression
    '        End If

    '    Catch erreur As Exception
    '        'Message d'erreur
    '        MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
    '    Finally
    '        'Vider la mémoire
    '        pTable = Nothing
    '        pTableDef = Nothing
    '    End Try
    'End Sub

    '''<summary>
    ''' Routine qui permet de sélectionner tous les éléments de la table en fonction de son Definition Query.
    ''' Le nombre d'éléments sélectionnés est afficher dans le message texte.
    '''</summary>
    ''' 
    Private Sub btnSelectionnerRequete_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnSelectionnerRequete.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris
        Dim pDataset As IDataset = Nothing                  'Interface pour extraire le nom de la table
        Dim pTable As ITable = Nothing                      'Interface contenant l'information de la table de base à traiter
        Dim pTableSelection As ITableSelection = Nothing        'Interface qui permet de sélectionner des éléments d'un StandaloneTable
        Dim pFeatureSelection As IFeatureSelection = Nothing    'Interface qui permet de sélectionner des éléments d'un FeatureLayer

        Try
            'Vérifier si un Node est sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Extraire la table par le text du node
            pTable = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), ITable)

            'Vérifier si la table a été trouvé
            If pTable IsNot Nothing Then
                'Interface pour extraire le nom de la table
                pDataset = CType(pTable, IDataset)

                'Message de début de la recherche
                txtMessage.Text = "Recherche en cours : " & pDataset.Name
                txtMessage.Refresh()

                'Vérifier le type de table
                If TypeOf (pTable) Is IFeatureLayer Then
                    'Interface pour sélectionner les éléments
                    pFeatureSelection = CType(pTable, IFeatureSelection)
                    'Sélectionner les éléments selon la requête de la table
                    pFeatureSelection.SelectFeatures(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                    'Afficher le message
                    txtMessage.Text = pFeatureSelection.SelectionSet.Count.ToString & " Élément(s) trouvé(s) : " & pDataset.Name
                    txtMessage.Refresh()
                Else
                    'Interface pour sélectionner les éléments
                    pTableSelection = CType(pTable, ITableSelection)
                    'Sélectionner les éléments selon la requête de la table
                    pTableSelection.SelectRows(Nothing, esriSelectionResultEnum.esriSelectionResultNew, False)
                    'Afficher le message
                    txtMessage.Text = pTableSelection.SelectionSet.Count.ToString & " Élément(s) trouvé(s) : " & pDataset.Name
                    txtMessage.Refresh()
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pTable = Nothing
            pTableSelection = Nothing
            pFeatureSelection = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de modifier la requête attributive (DefinitionQuery) contenu dans un FeatureLayer ou un StandaloneTable.
    ''' Un menu pour construire la requête est affiché.
    '''</summary>
    ''' 
    Private Sub btnModifierRequete_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnModifierRequete.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris
        Dim pTableDef As ITableDefinition = Nothing         'Interface qui permet d'extraire et définir la requête attributive
        Dim pTableSel As ITableSelection = Nothing          'Interface qui permet de traiter la sélection
        Dim pQueryPropPage As IQueryPropertyPage = Nothing  'Interface qui permet de modifier la requête via la page de propriété d'une table
        Dim pComPropPage As IComPropertyPage = Nothing      'Interface qui permet de définir le type de fenêtre de dialogue à afficher via la page de propriété
        Dim pComPropSheet As IComPropertySheet = Nothing    'Interface qui permet d'afficher la fenêtre du DefinitionQuery via une feuille de propriété
        Dim pSet As ISet = Nothing                          'Interface qui permet de contenir des objets

        Try
            'Vérifier si un Node est sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Extraire la table par le text du node
            pTableDef = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), ITableDefinition)

            'Vérifier si le StandaloneTable a été trouvé
            If pTableDef IsNot Nothing Then
                'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
                pMouseCursor = New MouseCursorClass
                pMouseCursor.SetCursor(2)

                'Message de modification de la requête
                txtMessage.Text = "Modifier la requête : " & rtxRequete.Text
                txtMessage.Refresh()

                'Interface pour déselectionner les éléments
                pTableSel = CType(pTableDef, ITableSelection)

                'Désélectionner les éléments car très lent sinon
                pTableSel.Clear()

                'Afficher la requête de la table
                rtxRequete.Text = pTableDef.DefinitionExpression

                'Objets ESRI pour afficher la fenêtre du Definition query.
                'Ces objets ainsi que la façon dont on doit appeler la fenêtre proviennent 
                'directement du support ESRI. J'avoue que c'est un peu incompréhensible mais
                'ça marche, c'est l'important.

                'Créer un nouvel ensemble d'objet vide
                pSet = New ESRI.ArcGIS.esriSystem.Set
                'Creer une page de propriété afin de définir le type de boite de dialogue à afficher
                pComPropPage = CType(New QueryPropertyPage, IComPropertyPage)
                'Créer une feuille de propriété afin de pouvoir afficher la boite de dialogue
                pComPropSheet = New ComPropertySheet

                'Associer la page de propriété à la page pour modifier le DefinitionQuery d'une table
                pQueryPropPage = CType(pComPropPage, IQueryPropertyPage)
                'Définir la table contenant le DefinitionQuery
                pQueryPropPage.Table = CType(pTableDef, ITable)
                'Définir la requête de la table
                pQueryPropPage.Expression = pTableDef.DefinitionExpression

                'Définir le titre de la page
                pComPropPage.Title = "Definition Query"
                'Définir le titre de la feuille
                pComPropSheet.Title = treRelations.SelectedNode.Text

                'Ajouter un nouvel identifiant de catégorie
                pComPropSheet.AddCategoryID(New UID)
                'Ajouter la page de propriété à la feuille de propriété
                pComPropSheet.AddPage(pComPropPage)
                'Afficher la fenêtre pour modifier le DefinitionQuery
                pComPropSheet.EditProperties(pSet, 0)

                'Définir la requête retournée dans la table
                rtxRequete.Text = pQueryPropPage.QueryFilter.WhereClause

                'Modifier la requête dans la table
                pTableDef.DefinitionExpression = pQueryPropPage.QueryFilter.WhereClause

                'Vérifier la présence de la requête attributive
                If pTableDef.DefinitionExpression.Length > 0 Then
                    'Changer la couleur du texte pour rouge
                    'treRelations.SelectedNode.ForeColor = Color.Red
                    treRelations.SelectedNode.StateImageIndex = 0
                    'Si pas de requête attributive
                Else
                    'Changer la couleur du texte pour noir
                    'treRelations.SelectedNode.ForeColor = Color.Black
                    treRelations.SelectedNode.StateImageIndex = -1
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTableDef = Nothing
            pTableSel = Nothing
            pQueryPropPage = Nothing
            pComPropPage = Nothing
            pComPropSheet = Nothing
            pSet = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire la requête attributive de la table sélectionnée.
    '''</summary>
    ''' 
    Private Sub btnDetruireRequete_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnDetruireRequete.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris
        Dim pTableDef As ITableDefinition = Nothing         'Interface qui permet d'extraire et définir la requête attributive
        Dim pTableSel As ITableSelection = Nothing          'Interface qui permet de traiter la sélection

        Try
            'Vérifier si un Node est sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Extraire la table par le text du node
            pTableDef = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), ITableDefinition)

            'Vérifier si le StandaloneTable a été trouvé
            If pTableDef IsNot Nothing Then
                'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
                pMouseCursor = New MouseCursorClass
                pMouseCursor.SetCursor(2)

                'Message de destruction de la requête
                txtMessage.Text = "Détruire la requête : " & pTableDef.DefinitionExpression
                txtMessage.Refresh()

                'Interface pour déselectionner les éléments
                pTableSel = CType(pTableDef, ITableSelection)

                'Désélectionner les éléments car très lent sinon
                pTableSel.Clear()

                'Afficher la requête vide
                rtxRequete.Text = ""

                'Détruire la requête dans la table
                pTableDef.DefinitionExpression = ""

                'Changer la couleur du texte pour noir
                treRelations.SelectedNode.ForeColor = Color.Black
                treRelations.SelectedNode.StateImageIndex = -1

            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTableDef = Nothing
            pTableSel = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine appelé lorsque le focus n'est plus sur le RichTextBox contenant la requête.
    ''' Elle permet de mettre la nouvelle requête modifiée dans la table sélectionnée.
    '''</summary>
    ''' 
    Private Sub rtxRequete_LostFocus(ByVal sender As Object, ByVal e As System.EventArgs) Handles rtxRequete.LostFocus
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris
        Dim pTableDef As ITableDefinition = Nothing 'Interface qui permet d'extraire et définir la requête attributive
        Dim pTableSel As ITableSelection = Nothing          'Interface qui permet de traiter la sélection

        Try
            'Vérifier si un Node est sélectionné
            If treRelations.SelectedNode Is Nothing Then Exit Sub

            'Extraire la table par le text du node
            pTableDef = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), ITableDefinition)

            'Vérifier si le StandaloneTable a été trouvé
            If pTableDef IsNot Nothing Then
                'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
                pMouseCursor = New MouseCursorClass
                pMouseCursor.SetCursor(2)

                'Message de Modification la requête
                txtMessage.Text = "Modifier la requête : " & rtxRequete.Text
                txtMessage.Refresh()

                'Interface pour déselectionner les éléments
                pTableSel = CType(pTableDef, ITableSelection)

                'Désélectionner les éléments car très lent sinon
                pTableSel.Clear()

                'Afficher la requête de la table
                pTableDef.DefinitionExpression = rtxRequete.Text

                'Vérifier la présence de la requête attributive
                If pTableDef.DefinitionExpression.Length > 0 Then
                    'Changer la couleur du texte pour rouge
                    'treRelations.SelectedNode.ForeColor = Color.Red
                    treRelations.SelectedNode.StateImageIndex = 0
                    'Si pas de requête attributive
                Else
                    'Changer la couleur du texte pour noir
                    'treRelations.SelectedNode.ForeColor = Color.Black
                    treRelations.SelectedNode.StateImageIndex = -1
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pTableDef = Nothing
            pTableSel = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de rechercher tous les éléments en relation liés à tous les éléments de la table traitée.
    ''' Le traitement est récursif entre les éléments en relation trouvés et ses éléments en relation.
    ''' Le traitement arrête lorsque les éléments en relation trouvés n'ont plus de relation.
    '''</summary>
    ''' 
    Private Sub btnRechercherRelation_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnRechercherRelation.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing                  'Interface qui permet de changer le curseur de la souris.
        Dim pDataset As IDataset = Nothing                          'Interface pour extraire le nom de la table.
        Dim pTable As ITable = Nothing                              'Interface contenant l'information de la table de base à traiter.
        Dim pTableRel As ITable = Nothing                           'Interface contenant l'information de la table en relation à traiter.
        Dim pTableSelection As ITableSelection = Nothing            'Interface qui permet de sélectionner des éléments.
        Dim pFeatureSelection As IFeatureSelection = Nothing        'Interface qui permet de sélectionner des éléments.
        Dim pRelClassColl As IRelationshipClassCollection = Nothing 'Interface contenant les relations d'une table.
        Dim pSelectionSet As ISelectionSet = Nothing                'Interface contenant les éléments sélectionnés.

        Try
            'Vérifier si un Node est sélectionné
            If treRelations.SelectedNode Is Nothing Then
                'désactiver les boutons liés à un Node de sélectionné
                btnModifierRequete.Enabled = False
                btnRechercherRelation.Enabled = False
                'Sortir
                Exit Sub
            End If

            'Extraire la table par le text du node
            pTable = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), ITable)

            'Vérifier si la table a été trouvé
            If pTable IsNot Nothing Then
                'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
                pMouseCursor = New MouseCursorClass
                pMouseCursor.SetCursor(2)

                'Interface pour extraire le nom de la table
                pDataset = CType(pTable, IDataset)

                'Message de début de la recherche
                txtMessage.Text = "Recherche en cours : " & pDataset.Name
                txtMessage.Refresh()

                'Conserver les listes des valeurs en mémoire
                Call ConserverListesValeurs()

                'Initialiser l'interface d'annlation du traitement en progression
                m_TrackCancel = New CancelTracker
                m_TrackCancel.CancelOnKeyPress = True
                m_TrackCancel.CancelOnClick = False

                'Vérifier si la table est un IFeatureSelection
                If TypeOf pTable Is IFeatureSelection Then
                    'Interface pour sélectionner les éléments
                    pFeatureSelection = CType(pTable, IFeatureSelection)
                    'Vérifier si aucune sélection déjà effectuée
                    If pFeatureSelection.SelectionSet.Count = 0 Then
                        'Sélectionner les éléments selon la requête de la table
                        pFeatureSelection.SelectFeatures(ConstruireRequeteAttributive(pTable), esriSelectionResultEnum.esriSelectionResultNew, False)
                    End If
                    'Définir l'interface contenant les éléments sélectionnés
                    pSelectionSet = pFeatureSelection.SelectionSet
                Else
                    'Interface pour sélectionner les éléments
                    pTableSelection = CType(pTable, ITableSelection)
                    'Vérifier si aucune sélection déjà effectuée
                    If pTableSelection.SelectionSet.Count = 0 Then
                        'Sélectionner les éléments selon la requête de la table
                        pTableSelection.SelectRows(ConstruireRequeteAttributive(pTable), esriSelectionResultEnum.esriSelectionResultNew, False)
                    End If
                    'Définir l'interface contenant les éléments sélectionnés
                    pSelectionSet = pTableSelection.SelectionSet
                End If

                'Afficher le message
                txtMessage.Text = pSelectionSet.Count.ToString & " Élément(s) trouvé(s) : " & pDataset.Name
                txtMessage.Refresh()

                'Initialiser le menu d'identification
                m_MenuIdentification.Initialiser()

                'Rechercher les éléments en relation
                Call RechercherElementsEnRelationParNode(pTable, treRelations.SelectedNode.Parent)
            End If

        Catch erreur As Exception
            'Message d'erreur
            m_TrackCancel = Nothing
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            m_TrackCancel = Nothing
            pMouseCursor = Nothing
            pDataset = Nothing
            pTable = Nothing
            pTableRel = Nothing
            pTableSelection = Nothing
            pRelClassColl = Nothing
            pSelectionSet = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de construire une liste des valeurs d'attributs présentes dans la table.
    '''</summary>
    ''' 
    Private Sub dgvListesAttributs_DoubleClick(ByVal sender As Object, ByVal e As System.EventArgs) Handles dgvListesAttributs.DoubleClick
        'Déclarer les variables de ravail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pTable As ITable = Nothing              'Interface contenant la table sélectionnée.
        Dim pDataStats As New DataStatistics        'Interface pour créer des statistiques
        Dim pEnumVar As IEnumerator = Nothing       'Interface pour extraire les valeurs uniques.
        Dim pValue As Object = Nothing              'Contient une valeur unique
        Dim sListeValeur As String = ""             'Liste des valeurs d'attributs trouvées.

        Try
            'Extraire la table par le text du node
            pTable = CType(m_MapLayer.ExtraireTableByName(treRelations.SelectedNode.Text), ITable)

            'Vérifier si la table a été trouvé
            If pTable IsNot Nothing Then
                'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
                pMouseCursor = New MouseCursorClass
                pMouseCursor.SetCursor(2)

                'Vérifier si seulement une colonne est sélectionnée
                If dgvListesAttributs.SelectedCells.Count > 0 Then
                    'Définir le maximum d'éléments à vérifier
                    pDataStats.SampleRate = 2000

                    'Extraire le nom de l'attribut
                    pDataStats.Field = dgvListesAttributs.Item(0, dgvListesAttributs.CurrentRow.Index).Value.ToString

                    'Définir le curseur de recherche
                    pDataStats.Cursor = pTable.Search(Nothing, False)

                    'Interface pour extraire les valeurs uniques
                    pEnumVar = pDataStats.UniqueValues

                    'Initialiser l'extraction
                    pEnumVar.Reset()

                    'Traiter tous les éléments
                    Do While pEnumVar.MoveNext
                        'Définir la valeur
                        pValue = pEnumVar.Current
                        'Construire la liste
                        sListeValeur = sListeValeur & pValue.ToString & ","
                        'Vérifier la longueur
                        If sListeValeur.Length > m_MaxItems Then Exit Do
                    Loop

                    'Enlever la virgule à la fin
                    If sListeValeur.Length > 0 Then sListeValeur = sListeValeur.Substring(0, sListeValeur.Length - 1)

                    'Définir la liste des valeurs
                    dgvListesAttributs.Item(1, dgvListesAttributs.CurrentRow.Index).Value = sListeValeur
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pTable = Nothing
            pDataStats = Nothing
            pEnumVar = Nothing
            pValue = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions privées"
    '''<summary>
    ''' Routine qui permet de remplir la collection des tables en relation à partir d'un noeud de départ.
    '''</summary>
    '''
    '''<param name="qTableColl">Collection contenant toutes les tables en relation.</param>
    '''<param name="qNode">Objet contenant le nom de la Table de départ et des noeuds enfants.</param>
    ''' 
    ''' <remarks>
    ''' Si le node est invalide, rien n'est effectué.
    '''</remarks>
    ''' 
    Private Sub ExtraireTableNoeudEnfant(ByRef qTableColl As Collection, ByVal qNode As TreeNode)
        'Déclarer les variables de travail
        Dim pTable As ITable = Nothing                  'Interface contenant l'information de la table traitée
        Dim i As Integer = 0                            'Compteur

        Try
            'Sortir si aucun noeud n'est sélectionné
            If qNode Is Nothing Then Exit Sub

            'Traiter tous les nodes enfants
            For i = 0 To qNode.Nodes.Count - 1
                'Extraire la table par le text du node traité
                pTable = m_MapLayer.ExtraireTableByName(qNode.Nodes.Item(i).Text)

                'Vérifier si la table est valide
                If pTable IsNot Nothing Then
                    'vérifier si la table est déjà entrée dans la collection
                    If qTableColl.Contains(qNode.Nodes.Item(i).Text) = False Then
                        'Ajouter la table dans la collection
                        qTableColl.Add(pTable, qNode.Nodes.Item(i).Text)
                    End If
                End If

                'Extraire toutes les tables du Noeud en relation
                Call ExtraireTableNoeudEnfant(qTableColl, qNode.Nodes.Item(i))
            Next

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pTable = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de rechercher tous les éléments en relation liés à tous les éléments de la table traitée.
    ''' Le traitement est récursif entre les éléments en relation trouvés et ses éléments en relation.
    ''' Le traitement arrête lorsque les éléments en relation trouvés n'ont plus de relation.
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant la table de base.</param>
    '''<param name="qNode">Interface contenant le nom de la Table en relation.</param>
    ''' 
    ''' <remarks>
    ''' Si le node est invalide, c'est qu'il n'y a plus de table en relation. Le traitement récursif est alors arrêté.
    '''</remarks>
    ''' 
    Private Sub RechercherElementsEnRelationParNode(ByRef pTable As ITable, ByRef qNode As TreeNode)
        'Déclarer les variables de travail
        Dim pDataset As IDataset = Nothing              'Interface pour extraire le nom de la table
        Dim pTableRel As ITable = Nothing               'Interface contenant l'information de la table en relation à traiter
        Dim pTableSel As ITableSelection = Nothing      'Interface contenant l'information des éléments sélectionnés
        Dim pFeatureLayer As IFeatureLayer = Nothing    'Interface qui contient le Layer de sélection

        Try
            'Sortir si annuler
            If m_TrackCancel.Continue = False Then
                'Message d'annulation du traitement
                txtMessage.Text = "Annulation du traitement"
                txtMessage.Refresh()
                Throw New System.Exception("Annulation du traitement")
            End If

            'Vérifier l'absence du Node parent
            If qNode Is Nothing Then
                'Vérifier si le type de table est un StandaloneTable
                If TypeOf (pTable) Is StandaloneTable Then
                    'Remplir le menu d'identification
                    m_MenuIdentification.IdentifierTable2(CType(pTable, IStandaloneTable), True)
                    'Afficher le menu d'identification
                    m_MenuIdentification.Show(True)

                    'Si le type de table est un FeatureLayer
                ElseIf TypeOf pTable Is FeatureLayer Then
                    'Interface pour extraire le nom de la table
                    pFeatureLayer = CType(pTable, IFeatureLayer)
                    'Rendre le FeatureLayer visible
                    pFeatureLayer.Visible = True

                    'Vérifier si on doit créer un Layer de sélection
                    If m_CreerLayer Then
                        'Créer le Layer de sélection
                        pFeatureLayer = CreerLayerSelection(pFeatureLayer, pFeatureLayer.Name & "_" & CStr(m_Compteur))

                        'Compter le nombre de résultat
                        m_Compteur = m_Compteur + 1

                        'Ajouter le Node du FeatureLayer
                        qNode = treRelations.Nodes.Add(pFeatureLayer.Name, pFeatureLayer.Name)
                        qNode.Tag = pFeatureLayer.FeatureClass.AliasName

                        'Identifier toutes les relations du FeatureLayer de sélection du Node traité
                        Call IdentifierRelations(CType(pFeatureLayer, IRelationshipClassCollection), qNode, New Collection)
                    End If

                    'Remplir le menu d'identification
                    m_MenuIdentification.IdentifierFeatureLayer(pFeatureLayer, True)
                    'Afficher le menu d'identification
                    m_MenuIdentification.Show(True)

                    'Effectuer un Zoom selon les éléments sélectionnés
                    ZoomToFeatureSelection(CType(pFeatureLayer, IFeatureSelection))
                End If

                'Si le node parent est présent
            Else
                'Extraire la table par le text du node
                pTableRel = CType(m_MapLayer.ExtraireTableByName(qNode.Text), ITable)

                'Vérifier si la table a été trouvé
                If pTableRel IsNot Nothing Then
                    'Interface pour extraire le nom de la table
                    pDataset = CType(pTableRel, IDataset)

                    'Message de début de la recherche
                    txtMessage.Text = "Recherche en cours : " & pDataset.Name
                    txtMessage.Refresh()

                    'Vérifier si le type de table est un FeatureLayer
                    If TypeOf (pTableRel) Is IFeatureLayer Then
                        'Sélectionner les éléments en relation
                        RechercherFeatureEnRelation(pTable, CType(pTableRel, IFeatureLayer))

                        'Si le type de table est un StandaloneTable
                    Else
                        'Sélectionner les éléments en relation
                        RechercherRowEnRelation(pTable, CType(pTableRel, IStandaloneTable))
                    End If

                    'Interface pour vérifier la présence des éléments sélectionnés
                    pTableSel = CType(pTableRel, ITableSelection)

                    'Afficher le message
                    txtMessage.Text = pTableSel.SelectionSet.Count.ToString & " Élément(s) trouvé(s) : " & pDataset.Name
                    txtMessage.Refresh()

                    'Rechercher les éléments en relation des éléments en relation trouvés de façon récursive
                    Call RechercherElementsEnRelationParNode(pTableRel, qNode.Parent)
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pDataset = Nothing
            pTableRel = Nothing
            pTableSel = Nothing
            pFeatureLayer = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction permet de sélectionner les éléments d'un FeatureLayer en fonction des éléments sélectionnés contenus dans une table de base.
    ''' Les éléments trouvés sont sélectionnés dans la table en relation.
    ''' Un relation doit obligatoirement être présente entre deux tables. 
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant la table de base.</param>
    '''<param name="pTableRel">Interface contenant les éléments à sélectionner dans le FeatureLayer en relation.</param>
    ''' 
    ''' <remarks>
    ''' Si aucun élément n'est sélectionné dans la table de base, rien n'est effectué.
    '''</remarks>
    Private Sub RechercherFeatureEnRelation(ByRef pTable As ITable, ByRef pTableRel As IFeatureLayer)
        'Déclarer les variables de travail
        Dim pTableSelection As ITableSelection = Nothing            'Interface qui permet de traiter la sélection de la table de base
        Dim pFeatureSelection As IFeatureSelection = Nothing        'Interface qui permet de traiter la sélection de la table en relation
        Dim pRelClassColl As IRelationshipClassCollection = Nothing 'Interface contenant les classes en relation avec le FeatureLayer traité
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing       'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing               'Interface contenant la classe en relation et ses paramètres
        Dim qValeurColl As Collection = Nothing                     'Contient la collection des valeurs à rechercher
        Dim pQueryFilter As IQueryFilter = Nothing                  'Contient la requête pour sélectionner les éléments liés
        Dim pDataset As IDataset = Nothing                          'Interface contenant le nom de la table
        Dim pRow As IRow = Nothing                                  'Interface contenant l'élément utilisé pour trouver l'élément en relation
        Dim pEnumIds As IEnumIDs = Nothing                          'Interface qui permet d'extraire les Ids sélectionnés
        Dim nId As Integer = Nothing                                'Id d'un élément sélectionné
        Dim nPos As Integer = Nothing                               'Contient la position de l'attribut
        Dim sValeur As String = Nothing                             'Contient la valeur du lien à rechercher
        Dim i As Integer = 0            'Compteur

        Try
            'Interface pour sélectionner les éléments liés
            pTableSelection = CType(pTable, ITableSelection)
            'Vérifier la présence d'éléments sélectionnés
            If pTableSelection.SelectionSet.Count > 0 Then
                'Interface pour extraire le nom de la table
                pDataset = CType(pTable, IDataset)
                'Interface pour sélectionner les éléments liés
                pFeatureSelection = CType(pTableRel, IFeatureSelection)
                'Interface contenant la collection des Relate de la classe de découpage
                pRelClassColl = CType(pTableRel, IRelationshipClassCollection)
                'Interface pour énumérer les relates de la classe de découpage
                pEnumRelClass = pRelClassColl.RelationshipClasses
                'Initialiser la recherche des Relate de la classe de découpage
                pEnumRelClass.Reset()
                'Trouver la première classe en relation
                pRelClass = pEnumRelClass.Next

                'Traiter tous les classe en relation
                Do Until pRelClass Is Nothing
                    'Vérifier si la table en relation correspond avec la bonne table
                    If pDataset.BrowseName = pRelClass.ForwardPathLabel Then
                        'Sortir de la boucle
                        Exit Do
                    End If
                    'Trouver la prochaine classe en relation 
                    pRelClass = pEnumRelClass.Next
                Loop

                'Vérifier si la relation a été trouvé
                If pRelClass IsNot Nothing Then
                    'Initialiser la sélection
                    pFeatureSelection.Clear()
                    'Initialiser le QueryFilter
                    pQueryFilter = New QueryFilter
                    'Initialiser la collection des valeurs à rechercher
                    qValeurColl = New Collection
                    'Extraire la position de l'attribut du lien à rechercher
                    nPos = pTable.Fields.FindField(pRelClass.OriginForeignKey)

                    'Définir le curseur d'extraction des éléments
                    pEnumIds = pTableSelection.SelectionSet.IDs
                    'Extraire le premier Id
                    nId = pEnumIds.Next

                    'Traiter tous les éléments liés
                    Do Until nId = -1
                        'Sortir si annuler
                        If m_TrackCancel.Continue = False Then
                            'Message d'annulation du traitement
                            txtMessage.Text = "Annulation du traitement"
                            txtMessage.Refresh()
                            Throw New System.Exception("Annulation du traitement")
                        End If

                        'Extraire l'élément
                        pRow = pTable.GetRow(nId)

                        'Extraire la valeur du lien à rechercher
                        sValeur = CStr(pRow.Value(nPos))
                        'Vérifier si la valeur à rechercher n'a jamais été traitée
                        If Not qValeurColl.Contains(sValeur) Then
                            'Ajouter la valeur à rechercher dans la collection des valeurs
                            qValeurColl.Add(sValeur, sValeur)

                            'Ajouter la valeur trouvée dans la requête
                            pQueryFilter.WhereClause = pQueryFilter.WhereClause & "'" & sValeur & "',"

                            'Vérifier si la limite est dépassée
                            If pQueryFilter.WhereClause.Length > m_MaxItems Then
                                'Enlever la dernière ,
                                pQueryFilter.WhereClause = pQueryFilter.WhereClause.Substring(0, pQueryFilter.WhereClause.Length - 1)
                                'Vérifier si le type d'attribut n'est pas un String
                                If pTable.Fields.Field(nPos).Type <> esriFieldType.esriFieldTypeString Then
                                    'Enlever les ' car ce n'est pas un String
                                    pQueryFilter.WhereClause = pQueryFilter.WhereClause.Replace("'", "")
                                End If
                                'Compléter la requête attributive
                                pQueryFilter.WhereClause = pRelClass.OriginPrimaryKey & " IN (" & pQueryFilter.WhereClause & ")"
                                'Ajouter les éléments liés à l'élément en relation
                                pFeatureSelection.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAdd, False)
                                'Initialiser la requête attributive
                                pQueryFilter.WhereClause = ""
                            End If
                        End If
                        'Afficher l'état de la progression
                        i = i + 1
                        If (i Mod 10) = 0 Then txtMessage.Text = i.ToString & "/" & pTableSelection.SelectionSet.Count.ToString

                        'Extraire le prochain Id
                        nId = pEnumIds.Next
                    Loop

                    'Vérifier si la limite est dépassée
                    If pQueryFilter.WhereClause.Length > 0 Then
                        'Enlever la dernière ,
                        pQueryFilter.WhereClause = pQueryFilter.WhereClause.Substring(0, pQueryFilter.WhereClause.Length - 1)
                        'Vérifier si le type d'attribut n'est pas un String
                        If pTable.Fields.Field(nPos).Type <> esriFieldType.esriFieldTypeString Then
                            'Enlever les ' car ce n'est pas un String
                            pQueryFilter.WhereClause = pQueryFilter.WhereClause.Replace("'", "")
                        End If
                        'Compléter la requête attributive
                        pQueryFilter.WhereClause = pRelClass.OriginPrimaryKey & " IN (" & pQueryFilter.WhereClause & ")"
                        'Ajouter les éléments liés à l'élément en relation
                        pFeatureSelection.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAdd, False)
                    End If
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pTableSelection = Nothing
            pFeatureSelection = Nothing
            pRelClassColl = Nothing
            pEnumRelClass = Nothing
            pRelClass = Nothing
            pQueryFilter = Nothing
            qValeurColl = Nothing
            pDataset = Nothing
            pRow = Nothing
            pEnumIds = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction permet de sélectionner les éléments d'un StandaloneTable en fonction des éléments contenus dans une table de base.
    ''' Les éléments trouvés sont sélectionnés dans la table en relation.
    ''' Un relation doit obligatoirement être présente entre deux tables. 
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant la table de base.</param>
    '''<param name="pTableRel">Interface contenant les éléments à sélectionner dans la Table en relation.</param>
    ''' 
    ''' <remarks>
    ''' Si aucun élément n'est sélectionné dans la table de base, rien n'est effectué.
    '''</remarks>
    Private Sub RechercherRowEnRelation(ByRef pTable As ITable, ByRef pTableRel As IStandaloneTable)
        'Déclarer les variables de travail
        Dim pTableSelection As ITableSelection = Nothing            'Interface qui permet de traiter la sélection de la table de base
        Dim pTableRelSelection As ITableSelection = Nothing         'Interface qui permet de traiter la sélection de la table en relation
        Dim pRelClassColl As IRelationshipClassCollection = Nothing 'Interface contenant les classes en relation avec le FeatureLayer traité
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing       'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing               'Interface contenant la classe en relation et ses paramètres
        Dim pQueryFilter As IQueryFilter = Nothing                  'Contient la requête pour sélectionner les éléments liés
        Dim qValeurColl As Collection = Nothing                     'Contient la collection des valeurs à rechercher
        Dim pDataset As IDataset = Nothing                          'Interface contenant le nom de la table
        Dim pRow As IRow = Nothing                                  'Interface contenant l'élément utilisé pour trouver l'élément en relation
        Dim pEnumIds As IEnumIDs = Nothing                          'Interface qui permet d'extraire les Ids sélectionnés
        Dim nId As Integer = Nothing                                'Id d'un élément sélectionné
        Dim nPos As Integer = Nothing                               'Contient la position de l'attribut
        Dim sValeur As String = Nothing                             'Contient la valeur du lien à rechercher
        Dim i As Integer = 0            'Compteur

        Try
            'Interface pour sélectionner les éléments liés
            pTableSelection = CType(pTable, ITableSelection)
            'Vérifier la présence d'éléments sélectionnés
            If pTableSelection.SelectionSet.Count > 0 Then
                'Interface pour extraire le nom de la table
                pDataset = CType(pTable, IDataset)
                'Interface pour sélectionner les éléments liés
                pTableRelSelection = CType(pTableRel, ITableSelection)
                'Interface contenant la collection des Relate de la classe de découpage
                pRelClassColl = CType(pTableRel, IRelationshipClassCollection)
                'Interface pour énumérer les relates de la classe de découpage
                pEnumRelClass = pRelClassColl.RelationshipClasses
                'Initialiser la recherche des Relate de la classe de découpage
                pEnumRelClass.Reset()
                'Trouver la première classe en relation
                pRelClass = pEnumRelClass.Next

                'Traiter tous les classe en relation
                Do Until pRelClass Is Nothing
                    'Vérifier si la table en relation correspond avec la bonne table
                    If pDataset.BrowseName = pRelClass.ForwardPathLabel Then
                        'Sortir de la boucle
                        Exit Do
                    End If
                    'Trouver la prochaine classe en relation 
                    pRelClass = pEnumRelClass.Next
                Loop

                'Vérifier si la relation a été trouvé
                If pRelClass IsNot Nothing Then
                    'Initialiser la sélection
                    pTableRelSelection.Clear()
                    'Initialiser le QueryFilter
                    pQueryFilter = New QueryFilter
                    'Initialiser la collection des valeurs à rechercher
                    qValeurColl = New Collection
                    'Extraire la position de l'attribut du lien à rechercher
                    nPos = pTable.Fields.FindField(pRelClass.OriginForeignKey)

                    'Définir le curseur d'extraction des éléments
                    pEnumIds = pTableSelection.SelectionSet.IDs
                    'Extraire le premier Id
                    nId = pEnumIds.Next

                    'Traiter tous les éléments liés
                    Do Until nId = -1
                        'Sortir si annuler
                        If m_TrackCancel.Continue = False Then
                            'Message d'annulation du traitement
                            txtMessage.Text = "Annulation du traitement"
                            txtMessage.Refresh()
                            Throw New System.Exception("Annulation du traitement")
                        End If

                        'Extraire l'élément
                        pRow = pTable.GetRow(nId)

                        'Extraire la valeur du lien à rechercher
                        sValeur = CStr(pRow.Value(nPos))
                        'Vérifier si la valeur à rechercher n'a jamais été traitée
                        If Not qValeurColl.Contains(sValeur) Then
                            'Ajouter la valeur à rechercher dans la collection des valeurs
                            qValeurColl.Add(sValeur, sValeur)

                            'Ajouter la valeur trouvée dans la requête
                            pQueryFilter.WhereClause = pQueryFilter.WhereClause & "'" & sValeur & "',"

                            'Vérifier si la limite est dépassée
                            If pQueryFilter.WhereClause.Length > m_MaxItems Then
                                'Enlever la dernière '
                                pQueryFilter.WhereClause = pQueryFilter.WhereClause.Substring(0, pQueryFilter.WhereClause.Length - 1)
                                'Vérifier si le type d'attribut n'est pas un String
                                If pTable.Fields.Field(nPos).Type <> esriFieldType.esriFieldTypeString Then
                                    'Enlever les ' car ce n'est pas un String
                                    pQueryFilter.WhereClause = pQueryFilter.WhereClause.Replace("'", "")
                                End If
                                'Compléter la requête attributive
                                pQueryFilter.WhereClause = pRelClass.OriginPrimaryKey & " IN (" & pQueryFilter.WhereClause & ")"
                                'Ajouter les éléments liés à l'élément en relation
                                pTableRelSelection.SelectRows(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAdd, False)
                                'Initialiser la requête attributive
                                pQueryFilter.WhereClause = ""
                            End If
                        End If
                        'Afficher l'état de la progression
                        i = i + 1
                        If (i Mod 10) = 0 Then txtMessage.Text = i.ToString & "/" & pTableSelection.SelectionSet.Count.ToString

                        'Extraire le prochain Id
                        nId = pEnumIds.Next
                    Loop

                    'Vérifier si la limite est dépassée
                    If pQueryFilter.WhereClause.Length > 0 Then
                        'Enlever la dernière '
                        pQueryFilter.WhereClause = pQueryFilter.WhereClause.Substring(0, pQueryFilter.WhereClause.Length - 1)
                        'Vérifier si le type d'attribut n'est pas un String
                        If pTable.Fields.Field(nPos).Type <> esriFieldType.esriFieldTypeString Then
                            'Enlever les ' car ce n'est pas un String
                            pQueryFilter.WhereClause = pQueryFilter.WhereClause.Replace("'", "")
                        End If
                        'Compléter la requête attributive
                        pQueryFilter.WhereClause = pRelClass.OriginPrimaryKey & " IN (" & pQueryFilter.WhereClause & ")"
                        'Ajouter les éléments liés à l'élément en relation
                        pTableRelSelection.SelectRows(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAdd, False)
                    End If
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pTableSelection = Nothing
            pTableRelSelection = Nothing
            pRelClassColl = Nothing
            pEnumRelClass = Nothing
            pRelClass = Nothing
            pQueryFilter = Nothing
            qValeurColl = Nothing
            pDataset = Nothing
            pRow = Nothing
            pEnumIds = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine permet de remplir le DataGridView à partir des attributs d'un élément spécifié. 
    '''</summary>
    '''
    '''<param name="pTable">Contient la table à traiter.</param>
    '''<param name="qDataGridView">DataGridView à remplir.</param>
    '''
    ''' <remarks>
    ''' Si l'élément est invalide, le DataGridView est vide.
    '''</remarks>
    Private Sub DataGridAttributElement(ByVal pTable As ITable, ByRef qDataGridView As DataGridView)
        'Déclarer les variables de travail
        Dim qBindingSource As BindingSource         'BindingSource utilisé pour lié le DataGridView et le DataSet
        Dim qDataTable As DataTable = Nothing       'DataTable utilisé pour contenir les colonnes et les lignes
        Dim qDataSet As DataSet = Nothing           'DataSet utilisé pour présenter et lié les données au DataGridView.
        Dim qDataRow As DataRow = Nothing           'DataRow utilisé pour définir les noms et valeurs d'Atrributs
        Dim pFields As IFields = Nothing            'Interface contenant les attributs de l'élément
        Dim qDataColNom As DataColumn = Nothing     'DataColumn utilisé pour définir la colonne Nom
        Dim qDataColValeur As DataColumn = Nothing  'DataColumn utilisé pour définir la colonne Valeur
        Dim i As Integer = Nothing                  'Compteur

        Try
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

            'Définir la colonne des listes des valeurs
            qDataColValeur = New DataColumn
            With qDataColValeur
                .DataType = System.Type.GetType("System.String")
                .ColumnName = "Valeurs"
                .Caption = "Valeurs"
            End With
            'Ajouter la colonne Valeur à la table
            qDataTable.Columns.Add(qDataColValeur)

            'Ajouter la table contenant les colonnes au dataset
            qDataSet.Tables.Add(qDataTable)

            'Vérifier si l'élément est invalide
            If pTable Is Nothing Then Return

            'Définir l'interface des attributs
            pFields = pTable.Fields

            'Traiter tous les attributs de l'élément
            For i = 0 To pFields.FieldCount - 1
                'Créer une nouvelle ligne dans la table
                qDataRow = qDataTable.NewRow()

                'Définir le nom de l'attribut
                qDataRow("Nom") = pFields.Field(i).Name

                'Vérifier si une liste de valeur existe
                If m_ListeValeur.Contains(pFields.Field(i).Name) Then
                    'Définir la valeur de l'attribut selon une liste déjà utilisée
                    qDataRow("Valeurs") = m_ListeValeur.Item(pFields.Field(i).Name).ToString
                    'Si la liste n'existe pas
                Else
                    'Définir la valeur de l'attribut
                    qDataRow("Valeurs") = ""
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
        End Try
    End Sub

    '''<summary>
    ''' Routine permet de conserver en mémoire les listes des valeurs par attribut de la table sélectionnée. 
    '''</summary>
    '''
    ''' <remarks>
    '''Les listes des valeurs sont conservées en mémoire de façon globale.
    '''</remarks>
    Private Sub ConserverListesValeurs()
        'Déclarer les variables de travail
        Dim i As Integer = 0    'Compteur

        Try

            'Traiter tous les attributs
            For i = 0 To dgvListesAttributs.Rows.Count - 2
                'Vérifier la présence d'une liste de valeurs
                If dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Length > 0 Then
                    'Vérifier la présence de la liste
                    If m_ListeValeur.Contains(dgvListesAttributs.Rows(i).Cells(0).Value.ToString) Then
                        'Détruire la liste valeur
                        m_ListeValeur.Remove(dgvListesAttributs.Rows(i).Cells(0).Value.ToString)
                    End If

                    'Conserver la liste des valeurs
                    m_ListeValeur.Add(dgvListesAttributs.Rows(i).Cells(1).Value.ToString, _
                                      dgvListesAttributs.Rows(i).Cells(0).Value.ToString)

                    'Si pas de liste de valeur
                Else
                    'Vérifier la présence de la liste
                    If m_ListeValeur.Contains(dgvListesAttributs.Rows(i).Cells(0).Value.ToString) Then
                        'Détruire la liste valeur
                        m_ListeValeur.Remove(dgvListesAttributs.Rows(i).Cells(0).Value.ToString)
                    End If
                End If
            Next

        Catch erreur As Exception
            'Message d'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de construire et retourner une requête attributive selon la liste d'attributs pour la table sélectionnée.
    '''</summary>
    ''' 
    Private Function ConstruireRequeteAttributive(ByVal pTable As ITable) As IQueryFilter
        'Déclarer les variables de travail
        Dim pQueryFilter As New QueryFilter     'Contient la requête attributive.
        Dim nPos As Integer = -1                'Contient la position de l'attribut traité.

        'Définir la valeur de retour par défaut
        ConstruireRequeteAttributive = Nothing

        Try
            'Traiter tous les attributs
            For i = 0 To dgvListesAttributs.Rows.Count - 2
                'Vérifier la présence d'une liste de valeurs
                If dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Length > 0 Then
                    'Extraire la position de l'attribut dans la table
                    nPos = pTable.FindField(dgvListesAttributs.Rows(i).Cells(0).Value.ToString)

                    'Vérifier si la table possède l'attribut
                    If nPos <> -1 Then
                        'Vérifier si l'attribut est un String
                        If pTable.Fields.Field(nPos).Type = esriFieldType.esriFieldTypeString Then
                            'Vérifier la présence d'une requête
                            If pQueryFilter.WhereClause.Length > 0 Then
                                'Définir la requête selon la liste des valeurs de type String
                                pQueryFilter.WhereClause = pQueryFilter.WhereClause & " AND " _
                                    & dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN ('" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Replace(",", "','") & "')"
                                'Si aucune requête présente
                            Else
                                'Définir la requête selon la liste des valeurs de type String
                                pQueryFilter.WhereClause = dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN ('" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString.Replace(",", "','") & "')"
                            End If

                            'Si le type n'est pas un String
                        Else
                            'Vérifier la présence d'une requête
                            If pQueryFilter.WhereClause.Length > 0 Then
                                'Définir la requête selon la liste des valeurs
                                pQueryFilter.WhereClause = pQueryFilter.WhereClause & " AND " _
                                    & dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN (" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString & ")"
                                'Si aucune requête présente
                            Else
                                'Définir la requête selon la liste des valeurs
                                pQueryFilter.WhereClause = dgvListesAttributs.Rows(i).Cells(0).Value.ToString _
                                    & " IN (" & dgvListesAttributs.Rows(i).Cells(1).Value.ToString & ")"
                            End If
                        End If
                    End If
                End If
            Next

            'Retourner la requête attributive
            ConstruireRequeteAttributive = pQueryFilter

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pQueryFilter = Nothing
        End Try
    End Function
#End Region
End Class