-- Administrator preparation ONLY, before the workshop timer.
-- First-run bootstrap for a fresh eligible workshop account, not a migration.
-- Read admin-preflight.md first. ACCOUNTADMIN does not enable App Runtime.
-- No Application Service is created here; participant targets stay unused.
-- Run this entire block, never selected statements. An error stops the block.
-- DDL auto-commits: a partial failure needs inspection, NOT a reset or rerun.
-- Plain CREATE deliberately refuses existing names; nothing is replaced.
EXECUTE IMMEDIATE $$
DECLARE
  wrong_role EXCEPTION (-20001, 'Use an explicitly selected workshop connection with ACCOUNTADMIN.');
BEGIN
  IF (CURRENT_ROLE() <> 'ACCOUNTADMIN') THEN
    RAISE wrong_role;
  END IF;

  -- First collision gate: never adopt or modify an existing workshop database.
  CREATE DATABASE SAAS_SEAT_SWEEPER
    COMMENT = 'Synthetic Seat Sweeper workshop data; shared within this workshop account';
  USE DATABASE SAAS_SEAT_SWEEPER;
  CREATE WAREHOUSE SAAS_SWEEPER_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Seat Sweeper SQL compute; separate from app runtime compute';
  USE WAREHOUSE SAAS_SWEEPER_WH;

  CREATE SCHEMA RAW COMMENT = 'Synthetic source tables';
  CREATE SCHEMA APP COMMENT = 'Governed views and unique participant Application Services';
  CREATE SCHEMA GOVERNANCE COMMENT = 'Workshop data policies and approved network rules';

  CREATE ROLE SAAS_SWEEPER_MANAGER COMMENT = 'Workshop manager: all departments and reclamation writes';
  CREATE ROLE SAAS_SWEEPER_RESTRICTED COMMENT = 'Workshop restricted direct SQL reader: Engineering only';
  GRANT ROLE SAAS_SWEEPER_MANAGER TO ROLE ACCOUNTADMIN;
  GRANT ROLE SAAS_SWEEPER_RESTRICTED TO ROLE ACCOUNTADMIN;
  GRANT USAGE ON WAREHOUSE SAAS_SWEEPER_WH TO ROLE SAAS_SWEEPER_MANAGER;
  GRANT USAGE ON WAREHOUSE SAAS_SWEEPER_WH TO ROLE SAAS_SWEEPER_RESTRICTED;
  GRANT USAGE ON DATABASE SAAS_SEAT_SWEEPER TO ROLE SAAS_SWEEPER_MANAGER;
  GRANT USAGE ON DATABASE SAAS_SEAT_SWEEPER TO ROLE SAAS_SWEEPER_RESTRICTED;

  -- No AI grants, secrets, authentication changes, or egress integrations here.
  -- Optional, separately approved build egress: 07_build_egress.sql.
  RETURN 'Bootstrap complete. Next: 02_seed_data.sql, then 03_rbac_demo.sql.';
END;
$$;