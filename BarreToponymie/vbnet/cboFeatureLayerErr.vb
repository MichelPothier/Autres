﻿Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports System.Data.OleDb
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geometry

'**
'Nom de la composante : cboFeatureLayerErr.vb
'
'''<summary>
''' Commande qui permet de définir le FeatureLayer contenant les erreurs de toponymie BDG de type point à traiter.
'''</summary>
'''
'''<remarks>
''' Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être utilisé dans ArcMap (ArcGisESRI).
'''
''' Auteur : Michel Pothier
''' Date : 06 décembre 2016
'''</remarks>
''' 
Public Class cboFeatureLayerErr
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
                    m_cboFeatureLayerErr = Me

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

            'Définir le FeatureLayer de sélection. 
            m_FeatureLayerErreur = m_MapLayer.ExtraireFeatureLayerByName(CStr(Me.GetItem(cookie).Tag), True)

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
    ''' Routine qui permet de remplir le ComboBox à partir des noms de FeatureLayer contenus dans la Map active.
    '''</summary>
    ''' 
    Public Sub RemplirComboBox()
        'Déclarer la variables de travail
        Dim qFeatureLayerColl As Collection = Nothing   'Contient la liste des FeatureLayer visibles
        Dim pFeatureLayer As IFeatureLayer = Nothing    'Interface contenant une classe de données
        Dim sNom As String = Nothing                    'Nom du FeatureLayer sélectionné
        Dim iDefaut As Integer = Nothing                'Index par défaut
        Dim i As Integer = Nothing                      'Compteur

        Try
            'Initialiser le nom du FeatureLayer
            sNom = ""
            'Vérifier si le FeatureLayer est valide
            If m_FeatureLayerErreur IsNot Nothing Then
                'Conserver le FeatureLayer sélectionné
                sNom = m_FeatureLayerErreur.Name
            End If
            'Effacer tous les FeatureLayer existants
            Me.Clear()
            m_FeatureLayerErreur = Nothing
            'Définir l'objet pour extraire les FeatureLayer
            m_MapLayer = New clsGererMapLayer(m_MxDocument.FocusMap, True)
            'Définir la liste des FeatureLayer
            qFeatureLayerColl = m_MapLayer.DefinirCollectionFeatureLayer(True, esriGeometryType.esriGeometryPoint)
            'Vérifier si les FeatureLayers sont présents
            If qFeatureLayerColl IsNot Nothing Then
                'Traiter tous les FeatureLayer
                For i = 1 To qFeatureLayerColl.Count
                    'Définir le FeatureLayer
                    pFeatureLayer = CType(qFeatureLayerColl.Item(i), IFeatureLayer)
                    'Vérifier si la classe contient l'attribut LINK_TOPO
                    If pFeatureLayer.FeatureClass.FindField("LINK_TOPO") >= 0 Then
                        'Ajouter le FeatureLayer
                        iDefaut = Me.Add(pFeatureLayer.Name, pFeatureLayer.Name)
                        'Vérifier si le nom du FeatureLayer correspond à celui sélectionné
                        If pFeatureLayer.Name = sNom Then
                            'Sélectionné la valeur par défaut
                            Me.Select(iDefaut)
                        End If
                    End If
                Next
                'Sélectionner le dernier si rien
                If Me.Value = "" And iDefaut > 0 Then Me.Select(iDefaut)
            End If

        Catch erreur As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            qFeatureLayerColl = Nothing
            pFeatureLayer = Nothing
        End Try
    End Sub
#End Region
End Class
