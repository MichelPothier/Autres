﻿Imports System.Windows.Forms
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.esriSystem

'**
'Nom de la composante : cmdActiverMenuIdentification.vb
'
'''<summary>
''' Commande qui permet d'activer le menu d'identification des éléments sélectionnés 
''' afin de pouvoir montrer leurs attributs et les divers liens avec d'autres tables 
''' et leurs attributs via les relations.
'''</summary>
'''
'''<remarks>
'''Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être
'''utilisé dans ArcMap (ArcGisESRI).
'''
'''Auteur : Michel Pothier
'''Date : 20 novembre 2013
'''</remarks>
''' 
Public Class cmdActiverMenuIdentification
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap

    Public Sub New()
        'Définir les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver ou créer un DockableWindow
        Dim pDockWindowIdentification As IDockableWindow 'Interface contenant le DockableWindow

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

                    'Vérifier si le menu d'identification est inactif
                    If m_MenuIdentification Is Nothing Then
                        'Créer un nouveau menu
                        windowID.Value = "MPO_BarreSIB_dckMenuIdentification"
                        pDockWindowIdentification = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
                        pDockWindowIdentification.Show(False)
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
            pDockWindowIdentification = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnClick()
        Try
            'Sortir si le menu n'est pas créé
            If m_MenuIdentification Is Nothing Then Return

            'Activer ou désactiver le menu
            m_MenuIdentification.Show((Not m_MenuIdentification.IsVisible()))
            Checked = m_MenuIdentification.IsVisible()

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
