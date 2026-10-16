-- Optional ADMIN-ONLY build egress, after 01-03. Not runtime internet access.
-- Use only after security approval and a build-path preflight demonstrates need.
-- Before this block, in the SAME selected-account session, set:
-- SET workshop_build_egress_approved = TRUE;
-- Unset/false approval fails before DDL. Execute the entire block at once.
-- New names only. Do not reuse, replace, or widen an unrelated integration.
EXECUTE IMMEDIATE $$
DECLARE
  not_approved EXCEPTION (-20007, 'Narrow build egress requires explicit administrator approval.');
BEGIN
  IF (CURRENT_ROLE() <> 'ACCOUNTADMIN' OR NOT COALESCE($workshop_build_egress_approved, FALSE)) THEN
    RAISE not_approved;
  END IF;
  CREATE NETWORK RULE SAAS_SEAT_SWEEPER.GOVERNANCE.BUILD_EGRESS
    MODE = EGRESS
    TYPE = HOST_PORT
    VALUE_LIST = ('registry.npmjs.org:443', 'fonts.googleapis.com:443', 'fonts.gstatic.com:443')
    COMMENT = 'Approved Seat Sweeper build-only npm and font hosts';
  CREATE EXTERNAL ACCESS INTEGRATION SAAS_SWEEPER_BUILD_EAI
    ALLOWED_NETWORK_RULES = (SAAS_SEAT_SWEEPER.GOVERNANCE.BUILD_EGRESS)
    ENABLED = TRUE
    COMMENT = 'Seat Sweeper build egress only; no runtime or arbitrary host access';
  RETURN 'Build EAI created. Resolve it with snow app setup --build-eai SAAS_SWEEPER_BUILD_EAI.';
END;
$$;