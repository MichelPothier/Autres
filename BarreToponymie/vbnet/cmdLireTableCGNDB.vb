Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.EditorExt
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.GeoDatabaseUI
Imports ESRI.ArcGIS.DataSourcesRaster
Imports System.IO

'**
'Nom de la composante : cmdLireTableBDG.vb
'
'''<summary>
''' Commande qui permet de lire la table des toponymes de la BDG.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 06 décembre 2016
'''</remarks>
''' 
Public Class cmdLireTableCGNDB
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    Public Sub New()
        'Définir les variables de travail

        Try
            'Par défaut la commande est inactive
            Enabled = False
            'Vérifier si l'application est définie
            If Not Hook Is Nothing Then
                'Définir l'application
                m_Application = CType(Hook, IApplication)

                'Vérifier si l'application est ArcMap
                If TypeOf Hook Is IMxApplication Then
                    'Définir le document
                    m_MxDocument = CType(m_Application.Document, IMxDocument)
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
        End Try
    End Sub

    Protected Overrides Sub OnClick()
        'Déclarer les variables de travail
        Dim pTrackCancel As ITrackCancel = Nothing                  'Interface qui permet d'annuler la sélection avec la touche ESC.
        Dim pMouseCursor As IMouseCursor = Nothing                  'Interface qui permet de changer le curseur de la souris.
        Dim iMsgBoxStyle As MsgBoxStyle = 0             'Indique le style du MsgBox utilisé.
        Dim qStartTime As DateTime = Nothing            'Date de départ.
        Dim qEndTime As DateTime = Nothing              'Date de fin.
        Dim qElapseTime As TimeSpan = Nothing           'Temps de traitement.

        Try
            'Initialiser le temps d'exécution
            qStartTime = DateTime.Now
            'Initialiser le style du MsgBox
            iMsgBoxStyle = MsgBoxStyle.Information

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si la table est valide
            If m_TableToponymeCGNDB.Table Is Nothing Then
                'Afficher un message d'erreur
                MsgBox("ERREUR : La table des toponymes CGNDB est invalide : " & m_TableToponymeCGNDB.Name)
                Exit Sub
            End If

            'Permettre d'annuler la sélection avec la touche ESC
            pTrackCancel = New CancelTracker
            pTrackCancel.CancelOnKeyPress = True
            pTrackCancel.CancelOnClick = False
            pTrackCancel.Progressor = m_Application.StatusBar.ProgressBar

            'Créer la liste des noms de toponyme CGNDB abrogé
            Call CreerListeNomToponymeAbroge(pTrackCancel)

            'Créer la liste des noms de toponyme CGNDB officiel
            Call CreerListeNomToponymeOfficiel(pTrackCancel)

            'Cacher la barre de progression
            pTrackCancel.Progressor.Hide()

            'Définir le temps d'exécution
            qEndTime = DateTime.Now
            qElapseTime = qEndTime.Subtract(qStartTime)

            'Afficher le résultat obtenu
            MsgBox("Lire les toponymes de la CGNDB :" & vbCrLf _
                   & "-Nombre de toponymes CGNDB officiels : " & m_ListeNomToponymeOfficiel.Count.ToString & vbCrLf _
                   & "-Nombre de toponymes CGNDB abrogés : " & m_ListeNomToponymeAbroge.Count.ToString & vbCrLf _
                   & "-Temps d'exécution : " & qElapseTime.ToString(), iMsgBoxStyle)

        Catch erreur As Exception
            'Vérifier si le traitement a été annulé
            If TypeOf (erreur) Is CancelException Then
                'Vérifier si la barre de progression est active
                If pTrackCancel IsNot Nothing Then
                    'Cacher la barre de progression
                    pTrackCancel.Progressor.Hide()
                    'Afficher le message
                    m_Application.StatusBar.Message(0) = erreur.Message
                End If
            Else
                'Message d'erreur
                MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
            End If

        Finally
            'Vider la mémoire
            pTrackCancel = Nothing
            pMouseCursor = Nothing
            iMsgBoxStyle = Nothing
            qStartTime = Nothing
            qEndTime = Nothing
            qElapseTime = Nothing
            'Récupération de la mémoire disponble
            GC.Collect()
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        'Rendre inactive par défaut
        Enabled = False

        'Vérifier si la table est valide
        If m_TableToponymeCGNDB IsNot Nothing Then
            'Vérifier si la table est valide
            If m_TableToponymeCGNDB.Table IsNot Nothing Then
                'Vérifier si l'attribut TOPONYMIC_FEATURE_ID est présent
                If m_TableToponymeCGNDB.Table.FindField("TOPONYMIC_FEATURE_ID") >= -1 Then
                    'Rendre active
                    Enabled = True
                End If
            End If
        End If
    End Sub
End Class
