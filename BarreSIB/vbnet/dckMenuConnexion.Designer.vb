<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class dckMenuConnexion
  Inherits System.Windows.Forms.UserControl

  'Form overrides dispose to clean up the component list.
  <System.Diagnostics.DebuggerNonUserCode()> _
  Protected Overrides Sub Dispose(ByVal disposing As Boolean)
    If disposing AndAlso components IsNot Nothing Then
      components.Dispose()
    End If
    MyBase.Dispose(disposing)
  End Sub

  'Required by the Windows Form Designer
  Private components As System.ComponentModel.IContainer

  'NOTE: The following procedure is required by the Windows Form Designer
  'It can be modified using the Windows Form Designer.  
  'Do not modify it using the code editor.
  <System.Diagnostics.DebuggerStepThrough()> _
  Private Sub InitializeComponent()
        Me.btnExecuter = New System.Windows.Forms.Button()
        Me.btnFermer = New System.Windows.Forms.Button()
        Me.lblUsager = New System.Windows.Forms.Label()
        Me.cboUsager = New System.Windows.Forms.ComboBox()
        Me.lblMotPasse = New System.Windows.Forms.Label()
        Me.txtMotPasse = New System.Windows.Forms.TextBox()
        Me.lblMessage = New System.Windows.Forms.Label()
        Me.rtxMessage = New System.Windows.Forms.RichTextBox()
        Me.SuspendLayout()
        '
        'btnExecuter
        '
        Me.btnExecuter.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.btnExecuter.Location = New System.Drawing.Point(0, 270)
        Me.btnExecuter.Name = "btnExecuter"
        Me.btnExecuter.Size = New System.Drawing.Size(300, 30)
        Me.btnExecuter.TabIndex = 0
        Me.btnExecuter.Text = "Executer"
        Me.btnExecuter.UseVisualStyleBackColor = True
        '
        'btnFermer
        '
        Me.btnFermer.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.btnFermer.Location = New System.Drawing.Point(0, 242)
        Me.btnFermer.Name = "btnFermer"
        Me.btnFermer.Size = New System.Drawing.Size(300, 28)
        Me.btnFermer.TabIndex = 1
        Me.btnFermer.Text = "Fermer"
        Me.btnFermer.UseVisualStyleBackColor = True
        '
        'lblUsager
        '
        Me.lblUsager.AutoSize = True
        Me.lblUsager.Dock = System.Windows.Forms.DockStyle.Top
        Me.lblUsager.Location = New System.Drawing.Point(0, 0)
        Me.lblUsager.Name = "lblUsager"
        Me.lblUsager.Size = New System.Drawing.Size(72, 13)
        Me.lblUsager.TabIndex = 7
        Me.lblUsager.Text = "Nom d'usager"
        '
        'cboUsager
        '
        Me.cboUsager.Dock = System.Windows.Forms.DockStyle.Top
        Me.cboUsager.FormattingEnabled = True
        Me.cboUsager.Location = New System.Drawing.Point(0, 13)
        Me.cboUsager.Name = "cboUsager"
        Me.cboUsager.Size = New System.Drawing.Size(300, 21)
        Me.cboUsager.TabIndex = 8
        '
        'lblMotPasse
        '
        Me.lblMotPasse.AutoSize = True
        Me.lblMotPasse.Dock = System.Windows.Forms.DockStyle.Top
        Me.lblMotPasse.Location = New System.Drawing.Point(0, 34)
        Me.lblMotPasse.Name = "lblMotPasse"
        Me.lblMotPasse.Size = New System.Drawing.Size(71, 13)
        Me.lblMotPasse.TabIndex = 9
        Me.lblMotPasse.Text = "Mot de passe"
        '
        'txtMotPasse
        '
        Me.txtMotPasse.Dock = System.Windows.Forms.DockStyle.Top
        Me.txtMotPasse.Location = New System.Drawing.Point(0, 47)
        Me.txtMotPasse.Name = "txtMotPasse"
        Me.txtMotPasse.Size = New System.Drawing.Size(300, 20)
        Me.txtMotPasse.TabIndex = 11
        Me.txtMotPasse.UseSystemPasswordChar = True
        '
        'lblMessage
        '
        Me.lblMessage.AutoSize = True
        Me.lblMessage.Dock = System.Windows.Forms.DockStyle.Top
        Me.lblMessage.Location = New System.Drawing.Point(0, 67)
        Me.lblMessage.Name = "lblMessage"
        Me.lblMessage.Size = New System.Drawing.Size(112, 13)
        Me.lblMessage.TabIndex = 13
        Me.lblMessage.Text = "Messages d'exécution"
        '
        'rtxMessage
        '
        Me.rtxMessage.Dock = System.Windows.Forms.DockStyle.Fill
        Me.rtxMessage.Location = New System.Drawing.Point(0, 80)
        Me.rtxMessage.Name = "rtxMessage"
        Me.rtxMessage.Size = New System.Drawing.Size(300, 162)
        Me.rtxMessage.TabIndex = 14
        Me.rtxMessage.Text = ""
        '
        'dckMenuConnexion
        '
        Me.Controls.Add(Me.rtxMessage)
        Me.Controls.Add(Me.lblMessage)
        Me.Controls.Add(Me.txtMotPasse)
        Me.Controls.Add(Me.lblMotPasse)
        Me.Controls.Add(Me.cboUsager)
        Me.Controls.Add(Me.lblUsager)
        Me.Controls.Add(Me.btnFermer)
        Me.Controls.Add(Me.btnExecuter)
        Me.Name = "dckMenuConnexion"
        Me.Size = New System.Drawing.Size(300, 300)
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents btnExecuter As System.Windows.Forms.Button
    Friend WithEvents btnFermer As System.Windows.Forms.Button
    Friend WithEvents lblUsager As System.Windows.Forms.Label
    Friend WithEvents cboUsager As System.Windows.Forms.ComboBox
    Friend WithEvents lblMotPasse As System.Windows.Forms.Label
    Friend WithEvents txtMotPasse As System.Windows.Forms.TextBox
    Friend WithEvents lblMessage As System.Windows.Forms.Label
    Friend WithEvents rtxMessage As System.Windows.Forms.RichTextBox

End Class
