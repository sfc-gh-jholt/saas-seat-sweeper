# Deploy the approved read-only starter

This prompt follows explicit approval of the exact remote target and deployment effects.

```text
Deploy the reviewed read-only starter to the exact participant target we just approved. Confirm the connection/account, role, service FQN, warehouse and integration references still match the reviewed manifest and unused-target evidence. Stop if they differ. Use the installed, checked CLI surface; do not upgrade tools, alter prerequisites, or deploy the reference app.

Record actual start/end times and upload, build and deployment outcomes. Do not start overlapping deployments or retry automatically. If a phase fails, collect available logs/status and propose the smallest recovery for our review; no broad policy fixes. Report resources actually created or reused. A completed command is not proof of a working endpoint: hand us the returned URL and package/version for the separate verification step. Do not invent tool output if command execution is unavailable.
```
