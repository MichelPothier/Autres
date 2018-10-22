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
''' Module principale permettant le calcul et l'écriture de l'information pour les classes d'une Géodatabase dans une table de statistiques.
''' 
''' Les 11 paramètres de la ligne de commande du programme sont les suivants:
''' -------------------------------------------------------------------------
''' 1-Table des statistiques : Nom de la table de la table des statistiques dans laquelle l'information sera écrites.
'''                            Obligatoire, Défaut : TBL_STATISTIQUE_ELEMENT_SOMMET
''' 2-Geodatabase des classes: Nom de la Géodatabase contenant les classes à traiter.
'''                            Obligatoire, Défaut : Database Connections\BDRS_PRO_BDG.sde
''' 3-Liste des classes      : Liste des classes spatiales à traiter.
'''                            Obligatoire, Défaut : 
''' 4-Attribut de découpage  : Nom de l'attribut du Layer de découpage dans lequel les identifiants seront utilisés pour effectuer le traitement.
'''                            Optionnel, Défaut : DATASET_NAME
''' 5-Liste des identifiants : Liste des identifiants de découpage à traiter.
'''                            Optionnel, Défaut : Tous les identifiants de découpage présents dans les classes spatiales.
''' 6-Fichier journal        : Nom du fichier journal dans lequel l'information sur l'exécution du traitement sera écrite.
'''                            Optionnel, Défaut : 
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
    '''<summary>Nom de la Géodatabase contenant les classes à traiter.</summary>
    Private m_NomGeodatabaseClasses As String = "Database Connections\BDRS_PRO_BDG_DBA.sde"
    '''<summary>Liste des classes à traiter.</summary>
    Private m_ListeClasses As String = ""
    '''<summary>Nom de l'attribut de découpage dans lequel les identifiants seront utilisés pour effectuer le traitement.</summary>
    Private m_NomAttributDecoupage As String = "DATASET_NAME"
    '''<summary>Liste des identifiants de découpage à traiter.</summary>
    Private m_ListeIdentifiants As String = ""
    '''<summary>Nom du fichier journal dans lequel l'exécution du traitement sera inscrit.</summary>
    Private m_NomFichierJournal As String = ""

    <STAThread()> _
    Sub Main()
        'Déclarer les variables de travail
        Dim oCreerStatistiques As clsCreerStatistiques = Nothing  'Objet qui permet d'exécuter le traitement de création des statistiques.

        Try
            'ESRI License Initializer generated code.
            m_AOLicenseInitializer.InitializeApplication(New esriLicenseProductCode() {esriLicenseProductCode.esriLicenseProductCodeStandard}, _
                                                         New esriLicenseExtensionCode() {})

            'Valider les parametres de la ligne de commandes
            Call ValiderParametres()

            'Initialiser le traitement de création des statistiques
            oCreerStatistiques = New clsCreerStatistiques(m_NomTableStatistiques, m_NomGeodatabaseClasses, m_ListeClasses, m_NomAttributDecoupage, _
                                                          m_ListeIdentifiants, m_NomFichierJournal)

            'Exécuter le traitement de sréation des staistiques
            oCreerStatistiques.Executer()

            'Retourner le code d'exéution du traitement
            System.Environment.Exit(0)

        Catch ex As Exception
            'Afficher l'erreur
            Console.WriteLine(ex.Message)
            'Écrire le message d'erreur
            File.AppendAllText("D:\Erreur_" & System.DateTime.Now.ToString("yyyyMMdd_HHmmss") & ".log", ex.Message & vbCrLf)
            'Retourner le code d'échec du traitement
            System.Environment.Exit(-1)
        Finally
            'Vider la mémoire
            'Fermer adéquatement l'application utilisant les licences ESRI
            m_AOLicenseInitializer.ShutdownApplication()
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider et définir les paramètres du programme.
    '''</summary>
    '''
    Sub ValiderParametres()
        'Déclaration des variables de travail
        Dim args() As String = System.Environment.GetCommandLineArgs()  'Contient les paramètres de la ligne de commandes

        Try
            'Valider le paramètre de la table des statistiques.
            Call ValiderParametreTableStatistiques(args)

            'Valider le paramètre de la Geodatabase des classes à traiter.
            Call ValiderParametreGeodatabaseClasses(args)

            'Valider le paramètre de la liste des classes à traiter.
            Call ValiderParametreListeClasses(args)

            'Valider le paramètre de l'attribut contenant l'identifiant de découpage à traiter.
            Call ValiderParametreAttributDecoupage(args)

            'Valider le paramètre de la liste des identifiants à traiter.
            Call ValiderParametreListeIdentifiants(args)

            'Valider le paramètre du fichier journal dans lequel l'information sur l'exécution du traitement sera écrite.
            Call ValiderParametreFichierJournal(args)

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            args = Nothing
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre de la table des contraintes d'intégrité.
    '''</summary>
    '''
    Sub ValiderParametreTableStatistiques(ByVal args() As String)
        Try
            'Vérifier si le paramètre de la table des statistiques est présent.
            If args.Length - 1 > 0 Then
                'Vérifier si le paramètre contient le nom de la table des statistiques
                If args(1) <> "#" Then
                    'Définir le nom de la table des statistiques
                    m_NomTableStatistiques = args(1)
                End If

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreTableStatistiques", "ERREUR : Le paramètre du nom de la table des statistiques est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre du nom de la Geodatabase des classes à traiter.
    '''</summary>
    '''
    Sub ValiderParametreGeodatabaseClasses(ByVal args() As String)
        Try
            'Vérifier si le paramètre de la Geodatabase des classes est présent.
            If args.Length - 1 > 1 Then
                'Vérifier si le paramètre contient le nom de la Géodatabase des classes
                If args(2) <> "#" Then
                    'Définir le nom de la Géodatabase des classes
                    m_NomGeodatabaseClasses = args(2)
                End If

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreGeodatabaseClasses", "ERREUR : Le paramètre de la Geodatabase des classes est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre de la liste des classes à traiter.
    '''</summary>
    '''
    Sub ValiderParametreListeClasses(ByVal args() As String)
        Try
            'Valider le paramètre de la liste des classes à traiter.
            If args.Length - 1 > 2 Then
                'Vérifier si le paramètre contient la liste des classes
                If args(3) <> "#" Then
                    'Définir la liste des classes
                    m_ListeClasses = args(3).ToUpper
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre du nom de l'attribut contenant l'identifiant de découpage à valider.
    '''</summary>
    '''
    Sub ValiderParametreAttributDecoupage(ByVal args() As String)
        Try
            'Valider le paramètre du nom de l'attribut contenant l'identifiant de découpage à traiter
            If args.Length - 1 > 3 Then
                'Vérifier si le paramètre contient le nom de l'attribut de découpage
                If args(4) <> "#" Then
                    'Définir le nom de l'attribut de découpage
                    m_NomAttributDecoupage = args(4).ToUpper
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre de la liste des identifiants.
    '''</summary>
    '''
    Sub ValiderParametreListeIdentifiants(ByVal args() As String)
        Try
            'Vérifier si le paramètre de la liste des identifiants. est présent.
            If args.Length - 1 > 4 Then
                'Vérifier si le paramètre la liste des identifiants.
                If args(5) <> "#" Then
                    'Définir la liste des identifiants.
                    m_ListeIdentifiants = args(5).ToUpper
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre du fichier journal dans lequel l'information sur l'exécution du traitement sera écrite.
    '''</summary>
    '''
    Sub ValiderParametreFichierJournal(ByVal args() As String)
        Try
            'Valider le paramètre du répertoire dans lequel les erreurs seront écrites
            If args.Length - 1 > 5 Then
                'Vérifier si le paramètre contient le nom du fichier journal
                If args(6) <> "#" Then
                    'Définir le nom du fichier journal
                    m_NomFichierJournal = args(6)
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        End Try
    End Sub
End Module
