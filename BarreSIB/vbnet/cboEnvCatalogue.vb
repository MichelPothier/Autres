Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports System.Data.OleDb

'**
'Nom de la composante : cboEnvCatalogue.vb
'
'''<summary>
''' Commande qui permet de définir l'environnement de travail (instance) de la base de données des catalogues 
''' utilisé pour afficher la description des valeurs d'attributs.
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
Public Class cboEnvCatalogue
    Inherits ESRI.ArcGIS.Desktop.AddIns.ComboBox

    'Déclarer les variables de travail
    Dim gpApp As IApplication = Nothing     'Interface ESRI contenant l'application ArcMap
    Dim gpMxDoc As IMxDocument = Nothing    'Interface ESRI contenant un document ArcMap
    Dim giNone As Integer                   'Numéro pour indiquer qu'aucun environnement n'est sélectionné
    Dim giPro As Integer                    'Numéro pour indiquer que l'environnement est CATREL_PRO
    Dim giTst As Integer                    'Numéro pour indiquer que l'environnement est CATREL_TST

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

                    'Ajouter la déconnexion à la BD
                    giNone = Me.Add("", "")

                    'Ajouter l'environnement CATREL_PRO
                    giPro = Me.Add("CATREL_PRO", "CATREL_PRO")

                    'Ajouter l'environnement CATREL_TST
                    giTst = Me.Add("CATREL_TST", "CATREL_TST")

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
        Dim sEnv As String                  'Contient le nom de l'environnement de travail (instance de la BD).

        Try
            'Si aucun n'est sélectionné
            If cookie = -1 Then
                'On ne fait rien
                Exit Sub
            End If

            'Définir la BD sélectionnée. 
            sEnv = CStr(Me.GetItem(cookie).Tag)

            'Vérifier si la BD est spécifiée
            If sEnv <> "" Then
                'Définir le catalogue 1:BDG par défaut.
                m_Catalogue = New clsGererCatalogue(sEnv, 1)

                'Vérifier si le catalogue est invalide
                If Not m_Catalogue.EstValide Then
                    'Retirer le catalogue invalide de la sélection
                    Me.Select(giNone)
                    'Déconnecter la BD des catalogues
                    m_Catalogue = Nothing
                End If
            Else
                'Déconnecter la BD des catalogues
                m_Catalogue = Nothing
            End If

        Catch erreur As Exception
            MsgBox(erreur.ToString)
        End Try
    End Sub

    Protected Overrides Sub OnUpdate()
        Me.Enabled = True
    End Sub
End Class
