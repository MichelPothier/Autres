Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.GeoDatabaseDistributed
Imports ESRI.ArcGIS.DataManagementTools
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Display

'**
'Nom de la composante : cmdCreerGdbEnfant.vb
'
'''<summary>
''' Commande qui permet de créer une Géodatabase Enfant et son archive à partir d'une géodatabase Parent en utilisant un réplica de type checkOut.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 16 janvier 2017
'''</remarks>
''' 
Public Class cmdCreerGdbEnfant
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
        Dim pGererReplica As clsGererReplica = Nothing      'Objet utilisé pour gérer un réplica de géodatabase.
        Dim pTrackCancel As ITrackCancel = Nothing          'Interface qui permet d'annuler la sélection avec la touche ESC.
        Dim sNomGdbParent As String = Nothing               'Nom de la Géodatabase parent.
        Dim sNomGdbEnfant As String = Nothing               'Nom de la Géodatabase enfant.
        Dim sListeClasses As String = Nothing               'Liste des noms de classe à extraire dans le réplica.
        Dim sListeIdentifiants As String = Nothing          'Liste des identifiants à extraire dans le réplica.
        Dim sNomReplica As String = Nothing                 'Nom du réplica traité.
        Dim sNoNC As String = Nothing                       'Numéro de non-conformité traité.
        Dim sMessage As String = Nothing                    'Message à retourner.
        Dim sPremierIdentifiant As String = ""              'Nom du premier identifiant de la liste des identifiants.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Définir le numéro de non-conformité
            sNoNC = m_MenuNonConformite.cboNonConformite.Text.Split(":".ToCharArray)(0)

            'Vérifier si les identifiants et les classes ne sont pas réservés et en production
            If Not m_GererNC.ReservationValide(sNoNC, m_MenuNonConformite.treIdentifiants, m_MenuNonConformite.treClasses) Then
                'Retourner une erreur de réservation
                Throw New AnnulerExecutionException("ERREUR: La réservation des identifiants et des classes est invalide!")
            End If

            'Vérifier si la note de création du réplica est présente pour les identifiants à traiter
            If m_GererNC.NoteReplicaPresente(sNoNC, m_MenuNonConformite.treIdentifiants, sMessage) Then
                'Retourner une erreur de réservation
                Throw New AnnulerExecutionException("ERREUR : " & sMessage)
            End If

            'Définir la liste des classes séparées par des virgules et sans apostrophe
            sListeClasses = m_GererNC.DefinirListeClasses(m_MenuNonConformite.treClasses)

            'Définir la liste des identifiants séparés par des virgules et apostrophes
            sListeIdentifiants = m_GererNC.DefinirListeIdentifiants(m_MenuNonConformite.treIdentifiants)

            'Définir le premier identifiant de la liste des identifiant
            sPremierIdentifiant = sListeIdentifiants.Split(CChar(","))(0)

            'Définir le nom du réplica à partir du numéro de non-conformité et des la liste des identifiants
            sNomReplica = "NC_" & sNoNC & "_" & sPremierIdentifiant.Replace("'", "")
            
            'Ajouter le nombre d'identifiants dans le nom du réplica
            sNomReplica = sNomReplica & "_" & m_NbIdentifiants.ToString

            'Définir le nom de la Géodatabase parent
            sNomGdbParent = m_MenuNonConformite.cboGeodatabaseParent.Text

            'Définir le nom de la géodatabase enfant à partir du numéro de non-conformité
            sNomGdbEnfant = m_MenuNonConformite.cboGeodatabaseEnfant.Text.Replace("[NC]", sNomReplica)

            'Créer un nouvel objet pour gérer un réplica
            pGererReplica = New clsGererReplica

            'Permettre d'afficher les messages et annnuler la progression au besoin
            pTrackCancel = New CancelTracker
            pTrackCancel.CancelOnKeyPress = True
            pTrackCancel.CancelOnClick = False
            pTrackCancel.Progressor = m_Application.StatusBar.ProgressBar
            pGererReplica.TrackCancel = pTrackCancel

            'Créer un réplica de type CheckOut pour une liste de classes et d'identifiants de la BDG
            pGererReplica.CreerReplicaBDG(sNomReplica, sNomGdbParent, sNomGdbEnfant, sListeClasses, sListeIdentifiants, "DATASET_NAME")

            'Ajouter la note de réplica pour tous les identifiants dans la table F502_PS
            Call m_GererNC.AjouterNoteReplica(sNomReplica, sNoNC, m_MenuNonConformite.treIdentifiants)

            'Ajouter les classes de la géodatabase enfant dans la Map active
            pGererReplica.AjouterClassesGdbEnfantMap(m_MxDocument.FocusMap)

            'Définir le réplica et le nom de la Géodatabase enfant via le ComboBox
            m_cboGeodatabaseEnfant.DefinirGdbEnfant(pGererReplica)

            'Sélectionner la page de description du réplica
            m_MenuNonConformite.tabMenuNonConformite.SelectTab(m_MenuNonConformite.tabReplica)

            'Définir le réplica
            m_GererReplica = pGererReplica

            'Remplir la description du replica de la Géodatabase enfant et parent
            m_GererReplica.DescriptionReplica(m_MenuNonConformite.treReplica)

        Catch ex As AnnulerExecutionException
            'Message d'erreur
            MsgBox(ex.Message)
        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pGererReplica = Nothing
            pTrackCancel = Nothing
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        'Vérifier si le nombre d'identifiants et de classes
        If m_NbIdentifiants = 0 Or m_NbClasses = 0 Then
            Enabled = False
        Else
            Enabled = True
        End If
    End Sub
End Class
