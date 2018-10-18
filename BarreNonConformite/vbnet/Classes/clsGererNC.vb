Imports System.Data.OleDb
Imports System.Windows.Forms
Imports ESRI.ArcGIS.esriSystem

'**
'Nom de la composante : clsGererNC.vb
'
'''<summary>
''' Librairie de Classe qui permet de gérer l'information des non-conformités dans la Base de données SIB.
'''</summary>
'''
'''<remarks>
'''Cette librairie est utilisable pour les outils interactifs ou Batch dans ArcMap (ArcGis de ESRI).
'''
'''Auteur : Michel Pothier
'''Date : 21 février 2017
'''</remarks>
''' 
Public Class clsGererNC
    'Déclarer les variables globales
    '''<summary>Nom de l'environnement de travail (instance de la BD) [SIB_PRO/SIB_TST/SIB_DEV/BDG_SIB_TST].</summary>
    Protected gsEnv As String = "SIB_PRO"
    '''<summary>Type de produit pour lesquels on veut gérer les non-conformités.</summary>
    Protected gsTypeProduit As String = "BDG"
    '''<summary>Type de travail pour lesquels on veut corriger les non-conformités.</summary>
    Protected gsTypeTravail As String = "COR-NC"
    '''<summary>Objet contenant la connexion à la base de données SIB.</summary>
    Protected gqConnection As OleDbConnection = Nothing
    '''<summary> Interface pour annuler le traitement et afficher l'information.</summary>
    Protected gpTrackCancel As ITrackCancel = Nothing

#Region "Propriétés"
    '''<summary>
    ''' Propriété qui permet de définir et retourner l'environnement de travail (instance de la BD).
    '''</summary>
    ''' 
    Public Property Env() As String
        Get
            Env = gsEnv
        End Get
        Set(value As String)
            'Définir l'environnment
            gsEnv = value

            'Fermer la connxion à la BD de SIB
            If gqConnection IsNot Nothing Then gqConnection.Close()

            'Créer une nouvelle connexion à la BD de SIB
            gqConnection = New OleDbConnection(ConnectionString)

            'Ouvrir la connexion à la BD de SIB
            gqConnection.Open()
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner le type de produit.
    '''</summary>
    ''' 
    Public Property TypeProduit() As String
        Get
            TypeProduit = gsTypeProduit
        End Get
        Set(ByVal value As String)
            gsTypeProduit = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le type de travail.
    '''</summary>
    ''' 
    Public ReadOnly Property TypeTravail() As String
        Get
            TypeTravail = gsTypeTravail
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le texte de connexion à la Bd des catalogues.
    '''</summary>
    ''' 
    Public ReadOnly Property ConnectionString() As String
        Get
            'Définir le texte de connexion à la BD des catalogues
            ConnectionString = ""

            'Vérifier l'environnement spécifié
            If gsEnv = "SIB_PRO" Then
                'Définir le texte de connexion à la BD des catalogues
                ConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=" & gsEnv & ";" & "User Id=sibdba;" & "Password=ncdintel;"
            ElseIf gsEnv = "SIB_TST" Then
                'Définir le texte de connexion à la BD des catalogues
                ConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=" & gsEnv & ";" & "User Id=sibdba;" & "Password=sibdba;"
            ElseIf gsEnv = "SIB_DEV" Then
                'Définir le texte de connexion à la BD des catalogues
                ConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=" & gsEnv & ";" & "User Id=sibdba;" & "Password=sibdba;"
            ElseIf gsEnv = "BDG_SIB_TST" Then
                'Définir le texte de connexion à la BD des catalogues
                ConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=" & gsEnv & ";" & "User Id=sibdba;" & "Password=sibdba;"
            End If
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner l'interface pour annuler le traitement et afficher l'information.
    '''</summary>
    ''' 
    Public Property TrackCancel() As ITrackCancel
        Get
            TrackCancel = gpTrackCancel
        End Get
        Set(ByVal value As ITrackCancel)
            gpTrackCancel = value
        End Set
    End Property
#End Region

#Region "Routines et fonctions d'intialisation"
    '''<summary>
    '''Routine qui permet d'initialiser la classe pour gérer l'information des non-conformités.
    '''</summary>
    ''' 
    '''<param name="sEnv">Environnement de travail.</param>
    '''<param name="sTypeProduit">Type de produit.</param>
    '''<param name="sTypeTravail">Type de travail.</param>
    '''
    Public Sub New(Optional ByVal sEnv As String = "SIB_PRO", Optional ByVal sTypeProduit As String = "BDG", Optional ByVal sTypeTravail As String = "COR-NC")
        Try
            'Définir l'environnement
            gsEnv = sEnv.ToUpper
            'Définir le type de produit
            gsTypeProduit = sTypeProduit.ToUpper
            'Définir le type de travail
            gsTypeTravail = sTypeTravail.ToUpper

            'Créer une nouvelle connexion à la BD de SIB
            gqConnection = New OleDbConnection(ConnectionString)

            'Ouvrir la connexion à la BD de SIB
            gqConnection.Open()

        Catch ex As Exception
            Throw
        End Try
    End Sub

    '''<summary>
    '''Routine qui permet de fermer adéquatement l'objet pour gérer l'information des non-conformités.
    '''</summary>
    ''' 
    Protected Overrides Sub Finalize()
        ''Fermer la connxion à la BD de SIB
        'If gqConnection IsNot Nothing Then
        '    If gqConnection.State = ConnectionState.Open Then
        '        gqConnection.Close()
        '    End If
        'End If

        'Vider la mémoire
        gsEnv = Nothing
        gsTypeProduit = Nothing
        gsTypeTravail = Nothing
        gqConnection = Nothing
        gpTrackCancel = Nothing
        'Finaliser
        MyBase.Finalize()
    End Sub

    '''<summary>
    ''' Permet d'indiquer si l'outil de gestion des NCs est valide.
    '''</summary>
    ''' 
    '''<returns>"Boolean" pour indiquer si l'outil de gestion des NCs est valide (True) ou invalide (False).</returns>
    ''' 
    Public Function EstValide() As Boolean
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Indique que le catalogue est invalide par défaut
        EstValide = True

        Try
            '-------------------------------------------------------
            'Définir la requête SQL de validation du type de produit
            sQueryString = "SELECT count(TY_PRODUIT)" _
                         & "  FROM F000_PR" _
                         & " WHERE TY_PRODUIT='" & gsTypeProduit & "'"
            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)
            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()
            'Lire le résultat de la requête SQL
            qReader.Read()
            'Vérifier si un résultat est présent
            If CInt(qReader.GetValue(0)) = 0 Then
                'Indique que l'outil de gestion des NC est invalide
                EstValide = False
            End If
            'Fermer l'objet de lecture
            qReader.Close()

            '-------------------------------------------------------
            'Définir la requête SQL de validation du type de travail
            sQueryString = "SELECT count(TY_TRAV)" _
                         & "  FROM F105_ET" _
                         & " WHERE TY_TRAV='" & gsTypeTravail & "'" _
                         & "   AND TY_PRODUIT='" & gsTypeProduit & "'"
            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)
            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()
            'Lire le résultat de la requête SQL
            qReader.Read()
            'Vérifier si un résultat est présent
            If CInt(qReader.GetValue(0)) = 0 Then
                'Indique que l'outil de gestion des NC est invalide
                EstValide = False
            End If
            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function
#End Region

