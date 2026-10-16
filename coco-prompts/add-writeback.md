# Rescue prompt/reference: Reclamation invariants

Use only when the staged [feature exercise](../lab-instructions/06-build-reclamation.md) is blocked. The main path is plan, approved local implementation, then challenge; this detailed reference is not a fourth required prompt. Keep the minute-110 checkpoint cutoff.

## Prompt

```text
Inspect our existing reclamation attempt in starter-app and identify the smallest gap against the requirements below. Propose a focused rescue first; do not edit until we approve that local repair. After approval, change only the reviewed feature source/tests and run isolated local gates. No live SQL, connected POST requests, deployment, dependency upgrades or authorization changes. If the minute-110 cutoff is reached, propose the prepared checkpoint instead of restarting generation.

The bounded feature belongs on /licenses, not in a replacement app.

The /licenses page should show inactive paid license assignments from SAAS_SEAT_SWEEPER.APP.V_INACTIVE_USERS_RLS and include a "Reclaim" button for each row. Clicking it should:

1. Call a POST API route at /api/reclaim with a JSON body containing emp_id and asset_id.
2. The API route should update SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS by setting status = 'Flagged' where emp_id, asset_id, and status = 'Inactive' match the request.
3. Return a JSON response indicating success and the number of rows affected.
4. Show visible success only when rows_affected > 0; show distinct no-op feedback when it is zero. Show safe failure feedback on HTTP, network, or malformed response errors. Never mark a row Flagged based solely on HTTP 200.
5. Refresh the server-rendered Licenses rows, Monthly Waste/opportunity, Inactive Assignments, and Annualized Opportunity using router.refresh() after both success and no-op. Overview must reflect authoritative data on navigation. Do not optimistically claim reduced billed spend.
6. Explain that annualized opportunity is monthly opportunity * 12, not realized savings. Flagging only requests review; it does not cancel vendor licenses. Disable duplicate submissions while pending and retain feedback after refresh.

Require emp_id and asset_id to be positive JavaScript safe integers (no strings, fractions, zero, negatives, NaN, Infinity, or unsafe integers). Reject invalid JSON, null, arrays, and missing fields with HTTP 400 before querying.

Use ? placeholders and querySnowflake(sql, { binds: [emp_id, asset_id] }). The supplied helper supports SDK binds on its normal owner, caller, password, and TOML paths. Never interpolate IDs into SQL. Keep the Inactive status guard so repeated requests are idempotent.

Read the Snowflake DML summary's "number of rows updated" field case-insensitively, accepting valid numeric strings. Do not use rows.length; a single summary row can report zero updates. Missing or malformed counts are unknown outcomes and must not silently become zero. Return a safe 500 error without database details or credentials; advise refreshing before retry because a write may already have happened.

Keep Snowflake result handling consistent with the rest of the app: every querySnowflake() result that is read as rows should pass through lowercaseKeys() or an equivalent key-normalization helper before values are accessed.

Use the shared InactiveUsersTable and contract drawer. Preserve the participant's snowflake.yml, build-only app.yml, dependency lockfile, informational Ask page, and supplied connection helper. Do not add a PAT, agent, arbitrary-query route, or general-purpose write endpoint. Keep owner's rights; do not change authorization or execute any live SQL/deploy without approval.

Add focused Vitest route/helper/UI tests: one update, repeated zero update, invalid IDs/JSON, malformed DML summary, safe database failure, visible success/no-op/failure, pending state, metric refresh. Replace the read-only-only UI test when adding the feature. Run npm test, npx tsc --noEmit, and npm run build with database access mocked in tests. Report test evidence and any unverified live behavior.
```

## Notes for facilitators

- This prompt demonstrates that the app can do more than display data — write-back is the most common early pattern in real deployments.
- The SQL uses an UPDATE statement, which means the app needs UPDATE privilege on `RAW.EMPLOYEE_ASSETS`. The `SAAS_SWEEPER_MANAGER` role has this; the `SAAS_SWEEPER_RESTRICTED` role does not by design.
- Fresh workshop accounts use ACCOUNTADMIN for setup. The supplied app uses owner's rights: app-entry permissions and data permissions are separate. A restricted browser visitor does not automatically imply restricted SQL execution. Do not add per-visitor authorization claims.
- Repeat the same HTTP POST with the same IDs to prove a no-op; a successful refresh may remove the row/button. Capture before/after opportunity totals, not claimed realized savings.
- Recovery: apply the generated `checkpoints/completed-writeback` overlay using `checkpoints/apply_writeback.py --target <participant-app>` after reviewing `--dry-run`. It preserves deployment configuration and does not enable Ask.