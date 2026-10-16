# 00 - Business workflow and outcome

Learn to direct and verify CoCo while taking a prepared read-only app through two deployments and one bounded business feature.

**Time limit:** 10 minutes, 00:00-00:10. Use 3 minutes for the workflow, 4 for orientation, and 3 for your evidence baseline. The complete lab is 180 minutes, including break and cleanup; the [FAQ](12-honest-faq.md) is untimed.

## Action

Watch the finished workflow: inspect inactive paid licenses, read a contract, flag an assignment for review, and inspect remaining opportunity. Flagging is not vendor cancellation or realized savings. Annualized opportunity is remaining monthly inactive-license cost multiplied by 12, not a forecast.

[Prompt CoCo: Understand the lab and what to verify](../coco-prompts/workshop-orient.md)

## Your decision

You work individually in your own prepared account and application project. Pause to review each proposal and its evidence before approving the next action. Your repeated workflow is **inspect, propose, approve, act, verify**. Confirm scope before each action, challenge unsupported claims, and record actual evidence. CoCo's available tools vary by delivery surface: if execution is unavailable, use the manual fallback and return the result. Parallel read-only reviews are optional only after support is verified; sequential review is sufficient.

Open the unpacked package root in CoCo; keep application work scoped to `starter-app/`, not `reference-app/`. This lets CoCo read the agenda and reviewer checklists without guessing parent paths. Full-app scaffolding and building a new agent are not timed prerequisites. The [feature module](06-build-reclamation.md) separates planning, implementation and proof.

### Before the timer: administrator preparation

Fresh accounts start basically empty even with ACCOUNTADMIN. Finish [administrator preflight](../admin-preflight.md) before the timer: eligibility, authentication, synthetic data, warehouse, shared deployment database/schema, governed views, workshop roles, approved build/network prerequisites, and a separate restricted test identity. Prepare the facilitator AI demo separately.

Your participant service, deployment and endpoint must **not** already exist. Do not use a personal database for the grant/revoke exercise. ACCOUNTADMIN is the isolated workshop starting context, not proof of eligibility or a production least-privilege recommendation.

### Evidence baseline and timing

Local command checks on 2026-10-15 used CLI `3.18.0.dev0`, Node `22.12.0`, npm `10.9.0`; they were not a fresh end-to-end rehearsal. Release `3.29.0` was discovered but not installed/tested. Do not auto-upgrade. Keep `snowflake.yml` plus build-only `app.yml`; no `app.yml` v2 migration. This CLI uses `--deploy-only`, not `--promote-only`.

- 00:00-00:10: Business workflow and outcome.
- 00:10-00:25: Inspect and run the starter.
- 00:25-00:40: Configure your deployment.
- 00:40-01:05: Deploy version one.
- 01:05-01:20: Prove access boundaries.
- 01:20-01:30: Break.
- 01:30-01:55: Build reclamation with CoCo.
- 01:55-02:15: Deploy version two.
- 02:15-02:30: Operate what you deployed.
- 02:30-02:40: Ask the same business question.
- 02:40-02:50: Compare your actual stack.
- 02:50-03:00: Cleanup and close.

## Expected evidence

Record your name, assigned account, explicit connection, approved role and preflight completion in [scorecard.md](../scorecard.md). First participant URL target: minute 65. A facilitator URL is observed evidence, not your deployment.

Release gates remain open until verified: dependency vulnerabilities, an obtainable supported delivery CLI, fresh-account deployments/access tests, and timed persona rehearsals. A 180-minute schedule alone does not prove delivery readiness.

## Recovery

If preflight is incomplete, tell the facilitator now. Do not use an internal telemetry account, broaden network permissions, or improvise missing infrastructure. Observe the separate facilitator demo while the administrator resolves the gate.

## Checklist

- [ ] One isolated account per participant; preflight and explicit connection confirmed.
- [ ] Our service has not been predeployed.
- [ ] I review CoCo's evidence and approve each action within its stated scope.
- [ ] We distinguish flagging, opportunity and actual savings.

Next: [Inspect and run the starter](01-run-starter.md).
