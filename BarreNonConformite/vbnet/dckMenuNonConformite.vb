Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.esriSystem
Imports System.Windows.Forms
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.GeoDatabaseDistributed
Imports ESRI.ArcGIS.Geometry
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Display

''' <summary>
''' Menu de gestion des données en non-conformité, leurs réplicas, leurs conflits et leurs différences.
''' </summary>
Public Class dckMenuNonConformite
    Private m_hook As Object

#Region "Routines et fonctions d'événements - Initialisation"
    Public Sub New(ByVal hook As Object)
        'This call is required by the Windows Form Designer.
        InitializeComponent()

        'Add any initialization after the InitializeComponent() call.
        Me.Hook = hook

        'Définir l'application
        m_Application = CType(hook, IApplication)

        'Définir le document
        m_MxDocument = CType(m_Application.Document, IMxDocument)

        'Conserver le menu en mémoire
        m_MenuNonConformite = Me

        'Initialiser le menu
        Call Initialiser()
    End Sub

    ''' <summary>
    ''' Host object of the dockable window
    ''' </summary> 
    Public Property Hook() As Object
        Get
            Return m_hook
        End Get
        Set(ByVal value As Object)
            m_hook = value
        End Set
    End Property

    ''' <summary>
    ''' Implementation class of the dockable window add-in. It is responsible for
    ''' creating and disposing the user interface class for the dockable window.
    ''' </summary>
    Public Class AddinImpl
        Inherits ESRI.ArcGIS.Desktop.AddIns.DockableWindow

        Private m_windowUI As dckMenuNonConformite

        Protected Overrides Function OnCreateChild() As System.IntPtr
            m_windowUI = New dckMenuNonConformite(Me.Hook)
            Return m_windowUI.Handle
        End Function

        Protected Overrides Sub Dispose(ByVal Param As Boolean)
            If m_windowUI IsNot Nothing Then
                m_windowUI.Dispose(Param)
            End If

            MyBase.Dispose(Param)
        End Sub

    End Class

    Private Sub btnInitialiser_Click(sender As Object, e As EventArgs) Handles btnInitialiser.Click
        Try
            'Initialiser le menu
            Call Initialiser()

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
        End Try
    End Sub

#End Region

#Region "Routines et fonctions d'événements - Non-Conformité"
    Private Sub cboEnvSIB_SelectedIndexChanged(sender As Object, e As EventArgs) Handles cboEnvSIB.SelectedIndexChanged
        'Déclarer les variables de travail
        Dim pNoNC As KeyValuePair(Of String, String) = Nothing  'Contient les numéros de non-conformités dans SIB.
        Dim pNode As TreeNode = Nothing     'Contient un noeud de travail.

        Try
            'Définir l'environnement de SIB
            m_GererNC.Env = cboEnvSIB.Text

            'Initialiser le numéro de non-conformité
            cboNonConformite.Items.Clear()
            cboNonConformite.Text = ""

            'Initialiser la description de la NC
            rtbDescription.Clear()
            rtbDescription.Text = ""

            'Définir tous les numéros de non-conformité
            For Each pNoNC In m_GererNC.CreerDictionnaireNoNC
                'Ajouter le numéro de non-conformité (pNoNC.Key, pNoNC.Value)
                cboNonConformite.Items.Add(pNoNC.Key & ": " & pNoNC.Value)
            Next

            'Initialiser les identifiants
            m_NbIdentifiants = 0
            treIdentifiants.Nodes.Clear()
            lblNbIdentifiants.Text = "Nombre d'identifiants = 0"

            'Désélectionner toutes les classes
            For Each pNode In treClasses.Nodes
                'Désélectionner la classe
                pNode.Checked = False
            Next
            'Initialiser les classes
            m_NbClasses = 0
            lblNbClasses.Text = "Nombre de classes = 0"

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pNoNC = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub cboTypeProduit_SelectedIndexChanged(sender As Object, e As EventArgs) Handles cboTypeProduit.SelectedIndexChanged
        'Déclarer les variables de travail
        Dim pNoNC As KeyValuePair(Of String, String) = Nothing  'Contient les numéros de non-conformités dans SIB.
        Dim pNode As TreeNode = Nothing     'Contient un noeud de travail.

        Try
            'Définir le type de produit
            m_GererNC.TypeProduit = cboTypeProduit.Text

            'Initialiser le numéro de non-conformité
            cboNonConformite.Items.Clear()
            cboNonConformite.Text = ""

            'Initialiser la description de la NC
            rtbDescription.Clear()
            rtbDescription.Text = ""

            'Définir tous les numéros de non-conformité
            For Each pNoNC In m_GererNC.CreerDictionnaireNoNC
                'Ajouter le numéro de non-conformité (pNoNC.Key, pNoNC.Value)
                cboNonConformite.Items.Add(pNoNC.Key & ": " & pNoNC.Value)
            Next

            'Initialiser les identifiants
            m_NbIdentifiants = 0
            treIdentifiants.Nodes.Clear()
            lblNbIdentifiants.Text = "Nombre d'identifiants = 0"

            'Désélectionner toutes les classes
            For Each pNode In treClasses.Nodes
                'Désélectionner la classe
                pNode.Checked = False
            Next
            'Initialiser les classes
            m_NbClasses = 0
            lblNbClasses.Text = "Nombre de classes = 0"

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pNoNC = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub cboNonConformite_SelectedIndexChanged(sender As Object, e As EventArgs) Handles cboNonConformite.SelectedIndexChanged
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing              'Interface qui permet de changer le curseur de la souris.
        Dim pClasse As KeyValuePair(Of String, String) = Nothing 'Contient un code de classe et un nom de classe.
        Dim pNode As TreeNode = Nothing     'Contient un noeud de TreeView.
        Dim sNoNC As String = ""            'Contient le numéro de non-conformité.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            '---------------------------------------------------------
            'Vérifier si le NO_NC es spécifié
            If cboNonConformite.Text.Length > 0 Then
                'Définir le numéro de non-conformité
                sNoNC = cboNonConformite.Text.Substring(0, cboNonConformite.Text.IndexOf(":"))

                'Définir la description de la non-conformité
                rtbDescription.Text = m_GererNC.ExtraireDescriptionNoNC(sNoNC)

                'Définir l'information pour les identifiants de la non-conformité
                m_GererNC.DefinirInfoIdentifiantsNC(sNoNC, treIdentifiants)
            End If

            'Définir le nombre d'identifiants
            lblNbIdentifiants.Text = "Nombre d'identifiants = " & m_NbIdentifiants.ToString & "/" & treIdentifiants.Nodes.Count.ToString

            '---------------------------------------------------------
            'Initialiser les classes de la non-conformité spécifiée
            treClasses.Nodes.Clear()

            'Initialiser le nombre de classes sélectionnés
            m_NbClasses = 0
            'Définir toutes les classes du dictionnaire
            For Each pClasse In m_GererNC.CreerDictionaireClasses()
                'Ajouter l'identifiant du numéro de non-conformité (pNoNC.Key, pNoNC.Value)
                pNode = treClasses.Nodes.Add(pClasse.Key, pClasse.Key & " : " & pClasse.Value)
                'Vérifier si la classe est présente dans la description
                If rtbDescription.Text.ToUpper.Contains(pClasse.Value.ToUpper) Then
                    'Indiquer que la classe est présente dans la description
                    pNode.Checked = True
                End If
            Next

            'Définir le nombre de classes
            lblNbClasses.Text = "Nombre de classes = " & m_NbClasses.ToString & "/" & treClasses.Nodes.Count.ToString

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pClasse = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub dckMenuParametres_Resize(sender As Object, e As EventArgs) Handles Me.Resize
        'Déclarer les variables de travail
        Dim iDeltaHeight As Integer
        Dim iDeltaWidth As Integer

        Try
            'Calculer les deltas
            iDeltaHeight = Me.Height - m_Height
            iDeltaWidth = Me.Width - m_Width

            'Vérifier si le menu est initialisé
            If m_MenuNonConformite IsNot Nothing Then
                'Vérifier si la hauteur du menu est supérieure à la limite
                If m_MenuNonConformite.Size.Height > 220 Then
                    'Redimensionner les objets du menu en hauteur
                    tabMenuNonConformite.Height = tabMenuNonConformite.Height + iDeltaHeight
                    rtbDescription.Height = rtbDescription.Height + iDeltaHeight
                    treIdentifiants.Height = treIdentifiants.Height + iDeltaHeight
                    treClasses.Height = treClasses.Height + iDeltaHeight
                    treConflits.Height = treConflits.Height + iDeltaHeight
                    treDifferences.Height = treDifferences.Height + iDeltaHeight
                    treReplica.Height = treReplica.Height + iDeltaHeight
                    lblNbIdentifiants.Top = lblNbIdentifiants.Top + iDeltaHeight
                    lblNbClasses.Top = lblNbClasses.Top + iDeltaHeight
                    lblNbConflits.Top = lblNbConflits.Top + iDeltaHeight
                    lblNbDifferences.Top = lblNbDifferences.Top + iDeltaHeight
                    btnInitialiser.Top = btnInitialiser.Top + iDeltaHeight
                    'Initialiser les variables de dimension
                    m_Height = Me.Height
                End If

                'Vérifier si la largeur du menu est supérieure à la limite
                If m_MenuNonConformite.Size.Width > 120 Then
                    'Redimensionner les objets du menu en largeur
                    tabMenuNonConformite.Width = tabMenuNonConformite.Width + iDeltaWidth
                    cboGeodatabaseParent.Width = cboGeodatabaseParent.Width + iDeltaWidth
                    cboGeodatabaseEnfant.Width = cboGeodatabaseEnfant.Width + iDeltaWidth
                    cboNonConformite.Width = cboNonConformite.Width + iDeltaWidth
                    rtbDescription.Width = rtbDescription.Width + iDeltaWidth
                    treIdentifiants.Width = treIdentifiants.Width + iDeltaWidth
                    treClasses.Width = treClasses.Width + iDeltaWidth
                    treConflits.Width = treConflits.Width + iDeltaWidth
                    treDifferences.Width = treDifferences.Width + iDeltaWidth
                    treReplica.Width = treReplica.Width + iDeltaWidth
                    'Initialiser les variables de dimension
                    m_Width = Me.Width
                End If
            End If

        Catch erreur As Exception
            MsgBox("--Message: " & erreur.Message & vbCrLf & "--Source: " & erreur.Source & vbCrLf & "--StackTrace: " & erreur.StackTrace & vbCrLf)
        End Try
    End Sub
