# Implement the reviewed reclamation plan

Stage 2: local source changes and isolated tests only, after plan approval.

```text
Implement only the reclamation plan we just reviewed in starter-app. Follow the module 06 reviewer checklist and existing patterns, keeping the feature narrowly scoped to flagging one inactive paid assignment for review. Preserve manifests, dependencies, lockfile, connection helper, authorization model and the informational Ask page.

Add focused local tests with mocked database access for the approved success, no-op, invalid-input, failure and refresh behavior. Run the explicit type check, tests and build after checking those scripts cannot perform live writes; report any blocked gate. No live SQL, connected mutation requests, deploys, infrastructure changes or new agent. A local browser can still write to remote Snowflake, so do not exercise Reclaim against it yet. Show the diff and test output for our review, separating proven local behavior from unverified live behavior.
```
