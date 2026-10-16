-- =====================================================================
-- SaaS Seat Sweeper Workshop — Streaming Backdrop (Optional)
-- Optional facilitator-only exploration, excluded from the standard workshop.
-- This is NOT a teaching module in the standard 3-hour format.
-- The supplied app does not read this dynamic table; no moving-dashboard claim.
-- It adds refresh cost and needs separate approval, integration, and rehearsal.
-- Run the entire block only after 01-03; never auto-run sql/*.sql.
-- SET workshop_streaming_approved = TRUE; -- after separate administrator approval
-- =====================================================================

USE DATABASE SAAS_SEAT_SWEEPER;
USE WAREHOUSE SAAS_SWEEPER_WH;
USE SCHEMA RAW;

EXECUTE IMMEDIATE $$
DECLARE
  not_approved EXCEPTION (-20004, 'Optional streaming setup requires ACCOUNTADMIN and explicit approval.');
BEGIN
  IF (CURRENT_ROLE() <> 'ACCOUNTADMIN' OR NOT COALESCE($workshop_streaming_approved, FALSE)) THEN
    RAISE not_approved;
  END IF;

-- ---------------------------------------------------------------------
-- Raw events table: simulated order/license-activity events.
-- A facilitator-run simulator (or a simple task) inserts rows here periodically.
-- ---------------------------------------------------------------------
CREATE TABLE LICENSE_EVENTS (
  event_id      NUMBER AUTOINCREMENT PRIMARY KEY,
  event_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  emp_id        NUMBER REFERENCES EMPLOYEES(emp_id),
  asset_id      NUMBER REFERENCES ASSETS(asset_id),
  event_type    VARCHAR(30),  -- 'activated', 'deactivated', 'last_used', 'flagged'
  metadata      VARIANT
);

-- ---------------------------------------------------------------------
-- Dynamic table: aggregates events into a 1-minute-lag serving layer.
-- The app can read from this to show "live" activity counts.
-- ---------------------------------------------------------------------
USE SCHEMA APP;

CREATE DYNAMIC TABLE DT_LIVE_ACTIVITY
  TARGET_LAG = '1 minute'
  WAREHOUSE = SAAS_SWEEPER_WH
  REFRESH_MODE = AUTO
  AS
  SELECT
    e.emp_id,
    e.asset_id,
    emp.department,
    a.asset_name,
    COUNT(*) AS event_count,
    MAX(e.event_time) AS last_event_time
  FROM RAW.LICENSE_EVENTS e
  JOIN RAW.EMPLOYEES emp ON e.emp_id = emp.emp_id
  JOIN RAW.ASSETS a ON e.asset_id = a.asset_id
  GROUP BY e.emp_id, e.asset_id, emp.department, a.asset_name;

-- Apply row access policy to the live activity view.
-- Note: WITH ROW ACCESS POLICY must appear between the view name and AS SELECT,
-- not trailing after the query body (see ISSUES_LOG.md ISSUE-001).
CREATE VIEW V_LIVE_ACTIVITY_RLS
WITH ROW ACCESS POLICY GOVERNANCE.dept_isolation ON (department)
AS
SELECT
  emp_id,
  asset_id,
  department,
  asset_name,
  event_count,
  last_event_time
FROM DT_LIVE_ACTIVITY;

GRANT SELECT ON V_LIVE_ACTIVITY_RLS TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON V_LIVE_ACTIVITY_RLS TO ROLE SAAS_SWEEPER_RESTRICTED;

  RETURN 'Optional backdrop created; supplied app is not wired to it. Track refresh cost and teardown separately.';
END;
$$;

-- ---------------------------------------------------------------------
-- Note for facilitators:
-- To explore event aggregation outside the workshop, run this in a
-- separate session every 30-60 seconds (or set up a TASK):
--
--   INSERT INTO RAW.LICENSE_EVENTS (emp_id, asset_id, event_type, metadata)
--   SELECT
--     UNIFORM(1, 200, RANDOM()) AS emp_id,
--     UNIFORM(1, 15, RANDOM()) AS asset_id,
--     'last_used' AS event_type,
--   OBJECT_CONSTRUCT('source', 'simulator') AS metadata
--   FROM TABLE(GENERATOR(ROWCOUNT => 5));
--
-- This is an optional extension, not a prerequisite or a teaching module.
-- Do not explain the streaming pipeline in the standard 3-hour format
-- unless a participant specifically asks about it.
-- ---------------------------------------------------------------------