#End Region

#Region "Routines et fonctions d'événements - Réplica"
    Private Sub treReplica_KeyDown(sender As Object, e As KeyEventArgs) Handles treReplica.KeyDown
        'Déclarer les variables de travail
        Dim qTreeView As TreeView = Nothing    'Contient le TeeView
        Dim pNode As TreeNode = Nothing

        Try
            'Vérifier si la touche Shift est enfoncée
            If e.Shift Then
                'Vérifier si le type d'objet est un TreeView
                If TypeOf sender Is TreeView Then
                    'Définir le TreeView
                    qTreeView = CType(sender, TreeView)
                    'Vérifier si un Node est sélectionné
                    If qTreeView.SelectedNode IsNot Nothing Then
                        'Vérifier si le Node est ouvert
                        If qTreeView.SelectedNode.IsExpanded Then
                            'Ouvrir tous les Nodes
                            For Each pNode In qTreeView.SelectedNode.Nodes
                                pNode.Collapse()
                            Next
                            qTreeView.SelectedNode.Collapse()
                        Else
                            'Ouvrir tous les Nodes
                            qTreeView.SelectedNode.ExpandAll()
                        End If
                    End If
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qTreeView = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions d'événements - Classes"
    Private Sub treClasses_AfterCheck(sender As Object, e As TreeViewEventArgs) Handles treClasses.AfterCheck
        Try
            'Vérifier si le noeud est sélectionné
            If e.Node.Checked Then
                'Ajouter une classes dans le nombre
                m_NbClasses = m_NbClasses + 1

                'Si le noeud n'est pas sélectionné
            Else
                'Diminuer une classe dans le nombre
                m_NbClasses = m_NbClasses - 1
            End If

            'Afficher le nombre de classes
            lblNbClasses.Text = "Nombre de classes = " & m_NbClasses.ToString & "/" & treClasses.Nodes.Count.ToString

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        End Try
    End Sub

    Private Sub btnSelectClasse_Click(sender As Object, e As EventArgs) Handles btnSelectClasse.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNode As TreeNode = Nothing             'Contient le noeud à traiter.
        Dim sNomClasse As String = Nothing          'Contient le nom de la classe.
        Dim iNbCls As Integer = 0                   'Compteur de classes.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Initialiser le compteur
            iNbCls = 0

            'Traiter tous les noeuds
            For Each pNode In treClasses.Nodes
                'Définir le nom de la classe
                sNomClasse = pNode.Text.Substring(10).ToUpper

                'Vérifier si la classe est présente dans la description
                If rtbDescription.Text.ToUpper.Contains(sNomClasse) Then
                    'Sélectionner le noeud
                    If pNode.Checked = False Then pNode.Checked = True

                    'Compter le nombre d'identifiants
                    iNbCls = iNbCls + 1

                    'Si la classe est absente dans la description de la NC
                Else
                    'Désélectionner le noeud
                    If pNode.Checked = True Then pNode.Checked = False
                End If
            Next

            'Définir le nombre de classes
            m_NbClasses = iNbCls

            'Définir le nombre de classes
            treClasses.Text = "Nombre de classes = " & m_NbClasses.ToString & "/" & treClasses.Nodes.Count.ToString

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnDeselectClasse_Click(sender As Object, e As EventArgs) Handles btnDeselectClasse.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNode As TreeNode = Nothing             'Contient le noeud à traiter.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Initialiser le compteur
            m_NbClasses = treClasses.Nodes.Count

            'Traiter tous les noeuds
            For Each pNode In treClasses.Nodes
                'Désélectionner le noeud
                pNode.Checked = False
            Next

            'Initialiser le nombre de classes
            m_NbClasses = 0

            'Définir le nombre de classes
            treClasses.Text = "Nombre de classes = " & m_NbClasses.ToString & "/" & treClasses.Nodes.Count.ToString

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNode = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions d'événements - Identifiants"
    Private Sub treIdentifiants_DoubleClick(sender As Object, e As EventArgs) Handles treIdentifiants.DoubleClick
        Try
            'Vérifier si un Node est sélectionné
            If treIdentifiants.SelectedNode IsNot Nothing Then
                'Vérifier si le noeud est ouvert
                If treIdentifiants.SelectedNode.IsExpanded Then
                    'Ajouter les classes de l'identifiant en production
                    Call m_GererNC.DefinirInfoClassesProduction(treIdentifiants.SelectedNode)

                    'Si le noeud n'est pas ouvert
                ElseIf treIdentifiants.SelectedNode.Nodes.Count = 0 Then
                    'Ajouter les classes de l'identifiant en production
                    Call m_GererNC.DefinirInfoClassesProduction(treIdentifiants.SelectedNode)
                    'Ouvrir le noeud
                    treIdentifiants.SelectedNode.Expand()
                End If

                'Sélectionner les classes du TreeView selon les classes de l'identifiant
                m_GererNC.SelectionnerClasses(treIdentifiants.SelectedNode, treClasses)

                'Sélectionner l'identifiant
                If treIdentifiants.SelectedNode.Checked = False Then treIdentifiants.SelectedNode.Checked = True
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    Private Sub treIdentifiants_KeyDown(sender As Object, e As KeyEventArgs) Handles treIdentifiants.KeyDown
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud traité

        Try
            'Vérifier si la touche Shift est enfoncée
            If e.Shift Then
                'Vérifier si un Node est sélectionné
                If treIdentifiants.SelectedNode IsNot Nothing Then
                    'Vérifier si le Node est ouvert
                    If treIdentifiants.SelectedNode.IsExpanded Then
                        'Fermer tous les Nodes
                        For Each pNode In treIdentifiants.SelectedNode.Nodes
                            pNode.Collapse()
                        Next
                        treIdentifiants.SelectedNode.Collapse()
                    Else
                        'Ouvrir tous les Nodes
                        treIdentifiants.SelectedNode.ExpandAll()
                    End If
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    Private Sub treIdentifiants_AfterCheck(sender As Object, e As TreeViewEventArgs) Handles treIdentifiants.AfterCheck
        Try
            'Vérifier si le noeud est sélectionné
            If e.Node.Checked Then
                'Ajouter un identifiant dans le nombre
                m_NbIdentifiants = m_NbIdentifiants + 1

                'Si le noeud n'est pas sélectionné
            Else
                'Diminuer un identifiant dans le nombre
                m_NbIdentifiants = m_NbIdentifiants - 1
            End If

            'Afficher le nombre d'identifiants
            lblNbIdentifiants.Text = "Nombre d'identifiants = " & m_NbIdentifiants.ToString & "/" & treIdentifiants.Nodes.Count.ToString

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        End Try
    End Sub

    Private Sub btnOuvrirIdentifiant_Click(sender As Object, e As EventArgs) Handles btnOuvrirIdentifiant.Click
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud traité

        Try
            'Traiter tous les noeuds
            For Each pNode In treIdentifiants.Nodes
                'Ouvrir tous les noeuds
                pNode.Expand()
            Next

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnFermerIdentifiant_Click(sender As Object, e As EventArgs) Handles btnFermerIdentifiant.Click
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud traité

        Try
            'Traiter tous les noeuds
            For Each pNode In treIdentifiants.Nodes
                'Ouvrir tous les noeuds
                pNode.Collapse()
            Next

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnSelectIdentifiant_Click(sender As Object, e As EventArgs) Handles btnSelectIdentifiant.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNode As TreeNode = Nothing             'Contient le noeud à traiter.
        Dim iNbId As Integer = 0                    'Compteur d'identifiants.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Initialiser le compteur
            iNbId = 0

            'Traiter tous les noeuds
            For Each pNode In treIdentifiants.Nodes
                'Vérifier si l'édition de fin est inconnu (99999)
                If pNode.Text.Contains("99999") Then
                    'Sélectionner le noeud
                    pNode.Checked = True

                    'Compter le nombre d'identifiants
                    iNbId = iNbId + 1

                    'Si l'édition de fin est connu
                Else
                    'Désélectionner le noeud
                    pNode.Checked = False
                End If
            Next

            'Définir le nombre d'identifiants
            m_NbIdentifiants = iNbId

            'Définir le nombre d'identifiants
            lblNbIdentifiants.Text = "Nombre d'identifiants = " & m_NbIdentifiants.ToString & "/" & treIdentifiants.Nodes.Count.ToString

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnDeselectIdentifiant_Click(sender As Object, e As EventArgs) Handles btnDeselectIdentifiant.Click
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud traité

        Try
            'Traiter tous les noeuds
            For Each pNode In treIdentifiants.Nodes
                'Ouvrir tous les noeuds
                If pNode.Checked Then pNode.Checked = False
            Next

            'Initialiser le compteur
            m_NbIdentifiants = 0

            'Définir le nombre d'identifiants
            lblNbIdentifiants.Text = "Nombre d'identifiants = " & m_NbIdentifiants.ToString & "/" & treIdentifiants.Nodes.Count.ToString

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnInitialiserClassesIdentifiants_Click(sender As Object, e As EventArgs) Handles btnInitialiserClassesIdentifiants.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNode As TreeNode = Nothing             'Contient un noeud de travail.
        Dim sNoNC As String = ""                    'Contient le numéro de non-conformité.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Définir le numéro de non-conformité
            sNoNC = cboNonConformite.Text.Substring(0, cboNonConformite.Text.IndexOf(":"))

            'Définir l'information pour les identifiants de la non-conformité
            m_GererNC.DefinirInfoIdentifiantsNC(sNoNC, treIdentifiants)

            'Définir toutes les classes
            For Each pNode In treClasses.Nodes
                'Vérifier si la classe est présente dans la description
                If rtbDescription.Text.ToUpper.Contains(pNode.Name.ToUpper) Then
                    'Indiquer que la classe est présente dans la description
                    pNode.Checked = True
                End If
            Next

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnAfficherClassesProduction_Click(sender As Object, e As EventArgs) Handles btnAfficherClassesProduction.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNode As TreeNode = Nothing             'Noeud traité

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Traiter tous les noeuds
            For Each pNode In treIdentifiants.Nodes
                'Ouvrir tous les noeuds
                If pNode.Checked Then
                    'Ajouter les classes de l'identifiant en production
                    Call m_GererNC.DefinirInfoClassesProduction(pNode)

                    'Ouvrir le noeud
                    pNode.Expand()
                End If
            Next

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNode = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions d'événements - Conflits"
    Private Sub treConflits_KeyDown(sender As Object, e As KeyEventArgs) Handles treConflits.KeyDown
        'Déclarer les variables de travail
        Dim qTreeView As TreeView = Nothing     'Contient le TeeView
        Dim pNode As TreeNode = Nothing         'Noeud traité

        Try
            'Vérifier si la touche Shift est enfoncée
            If e.Shift Then
                'Vérifier si le type d'objet est un TreeView
                If TypeOf sender Is TreeView Then
                    'Définir le TreeView
                    qTreeView = CType(sender, TreeView)
                    'Vérifier si un Node est sélectionné
                    If qTreeView.SelectedNode IsNot Nothing Then
                        'Vérifier si le Node est ouvert
                        If qTreeView.SelectedNode.IsExpanded Then
                            'Fermer tous les Nodes
                            For Each pNode In qTreeView.SelectedNode.Nodes
                                pNode.Collapse()
                            Next
                            qTreeView.SelectedNode.Collapse()
                        Else
                            'Ouvrir tous les Nodes
                            qTreeView.SelectedNode.ExpandAll()
                        End If
                    End If
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qTreeView = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub treConflits_AfterSelect(sender As Object, e As TreeViewEventArgs) Handles treConflits.AfterSelect
        Try
            'Afficher l'information sur les conflits
            Call AfficherInfoConflits(e.Node)

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    Private Sub treConflits_NodeMouseClick(sender As Object, e As TreeNodeMouseClickEventArgs) Handles treConflits.NodeMouseClick
        Try
            'Vérifier si un noeud est sélectionné
            If treConflits.SelectedNode IsNot Nothing Then
                'Si le noeud est le même que celui sélectionné
                If e.Node.Name = treConflits.SelectedNode.Name Then
                    'Afficher l'information sur les conflits
                    Call AfficherInfoConflits(e.Node)
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        End Try
    End Sub

    Private Sub btnOuvrirFermerConflits_Click(sender As Object, e As EventArgs) Handles btnOuvrirFermerConflits.Click
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud traité

        Try
            'Vérifier si un Node est sélectionné
            If treConflits.SelectedNode IsNot Nothing Then
                'Vérifier si le Node est ouvert
                If treConflits.SelectedNode.IsExpanded Then
                    'Fermer tous les Nodes
                    For Each pNode In treConflits.SelectedNode.Nodes
                        pNode.Collapse()
                    Next
                    treConflits.SelectedNode.Collapse()
                Else
                    'Ouvrir tous les Nodes
                    treConflits.SelectedNode.ExpandAll()
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnAccepterActionParent_Click(sender As Object, e As EventArgs) Handles btnAccepterActionParent.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNodeReplica As TreeNode = Nothing      'Contient le noeud du réplica.
        Dim pNodeResultat As TreeNode = Nothing     'Contient le noeud de résultat.
        Dim pNodeTraiter As TreeNode = Nothing      'Contient le noeud à traiter.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Vérifier si des conflits sont présentes
                If treConflits.Nodes.Count > 0 Then
                    'Définir le noeud du réplica
                    pNodeReplica = treConflits.Nodes.Item(0)

                    'Définir le noeud à traiter
                    pNodeTraiter = treConflits.SelectedNode

                    'Vérifier si des Conflits sont présentes
                    If treConflits.Nodes.Count > 1 Then
                        'Définir le noeud de résultat
                        pNodeResultat = treConflits.Nodes.Item(1)

                        'Vérifier si le noeud traiter n'est pas un résulat
                        If pNodeTraiter.Tag.ToString <> "RESULTAT" And pNodeTraiter.Tag.ToString <> "TROUVER" Then
                            'Détruire le noeud de résultat
                            pNodeResultat.Remove()
                        End If
                    End If

                    'Désélectionner le noeud à traiter
                    treConflits.SelectedNode = Nothing

                    'Accepter les actions sélectionnées qui a été effectuées dans la Géodatabase parent
                    m_GererReplica.AccepterActionParent(pNodeTraiter, pNodeReplica)

                    'Sélectionner le noeud du réplica
                    treConflits.SelectedNode = pNodeReplica

                    'Rafraîchier l'affichage
                    m_MxDocument.ActiveView.Refresh()
                    System.Windows.Forms.Application.DoEvents()
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNodeReplica = Nothing
            pNodeResultat = Nothing
            pNodeTraiter = Nothing
        End Try
    End Sub

    Private Sub btnRefuserActionParent_Click(sender As Object, e As EventArgs) Handles btnRefuserActionParent.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNodeReplica As TreeNode = Nothing      'Contient le noeud du réplica.
        Dim pNodeResultat As TreeNode = Nothing     'Contient le noeud de résultat.
        Dim pNodeTraiter As TreeNode = Nothing      'Contient le noeud à traiter.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Vérifier si des conflits sont présentes
                If treConflits.Nodes.Count > 0 Then
                    'Définir le noeud du réplica
                    pNodeReplica = treConflits.Nodes.Item(0)

                    'Définir le noeud à traiter
                    pNodeTraiter = treConflits.SelectedNode

                    'Vérifier si des Conflits sont présentes
                    If treConflits.Nodes.Count > 1 Then
                        'Définir le noeud de résultat
                        pNodeResultat = treConflits.Nodes.Item(1)

                        'Vérifier si le noeud traiter n'est pas un résulat
                        If pNodeTraiter.Tag.ToString <> "RESULTAT" And pNodeTraiter.Tag.ToString <> "TROUVER" Then
                            'Détruire le noeud de résultat
                            pNodeResultat.Remove()
                        End If
                    End If

                    'Désélectionner le noeud à traiter
                    treConflits.SelectedNode = Nothing

                    'Refuser les actions sélectionnées qui a été effectuées dans la Géodatabase parent
                    m_GererReplica.RefuserActionParent(pNodeTraiter, pNodeReplica)

                    'Sélectionner le noeud du réplica
                    treConflits.SelectedNode = pNodeReplica

                    'Rafraîchier l'affichage
                    m_MxDocument.ActiveView.Refresh()
                    System.Windows.Forms.Application.DoEvents()
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNodeReplica = Nothing
            pNodeResultat = Nothing
            pNodeTraiter = Nothing
        End Try
    End Sub

    Private Sub btnRechercherConflitsAvecDifferences_Click(sender As Object, e As EventArgs) Handles btnRechercherConflitsAvecDifferences.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Rechercher tous les éléments contenus dans le TreeView des conflits qui ont des différences
                Call m_GererReplica.RechercherElementsTreeView("ConflitsAvecDifferences", treConflits, treDifferences, True)
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
        End Try
    End Sub

    Private Sub btnRechercherConflitsSansDifferences_Click(sender As Object, e As EventArgs) Handles btnRechercherConflitsSansDifferences.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Rechercher tous les éléments contenus dans le TreeView des conflits qui n'ont pas des différences
                Call m_GererReplica.RechercherElementsTreeView("ConflitsSansDifferences", treConflits, treDifferences, False)
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
        End Try
    End Sub

    Private Sub cboRechercherConflits_KeyDown(sender As Object, e As KeyEventArgs) Handles cboRechercherConflits.KeyDown
        Try
            'Si la touche est Enter
            If e.KeyValue = Keys.Enter Then
                'Vérifier si un réplica est présent
                If m_GererReplica IsNot Nothing Then
                    'Rechercher tous les éléments contenus dans le TreeView des conflits qui contient le texte recherché
                    Call m_GererReplica.RechercherElements(treConflits, cboRechercherConflits.Text)
                End If

                'Vérifier si la recherche est déjà présente
                If Not cboRechercherConflits.Items.Contains(cboRechercherConflits.Text) Then
                    'Ajouter le texte
                    cboRechercherConflits.Items.Add(cboRechercherConflits.Text)
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub
#End Region

