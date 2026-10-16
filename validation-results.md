# Deploy-first release validation

## Status

Local release candidate assembled and validated. **Not approved for room delivery:** dependency vulnerabilities, an obtainable delivery-CLI rehearsal, fresh-account deployment/access tests, and both timed persona runs remain release blockers.

## Observed toolchain

- Snowflake CLI: 3.18.0.dev0; setup/deploy help checked locally.
- Node: v22.12.0; npm: 10.9.0.
- Latest public CLI release observed: 3.29.0; not installed or tested here.
- Manifest layout retained: build-only app.yml plus snowflake.yml.

## Completed read-only checks (October 16, 2026)

- Active connection identity verified after the account switch; no workshop SQL ran against the prior telemetry connection.
- `DESCRIBE TABLE SAAS_SEAT_SWEEPER.RAW.EMPLOYEE_ASSETS` confirmed numeric EMP_ID/ASSET_ID, DATE activity, and VARCHAR STATUS columns.
- Compile-only conditional reclamation UPDATE passed against the existing workshop table. No DML executed. SDK-bind behavior still requires the local focused tests and fresh-target live rehearsal.
- Existing retained reference Application Service was RUNNING at VERSION$9, with auto-suspend disabled. Status was inspected, not changed. This is not evidence of a new participant deployment.
- Packaging unit tests: five passed, including deterministic ZIP bytes and exclusion of local environments, deployment manifests and build output.
- Guide suite: 27/27 passed (20 renderer/QA fixtures and 7 offline Chrome tests). Covers all 13 modules at desktop and 360px, navigation/deep links, progress/reset, themes, copy success/denial, and blocked network/storage access.
- Parent browser smoke check: navigation, completion toggle, and clipboard copy worked; at 358px the document had no horizontal overflow and long code scrolled within its block.
- Final guide regeneration parity passed; guide-only QA reported zero critical issues and zero warnings.
- Integrated QA reported zero critical issues and four SQL-reference heuristic warnings (`APP`, `TABLES`, `SPECIFICATION`, `THE`). Those static heuristics are not a full SQL compilation check.
- Release ZIP creation verifies every archived byte and CRC against the selected source files and includes a SHA-256 file manifest. Secrets/environment files, dependencies/build output, private deployment manifests, internal research, and legacy broad teardown are excluded.
- Static administrator review found and corrected a SQL string-quoting defect in optional AI setup and non-stopping shell checks in the deployment checkpoint. Full fresh-account scripts remain unexecuted.
- Participant and facilitator recovery cutoffs reconciled at minute 110; the recovery instructions invoke the actual checksum-checked overlay applier. Cleanup defaults to the selected service, with broader CLI source cleanup explicitly separate.

## CoCo-led redesign verification (October 16, 2026)

This supersedes the earlier 27-test guide result above. The redesign changes workshop content and rendering, not application architecture or live services.

- All 11 non-break timed modules contain staged canonical prompts, human decision boundaries and evidence. Nineteen inline prompt cards are embedded from source files, with source and prompt hashes.
- Final guide suite: **37/37 passed** (27 fixture tests and 10 offline Chrome tests). Covers the introduction and all 13 modules at desktop and 360px, light/dark themes, expanded disclosures, keyboard focus, deep links, progress/reset, prompt/code copy success and denial, and blocked network/storage access.
- Every embedded prompt's copied payload matches its canonical text, including its final newline. Clipboard denial uses a selected readonly text field. An additional desktop-browser smoke check copied the feature-planning prompt successfully.
- Guide regeneration parity passed; two generations were identical. Guide-only QA: zero critical issues and zero warnings. Integrated QA, including TypeScript: zero critical issues and the same four SQL-reference heuristic warnings noted above.
- Packaging safety tests: 5/5 passed. Generated starter/checkpoint drift check reported no changed files.
- Preserved all agenda IDs, twelve timed slots totaling 180 minutes, minute-65 first endpoint target, minute-110 feature recovery decision and minute-135 second-deploy hard stop. This is schedule validation, not measured delivery time.
- Safety review corrected package-root context, exact live-proof endpoint/IDs/executor approval and uncertain-response handling. The challenge pass reuses unchanged gate results instead of requiring redundant full reruns.
- Added a default introduction landing page with lab outcomes, outline and agenda generated directly from `agenda.json`. It has no completion control and adds no minutes; existing module deep links remain valid.
- Module 01 now includes the synthetic dataset build recipe, table/assignment grain and source-to-view-to-metric trace before the first deployment. Its two prompts remain read-only inspection followed by approved baseline/launch; setup and reseeding stay outside the timed participant path. `dataset-guide.md` documents construction and optional real-source adaptation from inspected SQL/app source. No new SQL was authored or executed.
- Facilitator guide, participant scorecard, rehearsal record and release checklist now track delegation, approval, source/tool evidence, follow-ups and prompt/review latency.

The dependency, supported delivery CLI, fresh-account deployment/access and timed persona rehearsal gates remain unresolved. No new live SQL, deployment, grants or cleanup were performed for this redesign.

## Application verification

- Reference: clean npm install; 90/90 tests across 7 files; explicit TypeScript check and production build passed.
- Read-only starter: clean npm install; 41/41 tests across 6 files; explicit TypeScript check and production build passed.
- Completed overlay: independently staged clean install; 90/90 tests across 7 files; TypeScript and production build passed. No active Ask endpoint or mandatory PAT mount.
- Generator/recovery: 11/11 Python tests; repeated generation and drift check passed. Overlay preserves deployment configuration and verifies checksums before writes.
- Mocked page/POST integration proves bound positive IDs, accurate update count, repeated zero-row no-op, and refreshed opportunity values ($240/year, $20/month, one assignment to zero). These are synthetic test values, not live customer savings.
- npm reports 11 dependency vulnerabilities: 4 moderate, 6 high, 1 critical. No dependency upgrades were performed. Review and remediate before external delivery, then repeat clean-install tests/builds.

## Pending account and room checks

- Fresh eligible account bootstrap, using approved networking and authentication.
- First participant deployment into an absent service target, then second deployment with write-back.
- Real data success/no-op, contract drawer, route/static-asset behavior after both deployments.
- App-entry denial using a separate restricted identity, direct-SQL policy behavior, and restored access.
- Facilitator agent credential validity, SQL/citations, and tool-permission behavior.
- Live logs, version evidence, cost/suspension review, and scoped cleanup.
- Timed application-developer and data-engineer rehearsals preserving break and cleanup.

No live reference service is changed by local source/package checks. A successful build or an exact 180-minute agenda is not a completed live rehearsal.