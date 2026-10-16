-- =====================================================================
-- SaaS Seat Sweeper Workshop — Seed Data
-- Creates source tables and populates them with synthetic data.
-- Administrator-only, after 01_setup.sql. RANDOM() makes totals variable.
-- Entire block only: any pre-existing source table rejects the whole seed.
-- DDL auto-commits; inspect partial failures instead of rerunning or dropping.
-- =====================================================================

USE DATABASE SAAS_SEAT_SWEEPER;
USE WAREHOUSE SAAS_SWEEPER_WH;
USE SCHEMA RAW;

EXECUTE IMMEDIATE $$
DECLARE
  existing_tables NUMBER;
  seed_collision EXCEPTION (-20002, 'Seed refused: source tables already exist. Inspect; never reset automatically.');
BEGIN
  SELECT COUNT(*) INTO :existing_tables
  FROM SAAS_SEAT_SWEEPER.INFORMATION_SCHEMA.TABLES
  WHERE TABLE_SCHEMA = 'RAW'
    AND TABLE_NAME IN ('EMPLOYEES', 'CONTRACTS', 'ASSETS', 'EMPLOYEE_ASSETS');
  IF (existing_tables > 0) THEN
    RAISE seed_collision;
  END IF;

-- ---------------------------------------------------------------------
-- EMPLOYEES: 2,000 rows across 5 departments with manager relationships.
-- ---------------------------------------------------------------------
CREATE TABLE EMPLOYEES (
  emp_id        NUMBER PRIMARY KEY,
  name          VARCHAR(100) NOT NULL,
  department    VARCHAR(50)  NOT NULL,
  manager_id    NUMBER,
  email         VARCHAR(120)
);

INSERT INTO EMPLOYEES
SELECT
  SEQ4() + 1 AS emp_id,
  'Employee ' || LPAD(SEQ4() + 1, 4, '0') AS name,
  'Engineering' AS department,
  NULL AS manager_id,
  'emp' || LPAD(SEQ4() + 1, 4, '0') || '@company.com' AS email
FROM TABLE(GENERATOR(ROWCOUNT => 400))
UNION ALL
SELECT
  SEQ4() + 401,
  'Employee ' || LPAD(SEQ4() + 401, 4, '0'),
  'Sales',
  NULL,
  'emp' || LPAD(SEQ4() + 401, 4, '0') || '@company.com'
FROM TABLE(GENERATOR(ROWCOUNT => 400))
UNION ALL
SELECT
  SEQ4() + 801,
  'Employee ' || LPAD(SEQ4() + 801, 4, '0'),
  'Marketing',
  NULL,
  'emp' || LPAD(SEQ4() + 801, 4, '0') || '@company.com'
FROM TABLE(GENERATOR(ROWCOUNT => 400))
UNION ALL
SELECT
  SEQ4() + 1201,
  'Employee ' || LPAD(SEQ4() + 1201, 4, '0'),
  'Finance',
  NULL,
  'emp' || LPAD(SEQ4() + 1201, 4, '0') || '@company.com'
FROM TABLE(GENERATOR(ROWCOUNT => 400))
UNION ALL
SELECT
  SEQ4() + 1601,
  'Employee ' || LPAD(SEQ4() + 1601, 4, '0'),
  'Operations',
  NULL,
  'emp' || LPAD(SEQ4() + 1601, 4, '0') || '@company.com'
FROM TABLE(GENERATOR(ROWCOUNT => 400));

-- Assign manager_id: first employee in each department is the manager (self-reference avoided).
UPDATE EMPLOYEES SET manager_id = CASE
  WHEN department = 'Engineering' THEN 1
  WHEN department = 'Sales'       THEN 401
  WHEN department = 'Marketing'   THEN 801
  WHEN department = 'Finance'     THEN 1201
  WHEN department = 'Operations'  THEN 1601
END
WHERE emp_id <> 1 AND emp_id <> 401 AND emp_id <> 801 AND emp_id <> 1201 AND emp_id <> 1601;

-- Managers have no manager_id.
UPDATE EMPLOYEES SET manager_id = NULL WHERE emp_id IN (1, 401, 801, 1201, 1601);

-- ---------------------------------------------------------------------
-- CONTRACTS: 10 enterprise agreements with unstructured contract terms text.
-- The contract_terms_text is the unstructured data that Cortex Search indexes.
-- ---------------------------------------------------------------------
CREATE TABLE CONTRACTS (
  contract_id          NUMBER PRIMARY KEY,
  vendor_name          VARCHAR(100) NOT NULL,
  renewal_date         DATE,
  auto_renew           BOOLEAN,
  contract_terms_text  VARCHAR(8000) NOT NULL
);

