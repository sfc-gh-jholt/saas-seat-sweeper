# 08 - Operate what you deployed

Inspect the running app, read container signals, and explain why a healthy process can still display incorrect data.

**Time limit:** 15 minutes, 02:15-02:30. Use 3 minutes for status/version, 4 for resource samples, 6 for diagnosis, and 2 for your conclusion.

## Action

Use section 10 of [START_HERE.ipynb](../START_HERE.ipynb) for the runnable checks. Use your exact participant service and approved connection, not the facilitator reference. The helper supports only status, logs and metrics; it rechecks account identity before each query.

1. **Status:** compare deployed source version, instance count, SQL warehouse, upgrade state and suspension settings with your deployment record. `auto_suspend_secs = 0` disables automatic suspension.
2. **Container samples:** on a facilitator-verified managed-pool backend, inspect `runner` CPU and memory usage/request/limit, restart count and sample timestamps by instance. Requested resources are reservations; limits are ceilings. Do not mix timestamps or instances to calculate utilization. A counter increase warrants investigation; zero is not lifetime uptime proof.
3. **Logs:** read recent live output and identify a startup or query entry. The default log call covers instance 0, not every replica. Use a real `queryId` to find the corresponding query in Query History; `afterMs` measures SDK query duration, not HTTP latency.

For serverless or unknown backends, skip event-table metrics and use status/live logs. A blank compute-pool field does not identify the backend. Missing, stale or capped telemetry is an evidence limitation, not zero usage. Do not enable telemetry or change grants to complete the exercise.

## Your decision

This exercise is read-only. Propose a diagnosis and a regression test, not a live repair. Do not restart, scale, suspend, redeploy, inject a fault or alter account settings.

## Synthetic incident

The following is an **invented training fixture**, not output from your service. The misspelled column is deliberately different from the supplied working query. The query ID is a label, not a lookup target.

```text
Service status: RUNNING; current_instances: 1
UI observation: department spend shows zero while inactive-seat opportunity is nonzero
[snowflake] query error mode=spcs afterMs=960 queryId=FIXTURE_NOT_A_REAL_QUERY_ID:
SQL compilation error: invalid identifier 'TOTAL_MONTHLY_SPND'
GET / 200
```

Inspect `getDepartmentSpend()` in `starter-app/lib/seat-sweeper-data.ts`: it catches query failures and returns an empty array. Inspect the query logging in `starter-app/lib/snowflake.ts` to find query ID, timing and error evidence. Logs may be suppressed by `SNOWFLAKE_SDK_QUIET`; do not infer success from silence.

[Prompt CoCo: Diagnose the running app without changing it](../coco-prompts/notebook-diagnose.md)

**Check:** explain the misspelled-column failure, the empty-array fallback, and why an HTTP success can coexist with incorrect totals. Propose an explicit error state and a regression test that distinguishes failed reads from legitimate empty results. Do not implement another feature during this slot.

## Expected evidence

Record the actual service version, one timestamped container observation or a clear telemetry blocker, and one useful log entry or its absence. Separate real observations from the synthetic fixture. State what you would check next and who owns it; do not declare the whole application healthy from a single signal.

## Why this matters

Optional depth after the timed checks:

- Runtime/build compute, SQL warehouse compute, AI and retained storage have separate cost boundaries. Closing the browser is not cleanup.
- Missing metering is not zero spend. Historical usage can lag and does not automatically provide per-app dollar attribution.
- Code rollback does not reverse database writes. Use a recorded package version for the discussion; do not guess rollback commands or execute them here.
- Logs are not a complete tracing, alerting or retention strategy. The lab proves basic inspection and diagnosis, not production observability readiness.

## Recovery

If telemetry is unavailable, record the error and move to the synthetic incident; do not spend the entire slot waiting. Have the facilitator check backend support, MONITOR access and telemetry freshness separately. A failed service remains failed even if it has a URL. Move on at minute 150.

## Manual commands

Read-only fallback from the configured starter:

```bash
cd "$LAB_ROOT/starter-app"
snow app events --connection "$PARTICIPANT_CONNECTION" --last 30
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "DESCRIBE APPLICATION SERVICE ${PARTICIPANT_APP_FQN};"
```

The rehearsed 3.18.x CLI exposes runtime live logs through `--last`; its `--type` and time-window options are Native App-only. Use the notebook's SQL-backed helper for managed-pool metrics, or a separately rehearsed newer CLI. Do not copy raw SPCS service commands into an Application Service workflow.

## Checklist

- [ ] Actual status, version, instances and suspension settings checked.
- [ ] Container, instance, units and sample age recorded, or telemetry blocker stated.
- [ ] Reservations, limits and usage distinguished without mixing samples.
- [ ] SQL error traced through the empty-result fallback; real and fixture evidence kept separate.
- [ ] Runtime and warehouse costs distinguished; missing metering is not zero spend.
- [ ] One proposed fix/test recorded; no live configuration or application changes made.

Next: [Ask the same business question](09-ask-demo.md).
