Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Geodatabase

'**
'Nom de la composante : cmdConflit.vb
'
'''<summary>
'''Permet d'identifier les conflits entre la Géodatabase SDE et la version de travail.
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
'''</remarks>
''' 
Public Class cmdConflit
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
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim sNomReplica As String = ""              'Nom du réplica contenu dans la description.
        Dim sNomGdbParent As String = ""            'Nom de la Géodatabase parent dans la quelle les données ont été extraites.
        Dim sNomGdbArchiveCopier As String = ""     'Nom de la Géodatabase d'archive à copier.
        Dim sListeNomClasse As String = ""          'Liste des classes pour lesquels on veut gérer les différences et les conflits.
        Dim sRequeteAttributive As String = ""      'Requête attributive utilisée pour extraire les données de la Géodatabase parent.
        Dim vMsgBoxResult As MsgBoxResult = Nothing 'Contient le résultat d'une question.
        Dim bExterne As Boolean = True              'Indiquer on doit identifier les conflits à partir de l'archive externe.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Sélectionner la page des conflits
            m_MenuNonConformite.tabMenuNonConformite.SelectTab(m_MenuNonConformite.tabConflits)

            'Vérifier si l'archive est externe à la Géodatabase enfant
            If m_GererReplica.DataChanges Is Nothing Then
                'Vérifier si la description du réplica enfant est absent
                If m_GererReplica.ReplicaEnfant Is Nothing Then
                    'Définir les valeurs par défaut
                    sNomReplica = IO.Path.GetFileNameWithoutExtension(m_GererReplica.GdbEnfant.PathName)
                    sRequeteAttributive = "DATASET_NAME='" & sNomReplica & "'"

                    'Définir les paramètres de la description d'un réplica
                    sNomReplica = InputBox("Quel est le nom du réplica ?", "Description du réplica de la Géodatabase enfant", sNomReplica)
                    If sNomReplica = "" Then Exit Try

                    sNomGdbParent = InputBox("Quel est le nom de la Géodatabase parent ?", "Description du réplica de la Géodatabase enfant", "Database Connections\BDRS_PRO_BDG_DBA.sde")
                    If sNomGdbParent = "" Then Exit Try

                    sNomGdbArchiveCopier = InputBox("Quel est le nom  de la Géodatabase d'archive ?", "Description du réplica de la Géodatabase enfant", m_GererReplica.GdbEnfant.PathName)
                    If sNomGdbArchiveCopier = "" Then Exit Try

                    sListeNomClasse = InputBox("Quel est la liste des classes pour lesquels on veut gérer les différences et les conflits ?", "Description du réplica de la Géodatabase enfant", "nhn_hnet_Network_Linear_Flow_1,nhn_hhyd_Waterbody_2")
                    If sListeNomClasse = "" Then Exit Try

                    sRequeteAttributive = InputBox("Quel est la requête attributive utilisée pour extraire les données de la Géodatabase parent ?", "Description du réplica de la Géodatabase enfant", sRequeteAttributive)
                    If sRequeteAttributive = "" Then Exit Try

                    'Créer une description de réplica avec archive externe dans la Géodatabase enfant
                    Call m_GererReplica.CreerDescriptionReplicaEnfant(sNomReplica, sNomGdbParent, sNomGdbArchiveCopier, sListeNomClasse, sRequeteAttributive)
                End If

                'Si l'archive est interne à la Géodatabase enfant
            Else
                'Indiquer on doit identifier les différences à partir de l'archive externe
                vMsgBoxResult = MsgBox("Désirez-vous utiliser l'archive externe ?", MsgBoxStyle.YesNoCancel, "Identifier les conflits")

                'Vérifier si on défire annuler le traitement
                If vMsgBoxResult = MsgBoxResult.Cancel Then Exit Sub

                'Définir si on doit utiliser l'archive externe
                bExterne = vMsgBoxResult = MsgBoxResult.Yes
            End If

            'Identifier les conflits entre la Géodatabase parent et l'archive de la Géodatabase enfant dans un TreeView
            m_GererReplica.IdentifierConflits(m_MenuNonConformite.treConflits, bExterne)
            'Définir le nombre de conflits
            m_NbConflits = m_GererReplica.NbConflits

            'Extraire la description du replica de la Géodatabase enfant et parent
            m_GererReplica.DescriptionReplica(m_MenuNonConformite.treReplica)

            'Afficher l'information du noeud sélectionné
            m_MenuNonConformite.AfficherInfoConflits(m_MenuNonConformite.treConflits.SelectedNode)

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
        If m_GererReplica Is Nothing Then
            Enabled = False
        ElseIf m_GererReplica.DataChanges Is Nothing Then
            Enabled = False
        Else
            Enabled = True
        End If
    End Sub
End Class
