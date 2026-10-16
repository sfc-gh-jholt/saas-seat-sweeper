# Release checklist and evidence

Status: **not release-ready; live fresh-account and timed rehearsal pending**. This checklist separates authored/static evidence from operational proof. Do not replace a pending box with a historical reference success.

## Baseline

- [x] Local Snowflake CLI reports `3.18.0.dev0`; setup/deploy/teardown help was inspected during authoring on October 15, 2026.
- [x] Command contract: `snowflake.yml` deployment plus build-only `app.yml`; `--deploy-only`, not `--promote-only`.
- [ ] Record exact Node/npm versions, both lockfile hashes and package artifact hash for the release rehearsal.
- [ ] Record CoCo version/authentication and participant OS/shell compatibility. Prompt examples explicitly require Bash, not zsh.
- [ ] Release 3.29.0 is the reported latest release, **untested**. No upgrade or manifest migration approved or performed.

## Administrator readiness: all before minute zero

- [ ] Record account Apps eligibility/enablement, region/edition/policy support, approval owner and date. ACCOUNTADMIN alone is insufficient.
- [ ] Verify explicit workshop connection and unused bootstrap names; protect retained reference account/service. No private account identifiers or endpoint URLs in shareable files.
- [ ] Run 01, 02, 03 in order with stop-on-error; capture query IDs, actual owners and output. Re-running refuses existing objects without changing seed data/grants; test this refusal in a disposable account and compare before/after evidence.
- [ ] Verify 2,000 employees, 15 assets, 10 contracts, variable assignment baseline, five departments, eligible paid inactive assignments, no duplicate assignment keys, no orphan references and nonempty contract text.
- [ ] Verify approved default build path or separately approved narrow `SAAS_SWEEPER_BUILD_EAI`. No broad network access, assumed ALLOW_ALL integration, raw SPCS pool/ECR requirement or authentication weakening.
- [ ] Resolve setup with explicit connection/name/database/schema/warehouse and actual generated resources; unknown values block release. No participant PAT/AI dependency or reference target copied into starter metadata.
- [ ] Prepare separate non-admin restricted identity and isolated browser; audit user, inherited-role and PUBLIC grants. Rehearse grant/allow/revoke/deny with fresh authentication and exact service evidence.
- [ ] Rehearse direct SQL Engineering-only read and denied UPDATE separately; explain owner-rights UI and no per-visitor AI identity.

## Application and package dependencies (owned outside this track)

- [x] Starter is read-only; completed reference remains intact. Participant target configuration is absent in generated starter; no live participant target was created.
- [x] Reference, starter, and independently staged completed overlay pass clean install, TypeScript, focused tests and production build. See `validation-results.md`.
- [ ] Remediate dependency audit: 11 reported vulnerabilities (4 moderate, 6 high, 1 critical), then rerun clean installs/tests/builds before external delivery.
- [ ] First reclaim affects one row; repeated HTTP request affects zero; invalid request rejected; visible errors/no-op feedback and opportunity refresh tested locally and remotely.
- [x] Canonical agenda, participant Markdown, HTML and root README agree on deploy-first ordering, exact slots, 180 minutes, minute-65 endpoint and shared APPDEV/DE agenda.
- [ ] Recovery checkpoints build and run from the packaged download. Participant completed-feature checkpoint contains no facilitator credentials, reference target or mandatory secret mount.
- [x] Legacy broad `teardown.sql`, historical maintainer records and private deployment manifest are isolated outside the repository. Participant cleanup remains selected-target only.
- [ ] Before public distribution, review the complete Git candidate set with `python3 scripts/check_repository.py`, confirm publication rights/license, and verify the clean checkout without local credentials or build artifacts.
- [ ] Portable guide links/assets, two deterministic guide regenerations, browser layouts and upload exclusions pass package-owner verification. No credentials, local environment files, internal research, private account URLs or machine-specific paths in the download.

## CoCo-led delivery checks

- [x] Every working module has a visible canonical prompt, a human decision boundary, and checkable evidence; break and untimed FAQ are exceptions.
- [x] Copy prompt copies only the canonical prompt text; shell/SQL controls remain distinct. Prompt sources, guide, and archive agree byte-for-byte.
- [x] Staged feature prompts keep inspection, local implementation, and approved live verification distinct; the long technical contract is rescue/reference.
- [x] Read-only, local-edit, deployment, write, grant/revoke, and cleanup scopes are not silently combined by a prompt.
- [ ] Verify the chosen CoCo delivery surface supports needed tools. Optional parallel reviews have a sequential fallback and are not required to finish.
- [ ] Timed runs include prompt reading, tool/model latency, human review, corrections and fallback use—not only application build waits.
- [x] Desktop/mobile browser tests cover visible prompts, decisions, evidence, expanded fallback sections, keyboard focus, copy denial and navigation.

## Optional facilitator AI gate

- [ ] Decide live playground, approved reference SSE demo, or labeled recording before delivery. AI omission does not block participant read/write app deployment; disclose any departure from the planned facilitator demo.
- [ ] If creating AI objects, use isolated facilitator sandbox and explicit 05 opt-in after 01-03, not a retained live reference replacement. Validate semantic counts/descriptions against actual grain and filters; current definitions require review before presentation as authoritative metrics.
- [ ] Structured/contract/combined questions verified with SQL and citations/quotes where present. Record identity, tools, errors and date; no guaranteed model output or automatic visitor-policy propagation.
- [ ] For SSE only, approve dedicated read-only service identity, role policy coverage, existing authentication/network policy compliance, narrow runtime path, current PAT expiry, mount and rotation/revocation owner. Historical August 26, 2026 expiry is past; rotation unknown. Never paste secrets into release evidence.
- [ ] Optional 04 backdrop either excluded or separately approved, costed, wired and rehearsed; supplied dashboard does not read it automatically.

## Timed rehearsal: APPDEV lens

- [ ] Fresh eligible account, packaged starter, unused target and no prewarm. Record first endpoint elapsed time; target at or before minute 65.
- [ ] Inspect, generate bounded feature, review code, test and deploy version two by minute 135. Record queue/build waits and checkpoint assistance.
- [ ] Entry/SQL boundary proof, ten-minute break, operations, optional facilitator Ask, scorecard and cleanup all fit their slots; finish at minute 180.
- [ ] Record actuals, blockers, facilitator interventions and fallback use in private delivery evidence. No silently dropped segments to meet arithmetic.

## Timed rehearsal: DE lens

- [ ] Repeat the same agenda with DE review emphasis on grain, policy context, bound update, counts and reconciliation; participant still inspects, changes, tests and redeploys.
- [ ] Record minute-65 endpoint, minute-110 feature checkpoint decision, minute-135 second-deploy cutoff, preserved break and minute-180 cleanup.
- [ ] Explain any overrun, revise checkpoints or mandatory scope, and repeat rehearsal. An APPDEV run does not count as DE evidence.

## Cleanup and sign-off

- [ ] Rehearse service-only 08 cleanup and, if used, the selected-project CLI alternative. Confirm exact selected target removed and unrelated/reference services survive.
- [ ] Inventory retained data, source/artifact storage, integrations and optional AI/search/streaming resources with named owner/expiry; no free-retention claim.
- [ ] Attach private evidence references for setup, both deploys, access denial, feature behavior, logs, elapsed timing and cleanup. Keep shareable checklist free of those private URLs/identifiers.
- [ ] Delivery owner signs off the exact package version and unresolved limitations. Consult `validation-results.md` for local and read-only checks. No fresh-account bootstrap, deployment, credential validation, or timed completion is claimed until explicitly recorded.