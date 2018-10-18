Public Class InputBoxForm
    Public Property Titre As String
    Public Property Question As String
    Public Property Reponse As String

    Public Sub New()
        InitializeComponent()
    End Sub

    Public Sub New(ByVal titre As String, ByVal question As String, Optional ByVal reponse As String = "")
        InitializeComponent()
        Me.Titre = titre
        Me.Question = question
        Me.Reponse = reponse
    End Sub

    Private Sub InputBoxForm_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        Me.Text = Me.Titre
        PromptLabel.Text = Me.Question
        InputTextBox.Text = Me.Reponse
    End Sub

    Private Sub okButton_Click(sender As Object, e As EventArgs) Handles OkBouton.Click, CancelBouton.Click
        Me.Reponse = InputTextBox.Text
        Me.Close()
    End Sub
End Class