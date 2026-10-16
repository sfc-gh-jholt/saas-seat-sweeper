# Fresh-account administrator preflight

Complete this before the participant timer. A provisioned account with ACCOUNTADMIN is a starting point, not a ready workshop. This runbook is authored and statically checked only; target-account execution and the 180-minute rehearsal are still pending.

## Notebook-track preparation

For `START_HERE.ipynb`, participants execute SQL 01–03 and the data checks during the lab. Do not also perform sections 4–5 below in their accounts. Those sections remain the prepared-data HTML-track runbook and recovery reference.

Before the notebook session, verify a local Python kernel with `snowflake-connector-python` and `ipykernel`, interactive `input()` support, the assigned named connection, and the `snowflake-apps` skill. The notebook's offline parser tests used Connector 4.7.3 and nbformat 5.11.1; this is not a live kernel/deployment certification. The profile should omit database/schema/warehouse defaults until bootstrap; the helper also overrides them to empty context. Do not store credentials in the notebook.

Leave the fixed database, warehouse and role names unused. Prepare the restricted human identity beforehand, then assign its workshop role after participant SQL 03. If custom build egress depends on the workshop schema, complete the separately approved integration setup after SQL 01–03 and before deployment configuration. Do not silently pre-create the workshop schema to satisfy that dependency. Confirm this ordering fits a timed rehearsal; if it does not, select the prepared-data track rather than mixing both.

## 1. Eligibility is a separate go/no-go gate

Confirm the selected account is eligible for Snowflake App Runtime, its region and edition support the required features, and the administrator has completed the account's Apps enablement/setup experience. Check current product availability and the account's actual setup result; ACCOUNTADMIN alone does not enable an unavailable feature. Confirm row access policies are supported as well. Do not treat a fresh trial account or a successful SQL login as eligibility evidence.

Use the approved provisioned workshop account, never an internal telemetry account or a retained live reference target. Keep account locators, connection names, endpoint URLs, restricted-user details, and evidence in a private delivery record, not in the participant download. Record the approval owner, date, cost owner, delivery date, and cleanup/retention decision.

If App Runtime cannot be enabled through the approved account process, stop deployment preparation. Offer a clearly labeled local-only or facilitator-observation session; it does not fulfill the individual deployment outcome. Do not manufacture raw SPCS compute pools, an ECR build/push workflow, or a new rights model to work around the gate.

## 2. Pin tools and select the account explicitly

The local command baseline is Snowflake CLI **3.18.0.dev0**, using `snowflake.yml` for deployment and build-only `app.yml`. The reported latest release **3.29.0 is untested for this package**. Do not upgrade or migrate manifests during preparation without a separate full rehearsal.

Before delivery, record `snow --version`, `node --version`, `npm --version`, CoCo authentication status, and lockfile hashes. Use a Node version satisfying both app package requirements and validate the exact version; no Node baseline is yet release-certified. Check `snow app setup --help`, `snow app deploy --help`, and `snow app events --help`. This baseline supports `--deploy-only`, not `--promote-only`.

Use an existing approved connection configured for the workshop account. Examples below use Bash (`read -p`), not macOS's default zsh. Open a Bash terminal first. They prompt for values rather than inventing them. Start in the unpacked package root; preserve these variables for later commands:

```bash
set -euo pipefail
WORKSHOP_ROOT="$PWD"
read -r -p 'Approved workshop connection name: ' WORKSHOP_CONNECTION
test -n "$WORKSHOP_CONNECTION" && snow connection test --connection "$WORKSHOP_CONNECTION"
```

Inspect the account, user, role, warehouse and database in that result before any DDL. Authenticate using the organization's existing SSO/key-pair process. Never relax authentication policies, network policies, MFA, or PAT enforcement to make the lab work.

## 3. Inspect collisions before first-run SQL

In an ACCOUNTADMIN worksheet in the selected workshop account, inspect existing databases, warehouses and roles. Confirm that `SAAS_SEAT_SWEEPER`, `SAAS_SWEEPER_WH`, `SAAS_SWEEPER_MANAGER`, and `SAAS_SWEEPER_RESTRICTED` are unclaimed for a fresh bootstrap. If any already exist, stop and inspect ownership, contents, dependents and grants. Do not adopt or replace them blindly. In particular, preserve all retained reference services.

