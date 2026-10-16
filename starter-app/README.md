# Seat Sweeper participant starter

Generated from the completed reference plus small workshop overlays. Start here, not in the facilitator reference app. Deploy this read-only app first, add reclamation, then redeploy.

## Local checks

Use the provisioned workshop account and its named CLI connection with ACCOUNTADMIN for the lab. Explicitly set `SNOWFLAKE_CONNECTION_NAME` to that connection before starting locally; do not inherit an internal or facilitator connection. No agent, Ask PAT, or mounted secret is required.

Run from this app directory:

```bash
npm ci --include=dev
npm test
npm run typecheck
npm run build
npm run dev
```

Inspect Overview, Licenses, Inventory, the contract drawer, and the informational Ask page. The build copies `public/` and `.next/static/` into `.next/standalone/`; the remote run command uses the standalone server.

## Deployment configuration

`app.yml` is build-only. `snowflake.yml` is intentionally absent: resolve the participant's unique deployment target with the facilitator-approved CLI setup procedure in `../checkpoints/deployment-configuration/README.md`. Never copy the reference deployment manifest. Keep this two-file layout; do not silently switch to app.yml v2.

## Write-back exercise and recovery

Use `../coco-prompts/add-writeback.md`. If blocked, apply the small overlay using `../checkpoints/apply_writeback.py`; review its dry-run first. It preserves your `snowflake.yml`, build manifest, and informational Ask page.

Queries run with owner's rights. App-entry access is separate from data authorization. ACCOUNTADMIN is a workshop setup convenience, not a production role recommendation. Flagging means review status, not vendor cancellation or realized savings.

The shared data module intentionally returns empty arrays after read failures as a labeled diagnosis fixture. Unexpected zero metrics require checking the connection/grants; they are not verified zero spend. Builds and mocked tests do not replace an account rehearsal.