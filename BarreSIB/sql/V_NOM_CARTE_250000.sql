DROP VIEW V_NOM_CARTE_250000;

/* Formatted on 2014-12-01 15:16:47 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW V_NOM_CARTE_250000
(
   DATASET_NAME,
   NAME_ENG,
   NAME_FRA
)
AS
     SELECT SUBSTR (MAP_NUMBER, 0, 4), UPPER (MAP_TITLE), UPPER (MAP_TITLE)
       FROM CGNS3.MAPS_V@CGNSU_VIEW
      WHERE SCALE = 250000 AND MAP_TITLE IS NOT NULL
   ORDER BY MAP_NUMBER;

COMMENT ON TABLE V_NOM_CARTE_250000 IS 'COMMENTAIRE:
Vue permettant de montrer les noms des cartes.';



GRANT SELECT ON V_NOM_CARTE_250000 TO MDDTN;

GRANT SELECT ON V_NOM_CARTE_250000 TO SIBLIRE;

GRANT SELECT ON V_NOM_CARTE_250000 TO SIBLIREDIFF;

GRANT SELECT ON V_NOM_CARTE_250000 TO SIBMAJ;