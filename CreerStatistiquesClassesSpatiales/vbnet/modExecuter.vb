Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.Geometry
Imports System.Windows.Forms
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.EditorExt
Imports ESRI.ArcGIS.DataSourcesGDB
Imports System.Text
Imports System.IO
Imports Microsoft.VisualBasic.FileIO

'**
'Nom de la composante : modExecuter.vb 
'
'''<summary>
''' Module principale permettant le calcul et l'�criture de l'information pour les classes d'une G�odatabase dans une table de statistiques.
''' 
''' Les 11 param�tres de la ligne de commande du programme sont les suivants:
''' -------------------------------------------------------------------------
''' 1-Table des statistiques : Nom de la table de la table des statistiques dans laquelle l'information sera �crites.
'''                            Obligatoire, D�faut : TBL_STATISTIQUE_ELEMENT_SOMMET
''' 2-Geodatabase des classes: Nom de la G�odatabase contenant les classes � traiter.
'''                            Obligatoire, D�faut : Database Connections\BDRS_PRO_BDG.sde
''' 3-Liste des classes      : Liste des classes spatiales � traiter.
'''                            Obligatoire, D�faut : 
''' 4-Attribut de d�coupage  : Nom de l'attribut du Layer de d�coupage dans lequel les identifiants seront utilis�s pour effectuer le traitement.
'''                            Optionnel, D�faut : DATASET_NAME
''' 5-Liste des identifiants : Liste des identifiants de d�coupage � traiter.
'''                            Optionnel, D�faut : Tous les identifiants de d�coupage pr�sents dans les classes spatiales.
''' 6-Fichier journal        : Nom du fichier journal dans lequel l'information sur l'ex�cution du traitement sera �crite.
'''                            Optionnel, D�faut : 
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
''' Date : 04 Octobre 2016
'''</remarks>
''' 
Module modExecuter
    '''<summary> Interface d'initialisation des licences ESRI.</summary>
    Private m_AOLicenseInitializer As LicenseInitializer = New CreerStatistiquesClassesSpatiales.LicenseInitializer()
    '''<summary>Nom de la table contenant l'information sur les statistiques des classes.</summary>
    Private m_NomTableStatistiques As String = "TBL_STATISTIQUE_ELEMENT_SOMMET"
    '''<summary>Nom de la G�odatabase contenant les classes � traiter.</summary>
    Private m_NomGeodatabaseClasses As String = "Database Connections\BDRS_PRO_BDG_DBA.sde"
    '''<summary>Liste des classes � traiter.</summary>
    Private m_ListeClasses As String = ""
    '''<summary>Nom de l'attribut de d�coupage dans lequel les identifiants seront utilis�s pour effectuer le traitement.</summary>
    Private m_NomAttributDecoupage As String = "DATASET_NAME"
    '''<summary>Liste des identifiants de d�coupage � traiter.</summary>
    Private m_ListeIdentifiants As String = ""
    '''<summary>Nom du fichier journal dans lequel l'ex�cution du traitement sera inscrit.</summary>
    Private m_NomFichierJournal As String = ""

    <STAThread()> _
    Sub Main()
        'D�clarer les variables de travail
        Dim oCreerStatistiques As clsCreerStatistiques = Nothing  'Objet qui permet d'ex�cuter le traitement de cr�ation des statistiques.

        Try
            'ESRI License Initializer generated code.
            m_AOLicenseInitializer.InitializeApplication(New esriLicenseProductCode() {esriLicenseProductCode.esriLicenseProductCodeStandard}, _
                                                         New esriLicenseExtensionCode() {})

            'Valider les parametres de la ligne de commandes
            Call ValiderParametres()

            'Initialiser le traitement de cr�ation des statistiques
            oCreerStatistiques = New clsCreerStatistiques(m_NomTableStatistiques, m_NomGeodatabaseClasses, m_ListeClasses, m_NomAttributDecoupage, _
                                                          m_ListeIdentifiants, m_NomFichierJournal)

            'Ex�cuter le traitement de sr�ation des staistiques
            oCreerStatistiques.Executer()

            'Retourner le code d'ex�ution du traitement
            System.Environment.Exit(0)

        Catch ex As Exception
            'Afficher l'erreur
            Console.WriteLine(ex.Message)
            '�crire le message d'erreur
            File.AppendAllText("D:\Erreur_" & System.DateTime.Now.ToString("yyyyMMdd_HHmmss") & ".log", ex.Message & vbCrLf)
            'Retourner le code d'�chec du traitement
            System.Environment.Exit(-1)
        Finally
            'Vider la m�moire
            'Fermer ad�quatement l'application utilisant les licences ESRI
            m_AOLicenseInitializer.ShutdownApplication()
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider et d�finir les param�tres du programme.
    '''</summary>
    '''
    Sub ValiderParametres()
        'D�claration des variables de travail
        Dim args() As String = System.Environment.GetCommandLineArgs()  'Contient les param�tres de la ligne de commandes

        Try
            'Valider le param�tre de la table des statistiques.
            Call ValiderParametreTableStatistiques(args)

            'Valider le param�tre de la Geodatabase des classes � traiter.
            Call ValiderParametreGeodatabaseClasses(args)

            'Valider le param�tre de la liste des classes � traiter.
            Call ValiderParametreListeClasses(args)

            'Valider le param�tre de l'attribut contenant l'identifiant de d�coupage � traiter.
            Call ValiderParametreAttributDecoupage(args)

            'Valider le param�tre de la liste des identifiants � traiter.
            Call ValiderParametreListeIdentifiants(args)

            'Valider le param�tre du fichier journal dans lequel l'information sur l'ex�cution du traitement sera �crite.
            Call ValiderParametreFichierJournal(args)

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la m�moire
            args = Nothing
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre de la table des contraintes d'int�grit�.
    '''</summary>
    '''
    Sub ValiderParametreTableStatistiques(ByVal args() As String)
        Try
            'V�rifier si le param�tre de la table des statistiques est pr�sent.
            If args.Length - 1 > 0 Then
                'V�rifier si le param�tre contient le nom de la table des statistiques
                If args(1) <> "#" Then
                    'D�finir le nom de la table des statistiques
                    m_NomTableStatistiques = args(1)
                End If

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreTableStatistiques", "ERREUR : Le param�tre du nom de la table des statistiques est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre du nom de la Geodatabase des classes � traiter.
    '''</summary>
    '''
    Sub ValiderParametreGeodatabaseClasses(ByVal args() As String)
        Try
            'V�rifier si le param�tre de la Geodatabase des classes est pr�sent.
            If args.Length - 1 > 1 Then
                'V�rifier si le param�tre contient le nom de la G�odatabase des classes
                If args(2) <> "#" Then
                    'D�finir le nom de la G�odatabase des classes
                    m_NomGeodatabaseClasses = args(2)
                End If

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreGeodatabaseClasses", "ERREUR : Le param�tre de la Geodatabase des classes est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre de la liste des classes � traiter.
    '''</summary>
    '''
    Sub ValiderParametreListeClasses(ByVal args() As String)
        Try
            'Valider le param�tre de la liste des classes � traiter.
            If args.Length - 1 > 2 Then
                'V�rifier si le param�tre contient la liste des classes
                If args(3) <> "#" Then
                    'D�finir la liste des classes
                    m_ListeClasses = args(3).ToUpper
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre du nom de l'attribut contenant l'identifiant de d�coupage � valider.
    '''</summary>
    '''
    Sub ValiderParametreAttributDecoupage(ByVal args() As String)
        Try
            'Valider le param�tre du nom de l'attribut contenant l'identifiant de d�coupage � traiter
            If args.Length - 1 > 3 Then
                'V�rifier si le param�tre contient le nom de l'attribut de d�coupage
                If args(4) <> "#" Then
                    'D�finir le nom de l'attribut de d�coupage
                    m_NomAttributDecoupage = args(4).ToUpper
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre de la liste des identifiants.
    '''</summary>
    '''
    Sub ValiderParametreListeIdentifiants(ByVal args() As String)
        Try
            'V�rifier si le param�tre de la liste des identifiants. est pr�sent.
            If args.Length - 1 > 4 Then
                'V�rifier si le param�tre la liste des identifiants.
                If args(5) <> "#" Then
                    'D�finir la liste des identifiants.
                    m_ListeIdentifiants = args(5).ToUpper
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre du fichier journal dans lequel l'information sur l'ex�cution du traitement sera �crite.
    '''</summary>
    '''
    Sub ValiderParametreFichierJournal(ByVal args() As String)
        Try
            'Valider le param�tre du r�pertoire dans lequel les erreurs seront �crites
            If args.Length - 1 > 5 Then
                'V�rifier si le param�tre contient le nom du fichier journal
                If args(6) <> "#" Then
                    'D�finir le nom du fichier journal
                    m_NomFichierJournal = args(6)
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub
End Module
