Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports System.Data.OleDb
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geometry

'**
'Nom de la composante : cboTableBDG.vb
'
'''<summary>
''' Commande qui permet de définir la table des toponymes de la BDG.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 06 décembre 2016
'''</remarks>
''' 
Public Class cboTableBDG
    Inherits ESRI.ArcGIS.Desktop.AddIns.ComboBox

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

                    'Définir le comboBox
                    m_cboTableBDG = Me

                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

        Catch erreur As Exception
            'Afficher un message d'erreur
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub

    Protected Overloads Overrides Sub OnFocus(ByVal focus As Boolean)
        Try
            'Remplir le ComboBox
            Call RemplirComboBox()

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

            'Définir la table 
            m_TableToponymeBDG = m_MapLayer.ExtraireStandaloneTableByName(CStr(Me.GetItem(cookie).Tag))

        Catch erreur As Exception
            'Afficher un message d'erreur
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        Me.Enabled = True
    End Sub

#Region "Routines et fonctions publiques"
    '''<summary>
    ''' Routine qui permet de remplir le ComboBox à partir des noms de table contenus dans la Map active.
    '''</summary>
    ''' 
    Public Sub RemplirComboBox()
        'Déclarer la variables de travail
        Dim pStandaloneTableColl As IStandaloneTableCollection  'Interface qui permet d'extraire les StandaloneTable de la Map
        Dim pStandaloneTable As IStandaloneTable = Nothing      'Interface contenant une classe de données
        Dim sNom As String = Nothing                    'Nom du FeatureLayer sélectionné
        Dim iDefaut As Integer = Nothing                'Index par défaut
        Dim i As Integer = Nothing                      'Compteur

        Try
            'Initialiser le nom de la table
            sNom = ""
            'Vérifier si la table est valide
            If m_TableToponymeBDG IsNot Nothing Then
                'Conserver la table sélectionnée
                sNom = m_TableToponymeBDG.Name
            End If
            'Effacer toutes les tables existantes
            Me.Clear()
            m_TableToponymeBDG = Nothing
            'Définir l'objet pour extraire les tables
            m_MapLayer = New clsGererMapLayer(m_MxDocument.FocusMap, True)
            'Définir la liste des StandaloneTable
            pStandaloneTableColl = CType(m_MxDocument.FocusMap, IStandaloneTableCollection)

            'Traiter tous les StandaloneTable
            For i = 0 To pStandaloneTableColl.StandaloneTableCount - 1
                'Définir le StandaloneTable
                pStandaloneTable = pStandaloneTableColl.StandaloneTable(i)
                'Vérifier si la classe contient l'attribut NAMEID
                If pStandaloneTable.Table.FindField("NAMEID") >= 0 Then
                    'Ajouter le FeatureLayer
                    iDefaut = Me.Add(pStandaloneTable.Name, pStandaloneTable.Name)
                    'Vérifier si le nom du FeatureLayer correspond à celui sélectionné
                    If pStandaloneTable.Name = sNom Then
                        'Sélectionné la valeur par défaut
                        Me.Select(iDefaut)
                    End If
                End If
                'Sélectionner le dernier si rien
                If Me.Value = "" And iDefaut > 0 Then Me.Select(iDefaut)
            Next

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pStandaloneTableColl = Nothing
            pStandaloneTable = Nothing
            sNom = Nothing
            i = Nothing
        End Try
    End Sub
#End Region
End Class