The fixed data database is intentional: application queries use `SAAS_SEAT_SWEEPER.RAW` and `SAAS_SEAT_SWEEPER.APP`. Each participant chooses a unique app name such as `SEAT_SWEEPER_USER_01`; the app object must be `SAAS_SEAT_SWEEPER.APP.<participant-chosen unique name>`. Reserve `SEAT_SWEEPER_REF` for the retained reference. Use one isolated account per participant: multiple apps in one account still share data, roles and policy state, so writes affect each other's baseline.

## 4. Bootstrap data and policy objects once

After approval, run the following files individually and in this order, stopping immediately on the first error. Never run a glob over `sql/*.sql` and never use a client mode that continues after an error.

```bash
snow sql --connection "$WORKSHOP_CONNECTION" --role ACCOUNTADMIN --enable-templating NONE --filename "$WORKSHOP_ROOT/sql/01_setup.sql" &&
snow sql --connection "$WORKSHOP_CONNECTION" --role ACCOUNTADMIN --enable-templating NONE --filename "$WORKSHOP_ROOT/sql/02_seed_data.sql" &&
snow sql --connection "$WORKSHOP_CONNECTION" --role ACCOUNTADMIN --enable-templating NONE --filename "$WORKSHOP_ROOT/sql/03_rbac_demo.sql"
```

`01` creates the database, RAW/APP/GOVERNANCE schemas, X-Small SQL warehouse with 60-second auto-suspend, and the two existing workshop role names. It does not create any Application Service, secret, AI grant or egress integration. ACCOUNTADMIN owns preparation objects; participant deployment under ACCOUNTADMIN is an isolated training convenience, not a recommended production app identity.

`02` creates and seeds four ordinary Snowflake tables. Its full block refuses to run if any source table already exists. It no longer drops or replaces tables. Random sampling and relative activity dates mean participants must capture their own baseline. Contract prose, rates and fixed renewal dates are synthetic examples, not current vendor terms.

`03` creates the department policy and six views. The policy intentionally matches `CURRENT_ROLE()`: manager and ACCOUNTADMIN see all departments; restricted sees Engineering; other primary roles see no department rows. This is an explicit workshop policy, not a role-hierarchy-aware production design. Restricted receives governed views plus shared contract/inventory views, not RAW access or unfiltered helper views. Manager receives reclamation UPDATE access. No role receives AI privileges in the mandatory preparation.

These are **first-run scripts, not idempotent migrations**. Whole-block exceptions stop subsequent mutations in that block, but Snowflake DDL auto-commits: a failure can leave earlier objects. Inspect partial state and author a narrowly reviewed continuation; do not drop the database, rerun seed, or use CREATE OR REPLACE as recovery. Existing older installations need a separate grant/policy migration review; these scripts do not revoke historical overgrants.

## 5. Verify data before starting the clock

Run `02`'s read-only verification queries separately after successful seeding. Expect exactly 2,000 employees, 15 assets and 10 contracts; assignment count varies. Require zero orphan references, no empty contract text and at least one eligible inactive paid assignment for the feature test. Primary/foreign-key declarations on ordinary tables are not an integrity-test substitute.

```sql
USE ROLE ACCOUNTADMIN;
USE WAREHOUSE SAAS_SWEEPER_WH;
SELECT department, total_monthly_spend
FROM SAAS_SEAT_SWEEPER.APP.V_SPEND_BY_DEPARTMENT_RLS
ORDER BY department;
SELECT COUNT(*) AS eligible_paid_assignments
FROM SAAS_SEAT_SWEEPER.APP.V_INACTIVE_USERS_RLS
WHERE monthly_cost_per_seat > 0;
SELECT emp_id, asset_id, COUNT(*) AS copies
FROM SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS
GROUP BY emp_id, asset_id HAVING COUNT(*) > 1;
```

Record five departments, positive eligible count, zero duplicate key groups, baseline spend/opportunity, query IDs and seed date. No reseeding during the lab to restore old screenshots. `Flagged` means review requested, not vendor cancellation or realized savings.

## 6. Resolve build and runtime integrations without broad access

Complete the approved account Apps setup first. In a separate rehearsal project, resolve settings using [deployment-checkpoint.md](deployment-checkpoint.md). Do not pre-deploy or prewarm the participant's target; use a distinct disposable rehearsal name and keep its evidence separate.

