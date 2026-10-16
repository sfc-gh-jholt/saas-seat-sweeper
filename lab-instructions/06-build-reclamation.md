# 06 - Build reclamation with CoCo

Direct a small business feature through a plan, approved local implementation and independent proof instead of pasting a complete solution.

**Time limit:** 25 minutes, 01:30-01:55. Use 3 minutes for the plan, 12 for implementation/review, 5 for local proof, and 5 for approved live proof or recovery. Implementation cutoff: minute 110.

## Action

Work in `starter-app/` with the participant connection selected, never Snowhouse. The goal is to flag one inactive paid assignment for review, not cancel a vendor license or claim realized savings.

[Prompt CoCo: Propose the smallest reclamation feature without edits](../coco-prompts/plan-reclamation.md)

### Your decision

Review proposed files, behavior and tests against the checklist below. Approve only the bounded local implementation; preserve manifests, dependencies, lockfile and authorization. This does **not** authorize live SQL, connected POST requests or deployment.

[Prompt CoCo: Implement our reviewed plan and run local tests](../coco-prompts/implement-reclamation.md)

### Your decision

Inspect the actual diff, not just CoCo's summary. Reject unrelated changes. Accept the local test scope for a challenge pass; if a fix is needed, review that proposal before another implementation. Live writes remain unapproved.

[Prompt CoCo: Challenge the diff and separate local proof from live proof](../coco-prompts/challenge-reclamation.md)

### Your decision

Only after local gates pass, approve the exact participant account/user/role and **one selected synthetic assignment** for the live proof, including its identical replay and invalid-input probe. A localhost endpoint still writes to remote Snowflake. Keep the restricted service grant revoked. If you cannot approve or finish safely, label live proof unverified.

### Prove the no-op by repeating the HTTP request

After that separate approval, record the chosen inactive paid assignment's IDs, seat cost and current totals. Click Reclaim once in local `/licenses` with Developer Tools Network open. Capture body/status/count/feedback; then replay the same HTTP request because the row/button may disappear. Check stored state and refresh Licenses and Overview. Do not induce a real database failure; test failure handling with mocks.

## Expected evidence

Keep **local** evidence (changed files, focused tests, explicit type check and build) separate from **live** evidence (first count 1, replay 0, invalid-input 4xx, stored `Flagged`, refreshed totals). Monthly remaining opportunity should fall once by the seat cost; annualized opportunity by 12 times that cost. HTTP 200 alone proves neither success nor no-op. Label checkpoint use and any missing proof.

## Recovery

At minute 110, stop open-ended generation. Use the [detailed rescue prompt/reference](../coco-prompts/add-writeback.md) only for a focused gap, or review the prepared `checkpoints/completed-writeback/` overlay. Preview conflicts and preserve your edits outside the upload directory before approving application. Do not copy an entire app or a reference manifest.

The checksum-checked overlay replaces feature source/tests and removes the starter-only test; it preserves `snowflake.yml`, `app.yml`, dependencies and credentials. If missing, request the prepared package rather than claiming recovery. Rerun local gates. At minute 115, if still failing, mark blocked and observe the demo rather than deploy unverified changes.

## Manual commands

Local gates from the starter, with mocked database access in focused tests:

```bash
cd "$LAB_ROOT/starter-app"
npx tsc --noEmit
npm test
npm run build
```

Read-only candidate selection after target approval:

```bash
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --warehouse "$PARTICIPANT_WAREHOUSE" -q "SELECT emp_id, asset_id, monthly_cost_per_seat, status FROM SAAS_SEAT_SWEEPER.APP.V_INACTIVE_USERS_RLS WHERE monthly_cost_per_seat > 0 ORDER BY emp_id, asset_id LIMIT 5;"
```

Only after the separately approved live Reclaim click, replay its exact numeric IDs. Use the actual local port. Reject nonnumeric values before the SQL verification command; do not substitute arbitrary SQL text.

```bash
export EMP_ID="REPLACE_WITH_NUMERIC_EMP_ID"
export ASSET_ID="REPLACE_WITH_NUMERIC_ASSET_ID"
[[ "$EMP_ID" =~ ^[1-9][0-9]*$ ]] && [[ "$ASSET_ID" =~ ^[1-9][0-9]*$ ]] || exit 1
curl -sS -i -X POST http://localhost:3000/api/reclaim -H 'Content-Type: application/json' --data "{\"emp_id\":${EMP_ID},\"asset_id\":${ASSET_ID}}"
curl -sS -i -X POST http://localhost:3000/api/reclaim -H 'Content-Type: application/json' --data '{"emp_id":"invalid","asset_id":1}'
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" --warehouse "$PARTICIPANT_WAREHOUSE" -q "SELECT emp_id, asset_id, status FROM SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS WHERE emp_id = ${EMP_ID} AND asset_id = ${ASSET_ID};"
```

## Recovery commands

Preview first; run the second command only after reviewing conflicts and approving the overlay:

```bash
python3 "$LAB_ROOT/checkpoints/apply_writeback.py" --target "$LAB_ROOT/starter-app" --dry-run
```

```bash
python3 "$LAB_ROOT/checkpoints/apply_writeback.py" --target "$LAB_ROOT/starter-app"
```

## Checklist

- [ ] POST `/api/reclaim` validates JSON object and positive safe-integer `emp_id`/`asset_id` before querying; malformed JSON, null, arrays and invalid fields return 400.
- [ ] SQL uses bound IDs, never interpolation; exact assignment plus `status = 'Inactive'` guards the transition to `Flagged`, making repeats idempotent.
- [ ] `rows_affected` reads case-normalized DML `number of rows updated`, accepting valid numeric strings, not `rows.length`. Missing/malformed counts are unknown outcomes, not fabricated zero.
- [ ] SQL errors return safe failures without database details; unknown outcomes advise refresh before retry because a write may have happened. Row result keys are normalized.
- [ ] UI distinguishes success/no-op/failure, disables duplicate pending submissions and retains feedback; both success and no-op refresh authoritative rows and opportunity metrics. Overview agrees on navigation; no claimed billed-spend reduction.
- [ ] Focused route/helper/UI tests cover one update, zero update, invalid input/JSON, malformed summary, database failure, feedback, pending state and refresh. Generic helper tests or a build alone are insufficient.
- [ ] Type check/tests/build and separately approved live proof are recorded honestly; no new agent, manifest, dependency or authorization changes.

Next: [Deploy version two](07-deploy-v2.md).
