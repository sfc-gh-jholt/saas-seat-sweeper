-- =====================================================================
-- SaaS Seat Sweeper Workshop — RBAC Demo
-- Creates roles, row access policy, and app-facing views with RBAC enforced.
-- Administrator-only, after 01 and 02. Run the full block once.
-- Existing objects cause failure, not replacement. This is not a migration.
-- =====================================================================

USE DATABASE SAAS_SEAT_SWEEPER;
USE WAREHOUSE SAAS_SWEEPER_WH;
USE SCHEMA GOVERNANCE;

EXECUTE IMMEDIATE $$
BEGIN

-- ---------------------------------------------------------------------
-- Row Access Policy: restricts visibility to Engineering department.
-- Applied to app-facing views so the restricted role sees only Engineering.
-- ---------------------------------------------------------------------
CREATE ROW ACCESS POLICY dept_isolation
  AS (dept_col VARCHAR) RETURNS BOOLEAN ->
  CASE
    WHEN CURRENT_ROLE() = 'SAAS_SWEEPER_MANAGER' THEN TRUE
    WHEN CURRENT_ROLE() = 'ACCOUNTADMIN' THEN TRUE
    WHEN CURRENT_ROLE() = 'SAAS_SWEEPER_RESTRICTED' THEN dept_col = 'Engineering'
    ELSE FALSE -- intentional primary-role workshop policy, default deny
  END;

-- ---------------------------------------------------------------------
-- App-facing views (in APP schema) with RBAC policies applied.
-- The Next.js app reads from these views, not from RAW tables directly.
-- ---------------------------------------------------------------------
USE SCHEMA APP;

-- V_SPEND_BY_DEPARTMENT: total monthly spend per department.
CREATE VIEW V_SPEND_BY_DEPARTMENT AS
SELECT
  e.department,
  SUM(a.monthly_cost_per_seat) AS total_monthly_spend,
  COUNT(DISTINCT ea.emp_id) AS employee_count,
  COUNT(*) AS assignment_count
FROM RAW.EMPLOYEE_ASSETS ea
JOIN RAW.EMPLOYEES e ON ea.emp_id = e.emp_id
JOIN RAW.ASSETS a ON ea.asset_id = a.asset_id
WHERE ea.status = 'Active'
GROUP BY e.department;

-- Apply row access policy to the department column.
-- Note: WITH ROW ACCESS POLICY must appear between the view name and AS SELECT,
-- not after the SELECT statement. Trailing WITH ... ON (...) after the query body
-- is a syntax error ("unexpected 'WITH'").
CREATE VIEW V_SPEND_BY_DEPARTMENT_RLS
WITH ROW ACCESS POLICY GOVERNANCE.dept_isolation ON (department)
AS
SELECT
  department,
  total_monthly_spend,
  employee_count,
  assignment_count
FROM V_SPEND_BY_DEPARTMENT;

-- V_INACTIVE_USERS: users who haven't been active in 30+ days.
CREATE VIEW V_INACTIVE_USERS AS
SELECT
  e.emp_id,
  e.name,
  e.department,
  e.email,
  ea.asset_id,
  a.asset_name,
  a.monthly_cost_per_seat,
  ea.last_active_date,
  DATEDIFF('day', ea.last_active_date, CURRENT_DATE()) AS days_inactive,
  ea.status
FROM RAW.EMPLOYEE_ASSETS ea
JOIN RAW.EMPLOYEES e ON ea.emp_id = e.emp_id
JOIN RAW.ASSETS a ON ea.asset_id = a.asset_id
WHERE ea.status = 'Inactive'
  AND DATEDIFF('day', ea.last_active_date, CURRENT_DATE()) >= 30;

-- Apply row access policy to the department column.
CREATE VIEW V_INACTIVE_USERS_RLS
WITH ROW ACCESS POLICY GOVERNANCE.dept_isolation ON (department)
AS
SELECT
  emp_id,
  name,
  department,
  email,
  asset_id,
  asset_name,
  monthly_cost_per_seat,
  last_active_date,
  days_inactive,
  status
FROM V_INACTIVE_USERS;

-- V_CONTRACT_TERMS: contract details for the side panel (no RLS needed — contracts are shared).
CREATE VIEW V_CONTRACT_TERMS AS
SELECT
  a.asset_id,
  a.asset_name,
  c.contract_id,
  c.vendor_name,
  c.renewal_date,
  c.auto_renew,
  c.contract_terms_text
