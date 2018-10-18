<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class InputBoxForm
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()> _
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()> _
    Private Sub InitializeComponent()
        Me.PromptLabel = New System.Windows.Forms.Label()
        Me.InputTextBox = New System.Windows.Forms.RichTextBox()
        Me.OkBouton = New System.Windows.Forms.Button()
        Me.CancelBouton = New System.Windows.Forms.Button()
        Me.SuspendLayout()
        '
        'PromptLabel
        '
        Me.PromptLabel.AutoSize = True
        Me.PromptLabel.Dock = System.Windows.Forms.DockStyle.Top
        Me.PromptLabel.Location = New System.Drawing.Point(0, 0)
        Me.PromptLabel.Name = "PromptLabel"
        Me.PromptLabel.Size = New System.Drawing.Size(56, 13)
        Me.PromptLabel.TabIndex = 0
        Me.PromptLabel.Text = "Attribut :"
        '
        'InputTextBox
        '
        Me.InputTextBox.Dock = System.Windows.Forms.DockStyle.Fill
        Me.InputTextBox.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.InputTextBox.Location = New System.Drawing.Point(0, 13)
        Me.InputTextBox.Name = "InputTextBox"
        Me.InputTextBox.Size = New System.Drawing.Size(734, 149)
        Me.InputTextBox.TabIndex = 1
        Me.InputTextBox.Text = ""
        Me.InputTextBox.WordWrap = False
        '
        'OkBouton
        '
        Me.OkBouton.DialogResult = System.Windows.Forms.DialogResult.OK
        Me.OkBouton.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.OkBouton.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.OkBouton.Location = New System.Drawing.Point(0, 137)
        Me.OkBouton.Name = "OkBouton"
        Me.OkBouton.Size = New System.Drawing.Size(734, 25)
        Me.OkBouton.TabIndex = 2
        Me.OkBouton.Text = "OK"
        Me.OkBouton.UseVisualStyleBackColor = True
        '
        'CancelBouton
        '
        Me.CancelBouton.DialogResult = System.Windows.Forms.DialogResult.Cancel
        Me.CancelBouton.Dock = System.Windows.Forms.DockStyle.Bottom
        Me.CancelBouton.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.CancelBouton.Location = New System.Drawing.Point(0, 112)
        Me.CancelBouton.Name = "CancelBouton"
        Me.CancelBouton.Size = New System.Drawing.Size(734, 25)
        Me.CancelBouton.TabIndex = 3
        Me.CancelBouton.Text = "Cancel"
        Me.CancelBouton.UseVisualStyleBackColor = True
        '
        'InputBoxForm
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(7.0!, 13.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.ClientSize = New System.Drawing.Size(734, 162)
        Me.Controls.Add(Me.CancelBouton)
        Me.Controls.Add(Me.OkBouton)
        Me.Controls.Add(Me.InputTextBox)
        Me.Controls.Add(Me.PromptLabel)
        Me.Font = New System.Drawing.Font("Microsoft Sans Serif", 8.25!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Name = "InputBoxForm"
        Me.Text = "InputBoxForm"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub
    Friend WithEvents PromptLabel As System.Windows.Forms.Label
    Friend WithEvents InputTextBox As System.Windows.Forms.RichTextBox
    Friend WithEvents OkBouton As System.Windows.Forms.Button
    Friend WithEvents CancelBouton As System.Windows.Forms.Button
End Class