INSERT INTO CONTRACTS (contract_id, vendor_name, renewal_date, auto_renew, contract_terms_text)
VALUES
(1, 'GitHub Copilot Enterprise', '2026-03-15', TRUE,
 'Enterprise agreement for GitHub Copilot seats. Minimum 50 seats. Per-seat pricing at $39/user/month. Cancellation requires 60 days written notice. Early termination within the first 12 months incurs a true-up penalty equal to 3 months of per-seat cost for all remaining seats. Seats may be reduced by up to 20% annually without penalty. Auto-renews for 12-month terms unless cancelled in writing. Support is included via GitHub Standard Support.'),

(2, 'Figma Enterprise', '2026-07-01', TRUE,
 'Figma Enterprise platform agreement. Minimum 30 seats. Per-seat pricing at $75/user/month for full seats, $15/user/month for viewer seats. Cancellation requires 90 days written notice. True-up clause: if seat count drops below the contracted minimum, customer pays the difference for the remainder of the term. Annual true-up reconciliation in January. Auto-renews for 12-month terms. SLA: 99.9% uptime, 4-hour P1 response. Support via Figma Enterprise support portal.'),

(3, 'Datadog Pro', '2026-01-31', FALSE,
 'Datadog Pro infrastructure monitoring agreement. Per-host pricing at $15/host/month for infrastructure, $30/host/month for APM. No minimum seat or host count. Cancellation requires 30 days written notice. No true-up penalty. Does not auto-renew. Customer must explicitly renew. Support via Datadog standard support. Data retention: 15 months for metrics, 30 days for traces. Overage charges apply if ingested metrics exceed plan limits.'),

(4, 'Jira Cloud Enterprise', '2026-09-15', TRUE,
 'Atlassian Jira Cloud Enterprise agreement. Per-user pricing at $14.50/user/month. Minimum 100 users. Cancellation requires 60 days written notice. Early termination penalty: 2 months of per-user cost for all remaining users. Seats may be reduced by up to 15% annually without penalty. Auto-renews for 12-month terms. Includes Jira Service Management at no additional cost for up to 3 agents. Support via Atlassian Premier Support.'),

(5, 'Snowflake', '2026-11-01', TRUE,
 'Snowflake data platform enterprise agreement. Consumption-based pricing. No minimum seat count. Cancellation requires 30 days written notice. No true-up penalty. Auto-renews for 12-month terms. Includes 10% capacity commitment discount. Support via Snowflake Enterprise Support. Additional credits purchasable on-demand. Unused credits roll over for 12 months.'),

(6, 'M3 MacBook Pro Hardware Pool', NULL, FALSE,
 'Hardware asset pool agreement for M3 MacBook Pro laptops. Per-unit cost $2,499. No contract renewal. Hardware assigned to employees and returned upon departure. Loss or damage: employee responsible for deductible of $250. Devices replaced every 3 years. IT handles provisioning and deprovisioning via MDM. No cancellation terms applicable to hardware assets.'),

(7, 'Dell U2723QE Monitor Pool', NULL, FALSE,
 'Hardware asset pool for Dell U2723QE 27-inch monitors. Per-unit cost $479. No contract renewal. Monitors assigned to employees for remote work. Loss or damage: employee responsible for replacement cost. Devices replaced every 5 years. IT handles provisioning. No cancellation terms applicable to hardware assets.'),

(8, 'Slack Pro', '2026-05-15', TRUE,
 'Slack Pro messaging platform agreement. Per-user pricing at $8.75/user/month. Minimum 50 users. Cancellation requires 45 days written notice. Seats may be reduced at any time without penalty. Auto-renews for 12-month terms. Includes message history retention of 90 days. Upgrade to Slack Business Plus available mid-term. Support via Slack standard support.'),

(9, 'Notion Enterprise', '2026-08-01', TRUE,
 'Notion Enterprise workspace agreement. Per-user pricing at $20/user/month. Minimum 25 users. Cancellation requires 60 days written notice. Early termination within first 6 months: customer forfeits any prepaid annual discount. Seats may be reduced by up to 25% annually without penalty. Auto-renews for 12-month terms. Includes unlimited blocks and file uploads. Support via Notion Enterprise support.'),

(10, '1Password Business', '2026-06-30', TRUE,
 '1Password Business password manager agreement. Per-user pricing at $7.99/user/month. Minimum 20 users. Cancellation requires 30 days written notice. No true-up penalty. Seats may be reduced at any billing cycle. Auto-renews for 12-month terms. Includes 1GB document storage per user. Provisioning via SCIM. Support via 1Password standard support. Includes travel mode and watchtower security alerts.');

-- ---------------------------------------------------------------------
-- ASSETS: 15 assets linked to contracts. Mix of License and Hardware.
-- ---------------------------------------------------------------------
CREATE TABLE ASSETS (
  asset_id              NUMBER PRIMARY KEY,
  asset_name            VARCHAR(100) NOT NULL,
  monthly_cost_per_seat NUMBER(10,2) NOT NULL,
  asset_type            VARCHAR(20)  NOT NULL,  -- 'License' or 'Hardware'
  contract_id           NUMBER REFERENCES CONTRACTS(contract_id)
);

