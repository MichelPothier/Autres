DROP VIEW SIBDBA.V_PROCESS_STEP;

/* Formatted on 2014-10-01 16:55:56 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW SIBDBA.V_PROCESS_STEP
(
   TY_PRODUIT,
   IDENTIFIANT,
   ED,
   VER,
   NO_SEQ,
   DESCRIPTION,
   DT_PROCESS,
   NO_MEP,
   ABR,
   LIEN
)
AS
   SELECT A.TY_PRODUIT,
          A.IDENTIFIANT,
          A.ED,
          A.VER,
          cast(A.NO_SEQ as number(5)),
          A.DESCRIPTION,
          A.DT_PROCESS,
          cast(A.NO_MEP as number(10)),
          NVL(B.ABR, '-'),
          A.TY_PRODUIT || '-' || A.IDENTIFIANT || '-' || A.ED || '.' || A.VER
     FROM F235_PS A, F235_SU B
    WHERE     A.TY_PRODUIT = B.TY_PRODUIT(+)
          AND A.IDENTIFIANT = B.IDENTIFIANT(+)
          AND A.ED = B.ED(+)
          AND A.VER = B.VER(+)
          AND A.NO_SEQ = B.NO_SEQ(+);

COMMENT ON TABLE SIBDBA.V_PROCESS_STEP IS 'COMMENTAIRE:
Vue permettant de montrer les métadonnées de type PROCESS STEP.';



CREATE OR REPLACE PUBLIC SYNONYM V_PROCESS_STEP FOR SIBDBA.V_PROCESS_STEP;


GRANT SELECT ON SIBDBA.V_PROCESS_STEP TO MDDTN;

GRANT SELECT ON SIBDBA.V_PROCESS_STEP TO SIBLIRE;

GRANT SELECT ON SIBDBA.V_PROCESS_STEP TO SIBLIREDIFF;

GRANT SELECT ON SIBDBA.V_PROCESS_STEP TO SIBMAJ;