#Region "Routines et fonctions publiques"
    '''<summary>
    ''' Fonction qui permet de créer un dictionnaire des environnements de travail.
    '''</summary>
    ''' 
    '''<returns>"Dictionary(Of String, String)" correspondant à la liste des environnements possibles (Env, Env).</returns>
    ''' 
    Public Function CreerDictionaireEnv() As Dictionary(Of String, String)
        'Définir la valeur de retour par défaut
        CreerDictionaireEnv = New Dictionary(Of String, String)

        Try
            'Ajouter l'environnement de production
            CreerDictionaireEnv.Add("SIB_PRO", "SIB_PRO")
            'Ajouter l'environnement de test
            CreerDictionaireEnv.Add("SIB_TST", "SIB_TST")
            'Ajouter l'environnement de développement
            CreerDictionaireEnv.Add("SIB_DEV", "SIB_DEV")
            'Ajouter l'environnement de test de production BDG
            CreerDictionaireEnv.Add("BDG_SIB_TST", "BDG_SIB_TST")

        Catch erreur As Exception
            Throw
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de créer un dictionnaire des types de produit.
    '''</summary>
    ''' 
    '''<returns>"Dictionary(Of String, String)" correspondant à la liste des types de produit possibles (TypeProduit, TypeProduit).</returns>
    ''' 
    Public Function CreerDictionaireTypeProduit() As Dictionary(Of String, String)
        'Définir la valeur de retour par défaut
        CreerDictionaireTypeProduit = New Dictionary(Of String, String)

        Try
            'Ajouter le type de produit BDG
            CreerDictionaireTypeProduit.Add("BDG", "BDG")
            'Ajouter le type de produit RHN
            CreerDictionaireTypeProduit.Add("RHN", "RHN")

        Catch erreur As Exception
            Throw
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de créer un dictionnaire des numéros de non-conformité dont l'édition de fin est 99999 selon un type de produit.
    '''</summary>
    ''' 
    '''<returns>"Dictionary(Of String, Integer)" correspondant à la liste des numéros de non-conformité avec son type et sa description.</returns>
    ''' 
    Public Function CreerDictionnaireNoNC() As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur de retour par défaut
        CreerDictionnaireNoNC = New Dictionary(Of String, String)

        Try
            'Définir la requête SQL
            sQueryString = "SELECT DISTINCT A.NO_NC, B.TY_PRODUIT, A.TY_NC, A.TITRE" _
                         & "  FROM F702_NC A, F705_PR B" _
                         & " WHERE A.DATE_TRAITEMENT IS NULL AND A.NO_NC=B.NO_NC AND B.TY_PRODUIT='" & gsTypeProduit & "' AND B.ED_FIN=99999 ORDER BY NO_NC"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire chaque ligne du résultat de la requête SQL
            While qReader.Read()
                'Ajouter le numéro de non-conformité
                CreerDictionnaireNoNC.Add(qReader.GetValue(0).ToString, _
                                      "Produit=" & qReader.GetString(1) & ", Type=" & qReader.GetString(2) & ", Titre=" & qReader.GetString(3))
            End While

            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de créer un dictionnaire des identifiants de non-conformité selon un numéro de non-conformité. 
    ''' Le numéro d'édition/Version de début et de fin et le nombre de classes seront contenus dans la descroption.
    '''</summary>
    ''' 
    '''<param name="sNoNC">Numéro de non-conformité.</param>
    ''' 
    '''<returns>"Dictionary(Of String, String)" correspondant à la liste des identifiants du numéro de non-conformité spécifié.</returns>
    ''' 
    Public Function CreerDictionnaireIdentifiantsNoNC(ByVal sNoNC As String) As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur de retour par défaut
        CreerDictionnaireIdentifiantsNoNC = New Dictionary(Of String, String)

        Try
            'Définir la requête SQL
            'sQueryString = "SELECT A.IDENTIFIANT, A.ED_DEBUT, A.VER_DEBUT, A.ED_FIN, A.VER_FIN, COUNT(C.CD_ELEM_TOPO)" _
            '             & "  FROM F705_PR A, F502_PS B, F502_LE C" _
            '             & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.NO_NC='" & sNoNC & "'" _
            '             & "   AND B.NO_MAP=C.NO_MAP(+)" _
            '             & "   AND A.IDENTIFIANT=B.IDENTIFIANT(+) AND A.TY_PRODUIT=B.TY_PRODUIT(+) AND B.E_PLSNRC(+)='P'" _
            '             & " GROUP BY A.IDENTIFIANT, A.ED_DEBUT, A.VER_DEBUT, A.ED_FIN, A.VER_FIN" _
            '             & " ORDER BY IDENTIFIANT"
            sQueryString = "SELECT A.IDENTIFIANT, A.ED_DEBUT, A.VER_DEBUT, A.ED_FIN, A.VER_FIN, A.TY_PRODUIT, B.NO_MAP, B.E_PLSNRC, B.NB_CLASSE" _
                         & "  FROM F705_PR A, " _
                         & "       (SELECT BB.IDENTIFIANT,BB.E_PLSNRC,CC.NO_MAP,COUNT(CD_ELEM_TOPO) AS NB_CLASSE FROM F502_PS BB, F502_NC CC, F502_LE DD  WHERE CC.NO_NC='" & sNoNC & "' AND BB.NO_MAP=CC.NO_MAP AND CC.NO_MAP=DD.NO_MAP GROUP BY BB.IDENTIFIANT,BB.E_PLSNRC,CC.NO_MAP) B" _
                         & " WHERE A.NO_NC='" & sNoNC & "' AND A.IDENTIFIANT=B.IDENTIFIANT(+)" _
                         & " ORDER BY IDENTIFIANT"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire chaque ligne du résultat de la requête SQL
            While qReader.Read()
                'Ajouter l'identifiant dans le dictionnaire résultant
                CreerDictionnaireIdentifiantsNoNC.Add(qReader.GetString(0), _
                                                     "Ed.Ver_Début=" & qReader.GetValue(1).ToString & "." & qReader.GetValue(2).ToString & _
                                                     ", Ed.Ver_Fin=" & qReader.GetValue(3).ToString & "." & qReader.GetValue(4).ToString & _
                                                     ", TypeProduit=" & qReader.GetValue(5).ToString & _
                                                     ", NoMap=" & qReader.GetValue(6).ToString & _
                                                     ", Etat=" & qReader.GetValue(7).ToString & _
                                                     ", NbClasses=" & qReader.GetValue(8).ToString)
            End While

            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de créer un dictionnaire des codes de classes en production à partir d'un numéro de mise au programme.
    '''</summary>
    ''' 
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    ''' 
    '''<returns>"Dictionary(Of String, String)" correspondant à la liste des identifiants du numéro de non-conformité spécifié.</returns>
    ''' 
    Public Function CreerDictionnaireCodeClasseEnProduction(ByVal sNoMap As String) As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur de retour par défaut
        CreerDictionnaireCodeClasseEnProduction = New Dictionary(Of String, String)

        Try
            'Définir la requête SQL pour retourner les classes d'un identifiant en production
            sQueryString = "SELECT B.CD_ELEM_TOPO" _
                         & "  FROM F502_PS A, F502_LE B" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.NO_MAP=" & sNoMap & "' AND A.E_PLSNRC='P'" _
                         & "   AND A.NO_MAP=B.NO_MAP" _
                         & " ORDER BY B.CD_ELEM_TOPO"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire chaque ligne du résultat de la requête SQL
            While qReader.Read()
                'Ajouter le code de classe en production
                CreerDictionnaireCodeClasseEnProduction.Add(qReader.GetString(0), qReader.GetString(0))
            End While

            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de créer un dictionnaire des classes possibles contenues dans la BD des catalogues.
    '''</summary>
    ''' 
    '''<returns>"Collection" correspondant à la liste des classes possibles (codeClasse, nomClasse).</returns>
    ''' 
    Public Function CreerDictionaireClasses() As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim qConnection As OleDbConnection = Nothing    'Objet utilisé pour se connecter à la BD des catalogues.
        Dim qCommand As OleDbCommand = Nothing          'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing        'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing            'Requête SQL utilisée.
        Dim sTypeCatalogue As String = "1"              'Type de catalogue utilisé selon le type de produit (1=BDG, 2=GEOBASE)

        'Définir la valeur de retour par défaut
        CreerDictionaireClasses = New Dictionary(Of String, String)

        Try
            'Créer une nouvelle connexion à la BD de SIB
            qConnection = New OleDbConnection("PROVIDER=MSDAORA;" & "DATA SOURCE=CATREL_PRO;" & "User Id=bdg_view;" & "Password=bdg_view;")

            'Ouvrir la connexion à la BD de SIB
            qConnection.Open()

            'Vérifier si le type de produit est RHN, le type de catalogue est GEOBASE
            If gsTypeProduit = "RHN" Then sTypeCatalogue = "2"

            'Définir la requête SQL
            sQueryString = "SELECT DISTINCT B.FEAT_TYPE_CODE_BD, B.FEAT_TYPE_NAME_DATABASE" _
                         & "  FROM FEAT_CATALOGUE A, FEAT_TYPE B" _
                         & " WHERE A.FEAT_CATAL_TYPE=" & sTypeCatalogue _
                         & "   AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK" _
                         & "   AND B.FEAT_TYPE_CODE_BD LIKE '%000_'" _
                         & "   AND B.FEAT_TYPE_NAME_DATABASE IS NOT NULL" _
                         & " ORDER BY B.FEAT_TYPE_NAME_DATABASE"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, qConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire chaque ligne du résultat de la requête SQL
            While qReader.Read()
                'Ajouter la classe
                CreerDictionaireClasses.Add(qReader.GetValue(0).ToString, qReader.GetString(1))
            End While

            'Fermer l'objet de lecture
            qReader.Close()

            'Ouvrir la connexion à la BD de SIB
            qConnection.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Fermer l'objet de connexion
            If qConnection IsNot Nothing Then qConnection.Close()
            'Vider la mémoire
            qConnection = Nothing
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la DESCRIPTION d'un numéro de non-conformité spécifié.
    '''</summary>
    ''' 
    '''<param name="sNoNC">Numéro de non-conformité.</param>
    ''' 
    '''<returns>"String" correspondant à la description du numéro de non-conformité spécifié.</returns>
    ''' 
    Public Function ExtraireDescriptionNoNC(ByVal sNoNC As String) As String
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur de retour par défaut
        ExtraireDescriptionNoNC = ""

        Try
            'Définir la requête SQL
            sQueryString = "SELECT DESCR" _
                         & "  FROM F702_NC" _
                         & " WHERE NO_NC='" & sNoNC & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire la ligne du résultat de la requête SQL
            qReader.Read()

            'Définir la description
            ExtraireDescriptionNoNC = qReader.GetString(0)

            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de remplir l'information des identifiants d'une non-conformatité dans un TreeView.
    '''</summary>
    ''' 
    '''<param name="sNoNc">Contient le numéro de non-conformité.</param>
    '''<param name="treIdentifiants">TreeView dans lequel l'information des identifiants d'un numéro de non-conformité sera ajouté.</param>
    ''' 
    Public Sub DefinirInfoIdentifiantsNC(ByVal sNoNc As String, ByRef treIdentifiants As TreeView)
        'Déclarer les variables de travail
        Dim pId As KeyValuePair(Of String, String) = Nothing    'Contient un identifiant avec son édition et version de début et fin.
        Dim pNode As TreeNode = Nothing     'Contient un noeud de TreeView.
        Dim bId = False                     'Permet d'indiquer si un identifiant a été identifié.

        Try
            'Débuter la mise à jour du TreeView
            treIdentifiants.BeginUpdate()

            'Initialiser les identifiants de la non-conformité spécifiée
            treIdentifiants.Nodes.Clear()

            'Initialiser le nombre d'identifiants sélectionnés
            m_NbIdentifiants = 0

            'Définir tous les identifiants du numéro de non-conformité
            For Each pId In m_GererNC.CreerDictionnaireIdentifiantsNoNC(sNoNc)
                'Ajouter l'identifiant du numéro de non-conformité (pId.Key, pId.Value)
                pNode = treIdentifiants.Nodes.Add(pId.Key, pId.Key & " : " & pId.Value)

                ''Vérifier si l'identifiant n'a pas été traité
                'If pId.Value.Contains("99999") And Not bId Then
                '    'Indiquer que l'identifiant n'a pas été traité
                '    pNode.Checked = True
                '    bId = True
                'End If
            Next

        Catch ex As Exception
            'Message d'erreur
            Throw
        Finally
            'Terminer la mise à jour du TreeView
            treIdentifiants.EndUpdate()
            'Vider la mémoire
            pId = Nothing
            pNode = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de définir l'information pour les classes qui sont mises au programme et qui sont en production pour un noeud d'identifiant de TreeView.
    '''</summary>
    ''' 
    '''<param name="qNodeIdentifiant">Noeud d'un identifiant à traiter.</param>
    ''' 
    Public Sub DefinirInfoClassesProduction(ByRef qNodeIdentifiant As TreeNode)
        'Déclarer les variables de travail
        Dim qListeClasses As Dictionary(Of String, String)  'Dictionnaire contenant la liste des classes.
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        Try
            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Afficher les classes en production de l'identifiant : " & qNodeIdentifiant.Name

            'Initialiser les noeuds de l'identifiant
            qNodeIdentifiant.Nodes.Clear()

            'Définir le dictionnaire des classes
            qListeClasses = Me.CreerDictionaireClasses()

            'Définir la requête SQL
            sQueryString = "SELECT C.TY_TRAV, A.NO_MAP, B.CD_ELEM_TOPO" _
                         & "  FROM F502_PS A, F502_LE B, F503_TR C" _
                         & " WHERE TY_PRODUIT='" & gsTypeProduit & "' AND IDENTIFIANT='" & qNodeIdentifiant.Name & "' AND TY_TRAV='COR-NC'" _
                         & "   AND A.NO_MAP=B.NO_MAP AND A.NO_MAP=C.NO_MAP(+)" _
                         & " ORDER BY C.TY_TRAV, A.NO_MAP, B.CD_ELEM_TOPO"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire chaque ligne du résultat de la requête SQL
            While qReader.Read()
                'Ajouter la classe dans le noeud de l'identifiant
                qNodeIdentifiant.Nodes.Add(qReader.GetValue(0).ToString & ":" & qReader.GetValue(1).ToString & ":" & qReader.GetValue(2).ToString, _
                                           "TY_TRAV=" & qReader.GetValue(0).ToString _
                                           & ", NO_MAP=" & qReader.GetValue(1).ToString _
                                           & ", Classe=" & qReader.GetValue(2).ToString & ":" & qListeClasses.Item(qReader.GetValue(2).ToString))
            End While

            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qListeClasses = Nothing
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de réserver tous les identifiants sélectionnés d'un TreeView d'identifiants pour toutes les classes sélectionnées d'un TreeView de classes
    ''' selon un numéro de non-conformité.
    '''</summary>
    ''' 
    '''<param name="sNoNC">Contient le numéro de non-conformité.</param>
    '''<param name="treIdentifiants">TreeView contenant les identifiants à réserver.</param>
    '''<param name="treClasses">TreeView contenant les classes à réserver.</param>
    ''' 
    '''<remarks>
    '''Le traitement de réservation permet d'effectuer les étapes suivantes :
    ''' -Pour chaque identifiant sélectionné:
    '''   -Si l'identifiant n'est pas au programme
    '''     -Créer un nouveau NO_MAP.
    '''     -Ajouter l'info du NO_MAP dans la table F502_PS.
    '''     -Ajouter le lien le NO_MAP avec le NO_NC dans la table F502_NC.
    '''     -Ajouter le lien le NO_MAP avec le TY_TRAV dans la table F503_TR.
    '''     -Pour chaque classe sélectionnée:
    '''       -Ajouter le code de classe avec le NO_MAP dans la table F502_LE.
    '''</remarks>
    ''' 
    Public Sub ReserverIdentifiantsClasses(ByVal sNoNC As String, ByRef treIdentifiants As TreeView, ByRef treClasses As TreeView)
        'Déclarer les variables de travail
        Dim qListeClasses As Dictionary(Of String, String)  'Dictionnaire contenant la liste des classes.
        Dim qNodeClasse As TreeNode = Nothing       'Noeud d'un TreeView contenant une classe.
        Dim qNodeIdentifiant As TreeNode = Nothing  'Noeud d'un TreeView contenant un identifiant.
        Dim sListeCodesClasses As String = Nothing  'Contient la liste des codes de classes à réserver.
        Dim sUsager As String = Nothing             'Contient le nom de l'usager par défaut.
        Dim sNote As String = Nothing               'Contient le note par défaut.
        Dim sNormes As String = Nothing             'Contient le numéro des normes par défaut.
        Dim sDatePrevue As String = Nothing         'Contient la date prévue par défaut.
        Dim sCodeClasse As String = Nothing         'Contient le code de classe.
        Dim iNoMap As Integer = 0                   'Contient le no_map.

        Try
            'Définir le nom de l'usager
            sUsager = System.Environment.GetEnvironmentVariable("USERNAME").ToUpper

            'Vérifier si l'accès à SIB n'est pas autorisé
            If Not AccesAutoriser(sUsager, "PROD-RSP") Then
                'Retourner une erreur d'accès non autorisé
                Throw New AnnulerExecutionException("ERREUR : Accès non autorisé : Usager=" & sUsager & ", Groupe=PROD-RSP")
            End If

            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Début du traitement de réservation des identifiants et des classes !"

            'Définir la date prévue de la mise au programme (NOW + 2 jours)
            sDatePrevue = DateAdd(DateInterval.Day, 2, Date.Now).ToString.Substring(0, 10)

            'Définir la note de la mise au programme
            sNote = "#" & gsTypeTravail & "=" & sNoNC

            'Définir le dictionnaire des classes
            qListeClasses = Me.CreerDictionaireClasses()

            'Extraire le numéro des normes par défaut
            sNormes = ExtraireNormesDefaut()

            'Définir la liste des codes des classes contenus dans un TreeView de classes.
            sListeCodesClasses = DefinirListeCodesClasses(treClasses)

            'Traiter tous les identifiants
            For Each qNodeIdentifiant In treIdentifiants.Nodes
                'Vérifier si l'identifiant est sélectionné
                If qNodeIdentifiant.Checked Then
                    'Afficher l'information de fin de traitement
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Réservation de l'identifiant : " & qNodeIdentifiant.Name & " ..."

                    'Vider le contenu du noeud de l'identifiant
                    qNodeIdentifiant.Nodes.Clear()

                    'Vérifier si l'édition de fin de l'identifiant de non-conformité est inconnue (99999)
                    If qNodeIdentifiant.Text.Contains("99999") Then
                        'Vérifier la présence de classes en production pour l'identifiant
                        If NbClassesIdentifiantEnProduction(qNodeIdentifiant.Name, sListeCodesClasses) > 0 Then
                            'Ajouter les classes de l'identifiant en production
                            Call DefinirInfoClassesProduction(qNodeIdentifiant)

                            'Si aucune classe de l'identifiant n'est en production
                        Else
                            Try
                                'Extraire le no_map
                                iNoMap = CreerNouveauNoMap()

                                'Ajouter l'information du NO_MAP dans la table F502_PS
                                Call InsererInfoNoMapTableF502_PS(sUsager, iNoMap.ToString, qNodeIdentifiant.Name, sNote, sDatePrevue, sNormes)

                                'Ajouter un lien entre le NO_NC et le NO_MAP dans la table F502_NC
                                Call InsererLienNoNcNoMapTableF502_NC(sUsager, iNoMap.ToString, sNoNC)

                                'Ajouter un lien entre le TY_TRAV et le NO_MAP dans la table F503_TR
                                Call InsererLienTyTravNoMapTableF503_TR(sUsager, iNoMap.ToString)

                                'Traiter toutes les classes
                                For Each qNodeClasse In treClasses.Nodes
                                    'Vérifier si la classe est sélectionnée
                                    If qNodeClasse.Checked Then
                                        ''Afficher l'information de fin de traitement
                                        'If gpTrackCancel.Progressor IsNot Nothing Then
                                        '    gpTrackCancel.Progressor.Message = "Réservation de l'identifiant : " & qNodeIdentifiant.Name & ", Classe : " & qNodeClasse.Text
                                        'End If

                                        'Ajouter le lien entre le code de classe et le NO_NC dans la table F502_LE
                                        Call InsererLienCodeClasseNoMapTableF502_LE(sUsager, iNoMap.ToString, qNodeClasse.Name)

                                        'Ajouter le type de travail, le numéro de mise au programme et la classe dans le noeud de l'identifiant
                                        qNodeIdentifiant.Nodes.Add(gsTypeTravail & ":" & iNoMap.ToString & ":" & qNodeClasse.Name, _
                                                                   "TY_TRAV=" & gsTypeTravail & ", NO_MAP=" & iNoMap.ToString & _
                                                                   ", Classe=" & qNodeClasse.Name & ":" & qListeClasses.Item(qNodeClasse.Name))
                                    End If
                                Next

                            Catch ex As Exception
                                'Commande pour refuser la modification
                                Call Rollback()
                                'Retourner l'erreur
                                Throw
                            End Try

                            'Commande pour accepter la modification
                            Call Commit()

                            'Modifier le nombre de classes
                            'qNodeIdentifiant.Text = qNodeIdentifiant.Text.Replace("NbClasses=0", "NbClasses=" & qNodeIdentifiant.Nodes.Count.ToString)
                            qNodeIdentifiant.Text = qNodeIdentifiant.Text.Substring(0, qNodeIdentifiant.Text.LastIndexOf("NoMap=")) & "NoMap=" & iNoMap.ToString & ", Etat=P, NbClasses=" & qNodeIdentifiant.Nodes.Count.ToString
                        End If

                        'Si l'édition de fin de l'identifiant de non-conformité est connue
                    Else
                        'L'identifiant ne peut pas être réservé car il a déjà été traité
                        qNodeIdentifiant.Nodes.Add("ERREUR", "ERREUR : L'identifiant ne peut pas être réservé car il a déjà été traité !")
                        'Désélectionner le noeud
                        qNodeIdentifiant.Checked = False
                        'Ouvrir le noeud
                        qNodeIdentifiant.Expand()
                    End If
                End If
            Next

            'Ouvrir tous les noeuds
            treIdentifiants.ExpandAll()

            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement de réservation des identifiants et des classes !"

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            qListeClasses = Nothing
            qNodeClasse = Nothing
            qNodeIdentifiant = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'annuler la réservation de tous les identifiants sélectionnés d'un TreeView d'identifiants et d'un numéro de non-conformité.
    '''</summary>
    ''' 
    '''<param name="sNoNC">Contient le numéro de non-conformité.</param>
    '''<param name="treIdentifiants">TreeView contenant les identifiants à réserver.</param>
    ''' 
    '''<remarks>
    '''Le traitement de réservation permet d'effectuer les étapes suivantes :
    ''' -Pour chaque identifiant sélectionné:
    '''   -Si l'identifiant est au programme
    '''     -Détruire l'info du NO_MAP dans la table F502_PS.
    '''     -Détruire le lien le NO_MAP avec le NO_NC dans la table F502_NC.
    '''     -Détruire le lien le NO_MAP avec le TY_TRAV dans la table F503_TR.
    '''     -Pour chaque classe sélectionnée:
    '''       -Détruire le code de classe avec le NO_MAP dans la table F502_LE.
    '''</remarks>
    ''' 
    Public Sub AnnulerReserverIdentifiantsClasses(ByVal sNoNC As String, ByRef treIdentifiants As TreeView)
        'Déclarer les variables de travail
        Dim qListeClasses As Dictionary(Of String, String)  'Dictionnaire contenant la liste des codes de classes.
        Dim qNodeIdentifiant As TreeNode = Nothing  'Noeud d'un TreeView contenant un identifiant.
        Dim sUsager As String = Nothing             'Contient le nom de l'usager par défaut.
        Dim sCodeClasse As String = Nothing         'Contient le code de classe.
        Dim iNoMap As Integer = 0                   'Contient le no_map.

        Try
            'Définir le nom de l'usager
            sUsager = System.Environment.GetEnvironmentVariable("USERNAME").ToUpper

            'Vérifier si l'accès à SIB n'est pas autorisé
            If Not AccesAutoriser(sUsager, "PROD-RSP") Then
                'Retourner une erreur d'accès non autorisé
                Throw New AnnulerExecutionException("ERREUR : Accès non autorisé : Usager=" & sUsager & ", Groupe=PROD-RSP")
            End If

            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Début du traitement d'annulation de réservation des identifiants et des classes !"

            'Traiter tous les identifiants
            For Each qNodeIdentifiant In treIdentifiants.Nodes
                'Vérifier si l'identifiant est sélectionné
                If qNodeIdentifiant.Checked Then
                    'Afficher l'information de fin de traitement
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Annulation de la réservation de l'identifiant : " & qNodeIdentifiant.Name & " ..."

                    'Vider le contenu du noeud de l'identifiant
                    qNodeIdentifiant.Nodes.Clear()

                    'Vérifier si l'édition de fin de l'identifiant de non-conformité est inconnue (99999)
                    If qNodeIdentifiant.Text.Contains("99999") Then
                        'Définir le No_MAP à partir de l'identifiant, le type de produit et le type de travail
                        iNoMap = DefinirNoMapEnProduction(qNodeIdentifiant.Name)

                        'Vérifier si le numéro de mise au programme est valide
                        If iNoMap > 0 Then
                            Try
                                'Détruire l'information du NO_MAP dans la table F502_PS
                                Call DetruireInfoNoMapTableF502_PS(iNoMap.ToString)

                                'Détruire un lien entre le NO_NC et le NO_MAP dans la table F502_NC
                                Call DetruireLienNoNcNoMapTableF502_NC(iNoMap.ToString, sNoNC)

                                'Détruire un lien entre le TY_TRAV et le NO_MAP dans la table F503_TR
                                Call DetruireLienTyTravNoMapTableF503_TR(iNoMap.ToString)

                                'Détruire le lien entre le code de classe et le NO_NC dans la table F502_LE
                                Call DetruireLienCodeClasseNoMapTableF502_LE(iNoMap.ToString)

                            Catch ex As Exception
                                'Commande pour refuser la modification
                                Call Rollback()
                                'Retourner l'erreur
                                Throw
                            End Try

                            'Commande pour accepter la modification
                            Call Commit()

                            'Modifier le nombre de classes
                            qNodeIdentifiant.Text = qNodeIdentifiant.Text.Substring(0, qNodeIdentifiant.Text.LastIndexOf("NoMap=")) & "NoMap=, Etat=, NbClasses="
                        End If

                        'Si l'édition de fin de l'identifiant de non-conformité est connue
                    Else
                        'La réservation ne peut être détruite car la production est déjà terminée 
                        qNodeIdentifiant.Nodes.Add("ERREUR", "ERREUR : La réservation ne peut être détruite car la production est terminée !")
                        'Désélectionner le noeud
                        qNodeIdentifiant.Checked = False
                        'Ouvrir le noeud
                        qNodeIdentifiant.Expand()
                    End If
                End If
            Next

            'Ouvrir tous les noeuds
            treIdentifiants.ExpandAll()

            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement d'annulation de réservation des identifiants et des classes !"

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            qListeClasses = Nothing
            qNodeIdentifiant = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de fermer la réservation de tous les identifiants sélectionnés d'un TreeView d'identifiants et d'un numéro de non-conformité.
    '''</summary>
    ''' 
    '''<param name="sNoNC">Contient le numéro de non-conformité.</param>
    '''<param name="treIdentifiants">TreeView contenant les identifiants à réserver.</param>
    ''' 
    '''<remarks>
    '''Le traitement de réservation permet d'effectuer les étapes suivantes :
    ''' -Pour chaque identifiant sélectionné:
    '''   -Si l'identifiant est au programme
    '''     -Détruire l'info du NO_MAP dans la table F502_PS.
    '''     -Détruire le lien le NO_MAP avec le NO_NC dans la table F502_NC.
    '''     -Détruire le lien le NO_MAP avec le TY_TRAV dans la table F503_TR.
    '''     -Pour chaque classe sélectionnée:
    '''       -Détruire le code de classe avec le NO_MAP dans la table F502_LE.
    '''</remarks>
    ''' 
    Public Sub FermerReserverIdentifiantsClasses(ByVal sNoNC As String, ByRef treIdentifiants As TreeView)
        'Déclarer les variables de travail
        Dim qListeClasses As Dictionary(Of String, String)  'Dictionnaire contenant la liste des codes de classes.
        Dim qNodeIdentifiant As TreeNode = Nothing  'Noeud d'un TreeView contenant un identifiant.
        Dim sUsager As String = Nothing             'Contient le nom de l'usager par défaut.
        Dim sCodeClasse As String = Nothing         'Contient le code de classe.
        Dim sMessage As String = ""                 'Contient un message d'erreur.
        Dim iNoMap As Integer = 0                   'Contient le numéro de mise au programme de l'identifiant.
        Dim iEdCour As Integer = 0                  'Contient le numéro de l'édition courante de l'identifiant.
        Dim iVerCour As Integer = 0                 'Contient le numéro de la version courante de l'identifiant.
        Dim iVerMeta As Integer = 0                 'Contient le numéro de la version des métadonnées de l'identifiant.

        Try
            'Définir le nom de l'usager
            sUsager = System.Environment.GetEnvironmentVariable("USERNAME").ToUpper

            'Vérifier si l'accès à SIB n'est pas autorisé
            If Not AccesAutoriser(sUsager, "PROD-RSP") Then
                'Retourner une erreur d'accès non autorisé
                Throw New AnnulerExecutionException("ERREUR : Accès non autorisé : Usager=" & sUsager & ", Groupe=PROD-RSP")
            End If

            'Vérifier si tous les identifiants sélectionnés possède un Réplica
            If Not NoteReplicaTousPresents(sNoNC, treIdentifiants, sMessage) Then
                'Retourner une erreur
                Throw New AnnulerExecutionException(sMessage)
            End If

            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Début du traitement de fermeture de réservation des identifiants et des classes !"

            'Traiter tous les identifiants
            For Each qNodeIdentifiant In treIdentifiants.Nodes
                'Vérifier si l'identifiant est sélectionné
                If qNodeIdentifiant.Checked Then
                    'Afficher l'information de fin de traitement
                    If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fermeture de réservation de l'identifiant : " & qNodeIdentifiant.Name & " ..."

                    'Vider le contenu du noeud de l'identifiant
                    qNodeIdentifiant.Nodes.Clear()

                    'Vérifier si l'édition de fin de l'identifiant de non-conformité est inconnue (99999)
                    If qNodeIdentifiant.Text.Contains("99999") Then
                        'Définir le No_MAP à partir de l'identifiant, le type de produit et le type de travail
                        iNoMap = DefinirNoMapEnProduction(qNodeIdentifiant.Name)

                        'Vérifier si le numéro de mise au programme est valide
                        If iNoMap > 0 Then
                            Try
                                'Extraire l'information des métadonnées de l'identifiant courant
                                Call ExtraireInfoMetaIdentifiantCourant(qNodeIdentifiant.Name, iEdCour, iVerCour, iVerMeta)

                                'Insérer une nouvelle étiquette du Proc/Desc="RESOLUTION_NC/BDG" dans la table F235_PS
                                Call InsererProcDescTableF235_PS(sUsager, qNodeIdentifiant.Name, iEdCour, iVerCour, "RESOLUTION_NC/BDG")

                                'Modifier la date des métadonnées dans la table F235_MR
                                Call ModifierDateMetadonneesTableF235_MR(sUsager, qNodeIdentifiant.Name, iEdCour, iVerCour)

                                'Incrémenter le numéro de version des métadonnées dans la table F235_PR
                                Call IncrementerVersionMetadonneesTableF235_PR(sUsager, qNodeIdentifiant.Name, iVerMeta)

                                'Modifier le numéro d'édition et version de fin dans la table F705_PR
                                Call ModifierEditionVersionFinTableF705_PR(sUsager, qNodeIdentifiant.Name, iEdCour, iVerCour, sNoNC)

                                'Fermer le numéro de mise au programme (E_PLSNRC='T') dans la table F502_PS
                                Call FermerNoMapTableF502_PS(sUsager, iNoMap.ToString)

                            Catch ex As Exception
                                'Commande pour refuser la modification
                                Call Rollback()
                                'Retourner l'erreur
                                Throw
                            End Try

                            'Commande pour accepter la modification
                            Call Commit()

                            'Modifier l'édition et version de fin
                            qNodeIdentifiant.Text = qNodeIdentifiant.Text.Replace("99999.99", iEdCour.ToString & "." & iVerCour.ToString)

                            'Modifier l'état
                            qNodeIdentifiant.Text = qNodeIdentifiant.Text.Replace("Etat=P", "Etat=T")

                            'Désélectionner le noeud
                            qNodeIdentifiant.Checked = False

                            'Fermer le noeud
                            qNodeIdentifiant.Collapse()
                        End If

                        'Si l'édition de fin de l'identifiant de non-conformité est connue
                    Else
                        'La réservation ne peut être fermée car la production est déjà terminée
                        qNodeIdentifiant.Nodes.Add("ERREUR", "ERREUR : La réservation ne peut être fermée car la production est déjà terminée !")
                        'Désélectionner le noeud
                        qNodeIdentifiant.Checked = False
                        'Ouvrir le noeud
                        qNodeIdentifiant.Expand()
                    End If
                End If
            Next

            'Si toutes les intervalles de fin de la non-conformité sont inscrits
            If NbIdentifiantsNonConformesNonFermer(sNoNC) = 0 Then
                'Modifier la date de traitement dans la table F702_NC
                Call ModifierDateTraitementTableF702_NC(sUsager, sNoNC)
            End If

            'Ouvrir tous les noeuds
            treIdentifiants.ExpandAll()

            'Afficher l'information de fin de traitement
            If gpTrackCancel.Progressor IsNot Nothing Then gpTrackCancel.Progressor.Message = "Fin du traitement de fermeture de réservation des identifiants et des classes !"

        Catch ex As Exception
            'Retourner l'erreur
            Throw
        Finally
            'Vider la mémoire
            qListeClasses = Nothing
            qNodeIdentifiant = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Function qui permet d'indiquer si les identifiants et les classes de la non-conformité sont réservés en production.
    '''</summary>
    '''
    '''<param name="sNoNc">Contient le numéro de non-conformité à traiter.</param>
    '''<param name="treIdentifiants">TreeView contenant les identifiants sélectionnés.</param>
    '''<param name="treClasses">TreeView contenant les classes à réserver.</param>
    ''' 
    '''<returns>Boolean qui indique si les identifiants et les classes de la non-conformité sont réservés en production.</returns>
    ''' 
    Public Function ReservationValide(ByVal sNoNc As String, ByVal treIdentifiants As TreeView, ByVal treClasses As TreeView) As Boolean
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim sListeIdentifiants As String = Nothing  'Contient la liste des identifiants.
        Dim sListeCodesClasses As String = Nothing  'Contient la liste des codes de classes.
        Dim iNbIdentifiants As Integer = -1         'Contient le nombre d'identifiants.
        Dim iNbClasses As Integer = -1              'Contient le nombre de classes.

        'Définir la valeur par défaut
        ReservationValide = False

        'Définir la liste des identifiants
        sListeIdentifiants = DefinirListeIdentifiants(treIdentifiants, iNbIdentifiants)

        'Définir la liste des codes classes
        sListeCodesClasses = DefinirListeCodesClasses(treClasses, iNbClasses)

        Try
            'Définir la requête SQL pour retourner le nombre  d'identifiants et de classes en production
            sQueryString = "SELECT COUNT(DISTINCT A.IDENTIFIANT||D.CD_ELEM_TOPO)" _
                         & "  FROM F705_PR A, F502_PS B, F502_NC C, F502_LE D" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.ED_FIN=99999 AND B.E_PLSNRC='P' AND A.NO_NC='" & sNoNc & "'" _
                         & "   AND A.IDENTIFIANT IN (" & sListeIdentifiants & ") AND A.IDENTIFIANT=B.IDENTIFIANT" _
                         & "   AND D.CD_ELEM_TOPO IN (" & sListeCodesClasses & ") AND B.NO_MAP=C.NO_MAP AND B.NO_MAP=D.NO_MAP"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Indique si des classes d'un identifiant sont en production
            ReservationValide = CInt(qCommand.ExecuteScalar) = iNbIdentifiants * iNbClasses

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
            sListeIdentifiants = Nothing
            sListeCodesClasses = Nothing
        End Try
    End Function

    '''<summary>
    ''' Function qui permet d'indiquer si une note de réplica est présente pour au moins un des identifiants spécifiés.
    '''</summary>
    '''
    '''<param name="sNoNc">Contient le numéro de non-conformité à traiter.</param>
    '''<param name="treIdentifiants">TreeView contenant les identifiants sélectionnés.</param>
    '''<param name="sMessage">Contient le message des identifiants dont le réplica est déjà créé.</param>
    ''' 
    '''<returns>Boolean qui indique si les identifiants et les classes de la non-conformité sont réservés en production..</returns>
    ''' 
    Public Function NoteReplicaPresente(ByVal sNoNc As String, ByVal treIdentifiants As TreeView, Optional ByRef sMessage As String = "") As Boolean
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim sListeIdentifiants As String = Nothing  'Contient la liste des identifiants.

        'Définir la valeur par défaut
        NoteReplicaPresente = False
        sMessage = ""

        'Définir la liste des identifiants
        sListeIdentifiants = DefinirListeIdentifiants(treIdentifiants)

        Try
            'Définir la requête SQL
            sQueryString = "SELECT DISTINCT A.IDENTIFIANT" _
                         & "  FROM F705_PR A, F502_PS B, F502_NC C" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.ED_FIN=99999 AND B.E_PLSNRC='P' AND A.NO_NC='" & sNoNc & "' AND B.NOTE LIKE '%#REPLICA%'" _
                         & "   AND A.IDENTIFIANT IN (" & sListeIdentifiants & ") AND A.IDENTIFIANT=B.IDENTIFIANT AND B.NO_MAP=C.NO_MAP" _
                         & "  ORDER BY A.IDENTIFIANT"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            qReader = qCommand.ExecuteReader

            'Vérifier si des identifiants sont présents
            If qReader.HasRows Then
                'Indique qu'une note de réplica est présente
                NoteReplicaPresente = True

                'Initialiser le message de retour
                sMessage = "Réplica déjà créé pour les identifiants suivants : " & vbCrLf

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Ajouter la valeur
                    sMessage = sMessage & "/" & qReader.GetString(0)
                End While
            End If

            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
            sListeIdentifiants = Nothing
        End Try
    End Function

    '''<summary>
    ''' Function qui permet d'indiquer si une note de réplica est présente pour tous les identifiants spécifiés.
    '''</summary>
    '''
    '''<param name="sNoNc">Contient le numéro de non-conformité à traiter.</param>
    '''<param name="treIdentifiants">TreeView contenant les identifiants sélectionnés.</param>
    '''<param name="sMessage">Contient le message des identifiants dont le réplica est déjà créé.</param>
    ''' 
    '''<returns>Boolean qui indique si les identifiants et les classes de la non-conformité sont réservés en production..</returns>
    ''' 
    Public Function NoteReplicaTousPresents(ByVal sNoNc As String, ByVal treIdentifiants As TreeView, Optional ByRef sMessage As String = "") As Boolean
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim sListeIdentifiants As String = Nothing  'Contient la liste des identifiants.
        Dim iNbIdentifiantsTreeView As Integer = 0  'Contient le nombre d'identifiants dans le TreeView.
        Dim iNbIdentifiantsReplica As Integer = 0   'Contient le nombre d'identifiants avec un Réplica.

        'Définir la valeur par défaut
        NoteReplicaTousPresents = False
        sMessage = ""

        Try
            'Définir la liste des identifiants
            sListeIdentifiants = DefinirListeIdentifiants(treIdentifiants, iNbIdentifiantsTreeView)

            'Définir la requête SQL pour extraire les identifiants avec Réplica
            sQueryString = "SELECT COUNT(DISTINCT A.IDENTIFIANT)" _
                         & "  FROM F705_PR A, F502_PS B, F502_NC C" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.ED_FIN=99999 AND A.NO_NC='" & sNoNc & "' AND B.NOTE LIKE '%#REPLICA%'" _
                         & "   AND A.IDENTIFIANT IN (" & sListeIdentifiants & ") AND A.IDENTIFIANT=B.IDENTIFIANT AND B.NO_MAP=C.NO_MAP" _
                         & "  ORDER BY A.IDENTIFIANT"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande pour extraire le nombre d'identifiants avec Replica
            iNbIdentifiantsReplica = CInt(qCommand.ExecuteScalar)

            'Vérifier s'il y a un réplica pour tous les identifiants
            If iNbIdentifiantsTreeView = iNbIdentifiantsReplica Then
                'Indique qu'une note de réplica est présente
                NoteReplicaTousPresents = True

                'S'il n'y a pas de réplica pour tous les identifiants
            Else
                'Initialiser le message d'erreur
                sMessage = "ERREUR : Il n'y a pas de Réplica pour tous les identifiants, Nb. identifiants: " & iNbIdentifiantsTreeView.ToString _
                         & ", Nb. Réplica:" & iNbIdentifiantsReplica.ToString & vbCrLf
            End If

        Catch erreur As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
            sListeIdentifiants = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'ajouter une note de réplica pour tous les identifiants spécifiés dans la table F502_PS.
    '''</summary>
    '''
    '''<param name="sNomReplica">Contient le nom du réplica.</param>
    '''<param name="sNoNc">Contient le numéro de non-conformité à traiter.</param>
    '''<param name="treIdentifiants">TreeView contenant les identifiants sélectionnés.</param>
    ''' 
    Public Sub AjouterNoteReplica(ByVal sNomReplica As String, ByVal sNoNc As String, ByVal treIdentifiants As TreeView)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim sListeIdentifiants As String = Nothing  'Contient la liste des identifiants.
        Dim sUsager As String = Nothing             'contient le nom de l'usager.
        Dim iNbIdentifiants As Integer = -1         'Contient le nombre d'identifiants.
        Dim iNbModif As Integer = -1                'Contient le nombre de modifications.

        'Définir le nom de l'usager
        sUsager = System.Environment.GetEnvironmentVariable("USERNAME").ToUpper

        'Définir la liste des identifiants
        sListeIdentifiants = DefinirListeIdentifiants(treIdentifiants, iNbIdentifiants)

        Try
            'Définir la requête SQL
            sQueryString = "UPDATE F502_PS" _
                         & "   SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" & sUsager & "', DT_M=SYSDATE, NOTE=NOTE||'#REPLICA=" & sNomReplica & "'" _
                         & " WHERE NO_MAP IN (" _
                         & "SELECT DISTINCT B.NO_MAP" _
                         & "  FROM F705_PR A, F502_PS B, F502_NC C" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.ED_FIN=99999 AND B.E_PLSNRC='P' AND A.NO_NC='" & sNoNc & "'" _
                         & "   AND A.IDENTIFIANT IN (" & sListeIdentifiants & ") AND A.IDENTIFIANT=B.IDENTIFIANT AND B.NO_MAP=C.NO_MAP)"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery

            'Vérifier la présence d'erreur
            If iNbModif <> iNbIdentifiants Then Throw New Exception("ERREUR: Ajouter la note de réplica dans la table F502_PS : " & vbCrLf & sQueryString)

            'Sauver les modifications
            Me.Commit()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
            sListeIdentifiants = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Function qui permet de définir la liste des identifiants sélectionnés à partir d'un TreeView.
    '''</summary>
    '''-------------------------------------------------------------------------------------
    '''<param name="treIdentifiants">TreeView contenant les identifiants sélectionnés.</param>
    '''<param name="iNbIdentifiants">Contient le nombre d'identifiants sélectionnés.</param>
    ''' 
    '''<returns>String contenant le liste des identifiants séparés par des virgules et des apostrophes.</returns>
    ''' 
    Public Function DefinirListeIdentifiants(ByVal treIdentifiants As TreeView, Optional ByRef iNbIdentifiants As Integer = -1) As String
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing     'Contient le noeud à traiter.

        'Par défaut la liste des identifiants est vide
        DefinirListeIdentifiants = ""

        Try
            'Initialiser le nombre d'identifiants
            iNbIdentifiants = 0

            'Traiter tous les identifiants du TreeView
            For i = 0 To treIdentifiants.Nodes.Count - 1
                'Définir le noeud traité
                pNode = treIdentifiants.Nodes.Item(i)

                'Vérifier si l'identifiant est sélectionné
                If pNode.Checked = True Then
                    'Ajouter l'identifiant à la liste
                    DefinirListeIdentifiants = DefinirListeIdentifiants & "'" & pNode.Text.Substring(0, pNode.Text.IndexOf(" ")) & "'"

                    'Compter le nombre d'identifiants
                    iNbIdentifiants = iNbIdentifiants + 1
                End If
            Next

            'Ajouter les séparateurs
            DefinirListeIdentifiants = DefinirListeIdentifiants.Replace("''", "','")

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet définir la liste des codes des classes contenus dans un TreeView de classes.
    '''</summary>
    ''' 
    '''<param name="treClasses">TreeView contenant les classes sélectionnées.</param>
    '''<param name="iNbClasses">Contient le nombre de classes sélectionnées.</param>
    ''' 
    '''<returns>"String" correspondant à la liste des codes des classes contenus dans un TreeView de classes.</returns>
    ''' 
    Public Function DefinirListeCodesClasses(ByVal treClasses As TreeView, Optional ByRef iNbClasses As Integer = -1) As String
        'Déclarer les variables de travail
        Dim qNodeClasse As TreeNode = Nothing       'Noeud d'un TreeView contenant une classe.

        'Définir la valeur par défaut
        DefinirListeCodesClasses = ""

        Try
            'Initialiser le nombre de classes
            iNbClasses = 0

            'Traiter toutes les classes
            For Each qNodeClasse In treClasses.Nodes
                'Vérifier si la classe est sélectionnée
                If qNodeClasse.Checked Then
                    'Définir la liste des codes de classes
                    DefinirListeCodesClasses = DefinirListeCodesClasses & "'" & qNodeClasse.Name & "'"

                    'Compter le nombre de classes
                    iNbClasses = iNbClasses + 1
                End If
            Next

            'Ajouter les séparateurs
            DefinirListeCodesClasses = DefinirListeCodesClasses.Replace("''", "','")

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            qNodeClasse = Nothing
        End Try
    End Function

    '''<summary>
    ''' Function qui permet de définir la liste des classes sélectionnées à partir d'un TreeView.
    '''</summary>
    '''
    '''<param name="treClasses">TreeView contenant les classes sélectionnées.</param>
    '''<param name="iNbClasses">Contient le nombre de classes sélectionnées.</param>
    ''' 
    '''<returns>String contenant le liste des classes séparées par des virgules sans apostrophes.</returns>
    ''' 
    Public Function DefinirListeClasses(ByVal treClasses As TreeView, Optional ByRef iNbClasses As Integer = -1) As String
        'Déclarer les variables de travail
        Dim pNode As TreeNode = Nothing                 'Contient le noeud à traiter.

        'Par défaut la liste des classes est vide
        DefinirListeClasses = ""

        Try
            'Initialiser le nombre de classes
            iNbClasses = 0

            'Traiter toutes les classes du TreeView
            For i = 0 To treClasses.Nodes.Count - 1
                'Définir le noeud traité
                pNode = treClasses.Nodes.Item(i)

                'Vérifier si la classe est sélectionnée
                If pNode.Checked = True Then
                    'Ajouter la classe à la liste
                    DefinirListeClasses = DefinirListeClasses & "'" & pNode.Text.Substring(10) & "'"

                    'Compter le nombre de classes
                    iNbClasses = iNbClasses + 1
                End If
            Next

            'Ajouter les séparateurs de classes
            DefinirListeClasses = DefinirListeClasses.Replace("''", "','")

            'Enlever les apostrophes
            DefinirListeClasses = DefinirListeClasses.Replace("'", "")

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNode = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet de sélectionner les classes à partir de l'information d'un TreeNode.
    '''</summary>
    '''    
    '''<param name="pSelectNode">TreeNode contenant l'identifiant et les classes à sélectionner.</param>
    '''<param name="treClasses">TreeView contenant les classes sélectionnées.</param>
    ''' 
    Public Sub SelectionnerClasses(ByVal pSelectNode As TreeNode, ByRef treClasses As TreeView)
        'Déclarer les variables de travail
        Dim pNodeClasse As TreeNode = Nothing           'Contient le noeud de la classe à traiter.
        Dim pNodeIdClasse As TreeNode = Nothing         'Contient le noeud de la classe de l'identifiant à traiter.
        Dim sNomClasse As String = ""                   'Contient le nom de la classe de l'identifiant.

        Try
            'Traiter toutes les classes du TreeView
            For i = 0 To treClasses.Nodes.Count - 1
                'Définir le noeud de la classe à  traiter
                pNodeClasse = treClasses.Nodes.Item(i)
                'Désélectionner la classe
                If pNodeClasse.Checked Then pNodeClasse.Checked = False

                'Traiter toutes les classes de l'identifiant
                For j = 0 To pSelectNode.Nodes.Count - 1
                    'Définir le noeud de la classe à  traiter
                    pNodeIdClasse = pSelectNode.Nodes.Item(j)
                    'Définir le nom de la classe
                    sNomClasse = pNodeIdClasse.Text.Split(CChar(":"))(1)

                    'Vérifier si la classe doit être sélectionnée
                    If pNodeClasse.Text.Contains(sNomClasse) Then
                        'Sélectionner la classe
                        If pNodeClasse.Checked = False Then pNodeClasse.Checked = True
                    End If
                Next
            Next

        Catch ex As Exception
            Throw
        Finally
            'Vider la mémoire
            pNodeClasse = Nothing
            pNodeIdClasse = Nothing
        End Try
    End Sub
