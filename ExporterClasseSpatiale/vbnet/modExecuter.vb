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
''' Module principale permettant l'ex�cution de l'export d'une classe spatiale.
''' 
''' Les 3 param�tres de la ligne de commande du programme sont les suivants:
''' -------------------------------------------------------------------------
''' 1-Classe spatiale � exporter : Nom complet de la classe spatiale � exporter.
'''                                Obligatoire, D�faut : 
''' 2-Nouvelle classe spatiale   : Nom complet de la nouvelle classe spatiale.
'''                                Obligatoire, D�faut : 
''' 3-Nom du fichier journal     : Nom complet du fichier contenant le journal de l'ex�cution du traitement.
'''                                Obligatoire, D�faut : 
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
    '''<summary>Nom de la classe spatiale d'entr�e.</summary>
    Private m_NomClasseSpatialeEntree As String = ""
    '''<summary>Nom de la classe spatiale de sortie.</summary>
    Private m_NomClasseSpatialeSortie As String = ""
    '''<summary>Nom du fichier journal dans lequel l'ex�cution du traitement sera inscrit.</summary>
    Private m_NomFichierJournal As String = ""
    '''<summary>Nombre total d'�l�ments trait�s.</summary>
    Private m_NombreTotalElements As Long = 0
    '''<summary>Interface qui permet d'annuler l'ex�cution du traitement en inteactif.</summary>
    Private m_TrackCancel As ITrackCancel = Nothing

    <STAThread()> _
    Sub Main()
        'D�clarer les variables de travail

        Try
            'ESRI License Initializer generated code.
            m_AOLicenseInitializer.InitializeApplication(New esriLicenseProductCode() {esriLicenseProductCode.esriLicenseProductCodeStandard}, _
                                                         New esriLicenseExtensionCode() {})

            'Valider les parametres de la ligne de commandes
            Call ValiderParametres()

            'Permettre d'annuler la s�lection avec la touche ESC
            m_TrackCancel = New CancelTracker
            m_TrackCancel.CancelOnKeyPress = False
            m_TrackCancel.CancelOnClick = False

            'Ex�cuter le traitement d'export
            Call Executer()

            'Retourner le code d'ex�ution du traitement
            System.Environment.Exit(0)

        Catch ex As Exception
            'Afficher l'erreur
            Console.WriteLine(ex.Message)
            'Retourner le code d'�chec du traitement
            System.Environment.Exit(-1)
        Finally
            'Vider la m�moire
            m_TrackCancel = Nothing
            m_NomClasseSpatialeEntree = Nothing
            m_NomClasseSpatialeSortie = Nothing
            m_NomFichierJournal = Nothing
            'Fermer ad�quatement l'application utilisant les licences ESRI
            m_AOLicenseInitializer.ShutdownApplication()
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider et d�finir les param�tres du programme.
    '''</summary>
    '''
    Sub Executer()
        'D�claration des variables de travail
        Dim dDateDebut As DateTime = Nothing            'Contient la date de d�but du traitement.

        Try
            'D�finir la date de d�but
            dDateDebut = System.DateTime.Now

            'V�rifier si le nom du fichier journal est pr�sent
            If m_NomFichierJournal.Length > 0 Then
                'Red�finir les noms de fichier contenant le mot %DATE_TIME%
                m_NomFichierJournal = m_NomFichierJournal.Replace("%DATE_TIME%", dDateDebut.ToString("yyyyMMdd_HHmmss"))
                'V�rifier si les r�pertoires existent
                If Not IO.Directory.Exists(IO.Path.GetDirectoryName(m_NomFichierJournal)) Then
                    'Cr�er le r�pertoire
                    IO.Directory.CreateDirectory(IO.Path.GetDirectoryName(m_NomFichierJournal))
                End If
            End If

            'Afficher les param�tres d'ex�cution du traitement
            EcrireMessage("")
            EcrireMessage("--------------------------------------------------------------------------------")
            EcrireMessage("-Version : " & IO.File.GetLastWriteTime(System.Reflection.Assembly.GetExecutingAssembly().Location).ToString)
            EcrireMessage("-Usager  : " & System.Environment.GetEnvironmentVariable("USERNAME"))
            EcrireMessage("-Date    : " & dDateDebut.ToString)
            EcrireMessage("")
            EcrireMessage("-Param�tres :")
            EcrireMessage(" ------------------------")
            EcrireMessage(" Nom de la classe d'entr�e   : " & m_NomClasseSpatialeEntree)
            EcrireMessage(" Nom de la classe de sortie  : " & m_NomClasseSpatialeSortie)
            EcrireMessage(" Journal d'ex�cution         : " & m_NomFichierJournal)
            EcrireMessage("--------------------------------------------------------------------------------")

            '�crire la statistique d'utilisation
            Call EcrireStatistiqueUtilisation(m_NomClasseSpatialeEntree & " " & m_NomClasseSpatialeSortie)

            'Exporter la classe spatiale
            EcrireMessage("")
            EcrireMessage("Exportation en cours ...")
            Call Exporter(m_NomClasseSpatialeEntree, m_NomClasseSpatialeSortie)

            'Afficher le r�sultat de l'ex�cution de la requ�te
            EcrireMessage("")
            EcrireMessage("-Statistiques sur le traitement ex�cut�:")
            EcrireMessage(" ---------------------------------------")
            EcrireMessage("  Nombre total d'�l�ments trait�s      : " & m_NombreTotalElements.ToString)
            EcrireMessage("")
            EcrireMessage("-Temps total d'ex�cution : " & System.DateTime.Now.Subtract(dDateDebut).ToString)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la m�moire
            dDateDebut = Nothing
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet d'exporter la classe d'entr�e vers la classe de sortie.
    '''</summary>
    '''
    Sub Exporter(ByVal sNomClasseSpatialeEntree As String, ByVal sNomClasseSpatialeSortie As String)
        'D�claration des variables de travail
        Dim pFeatureClassEntree As IFeatureClass = Nothing      'Interface contenant la classe spatiale d'entr�e.
        Dim pFeatureClassSortie As IFeatureClass = Nothing      'Interface contenant la classe spatiale de sortie.
        Dim pSchemaLock As ISchemaLock = Nothing                'Interface pour bloquer la classe de sortie.
        Dim pFeatureClassLoad As IFeatureClassLoad = Nothing    'Interface utilis� pour indiquer le mode de chargement.
        Dim pSearchCursor As IFeatureCursor = Nothing           'Interface pour rechercher les �l�ments.
        Dim pInsertCursor As IFeatureCursor = Nothing           'Interface pour ins�rer les �l�ments.
        Dim pFeature As IFeature = Nothing                      'Interface contenant l'�l�ment de la classe d'entr�e.
        Dim pFeatureBuffer As IFeatureBuffer = Nothing          'Interface contenant l'�l�ment � �crire dans la classe de sortie.
        Dim iPosAtt() As Integer        'Contient les position des attributs dans la classe de sortie.

        Try
            'D�finir la classe spatiale d'entr�e
            pFeatureClassEntree = DefinirClasseSpatiale(sNomClasseSpatialeEntree)

            'D�finir la classe spatiale d'entr�e
            pFeatureClassSortie = CreerClasseSpatiale(sNomClasseSpatialeSortie, pFeatureClassEntree)

            'Interface pour bloquer la classe de sortie
            pSchemaLock = CType(pFeatureClassSortie, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            'Interface pour indiquer le mode de chargement dans la classe de sortie
            pFeatureClassLoad = CType(pFeatureClassSortie, IFeatureClassLoad)
            pFeatureClassLoad.LoadOnlyMode = True

            'D�finir le vecteur des positions d'attribut
            ReDim iPosAtt(pFeatureClassEntree.Fields.FieldCount - 1)
            'Traiter tous les attributs
            For i = 0 To pFeatureClassEntree.Fields.FieldCount - 1
                'D�finir la position de l'attribut dans la classe de sortie
                iPosAtt(i) = pFeatureClassSortie.Fields.FindField(pFeatureClassEntree.Fields.Field(i).Name)
            Next

            'D�finir le curseur d'insertion
            pInsertCursor = pFeatureClassSortie.Insert(True)

            'Cr�er un �l�ment vide � �crire dans la classe de sortie
            pFeatureBuffer = pFeatureClassSortie.CreateFeatureBuffer

            'D�finir le curseur de recherche
            pSearchCursor = pFeatureClassEntree.Search(Nothing, False)

            'Extraire le premier �l�ment
            pFeature = pSearchCursor.NextFeature

            'Traiter tous les �l�ments de la classe d'entr�e
            Do Until pFeature Is Nothing
                'Compter le nombre d'�l�ments
                m_NombreTotalElements = m_NombreTotalElements + 1

                'Traiter tous les attributs
                For i = 0 To pFeature.Fields.FieldCount - 1
                    'V�rifier si l'attribut est �ditable
                    If pFeatureBuffer.Fields.Field(i).Editable = True Then
                        'D�finir la valeur de l'�l�ment d'�criture
                        pFeatureBuffer.Value(iPosAtt(i)) = pFeature.Value(i)
                    End If
                Next

                'Ajouter l'�l�ment dans la classe de sortie
                pInsertCursor.InsertFeature(pFeatureBuffer)

                'V�rifier si on doit faire un Flush
                If (m_NombreTotalElements Mod 10000) = 0 Then
                    'Vider l'�criture des �l�ments
                    pInsertCursor.Flush()
                End If

                'Extraire le prochain �l�ment
                pFeature = pSearchCursor.NextFeature
            Loop

            'Vider l'�criture des �l�ments
            pInsertCursor.Flush()

            'Lib�rer les curseurs des classes
            ComReleaser.ReleaseCOMObject(pSearchCursor)
            ComReleaser.ReleaseCOMObject(pInsertCursor)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Lib�rer la classe de sortie
            If pSchemaLock IsNot Nothing Then pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
            If pFeatureClassLoad IsNot Nothing Then pFeatureClassLoad.LoadOnlyMode = False
            'Vider la m�moire
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
    '''Routine qui permet d'exporter la classe d'entr�e vers la classe de sortie.
    '''</summary>
    '''
    Sub Exporter2(ByVal sNomClasseSpatialeEntree As String, ByVal sNomClasseSpatialeSortie As String)
        'D�claration des variables de travail
        Dim pFeatureClassEntree As IFeatureClass = Nothing      'Interface contenant la classe spatiale d'entr�e.
        Dim pFeatureClassSortie As IFeatureClass = Nothing      'Interface contenant la classe spatiale de sortie.
        Dim pSchemaLock As ISchemaLock = Nothing                'Interface pour bloquer la classe de sortie.
        Dim pFeatureClassLoad As IFeatureClassLoad = Nothing    'Interface utilis� pour indiquer le mode de chargement.
        Dim pFeatureClassWrite As IFeatureClassWrite = Nothing  'Interface utilis� pour �crire les �l�ments.
        Dim pSearchCursor As IFeatureCursor = Nothing           'Interface pour rechercher les �l�ments.
        Dim pFeature As IFeature = Nothing                      'Interface contenant l'�l�ment de la classe d'entr�e.
        Dim pFeatureBuffer As IFeature = Nothing                'Interface contenant l'�l�ment � �crire dans la classe de sortie.
        Dim pSet As ISet = New ESRI.ArcGIS.esriSystem.Set       'Interface contenant un ensemble d'�l�ments.
        Dim iPosAtt() As Integer        'Contient les position des attributs dans la classe de sortie.

        Try
            'D�finir la classe spatiale d'entr�e
            pFeatureClassEntree = DefinirClasseSpatiale(sNomClasseSpatialeEntree)

            'D�finir la classe spatiale d'entr�e
            pFeatureClassSortie = CreerClasseSpatiale(sNomClasseSpatialeSortie, pFeatureClassEntree)

            'Interface pour bloquer la classe de sortie
            pSchemaLock = CType(pFeatureClassSortie, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriExclusiveSchemaLock)

            'Interface pour indiquer le mode de chargement dans la classe de sortie
            pFeatureClassLoad = CType(pFeatureClassSortie, IFeatureClassLoad)
            pFeatureClassLoad.LoadOnlyMode = True

            'Interface pour �crire les �l�ments
            pFeatureClassWrite = CType(pFeatureClassSortie, IFeatureClassWrite)

            'D�finir le vecteur des positions d'attribut
            ReDim iPosAtt(pFeatureClassEntree.Fields.FieldCount - 1)
            'Traiter tous les attributs
            For i = 0 To pFeatureClassEntree.Fields.FieldCount - 1
                'D�finir la position de l'attribut dans la classe de sortie
                iPosAtt(i) = pFeatureClassSortie.Fields.FindField(pFeatureClassEntree.Fields.Field(i).Name)
            Next

            'D�finir le curseur de recherche
            EcrireMessage("")
            EcrireMessage("Lecture des �l�ments en cours ...")
            pSearchCursor = pFeatureClassEntree.Search(Nothing, False)

            'Extraire le premier �l�ment
            pFeature = pSearchCursor.NextFeature

            'Traiter tous les �l�ments de la classe d'entr�e
            Do Until pFeature Is Nothing
                'Compter le nombre d'�l�ments
                m_NombreTotalElements = m_NombreTotalElements + 1

                'Cr�er un �l�ment vide � �crire dans la classe de sortie
                pFeatureBuffer = pFeatureClassSortie.CreateFeature

                'Traiter tous les attributs
                For i = 0 To pFeature.Fields.FieldCount - 1
                    'V�rifier si l'attribut est �ditable
                    If pFeatureBuffer.Fields.Field(i).Editable = True Then
                        'D�finir la valeur de l'�l�ment d'�criture
                        pFeatureBuffer.Value(iPosAtt(i)) = pFeature.Value(i)
                    End If
                Next

                'Ajouter l'�l�ment
                pSet.Add(pFeatureBuffer)

                'Extraire le prochain �l�ment
                pFeature = pSearchCursor.NextFeature
            Loop

            '�crire les �l�ments dans la classe
            EcrireMessage("")
            EcrireMessage("�criture des �l�ments en cours ...")
            pFeatureClassWrite.WriteFeatures(pSet)

            'Lib�rer les curseurs des classes
            ComReleaser.ReleaseCOMObject(pSearchCursor)

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Lib�rer la classe de sortie
            If pSchemaLock IsNot Nothing Then pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)
            If pFeatureClassLoad IsNot Nothing Then pFeatureClassLoad.LoadOnlyMode = False
            'Vider la m�moire
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
    '''Fonction qui permet de d�finir et retourner une classe spatiale.
    '''</summary>
    ''' 
    '''<param name="sNomClasseSpatiale"> Nom de la table contenant les statistiques d'erreurs et de traitement.</param>
    ''' 
    '''<returns>"IFeatureClass" contenant une classe spatiale. Si le nom de la table est invalide, Nothing sera retourn�.</returns>
    ''' 
    Private Function CreerClasseSpatiale(ByVal sNomClasseSpatiale As String, ByVal pBaseFeatureClass As IFeatureClass) As IFeatureClass
        'D�claration des variables de travail
        Dim pWorkspace As IWorkspace2 = Nothing                 'Interface utilis� pour v�rifier la pr�sence d'une classe spatiale.
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface contenant une G�odatabase.
        Dim sNomClasse As String = ""                           'Contient le nom de la classe spatiale.
        Dim sNomGeodatabase As String = ""                      'Contient le nom de la G�odatabase.
        Dim pUID As New UID                                     'Interface pour g�n�rer un UID.

        'Par d�faut, la classe spatiale est invalide
        CreerClasseSpatiale = Nothing

        Try
            'V�rifier si le nom de laclasse est pr�sent
            If sNomClasseSpatiale.Length > 0 Then
                'D�finir le nom de la table des statistiques
                sNomClasseSpatiale = sNomClasseSpatiale.ToLower.Replace("database connections", Environment.GetEnvironmentVariable("APPDATA") & "\ESRI\Desktop10.3\ArcCatalog")

                'D�finir le nom de la classe sans le nom de la G�odatabase
                sNomClasse = System.IO.Path.GetFileName(sNomClasseSpatiale)

                'D�finir le nom de la g�odatabase sans celui du nom de la table
                sNomGeodatabase = sNomClasseSpatiale.Replace("\" & sNomClasse, "")
                sNomGeodatabase = sNomGeodatabase.Replace(sNomClasse, "")

                'V�rifier si le nom de la G�odatabase de la table est absent
                If sNomGeodatabase.Length = 0 Then
                    'Retourner l'erreur
                    Throw New Exception("ERREUR : Le nom de la G�odatabase est absent du nom de la classe : " & sNomGeodatabase)

                    'Si le nom de la G�odatabase est pr�sent
                Else
                    'Ouvrir la g�odatabase de la classe spatiale
                    pFeatureWorkspace = CType(DefinirGeodatabase(sNomGeodatabase), IFeatureWorkspace)

                    'V�rifier si la G�odatabase est valide
                    If pFeatureWorkspace Is Nothing Then
                        'Retourner l'erreur
                        Throw New Exception("ERREUR : Le nom de la G�odatabase est invalide : " & sNomGeodatabase)
                    End If
                End If

                'Interface pour v�rifier si la classe existe
                pWorkspace = CType(pFeatureWorkspace, IWorkspace2)

                'V�rifier si la classe existe
                If pWorkspace.NameExists(esriDatasetType.esriDTFeatureClass, sNomClasse) Then
                    'Retourner l'erreur
                    Throw New Exception("ERREUR : La classe spatiale existe d�j� : " & sNomClasse)

                    'Si la classe n'existe pas
                Else
                    Try
                        'Cr�er un nouveau UID
                        pUID.Generate()
                        'D�finir le type d'�l�ment
                        pUID.Value = "esriGeodatabase.Feature"
                        'Ouvrir la table des statistiques
                        CreerClasseSpatiale = pFeatureWorkspace.CreateFeatureClass(sNomClasse, pBaseFeatureClass.Fields, pUID, Nothing, esriFeatureType.esriFTSimple, pBaseFeatureClass.ShapeFieldName, "")

                    Catch ex As Exception
                        'Retourner l'erreur
                        Throw New Exception("ERREUR : Incapable de cr�er la classe spatiale : " & sNomClasse)
                    End Try
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la m�moire
            pWorkspace = Nothing
            pFeatureWorkspace = Nothing
            sNomClasse = Nothing
            sNomGeodatabase = Nothing
            pUID = Nothing
        End Try
    End Function

    '''<summary>
    '''Fonction qui permet de d�finir et retourner une classe spatiale.
    '''</summary>
    ''' 
    '''<param name="sNomClasseSpatiale"> Nom de la table contenant les statistiques d'erreurs et de traitement.</param>
    ''' 
    '''<returns>"IFeatureClass" contenant une classe spatiale. Si le nom de la table est invalide, Nothing sera retourn�.</returns>
    ''' 
    Private Function DefinirClasseSpatiale(ByVal sNomClasseSpatiale As String) As IFeatureClass
        'D�claration des variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface contenant une G�odatabase.
        Dim sNomClasse As String = ""                           'Contient le nom de la classe spatiale.
        Dim sNomGeodatabase As String = ""                      'Contient le nom de la G�odatabase.

        'Par d�faut, la classe spatiale est invalide
        DefinirClasseSpatiale = Nothing

        Try
            'V�rifier si le nom de laclasse est pr�sent
            If sNomClasseSpatiale.Length > 0 Then
                'D�finir le nom de la table des statistiques
                sNomClasseSpatiale = sNomClasseSpatiale.ToLower.Replace("database connections", Environment.GetEnvironmentVariable("APPDATA") & "\ESRI\Desktop10.3\ArcCatalog")

                'D�finir le nom de la classe sans le nom de la G�odatabase
                sNomClasse = System.IO.Path.GetFileName(sNomClasseSpatiale)

                'D�finir le nom de la g�odatabase sans celui du nom de la table
                sNomGeodatabase = sNomClasseSpatiale.Replace("\" & sNomClasse, "")
                sNomGeodatabase = sNomGeodatabase.Replace(sNomClasse, "")

                'V�rifier si le nom de la G�odatabase de la table est absent
                If sNomGeodatabase.Length = 0 Then
                        'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Le nom de la G�odatabase est absent du nom de la classe : " & sNomGeodatabase)

                    'Si le nom de la G�odatabase est pr�sent
                Else
                    'Ouvrir la g�odatabase de la classe spatiale
                    pFeatureWorkspace = CType(DefinirGeodatabase(sNomGeodatabase), IFeatureWorkspace)

                    'V�rifier si la G�odatabase est valide
                    If pFeatureWorkspace Is Nothing Then
                        'Retourner l'erreur
                        Err.Raise(-1, , "ERREUR : Le nom de la G�odatabase est invalide : " & sNomGeodatabase)
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
            'Vider la m�moire
            pFeatureWorkspace = Nothing
            sNomClasse = Nothing
            sNomGeodatabase = Nothing
        End Try
    End Function

    '''<summary>
    '''Routine qui permet d'ouvrir et retourner la Geodatabase � partir d'un nom de G�odatabase.
    '''</summary>
    '''
    '''<param name="sNomGeodatabase"> Nom de la g�odatabase � ouvrir.</param>
    ''' 
    Private Function DefinirGeodatabase(ByRef sNomGeodatabase As String) As IWorkspace
        'D�claration des variables de travail
        Dim pFactoryType As Type = Nothing                      'Interface utilis� pour d�finir le type de g�odatabase.
        Dim pWorkspaceFactory As IWorkspaceFactory = Nothing    'Interface utilis� pour ouvrir la g�odatabase.

        'Par d�faut, aucune G�odatabase n'est retourn�e
        DefinirGeodatabase = Nothing

        Try
            'Valider le param�tre de la Geodatabase
            If sNomGeodatabase.Length > 0 Then
                'Red�finir le nom de la G�odatbase lorsque c'est une SDE
                sNomGeodatabase = sNomGeodatabase.ToLower.Replace("database connections", Environment.GetEnvironmentVariable("APPDATA") & "\ESRI\Desktop10.3\ArcCatalog")

                'V�rifier si la Geodatabase est SDE
                If sNomGeodatabase.Contains(".sde") Then
                    'D�finir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.SdeWorkspaceFactory")

                    'Si la Geodatabse est une File Geodatabase
                ElseIf sNomGeodatabase.Contains(".gdb") Then
                    'D�finir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.FileGDBWorkspaceFactory")

                    'Si la Geodatabse est une personnelle Geodatabase
                ElseIf sNomGeodatabase.Contains(".mdb") Then
                    'D�finir le type de workspace : SDE
                    pFactoryType = Type.GetTypeFromProgID("esriDataSourcesGDB.AccessWorkspaceFactory")

                    'Sinon
                Else
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Le nom de la G�odatabase ne correspond pas � une Geodatabase !")
                End If

                'Interface pour ouvrir le Workspace
                pWorkspaceFactory = CType(Activator.CreateInstance(pFactoryType), IWorkspaceFactory)

                Try
                    'Ouvrir le workspace de la G�odatabase
                    DefinirGeodatabase = pWorkspaceFactory.OpenFromFile(sNomGeodatabase, 0)
                Catch ex As Exception
                    'Retourner l'erreur
                    Err.Raise(-1, , "ERREUR : Incapable d'ouvrir la G�odatabase : " & sNomGeodatabase)
                End Try
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la m�moire
            pFactoryType = Nothing
            pWorkspaceFactory = Nothing
        End Try
    End Function

    '''<summary>
    '''Routine qui permet de valider et d�finir les param�tres du programme.
    '''</summary>
    '''
    Sub ValiderParametres()
        'D�claration des variables de travail
        Dim args() As String = System.Environment.GetCommandLineArgs()  'Contient les param�tres de la ligne de commandes

        Try
            'Valider le param�tre de la Geodatabase des classes � valider.
            Call ValiderParametreClasseSpatialeEntree(args)

            'Valider le param�tre de la table contenant les contraintes d'int�grit�.
            Call ValiderParametreClasseSpatialeSortie(args)

            'Valider le param�tre du fichier journal dans lequel l'information sur l'ex�cution du traitement sera �crite.
            Call ValiderParametreFichierJournal(args)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la m�moire
            args = Nothing
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre du nom de la Geodatabase des classes � valider.
    '''</summary>
    '''
    Sub ValiderParametreClasseSpatialeEntree(ByVal args() As String)
        Try
            'V�rifier si le param�tre de la classe spatiale d'entr�e est pr�sent.
            If args.Length - 1 > 0 Then
                'D�finir le nom de la classe spatiale d'entr�e
                m_NomClasseSpatialeEntree = args(1)

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreClasseSpatialeEntree", "ERREUR : Le param�tre de la classe spatiale d'entr�e est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre de la table des contraintes d'int�grit�.
    '''</summary>
    '''
    Sub ValiderParametreClasseSpatialeSortie(ByVal args() As String)
        Try
            'V�rifier si le param�tre de la classe spatiale de sortie est pr�sent.
            If args.Length - 1 > 1 Then
                'D�finir le nom de la classe spatiale de sortie
                m_NomClasseSpatialeSortie = args(2)

            Else
                'Retourner l'erreur
                Err.Raise(-1, "ValiderParametreClasseSpatialeSortie", "ERREUR : Le param�tre de la classe spatiale de sortie est absent !")
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de valider le param�tre du fichier journal dans lequel l'information sur l'ex�cution du traitement sera �crite.
    '''</summary>
    '''
    Sub ValiderParametreFichierJournal(ByVal args() As String)
        Try
            'Valider le param�tre du r�pertoire dans lequel les erreurs seront �crites
            If args.Length - 1 > 2 Then
                'V�rifier si le param�tre contient le nom du fichier journal
                If args(3) <> "#" Then
                    'D�finir le nom du fichier journal
                    m_NomFichierJournal = args(3)
                End If
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'�crire le message d'ex�cution dans  un fichier journal et/ou dans la console.
    '''</summary>
    ''' 
    '''<param name="sMessage"> Message � �crire dans un fichier journal et/ou dans la console.</param>
    '''
    Private Sub EcrireMessage(ByVal sMessage As String)
        Try
            'V�rifier si le nom du fichier journal est pr�sent
            If m_NomFichierJournal.Length > 0 Then
                '�crire le message dans le RichTextBox
                File.AppendAllText(m_NomFichierJournal, sMessage & vbCrLf)
            End If

            '�crire dans la console
            Console.WriteLine(sMessage)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'�crire les statistiques d'utilisation d'un usager.
    ''' 
    '''<param name="sCommande"> Commande � �crire dans le fichier de statistique d'utilisation.</param>
    '''<param name="sNomRepertoire"> Nom du r�pertoire dans lequel le fichier de statistique est pr�sent.</param>
    ''' 
    '''</summary>
    '''
    Private Sub EcrireStatistiqueUtilisation(ByVal sCommande As String, Optional ByVal sNomRepertoire As String = "S:\Developpement\geo\")
        'D�clarer les variables de travail
        Dim oStreamWriter As StreamWriter = Nothing     'Objet utilis� pour �crire dans un fichier text.
        Dim sNomFichier As String = ""                  'Nom complet du fichier de statistique d'utilisation.
        Dim sNomUsager As String = ""                   'Nom de l'usager.

        Try
            'D�finir le nom de l'usager
            sNomUsager = Environment.GetEnvironmentVariable("USERNAME")

            'D�finir le nom complet du fichier
            sNomFichier = sNomRepertoire & sNomUsager & ".txt"

            'V�rifier si le fichier existe
            If File.Exists(sNomFichier) Then
                'D�finir l'objet pour �crire � la fin du fichier
                oStreamWriter = File.AppendText(sNomFichier)

                'Si le fichier n'existe pas
            Else
                'D�finir l'objet pour �crire dans un nouveau fichier cr��
                oStreamWriter = File.CreateText(sNomFichier)

                '�crire l'ent�te du fichier
                oStreamWriter.WriteLine("Date, 	 Env, 	 Usager, 	 UsagerBD, 	 UsagerSIB, 	 Outil")
            End If

            '�crire la commande utilis�e
            oStreamWriter.WriteLine(DateTime.Now.ToString & "," & vbTab & System.IO.Path.GetFileName(System.Environment.GetCommandLineArgs()(0)) & "," & vbTab & sNomUsager & "," & vbTab & "NONE," & vbTab & "NONE," & vbTab & sCommande)

            'Fermer le fichier
            oStreamWriter.Close()

        Catch ex As Exception
            'Retourner l'erreur
            'Throw
        Finally
            'Vider la m�moire
            oStreamWriter = Nothing
            sNomFichier = Nothing
            sNomUsager = Nothing
        End Try
    End Sub
End Module
