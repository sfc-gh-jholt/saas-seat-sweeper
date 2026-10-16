# 08 - Operate what you deployed

Ask CoCo for an evidence-backed operational assessment without letting diagnosis silently become remediation.

**Time limit:** 15 minutes, 02:15-02:30. Use 5 minutes for status/logs, 5 for costs/settings, and 5 for recovery/version ownership.

## Action

Inspect the actual participant service using the already-approved connection and role.

[Prompt CoCo: Inspect operations and separate facts from gaps](../coco-prompts/inspect-operations.md)

## Your decision

Check the evidence before accepting a health claim. Choose a follow-up owner, not a configuration change: this slot authorizes read-only inspection only. Do not approve speculative rollback, suspension changes or account-wide telemetry to make a check pass.

Capture `status`, `url`, source package/version, `is_upgrading`, `auto_suspend_secs` and `auto_resume`. A zero suspension interval disables auto-suspend. A blank log result does not prove health; not every request or SQL statement is necessarily logged. Use this CLI's `--last`, not guessed newer flags or Native App commands.

- Runtime/build compute, SQL warehouse compute, AI usage and storage/retention are separate cost boundaries. Closing the browser is not cleanup; idle services and retained logs/artifacts are not automatically free.
- Historical usage can lag; the previously documented App Runtime compute-history latency is up to three hours. Missing rows do not mean zero spend or establish per-app dollars.
- Prior package versions support a recovery discussion, not a promise that rollback works. Code rollback does not undo database writes. Do not invent `snow app deploy --version`, use `snow app version`, or borrow raw SPCS lifecycle commands.

## Expected evidence

Record actual status/version/settings, a log observation or failure, earlier version and named incident/cost owner. Separate observed facts, missing evidence and proposed follow-up. This live-log check does not prove configured event-table tracing, instrumentation, retention, alerts or an APM dashboard. Measure resumption/cold starts separately in the target account.

## Recovery

At minute 140, if logs fail, record the error and have the administrator check MONITOR access and service state. Local reproduction or captured facilitator output is an observed fallback. No authentication changes or account-wide telemetry enablement. A failed service remains failed even if it has a URL. Move on at minute 150 without waiting for history.

## Manual commands

Read-only fallback from the configured starter:

```bash
cd "$LAB_ROOT/starter-app"
snow app events --connection "$PARTICIPANT_CONNECTION" --last 100
snow sql --connection "$PARTICIPANT_CONNECTION" --role "$PARTICIPANT_ROLE" -q "DESCRIBE APPLICATION SERVICE ${PARTICIPANT_APP_FQN};"
```

## Checklist

- [ ] Actual logs/status/settings or their failures recorded.
- [ ] Runtime, warehouse, AI and storage costs distinguished.
- [ ] Prior actual version recorded without claiming data rollback.
- [ ] Missing metering is not zero spend; missing logs are not health.
- [ ] Proposed remediation has an owner and awaits separate approval.

Next: [Ask the same business question](09-ask-demo.md).
