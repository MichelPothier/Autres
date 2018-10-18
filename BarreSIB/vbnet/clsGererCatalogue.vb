Imports System.Data.OleDb

'**
'Nom de la composante : clsGererCatalogue.vb
'
'''<summary>
''' Librairie de Classe qui permet de gérer l'information d'une base de données des catalogues.
'''</summary>
'''
'''<remarks>
'''Cette librairie est utilisable pour les outils interactifs ou Batch dans ArcMap (ArcGis de ESRI).
'''
'''Auteur : Michel Pothier
'''Date : 26 mars 2015
'''</remarks>
''' 
Public Class clsGererCatalogue
    'Déclarer les variables globales
    '''<summary>Nom de l'environnement de travail (instance de la BD) [CATREL_PRO/CATREL_TST].</summary>
    Protected gsEnv As String
    '''<summary>Numéro du type de catalogue (FEAT_CATAL_TYPE).</summary>
    Protected giCatalogue As Integer

#Region "Propriétés"
    '''<summary>
    ''' Propriété qui permet de définir et retourner l'environnement de travail (instance de la BD).
    '''</summary>
    ''' 
    Public Property Env() As String
        Get
            Env = gsEnv
        End Get
        Set(ByVal value As String)
            gsEnv = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de retourner le texte de connexion à la Bd des catalogues.
    '''</summary>
    ''' 
    Public ReadOnly Property ConnectionString() As String
        Get
            'Définir le texte de connexion à la BD des catalogues
            ConnectionString = "PROVIDER=MSDAORA;" & "DATA SOURCE=" & gsEnv & ";" & "User Id=bdg_view;" & "Password=bdg_view;"
        End Get
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner le numéro du type de catalogue (FEAT_CATAL_TYPE).
    '''</summary>
    ''' 
    Public Property NumeroCatalogue() As Integer
        Get
            NumeroCatalogue = giCatalogue
        End Get
        Set(ByVal value As Integer)
            giCatalogue = value
        End Set
    End Property

    '''<summary>
    ''' Propriété qui permet de définir et retourner le nom du type de catalogue (FEAT_CATAL_TYPE).
    '''</summary>
    ''' 
    Public Property NomCatalogue() As String
        Get
            'Définir le nom du catalogue à partir du numéro du catalogue
            NomCatalogue = ExtraireListeCatalogue.Item(giCatalogue.ToString)
        End Get
        Set(ByVal value As String)
            'Variable utilisée pour extraire le Key à partir de la valeur
            Dim pair As KeyValuePair(Of String, String)
            'Traiter toutes les valeurs du dictionnaire
            For Each pair In ExtraireListeCatalogue()
                'Vérifier si la valeur correspond
                If pair.Value = value Then
                    'Définir le numéro du catalogue à partir du nom du catalogue
                    giCatalogue = CInt(pair.Key)
                    'Sortir de la boucle
                    Exit For
                End If
            Next
        End Set
    End Property
#End Region

#Region "Routine et fonction publiques"
    '''<summary>
    '''Routine qui permet d'initialiser la classe pour gérer l'information des catalogues.
    '''</summary>
    '''
    Public Sub New(Optional ByVal sEnv As String = "CATREL_PRO", Optional ByVal iCatalogue As Integer = 1)
        'Définir l'environnement de travail
        gsEnv = sEnv
        'Définir le numéro du type de catalogue
        giCatalogue = iCatalogue

    End Sub

    '''<summary>
    '''Routine qui permet de vider la mémoire des objets de la classe.
    '''</summary>
    '''
    Protected Overrides Sub finalize()
        'Vider la mémoire
        'gpMap = Nothing
    End Sub

    '''<summary>
    ''' Permet d'indiquer si la BD des catalogues est valide.
    '''</summary>
    ''' 
    '''<returns>"Boolean" pour indiquer si la BD est valide (True) ou invalide (False).</returns>
    ''' 
    Public Function EstValide() As Boolean
        'Déclarer les variables de travail
        Dim sQueryString As String      'Requête utilisée pour valider la BD des catalogues
        Dim qCommand As OleDbCommand    'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader  'Object utilisé pour lire le résultat de la requête

        'Indique que le catalogue est invalide par défaut
        EstValide = False

        Try
            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(ConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL de validation du catalogue
                sQueryString = "SELECT COUNT(FEAT_CATAL_TYPE)" _
                             & "  FROM FEAT_CATALOGUE" _
                             & " WHERE FEAT_CATAL_TYPE=" & giCatalogue.ToString

                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)

                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire le résultat de la requête SQL
                qReader.Read()

                'Vérifier si un résultat est présent
                If CInt(qReader.GetValue(0)) > 0 Then
                    'Indique que le catalogue est valide
                    EstValide = True
                Else
                    'Indique que le catalogue est invalide
                    EstValide = False
                End If

                'Fermer la lecture
                qReader.Close()

                'Fermer la connexion
                qConnection.Close()
            End Using

        Catch erreur As Exception

        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la liste des environnements de travail.
    '''</summary>
    ''' 
    '''<returns>"Dictionary(Of String, String)" correspondant à la liste des environnements possibles (Env, Env).</returns>
    ''' 
    Public Function ExtraireListeEnv() As Dictionary(Of String, String)
        'Définir la valeur de retour par défaut
        ExtraireListeEnv = New Dictionary(Of String, String)

        Try
            'Ajouter l'environnement du catalogue de production
            ExtraireListeEnv.Add("CATREL_PRO", "CATREL_PRO")
            'Ajouter l'environnement du catalogue de test
            ExtraireListeEnv.Add("CATREL_TST", "CATREL_TST")

        Catch erreur As Exception
            Throw
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la liste des catalogues possibles.
    '''</summary>
    ''' 
    '''<returns>"Dictionary(Of String, Integer)" correspondant à la liste des catalogues possibles (nomCatalogue, numeroCatalogue).</returns>
    ''' 
    Public Function ExtraireListeCatalogue() As Dictionary(Of String, String)
        'Définir la valeur de retour par défaut
        ExtraireListeCatalogue = New Dictionary(Of String, String)

        Try
            'Ajouter tous les catalogues possibles
            ExtraireListeCatalogue.Add("0", "MAIN")
            ExtraireListeCatalogue.Add("1", "BDG")
            ExtraireListeCatalogue.Add("2", "GEO")
            ExtraireListeCatalogue.Add("3", "PROD")
            ExtraireListeCatalogue.Add("4", "BDRS_MAIN")
            ExtraireListeCatalogue.Add("5", "BDRS_MGT")
            ExtraireListeCatalogue.Add("10", "BDRS_MGT_MISST_50K")
            ExtraireListeCatalogue.Add("11", "BDRS_MGT_MISST_250K")
            ExtraireListeCatalogue.Add("12", "BDRS_MGT_MISST_GE")
            ExtraireListeCatalogue.Add("13", "BDRS_MGT_MISST_ME")
            ExtraireListeCatalogue.Add("14", "BDRS_MGT_MISST_PE")
            ExtraireListeCatalogue.Add("15", "BDRS_MGT_MISST_Multi")
            ExtraireListeCatalogue.Add("20", "BDRS_EXPL_MISST_50K")
            ExtraireListeCatalogue.Add("21", "BDRS_EXPL_MISST_250K")
            ExtraireListeCatalogue.Add("22", "BDRS_EXPL_MISST_GE")
            ExtraireListeCatalogue.Add("23", "BDRS_EXPL_MISST_ME")
            ExtraireListeCatalogue.Add("24", "BDRS_EXPL_MISST_PE")
            ExtraireListeCatalogue.Add("25", "BDRS_EXPL_MISST_Multi")
            ExtraireListeCatalogue.Add("30", "BDRS_MGT_ECSCF")

        Catch erreur As Exception
            Throw
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la liste des sous-catalogues possibles.
    '''</summary>
    ''' 
    '''<returns>"Dictionary(Of String, Integer)" correspondant à la liste des sous-catalogues possibles (nomSousCatalogue, numeroSousCatalogue).</returns>
    ''' 
    Public Function ExtraireListeSousCatalogue() As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim sQueryString As String      'Requête utilisée pour valider la BD des catalogues
        Dim qCommand As OleDbCommand    'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader  'Object utilisé pour lire le résultat de la requête

        'Définir la valeur de retour par défaut
        ExtraireListeSousCatalogue = New Dictionary(Of String, String)

        Try
            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(ConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL
                sQueryString = "SELECT FEAT_CATAL_ID, FEAT_CATAL_NAME_FR, FEAT_CATAL_NAME_EN, FEAT_CATAL_BDG_VER_NUM" _
                             & "  FROM FEAT_CATALOGUE" _
                             & " WHERE FEAT_CATAL_TYPE=" & giCatalogue.ToString

                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)

                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Ajouter le sous-catalogue
                    ExtraireListeSousCatalogue.Add(qReader.GetValue(0).ToString, qReader.GetString(1) & " / " & qReader.GetString(2) & " (" & qReader.GetString(3) & ")")
                End While

                'Fermer la lecture
                qReader.Close()

                'Fermer la connexion
                qConnection.Close()
            End Using

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la liste des classes possibles.
    '''</summary>
    ''' 
    '''<param name="iSousCatalogue">Numéro du sous-catalogue (FEAT_CATAL_ID), -1='Tous les sous-catalogues'.</param>
    ''' 
    '''<returns>"Collection" correspondant à la liste des classes possibles (nomClasse, nomClasse).</returns>
    ''' 
    Public Function ExtraireListeClasse(Optional ByVal iSousCatalogue As Integer = -1) As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim sQueryString As String      'Requête utilisée pour valider la BD des catalogues
        Dim qCommand As OleDbCommand    'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader  'Object utilisé pour lire le résultat de la requête

        'Définir la valeur de retour par défaut
        ExtraireListeClasse = New Dictionary(Of String, String)

        Try
            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(ConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL
                sQueryString = "SELECT DISTINCT B.FEAT_TYPE_NAME_DATABASE" _
                             & "  FROM FEAT_CATALOGUE A, FEAT_TYPE B" _
                             & " WHERE A.FEAT_CATAL_TYPE=" & giCatalogue.ToString _
                             & "   AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"
                'Vérifier si le sous-catalogue est spécifié
                If iSousCatalogue <> -1 Then
                    'Ajouter la condition du sous-catalogue dans la requête
                    sQueryString = sQueryString & " AND A.FEAT_CATAL_ID=" & iSousCatalogue.ToString
                End If

                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)

                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Ajouter la classe
                    ExtraireListeClasse.Add(qReader.GetString(0), qReader.GetString(0))
                End While

                'Fermer la lecture
                qReader.Close()

                'Fermer la connexion
                qConnection.Close()
            End Using

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la liste des codes spécifiques possibles.
    '''</summary>
    ''' 
    '''<param name="sClasse">Nom de la classe (FEAT_TYPE_NAME_DATABASE), ""='Toutes les classes'.</param>
    ''' 
    '''<returns>"Collection" correspondant à la liste des classes possibles (codeSpécifique, nomCodeSpécifique).</returns>
    ''' 
    Public Function ExtraireListeCodeSpecifique(Optional ByVal sClasse As String = "") As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim sQueryString As String      'Requête utilisée pour valider la BD des catalogues
        Dim qCommand As OleDbCommand    'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader  'Object utilisé pour lire le résultat de la requête

        'Définir la valeur de retour par défaut
        ExtraireListeCodeSpecifique = New Dictionary(Of String, String)

        Try
            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(ConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL
                sQueryString = "SELECT DISTINCT B.FEAT_TYPE_CODE_BD, B.FEAT_TYPE_NAME_FR" _
                             & "  FROM FEAT_CATALOGUE A, FEAT_TYPE B" _
                             & " WHERE A.FEAT_CATAL_TYPE=" & giCatalogue.ToString _
                             & "   AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK"

                'Vérifier si la classe est spécifiée
                If sClasse <> "" Then
                    'Ajouter la condition de la classe dans la requête
                    sQueryString = sQueryString & " AND B.FEAT_TYPE_NAME_DATABASE='" & sClasse.ToUpper() & "'"
                Else
                    'Ajouter la condition de la classe non nulle dans la requête
                    sQueryString = sQueryString & " AND B.FEAT_TYPE_NAME_DATABASE IS NOT NULL"
                End If

                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)

                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Ajouter le code spécifique
                    ExtraireListeCodeSpecifique.Add(qReader.GetValue(0).ToString, qReader.GetString(1))
                End While

                'Fermer la lecture
                qReader.Close()

                'Fermer la connexion
                qConnection.Close()
            End Using

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la liste des attributs possibles.
    '''</summary>
    ''' 
    '''<param name="iCodeSpecifique">Numéro du code spécifique (FEAT_TYPE_CODE_BD), -1='Tous les codes spécifiques'.</param>
    '''<param name="bAttributCode">Indique si on veut seulement les attributs codés, False='Tous les attributs', True='Seulement les attributs codés' .</param>
    ''' 
    '''<returns>"Dictionary(Of String, String)" correspondant à la liste des attributs possibles (nomAttribut, nomAttribut).</returns>
    ''' 
    Public Function ExtraireListeAttribut(Optional ByVal iCodeSpecifique As Integer = -1, Optional ByVal bAttributCode As Boolean = False) As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim sQueryString As String      'Requête utilisée pour valider la BD des catalogues
        Dim qCommand As OleDbCommand    'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader  'Object utilisé pour lire le résultat de la requête

        'Définir la valeur de retour par défaut
        ExtraireListeAttribut = New Dictionary(Of String, String)

        Try
            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(ConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL
                sQueryString = "SELECT DISTINCT D.FEAT_ATTR_NAME_DATABASE" _
                             & "  FROM FEAT_CATALOGUE A, FEAT_TYPE B, RELATION_FEAT_ATTR C,FEAT_ATTR D" _
                             & " WHERE A.FEAT_CATAL_TYPE=" & giCatalogue.ToString _
                             & "   AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID"

                'Vérifier si la classe est spécifiée
                If iCodeSpecifique <> -1 Then
                    'Ajouter la condition de la classe dans la requête
                    sQueryString = sQueryString & " AND B.FEAT_TYPE_CODE_BD=" & iCodeSpecifique.ToString
                End If

                'Vérifier si on veut seulement les attributs codés
                If bAttributCode Then
                    'Ajouter la condition pour extraire seulement les attributs codés
                    sQueryString = sQueryString & " AND D.FEAT_ATTR_DOMAIN_TYPE=-1"
                End If

                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)

                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Ajouter l'attribut
                    ExtraireListeAttribut.Add(qReader.GetString(0), qReader.GetString(0))
                End While

                'Fermer la lecture
                qReader.Close()

                'Fermer la connexion
                qConnection.Close()
            End Using

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
        End Try
    End Function

    '''<summary>
    ''' Fonction qui permet d'extraire la liste des valeurs d'attributs possibles.
    '''</summary>
    ''' 
    '''<param name="sClasse">Nom de la classe (FEAT_TYPE_NAME_DATABASE), ""='Toutes les classes'.</param>
    '''<param name="iCodeSpecifique">Numéro du code spécifique (FEAT_TYPE_CODE_BD), -1='Tous les codes spécifiques'.</param>
    '''<param name="sAttribut">Nom de l'attribut (FEAT_ATTR_NAME_DATABASE), ""='Tous les attributs'.</param>
    ''' 
    '''<returns>"Dictionary(Of String, String)" correspondant à la liste des valeurs d'attributs possibles (nomAttribut_codeValeur, nomValeur).</returns>
    ''' 
    Public Function ExtraireListeValeurAttribut(Optional ByVal sClasse As String = "", Optional ByVal iCodeSpecifique As Integer = -1, Optional ByVal sAttribut As String = "") As Dictionary(Of String, String)
        'Déclarer les variables de travail
        Dim sQueryString As String      'Requête utilisée pour valider la BD des catalogues
        Dim qCommand As OleDbCommand    'Objet utilisé pour exécuter la requête
        Dim qReader As OleDbDataReader  'Object utilisé pour lire le résultat de la requête

        'Définir la valeur de retour par défaut
        ExtraireListeValeurAttribut = New Dictionary(Of String, String)

        Try
            'Créer une nouvelle connexion
            Using qConnection As New OleDbConnection(ConnectionString)
                'Ouvrir la connexion
                qConnection.Open()

                'Définir la requête SQL
                sQueryString = "SELECT DISTINCT D.FEAT_ATTR_NAME_DATABASE, E.ATTR_VALUE_INTERNAL_CODE, E.ATTR_VALUE_LABEL_FR" _
                             & "  FROM FEAT_CATALOGUE A, FEAT_TYPE B, RELATION_FEAT_ATTR C,FEAT_ATTR D, FEAT_ATTR_VALUE E" _
                             & " WHERE A.FEAT_CATAL_TYPE=" & giCatalogue.ToString & " AND D.FEAT_ATTR_DOMAIN_TYPE=-1" _
                             & "   AND A.FEAT_CATAL_ID=B.FEAT_CATAL_FK AND B.FEAT_TYPE_ID=C.FEAT_TYPE_FK" _
                             & "   AND C.FEAT_ATTR_FK=D.FEAT_ATTR_ID AND D.FEAT_ATTR_ID=E.FEAT_ATTR_FK"

                'Vérifier si la classe est spécifiée
                If sClasse <> "" Then
                    'Ajouter la condition de la classe dans la requête
                    sQueryString = sQueryString & " AND B.FEAT_TYPE_NAME_DATABASE='" & sClasse.ToUpper() & "'"
                End If

                'Vérifier si la classe est spécifiée
                If iCodeSpecifique <> -1 Then
                    'Ajouter la condition de la classe dans la requête
                    sQueryString = sQueryString & " AND B.FEAT_TYPE_CODE_BD=" & iCodeSpecifique.ToString
                End If

                'Vérifier si l'attribut est spécifié
                If sAttribut <> "" Then
                    'Ajouter la condition de la classe dans la requête
                    sQueryString = sQueryString & " AND D.FEAT_ATTR_NAME_DATABASE='" & sAttribut.ToUpper() & "'"
                End If

                'Créer une nouvelle commande qui permet d'exécuter une SQL
                qCommand = New OleDbCommand(sQueryString, qConnection)

                'Exécuter la requête SQL
                qReader = qCommand.ExecuteReader()

                'Lire chaque ligne du résultat de la requête SQL
                While qReader.Read()
                    'Ajouter la valeur d'attribut
                    ExtraireListeValeurAttribut.Add(qReader.GetString(0) & "_" & qReader.GetValue(1).ToString, qReader.GetString(2))
                End While

                'Fermer la lecture
                qReader.Close()

                'Fermer la connexion
                qConnection.Close()
            End Using

        Catch erreur As Exception
            Throw
        Finally
            'Vider la mémoire
            qCommand = Nothing
            qReader = Nothing
        End Try
    End Function

#End Region

#Region "Routine et fonction privées"

#End Region
End Class
