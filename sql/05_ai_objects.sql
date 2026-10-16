-- =====================================================================
-- SaaS Seat Sweeper Workshop — AI Objects
-- Creates the semantic view, Cortex Search service, and Cortex Agent
-- that power the facilitator /ask demonstration. OPTIONAL; after 01-03 only.
-- 04 is not a dependency. Participants do not execute this file.
-- Run the entire block once in a fresh approved facilitator sandbox, never the
-- retained live reference account. Existing names fail without replacement.
-- DDL auto-commits: inspect partial failures; this is NOT a reset or migration.
-- Before running, explicitly approve AI spend and set in this same session:
-- SET workshop_ai_approved = TRUE;
-- =====================================================================

USE DATABASE SAAS_SEAT_SWEEPER;
USE WAREHOUSE SAAS_SWEEPER_WH;
USE SCHEMA APP;

EXECUTE IMMEDIATE $$
DECLARE
  not_approved EXCEPTION (-20005, 'Optional AI preparation requires ACCOUNTADMIN and explicit approval.');
BEGIN
  IF (CURRENT_ROLE() <> 'ACCOUNTADMIN' OR NOT COALESCE($workshop_ai_approved, FALSE)) THEN
    RAISE not_approved;
  END IF;

-- ---------------------------------------------------------------------
-- SEMANTIC VIEW over the app-facing RBAC views.
-- Cortex Analyst uses this for structured spend and license questions.
-- Two source views have department policies; asset inventory is shared.
-- Policy evaluation follows the effective execution context, NOT automatically
-- the web visitor. Validate under the actual AI identity before making claims.
-- ---------------------------------------------------------------------
CREATE SEMANTIC VIEW SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_SEMANTIC_VIEW
  TABLES (
    department_spend AS SAAS_SEAT_SWEEPER.APP.V_SPEND_BY_DEPARTMENT_RLS
      PRIMARY KEY (department)
      COMMENT = 'Monthly spend, employee count, and assignment count per department (RLS-enforced).',
    inactive_license AS SAAS_SEAT_SWEEPER.APP.V_INACTIVE_USERS_RLS
      PRIMARY KEY (emp_id, asset_id)
      COMMENT = 'Inactive assignments (30+ days), including hardware and zero-cost assets. One row per employee and asset; department policy uses execution role.',
    asset_inventory AS SAAS_SEAT_SWEEPER.APP.V_ASSET_INVENTORY
      PRIMARY KEY (asset_id)
      COMMENT = 'Asset inventory with contract metadata and assigned seat counts.'
  )
  RELATIONSHIPS (
    inactive_license_to_department AS
      inactive_license (department) REFERENCES department_spend (department),
    inactive_license_to_asset AS
      inactive_license (asset_id) REFERENCES asset_inventory (asset_id)
  )
  FACTS (
    inactive_license.monthly_cost_per_seat AS inactive_license.monthly_cost_per_seat,
    asset_inventory.assigned_count AS asset_inventory.assigned_count
  )
  DIMENSIONS (
    department_spend.department AS department_spend.department,
    inactive_license.department AS inactive_license.department,
    inactive_license.asset_name AS inactive_license.asset_name,
    inactive_license.days_inactive AS inactive_license.days_inactive,
    inactive_license.status AS inactive_license.status,
    asset_inventory.asset_name AS asset_inventory.asset_name,
    asset_inventory.asset_type AS asset_inventory.asset_type,
    asset_inventory.vendor_name AS asset_inventory.vendor_name,
    asset_inventory.renewal_date AS asset_inventory.renewal_date,
    asset_inventory.auto_renew AS asset_inventory.auto_renew
  )
  METRICS (
    department_spend.total_monthly_spend AS SUM(department_spend.total_monthly_spend)
      COMMENT = 'Total monthly seat cost across active assignments; zero-cost assets contribute zero.',
    department_spend.employee_count AS SUM(department_spend.employee_count)
      COMMENT = 'Employees with at least one active asset assignment, counted once within their department.',
    department_spend.assignment_count AS SUM(department_spend.assignment_count)
      COMMENT = 'Active asset assignments, including hardware and zero-cost assets.',
    inactive_license.monthly_waste AS SUM(inactive_license.monthly_cost_per_seat)
      COMMENT = 'Monthly seat cost of inactive assignments aged at least 30 days; opportunity, not realized savings.',
    inactive_license.inactive_license_count AS COUNT(inactive_license.emp_id)
      COMMENT = 'Count of inactive employee-asset assignments, not distinct people; includes zero-cost and hardware assets.',
    asset_inventory.total_assigned_seats AS SUM(asset_inventory.assigned_count)
      COMMENT = 'Total assigned seats across all assets.'
  )
  COMMENT = 'Semantic view for SaaS Seat Sweeper: department spend, inactive licenses, and asset inventory.';

