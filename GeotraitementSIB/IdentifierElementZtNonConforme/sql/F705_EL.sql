ALTER TABLE F705_EL DROP PRIMARY KEY CASCADE;

DROP TABLE F705_EL CASCADE CONSTRAINTS;

CREATE TABLE F705_EL
(
  UPDT_FLD             VARCHAR2(23 BYTE)               NOT NULL,
  ETAMPE               VARCHAR2(23 BYTE)               NOT NULL,
  DT_C                 DATE                            NOT NULL,
  DT_M                 DATE                            NOT NULL,
  NO_NC                VARCHAR2(5 BYTE)                NOT NULL,
  CATALOGUE            VARCHAR2(64 BYTE)               NOT NULL,
  DEPOT                VARCHAR2(16 BYTE)               NOT NULL,
  PARTITION            VARCHAR2(16 BYTE)               NOT NULL,
  CLASSE               VARCHAR2(64 BYTE)               NOT NULL,
  OBJET_ID             INTEGER                         NOT NULL,
  ELEMENT_ID           VARCHAR2(64 BYTE),
  ZT_ID_DEBUT          VARCHAR2(64 BYTE)               NOT NULL,
  ZT_ID_FIN            VARCHAR2(64 BYTE),
  DATE_TRAITEMENT      DATE
)
TABLESPACE USER_SIBDBA
RESULT_CACHE (MODE DEFAULT)
PCTUSED    0
PCTFREE    10
INITRANS   1
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            NEXT             1M
            MINEXTENTS       1
            MAXEXTENTS       UNLIMITED
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
            FLASH_CACHE      DEFAULT
            CELL_FLASH_CACHE DEFAULT
           )
LOGGING 
NOCOMPRESS 
NOCACHE
NOPARALLEL
MONITORING;

COMMENT ON TABLE F705_EL IS 'COMMENTAIRE:
Table qui permet de contenir l''information sur les d�p�ts, partition, classes et �l�ments qui sont non-conformes pour une zone de transaction dans SIB.';

COMMENT ON COLUMN F705_EL.UPDT_FLD IS 'Champ syst�me. Voir la description du domaine UPDT_FLD pour plus de d�tails.';

COMMENT ON COLUMN F705_EL.ETAMPE IS 'Champ syst�me. Voir la description du domaine ETAMPE pour plus de d�tails.';

COMMENT ON COLUMN F705_EL.DT_C IS 'Champ syst�me. Contient la date de cr�ation de l''enregistrement.';

COMMENT ON COLUMN F705_EL.DT_M IS 'Champ syst�me. Contient la date de modification de l''enregistrement.';

COMMENT ON COLUMN F705_EL.NO_NC IS 'Num�ro unique utilis� pour identifier et d�crire une non-conformit� sur des donn�es.
Ce num�ro contient 5 chiffres sous forme de caract�res (exemple : 03054).';

COMMENT ON COLUMN F705_EL.CATALOGUE IS 'Nom du catalogue d�crivant les �l�ments non-conformes.
Le catalogue contient l''information d�crivant les d�p�ts, les partitions, les classes et les �l�ments.';

COMMENT ON COLUMN F705_EL.DEPOT IS 'Nom du d�p�t dans lequel on retrouve les �l�ments non-conformes.
Le d�p�t est un contenant dans lequel on retrouve les partitions, les classes et les �l�ments.';

COMMENT ON COLUMN F705_EL.PARTITION IS 'Nom de la partition dans lequel on retrouve les �l�ments non-conformes.
La partition correspond � un type de produit dans SIB et est contenue dans un d�p�t';

COMMENT ON COLUMN F705_EL.CLASSE IS 'Nom de la classe dans lequel on retrouve les �l�ments non-conformes.
Une classe contient les attributs et les g�om�tries des �l�ments.';

COMMENT ON COLUMN F705_EL.OBJET_ID IS 'Num�ro qui permet d''identifier de fa�on unique dans une classe un �l�ment non-conforme.
Ce num�ro ne contient que des chiffres. La valeur 0 indique qu''il n''y a pas d''�l�ment.';

COMMENT ON COLUMN F705_EL.ELEMENT_ID IS 'Valeur qui permet d''identifier de fa�on unique au monde un �l�ment non-conforme.
Cette valeur est un UUID qui contient un m�lange de chiffres et de caract�res. La valeur NULL indique qu''il n'' y a pas d''�l�ments.';

COMMENT ON COLUMN F705_EL.ZT_ID_DEBUT IS 'Valeur qui permet d''identifier de fa�on unique une zone de traitement qui contient les �l�ments non-conformes non-corrig�s.
Cette valeur contient un m�lange de chiffres et de caract�res.';

COMMENT ON COLUMN F705_EL.ZT_ID_FIN IS 'Valeur qui permet d''identifier de fa�on unique une zone de traitement qui contient les �l�ments non-conformes corrig�s.
Cette valeur contient un m�lange de chiffres et de caract�res. La valeur NULL indique qu''il n'' y a pas encore de zone de traitement qui corrige l''�l�ment non-conforme.';

COMMENT ON COLUMN F705_EL.DATE_TRAITEMENT IS 'Date de la correction de l''�l�ment non-conforme.
Cette date contient l''ann�e, le mois, le jour, l''heure, les minutes et les secondes (exemple : 2014-12-16 11:43:09)';


CREATE UNIQUE INDEX PK_F705_EL ON F705_EL
(NO_NC, CATALOGUE, DEPOT, PARTITION, CLASSE, OBJET_ID, ZT_ID_DEBUT)
LOGGING
TABLESPACE USER_SIBDBA
PCTFREE    10
INITRANS   2
MAXTRANS   255
STORAGE    (
            INITIAL          64K
            NEXT             1M
            MINEXTENTS       1
            MAXEXTENTS       UNLIMITED
            PCTINCREASE      0
            BUFFER_POOL      DEFAULT
            FLASH_CACHE      DEFAULT
            CELL_FLASH_CACHE DEFAULT
           )
NOPARALLEL;


CREATE OR REPLACE PUBLIC SYNONYM F705_EL FOR F705_EL;


ALTER TABLE F705_EL ADD (
  CONSTRAINT PK_F705_EL
  PRIMARY KEY
  (NO_NC, CATALOGUE, DEPOT, PARTITION, CLASSE, OBJET_ID, ZT_ID_DEBUT)
  USING INDEX PK_F705_EL
  ENABLE VALIDATE);

GRANT SELECT ON F705_EL TO MDDTN;

GRANT DELETE, INSERT, SELECT, UPDATE ON F705_EL TO SIBISO;

GRANT SELECT ON F705_EL TO SIBLIRE;

GRANT SELECT ON F705_EL TO SIBLIREDIFF;

GRANT DELETE, INSERT, SELECT, UPDATE ON F705_EL TO SIBMAJ;

GRANT DELETE, INSERT, SELECT, UPDATE ON F705_EL TO SIBMAJISO;

COMMIT;