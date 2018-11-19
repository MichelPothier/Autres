ALTER TABLE F710_ZT DROP PRIMARY KEY CASCADE;

DROP TABLE F710_ZT CASCADE CONSTRAINTS;

CREATE TABLE F710_ZT
(
  UPDT_FLD              VARCHAR2(23 BYTE)               NOT NULL,
  ETAMPE                VARCHAR2(23 BYTE)               NOT NULL,
  DT_C                  DATE                            NOT NULL,
  DT_M                  DATE                            NOT NULL,
  NO_NC                 VARCHAR2(5 BYTE)                NOT NULL,
  ZT_ID          	    VARCHAR2(64 BYTE)               NOT NULL,
  X_MIN          	    NUMBER               			NOT NULL,
  X_MAX          	    NUMBER               			NOT NULL,
  Y_MIN          	    NUMBER               			NOT NULL,
  Y_MAX          	    NUMBER               			NOT NULL,
  SHAPE_WKT				CLOB							NOT NULL
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

COMMENT ON TABLE F710_ZT IS 'COMMENTAIRE:
Table qui permet de contenir l''information g�ographique des zones de transaction de non-conformit� dans SIB.';

COMMENT ON COLUMN F710_ZT.UPDT_FLD IS 'Champ syst�me. Voir la description du domaine UPDT_FLD pour plus de d�tails.';

COMMENT ON COLUMN F710_ZT.ETAMPE IS 'Champ syst�me. Voir la description du domaine ETAMPE pour plus de d�tails.';

COMMENT ON COLUMN F710_ZT.DT_C IS 'Champ syst�me. Contient la date de cr�ation de l''enregistrement.';

COMMENT ON COLUMN F710_ZT.DT_M IS 'Champ syst�me. Contient la date de modification de l''enregistrement.';

COMMENT ON COLUMN F710_ZT.NO_NC IS 'Num�ro unique utilis� pour identifier et d�crire une non-conformit� sur des donn�es.
Ce num�ro contient 5 chiffres sous forme de caract�res (exemple : 03054).';

COMMENT ON COLUMN F710_ZT.ZT_ID IS 'Valeur qui permet d''identifier de fa�on unique une zone de traitement qui contient les �l�ments non-conformes.
Cette valeur contient un m�lange de chiffres et de caract�res.';

COMMENT ON COLUMN F710_ZT.X_MIN IS 'Valeur minimum de la coordonn�e g�ographique X (latitude) de la ZT de non-conformit�.';

COMMENT ON COLUMN F710_ZT.X_MAX IS 'Valeur maximum de la coordonn�e g�ographique X (latitude) de la ZT de non-conformit�.';

COMMENT ON COLUMN F710_ZT.Y_MIN IS 'Valeur minimum de la coordonn�e g�ographique Y (longitude) de la ZT de non-conformit�.';

COMMENT ON COLUMN F710_ZT.Y_MAX IS 'Valeur maximum de la coordonn�e g�ographique Y (longitude) de la ZT de non-conformit�.';

COMMENT ON COLUMN F710_ZT.SHAPE_WKT IS 'G�om�trie de type MULTIPOLYGON de la ZT.
Cette g�om�trie est en format WKT pour une classe de type polygon ESRI';


CREATE UNIQUE INDEX PK_F710_ZT ON F710_ZT
(ZT_ID)
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


CREATE OR REPLACE PUBLIC SYNONYM F710_ZT FOR F710_ZT;


ALTER TABLE F710_ZT ADD (
  CONSTRAINT PK_F710_ZT
  PRIMARY KEY
  (ZT_ID)
  USING INDEX PK_F710_ZT
  ENABLE VALIDATE);

GRANT SELECT ON F710_ZT TO MDDTN;

GRANT DELETE, INSERT, SELECT, UPDATE ON F710_ZT TO SIBISO;

GRANT SELECT ON F710_ZT TO SIBLIRE;

GRANT SELECT ON F710_ZT TO SIBLIREDIFF;

GRANT DELETE, INSERT, SELECT, UPDATE ON F710_ZT TO SIBMAJ;

GRANT DELETE, INSERT, SELECT, UPDATE ON F710_ZT TO SIBMAJISO;

COMMIT;