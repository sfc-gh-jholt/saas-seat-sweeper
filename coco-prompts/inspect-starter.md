# Inspect the starter

Read-only source inspection. No credentials belong in this prompt.

```text
Inspect sql/02_seed_data.sql, sql/03_rbac_demo.sql and starter-app read-only, without connecting to Snowflake. In a concise five-minute walkthrough, explain how the four source tables are built and their grain, including employee/asset assignment keys and optional contract links. Distinguish fixed seed counts from random assignments; explain why independently sampled status and activity date matter. Cite source paths and lines, not assumed live results.

Trace one remaining-opportunity metric from source joins and status/date filters through the governed view, app paid-seat filter and aggregation to the UI. Name one modeling risk to check. Explain effective query identity and the error-to-empty-result limitation; never print secrets. Propose only the minimal approved-account read-only baseline checks and local launch. Do not edit, seed, create views, change grants or deploy. Stop for identity/target approval before execution; keep Licenses read-only and Ask informational.
```
