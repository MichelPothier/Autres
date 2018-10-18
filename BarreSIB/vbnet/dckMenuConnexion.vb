Imports System.Windows.Forms
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.ArcMapUI
Imports System.Drawing
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.esriSystem

''' <summary>
''' Designer class of the dockable window add-in. It contains user interfaces that
''' make up the dockable window.
''' </summary>
Public Class dckMenuConnexion
    'Déclarer les variables de travail
    Private m_hook As Object

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

        Private m_windowUI As dckMenuConnexion

        Protected Overrides Function OnCreateChild() As System.IntPtr
            m_windowUI = New dckMenuConnexion(Me.Hook)
            Return m_windowUI.Handle
        End Function

        Protected Overrides Sub Dispose(ByVal Param As Boolean)
            If m_windowUI IsNot Nothing Then
                m_windowUI.Dispose(Param)
            End If

            MyBase.Dispose(Param)
        End Sub
    End Class

    '''<summary>
    ''' Routine qui permet d'initialiser le menu lors de la création du menu.
    '''</summary>
    '''
    Public Sub New(ByVal hook As Object)
        ' This call is required by the Windows Form Designer.
        InitializeComponent()

        ' Add any initialization after the InitializeComponent() call.
        Me.Hook = hook

        Try
            'Définir l'application
            m_Application = CType(hook, IApplication)

            'Définir le document
            m_MxDocument = CType(m_Application.Document, IMxDocument)

            'Définir le menu de connexion
            m_MenuConnexion = Me

            'Lire les valeurs par défaut dans le setting
            My.Settings.Reload()
            cboUsager.Text = My.Settings.username
            txtMotPasse.Text = My.Settings.password

            'Vérifier si l'usager n'est pas spécifié
            If cboUsager.Text.Length = 0 Then
                'Définir l'usager pas défaut via la variable d'environnement USERNAME
                cboUsager.Text = Environment.GetEnvironmentVariable("USERNAME")
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'afficher le menu.
    '''</summary>
    '''
    Public Overloads Sub Show(ByVal Show As Boolean)
        'Déclarer les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver un DockableWindow
        Dim pDockWindow As IDockableWindow 'Interface contenant le DockableWindow

        Try
            'Trouver le Dockable Window
            windowID.Value = "MPO_BarreSIB_dckMenuConnexion"
            pDockWindow = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
            pDockWindow.Show(Show)

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            windowID = Nothing
            pDockWindow = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'indiquer si le menu est affiché.
    '''</summary>
    '''
    Public Overloads Function IsVisible() As Boolean
        'Déclarer les variables de travail
        Dim windowID As UID = New UIDClass 'Interface pour trouver un DockableWindow
        Dim pDockWindow As IDockableWindow 'Interface contenant le DockableWindow

        Try
            'Trouver le Dockable Window
            windowID.Value = "MPO_BarreSIB_dckMenuConnexion"
            pDockWindow = My.ArcMap.DockableWindowManager.GetDockableWindow(windowID)
            Return pDockWindow.IsVisible

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            windowID = Nothing
            pDockWindow = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine appelée lorsque le focus est perdu sur le ComboBos de l'usager.
    '''</summary>
    '''
    Private Sub cboUsager_LostFocus(ByVal sender As Object, ByVal e As System.EventArgs) Handles cboUsager.LostFocus
        'Vérifier si l'usager est déjà présent
        If Not cboUsager.Items.Contains(cboUsager.Text) Then
            'Ajouter le nouveau text dans la liste des usagers
            cboUsager.Items.Add(cboUsager.Text)
        End If
    End Sub

    '''<summary>
    ''' Routine appelée lorsque la connexion à SIB est nécessaire.
    '''</summary>
    '''
    Private Sub btnExecuter_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnExecuter.Click
        'Déclarer les variables de travail
        Dim qProcess As Process 'Objet qui permet d'exécuter un traitement
        Dim qProcessInfo As ProcessStartInfo = New ProcessStartInfo() 'Objet qui permet de définir l'information d'un traitement
        Dim pMouseCursor As IMouseCursor = Nothing          'Interface qui permet de changer le curseur de la souris

        Try
            'Changer le curseur en Sablier pour montrer qu'une tâche est en cours
            pMouseCursor = New MouseCursorClass
            pMouseCursor.SetCursor(2)

            'Initialiser le text
            rtxMessage.Text = ""

            'Vérifier si le nom de l'usager est présent
            If cboUsager.Text.Length > 0 Then
                'Vérifier si le mot de passe est présent
                If txtMotPasse.Text.Length > 0 Then
                    'Définir le nom du fichier à exécuter
                    qProcessInfo.FileName = Environment.GetEnvironmentVariable("PYTHON27")
                    qProcessInfo.CreateNoWindow = True
                    qProcessInfo.UseShellExecute = False
                    qProcessInfo.WindowStyle = ProcessWindowStyle.Hidden
                    qProcessInfo.RedirectStandardOutput = True
                    qProcessInfo.RedirectStandardError = True

                    'Appel le script pour définir un mot de passe dans SIB_PRO
                    'Process.Start("S:\applications\sib\pro\py\ConnecterCompteSIB.py", "SIB_PRO sibapp $1bapp " + cboUsager.Text + " " + txtMotPasse.Text)
                    rtxMessage.AppendText("S:\applications\sib\pro\py\ConnecterCompteSIB.py SIB_PRO" + vbNewLine)
                    rtxMessage.ScrollToCaret()
                    qProcessInfo.Arguments = "S:\applications\sib\pro\py\ConnecterCompteSIB.py SIB_PRO sibapp $1bapp " + cboUsager.Text + " " + txtMotPasse.Text
                    qProcess = Process.Start(qProcessInfo)
                    qProcess.WaitForExit()
                    rtxMessage.Text = rtxMessage.Text + qProcess.StandardOutput.ReadToEnd

                    'Appel le script pour définir un mot de passe dans SIB_TST
                    'Process.Start("S:\applications\sib\pro\py\ConnecterCompteSIB.py", "SIB_TST sibapp sibapp " + cboUsager.Text + " " + txtMotPasse.Text)
                    rtxMessage.AppendText("S:\applications\sib\pro\py\ConnecterCompteSIB.py SIB_TST" + vbNewLine)
                    rtxMessage.ScrollToCaret()
                    qProcessInfo.Arguments = "S:\applications\sib\pro\py\ConnecterCompteSIB.py SIB_TST sibapp sibapp " + cboUsager.Text + " " + txtMotPasse.Text
                    qProcess = Process.Start(qProcessInfo)
                    qProcess.WaitForExit()
                    rtxMessage.AppendText(qProcess.StandardOutput.ReadToEnd)

                    'Appel le script pour définir un mot de passe dans BDG_SIB_TST
                    'Process.Start("S:\applications\sib\pro\py\ConnecterCompteSIB.py", "BDG_SIB_TST sibapp sibapp " + cboUsager.Text + " " + txtMotPasse.Text)
                    rtxMessage.AppendText("S:\applications\sib\pro\py\ConnecterCompteSIB.py BDG_SIB_TST" + vbNewLine)
                    rtxMessage.ScrollToCaret()
                    qProcessInfo.Arguments = "S:\applications\sib\pro\py\ConnecterCompteSIB.py BDG_SIB_TST sibapp sibapp " + cboUsager.Text + " " + txtMotPasse.Text
                    qProcess = Process.Start(qProcessInfo)
                    qProcess.WaitForExit()
                    rtxMessage.AppendText(qProcess.StandardOutput.ReadToEnd)

                    'Sauver les valeurs par défaut
                    My.Settings.Reload()
                    My.Settings.username = cboUsager.Text
                    My.Settings.password = txtMotPasse.Text
                    My.Settings.Save()
                End If
            End If

        Catch erreur As Exception
            'Message d'erreur
            MessageBox.Show(erreur.ToString, "", MessageBoxButtons.OK, MessageBoxIcon.Stop)
        Finally
            'Vider la mémoire
            qProcess = Nothing
            qProcessInfo = Nothing
            pMouseCursor = Nothing
        End Try

    End Sub

    '''<summary>
    ''' Routine appelée lorsqu'on veut annuler la connexion à SIB.
    '''</summary>
    '''
    Private Sub btnFermer_Click(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles btnFermer.Click
        'Cacher le menu
        Me.Show(False)
    End Sub
End Class