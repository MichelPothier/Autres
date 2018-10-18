<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class dckMenuRelations
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(dckMenuRelations))
        Me.sptRelations = New System.Windows.Forms.SplitContainer()
        Me.sptRelations2 = New System.Windows.Forms.SplitContainer()
        Me.treRelations = New System.Windows.Forms.TreeView()
        Me.tooRelations = New System.Windows.Forms.ToolStrip()
        Me.btnRafraichirRelations = New System.Windows.Forms.ToolStripButton()
        Me.btnCopierRelation = New System.Windows.Forms.ToolStripButton()
        Me.btnCollerRelation = New System.Windows.Forms.ToolStripButton()
        Me.btnDetruireRelation = New System.Windows.Forms.ToolStripButton()
        Me.btnAjouterRelation = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator2 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnOuvrirTable = New System.Windows.Forms.ToolStripButton()
        Me.btnIdentifier = New System.Windows.Forms.ToolStripButton()
        Me.lblRelations = New System.Windows.Forms.Label()
        Me.dgvListesAttributs = New System.Windows.Forms.DataGridView()
        Me.tooListesValeurs = New System.Windows.Forms.ToolStrip()
        Me.btnTransfererListes = New System.Windows.Forms.ToolStripButton()
        Me.btnTransfererListesTables = New System.Windows.Forms.ToolStripButton()
        Me.btnTransfererListesVides = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator1 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnAjouterListeAttributs = New System.Windows.Forms.ToolStripButton()
        Me.btnDetruireListeAttributs = New System.Windows.Forms.ToolStripButton()
        Me.lblAttribut = New System.Windows.Forms.Label()
        Me.rtxRequete = New System.Windows.Forms.RichTextBox()
        Me.tooRequete = New System.Windows.Forms.ToolStrip()
        Me.btnSelectionnerRequete = New System.Windows.Forms.ToolStripButton()
        Me.btnModifierRequete = New System.Windows.Forms.ToolStripButton()
        Me.btnDetruireRequete = New System.Windows.Forms.ToolStripButton()
        Me.btnRechercherRelation = New System.Windows.Forms.Button()
        Me.txtMessage = New System.Windows.Forms.TextBox()
        Me.lblRequete = New System.Windows.Forms.Label()
        CType(Me.sptRelations, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.sptRelations.Panel1.SuspendLayout()
        Me.sptRelations.Panel2.SuspendLayout()
        Me.sptRelations.SuspendLayout()
        CType(Me.sptRelations2, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.sptRelations2.Panel1.SuspendLayout()
        Me.sptRelations2.Panel2.SuspendLayout()
        Me.sptRelations2.SuspendLayout()
        Me.tooRelations.SuspendLayout()
        CType(Me.dgvListesAttributs, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.tooListesValeurs.SuspendLayout()
        Me.tooRequete.SuspendLayout()
        Me.SuspendLayout()
        '
        'sptRelations
        '
        Me.sptRelations.Dock = System.Windows.Forms.DockStyle.Fill
        Me.sptRelations.Location = New System.Drawing.Point(0, 0)
        Me.sptRelations.Name = "sptRelations"
        Me.sptRelations.Orientation = System.Windows.Forms.Orientation.Horizontal
        '
        'sptRelations.Panel1
        '
        Me.sptRelations.Panel1.Controls.Add(Me.sptRelations2)
        '
        'sptRelations.Panel2
        '
        Me.sptRelations.Panel2.Controls.Add(Me.rtxRequete)
        Me.sptRelations.Panel2.Controls.Add(Me.tooRequete)
        Me.sptRelations.Panel2.Controls.Add(Me.btnRechercherRelation)
        Me.sptRelations.Panel2.Controls.Add(Me.txtMessage)
        Me.sptRelations.Panel2.Controls.Add(Me.lblRequete)
        Me.sptRelations.Size = New System.Drawing.Size(300, 300)
        Me.sptRelations.SplitterDistance = 191
        Me.sptRelations.TabIndex = 0
        '
        'sptRelations2
        '
        Me.sptRelations2.Dock = System.Windows.Forms.DockStyle.Fill
        Me.sptRelations2.Location = New System.Drawing.Point(0, 0)
        Me.sptRelations2.Name = "sptRelations2"
        Me.sptRelations2.Orientation = System.Windows.Forms.Orientation.Horizontal
        '
        'sptRelations2.Panel1
        '
        Me.sptRelations2.Panel1.Controls.Add(Me.treRelations)
        Me.sptRelations2.Panel1.Controls.Add(Me.tooRelations)
        Me.sptRelations2.Panel1.Controls.Add(Me.lblRelations)
        '
        'sptRelations2.Panel2
        '
        Me.sptRelations2.Panel2.Controls.Add(Me.dgvListesAttributs)
        Me.sptRelations2.Panel2.Controls.Add(Me.tooListesValeurs)
        Me.sptRelations2.Panel2.Controls.Add(Me.lblAttribut)
        Me.sptRelations2.Size = New System.Drawing.Size(300, 191)
        Me.sptRelations2.SplitterDistance = 109
        Me.sptRelations2.TabIndex = 5
        '
        'treRelations
        '
        Me.treRelations.AllowDrop = True
        Me.treRelations.Dock = System.Windows.Forms.DockStyle.Fill
        Me.treRelations.HideSelection = False
        Me.treRelations.Location = New System.Drawing.Point(0, 38)
        Me.treRelations.Name = "treRelations"
        Me.treRelations.Size = New System.Drawing.Size(300, 71)
        Me.treRelations.TabIndex = 7
        '
        'tooRelations
        '
        Me.tooRelations.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnRafraichirRelations, Me.btnCopierRelation, Me.btnCollerRelation, Me.btnDetruireRelation, Me.btnAjouterRelation, Me.ToolStripSeparator2, Me.btnOuvrirTable, Me.btnIdentifier})
        Me.tooRelations.Location = New System.Drawing.Point(0, 13)
        Me.tooRelations.Name = "tooRelations"
        Me.tooRelations.Size = New System.Drawing.Size(300, 25)
        Me.tooRelations.TabIndex = 6
        Me.tooRelations.Text = "ToolStrip1"
        '
        'btnRafraichirRelations
        '
        Me.btnRafraichirRelations.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRafraichirRelations.Image = CType(resources.GetObject("btnRafraichirRelations.Image"), System.Drawing.Image)
        Me.btnRafraichirRelations.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRafraichirRelations.Name = "btnRafraichirRelations"
        Me.btnRafraichirRelations.Size = New System.Drawing.Size(23, 22)
        Me.btnRafraichirRelations.Text = "Rafraîchir la structure des relations entre les tables"
        '
        'btnCopierRelation
        '
        Me.btnCopierRelation.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnCopierRelation.Image = CType(resources.GetObject("btnCopierRelation.Image"), System.Drawing.Image)
        Me.btnCopierRelation.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnCopierRelation.Name = "btnCopierRelation"
        Me.btnCopierRelation.Size = New System.Drawing.Size(23, 22)
        Me.btnCopierRelation.Text = "Copier la relation de la table sélectionnée en mémoire"
        '
        'btnCollerRelation
        '
        Me.btnCollerRelation.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnCollerRelation.Enabled = False
        Me.btnCollerRelation.Image = CType(resources.GetObject("btnCollerRelation.Image"), System.Drawing.Image)
        Me.btnCollerRelation.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnCollerRelation.Name = "btnCollerRelation"
        Me.btnCollerRelation.Size = New System.Drawing.Size(23, 22)
        Me.btnCollerRelation.Text = "Coller la relation en mémoire dans la table sélectionnée"
        '
        'btnDetruireRelation
        '
        Me.btnDetruireRelation.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnDetruireRelation.Image = CType(resources.GetObject("btnDetruireRelation.Image"), System.Drawing.Image)
        Me.btnDetruireRelation.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnDetruireRelation.Name = "btnDetruireRelation"
        Me.btnDetruireRelation.Size = New System.Drawing.Size(23, 22)
        Me.btnDetruireRelation.Text = "Détruire la relation de la table sélectionnée"
        '
        'btnAjouterRelation
        '
        Me.btnAjouterRelation.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnAjouterRelation.Image = CType(resources.GetObject("btnAjouterRelation.Image"), System.Drawing.Image)
        Me.btnAjouterRelation.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnAjouterRelation.Name = "btnAjouterRelation"
        Me.btnAjouterRelation.Size = New System.Drawing.Size(23, 22)
        Me.btnAjouterRelation.Text = "Ajouter une relation à partir du menu de construction"
        '
        'ToolStripSeparator2
        '
        Me.ToolStripSeparator2.Name = "ToolStripSeparator2"
        Me.ToolStripSeparator2.Size = New System.Drawing.Size(6, 25)
        '
        'btnOuvrirTable
        '
        Me.btnOuvrirTable.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnOuvrirTable.Image = CType(resources.GetObject("btnOuvrirTable.Image"), System.Drawing.Image)
        Me.btnOuvrirTable.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnOuvrirTable.Name = "btnOuvrirTable"
        Me.btnOuvrirTable.Size = New System.Drawing.Size(23, 22)
        Me.btnOuvrirTable.Text = "Ouvrir la table sélectionnée"
        '
        'btnIdentifier
        '
        Me.btnIdentifier.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnIdentifier.Image = CType(resources.GetObject("btnIdentifier.Image"), System.Drawing.Image)
        Me.btnIdentifier.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnIdentifier.Name = "btnIdentifier"
        Me.btnIdentifier.Size = New System.Drawing.Size(23, 22)
        Me.btnIdentifier.Text = "Identifer les éléments sélectionnés de la table sélectionnée"
        '
        'lblRelations
        '
        Me.lblRelations.AutoSize = True
        Me.lblRelations.Dock = System.Windows.Forms.DockStyle.Top
        Me.lblRelations.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblRelations.Location = New System.Drawing.Point(0, 0)
        Me.lblRelations.Name = "lblRelations"
        Me.lblRelations.Size = New System.Drawing.Size(226, 13)
        Me.lblRelations.TabIndex = 2
        Me.lblRelations.Text = "Structure des relations entre les tables"
        '
        'dgvListesAttributs
        '
        Me.dgvListesAttributs.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill
        Me.dgvListesAttributs.BackgroundColor = System.Drawing.SystemColors.ButtonHighlight
        Me.dgvListesAttributs.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.dgvListesAttributs.Dock = System.Windows.Forms.DockStyle.Fill
        Me.dgvListesAttributs.EditMode = System.Windows.Forms.DataGridViewEditMode.EditOnKeystroke
        Me.dgvListesAttributs.Location = New System.Drawing.Point(0, 38)
        Me.dgvListesAttributs.MultiSelect = False
        Me.dgvListesAttributs.Name = "dgvListesAttributs"
        Me.dgvListesAttributs.RowHeadersVisible = False
        Me.dgvListesAttributs.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect
        Me.dgvListesAttributs.Size = New System.Drawing.Size(300, 40)
        Me.dgvListesAttributs.TabIndex = 5
        '
        'tooListesValeurs
        '
        Me.tooListesValeurs.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnTransfererListes, Me.btnTransfererListesTables, Me.btnTransfererListesVides, Me.ToolStripSeparator1, Me.btnAjouterListeAttributs, Me.btnDetruireListeAttributs})
        Me.tooListesValeurs.Location = New System.Drawing.Point(0, 13)
        Me.tooListesValeurs.Name = "tooListesValeurs"
        Me.tooListesValeurs.Size = New System.Drawing.Size(300, 25)
        Me.tooListesValeurs.TabIndex = 4
        Me.tooListesValeurs.Text = "Liste des valeurs"
        '
        'btnTransfererListes
        '
        Me.btnTransfererListes.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnTransfererListes.Image = CType(resources.GetObject("btnTransfererListes.Image"), System.Drawing.Image)
        Me.btnTransfererListes.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnTransfererListes.Name = "btnTransfererListes"
        Me.btnTransfererListes.Size = New System.Drawing.Size(23, 22)
        Me.btnTransfererListes.Text = "Construire et transférer la requête dans la table sélectionnée"
        '
        'btnTransfererListesTables
        '
        Me.btnTransfererListesTables.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnTransfererListesTables.Image = CType(resources.GetObject("btnTransfererListesTables.Image"), System.Drawing.Image)
        Me.btnTransfererListesTables.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnTransfererListesTables.Name = "btnTransfererListesTables"
        Me.btnTransfererListesTables.Size = New System.Drawing.Size(23, 22)
        Me.btnTransfererListesTables.Text = "Construire et transférer la requête dans toutes les tables en relation avec la ta" & _
    "ble sélectionnée"
        '
        'btnTransfererListesVides
        '
        Me.btnTransfererListesVides.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnTransfererListesVides.Image = CType(resources.GetObject("btnTransfererListesVides.Image"), System.Drawing.Image)
        Me.btnTransfererListesVides.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnTransfererListesVides.Name = "btnTransfererListesVides"
        Me.btnTransfererListesVides.Size = New System.Drawing.Size(23, 22)
        Me.btnTransfererListesVides.Text = "Détruire la requête dans toutes les tables en relation avec la table sélectionée"
        '
        'ToolStripSeparator1
        '
        Me.ToolStripSeparator1.Name = "ToolStripSeparator1"
        Me.ToolStripSeparator1.Size = New System.Drawing.Size(6, 25)
        '
        'btnAjouterListeAttributs
        '
        Me.btnAjouterListeAttributs.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnAjouterListeAttributs.Image = CType(resources.GetObject("btnAjouterListeAttributs.Image"), System.Drawing.Image)
        Me.btnAjouterListeAttributs.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnAjouterListeAttributs.Name = "btnAjouterListeAttributs"
        Me.btnAjouterListeAttributs.Size = New System.Drawing.Size(23, 22)
        Me.btnAjouterListeAttributs.Text = "Ajouter les valeurs d'attributs dans la liste en mémoire"
        '
        'btnDetruireListeAttributs
        '
        Me.btnDetruireListeAttributs.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnDetruireListeAttributs.Image = CType(resources.GetObject("btnDetruireListeAttributs.Image"), System.Drawing.Image)
        Me.btnDetruireListeAttributs.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnDetruireListeAttributs.Name = "btnDetruireListeAttributs"
        Me.btnDetruireListeAttributs.Size = New System.Drawing.Size(23, 22)
        Me.btnDetruireListeAttributs.Text = "Détruire les valeurs d'attributs dans la liste en mémoire"
        '
        'lblAttribut
        '
        Me.lblAttribut.AutoSize = True
        Me.lblAttribut.Dock = System.Windows.Forms.DockStyle.Top
        Me.lblAttribut.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblAttribut.Location = New System.Drawing.Point(0, 0)
        Me.lblAttribut.Name = "lblAttribut"
        Me.lblAttribut.Size = New System.Drawing.Size(167, 13)
        Me.lblAttribut.TabIndex = 0
        Me.lblAttribut.Text = "Liste des valeurs d'attributs "
        '
        'rtxRequete
        '
        Me.rtxRequete.Dock = System.Windows.Forms.DockStyle.Fill
        Me.rtxRequete.Location = New System.Drawing.Point(0, 38)
        Me.rtxRequete.Name = "rtxRequete"
        Me.rtxRequete.Size = New System.Drawing.Size(300, 20)
        Me.rtxRequete.TabIndex = 16
        Me.rtxRequete.Text = ""
        '
        'tooRequete
        '
        Me.tooRequete.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnSelectionnerRequete, Me.btnModifierRequete, Me.btnDetruireRequete})
        Me.tooRequete.Location = New System.Drawing.Point(0, 13)
        Me.tooRequete.Name = "tooRequete"
        Me.tooRequete.Size = New System.Drawing.Size(300, 25)
        Me.tooRequete.TabIndex = 15
        Me.tooRequete.Text = "ToolStrip1"
        '
        'btnSelectionnerRequete
        '
        Me.btnSelectionnerRequete.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnSelectionnerRequete.Image = CType(resources.GetObject("btnSelectionnerRequete.Image"), System.Drawing.Image)
        Me.btnSelectionnerRequete.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnSelectionnerRequete.Name = "btnSelectionnerRequete"
        Me.btnSelectionnerRequete.Size = New System.Drawing.Size(23, 22)
        Me.btnSelectionnerRequete.Text = "Sélectionner les éléments de la table sélectionnée en fonction de la requête attr" & _
    "ibutive"
        '
        'btnModifierRequete
        '
        Me.btnModifierRequete.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnModifierRequete.Image = CType(resources.GetObject("btnModifierRequete.Image"), System.Drawing.Image)
        Me.btnModifierRequete.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnModifierRequete.Name = "btnModifierRequete"
        Me.btnModifierRequete.Size = New System.Drawing.Size(23, 22)
        Me.btnModifierRequete.Text = "Modifier la requête attributive de la table sélectionnée à partir du menu de cons" & _
    "truction"
        '
        'btnDetruireRequete
        '
        Me.btnDetruireRequete.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnDetruireRequete.Image = CType(resources.GetObject("btnDetruireRequete.Image"), System.Drawing.Image)
        Me.btnDetruireRequete.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnDetruireRequete.Name = "btnDetruireRequete"
        Me.btnDetruireRequete.Size = New System.Drawing.Size(23, 22)
        Me.btnDetruireRequete.Text = "Détruire la requête attributive de la table sélectionnée"
        '
        'btnRechercherRelation
        '
        Me.btnRechercherRelation.BackColor = System.Drawing.SystemColors.GradientActiveCaption
        Me.btnRechercherRelation.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.btnRechercherRelation.Location = New System.Drawing.Point(0, 58)
        Me.btnRechercherRelation.Name = "btnRechercherRelation"
        Me.btnRechercherRelation.Size = New System.Drawing.Size(300, 27)
        Me.btnRechercherRelation.TabIndex = 9
        Me.btnRechercherRelation.Text = "Rechercher les éléments parents ..."
        Me.btnRechercherRelation.UseVisualStyleBackColor = False
        '
        'txtMessage
        '
        Me.txtMessage.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.txtMessage.Location = New System.Drawing.Point(0, 85)
        Me.txtMessage.Name = "txtMessage"
        Me.txtMessage.Size = New System.Drawing.Size(300, 20)
        Me.txtMessage.TabIndex = 8
        '
        'lblRequete
        '
        Me.lblRequete.AutoSize = True
        Me.lblRequete.Dock = System.Windows.Forms.DockStyle.Top
        Me.lblRequete.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.lblRequete.Location = New System.Drawing.Point(0, 0)
        Me.lblRequete.Name = "lblRequete"
        Me.lblRequete.Size = New System.Drawing.Size(256, 13)
        Me.lblRequete.TabIndex = 0
        Me.lblRequete.Text = "Requête attributive de la table sélectionnée"
        '
        'dckMenuRelations
        '
        Me.Controls.Add(Me.sptRelations)
        Me.Name = "dckMenuRelations"
        Me.Size = New System.Drawing.Size(300, 300)
        Me.sptRelations.Panel1.ResumeLayout(False)
        Me.sptRelations.Panel2.ResumeLayout(False)
        Me.sptRelations.Panel2.PerformLayout()
        CType(Me.sptRelations, System.ComponentModel.ISupportInitialize).EndInit()
        Me.sptRelations.ResumeLayout(False)
        Me.sptRelations2.Panel1.ResumeLayout(False)
        Me.sptRelations2.Panel1.PerformLayout()
        Me.sptRelations2.Panel2.ResumeLayout(False)
        Me.sptRelations2.Panel2.PerformLayout()
        CType(Me.sptRelations2, System.ComponentModel.ISupportInitialize).EndInit()
        Me.sptRelations2.ResumeLayout(False)
        Me.tooRelations.ResumeLayout(False)
        Me.tooRelations.PerformLayout()
        CType(Me.dgvListesAttributs, System.ComponentModel.ISupportInitialize).EndInit()
        Me.tooListesValeurs.ResumeLayout(False)
        Me.tooListesValeurs.PerformLayout()
        Me.tooRequete.ResumeLayout(False)
        Me.tooRequete.PerformLayout()
        Me.ResumeLayout(False)

    End Sub
    Friend WithEvents sptRelations As System.Windows.Forms.SplitContainer
    Friend WithEvents lblRequete As System.Windows.Forms.Label
    Friend WithEvents btnRechercherRelation As System.Windows.Forms.Button
    Friend WithEvents txtMessage As System.Windows.Forms.TextBox
    Friend WithEvents sptRelations2 As System.Windows.Forms.SplitContainer
    Friend WithEvents lblRelations As System.Windows.Forms.Label
    Friend WithEvents lblAttribut As System.Windows.Forms.Label
    Friend WithEvents dgvListesAttributs As System.Windows.Forms.DataGridView
    Friend WithEvents tooListesValeurs As System.Windows.Forms.ToolStrip
    Friend WithEvents btnTransfererListes As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnTransfererListesTables As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnTransfererListesVides As System.Windows.Forms.ToolStripButton
    Friend WithEvents tooRelations As System.Windows.Forms.ToolStrip
    Friend WithEvents btnRafraichirRelations As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnCopierRelation As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnCollerRelation As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnDetruireRelation As System.Windows.Forms.ToolStripButton
    Friend WithEvents treRelations As System.Windows.Forms.TreeView
    Friend WithEvents rtxRequete As System.Windows.Forms.RichTextBox
    Friend WithEvents tooRequete As System.Windows.Forms.ToolStrip
    Friend WithEvents btnSelectionnerRequete As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnModifierRequete As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnDetruireRequete As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnAjouterRelation As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnOuvrirTable As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnIdentifier As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnDetruireListeAttributs As System.Windows.Forms.ToolStripButton
    Friend WithEvents ToolStripSeparator2 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents ToolStripSeparator1 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents btnAjouterListeAttributs As System.Windows.Forms.ToolStripButton

End Class
