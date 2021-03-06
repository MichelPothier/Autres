DROP VIEW SIBDBA.V_ORIGINATOR;

/* Formatted on 2013/12/23 11:00:16 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW SIBDBA.V_ORIGINATOR
(
   TY_PRODUIT,
   IDENTIFIANT,
   ED,
   VER,
   ORIGINATOR,
   LIEN
)
AS
   SELECT TY_PRODUIT,
          IDENTIFIANT,
          ED,
          VER,
          ORIGINATOR,
          TY_PRODUIT || '-' || IDENTIFIANT || '-' || ED || '.' || VER
     FROM F235_OR;

COMMENT ON TABLE SIBDBA.V_ORIGINATOR IS 'COMMENTAIRE:
Vue permettant de montrer les métadonnées de type ORIGINATOR.';



CREATE OR REPLACE PUBLIC SYNONYM V_ORIGINATOR FOR SIBDBA.V_ORIGINATOR;


GRANT SELECT ON SIBDBA.V_ORIGINATOR TO MDDTN;

GRANT SELECT ON SIBDBA.V_ORIGINATOR TO SIBLIRE;

GRANT SELECT ON SIBDBA.V_ORIGINATOR TO SIBLIREDIFF;

GRANT SELECT ON SIBDBA.V_ORIGINATOR TO SIBMAJ;
