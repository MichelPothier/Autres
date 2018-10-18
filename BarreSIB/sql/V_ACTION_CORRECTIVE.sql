DROP VIEW SIBDBA.V_ACTION_CORRECTIVE;

/* Formatted on 2013/12/23 10:41:22 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW SIBDBA.V_ACTION_CORRECTIVE
(
   NO_NC,
   TY_PRODUIT,
   IDENTIFIANT,
   NO_ACTION,
   TITRE,
   NOM_SOURCE,
   TY_ACTION_ISO,
   ORIGINE_ACTION,
   DESCR,
   RESP_DESCR,
   CAUSE,
   DATE_SAISIE,
   TRAITEMENT,
   DATE_TRAITEMENT,
   SUIVI_TRAIT,
   RESP_CORR,
   ECHEANCE_INIT,
   RESP_SUIVI,
   DATE_FERMETURE,
   DOC_CONNEXE
)
AS
   SELECT F705_PR.NO_NC,
          TY_PRODUIT,
          IDENTIFIANT,
          F701_AC.NO_ACTION,
          TITRE,
          NOM_SOURCE,
          TY_ACTION_ISO,
          ORIGINE_ACTION,
          DESCR,
          RESP_DESCR,
          CAUSE,
          DATE_SAISIE,
          TRAITEMENT,
          DATE_TRAITEMENT,
          SUIVI_TRAIT,
          RESP_CORR,
          ECHEANCE_INIT,
          RESP_SUIVI,
          DATE_FERMETURE,
          DOC_CONNEXE
     FROM F701_AC, F704_LI, F705_PR
    WHERE     F701_AC.NO_ACTION = F704_LI.NO_ACTION
          AND F704_LI.NO_NC = F705_PR.NO_NC
          AND TY_LIEN = 'AC';

COMMENT ON TABLE SIBDBA.V_ACTION_CORRECTIVE IS 'COMMENTAIRE:
Vue permettant de montrer les actions correctives.';



CREATE OR REPLACE PUBLIC SYNONYM V_ACTION_CORRECTIVE FOR SIBDBA.V_ACTION_CORRECTIVE;


GRANT SELECT ON SIBDBA.V_ACTION_CORRECTIVE TO MDDTN;

GRANT SELECT ON SIBDBA.V_ACTION_CORRECTIVE TO SIBLIRE;

GRANT SELECT ON SIBDBA.V_ACTION_CORRECTIVE TO SIBLIREDIFF;

GRANT SELECT ON SIBDBA.V_ACTION_CORRECTIVE TO SIBMAJ;