FROM RAW.ASSETS a
LEFT JOIN RAW.CONTRACTS c ON a.contract_id = c.contract_id;

-- V_ASSET_INVENTORY: all assets with their contract info.
CREATE VIEW V_ASSET_INVENTORY AS
SELECT
  a.asset_id,
  a.asset_name,
  a.monthly_cost_per_seat,
  a.asset_type,
  a.contract_id,
  c.vendor_name,
  c.renewal_date,
  c.auto_renew,
  COUNT(ea.emp_id) AS assigned_count
FROM RAW.ASSETS a
LEFT JOIN RAW.CONTRACTS c ON a.contract_id = c.contract_id
LEFT JOIN RAW.EMPLOYEE_ASSETS ea ON a.asset_id = ea.asset_id AND ea.status = 'Active'
GROUP BY a.asset_id, a.asset_name, a.monthly_cost_per_seat, a.asset_type, a.contract_id,
         c.vendor_name, c.renewal_date, c.auto_renew;

-- ---------------------------------------------------------------------
-- Grants: give workshop roles access to the views and underlying tables.
-- ---------------------------------------------------------------------
USE SCHEMA APP;
GRANT USAGE ON SCHEMA APP TO ROLE SAAS_SWEEPER_MANAGER;
GRANT USAGE ON SCHEMA APP TO ROLE SAAS_SWEEPER_RESTRICTED;

GRANT SELECT ON V_SPEND_BY_DEPARTMENT_RLS TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON V_SPEND_BY_DEPARTMENT_RLS TO ROLE SAAS_SWEEPER_RESTRICTED;

GRANT SELECT ON V_INACTIVE_USERS_RLS TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON V_INACTIVE_USERS_RLS TO ROLE SAAS_SWEEPER_RESTRICTED;

GRANT SELECT ON V_CONTRACT_TERMS TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON V_CONTRACT_TERMS TO ROLE SAAS_SWEEPER_RESTRICTED;

GRANT SELECT ON V_ASSET_INVENTORY TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON V_ASSET_INVENTORY TO ROLE SAAS_SWEEPER_RESTRICTED;

-- The manager role can also write back (flag licenses for reclamation).
GRANT USAGE ON SCHEMA RAW TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT, UPDATE ON RAW.EMPLOYEE_ASSETS TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON RAW.EMPLOYEES TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON RAW.ASSETS TO ROLE SAAS_SWEEPER_MANAGER;
GRANT SELECT ON RAW.CONTRACTS TO ROLE SAAS_SWEEPER_MANAGER;

-- No RAW or unfiltered helper-view grants to the restricted role: those would
-- bypass the RLS views. Shared contract/inventory aggregates are not dept-filtered.
  RETURN 'Views and grants complete. Verify direct SQL separately from app entry.';
END;
$$;

-- ---------------------------------------------------------------------
-- Verification: test RBAC behavior.
-- ---------------------------------------------------------------------

-- Under the approved ACCOUNTADMIN setup session: expect all 5 departments.
SELECT 'manager_view' AS test, department, total_monthly_spend
FROM V_SPEND_BY_DEPARTMENT_RLS
ORDER BY total_monthly_spend DESC;

-- Direct SQL demonstration only. CURRENT_ROLE deliberately matches primary role,
-- not role inheritance. Disable secondary roles for a meaningful SQL write check.
-- This DOES NOT change browser OAuth identity or prove app-entry denial.
-- App entry needs a separate non-admin user and isolated browser session; see
-- admin-preflight.md. Review inherited and PUBLIC grants for that user as well.
-- USE SECONDARY ROLES NONE;
-- USE ROLE SAAS_SWEEPER_RESTRICTED;
-- SELECT department, total_monthly_spend FROM APP.V_SPEND_BY_DEPARTMENT_RLS;
-- Expected: only 'Engineering' row returned.
-- UPDATE RAW.EMPLOYEE_ASSETS SET status = 'Flagged' WHERE 1 = 0;
-- Expected: access denied, NOT a successful zero-row update.
-- USE ROLE ACCOUNTADMIN;
-- Restore the session's previously recorded secondary-role setting, not a guess.
