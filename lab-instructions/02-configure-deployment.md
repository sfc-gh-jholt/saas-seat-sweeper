# 02 - Configure your deployment

Choose your app's name and review its deployment settings before creating anything in Snowflake.

**Time limit:** 15 minutes, 00:25-00:40. Use 3 minutes for before-state, 7 for proposal/review/setup, and 5 for validation.

## Action

Use the participant connection already approved in module 01. Inspect account prerequisites read-only and preview setup; no resource creation yet.

[Prompt CoCo: Inspect prerequisites and propose the exact target](../coco-prompts/plan-deployment.md)

## Your decision

Check that CoCo has the right account, role, warehouse and approved build resources. Choose an unused app name, review the dry-run, then approve the configuration change. If that name already exists, choose another; don't delete an existing app.

[Prompt CoCo: Apply only the reviewed deployment configuration](../coco-prompts/configure-reviewed-target.md)

Spend five minutes of this slot tracing the manifests, not just approving their contents:

- In `starter-app/app.yml`, follow dependency installation, build and startup. `npm run build` also runs the static-asset copy script in `package.json`; the Node entrypoint must exist after that build.
- In the proposed `snowflake.yml`, locate your service target, SQL warehouse, build/runtime resources, network integrations and upload exclusions. Build egress is separate from runtime egress.
- Predict which phase and log would expose a missing build output or incorrect startup command. Point to the fields before approving setup.

This is an App Runtime manifest walkthrough, not a raw SPCS container-spec exercise. Do not add raw SPCS CPU/memory fields to these files. Compare reported runtime limits and settings during the operations exercise.

Review `identifier.name`, `identifier.database`, `identifier.schema`, `query_warehouse` and resolved resource references. Keep `snowflake.yml` and build-only `app.yml` with install/build/run phases (`npm ci --include=dev`, `npm run build`, `.next/standalone/server.js`). Setup is not app generation. A skipped existing manifest may still contain stale values.

Keep the lockfile, source and public/static assets in the bundle; exclude `node_modules`, `.next`, `.git`, `.env*`, credentials, logs and backups. No facilitator PAT is required. Never upload secrets or create missing build/network prerequisites to finish this slot.

## Expected evidence

Keep a note of your app's full name and the configuration changes. Check that validation passes and the local bundle includes the source and lockfile, but no credentials. You haven't deployed yet.

## Why this matters

This lab keeps deployment settings in `snowflake.yml` and build steps in `app.yml`. Their version fields mean different things. Use the supplied layout rather than migrating it during the exercise.

## Recovery

At minute 35, use the facilitator-reviewed configuration checkpoint with only your approved values. If build-only `app.yml` blocks setup, move it temporarily outside the upload directory, repeat dry-run/setup and restore it before validation. If setup emits deployment `app.yml` v2, stop: this is a different CLI path needing rehearsal. Do not upgrade or overwrite the build file.

## Manual commands

Use a second terminal with module 01 variables; leave the local server separate.

```bash
cd "$LAB_ROOT/starter-app"
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "SHOW APPLICATION SERVICES IN SCHEMA ${PARTICIPANT_DATABASE}.${PARTICIPANT_SCHEMA};"
snow app setup --help
snow app setup --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --app-name "$PARTICIPANT_APP_NAME" --database "$PARTICIPANT_DATABASE" --schema "$PARTICIPANT_SCHEMA" --warehouse "$PARTICIPANT_WAREHOUSE" --dry-run
```

If required, obtain existing resource names from preflight and append `--build-eai "$PARTICIPANT_BUILD_EAI"` and/or `--compute-pool "$PARTICIPANT_COMPUTE_POOL"` to both dry-run and setup. Omit when approved defaults already resolve them. After the decision above:

```bash
snow app setup --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --app-name "$PARTICIPANT_APP_NAME" --database "$PARTICIPANT_DATABASE" --schema "$PARTICIPANT_SCHEMA" --warehouse "$PARTICIPANT_WAREHOUSE"
snow app validate --connection "$PARTICIPANT_CONNECTION"
snow app bundle
```

Inspect `output/bundle` locally; bundle does not connect to Snowflake.

## Checklist

- [ ] Exact target absent before deploy; dry-run reviewed first.
- [ ] Local changes match approved account/resources and preserve build configuration.
- [ ] Validation and bundle evidence recorded, not assumed.
- [ ] Lockfile/static assets included; credentials and debris excluded.

Next: [Deploy version one](03-deploy-v1.md).
