# SaaS Seat Sweeper facilitator guide

Workshop contract: learn to direct and verify CoCo while shipping a real internal application. Start with read-only source and prepared data, use CoCo to inspect and plan the first deployment, build a bounded reclamation feature, and verify a second deployment. Seat Sweeper is the deliverable; CoCo is the working method. The completed reference remains a solution/fallback. The live timed rehearsal remains pending.

## Facilitate the interaction, not a command recital

Keep participants in the repeated loop: **inspect, propose, approve, act, verify**. Prompt cards are the primary path. Manual commands and detailed rescue prompts are fallback/reference, not a second required workload. Do not read every technical note aloud.

Each person works individually. Before each interaction, the participant supplies the concrete goal and scope, then reviews the account/target, proposed changes and evidence before approving action. Preserve the break; no role swap is required. A confident response is not proof: ask participants to open a cited file, inspect a diff, or read the actual tool/test result. Correct unsupported claims with a focused follow-up rather than repeatedly regenerating the whole solution.

Use the stage labels precisely: read-only inspection authorizes no edits; local implementation authorizes only reviewed app files; deployment, live writes, grants/revokes, and cleanup need their own exact-target approval. If CoCo asks a sensible blocking question, resolve it within the allotted slot. If it wanders, narrow the task or use the checkpoint at the existing cutoff.

Keep prompts short enough to read before sending. The feature's exhaustive implementation contract is a rescue resource and review checklist, not the opening prompt. Judge a participant's work by whether they scoped, reviewed, and verified it—not by whether their model response matched the facilitator's wording.

Parallel read-only reviews are optional only after the delivery surface's agent tools have been verified. Never require a feature absent from that surface: the same two reviews can run sequentially. Do not run competing writers against the same files or hide extra work inside the deployment wait.

## Before the timer

Complete [admin-preflight.md](admin-preflight.md), [deployment-checkpoint.md](deployment-checkpoint.md) and the gates in [release-checklist.md](release-checklist.md). Fresh ACCOUNTADMIN accounts need eligibility/Apps setup, data, warehouse, roles, policies and approved integrations prepared first. No mandatory manual raw SPCS pool, Docker/ECR build, participant AI stack, or PAT setup.

Each participant owns an isolated workshop account and a unique `SAAS_SEAT_SWEEPER.APP.<chosen name>` target within it; the fixed data names are prepared in that account. Do not deploy into their target beforehand. Preserve the retained reference service and its manifests. Keep facilitator account details, URLs, credentials and private evidence out of the shareable package.

Use CLI 3.18.0.dev0's two-file layout and `--deploy-only` for phase recovery. Release 3.29.0 is untested here; no upgrade or manifest migration is part of the workshop. Check help before teaching flags. Tool authentication, data baselines, isolated restricted identity/browser, local recovery checkpoint and optional facilitator AI must be ready before minute zero.

Start on the **Introduction & agenda** landing page: explain what participants will build, the CoCo working method, and where dataset preparation fits before the first deployment. Use it within the existing opening ten minutes, not as an extra segment.

## Exact 180-minute agenda

These slots are the approved agenda contract; the package's canonical agenda metadata must match them. APPDEV and DE are review lenses on the same agenda, not additional minutes or alternate tracks.

