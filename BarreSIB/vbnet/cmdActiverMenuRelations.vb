Imports System.Windows.Forms
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.esriSystem

'**
'Nom de la composante : cmdActiverMenuRelations.vb
'
'''<summary>
''' Commande qui permet d'activer le menu des relations afin de pouvoir montrer les relations entre toutes les tables
''' et pouvoir définir et afficher la requête attributive de la table sélectionnée.
'''</summary>
'''
'''<remarks>
'''Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être
'''utilisé dans ArcMap (ArcGisESRI).
'''
'''Auteur : Michel Pothier
'''Date : 14 juillet 2014
'''</remarks>
''' 
Public Class cmdActiverMenuRelations
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap

    Public Sub New()
        'Définir les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver ou créer un DockableWindow
        Dim pDockWindowRelations As IDockableWindow 'Interface contenant le DockableWindow

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

                    'Vérifier si le menu est inactif
                    If m_MenuRelations Is Nothing Then
                        'Créer un nouveau menu
                        windowID.Value = "MPO_BarreSIB_dckMenuRelations"
                        pDockWindowRelations = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
                        pDockWindowRelations.Show(False)
                    End If

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
            pDockWindowRelations = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnClick()
        Try
            'Sortir si le menu n'est pas créé
            If m_MenuRelations Is Nothing Then Return

            'Activer ou désactiver le menu
            m_MenuRelations.Show((Not m_MenuRelations.IsVisible()))
            Checked = m_MenuRelations.IsVisible()

            'Vérifier si le menu est visible
            If Checked Then
                'Identifier toutes les relations pour toutes les tables de la Map active
                m_MenuRelations.IdentifierMap(gpMxDoc.FocusMap)
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        Try
            Enabled = True
        Catch erreur As Exception
            MsgBox(erreur.ToString)
        End Try
    End Sub
End Class
