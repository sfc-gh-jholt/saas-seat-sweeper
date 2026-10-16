# SaaS Seat Sweeper — Reference App

Completed Next.js solution and facilitator demonstration. Participants start from the generated read-only `starter-app/`, deploy once, add reclamation, then deploy again. Do not copy this directory's facilitator deployment targeting to participant accounts.

## What it does

- **Dashboard**: total monthly spend by department (with RBAC row access policy applied)
- **Inactive users**: users who haven't been active in 30+ days, with a "Reclaim License" button
- **Asset inventory**: all assets with their contract info, renewal dates, and assigned counts
- **Contract terms**: side panel showing unstructured contract text (for the ask-your-data demo)

## Deploy

```bash
# From this directory:
snow app setup --app-name seat-sweeper-ref
snow app deploy --verbose
```

Verify in `snowflake.yml` that:
- `identifier.database` is set to `SAAS_SEAT_SWEEPER` (or your deploy database)
- `identifier.schema` is set to `APP` (or your deploy schema)
- `query_warehouse` is set to `SAAS_SWEEPER_WH`

Do NOT deploy to a personal database. You cannot grant privileges on an Application Service that lives in a personal database, so the RBAC segment becomes unprovable. `GRANT ... ON FUTURE APPLICATION SERVICES IN SCHEMA` is also unsupported.

Also note: Snowflake App Runtime is not available on trial accounts.

## Data access

The app reads from views in `SAAS_SEAT_SWEEPER.APP`:
- `V_SPEND_BY_DEPARTMENT_RLS` — department spend with row access policy
- `V_INACTIVE_USERS_RLS` — inactive users with row access policy
- `V_CONTRACT_TERMS` — contract terms text (no RLS — contracts are shared)
- `V_ASSET_INVENTORY` — asset inventory with contract metadata

Write-back goes to `SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS` (UPDATE status to 'Flagged').

The route validates positive safe-integer IDs, uses SDK binds, and parses the DML summary (zero is a no-op). Flagging is a review status, not vendor cancellation or realized savings. The UI refreshes authoritative server-rendered metrics after updates and no-ops. Unknown outcomes advise a refresh before retrying.

## Offline validation and generation

Run `npm ci --include=dev`, `npm test`, `npm run typecheck`, and `npm run build` here. Tests mock Snowflake and fetch; no account mutation is needed. The build ships `public/` and `.next/static/` with the standalone server. Type errors fail the production build.

From the package root, `python3 scripts/prepare_apps.py` generates the read-only starter and small completed-writeback checkpoint; `--check` detects drift, and `--output-root <clean-directory>` stages for packaging. See `../checkpoints/README.md` for application and safety boundaries.

The shared data helper's empty-on-read-error behavior is an intentional, visibly labeled diagnosis fixture, not production error handling. Reference Ask still uses its separately prepared mounted PAT or service-token fallback. The participant starter and completed-writeback overlay require neither Ask credentials nor agent objects.

## Auth model

The app uses **owner's rights** by default: every query runs as the service identity, not as the person viewing the page. Consequence to be precise about — `GRANT USAGE ON APPLICATION SERVICE` controls *who can open the app*, not *which rows they see once inside*. Two visitors with different roles see identical data.

To enable caller's rights for a specific query (so it runs as the calling user and per-user RBAC applies), pass `{ callersRights: true }` to `querySnowflake`. That path reads the `sf-context-current-user-token` request header and only works when the app runs in Snowflake — it is a no-op in local dev.

There is no `executeAsCaller` key in `app.yml`. The supported top-level `app.yml` keys are `install`, `build`, `run`, `artifacts`, `profile`, `environment_variables`, `secrets`, and `external_access_integrations`. The related service-level setting is `EXECUTE_AS_ROLE` on `CREATE APPLICATION SERVICE`, which sets the role used for owner's-rights queries — but it is only valid for an app created in a *personal* database, and it cannot be changed with `ALTER`. Since this app must live in a shared database for the RBAC segment, `EXECUTE_AS_ROLE` does not apply here.