- **00:00-00:10 (10 min): Business workflow and outcome.** Show finished read/reclaim workflow, then identify what is absent in the read-only starter. Evidence: participant can name the feature to build. Recovery: use a labeled recording if the facilitator demo is unavailable.
- **00:10-00:25 (15 min): Inspect and run the starter.** Ask CoCo for a five-minute walkthrough of the seed recipe, four source-table grains, assignment joins and metric filters. Review cited SQL and the app's paid-seat calculation, then use five minutes for identity approval/launch and five for baseline reconciliation. The build is prepared, not hidden: participants inspect it but do not rerun setup or seed. Evidence: populated local dashboard and query source. At minute 22 move blocked participants to the prepared local checkpoint; no full-app generation or dependency exercise.
- **00:25-00:40 (15 min): Configure deployment.** Ask CoCo for a read-only readiness assessment and configuration proposal; review name/database/schema/warehouse, approved integration and upload exclusions before authorizing setup. Evidence: resolved manifest and absent exact participant service. At minute 35 use the deployment checkpoint, not a copied reference manifest. Unresolved eligibility/integration at minute 40 means local/observation mode.
- **00:40-01:05 (25 min): Deploy version one.** Approve the exact reviewed target and have CoCo deploy and verify the resulting service/version/endpoint. Allow upload/build/deploy wait time. Use one three-minute facilitator-owned failure example while builds run: ask CoCo to diagnose existing evidence and propose the smallest next check, never damage participant targets. Evidence: participant's authenticated endpoint, version, status and read-only UI. At minute 60 triage once using the failed phase; at minute 65 stop blocking the room. Local checkpoint or facilitator URL continues learning but does not count as individual deployment completion. **First endpoint target: minute 65.**
- **01:05-01:20 (15 min): Prove access boundaries.** Use the visible CoCo challenge prompt to test the restricted-visitor claim against the code. Allocate seven minutes to the isolated restricted-identity entry proof, five to direct SQL filtering/denied write, and three to review CoCo's identity explanation. Prompts replace instruction time, not the evidence. Evidence: allow/deny under the same separate identity plus SQL results. If isolation fails, show labeled prior evidence and mark the live proof incomplete. Never claim a worksheet role switch proves browser denial.
- **01:20-01:30 (10 min): Break.** Preserve all ten minutes.
- **01:30-01:55 (25 min): Build reclamation with CoCo.** Use three staged prompts: inspect/propose without edits, implement the reviewed local plan, and verify/challenge the result. Review binding, validation, conditional transition, affected-row count, visible failure/no-op feedback and refreshed opportunity totals. Keep technical detail in the reviewer checklist/rescue prompt. Evidence: first HTTP request changes one row, repeat changes zero. Repeat the request, not a button that disappears. At minute 110 use the completed feature checkpoint if blocked, then test it by minute 115. Label checkpoint-assisted completion.
- **01:55-02:15 (20 min): Deploy version two.** Ask CoCo to review the diff and test evidence, approve the exact redeploy target, then capture the new version and verify the feature remotely, including invalid input and repeated no-op. At minute 130 diagnose once; minute 135 is the hard cutoff. Local-only feature success is not deployed-feature success; preserve the result honestly.
- **02:15-02:30 (15 min): Operate what you deployed.** Use CoCo for read-only inspection: five minutes for logs/status, five for cost boundaries and actual suspension settings, five to identify the prior version and propose a rollback decision. Require observed facts, missing evidence, and proposed actions to be separated. Actual rollback is optional/facilitator-led unless rehearsal proves it fits. Use `snow app events --last 100` with explicit project/connection. Do not wait for delayed ACCOUNT_USAGE records.
- **02:30-02:40 (10 min): Ask the same business question.** Two minutes structured, two contract retrieval, three combined, three evidence/identity/cost discussion. Use the prepared facilitator agent; participants do not build it. CoCo helps develop and operate the app; this Cortex Agent answers business questions at runtime. Ask participants to distinguish those two agent roles and their identities. If AI credentials or answers fail, use the approved playground or a labeled recording; stop troubleshooting at minute 160.
- **02:40-02:50 (10 min): Compare your actual stack.** Record participant-configured work, platform-managed work, facilitator preparation and remaining application responsibilities. Also record one scope constraint, one human decision, and one independently checked CoCo claim. No fixed number of systems avoided and no invented one-to-one AWS replacements. Evidence: participant's own scorecard and next use case.
- **02:50-03:00 (10 min): Cleanup and close.** Ask CoCo to inventory the selected target and propose cleanup without executing it. Use [teardown-guide.md](teardown-guide.md) for exact-target approval, removal or agreed retention, and verification. Record owner/deadline for retained resources and unresolved cleanup. Never sacrifice the break, access proof or cleanup to hide an overrun.

Total: **180 minutes**, including the ten-minute break and ten-minute cleanup. Timings are a plan, not measured delivery evidence.

