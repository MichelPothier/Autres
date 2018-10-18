Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports System.Data.OleDb

'**
'Nom de la composante : cboTypeCatalogue.vb
'
'''<summary>
''' Commande qui permet de définir le type de catalogue utilisé pour afficher la description des valeurs d'attributs.
'''</summary>
'''
'''<remarks>
'''Ce traitement est utilisable en mode interactif à l'aide de ses interfaces graphiques et doit être
'''utilisé dans ArcMap (ArcGisESRI).
'''
'''Auteur : Michel Pothier
'''Date : 25 mars 2015
'''</remarks>
''' 
Public Class cboTypeCatalogue
    Inherits ESRI.ArcGIS.Desktop.AddIns.ComboBox

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap
    Dim giBDG As Integer                    'Numéro du catalogue BDG

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

                    'Ajouter le catalogue
                    Me.Add("MAIN", "MAIN")
                    'Ajouter le catalogue
                    giBDG = Me.Add("BDG", "BDG")
                    'Ajouter le catalogue
                    Me.Add("GEO", "GEO")
                    'Ajouter le catalogue
                    Me.Add("PROD", "PROD")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MAIN", "BDRS_MAIN")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT", "BDRS_MGT")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT_MISST_50K", "BDRS_MGT_MISST_50K")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT_MISST_250K", "BDRS_MGT_MISST_250K")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT_MISST_GE", "BDRS_MGT_MISST_GE")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT_MISST_ME", "BDRS_MGT_MISST_ME")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT_MISST_PE", "BDRS_MGT_MISST_PE")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT_MISST_Multi", "BDRS_MGT_MISST_Multi")
                    'Ajouter le catalogue
                    Me.Add("BDRS_EXPL_MISST_50K", "BDRS_EXPL_MISST_50K")
                    'Ajouter le catalogue
                    Me.Add("BDRS_EXPL_MISST_250K", "BDRS_EXPL_MISST_250K")
                    'Ajouter le catalogue
                    Me.Add("BDRS_EXPL_MISST_GE", "BDRS_EXPL_MISST_GE")
                    'Ajouter le catalogue
                    Me.Add("BDRS_EXPL_MISST_ME", "BDRS_EXPL_MISST_ME")
                    'Ajouter le catalogue
                    Me.Add("BDRS_EXPL_MISST_PE", "BDRS_EXPL_MISST_PE")
                    'Ajouter le catalogue
                    Me.Add("BDRS_EXPL_MISST_Multi", "BDRS_EXPL_MISST_Multi")
                    'Ajouter le catalogue
                    Me.Add("BDRS_MGT_ECSCF", "BDRS_MGT_ECSCF")

                    'Sélectionner le catalogue BDG par défaut
                    Me.Select(giBDG)

                Else
                    'Rendre désactive la commande
                    Enabled = False
                End If
            End If

        Catch erreur As Exception
            MsgBox(erreur.ToString)
        End Try
    End Sub

    Protected Overloads Overrides Sub OnSelChange(ByVal cookie As Integer)
        'Définir les variables de travail
        Dim sCatalogue As String            'Contient le nom du catalogue.

        Try
            'Si aucun n'est sélectionné
            If cookie = -1 Then
                'On ne fait rien
                Exit Sub
            End If

            'Vérifier si l'environnement du catalogue est spécifié
            If m_Catalogue IsNot Nothing Then
                'Définir la BD sélectionnée. 
                sCatalogue = CStr(Me.GetItem(cookie).Tag)

                'Définir le catalogue utilisé pour afficher la description des valeurs d'attributs
                m_Catalogue.NomCatalogue = sCatalogue
            End If

        Catch erreur As Exception
            MsgBox(erreur.ToString)
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        'Vérifier si l'environnement du catalogue est spécifié
        If m_Catalogue Is Nothing Then
            Me.Enabled = False
        Else
            Me.Enabled = True
        End If
    End Sub
End Class
