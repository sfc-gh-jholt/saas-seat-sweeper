# Build with CoCo: SaaS Seat Sweeper

A three-hour hands-on lab in directing and verifying agentic work on Snowflake. Use Cortex Code to inspect a supplied application, plan and perform its first deployment, implement a bounded feature, diagnose failures, and verify a second deployment. Seat Sweeper gives the work a concrete Finance/IT outcome; the transferable skill is knowing what to delegate, when to approve, and how to check the result.

**Inspect. Propose. Approve. Act. Verify. Two real deployments in 180 minutes.**

Flagging a seat is a review status, not vendor cancellation or realized savings. The application uses synthetic data and service-identity queries; it is not a production-hardening certification.

## Start here

**Notebook track (local CoCo Desktop):** clone this repository and open [START_HERE.ipynb](START_HERE.ipynb). It combines short instructions, runnable Python/SQL cells and three focused CoCo prompts. Each participant builds their own synthetic dataset, then uses the `snowflake-apps` skill for two deployments. Setup requires explicit account/user checks and fresh confirmation per script; no default connection is used.

Before the session, the facilitator verifies the local Python kernel (`snowflake-connector-python` and `ipykernel`), named connection, Node/npm, delivery CLI, App Runtime eligibility and skill availability. Do not pre-run SQL 01–03 for the notebook track. After participant bootstrap, complete any approved schema-dependent build integration and restricted-user role assignment before the relevant exercise. The notebook's revised opening time budgets are proposed and not yet rehearsed.

**Prepared-data HTML track (reference):** the existing guide below uses administrator-prepared data and the original opening schedule. Choose one track; do not execute both setup paths. The broader guide conversion is not complete.

1. The administrator completes [Fresh-account preflight](admin-preflight.md) before the timer starts. Accounts may begin essentially empty with ACCOUNTADMIN. That role does not guarantee App Runtime eligibility, configured networking, or working local credentials.
2. Open [the portable HTML guide](lab-guide.html#introduction) for the lab outline and three-hour agenda, then start Module 00. The [introduction source](introduction.md) is also available in Markdown. Within each exercise, use the visible **Prompt CoCo** cards, review **Your decision**, and inspect evidence before marking complete. Expand manual commands only when needed. HTML embeds the canonical prompt files; Markdown links to the same sources.
3. Clone the facilitator-provided workshop repository at the delivery revision, then open its root in CoCo so it can read the agenda, prompts, reviewer checklists and starter together. A downloaded ZIP is an alternative; open its extracted root. Make application changes in `starter-app/`, not `reference-app/`. The starter has no active reclamation endpoint or required AI credential. Its deployment target is deliberately not configured.
4. Keep [the scorecard](scorecard.md) and [cleanup guide](teardown-guide.md) with your evidence.

Each person works individually, using their own isolated account, application project and deployment target. Data and approved prerequisites exist before the session; the participant's Application Service and endpoint do not. A facilitator demonstration URL is observation-only recovery, not completion of your deployment.

## Session

The [agenda](agenda.json) assigns exactly 180 minutes, including a ten-minute break and ten-minute cleanup. The first live endpoint target is minute 65. Both personas inspect, change, test, and redeploy; neither needs a different agenda.

The full-app scaffold prompt is optional take-home work. AI-object creation, CI/CD, and raw container infrastructure are not on the mandatory path. CoCo is the development/operations assistant throughout; the facilitator's Cortex Agent is a separate runtime business-question demo with its own identity and credential lifecycle. Neither a green build nor a confident model response substitutes for observed evidence.

## Package contents

- `START_HERE.ipynb`: local notebook entry point; no saved outputs or account-specific configuration.
- `scripts/notebook_lab.py`: guarded first-run bootstrap helper; no connection on import.
- `lab-guide.html`: self-contained prepared-data reference guide; no hosted asset dependency.
- `lab-instructions/` and `agenda.json`: canonical participant content and timing.
- `introduction.md`: lab outline; the HTML landing page adds the agenda directly from `agenda.json`.
- `dataset-guide.md`: source-table grain, seed construction, governed metric path and optional real-data adaptation; used in Module 01 before deployment.
- `starter-app/`: generated read-only starting application and pinned npm lockfile.
- `reference-app/`: completed solution source, with facilitator-only Ask integration.
- `checkpoints/`: generated recovery instructions/files; retain your own deployment manifest.
- `coco-prompts/`: staged canonical prompts for inspection, planning, implementation, diagnosis, verification and cleanup, plus rescue/optional extensions.
- `sql/`: administrator-reviewed setup; not a command to run every script indiscriminately.
- `admin-preflight.md`, `facilitator-guide.md`, `deployment-checkpoint.md`, `teardown-guide.md`: setup, delivery, recovery, and narrow cleanup.
- `scorecard.md`: participant outcome and evidence record.
- `release-checklist.md`, `validation-results.md`, `rehearsal-record.md`: delivery status and reusable rehearsal records; not extra participant exercises.

## Repository boundaries

Participants need the guide, prompts, SQL, `starter-app/` and recovery checkpoints. The completed `reference-app/`, starter overlay and `scripts/` remain as portable source dependencies so a clean clone can regenerate and verify the lab. They are not a second participant application to deploy. Facilitator/setup documents remain because the lab cannot be delivered from source alone.

Historical issue/alignment logs, research notes and the legacy broad teardown are not distributed. Account-specific deployment manifests, environment files, credentials, dependencies, caches, logs and build archives are excluded from Git. Keep private delivery evidence outside this repository. Do not force-add ignored files.

The root `.gitignore` allowlists reviewed entry points. Before any commit or publication, run `python3 scripts/check_repository.py`; it compares the complete proposed Git file set with the package allowlist and scans candidate content. New public entry points require an explicit update to both allowlists. This check is not a substitute for reviewing every file or selecting an appropriate license before distribution.

## Maintain and generate

From the package root, after installing Python/uv and the documented prerequisites:

```bash
python3 scripts/prepare_apps.py
uv run --project scripts python scripts/build_guide.py
uv run --project scripts python scripts/qa_validator.py --verbose
python3 scripts/validate_notebook.py
python3 scripts/test_notebook.py
python3 scripts/check_repository.py
python3 scripts/package_workshop.py
```

The app generator refuses unsafe destinations and provides its own recovery interface; consult `--help` before resetting a participant working directory. Apply the bounded feature recovery with `python3 checkpoints/apply_writeback.py --target starter-app --dry-run`, then remove `--dry-run` only after reviewing replacements. Edit canonical sources rather than a generated copy. The packaging script includes only intended files, scans for common credential/private-path patterns, and produces a local ZIP plus a content-digest manifest. A scan is a defense in depth, not a guarantee against all possible secrets.

No package creation uploads or publishes anything. Sharing destination and recipients are a separate decision.

## Release status

Consult [the release checklist](release-checklist.md) and `validation-results.md` for actual test results. Historical deployment evidence is not current verification. The locally observed development CLI is not an assumed publicly installable prerequisite; choose and rehearse the delivery CLI before promising this lab is room-ready.

Do not run commands against an implicit default connection. Confirm the assigned workshop account and explicit connection first. The maintainer's live reference target is never the default destination in the downloadable package.