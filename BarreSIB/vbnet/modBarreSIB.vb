Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.SystemUI
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.Geometry
Imports System.Windows.Forms
Imports ESRI.ArcGIS.esriSystem

'**
'Nom de la composante : modBarreSIB.vb 
'
'''<summary>
'''Librairies de routines contenant toutes les fonctionnalités nécessaires au système SIB.
'''</summary>
'''
'''<remarks>
'''Auteur : Michel Pothier
'''</remarks>
''' 
Module modBarreSIB
    'Liste des variables publiques utilisées
    ''' <summary>Interface utilisé pour arrêter un traitement en progression.</summary>
    Public m_TrackCancel As ITrackCancel = Nothing
    ''' <summary>Interface ESRI contenant l'application ArcMap.</summary>
    Public m_Application As IApplication = Nothing
    ''' <summary>Interface ESRI contenant le document ArcMap.</summary>
    Public m_MxDocument As IMxDocument = Nothing
    ''' <summary>Objet contenant le menu de connexion.</summary>
    Public m_MenuConnexion As dckMenuConnexion
    ''' <summary>Objet contenant le menu d'identification.</summary>
    Public m_MenuIdentification As dckMenuIdentification
    ''' <summary>Objet contenant le menu des relations.</summary>
    Public m_MenuRelations As dckMenuRelations
    ''' <summary>Objet qui permet de gérer la Map et ses layers.</summary>
    Public m_MapLayer As clsGererMapLayer = Nothing
    ''' <summary>Objet qui permet de gérer l'information des catalogues.</summary>
    Public m_Catalogue As clsGererCatalogue = Nothing
    ''' <summary>Conteur de de recherche effectuée.</summary>
    Public m_Compteur As Integer = 1
    ''' <summary>Conteur de de recherche effectuée.</summary>
    Public m_MaxItems As Integer = 1000
    ''' <summary>Indique si on doit créer un Layer de sélection après une recherche.</summary>
    Public m_CreerLayer As Boolean = False

    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un document est ouvert.</summary>
    Public m_DocumentEventsOpenDocument As IDocumentEvents_OpenDocumentEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un nouveau document est ouvert.</summary>
    Public m_DocumentEventsNewDocument As IDocumentEvents_NewDocumentEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un nouveau document est activé.</summary>
    Public m_ActiveViewEventsContentsChanged As IActiveViewEvents_ContentsChangedEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un nouvel item est ajouté à la Map active.</summary>
    Public m_ActiveViewEventsItemAdded As IActiveViewEvents_ItemAddedEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un nouvel item est retiré de la Map active</summary>
    Public m_ActiveViewEventsItemDeleted As IActiveViewEvents_ItemDeletedEventHandler

    '''<summary>Valeur initiale de la dimension en hauteur du menu de production.</summary>
    Public m_Height As Integer = 330
    '''<summary>Valeur initiale de la dimension en largeur du menu de production.</summary>
    Public m_Width As Integer = 300

#Region "Routines et fonctions publiques pour le menu de production"
    '''<summary>
    ''' Routine permet de créer un FeatureLayer de sélection, le rendre visible, de l'ajouter au début de la Map active et de rendre invisible les autres Layers.
    '''</summary>
    '''
    '''<param name="pFeatureLayer">FeatureLayer contenant la sélection d'éléments.</param>
    '''<param name="sNomLayer">Nom de l'attribut à ajouter dans la requête.</param>
    ''' 
    '''<returns>"IFeatureLayer" généré et ajouté dans la Map active</returns>
    ''' 
    ''' <remarks>
    ''' Si aucun élément n'est sélectionné, rien n'est effectué.
    '''</remarks>
    Public Function CreerLayerSelection(ByVal pFeatureLayer As IFeatureLayer, ByVal sNomLayer As String) As IFeatureLayer
        'Déclarer les variables de travail
        Dim pFeatureSelection As IFeatureSelection = Nothing    'Interface qui permet de traiter la sélection du Layer
        Dim pSelectionSet As ISelectionSet = Nothing            'Interface contenant la sélection du Layer

        Dim pGeoFeatureLayer As IGeoFeatureLayer = Nothing      'Interface contenant les paramètres d'affichage d'un Layer
        Dim pDisplayString As IDisplayString = Nothing          'Interface utilisé pour extraire l'information du display
        Dim pFLDef As IFeatureLayerDefinition = Nothing         'Interface utilisé pour créer un Layer de sélection

        Dim pNewFeatureLayer As IFeatureLayer = Nothing         'Interface contenant le nouveau FeatureLayer
        Dim pNewGeoFeatureLayer As IGeoFeatureLayer = Nothing   'Interface contenant les nouveaux paramètres d'affichage d'un Layer
        Dim pNewDisplayString As IDisplayString = Nothing       'Interface utilisé pour remettre l'information du display
        Dim pNewFLDef As IFeatureLayerDefinition = Nothing      'Interface utilisé pour ajouter une recherche attributive

        'Initialiser lae FeatureLayer de retour
        CreerLayerSelection = Nothing

        Try
            'Interface pour traiter la sélection
            pFeatureSelection = CType(pFeatureLayer, IFeatureSelection)
            pSelectionSet = pFeatureSelection.SelectionSet

            'Vérifier si au moins un élément est sélectionné
            If pSelectionSet.Count > 0 Then
                'Interface pour créer un FeatureLayer selon la sélection
                pFLDef = CType(pFeatureLayer, IFeatureLayerDefinition)
                pNewFeatureLayer = pFLDef.CreateSelectionLayer(sNomLayer, True, "", "")
                pNewFeatureLayer.DisplayField = pFeatureLayer.DisplayField
                pNewFLDef = CType(pNewFeatureLayer, IFeatureLayerDefinition)
                pNewFLDef.DefinitionExpression = pFLDef.DefinitionExpression

                'Remettre l'information du display
                pDisplayString = CType(pFeatureLayer, IDisplayString)
                pNewDisplayString = CType(pNewFeatureLayer, IDisplayString)
                pNewDisplayString.ExpressionProperties = pDisplayString.ExpressionProperties

                'Conserver la représentation graphique
                pGeoFeatureLayer = CType(pFeatureLayer, IGeoFeatureLayer)
                pNewGeoFeatureLayer = CType(pNewFeatureLayer, IGeoFeatureLayer)
                pNewGeoFeatureLayer.Renderer = pGeoFeatureLayer.Renderer
                pNewGeoFeatureLayer.AnnotationProperties = pGeoFeatureLayer.AnnotationProperties
                pNewGeoFeatureLayer.DisplayAnnotation = pGeoFeatureLayer.DisplayAnnotation

                'Remettre la sélection dans le nouveau layer
                pFeatureSelection = CType(pNewFeatureLayer, IFeatureSelection)
                pFeatureSelection.SelectionSet = pSelectionSet

                'Copier tous les relationships de l'ancien FeatureLayer vers le nouveau FeatureLayer.
                CopierRelationShipFeatureLayer(pFeatureLayer, pNewFeatureLayer)

                'Ajouter le Layer visible
                pNewFeatureLayer.Visible = True
                m_MxDocument.FocusMap.AddLayer(pNewFeatureLayer)

                'Conserver seulement l'affichage visible du Layer de sélection ajouté
                For i = 1 To m_MxDocument.FocusMap.LayerCount - 1
                    'Rendre le Layer invisible
                    m_MxDocument.FocusMap.Layer(i).Visible = False
                Next

                'Définir le FeatureLayer de retour
                CreerLayerSelection = pNewFeatureLayer
            End If

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pFeatureSelection = Nothing
            pSelectionSet = Nothing
            pGeoFeatureLayer = Nothing
            pDisplayString = Nothing
            pFLDef = Nothing
            pNewFeatureLayer = Nothing
            pNewGeoFeatureLayer = Nothing
            pNewDisplayString = Nothing
            pNewFLDef = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'effectuer un Zoom selon les éléments sélectionnés d'un FeatureLayer.
    '''</summary>
    '''
    '''<param name="pFeatureSelection">Interface qui permet d'extraire les éléments sélectionnés d'un FeatureLayer.</param>
    '''
    ''' <remarks>
    ''' Si aucune sélection n'est présente, Aucun Zomm n'est effectué.
    '''</remarks>
    Public Sub ZoomToFeatureSelection(ByRef pFeatureSelection As IFeatureSelection)
        'Déclarer les variables de travail
        Dim pFeature As IFeature = Nothing      'Interface qui contient un élément sélectionnés
        Dim pEnvelope As IEnvelope = Nothing    'Interface qui contient l'enveloppe de tous les éléments sélectionnés
        Dim pEnumIds As IEnumIDs = Nothing      'Interface pour extraire tous les Ids sélectionnés
        Dim nId As Integer = Nothing            'Identifiant d'un élément

        'Sortir si aucun élément sélectionné
        If pFeatureSelection Is Nothing Then Return

        Try
            'Vérifier si au moins un élément est sélectionné
            If pFeatureSelection.SelectionSet.Count > 0 Then
                'Interface pour extraire tous les Ids
                pEnumIds = pFeatureSelection.SelectionSet.IDs

                'Extraire le premier Id
                nId = pEnumIds.Next

                'Traiter tous les Ids
                Do Until nId = -1
                    'Extraire l'élément
                    pFeature = CType(pFeatureSelection.SelectionSet.Target.GetRow(nId), IFeature)

                    'Vérifier si l'enveloppe est nulle
                    If pEnvelope Is Nothing Then
                        'Définir l'enveloppe initiale à partir du premier élément trouvé
                        pEnvelope = pFeature.ShapeCopy.Envelope
                    Else
                        'Union avec les enveloppes des autres éléments
                        pEnvelope.Union(pFeature.ShapeCopy.Envelope)
                    End If

                    'Extraire le premier Id
                    nId = pEnumIds.Next
                Loop

                'Agrandir l'enveloppe de 10% de l'élément en erreur
                pEnvelope.Expand(pEnvelope.Width / 10, pEnvelope.Height / 10, False)
                'Définir la nouvelle fenêtre de travail
                m_MxDocument.ActiveView.Extent = pEnvelope
                'Rafraîchier l'affichage
                m_MxDocument.ActiveView.Refresh()
                m_MxDocument.UpdateContents()
                'Permet de vider la mémoire sur les évènements
                System.Windows.Forms.Application.DoEvents()
            End If

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pFeature = Nothing
            pEnvelope = Nothing
            pEnumIds = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de copier une ou toutes les relationships d'une table d'origine vers une table de destination.
    ''' Une table est soit un FeatureLayer ou un StandaloneTable.
    '''</summary>
    '''
    '''<param name="pTableOrigine">Interface contenant les relations à copier.</param>
    '''<param name="pRelClass">Interface contenant la classe en relation et ses paramètres.</param>
    '''
    ''' <remarks>
    ''' Si aucune relation n'est présent dans la table d'origine, aucune relation ne sera ajoutée dans la table de destination.
    '''</remarks>
    Public Function AjouterRelationShipTable(ByVal pTableOrigine As IDataset, ByRef pRelClass As IRelationshipClass) As Boolean
        'Déclarer les variables de travail
        Dim pRelClassCollEdit As IRelationshipClassCollectionEdit = Nothing 'Interface qui permet d'ajouter les relationships

        'Par défaut, L'ajout ne peut être effectuée
        AjouterRelationShipTable = False

        Try
            'Vérifier si la table d'origine ou la relation sont invalides
            If pTableOrigine Is Nothing Or pRelClass Is Nothing Then Return AjouterRelationShipTable

            'Sortir si la relation est déjà présente
            If TrouverRelationShipTable(pTableOrigine, pRelClass.ForwardPathLabel) IsNot Nothing Then Return AjouterRelationShipTable

            'Interface pour ajouter les relationships
            pRelClassCollEdit = CType(pTableOrigine, IRelationshipClassCollectionEdit)

            'Ajouter la relation dans la table
            pRelClassCollEdit.AddRelationshipClass(pRelClass)

            'Indiquer que l'ajout de la relation s'est effectuée correctement
            AjouterRelationShipTable = True
 
        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pRelClassCollEdit = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de copier tous les relationships de l'ancien FeatureLayer vers le nouveau FeatureLayer.. 
    '''</summary>
    '''
    '''<param name="pFeatureLayer">Interface contenant les relationship et correspondant à l'ancien FeatureLayer.</param>
    '''<param name="pNewFeatureLayer">Interface correspondantau nouveau FeatureLayer et dans lequel on veut copier les relationship.</param>
    '''
    ''' <remarks>
    ''' Si aucun relationship n'est présent dans l'ancien FeatureLayer, aucun relationship ne sera ajouté dans le nouveau.
    '''</remarks>
    Public Sub CopierRelationShipFeatureLayer(ByVal pFeatureLayer As IFeatureLayer, ByRef pNewFeatureLayer As IFeatureLayer)
        'Déclarer les variables de travail
        Dim pRelClassColl As IRelationshipClassCollection = Nothing         'Interface qui permet d'extraire les relationships
        Dim pRelClassCollEdit As IRelationshipClassCollectionEdit = Nothing 'Interface qui permet d'ajouter les relationships
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing               'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing                       'Interface contenant la classe en relation et ses paramètres

        Try
            'Interface extraire les relationships
            pRelClassColl = CType(pFeatureLayer, IRelationshipClassCollection)

            'Interface ajouter les relationships
            pRelClassCollEdit = CType(pNewFeatureLayer, IRelationshipClassCollectionEdit)

            'Interface pour énumérer les relates de la classe de découpage
            pEnumRelClass = pRelClassColl.RelationshipClasses

            'Initialiser la recherche des Relate de la classe de découpage
            pEnumRelClass.Reset()

            'Trouver la première classe en relation
            pRelClass = pEnumRelClass.Next

            'Traiter tous les classes en relation
            Do Until pRelClass Is Nothing
                'Initialiser la méthode d'affichage
                pRelClassCollEdit.AddRelationshipClass(pRelClass)

                'Trouver la prochaine classe en relation 
                pRelClass = pEnumRelClass.Next
            Loop

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pRelClassColl = Nothing
            pRelClassCollEdit = Nothing
            pEnumRelClass = Nothing
            pRelClass = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de copier une ou toutes les relationships d'une table d'origine vers une table de destination.
    ''' Une table est soit un FeatureLayer ou un StandaloneTable.
    '''</summary>
    '''
    '''<param name="pTableOrigine">Interface contenant les relations à copier.</param>
    '''<param name="pTableDestination">Interface contenant la table dans lesquels les relations seront copiées.</param>
    '''<param name="sNomRelation">Nom de la relation à copier. "*" indique toutes les relations.</param>
    '''
    ''' <remarks>
    ''' Si aucune relation n'est présent dans la table d'origine, aucune relation ne sera ajoutée dans la table de destination.
    '''</remarks>
    Public Function CopierRelationShipTable(ByVal pTableOrigine As IDataset, ByRef pTableDestination As IDataset, Optional ByVal sNomRelation As String = "*") As Boolean
        'Déclarer les variables de travail
        Dim pRelClassColl As IRelationshipClassCollection = Nothing         'Interface qui permet d'extraire les relationships
        Dim pRelClassCollEdit As IRelationshipClassCollectionEdit = Nothing 'Interface qui permet d'ajouter les relationships
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing               'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing                       'Interface contenant la classe en relation et ses paramètres

        'Par défaut, La copie ne peut être effectuée
        CopierRelationShipTable = False

        Try
            'Vérifier si la table d'origine ou la table de destination sont invalides
            If pTableOrigine Is Nothing Or pTableDestination Is Nothing Then Return CopierRelationShipTable

            'Sortir si la classe de la table de destination n'est pas la même que celle de l'origine
            If pTableOrigine.BrowseName <> pTableDestination.BrowseName Then Return CopierRelationShipTable

            'Sortir si la relation est déjà présente
            If TrouverRelationShipTable(pTableDestination, sNomRelation) IsNot Nothing Then Return CopierRelationShipTable

            'Interface extraire les relationships
            pRelClassColl = CType(pTableOrigine, IRelationshipClassCollection)

            'Interface pour ajouter les relationships
            pRelClassCollEdit = CType(pTableDestination, IRelationshipClassCollectionEdit)

            'Interface pour énumérer les relates de la table
            pEnumRelClass = pRelClassColl.RelationshipClasses

            'Initialiser la recherche des Relate de la table
            pEnumRelClass.Reset()

            'Trouver la première classe en relation
            pRelClass = pEnumRelClass.Next

            'Traiter toutes les classes en relation
            Do Until pRelClass Is Nothing
                'Vérifier si le nom de la relation correspond à celle spécifiée
                If sNomRelation = "*" Or sNomRelation.ToUpper = pRelClass.ForwardPathLabel.ToUpper Then
                    'Ajouter la relation dans la table de destination
                    pRelClassCollEdit.AddRelationshipClass(pRelClass)

                    'Indiquer que la copie des relations s'est effectuée correctement
                    CopierRelationShipTable = True
                End If

                'Trouver la prochaine classe en relation 
                pRelClass = pEnumRelClass.Next
            Loop

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pRelClassColl = Nothing
            pRelClassCollEdit = Nothing
            pEnumRelClass = Nothing
            pRelClass = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de détruire une ou toutes les relationships d'une table.
    ''' Une table est soit un FeatureLayer ou un StandaloneTable.
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant les relations à détruire.</param>
    '''<param name="sNomRelation">Nom de la relation à détruire. "*" indique toutes les relations.</param>
    '''
    ''' <remarks>
    ''' Si aucune relation n'est présente dans la table, aucune relation ne sera détruire dans la table.
    '''</remarks>
    Public Function DetruireRelationShipTable(ByVal pTable As IDataset, Optional ByVal sNomRelation As String = "*") As Boolean
        'Déclarer les variables de travail
        Dim pRelClassColl As IRelationshipClassCollection = Nothing         'Interface qui permet d'extraire les relationships
        Dim pRelClassCollEdit As IRelationshipClassCollectionEdit = Nothing 'Interface qui permet de détruire les relationships
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing               'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing                       'Interface contenant la classe en relation et ses paramètres

        'Par défaut, La destruction ne peut être effectuée
        DetruireRelationShipTable = False

        Try
            'Vérifier si la table est invalide
            If pTable Is Nothing Then Return DetruireRelationShipTable

            'Interface extraire les relationships
            pRelClassColl = CType(pTable, IRelationshipClassCollection)

            'Interface pour détruire les relationships
            pRelClassCollEdit = CType(pTable, IRelationshipClassCollectionEdit)

            'Interface pour énumérer les relates de la table
            pEnumRelClass = pRelClassColl.RelationshipClasses

            'Initialiser la recherche des Relate de la table
            pEnumRelClass.Reset()

            'Trouver la première classe en relation
            pRelClass = pEnumRelClass.Next

            'Traiter toutes les classes en relation
            Do Until pRelClass Is Nothing
                'Vérifier si le nom de la relation correspond à celle spécifiée
                If sNomRelation = "*" Or sNomRelation.ToUpper = pRelClass.ForwardPathLabel.ToUpper Then
                    'Détruire la relation dans la table
                    pRelClassCollEdit.RemoveRelationshipClass(pRelClass)

                    'Indiquer que la destruction de relation s'est effectuée correctement
                    DetruireRelationShipTable = True
                End If

                'Trouver la prochaine classe en relation 
                pRelClass = pEnumRelClass.Next
            Loop

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pRelClassColl = Nothing
            pRelClassCollEdit = Nothing
            pEnumRelClass = Nothing
            pRelClass = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de trouver une relation d'une table en fonction d'un nom de relation.
    ''' Une table est soit un FeatureLayer ou un StandaloneTable.
    '''</summary>
    '''
    '''<param name="pTable">Interface contenant les relations à trouver.</param>
    '''<param name="sNomRelation">Nom de la relation à trouver.</param>
    '''
    ''' <remarks>
    ''' Si aucune relation n'est présente dans la table, aucune relation ne sera détruire dans la table.
    '''</remarks>
    Public Function TrouverRelationShipTable(ByVal pTable As IDataset, ByVal sNomRelation As String) As IRelationshipClass
        'Déclarer les variables de travail
        Dim pRelClassColl As IRelationshipClassCollection = Nothing         'Interface qui permet d'extraire les relationships
        Dim pEnumRelClass As IEnumRelationshipClass = Nothing               'Interface qui permet d'accéder aux classes en relation
        Dim pRelClass As IRelationshipClass = Nothing                       'Interface contenant la classe en relation et ses paramètres

        'Par défaut, La destruction ne peut être effectuée
        TrouverRelationShipTable = Nothing

        Try
            'Vérifier si la table est invalide
            If pTable Is Nothing Then Return TrouverRelationShipTable

            'Interface extraire les relationships
            pRelClassColl = CType(pTable, IRelationshipClassCollection)

            'Interface pour énumérer les relates de la table
            pEnumRelClass = pRelClassColl.RelationshipClasses

            'Initialiser la recherche des Relate de la table
            pEnumRelClass.Reset()

            'Trouver la première classe en relation
            pRelClass = pEnumRelClass.Next

            'Traiter toutes les classes en relation
            Do Until pRelClass Is Nothing
                'Vérifier si le nom de la relation correspond à celle spécifiée
                If sNomRelation.ToUpper = pRelClass.ForwardPathLabel.ToUpper Then
                    'Indiquer que la destruction de relation s'est effectuée correctement
                    TrouverRelationShipTable = pRelClass

                    'Sortir de la boucle
                    Exit Do
                End If

                'Trouver la prochaine classe en relation 
                pRelClass = pEnumRelClass.Next
            Loop

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pRelClassColl = Nothing
            pEnumRelClass = Nothing
            pRelClass = Nothing
        End Try
    End Function
#End Region
End Module
