# 11 - Cleanup and close

Have CoCo inventory the exact target, then execute only your approved removal or retention decision and verify the result.

**Time limit:** 10 minutes, 02:50-03:00. Use 2 minutes for inventory/approval, 5 for execution/verification, and 3 for handoff.

## Action

Save evidence/version IDs without secrets. Stopping the local server does not stop the remote app.

[Prompt CoCo: Inventory our target and propose cleanup without changes](../coco-prompts/plan-cleanup.md)

## Your decision

Match the explicit account/connection, starter manifest and `PARTICIPANT_APP_FQN`. Approve **one** precise path: default service-only removal from [selected-target cleanup](../teardown-guide.md), separately approved broader CLI teardown including uploaded source, or retention with named cost/removal owner and expiry. Deletion is destructive and not reversible. Never approve a reference/facilitator target or shared infrastructure implicitly.

[Prompt CoCo: Execute only our selected cleanup decision and verify](../coco-prompts/execute-cleanup.md)

Verify exact-name absence in command output; a browser error is not proof. Even if no service was created, inventory failed-build artifacts. For retention, record actual service/version/status, suspension/resume settings, approved access, cost owner, expiry date/time and final-removal owner. Closing the browser is not a retention policy.

Application teardown is not account cleanup. The administrator owns residual source/artifact storage, packages, warehouse, seeded data, roles/test identities, integrations, credentials and session AI services. The legacy broad `teardown.sql` is not distributed; use only the selected-target cleanup procedure. Never drop shared infrastructure because one participant finished.

## Expected evidence

Record either exact-target absence and residual-resource handoff, or explicit retention approval with owner/deadline and observed state. Save the next internal use case and its owner before closing. An agent's success summary does not replace verification output.

## Recovery

At minute 177, capture failures/residual resources and assign the administrator a named cleanup action and deadline. Mark cleanup incomplete; do not claim all charges stopped or broaden DROP scope to get a success banner.

## Manual commands

Stop the local server with Ctrl+C. The default service-only path is the reviewed `sql/08_selected_app_cleanup.sql` procedure in [teardown-guide.md](../teardown-guide.md). The alternative below has broader source-cleanup effects: run only if that exact scope was approved, never in addition to the default path.

```bash
cd "$LAB_ROOT/starter-app" &&
snow app teardown --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --force
```

Read-only verification after the selected path:

```bash
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "SHOW APPLICATION SERVICES IN SCHEMA ${PARTICIPANT_DATABASE}.${PARTICIPANT_SCHEMA};"
```

## Checklist

- [ ] Local server stopped; redacted evidence saved.
- [ ] Exact removal or retention scope approved before action.
- [ ] Service absent, or retention owner/deadline/state recorded.
- [ ] Residual resources have an administrator owner/deadline.
- [ ] No other app/shared infrastructure removed; handoff complete by minute 180.

Untimed reference: [Honest FAQ](12-honest-faq.md).
