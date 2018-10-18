Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.Carto

'**
'Nom de la composante : tooIdentifierEnveloppe.vb
'
'''<summary>
'''Commande qui permet d'identifier et sélectionner des éléments selon une enveloppe et de remplir le menu d'identification.
'''</summary>
'''
'''<remarks>
'''Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être
'''utilisé dans ArcMap (ArcGisESRI).
'''
'''Auteur : Michel Pothier
'''</remarks>
''' 
Public Class tooIdentifierEnveloppe
    Inherits ESRI.ArcGIS.Desktop.AddIns.Tool

    'Déclarer les variable de travail
    Private gpApp As IApplication
    Private gpMxDoc As IMxDocument
    Private mpPoint As IPoint
    Private mpFeedbackEnv As INewEnvelopeFeedback
    Private mbMouseDown As Boolean

    Public Sub New()
        'Définir les variables de travail
        Dim windowID As UID = New UIDClass

        Try
            'Vérifier si l'application est définie
            If Not Hook Is Nothing Then
                'Définir l'application
                gpApp = CType(Hook, IApplication)

                'Vérifier si l'application est ArcMap
                If TypeOf Hook Is IMxApplication Then
                    'Rendre active la commande
                    Enabled = True
                    'Définir le document
                    gpMxDoc = CType(gpApp.Document, IMxDocument)
                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MsgBox(erreur.ToString)
        Finally
            'Vider la mémoire
            windowID = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnMouseDown(ByVal arg As ESRI.ArcGIS.Desktop.AddIns.Tool.MouseEventArgs)
        'On ne fait rien si ce n'est pas le button gauche de la souris
        If arg.Button <> Windows.Forms.MouseButtons.Left Then Exit Sub

        Try
            'Transformer la position de la souris en postion de la map
            mpPoint = gpMxDoc.ActiveView.ScreenDisplay.DisplayTransformation.ToMapPoint(arg.X, arg.Y)

            'Conserver le point de la position actuelle de la souris et indiquer le début du traitement
            mbMouseDown = True

        Catch erreur As Exception
            MsgBox(erreur.ToString)
        Finally
            'Vider la mémoire
        End Try
    End Sub

    Protected Overrides Sub OnMouseMove(ByVal arg As ESRI.ArcGIS.Desktop.AddIns.Tool.MouseEventArgs)
        Try
            'Sortir si le traitement n'a pas été initialisé
            If mpPoint Is Nothing Or mbMouseDown = False Then Exit Sub

            'vérifier si l'enveloppe a été initialisée
            If (mpFeedbackEnv Is Nothing) Then
                'Créer l'enveloppe virtuelle initiale pour définir la zone d'affichage
                mpFeedbackEnv = New NewEnvelopeFeedback
                'Définir la fenêtre d'affichage
                mpFeedbackEnv.Display = gpMxDoc.ActiveView.ScreenDisplay
                'Initialiser le premier point de l'enveloppe virtuelle
                mpFeedbackEnv.Start(mpPoint)
            End If

            'Transformer la position de la souris en postion de la map
            mpPoint = gpMxDoc.ActiveView.ScreenDisplay.DisplayTransformation.ToMapPoint(arg.X, arg.Y)

            'Bouger l'enveloppe au point de la position actuelle de la souris
            mpFeedbackEnv.MoveTo(mpPoint)

        Catch erreur As Exception
            MsgBox(erreur.ToString)
        Finally
            'Vider la mémoire
        End Try
    End Sub

    Protected Overrides Sub OnMouseUp(ByVal arg As ESRI.ArcGIS.Desktop.AddIns.Tool.MouseEventArgs)
        'Déclarer les variables de travail
        Dim oRectangle As tagRECT                               'Contient le rectangle en pixel.
        Dim pEnvelope As IEnvelope = Nothing                    'Interface contenant l'enveloppe utilisé pour afficher les SNRCs
        Dim pPoint As IPoint = Nothing                          'Interface contenant le point de recherche du SNRC
        Dim pScreenDisplay As IScreenDisplay = Nothing          'Interface ESRI contenant la fenêtre d'affichage.
        Dim pSelectionEnv As ISelectionEnvironment = Nothing    'Interface pour définir l'environnement de sélection

        Try
            'Initialiser les variables de travail
            pScreenDisplay = gpMxDoc.ActiveView.ScreenDisplay

            'Créer un nouvel enviromment de sélection
            pSelectionEnv = New SelectionEnvironmentClass()

            'Si aucune enveloppe n'est captée, c'est un point qui est capté
            If mpFeedbackEnv Is Nothing Then
                'Sortir si aucun point n'a été défini
                If mpPoint Is Nothing Then
                    Exit Sub
                End If

                'Définir le rectangle en pixel
                oRectangle.left = arg.X - pSelectionEnv.SearchTolerance
                oRectangle.top = arg.Y - pSelectionEnv.SearchTolerance
                oRectangle.right = arg.X + pSelectionEnv.SearchTolerance
                oRectangle.bottom = arg.Y + pSelectionEnv.SearchTolerance
                'Transformer le rectangle en enveloppe '5 = esriTransformPosition + esriTransformToMap'.
                pEnvelope = New EnvelopeClass()
                gpMxDoc.ActiveView.ScreenDisplay.DisplayTransformation.TransformRect(pEnvelope, oRectangle, 5)

                'Si c'est une enveloppe qui est captée
            Else
                'Définir l'enveloppe d'affichage
                pEnvelope = mpFeedbackEnv.Stop

                'Il faut que l'enveloppe soit dans la même projection que le projet.  
                'On peut utiliser la référence spatiale du point de départ.
                pEnvelope.SpatialReference = mpPoint.SpatialReference
            End If
            'Vérifier si Le shift ou le ctl est présent
            If arg.Shift = True Then
                'Ajouter la sélection
                pSelectionEnv.CombinationMethod = esriSelectionResultEnum.esriSelectionResultAdd
            ElseIf arg.Control = True Then
                'Ajouter ou enlever la sélection
                pSelectionEnv.CombinationMethod = esriSelectionResultEnum.esriSelectionResultXOR
            Else
                'Créer une nouvelle sélection
                pSelectionEnv.CombinationMethod = esriSelectionResultEnum.esriSelectionResultNew
            End If

            'Sélectionner les éléments selon l'enveloppe et l'environnement de sélection
            gpMxDoc.FocusMap.SelectByShape(pEnvelope, pSelectionEnv, False)

            'Identifier les éléments sélectionnés via le menu d'identification
            m_MenuIdentification.IdentifierMap(gpMxDoc.FocusMap)

            'Afficher le menu d'identification
            'm_DockWindowIdentification.Show(True)
            m_MenuIdentification.Show(True)

            'Vérifier le nombre d'élément sélectionné
            If gpMxDoc.FocusMap.SelectionCount = 0 Then
                'Rafraîchier l'affichage complet
                m_MxDocument.ActiveView.Refresh()
            Else
                'Affichage de la sélection
                gpMxDoc.ActiveView.PartialRefresh(esriViewDrawPhase.esriViewGeoSelection, Nothing, gpMxDoc.ActiveView.Extent)
            End If

        Catch erreur As Exception
            'Message d'erreur
            MsgBox(erreur.ToString)
        Finally
            'Réinitialiser les variables globales
            mbMouseDown = False
            mpFeedbackEnv = Nothing
            mpPoint = Nothing
            'Vider la mémoire
            oRectangle = Nothing
            pEnvelope = Nothing
            pPoint = Nothing
            pScreenDisplay = Nothing
            pSelectionEnv = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        Try
            'La commande est toujours active
            Enabled = True

        Catch erreur As Exception
            MsgBox(erreur.ToString)
        End Try
    End Sub
End Class
