# 01 - Inspect and run the starter

Explore the sample data, run the starter, and check that the numbers on screen match the data.

**Time limit:** 15 minutes, 00:10-00:25. Use 5 minutes for the dataset recipe and metric trace, 5 for identity approval and launch, and 5 for data/UI reconciliation.

## Action

Open the cloned repository root in CoCo, not just the starter folder. Start by reading the source; you'll approve the account connection before running anything.

### Data prep: from source records to a usable metric

Before deployment, inspect what the app is built on. The administrator has already executed the build; your job is to understand and check its result, not rerun setup.

- **Build recipe:** `01_setup.sql` prepares the environment; `02_seed_data.sql` creates employees, assets, contracts and assignments; `03_rbac_demo.sql` joins them into governed app-facing views.
- **Grain:** an assignment is an employee/asset pair, not an employee. Several assignments can belong to one person; several assets can share a contract.
- **Transformation:** the inactive view requires `Inactive` status and at least 30 days since activity. The app then selects positive seat cost, sums it per assignment, and annualizes by multiplying by 12.
- **Check:** capture your account's baseline, not a screenshot's totals. Random sampling makes assignment counts vary; status and activity dates are sampled independently.

The [dataset build guide](../dataset-guide.md) explains the four tables, seed construction, checks and how to substitute real sources later. It is optional depth, not an extra timed module.

[Prompt CoCo: Explain the dataset recipe and trace a metric](../coco-prompts/inspect-starter.md)

## Your decision

Review CoCo's explanation and proposed launch commands. Confirm your assigned account, connection, role and warehouse, then approve the local launch and read-only checks. Select that same connection in CoCo and replace any `REPLACE_...` values. Don't rerun the setup scripts or change views in this exercise.

[Prompt CoCo: Launch the approved starter and reconcile data](../coco-prompts/run-starter.md)

Open Overview, Licenses, Inventory and Ask. Try opening a contract in Inventory. Licenses should be read-only, and Ask should explain the later demo. If totals are zero, check for errors: the starter can display empty results after a failed query.

The helper prefers a mounted service token, then environment user/password, then named TOML connections. Inspect overrides without revealing secrets; with facilitator help remove unintended overrides only from this app's launch environment. Do not edit global credentials or weaken authentication.

## Expected evidence

In your scorecard, note the account/user/role, monthly and annualized opportunity, and one contract you opened. Compare the department totals from a direct view query with Overview. Explain why one employee can have several assignments. Matching totals checks the data path, not each visitor's permissions.

## Recovery

If you're still blocked at minute 22, save the first error and ask the facilitator to check the connection or supply a clean starter. Don't regenerate dependencies or replace your app with the completed reference. Note any checkpoint you use and continue with the facilitator's guidance.

## Manual commands

Fallback only after the decision above. Use a dedicated Bash terminal; repeat variable assignments in any second terminal. Keep the server terminal open. ACCOUNTADMIN is only the approved isolated-workshop role.

```bash
set -euo pipefail
export LAB_ROOT="/REPLACE_WITH_ABSOLUTE_PACKAGE_PATH/seat-sweeper"
export PARTICIPANT_CONNECTION="REPLACE_WITH_PARTICIPANT_CONNECTION"
export PARTICIPANT_ROLE="ACCOUNTADMIN"
export PARTICIPANT_APP_NAME="SEAT_SWEEPER_USER_01"
export PARTICIPANT_DATABASE="SAAS_SEAT_SWEEPER"
export PARTICIPANT_SCHEMA="APP"
export PARTICIPANT_WAREHOUSE="SAAS_SWEEPER_WH"
export PARTICIPANT_APP_FQN="${PARTICIPANT_DATABASE}.${PARTICIPANT_SCHEMA}.${PARTICIPANT_APP_NAME}"
test -d "$LAB_ROOT/starter-app"
[[ "$PARTICIPANT_APP_NAME" =~ ^SEAT_SWEEPER_[A-Z0-9_]+$ ]]
[[ "$PARTICIPANT_APP_NAME" != SEAT_SWEEPER_REF ]]
cd "$LAB_ROOT/starter-app"
snow --version
node --version
npm --version
snow connection test --connection "$PARTICIPANT_CONNECTION"
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE();"
```

After confirming the identity output:

```bash
npm ci
SNOWFLAKE_CONNECTION_NAME="$PARTICIPANT_CONNECTION" SNOWFLAKE_DEFAULT_CONNECTION_NAME="$PARTICIPANT_CONNECTION" SNOWFLAKE_ROLE="$PARTICIPANT_ROLE" SNOWFLAKE_WAREHOUSE="$PARTICIPANT_WAREHOUSE" npm run dev
```

Open `http://localhost:3000` or the printed port. In the second configured terminal:

```bash
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --warehouse "$PARTICIPANT_WAREHOUSE" -q "SELECT department, total_monthly_spend, employee_count, assignment_count FROM SAAS_SEAT_SWEEPER.APP.V_SPEND_BY_DEPARTMENT_RLS ORDER BY total_monthly_spend DESC;"
```

## Checklist

- [ ] I can explain the source-table grain, seed/build order and one data-modeling risk without reseeding.
- [ ] Cited source and identity match my assigned account.
- [ ] Explicit connection selectors used; no secrets copied into source.
- [ ] Four routes load with no active reclamation workflow.
- [ ] Direct read and UI reconcile, or the discrepancy is recorded.
- [ ] I checked that zero totals aren't caused by a query error.

Next: [Configure your deployment](02-configure-deployment.md).
