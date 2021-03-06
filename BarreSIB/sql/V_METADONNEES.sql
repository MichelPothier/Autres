DROP VIEW SIBDBA.V_METADONNEES;

/* Formatted on 2013/12/23 10:57:40 (QP5 v5.240.12305.39446) */
CREATE OR REPLACE FORCE VIEW SIBDBA.V_METADONNEES
(
   TY_PRODUIT,
   IDENTIFIANT,
   ED,
   VER,
   JEU_COUR,
   DT_MEP,
   VER_META,
   ISSUE_ID,
   GEO_DATA_PRESENT_FORM,
   DT_CONTENT_BEG,
   DT_CONTENT_END,
   CURRENTNESS_REF,
   STATUS_PROGRESS,
   MAINTENANCE_FREQ,
   CLOUD_COVER,
   CLOUD_COVER_2,
   DATASET_CREDIT,
   NATIVE_DATASET_ENV,
   SERIES_NAME,
   DT_PUBLICATION,
   PUBLICATION_PLACE,
   PUBLISHER,
   ABSTRACT_DESC,
   PURPOSE_DESC,
   SUPPLEMENTAL_INFO,
   WESTBC,
   EASTBC,
   SOUTHBC,
   NORTHBC,
   ACCESS_CONSTRAINTS,
   USE_CONSTRAINTS,
   ATTRIBUTE_ACC_REP,
   LOGICAL_CONSIST_REP,
   COMPLETENESS_REP,
   INDIRECT_SPATIAL_REF,
   DIRECT_SPATIAL_REF,
   LIEN
)
AS
   SELECT TY_PRODUIT,
          IDENTIFIANT,
          ED,
          VER,
          JEU_COUR,
          TO_DATE (DT_MEP),
          VER_META,
          ISSUE_ID,
          GEO_DATA_PRESENT_FORM,
          DT_CONTENT_BEG,
          DT_CONTENT_END,
          CURRENTNESS_REF,
          STATUS_PROGRESS,
          MAINTENANCE_FREQ,
          CLOUD_COVER,
          CLOUD_COVER_2,
          DATASET_CREDIT,
          NATIVE_DATASET_ENV,
          SERIES_NAME,
          --INFORMATION DE PUBLICATION
          DT_PUBLICATION,
          PUBLICATION_PLACE,
          PUBLISHER,
          --DESCRIPTION
          ABSTRACT_DESC,
          PURPOSE_DESC,
          SUPPLEMENTAL_INFO,
          --DOMAINE SPATIAL
          WESTBC,
          EASTBC,
          SOUTHBC,
          NORTHBC,
          --CONTRAINTE
          ACCESS_CONSTRAINTS,
          USE_CONSTRAINTS,
          --RAPPORT
          ATTRIBUTE_ACC_REP,
          LOGICAL_CONSIST_REP,
          COMPLETENESS_REP,
          --SPATIAL DATA ORGANISATION INFORMATION
          INDIRECT_SPATIAL_REF,
          DIRECT_SPATIAL_REF,
          TY_PRODUIT || '-' || IDENTIFIANT || '-' || ED || '.' || VER
     FROM F235_PR;

COMMENT ON TABLE SIBDBA.V_METADONNEES IS 'COMMENTAIRE:
Vue permettant de montrer les métadonnées.';



CREATE OR REPLACE PUBLIC SYNONYM V_METADONNEES FOR SIBDBA.V_METADONNEES;


GRANT SELECT ON SIBDBA.V_METADONNEES TO MDDTN;

GRANT SELECT ON SIBDBA.V_METADONNEES TO SIBLIRE;

GRANT SELECT ON SIBDBA.V_METADONNEES TO SIBLIREDIFF;

GRANT SELECT ON SIBDBA.V_METADONNEES TO SIBMAJ;
