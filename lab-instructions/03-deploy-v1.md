# 03 - Deploy version one

Direct CoCo through an approved deployment, then challenge its completion claim with status, version and authenticated endpoint evidence.

**Time limit:** 25 minutes, 00:40-01:05. Use 2 minutes for approval/start, 13 for build and failure diagnosis, and 10 for verification/recovery. First URL target: minute 65.

## Action

Use the reviewed configuration and absent-target evidence from module 02; do not deploy the completed reference.

## Your decision

Confirm account, explicit connection, service FQN, deploying role, warehouse and integration references. Approve this first remote deployment, including its reviewed resource effects and cost; configuration approval alone was not deployment approval.

[Prompt CoCo: Deploy our reviewed read-only starter](../coco-prompts/deploy-first-version.md)

Record actual timestamps and upload/build/deployment phases. While waiting, diagnose the facilitator's three-minute missing/stale-lockfile example. Do not break your own app to reproduce it.

[Prompt CoCo: Verify the first endpoint and challenge the evidence](../coco-prompts/verify-first-version.md)

Open the returned URL and authenticate to your assigned account. Check Overview, read-only Licenses, Inventory/contract drawer and Ask landing page. The actual version may not be `VERSION$1`; RUNNING alone does not prove working queries or UI.

## Expected evidence

Record elapsed time, service FQN, actual status, source package/version, URL, redacted log excerpt and deployed baseline. Reconcile local versus remote values only when visibility and intervening data changes permit. Record resources actually created or reused, not assumed.

This path avoids manually building/pushing a Docker image and configuring endpoint TLS; administrator preparation still counts as work. Runtime and SQL warehouse compute remain separate cost boundaries.

## Recovery

At minute 55, capture the error and inspect logs/status before any retry; never overlap deployments. At minute 60, if unresolved, use the tested local starter and observe the separately supplied facilitator URL. Mark your deployment blocked, not completed; protect the access slot and break.

Retry a phase only after facilitator diagnosis and verification of prior artifacts. Source changes require fresh upload/build, not only the final phase. Do not assume a previous runtime remains healthy.

## Manual commands

After target approval, from the configured starter:

```bash
cd "$LAB_ROOT/starter-app"
date -u
snow app deploy --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --verbose
date -u
```

Read-only verification:

```bash
snow app open --connection "$PARTICIPANT_CONNECTION" --print-only
snow app events --connection "$PARTICIPANT_CONNECTION" --last 100
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "DESCRIBE APPLICATION SERVICE ${PARTICIPANT_APP_FQN};"
```

## Recovery commands

This CLI has `--upload-only`, `--build-only`, `--deploy-only`. Only after an approved deployment-phase fix with unchanged source and a verified built package:

```bash
snow app deploy --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --deploy-only --verbose
```

## Checklist

- [ ] Exact remote target and effects approved before action.
- [ ] Actual status/version/URL/time recorded.
- [ ] Authenticated endpoint shows the read-only starter, or proof is blocked.
- [ ] One build failure classified without damaging our deployment.
- [ ] Observed fallback is not labeled participant-completed.

Next: [Prove access boundaries](04-access.md).
