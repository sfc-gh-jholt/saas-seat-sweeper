# 07 - Deploy version two

Deploy your updated app and check that Reclaim works at the Snowflake-hosted URL.

**Time limit:** 20 minutes, 01:55-02:15. Use 2 minutes for review/approval, 10 for deployment, and 8 for endpoint verification/recovery.

## Action

Have your diff and local test results ready, along with the URL and version from your first deployment.

[Prompt CoCo: Check that I'm ready to redeploy](../coco-prompts/plan-second-deploy.md)

## Your decision

First, check that the account and app name still match your first deployment, then approve redeployment. Keep the restricted user's app grant revoked.

Approve the live test separately: name the authenticated URL, numeric `emp_id` and `asset_id`, and who will send the request. Choose an assignment that hasn't already been flagged. Either you click or CoCo sends the request, not both. Repeat that same request once to check the no-op. If a response is unclear, inspect stored state before retrying; don't pick another assignment.

[Prompt CoCo: Deploy and check my updated app](../coco-prompts/deploy-verify-second-version.md)

Compare DESCRIBE `source` with the first deployment: "version two" is not a guaranteed `VERSION$2`. Open the returned authenticated URL; check Reclaim, Inventory/contract drawer, navigation and static assets after remote build.

With Developer Tools Network open, click Reclaim once and inspect `/api/reclaim`. Replay the **same HTTP request**, not the vanished button: use the browser's replay action if available. Otherwise inspect Copy as fetch before replaying the unchanged request in that same page's console, targeting only your app's `/api/reclaim`. Never paste cookies or authorization headers into CoCo or shared evidence. Unauthenticated `curl` tests authentication, not the protected endpoint's no-op.

## Expected evidence

Save the new version, URL and deployment time. Confirm response counts of 1 then 0, a stored `Flagged` status, and matching totals on Licenses and Overview. The repeated request must not lower opportunity again. Note any checkpoint used or test you couldn't finish.

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