## APPDEV review lens

Inspect the request/data boundary, connection helper, uppercase-to-lowercase normalization and generated code as maintained application code. During reclamation, focus on input validation, bound parameters, accurate update counts, repeat-request behavior, visible errors and UI refresh. During deployment, inspect dependency lockfile, upload exclusions, remote-build phases, endpoint authentication and logs. Success still requires inspect, change, test and redeploy.

## DE review lens

Trace governed views to source tables, distinguish active spend from inactive opportunity, inspect table grain/key assumptions and understand the deliberate primary-role policy. Module 01 explicitly covers the dataset build recipe; use [dataset-guide.md](dataset-guide.md) for optional depth rather than adding a second setup exercise. During reclamation, inspect the exact predicate, no-op result and dashboard reconciliation; the supplied app shell keeps React authoring bounded. During operations, distinguish SQL warehouse compute from application runtime and optional AI/search costs. Success still requires inspect, change, test and redeploy; semantic authoring and streaming remain optional follow-up.

## Three boundaries, three different proofs

App entry uses USAGE on the **APPLICATION SERVICE**, not a raw SPCS SERVICE. Prove it with the separate non-admin identity described in preflight. Audit PUBLIC and inherited grants, use an isolated browser, reauthenticate after revoke and record the actual result. ACCOUNTADMIN participants cannot prove denial by switching worksheet roles.

Direct SQL policies run in the SQL session's effective context. Disable secondary roles for the denied-write demonstration and restore the recorded original setting afterward. The workshop department policy deliberately tests CURRENT_ROLE, not inheritance. Contract/inventory views expose shared synthetic content; they are not department-filtered.

The starter/reference query path uses **owner's rights**, not per-visitor row identity. An admitted restricted visitor can see the owner's results, and in the completed app may trigger the owner's reclamation update. Optional Ask uses its PAT/service execution identity, not the browser visitor. SQL policy checks and indexed-search access need their own evidence. Never describe this as automatic end-to-end AI governance.

## Honest operating answers

- Remote build and running app are separate phases with separate network settings. Teach what setup resolved and what deploy output actually created/reused; do not claim a new pool was created for each attendee.
- Use live logs and Application Service SHOW/DESCRIBE evidence. An active event table and suitable emitted telemetry are prerequisites for structured historical telemetry. Empty results are not proof of health; do not promise tracing from console lines. Verify version-sensitive SQL log syntax before teaching it.
- Runtime compute, SQL warehouse compute, optional orchestration/tool/search compute, source/artifact storage and retention have distinct cost boundaries. Idle runtime can bill; inspect actual suspension settings rather than assume a safe default. Retention is not free. Warehouse auto-suspend does not stop the app or optional search/refresh workloads.
- Never promise fixed redeploy/cold-start times, per-app chargeback, unlimited preview eligibility, or production SLA coverage without current account/product evidence. Check applicable terms at delivery.
- Flagging is a review status. Opportunity totals are not realized savings, and synthetic contract prose is not legal advice or real vendor pricing.

## Curated facilitator AI questions

- Structured: "Which department has the most inactive Figma assignments?" Inspect generated SQL and compare with the selected account's data.
- Retrieval: "What is the penalty for cancelling Datadog seats early?" Inspect the supporting synthetic clause and citation/quote.
- Combined: "If I cancel all inactive Figma users today, will we be charged a true-up penalty?" Distinguish estimated seat opportunity from contractual constraints.

Clarification behavior is a test, not a promise. Show missing evidence or mistakes candidly; do not keep submitting free-form questions until one appears correct. A working historical mounted PAT is not evidence of current validity.

## Delivery evidence and follow-up

Record actual start/end times, first endpoint time, both build waits, prompt/review latency, focused follow-ups, which checkpoint each participant used, restricted identity results, SQL checks, AI mode used, and cleanup outcome. Keep private details outside the package. Rehearse APPDEV and DE lenses independently against the same 180-minute agenda. Until both pass, release remains gated; a locally parsed document is not a tested workshop.