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
'Nom de la composante : cmdExecuter.vb
'
'''<summary>
''' Commande qui permet d'exécuter l'action pour identifier les erreurs dans les éléments de toponymie.
''' 
''' Seuls les éléments sélectionnés sont traités.
''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 24 novembre 2016
'''</remarks>
''' 
Public Class cmdExecuter
    Inherits ESRI.ArcGIS.Desktop.AddIns.Button

    'Déclarer les variables de travail

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
        Dim pSpatialRef As ISpatialReference = Nothing              'Interface contenant la référence spatiale.
        Dim pSpatialRefFact As ISpatialReferenceFactory2 = Nothing  'Interface pour extraire une référence spatiale existante.
        Dim pSpatialRefRes As ISpatialReferenceResolution = Nothing 'Interface qui permet d'initialiser la résolution XY.
        Dim pSpatialRefTol As ISpatialReferenceTolerance = Nothing  'Interface qui permet d'initialiser la tolérance XY.
        Dim pTrackCancel As ITrackCancel = Nothing                  'Interface qui permet d'annuler la sélection avec la touche ESC.
        Dim pMouseCursor As IMouseCursor = Nothing                  'Interface qui permet de changer le curseur de la souris.
        Dim iMsgBoxStyle As MsgBoxStyle = 0             'Indique le style du MsgBox utilisé.
        Dim qStartTime As DateTime = Nothing            'Date de départ.
        Dim qEndTime As DateTime = Nothing              'Date de fin.
        Dim qElapseTime As TimeSpan = Nothing           'Temps de traitement.
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

            'Interface pour extraire la référence spatiale
            pSpatialRefFact = New SpatialReferenceEnvironment
            'Définir la référence spatiale LCC NAD83 CSRS:3979
            pSpatialRef = pSpatialRefFact.CreateSpatialReference(3979)
            'Définir la résolution XY
            pSpatialRefRes = CType(pSpatialRef, ISpatialReferenceResolution)
            pSpatialRefRes.SetDefaultXYResolution()
            'Définir la tolérance XY
            pSpatialRefTol = CType(pSpatialRef, ISpatialReferenceTolerance)
            pSpatialRefTol.XYTolerance = m_Precision

            'Initialiser le nombre d'éléments
            m_NbElements = 0
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0

            'Si l'action est "1:Unnecessary/Inutile"
            If m_Action.Contains("1:") Then
                'Exécuter l'action spécifiée
                Call TraiterToponymeInutile(pTrackCancel)

                'Si l'action est "2:Superimposed/Superpose"
            ElseIf m_Action.Contains("2:") Then
                'Exécuter l'action spécifiée
                Call TraiterToponymeSuperpose(pTrackCancel, pSpatialRef)

                'Si l'action est "3:Rescinded/Abroge"
            ElseIf m_Action.Contains("3:") Then
                'Exécuter l'action spécifiée
                Call TraiterToponymeAbroge(pTrackCancel)

                'Si l'action est "4:Official/Officiel"
            ElseIf m_Action.Contains("4:") Then
                'Exécuter l'action spécifiée
                Call TraiterToponymeOfficiel(pTrackCancel)

                'Si l'action est "5:Multiple/Multiple"
            ElseIf m_Action.Contains("5:") Then
                'Exécuter l'action spécifiée
                Call TraiterToponymeMultiple(pTrackCancel)
            End If

            'Cacher la barre de progression
            pTrackCancel.Progressor.Hide()

            'Vérifier si le fichier d'erreur est présent
            If m_FeatureClassErreur IsNot Nothing Then
                'Ajouter le FeatureLayer d'erreurs dans la Map active
                m_FeatureLayerErreur = New FeatureLayer
                m_FeatureLayerErreur.FeatureClass = m_FeatureClassErreur
                m_FeatureLayerErreur.Name = m_FeatureClassErreur.AliasName
                m_MxDocument.FocusMap.AddLayer(m_FeatureLayerErreur)
            End If

            'Définir le temps d'exécution
            qEndTime = DateTime.Now
            qElapseTime = qEndTime.Subtract(qStartTime)

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
            MsgBox(m_Action & vbCrLf _
                   & "-Référence spatiale : " & pSpatialRef.FactoryCode.ToString & ":" & pSpatialRef.Name & vbCrLf _
                   & "-Précision de la référence spatiale : " & pSpatialRefTol.XYTolerance.ToString("0.0#######") & vbCrLf _
                   & "-Nombre de toponymes BDG : " & iNbToponymeBDG.ToString & vbCrLf _
                   & "-Nombre de toponymes CGNDB officiels : " & iNbToponymeBDG.ToString & vbCrLf _
                   & "-Nombre d'éléments traités : " & m_NbElements.ToString & vbCrLf _
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
            pSpatialRef = Nothing
            pSpatialRefFact = Nothing
            pSpatialRefRes = Nothing
            pSpatialRefTol = Nothing
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

        'Vérifier si leLayer est valide
        If m_FeatureLayerBDG IsNot Nothing And m_TableToponymeBDG IsNot Nothing And m_TableToponymeCGNDB IsNot Nothing Then
            'Vérifier si la classe est valide
            If m_FeatureLayerBDG.FeatureClass IsNot Nothing Then
                'Vérifier si l'attribut NAMEID est présent
                If m_FeatureLayerBDG.FeatureClass.FindField("NAMEID") >= -1 Then
                    'Rendre active
                    Enabled = True
                End If
            End If
        End If
    End Sub
End Class