INSERT INTO ASSETS (asset_id, asset_name, monthly_cost_per_seat, asset_type, contract_id) VALUES
(1,  'GitHub Copilot',           39.00,  'License',  1),
(2,  'Figma Full Seat',          75.00,  'License',  2),
(3,  'Figma Viewer Seat',        15.00,  'License',  2),
(4,  'Datadog Infrastructure',   15.00,  'License',  3),
(5,  'Datadog APM',               30.00,  'License',  3),
(6,  'Jira Enterprise',          14.50,  'License',  4),
(7,  'Snowflake Compute',         0.00,  'License',  5),  -- consumption-based
(8,  'M3 MacBook Pro',           0.00,  'Hardware', 6),  -- one-time cost
(9,  'Dell Monitor',              0.00,  'Hardware', 7),  -- one-time cost
(10, 'Slack Pro',                 8.75,  'License',  8),
(11, 'Notion Enterprise',        20.00,  'License',  9),
(12, '1Password Business',        7.99,  'License',  10),
(13, 'VS Code Enterprise',       0.00,   'License',  NULL),  -- free, no contract
(14, 'Zoom Pro',                  15.99, 'License',  NULL),  -- simplified
(15, 'GitHub Enterprise',        21.00,  'License',  1);  -- shares GitHub contract

-- ---------------------------------------------------------------------
-- EMPLOYEE_ASSETS: ~7,000 mappings (avg 3-4 assets per employee).
-- last_active_date spread over last 90 days; ~15% are inactive (>30 days).
-- status: Active or Inactive.
-- ---------------------------------------------------------------------
CREATE TABLE EMPLOYEE_ASSETS (
  emp_id            NUMBER NOT NULL REFERENCES EMPLOYEES(emp_id),
  asset_id          NUMBER NOT NULL REFERENCES ASSETS(asset_id),
  last_active_date  DATE,
  status            VARCHAR(20) DEFAULT 'Active',
  PRIMARY KEY (emp_id, asset_id)
);

-- Assign 3-4 assets per employee using UNIFORM distribution.
-- Random sample: capture the baseline from this account rather than old totals.
INSERT INTO EMPLOYEE_ASSETS (emp_id, asset_id, last_active_date, status)
SELECT
  e.emp_id,
  a.asset_id,
  DATEADD('day', -UNIFORM(1, 90, RANDOM()), CURRENT_DATE()),
  CASE
    WHEN UNIFORM(1, 100, RANDOM()) <= 15 THEN 'Inactive'
    ELSE 'Active'
  END
FROM EMPLOYEES e
CROSS JOIN ASSETS a
WHERE UNIFORM(1, 100, RANDOM()) <= 20  -- ~20% chance of each (emp, asset) pair existing
  AND NOT (
    a.asset_id = 8 AND e.emp_id > 1000  -- only first 1,000 employees get MacBook Pros
  )
  AND NOT (
    a.asset_id = 9 AND e.emp_id > 1200  -- only first 1,200 employees get monitors
  );

-- Ensure every employee has at least one asset (GitHub Enterprise for all).
INSERT INTO EMPLOYEE_ASSETS (emp_id, asset_id, last_active_date, status)
SELECT e.emp_id, 15, CURRENT_DATE(), 'Active'
FROM EMPLOYEES e
WHERE NOT EXISTS (
  SELECT 1 FROM EMPLOYEE_ASSETS ea WHERE ea.emp_id = e.emp_id AND ea.asset_id = 15
);

  RETURN 'Seed complete. Run the read-only verification below; do not reseed.';
END;
$$;

-- ---------------------------------------------------------------------
-- Read-only verification (run separately only after the block succeeds).
-- ---------------------------------------------------------------------
SELECT 'EMPLOYEES' AS table_name, COUNT(*) AS row_count FROM EMPLOYEES
UNION ALL SELECT 'ASSETS', COUNT(*) FROM ASSETS
UNION ALL SELECT 'CONTRACTS', COUNT(*) FROM CONTRACTS
UNION ALL SELECT 'EMPLOYEE_ASSETS', COUNT(*) FROM EMPLOYEE_ASSETS;

-- Verify FK integrity
SELECT 'orphan_employee_assets' AS check_name, COUNT(*) AS violations
FROM EMPLOYEE_ASSETS ea
LEFT JOIN EMPLOYEES e ON ea.emp_id = e.emp_id
WHERE e.emp_id IS NULL;

SELECT 'orphan_asset_refs' AS check_name, COUNT(*) AS violations
FROM EMPLOYEE_ASSETS ea
LEFT JOIN ASSETS a ON ea.asset_id = a.asset_id
WHERE a.asset_id IS NULL;

-- Verify contract terms text is non-empty
SELECT 'empty_contract_terms' AS check_name, COUNT(*) AS violations
FROM CONTRACTS
WHERE contract_terms_text IS NULL OR contract_terms_text = '';

-- Inactive user count (should be ~15% of mappings)
SELECT 'inactive_users' AS metric, COUNT(*) AS count
FROM EMPLOYEE_ASSETS
WHERE status = 'Inactive';
