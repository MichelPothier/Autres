Imports System.Windows.Forms
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.esriSystem

'**
'Nom de la composante : cmdConnecterSIB.vb
'
'''<summary>
''' Commande qui permet de se connecter à SIB afin de pouvoir utiliser tous les outils reliés à SIB.
'''</summary>
'''
'''<remarks>
'''Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être
'''utilisé dans ArcMap (ArcGisESRI).
'''
'''Auteur : Michel Pothier
'''Date : 27 août 2014
'''</remarks>
''' 
Public Class cmdConnecterSIB
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap

    Public Sub New()
        'Définir les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver ou créer un DockableWindow
        Dim pDockWindowConnexion As IDockableWindow 'Interface contenant le DockableWindow

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

                    'Vérifier si le menu de Connexion est inactif
                    If m_MenuConnexion Is Nothing Then
                        'Créer un nouveau menu
                        windowID.Value = "MPO_BarreSIB_dckMenuConnexion"
                        pDockWindowConnexion = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
                        pDockWindowConnexion.Show(False)
                    End If

                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

        Catch erreur As Exception
            MsgBox(erreur.ToString)
        Finally
            'Vider la mémoire
            windowID = Nothing
            pDockWindowConnexion = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnClick()
        Try
            'Sortir si le menu n'est pas créé
            If m_MenuConnexion Is Nothing Then Return

            'Activer ou désactiver le menu
            m_MenuConnexion.Show((Not m_MenuConnexion.IsVisible()))
            Checked = m_MenuConnexion.IsVisible()

            'Dim sNom As String = Nothing
            'sNom = Environment.GetEnvironmentVariable("nom")

            'My.Settings.Reload()
            ''My.Settings.username = "mpothier"
            'MessageBox.Show(My.Settings.username, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
            ''My.Settings.password = "12345"
            'MessageBox.Show(My.Settings.password, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
            ''My.Settings.environment = "PRO"
            'MessageBox.Show(My.Settings.environment, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
            'My.Settings.Save()

            'Environment.SetEnvironmentVariable("nom", "Linda")

        Catch erreur As Exception
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