#End Region

#Region "Routines et fonctions privées"
    '''<summary>
    ''' Routine qui permet de modifier la date de traitement dans la table F702_NC.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sNoNC">Contient le numéro de non-conformité.</param>
    ''' 
    Private Sub ModifierDateTraitementTableF702_NC(ByVal sUsager As String, ByVal sNoNC As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Modifier la date de traitement dans la table F702_NC
            sQueryString = "UPDATE F702_NC" _
                         & "   SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" & sUsager & "', DT_M=SYSDATE, DATE_TRAITEMENT=SYSDATE" _
                         & " WHERE NO_NC='" & sNoNC & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Modifier la date de traitement dans la table F702_NC : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'insérer une nouvelle étiquette du Proc/Desc dans la table F235_PS.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sIdentifiant">Contient l'identifiant à traiter.</param>
    '''<param name="iEdCour">Contient le numéro de l'édition courante.</param>
    '''<param name="iVerCour">Contient le numéro de la version courante.</param>
    '''<param name="sProcDesc">Contient l'étiquette du Processus de description (Proc/Desc).</param>
    ''' 
    Private Sub InsererProcDescTableF235_PS(ByVal sUsager As String, ByVal sIdentifiant As String, ByVal iEdCour As Integer, ByVal iVerCour As Integer, ByVal sProcDesc As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNoSeq As Integer = 0                   'Contient le numéro de séquence du Proc/Desc à ajouter.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Extraire le nouveau numéro de séquence
            sQueryString = "SELECT MAX(NO_SEQ) + 1" _
                         & "  FROM F235_PS " _
                         & " WHERE TY_PRODUIT='" & gsTypeProduit & "' AND IDENTIFIANT='" & sIdentifiant & "' AND ED=" & iEdCour.ToString & " AND VER=" & iVerCour.ToString

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNoSeq = CInt(qCommand.ExecuteScalar())

            'Insérer une nouvelle étiquette du Proc/Desc dans la table F235_PS
            sQueryString = "INSERT INTO F235_PS" _
                         & "   Values (P0G03_UTL.PU_HORODATEUR, '" & sUsager & "', SYSDATE, SYSDATE, '" & gsTypeProduit & "', " _
                         & "'" & sIdentifiant & "', " & iEdCour.ToString & ", " & iVerCour.ToString & ", " & iNoSeq.ToString _
                         & ", '{$PS$" & sProcDesc & "}', TO_CHAR(SYSDATE, 'YYYYMMDD'), 0)"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Insérer une nouvelle étiquette du Proc/Desc dans la table F235_PS : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de modifier la date des métadonnées dans la table F235_MR.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sIdentifiant">Contient l'identifiant à traiter.</param>
    '''<param name="iEdCour">Contient le numéro de l'édition courante.</param>
    '''<param name="iVerCour">Contient le numéro de la version courante.</param>
    ''' 
    Private Sub ModifierDateMetadonneesTableF235_MR(ByVal sUsager As String, ByVal sIdentifiant As String, ByVal iEdCour As Integer, ByVal iVerCour As Integer)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Modifier la date des métadonnées dans la table F235_MR
            sQueryString = "UPDATE F235_MR" _
                         & "   SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" & sUsager & "', DT_M=SYSDATE, DT_METADATA=TO_CHAR(SYSDATE, 'YYYYMMDD')" _
                         & " WHERE TY_PRODUIT='" & gsTypeProduit & "' AND IDENTIFIANT='" & sIdentifiant & "' AND ED=" & iEdCour.ToString & " AND VER=" & iVerCour.ToString

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Modifier la date des métadonnées dans la table F235_MR : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'incrémenter le numéro de la version des métadonnées dans la table F235_PR.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sIdentifiant">Contient l'identifiant à traiter.</param>
    '''<param name="iVerMeta">Contient le numéro de version des métadonnées.</param>
    ''' 
    Private Sub IncrementerVersionMetadonneesTableF235_PR(ByVal sUsager As String, ByVal sIdentifiant As String, ByVal iVerMeta As Integer)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Incrémenter le numéro de version des métadonnées
            iVerMeta = iVerMeta + 1

            'Modifier le numéro de la version des métadonnées dans la table F235_PR
            sQueryString = "UPDATE F235_PR" _
                         & "   SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" & sUsager & "', DT_M=SYSDATE, VER_META=" & iVerMeta.ToString _
                         & " WHERE TY_PRODUIT='" & gsTypeProduit & "' AND IDENTIFIANT='" & sIdentifiant & "' AND JEU_COUR=1"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Modifier le numéro de la version des métadonnées dans la table F235_PR : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de modifier l'édition et version de fin dans la table F705_PR.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sIdentifiant">Contient l'identifiant à traiter.</param>
    '''<param name="iEdCour">Contient le numéro de l'édition courante.</param>
    '''<param name="iVerCour">Contient le numéro de la version courante.</param>
    '''<param name="sNoNC">Contient le numéro de non-conformité.</param>
    ''' 
    Private Sub ModifierEditionVersionFinTableF705_PR(ByVal sUsager As String, ByVal sIdentifiant As String, ByVal iEdCour As Integer, ByVal iVerCour As Integer, ByVal sNoNC As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Modifier l'édition et version de fin dans la table F705_PR
            sQueryString = "UPDATE F705_PR" _
                         & "   SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" & sUsager & "', DT_M=SYSDATE, ED_FIN=" & iEdCour.ToString & ", VER_FIN=" & iVerCour.ToString _
                         & " WHERE TY_PRODUIT='" & gsTypeProduit & "' AND IDENTIFIANT='" & sIdentifiant & "' AND NO_NC='" & sNoNC & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Modifier l'édition et version de fin dans la table F705_PR : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de fermer le NO_MAP (E_PLSNRC='T') dans la table F502_PS.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    ''' 
    Private Sub FermerNoMapTableF502_PS(ByVal sUsager As String, ByVal sNoMap As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Modifier l'état à T:Terminer du NO_MAP dans la table F502_PS
            sQueryString = "UPDATE F502_PS" _
                         & "   SET UPDT_FLD=P0G03_UTL.PU_HORODATEUR, ETAMPE='" & sUsager & "', DT_M=SYSDATE, E_PLSNRC='T'" _
                         & " WHERE NO_MAP= " & sNoMap

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Modifier l'état à T:Terminer du NO_MAP dans la table F502_PS : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'insérer l'information du NO_MAP dans la table F502_PS.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    '''<param name="sIdentifiant">Contient l'identifiant de la mise au programme.</param>
    '''<param name="sNote">Contient la note de la mise au programme.</param>
    '''<param name="sDatePrevue">Contient la date prévue de la mise au programme.</param>
    '''<param name="sNormes">Contient le numéro des normes de production.</param>
    ''' 
    Private Sub InsererInfoNoMapTableF502_PS(ByVal sUsager As String, ByVal sNoMap As String, ByVal sIdentifiant As String, _
                                             ByVal sNote As String, ByVal sDatePrevue As String, ByVal sNormes As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Ajouter l'information du NO_MAP dans la table F502_PS
            sQueryString = "Insert into F502_PS (UPDT_FLD, ETAMPE, DT_C, DT_M, NO_MAP, TY_PRODUIT, IDENTIFIANT, TYPE, NOTE, DT_PREVUE, E_PLSNRC, NORMES)" _
                         & " Values (P0G03_UTL.PU_HORODATEUR, '" & sUsager & "', SYSDATE, SYSDATE, " & sNoMap & ", '" & gsTypeProduit & "', '" & sIdentifiant _
                         & "', 'A', '" & sNote & "', TO_DATE('" & sDatePrevue & "', 'YYYY-MM-DD'), 'P', '" & sNormes & "')"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Ajouter l'information du NO_MAP dans la table F502_PS : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire l'information du NO_MAP dans la table F502_PS.
    '''</summary>
    ''' 
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    ''' 
    Private Sub DetruireInfoNoMapTableF502_PS(ByVal sNoMap As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        Try
            'Détruire l'information du NO_MAP dans la table F502_PS
            sQueryString = "DELETE F502_PS WHERE NO_MAP=" & sNoMap & "AND TY_PRODUIT='" & gsTypeProduit & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            qCommand.ExecuteNonQuery()

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'insérer un lien entre le NO_MAP et le NO_NC dans la table F502_NC.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    '''<param name="sNoNC">Contient le numéro de non-conformité.</param>
    ''' 
    Private Sub InsererLienNoNcNoMapTableF502_NC(ByVal sUsager As String, ByVal sNoMap As String, ByVal sNoNC As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Ajouter un lien entre le NO_MAP et le NO_NC dans la table F502_NC
            sQueryString = "Insert into F502_NC (UPDT_FLD, ETAMPE, DT_C, DT_M, NO_MAP, NO_NC)" _
                         & " Values (P0G03_UTL.PU_HORODATEUR, '" & sUsager & "', SYSDATE, SYSDATE, " & sNoMap & ", '" & sNoNC & "')"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Ajouter un lien entre le NO_MAP et le NO_NC dans la table F502_NC : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire un lien entre le NO_MAP et le NO_NC dans la table F502_NC.
    '''</summary>
    ''' 
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    '''<param name="sNoNC">Contient le numéro de non-conformité.</param>
    ''' 
    Private Sub DetruireLienNoNcNoMapTableF502_NC(ByVal sNoMap As String, ByVal sNoNC As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        Try
            'Détruire un lien entre le NO_MAP et le NO_NC dans la table F502_NC
            sQueryString = "DELETE F502_NC WHERE NO_MAP=" & sNoMap & " AND NO_NC='" & sNoNC & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            qCommand.ExecuteNonQuery()

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'insérer un lien entre le NO_MAP et le TY_TRAV dans la table F503_TR.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    ''' 
    Private Sub InsererLienTyTravNoMapTableF503_TR(ByVal sUsager As String, ByVal sNoMap As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Ajouter un lien entre le NO_MAP et le TY_TRAV dans la table F503_TR
            sQueryString = "Insert into F503_TR (UPDT_FLD, ETAMPE, DT_C, DT_M, NO_MAP, TY_TRAV, NO_SEQ, NB_JRS_EXT, NO_LOT, GROUPE, NO_CATALOGUE)" _
                         & " Values (P0G03_UTL.PU_HORODATEUR, '" & sUsager & "', SYSDATE, SYSDATE, " & sNoMap & ", '" & gsTypeTravail & "', 1, NULL, NULL, NULL, NULL)"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Ajouter un lien entre le NO_MAP et le TY_TRAV dans la table F503_TR : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire un lien entre le NO_MAP et le TY_TRAV dans la table F503_TR.
    '''</summary>
    ''' 
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    ''' 
    Private Sub DetruireLienTyTravNoMapTableF503_TR(ByVal sNoMap As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        Try
            'Détruire un lien entre le NO_MAP et le TY_TRAV dans la table F503_TR
            sQueryString = "DELETE F503_TR WHERE NO_MAP=" & sNoMap & " AND TY_TRAV='" & gsTypeTravail & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            qCommand.ExecuteNonQuery()

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'insérer un lien entre le code de classe et le NO_NC dans la table F502_LE.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    '''<param name="sCodeClasse">Contient le code de la classe à mettre au programme.</param>
    ''' 
    Private Sub InsererLienCodeClasseNoMapTableF502_LE(ByVal sUsager As String, ByVal sNoMap As String, ByVal sCodeClasse As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim iNbModif As Integer = 0                 'Contient le nombre de modifications.

        Try
            'Ajouter le lien entre le code de classe et le NO_NC dans la table F502_LE
            sQueryString = "Insert into F502_LE (UPDT_FLD, ETAMPE, DT_C, DT_M, NO_MAP, CD_ELEM_TOPO, COLLISION_ACTIVE)" _
                         & " Values (P0G03_UTL.PU_HORODATEUR, '" & sUsager & "', SYSDATE, SYSDATE, " & sNoMap & ", '" & sCodeClasse & "', 1)"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            iNbModif = qCommand.ExecuteNonQuery()

            'Vérifier la présence d'erreur
            If iNbModif <> 1 Then Throw New Exception("ERREUR: Ajouter le lien entre le code de classe et le NO_NC dans la table F502_LE : " & vbCrLf & sQueryString)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet de détruire un lien entre le code de classe et le NO_NC dans la table F502_LE.
    '''</summary>
    ''' 
    '''<param name="sNoMap">Contient le numéro de mise au programme.</param>
    '''<param name="sCodeClasse">Contient le code de la classe à mettre au programme.</param>
    ''' 
    Private Sub DetruireLienCodeClasseNoMapTableF502_LE(ByVal sNoMap As String, Optional ByVal sCodeClasse As String = Nothing)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        Try
            'Détruire le lien entre le code de classe et le NO_NC dans la table F502_LE
            sQueryString = "DELETE F502_LE WHERE NO_MAP=" & sNoMap

            'Vérifier si le code de classe est présent
            If sCodeClasse IsNot Nothing Then
                'Ajouter le code de classe dans la requête
                sQueryString = sQueryString & " AND CD_ELEM_TOPO='" & sCodeClasse & "'"
            End If

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la commande
            qCommand.ExecuteNonQuery()

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'effectuer un Commit afin de conserver les modifications.
    '''</summary>
    ''' 
    Private Sub Commit()
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.

        Try
            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand("COMMIT", gqConnection)

            'Exécuter la commande
            qCommand.ExecuteNonQuery()

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'effectuer un Rollback afin de ne pas conserver les modifications.
    '''</summary>
    ''' 
    Private Sub Rollback()
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.

        Try
            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand("ROLLBACK", gqConnection)

            'Exécuter la commande
            qCommand.ExecuteNonQuery()

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Routine qui permet d'extraire l'nformation des metadonnees d'un identifiant courant dans la table F235_PR.
    '''</summary>
    ''' 
    '''<param name="sIdentifiant">Contient l'identifiant à traiter.</param>
    '''<param name="iEdCour">Contient le numéro de l'édition courante.</param>
    '''<param name="iVerCour">Contient le numéro de la version courante.</param>
    '''<param name="iVerMeta">Contient le numéro de la version des métadonnées de l'identifiant courant.</param>
    ''' 
    Private Sub ExtraireInfoMetaIdentifiantCourant(ByVal sIdentifiant As String, ByRef iEdCour As Integer, ByRef iVerCour As Integer, ByRef iVerMeta As Integer)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        Try
            'Définir la requête SQL
            sQueryString = "SELECT ED, VER, VER_META" _
                         & "  FROM F235_PR A" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.IDENTIFIANT='" & sIdentifiant & "' AND JEU_COUR=1"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Vérifier si une valeur est présente
            If Not qReader.HasRows Then
                Throw New Exception("ERREUR : Aucun identifiant courant n'est présent : " & vbCrLf & sQueryString)
            End If

            'Lire chaque ligne du résultat de la requête SQL
            qReader.Read()

            'Définir le numéro d'édition courante
            iEdCour = CInt(qReader.GetValue(0))

            'Définir le numéro de version courante
            iVerCour = CInt(qReader.GetValue(1))

            'Définir le numéro de version des métadonnées courante
            iVerMeta = CInt(qReader.GetValue(2))

        Catch ex As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Sub

    '''<summary>
    ''' Fonction qui permet de retourner le nombre d'identifiants non-conformes et non fermés
    '''</summary>
    ''' 
    '''<param name="sNoNc">Contient le numéro de non-conformité.</param>
    ''' 
    '''<returns>"Integer" correspondant au nombre d'identifiants non-conformes et non fermés.</returns>
    ''' 
    Private Function NbIdentifiantsNonConformesNonFermer(ByVal sNoNc As String) As Integer
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur par défaut
        NbIdentifiantsNonConformesNonFermer = 0

        Try
            'Définir la requête SQL pour retourner le nombre d'identifiants non-conformes et non fermés
            sQueryString = "SELECT COUNT(IDENTIFIANT)" _
                         & "  FROM F705_PR" _
                         & " WHERE NO_NC='" & sNoNc & "' AND ED_FIN=99999"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Indique si des classes d'un identifiant sont en production
            NbIdentifiantsNonConformesNonFermer = CInt(qCommand.ExecuteScalar)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de retourner le nombre de classes en production pour un identifiant.
    '''</summary>
    ''' 
    '''<param name="sIdentifiant">Contient l'identifiant en production.</param>
    '''<param name="sListeCodesClasses">Contient la liste des codes de classes en production.</param>
    ''' 
    '''<returns>"Integer" correspondant au nombre de classes d'un identifiant en production.</returns>
    ''' 
    Private Function NbClassesIdentifiantEnProduction(ByVal sIdentifiant As String, ByVal sListeCodesClasses As String) As Integer
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur par défaut
        NbClassesIdentifiantEnProduction = 0

        Try
            'Définir la requête SQL pour retourner le nombre de classes d'un identifiant en production
            sQueryString = "SELECT COUNT(B.CD_ELEM_TOPO)" _
                         & "  FROM F502_PS A, F502_LE B" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.IDENTIFIANT='" & sIdentifiant & "' AND A.E_PLSNRC='P'" _
                         & "   AND A.NO_MAP=B.NO_MAP AND B.CD_ELEM_TOPO IN (" & sListeCodesClasses & ") AND B.COLLISION_ACTIVE=1"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Indique si des classes d'un identifiant sont en production
            NbClassesIdentifiantEnProduction = CInt(qCommand.ExecuteScalar)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'indiquer si l'identifiant est en production à partir du type de produit et du type de travail.
    '''</summary>
    ''' 
    '''<param name="sIdentifiant">Contient l'identifiant en production.</param>
    ''' 
    '''<returns>"Boolean" pour indiquer si l'identifiant est en production pour un type de travail spécifique.</returns>
    ''' 
    Private Function IdentifiantEnProduction(ByVal sIdentifiant As String) As Boolean
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur par défaut
        IdentifiantEnProduction = True

        Try
            'Définir la requête SQL pour retourner le nombre de classes d'un identifiant en production
            sQueryString = "SELECT COUNT(DISTINCT A.IDENTIFIANT)" _
                         & "  FROM F502_PS A, F503_TR B" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.IDENTIFIANT='" & sIdentifiant & "' AND A.E_PLSNRC='P'" _
                         & "   AND A.NO_MAP=B.NO_MAP AND (A.NOTE LIKE '%#" & gsTypeTravail & "%' OR B.TY_TRAV='" & gsTypeTravail & "')"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Indique si des classes d'un identifiant sont en production
            IdentifiantEnProduction = CInt(qCommand.ExecuteScalar) = 1

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de définir le numéro de mise au programme à partir d'un numéro de non-conformité, du type de produit et d'un identifiant.
    '''</summary>
    ''' 
    '''<param name="sNoNc">Contient le numéro de non-conformité.</param>
    '''<param name="sIdentifiant">Contient l'identifiant en production.</param>
    ''' 
    '''<returns>"Integer" contenant le numéro de mise au programme, -1 sinon.</returns>
    ''' 
    Private Function DefinirNoMapEnProduction(ByVal sNoNc As String, ByVal sIdentifiant As String) As Integer
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur par défaut
        DefinirNoMapEnProduction = -1

        Try
            'Définir la requête SQL pour définir le NO_MAP d'un identifiant qui est en production
            sQueryString = "SELECT DISTINCT A.NO_MAP" _
                         & "  FROM F502_PS A, F502_NC B" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.IDENTIFIANT='" & sIdentifiant & "' AND A.E_PLSNRC='P'" _
                         & "   AND A.NO_MAP=B.NO_MAP AND B.NO_NC='" & sNoNc & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'vérifier si une valeur est présente
            If qReader.HasRows Then
                'Lire chaque ligne du résultat de la requête SQL
                qReader.Read()

                'Définir le NO_MAP d'un identifiant qui est en production
                DefinirNoMapEnProduction = CInt(qReader.GetValue(0))
            End If

        Catch ex As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de définir le numéro de mise au programme à partir d'un identifiant, du type de produit et du type de travail.
    '''</summary>
    ''' 
    '''<param name="sIdentifiant">Contient l'identifiant en production.</param>
    ''' 
    '''<returns>"Integer" contenant le numéro de mise au programme, -1 sinon.</returns>
    ''' 
    Private Function DefinirNoMapEnProduction(ByVal sIdentifiant As String) As Integer
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur par défaut
        DefinirNoMapEnProduction = -1

        Try
            'Définir la requête SQL pour définir le NO_MAP d'un identifiant qui est en production
            sQueryString = "SELECT DISTINCT A.NO_MAP" _
                         & "  FROM F502_PS A, F503_TR B" _
                         & " WHERE A.TY_PRODUIT='" & gsTypeProduit & "' AND A.IDENTIFIANT='" & sIdentifiant & "' AND A.E_PLSNRC='P'" _
                         & "   AND A.NO_MAP=B.NO_MAP(+) AND (A.NOTE LIKE '%#" & gsTypeTravail & "%' OR B.TY_TRAV='" & gsTypeTravail & "')"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'vérifier si une valeur est présente
            If qReader.HasRows Then
                'Lire chaque ligne du résultat de la requête SQL
                qReader.Read()

                'Définir le NO_MAP d'un identifiant qui est en production
                DefinirNoMapEnProduction = CInt(qReader.GetValue(0))
            End If

        Catch ex As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet de créer un nouveau numéro de mise au programme.
    '''</summary>
    ''' 
    '''<returns>"Integer" correspondant au nouveau numéro de mise au programme.</returns>
    ''' 
    Private Function CreerNouveauNoMap() As Integer
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur par défaut
        CreerNouveauNoMap = -1

        Try
            'Extraire la norme
            sQueryString = "SELECT SEQ502PS_NO_MAP.NEXTVAL from dual"

            'Commande pour créer un nouveau no_map
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Extraire le no_map
            CreerNouveauNoMap = CInt(qCommand.ExecuteScalar)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire le numéro des normes par défaut.
    '''</summary>
    ''' 
    '''<returns>"String" correspondant au numéro des normes par défaut.</returns>
    ''' 
    Private Function ExtraireNormesDefaut() As String
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.

        'Définir la valeur par défaut
        ExtraireNormesDefaut = ""

        Try
            'Extraire la norme
            sQueryString = "SELECT DF_STRING FROM F010_DP WHERE TY_PRODUIT = '" & gsTypeProduit & "' AND NOM_CHAMP = 'normes'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            ExtraireNormesDefaut = CStr(qCommand.ExecuteScalar)

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'indiquer si l'accès est autorisé d'un usager pour une liste de codes de groupe de privilège.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sListeCodesGroupe">Contient la liste des codes de groupe de privilège à vérifier.</param>
    ''' 
    '''<returns>"Boolean" qui permet d'indiquer si l'accès est autorisé.</returns>
    ''' 
    Private Function AccesAutoriser(ByVal sUsager As String, ByVal sListeCodesGroupe As String) As Boolean
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing  'Objet utilisé pour exécuter la requête SQL.
        Dim sQueryString As String = Nothing    'Requête SQL utilisée.
        Dim iNbGrpLst As Integer = -1           'Contient le nombre de codes de groupe dans la liste
        Dim iNbGrp As Integer = -1              'Contient le nombre de codes de groupe trouvés

        'Définir la valeur par défaut
        AccesAutoriser = True

        Try
            'Commande pour extraire le nombre de codes de groupe trouvés
            sQueryString = "SELECT COUNT(CD_GRP) FROM F007_UG WHERE CD_USER='" & sUsager & "' AND CD_GRP IN ('" & sListeCodesGroupe.Replace(",", "','") & "')"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Extraire le nombre de codes de groupe dans la liste
            iNbGrpLst = sListeCodesGroupe.Split(CChar(",")).Length

            'Extraire le nombre de codes de groupe trouvés
            iNbGrp = CInt(qCommand.ExecuteScalar.ToString)

            'Vérifier si l'accès est autorisé
            AccesAutoriser = iNbGrp = iNbGrpLst

        Catch ex As Exception
            Throw
        Finally
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            sQueryString = Nothing
        End Try
    End Function

    '''<summary>
    ''' Routine qui permet d'envoyer un courriel de fin de non-conformité.
    '''</summary>
    ''' 
    '''<param name="sUsager">Contient le nom de l'usager.</param>
    '''<param name="sNoNc">Contient le numéro de la non-conformité.</param>
    '''<param name="sResponsable">Contient le nom des responsables de la non-conformité.</param>
    ''' 
    Private Sub EnvoyerCourriel(ByVal sUsager As String, ByVal sNoNc As String, ByVal sResponsable As String)
        'Déclarer les variables de travail
        Dim qCommand As OleDbCommand = Nothing      'Objet utilisé pour exécuter la requête SQL.
        Dim qReader As OleDbDataReader = Nothing    'Object utilisé pour lire le résultat de la requête SQL.
        Dim oProcess As Process = Nothing           'Contient un processus pour envoyer un courriel.
        Dim sQueryString As String = Nothing        'Requête SQL utilisée.
        Dim sCmd As String = Nothing                'Contient la commande pour envoyer un courriel.
        Dim sSujet As String = Nothing              'Contient le sujet du courriel.
        Dim sContenu As String = Nothing            'Contient le contenu du courriel.
        Dim sCourriel As String = Nothing           'Contient l'adresse courriel.

        Try
            'Définir le sujet du courriel
            sSujet = "Fermeture de la correction INSITU de la non-conformité #" & sNoNc

            'Définir le contenu du courriel
            sContenu = "Bonjour,\n\nTous les jeux de données associés à la non conformité #" & sNoNc & " sont maitenant corrigés.\n\n" & sUsager

            'Définir le nom de la commande pour envoyer le courriel
            sCmd = "S:\applications\cits\pro\py\EnvoyerCourriel.py -to " & sCourriel & " -subj " & sSujet & " -f " & sContenu & " -encodage utf-8"

            'Définir la requête SQL
            sQueryString = "SELECT DISTINCT ADR_EMAIL" _
                         & "  FROM F005_US" _
                         & " WHERE CD_USER IN ('" & sResponsable.Replace(",", "','") & "'"

            'Créer une nouvelle commande qui permet d'exécuter une SQL
            qCommand = New OleDbCommand(sQueryString, gqConnection)

            'Exécuter la requête SQL
            qReader = qCommand.ExecuteReader()

            'Lire chaque ligne du résultat de la requête SQL
            While qReader.Read()
                'Envoyer le courriel
                oProcess = Process.Start(Environment.GetEnvironmentVariable("python27"), sCmd)
            End While

            'Fermer l'objet de lecture
            qReader.Close()

        Catch erreur As Exception
            Throw
        Finally
            'Fermer l'objet de lecture
            If qReader IsNot Nothing Then qReader.Close()
            'Fermer la commande SQL
            If qCommand IsNot Nothing Then qCommand.Dispose()
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
            oProcess = Nothing
        End Try
    End Sub
#End Region
End Class

'''<summary>
''' Classe qui permet d'envoyer une exception spéciale.
'''</summary>
Public Class AnnulerExecutionException : Inherits ApplicationException
    Public Sub New()
        MyBase.New()
    End Sub
    Public Sub New(ByVal message As String)
        MyBase.New(message)
    End Sub
    Public Sub New(ByVal message As String, ByVal innerEx As Exception)
        MyBase.New(message, innerEx)
    End Sub
End Class
