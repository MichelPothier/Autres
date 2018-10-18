<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class dckMenuIdentification
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(dckMenuIdentification))
        Dim DataGridViewCellStyle1 As System.Windows.Forms.DataGridViewCellStyle = New System.Windows.Forms.DataGridViewCellStyle()
        Me.lblInformation = New System.Windows.Forms.Label()
        Me.sptIdentification = New System.Windows.Forms.SplitContainer()
        Me.treIdentification = New System.Windows.Forms.TreeView()
        Me.tooIdentification = New System.Windows.Forms.ToolStrip()
        Me.btnRafraichir = New System.Windows.Forms.ToolStripButton()
        Me.cboTrier = New System.Windows.Forms.ToolStripComboBox()
        Me.txtMaxItem = New System.Windows.Forms.ToolStripTextBox()
        Me.dgvIdentification = New System.Windows.Forms.DataGridView()
        CType(Me.sptIdentification, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.sptIdentification.Panel1.SuspendLayout()
        Me.sptIdentification.Panel2.SuspendLayout()
        Me.sptIdentification.SuspendLayout()
        Me.tooIdentification.SuspendLayout()
        CType(Me.dgvIdentification, System.ComponentModel.ISupportInitialize).BeginInit()
        Me.SuspendLayout()
        '
        'lblInformation
        '
        Me.lblInformation.AutoSize = True
        Me.lblInformation.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.lblInformation.Location = New System.Drawing.Point(0, 317)
        Me.lblInformation.Name = "lblInformation"
        Me.lblInformation.Size = New System.Drawing.Size(115, 13)
        Me.lblInformation.TabIndex = 0
        Me.lblInformation.Text = "0 Layer(s), 0 Feature(s)"
        '
        'sptIdentification
        '
        Me.sptIdentification.Dock = System.Windows.Forms.DockStyle.Fill
        Me.sptIdentification.Location = New System.Drawing.Point(0, 0)
        Me.sptIdentification.Name = "sptIdentification"
        Me.sptIdentification.Orientation = System.Windows.Forms.Orientation.Horizontal
        '
        'sptIdentification.Panel1
        '
        Me.sptIdentification.Panel1.Controls.Add(Me.treIdentification)
        Me.sptIdentification.Panel1.Controls.Add(Me.tooIdentification)
        '
        'sptIdentification.Panel2
        '
        Me.sptIdentification.Panel2.Controls.Add(Me.dgvIdentification)
        Me.sptIdentification.Size = New System.Drawing.Size(300, 317)
        Me.sptIdentification.SplitterDistance = 155
        Me.sptIdentification.TabIndex = 1
        '
        'treIdentification
        '
        Me.treIdentification.Dock = System.Windows.Forms.DockStyle.Fill
        Me.treIdentification.Location = New System.Drawing.Point(0, 25)
        Me.treIdentification.Name = "treIdentification"
        Me.treIdentification.Size = New System.Drawing.Size(300, 130)
        Me.treIdentification.TabIndex = 2
        '
        'tooIdentification
        '
        Me.tooIdentification.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnRafraichir, Me.cboTrier, Me.txtMaxItem})
        Me.tooIdentification.Location = New System.Drawing.Point(0, 0)
        Me.tooIdentification.Name = "tooIdentification"
        Me.tooIdentification.Size = New System.Drawing.Size(300, 25)
        Me.tooIdentification.TabIndex = 1
        Me.tooIdentification.Text = "ToolStrip1"
        '
        'btnRafraichir
        '
        Me.btnRafraichir.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRafraichir.Image = CType(resources.GetObject("btnRafraichir.Image"), System.Drawing.Image)
        Me.btnRafraichir.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRafraichir.Name = "btnRafraichir"
        Me.btnRafraichir.Size = New System.Drawing.Size(23, 22)
        Me.btnRafraichir.Text = "Rafraîchir"
        Me.btnRafraichir.ToolTipText = "Rafraîchir le contenu"
        '
        'cboTrier
        '
        Me.cboTrier.Items.AddRange(New Object() {"Ascendant", "Descendant"})
        Me.cboTrier.Name = "cboTrier"
        Me.cboTrier.Size = New System.Drawing.Size(85, 25)
        Me.cboTrier.Text = "Descendant"
        Me.cboTrier.ToolTipText = "Trier l'affichage"
        '
        'txtMaxItem
        '
        Me.txtMaxItem.Name = "txtMaxItem"
        Me.txtMaxItem.Size = New System.Drawing.Size(50, 25)
        Me.txtMaxItem.Text = "1000"
        Me.txtMaxItem.ToolTipText = "Nombre maximum d'items à afficher par noeud."
        '
        'dgvIdentification
        '
        Me.dgvIdentification.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.Fill
        Me.dgvIdentification.BackgroundColor = System.Drawing.SystemColors.ButtonHighlight
        Me.dgvIdentification.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize
        Me.dgvIdentification.Dock = System.Windows.Forms.DockStyle.Fill
        Me.dgvIdentification.EditMode = System.Windows.Forms.DataGridViewEditMode.EditOnEnter
        Me.dgvIdentification.Location = New System.Drawing.Point(0, 0)
        Me.dgvIdentification.Name = "dgvIdentification"
        Me.dgvIdentification.RowHeadersVisible = False
        DataGridViewCellStyle1.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.dgvIdentification.RowsDefaultCellStyle = DataGridViewCellStyle1
        Me.dgvIdentification.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect
        Me.dgvIdentification.Size = New System.Drawing.Size(300, 158)
        Me.dgvIdentification.TabIndex = 0
        Me.dgvIdentification.VirtualMode = True
        '
        'dckMenuIdentification
        '
        Me.Controls.Add(Me.sptIdentification)
        Me.Controls.Add(Me.lblInformation)
        Me.Name = "dckMenuIdentification"
        Me.Size = New System.Drawing.Size(300, 330)
        Me.sptIdentification.Panel1.ResumeLayout(False)
        Me.sptIdentification.Panel1.PerformLayout()
        Me.sptIdentification.Panel2.ResumeLayout(False)
        CType(Me.sptIdentification, System.ComponentModel.ISupportInitialize).EndInit()
        Me.sptIdentification.ResumeLayout(False)
        Me.tooIdentification.ResumeLayout(False)
        Me.tooIdentification.PerformLayout()
        CType(Me.dgvIdentification, System.ComponentModel.ISupportInitialize).EndInit()
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents lblInformation As System.Windows.Forms.Label
    Friend WithEvents sptIdentification As System.Windows.Forms.SplitContainer
    Friend WithEvents dgvIdentification As System.Windows.Forms.DataGridView
    Friend WithEvents treIdentification As System.Windows.Forms.TreeView
    Friend WithEvents tooIdentification As System.Windows.Forms.ToolStrip
    Friend WithEvents btnRafraichir As System.Windows.Forms.ToolStripButton
    Friend WithEvents cboTrier As System.Windows.Forms.ToolStripComboBox
    Friend WithEvents txtMaxItem As System.Windows.Forms.ToolStripTextBox

End Class
