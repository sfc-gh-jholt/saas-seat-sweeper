# Optional take-home prompt - scaffold a read-only Seat Sweeper

This is not the timed workshop path. Participants run the supplied `starter-app/`, deploy it, then follow the staged [reclamation exercise](../lab-instructions/06-build-reclamation.md) for the bounded feature. The packager generates starter and recovery assets with `scripts/prepare_apps.py`; do not generate competing app copies during class. Preserve `reference-app/` as the completed solution.

For take-home work, choose a separate scratch directory and an explicitly approved participant connection. Replace all `REPLACE_...` placeholders before submitting this prompt. Do not allow the current/default Snowhouse connection to be used accidentally. Account preparation remains a prerequisite; this prompt does not authorize live SQL, deployment, account changes, or an upgrade.

## Prompt

```text
Create a read-only SaaS Seat Sweeper prototype in REPLACE_WITH_ABSOLUTE_SCRATCH_DIRECTORY.
Use only the explicitly approved connection REPLACE_WITH_PARTICIPANT_CONNECTION if
I later authorize data access. Do not run live SQL, deploy, create infrastructure,
upgrade tools/dependencies, or change authentication/network policies now.

Inspect the supplied starter/reference source before writing code. Reuse the
connection helper, result-key normalization, styling conventions, dependency
lockfile, and server-side data access patterns. Do not edit the original starter,
reference, or any configured participant deployment manifest. Keep the tested
snowflake.yml plus build-only app.yml layout; no app.yml v2 migration.

Create Next.js App Router pages with a persistent left sidebar:
- /: Overview of monthly inactive-license opportunity, annualized remaining
  opportunity (monthly * 12), active-assignment spend and department spend.
- /licenses: read-only inactive paid assignments with names, departments, assets,
  costs and days inactive, plus contract inspection. No active Reclaim button.
- /inventory: assets, active assigned counts, renewal metadata and contract drawer.
- /ask: clearly labeled landing page with structured, contract-text and combined
  example questions. No live agent endpoint or copied credentials.

Use SAAS_SEAT_SWEEPER.APP.V_SPEND_BY_DEPARTMENT_RLS and V_INACTIVE_USERS_RLS for
the corresponding reads, and V_ASSET_INVENTORY and V_CONTRACT_TERMS for inventory
and contract details. These are the prepared workshop source contract; inspect
the supplied SQL definitions rather than inventing columns. Server Components
should use the shared data module, not relative fetches to internal API routes.
Normalize unquoted Snowflake result keys before consuming fields.

Do not add POST /api/reclaim, UPDATE statements, or any other write-back.
Reclamation is a separate staged follow-up in lab-instructions/06-build-reclamation.md;
coco-prompts/add-writeback.md is its detailed rescue reference, not the main prompt.
Label all savings-like values as opportunity, not realized savings or forecasts.
Do not promise per-visitor filtering: the supplied deployed app uses owner's
rights, while local development uses the explicitly selected local credentials.
Do not imply the Ask landing page is a functioning agent.

Include visible loading, empty and error states. Explain any reused catch-to-empty
fixture rather than presenting it as production-safe behavior. Preserve explicit
type checking and focused tests; a successful Next.js build is not enough.
Keep dependency versions pinned by the supplied lockfile. No new libraries are
required for this exercise. Never copy facilitator manifests, secret mounts,
credentials, URLs or broad network integration references.

Return the changed files, assumptions, proposed local verification commands,
and remaining account-preparation dependencies. Wait for approval before live
data access or deployment.
```

## Review after generation

- [ ] The output is in the approved scratch directory only.
- [ ] All four routes exist; Licenses is read-only and Ask is clearly a landing page.
- [ ] Result normalization, data contracts, metric meanings, and error handling were reviewed.
- [ ] No account defaults, facilitator credentials, or fixed demo destinations were copied.
- [ ] No reclaim feature was added prematurely.
- [ ] Type checks, tests, and a local build are planned before deployment approval.

Adding `date-fns` and demonstrating a lockfile change is also optional take-home work. It is not required before either timed deployment and must not consume the protected break or cleanup slots.