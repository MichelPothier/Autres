Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.esriSystem

'**
'Nom de la composante : cmdIdentifierSelection.vb
'
'''<summary>
'''Commande qui permet d'identifier les éléments sélectionnés en remplissant le menu d'identification.
'''</summary>
'''
'''<remarks>
'''Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être
'''utilisé dans ArcMap (ArcGisESRI).
'''
'''Auteur : Michel Pothier
'''</remarks>
''' 
Public Class cmdIdentifierSelection
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap

    Public Sub New()
        'Définir les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver ou créer un DockableWindow
        Dim pDockWindowIdentification As IDockableWindow 'Interface contenant le DockableWindow

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

                    'Vérifier si le menu d'identification est inactif
                    If m_MenuIdentification Is Nothing Then
                        'Créer un nouveau menu
                        windowID.Value = "MPO_BarreSIB_dckMenuIdentification"
                        pDockWindowIdentification = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
                        pDockWindowIdentification.Show(False)
                    End If
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MsgBox(erreur.ToString)
        Finally
            'Vider la mémoire
            windowID = Nothing
            pDockWindowIdentification = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnClick()
        Try
            'Identifier les éléments sélectionnés via le menu d'identification
            m_MenuIdentification.IdentifierMap(gpMxDoc.FocusMap)

            'Afficher le menu d'identification
            m_MenuIdentification.Show(True)

        Catch erreur As Exception
            'Message d'erreur
            MsgBox(erreur.ToString)
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
