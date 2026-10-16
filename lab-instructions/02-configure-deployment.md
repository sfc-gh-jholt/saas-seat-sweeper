# 02 - Configure your deployment

Have CoCo propose an evidence-backed deployment target before you approve any configuration changes.

**Time limit:** 15 minutes, 00:25-00:40. Use 3 minutes for before-state, 7 for proposal/review/setup, and 5 for validation.

## Action

Use the participant connection already approved in module 01. Inspect account prerequisites read-only and preview setup; no resource creation yet.

[Prompt CoCo: Inspect prerequisites and propose the exact target](../coco-prompts/plan-deployment.md)

## Your decision

Review the exact unused service name, account, role, warehouse, prepared pool/EAI references and artifact destinations. Approve local configuration only after the dry-run matches. If the name exists, choose another approved name and recompute the FQN; do not drop it or call redeployment a first deployment.

[Prompt CoCo: Apply only the reviewed deployment configuration](../coco-prompts/configure-reviewed-target.md)

Review `identifier.name`, `identifier.database`, `identifier.schema`, `query_warehouse` and resolved resource references. Keep `snowflake.yml` and build-only `app.yml` with install/build/run phases (`npm ci --include=dev`, `npm run build`, `.next/standalone/server.js`). Setup is not app generation. A skipped existing manifest may still contain stale values.

Keep the lockfile, source and public/static assets in the bundle; exclude `node_modules`, `.next`, `.git`, `.env*`, credentials, logs and backups. No facilitator PAT is required. Never upload secrets or create missing build/network prerequisites to finish this slot.

## Expected evidence

Record absent-target before-state, reviewed configuration diff, approved role/resources, validation result and inspected local bundle. Separate administrator-prepared resources from your changes. `snowflake.yml`'s `definition_version: "2"` is not deployment `app.yml`'s `version: 2`.

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