Do not assume an integration named `ALLOW_ALL_ACCESS_INTEGRATION` exists or is acceptable. Never copy the reference manifest's integration, pools, stage or service name into a participant configuration. If the platform-approved default build path works, no custom integration is necessary. If build policy requires explicit egress, security must approve the exact dependency destinations first. `sql/07_build_egress.sql` supplies a separately gated first-run option named `SAAS_SWEEPER_BUILD_EAI`, limited to npm registry and Google Fonts hosts on port 443. Resolve it with setup's `--build-eai` option only after creation/inspection and approval. Add no wildcard host or general internet access. A dependency requiring another host is a review blocker, not permission to widen the rule.

Generated pool references are platform/account configuration, not an instruction to manually create compute pools. Missing managed resources or unresolved setup values go back to the account Apps administrator. Build access and runtime access are separate: the participant read/write app must not require a mounted PAT or Agent API egress. Document any genuinely required runtime integration separately and verify it against the actual account policy before allowing it.

## 7. Prepare a real restricted identity and isolated session

Provision or select a **separate non-admin human test identity** through the organization's approved identity/SSO process. Use `SAAS_SWEEPER_RESTRICTED` as its workshop role. Do not attach ACCOUNTADMIN, manager, app-owner, deployment, or any role inheriting equivalent rights. Review grants to the user, recursive role inheritance, PUBLIC, database/schema and Application Service grants; check direct and inherited paths. Keep authentication policies intact. Do not distribute shared credentials.

Prepare a separate browser profile authenticated as that identity, not the administrator's browser session. Confirm the signed-in username/account before every app-entry proof. A worksheet role switch, even with `USE SECONDARY ROLES NONE`, does not change the browser OAuth identity and cannot prove app-entry revoke denial for an ACCOUNTADMIN participant.

Rehearse on a disposable rehearsal service: confirm denied entry before grant, grant USAGE on that exact APPLICATION SERVICE to the restricted role, confirm entry, revoke that grant, then reauthenticate/reopen and confirm denial. Record timestamps, actual error and identity; do not mistake a cached page for fresh authorization. Restore only the intended final grant. If no truly restricted identity is available, mark app-entry proof blocked and show labeled recorded evidence instead of claiming a live denial.

For a service actually named `SEAT_SWEEPER_USER_01`, the administrator's separately approved grant and revoke are below. Substitute only the exact recorded service name; execute each statement at the corresponding proof step, not together. The restricted user's role assignment and approved login must already be in place.

```sql
GRANT USAGE ON APPLICATION SERVICE SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_USER_01
  TO ROLE SAAS_SWEEPER_RESTRICTED;
-- Test in the isolated restricted browser, then obtain approval for the revoke.
REVOKE USAGE ON APPLICATION SERVICE SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_USER_01
  FROM ROLE SAAS_SWEEPER_RESTRICTED;
```

Direct SQL is a different proof: record current role/secondary roles; use `USE SECONDARY ROLES NONE` and `USE ROLE SAAS_SWEEPER_RESTRICTED`, then query the department RLS view and attempt the no-row UPDATE in `03`. Expect only Engineering and an authorization error on UPDATE. Restore the prior session context explicitly. The app itself runs owner's rights: entry permission does not produce per-visitor SQL row filtering or deny an admitted visitor the owner's write capability.

## 8. Optional facilitator AI preparation, separate from participants

Only the facilitator sandbox may run `05_ai_objects.sql`, after 01-03 and separate AI/cost approval; 04 is not a prerequisite. The optional block requires `workshop_ai_approved = TRUE` in the same session and refuses existing object names. Never run it against the retained reference. The manager can use the approved playground; this is distinct from deploying a token-backed web demo.

`06_ask_pat_secret.sql` is now a non-executing security runbook. Prefer the prepared playground if a compliant dedicated read-only service identity, valid token, secret mount and narrow runtime path are not ready. The historically recorded PAT expired August 26, 2026; rotation is unverified. Do not require participants to mount it, copy it, or obtain one. No authentication-policy weakening is permitted. An ordinary local connection is not the reference route's service-token fallback.

Capture one structured answer with SQL, one contract-text answer with relevant citation/quote, and one combined answer. Inspect evidence, effective identity and tools; generated answers and clarifications are not guaranteed. Indexed Search content access and SQL policy evaluation must each be tested; governance is not automatically inherited from the visitor. Streaming backdrop `04` is optional, incurs refresh cost, and is not connected to the supplied dashboard.

## Release decision

Use [release-checklist.md](release-checklist.md) to record evidence and blockers. Do not call the account ready until eligibility, setup, both app builds, fresh-target deployment, restricted-identity proof, cutoffs and selected-target cleanup have passed. A working historical reference is not fresh-account evidence.