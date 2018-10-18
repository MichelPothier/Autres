Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.esriSystem

'**
'Nom de la composante : cmdCorriger 
'
'''<summary>
''' Commande qui permet de corriger les erreurs de toponimie selon la décision spécifiée dans l'erreur.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 24 novembre 2016
'''</remarks>
Public Class cmdCorriger
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    'Déclarer les variables globale de travail
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

                    'Conserver le document
                    m_MxDocument = gpMxDoc
                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

        Catch erreur As Exception
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
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
        Dim iNbSnrcProduction As Integer = 0            'Nombre de SNRC en production.
        Dim iNbToponymeBDG As Integer = 0               'Nombre de toponyme BDG.
        Dim iNbToponymeOfficiel As Integer = 0          'Nombre de toponyme officiel.

        Try
            'Initialiser le temps d'exécution
            qStartTime = DateTime.Now
            'Initialiser le style du MsgBox
            iMsgBoxStyle = MsgBoxStyle.Information

            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si la Featureclass est valide
            If m_FeatureLayerBDG.FeatureClass Is Nothing Then
                'Afficher un message d'erreur
                MsgBox("ERREUR : La FeatureClass de toponymie est invalide : " & m_FeatureLayerBDG.Name)
                Exit Sub
            End If

            'Permettre d'annuler la sélection avec la touche ESC
            pTrackCancel = New CancelTracker
            pTrackCancel.CancelOnKeyPress = True
            pTrackCancel.CancelOnClick = False
            pTrackCancel.Progressor = m_Application.StatusBar.ProgressBar

            'Initialiser le nombre d'éléments
            m_NbElements = 0
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0

            'Corriger les erreurs de toponymie
            Call CorrigerErreursToponymie(pTrackCancel)

            'Cacher la barre de progression
            pTrackCancel.Progressor.Hide()

            'Définir le temps d'exécution
            qEndTime = DateTime.Now
            qElapseTime = qEndTime.Subtract(qStartTime)

            'Vérifier si la liste des Snrc en production est valide
            If m_ListeNomToponymeBDG IsNot Nothing Then
                'Définir le nombre de Snrc en production
                iNbSnrcProduction = m_ListeSnrcProduction.Count
            End If

            'Vérifier si la liste des toponymes BDG est valide
            If m_ListeNomToponymeBDG IsNot Nothing Then
                'Définir le nombre de toponyme BDG
                iNbToponymeBDG = m_ListeNomToponymeBDG.Count
            End If

            'Vérifier si la liste des toponymes Officiel est valide
            If m_ListeNomToponymeBDG IsNot Nothing Then
                'Définir le nombre de toponyme Officiel
                iNbToponymeOfficiel = m_ListeNomToponymeOfficiel.Count
            End If

            'Afficher le résultat obtenu
            MsgBox("Corriger les erreurs de toponymie :" & vbCrLf _
                   & "-Nombre de Snrc en production : " & iNbSnrcProduction.ToString & vbCrLf _
                   & "-Nombre de toponymes BDG : " & iNbToponymeBDG.ToString & vbCrLf _
                   & "-Nombre de toponymes CGNDB officiels : " & iNbToponymeOfficiel.ToString & vbCrLf _
                   & "-Nombre d'éléments traités : " & m_NbElements.ToString & vbCrLf _
                   & "-Nombre de corrections effectuées : " & m_NbCorrections.ToString & vbCrLf _
                   & "-Nombre d'erreurs trouvées : " & m_NbErreurs.ToString & vbCrLf _
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
        Try
            'Rendre inactive par défaut
            Enabled = False

            'Vérifier si leLayer d'erreur est valide
            If m_FeatureLayerErreur IsNot Nothing And m_TableToponymeBDG IsNot Nothing And m_TableToponymeCGNDB IsNot Nothing Then
                'Vérifier si la classe est valide
                If m_FeatureLayerErreur.FeatureClass IsNot Nothing Then
                    'Vérifier si l'attribut LINK_TOPO est présent
                    If m_FeatureLayerErreur.FeatureClass.FindField("LINK_TOPO") >= 0 Then
                        'Rendre active
                        Enabled = True
                    End If
                End If
            End If

        Catch ex As Exception
            'On ne fait rien
        End Try
    End Sub
End Class