#Region "Routines et fonctions d'événements - Différences"
    Private Sub treDifferences_KeyDown(sender As Object, e As KeyEventArgs) Handles treDifferences.KeyDown
        'Déclarer les variables de travail
        Dim qTreeView As TreeView = Nothing    'Contient le TeeView
        Dim pNode As TreeNode = Nothing

        Try
            'Vérifier si la touche Shift est enfoncée
            If e.Shift Then
                'Vérifier si le type d'objet est un TreeView
                If TypeOf sender Is TreeView Then
                    'Définir le TreeView
                    qTreeView = CType(sender, TreeView)
                    'Vérifier si un Node est sélectionné
                    If qTreeView.SelectedNode IsNot Nothing Then
                        'Vérifier si le Node est ouvert
                        If qTreeView.SelectedNode.IsExpanded Then
                            'Ouvrir tous les Nodes
                            For Each pNode In qTreeView.SelectedNode.Nodes
                                pNode.Collapse()
                            Next
                            qTreeView.SelectedNode.Collapse()
                        Else
                            'Ouvrir tous les Nodes
                            qTreeView.SelectedNode.ExpandAll()
                        End If
                    End If
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qTreeView = Nothing
            pNode = Nothing
        End Try
    End Sub

    Private Sub treDifferences_AfterSelect(sender As Object, e As TreeViewEventArgs) Handles treDifferences.AfterSelect
        Try
            'Afficher l'information sur les différences
            Call AfficherInfoDifferences(e.Node)

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub

    Private Sub treDifferences_NodeMouseClick(sender As Object, e As TreeNodeMouseClickEventArgs) Handles treDifferences.NodeMouseClick
        Try
            'Vérifier si un noeud est sélectionné
            If treDifferences.SelectedNode IsNot Nothing Then
                If e.Node.Name = treDifferences.SelectedNode.Name Then
                    'Afficher l'information sur les différences
                    Call AfficherInfoDifferences(e.Node)
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        End Try
    End Sub

    Private Sub btnOuvrirFermerDifferences_Click(sender As Object, e As EventArgs) Handles btnOuvrirFermerDifferences.Click
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing         'Noeud traité

        Try
            'Vérifier si un Node est sélectionné
            If treDifferences.SelectedNode IsNot Nothing Then
                'Vérifier si le Node est ouvert
                If treDifferences.SelectedNode.IsExpanded Then
                    'Fermer tous les Nodes
                    For Each pNode In treDifferences.SelectedNode.Nodes
                        pNode.Collapse()
                    Next
                    'Fermer le noeud sélectionné
                    treDifferences.SelectedNode.Collapse()
                Else
                    'Ouvrir tous les Nodes
                    treDifferences.SelectedNode.ExpandAll()
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Sub

    Private Sub btnAccepterActionEnfant_Click(sender As Object, e As EventArgs) Handles btnAccepterActionEnfant.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNodeReplica As TreeNode = Nothing      'Contient le noeud du réplica.
        Dim pNodeResultat As TreeNode = Nothing     'Contient le noeud de résultat.
        Dim pNodeTraiter As TreeNode = Nothing      'Contient le noeud à traiter.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Vérifier si des différences sont présentes
                If treDifferences.Nodes.Count > 0 Then
                    'Définir le noeud du réplica
                    pNodeReplica = treDifferences.Nodes.Item(0)

                    'Définir le noeud à traiter
                    pNodeTraiter = treDifferences.SelectedNode

                    'Vérifier si des différences sont présentes
                    If treDifferences.Nodes.Count > 1 Then
                        'Définir le noeud de résultat
                        pNodeResultat = treDifferences.Nodes.Item(1)

                        'Vérifier si le noeud traiter n'est pas un résulat
                        If pNodeTraiter.Tag.ToString <> "RESULTAT" And pNodeTraiter.Tag.ToString <> "TROUVER" Then
                            'Détruire le noeud de résultat
                            pNodeResultat.Remove()
                        End If
                    End If

                    'Désélectionner le noeud à traiter
                    treDifferences.SelectedNode = Nothing

                    'Accepter les actions sélectionnées qui a été effectuées dans la Géodatabase enfant
                    m_GererReplica.AccepterActionEnfant(pNodeTraiter, pNodeReplica)

                    'Sélectionner le noeud du réplica
                    treDifferences.SelectedNode = pNodeReplica

                    'Rafraîchier l'affichage
                    m_MxDocument.ActiveView.Refresh()
                    System.Windows.Forms.Application.DoEvents()
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNodeReplica = Nothing
            pNodeResultat = Nothing
            pNodeTraiter = Nothing
        End Try
    End Sub

    Private Sub btnRefuserActionEnfant_Click(sender As Object, e As EventArgs) Handles btnRefuserActionEnfant.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.
        Dim pNodeReplica As TreeNode = Nothing      'Contient le noeud du réplica.
        Dim pNodeResultat As TreeNode = Nothing     'Contient le noeud de résultat.
        Dim pNodeTraiter As TreeNode = Nothing      'Contient le noeud à traiter.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Vérifier si des différences sont présentes
                If treDifferences.Nodes.Count > 0 Then
                    'Définir le noeud du réplica
                    pNodeReplica = treDifferences.Nodes.Item(0)

                    'Définir le noeud à traiter
                    pNodeTraiter = treDifferences.SelectedNode

                    'Vérifier si des différences sont présentes
                    If treDifferences.Nodes.Count > 1 Then
                        'Définir le noeud de résultat
                        pNodeResultat = treDifferences.Nodes.Item(1)

                        'Vérifier si le noeud traiter n'est pas un résulat
                        If pNodeTraiter.Tag.ToString <> "RESULTAT" And pNodeTraiter.Tag.ToString <> "TROUVER" Then
                            'Détruire le noeud de résultat
                            pNodeResultat.Remove()
                        End If
                    End If

                    'Désélectionner le noeud à traiter
                    treDifferences.SelectedNode = Nothing

                    'Refuser les actions sélectionnées qui a été effectuées dans la Géodatabase enfant
                    m_GererReplica.RefuserActionEnfant(pNodeTraiter, pNodeReplica)

                    'Sélectionner le noeud du réplica
                    treDifferences.SelectedNode = pNodeReplica

                    'Rafraîchier l'affichage
                    m_MxDocument.ActiveView.Refresh()
                    System.Windows.Forms.Application.DoEvents()
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
            pNodeReplica = Nothing
            pNodeResultat = Nothing
            pNodeTraiter = Nothing
        End Try
    End Sub

    Private Sub btnRechercherDifferencesAvecConflits_Click(sender As Object, e As EventArgs) Handles btnRechercherDifferencesAvecConflits.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Rechercher tous les éléments contenus dans le TreeView des différences qui ont des conflits
                Call m_GererReplica.RechercherElementsTreeView("DifferencesAvecConflits", treDifferences, treConflits, True)
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
        End Try
    End Sub

    Private Sub btnRechercherDifferencesSansConflits_Click(sender As Object, e As EventArgs) Handles btnRechercherDifferencesSansConflits.Click
        'Déclarer les variables de travail
        Dim pMouseCursor As IMouseCursor = Nothing  'Interface qui permet de changer le curseur de la souris.

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Vérifier si un réplica est présent
            If m_GererReplica IsNot Nothing Then
                'Rechercher tous les éléments contenus dans le TreeView des différences qui n'ont pas des conflits
                Call m_GererReplica.RechercherElementsTreeView("DifferencesSansConflits", treDifferences, treConflits, False)
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            pMouseCursor = Nothing
        End Try
    End Sub

    Private Sub cboRechercherDifferences_KeyDown(sender As Object, e As KeyEventArgs) Handles cboRechercherDifferences.KeyDown
        Try
            'Si c'est la touche Enter
            If e.KeyValue = Keys.Enter Then
                'Vérifier si un réplica est présent
                If m_GererReplica IsNot Nothing Then
                    'Rechercher tous les éléments contenus dans le TreeView des différences qui contient le texte recherché
                    Call m_GererReplica.RechercherElements(treDifferences, cboRechercherDifferences.Text)
                End If

                'Vérifier si la recherche est déjà présente
                If Not cboRechercherDifferences.Items.Contains(cboRechercherDifferences.Text) Then
                    'Ajouter le texte
                    cboRechercherDifferences.Items.Add(cboRechercherDifferences.Text)
                End If
            End If

        Catch ex As Exception
            'Message d'erreur
            MessageBox.Show(ex.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        End Try
    End Sub
#End Region

#Region "Routines et fonctions publics"
    '''<summary>
    ''' Permet d'initialiser le menu pour l'affichage et la modification des paramètres de la barre de non-conformité.
    '''</summary>
    '''
    Public Sub Initialiser()
        Try
            'Initialiser les symboles
            Call InitSymbole()

            'Définir la Géodatabase
            cboGeodatabaseParent.Items.Clear()
            cboGeodatabaseParent.Text = "BDRS_TST_BDG_DBA"
            cboGeodatabaseParent.Items.Add("BDRS_PRO_BDG_DBA")
            cboGeodatabaseParent.Items.Add("BDRS_TST_BDG_DBA")
            cboGeodatabaseParent.Items.Add("GEO_PRO_GEOBASE_DBA")
            cboGeodatabaseParent.Items.Add("GEO_TST_GEOBASE_DBA")
            cboGeodatabaseParent.Items.Add("Database Connections\BDRS_PRO_BDG_DBA.SDE")
            cboGeodatabaseParent.Items.Add("Database Connections\BDRS_TST_BDG_DBA.SDE")

            'Définir la version de travail
            cboGeodatabaseEnfant.Items.Clear()
            cboGeodatabaseEnfant.Text = "D:\COR-NC\[NC].gdb"
            cboGeodatabaseEnfant.Items.Add("D:\COR-NC\[NC].gdb")
            cboGeodatabaseEnfant.Items.Add("D:\COR-NC\[NC].mdb")
            cboGeodatabaseEnfant.Items.Add("C:\COR-NC\[NC].gdb")
            cboGeodatabaseEnfant.Items.Add("C:\COR-NC\[NC].mdb")

            'Définir le type de travail
            'cboTypeTravail.Items.Clear()
            'cboTypeTravail.Text = "COR-NC"
            'cboTypeTravail.Items.Add("COR-NC")

            'Initialiser le menu pour l'information sur le réplica
            Call InitialiserReplica()

            'Initialiser le menu pour l'information de non-conformité.
            Call InitialiserNonConformite()

            'Remplir la liste des Geodatabases de Version
            If m_cboGeodatabaseEnfant IsNot Nothing Then
                'Initialiser le ComboBox de la Géodatabase enfant
                m_cboGeodatabaseEnfant.Init()
            End If

        Catch ex As Exception
            'Message d'erreur
            MsgBox("--Message: " & ex.Message & vbCrLf & "--Source: " & ex.Source & vbCrLf & "--StackTrace: " & ex.StackTrace & vbCrLf)
        End Try
    End Sub

    '''<summary>
    ''' Permet d'initialiser le menu pour l'information de non-conformité.
    '''</summary>
    '''
    Public Sub InitialiserNonConformite()
        'Déclarer les variables de travail
        Dim pEnv As KeyValuePair(Of String, String) = Nothing           'Contient le dictionnaire des environnements de SIB.
        Dim pTypeProduit As KeyValuePair(Of String, String) = Nothing   'Contient le dictionnaire des types de produit.
        Dim pTrackCancel As ITrackCancel = Nothing                      'Interface utilisé pour afficher les messages.

        Try
            'Initialiser le nombre de classe de d'identifiant
            m_NbClasses = 0
            m_NbIdentifiants = 0

            'Créer un nouvel objet pour gérer les non-conformités
            m_GererNC = New clsGererNC

            'Permettre d'afficher les messages et annnuler la progression au besoin
            pTrackCancel = New CancelTracker
            pTrackCancel.CancelOnKeyPress = True
            pTrackCancel.CancelOnClick = False
            pTrackCancel.Progressor = m_Application.StatusBar.ProgressBar
            m_GererNC.TrackCancel = pTrackCancel

            'Définir le type de travail
            'cboTypeTravail.Items.Clear()
            'cboTypeTravail.Text = "COR-NC"
            'cboTypeTravail.Items.Add("COR-NC")

            'Initialiser le numéro de non-conformité
            cboNonConformite.Items.Clear()
            cboNonConformite.Text = ""

            'Initialiser la description
            rtbDescription.Clear()
            rtbDescription.Text = ""

            'Définir l'attribut de découpage
            'cboAttributDecoupage.Items.Clear()
            'cboAttributDecoupage.Text = "DATASET_NAME"
            'cboAttributDecoupage.Items.Add("DATASET_NAME")

            'Définir l'attribut d'identifiant unique
            'cboAttributIdUnique.Items.Clear()
            'cboAttributIdUnique.Text = "BDG_ID"
            'cboAttributIdUnique.Items.Add("BDG_ID")

            'Initialiser les identifiants
            treIdentifiants.Nodes.Clear()
            lblNbIdentifiants.Text = "Nombre d'identifiants = 0"

            'Initialiser les classes
            treClasses.Nodes.Clear()
            lblNbClasses.Text = "Nombre de classes = 0"

            'Vider l'environnement SIB
            cboEnvSIB.Items.Clear()
            'Définir tous les environnements
            For Each pEnv In m_GererNC.CreerDictionaireEnv
                'Ajouter l'environnement (pair.Key, pair.Value)
                cboEnvSIB.Items.Add(pEnv.Key)
            Next
            'Définir l'environnement par défaut
            m_GererNC.Env = m_GererNC.CreerDictionaireEnv.Item("SIB_TST")
            cboEnvSIB.Text = m_GererNC.Env

            'Vider le type de produit
            cboTypeProduit.Items.Clear()
            'Définir tous les types de produit
            For Each pTypeProduit In m_GererNC.CreerDictionaireTypeProduit
                'Ajouter le type de produit (pair.Key, pair.Value)
                cboTypeProduit.Items.Add(pTypeProduit.Key)
            Next
            'Définir le type de produit par défaut
            m_GererNC.TypeProduit = m_GererNC.CreerDictionaireTypeProduit.Item("BDG")
            cboTypeProduit.Text = m_GererNC.TypeProduit

            'Afficher l'onglet de la non-conformité par défaut
            tabMenuNonConformite.SelectTab(tabNonConformite)

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pEnv = Nothing
            pTypeProduit = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Permet d'initialiser le menu pour l'information sur le réplica.
    '''</summary>
    '''
    Public Sub InitialiserReplica()
        Try
            'Initialiser la classe du réplica
            m_GererReplica = Nothing
            m_NbConflits = -1
            m_NbDifferences = -1

            'Initialiser les conflits
            treConflits.Nodes.Clear()
            lblNbConflits.Text = "Nombre de conflits = 0"
            cboRechercherConflits.Items.Clear()
            cboRechercherConflits.Text = ""
            cboRechercherConflits.Enabled = False
            btnRechercherConflitsAvecDifferences.Enabled = False
            btnRechercherConflitsSansDifferences.Enabled = False
            btnRefuserActionParent.Enabled = False
            btnAccepterActionParent.Enabled = False
            btnOuvrirFermerConflits.Enabled = False

            'Initialiser les différences
            treDifferences.Nodes.Clear()
            lblNbDifferences.Text = "Nombre de differences = 0"
            cboRechercherDifferences.Items.Clear()
            cboRechercherDifferences.Text = ""
            cboRechercherDifferences.Enabled = False
            btnRechercherDifferencesAvecConflits.Enabled = False
            btnRechercherDifferencesSansConflits.Enabled = False
            btnRefuserActionEnfant.Enabled = False
            btnAccepterActionEnfant.Enabled = False
            btnOuvrirFermerDifferences.Enabled = False

            'Initialiser la description du réplica
            treReplica.Nodes.Clear()

            'Afficher l'onglet du réplica par défaut
            tabMenuNonConformite.SelectTab(tabReplica)

        Catch ex As Exception
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'afficher/dessiner l'information sur les conflits à partir d'un noeud sélectionné d'un TreeView.
    '''</summary>
    '''
    '''<param name="pSelectNode">Noeud sélectionné d'un TreeView.</param>
    ''' 
    Public Sub AfficherInfoConflits(ByVal pSelectNode As TreeNode)
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing                 'Contient le noeud à traiter.
        Dim pRow As IRow = Nothing                      'Interface contenant un élément.
        Dim pFeature As IFeature = Nothing              'Interface contenant un élément géographique.
        Dim pGeomBag As IGeometryBag = Nothing   'Interface contenant les géométries d'un élément.
        Dim pGeomColl As IGeometryCollection = Nothing   'Interface contenant les géométries d'un élément.
        Dim pGeometry As IGeometry = Nothing            'Interface contenant la géométrie d'un élément.
        Dim pConflitCourant As IGeometry = Nothing      'Interface contenant la géométrie d'un élément courant.
        Dim pConflitArchive As IGeometry = Nothing      'Interface contenant la géométrie d'un élément d'archive.
        Dim iNbElements As Integer = 0                  'Contient le nombre d'éléments.
        Dim iNbAttributs As Integer = 0                 'Contient le nombre dattributs d'éléments.

        Try
            'Activer les boutons pour gérer les conflits
            cboRechercherConflits.Enabled = False
            btnRechercherConflitsAvecDifferences.Enabled = False
            btnRechercherConflitsSansDifferences.Enabled = False
            btnOuvrirFermerConflits.Enabled = False
            btnRefuserActionParent.Enabled = False
            btnAccepterActionParent.Enabled = False
            If treConflits.Nodes.Count > 0 Then
                If treConflits.Nodes.Item(0).Nodes.Count > 0 Then
                    cboRechercherConflits.Enabled = True
                    btnRechercherConflitsAvecDifferences.Enabled = True
                    btnRechercherConflitsSansDifferences.Enabled = True
                    btnOuvrirFermerConflits.Enabled = True
                    btnRefuserActionParent.Enabled = True
                    btnAccepterActionParent.Enabled = True
                End If
            End If

            'Si le noeud est RESULTAT
            If pSelectNode.Tag.ToString = "RESULTAT" Then
                'Afficher l'information
                lblNbConflits.Text = "Nombre d'attributs trouvés = " & pSelectNode.Nodes.Count.ToString

                'Si le noeud est REPLICA
            ElseIf pSelectNode.Tag.ToString = "REPLICA" Then
                'Traiter toutes les classes
                Call m_GererReplica.CalculerDifferences(pSelectNode, iNbElements, iNbAttributs)
                'Afficher l'information
                lblNbConflits.Text = "Nombre de conflits : NbElements=" & iNbElements.ToString & " , NbAttributs=" & iNbAttributs.ToString

                'Si le noeud est CLASSE
            ElseIf pSelectNode.Tag.ToString = "CLASSE" Then
                'Traiter toutes les classes
                Call m_GererReplica.CalculerDifferences(pSelectNode, iNbElements, iNbAttributs)
                'Afficher l'information
                lblNbConflits.Text = "Nombre de conflits : NbElements=" & iNbElements.ToString & " , NbAttributs=" & iNbAttributs.ToString

                'Si le noeud est ETAT
            ElseIf pSelectNode.Tag.ToString = "ETAT" Then
                'Traiter toutes les classes
                Call m_GererReplica.CalculerDifferences(pSelectNode, iNbElements, iNbAttributs)
                'Afficher l'information
                lblNbConflits.Text = "Nombre de conflits : NbElements=" & iNbElements.ToString & " , NbAttributs=" & iNbAttributs.ToString

                'Si c'est un noeud d'élément
            ElseIf pSelectNode.Tag.ToString = "ELEMENT" Then
                'Afficher l'information
                lblNbConflits.Text = "Nombre d'attributs en conflit = " & pSelectNode.Nodes.Count.ToString

                'Si le noeud parent est DETRUIRE
                If pSelectNode.Parent.Name = "DETRUIRE" Then
                    'Définir l'élément d'archive
                    pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Zoom selon la géométrie de l'élément
                        Call ZoomToGeometry(pFeature.Shape)
                        'Dessiner la géométrie et les sommets de l'élément sans rafraichir
                        Call bDessinerGeometrie(pFeature.Shape, False, True, True)
                    End If

                    'Si le noeud parent est AJOUTER
                ElseIf pSelectNode.Parent.Name = "AJOUTER" Then
                    'Définir l'élément courant
                    pRow = m_GererReplica.ExtraireElementParent(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Zoom selon la géométrie de l'élément
                        Call ZoomToGeometry(pFeature.Shape)
                        'Dessiner la géométrie et les sommets de l'élément sans rafraichir
                        Call bDessinerGeometrie(pFeature.Shape, False, True, True)
                    End If

                    'Si le noeud parent est MODIFIER
                ElseIf pSelectNode.Parent.Name = "MODIFIER" Then
                    'Définir l'élément d'archive
                    pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément d'archive
                        pConflitArchive = pFeature.Shape

                        'Définir l'élément courant
                        pRow = m_GererReplica.ExtraireElementParent(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément courant
                        pConflitCourant = pFeature.Shape

                        'Créer un Bag vide
                        pGeomBag = New GeometryBag
                        'Interface pour ajouter des composantes
                        pGeomColl = CType(pGeomBag, IGeometryCollection)
                        'Ajouter la géométrie de l'élément courant au Bag
                        pGeomColl.AddGeometry(pConflitCourant)
                        'Ajouter la géométrie de l'élément d'archive au Bag
                        pGeomColl.AddGeometry(pConflitArchive)
                        'Zoom selon les géométries de l'élément
                        Call ZoomToGeometry(CType(pGeomBag, IGeometry))

                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Dessiner la géométrie et les sommets de l'élément d'archive sans rafraichir
                        Call bDessinerGeometrie(pConflitArchive, False, True, True)

                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Dessiner la géométrie et les sommets de l'élément courant sans rafraichir
                        Call bDessinerGeometrie(pFeature.Shape, False, True, True)
                    End If
                End If

                'Sinon c'est un noeud de géométrie
            ElseIf pSelectNode.Tag.ToString = "GEOMETRIE" Then
                'Si le noeud parent est DETRUIRE
                If pSelectNode.Parent.Parent.Name = "DETRUIRE" Then
                    'Définir l'élément d'archive
                    pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Copier la géométrie de l'élément
                        pGeometry = pFeature.ShapeCopy
                        'Définir la géométrie de l'élément courant
                        pGeometry.SetEmpty()
                        'Extraire les différences entre les géométries
                        Call ExtraireDifferencesGeometrie(pGeometry, pFeature.Shape, pConflitCourant, pConflitArchive, lblNbConflits.Text)
                        'Zoom selon la géométrie de l'élément
                        Call ZoomToGeometry(pFeature.Shape)
                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Dessiner la géométrie et les sommets des différences de l'élément d'archive sans rafraichir
                        Call bDessinerGeometrie(pConflitArchive, False, True, True)
                    End If

                    'Si le noeud parent est AJOUTER
                ElseIf pSelectNode.Parent.Parent.Name = "AJOUTER" Then
                    'Définir l'élément courant
                    pRow = m_GererReplica.ExtraireElementParent(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Copier la géométrie de l'élément
                        pGeometry = pFeature.ShapeCopy
                        'Définir la géométrie de l'élément d'archive
                        pGeometry.SetEmpty()
                        'Extraire les différences entre les géométries
                        Call ExtraireDifferencesGeometrie(pFeature.Shape, pGeometry, pConflitCourant, pConflitArchive, lblNbConflits.Text)
                        'Zoom selon la géométrie de l'élément
                        Call ZoomToGeometry(pFeature.Shape)
                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Dessiner la géométrie et les sommets des différences de l'élément courant sans rafraichir
                        Call bDessinerGeometrie(pConflitCourant, False, True, True)
                    End If

                    'Si le noeud parent est MODIFIER
                ElseIf pSelectNode.Parent.Parent.Name = "MODIFIER" Then
                    'Extraire l'élément courant
                    pRow = m_GererReplica.ExtraireElementParent(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément courant
                        pGeometry = pFeature.Shape
                        'Extraire l'élément d'archive
                        pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                        'Définir l'élément géographique
                        pFeature = CType(pRow, IFeature)
                        'Créer un Bag vide
                        pGeomBag = New GeometryBag
                        'Interface pour ajouter des composantes
                        pGeomColl = CType(pGeomBag, IGeometryCollection)
                        'Ajouter la géométrie de l'élément courant au Bag
                        pGeomColl.AddGeometry(pGeometry)
                        'Ajouter la géométrie de l'élément d'archive au Bag
                        pGeomColl.AddGeometry(pFeature.Shape)
                        'Zoom selon les géométries de l'élément
                        Call ZoomToGeometry(CType(pGeomBag, IGeometry))

                        'Extraire les différences entre les géométries
                        Call ExtraireDifferencesGeometrie(pGeometry, pFeature.Shape, pConflitCourant, pConflitArchive, lblNbConflits.Text)

                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Dessiner la géométrie et les sommets des différences de l'élément d'archive sans rafraichir
                        Call bDessinerGeometrie(pConflitArchive, False, True, True)

                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Dessiner la géométrie et les sommets des différences de l'élément courant sans rafraichir
                        Call bDessinerGeometrie(pConflitCourant, False, True, True)
                    End If
                End If

                'Sinon c'est un noeud d'attribut
            Else
                'Afficher l'information du noeud parent
                Call AfficherInfoConflits(pSelectNode.Parent)

                'Afficher l'information
                lblNbConflits.Text = "Valeurs d'attribut en conflit = " & pSelectNode.Text
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
            pRow = Nothing
            pFeature = Nothing
            pGeomBag = Nothing
            pGeomColl = Nothing
            pGeometry = Nothing
            pConflitCourant = Nothing
            pConflitArchive = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'afficher/dessiner l'information sur les différences à partir d'un noeud sélectionné d'un TreeView.
    '''</summary>
    '''
    '''<param name="pSelectNode">Noeud sélectionné d'un TreeView.</param>
    ''' 
    Public Sub AfficherInfoDifferences(ByVal pSelectNode As TreeNode)
        'Déclarer les variables de travail
        Dim pNodeClasse As TreeNode = Nothing           'Contient le noeud de la classe.
        Dim pRow As IRow = Nothing                      'Interface contenant un élément.
        Dim pFeatureCourant As IFeature = Nothing       'Interface contenant un élément courant.
        Dim pFeatureArchive As IFeature = Nothing       'Interface contenant un élément d'archive.
        Dim pGeomBag As IGeometryBag = Nothing          'Interface contenant les géométries d'un élément.
        Dim pGeomColl As IGeometryCollection = Nothing  'Interface contenant les géométries d'un élément.
        Dim pGeometryCourant As IGeometry = Nothing     'Interface contenant la géométrie d'un élément courant.
        Dim pGeometryArchive As IGeometry = Nothing     'Interface contenant la géométrie d'un élément de l'archive.
        Dim pDiffCourant As IGeometry = Nothing         'Interface contenant la géométrie d'un élément courant.
        Dim pDiffArchive As IGeometry = Nothing         'Interface contenant la géométrie d'un élément d'archive.
        Dim iNbElements As Integer = 0                  'Contient le nombre d'éléments.
        Dim iNbAttributs As Integer = 0                 'Contient le nombre dattributs d'éléments.

        Try
            'Activer les boutons pour gérer les différences
            cboRechercherDifferences.Enabled = True
            btnRechercherDifferencesAvecConflits.Enabled = False
            btnRechercherDifferencesSansConflits.Enabled = False
            btnOuvrirFermerDifferences.Enabled = False
            btnRefuserActionEnfant.Enabled = False
            btnAccepterActionEnfant.Enabled = False
            'Vérifier s'il y a des différences
            If treDifferences.Nodes.Count > 0 Then
                If treDifferences.Nodes.Item(0).Nodes.Count > 0 Then
                    'Activer les boutons pour les différences
                    cboRechercherDifferences.Enabled = True
                    btnRechercherDifferencesAvecConflits.Enabled = True
                    btnRechercherDifferencesSansConflits.Enabled = True
                    btnOuvrirFermerDifferences.Enabled = True
                    btnRefuserActionEnfant.Enabled = True
                    'Vérifier s'il n'y a pas de conflit
                    If m_GererReplica.NbConflits = 0 Then
                        btnAccepterActionEnfant.Enabled = True
                    End If
                End If
            End If

            'Si le noeud est RESULTAT
            If pSelectNode.Tag.ToString = "RESULTAT" Then
                'Afficher l'information
                lblNbDifferences.Text = "Nombre d'attributs trouvés = " & pSelectNode.Nodes.Count.ToString

                'Si le noeud est REPLICA
            ElseIf pSelectNode.Tag.ToString = "REPLICA" Then
                'Traiter toutes les classes
                Call m_GererReplica.CalculerDifferences(pSelectNode, iNbElements, iNbAttributs)
                'Afficher l'information
                lblNbDifferences.Text = "Nombre de différences : NbElements=" & iNbElements.ToString & " , NbAttributs=" & iNbAttributs.ToString

                'Si le noeud est CLASSE
            ElseIf pSelectNode.Tag.ToString = "CLASSE" Then
                'Traiter toutes les classes
                Call m_GererReplica.CalculerDifferences(pSelectNode, iNbElements, iNbAttributs)
                'Afficher l'information
                lblNbDifferences.Text = "Nombre de différences : NbElements=" & iNbElements.ToString & " , NbAttributs=" & iNbAttributs.ToString

                'Si le noeud est ETAT
            ElseIf pSelectNode.Tag.ToString = "ETAT" Then
                'Traiter toutes les classes
                Call m_GererReplica.CalculerDifferences(pSelectNode, iNbElements, iNbAttributs)
                'Afficher l'information
                lblNbDifferences.Text = "Nombre de différences : NbElements=" & iNbElements.ToString & " , NbAttributs=" & iNbAttributs.ToString

                'Si c'est un noeud d'élément
            ElseIf pSelectNode.Tag.ToString = "ELEMENT" Then
                'Afficher l'information
                lblNbDifferences.Text = "Nombre d'attributs différents = " & pSelectNode.Nodes.Count.ToString

                'Si le noeud parent est DETRUIRE
                If pSelectNode.Parent.Name = "DETRUIRE" Then
                    'Définir l'élément d'archive
                    pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément d'archive
                        pFeatureArchive = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément d'archive
                        pGeometryArchive = pFeatureArchive.ShapeCopy
                        'Projeter la géométrie de l'élément d'archive selon la référence spatiale de la Map active
                        pGeometryArchive.Project(m_MxDocument.FocusMap.SpatialReference)

                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Zoom selon la géométrie de l'élément d'archive
                        Call ZoomToGeometry(pGeometryArchive)
                        'Dessiner la géométrie et les sommets de l'élément sans rafraichir
                        Call bDessinerGeometrie(pGeometryArchive, False, True, True)
                    End If

                    'Si le noeud parent est AJOUTER
                ElseIf pSelectNode.Parent.Name = "AJOUTER" Then
                    'Définir l'élément courant
                    pRow = m_GererReplica.ExtraireElementEnfant(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément courant
                        pFeatureCourant = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément courant
                        pGeometryCourant = pFeatureCourant.ShapeCopy
                        'Projeter la géométrie de l'élément courant selon la référence spatiale de la Map active
                        pGeometryCourant.Project(m_MxDocument.FocusMap.SpatialReference)

                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Zoom selon la géométrie de l'élément courant
                        Call ZoomToGeometry(pGeometryCourant)
                        'Dessiner la géométrie et les sommets de l'élément sans rafraichir
                        Call bDessinerGeometrie(pGeometryCourant, False, True, True)
                    End If

                    'Si le noeud parent est MODIFIER
                ElseIf pSelectNode.Parent.Name = "MODIFIER" Then
                    'Définir l'élément d'archive
                    pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément d'archive
                        pFeatureArchive = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément d'archive
                        pGeometryArchive = pFeatureArchive.ShapeCopy
                        'Projeter la géométrie de l'élément d'archive selon la référence spatiale de la Map active
                        pGeometryArchive.Project(m_MxDocument.FocusMap.SpatialReference)
                        'Définir la géométrie de l'élément d'archive
                        pDiffArchive = pGeometryArchive

                        'Définir l'élément courant
                        pRow = m_GererReplica.ExtraireElementEnfant(CInt(pSelectNode.Name), pSelectNode.Parent.Parent.Name)
                        'Définir l'élément géographique
                        pFeatureCourant = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément courant
                        pGeometryCourant = pFeatureCourant.ShapeCopy
                        'Projeter la géométrie de l'élément courant selon la référence spatiale de la Map active
                        pGeometryCourant.Project(m_MxDocument.FocusMap.SpatialReference)
                        'Définir la géométrie de l'élément courant
                        pDiffCourant = pGeometryCourant

                        'Créer un Bag vide
                        pGeomBag = New GeometryBag
                        pGeomBag.SpatialReference = m_MxDocument.FocusMap.SpatialReference
                        'Interface pour ajouter des composantes
                        pGeomColl = CType(pGeomBag, IGeometryCollection)
                        'Ajouter la géométrie de l'élément courant au Bag
                        pGeomColl.AddGeometry(pDiffCourant)
                        'Ajouter la géométrie de l'élément d'archive au Bag
                        pGeomColl.AddGeometry(pDiffArchive)
                        'Zoom selon les géométries de l'élément
                        Call ZoomToGeometry(CType(pGeomBag, IGeometry))

                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Dessiner la géométrie et les sommets de l'élément d'archive sans rafraichir
                        Call bDessinerGeometrie(pDiffArchive, False, True, True)

                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Dessiner la géométrie et les sommets de l'élément courant sans rafraichir
                        Call bDessinerGeometrie(pDiffCourant, False, True, True)
                    End If
                End If

                'Sinon c'est un noeud de géométrie
            ElseIf pSelectNode.Tag.ToString = "GEOMETRIE" Then
                'Si le noeud parent est DETRUIRE
                If pSelectNode.Parent.Parent.Name = "DETRUIRE" Then
                    'Définir l'élément d'archive
                    pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément d'archive
                        pFeatureArchive = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément d'archive
                        pGeometryArchive = pFeatureArchive.ShapeCopy
                        'Projeter la géométrie de l'élément d'archive selon la référence spatiale de la Map active
                        pGeometryArchive.Project(m_MxDocument.FocusMap.SpatialReference)

                        'Définir la géométrie de l'élément courant à partir de celui de l'archive
                        pGeometryCourant = pFeatureArchive.ShapeCopy
                        'Projeter la géométrie de l'élément courant selon la référence spatiale de la Map active
                        pGeometryCourant.Project(m_MxDocument.FocusMap.SpatialReference)
                        'Définir la géométrie de l'élément courant
                        pGeometryCourant.SetEmpty()

                        'Extraire les différences entre les géométries
                        Call ExtraireDifferencesGeometrie(pGeometryCourant, pGeometryArchive, pDiffCourant, pDiffArchive, lblNbDifferences.Text)
                        'Zoom selon la géométrie de l'élément d'archive
                        Call ZoomToGeometry(pGeometryArchive)
                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Dessiner la géométrie et les sommets des différences de l'élément d'archive sans rafraichir
                        Call bDessinerGeometrie(pDiffArchive, False, True, True)
                    End If

                    'Si le noeud parent est AJOUTER
                ElseIf pSelectNode.Parent.Parent.Name = "AJOUTER" Then
                    'Définir l'élément courant
                    pRow = m_GererReplica.ExtraireElementEnfant(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément géographique
                        pFeatureCourant = CType(pRow, IFeature)
                        'Copier la géométrie de l'élément
                        pGeometryCourant = pFeatureCourant.ShapeCopy
                        'Projeter la géométrie de l'élément courant selon la référence spatiale de la Map active
                        pGeometryCourant.Project(m_MxDocument.FocusMap.SpatialReference)

                        'Définir la géométrie d'archive à partir du courant
                        pGeometryArchive = pFeatureCourant.ShapeCopy
                        'Projeter la géométrie de l'élément d'archive selon la référence spatiale de la Map active
                        pGeometryArchive.Project(m_MxDocument.FocusMap.SpatialReference)
                        'Définir la géométrie de l'élément d'archive
                        pGeometryArchive.SetEmpty()

                        'Extraire les différences entre les géométries
                        Call ExtraireDifferencesGeometrie(pGeometryCourant, pGeometryArchive, pDiffCourant, pDiffArchive, lblNbDifferences.Text)
                        'Zoom selon la géométrie de l'élément
                        Call ZoomToGeometry(pGeometryCourant)
                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Dessiner la géométrie et les sommets des différences de l'élément courant sans rafraichir
                        Call bDessinerGeometrie(pDiffCourant, False, True, True)
                    End If

                    'Si le noeud parent est MODIFIER
                ElseIf pSelectNode.Parent.Parent.Name = "MODIFIER" Then
                    'Extraire l'élément courant
                    pRow = m_GererReplica.ExtraireElementEnfant(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                    'Vérifier si l'élément est géographique
                    If TypeOf (pRow) Is IFeature Then
                        'Définir l'élément courant
                        pFeatureCourant = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément courant
                        pGeometryCourant = pFeatureCourant.ShapeCopy
                        'Projeter la géométrie de l'élément courant selon la référence spatiale de la Map active
                        pGeometryCourant.Project(m_MxDocument.FocusMap.SpatialReference)

                        'Extraire l'élément d'archive
                        pRow = m_GererReplica.ExtraireElementArchive(CInt(pSelectNode.Parent.Name), pSelectNode.Parent.Parent.Parent.Name)
                        'Définir l'élément d'archive
                        pFeatureArchive = CType(pRow, IFeature)
                        'Définir la géométrie de l'élément d'archive
                        pGeometryArchive = pFeatureArchive.ShapeCopy
                        'Projeter la géométrie de l'élément courant selon la référence spatiale de la Map active
                        pGeometryArchive.Project(m_MxDocument.FocusMap.SpatialReference)

                        'Créer un Bag vide
                        pGeomBag = New GeometryBag
                        pGeomBag.SpatialReference = m_MxDocument.FocusMap.SpatialReference
                        'Interface pour ajouter des composantes
                        pGeomColl = CType(pGeomBag, IGeometryCollection)
                        'Ajouter la géométrie de l'élément courant au Bag
                        pGeomColl.AddGeometry(pGeometryCourant)
                        'Ajouter la géométrie de l'élément d'archive au Bag
                        pGeomColl.AddGeometry(pGeometryArchive)

                        'Zoom selon les géométries courant et archive
                        Call ZoomToGeometry(CType(pGeomBag, IGeometry))

                        'Extraire les différences entre les géométries
                        Call ExtraireDifferencesGeometrie(pGeometryCourant, pGeometryArchive, pDiffCourant, pDiffArchive, lblNbDifferences.Text)

                        'Initialiser la symbologie pour les éléments d'archive
                        Call InitSymboleArchive()
                        'Dessiner la géométrie et les sommets des différences de l'élément d'archive sans rafraichir
                        Call bDessinerGeometrie(pDiffArchive, False, True, True)

                        'Initialiser la symbologie pour les éléments courant
                        Call InitSymboleCourant()
                        'Dessiner la géométrie et les sommets des différences de l'élément courant sans rafraichir
                        Call bDessinerGeometrie(pDiffCourant, False, True, True)
                    End If
                End If

                'Sinon c'est un noeud d'attribut
            Else
                'Afficher l'information du noeud parent
                Call AfficherInfoDifferences(pSelectNode.Parent)

                'Afficher l'information
                lblNbDifferences.Text = "Valeurs d'attribut différentes = " & pSelectNode.Text
            End If

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeClasse = Nothing
            pRow = Nothing
            pFeatureCourant = Nothing
            pFeatureArchive = Nothing
            pGeomBag = Nothing
            pGeomColl = Nothing
            pGeometryCourant = Nothing
            pGeometryArchive = Nothing
            pDiffCourant = Nothing
            pDiffArchive = Nothing
        End Try
    End Sub
#End Region
End Class