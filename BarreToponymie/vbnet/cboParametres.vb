Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports System.Data.OleDb
Imports System.Windows.Forms

'**
'Nom de la composante : cboParametres.vb
'
'''<summary>
''' Commande qui permet de définir les paramètres de l'action à traiter sur les éléments de toponymie.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 24 novembre 2016
'''</remarks>
''' 
Public Class cboParametres
    Inherits ESRI.ArcGIS.Desktop.AddIns.ComboBox

    'Déclarer les variables de travail
    Dim gsAction As String = ""             'Nom de la dernière action.

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

                    'Définir la liste des paramètres
                    Me.Add(CStr(m_Parametres), CStr(m_Parametres))

                    'Définir le paramètre par défaut
                    Me.Value = m_Parametres

                    'Vérifier si la valeur du paramètre est numérique
                    If IsNumeric(m_Parametres) Then
                        'Définir la précision
                        m_Precision = CDbl(m_Parametres)
                    End If

                    'Définir le comboBox des paramètres
                    m_cboParametres = Me

                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

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
                'Vérifier si la valeur du paramètre est numérique
                If IsNumeric(m_Parametres) Then
                    'Définir la précision
                    m_Precision = CDbl(m_Parametres)
                End If
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

    Protected Overloads Overrides Sub OnSelChange(ByVal cookie As Integer)
        Try
            'Si aucun n'est sélectionné
            If cookie = -1 Then
                'On ne fait rien
                Exit Sub
            End If

            'Définir les paramètres de la requête
            m_Parametres = CStr(Me.GetItem(cookie).Tag)

            'Vérifier si la valeur du paramètre est numérique
            If IsNumeric(m_Parametres) Then
                'Définir la précision
                m_Precision = CDbl(m_Parametres)
            End If

        Catch erreur As Exception
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

    '''<summary>
    ''' Routine qui permet d'initialiser la liste des paramètres possibles et sélectionner le premier par défaut.
    ''' 
    '''</summary>
    '''
    Public Sub initParametres()
        Try
            'Vérifier si la requête a changé
            If m_Action <> gsAction Then
                'Vider la liste des paramètres
                Me.Clear()

                'Ajouter la valeur dans la liste des items
                Me.Add(m_Precision.ToString("0.0#######"), m_Precision.ToString("0.0#######"))

                'Définir le premier paramètre par défaut
                Me.Value = CStr(m_Precision.ToString("0.0#######"))

                'Définir la valeur des paramètres
                m_Parametres = Me.Value

                'Vérifier si la valeur du paramètre est numérique
                If IsNumeric(m_Parametres) Then
                    'Définir la précision
                    m_Precision = CDbl(m_Parametres)
                End If

                'Conserver le nom de l'action
                gsAction = m_Action
            End If

        Catch erreur As Exception
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub
End Class
