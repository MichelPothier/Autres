DROP VIEW V_NOM_CARTE_50000;

/* Formatted on 2014-12-01 13:43:13 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW V_NOM_CARTE_50000
(
          DATASET_NAME,
          NAME_ENG,
          NAME_FRA
)
AS
   SELECT MAP_NUMBER,
          UPPER(MAP_TITLE),
          UPPER(MAP_TITLE) 
     FROM CGNS3.MAPS_V@CGNSU_VIEW
    WHERE SCALE = 50000
      AND MAP_TITLE IS NOT NULL
 ORDER BY MAP_NUMBER;

COMMENT ON TABLE V_NOM_CARTE_50000 IS 'COMMENTAIRE:
Vue permettant de montrer les noms des cartes.';

CREATE OR REPLACE PUBLIC SYNONYM V_USAGERS FOR V_NOM_CARTE_50000;

GRANT SELECT ON V_NOM_CARTE_50000 TO MDDTN;

GRANT SELECT ON V_NOM_CARTE_50000 TO SIBLIRE;

GRANT SELECT ON V_NOM_CARTE_50000 TO SIBLIREDIFF;

GRANT SELECT ON V_NOM_CARTE_50000 TO SIBMAJ;