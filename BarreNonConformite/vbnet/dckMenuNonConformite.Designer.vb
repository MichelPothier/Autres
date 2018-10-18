<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class dckMenuNonConformite
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
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(dckMenuNonConformite))
        Me.btnInitialiser = New System.Windows.Forms.Button()
        Me.tabMenuNonConformite = New System.Windows.Forms.TabControl()
        Me.tabNonConformite = New System.Windows.Forms.TabPage()
        Me.cboEnvSIB = New System.Windows.Forms.ComboBox()
        Me.lblEnvSib = New System.Windows.Forms.Label()
        Me.rtbDescription = New System.Windows.Forms.RichTextBox()
        Me.lblDescription = New System.Windows.Forms.Label()
        Me.cboNonConformite = New System.Windows.Forms.ComboBox()
        Me.lblNonConformite = New System.Windows.Forms.Label()
        Me.cboGeodatabaseEnfant = New System.Windows.Forms.ComboBox()
        Me.lblGeodatabaseEnfant = New System.Windows.Forms.Label()
        Me.cboGeodatabaseParent = New System.Windows.Forms.ComboBox()
        Me.lblGeodatabaseParent = New System.Windows.Forms.Label()
        Me.tabIdentifiants = New System.Windows.Forms.TabPage()
        Me.tooIdentifiants = New System.Windows.Forms.ToolStrip()
        Me.btnOuvrirIdentifiant = New System.Windows.Forms.ToolStripButton()
        Me.btnFermerIdentifiant = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator6 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnSelectIdentifiant = New System.Windows.Forms.ToolStripButton()
        Me.btnDeselectIdentifiant = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator7 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnInitialiserClassesIdentifiants = New System.Windows.Forms.ToolStripButton()
        Me.btnAfficherClassesProduction = New System.Windows.Forms.ToolStripButton()
        Me.lblNbIdentifiants = New System.Windows.Forms.Label()
        Me.treIdentifiants = New System.Windows.Forms.TreeView()
        Me.lblListeIdentifiants = New System.Windows.Forms.Label()
        Me.tabClasses = New System.Windows.Forms.TabPage()
        Me.tooClasses = New System.Windows.Forms.ToolStrip()
        Me.btnSelectClasse = New System.Windows.Forms.ToolStripButton()
        Me.btnDeselectClasse = New System.Windows.Forms.ToolStripButton()
        Me.lblNbClasses = New System.Windows.Forms.Label()
        Me.treClasses = New System.Windows.Forms.TreeView()
        Me.lblListeClasses = New System.Windows.Forms.Label()
        Me.tabReplica = New System.Windows.Forms.TabPage()
        Me.treReplica = New System.Windows.Forms.TreeView()
        Me.lblDescReplica = New System.Windows.Forms.Label()
        Me.tabConflits = New System.Windows.Forms.TabPage()
        Me.tooConflits = New System.Windows.Forms.ToolStrip()
        Me.btnOuvrirFermerConflits = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator1 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnAccepterActionParent = New System.Windows.Forms.ToolStripButton()
        Me.btnRefuserActionParent = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator2 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnRechercherConflitsAvecDifferences = New System.Windows.Forms.ToolStripButton()
        Me.btnRechercherConflitsSansDifferences = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator5 = New System.Windows.Forms.ToolStripSeparator()
        Me.cboRechercherConflits = New System.Windows.Forms.ToolStripComboBox()
        Me.lblListeConflits = New System.Windows.Forms.Label()
        Me.lblNbConflits = New System.Windows.Forms.Label()
        Me.treConflits = New System.Windows.Forms.TreeView()
        Me.tabDifferences = New System.Windows.Forms.TabPage()
        Me.tooDifferences = New System.Windows.Forms.ToolStrip()
        Me.btnOuvrirFermerDifferences = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator3 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnAccepterActionEnfant = New System.Windows.Forms.ToolStripButton()
        Me.btnRefuserActionEnfant = New System.Windows.Forms.ToolStripButton()
        Me.ToolStripSeparator4 = New System.Windows.Forms.ToolStripSeparator()
        Me.btnRechercherDifferencesAvecConflits = New System.Windows.Forms.ToolStripButton()
        Me.btnRechercherDifferencesSansConflits = New System.Windows.Forms.ToolStripButton()
        Me.cboRechercherDifferences = New System.Windows.Forms.ToolStripComboBox()
        Me.lblListeDifferences = New System.Windows.Forms.Label()
        Me.lblNbDifferences = New System.Windows.Forms.Label()
        Me.treDifferences = New System.Windows.Forms.TreeView()
        Me.lblTypeProduit = New System.Windows.Forms.Label()
        Me.cboTypeProduit = New System.Windows.Forms.ComboBox()
        Me.tabMenuNonConformite.SuspendLayout()
        Me.tabNonConformite.SuspendLayout()
        Me.tabIdentifiants.SuspendLayout()
        Me.tooIdentifiants.SuspendLayout()
        Me.tabClasses.SuspendLayout()
        Me.tooClasses.SuspendLayout()
        Me.tabReplica.SuspendLayout()
        Me.tabConflits.SuspendLayout()
        Me.tooConflits.SuspendLayout()
        Me.tabDifferences.SuspendLayout()
        Me.tooDifferences.SuspendLayout()
        Me.SuspendLayout()
        '
        'btnInitialiser
        '
        Me.btnInitialiser.Location = New System.Drawing.Point(3, 273)
        Me.btnInitialiser.Name = "btnInitialiser"
        Me.btnInitialiser.Size = New System.Drawing.Size(90, 26)
        Me.btnInitialiser.TabIndex = 0
        Me.btnInitialiser.Text = "Initialiser"
        Me.btnInitialiser.UseVisualStyleBackColor = True
        '
        'tabMenuNonConformite
        '
        Me.tabMenuNonConformite.Controls.Add(Me.tabNonConformite)
        Me.tabMenuNonConformite.Controls.Add(Me.tabIdentifiants)
        Me.tabMenuNonConformite.Controls.Add(Me.tabClasses)
        Me.tabMenuNonConformite.Controls.Add(Me.tabReplica)
        Me.tabMenuNonConformite.Controls.Add(Me.tabConflits)
        Me.tabMenuNonConformite.Controls.Add(Me.tabDifferences)
        Me.tabMenuNonConformite.Location = New System.Drawing.Point(4, 8)
        Me.tabMenuNonConformite.Name = "tabMenuNonConformite"
        Me.tabMenuNonConformite.SelectedIndex = 0
        Me.tabMenuNonConformite.Size = New System.Drawing.Size(293, 262)
        Me.tabMenuNonConformite.TabIndex = 1
        '
        'tabNonConformite
        '
        Me.tabNonConformite.Controls.Add(Me.cboTypeProduit)
        Me.tabNonConformite.Controls.Add(Me.lblTypeProduit)
        Me.tabNonConformite.Controls.Add(Me.cboEnvSIB)
        Me.tabNonConformite.Controls.Add(Me.lblEnvSib)
        Me.tabNonConformite.Controls.Add(Me.rtbDescription)
        Me.tabNonConformite.Controls.Add(Me.lblDescription)
        Me.tabNonConformite.Controls.Add(Me.cboNonConformite)
        Me.tabNonConformite.Controls.Add(Me.lblNonConformite)
        Me.tabNonConformite.Controls.Add(Me.cboGeodatabaseEnfant)
        Me.tabNonConformite.Controls.Add(Me.lblGeodatabaseEnfant)
        Me.tabNonConformite.Controls.Add(Me.cboGeodatabaseParent)
        Me.tabNonConformite.Controls.Add(Me.lblGeodatabaseParent)
        Me.tabNonConformite.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.tabNonConformite.Location = New System.Drawing.Point(4, 22)
        Me.tabNonConformite.Name = "tabNonConformite"
        Me.tabNonConformite.Padding = New System.Windows.Forms.Padding(3)
        Me.tabNonConformite.Size = New System.Drawing.Size(285, 236)
        Me.tabNonConformite.TabIndex = 0
        Me.tabNonConformite.Text = "*Non-Conformité"
        Me.tabNonConformite.UseVisualStyleBackColor = True
        '
        'cboEnvSIB
        '
        Me.cboEnvSIB.FormattingEnabled = True
        Me.cboEnvSIB.Location = New System.Drawing.Point(6, 110)
        Me.cboEnvSIB.Name = "cboEnvSIB"
        Me.cboEnvSIB.Size = New System.Drawing.Size(69, 21)
        Me.cboEnvSIB.Sorted = True
        Me.cboEnvSIB.TabIndex = 17
        '
        'lblEnvSib
        '
        Me.lblEnvSib.AutoSize = True
        Me.lblEnvSib.Location = New System.Drawing.Point(3, 94)
        Me.lblEnvSib.Name = "lblEnvSib"
        Me.lblEnvSib.Size = New System.Drawing.Size(49, 13)
        Me.lblEnvSib.TabIndex = 16
        Me.lblEnvSib.Text = "Env SIB:"
        '
        'rtbDescription
        '
        Me.rtbDescription.Location = New System.Drawing.Point(6, 150)
        Me.rtbDescription.Name = "rtbDescription"
        Me.rtbDescription.Size = New System.Drawing.Size(273, 80)
        Me.rtbDescription.TabIndex = 15
        Me.rtbDescription.Text = ""
        '
        'lblDescription
        '
        Me.lblDescription.AutoSize = True
        Me.lblDescription.Location = New System.Drawing.Point(3, 134)
        Me.lblDescription.Name = "lblDescription"
        Me.lblDescription.Size = New System.Drawing.Size(165, 13)
        Me.lblDescription.TabIndex = 14
        Me.lblDescription.Text = "Description de la non-conformité :"
        '
        'cboNonConformite
        '
        Me.cboNonConformite.FormattingEnabled = True
        Me.cboNonConformite.Location = New System.Drawing.Point(160, 110)
        Me.cboNonConformite.Name = "cboNonConformite"
        Me.cboNonConformite.Size = New System.Drawing.Size(118, 21)
        Me.cboNonConformite.Sorted = True
        Me.cboNonConformite.TabIndex = 9
        '
        'lblNonConformite
        '
        Me.lblNonConformite.AutoSize = True
        Me.lblNonConformite.Location = New System.Drawing.Point(159, 94)
        Me.lblNonConformite.Name = "lblNonConformite"
        Me.lblNonConformite.Size = New System.Drawing.Size(123, 13)
        Me.lblNonConformite.TabIndex = 8
        Me.lblNonConformite.Text = "Numéro Non-Conformité:"
        '
        'cboGeodatabaseEnfant
        '
        Me.cboGeodatabaseEnfant.FormattingEnabled = True
        Me.cboGeodatabaseEnfant.Location = New System.Drawing.Point(4, 61)
        Me.cboGeodatabaseEnfant.Name = "cboGeodatabaseEnfant"
        Me.cboGeodatabaseEnfant.Size = New System.Drawing.Size(274, 21)
        Me.cboGeodatabaseEnfant.TabIndex = 5
        '
        'lblGeodatabaseEnfant
        '
        Me.lblGeodatabaseEnfant.AutoSize = True
        Me.lblGeodatabaseEnfant.Location = New System.Drawing.Point(1, 45)
        Me.lblGeodatabaseEnfant.Name = "lblGeodatabaseEnfant"
        Me.lblGeodatabaseEnfant.Size = New System.Drawing.Size(169, 13)
        Me.lblGeodatabaseEnfant.TabIndex = 4
        Me.lblGeodatabaseEnfant.Text = "Géodatabase Enfant (.mdb/.gdb) :"
        '
        'cboGeodatabaseParent
        '
        Me.cboGeodatabaseParent.FormattingEnabled = True
        Me.cboGeodatabaseParent.Location = New System.Drawing.Point(4, 19)
        Me.cboGeodatabaseParent.Name = "cboGeodatabaseParent"
        Me.cboGeodatabaseParent.Size = New System.Drawing.Size(274, 21)
        Me.cboGeodatabaseParent.TabIndex = 1
        '
        'lblGeodatabaseParent
        '
        Me.lblGeodatabaseParent.AutoSize = True
        Me.lblGeodatabaseParent.Location = New System.Drawing.Point(3, 3)
        Me.lblGeodatabaseParent.Name = "lblGeodatabaseParent"
        Me.lblGeodatabaseParent.Size = New System.Drawing.Size(140, 13)
        Me.lblGeodatabaseParent.TabIndex = 0
        Me.lblGeodatabaseParent.Text = "Géodatabase Parent (.sde) :"
        '
        'tabIdentifiants
        '
        Me.tabIdentifiants.Controls.Add(Me.tooIdentifiants)
        Me.tabIdentifiants.Controls.Add(Me.lblNbIdentifiants)
        Me.tabIdentifiants.Controls.Add(Me.treIdentifiants)
        Me.tabIdentifiants.Controls.Add(Me.lblListeIdentifiants)
        Me.tabIdentifiants.Location = New System.Drawing.Point(4, 22)
        Me.tabIdentifiants.Name = "tabIdentifiants"
        Me.tabIdentifiants.Padding = New System.Windows.Forms.Padding(3)
        Me.tabIdentifiants.Size = New System.Drawing.Size(285, 236)
        Me.tabIdentifiants.TabIndex = 1
        Me.tabIdentifiants.Text = "Identifiants"
        Me.tabIdentifiants.UseVisualStyleBackColor = True
        '
        'tooIdentifiants
        '
        Me.tooIdentifiants.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnOuvrirIdentifiant, Me.btnFermerIdentifiant, Me.ToolStripSeparator6, Me.btnSelectIdentifiant, Me.btnDeselectIdentifiant, Me.ToolStripSeparator7, Me.btnInitialiserClassesIdentifiants, Me.btnAfficherClassesProduction})
        Me.tooIdentifiants.Location = New System.Drawing.Point(3, 3)
        Me.tooIdentifiants.Name = "tooIdentifiants"
        Me.tooIdentifiants.Size = New System.Drawing.Size(279, 25)
        Me.tooIdentifiants.TabIndex = 16
        Me.tooIdentifiants.Text = "Outils pour les identifiants"
        '
        'btnOuvrirIdentifiant
        '
        Me.btnOuvrirIdentifiant.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnOuvrirIdentifiant.Image = CType(resources.GetObject("btnOuvrirIdentifiant.Image"), System.Drawing.Image)
        Me.btnOuvrirIdentifiant.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnOuvrirIdentifiant.Name = "btnOuvrirIdentifiant"
        Me.btnOuvrirIdentifiant.Size = New System.Drawing.Size(23, 22)
        Me.btnOuvrirIdentifiant.Text = "Ouvrir tous les identifiants"
        '
        'btnFermerIdentifiant
        '
        Me.btnFermerIdentifiant.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnFermerIdentifiant.Image = CType(resources.GetObject("btnFermerIdentifiant.Image"), System.Drawing.Image)
        Me.btnFermerIdentifiant.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnFermerIdentifiant.Name = "btnFermerIdentifiant"
        Me.btnFermerIdentifiant.Size = New System.Drawing.Size(23, 22)
        Me.btnFermerIdentifiant.Text = "Fermer tous les identifiants"
        '
        'ToolStripSeparator6
        '
        Me.ToolStripSeparator6.Name = "ToolStripSeparator6"
        Me.ToolStripSeparator6.Size = New System.Drawing.Size(6, 25)
        '
        'btnSelectIdentifiant
        '
        Me.btnSelectIdentifiant.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnSelectIdentifiant.Image = CType(resources.GetObject("btnSelectIdentifiant.Image"), System.Drawing.Image)
        Me.btnSelectIdentifiant.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnSelectIdentifiant.Name = "btnSelectIdentifiant"
        Me.btnSelectIdentifiant.Size = New System.Drawing.Size(23, 22)
        Me.btnSelectIdentifiant.Text = "Selectionner tous les identifiants"
        '
        'btnDeselectIdentifiant
        '
        Me.btnDeselectIdentifiant.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnDeselectIdentifiant.Image = CType(resources.GetObject("btnDeselectIdentifiant.Image"), System.Drawing.Image)
        Me.btnDeselectIdentifiant.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnDeselectIdentifiant.Name = "btnDeselectIdentifiant"
        Me.btnDeselectIdentifiant.Size = New System.Drawing.Size(23, 22)
        Me.btnDeselectIdentifiant.Text = "Désélectionner tous les identifiants"
        '
        'ToolStripSeparator7
        '
        Me.ToolStripSeparator7.Name = "ToolStripSeparator7"
        Me.ToolStripSeparator7.Size = New System.Drawing.Size(6, 25)
        '
        'btnInitialiserClassesIdentifiants
        '
        Me.btnInitialiserClassesIdentifiants.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnInitialiserClassesIdentifiants.Image = CType(resources.GetObject("btnInitialiserClassesIdentifiants.Image"), System.Drawing.Image)
        Me.btnInitialiserClassesIdentifiants.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnInitialiserClassesIdentifiants.Name = "btnInitialiserClassesIdentifiants"
        Me.btnInitialiserClassesIdentifiants.Size = New System.Drawing.Size(23, 22)
        Me.btnInitialiserClassesIdentifiants.Text = "Initialiser les classes des identifiants"
        '
        'btnAfficherClassesProduction
        '
        Me.btnAfficherClassesProduction.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnAfficherClassesProduction.Image = CType(resources.GetObject("btnAfficherClassesProduction.Image"), System.Drawing.Image)
        Me.btnAfficherClassesProduction.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnAfficherClassesProduction.Name = "btnAfficherClassesProduction"
        Me.btnAfficherClassesProduction.Size = New System.Drawing.Size(23, 22)
        Me.btnAfficherClassesProduction.Text = "Afficher les classes en production des identifiants sélectionnés"
        '
        'lblNbIdentifiants
        '
        Me.lblNbIdentifiants.AutoSize = True
        Me.lblNbIdentifiants.Location = New System.Drawing.Point(2, 218)
        Me.lblNbIdentifiants.Name = "lblNbIdentifiants"
        Me.lblNbIdentifiants.Size = New System.Drawing.Size(120, 13)
        Me.lblNbIdentifiants.TabIndex = 15
        Me.lblNbIdentifiants.Text = "Nombre d'identifiants : 0"
        '
        'treIdentifiants
        '
        Me.treIdentifiants.CheckBoxes = True
        Me.treIdentifiants.Location = New System.Drawing.Point(2, 45)
        Me.treIdentifiants.Name = "treIdentifiants"
        Me.treIdentifiants.Size = New System.Drawing.Size(281, 169)
        Me.treIdentifiants.TabIndex = 14
        '
        'lblListeIdentifiants
        '
        Me.lblListeIdentifiants.AutoSize = True
        Me.lblListeIdentifiants.Location = New System.Drawing.Point(-1, 28)
        Me.lblListeIdentifiants.Name = "lblListeIdentifiants"
        Me.lblListeIdentifiants.Size = New System.Drawing.Size(275, 13)
        Me.lblListeIdentifiants.TabIndex = 13
        Me.lblListeIdentifiants.Text = "Liste des identifiants  (Double-Click pour voir les classes):"
        '
        'tabClasses
        '
        Me.tabClasses.Controls.Add(Me.tooClasses)
        Me.tabClasses.Controls.Add(Me.lblNbClasses)
        Me.tabClasses.Controls.Add(Me.treClasses)
        Me.tabClasses.Controls.Add(Me.lblListeClasses)
        Me.tabClasses.Location = New System.Drawing.Point(4, 22)
        Me.tabClasses.Name = "tabClasses"
        Me.tabClasses.Size = New System.Drawing.Size(285, 236)
        Me.tabClasses.TabIndex = 2
        Me.tabClasses.Text = "Classes"
        Me.tabClasses.UseVisualStyleBackColor = True
        '
        'tooClasses
        '
        Me.tooClasses.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnSelectClasse, Me.btnDeselectClasse})
        Me.tooClasses.Location = New System.Drawing.Point(0, 0)
        Me.tooClasses.Name = "tooClasses"
        Me.tooClasses.Size = New System.Drawing.Size(285, 25)
        Me.tooClasses.TabIndex = 14
        Me.tooClasses.Text = "Outils pour les classes"
        '
        'btnSelectClasse
        '
        Me.btnSelectClasse.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnSelectClasse.Image = CType(resources.GetObject("btnSelectClasse.Image"), System.Drawing.Image)
        Me.btnSelectClasse.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnSelectClasse.Name = "btnSelectClasse"
        Me.btnSelectClasse.Size = New System.Drawing.Size(23, 22)
        Me.btnSelectClasse.Text = "Sélectionner toutes les classes"
        '
        'btnDeselectClasse
        '
        Me.btnDeselectClasse.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnDeselectClasse.Image = CType(resources.GetObject("btnDeselectClasse.Image"), System.Drawing.Image)
        Me.btnDeselectClasse.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnDeselectClasse.Name = "btnDeselectClasse"
        Me.btnDeselectClasse.Size = New System.Drawing.Size(23, 22)
        Me.btnDeselectClasse.Text = "Désélectionner toutes les classes"
        '
        'lblNbClasses
        '
        Me.lblNbClasses.AutoSize = True
        Me.lblNbClasses.Location = New System.Drawing.Point(2, 218)
        Me.lblNbClasses.Name = "lblNbClasses"
        Me.lblNbClasses.Size = New System.Drawing.Size(112, 13)
        Me.lblNbClasses.TabIndex = 13
        Me.lblNbClasses.Text = "Nombre de classes : 0"
        '
        'treClasses
        '
        Me.treClasses.CheckBoxes = True
        Me.treClasses.Location = New System.Drawing.Point(2, 45)
        Me.treClasses.Name = "treClasses"
        Me.treClasses.Size = New System.Drawing.Size(281, 169)
        Me.treClasses.TabIndex = 12
        '
        'lblListeClasses
        '
        Me.lblListeClasses.AutoSize = True
        Me.lblListeClasses.Location = New System.Drawing.Point(-1, 28)
        Me.lblListeClasses.Name = "lblListeClasses"
        Me.lblListeClasses.Size = New System.Drawing.Size(93, 13)
        Me.lblListeClasses.TabIndex = 11
        Me.lblListeClasses.Text = "Liste des classes :"
        '
        'tabReplica
        '
        Me.tabReplica.Controls.Add(Me.treReplica)
        Me.tabReplica.Controls.Add(Me.lblDescReplica)
        Me.tabReplica.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.tabReplica.Location = New System.Drawing.Point(4, 22)
        Me.tabReplica.Name = "tabReplica"
        Me.tabReplica.Size = New System.Drawing.Size(285, 236)
        Me.tabReplica.TabIndex = 5
        Me.tabReplica.Text = "*Replica"
        Me.tabReplica.UseVisualStyleBackColor = True
        '
        'treReplica
        '
        Me.treReplica.Location = New System.Drawing.Point(0, 24)
        Me.treReplica.Name = "treReplica"
        Me.treReplica.Size = New System.Drawing.Size(284, 211)
        Me.treReplica.TabIndex = 1
        '
        'lblDescReplica
        '
        Me.lblDescReplica.AutoSize = True
        Me.lblDescReplica.Location = New System.Drawing.Point(0, 6)
        Me.lblDescReplica.Name = "lblDescReplica"
        Me.lblDescReplica.Size = New System.Drawing.Size(115, 13)
        Me.lblDescReplica.TabIndex = 0
        Me.lblDescReplica.Text = "Description du réplica :"
        '
        'tabConflits
        '
        Me.tabConflits.Controls.Add(Me.tooConflits)
        Me.tabConflits.Controls.Add(Me.lblListeConflits)
        Me.tabConflits.Controls.Add(Me.lblNbConflits)
        Me.tabConflits.Controls.Add(Me.treConflits)
        Me.tabConflits.Location = New System.Drawing.Point(4, 22)
        Me.tabConflits.Name = "tabConflits"
        Me.tabConflits.Size = New System.Drawing.Size(285, 236)
        Me.tabConflits.TabIndex = 3
        Me.tabConflits.Text = "Conflits"
        Me.tabConflits.UseVisualStyleBackColor = True
        '
        'tooConflits
        '
        Me.tooConflits.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnOuvrirFermerConflits, Me.ToolStripSeparator1, Me.btnAccepterActionParent, Me.btnRefuserActionParent, Me.ToolStripSeparator2, Me.btnRechercherConflitsAvecDifferences, Me.btnRechercherConflitsSansDifferences, Me.ToolStripSeparator5, Me.cboRechercherConflits})
        Me.tooConflits.Location = New System.Drawing.Point(0, 0)
        Me.tooConflits.Name = "tooConflits"
        Me.tooConflits.Size = New System.Drawing.Size(285, 25)
        Me.tooConflits.TabIndex = 3
        Me.tooConflits.Text = "Outils pour les conflits"
        '
        'btnOuvrirFermerConflits
        '
        Me.btnOuvrirFermerConflits.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnOuvrirFermerConflits.Image = CType(resources.GetObject("btnOuvrirFermerConflits.Image"), System.Drawing.Image)
        Me.btnOuvrirFermerConflits.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnOuvrirFermerConflits.Name = "btnOuvrirFermerConflits"
        Me.btnOuvrirFermerConflits.Size = New System.Drawing.Size(23, 22)
        Me.btnOuvrirFermerConflits.Text = "+ Ouvrir/ - Fermer"
        '
        'ToolStripSeparator1
        '
        Me.ToolStripSeparator1.Name = "ToolStripSeparator1"
        Me.ToolStripSeparator1.Size = New System.Drawing.Size(6, 25)
        '
        'btnAccepterActionParent
        '
        Me.btnAccepterActionParent.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnAccepterActionParent.Image = CType(resources.GetObject("btnAccepterActionParent.Image"), System.Drawing.Image)
        Me.btnAccepterActionParent.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnAccepterActionParent.Name = "btnAccepterActionParent"
        Me.btnAccepterActionParent.Size = New System.Drawing.Size(23, 22)
        Me.btnAccepterActionParent.Text = "Accepter l'action effectuée dans la GdbParent"
        '
        'btnRefuserActionParent
        '
        Me.btnRefuserActionParent.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRefuserActionParent.Image = CType(resources.GetObject("btnRefuserActionParent.Image"), System.Drawing.Image)
        Me.btnRefuserActionParent.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRefuserActionParent.Name = "btnRefuserActionParent"
        Me.btnRefuserActionParent.Size = New System.Drawing.Size(23, 22)
        Me.btnRefuserActionParent.Text = "Refuser l'action effectuée dans la GdbParent"
        '
        'ToolStripSeparator2
        '
        Me.ToolStripSeparator2.Name = "ToolStripSeparator2"
        Me.ToolStripSeparator2.Size = New System.Drawing.Size(6, 25)
        '
        'btnRechercherConflitsAvecDifferences
        '
        Me.btnRechercherConflitsAvecDifferences.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRechercherConflitsAvecDifferences.Image = CType(resources.GetObject("btnRechercherConflitsAvecDifferences.Image"), System.Drawing.Image)
        Me.btnRechercherConflitsAvecDifferences.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRechercherConflitsAvecDifferences.Name = "btnRechercherConflitsAvecDifferences"
        Me.btnRechercherConflitsAvecDifferences.Size = New System.Drawing.Size(23, 22)
        Me.btnRechercherConflitsAvecDifferences.Text = "Rechercher Conflits avec Differences"
        '
        'btnRechercherConflitsSansDifferences
        '
        Me.btnRechercherConflitsSansDifferences.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRechercherConflitsSansDifferences.Image = CType(resources.GetObject("btnRechercherConflitsSansDifferences.Image"), System.Drawing.Image)
        Me.btnRechercherConflitsSansDifferences.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRechercherConflitsSansDifferences.Name = "btnRechercherConflitsSansDifferences"
        Me.btnRechercherConflitsSansDifferences.Size = New System.Drawing.Size(23, 22)
        Me.btnRechercherConflitsSansDifferences.Text = "Rechercher Conflits sans Differences"
        '
        'ToolStripSeparator5
        '
        Me.ToolStripSeparator5.Name = "ToolStripSeparator5"
        Me.ToolStripSeparator5.Size = New System.Drawing.Size(6, 25)
        '
        'cboRechercherConflits
        '
        Me.cboRechercherConflits.AutoToolTip = True
        Me.cboRechercherConflits.DropDownWidth = 150
        Me.cboRechercherConflits.Name = "cboRechercherConflits"
        Me.cboRechercherConflits.Size = New System.Drawing.Size(100, 25)
        Me.cboRechercherConflits.ToolTipText = "Texte à rechercher (<Enter> pour exécuter la recherche)"
        '
        'lblListeConflits
        '
        Me.lblListeConflits.AutoSize = True
        Me.lblListeConflits.Location = New System.Drawing.Point(-1, 28)
        Me.lblListeConflits.Name = "lblListeConflits"
        Me.lblListeConflits.Size = New System.Drawing.Size(268, 13)
        Me.lblListeConflits.TabIndex = 2
        Me.lblListeConflits.Text = "Liste des conflits (GdbParent/GdbArchive/GdbEnfant) :"
        '
        'lblNbConflits
        '
        Me.lblNbConflits.AutoSize = True
        Me.lblNbConflits.Location = New System.Drawing.Point(2, 218)
        Me.lblNbConflits.Name = "lblNbConflits"
        Me.lblNbConflits.Size = New System.Drawing.Size(110, 13)
        Me.lblNbConflits.TabIndex = 1
        Me.lblNbConflits.Text = "Nombre de conflits : 0"
        '
        'treConflits
        '
        Me.treConflits.Location = New System.Drawing.Point(2, 45)
        Me.treConflits.Name = "treConflits"
        Me.treConflits.Size = New System.Drawing.Size(281, 169)
        Me.treConflits.TabIndex = 0
        '
        'tabDifferences
        '
        Me.tabDifferences.Controls.Add(Me.tooDifferences)
        Me.tabDifferences.Controls.Add(Me.lblListeDifferences)
        Me.tabDifferences.Controls.Add(Me.lblNbDifferences)
        Me.tabDifferences.Controls.Add(Me.treDifferences)
        Me.tabDifferences.Location = New System.Drawing.Point(4, 22)
        Me.tabDifferences.Name = "tabDifferences"
        Me.tabDifferences.Size = New System.Drawing.Size(285, 236)
        Me.tabDifferences.TabIndex = 4
        Me.tabDifferences.Text = "Différences"
        Me.tabDifferences.UseVisualStyleBackColor = True
        '
        'tooDifferences
        '
        Me.tooDifferences.Items.AddRange(New System.Windows.Forms.ToolStripItem() {Me.btnOuvrirFermerDifferences, Me.ToolStripSeparator3, Me.btnAccepterActionEnfant, Me.btnRefuserActionEnfant, Me.ToolStripSeparator4, Me.btnRechercherDifferencesAvecConflits, Me.btnRechercherDifferencesSansConflits, Me.cboRechercherDifferences})
        Me.tooDifferences.Location = New System.Drawing.Point(0, 0)
        Me.tooDifferences.Name = "tooDifferences"
        Me.tooDifferences.Size = New System.Drawing.Size(285, 25)
        Me.tooDifferences.TabIndex = 6
        Me.tooDifferences.Text = "Outils pour les différences"
        '
        'btnOuvrirFermerDifferences
        '
        Me.btnOuvrirFermerDifferences.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnOuvrirFermerDifferences.Image = CType(resources.GetObject("btnOuvrirFermerDifferences.Image"), System.Drawing.Image)
        Me.btnOuvrirFermerDifferences.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnOuvrirFermerDifferences.Name = "btnOuvrirFermerDifferences"
        Me.btnOuvrirFermerDifferences.Size = New System.Drawing.Size(23, 22)
        Me.btnOuvrirFermerDifferences.Text = "+ Ouvrir/ - Fermer"
        '
        'ToolStripSeparator3
        '
        Me.ToolStripSeparator3.Name = "ToolStripSeparator3"
        Me.ToolStripSeparator3.Size = New System.Drawing.Size(6, 25)
        '
        'btnAccepterActionEnfant
        '
        Me.btnAccepterActionEnfant.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnAccepterActionEnfant.Image = CType(resources.GetObject("btnAccepterActionEnfant.Image"), System.Drawing.Image)
        Me.btnAccepterActionEnfant.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnAccepterActionEnfant.Name = "btnAccepterActionEnfant"
        Me.btnAccepterActionEnfant.Size = New System.Drawing.Size(23, 22)
        Me.btnAccepterActionEnfant.Text = "Accepter l'action effectuée dans la GdbEnfant"
        '
        'btnRefuserActionEnfant
        '
        Me.btnRefuserActionEnfant.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRefuserActionEnfant.Image = CType(resources.GetObject("btnRefuserActionEnfant.Image"), System.Drawing.Image)
        Me.btnRefuserActionEnfant.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRefuserActionEnfant.Name = "btnRefuserActionEnfant"
        Me.btnRefuserActionEnfant.Size = New System.Drawing.Size(23, 22)
        Me.btnRefuserActionEnfant.Text = "Refuser l'action effectuée dans la GdbEnfant"
        '
        'ToolStripSeparator4
        '
        Me.ToolStripSeparator4.Name = "ToolStripSeparator4"
        Me.ToolStripSeparator4.Size = New System.Drawing.Size(6, 25)
        '
        'btnRechercherDifferencesAvecConflits
        '
        Me.btnRechercherDifferencesAvecConflits.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRechercherDifferencesAvecConflits.Image = CType(resources.GetObject("btnRechercherDifferencesAvecConflits.Image"), System.Drawing.Image)
        Me.btnRechercherDifferencesAvecConflits.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRechercherDifferencesAvecConflits.Name = "btnRechercherDifferencesAvecConflits"
        Me.btnRechercherDifferencesAvecConflits.Size = New System.Drawing.Size(23, 22)
        Me.btnRechercherDifferencesAvecConflits.Text = "Rechercher Differences avec Conflits"
        '
        'btnRechercherDifferencesSansConflits
        '
        Me.btnRechercherDifferencesSansConflits.DisplayStyle = System.Windows.Forms.ToolStripItemDisplayStyle.Image
        Me.btnRechercherDifferencesSansConflits.Image = CType(resources.GetObject("btnRechercherDifferencesSansConflits.Image"), System.Drawing.Image)
        Me.btnRechercherDifferencesSansConflits.ImageTransparentColor = System.Drawing.Color.Magenta
        Me.btnRechercherDifferencesSansConflits.Name = "btnRechercherDifferencesSansConflits"
        Me.btnRechercherDifferencesSansConflits.Size = New System.Drawing.Size(23, 22)
        Me.btnRechercherDifferencesSansConflits.Text = "Rechercher Differences sans Conflits"
        '
        'cboRechercherDifferences
        '
        Me.cboRechercherDifferences.AutoToolTip = True
        Me.cboRechercherDifferences.DropDownWidth = 150
        Me.cboRechercherDifferences.Name = "cboRechercherDifferences"
        Me.cboRechercherDifferences.Size = New System.Drawing.Size(100, 25)
        Me.cboRechercherDifferences.ToolTipText = "Texte à rechercher (<Enter> pour exécuter la recherche)"
        '
        'lblListeDifferences
        '
        Me.lblListeDifferences.AutoSize = True
        Me.lblListeDifferences.Location = New System.Drawing.Point(-1, 28)
        Me.lblListeDifferences.Name = "lblListeDifferences"
        Me.lblListeDifferences.Size = New System.Drawing.Size(234, 13)
        Me.lblListeDifferences.TabIndex = 5
        Me.lblListeDifferences.Text = "Liste des différences  (GdbEnfant/GdbArchive) :"
        '
        'lblNbDifferences
        '
        Me.lblNbDifferences.AutoSize = True
        Me.lblNbDifferences.Location = New System.Drawing.Point(2, 218)
        Me.lblNbDifferences.Name = "lblNbDifferences"
        Me.lblNbDifferences.Size = New System.Drawing.Size(129, 13)
        Me.lblNbDifferences.TabIndex = 4
        Me.lblNbDifferences.Text = "Nombre de différences : 0"
        '
        'treDifferences
        '
        Me.treDifferences.Location = New System.Drawing.Point(2, 45)
        Me.treDifferences.Name = "treDifferences"
        Me.treDifferences.Size = New System.Drawing.Size(281, 169)
        Me.treDifferences.TabIndex = 3
        '
        'lblTypeProduit
        '
        Me.lblTypeProduit.AutoSize = True
        Me.lblTypeProduit.Location = New System.Drawing.Point(78, 94)
        Me.lblTypeProduit.Name = "lblTypeProduit"
        Me.lblTypeProduit.Size = New System.Drawing.Size(70, 13)
        Me.lblTypeProduit.TabIndex = 19
        Me.lblTypeProduit.Text = "Type Produit:"
        '
        'cboTypeProduit
        '
        Me.cboTypeProduit.FormattingEnabled = True
        Me.cboTypeProduit.Location = New System.Drawing.Point(81, 110)
        Me.cboTypeProduit.Name = "cboTypeProduit"
        Me.cboTypeProduit.Size = New System.Drawing.Size(73, 21)
        Me.cboTypeProduit.Sorted = True
        Me.cboTypeProduit.TabIndex = 20
        '
        'dckMenuNonConformite
        '
        Me.Controls.Add(Me.tabMenuNonConformite)
        Me.Controls.Add(Me.btnInitialiser)
        Me.Name = "dckMenuNonConformite"
        Me.Size = New System.Drawing.Size(300, 300)
        Me.tabMenuNonConformite.ResumeLayout(False)
        Me.tabNonConformite.ResumeLayout(False)
        Me.tabNonConformite.PerformLayout()
        Me.tabIdentifiants.ResumeLayout(False)
        Me.tabIdentifiants.PerformLayout()
        Me.tooIdentifiants.ResumeLayout(False)
        Me.tooIdentifiants.PerformLayout()
        Me.tabClasses.ResumeLayout(False)
        Me.tabClasses.PerformLayout()
        Me.tooClasses.ResumeLayout(False)
        Me.tooClasses.PerformLayout()
        Me.tabReplica.ResumeLayout(False)
        Me.tabReplica.PerformLayout()
        Me.tabConflits.ResumeLayout(False)
        Me.tabConflits.PerformLayout()
        Me.tooConflits.ResumeLayout(False)
        Me.tooConflits.PerformLayout()
        Me.tabDifferences.ResumeLayout(False)
        Me.tabDifferences.PerformLayout()
        Me.tooDifferences.ResumeLayout(False)
        Me.tooDifferences.PerformLayout()
        Me.ResumeLayout(False)

    End Sub
    Friend WithEvents btnInitialiser As System.Windows.Forms.Button
    Friend WithEvents tabMenuNonConformite As System.Windows.Forms.TabControl
    Friend WithEvents tabNonConformite As System.Windows.Forms.TabPage
    Friend WithEvents cboGeodatabaseEnfant As System.Windows.Forms.ComboBox
    Friend WithEvents lblGeodatabaseEnfant As System.Windows.Forms.Label
    Friend WithEvents cboGeodatabaseParent As System.Windows.Forms.ComboBox
    Friend WithEvents lblGeodatabaseParent As System.Windows.Forms.Label
    Friend WithEvents tabIdentifiants As System.Windows.Forms.TabPage
    Friend WithEvents tabClasses As System.Windows.Forms.TabPage
    Friend WithEvents cboNonConformite As System.Windows.Forms.ComboBox
    Friend WithEvents lblNonConformite As System.Windows.Forms.Label
    Friend WithEvents tabConflits As System.Windows.Forms.TabPage
    Friend WithEvents rtbDescription As System.Windows.Forms.RichTextBox
    Friend WithEvents lblDescription As System.Windows.Forms.Label
    Friend WithEvents lblListeClasses As System.Windows.Forms.Label
    Friend WithEvents tabDifferences As System.Windows.Forms.TabPage
    Friend WithEvents lblListeConflits As System.Windows.Forms.Label
    Friend WithEvents lblNbConflits As System.Windows.Forms.Label
    Friend WithEvents treConflits As System.Windows.Forms.TreeView
    Friend WithEvents lblListeDifferences As System.Windows.Forms.Label
    Friend WithEvents lblNbDifferences As System.Windows.Forms.Label
    Friend WithEvents treDifferences As System.Windows.Forms.TreeView
    Friend WithEvents lblNbIdentifiants As System.Windows.Forms.Label
    Friend WithEvents treIdentifiants As System.Windows.Forms.TreeView
    Friend WithEvents lblListeIdentifiants As System.Windows.Forms.Label
    Friend WithEvents lblNbClasses As System.Windows.Forms.Label
    Friend WithEvents treClasses As System.Windows.Forms.TreeView
    Friend WithEvents tabReplica As System.Windows.Forms.TabPage
    Friend WithEvents lblDescReplica As System.Windows.Forms.Label
    Friend WithEvents treReplica As System.Windows.Forms.TreeView
    Friend WithEvents cboEnvSIB As System.Windows.Forms.ComboBox
    Friend WithEvents lblEnvSib As System.Windows.Forms.Label
    Friend WithEvents tooConflits As System.Windows.Forms.ToolStrip
    Friend WithEvents btnOuvrirFermerConflits As System.Windows.Forms.ToolStripButton
    Friend WithEvents ToolStripSeparator1 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents btnAccepterActionParent As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnRefuserActionParent As System.Windows.Forms.ToolStripButton
    Friend WithEvents ToolStripSeparator2 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents btnRechercherConflitsAvecDifferences As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnRechercherConflitsSansDifferences As System.Windows.Forms.ToolStripButton
    Friend WithEvents cboRechercherConflits As System.Windows.Forms.ToolStripComboBox
    Friend WithEvents tooDifferences As System.Windows.Forms.ToolStrip
    Friend WithEvents btnOuvrirFermerDifferences As System.Windows.Forms.ToolStripButton
    Friend WithEvents ToolStripSeparator3 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents btnRefuserActionEnfant As System.Windows.Forms.ToolStripButton
    Friend WithEvents ToolStripSeparator4 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents btnRechercherDifferencesAvecConflits As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnRechercherDifferencesSansConflits As System.Windows.Forms.ToolStripButton
    Friend WithEvents cboRechercherDifferences As System.Windows.Forms.ToolStripComboBox
    Friend WithEvents ToolStripSeparator5 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents btnAccepterActionEnfant As System.Windows.Forms.ToolStripButton
    Friend WithEvents tooIdentifiants As System.Windows.Forms.ToolStrip
    Friend WithEvents btnOuvrirIdentifiant As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnSelectIdentifiant As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnFermerIdentifiant As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnDeselectIdentifiant As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnAfficherClassesProduction As System.Windows.Forms.ToolStripButton
    Friend WithEvents ToolStripSeparator6 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents ToolStripSeparator7 As System.Windows.Forms.ToolStripSeparator
    Friend WithEvents btnInitialiserClassesIdentifiants As System.Windows.Forms.ToolStripButton
    Friend WithEvents tooClasses As System.Windows.Forms.ToolStrip
    Friend WithEvents btnSelectClasse As System.Windows.Forms.ToolStripButton
    Friend WithEvents btnDeselectClasse As System.Windows.Forms.ToolStripButton
    Friend WithEvents cboTypeProduit As System.Windows.Forms.ComboBox
    Friend WithEvents lblTypeProduit As System.Windows.Forms.Label

End Class
