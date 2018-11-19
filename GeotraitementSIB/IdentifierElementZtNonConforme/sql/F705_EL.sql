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
Table qui permet de contenir l''information sur les dépôts, partition, classes et éléments qui sont non-conformes pour une zone de transaction dans SIB.';

COMMENT ON COLUMN F705_EL.UPDT_FLD IS 'Champ système. Voir la description du domaine UPDT_FLD pour plus de détails.';

COMMENT ON COLUMN F705_EL.ETAMPE IS 'Champ système. Voir la description du domaine ETAMPE pour plus de détails.';

COMMENT ON COLUMN F705_EL.DT_C IS 'Champ système. Contient la date de création de l''enregistrement.';

COMMENT ON COLUMN F705_EL.DT_M IS 'Champ système. Contient la date de modification de l''enregistrement.';

COMMENT ON COLUMN F705_EL.NO_NC IS 'Numéro unique utilisé pour identifier et décrire une non-conformité sur des données.
Ce numéro contient 5 chiffres sous forme de caractères (exemple : 03054).';

COMMENT ON COLUMN F705_EL.CATALOGUE IS 'Nom du catalogue décrivant les éléments non-conformes.
Le catalogue contient l''information décrivant les dépôts, les partitions, les classes et les éléments.';

COMMENT ON COLUMN F705_EL.DEPOT IS 'Nom du dépôt dans lequel on retrouve les éléments non-conformes.
Le dépôt est un contenant dans lequel on retrouve les partitions, les classes et les éléments.';

COMMENT ON COLUMN F705_EL.PARTITION IS 'Nom de la partition dans lequel on retrouve les éléments non-conformes.
La partition correspond à un type de produit dans SIB et est contenue dans un dépôt';

COMMENT ON COLUMN F705_EL.CLASSE IS 'Nom de la classe dans lequel on retrouve les éléments non-conformes.
Une classe contient les attributs et les géométries des éléments.';

COMMENT ON COLUMN F705_EL.OBJET_ID IS 'Numéro qui permet d''identifier de façon unique dans une classe un élément non-conforme.
Ce numéro ne contient que des chiffres. La valeur 0 indique qu''il n''y a pas d''élément.';

COMMENT ON COLUMN F705_EL.ELEMENT_ID IS 'Valeur qui permet d''identifier de façon unique au monde un élément non-conforme.
Cette valeur est un UUID qui contient un mélange de chiffres et de caractères. La valeur NULL indique qu''il n'' y a pas d''éléments.';

COMMENT ON COLUMN F705_EL.ZT_ID_DEBUT IS 'Valeur qui permet d''identifier de façon unique une zone de traitement qui contient les éléments non-conformes non-corrigés.
Cette valeur contient un mélange de chiffres et de caractères.';

COMMENT ON COLUMN F705_EL.ZT_ID_FIN IS 'Valeur qui permet d''identifier de façon unique une zone de traitement qui contient les éléments non-conformes corrigés.
Cette valeur contient un mélange de chiffres et de caractères. La valeur NULL indique qu''il n'' y a pas encore de zone de traitement qui corrige l''élément non-conforme.';

COMMENT ON COLUMN F705_EL.DATE_TRAITEMENT IS 'Date de la correction de l''élément non-conforme.
Cette date contient l''année, le mois, le jour, l''heure, les minutes et les secondes (exemple : 2014-12-16 11:43:09)';


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