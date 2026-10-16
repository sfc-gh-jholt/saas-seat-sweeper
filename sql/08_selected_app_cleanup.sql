-- NARROW CLEANUP ONLY. Never execute during authoring/static validation.
-- Drops exactly one participant APPLICATION SERVICE, irreversibly.
-- Does NOT delete data, roles, warehouse, repository, stages, AI, or integrations.
-- Read teardown-guide.md. Get exact selected-account/target confirmation first.
-- Set these in the SAME session after reviewing the manifest and live inventory:
-- SET workshop_app_name = 'SEAT_SWEEPER_USER_01'; -- replace with actual chosen name
-- SET workshop_confirm_drop = 'SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_USER_01';
-- Execute whole block only. Unset variables fail before DROP. Never wildcard.
EXECUTE IMMEDIATE $$
DECLARE
  app_name VARCHAR DEFAULT $workshop_app_name;
  app_fqn VARCHAR;
  unsafe_target EXCEPTION (-20008, 'Cleanup refused: participant name or exact confirmation is invalid.');
BEGIN
  IF (app_name IS NULL OR NOT REGEXP_LIKE(app_name, 'SEAT_SWEEPER_[A-Z0-9_]+')
      OR app_name IN ('SEAT_SWEEPER_REF', 'SEAT_SWEEPER_AGENT', 'SEAT_SWEEPER_PAT')) THEN
    RAISE unsafe_target;
  END IF;
  app_fqn := 'SAAS_SEAT_SWEEPER.APP.' || app_name;
  IF ($workshop_confirm_drop IS NULL OR $workshop_confirm_drop <> app_fqn) THEN
    RAISE unsafe_target;
  END IF;
  -- app_name is restricted to uppercase identifier characters; no raw SQL input.
  EXECUTE IMMEDIATE 'DROP APPLICATION SERVICE ' || app_fqn;
  RETURN 'Dropped selected service only: ' || app_fqn || '. Source/build artifacts remain; inspect separately.';
END;
$$;