# Run the approved access experiment

Use after approving the exact grant/revoke scope, restricted identity and no-row probe.

```text
Guide only the module 04 access experiment we just approved on our exact participant service. Confirm the administrator connection and the separate restricted user's connection/role before each relevant step. Apply only the approved service USAGE grant and its matching revoke; guide clean restricted browser sessions and record their actual outcomes. Run the reviewed direct-SQL reads and no-row UPDATE probe under the restricted role with secondary roles NONE.

Do not infer browser identity from a worksheet role. Treat successful zero-row DML as a failed negative test, not write denial. Capture the actual privilege error or explain a different failure. Finish with the exact service grant revoked before write-back development. Stop unexpected access for administrator review; never revoke unrelated grants or change authentication/network policies. Mark anything we could not execute or observe as unverified.
```
