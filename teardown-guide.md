# Selected-target cleanup and retention

Reserve minutes 170-180. Authoring this guide does not authorize live cleanup. All commands below are for a later approved delivery and require exact account/target confirmation. Dropping an Application Service is irreversible; there is no UNDROP safety net.

**The legacy broad `teardown.sql` is not distributed.** Use only the selected-target procedure below; do not recover or run historical account-wide teardown examples.

## Review before deleting

Read the participant-generated snowflake.yml and private delivery record. Confirm explicit workshop connection, signed-in account/user, exact service FQN, owner and agreed retention decision. Confirm this is the chosen participant name in `SAAS_SEAT_SWEEPER.APP`, not `SEAT_SWEEPER_REF` or another participant's target. Inspect the exact service, source stage/workspace and artifact repository recorded by setup/deployment. Do not guess related names from a suffix.

Get approval for a concrete list of objects. Source/build artifacts may be shared even when service names differ. Preserve the fixed data database, schemas, seed tables, warehouse, roles, approved integration, AI objects and retained reference service. Do not drop or alter any of those during participant cleanup.

## Default: drop just the selected participant service

Use `sql/08_selected_app_cleanup.sql` as a whole block in a worksheet on the confirmed workshop account. First set its two session variables to the actual chosen name and exact FQN from the manifest. Its `SEAT_SWEEPER_` identifier allowlist and exact confirmation check reject empty/mismatched targets and the reserved reference name. It intentionally contains no default executable target and no cascade cleanup.

For example, only if the participant really chose `SEAT_SWEEPER_USER_01` and approved its deletion:

```sql
SET workshop_app_name = 'SEAT_SWEEPER_USER_01';
SET workshop_confirm_drop = 'SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_USER_01';
```

Then run the reviewed `08` block, not every file in the SQL directory. It drops only that APPLICATION SERVICE and leaves source/build artifacts for separate inspection. No role switch automatically validates the account selection; inspect the current account before approving.

## Optional CLI cleanup of app and uploaded source

If approval explicitly includes uploaded source cleanup, the pinned CLI exposes the following path instead of the service-only block:

```bash
snow app teardown --connection "$WORKSHOP_CONNECTION" --project "$APP_PROJECT" --force
```

Use the selected participant project variables from the deployment checkpoint. Do not run from reference-app. This command's scope can include source-stage/workspace content; inspect the actual manifest and installed help first. Artifact repositories/packages are not assumed deleted. Do not run this and the SQL block as an unexamined sequence. Shared repositories, integrations, secrets, data and roles require a separate administrator inventory and approval, not broad drops.

## Verify or record retention

After approved removal, use the same account to list Application Services in `SAAS_SEAT_SWEEPER.APP` and confirm the exact chosen name is absent. Verify other participants and the reference remain. Record remaining stage/repository artifacts and cleanup owner/deadline; service removal is not proof that storage or optional AI/search billing has stopped.

If retaining a participant app, record a named cost owner and explicit expiry/deletion date. Inspect actual runtime suspension/resume settings and obtain separate approval for any change; merely closing the browser does not stop compute, and warehouse auto-suspend does not suspend the app. Retained source/artifact/data storage and telemetry retention can cost money. Do not claim suspension is deletion or that retention is free.

Optional facilitator AI/search/streaming resources need their own cost/cleanup inventory. Revoke workshop credentials through the approved identity process without changing account authentication policy. Never delete the retained reference's secret or revoke a shared role as participant cleanup. At minute 180, unresolved deletion is a tracked action with an owner, not a claimed success.

## Release gate

Service-only SQL and CLI cleanup are **not live-verified in this pass**. Rehearse selected-target deletion and survival of unrelated/reference objects in an isolated account before release. The literal SQL examples are not evidence that they ran.