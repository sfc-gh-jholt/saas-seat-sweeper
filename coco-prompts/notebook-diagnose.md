# Diagnose a running app with incorrect data

```text
Use the synthetic incident in lab-instructions/08-operate.md and inspect only starter-app/lib/seat-sweeper-data.ts and the query logging in starter-app/lib/snowflake.ts. Explain why RUNNING and HTTP 200 do not prove the displayed totals are correct. Trace the SQL error to the empty-array fallback, distinguish SDK query duration from HTTP latency, and explain how a real query ID would connect logs to Query History. The fixture ID is not real; do not query it.

Respond in four bullets: evidence, likely cause, smallest proposed fix, and one regression test. Do not edit files, execute SQL, redeploy, inject faults, or change telemetry. Keep captured logs and credentials out of your answer.
```
