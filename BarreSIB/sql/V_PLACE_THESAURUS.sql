DROP VIEW SIBDBA.V_PLACE_THESAURUS;

/* Formatted on 2013/12/23 11:01:14 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW SIBDBA.V_PLACE_THESAURUS
(
   TY_PRODUIT,
   IDENTIFIANT,
   ED,
   VER,
   NO_SEQ,
   THESAURUS,
   NO_SEQ_KEYWORD,
   KEYWORD,
   LIEN
)
AS
   SELECT A.TY_PRODUIT,
          A.IDENTIFIANT,
          A.ED,
          A.VER,
          A.NO_SEQ,
          A.THESAURUS,
          B.NO_SEQ,
          B.KEYWORD,
          A.TY_PRODUIT || '-' || A.IDENTIFIANT || '-' || A.ED || '.' || A.VER
     FROM F235_PK A, F235_KT B
    WHERE     A.TY_PRODUIT = B.TY_PRODUIT
          AND A.IDENTIFIANT = B.IDENTIFIANT
          AND A.ED = B.ED
          AND A.VER = B.VER
          AND A.THESAURUS = B.THESAURUS;

COMMENT ON TABLE SIBDBA.V_PLACE_THESAURUS IS 'COMMENTAIRE:
Vue permettant de montrer les métadonnées de type PLACE_THESAURUS.';



CREATE OR REPLACE PUBLIC SYNONYM V_PLACE_THESAURUS FOR SIBDBA.V_PLACE_THESAURUS;


GRANT SELECT ON SIBDBA.V_PLACE_THESAURUS TO MDDTN;

GRANT SELECT ON SIBDBA.V_PLACE_THESAURUS TO SIBLIRE;

GRANT SELECT ON SIBDBA.V_PLACE_THESAURUS TO SIBLIREDIFF;

GRANT SELECT ON SIBDBA.V_PLACE_THESAURUS TO SIBMAJ;
