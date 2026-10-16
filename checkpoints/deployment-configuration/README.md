# Deployment configuration recovery checkpoint

This checkpoint deliberately ships **no deployment manifest**. Account settings cannot be safely inferred from the facilitator reference. The participant starts in a fresh, provisioned workshop account using ACCOUNTADMIN, with data and approved integrations prepared by the facilitator.

1. Confirm the participant's named connection, account, role, shared database/schema, warehouse, and unique app name with the facilitator. Do not use an internal telemetry account or copy `reference-app/snowflake.yml`.
2. Run `snow --version` and `snow app setup --help`. Use the workshop-rehearsed CLI supporting the two-file `snowflake.yml` plus build-only `app.yml` layout. This package does not authorize a layout migration.
3. From the participant app, run `snow app setup --app-name <your-unique-app-name> --connection <your-workshop-connection> --dry-run`. Supply only verified account values and flags supported by the installed help. Review the resolved target before running without `--dry-run`.
4. If setup skips because `app.yml` exists, keep a backup and follow the facilitator's rehearsed setup procedure. If the CLI produces `app.yml` v2 instead of `snowflake.yml`, stop and obtain the two-file configuration procedure for that CLI; do not rename v2 content to `snowflake.yml` or silently migrate.
5. Review the resulting `snowflake.yml`: exact unique target, shared database/schema, warehouse, and approved build/runtime integrations. Preserve the supplied build-only `app.yml`; no Ask PAT secret is needed. Verify upload exclusions for `node_modules`, `.next`, `.git`, `.env*`, credentials, keys, logs, and build outputs.
6. Capture the before-state showing the participant service does not yet exist. Only then perform the workshop's approved first deployment. A facilitator endpoint is observation-only, not evidence of your deployment.

No setup or deployment command was run by the generator. Local test/build checks do not validate account eligibility, grants, network integrations, or deployment timing.