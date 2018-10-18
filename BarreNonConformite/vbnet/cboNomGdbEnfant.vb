Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports System.Data.OleDb
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.DataSourcesGDB
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Display

'**
'Nom de la composante : cboNomGdbEnfant.vb
'
'''<summary>
''' Commande qui permet de définir la Géodatabase-Enfant (.mdb/.gdb) contenant les données retirées à modifier et à retourner dans la Géodatabase-Parent (.sde).
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 17 janvier 2017
'''</remarks>
''' 
Public Class cboNomGdbEnfant
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

                    'Définir le ComboBox
                    m_cboGeodatabaseEnfant = Me

                    'Remplir le ComboBox
                    Call RemplirComboBox()

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

    Protected Overrides Sub Finalize()
        MyBase.Finalize()
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
        'Déclarer les variables de travail
        Dim pGererReplica As clsGererReplica = Nothing  'Objet qui permet de gérer un réplica de Géodatabase enfant.
        Dim pTrackCancel As ITrackCancel = Nothing      'Interface qui permet d'annuler la sélection avec la touche ESC.
        Dim pMouseCursor As IMouseCursor = Nothing      'Interface qui permet de changer le curseur de la souris.

        Try
            'Si aucun n'est sélectionné
            If cookie = -1 Or Me.Value.Length = 0 Then
                'On ne fait rien
                Exit Sub
            End If

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si aucune géodatabase n'est présente
            If Me.Value <> "-" Then
                'Créer l'objet pour gérer le réplica
                pGererReplica = New clsGererReplica

                'Définir la géodatabase enfant
                pGererReplica.Init(CStr(Me.GetItem(cookie).Tag))

                'Définir la barre de progression
                'm_Application.StatusBar.ProgressBar.Position = 0
                'm_Application.StatusBar.ShowProgressBar("Traitement en cours ...", 0, 1, 1, True)

                'Permettre d'annuler la sélection avec la touche ESC
                pTrackCancel = New CancelTracker
                pTrackCancel.CancelOnKeyPress = True
                pTrackCancel.CancelOnClick = False
                pTrackCancel.Progressor = m_Application.StatusBar.ProgressBar
                pGererReplica.TrackCancel = pTrackCancel

                'Initialiser le menu pour l'information du réplica
                m_MenuNonConformite.InitialiserReplica()

                'Définir le réplica de la Géodatabase enfant
                m_GererReplica = pGererReplica

                'Extraire la description du replica de la Géodatabase enfant et parent
                m_GererReplica.DescriptionReplica(m_MenuNonConformite.treReplica)

                's'il faut enlever la Géodatabse sélectionné
            Else
                'Initialiser le menu pour l'information du réplica
                m_MenuNonConformite.InitialiserReplica()
            End If

        Catch erreur As Exception
            'Afficher un message d'erreur
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pGererReplica = Nothing
            pTrackCancel = Nothing
            'Récupérer la mémoire
            GC.Collect()
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        Me.Enabled = True
    End Sub

    '''<summary>
    ''' Routine qui permet d'initialiser le comboBox.
    '''</summary>
    ''' 
    Public Sub Init()
        'Effacer toutes les Géodatabases existantes
        Me.Clear()
    End Sub

    '''<summary>
    ''' Routine qui permet de définir le réplica de la Géodatabase enfant.
    '''</summary>
    ''' 
    Public Sub DefinirGdbEnfant(ByVal pGererReplica As clsGererReplica)
        'Déclarer les variables de travail
        Dim sMessage As String = ""     'Message d'erreurs

        Try
            'Vérifier si le réplica est valide
            If pGererReplica.EstValide(sMessage) Then
                'Conserver le réplica valide
                m_GererReplica = pGererReplica

                'Définir le nom complet de la Géodabase enfant
                Me.Value = m_GererReplica.GdbEnfant.PathName

                'Initialiser les compteur de conflits et de différences
                m_NbConflits = -1
                m_NbDifferences = -1

                'Si le réplica est invalide
            Else
                'Retourner l'erreur
                Throw New Exception(sMessage)
            End If

        Catch erreur As Exception
            'Afficher un message d'erreur
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de remplir le ComboBox à partir des noms de Géodatabase contenus dans la Map active.
    '''</summary>
    ''' 
    Public Sub RemplirComboBox()
        'Déclarer la variables de travail
        Dim qMapLayer As clsGererMapLayer = Nothing     'Objet utilisé pour extraire les Géodatabases.
        Dim qGdbColl As Collection = Nothing            'Object contenant la liste des Géodatabases
        Dim pWorkspace As IWorkspace = Nothing          'Interface contenant la Géodatabase.
        Dim sNom As String = Nothing                    'Nom du FeatureLayer sélectionné.
        Dim iDefaut As Integer = -1                     'Index par défaut.
        Dim bPresent As Boolean = Nothing               'Indique si l'item est présent.

        Try
            'Initialiser le nom du FeatureLayer
            sNom = Me.Value

            'Effacer toutes les Géodatabases existantes
            Me.Clear()

            'Définir l'objet pour extraire les Géodatabases
            qMapLayer = New clsGererMapLayer(m_MxDocument.FocusMap, True, esriGeometryType.esriGeometryAny, esriWorkspaceType.esriLocalDatabaseWorkspace)

            'Définir la collection des Géodatabase
            qGdbColl = qMapLayer.GeodatabaseCollection

            'Traiter toutes les Géodatabases
            For i = 1 To qGdbColl.Count
                'Interface contenant la Géodatabase
                pWorkspace = CType(qGdbColl.Item(i), IWorkspace)

                'Vérifier si C'est une Géodatabase local
                If pWorkspace.Type = esriWorkspaceType.esriLocalDatabaseWorkspace Then
                    'L'item est absent par défaut
                    bPresent = False
                    'Vérifier si la géodatabae est présente
                    For j = 0 To Me.items.Count - 1
                        'Vérifier
                        If Me.items.Item(j).ToString = pWorkspace.PathName Then
                            'L'item est présent
                            bPresent = True
                            'Sortir de la boucle
                            Exit For
                        End If
                    Next

                    'Si l'item est absent
                    If Not bPresent Then
                        'Vérifier si le nom de la Géodatabase correspond à celui sélectionné
                        If pWorkspace.PathName = sNom Then
                            'Ajouter la Géodatabase
                            iDefaut = Me.Add(pWorkspace.PathName, pWorkspace.PathName)
                        Else
                            'Ajouter la Géodatabase
                            Me.Add(pWorkspace.PathName, pWorkspace.PathName)
                        End If
                    End If
                End If
            Next

            'Ajouter le choix pour enlever
            Me.Add("-")

            'Si aucun n'est sélectionné
            If Me.Value = "" And iDefaut <> -1 Then
                'Sélectionné la valeur par défaut
                Me.Select(iDefaut)
            End If

        Catch erreur As Exception
            'Afficher un message d'erreur
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            qMapLayer = Nothing
            qGdbColl = Nothing
            pWorkspace = Nothing
            sNom = Nothing
            iDefaut = Nothing
            bPresent = Nothing
        End Try
    End Sub
End Class
