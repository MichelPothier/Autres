Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI

'**
'Nom de la composante : cmdAnnulerReservation.vb
'
'''<summary>
'''Permet d'annuler la réservation des données de la Géodatabase SDE.
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
'''</remarks>
''' 
Public Class cmdAnnulerReservation
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    Public Sub New()
        Try
            'Vérifier si l'application est définie
            If Not Hook Is Nothing Then
                'Définir l'application
                m_Application = CType(Hook, IApplication)

                'Vérifier si l'application est ArcMap
                If TypeOf Hook Is IMxApplication Then
                    'Rendre active la commande
                    Enabled = True
                    'Définir le document
                    m_MxDocument = CType(m_Application.Document, IMxDocument)

                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
        End Try
    End Sub

    Protected Overrides Sub OnClick()
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris.
        Dim sNoNC As String = Nothing                       'Numéro de non-conformité traité.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Sélectionner la page des différences
            m_MenuNonConformite.tabMenuNonConformite.SelectTab(m_MenuNonConformite.tabIdentifiants)

            'Définir le numéro de non-conformité
            sNoNC = m_MenuNonConformite.cboNonConformite.Text.Split(":".ToCharArray)(0)

            'Annuler la réservation des données dans SIB
            m_GererNC.AnnulerReserverIdentifiantsClasses(sNoNC, m_MenuNonConformite.treIdentifiants)

        Catch ex As AnnulerExecutionException
            'Message d'erreur
            MsgBox(ex.Message)
        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        'Vérifier si le nombre d'identifiants et de classes
        If m_NbIdentifiants = 0 Then
            Enabled = False
        Else
            Enabled = True
        End If
    End Sub
End Class
