Imports ESRI.ArcGIS.Carto
Imports ESRI.ArcGIS.ArcMapUI
Imports ESRI.ArcGIS.Framework
Imports ESRI.ArcGIS.Geodatabase
Imports ESRI.ArcGIS.Geometry
Imports System.Windows.Forms
Imports ESRI.ArcGIS.esriSystem
Imports ESRI.ArcGIS.Display
Imports ESRI.ArcGIS.EditorExt
Imports ESRI.ArcGIS.Editor
Imports ESRI.ArcGIS.DataSourcesRaster
Imports System.Data.OleDb

'**
'Nom de la composante : modBarreToponymie.vb 
'
'''<summary>
''' Librairies de routines contenant toutes les variables, routines et fonctions globales.
'''</summary>
'''
'''<remarks>
''' Auteur : Michel Pothier
''' Date : 24 Novembre 2016
'''</remarks>
''' 
Module modBarreToponymie
    'Liste des variables publiques utilisées
    ''' <summary>Interface utilisé pour arrêter un traitement en progression.</summary>
    Public m_TrackCancel As ITrackCancel = Nothing
    ''' <summary>Interface ESRI contenant l'application ArcMap.</summary>
    Public m_Application As IApplication = Nothing
    ''' <summary>Interface ESRI contenant le document ArcMap.</summary>
    Public m_MxDocument As IMxDocument = Nothing
    ''' <summary>Interface ESRI contenant le FeatureLayer de toponymie de la BDG.</summary>
    Public m_FeatureLayerBDG As IFeatureLayer = Nothing

    ''' <summary>Nom de la Géodatabase contenant les classes d'erreurs.</summary>
    Public m_NomGeodatabaseErreur As String = "C:\Toponymie\CorrectionCTI_Label.gdb"
    ''' <summary>Nom de la classe d'erreurs de base.</summary>
    Public m_NomClasseErreur As String = "ERREUR_TOPONYMY_0"
    '''<summary> Interface ESRI contenant les FeatureClass à valider.</summary>
    Public m_GeodatabaseErreur As IWorkspace = Nothing
    ''' <summary>Interface ESRI contenant le FeatureLayer d'erreur de toponymie.</summary>
    Public m_FeatureLayerErreur As IFeatureLayer = Nothing
    '''<summary>Interface ESRI contenant les erreurs.</summary>
    Public m_FeatureClassErreur As IFeatureClass = Nothing
    '''<summary>Interface ESRI utilisé pour ajouter des erreurs dans la classe d'erreurs.</summary>
    Public m_FeatureCursorErreur As IFeatureCursor = Nothing

    '''<summary>Object contenant la liste des Snrc BDG en production.</summary>
    Public m_ListeSnrcProduction As Dictionary(Of String, String)

    ' ''' <summary>Nom de la table d'information des toponymes BDG.</summary>
    'Public m_NomTableInfoToponymeBDG As String = "BDG_DBA.GES_TOPONYMIC_INFO"
    ' ''' <summary>Table d'information des toponymes BDG.</summary>
    'Public m_TableInfoToponymeBDG As ITable = Nothing
    '''<summary>Object contenant la liste des noms de toponyme BDG basé sur le NAMEID.</summary>
    Public m_ListeNomToponymeBDG As Dictionary(Of String, ToponymeBDG) = Nothing
    ''' <summary>Table d'information des toponymes de la BDG.</summary>
    Public m_TableToponymeBDG As IStandaloneTable = Nothing

    ' ''' <summary>Nom de la géodatabase de la table de toponymie officiel.</summary>
    'Public m_NomGeodatabaseToponymieOfficiel As String = "Database Connections\TOPONYMY_PRO.sde"
    ' ''' <summary>Géodatabase de la table de toponymie officiel.</summary>
    'Public m_GeodatabaseToponymieOfficiel As IWorkspace = Nothing
    ' ''' <summary>Nom de la table d'information des toponymes officiels.</summary>
    'Public m_NomTableInfoToponymeOfficiel As String = "TOPONYMY_DBA.TOPONYM_6"
    ' ''' <summary>Table d'information des toponymes officiels.</summary>
    'Public m_TableToponymieOfficiel As ITable = Nothing
    '''<summary>Object contenant la liste des noms des toponymes officiels basé sur les identifiants de nom .</summary>
    Public m_ListeNomToponymeId As Dictionary(Of String, String) = Nothing
    '''<summary>Object contenant la liste des noms des toponymes officiels basé sur les noms.</summary>
    Public m_ListeNomToponymeOfficiel As SortedDictionary(Of String, ISet) = Nothing
    '''<summary>Object contenant la liste des noms des toponymes abrogés.</summary>
    Public m_ListeNomToponymeAbroge As SortedDictionary(Of String, ISet) = Nothing
    ''' <summary>Table d'information des toponymes de la CGNDB.</summary>
    Public m_TableToponymeCGNDB As IStandaloneTable = Nothing

    ''' <summary>ComboBox utilisé pour gérer les valeurs des paramètres de l'action à effectuer.</summary>
    Public m_cboParametres As cboParametres = Nothing
    ''' <summary>ComboBox utilisé pour définir la classe des toponymes ponctuels.</summary>
    Public m_cboFeatureLayerBDG As cboFeatureLayerBDG = Nothing
    ''' <summary>ComboBox utilisé pour définir la classe d'erreurs.</summary>
    Public m_cboFeatureLayerErr As cboFeatureLayerErr = Nothing
    ''' <summary>ComboBox utilisé pour définir la table d'information des toponymes BDG.</summary>
    Public m_cboTableBDG As cboTableBDG = Nothing
    ''' <summary>ComboBox utilisé pour définir la table d'information des toponymes CGNDB.</summary>
    Public m_cboTableCGNDB As cboTableCGNDB = Nothing

    ''' <summary>Contient la valeur de la tolérance de précision par défaut.</summary>
    Public m_Precision As Double = 5.0
    ''' <summary>Contient les valeurs des paramètres de l'action à effectuer.</summary>
    Public m_Parametres As String = m_Precision.ToString("0.0#######")
    ''' <summary>Contient l'action à effectuer.</summary>
    Public m_Action As String = "1:Unnecessary/Inutile"

    ''' <summary>Contient le nombre d'éléments traités.</summary>
    Public m_NbElements As Integer = 0
    ''' <summary>Contient le nombre d'erreurs trouvées.</summary>
    Public m_NbErreurs As Integer = 0
    ''' <summary>Contient le nombre de corrections effectuées.</summary>
    Public m_NbCorrections As Integer = 0

    ''' <summary>Objet qui permet la gestion des FeatureLayer.</summary>
    Public m_MapLayer As clsGererMapLayer = Nothing

    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un document est ouvert.</summary>
    Public m_DocumentEventsOpenDocument As IDocumentEvents_OpenDocumentEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un nouveau document est ouvert.</summary>
    Public m_DocumentEventsNewDocument As IDocumentEvents_NewDocumentEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsque qu'un document est fermé.</summary>
    Public m_DocumentEventsCloseDocument As IDocumentEvents_CloseDocumentEventHandler
    ''''<summary>Interface ESRI qui permet de gérer l'événement lorsqu'un nouveau document est activé.</summary>
    Public m_ActiveViewEventsContentsChanged As IActiveViewEvents_ContentsChangedEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsqu'un nouvel item est ajouté à la Map active.</summary>
    Public m_ActiveViewEventsItemAdded As IActiveViewEvents_ItemAddedEventHandler
    '''<summary>Interface ESRI qui permet de gérer l'événement lorsqu'un nouvel item est retiré de la Map active</summary>
    Public m_ActiveViewEventsItemDeleted As IActiveViewEvents_ItemDeletedEventHandler

    ''' <summary>Structure contenant l'information d'un toponyme officiel basé sur le nom.</summary>
    Public Structure Toponyme
        Public NameId As String
        Public Snrc As String
    End Structure

    ''' <summary>Structure contenant l'information d'un toponyme BDG basé sur l'identifiant du nom.</summary>
    Public Structure ToponymeBDG
        Public Name As String
        Public OID As Integer
    End Structure

    '**
    'Nom de la composante : CancelException.vb
    '
    '''<summary>
    ''' Classe contenant une exception permettant d'annuler l'exécution d'un traitement.
    '''</summary>
    '''
    '''<remarks>
    ''' Auteur : Michel Pothier
    ''' Date : 24 novembre 2016
    '''</remarks>
    ''' 
    Public Class CancelException
        Inherits Exception

        Public Sub New()
        End Sub

        Public Sub New(message As String)
            MyBase.New(message)
        End Sub

        Public Sub New(message As String, inner As Exception)
            MyBase.New(message, inner)
        End Sub
    End Class

#Region "Routine et fonction : Corriger les erreurs de toponymie"
    '''<summary>
    ''' Routine qui permet de corriger les erreurs de toponymie selon la décision présente pour chaque erreur de toponyme visitée.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''
    Public Sub CorrigerErreursToponymie(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pSchemaLock As ISchemaLock = Nothing        'Interface pour enlever le lock sur la classe d'erreur.
        Dim pFeatureSel As IFeatureSelection = Nothing  'Interface utilisé pour sélectionner les éléments.
        Dim pCursor As ICursor = Nothing                'Interface utilisé pour lire les éléments.
        Dim pFeatureCursor As IFeatureCursor = Nothing  'Interface utilisé pour lire les éléments.
        Dim pFeatureErr As IFeature = Nothing           'Interface contenant l'élément de l'erreur.
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface pour effectuer une requête attributive.
        Dim sRequete As String = Nothing                'Contient la requête pour trouver les toponymes inconnus.
        Dim iDecision As Integer = 0                    'Contient la décision de l'erreur de toponymie.

        Try
            'Interface pour sélectionner les éléments d'erreurs
            pFeatureSel = CType(m_FeatureLayerErreur, IFeatureSelection)

            'Créer une requête vide
            pQueryFilter = New QueryFilter
            'Définir la requête attributive afin de traiter seulement les erreurs visitées.
            pQueryFilter.WhereClause = "STATUS = 1"

            'Afficher le message de traitement de la relation spatiale
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Sélection des éléments d'erreurs de toponyme (" & m_FeatureLayerErreur.Name & ") ..."
            'Vérifier si une sélection est déjà présente
            If pFeatureSel.SelectionSet.Count = 0 Then
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultNew, False)
            Else
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAnd, False)
            End If

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0
            'Initialiser le nombre de corrections
            m_NbCorrections = 0

            'Vérifier si des éléments ont été trouvé
            If pFeatureSel.SelectionSet.Count > 0 Then
                'Créer la liste des noms de toponyme CTI
                If m_ListeNomToponymeBDG Is Nothing Then Call CreerListeNomToponymeBDG(pTrackCancel, "GEONAMEDB='CTI_LABEL'")

                'Créer la liste des noms de toponyme CGNDB
                If m_ListeNomToponymeOfficiel Is Nothing Then Call CreerListeNomToponymeOfficiel(pTrackCancel)

                'Créer la liste des Snrc en production
                If m_ListeSnrcProduction Is Nothing Then Call CreerListeSnrcProduction(pTrackCancel)

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Corriger les erreurs de toponymie (" & m_FeatureLayerErreur.Name & ") ..."
                'Afficher la barre de progression
                InitBarreProgression(0, m_NbElements, pTrackCancel)

                'Interfaces pour extraire les éléments sélectionnés
                pFeatureSel.SelectionSet.Search(Nothing, False, pCursor)
                pFeatureCursor = CType(pCursor, IFeatureCursor)

                'Extraire le premier élément d'erreur
                pFeatureErr = pFeatureCursor.NextFeature()

                'Traiter tous les éléments du FeatureLayer d'erreurs
                Do Until pFeatureErr Is Nothing
                    'Extraire la décision
                    iDecision = CInt(pFeatureErr.Value(9))

                    'Vérifier si la décision de l'erreur est 1:Conserver
                    If iDecision = 1 Then
                        'Conserver l'élément sans changer la géométrie
                        Call ConserverToponyme(pFeatureErr)

                        'Si la décision de l'erreur est 2:Détruire
                    ElseIf iDecision = 2 Then
                        'Détruire l'élément
                        Call DetruireToponyme(pFeatureErr)

                        'Si la décision de l'erreur est 3:Déplacer
                    ElseIf iDecision = 3 Then
                        'Conserver l'élément et changer la géométrie
                        Call DeplacerToponyme(pFeatureErr)
                    End If

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")

                    'Extraire le prochain élément d'erreur à traiter
                    pFeatureErr = pFeatureCursor.NextFeature()
                Loop

                'Vider la sélection des éléments BDG
                pFeatureSel.Clear()

                'Release the update cursor to remove the lock on the input data.
                System.Runtime.InteropServices.Marshal.ReleaseComObject(pFeatureCursor)
            End If

            'Interface pour enlever le lock sur la classe d'erreurs
            pSchemaLock = CType(m_FeatureLayerErreur.FeatureClass, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pSchemaLock = Nothing
            pFeatureSel = Nothing
            pCursor = Nothing
            pFeatureCursor = Nothing
            pFeatureErr = Nothing
            pQueryFilter = Nothing
            sRequete = Nothing
            iDecision = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de corriger la décision de conserver le Toponyme qui consiste à :
    ''' -Remplacer le NAMEID du CTI_LABEL par celui de la CGNDB existant.
    ''' -Remplacer la valeur du GEONAMEDB de CTI_LABEL par CGNDB.
    ''' -Mettre 1:actif la valeur du ACTIVE_TOPONYM.
    ''' -Détruire l'enregistrement du CTI_LABEL dans GES_TOPONYMIC_INFO.
    ''' -Changer le STATUS de l'élément d'erreur pour indiquer comment il a été corrigé.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pFeatureErr"> Interface contenant l'élément d'erreur.</param>
    '''
    Private Sub ConserverToponyme(ByRef pFeatureErr As IFeature)
        'Déclarer les variables de travail
        Dim pFeatureBDG As IFeature = Nothing           'Interface contenant l'élément du toponyme BDG à corriger.
        Dim pRow As IRow = Nothing                      'Interface contenant l'élément d'information du toponyme.
        Dim pToponymeBDG As ToponymeBDG = Nothing       'Contient l'information du toponyme BDG.
        Dim sId_BDG As String = Nothing                 'Identifiant du toponyme de la BDG.
        Dim sId_CGNDB As String = Nothing               'Identifiant du toponyme de la CGNDB.
        Dim sNom_CGNDB As String = Nothing              'Nom du toponyme de la CGNDB.
        Dim sSnrc As String = Nothing                   'Contient le numéro Snrc.
        Dim iOid As Integer = Nothing                   'Contient l'identifiant.
        Dim iPosId As Integer = -1      'Contient la position de l'attribut de l'identifiant de toponyme.
        Dim iPosGeo As Integer = -1     'Contient la position de l'attribut de la provenance du toponyme.
        Dim iPosAct As Integer = -1     'Contient la position de l'attribut pour indiquer si le toponyme est actif.

        Try
            'Définir la position des attributs dans la table
            iPosId = m_FeatureLayerBDG.FeatureClass.FindField("NAMEID")
            iPosGeo = m_FeatureLayerBDG.FeatureClass.FindField("GEONAMEDB")
            iPosAct = m_FeatureLayerBDG.FeatureClass.FindField("ACTIVE_TOPONYM")

            'Extraire l'identifiant du toponyme de la CGNDB
            sId_CGNDB = pFeatureErr.Value(7).ToString

            'Extraire le nom du toponyme de la CGNDB
            sNom_CGNDB = pFeatureErr.Value(8).ToString

            'Vérifier si l'identifiant et le nom du toponyme de la CGNDB sont valides
            If IdNomCGNDB(sId_CGNDB, sNom_CGNDB) Then
                'Extraire le Snrc
                sSnrc = pFeatureErr.Value(3).ToString

                'Extraire l'identifiant du toponyme de la BDG
                sId_BDG = pFeatureErr.Value(4).ToString

                'Vérifier si le toponyme BDG est présent
                If m_ListeNomToponymeBDG.ContainsKey(sId_BDG) Then
                    'Extraire l'information du toponyme de la BDG
                    pToponymeBDG = m_ListeNomToponymeBDG.Item(sId_BDG)

                    Try
                        'Extraire le OID
                        iOid = CInt(pFeatureErr.Value(5))
                        'Extraire l'élément d'information du toponyme BDG
                        pRow = m_TableToponymeBDG.Table.GetRow(pToponymeBDG.OID)
                        'Extraire l'élément du toponyme BDG
                        pFeatureBDG = m_FeatureLayerBDG.FeatureClass.GetFeature(iOid)

                        '------------------------------------------------
                        'Changer le NAMEID du toponyme BDG
                        pFeatureBDG.Value(iPosId) = sId_CGNDB
                        'Changer le GEONAMEDB du toponyme BDG
                        pFeatureBDG.Value(iPosGeo) = "CGNDB"
                        'Changer le ACTIVE_TOPONYM du toponyme
                        pFeatureBDG.Value(iPosAct) = 1

                        '------------------------------------------------
                        If m_ListeSnrcProduction.ContainsKey(sSnrc) Then
                            'Mettre le STATUS=3:Corrigé-Production pour l'erreur de toponymie
                            pFeatureErr.Value(12) = 3
                            'Si le SNRC de l'élément du toponyme BDG n'est pas en production
                        Else
                            'Mettre le STATUS=2:Corrigé pour l'erreur de toponymie
                            pFeatureErr.Value(12) = 2
                        End If

                        '------------------------------------------------
                        'Sauver les modifications effectuées
                        pFeatureErr.Store()
                        pFeatureBDG.Store()

                        '------------------------------------------------
                        'Détruire l'enregistrement dans la table d'information des toponymes BDG
                        pRow.Delete()

                        'Compter le nombre de corrections
                        m_NbCorrections = m_NbCorrections + 1

                    Catch ex As Exception
                        'Compter le nombre d'erreurs
                        m_NbErreurs = m_NbErreurs + 1
                        'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                        pFeatureErr.Value(12) = 4
                        'Mettre le message d'erreur
                        pFeatureErr.Value(10) = "ERROR: invalid OID / ERREUR : OID invalide : " & m_TableToponymeBDG.Name & "=" & pToponymeBDG.OID.ToString & " / " & m_FeatureLayerBDG.Name & "=" & iOid.ToString
                        'Sauver les modifications
                        pFeatureErr.Store()
                    End Try

                    'Si le NAMEID de la BDG est invalide
                Else
                    'Compter le nombre d'erreurs
                    m_NbErreurs = m_NbErreurs + 1
                    'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                    pFeatureErr.Value(12) = 4
                    'Mettre le message d'erreur
                    pFeatureErr.Value(10) = "ERROR: The identifier and name of the GDB toponym is invalid / ERREUR : L'identifiant et le nom du toponyme de la BDG est invalide!, Id_BDG=" & sId_BDG
                    'Sauver les modifications
                    pFeatureErr.Store()
                End If

                'Si le NAMEID de la CGNDB est invalide
            Else
                'Compter le nombre d'erreurs
                m_NbErreurs = m_NbErreurs + 1
                'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                pFeatureErr.Value(12) = 4
                'Mettre le message d'erreur
                pFeatureErr.Value(10) = "ERROR: The identifier and name of the CGNDB toponym is invalid / ERREUR : L'identifiant et le nom du toponyme de la CGNDB est invalide!, Id_CGNDB=" & sId_CGNDB & ", NOM_CGNDB=" & sNom_CGNDB
                'Sauver les modifications
                pFeatureErr.Store()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureBDG = Nothing
            pRow = Nothing
            pToponymeBDG = Nothing
            sId_BDG = Nothing
            sId_CGNDB = Nothing
            sNom_CGNDB = Nothing
            sSnrc = Nothing
            iOid = Nothing
            iPosId = Nothing
            iPosGeo = Nothing
            iPosAct = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de corriger la décision de déplacer le Toponyme qui consiste à :
    ''' -Remplacer le NAMEID du CTI_LABEL par celui de la CGNDB existant.
    ''' -Remplacer la valeur du GEONAMEDB de CTI_LABEL par CGNDB.
    ''' -Mettre 1:actif la valeur du ACTIVE_TOPONYM.
    ''' -Changer la géométrie du toponyme BDG.
    ''' -Détruire l'enregistrement du CTI_LABEL dans GES_TOPONYMIC_INFO.
    ''' -Changer le STATUS de l'élément d'erreur pour indiquer comment il a été corrigé.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pFeatureErr"> Interface contenant l'élément d'erreur.</param>
    '''
    Private Sub DeplacerToponyme(ByRef pFeatureErr As IFeature)
        'Déclarer les variables de travail
        Dim pFeatureBDG As IFeature = Nothing           'Interface contenant l'élément du toponyme BDG à corriger.
        Dim pRow As IRow = Nothing                      'Interface contenant l'élément d'information du toponyme.
        Dim pToponymeBDG As ToponymeBDG = Nothing       'Contient l'information du toponyme BDG.
        Dim sId_BDG As String = Nothing                 'Identifiant du toponyme de la BDG.
        Dim sId_CGNDB As String = Nothing               'Identifiant du toponyme de la CGNDB.
        Dim sNom_CGNDB As String = Nothing              'Nom du toponyme de la CGNDB.
        Dim sSnrc As String = Nothing                   'Contient le numéro Snrc.
        Dim iOid As Integer = Nothing                   'Contient l'identifiant.
        Dim iPosId As Integer = -1      'Contient la position de l'attribut de l'identifiant de toponyme.
        Dim iPosGeo As Integer = -1     'Contient la position de l'attribut de la provenance du toponyme.
        Dim iPosAct As Integer = -1     'Contient la position de l'attribut pour indiquer si le toponyme est actif.
        Dim iPosSnrc As Integer = -1    'Contient la position de l'attribut du Snrc de toponyme.

        Try
            'Définir la position des attributs dans la table
            iPosId = m_FeatureLayerBDG.FeatureClass.FindField("NAMEID")
            iPosGeo = m_FeatureLayerBDG.FeatureClass.FindField("GEONAMEDB")
            iPosAct = m_FeatureLayerBDG.FeatureClass.FindField("ACTIVE_TOPONYM")
            iPosSnrc = m_FeatureLayerBDG.FeatureClass.FindField("DATASET_NAME")

            'Extraire l'identifiant du toponyme de la CGNDB
            sId_CGNDB = pFeatureErr.Value(7).ToString

            'Extraire le nom du toponyme de la CGNDB
            sNom_CGNDB = pFeatureErr.Value(8).ToString

            'Vérifier si l'identifiant et le nom du toponyme de la CGNDB sont valides
            If IdNomCGNDB(sId_CGNDB, sNom_CGNDB) Then
                'Extraire l'identifiant du toponyme de la BDG
                sId_BDG = pFeatureErr.Value(4).ToString

                'Vérifier si le toponyme BDG est présent
                If m_ListeNomToponymeBDG.ContainsKey(sId_BDG) Then
                    'Extraire l'information du toponyme de la BDG
                    pToponymeBDG = m_ListeNomToponymeBDG.Item(sId_BDG)

                    'Extraire le Snrc
                    sSnrc = pFeatureErr.Value(3).ToString

                    Try
                        'Extraire le OID
                        iOid = CInt(pFeatureErr.Value(5))
                        'Extraire l'élément d'information du toponyme BDG
                        pRow = m_TableToponymeBDG.Table.GetRow(pToponymeBDG.OID)
                        'Extraire l'élément du toponyme BDG
                        pFeatureBDG = m_FeatureLayerBDG.FeatureClass.GetFeature(iOid)

                        'Vérifier si le SNRC est le même avant de déplacer
                        If pFeatureBDG.Value(iPosSnrc).ToString = sSnrc Then
                            '------------------------------------------------
                            'Changer le NAMEID du toponyme BDG
                            pFeatureBDG.Value(iPosId) = sId_CGNDB
                            'Changer le GEONAMEDB du toponyme BDG
                            pFeatureBDG.Value(iPosGeo) = "CGNDB"
                            'Changer le ACTIVE_TOPONYM du toponyme
                            pFeatureBDG.Value(iPosAct) = 1
                            'Changer la géométrie du toponyme par celui de l'erreur
                            pFeatureBDG.Shape = pFeatureErr.ShapeCopy

                            '------------------------------------------------
                            If m_ListeSnrcProduction.ContainsKey(sSnrc) Then
                                'Mettre le STATUS=3:Corrigé-Production pour l'erreur de toponymie
                                pFeatureErr.Value(12) = 3
                                'Si le SNRC de l'élément du toponyme BDG n'est pas en production
                            Else
                                'Mettre le STATUS=2:Corrigé pour l'erreur de toponymie
                                pFeatureErr.Value(12) = 2
                            End If

                            '------------------------------------------------
                            'Sauver les modifications effectuées
                            pFeatureErr.Store()
                            pFeatureBDG.Store()

                            '------------------------------------------------
                            'Détruire l'enregistrement dans la table d'information des toponymes BDG
                            pRow.Delete()

                            'Compter le nombre de corrections
                            m_NbCorrections = m_NbCorrections + 1

                            'Si le SNRC est différent
                        Else
                            'Compter le nombre d'erreurs
                            m_NbErreurs = m_NbErreurs + 1
                            'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                            pFeatureErr.Value(12) = 4
                            'Mettre le message d'erreur
                            pFeatureErr.Value(10) = "ERROR: The NTS error is different from the original / ERREUR : Le SNRC de l'erreur est différent de l'originale : " & pFeatureBDG.Value(iPosSnrc).ToString & "<>" & sSnrc
                        End If

                    Catch ex As Exception
                        'Compter le nombre d'erreurs
                        m_NbErreurs = m_NbErreurs + 1
                        'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                        pFeatureErr.Value(12) = 4
                        'Mettre le message d'erreur
                        pFeatureErr.Value(10) = "ERROR: invalid OID / ERREUR : OID invalide : " & m_TableToponymeBDG.Name & "=" & pToponymeBDG.OID.ToString & " / " & m_FeatureLayerBDG.Name & "=" & iOid.ToString
                        'Sauver les modifications
                        pFeatureErr.Store()
                    End Try

                'Si le NAMEID de la BDG est invalide
                Else
                    'Compter le nombre d'erreurs
                    m_NbErreurs = m_NbErreurs + 1
                    'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                    pFeatureErr.Value(12) = 4
                    'Mettre le message d'erreur
                    pFeatureErr.Value(10) = "ERROR: The identifier and name of the GDB toponym is invalid / ERREUR : L'identifiant et le nom du toponyme de la BDG est invalide!, Id_BDG=" & sId_BDG
                    'Sauver les modifications
                    pFeatureErr.Store()
                End If

            'Si le NAMEID de la CGNDB est invalide
            Else
                'Compter le nombre d'erreurs
                m_NbErreurs = m_NbErreurs + 1
                'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                pFeatureErr.Value(12) = 4
                'Mettre le message d'erreur
                pFeatureErr.Value(10) = "ERROR: The identifier and name of the CGNDB toponym is invalid / ERREUR : L'identifiant et le nom du toponyme de la CGNDB est invalide!, Id_CGNDB=" & sId_CGNDB & ", NOM_CGNDB=" & sNom_CGNDB
                'Sauver les modifications
                pFeatureErr.Store()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureBDG = Nothing
            pRow = Nothing
            pToponymeBDG = Nothing
            sId_BDG = Nothing
            sId_CGNDB = Nothing
            sNom_CGNDB = Nothing
            sSnrc = Nothing
            iOid = Nothing
            iPosId = Nothing
            iPosGeo = Nothing
            iPosAct = Nothing
            iPosSnrc = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de corriger la décision de détruire le Toponyme qui consiste à :
    ''' -Détruire l'enregistrement du CTI_LABEL dans BDG_NAMED_FEATURE_0.
    ''' -Détruire l'enregistrement du CTI_LABEL dans GES_TOPONYMIC_INFO.
    ''' -Changer le STATUS de l'élément d'erreur pour indiquer comment il a été corrigé.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pFeatureErr"> Interface contenant l'élément d'erreur.</param>
    '''
    Private Sub DetruireToponyme(ByRef pFeatureErr As IFeature)
        'Déclarer les variables de travail
        Dim pFeatureBDG As IFeature = Nothing           'Interface contenant l'élément du toponyme BDG à corriger.
        Dim pRow As IRow = Nothing                      'Interface contenant l'élément d'information du toponyme.
        Dim pToponymeBDG As ToponymeBDG = Nothing       'Contient l'information du toponyme BDG.
        Dim sId_BDG As String = Nothing                 'Identifiant du toponyme de la BDG.
        Dim sSnrc As String = Nothing                   'Contient le numéro Snrc.
        Dim iOid As Integer = Nothing                   'Contient l'identifiant.

        Try
            'Extraire l'identifiant du toponyme de la BDG
            sId_BDG = pFeatureErr.Value(4).ToString

            'Vérifier si le toponyme BDG est présent
            If m_ListeNomToponymeBDG.ContainsKey(sId_BDG) Then
                'Extraire l'information du toponyme de la BDG
                pToponymeBDG = m_ListeNomToponymeBDG.Item(sId_BDG)

                Try
                    'Extraire le OID du Toponyme BDG
                    iOid = CInt(pFeatureErr.Value(5))
                    'Extraire l'élément d'information du toponyme BDG
                    pRow = m_TableToponymeBDG.Table.GetRow(pToponymeBDG.OID)
                    'Extraire l'élément du toponyme BDG
                    pFeatureBDG = m_FeatureLayerBDG.FeatureClass.GetFeature(iOid)

                    '------------------------------------------------
                    'Détruire l'élément du toponyme BDG
                    pFeatureBDG.Delete()

                    '------------------------------------------------
                    'Extraire le Snrc
                    sSnrc = pFeatureErr.Value(3).ToString
                    'Vérifier si le SNRC de l'élément du toponyme BDG est en production
                    If m_ListeSnrcProduction.ContainsKey(sSnrc) Then
                        'Mettre le STATUS=3:Corrigé-Production pour l'erreur de toponymie
                        pFeatureErr.Value(12) = 3
                        'Si le SNRC de l'élément du toponyme BDG n'est pas en production
                    Else
                        'Mettre le STATUS=2:Corrigé pour l'erreur de toponymie
                        pFeatureErr.Value(12) = 2
                    End If

                    '------------------------------------------------
                    'Sauver les modifications effectuées
                    pFeatureErr.Store()

                    '------------------------------------------------
                    'Détruire l'information du toponyme BDG
                    pRow.Delete()

                    'Compter le nombre de corrections
                    m_NbCorrections = m_NbCorrections + 1

                Catch ex As Exception
                    'Compter le nombre d'erreurs
                    m_NbErreurs = m_NbErreurs + 1
                    'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                    pFeatureErr.Value(12) = 4
                    'Mettre le message d'erreur
                    pFeatureErr.Value(10) = "ERROR: invalid OID / ERREUR : OID invalide : " & m_TableToponymeBDG.Name & "=" & pToponymeBDG.OID.ToString & " / " & m_FeatureLayerBDG.Name & "=" & iOid.ToString
                    'Sauver les modifications
                    pFeatureErr.Store()
                End Try

                'Si le NAMEID de la BDG est invalide
            Else
                'Compter le nombre d'erreurs
                m_NbErreurs = m_NbErreurs + 1
                'Mettre le STATUS=4:Erreur pour l'erreur de toponymie
                pFeatureErr.Value(12) = 4
                'Mettre le message d'erreur
                pFeatureErr.Value(10) = "ERROR: The identifier and name of the GDB toponym is invalid / ERREUR : L'identifiant et le nom du toponyme de la BDG est invalide!, Id_BDG=" & sId_BDG
                'Sauver les modifications
                pFeatureErr.Store()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureBDG = Nothing
            pRow = Nothing
            pToponymeBDG = Nothing
            sId_BDG = Nothing
            sSnrc = Nothing
            iOid = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet d'indiquer si l'identifiant et le nom du toponyme de la CGNDB est valide.
    '''</summary>
    ''' 
    '''<param name="sId"> Identifiant du toponyme CGNDG.</param>
    '''<param name="sNom"> Nom du toponyme CGNDG.</param>
    '''
    '''<returns>True si l'identifiant et le nom est valide, false sinon.</returns>
    ''' 
    Private Function IdNomCGNDB(ByVal sId As String, ByVal sNom As String) As Boolean
        'Déclarer les variables de travail
        Dim pSetToponyme As ISet = Nothing          'Contient un ensemble d'information de toponyme.
        Dim pToponyme As Toponyme = Nothing         'Objet contenant le NameId et le SNRC du toponyme.

        'Par défaut, ce n'est pas valide
        IdNomCGNDB = False

        Try
            'Vérifier si le NAMEID et le nom de la CGNDB sont valides
            If m_ListeNomToponymeOfficiel.ContainsKey(sNom) Then
                'Extraire l'information du toponyme
                pSetToponyme = m_ListeNomToponymeOfficiel.Item(sNom)

                'Initialiser la recherche
                pSetToponyme.Reset()

                'Traiter tous les toponymes présents
                For i = 1 To pSetToponyme.Count
                    'Extraire l'information du toponyme
                    pToponyme = CType(pSetToponyme.Next, Toponyme)

                    'Vérifier si l'identifiant du toponyme est valide
                    If pToponyme.NameId = sId Then Return True
                Next
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pSetToponyme = Nothing
            pToponyme = Nothing
        End Try
    End Function
#End Region

#Region "Routine et fonction 1:Unnecessary/Inutile"
    '''<summary>
    ''' Routine qui permet de traiter l'action 1:Unnecessary/Inutile pour les toponymes inconnus.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''
    '''<return>Les éléments qui se superposent seront inscrit dans la table d'erreurs avec le même numéro de lien.</return>
    '''
    Public Sub TraiterToponymeInutile(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pLienNomColl As SortedDictionary(Of String, ISet) = Nothing   'Object contenant les liens des noms de toponyme.
        Dim pFeatureSel As IFeatureSelection = Nothing  'Interface utilisé pour sélectionner les éléments.
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface pour effectuer une requête attributive.
        Dim sRequete As String = Nothing                'Contient la requête pour trouver les toponymes inconnus.

        Try
            'Afficher le message de traitement de la relation spatiale
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Sélection des éléments inutiles (" & m_FeatureLayerBDG.Name & ") ..."
            'Définir la requête pour sélectionner les toponymes inconnus
            sRequete = "GEONAMEDB='CTI_LABEL' AND NAMEID IN "
            sRequete = sRequete & "(SELECT DISTINCT NAMEID  FROM GES_TOPONYMIC_INFO WHERE GEONAMEDB='CTI_LABEL'"
            sRequete = sRequete & " and NAME_EN like '%Route' "
            sRequete = sRequete & " or NAME_EN like '%Byway'"
            sRequete = sRequete & " or NAME_EN like '%Freeway'"
            sRequete = sRequete & " or NAME_EN like '%Way'"
            sRequete = sRequete & " or NAME_EN like '%Highway'"
            sRequete = sRequete & " or NAME_EN like '%Highroad'"
            sRequete = sRequete & " or NAME_EN like '%Trail'"
            sRequete = sRequete & " or NAME_EN like '%Parkway'"
            sRequete = sRequete & " or NAME_EN like '%Road'"
            sRequete = sRequete & " or NAME_EN like '%Bridge'"
            sRequete = sRequete & " or NAME_EN like '%Drive'"
            sRequete = sRequete & " or NAME_FR like 'Route %'"
            sRequete = sRequete & " or NAME_FR like 'Rang %'"
            sRequete = sRequete & " or NAME_FR like 'Autoroute %'"
            sRequete = sRequete & " or NAME_FR like 'Pont %'"
            sRequete = sRequete & " or NAME_FR like 'Sentier %'  "
            sRequete = sRequete & " or NAME_EN like '% Airfield'"
            sRequete = sRequete & " or NAME_EN like '% Airport'"
            sRequete = sRequete & " or NAME_EN like '% Airpark'"
            sRequete = sRequete & " or NAME_EN like '% Seabase'"
            sRequete = sRequete & " or NAME_EN like '% Seaplane'"
            sRequete = sRequete & " or NAME_EN like '% Ferry'"
            sRequete = sRequete & " or NAME_FR like 'Base d''hydravion %'"
            sRequete = sRequete & " or NAME_FR like 'Terrain d''aviation %'"
            sRequete = sRequete & " or NAME_FR like 'Aroport %'"
            sRequete = sRequete & " or NAME_FR like 'Traversier %'"
            sRequete = sRequete & " or NAME_EN like '% Observatory'"
            sRequete = sRequete & " or NAME_EN like '% University'"
            sRequete = sRequete & " or NAME_EN like '% College'"
            sRequete = sRequete & " or NAME_EN like '% Experimental Farm' "
            sRequete = sRequete & " or NAME_FR like 'Collge %'"
            sRequete = sRequete & " or NAME_FR like 'Campus %'"
            sRequete = sRequete & " or NAME_FR like 'Ferme exprimentale %')"

            'Créer une requête vide
            pQueryFilter = New QueryFilter
            'Définir la requête attributive
            pQueryFilter.WhereClause = sRequete

            'Interface pour sélectionner les éléments
            pFeatureSel = CType(m_FeatureLayerBDG, IFeatureSelection)
            'Vérifier si une sélection est déjà présente
            If pFeatureSel.SelectionSet.Count = 0 Then
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultNew, False)
            Else
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAnd, False)
            End If

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0

            'Vérifier si des éléments ont été trouvé
            If pFeatureSel.SelectionSet.Count > 0 Then
                'Créer la liste des noms de toponyme CTI
                If m_ListeNomToponymeBDG Is Nothing Then Call CreerListeNomToponymeBDG(pTrackCancel, "GEONAMEDB='CTI_LABEL'")

                'Créer la liste des noms de toponyme CGNDB
                If m_ListeNomToponymeOfficiel Is Nothing Then Call CreerListeNomToponymeOfficiel(pTrackCancel)

                'Créer la nouvelle classe d'erreurs
                Call CreerClasseErreur("Unnecessary_Inutile_0")

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lire les éléments inutiles (" & m_FeatureLayerBDG.Name & ") ..."
                'Lecture des éléments multiples
                Call LireElementMultiple(m_FeatureLayerBDG, pTrackCancel, pLienNomColl)

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Écriture des erreurs trouvées (Unnecessary_Inutile_0) ..."
                'Écriture des erreurs trouvées
                Call EcrireErreursMultiple(m_FeatureLayerBDG, pTrackCancel, pLienNomColl, 1, 0, 0)

                'Vider la sélection des éléments BDG
                pFeatureSel.Clear()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pLienNomColl = Nothing
            pFeatureSel = Nothing
            pQueryFilter = Nothing
            sRequete = Nothing
        End Try
    End Sub
#End Region

#Region "Routine et fonction 2:Superimposed/Superpose"
    '''<summary>
    ''' Routine qui permet de traiter l'action 2:Superimposed/Superpose pour les toponymes superposés.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''
    '''<return>Les éléments qui se superposent seront inscrit dans la table d'erreurs avec le même numéro de lien.</return>
    '''
    Public Sub TraiterToponymeSuperpose(ByRef pTrackCancel As ITrackCancel, ByVal pSpatialRef As ISpatialReference)
        'Déclarer les variables de travail
        Dim pFeatureSel As IFeatureSelection = Nothing  'Interface utilisé pour sélectionner les éléments.
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface pour effectuer une requête attributive.
        Dim sRequete As String = Nothing                'Contient la requête pour trouver les toponymes inconnus.
        Dim pGeomSelColl As IGeometryCollection = Nothing   'Interface contenant les géométries des l'élément à traiter.
        Dim pGeomRelColl As IGeometryCollection = Nothing   'Interface contenant les géométries des éléments en relation.
        Dim pRelOpNxM As IRelationalOperatorNxM = Nothing   'Interface utilisé pour traiter la relation spatiale.
        Dim pRelResult As IRelationResult = Nothing         'Interface contenant le résultat du traitement de la relation spatiale.
        Dim iOidSel(0) As Integer   'Vecteur des OIds des éléments à traiter.
        Dim iOidRel(0) As Integer   'Vecteur des OIds des éléments en relation.

        Try
            'Afficher le message de traitement de la relation spatiale
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Sélection des éléments superposés (" & m_FeatureLayerBDG.Name & ") ..."
            'Définir la requête pour sélectionner les toponymes inconnus
            sRequete = "GEONAMEDB='CTI_LABEL' AND NAMEID NOT IN "
            sRequete = sRequete & "(SELECT DISTINCT NAMEID  FROM GES_TOPONYMIC_INFO WHERE GEONAMEDB='CTI_LABEL'"
            sRequete = sRequete & " and NAME_EN like '%Route' "
            sRequete = sRequete & " or NAME_EN like '%Byway'"
            sRequete = sRequete & " or NAME_EN like '%Freeway'"
            sRequete = sRequete & " or NAME_EN like '%Way'"
            sRequete = sRequete & " or NAME_EN like '%Highway'"
            sRequete = sRequete & " or NAME_EN like '%Highroad'"
            sRequete = sRequete & " or NAME_EN like '%Trail'"
            sRequete = sRequete & " or NAME_EN like '%Parkway'"
            sRequete = sRequete & " or NAME_EN like '%Road'"
            sRequete = sRequete & " or NAME_EN like '%Bridge'"
            sRequete = sRequete & " or NAME_EN like '%Drive'"
            sRequete = sRequete & " or NAME_FR like 'Route %'"
            sRequete = sRequete & " or NAME_FR like 'Rang %'"
            sRequete = sRequete & " or NAME_FR like 'Autoroute %'"
            sRequete = sRequete & " or NAME_FR like 'Pont %'"
            sRequete = sRequete & " or NAME_FR like 'Sentier %'  "
            sRequete = sRequete & " or NAME_EN like '% Airfield'"
            sRequete = sRequete & " or NAME_EN like '% Airport'"
            sRequete = sRequete & " or NAME_EN like '% Airpark'"
            sRequete = sRequete & " or NAME_EN like '% Seabase'"
            sRequete = sRequete & " or NAME_EN like '% Seaplane'"
            sRequete = sRequete & " or NAME_EN like '% Ferry'"
            sRequete = sRequete & " or NAME_FR like 'Base d''hydravion %'"
            sRequete = sRequete & " or NAME_FR like 'Terrain d''aviation %'"
            sRequete = sRequete & " or NAME_FR like 'Aroport %'"
            sRequete = sRequete & " or NAME_FR like 'Traversier %'"
            sRequete = sRequete & " or NAME_EN like '% Observatory'"
            sRequete = sRequete & " or NAME_EN like '% University'"
            sRequete = sRequete & " or NAME_EN like '% College'"
            sRequete = sRequete & " or NAME_EN like '% Experimental Farm' "
            sRequete = sRequete & " or NAME_FR like 'Collge %'"
            sRequete = sRequete & " or NAME_FR like 'Campus %'"
            sRequete = sRequete & " or NAME_FR like 'Ferme exprimentale %')"

            'Créer une requête vide
            pQueryFilter = New QueryFilter
            'Définir la requête attributive
            pQueryFilter.WhereClause = sRequete

            'Interface pour sélectionner les éléments
            pFeatureSel = CType(m_FeatureLayerBDG, IFeatureSelection)
            'Vérifier si une sélection est déjà présente
            If pFeatureSel.SelectionSet.Count = 0 Then
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultNew, False)
            Else
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAnd, False)
            End If

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0

            'Vérifier si des éléments ont été trouvé
            If pFeatureSel.SelectionSet.Count > 0 Then
                'Créer la liste des noms de toponyme BDG
                If m_ListeNomToponymeBDG Is Nothing Then Call CreerListeNomToponymeBDG(pTrackCancel, "GEONAMEDB='CTI_LABEL'")

                'Créer la liste des noms de toponyme CGNDB
                If m_ListeNomToponymeOfficiel Is Nothing Then Call CreerListeNomToponymeOfficiel(pTrackCancel)

                'Créer la nouvelle classe d'erreurs
                Call CreerClasseErreur("Superimposed_Superpose_0")

                'Afficher le message de lecture des éléments
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lecture des éléments (" & m_FeatureLayerBDG.Name & ") ..."
                'Lire les éléments à traiter 
                Call LireGeometrie(m_FeatureLayerBDG, pSpatialRef, pTrackCancel, pGeomSelColl, iOidSel)

                'Définir les géométries en relation
                pGeomRelColl = pGeomSelColl
                'Définir les Oids en relation
                iOidRel = iOidSel

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Traitement de l'action 2:Superimposed/Superpose (" & m_FeatureLayerBDG.Name & ") ..."
                'Interface pour traiter la relation spatiale
                pRelOpNxM = CType(pGeomSelColl, IRelationalOperatorNxM)
                'Exécuter la recherche et retourner le résultat de la relation spatiale
                pRelResult = pRelOpNxM.Intersects(CType(pGeomRelColl, IGeometryBag))

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Écriture des erreurs trouvées (" & m_FeatureLayerBDG.Name & ") ..."
                'Écriture des erreurs trouvées
                Call EcrireErreursSuperpose(pTrackCancel, pRelResult, pGeomSelColl, pGeomRelColl, iOidSel, iOidRel)

                'Vider la sélection des éléments BDG
                pFeatureSel.Clear()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureSel = Nothing
            pQueryFilter = Nothing
            sRequete = Nothing
            pGeomSelColl = Nothing
            pGeomRelColl = Nothing
            pRelOpNxM = Nothing
            pRelResult = Nothing
            iOidSel = Nothing
            iOidRel = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de lire les géométries et les OIDs des éléments d'un FeatureLayer.
    ''' 
    ''' Seuls les éléments sélectionnés sont lus.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pFeatureLayer"> Interface contenant les éléments à lire.</param>
    '''<param name="pSpatialRef"> Interface contenant la référence spatiale utilisée pour le traitement.</param>
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="pGeomColl"> Interface contenant les géométries des éléments lus.</param>
    '''<param name="iOid"> Vecteur des OIDs d'éléments lus.</param>
    ''' 
    Public Sub LireGeometrie(ByRef pFeatureLayer As IFeatureLayer, pSpatialRef As ISpatialReference, ByRef pTrackCancel As ITrackCancel,
                             ByRef pGeomColl As IGeometryCollection,
                             ByRef iOid() As Integer)
        'Déclarer les variables de travail
        Dim pFeatureSel As IFeatureSelection = Nothing      'Interface utilisé pour extraire et sélectionner les éléments du FeatureLayer.
        Dim pCursor As ICursor = Nothing                    'Interface utilisé pour lire les éléments.
        Dim pFeatureCursor As IFeatureCursor = Nothing      'Interface utilisé pour lire les éléments.
        Dim pFeature As IFeature = Nothing                  'Interface contenant l'élément lu.
        Dim pGeometry As IGeometry = Nothing                'Interface contenant la géométrie de l'élément lu.
        Dim pTopoOp As ITopologicalOperator = Nothing       'Interface pour extraire la limite de la géométrie.

        Try
            'Interface pour sélectionner les éléments
            pFeatureSel = CType(pFeatureLayer, IFeatureSelection)

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count

            'Afficher la barre de progression
            InitBarreProgression(0, m_NbElements, pTrackCancel)

            'Augmenter le vecteur des Oid selon le nombre d'éléments
            ReDim Preserve iOid(m_NbElements)

            'Créer un nouveau Bag vide
            pGeometry = New GeometryBag

            'Définir la référence spatiale
            pGeometry.SpatialReference = pSpatialRef
            pGeometry.SnapToSpatialReference()

            'Interface pour ajouter les géométries dans le Bag
            pGeomColl = CType(pGeometry, IGeometryCollection)

            'Interfaces pour extraire les éléments sélectionnés
            pFeatureSel.SelectionSet.Search(Nothing, False, pCursor)
            pFeatureCursor = CType(pCursor, IFeatureCursor)

            'Extraire le premier élément
            pFeature = pFeatureCursor.NextFeature()

            'Traiter tous les éléments du FeatureLayer
            For i = 0 To m_NbElements - 1
                'Vérifier si l'élément est présent
                If pFeature IsNot Nothing Then
                    'Définir la géométrie à traiter
                    pGeometry = pFeature.ShapeCopy

                    'Projeter la géométrie à traiter
                    pGeometry.Project(pSpatialRef)
                    pGeometry.SnapToSpatialReference()

                    'Ajouter la géométrie dans le Bag
                    pGeomColl.AddGeometry(pGeometry)

                    'Ajouter le OID de l'élément avec sa séquence 
                    iOid(i) = pFeature.OID
                End If

                'Vérifier si un Cancel a été effectué
                If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")

                'Extraire le prochain élément à traiter
                pFeature = pFeatureCursor.NextFeature()
            Next

            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(pFeatureCursor)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureSel = Nothing
            pCursor = Nothing
            pFeatureCursor = Nothing
            pFeature = Nothing
            pGeometry = Nothing
            pTopoOp = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet écrire les erreurs de l'action 2:Superimposed/Superpose du FeatureLayer traité.
    '''</summary>
    ''' 
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="pRelResult"> Résultat du traitement de la relation spatiale obtenu.</param>
    '''<param name="pGeomSelColl"> Interface contenant les géométries des éléments à traiter.</param>
    '''<param name="pGeomRelColl"> Interface contenant les géométries des éléments en relation.</param>
    '''<param name="iOidSel"> Vecteur des OIDs d'éléments à traiter.</param>
    '''<param name="iOidRel"> Vecteur des OIDs d'éléments en relation.</param>
    ''' 
    Private Sub EcrireErreursSuperpose(ByRef pTrackCancel As ITrackCancel, _
                                       ByVal pRelResult As IRelationResult,
                                       ByVal pGeomSelColl As IGeometryCollection,
                                       ByVal pGeomRelColl As IGeometryCollection, _
                                       ByVal iOidSel() As Integer,
                                       ByVal iOidRel() As Integer)
        'Déclarer les variables de travail
        Dim pSchemaLock As ISchemaLock = Nothing    'Interface pour enlever le lock sur la classe d'erreur.
        Dim pFeature As IFeature = Nothing          'Interface ESRI contenant l'élément en erreur.
        Dim pToponymeBDG As ToponymeBDG = Nothing   'Contient l'information du toponyme BDG.
        Dim pSetToponyme As ISet = Nothing      'Objet contenant tous les toponymes officiels d'un nom de toponyme.
        Dim iSel As Integer = -1                'Numéro de séquence de la géométrie traitée.
        Dim iRel As Integer = -1                'Numéro de séquence de la géométrie en relation.
        Dim iOid As Integer = 0                 'OID traité.
        Dim iNbLien As Integer = 0              'Numéro du lien.
        Dim iOidErr() As Integer                'Permet d'indiquer si le OID est en erreur
        Dim sConnectionString As String = Nothing   'Contient le texte de connexion à la BD de la toponymie
        Dim sNameId As String = Nothing                     'Contient le NameId du toponyme BDG.
        Dim iPosId As Integer = -1                          'Contient la position de l'attribut d'identifiant du toponyme.

        Try
            'Définir la position du NameId
            iPosId = m_FeatureLayerBDG.FeatureClass.FindField("NAMEID")

            'Afficher la barre de progression
            InitBarreProgression(0, pGeomSelColl.GeometryCount, pTrackCancel)

            'Augmenter le vecteur des Oid selon le nombre d'éléments
            ReDim Preserve iOidErr(m_NbElements)

            'Interface pour créer les erreurs
            m_FeatureCursorErreur = m_FeatureClassErreur.Insert(True)

            'Définir le texte de connexion à la BD
            sConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=TOPONYMY_PRO;" & "User Id=toponymy_view;" & "Password=viewtoponymy;"

            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(sConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Traiter tous les éléments
                For i = 0 To pRelResult.RelationElementCount - 1
                    'Extraire la géométrie traitée (left) et celle en relation (right) qui respectent la relation spatiale
                    pRelResult.RelationElement(i, iSel, iRel)

                    'Vérifier si on ne traite pas la même géométrie
                    If Not (iOidSel(iSel) = iOidRel(iRel)) Then
                        'Vérifier si le l'erreur n'a pas été identifiée
                        If iOidErr(iSel) = 0 Or iOidErr(iRel) = 0 Then
                            'Vérifier si le dernier OID est différent de celui traité
                            If iOid <> iOidSel(iSel) Then
                                'Conserver le OID traité
                                iOid = iOidSel(iSel)

                                'Compter le nombre de lien différent
                                iNbLien = iNbLien + 1

                                'Indiquer que l'erreur a été identifiée
                                iOidErr(iSel) = -1

                                'Conserver le nombre d'érreurs trouvées
                                m_NbErreurs = m_NbErreurs + 1

                                'Extraire l'élément de la classe des toponymes
                                pFeature = m_FeatureLayerBDG.FeatureClass.GetFeature(iOidSel(iSel))

                                'Extraire le NameId
                                sNameId = pFeature.Value(iPosId).ToString

                                'Définir le Toponyme BDG
                                pToponymeBDG = m_ListeNomToponymeBDG.Item(sNameId)

                                Try
                                    'Définir la liste des nameid du nom du toponyme officiel
                                    pSetToponyme = m_ListeNomToponymeOfficiel.Item(pToponymeBDG.Name)
                                Catch ex As Exception
                                    'Aucun nom du toponyme officiel
                                    pSetToponyme = Nothing
                                End Try

                                'Écrire une erreur
                                Call EcrireFeatureErreur(pFeature, 2, iNbLien, 1, pToponymeBDG.Name, pSetToponyme, qConnection)
                            End If

                            'Indiquer que l'erreur a été identifiée
                            iOidErr(iRel) = -1

                            'Conserver le nombre d'érreurs trouvées
                            m_NbErreurs = m_NbErreurs + 1

                            'Extraire l'élément de la classe des toponymes
                            pFeature = m_FeatureLayerBDG.FeatureClass.GetFeature(iOidRel(iRel))

                            'Extraire le NameId
                            sNameId = pFeature.Value(iPosId).ToString

                            'Définir le Toponyme BDG
                            pToponymeBDG = m_ListeNomToponymeBDG.Item(sNameId)

                            Try
                                'Définir la liste des nameid du nom du toponyme officiel
                                pSetToponyme = m_ListeNomToponymeOfficiel.Item(pToponymeBDG.Name)
                            Catch ex As Exception
                                'Aucun nom du toponyme officiel
                                pSetToponyme = Nothing
                            End Try

                            'Écrire une erreur
                            Call EcrireFeatureErreur(pFeature, 2, iNbLien, 2, pToponymeBDG.Name, pSetToponyme, qConnection)
                        End If
                    End If

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")
                Next

                'Fermer la connexion
                qConnection.Close()
            End Using

            'Conserver toutes les modifications
            m_FeatureCursorErreur.Flush()
            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(m_FeatureCursorErreur)

            'Interface pour enlever le lock sur la classe d'erreurs
            pSchemaLock = CType(m_FeatureClassErreur, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            iSel = Nothing
            iRel = Nothing
            iOid = Nothing
            iNbLien = Nothing
            iOidErr = Nothing
            pToponymeBDG = Nothing
            pSetToponyme = Nothing
            pFeature = Nothing
            pSchemaLock = Nothing
            sConnectionString = Nothing
            m_FeatureCursorErreur = Nothing
            sNameId = Nothing
            iPosId = Nothing
        End Try
    End Sub
#End Region

#Region "Routine et fonction 3:Rescinded/Abroge"
    '''<summary>
    ''' Routine qui permet de traiter l'action 3:Rescinded/Abroge pour les toponymes abrogés.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''
    '''<return>Les éléments qui sont abrogés avec le même nom seront inscrit dans la table d'erreurs avec le même numéro de lien.</return>
    '''
    Public Sub TraiterToponymeAbroge(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pFeatureSel As IFeatureSelection = Nothing  'Interface utilisé pour sélectionner les éléments.
        Dim pLienNomColl As SortedDictionary(Of String, ISet) = Nothing   'Object contenant les liens des noms de toponyme.
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface pour effectuer une requête attributive.
        Dim sRequete As String = Nothing                'Contient la requête pour trouver les toponymes inconnus.

        Try
            'Afficher le message de traitement de la relation spatiale
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Sélection des éléments abrogés (" & m_FeatureLayerBDG.Name & ") ..."
            'Définir la requête pour sélectionner les toponymes inconnus
            sRequete = "GEONAMEDB='CTI_LABEL' AND NAMEID NOT IN "
            sRequete = sRequete & "(SELECT DISTINCT NAMEID  FROM GES_TOPONYMIC_INFO WHERE GEONAMEDB='CTI_LABEL'"
            sRequete = sRequete & " and NAME_EN like '%Route' "
            sRequete = sRequete & " or NAME_EN like '%Byway'"
            sRequete = sRequete & " or NAME_EN like '%Freeway'"
            sRequete = sRequete & " or NAME_EN like '%Way'"
            sRequete = sRequete & " or NAME_EN like '%Highway'"
            sRequete = sRequete & " or NAME_EN like '%Highroad'"
            sRequete = sRequete & " or NAME_EN like '%Trail'"
            sRequete = sRequete & " or NAME_EN like '%Parkway'"
            sRequete = sRequete & " or NAME_EN like '%Road'"
            sRequete = sRequete & " or NAME_EN like '%Bridge'"
            sRequete = sRequete & " or NAME_EN like '%Drive'"
            sRequete = sRequete & " or NAME_FR like 'Route %'"
            sRequete = sRequete & " or NAME_FR like 'Rang %'"
            sRequete = sRequete & " or NAME_FR like 'Autoroute %'"
            sRequete = sRequete & " or NAME_FR like 'Pont %'"
            sRequete = sRequete & " or NAME_FR like 'Sentier %'  "
            sRequete = sRequete & " or NAME_EN like '% Airfield'"
            sRequete = sRequete & " or NAME_EN like '% Airport'"
            sRequete = sRequete & " or NAME_EN like '% Airpark'"
            sRequete = sRequete & " or NAME_EN like '% Seabase'"
            sRequete = sRequete & " or NAME_EN like '% Seaplane'"
            sRequete = sRequete & " or NAME_EN like '% Ferry'"
            sRequete = sRequete & " or NAME_FR like 'Base d''hydravion %'"
            sRequete = sRequete & " or NAME_FR like 'Terrain d''aviation %'"
            sRequete = sRequete & " or NAME_FR like 'Aroport %'"
            sRequete = sRequete & " or NAME_FR like 'Traversier %'"
            sRequete = sRequete & " or NAME_EN like '% Observatory'"
            sRequete = sRequete & " or NAME_EN like '% University'"
            sRequete = sRequete & " or NAME_EN like '% College'"
            sRequete = sRequete & " or NAME_EN like '% Experimental Farm' "
            sRequete = sRequete & " or NAME_FR like 'Collge %'"
            sRequete = sRequete & " or NAME_FR like 'Campus %'"
            sRequete = sRequete & " or NAME_FR like 'Ferme exprimentale %')"

            'Créer une requête vide
            pQueryFilter = New QueryFilter
            'Définir la requête attributive
            pQueryFilter.WhereClause = sRequete

            'Interface pour sélectionner les éléments
            pFeatureSel = CType(m_FeatureLayerBDG, IFeatureSelection)
            'Vérifier si une sélection est déjà présente
            If pFeatureSel.SelectionSet.Count = 0 Then
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultNew, False)
            Else
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAnd, False)
            End If

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0

            'Vérifier si des éléments ont été trouvé
            If pFeatureSel.SelectionSet.Count > 0 Then
                'Créer la liste des noms de toponyme BDG
                If m_ListeNomToponymeBDG Is Nothing Then Call CreerListeNomToponymeBDG(pTrackCancel, "GEONAMEDB='CTI_LABEL'")

                'Créer la liste des noms de toponyme CGNDB
                If m_ListeNomToponymeAbroge Is Nothing Then Call CreerListeNomToponymeAbroge(pTrackCancel)

                'Créer la liste des noms de toponyme CGNDB
                If m_ListeNomToponymeOfficiel Is Nothing Then Call CreerListeNomToponymeOfficiel(pTrackCancel)

                'Créer la nouvelle classe d'erreurs
                Call CreerClasseErreur("Rescinded_Abroge_0")

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lire les éléments abrogés (" & m_FeatureLayerBDG.Name & ") ..."
                'ÉLecture des éléments multiples
                Call LireElementMultiple(m_FeatureLayerBDG, pTrackCancel, pLienNomColl)

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Écriture des erreurs trouvées (Rescinded_Abroge_0) ..."
                'Écriture des erreurs trouvées
                Call EcrireErreursAbroge(m_FeatureLayerBDG, pTrackCancel, pLienNomColl, 3, 1, 1)

                'Vider la sélection des éléments BDG
                pFeatureSel.Clear()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureSel = Nothing
            pLienNomColl = Nothing
            pQueryFilter = Nothing
            sRequete = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet écrire les erreurs de l'action 3:Rescinded/Abroge du FeatureLayer traité.
    '''</summary>
    ''' 
    '''<param name="pFeatureLayer"> Interface contenant les éléments à lire.</param>
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="pLienNomColl">Contient la liste des liens entre les éléments pour chaque tiponyme.</param>
    '''<param name="iAction"> Contient le numéro de l'action effectuée.</param>
    '''<param name="iDecision"> Contient la décision par défaut.</param>
    '''<param name="iNbElementMin"> Contient le nombre minimum d'élément par défaut.</param>
    ''' 
    Private Sub EcrireErreursAbroge(ByRef pFeatureLayer As IFeatureLayer, ByRef pTrackCancel As ITrackCancel, _
                                    ByRef pLienNomColl As SortedDictionary(Of String, ISet), _
                                    Optional ByVal iAction As Integer = 5, _
                                    Optional ByVal iDecision As Integer = 1, _
                                    Optional ByVal iNbElementMin As Integer = 1)
        'Déclarer les variables de travail
        Dim pSchemaLock As ISchemaLock = Nothing    'Interface pour enlever le lock sur la classe d'erreur.
        Dim pFeature As IFeature = Nothing          'Interface contenant l'élément lu.
        Dim sNomToponyme As String = Nothing        'Contient le nom du toponyme.
        Dim pSetFeature As ISet = Nothing           'Objet contenant les éléments avec le même nom de toponyme.
        Dim pSetToponyme As ISet = Nothing          'Objet contenant tous les toponymes officiels d'un nom de toponyme.
        Dim iNbLien As Integer = 0                  'Contient le numéro de lien.
        Dim sConnectionString As String = Nothing   'Contient le texte de connexion à la BD de la toponymie

        Try
            'Afficher la barre de progression
            InitBarreProgression(0, pLienNomColl.Count, pTrackCancel)

            'Interface pour créer les erreurs
            m_FeatureCursorErreur = m_FeatureClassErreur.Insert(True)

            'Définir le texte de connexion à la BD
            sConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=TOPONYMY_PRO;" & "User Id=toponymy_view;" & "Password=viewtoponymy;"

            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(sConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Traiter tous les éléments du FeatureLayer
                For Each pLien As KeyValuePair(Of String, ISet) In pLienNomColl
                    'Définir le nom du toponyme
                    sNomToponyme = pLien.Key

                    'Vérifier si le nom est présent dans la table officiel des toponymes abrogés
                    If m_ListeNomToponymeAbroge.ContainsKey(sNomToponyme) Then
                        'Définir la liste des nameid du nom du toponyme officiel
                        pSetToponyme = m_ListeNomToponymeAbroge.Item(sNomToponyme)

                        'Définir l'ensemble de lien d'éléments
                        pSetFeature = pLien.Value

                        'Définir le numéro du lien
                        iNbLien = iNbLien + 1

                        'Extraire le premier élément
                        pSetFeature.Reset()
                        pFeature = CType(pSetFeature.Next, IFeature)

                        'Traiter tous les éléments
                        Do Until pFeature Is Nothing
                            'Conserver le nombre d'érreurs trouvées
                            m_NbErreurs = m_NbErreurs + 1

                            'Écrire une erreur
                            Call EcrireFeatureErreur(pFeature, iAction, iNbLien, iDecision, sNomToponyme, pSetToponyme, qConnection)

                            'Extraire le premier élément
                            pFeature = CType(pSetFeature.Next, IFeature)
                        Loop
                    End If

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")
                Next

                'Fermer la connexion
                qConnection.Close()
            End Using

            'Conserver toutes les modifications
            m_FeatureCursorErreur.Flush()
            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(m_FeatureCursorErreur)

            'Interface pour enlever le lock sur la classe d'erreurs
            pSchemaLock = CType(m_FeatureClassErreur, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pSchemaLock = Nothing
            pFeature = Nothing
            pSetFeature = Nothing
            pSetToponyme = Nothing
            iNbLien = Nothing
            sNomToponyme = Nothing
            sConnectionString = Nothing
            m_FeatureCursorErreur = Nothing
        End Try
    End Sub
#End Region

#Region "Routine et fonction 4:Official/Officiel"
    '''<summary>
    ''' Routine qui permet de traiter l'action 4:Official/Officiel pour les toponymes abrogés.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''
    '''<return>Les éléments qui sont abrogés avec le même nom seront inscrit dans la table d'erreurs avec le même numéro de lien.</return>
    '''
    Public Sub TraiterToponymeOfficiel(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pFeatureSel As IFeatureSelection = Nothing  'Interface utilisé pour sélectionner les éléments.
        Dim pLienNomColl As SortedDictionary(Of String, ISet) = Nothing   'Object contenant les liens des noms de toponyme.
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface pour effectuer une requête attributive.
        Dim sRequete As String = Nothing                'Contient la requête pour trouver les toponymes inconnus.

        Try
            'Afficher le message de traitement de la relation spatiale
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Sélection des éléments officiels (" & m_FeatureLayerBDG.Name & ") ..."
            'Définir la requête pour sélectionner les toponymes inconnus
            sRequete = "GEONAMEDB='CTI_LABEL' AND NAMEID NOT IN "
            sRequete = sRequete & "(SELECT DISTINCT NAMEID  FROM GES_TOPONYMIC_INFO WHERE GEONAMEDB='CTI_LABEL'"
            sRequete = sRequete & " and NAME_EN like '%Route' "
            sRequete = sRequete & " or NAME_EN like '%Byway'"
            sRequete = sRequete & " or NAME_EN like '%Freeway'"
            sRequete = sRequete & " or NAME_EN like '%Way'"
            sRequete = sRequete & " or NAME_EN like '%Highway'"
            sRequete = sRequete & " or NAME_EN like '%Highroad'"
            sRequete = sRequete & " or NAME_EN like '%Trail'"
            sRequete = sRequete & " or NAME_EN like '%Parkway'"
            sRequete = sRequete & " or NAME_EN like '%Road'"
            sRequete = sRequete & " or NAME_EN like '%Bridge'"
            sRequete = sRequete & " or NAME_EN like '%Drive'"
            sRequete = sRequete & " or NAME_FR like 'Route %'"
            sRequete = sRequete & " or NAME_FR like 'Rang %'"
            sRequete = sRequete & " or NAME_FR like 'Autoroute %'"
            sRequete = sRequete & " or NAME_FR like 'Pont %'"
            sRequete = sRequete & " or NAME_FR like 'Sentier %'  "
            sRequete = sRequete & " or NAME_EN like '% Airfield'"
            sRequete = sRequete & " or NAME_EN like '% Airport'"
            sRequete = sRequete & " or NAME_EN like '% Airpark'"
            sRequete = sRequete & " or NAME_EN like '% Seabase'"
            sRequete = sRequete & " or NAME_EN like '% Seaplane'"
            sRequete = sRequete & " or NAME_EN like '% Ferry'"
            sRequete = sRequete & " or NAME_FR like 'Base d''hydravion %'"
            sRequete = sRequete & " or NAME_FR like 'Terrain d''aviation %'"
            sRequete = sRequete & " or NAME_FR like 'Aroport %'"
            sRequete = sRequete & " or NAME_FR like 'Traversier %'"
            sRequete = sRequete & " or NAME_EN like '% Observatory'"
            sRequete = sRequete & " or NAME_EN like '% University'"
            sRequete = sRequete & " or NAME_EN like '% College'"
            sRequete = sRequete & " or NAME_EN like '% Experimental Farm' "
            sRequete = sRequete & " or NAME_FR like 'Collge %'"
            sRequete = sRequete & " or NAME_FR like 'Campus %'"
            sRequete = sRequete & " or NAME_FR like 'Ferme exprimentale %')"

            'Créer une requête vide
            pQueryFilter = New QueryFilter
            'Définir la requête attributive
            pQueryFilter.WhereClause = sRequete

            'Interface pour sélectionner les éléments
            pFeatureSel = CType(m_FeatureLayerBDG, IFeatureSelection)
            'Vérifier si une sélection est déjà présente
            If pFeatureSel.SelectionSet.Count = 0 Then
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultNew, False)
            Else
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAnd, False)
            End If

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0

            'Vérifier si des éléments ont été trouvé
            If pFeatureSel.SelectionSet.Count > 0 Then
                'Créer la liste des noms de toponyme BDG
                If m_ListeNomToponymeBDG Is Nothing Then Call CreerListeNomToponymeBDG(pTrackCancel, "GEONAMEDB='CTI_LABEL'")

                'Créer la liste des noms de toponyme CGNDB
                If m_ListeNomToponymeOfficiel Is Nothing Then Call CreerListeNomToponymeOfficiel(pTrackCancel)

                'Créer la nouvelle classe d'erreurs
                Call CreerClasseErreur("Official_Officiel_0")

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lire les éléments officiel (" & m_FeatureLayerBDG.Name & ") ..."
                'ÉLecture des éléments multiples
                Call LireElementMultiple(m_FeatureLayerBDG, pTrackCancel, pLienNomColl)

                'Afficher le message de traitement d'écriture des erreurs
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Écriture des erreurs trouvées (Official_Officiel_0) ..."
                'Écriture des erreurs trouvées
                Call EcrireErreursOfficiel(m_FeatureLayerBDG, pTrackCancel, pLienNomColl, 4, 1, 1)

                'Vider la sélection des éléments BDG
                pFeatureSel.Clear()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pLienNomColl = Nothing
            pFeatureSel = Nothing
            pQueryFilter = Nothing
            sRequete = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet écrire les erreurs de l'action 4:Official/Officiel du FeatureLayer traité.
    '''</summary>
    ''' 
    '''<param name="pFeatureLayer"> Interface contenant les éléments à lire.</param>
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="pLienNomColl">Contient la liste des liens entre les éléments pour chaque tiponyme.</param>
    '''<param name="iAction"> Contient le numéro de l'action effectuée.</param>
    '''<param name="iDecision"> Contient la décision par défaut.</param>
    '''<param name="iNbElementMin"> Contient le nombre minimum d'élément par défaut.</param>
    ''' 
    Private Sub EcrireErreursOfficiel(ByRef pFeatureLayer As IFeatureLayer, ByRef pTrackCancel As ITrackCancel, _
                                      ByRef pLienNomColl As SortedDictionary(Of String, ISet), _
                                      Optional ByVal iAction As Integer = 5, _
                                      Optional ByVal iDecision As Integer = 1, _
                                      Optional ByVal iNbElementMin As Integer = 1)
        'Déclarer les variables de travail
        Dim pSchemaLock As ISchemaLock = Nothing    'Interface pour enlever le lock sur la classe d'erreur.
        Dim pFeature As IFeature = Nothing          'Interface contenant l'élément lu.
        Dim sNomToponyme As String = Nothing        'Contient le nom du toponyme.
        Dim pSetFeature As ISet = Nothing           'Objet contenant les éléments avec le même nom de toponyme.
        Dim pSetToponyme As ISet = Nothing          'Objet contenant tous les toponymes officiels d'un nom de toponyme.
        Dim iNbLien As Integer = 0                  'Contient le numéro de lien.
        Dim sConnectionString As String = Nothing   'Contient le texte de connexion à la BD de la toponymie

        Try
            'Afficher la barre de progression
            InitBarreProgression(0, pLienNomColl.Count, pTrackCancel)

            'Interface pour créer les erreurs
            m_FeatureCursorErreur = m_FeatureClassErreur.Insert(True)

            'Définir le texte de connexion à la BD
            sConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=TOPONYMY_PRO;" & "User Id=toponymy_view;" & "Password=viewtoponymy;"

            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(sConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Traiter tous les éléments du FeatureLayer
                For Each pLien As KeyValuePair(Of String, ISet) In pLienNomColl
                    'Définir le nom du toponyme
                    sNomToponyme = pLien.Key

                    'Vérifier si le nom est présent dans la table officiel des toponymes abrogés
                    If m_ListeNomToponymeOfficiel.ContainsKey(sNomToponyme) Then
                        'Définir la liste des nameid du nom du toponyme officiel
                        pSetToponyme = m_ListeNomToponymeOfficiel.Item(sNomToponyme)

                        'Définir l'ensemble de lien d'éléments
                        pSetFeature = pLien.Value

                        'Définir le numéro du lien
                        iNbLien = iNbLien + 1

                        'Extraire le premier élément
                        pSetFeature.Reset()
                        pFeature = CType(pSetFeature.Next, IFeature)

                        'Traiter tous les éléments
                        Do Until pFeature Is Nothing
                            'Conserver le nombre d'érreurs trouvées
                            m_NbErreurs = m_NbErreurs + 1

                            'Écrire une erreur
                            Call EcrireFeatureErreur(pFeature, iAction, iNbLien, iDecision, sNomToponyme, pSetToponyme, qConnection)

                            'Extraire le premier élément
                            pFeature = CType(pSetFeature.Next, IFeature)
                        Loop
                    End If

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")
                Next

                'Fermer la connexion
                qConnection.Close()
            End Using

            'Conserver toutes les modifications
            m_FeatureCursorErreur.Flush()
            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(m_FeatureCursorErreur)

            'Interface pour enlever le lock sur la classe d'erreurs
            pSchemaLock = CType(m_FeatureClassErreur, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pSchemaLock = Nothing
            pFeature = Nothing
            pSetFeature = Nothing
            pSetToponyme = Nothing
            iNbLien = Nothing
            sNomToponyme = Nothing
            sConnectionString = Nothing
            m_FeatureCursorErreur = Nothing
        End Try
    End Sub
#End Region

#Region "Routine et fonction 5:Multiple/Multiple"
    '''<summary>
    ''' Routine qui permet de traiter l'action 5:Multiple/Multiple pour les toponymes multiples.
    ''' 
    ''' Seuls les éléments sélectionnés sont traités.
    ''' Si aucun élément n'est sélectionné, tous les éléments sont considérés sélectionnés.
    '''</summary>
    ''' 
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''
    '''<return>Les éléments Multiples seront inscrit dans la table d'erreurs avec le même numéro de lien.</return>
    '''
    Public Sub TraiterToponymeMultiple(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pLienNomColl As SortedDictionary(Of String, ISet) = Nothing   'Object contenant les liens des noms de toponyme.
        Dim pFeatureSel As IFeatureSelection = Nothing  'Interface utilisé pour sélectionner les éléments.
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface pour effectuer une requête attributive.
        Dim sRequete As String = Nothing                'Contient la requête pour trouver les toponymes inconnus.

        Try
            'Afficher le message de traitement de la relation spatiale
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Sélection des éléments multiples (" & m_FeatureLayerBDG.Name & ") ..."
            'Définir la requête pour sélectionner les toponymes inconnus
            sRequete = "GEONAMEDB='CTI_LABEL' AND NAMEID NOT IN "
            sRequete = sRequete & "(SELECT DISTINCT NAMEID  FROM GES_TOPONYMIC_INFO WHERE GEONAMEDB='CTI_LABEL'"
            sRequete = sRequete & " and NAME_EN like '%Route' "
            sRequete = sRequete & " or NAME_EN like '%Byway'"
            sRequete = sRequete & " or NAME_EN like '%Freeway'"
            sRequete = sRequete & " or NAME_EN like '%Way'"
            sRequete = sRequete & " or NAME_EN like '%Highway'"
            sRequete = sRequete & " or NAME_EN like '%Highroad'"
            sRequete = sRequete & " or NAME_EN like '%Trail'"
            sRequete = sRequete & " or NAME_EN like '%Parkway'"
            sRequete = sRequete & " or NAME_EN like '%Road'"
            sRequete = sRequete & " or NAME_EN like '%Bridge'"
            sRequete = sRequete & " or NAME_EN like '%Drive'"
            sRequete = sRequete & " or NAME_FR like 'Route %'"
            sRequete = sRequete & " or NAME_FR like 'Rang %'"
            sRequete = sRequete & " or NAME_FR like 'Autoroute %'"
            sRequete = sRequete & " or NAME_FR like 'Pont %'"
            sRequete = sRequete & " or NAME_FR like 'Sentier %'  "
            sRequete = sRequete & " or NAME_EN like '% Airfield'"
            sRequete = sRequete & " or NAME_EN like '% Airport'"
            sRequete = sRequete & " or NAME_EN like '% Airpark'"
            sRequete = sRequete & " or NAME_EN like '% Seabase'"
            sRequete = sRequete & " or NAME_EN like '% Seaplane'"
            sRequete = sRequete & " or NAME_EN like '% Ferry'"
            sRequete = sRequete & " or NAME_FR like 'Base d''hydravion %'"
            sRequete = sRequete & " or NAME_FR like 'Terrain d''aviation %'"
            sRequete = sRequete & " or NAME_FR like 'Aroport %'"
            sRequete = sRequete & " or NAME_FR like 'Traversier %'"
            sRequete = sRequete & " or NAME_EN like '% Observatory'"
            sRequete = sRequete & " or NAME_EN like '% University'"
            sRequete = sRequete & " or NAME_EN like '% College'"
            sRequete = sRequete & " or NAME_EN like '% Experimental Farm' "
            sRequete = sRequete & " or NAME_FR like 'Collge %'"
            sRequete = sRequete & " or NAME_FR like 'Campus %'"
            sRequete = sRequete & " or NAME_FR like 'Ferme exprimentale %')"

            'Créer une requête vide
            pQueryFilter = New QueryFilter
            'Définir la requête attributive
            pQueryFilter.WhereClause = sRequete

            'Interface pour sélectionner les éléments
            pFeatureSel = CType(m_FeatureLayerBDG, IFeatureSelection)
            'Vérifier si une sélection est déjà présente
            If pFeatureSel.SelectionSet.Count = 0 Then
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultNew, False)
            Else
                'Sélectionner les éléments
                pFeatureSel.SelectFeatures(pQueryFilter, esriSelectionResultEnum.esriSelectionResultAnd, False)
            End If

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count
            'Initialiser le nombre d'erreurs
            m_NbErreurs = 0

            'Vérifier si des éléments ont été trouvé
            If pFeatureSel.SelectionSet.Count > 0 Then
                'Créer la liste des noms de toponyme CTI
                If m_ListeNomToponymeBDG Is Nothing Then Call CreerListeNomToponymeBDG(pTrackCancel, "GEONAMEDB='CTI_LABEL'")

                'Créer la liste des noms de toponyme CGNDB
                If m_ListeNomToponymeOfficiel Is Nothing Then Call CreerListeNomToponymeOfficiel(pTrackCancel)

                'Créer la nouvelle classe d'erreurs
                Call CreerClasseErreur("Multiple_Multiple_0")

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lire les éléments multiples (" & m_FeatureLayerBDG.Name & ") ..."
                'Lecture des éléments multiples
                Call LireElementMultiple(m_FeatureLayerBDG, pTrackCancel, pLienNomColl)

                'Afficher le message de traitement de la relation spatiale
                If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Écriture des erreurs trouvées (Multiple_Multiple_0) ..."
                'Écriture des erreurs trouvées
                Call EcrireErreursMultiple(m_FeatureLayerBDG, pTrackCancel, pLienNomColl)

                'Vider la sélection des éléments BDG
                pFeatureSel.Clear()
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pLienNomColl = Nothing
            pFeatureSel = Nothing
            pQueryFilter = Nothing
            sRequete = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet lire les éléments de l'action 5:Multiple/Multiple du FeatureLayer traité.
    '''</summary>
    ''' 
    '''<param name="pFeatureLayer"> Interface contenant les éléments à lire.</param>
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="pLienNomColl"> Object contenant les liens des noms de toponyme.</param>
    ''' 
    Private Sub LireElementMultiple(ByRef pFeatureLayer As IFeatureLayer, ByRef pTrackCancel As ITrackCancel, _
                                    ByRef pLienNomColl As SortedDictionary(Of String, ISet))
        'Déclarer les variables de travail
        Dim pFeatureSel As IFeatureSelection = Nothing      'Interface utilisé pour extraire et sélectionner les éléments du FeatureLayer.
        Dim pCursor As ICursor = Nothing                    'Interface utilisé pour lire les éléments.
        Dim pFeatureCursor As IFeatureCursor = Nothing      'Interface utilisé pour lire les éléments.
        Dim pFeature As IFeature = Nothing                  'Interface contenant l'élément lu.
        Dim pSetFeature As ISet = Nothing                   'Objet content l'information du lien entre les éléments.
        Dim pToponymeBDG As ToponymeBDG = Nothing           'Contient l'information d'un toponyme BDG.
        Dim sNameId As String = Nothing                     'Contient le NameId du toponyme BDG.
        Dim iPosId As Integer = -1                          'Contient la position de l'attribut d'identifiant du toponyme.

        Try
            'Définir la position du NameId
            iPosId = pFeatureLayer.FeatureClass.FindField("NAMEID")

            'Interface pour sélectionner les éléments
            pFeatureSel = CType(pFeatureLayer, IFeatureSelection)

            'Conserver le nombre d'éléments à traiter
            m_NbElements = pFeatureSel.SelectionSet.Count

            'Afficher la barre de progression
            InitBarreProgression(0, m_NbElements, pTrackCancel)

            'Initialiser la collection de lien
            pLienNomColl = New SortedDictionary(Of String, ISet)

            'Interfaces pour extraire les éléments sélectionnés
            pFeatureSel.SelectionSet.Search(Nothing, False, pCursor)
            pFeatureCursor = CType(pCursor, IFeatureCursor)

            'Extraire le premier élément
            pFeature = pFeatureCursor.NextFeature()

            'Traiter tous les éléments du FeatureLayer
            For i = 0 To m_NbElements - 1
                'Vérifier si l'élément est présent
                If pFeature IsNot Nothing Then
                    'Extraire le NameId
                    sNameId = pFeature.Value(iPosId).ToString
                    'Vérifier si le nameid est présent dans la table des toponymes
                    If m_ListeNomToponymeBDG.ContainsKey(sNameId) Then
                        'Définir le nom du toponyme
                        pToponymeBDG = m_ListeNomToponymeBDG.Item(sNameId)

                        'Vérifier si le lien est déjà présent
                        If pLienNomColl.ContainsKey(pToponymeBDG.Name) Then
                            'Définir le lien
                            pSetFeature = CType(pLienNomColl.Item(pToponymeBDG.Name), ISet)

                            'Ajouter l'élément à l'ensemble
                            pSetFeature.Add(pFeature)

                            'Remettre l'item à jour
                            pLienNomColl(pToponymeBDG.Name) = pSetFeature

                            'Si le lien est absent
                        Else
                            'Créer un nouvel ensemble d'élément
                            pSetFeature = New ESRI.ArcGIS.esriSystem.Set

                            'Ajouter l'élément à l'ensemble
                            pSetFeature.Add(pFeature)

                            'Ajouter le lien du nom
                            pLienNomColl.Add(pToponymeBDG.Name, pSetFeature)
                        End If
                    End If
                End If

                'Vérifier si un Cancel a été effectué
                If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")

                'Extraire le prochain élément à traiter
                pFeature = pFeatureCursor.NextFeature()
            Next

            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(pFeatureCursor)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureSel = Nothing
            pCursor = Nothing
            pFeatureCursor = Nothing
            pFeature = Nothing
            pSetFeature = Nothing
            pToponymeBDG = Nothing
            sNameId = Nothing
            iPosId = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet écrire les erreurs de l'action 5:Multiple/Multiple du FeatureLayer traité.
    '''</summary>
    ''' 
    '''<param name="pFeatureLayer"> Interface contenant les éléments à lire.</param>
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="pLienNomColl">Contient la liste des liens entre les éléments pour chaque toponyme.</param>
    '''<param name="iAction"> Contient le numéro de l'action effectuée.</param>
    '''<param name="iDecision"> Contient la décision par défaut.</param>
    '''<param name="iNbElementMin"> Contient le nombre minimum d'élément par défaut.</param>
    ''' 
    Private Sub EcrireErreursMultiple(ByRef pFeatureLayer As IFeatureLayer, ByRef pTrackCancel As ITrackCancel, _
                                      ByRef pLienNomColl As SortedDictionary(Of String, ISet), _
                                      Optional ByVal iAction As Integer = 5, _
                                      Optional ByVal iDecision As Integer = 1, _
                                      Optional ByVal iNbElementMin As Integer = 1)
        'Déclarer les variables de travail
        Dim pSchemaLock As ISchemaLock = Nothing    'Interface pour enlever le lock sur la classe d'erreur.
        Dim pFeature As IFeature = Nothing          'Interface contenant l'élément lu.
        Dim sNomToponyme As String = Nothing        'Contient le nom du toponyme.
        Dim pSetFeature As ISet = Nothing           'Objet contenant les éléments avec le même nom de toponyme.
        Dim pSetToponyme As ISet = Nothing          'Objet contenant tous les toponymes officiels d'un nom de toponyme.
        Dim iNbLien As Integer = 0                  'Contient le numéro de lien.
        Dim sConnectionString As String = Nothing   'Contient le texte de connexion à la BD de la toponymie

        Try
            'Afficher la barre de progression
            InitBarreProgression(0, pLienNomColl.Count, pTrackCancel)

            'Interface pour créer les erreurs
            m_FeatureCursorErreur = m_FeatureClassErreur.Insert(True)

            'Définir le texte de connexion à la BD
            sConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=TOPONYMY_PRO;" & "User Id=toponymy_view;" & "Password=viewtoponymy;"

            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(sConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Traiter tous les éléments du FeatureLayer
                For Each pLien As KeyValuePair(Of String, ISet) In pLienNomColl
                    'Définir le nom du toponyme
                    sNomToponyme = pLien.Key

                    Try
                        'Définir la liste des nameid du nom du toponyme officiel
                        pSetToponyme = m_ListeNomToponymeOfficiel.Item(sNomToponyme)
                    Catch ex As Exception
                        'Aucun nom du toponyme officiel
                        pSetToponyme = Nothing
                    End Try

                    'Définir l'ensemble de lien d'éléments
                    pSetFeature = pLien.Value

                    'Vérifier la valeur minimum du nombre d'éléments
                    If pSetFeature.Count > iNbElementMin Then
                        'Définir le numéro du lien
                        iNbLien = iNbLien + 1

                        'Extraire le premier élément
                        pSetFeature.Reset()
                        pFeature = CType(pSetFeature.Next, IFeature)

                        'Traiter tous les éléments
                        Do Until pFeature Is Nothing
                            'Conserver le nombre d'érreurs trouvées
                            m_NbErreurs = m_NbErreurs + 1

                            'Écrire une erreur
                            Call EcrireFeatureErreur(pFeature, iAction, iNbLien, iDecision, sNomToponyme, pSetToponyme, qConnection)

                            'Extraire le premier élément
                            pFeature = CType(pSetFeature.Next, IFeature)
                        Loop
                    End If

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")
                Next

                'Fermer la connexion
                qConnection.Close()
            End Using

            'Conserver toutes les modifications
            m_FeatureCursorErreur.Flush()
            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(m_FeatureCursorErreur)

            'Interface pour enlever le lock sur la classe d'erreurs
            pSchemaLock = CType(m_FeatureClassErreur, ISchemaLock)
            pSchemaLock.ChangeSchemaLock(esriSchemaLock.esriSharedSchemaLock)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pSchemaLock = Nothing
            pFeature = Nothing
            pSetFeature = Nothing
            pSetToponyme = Nothing
            iNbLien = Nothing
            sNomToponyme = Nothing
            sConnectionString = Nothing
            m_FeatureCursorErreur = Nothing
        End Try
    End Sub
#End Region

#Region "Routine et fonction privées"
    '''<summary>
    ''' Routine qui permet de créer la liste des noms de toponyme BDG dans un dictionnaire basé sur le NAMEID.
    '''</summary>
    '''
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="sRequeteAttributive"> Requête attributive pour extraire seulement certains noms de toponyme.</param>
    ''' 
    Public Sub CreerListeNomToponymeBDG(ByRef pTrackCancel As ITrackCancel, ByVal sRequeteAttributive As String)
        'Déclarer les variables de travail
        Dim pQueryFilter As IQueryFilter = Nothing      'Interface pour effectuer une requête attributive.
        Dim pCursor As ICursor = Nothing                'Interface utilisé pour lire les éléments.
        Dim pRow As IRow = Nothing                      'Interface contenant le nom de la toponymie.
        Dim pToponymeBDG As ToponymeBDG = Nothing       'Contient l'information du toponyme de la BDG.
        Dim iPosOid As Integer = -1     'Contient la position de l'attribut de l'identifiant de l'élément.
        Dim iPosName As Integer = -1    'Contient la position de l'attribut du nom de toponyme.
        Dim iPosId As Integer = -1      'Contient la position de l'attribut de l'identifiant de toponyme.

        Try
            'Définir la position des attributs dans la table
            iPosOid = m_TableToponymeBDG.Table.FindField("OBJECTID")
            iPosName = m_TableToponymeBDG.Table.FindField("NAME_EN")
            iPosId = m_TableToponymeBDG.Table.FindField("NAMEID")

            'Afficher le message de lecture des éléments
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lecture des noms de toponyme BDG (" & m_TableToponymeBDG.Name & ") ..."

            'Initialiser la liste des noms de toponyme BDG
            m_ListeNomToponymeBDG = New Dictionary(Of String, ToponymeBDG)

            'Interface pour créer une nouvelle requête
            pQueryFilter = New QueryFilter
            'Définir les attributs à extraire
            pQueryFilter.SubFields = "NAMEID, NAME_EN, OBJECTID"
            'Définir la requête
            pQueryFilter.WhereClause = sRequeteAttributive

            'Afficher la barre de progression
            InitBarreProgression(0, m_TableToponymeBDG.Table.RowCount(pQueryFilter), pTrackCancel)

            'Interface pour extraire les noms de toponymes
            pCursor = m_TableToponymeBDG.Table.Search(pQueryFilter, False)

            'Extraire le premier toponyme
            pRow = pCursor.NextRow

            'Vérifier si le nameid est présent dans la table des toponymes
            Do Until pRow Is Nothing
                'Vérifier si le NAMEID est déjà présent
                If m_ListeNomToponymeBDG.ContainsKey(pRow.Value(iPosId).ToString) Then
                    'Afficher un message d'erreur
                    Debug.Print(pRow.Value(iPosId).ToString & ":" & pRow.Value(iPosName).ToString & " Duppliqué")
                Else
                    'Créer un nouveau Toponyme BDG
                    pToponymeBDG = New ToponymeBDG
                    'Définir l'information
                    pToponymeBDG.Name = pRow.Value(iPosName).ToString
                    pToponymeBDG.OID = CInt(pRow.Value(iPosOid))
                    'Ajouter le nom anglais du toponyme
                    m_ListeNomToponymeBDG.Add(pRow.Value(iPosId).ToString, pToponymeBDG)
                    If pToponymeBDG.OID = 0 Then Debug.Print(pToponymeBDG.OID.ToString & "-" & pToponymeBDG.Name)
                End If

                'Vérifier si un Cancel a été effectué
                If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")

                'Extraire le prochain toponyme
                pRow = pCursor.NextRow
            Loop

            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(pCursor)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pCursor = Nothing
            pQueryFilter = Nothing
            pRow = Nothing
            pToponymeBDG = Nothing
            iPosName = Nothing
            iPosId = Nothing
            iPosOid = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer la liste des noms de toponyme abrogés dans un dictionnaire basé sur le Nom du toponyme officiel.
    '''</summary>
    '''
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    ''' 
    Public Sub CreerListeNomToponymeAbroge(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface pour ouvrir la table de toponymie
        Dim pQueryFilter As IQueryFilter = Nothing  'Interface pour effectuer une requête attributive.
        Dim pCursor As ICursor = Nothing            'Interface utilisé pour lire les éléments.
        Dim pRow As IRow = Nothing                  'Interface contenant le nom de la toponymie.
        Dim pSetToponyme As ISet = Nothing          'Contient un ensemble d'information de toponyme.
        Dim pToponyme As Toponyme = Nothing         'Objet contenant le NameId et le SNRC du toponyme.
        Dim iPosName As Integer = -1    'Contient la position de l'attribut du nom de toponyme.
        Dim iPosId As Integer = -1      'Contient la position de l'attribut de l'identifiant de toponyme.
        Dim iPosSnrc As Integer = -1    'Contient la position de l'attribut du Snrc de toponyme.

        Try
            'Définir la position des attributs dans la table
            iPosName = m_TableToponymeCGNDB.Table.FindField("GEOGRAPHICAL_NAME")
            iPosId = m_TableToponymeCGNDB.Table.FindField("TOPONYMIC_FEATURE_ID")
            iPosSnrc = m_TableToponymeCGNDB.Table.FindField("GAZETTEER_MAP_ID")

            'Afficher le message de lecture des éléments
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lecture des noms de toponyme CGNDB abrogés (" & m_TableToponymeCGNDB.Name & ") ..."

            'Initialiser la liste des noms de toponyme abrogés
            m_ListeNomToponymeAbroge = New SortedDictionary(Of String, ISet)

            'Interface pour créer une nouvelle requête
            pQueryFilter = New QueryFilter
            'Définir les attributs à extraire
            pQueryFilter.SubFields = "GEOGRAPHICAL_NAME,TOPONYMIC_FEATURE_ID, GAZETTEER_MAP_ID"
            'Définir la requête
            pQueryFilter.WhereClause = "STATUS_CODE_CL IN (1193,1195,1196,1197,1200,1201)"

            'Afficher la barre de progression
            InitBarreProgression(0, m_TableToponymeCGNDB.Table.RowCount(pQueryFilter), pTrackCancel)

            'Interface pour extraire les noms de toponymes de la CGNDB
            pCursor = m_TableToponymeCGNDB.Table.Search(pQueryFilter, False)

            'Extraire le premier toponyme
            pRow = pCursor.NextRow

            'Vérifier si le nameid est présent dans la table des toponymes
            Do Until pRow Is Nothing
                'Vérifier si le Nom est déjà présent
                If m_ListeNomToponymeAbroge.ContainsKey(pRow.Value(iPosName).ToString.ToString) Then
                    'Créer un nouvel ensemble
                    pSetToponyme = CType(m_ListeNomToponymeAbroge.Item(pRow.Value(iPosName).ToString), ISet)

                    'Créer le toponyme
                    pToponyme = New Toponyme
                    'Définir le NameId du toponyme
                    pToponyme.NameId = pRow.Value(iPosId).ToString
                    'Définir le SNRC du toponyme
                    pToponyme.Snrc = pRow.Value(iPosSnrc).ToString
                    'Ajouter l'information du toponyme à l'ensemble
                    pSetToponyme.Add(pToponyme)

                    'Remettre l'item à jour
                    m_ListeNomToponymeAbroge(pRow.Value(iPosName).ToString) = pSetToponyme

                Else
                    'Créer un nouvel ensemble
                    pSetToponyme = New ESRI.ArcGIS.esriSystem.Set

                    'Créer le toponyme
                    pToponyme = New Toponyme
                    'Définir le NameId du toponyme
                    pToponyme.NameId = pRow.Value(iPosId).ToString
                    'Définir le SNRC du toponyme
                    pToponyme.Snrc = pRow.Value(iPosSnrc).ToString
                    'Ajouter le NAMEID à l'ensemble
                    pSetToponyme.Add(pToponyme)

                    'Ajouter le toponyme basé sur le nom
                    m_ListeNomToponymeAbroge.Add(pRow.Value(iPosName).ToString, pSetToponyme)
                End If

                'Vérifier si un Cancel a été effectué
                If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")

                'Extraire le prochain toponyme
                pRow = pCursor.NextRow
            Loop

            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(pCursor)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pCursor = Nothing
            pQueryFilter = Nothing
            pRow = Nothing
            pSetToponyme = Nothing
            pToponyme = Nothing
            iPosName = Nothing
            iPosId = Nothing
            iPosSnrc = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer la liste des noms de toponyme officiel dans un dictionnaire basé sur le Nom du toponyme officiel.
    '''</summary>
    '''
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    ''' 
    Public Sub CreerListeNomToponymeOfficiel(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing    'Interface pour ouvrir la table de toponymie
        Dim pQueryFilter As IQueryFilter = Nothing  'Interface pour effectuer une requête attributive.
        Dim pCursor As ICursor = Nothing            'Interface utilisé pour lire les éléments.
        Dim pRow As IRow = Nothing                  'Interface contenant le nom de la toponymie.
        Dim pSetToponyme As ISet = Nothing          'Contient un ensemble d'information de toponyme.
        Dim pToponyme As Toponyme = Nothing         'Objet contenant le NameId et le SNRC du toponyme.
        Dim iPosName As Integer = -1    'Contient la position de l'attribut du nom de toponyme.
        Dim iPosId As Integer = -1      'Contient la position de l'attribut de l'identifiant de toponyme.
        Dim iPosSnrc As Integer = -1    'Contient la position de l'attribut du Snrc de toponyme.
        Dim iPosPub As Integer = -1     'Contient la position de l'attribut de l'indice publique.

        Try
            'Définir la position des attributs dans la table
            iPosName = m_TableToponymeCGNDB.Table.FindField("GEOGRAPHICAL_NAME")
            iPosId = m_TableToponymeCGNDB.Table.FindField("TOPONYMIC_FEATURE_ID")
            iPosSnrc = m_TableToponymeCGNDB.Table.FindField("GAZETTEER_MAP_ID")
            iPosPub = m_TableToponymeCGNDB.Table.FindField("IS_PUBLIC_CL")

            'Afficher le message de lecture des éléments
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lecture des noms de toponyme CGNDB officiels (" & m_TableToponymeCGNDB.Name & ") ..."

            'Initialiser la liste des noms de toponyme officiel
            m_ListeNomToponymeOfficiel = New SortedDictionary(Of String, ISet)
            m_ListeNomToponymeId = New Dictionary(Of String, String)

            'Interface pour créer une nouvelle requête
            pQueryFilter = New QueryFilter
            'Définir les attributs à extraire
            pQueryFilter.SubFields = "GEOGRAPHICAL_NAME,TOPONYMIC_FEATURE_ID, GAZETTEER_MAP_ID, IS_PUBLIC_CL"
            'Définir la requête
            pQueryFilter.WhereClause = "STATUS_CODE_CL NOT IN (1193,1195,1196,1197,1200,1201)"

            'Afficher la barre de progression
            InitBarreProgression(0, m_TableToponymeCGNDB.Table.RowCount(pQueryFilter), pTrackCancel)

            'Interface pour extraire les noms de toponymes de la CGNDB
            pCursor = m_TableToponymeCGNDB.Table.Search(pQueryFilter, False)

            'Extraire le premier toponyme
            pRow = pCursor.NextRow

            'Vérifier si le nameid est présent dans la table des toponymes
            Do Until pRow Is Nothing
                'Vérifier si le Nom est déjà présent
                If m_ListeNomToponymeOfficiel.ContainsKey(pRow.Value(iPosName).ToString.ToString) Then
                    'Créer un nouvel ensemble
                    pSetToponyme = CType(m_ListeNomToponymeOfficiel.Item(pRow.Value(iPosName).ToString), ISet)

                    'Créer le toponyme
                    pToponyme = New Toponyme
                    'Définir le NameId du toponyme
                    pToponyme.NameId = pRow.Value(iPosId).ToString
                    'Définir le SNRC du toponyme
                    pToponyme.Snrc = pRow.Value(iPosSnrc).ToString
                    'Ajouter l'information du toponyme à l'ensemble
                    pSetToponyme.Add(pToponyme)

                    'Remettre l'item à jour
                    m_ListeNomToponymeOfficiel(pRow.Value(iPosName).ToString) = pSetToponyme

                Else
                    'Créer un nouvel ensemble
                    pSetToponyme = New ESRI.ArcGIS.esriSystem.Set

                    'Créer le toponyme
                    pToponyme = New Toponyme
                    'Définir le NameId du toponyme
                    pToponyme.NameId = pRow.Value(iPosId).ToString
                    'Définir le SNRC du toponyme
                    pToponyme.Snrc = pRow.Value(iPosSnrc).ToString
                    'Ajouter le NAMEID à l'ensemble
                    pSetToponyme.Add(pToponyme)

                    'Ajouter le toponyme basé sur le nom
                    m_ListeNomToponymeOfficiel.Add(pRow.Value(iPosName).ToString, pSetToponyme)
                End If

                'Vérifier si l'identifiant du toponyme officiel est absent
                If Not m_ListeNomToponymeId.ContainsKey(pRow.Value(iPosId).ToString) Then
                    'Ajouter l'identifiant du toponyme officiel avec son nom
                    Call m_ListeNomToponymeId.Add(pRow.Value(iPosId).ToString, pRow.Value(iPosName).ToString)

                    'Vérifier si le toponyme est public
                ElseIf CInt(pRow.Value(iPosPub)) = 11 Then
                    'Remettre l'item à jour
                    m_ListeNomToponymeId(pRow.Value(iPosId).ToString) = pRow.Value(iPosName).ToString
                End If

                'Vérifier si un Cancel a été effectué
                If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")

                'Extraire le prochain toponyme
                pRow = pCursor.NextRow
            Loop

            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(pCursor)

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pCursor = Nothing
            pQueryFilter = Nothing
            pRow = Nothing
            pSetToponyme = Nothing
            pToponyme = Nothing
            iPosName = Nothing
            iPosId = Nothing
            iPosSnrc = Nothing
            iPosPub = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer la liste des noms de toponyme BDG dans un dictionnaire basé sur le NAMEID.
    '''</summary>
    '''
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="sRequeteAttributive"> Requête attributive pour extraire seulement certains noms de toponyme.</param>
    ''' 
    Public Sub CreerListeNomToponymeBDG2(ByRef pTrackCancel As ITrackCancel, ByVal sRequeteAttributive As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête
        Dim sConnectionString As String = Nothing   'Contient le texte de connexion à la BD de la toponymie
        Dim sQueryString As String = Nothing        'Requête utilisée pour valider la BD des catalogues
        Dim pToponymeBDG As ToponymeBDG = Nothing   'contient l'information du toponyme de la BDG.

        Try
            'Afficher le message de lecture des éléments
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lecture des noms de toponyme BDG (" & m_TableToponymeBDG.Name & ") ..."

            'Initialiser la liste des noms de toponyme BDG
            m_ListeNomToponymeBDG = New Dictionary(Of String, ToponymeBDG)

            'Définir le texte de connexion à la BD
            sConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=BDRS_PRO;" & "User Id=bdg;" & "Password=pro;"

            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(sConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL pour extraire le nombre d'items
                sQueryString = "SELECT COUNT(NAMEID)" _
                             & "  FROM BDG_DBA.GES_TOPONYMIC_INFO" _
                             & " WHERE GEONAMEDB='CTI_LABEL'"
                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)
                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()
                'Lire le nombre d'items
                qReader.Read()
                'Afficher la barre de progression
                InitBarreProgression(0, CInt(qReader.GetValue(0)), pTrackCancel)
                'Fermer la lecture
                qReader.Close()

                'Définir la requête SQL
                sQueryString = "SELECT NAMEID, NAME_EN, OBJECTID" _
                             & "  FROM BDG_DBA.GES_TOPONYMIC_INFO" _
                             & " WHERE GEONAMEDB='CTI_LABEL'"
                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)
                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Vérifier si le NAMEID est déjà présent
                    If m_ListeNomToponymeBDG.ContainsKey(qReader.GetValue(1).ToString) Then
                        'Afficher un message d'erreur
                        Debug.Print(qReader.GetValue(0).ToString & ":" & qReader.GetValue(1).ToString & " Duppliqué")
                    Else
                        'Créer un nouveau Toponyme BDG
                        pToponymeBDG = New ToponymeBDG
                        'Définir l'information
                        pToponymeBDG.Name = qReader.GetValue(1).ToString
                        pToponymeBDG.OID = CInt(qReader.GetValue(2))
                        'Ajouter le nom anglais du toponyme
                        m_ListeNomToponymeBDG.Add(qReader.GetValue(0).ToString, pToponymeBDG)
                    End If

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")
                End While

                'Fermer la lecture
                qReader.Close()
                'Fermer les curseurs
                qCommand.Dispose()
                'Fermer la connexion
                qConnection.Close()
            End Using

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sConnectionString = Nothing
            sQueryString = Nothing
            pToponymeBDG = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer la liste des noms de toponyme CGNDB dans un dictionnaire basé sur le nom du toponyme.
    '''</summary>
    '''
    '''<param name="pListeNomToponyme"> Dictionnaire contenant le NameId et le SNRC des toponymes officiels.</param>
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    '''<param name="sRequeteAttributive"> Requête attributive pour extraire seulement certains noms de toponyme.</param>
    ''' 
    Public Sub CreerListeNomToponymeCGNDB2(ByRef pListeNomToponyme As SortedDictionary(Of String, ISet), ByRef pTrackCancel As ITrackCancel, ByVal sRequeteAttributive As String)
        'Déclarer les variables de travail
        Dim pSetToponyme As ISet = Nothing          'Contient un ensemble d'information de toponyme.
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête
        Dim sConnectionString As String = Nothing   'Contient le texte de connexion à la BD de la toponymie
        Dim sQueryString As String = Nothing        'Requête utilisée pour valider la BD des catalogues
        Dim pToponyme As Toponyme = Nothing         'Objet contenant le NameId et le SNRC du toponyme.

        Try
            'Afficher le message de lecture des éléments
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lecture des noms de toponyme CGNDB (" & m_TableToponymeCGNDB.Name & ") ..."

            'Initialiser la liste des noms de toponyme officiel
            pListeNomToponyme = New SortedDictionary(Of String, ISet)

            'Définir le texte de connexion à la BD
            sConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=TOPONYMY_PRO;" & "User Id=toponymy_view;" & "Password=viewtoponymy;"

            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(sConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL
                sQueryString = "SELECT COUNT(GEOGRAPHICAL_NAME)" _
                             & "  FROM TOPONYMY_DBA.TOPONYM_6" _
                             & " WHERE " & sRequeteAttributive
                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)
                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()
                'Lire le nombre d'items
                qReader.Read()
                'Afficher la barre de progression
                InitBarreProgression(0, CInt(qReader.GetValue(0)), pTrackCancel)
                'Fermer la lecture
                qReader.Close()

                'Définir la requête SQL
                sQueryString = "SELECT GEOGRAPHICAL_NAME,TOPONYMIC_FEATURE_ID, GAZETTEER_MAP_ID" _
                             & "  FROM TOPONYMY_DBA.TOPONYM_6" _
                             & " WHERE " & sRequeteAttributive
                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)
                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Vérifier si le Nom est déjà présent
                    If pListeNomToponyme.ContainsKey(qReader.GetValue(0).ToString) Then
                        'Créer un nouvel ensemble
                        pSetToponyme = CType(pListeNomToponyme.Item(qReader.GetValue(0).ToString), ISet)

                        'Créer le toponyme
                        pToponyme = New Toponyme
                        'Définir le NameId du toponyme
                        pToponyme.NameId = qReader.GetValue(1).ToString
                        'Définir le SNRC du toponyme
                        pToponyme.Snrc = qReader.GetValue(2).ToString
                        'Ajouter l'information du toponyme à l'ensemble
                        pSetToponyme.Add(pToponyme)

                        'Remettre l'item à jour
                        pListeNomToponyme(qReader.GetValue(0).ToString) = pSetToponyme

                    Else
                        'Créer un nouvel ensemble
                        pSetToponyme = New ESRI.ArcGIS.esriSystem.Set

                        'Créer le toponyme
                        pToponyme = New Toponyme
                        'Définir le NameId du toponyme
                        pToponyme.NameId = qReader.GetValue(1).ToString
                        'Définir le SNRC du toponyme
                        pToponyme.Snrc = qReader.GetValue(2).ToString
                        'Ajouter le NAMEID à l'ensemble
                        pSetToponyme.Add(pToponyme)

                        'Ajouter le nameid du toponyme
                        pListeNomToponyme.Add(qReader.GetValue(0).ToString, pSetToponyme)
                    End If

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")
                End While

                'Fermer la lecture
                qReader.Close()
                'Fermer les curseurs
                qCommand.Dispose()
                'Fermer la connexion
                qConnection.Close()
            End Using

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            pSetToponyme = Nothing
            qCommand = Nothing
            qReader = Nothing
            sConnectionString = Nothing
            sQueryString = Nothing
            pToponyme = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer la liste des Snrc de la BDG qui sont en production.
    '''</summary>
    '''
    '''<param name="pTrackCancel"> Permet d'annuler la sélection avec la touche ESC du clavier.</param>
    ''' 
    Private Sub CreerListeSnrcProduction(ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête
        Dim sConnectionString As String = Nothing   'Contient le texte de connexion à la BD de la toponymie
        Dim sQueryString As String = Nothing        'Requête utilisée pour valider la BD des catalogues

        Try
            'Afficher le message de lecture
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Message = "Lecture des Snrc BDG en production (SIB_PRO) ..."

            'Initialiser la liste des Snrcs en production
            m_ListeSnrcProduction = New Dictionary(Of String, String)

            'Définir le texte de connexion à la BD
            sConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=SIB_PRO;" & "User Id=modview;" & "Password=decyukon;"

            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(sConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL pour extraire le nombre d'items
                sQueryString = "SELECT COUNT(DISTINCT IDENTIFIANT)" _
                             & "  FROM SIBDBA.F502_PS" _
                             & " WHERE TY_PRODUIT='BDG' AND E_PLSNRC ='P' ORDER BY IDENTIFIANT"
                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)
                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()
                'Lire le nombre d'items
                qReader.Read()
                'Afficher la barre de progression
                InitBarreProgression(0, CInt(qReader.GetValue(0)), pTrackCancel)
                'Fermer la lecture
                qReader.Close()

                'Définir la requête SQL
                sQueryString = "SELECT DISTINCT IDENTIFIANT" _
                             & "  FROM SIBDBA.F502_PS" _
                             & " WHERE TY_PRODUIT='BDG' AND E_PLSNRC ='P' ORDER BY IDENTIFIANT"
                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)
                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Ajouter le Snrc en production
                    m_ListeSnrcProduction.Add(qReader.GetValue(0).ToString, qReader.GetValue(0).ToString)

                    'Vérifier si un Cancel a été effectué
                    If pTrackCancel.Continue = False Then Throw New CancelException("Traitement annulé !")
                End While

                'Fermer la lecture
                qReader.Close()
                'Fermer les curseurs
                qCommand.Dispose()
                'Fermer la connexion
                qConnection.Close()
            End Using

            'Cacher la barre de progression
            If pTrackCancel.Progressor IsNot Nothing Then pTrackCancel.Progressor.Hide()

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sConnectionString = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de créer la classe d'erreurs.
    '''</summary>
    '''
    '''<param name="sNomClasseErreur"> Nom de la nouvelle classe d'erreurs à créer.</param>
    ''' 
    Private Sub CreerClasseErreur(ByVal sNomClasseErreur As String)
        'Déclarer les variables de travail
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing        'Interface utilisé pour ouvrir une classe dans une géodatabase.

        Try
            'Définir la géodatabase des erreurs
            m_GeodatabaseErreur = DefinirGeodatabase(m_NomGeodatabaseErreur)
            'Interface pour ouvrir une classe existante
            pFeatureWorkspace = CType(m_GeodatabaseErreur, IFeatureWorkspace)

            Try
                'Définir la classe d'erreurs de base à copier
                m_FeatureClassErreur = pFeatureWorkspace.OpenFeatureClass(m_NomClasseErreur)
            Catch ex As Exception
                Throw New Exception("ERREUR : Impossible d'ouvrir la classe d'erreur : " & m_NomClasseErreur)
            End Try

            'Copier la classe d'erreurs de base dans une nouvelle
            ConvertFeatureClass(m_FeatureClassErreur, CType(m_GeodatabaseErreur, IWorkspace2), sNomClasseErreur)

            Try
                'Définir la nouvelle classe d'erreurs
                m_FeatureClassErreur = pFeatureWorkspace.OpenFeatureClass(sNomClasseErreur)
            Catch ex As Exception
                Throw New Exception("ERREUR : Impossible d'ouvrir la classe d'erreur : " & sNomClasseErreur)
            End Try

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureWorkspace = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'écrire une erreur dans la table d'erreurs
    '''</summary>
    ''' 
    '''<param name="pFeature"> Élément en erreur.</param>
    '''<param name="iAction"> Numéro de l'action effectuée.</param>
    '''<param name="iLien"> Numéro du lien entre les erreurs.</param>
    '''<param name="iDecision"> Décision par défaut.</param>
    '''<param name="sNomToponyme"> Nom du toponyme.</param>
    '''<param name="pSetToponyme"> Liste des Toponymes officiels pour un nom de toponyme.</param>
    '''
    Private Sub EcrireFeatureErreur(ByRef pFeature As IFeature, _
                                    ByVal iAction As Integer, ByVal iLien As Integer, ByVal iDecision As Integer,
                                    ByVal sNomToponyme As String,
                                    ByRef pSetToponyme As ISet,
                                    ByRef qConnection As OleDbConnection)
        'Déclarer les variables de travail
        Dim pFeatureBuffer As IFeatureBuffer = Nothing  'Interface ESRI contenant l'élément de l'incohérence à créer.
        Dim sNomToponymeOfficiel As String = Nothing    'Contient le nom du toponyme officiel.
        Dim pToponyme As Toponyme = Nothing             'Objet contenant le NameId et le SNRC du toponyme.
        Dim iPosOid As Integer = -1     'Contient la position de l'attribut de l'identifiant de l'élément.
        Dim iPosId As Integer = -1      'Contient la position de l'attribut de l'identifiant de toponyme.
        Dim iPosSnrc As Integer = -1    'Contient la position de l'attribut du Snrc de toponyme.
        Dim iPosBDG_ID As Integer = -1  'Contient la position de l'attribut BDG_ID.

        Try
            'Définir la position des attributs dans la table
            iPosOid = m_FeatureLayerBDG.FeatureClass.FindField("OBJECTID")
            iPosId = m_FeatureLayerBDG.FeatureClass.FindField("NAMEID")
            iPosSnrc = m_FeatureLayerBDG.FeatureClass.FindField("DATASET_NAME")
            iPosBDG_ID = m_FeatureLayerBDG.FeatureClass.FindField("BDG_ID")

            'Sortir si la classe d'erreurs est absente
            If m_FeatureCursorErreur Is Nothing Then Exit Sub

            'Créer un FeatureBuffer Point
            pFeatureBuffer = m_FeatureClassErreur.CreateFeatureBuffer

            'Définir la géométrie
            pFeatureBuffer.Shape = CType(pFeature.ShapeCopy, IGeometry)

            'Définir le numéro du lien
            pFeatureBuffer.Value(2) = iLien

            'Définir le DATASET_NAME
            pFeatureBuffer.Value(3) = pFeature.Value(iPosSnrc)

            'Définir le NAMEID_CTI
            pFeatureBuffer.Value(4) = pFeature.Value(iPosId)

            'Définir le OID_NAMED_FEATURE
            pFeatureBuffer.Value(5) = pFeature.Value(iPosOid)

            'Définir le NAME_CTI
            pFeatureBuffer.Value(6) = sNomToponyme

            'Définir la DECISION
            pFeatureBuffer.Value(9) = iDecision

            'Vérifier si un seul toponyme est présent
            If pSetToponyme IsNot Nothing Then
                'Vérifier si un seul toponyme est présent
                If pSetToponyme.Count = 1 Then
                    'Initialiser la recherche
                    pSetToponyme.Reset()
                    'Extraire le toponyme officiel
                    pToponyme = CType(pSetToponyme.Next, Toponyme)
                    'Définir le NAMEID_CGNDG
                    pFeatureBuffer.Value(7) = pToponyme.NameId

                    'Extraire le nom du toponyme officiel
                    'sNomToponymeOfficiel = ExtraireNomToponyme(pToponyme.NameId, qConnection)
                    sNomToponymeOfficiel = ExtraireNomToponyme(pToponyme.NameId)
                    'Vérifier si le nom officiel est présent
                    If sNomToponymeOfficiel IsNot Nothing Then
                        'Définir le NAME_CGNDG
                        pFeatureBuffer.Value(8) = sNomToponymeOfficiel
                    Else
                        'Définir la DECISION à 2:Détruire
                        pFeatureBuffer.Value(9) = 2
                    End If

                    'Définir le COMMENT
                    pFeatureBuffer.Value(10) = "Only one Toponym was found. / Seulement un toponyme a été trouvé. " & pFeature.Value(iPosSnrc).ToString & " / " & pToponyme.Snrc

                    'Vérifier si plusieurs toponymes sont présents
                ElseIf pSetToponyme.Count > 1 Then
                    'Initialiser la recherche
                    pSetToponyme.Reset()

                    'Traiter tous les toponymes
                    For i = 1 To pSetToponyme.Count
                        'Extraire le toponyme officiel
                        pToponyme = CType(pSetToponyme.Next, Toponyme)

                        'Sortir si le Snrc de l'élément BDG est le même que celui du Toponyme
                        If pFeature.Value(iPosSnrc).ToString = pToponyme.Snrc Then
                            'Définir le NAMEID_CGNDG
                            pFeatureBuffer.Value(7) = pToponyme.NameId

                            'Extraire le nom du toponyme officiel
                            'sNomToponymeOfficiel = ExtraireNomToponyme(pToponyme.NameId, qConnection)
                            sNomToponymeOfficiel = ExtraireNomToponyme(pToponyme.NameId)
                            'Vérifier si le nom officiel est présent
                            If sNomToponymeOfficiel IsNot Nothing Then
                                'Définir le NAME_CGNDG
                                pFeatureBuffer.Value(8) = sNomToponymeOfficiel
                            Else
                                'Définir la DECISION à 2:Détruire
                                pFeatureBuffer.Value(9) = 2
                            End If

                            'Sortir de la boucle puisque qu'on a trouvé le toponyme
                            Exit For
                        End If
                    Next

                    'Définir le COMMENT
                    pFeatureBuffer.Value(10) = pSetToponyme.Count.ToString & " Toponym was found. / " & pSetToponyme.Count.ToString & " toponymes ont été trouvés."
                End If
            End If

            'Définir le COMMENT
            'pFeatureBuffer.Value(10) = ""

            'Définir l'ACTION
            pFeatureBuffer.Value(11) = iAction

            'Définir le STATUS
            pFeatureBuffer.Value(12) = 0

            'Définir le BDG_ID
            pFeatureBuffer.Value(13) = pFeature.Value(iPosBDG_ID)

            'Insérer un nouvel élément dans la FeatureClass d'erreur
            m_FeatureCursorErreur.InsertFeature(pFeatureBuffer)

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pFeatureBuffer = Nothing
            sNomToponymeOfficiel = Nothing
            pToponyme = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet d'indiquer si l'identifiant et le nom du toponyme de la CGNDB est valide.
    '''</summary>
    ''' 
    '''<param name="sNameId"> Contient l'identifiant du toponyme officiel.</param>
    '''
    '''<returns>True si l'identifiant et le nom est valide, false sinon.</returns>
    ''' 
    Private Function ExtraireNomToponyme(ByVal sNameId As String) As String
        'Déclarer les variables de travail

        'Par défaut, ce n'est pas valide
        ExtraireNomToponyme = Nothing

        Try
            'Vérifier si l'identifiant est présent
            If m_ListeNomToponymeId.ContainsKey(sNameId) Then
                'Définir le nom du toponyme
                ExtraireNomToponyme = m_ListeNomToponymeId.Item(sNameId)
            End If

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'indiquer si l'identifiant et le nom du toponyme de la CGNDB est valide.
    '''</summary>
    ''' 
    '''<param name="sNameId"> Contient l'identifiant du toponyme officiel.</param>
    '''
    '''<returns>True si l'identifiant et le nom est valide, false sinon.</returns>
    ''' 
    Private Function ExtraireNomToponyme2(ByVal sNameId As String) As String
        'Déclarer les variables de travail
        Dim pQueryFilter As IQueryFilter = Nothing  'Interface contenant une requête attributive.
        Dim pCursor As ICursor = Nothing            'Interface utilisé pour lire les éléments.
        Dim pRow As IRow = Nothing                  'Interface contenant l'élément de toponyme officiel.

        'Par défaut, ce n'est pas valide
        ExtraireNomToponyme2 = Nothing

        Try
            'Interface pour créer une nouvelle requête
            pQueryFilter = New QueryFilter
            'Définir les attributs à extraire
            pQueryFilter.SubFields = "GEOGRAPHICAL_NAME"
            'Définir la requête
            pQueryFilter.WhereClause = "TOPONYMIC_FEATURE_ID='" & sNameId & "' AND STATUS_CODE_CL NOT IN (1193,1195,1196,1197,1200,1201)"

            'Interface pour extraire les noms de toponymes de la CGNDB
            pCursor = m_TableToponymeCGNDB.Table.Search(pQueryFilter, False)

            'Extraire le premier toponyme
            pRow = pCursor.NextRow

            'Vérifier si le toponyme est trouvé
            If pRow IsNot Nothing Then
                'Retourner le nom du toponyme
                ExtraireNomToponyme2 = pRow.Value(12).ToString
            End If

            'Release the update cursor to remove the lock on the input data.
            System.Runtime.InteropServices.Marshal.ReleaseComObject(pCursor)

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pQueryFilter = Nothing
            pCursor = Nothing
            pRow = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'extraire le nom du toponyme officiel.
    '''</summary>
    ''' 
    '''<param name="sNameId"> Contient l'identifiant du toponyme officiel.</param>
    '''<param name="qConnection"> Objet utilisé pour exécuter la requête SQL.</param>
    ''' 
    Private Function ExtraireNomToponyme(ByVal sNameId As String, ByRef qConnection As OleDbConnection) As String
        'Déclarer les variables de travail
        Dim sQueryString As String = Nothing        'Requête utilisée pour extraire un nom de toponyme.
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête.
        Dim sNomToponyme As String = Nothing        'contient le nom du toponyme correcpondant au NameId.

        'Définir la valeur par défaut
        ExtraireNomToponyme = Nothing

        Try
            'Définir la requête SQL pour extraire les toponymes officiels seulement
            sQueryString = "SELECT GEOGRAPHICAL_NAME" _
                         & "  FROM TOPONYMY_DBA.TOPONYM_6" _
                         & " WHERE TOPONYMIC_FEATURE_ID='" & sNameId & "'" _
                         & "   AND STATUS_CODE_CL NOT IN (1193,1195,1196,1197,1200,1201)"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, qConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire chaque ligne du résultat de la requête SQL
            While qReader.Read()
                'Définir le nom du toponyme
                sNomToponyme = qReader.GetValue(0).ToString
                'Sortir de la boucle
                Exit While
            End While

            'Fermer les curseurs
            qReader.Close()
            qCommand.Dispose()

            'Retourner le nom du toponyme
            Return sNomToponyme

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
            sNomToponyme = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'initialiser la barre de progression.
    ''' 
    '''<param name="iMin">Valeur minimum.</param>
    '''<param name="iMax">Valeur maximum.</param>
    '''<param name="pTrackCancel">Interface contenant la barre de progression.</param>
    ''' 
    '''</summary>
    '''
    Private Sub InitBarreProgression(ByVal iMin As Integer, ByVal iMax As Integer, ByRef pTrackCancel As ITrackCancel)
        'Déclarer les variables de travail
        Dim pStepPro As IStepProgressor = Nothing   'Interface qui permet de modifier les paramètres de la barre de progression.

        Try
            'sortir si le progressor est absent
            If pTrackCancel.Progressor Is Nothing Then Exit Sub

            'Interface pour modifier les paramètres de la barre de progression.
            pTrackCancel.Progressor = m_Application.StatusBar.ProgressBar
            pStepPro = CType(pTrackCancel.Progressor, IStepProgressor)

            'Changer les paramètres
            pStepPro.MinRange = iMin
            pStepPro.MaxRange = iMax
            pStepPro.Position = 0
            pStepPro.Show()

        Catch ex As Exception
            'Retourner l'erreur
            Throw ex
        Finally
            'Vider la mémoire
            pStepPro = Nothing
        End Try
    End Sub

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
        Dim sRepArcCatalog As String = ""                       'Nom du répertoire contenant les connexions des Géodatabase .sde.

        'Par défaut, aucune Géodatabase n'est retournée
        DefinirGeodatabase = Nothing

        Try
            'Valider le paramètre de la Geodatabase
            If sNomGeodatabase.Length > 0 Then
                'Extraire le nom du répertoire contenant les connexions des Géodatabase .sde.
                sRepArcCatalog = IO.Directory.GetDirectories(Environment.GetEnvironmentVariable("APPDATA"), "ArcCatalog", IO.SearchOption.AllDirectories)(0)

                'Redéfinir le nom complet de la Géodatabase .sde
                sNomGeodatabase = sNomGeodatabase.ToLower.Replace("database connections", sRepArcCatalog)

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
            Throw ex
        Finally
            'Vider la mémoire
            pFactoryType = Nothing
            pWorkspaceFactory = Nothing
        End Try
    End Function

    '''<summary>
    '''Fonction qui permet de convertir une FeatureClass d'un format vers un autre format.
    '''
    '''<param name="pSourceClass">Interface contenant la featureClass de départ.</param>
    '''<param name="pTargetWorkspace">Interface contenant la géodatabase d'arrivée.</param>
    '''<param name="sTargetName">Nom de la featureClass d'arrivée.</param>
    ''' 
    ''' <return>IEnumInvalidObject contenant les éléments invalides qui n'ont pas été transférés.</return>
    ''' 
    '''</summary>
    '''
    Private Function ConvertFeatureClass(ByVal pSourceClass As IFeatureClass, ByVal pTargetWorkspace As IWorkspace2, _
                                         ByVal sTargetName As String) As IEnumInvalidObject
        'Définir les variables de travail
        Dim pSourceDataset As IDataset = Nothing                    'Interface pour extraire le nom complet de la classe de départ.
        Dim pSourceFeatureClassName As IFeatureClassName = Nothing  'Interface pour ouvrir la classe de départ.
        Dim pSourceFields As IFields = Nothing                      'Interface contenant les attribut de la classe de départ.
        Dim pShapeField As IField = Nothing                         'Interface contenant l'attribut de la géométrie.
        Dim pTargetWorkspaceDataset As IDataset = Nothing           'Interface pour extraire le nom complet de la géodatabase d'arrivée.
        Dim pTargetWorkspaceName As IWorkspaceName = Nothing        'Interface pour ouvrir la géodatabase d'arrivée.
        Dim pTargetFeatureClassName As IFeatureClassName = Nothing  'Interface pour ouvrir la classe d'arrivée.
        Dim pTargetDatasetName As IDatasetName = Nothing            'Interface pour définir le Worspace d'arrivée.
        Dim pFieldChecker As IFieldChecker = Nothing                'Interface pour valider les attributs de la classe d'arrivée.
        Dim pTargetFields As IFields = Nothing                      'Interface contenant les attributs de la classe d'arrivée.
        Dim pEnumFieldError As IEnumFieldError = Nothing            'Interface contenant les attributs de la classe d'arrivée en erreur.
        Dim pGeometryDef As IGeometryDef = Nothing                  'Interface contenant la définition de l'attribut géométrie de la classe de départ.
        Dim pGeometryDefClone As IClone = Nothing                   'Interface utilisé pour cloner l'attribut géométrie de la classe de départ.
        Dim pTargetGeometryDefClone As IClone = Nothing             'Interface contenant l'attribut géométrie de la classe d'arrivée.
        Dim pTargetGeometryDef As IGeometryDef = Nothing            'Interface contenant la définition de la classe d'arrivée
        Dim pFeatureDataConverter As IFeatureDataConverter = Nothing 'Interface utilisé pour convertir une classe de départ vers une classe d'arrivée.
        Dim pFeatureWorkspace As IFeatureWorkspace = Nothing        'Interface pour ouvrir la FeatureClass existante
        Dim pDataset As IDataset = Nothing                          'Interface pour détruire la FeatureClass existante

        'Définir le résultat par défaut
        ConvertFeatureClass = Nothing

        Try
            'Interface pour extraire le nom complet de la classe de départ
            pSourceDataset = CType(pSourceClass, IDataset)
            'Interface pour ouvrir la classe de départ
            pSourceFeatureClassName = CType(pSourceDataset.FullName, IFeatureClassName)
            'Interface contenant les attribut de la classe de départ
            pSourceFields = pSourceClass.Fields
            'Interface contenant l'attribut de la géométrie
            pShapeField = pSourceFields.Field(pSourceFields.FindField(pSourceClass.ShapeFieldName))

            'Le nom de la FeatureClass ne doit pas dépasser 52
            If sTargetName.Length > 52 Then sTargetName = sTargetName.Substring(0, 52)
            'Interface pour extraire le nom complet de la géodatabase d'arrivée.
            pTargetWorkspaceDataset = CType(pTargetWorkspace, IDataset)
            'Interface pour ouvrir la géodatabase d'arrivée.
            pTargetWorkspaceName = CType(pTargetWorkspaceDataset.FullName, IWorkspaceName)
            'Interface pour ouvrir la classe d'arrivée.
            pTargetFeatureClassName = New FeatureClassNameClass()
            'Interface pour définir le Worspace d'arrivée.
            pTargetDatasetName = CType(pTargetFeatureClassName, IDatasetName)
            'Définir le nom de la Géodatabase d'arrivée
            pTargetDatasetName.Name = sTargetName
            'Définir le workspaceName d'arrivée
            pTargetDatasetName.WorkspaceName = pTargetWorkspaceName

            'Interface pour valider les attributs de la classe d'arrivée
            pFieldChecker = New FieldCheckerClass With _
                                                { _
                                                .InputWorkspace = pSourceDataset.Workspace, _
                                                .ValidateWorkspace = CType(pTargetWorkspace, IWorkspace) _
                                                }

            'Valider et définir les attributs de la classe d'arrivée
            pFieldChecker.Validate(pSourceClass.Fields, pEnumFieldError, pTargetFields)

            'Interface contenant la définition de la géométrie
            pGeometryDef = pShapeField.GeometryDef
            'Interface utilisé pour cloner l'attribut géométrie de la classe de départ
            pGeometryDefClone = CType(pGeometryDef, IClone)
            'Cloner l'attribut géométrie de la classe de départ pour la classe d'arrivée
            pTargetGeometryDefClone = pGeometryDefClone.Clone()
            'Interface contenant la définition de la classe d'arrivée
            pTargetGeometryDef = CType(pTargetGeometryDefClone, IGeometryDef)

            'Vérifier si la classe est déja présente
            If pTargetWorkspace.NameExists(esriDatasetType.esriDTFeatureClass, sTargetName) Then
                'Envoyer une erreur
                Throw New Exception("ERREUR : La classe existe déjà : " & sTargetName)
            End If

            'Instancier un objet pour convertir une classe
            pFeatureDataConverter = New FeatureDataConverterClass()
            'Convertir la FeatureClass en mémoire sur disque
            ConvertFeatureClass = pFeatureDataConverter.ConvertFeatureClass(pSourceFeatureClassName, Nothing, Nothing, _
                                                                            pTargetFeatureClassName, pTargetGeometryDef, pTargetFields, _
                                                                            Nothing, 1000, 0)

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            pSourceDataset = Nothing
            pSourceFeatureClassName = Nothing
            pSourceFields = Nothing
            pShapeField = Nothing
            pTargetWorkspaceDataset = Nothing
            pTargetWorkspaceName = Nothing
            pTargetFeatureClassName = Nothing
            pTargetDatasetName = Nothing
            pFieldChecker = Nothing
            pTargetFields = Nothing
            pEnumFieldError = Nothing
            pGeometryDef = Nothing
            pGeometryDefClone = Nothing
            pTargetGeometryDefClone = Nothing
            pTargetGeometryDef = Nothing
            pFeatureWorkspace = Nothing
            pDataset = Nothing
            pFeatureDataConverter = Nothing
        End Try
    End Function
#End Region
End Module
