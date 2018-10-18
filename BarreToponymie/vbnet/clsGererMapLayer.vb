Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geometry
Imports System.Windows.Forms
Imports ESRI.ArcGIS.Geodatabase

'**
'Nom de la composante : clsGererMapLayer.vb
'
'''<summary>
''' Librairie de Classe qui permet de manipuler les différents types de Layer contenu dans une Map.
'''</summary>
'''
'''<remarks>
'''Cette librairie est utilisable pour les outils interactifs ou Batch dans ArcMap (ArcGis de ESRI).
'''
'''Auteur : Michel Pothier
'''Date : 6 Mai 2011
'''</remarks>
''' 
Public Class clsGererMapLayer
    'Déclarer les variables globales
    '''<summary>Interface contenant la Map à Gérer.</summary>
    Protected gpMap As IMap = Nothing
    Protected gqFeatureLayerCollection As Collection = Nothing

#Region "Propriétés"
    '''<summary>
    ''' Propriété qui permet de définir et retourner la Map traitée.
    '''</summary>
    ''' 
    Public Property Map() As IMap
        Get
            Map = gpMap
        End Get
        Set(ByVal value As IMap)
            gpMap = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner la collection de FeatureLayer traitée.
    '''</summary>
    ''' 
    Public Property FeatureLayerCollection() As Collection
        Get
            FeatureLayerCollection = gqFeatureLayerCollection
        End Get
        Set(ByVal value As Collection)
            gqFeatureLayerCollection = value
        End Set
    End Property
#End Region

