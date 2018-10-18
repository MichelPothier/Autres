Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Carto

'**
'Nom de la composante : cmdAjouterLayerSelection.vb
'
'''<summary>
'''Commande qui permet de créer un nouveau « FeatureLayer » contenant seulement les éléments de la sélection 
'''de chacun des « FeatureLayers » visibles dans lesquels une sélection est présente. 
'''Les anciens « FeatureLayers » seront détruits. Seuls les éléments sélectionnés seront conservés dans les 
'''« FeatureLayers » peu importe s’ils contiennent ou non une liste d’identifiants d’éléments. 
'''Les requêtes attributives seront conservées dans chacun des « FeatureLayers » si présentes, mais pas les jointures. 
'''Les « FeatureLayers » non visibles ou n’ayant aucun élément de sélectionné ne seront pas affectés par ce traitement.
'''</summary>
'''
'''<remarks>
'''Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être
'''utilisé dans ArcMap (ArcGisESRI).
'''
'''Auteur : Michel Pothier
'''</remarks>
''' 
Public Class cmdAjouterSelectionLayer
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap

    Public Sub New()
        Try
            'Par défaut la commande est inactive
            Enabled = False
            'Vérifier si l'application est définie
            If Not Hook Is Nothing Then
                'Définir l'application
                gpApp = CType(Hook, IApplication)

                'Vérifier si l'application est ArcMap
                If TypeOf Hook Is IMxApplication Then
                    'Définir le document
                    gpMxDoc = CType(gpApp.Document, IMxDocument)
                    'Vérifier si au moins un élément est sélectionné
                    If gpMxDoc.FocusMap.SelectionCount > 0 Then
                        'Rendre active la commande
                        Enabled = True
                    End If
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MsgBox(erreur.ToString)
        End Try
    End Sub

    Protected Overrides Sub OnClick()
        'Déclarer les variables de travail
        Dim pFeaturelayer As IFeatureLayer = Nothing            'Interface contenant le FeatureLayer de sélection
        Dim pFeatureSelection As IFeatureSelection = Nothing    'Interface qui permet de vérifier la présence de sélection
        Dim pMapLayer As clsGererMapLayer = Nothing             'Objet qui permet de gérer la Map et ses layers
        Dim i As Integer = Nothing                              'Compteur

        Try
            'Définir le MapLayer et tous les FeatureLayer visibles
            pMapLayer = New clsGererMapLayer(gpMxDoc.FocusMap, True)

            'Traiter tous les Layers
            For i = 1 To pMapLayer.FeatureLayerCollection.Count
                'Interface pour vérifier la sélection
                pFeatureSelection = CType(pMapLayer.FeatureLayerCollection.Item(i), IFeatureSelection)

                'Vérifier la présence d'une sélection
                If pFeatureSelection.SelectionSet.Count > 0 Then
                    'Interface pour accéder au nom du FeatureLayer
                    pFeaturelayer = CType(pFeatureSelection, IFeatureLayer)

                    'Créer le FeatureLayer de sélection
                    pFeaturelayer = CreerLayerSelection(pFeaturelayer, pFeaturelayer.Name & "_" & m_Compteur.ToString)

                    'Compter le nombre de résultat
                    m_Compteur = m_Compteur + 1
                End If
            Next

            'Rafraîchier l'affichage
            m_MxDocument.ActiveView.Refresh()
            m_MxDocument.UpdateContents()

        Catch erreur As Exception
            'Message d'erreur
            MsgBox(erreur.ToString)
        Finally
            'Vider la mémoire
            pFeaturelayer = Nothing
            pFeatureSelection = Nothing
            pMapLayer = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        Try
            'Rendre désactive la commande
            Enabled = False
            'Vérifier si au moins un élément est sélectionné
            If gpMxDoc.FocusMap.SelectionCount > 0 Then
                'Rendre active la commande
                Enabled = True
            End If

        Catch erreur As Exception
            'Message d'erreur
            MsgBox(erreur.ToString)
        End Try
    End Sub
End Class
