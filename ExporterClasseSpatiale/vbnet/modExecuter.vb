Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.ADF
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
''' Module principale permettant l'exécution de l'export d'une classe spatiale.
''' 
''' Les 3 paramètres de la ligne de commande du programme sont les suivants:
''' -------------------------------------------------------------------------
''' 1-Classe spatiale à exporter : Nom complet de la classe spatiale à exporter.
'''                                Obligatoire, Défaut : 
''' 2-Nouvelle classe spatiale   : Nom complet de la nouvelle classe spatiale.
'''                                Obligatoire, Défaut : 
''' 3-Nom du fichier journal     : Nom complet du fichier contenant le journal de l'exécution du traitement.
'''                                Obligatoire, Défaut : 
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
''' Date : 20 octobre 2016
'''</remarks>
''' 
Module modExecuter
    '''<summary> Interface d'initialisation des licences ESRI.</summary>
    Private m_AOLicenseInitializer As LicenseInitializer = New ExporterClasseSpatiale.LicenseInitializer()
    '''<summary>Nom de la classe spatiale d'entrée.</summary>
    Private m_NomClasseSpatialeEntree As String = ""
    '''<summary>Nom de la classe spatiale de sortie.</summary>
    Private m_NomClasseSpatialeSortie As String = ""
    '''<summary>Nom du fichier journal dans lequel l'exécution du traitement sera inscrit.</summary>
    Private m_NomFichierJournal As String = ""
    '''<summary>Nombre total d'éléments traités.</summary>
    Private m_NombreTotalElements As Long = 0
    '''<summary>Interface qui permet d'annuler l'exécution du traitement en inteactif.</summary>
    Private m_TrackCancel As ITrackCancel = Nothing

    <STAThread()> _
    Sub Main()
        'Déclarer les variables de travail

        Try
            'ESRI License Initializer generated code.
            m_AOLicenseInitializer.InitializeApplication(New esriLicenseProductCode() {esriLicenseProductCode.esriLicenseProductCodeStandard}, _
                                                         New esriLicenseExtensionCode() {})

            'Valider les parametres de la ligne de commandes
            Call ValiderParametres()

            'Permettre d'annuler la sélection avec la touche ESC
            m_TrackCancel = New CancelTracker
            m_TrackCancel.CancelOnKeyPress = False
            m_TrackCancel.CancelOnClick = False

            'Exécuter le traitement d'export
            Call Executer()

            'Retourner le code d'exéution du traitement
            System.Environment.Exit(0)

        Catch ex As Exception
            'Afficher l'erreur
            Console.WriteLine(ex.Message)
            'Retourner le code d'échec du traitement
            System.Environment.Exit(-1)
        Finally
            'Vider la mémoire
            m_TrackCancel = Nothing
            m_NomClasseSpatialeEntree = Nothing
            m_NomClasseSpatialeSortie = Nothing
            m_NomFichierJournal = Nothing
            'Fermer adéquatement l'application utilisant les licences ESRI
            m_AOLicenseInitializer.ShutdownApplication()
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider et définir les paramètres du programme.
    '''</summary>
    '''
    Sub Executer()
        'Déclaration des variables de travail
        Dim dDateDebut As DateTime = Nothing            'Contient la date de début du traitement.

        Try
            'Définir la date de début
            dDateDebut = System.DateTime.Now

            'Vérifier si le nom du fichier journal est présent
            If m_NomFichierJournal.Length > 0 Then
                'Redéfinir les noms de fichier contenant le mot %DATE_TIME%
                m_NomFichierJournal = m_NomFichierJournal.Replace("%DATE_TIME%", dDateDebut.ToString("yyyyMMdd_HHmmss"))
                'Vérifier si les répertoires existent
                If Not IO.Directory.Exists(IO.Path.GetDirectoryName(m_NomFichierJournal)) Then
                    'Créer le répertoire
                    IO.Directory.CreateDirectory(IO.Path.GetDirectoryName(m_NomFichierJournal))
                End If
            End If

            'Afficher les paramètres d'exécution du traitement
            EcrireMessage("")
            EcrireMessage("--------------------------------------------------------------------------------")
            EcrireMessage("-Version : " & IO.File.GetLastWriteTime(System.Reflection.Assembly.GetExecutingAssembly().Location).ToString)
            EcrireMessage("-Usager  : " & System.Environment.GetEnvironmentVariable("USERNAME"))
            EcrireMessage("-Date    : " & dDateDebut.ToString)
            EcrireMessage("")
            EcrireMessage("-Paramètres :")
            EcrireMessage(" ------------------------")
            EcrireMessage(" Nom de la classe d'entrée   : " & m_NomClasseSpatialeEntree)
            EcrireMessage(" Nom de la classe de sortie  : " & m_NomClasseSpatialeSortie)
            EcrireMessage(" Journal d'exécution         : " & m_NomFichierJournal)
            EcrireMessage("--------------------------------------------------------------------------------")

            'Écrire la statistique d'utilisation
            Call EcrireStatistiqueUtilisation(m_NomClasseSpatialeEntree & " " & m_NomClasseSpatialeSortie)

            'Exporter la classe spatiale
            EcrireMessage("")
            EcrireMessage("Exportation en cours ...")
            Call Exporter(m_NomClasseSpatialeEntree, m_NomClasseSpatialeSortie)

            'Afficher le résultat de l'exécution de la requête
            EcrireMessage("")
            EcrireMessage("-Statistiques sur le traitement exécuté:")
            EcrireMessage(" ---------------------------------------")
            EcrireMessage("  Nombre total d'éléments traités      : " & m_NombreTotalElements.ToString)
            EcrireMessage("")
            EcrireMessage("-Temps total d'exécution : " & System.DateTime.Now.Subtract(dDateDebut).ToString)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            dDateDebut = Nothing
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet d'exporter la classe d'entrée vers la classe de sortie.
    '''</summary>
    '''
    Sub Exporter(ByVal sNomClasseSpatialeEntree As String, ByVal sNomClasseSpatialeSortie As String)
        'Déclaration des variables de travail
        Dim pFeatureClassEntree As IFeatureClass = Nothing      'Interface contenant la classe spatiale d'entrée.
        Dim pFeatureClassSortie As IFeatureClass = Nothing      'Interface contenant la classe spatiale de sortie.
        Dim pSchemaLock As ISchemaLock = Nothing                'Interface pour bloquer la classe de sortie.
        Dim pFeatureClassLoad As IFeatureClassLoad = Nothing    'Interface utilisé pour indiquer le mode de chargement.
        Dim pSearchCursor As IFeatureCursor = Nothing           'Interface pour rechercher les éléments.
        Dim pInsertCursor As IFeatureCursor = Nothing           'Interface pour insérer les éléments.
        Dim pFeature As IFeature = Nothing                      'Interface contenant l'élément de la classe d'entrée.
        Dim pFeatureBuffer As IFeatureBuffer = Nothing          'Interface contenant l'élément à écrire dans la classe de sortie.
        Dim iPosAtt() As Integer        'Contient les position des attributs dans la classe de sortie.

        Try
            'Définir la classe spatiale d'entrée
            pFeatureClassEntree = DefinirClasseSpatiale(sNomClasseSpatialeEntree)

            'Définir la classe spatiale d'entrée
            pFeatureClassSortie = CreerClasseSpatiale(sNomClasseSpatialeSortie, pFeatureClassEntree)

            'Interface pour bloquer la classe de sortie
            pSchemaLock = CType(pFeatureClassSortie, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            'Interface pour indiquer le mode de chargement dans la classe de sortie
            pFeatureClassLoad = CType(pFeatureClassSortie, IFeatureClassLoad)
            pFeatureClassLoad.LoadOnlyMode = True

            'Définir le vecteur des positions d'attribut
            ReDim iPosAtt(pFeatureClassEntree.Fields.FieldCount - 1)
            'Traiter tous les attributs
            For i = 0 To pFeatureClassEntree.Fields.FieldCount - 1
                'Définir la position de l'attribut dans la classe de sortie
                iPosAtt(i) = pFeatureClassSortie.Fields.FindField(pFeatureClassEntree.Fields.Field(i).Name)
            Next

            'Définir le curseur d'insertion
            pInsertCursor = pFeatureClassSortie.Insert(True)

            'Créer un élément vide à écrire dans la classe de sortie
            pFeatureBuffer = pFeatureClassSortie.CreateFeatureBuffer

            'Définir le curseur de recherche
            pSearchCursor = pFeatureClassEntree.Search(Nothing, False)

            'Extraire le premier élément
            pFeature = pSearchCursor.NextFeature

            'Traiter tous les éléments de la classe d'entrée
            Do Until pFeature Is Nothing
                'Compter le nombre d'éléments
                m_NombreTotalElements = m_NombreTotalElements + 1

                'Traiter tous les attributs
                For i = 0 To pFeature.Fields.FieldCount - 1
                    'Vérifier si l'attribut est éditable
                    If pFeatureBuffer.Fields.Field(i).Editable = True Then
                        'Définir la valeur de l'élément d'écriture
                        pFeatureBuffer.Value(iPosAtt(i)) = pFeature.Value(i)
                    End If
                Next

                'Ajouter l'élément dans la classe de sortie
                pInsertCursor.InsertFeature(pFeatureBuffer)

                'Vérifier si on doit faire un Flush
                If (m_NombreTotalElements Mod 10000) = 0 Then
                    'Vider l'écriture des éléments
                    pInsertCursor.Flush()
                End If

                'Extraire le prochain élément
                pFeature = pSearchCursor.NextFeature
            Loop

            'Vider l'écriture des éléments
            pInsertCursor.Flush()

            'Libérer les curseurs des classes
            ComReleaser.ReleaseCOMObject(pSearchCursor)
            ComReleaser.ReleaseCOMObject(pInsertCursor)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Libérer la classe de sortie
            If pSchemaLock IsNot Nothing Then pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
            If pFeatureClassLoad IsNot Nothing Then pFeatureClassLoad.LoadOnlyMode = False
            'Vider la mémoire
            pFeatureClassEntree = Nothing
            pFeatureClassSortie = Nothing
            pSchemaLock = Nothing
            pFeatureClassLoad = Nothing
            pSearchCursor = Nothing
            pInsertCursor = Nothing
            pFeature = Nothing
            pFeatureBuffer = Nothing
            iPosAtt = Nothing
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet d'exporter la classe d'entrée vers la classe de sortie.
    '''</summary>
    '''
    Sub Exporter2(ByVal sNomClasseSpatialeEntree As String, ByVal sNomClasseSpatialeSortie As String)
        'Déclaration des variables de travail
        Dim pFeatureClassEntree As IFeatureClass = Nothing      'Interface contenant la classe spatiale d'entrée.
        Dim pFeatureClassSortie As IFeatureClass = Nothing      'Interface contenant la classe spatiale de sortie.
        Dim pSchemaLock As ISchemaLock = Nothing                'Interface pour bloquer la classe de sortie.
        Dim pFeatureClassLoad As IFeatureClassLoad = Nothing    'Interface utilisé pour indiquer le mode de chargement.
        Dim pFeatureClassWrite As IFeatureClassWrite = Nothing  'Interface utilisé pour écrire les éléments.
        Dim pSearchCursor As IFeatureCursor = Nothing           'Interface pour rechercher les éléments.
        Dim pFeature As IFeature = Nothing                      'Interface contenant l'élément de la classe d'entrée.
        Dim pFeatureBuffer As IFeature = Nothing                'Interface contenant l'élément à écrire dans la classe de sortie.
        Dim pSet As ISet = New ESRI.ArcGIS.esriSystem.Set       'Interface contenant un ensemble d'éléments.
        Dim iPosAtt() As Integer        'Contient les position des attributs dans la classe de sortie.

        Try
            'Définir la classe spatiale d'entrée
            pFeatureClassEntree = DefinirClasseSpatiale(sNomClasseSpatialeEntree)

            'Définir la classe spatiale d'entrée
            pFeatureClassSortie = CreerClasseSpatiale(sNomClasseSpatialeSortie, pFeatureClassEntree)

            'Interface pour bloquer la classe de sortie
            pSchemaLock = CType(pFeatureClassSortie, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            'Interface pour indiquer le mode de chargement dans la classe de sortie
            pFeatureClassLoad = CType(pFeatureClassSortie, IFeatureClassLoad)
            pFeatureClassLoad.LoadOnlyMode = True

            'Interface pour écrire les éléments
            pFeatureClassWrite = CType(pFeatureClassSortie, IFeatureClassWrite)

            'Définir le vecteur des positions d'attribut
            ReDim iPosAtt(pFeatureClassEntree.Fields.FieldCount - 1)
            'Traiter tous les attributs
            For i = 0 To pFeatureClassEntree.Fields.FieldCount - 1
                'Définir la position de l'attribut dans la classe de sortie
                iPosAtt(i) = pFeatureClassSortie.Fields.FindField(pFeatureClassEntree.Fields.Field(i).Name)
            Next

            'Définir le curseur de recherche
            EcrireMessage("")
            EcrireMessage("Lecture des éléments en cours ...")
            pSearchCursor = pFeatureClassEntree.Search(Nothing, False)

            'Extraire le premier élément
            pFeature = pSearchCursor.NextFeature

            'Traiter tous les éléments de la classe d'entrée
            Do Until pFeature Is Nothing
                'Compter le nombre d'éléments
                m_NombreTotalElements = m_NombreTotalElements + 1

                'Créer un élément vide à écrire dans la classe de sortie
                pFeatureBuffer = pFeatureClassSortie.CreateFeature

                'Traiter tous les attributs
                For i = 0 To pFeature.Fields.FieldCount - 1
                    'Vérifier si l'attribut est éditable
                    If pFeatureBuffer.Fields.Field(i).Editable = True Then
                        'Définir la valeur de l'élément d'écriture
                        pFeatureBuffer.Value(iPosAtt(i)) = pFeature.Value(i)
                    End If
                Next

                'Ajouter l'élément
                pSet.Add(pFeatureBuffer)

                'Extraire le prochain élément
                pFeature = pSearchCursor.NextFeature
            Loop

            'Écrire les éléments dans la classe
            EcrireMessage("")
            EcrireMessage("Écriture des éléments en cours ...")
            pFeatureClassWrite.WriteFeatures(pSet)

            'Libérer les curseurs des classes
            ComReleaser.ReleaseCOMObject(pSearchCursor)

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Libérer la classe de sortie
            If pSchemaLock IsNot Nothing Then pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
            If pFeatureClassLoad IsNot Nothing Then pFeatureClassLoad.LoadOnlyMode = False
            'Vider la mémoire
            pFeatureClassEntree = Nothing
            pFeatureClassSortie = Nothing
            pSchemaLock = Nothing
            pFeatureClassLoad = Nothing
            pFeatureClassWrite = Nothing
            pSearchCursor = Nothing
            pFeature = Nothing
            pFeatureBuffer = Nothing
            pSet = Nothing
            iPosAtt = Nothing
        End Try
    End Sub

    '''<summary>
    '''Fonction qui permet de définir et retourner une classe spatiale.
    '''</summary>
    ''' 
    '''<param name="sNomClasseSpatiale"> Nom de la table contenant les statistiques d'erreurs et de traitement.</param>
    ''' 
    '''<returns>"IFeatureClass" contenant une classe spatiale. Si le nom de la table est invalide, Nothing sera retourné.</returns>
    ''' 
    Private Function CreerClasseSpatiale(ByVal sNomClasseSpatiale As String, ByVal pBaseFeatureClass As IFeatureClass) As IFeatureClass
        'Déclaration des variables de travail
        Dim pWorkspace As IWorkspace2 = Nothing                 'Interface utilisé pour vérifier la présence d'une classe spatiale.
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface contenant une Géodatabase.
        Dim sNomClasse As String = ""                           'Contient le nom de la classe spatiale.
        Dim sNomGeodatabase As String = ""                      'Contient le nom de la Géodatabase.
        Dim pUID As New UID                                     'Interface pour générer un UID.

        'Par défaut, la classe spatiale est invalide
        CreerClasseSpatiale = Nothing

        Try
            'Vérifier si le nom de laclasse est présent
            If sNomClasseSpatiale.Length > 0 Then
                'Définir le nom de la table des statistiques
                sNomClasseSpatiale = sNomClasseSpatiale.ToLower.Replace("database connections", Environment.GetEnvironmentVariable("APPDATA") & "\ESRI\Desktop10.3\ArcCatalog")

                'Définir le nom de la classe sans le nom de la Géodatabase
                sNomClasse = System.IO.Path.GetFileName(sNomClasseSpatiale)

                'Définir le nom de la géodatabase sans celui du nom de la table
                sNomGeodatabase = sNomClasseSpatiale.Replace("\" & sNomClasse, "")
                sNomGeodatabase = sNomGeodatabase.Replace(sNomClasse, "")

                'Vérifier si le nom de la Géodatabase de la table est absent
                If sNomGeodatabase.Length = 0 Then
                    'Retourner l'erreur
                    Throw New Exception("ERREUR : Le nom de la Géodatabase est absent du nom de la classe : " & sNomGeodatabase)

                    'Si le nom de la Géodatabase est présent
                Else
                    'Ouvrir la géodatabase de la classe spatiale
                    pFeatureWorkspace = CType(DefinirGeodatabase(sNomGeodatabase), IFeatureWorkspace)

                    'Vérifier si la Géodatabase est valide
                    If pFeatureWorkspace Is Nothing Then
                        'Retourner l'erreur
                        Throw New Exception("ERREUR : Le nom de la Géodatabase est invalide : " & sNomGeodatabase)
                    End If
                End If

                'Interface pour vérifier si la classe existe
                pWorkspace = CType(pFeatureWorkspace, IWorkspace2)

                'Vérifier si la classe existe
                If pWorkspace.NameExists(esriDatasetType.esriDTFeatureClass, sNomClasse) Then
                    'Retourner l'erreur
                    Throw New Exception("ERREUR : La classe spatiale existe déjà : " & sNomClasse)

                    'Si la classe n'existe pas
                Else
                    Try
                        'Créer un nouveau UID
                        pUID.Generate()
                        'Définir le type d'élément
                        pUID.Value = "esriGeodatabase.Feature"
                        'Ouvrir la table des statistiques
                        CreerClasseSpatiale = pFeatureWorkspace.CreateFeatureClass(sNomClasse, pBaseFeatureClass.Fields, pUID, Nothing, esriFeatureType.esriFTSimple, pBaseFeatureClass.ShapeFieldName, "")

                    Catch ex As Exception
                        'Retourner l'erreur
                        Throw New Exception("ERREUR : Incapable de créer la classe spatiale : " & sNomClasse)
                    End Try
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pWorkspace = Nothing
            pFeatureWorkspace = Nothing
            sNomClasse = Nothing
            sNomGeodatabase = Nothing
            pUID = Nothing
        End Try
    End Function

    '''<summary>
    '''Fonction qui permet de définir et retourner une classe spatiale.
    '''</summary>
    ''' 
    '''<param name="sNomClasseSpatiale"> Nom de la table contenant les statistiques d'erreurs et de traitement.</param>
    ''' 
    '''<returns>"IFeatureClass" contenant une classe spatiale. Si le nom de la table est invalide, Nothing sera retourné.</returns>
    ''' 
    Private Function DefinirClasseSpatiale(ByVal sNomClasseSpatiale As String) As IFeatureClass
        'Déclaration des variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface contenant une Géodatabase.
        Dim sNomClasse As String = ""                           'Contient le nom de la classe spatiale.
        Dim sNomGeodatabase As String = ""                      'Contient le nom de la Géodatabase.

        'Par défaut, la classe spatiale est invalide
        DefinirClasseSpatiale = Nothing

        Try
            'Vérifier si le nom de laclasse est présent
            If sNomClasseSpatiale.Length > 0 Then
                'Définir le nom de la table des statistiques
                sNomClasseSpatiale = sNomClasseSpatiale.ToLower.Replace("database connections", Environment.GetEnvironmentVariable("APPDATA") & "\ESRI\Desktop10.3\ArcCatalog")

                'Définir le nom de la classe sans le nom de la Géodatabase
                sNomClasse = System.IO.Path.GetFileName(sNomClasseSpatiale)

                'Définir le nom de la géodatabase sans celui du nom de la table
                sNomGeodatabase = sNomClasseSpatiale.Replace("\" & sNomClasse, "")
                sNomGeodatabase = sNomGeodatabase.Replace(sNomClasse, "")

                'Vérifier si le nom de la Géodatabase de la table est absent
                If sNomGeodatabase.Length = 0 Then
                        'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Le nom de la Géodatabase est absent du nom de la classe : " & sNomGeodatabase)

                    'Si le nom de la Géodatabase est présent
                Else
                    'Ouvrir la géodatabase de la classe spatiale
                    pFeatureWorkspace = CType(DefinirGeodatabase(sNomGeodatabase), IFeatureWorkspace)

                    'Vérifier si la Géodatabase est valide
                    If pFeatureWorkspace Is Nothing Then
                        'Retourner l'erreur
                        Err.Raise(-1, , "ERREUR : Le nom de la Géodatabase est invalide : " & sNomGeodatabase)
                    End If
                End If

                Try
                    'Ouvrir la table des statistiques
                    DefinirClasseSpatiale = pFeatureWorkspace.OpenFeatureClass(sNomClasse)
                Catch ex As Exception
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Incapable d'ouvrir la classe spatiale : " & sNomClasse)
                End Try
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pFeatureWorkspace = Nothing
            sNomClasse = Nothing
            sNomGeodatabase = Nothing
        End Try
    End Function

    '''<summary>
    '''Routine qui permet d'ouvrir et retourner la Geodatabase à partir d'un nom de Géodatabase.
    '''</summary>
    '''
    '''<param name="sNomGeodatabase"> Nom de la géodatabase à ouvrir.</param>
    ''' 
    Private Function DefinirGeodatabase(ByRef sNomGeodatabase As String) As IWorkspace
        'Déclaration des variables de travail
        Dim pFactoryType As Type = Nothing                      'Interface utilisé pour définir le type de géodatabase.
        Dim pWorkspaceFactory As IWorkspaceFactory = Nothing    'Interface utilisé pour ouvrir la géodatabase.

        'Par défaut, aucune Géodatabase n'est retournée
        DefinirGeodatabase = Nothing

        Try
            'Valider le paramètre de la Geodatabase
            If sNomGeodatabase.Length > 0 Then
                'Redéfinir le nom de la Géodatbase lorsque c'est une SDE
                sNomGeodatabase = sNomGeodatabase.ToLower.Replace("database connections", Environment.GetEnvironmentVariable("APPDATA") & "\ESRI\Desktop10.3\ArcCatalog")

                'Vérifier si la Geodatabase est SDE
                If sNomGeodatabase.Contains(".sde") Then
                    'Définir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.SdeWorkspaceFactory")

                    'Si la Geodatabse est une File Geodatabase
                ElseIf sNomGeodatabase.Contains(".gdb") Then
                    'Définir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.FileGDBWorkspaceFactory")

                    'Si la Geodatabse est une personnelle Geodatabase
                ElseIf sNomGeodatabase.Contains(".mdb") Then
                    'Définir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.AccessWorkspaceFactory")

                    'Sinon
                Else
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Le nom de la Géodatabase ne correspond pas à une Geodatabase !")
                End If

                'Interface pour ouvrir le Workspace
                pWorkspaceFactory = CType(Activator.CreateInstance(pFactoryType), IWorkspaceFactory)

                Try
                    'Ouvrir le workspace de la Géodatabase
                    DefinirGeodatabase = pWorkspaceFactory.OpenFromFile(sNomGeodatabase, 0)
                Catch ex As Exception
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Incapable d'ouvrir la Géodatabase : " & sNomGeodatabase)
                End Try
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pFactoryType = Nothing
            pWorkspaceFactory = Nothing
        End Try
    End Function

    '''<summary>
    '''Routine qui permet de valider et définir les paramètres du programme.
    '''</summary>
    '''
    Sub ValiderParametres()
        'Déclaration des variables de travail
        Dim args() As String = System.Environment.GetCommandLineArgs()  'Contient les paramètres de la ligne de commandes

        Try
            'Valider le paramètre de la Geodatabase des classes à valider.
            Call ValiderParametreClasseSpatialeEntree(args)

            'Valider le paramètre de la table contenant les contraintes d'intégrité.
            Call ValiderParametreClasseSpatialeSortie(args)

            'Valider le paramètre du fichier journal dans lequel l'information sur l'exécution du traitement sera écrite.
            Call ValiderParametreFichierJournal(args)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            args = Nothing
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre du nom de la Geodatabase des classes à valider.
    '''</summary>
    '''
    Sub ValiderParametreClasseSpatialeEntree(ByVal args() As String)
        Try
            'Vérifier si le paramètre de la classe spatiale d'entrée est présent.
            If args.Length - 1 > 0 Then
                'Définir le nom de la classe spatiale d'entrée
                m_NomClasseSpatialeEntree = args(1)

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreClasseSpatialeEntree", "ERREUR : Le paramètre de la classe spatiale d'entrée est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre de la table des contraintes d'intégrité.
    '''</summary>
    '''
    Sub ValiderParametreClasseSpatialeSortie(ByVal args() As String)
        Try
            'Vérifier si le paramètre de la classe spatiale de sortie est présent.
            If args.Length - 1 > 1 Then
                'Définir le nom de la classe spatiale de sortie
                m_NomClasseSpatialeSortie = args(2)

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreClasseSpatialeSortie", "ERREUR : Le paramètre de la classe spatiale de sortie est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le paramètre du fichier journal dans lequel l'information sur l'exécution du traitement sera écrite.
    '''</summary>
    '''
    Sub ValiderParametreFichierJournal(ByVal args() As String)
        Try
            'Valider le paramètre du répertoire dans lequel les erreurs seront écrites
            If args.Length - 1 > 2 Then
                'Vérifier si le paramètre contient le nom du fichier journal
                If args(3) <> "#" Then
                    'Définir le nom du fichier journal
                    m_NomFichierJournal = args(3)
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'écrire le message d'exécution dans  un fichier journal et/ou dans la console.
    '''</summary>
    ''' 
    '''<param name="sMessage"> Message à écrire dans un fichier journal et/ou dans la console.</param>
    '''
    Private Sub EcrireMessage(ByVal sMessage As String)
        Try
            'Vérifier si le nom du fichier journal est présent
            If m_NomFichierJournal.Length > 0 Then
                'Écrire le message dans le RichTextBox
                File.AppendAllText(m_NomFichierJournal, sMessage & vbCrLf)
            End If

            'Écrire dans la console
            Console.WriteLine(sMessage)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'écrire les statistiques d'utilisation d'un usager.
    ''' 
    '''<param name="sCommande"> Commande à écrire dans le fichier de statistique d'utilisation.</param>
    '''<param name="sNomRepertoire"> Nom du répertoire dans lequel le fichier de statistique est présent.</param>
    ''' 
    '''</summary>
    '''
    Private Sub EcrireStatistiqueUtilisation(ByVal sCommande As String, Optional ByVal sNomRepertoire As String = "S:\Developpement\geo\")
        'Déclarer les variables de travail
        Dim oStreamWriter As StreamWriter = Nothing     'Objet utilisé pour écrire dans un fichier text.
        Dim sNomFichier As String = ""                  'Nom complet du fichier de statistique d'utilisation.
        Dim sNomUsager As String = ""                   'Nom de l'usager.

        Try
            'Définir le nom de l'usager
            sNomUsager = Environment.GetEnvironmentVariable("USERNAME")

            'Définir le nom complet du fichier
            sNomFichier = sNomRepertoire & sNomUsager & ".txt"

            'Vérifier si le fichier existe
            If File.Exists(sNomFichier) Then
                'Définir l'objet pour écrire à la fin du fichier
                oStreamWriter = File.AppendText(sNomFichier)

                'Si le fichier n'existe pas
            Else
                'Définir l'objet pour écrire dans un nouveau fichier créé
                oStreamWriter = File.CreateText(sNomFichier)

                'Écrire l'entête du fichier
                oStreamWriter.WriteLine("Date, 	 Env, 	 Usager, 	 UsagerBD, 	 UsagerSIB, 	 Outil")
            End If

            'Écrire la commande utilisée
            oStreamWriter.WriteLine(DateTime.Now.ToString & "," & vbTab & System.IO.Path.GetFileName(System.Environment.GetCommandLineArgs()(0)) & "," & vbTab & sNomUsager & "," & vbTab & "NONE," & vbTab & "NONE," & vbTab & sCommande)

            'Fermer le fichier
            oStreamWriter.Close()

        Catch ex As Exception
            'Retourner l'erreur
            'Throw
        Finally
            'Vider la mémoire
            oStreamWriter = Nothing
            sNomFichier = Nothing
            sNomUsager = Nothing
        End Try
    End Sub
End Module