-- ---------------------------------------------------------------------
-- CORTEX SEARCH SERVICE over the CONTRACTS table.
-- Indexes contract_terms_text so the agent can answer unstructured
-- contract questions (cancellation penalties, true-up clauses, etc.).
-- ---------------------------------------------------------------------
CREATE CORTEX SEARCH SERVICE SAAS_SEAT_SWEEPER.APP.CONTRACT_TERMS_SEARCH
  ON contract_terms_text
  ATTRIBUTES vendor_name, contract_id
  WAREHOUSE = SAAS_SWEEPER_WH
  TARGET_LAG = '1 hour'
  COMMENT = 'Cortex Search over vendor contract terms text for the /ask route.'
AS (
  SELECT contract_id, vendor_name, contract_terms_text
  FROM SAAS_SEAT_SWEEPER.RAW.CONTRACTS
);

-- ---------------------------------------------------------------------
-- CORTEX AGENT with both tools:
--   1. Cortex Analyst (structured spend/license questions)
--   2. Cortex Search (unstructured contract terms)
-- Instructions request SQL and clarifications; they do not guarantee them.
-- Source contract text is synthetic and shared, not visitor-filtered retrieval.
-- ---------------------------------------------------------------------
CREATE AGENT SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_AGENT
FROM SPECIFICATION '
{
  "models": {
    "orchestration": "auto"
  },
  "orchestration": {
    "budget": {
      "seconds": 60,
      "tokens": 16000
    }
  },
  "instructions": {
    "orchestration": "You are Seat Sweeper Agent, an internal assistant for SaaS license and asset usage. You answer business questions using two tools: a structured data tool for spend and license questions, and a search tool for unstructured contract terms. Always show the SQL you generated for any structured-data answer. If a question is ambiguous (for example ''how are we doing?''), do not guess. Return 2-4 clarifying suggestions as a short list instead.",
    "response": "Be concise and concrete. Lead with the answer. Then show the generated SQL if a structured query was used. If the answer depends on contract terms, quote the relevant clause from the search results. Dollar amounts are monthly per-seat unless stated otherwise."
  },
  "tools": [
    {
      "tool_spec": {
        "type": "cortex_analyst_text_to_sql",
        "name": "query_seat_sweeper_data",
        "description": "Query structured SaaS license spend, inactive paid assignments, and asset inventory data. Use this for questions about cost, counts, departments, inactive users, renewal dates, and asset types."
      }
    },
    {
      "tool_spec": {
        "type": "cortex_search",
        "name": "search_contract_terms",
        "description": "Search unstructured vendor contract terms text for clauses about cancellation, true-up penalties, auto-renewal, minimum seat counts, and notice periods. Use this when the question asks about contract terms, penalties, or renewal obligations."
      }
    }
  ],
  "tool_resources": {
    "query_seat_sweeper_data": {
      "execution_environment": {
        "query_timeout": 60,
        "type": "warehouse",
        "warehouse": "SAAS_SWEEPER_WH"
      },
      "semantic_view": "SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_SEMANTIC_VIEW"
    },
    "search_contract_terms": {
      "execution_environment": {
        "query_timeout": 60,
        "type": "warehouse",
        "warehouse": "SAAS_SWEEPER_WH"
      },
      "search_service": "SAAS_SEAT_SWEEPER.APP.CONTRACT_TERMS_SEARCH"
    }
  }
}
';

-- Facilitator manager grants only. This does NOT prove visitor RBAC on /ask.
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE SAAS_SWEEPER_MANAGER;
GRANT USAGE ON AGENT SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_AGENT TO ROLE SAAS_SWEEPER_MANAGER;
GRANT REFERENCES, SELECT ON SEMANTIC VIEW SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_SEMANTIC_VIEW TO ROLE SAAS_SWEEPER_MANAGER;

-- ---------------------------------------------------------------------
-- Search USAGE permits querying indexed content. It is a separate boundary
-- from source-table policies. Future changes need explicit review and re-test;
-- never replace a live search service to repair a credential/grant issue.
-- ---------------------------------------------------------------------
GRANT USAGE ON CORTEX SEARCH SERVICE SAAS_SEAT_SWEEPER.APP.CONTRACT_TERMS_SEARCH TO ROLE SAAS_SWEEPER_MANAGER;
  RETURN 'Optional AI objects created. Credential setup and question validation remain separate gates.';
END;
$$;
