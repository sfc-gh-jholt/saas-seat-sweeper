# 08 - Operate what you deployed

Find your app's logs and settings, and understand what can keep running after you close the browser.

**Time limit:** 15 minutes, 02:15-02:30. Use 5 minutes for status/logs, 5 for costs/settings, and 5 for recovery/version ownership.

## Action

Inspect the actual participant service using the already-approved connection and role.

[Prompt CoCo: Show my app's status, logs and cost settings](../coco-prompts/inspect-operations.md)

## Your decision

This is a read-only exercise. Review what CoCo finds and note any follow-up needed. Don't change suspension settings, enable account-wide telemetry or attempt a rollback here.

Capture `status`, `url`, source package/version, `is_upgrading`, `auto_suspend_secs` and `auto_resume`. A zero suspension interval disables auto-suspend. A blank log result does not prove health; not every request or SQL statement is necessarily logged. Use this CLI's `--last`, not guessed newer flags or Native App commands.

- Runtime/build compute, SQL warehouse compute, AI usage and storage/retention are separate cost boundaries. Closing the browser is not cleanup; idle services and retained logs/artifacts are not automatically free.
- Historical usage can lag; the previously documented App Runtime compute-history latency is up to three hours. Missing rows do not mean zero spend or establish per-app dollars.
- Prior package versions support a recovery discussion, not a promise that rollback works. Code rollback does not undo database writes. Do not invent `snow app deploy --version`, use `snow app version`, or borrow raw SPCS lifecycle commands.

## Expected evidence

Record the status, version, suspension settings and one useful log entry or error. Note who owns any follow-up and ongoing costs. Finding logs is a starting point; it doesn't mean tracing, alerts or retention have been configured.

## Why this matters

Code rollback does not reverse database writes. App runtime, warehouse compute, AI and retained storage can have separate costs. Usage history may arrive late, so an empty result isn't proof of zero spend.

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
