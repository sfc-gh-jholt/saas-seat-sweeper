# 07 - Deploy version two

Use CoCo to review release readiness, then verify the approved feature at the authenticated deployed endpoint.

**Time limit:** 20 minutes, 01:55-02:15. Use 2 minutes for review/approval, 10 for deployment, and 8 for endpoint verification/recovery.

## Action

Bring your actual diff, local gates and version-one evidence; do not equate a generated feature with a tested release.

[Prompt CoCo: Review readiness and propose the second deployment](../coco-prompts/plan-second-deploy.md)

## Your decision

Confirm the same participant account/service/role and unchanged manifest target. Keep the restricted service grant revoked: the feature executes writes under owner's rights. Approve redeployment **and separately** the bounded endpoint proof: exact authenticated endpoint, numeric `emp_id`/`asset_id`, one designated request executor, and identical replay. Use a different assignment if the separately approved local proof already changed one. Only the designated actor sends requests; CoCo must not send a second request while the participant clicks. An uncertain response requires a stored-state check, not a blind retry or a new assignment.

[Prompt CoCo: Deploy the approved feature and verify remote evidence](../coco-prompts/deploy-verify-second-version.md)

Compare DESCRIBE `source` with the first deployment: "version two" is not a guaranteed `VERSION$2`. Open the returned authenticated URL; check Reclaim, Inventory/contract drawer, navigation and static assets after remote build.

With Developer Tools Network open, click Reclaim once and inspect `/api/reclaim`. Replay the **same HTTP request**, not the vanished button: use the browser's replay action if available. Otherwise inspect Copy as fetch before replaying the unchanged request in that same page's console, targeting only your app's `/api/reclaim`. Never paste cookies or authorization headers into CoCo or shared evidence. Unauthenticated `curl` tests authentication, not the protected endpoint's no-op.

## Expected evidence

Record both actual versions, deployment duration, authenticated URL, response counts 1 then 0, stored `Flagged` state and refreshed Licenses/Overview totals. Replay must not decrement opportunity again. Use module 06's approved read-only stored-state check with the selected numeric IDs. Distinguish deployed proof from local/mock tests; label checkpoint-assisted or blocked results.

## Recovery

At minute 130, inspect status/logs before retrying. For source/build failure, review a local fix or the module 06 bounded checkpoint; preserve the manifest. Only use `--deploy-only` after diagnosing a deployment-phase failure and verifying the built package. Do not overlap full deployments or assume the previous version is healthy. At minute 135, record blocked proof and move to operations with the actual state.

## Manual commands

After exact-target approval, from the starter:

```bash
cd "$LAB_ROOT/starter-app"
date -u
snow app deploy --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --verbose
date -u
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "DESCRIBE APPLICATION SERVICE ${PARTICIPANT_APP_FQN};"
snow app open --connection "$PARTICIPANT_CONNECTION" --print-only
```

## Recovery commands

Read-only diagnosis before proposing a retry:

```bash
snow app events --connection "$PARTICIPANT_CONNECTION" --last 100
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "DESCRIBE APPLICATION SERVICE ${PARTICIPANT_APP_FQN};"
```

## Checklist

- [ ] Same target, different actual package version verified.
- [ ] Local gates reviewed before deployment approval.
- [ ] Separately approved deployed mutation and identical no-op verified.
- [ ] Stored state and refreshed opportunity totals agree.
- [ ] Checkpoint/recovery use and missing proof recorded.

Next: [Operate what you deployed](08-operate.md).
