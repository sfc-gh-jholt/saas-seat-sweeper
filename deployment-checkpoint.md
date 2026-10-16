# Deployment configuration checkpoint

Recovery for minutes 25-40 and a preflight procedure for the administrator. This is not a pre-deployed participant app. No live setup/deploy was performed while authoring it. Keep the retained reference target unchanged.

## Inputs and safety checks

Finish [admin-preflight.md](admin-preflight.md) first. Use the participant's read-only `starter-app`, not the reference app or an internal telemetry connection. Each participant chooses a unique simple uppercase name beginning `SEAT_SWEEPER_`, never `SEAT_SWEEPER_REF`. Its object is `SAAS_SEAT_SWEEPER.APP.<chosen name>`; data stays in the fixed workshop database.

Use the CLI 3.18.0.dev0 baseline: generated `snowflake.yml` plus supplied build-only `app.yml`. Do not add `version: 2` to app.yml, use `--target`, migrate manifests, or upgrade to the untested 3.29.0 release in the room. Confirm setup/deploy flags with local `--help`.

The following Bash commands are for a future approved workshop run. Open a Bash terminal (the `read -p` prompts are not zsh syntax) and start in the unpacked package root:

```bash
set -euo pipefail
WORKSHOP_ROOT="$PWD"
APP_PROJECT="$WORKSHOP_ROOT/starter-app"
read -r -p 'Approved workshop connection: ' WORKSHOP_CONNECTION
read -r -p 'Unique app name (SEAT_SWEEPER_ prefix): ' WORKSHOP_APP_NAME
test -n "$WORKSHOP_CONNECTION"
[[ "$WORKSHOP_APP_NAME" =~ ^SEAT_SWEEPER_[A-Z0-9_]+$ ]]
[[ "$WORKSHOP_APP_NAME" != SEAT_SWEEPER_REF ]]
test -d "$APP_PROJECT"
snow connection test --connection "$WORKSHOP_CONNECTION"
```

Manually confirm the selected account and ACCOUNTADMIN training role. Inspect APP_PROJECT and its manifest files. If `snowflake.yml` already exists, setup may skip initialization rather than refresh values: preserve it outside the upload directory for review, then generate in a clean participant copy. Do not overwrite unknown deployment settings. On this pinned CLI, keep the supplied build-only app.yml intact. Stop if the installed CLI differs.

## Resolve settings with setup, not guessed object values

Run setup from the participant app directory (the baseline setup command does not expose deploy's `--project` flag):

```bash
cd "$APP_PROJECT" &&
snow app setup --connection "$WORKSHOP_CONNECTION" --role ACCOUNTADMIN \
  --app-name "$WORKSHOP_APP_NAME" --database SAAS_SEAT_SWEEPER --schema APP \
  --warehouse SAAS_SWEEPER_WH --dry-run
```

Inspect every resolved setting and its source. Require the chosen name, database `SAAS_SEAT_SWEEPER`, schema `APP`, and query warehouse `SAAS_SWEEPER_WH`. Record the actual generated source stage and artifact/managed-resource settings, not invented names or copied reference values.

If preflight required and approved the optional `SAAS_SWEEPER_BUILD_EAI`, add `--build-eai SAAS_SWEEPER_BUILD_EAI` to **both** setup commands. Otherwise retain only an inspected platform-approved build path. Never use an assumed `ALLOW_ALL_ACCESS_INTEGRATION`. If setup returns missing resources, an unrelated integration, a personal database, or any unknown value, stop and return to the administrator. Do not fill pool identifiers with a guessed size or manually provision raw SPCS infrastructure.

After reviewing the dry-run output, generate with the identical options (including the approved build-eai option, if used):

```bash
snow app setup --connection "$WORKSHOP_CONNECTION" --role ACCOUNTADMIN \
  --app-name "$WORKSHOP_APP_NAME" --database SAAS_SEAT_SWEEPER --schema APP \
  --warehouse SAAS_SWEEPER_WH
```

Read the generated snowflake.yml. Check the participant name, isolated source/artifact destinations, warehouse, managed-resource references and integration resolution. Ensure upload exclusions cover `.env*`, credentials, local logs, `.git`, `node_modules` and `.next`. Check the supplied app.yml's install/build/run/profile/icon entries. **No participant secrets mount or mandatory AI runtime integration is allowed.** A placeholder that parses is not a resolved deployment.

## Capture the before-state

In a worksheet on the same explicitly selected account:

```sql
SELECT CURRENT_ACCOUNT(), CURRENT_USER(), CURRENT_ROLE();
SHOW APPLICATION SERVICES IN SCHEMA SAAS_SEAT_SWEEPER.APP;
```

Compare the returned names **exactly** to the generated identifier. The chosen participant service must be absent. Existing other participants/reference services are not permission to replace them. If it already exists, choose a new unused name and repeat setup in a clean copy; do not relabel a redeploy as a first deploy. Do not prewarm by deploying into that target.

## Deploy and phase recovery

After the participant reviews and approves the exact resolved destination, start the timed first deploy:

```bash
snow app deploy --connection "$WORKSHOP_CONNECTION" --role ACCOUNTADMIN \
  --project "$APP_PROJECT" --verbose
```

Capture elapsed time, phase outcomes, service name, package version, status, returned endpoint and authenticated read-only UI. Keep the endpoint in private delivery evidence. Run the same command for version two only after reviewing and testing the feature. It performs another build/deployment; rerunning is not an idempotent no-op.

Use only the failed phase after reviewing its inputs. Supported baseline phase flags are `--upload-only`, `--build-only` and `--deploy-only`; the promotion phase is **not** `--promote-only` here. Do not rerun all three speculatively or claim success from upload/build alone. Logs:

```bash
snow app events --connection "$WORKSHOP_CONNECTION" --project "$APP_PROJECT" --last 100
```

At minute 60 triage once, then stop at minute 65. Use the prepared local checkpoint; a facilitator endpoint is observation-only. Mark deployment incomplete if no participant endpoint exists. Second-deploy cutoff is minute 135. Never repair account eligibility or broad network settings live to meet the timer.

## Evidence still required

Local help checks prove the commands expose these flags, not that account setup resolves or a remote build succeeds. Fresh-account dry-run/generation, first/second deployment, approved default/custom egress path and cleanup must be rehearsed before release. Record those results in [release-checklist.md](release-checklist.md).