#Region "Routine et fonction publiques"
    '''<summary>
    '''Routine qui permet d'initialiser la classe.
    '''</summary>
    '''
    Public Sub New(ByVal pMap As IMap, Optional ByVal bVisible As Boolean = False)
        'Définir les valeur par défaut
        gpMap = pMap

        'Définir la collection des FeatureLayer visibles par défaut
        gqFeatureLayerCollection = DefinirCollectionFeatureLayer(Not bVisible)
    End Sub

    '''<summary>
    '''Routine qui permet de vider la mémoire des objets de la classe.
    '''</summary>
    '''
    Protected Overrides Sub finalize()
        gpMap = Nothing
        gqFeatureLayerCollection = Nothing
    End Sub

    '''<summary>
    ''' Fonction qui permet d'extraire une table (FeatureLayer ou StandaloneTable) correspondant au nom spécifié.
    '''</summary>
    '''
    '''<param name="sTexte">Texte utilisé pour trouver la Table par défaut.</param>
    ''' 
    '''<returns>"ITable" correspondant au texte recherché, sinon "Nothing".</returns>
    ''' 
    Public Function ExtraireTableByName(ByVal sTexte As String) As ITable
        'Définir la valeur de retour par défaut
        ExtraireTableByName = Nothing

        Try
            'Extraire le FeatureLayer
            ExtraireTableByName = CType(ExtraireFeatureLayerByName(sTexte), ITable)

            'Vérifier si le FeatureLayer est valide
            If ExtraireTableByName Is Nothing Then
                'Extraire le StandaloneTable
                ExtraireTableByName = CType(ExtraireStandaloneTableByName(sTexte), ITable)
            End If

        Catch erreur As Exception
            Throw
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire le FeatureLayer correspondant au nom spécifié.
    '''</summary>
    '''
    '''<param name="sTexte">Texte utilisé pour trouver le FeatureLayer par défaut.</param>
    '''<param name="bNonVisible"> Indique si on doit aussi extraire les FeatureLayers non visibles.</param>
    ''' 
    '''<returns>"IFeatureLayer" correspondant au texte recherché, sinon "Nothing".</returns>
    ''' 
    Public Function ExtraireFeatureLayerByName(ByVal sTexte As String, Optional ByVal bNonVisible As Boolean = False) As IFeatureLayer
        'Déclarer la variables de travail
        Dim qFeatureLayerColl As Collection = Nothing   'Contient la liste des FeatureLayer visibles
        Dim pFeatureLayer As IFeatureLayer = Nothing    'Interface contenant une classe de données

        'Définir la valeur de retour par défaut
        ExtraireFeatureLayerByName = Nothing

        Try
            'Définir la liste des FeatureLayer
            qFeatureLayerColl = DefinirCollectionFeatureLayer(bNonVisible)

            'Traiter tous les FeatureLayer
            For i = 1 To qFeatureLayerColl.Count
                'Définir le FeatureLayer
                pFeatureLayer = CType(qFeatureLayerColl.Item(i), IFeatureLayer)
                'Vérifier la présence du texte recherché pour la valeur par défaut
                If sTexte.ToUpper = pFeatureLayer.Name.ToUpper Then
                    'Définir le featurelayer
                    ExtraireFeatureLayerByName = pFeatureLayer
                    'Sortir
                    Exit For
                End If
            Next

            'Vérifier si aucun trouvé
            If ExtraireFeatureLayerByName Is Nothing Then
                'Traiter tous les FeatureLayer
                For i = 1 To qFeatureLayerColl.Count
                    'Définir le FeatureLayer
                    pFeatureLayer = CType(qFeatureLayerColl.Item(i), IFeatureLayer)
                    'Vérifier la présence du texte recherché pour la valeur par défaut
                    If InStr(pFeatureLayer.Name.ToUpper, sTexte.ToUpper) > 0 Then
                        'Définir le featurelayer
                        ExtraireFeatureLayerByName = pFeatureLayer
                        'Sortir
                        Exit For
                    End If
                Next
            End If

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pFeatureLayer = Nothing
            qFeatureLayerColl = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire une table (FeatureLayer ou StandaloneTable) correspondant au nom du dataset name spécifié.
    '''</summary>
    '''
    '''<param name="sTexte">Texte utilisé pour trouver la Table par défaut.</param>
    ''' 
    '''<returns>"ITable" correspondant au texte recherché, sinon "Nothing".</returns>
    ''' 
    Public Function ExtraireTableByDatasetName(ByVal sTexte As String) As ITable
        'Définir la valeur de retour par défaut
        ExtraireTableByDatasetName = Nothing

        Try
            'Extraire le FeatureLayer
            ExtraireTableByDatasetName = CType(ExtraireFeatureLayerByDatasetName(sTexte), ITable)

            'Vérifier si le FeatureLayer est valide
            If ExtraireTableByDatasetName Is Nothing Then
                'Extraire le StandaloneTable
                ExtraireTableByDatasetName = CType(ExtraireStandaloneTableByDatasetName(sTexte), ITable)
            End If

        Catch erreur As Exception
            Throw
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire le FeatureLayer correspondant au nom du dataset name spécifié.
    '''</summary>
    '''
    '''<param name="sTexte">Texte utilisé pour trouver le FeatureLayer par défaut.</param>
    ''' 
    '''<returns>"IFeatureLayer" correspondant au texte recherché, sinon "Nothing".</returns>
    ''' 
    Public Function ExtraireFeatureLayerByDatasetName(ByVal sTexte As String) As IFeatureLayer
        'Déclarer la variables de travail
        Dim qFeatureLayerColl As Collection = Nothing   'Contient la liste des FeatureLayer visibles
        Dim pFeatureLayer As IFeatureLayer = Nothing    'Interface contenant une classe de données
        Dim pDataset As IDataset = Nothing              'Interface qui permet d'extraire le nom de la classe
        Dim i As Integer = Nothing                      'Compteur

        'Définir la valeur de retour par défaut
        ExtraireFeatureLayerByDatasetName = Nothing

        Try
            'Définir la liste des FeatureLayer
            qFeatureLayerColl = DefinirCollectionFeatureLayer(False)

            'Traiter tous les FeatureLayer
            For i = 1 To qFeatureLayerColl.Count
                'Définir le FeatureLayer
                pFeatureLayer = CType(qFeatureLayerColl.Item(i), IFeatureLayer)
                'Définir le Dataset
                pDataset = CType(pFeatureLayer.FeatureClass, IDataset)
                'Vérifier la présence du texte recherché pour la valeur par défaut
                If InStr(sTexte, pDataset.Name) > 0 Then
                    'Définir le featurelayer
                    ExtraireFeatureLayerByDatasetName = pFeatureLayer
                    'Sortir
                    Exit For
                End If
            Next

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            pFeatureLayer = Nothing
            qFeatureLayerColl = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire le StandaloneTable correspondant au nom du dataset name spécifié.
    '''</summary>
    '''
    '''<param name="sTexte">Texte utilisé pour trouver le FeatureLayer par défaut.</param>
    ''' 
    '''<returns>"IStandaloneTable" correspondant au texte recherché, sinon "Nothing".</returns>
    ''' 
    Public Function ExtraireStandaloneTableByDatasetName(ByVal sTexte As String) As IStandaloneTable
        'Déclarer la variables de travail
        Dim pStandaloneTableColl As IStandaloneTableCollection  'Interface qui permet d'extraire les StandaloneTable de la Map
        Dim pStandaloneTable As IStandaloneTable = Nothing      'Interface contenant une classe de données
        Dim pDataset As IDataset = Nothing                      'Interface qui permet d'extraire le nom de la classe
        Dim i As Integer = Nothing                              'Compteur

        'Définir la valeur de retour par défaut
        ExtraireStandaloneTableByDatasetName = Nothing

        Try
            'Définir la liste des StandaloneTable
            pStandaloneTableColl = CType(gpMap, IStandaloneTableCollection)

            'Traiter tous les StandaloneTable
            For i = 0 To pStandaloneTableColl.StandaloneTableCount - 1
                'Définir le StandaloneTable
                pStandaloneTable = pStandaloneTableColl.StandaloneTable(i)

                'Interface pour vérifier le nom de la classe
                pDataset = CType(pStandaloneTable.Table, IDataset)

                'Vérifier la présence du texte recherché pour la valeur par défaut
                If sTexte = pDataset.Name Then
                    'Retourner le StandaloneTable
                    ExtraireStandaloneTableByDatasetName = pStandaloneTable

                    'Sortir de la boucle
                    Exit For
                End If
            Next

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            pStandaloneTableColl = Nothing
            pStandaloneTable = Nothing
            pDataset = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire le StandaloneTable correspondant au nom du dataset name spécifié.
    '''</summary>
    '''
    '''<param name="sTexte">Texte utilisé pour trouver le FeatureLayer par défaut.</param>
    ''' 
    '''<returns>"IStandaloneTable" correspondant au texte recherché, sinon "Nothing".</returns>
    ''' 
    Public Function ExtraireStandaloneTableByName(ByVal sTexte As String) As IStandaloneTable
        'Déclarer la variables de travail
        Dim pStandaloneTableColl As IStandaloneTableCollection  'Interface qui permet d'extraire les StandaloneTable de la Map
        Dim pStandaloneTable As IStandaloneTable = Nothing      'Interface contenant une classe de données
        Dim i As Integer = Nothing                              'Compteur

        'Définir la valeur de retour par défaut
        ExtraireStandaloneTableByName = Nothing

        Try
            'Définir la liste des StandaloneTable
            pStandaloneTableColl = CType(gpMap, IStandaloneTableCollection)

            'Traiter tous les StandaloneTable
            For i = 0 To pStandaloneTableColl.StandaloneTableCount - 1
                'Définir le StandaloneTable
                pStandaloneTable = pStandaloneTableColl.StandaloneTable(i)

                'Vérifier la présence du texte recherché pour la valeur par défaut
                If InStr(sTexte, pStandaloneTable.Name) > 0 Then
                    'Retourner le StandaloneTable
                    ExtraireStandaloneTableByName = pStandaloneTable

                    'Sortir de la boucle
                    Exit For
                End If
            Next

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            pStandaloneTableColl = Nothing
            pStandaloneTable = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de définir la collection des FeatureLayers présents dans la Map.
    ''' On peut indiquer si on veut aussi extraire les FeatureLayers non visibles.
    '''</summary>
    ''' 
    '''<param name="bNonVisible"> Indique si on doit aussi extraire les FeatureLayers non visibles.</param>
    '''<param name="pEsriGeometryType"> Contient le type de géométrie des FeatureLayers recherchés.</param>
    ''' 
    '''<return>"Collection" contenant les "IFeatureLayer" visible ou non selon ce qui est demandé.</return>
    ''' 
    Public Function DefinirCollectionFeatureLayer(ByVal bNonVisible As Boolean, _
    Optional ByVal pEsriGeometryType As esriGeometryType = esriGeometryType.esriGeometryAny) As Collection
        'Déclarer les variables de travail
        Dim pLayer As ILayer = Nothing                      'Interface contenant un Layer
        Dim pGroupLayer As IGroupLayer = Nothing            'Interface contenant un Groupe de Layers
        Dim pFeatureLayer As IFeatureLayer = Nothing        'Interface contenant un FeatureLayer
        Dim i As Integer = Nothing                          'Compteur

        'Retourner le résultat par défaut
        DefinirCollectionFeatureLayer = New Collection

        Try
            'Traiter tous les Layers
            For i = 0 To gpMap.LayerCount - 1
                'Définir le Layer à traiter
                pLayer = gpMap.Layer(i)

                'Vérifier si on tient on doit extraire le Layer même s'il n'est pas visible
                If pLayer.Visible = True Or bNonVisible = True Then
                    'Vérifier le Layer est un FeatureLayer
                    If TypeOf pLayer Is IFeatureLayer Then
                        'Définir le FeatureLayer
                        pFeatureLayer = CType(pLayer, IFeatureLayer)

                        'Vérifier la présence de la FeatureClass
                        If Not pFeatureLayer.FeatureClass Is Nothing Then
                            'Vérifier le type de géométrie correspond à ce qui est recherché
                            If pEsriGeometryType = esriGeometryType.esriGeometryAny _
                            Or pFeatureLayer.FeatureClass.ShapeType = pEsriGeometryType Then
                                'Ajouter un nouveau FeatureLayer dans la collection
                                DefinirCollectionFeatureLayer.Add(pFeatureLayer)
                            End If
                        End If

                        'Vérifier les autres Layer dans un GroupLayer
                    ElseIf TypeOf pLayer Is IGroupLayer Then
                        'Définir le GroupLayer
                        pGroupLayer = CType(pLayer, IGroupLayer)

                        'Trouver les autres FeatureLayer dans un GroupLayer
                        Call DefinirCollectionFeatureLayerGroup(DefinirCollectionFeatureLayer, pGroupLayer, bNonVisible)
                    End If
                End If
            Next

        Catch e As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pLayer = Nothing
            pGroupLayer = Nothing
            pFeatureLayer = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire le GroupLayer dans lequel le Layer recherché est présent.
    '''</summary>
    '''
    '''<param name="pLayerRechercher">Interface contenant le Layer à rechercher dans la Map active.</param>
    '''<param name="nPosition">Position su Layer dans le GroupLayer.</param>
    ''' 
    '''<returns>"Collection" contenant les "IGroupLayer" recherchés.</returns>
    ''' 
    Public Function DefinirGroupLayer(ByVal pLayerRechercher As ILayer, ByRef nPosition As Integer) As IGroupLayer
        'Déclarer les variables de travail
        Dim pLayer As ILayer = Nothing              'Interface contenant un Layer
        Dim pGroupLayer As IGroupLayer = Nothing    'Interface contenant un GroupLayer
        Dim i As Integer = Nothing                  'Compteur

        'Définir la valeur par défaut
        DefinirGroupLayer = Nothing

        Try
            'Vérifier si le Layer est valide
            If pLayerRechercher Is Nothing Then Return Nothing

            'Traiter tous les Layers
            For i = 0 To gpMap.LayerCount - 1
                'Définir le Layer à traiter
                pLayer = gpMap.Layer(i)

                'Vérifier si le Layer trouvé est le même que celui recherché
                If pLayer IsNot pLayerRechercher Then
                    'Vérifier les autres Layer dans un GroupLayer
                    If TypeOf pLayer Is IGroupLayer Then
                        'Définir le GroupLayer
                        pGroupLayer = CType(pLayer, IGroupLayer)

                        'Trouver les autres GroupLayer dans un GroupLayer
                        DefinirGroupLayer = ExtraireGroupLayerGroup(pGroupLayer, pLayerRechercher, nPosition)
                    End If

                    'Sortir de la boucle si le GroupLayer a été trouvé
                    If Not DefinirGroupLayer Is Nothing Then Exit For
                End If
            Next

        Catch e As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pLayer = Nothing
            pGroupLayer = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'indiquer si le FeatureLayer est visible ou non dans la IMap.
    '''</summary>
    ''' 
    '''<param name="pLayerRechercher"> Interface ESRI contenant le Layer à rechercher.</param>
    '''<param name="bPresent"> Contient l'indication si le Layer à rechercher est présent dans la Map.</param>
    ''' 
    '''<return>"Collection" contenant les "IFeatureLayer" visible ou non.</return>
    ''' 
    Public Function EstVisible(ByVal pLayerRechercher As ILayer, ByVal bPresent As Boolean) As Boolean
        'Déclarer les variables de travail
        Dim pLayer As ILayer = Nothing              'Interface contenant un Layer
        Dim pGroupLayer As IGroupLayer = Nothing    'Interface contenant un Groupe de Layers
        Dim i As Integer = Nothing                  'Compteur

        Try
            'Traiter tous les Layers
            For i = 0 To gpMap.LayerCount - 1
                'Définir le Layer à traiter
                pLayer = gpMap.Layer(i)

                'Vérifier si le Layer trouvé est le même que celui recherché
                If pLayer Is pLayerRechercher Then
                    'Retourner l'indication s'il est visible ou non
                    EstVisible = pLayer.Visible

                    'Sortir de la recherche
                    Exit For

                    'Si ce n'est pas le Layer recherché et que c'est un GroupLayer
                ElseIf TypeOf pLayer Is IGroupLayer Then
                    'Définir le GroupLayer
                    pGroupLayer = CType(pLayer, IGroupLayer)

                    'Retourner l'indication s'il est visible ou non
                    EstVisible = EstVisibleGroup(pGroupLayer, pLayer, bPresent)

                    'Sortir si le Layer est présent dans le GroupLayer
                    If bPresent Then Exit For
                End If
            Next

        Catch e As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pLayer = Nothing
            pGroupLayer = Nothing
        End Try
    End Function
#End Region

#Region "Routine et fonction privées"
    '''<summary>
    ''' Routine qui permet de définir la collection des FeatureLayers contenus dans un GroupLayer.
    ''' On peut indiquer si on veut aussi extraire les FeatureLayers non visibles.
    '''</summary>
    ''' 
    '''<param name="qFeatureLayerColl">Collection des FeatureLayer.</param>
    '''<param name="pGroupLayer">Interface ESRI contenant un group de Layers.</param>
    '''<param name="bNonVisible">Indique si on doit aussi extraire les FeatureLayers non visibles.</param>
    '''<param name="pEsriGeometryType"> Contient le type de géométrie des FeatureLayers recherchés.</param>
    ''' 
    Private Sub DefinirCollectionFeatureLayerGroup(ByRef qFeatureLayerColl As Collection, ByVal pGroupLayer As IGroupLayer, _
    ByVal bNonVisible As Boolean, Optional ByVal pEsriGeometryType As esriGeometryType = esriGeometryType.esriGeometryAny)
        'Déclarer les variables de travail
        Dim pLayer As ILayer = Nothing                      'Interface contenant un Layer
        Dim pGroupLayer2 As IGroupLayer = Nothing           'Interface contenant un GroupLayer
        Dim pFeatureLayer As IFeatureLayer = Nothing        'Interface contenant un FeatureLayer
        Dim pCompositeLayer As ICompositeLayer = Nothing    'Interface utiliser pour extraire un Layer dans un GroupLayer
        Dim i As Integer = Nothing                          'Compteur

        Try
            'Interface pour accéder aux Layers du GroupLayer
            pCompositeLayer = CType(pGroupLayer, ICompositeLayer)

            'Trouver le Groupe de Layer
            For i = 0 To pCompositeLayer.Count - 1
                'Interface pour comparer le nom du Layer
                pLayer = pCompositeLayer.Layer(i)

                'Vérifier si on tient compte du selectable
                If pLayer.Visible = True Or bNonVisible = True Then
                    'Vérifier le Layer est un FeatureLayer
                    If TypeOf pLayer Is IFeatureLayer Then
                        'Définir le FeatureLayer
                        pFeatureLayer = CType(pLayer, IFeatureLayer)

                        'Vérifier la présence de la FeatureClass
                        If Not pFeatureLayer.FeatureClass Is Nothing Then
                            'Vérifier le type de géométrie correspond à ce qui est recherché
                            If pEsriGeometryType = esriGeometryType.esriGeometryAny _
                            Or pFeatureLayer.FeatureClass.ShapeType = pEsriGeometryType Then
                                'Ajouter un nouveau FeatureLayer dans la collection
                                qFeatureLayerColl.Add(pFeatureLayer)
                            End If
                        End If

                        'Vérifier les autres noms dans un GroupLayer
                    ElseIf TypeOf pLayer Is IGroupLayer Then
                        'Définir le GroupLayer
                        pGroupLayer2 = CType(pLayer, IGroupLayer)

                        'Trouver les autres FeatureLayer dans un GroupLayer
                        Call DefinirCollectionFeatureLayerGroup(qFeatureLayerColl, pGroupLayer2, bNonVisible)
                    End If
                End If
            Next i

        Catch e As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pLayer = Nothing
            pGroupLayer2 = Nothing
            pFeatureLayer = Nothing
            pCompositeLayer = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'extraire le GroupLayer contenant un FeatureLayer.
    ''' Le GroupLayer recherché est contenu dans un GroupLayer.
    '''</summary>
    ''' 
    '''<param name="pGroupLayer">Interface ESRI contenant un groupe de Layers.</param>
    '''<param name="pLayerRechercher">Interface ESRI contenant le Layer à rechercher.</param>
    '''<param name="nPosition">Position su Layer dans le GroupLayer.</param>
    ''' 
    Private Function ExtraireGroupLayerGroup(ByVal pGroupLayer As IGroupLayer, ByVal pLayerRechercher As ILayer, ByRef nPosition As Integer) As IGroupLayer
        'Déclarer les variables de travail
        Dim pLayer As ILayer = Nothing                      'Interface contenant un Layer
        Dim pGroupLayer2 As IGroupLayer = Nothing           'Interface contenant un GroupLayer
        Dim pCompositeLayer As ICompositeLayer = Nothing    'Interface utiliser pour extraire un Layer dans un GroupLayer
        Dim i As Integer = Nothing                          'Compteur

        'Initialiser les variables de travail
        ExtraireGroupLayerGroup = Nothing

        Try
            'Interface pour accéder aux Layers du GroupLayer
            pCompositeLayer = CType(pGroupLayer, ICompositeLayer)

            'Trouver le Groupe de Layer
            For i = 0 To pCompositeLayer.Count - 1
                'Interface pour comparer le nom du Layer
                pLayer = pCompositeLayer.Layer(i)

                'Vérifier si le Layer trouvé est le même que celui recherché
                If pLayerRechercher Is pLayer Then
                    'Retourner le Groupe du Layer recherché
                    ExtraireGroupLayerGroup = pGroupLayer
                    'Définir la position du Layer dans le GroupLayer
                    nPosition = i
                    'Sortir
                    Exit For
                Else
                    'Vérifier les autres noms dans un GroupLayer
                    If TypeOf pLayer Is IGroupLayer Then
                        'Définir le GroupLayer
                        pGroupLayer2 = CType(pLayer, IGroupLayer)

                        'Trouver les autres GroupLayer dans un GroupLayer
                        ExtraireGroupLayerGroup = ExtraireGroupLayerGroup(pGroupLayer2, pLayerRechercher, nPosition)
                    End If

                    'Sortir
                    If Not ExtraireGroupLayerGroup Is Nothing Then Exit For
                End If
            Next i

        Catch e As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pLayer = Nothing
            pGroupLayer2 = Nothing
            pCompositeLayer = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'indiquer si le FeatureLayer est visible ou non dans la IMap.
    '''</summary>
    ''' 
    '''<param name="pGroupLayer">Interface ESRI contenant un group de Layers.</param>
    '''<param name="pLayerRechercher"> Interface ESRI contenant le Layer à rechercher.</param>
    '''<param name="bPresent"> Contient l'indication si le Layer à rechercher est présent dans la Map.</param>
    ''' 
    '''<return>"Collection" contenant les "IFeatureLayer" visible ou non.</return>
    ''' 
    Private Function EstVisibleGroup(ByVal pGroupLayer As IGroupLayer, ByVal pLayerRechercher As ILayer, ByVal bPresent As Boolean) As Boolean
        'Déclarer les variables de travail
        Dim pLayer As ILayer = Nothing                      'Interface contenant un Layer
        Dim pGroupLayer2 As IGroupLayer = Nothing           'Interface contenant un Groupe de Layers
        Dim pCompositeLayer As ICompositeLayer = Nothing    'Interface utiliser pour extraire un Layer dans un GroupLayer
        Dim i As Integer = Nothing                          'Compteur

        Try
            'Interface pour accéder aux Layers du GroupLayer
            pCompositeLayer = CType(pGroupLayer, ICompositeLayer)

            'Trouver le Groupe de Layer
            For i = 0 To pCompositeLayer.Count - 1
                'Interface pour comparer le nom du Layer
                pLayer = pCompositeLayer.Layer(i)

                'Vérifier si le Layer trouvé est le même que celui recherché
                If pLayer Is pLayerRechercher Then
                    'Retourner l'indication s'il est visible ou non
                    EstVisibleGroup = pLayer.Visible

                    'Sortir de la recherche
                    Exit For

                    'Si ce n'est pas le Layer recherché et que c'est un GroupLayer
                ElseIf TypeOf pLayer Is IGroupLayer Then
                    'Définir le GroupLayer
                    pGroupLayer2 = CType(pLayer, IGroupLayer)

                    'Retourner l'indication s'il est visible ou non
                    EstVisibleGroup = EstVisibleGroup(pGroupLayer2, pLayer, bPresent)

                    'Sortir si le Layer est présent dans le GroupLayer
                    If bPresent Then Exit For
                End If
            Next

        Catch e As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pLayer = Nothing
            pGroupLayer = Nothing
            pCompositeLayer = Nothing
        End Try
    End Function
#End Region
End Class
