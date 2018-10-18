Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports System.Data.OleDb

'**
'Nom de la composante : cboAction.vb
'
'''<summary>
''' Commande qui permet de définir l'action à effectuer afin d'identifier les erreurs de toponymie.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 24 novembre 2016
'''</remarks>
''' 
Public Class cboAction
    Inherits ESRI.ArcGIS.Desktop.AddIns.ComboBox

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap

    Public Sub New()
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

                    'Définir la liste des actions
                    Me.Add(CStr("1:Unnecessary/Inutile"), CStr("1:Unnecessary/Inutile"))
                    Me.Add(CStr("2:Superimposed/Superpose"), CStr("2:Superimposed/Superpose"))
                    Me.Add(CStr("3:Rescinded/Abroge"), CStr("3:Rescinded/Abroge"))
                    Me.Add(CStr("4:Official/Officiel"), CStr("4:Official/Officiel"))
                    Me.Add(CStr("5:Multiple/Multiple"), CStr("5:Multiple/Multiple"))

                    'Définir l'action par défaut
                    Me.Value = "1:Unnecessary/Inutile"

                    'Définir les paramètres de l'action par défaut
                    m_Parametres = m_Precision.ToString("0.0#######")

                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

        Catch erreur As Exception
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub

    Protected Overloads Overrides Sub OnSelChange(ByVal cookie As Integer)
        Try
            'Si aucun n'est sélectionné
            If cookie = -1 Then
                'On ne fait rien
                Exit Sub
            End If

            'Définir l'action
            m_Action = CStr(Me.GetItem(cookie).Tag)

            'Définir les paramètres de l'action
            m_cboParametres.initParametres()

        Catch erreur As Exception
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub

    Protected Overloads Overrides Sub OnFocus(ByVal focus As Boolean)
        Try
            'Si le focus est perdu
            If Not focus Then
                'Définir les paramètres de la requête
                m_Parametres = Me.Value
                'Traiter tous les items de la collection. 
                For Each item As ESRI.ArcGIS.Desktop.AddIns.ComboBox.Item In Me.items
                    'Vérifier si la valeur est déjà présente
                    If Me.Value = item.Caption Then
                        'Sortir
                        Exit Sub
                    End If
                Next
                'Ajouter la valeur dans la liste des items
                Me.Add(Me.Value, Me.Value)
            End If

        Catch erreur As Exception
            'Afficher un message d'erreur
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        'Vérifier si le FeatureLayer de sélection est invalide
        If m_FeatureLayerBDG Is Nothing Then
            'Rendre désactive la commande
            Me.Enabled = False

            'Si le FeatureLayer de sélection est invalide
        Else
            'Rendre active la commande
            Me.Enabled = True
        End If
    End Sub
End Class
