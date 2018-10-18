DROP VIEW SIBDBA.V_METATADA_REFERENCE_INFO;

/* Formatted on 2013/12/23 10:58:16 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW SIBDBA.V_METATADA_REFERENCE_INFO
(
   TY_PRODUIT,
   IDENTIFIANT,
   ED,
   VER,
   DT_METADATA,
   STANDARD_NAME,
   STANDARD_VERSION,
   USE_CONSTRAINTS,
   ORGANISATION,
   PERSONNE,
   HOURS,
   NO_SEQ_MA,
   TYPE,
   ADDRESS,
   CITY,
   STATE,
   POSTAL,
   COUNTRY,
   NO_TEL,
   NO_FAX,
   EMAIL,
   LIEN
)
AS
   SELECT A.TY_PRODUIT,
          A.IDENTIFIANT,
          A.ED,
          A.VER,
          A.DT_METADATA,
          A.STANDARD_NAME,
          A.STANDARD_VERSION,
          A.USE_CONSTRAINTS,
          A.ORGANISATION,
          A.PERSONNE,
          A.HOURS,
          B.NO_SEQ_MA,
          B.TYPE,
          B.ADDRESS,
          B.CITY,
          B.STATE,
          B.POSTAL,
          B.COUNTRY,
          C.NO_TEL,
          D.NO_FAX,
          E.EMAIL,
          A.TY_PRODUIT || '-' || A.IDENTIFIANT || '-' || A.ED || '.' || A.VER
     FROM F235_MR A,
          F235_MA B,
          F235_MT C,
          F235_MX D,
          F235_ME E
    WHERE     A.TY_PRODUIT = B.TY_PRODUIT(+)
          AND A.IDENTIFIANT = B.IDENTIFIANT(+)
          AND A.ED = B.ED(+)
          AND A.VER = B.VER(+)
          AND A.TY_PRODUIT = C.TY_PRODUIT(+)
          AND A.IDENTIFIANT = C.IDENTIFIANT(+)
          AND A.ED = C.ED(+)
          AND A.VER = C.VER(+)
          AND A.TY_PRODUIT = D.TY_PRODUIT(+)
          AND A.IDENTIFIANT = D.IDENTIFIANT(+)
          AND A.ED = D.ED(+)
          AND A.VER = D.VER(+)
          AND A.TY_PRODUIT = E.TY_PRODUIT(+)
          AND A.IDENTIFIANT = E.IDENTIFIANT(+)
          AND A.ED = E.ED(+)
          AND A.VER = E.VER(+);

COMMENT ON TABLE SIBDBA.V_METATADA_REFERENCE_INFO IS 'COMMENTAIRE:
Vue permettant de montrer les m�tadonn�es de type METATADA_REFERENCE_INFO.';



CREATE OR REPLACE PUBLIC SYNONYM V_METATADA_REFERENCE_INFO FOR SIBDBA.V_METATADA_REFERENCE_INFO;


GRANT SELECT ON SIBDBA.V_METATADA_REFERENCE_INFO TO MDDTN;

GRANT SELECT ON SIBDBA.V_METATADA_REFERENCE_INFO TO SIBLIRE;

GRANT SELECT ON SIBDBA.V_METATADA_REFERENCE_INFO TO SIBLIREDIFF;

GRANT SELECT ON SIBDBA.V_METATADA_REFERENCE_INFO TO SIBMAJ;