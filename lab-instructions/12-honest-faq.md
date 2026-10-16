# 12 - Honest FAQ

Use these boundaries to challenge workshop claims and choose the next proof your team needs.

**Time limit:** Untimed reference, 0 agenda minutes. This does not extend the 180-minute workshop.

## What did this lab actually prove?

Each participant started from prepared read-only source, configured their own target, attempted a first Application Service deployment, added a bounded write-back feature, and attempted a second deployment. Your scorecard determines which proofs passed. A shared facilitator URL, a local build, and a participant-deployed URL are different outcomes.

The account began basically empty. An administrator prepared data, roles, warehouse, eligibility, and approved build/network prerequisites before the timer. ACCOUNTADMIN alone does not supply these. The participant service was intentionally not predeployed.

## Does Reclaim save money?

Not by itself. It flags an inactive assignment for review. It does not call a vendor API, cancel a license, enforce cancellation terms, or change an invoice. The remaining-opportunity metric decreases because the flagged record leaves the inactive queue. Annualization multiplies the remaining monthly cost by 12; realized savings need a separate verified business process.

## Are all users seeing only their own data?

No. This app's deployed reads and writes use owner's rights. A service USAGE grant controls entry, not per-visitor row visibility or action authorization. The SQL view exercise proves filtering for the selected SQL role; it does not prove visitor-specific UI filtering. The demo policy also permits other roles by default, and the restricted role has raw-table read grants, so this is not complete tenant isolation.

Production needs a reviewed identity and authorization design, including write authorization, input validation, sensitive-output handling, and appropriate least-privilege grants. Caller-aware execution is a separate implementation and testing task, not a promise that changing a flag secures every route. An ACCOUNTADMIN browser cannot establish the negative entry proof.

## Does the agent run as the visitor?

Not in this reference integration. The REST call uses the mounted PAT's principal/role, separately from the visitor and the SQL service identity. Inspect the actual credential and grants without exposing the secret. Credential rotation, expiry, network policy, and authorization remain responsibilities. Without a PAT, the reference fallback still requires a service token; ordinary local development does not automatically provide it.

## Are AI answers guaranteed or deterministic?

No. Inspect generated SQL for structured answers, retrieved passages/citations when available, and what the model inferred. Do not assume every response contains SQL, every retrieval includes a useful citation, or every ambiguous question triggers clarification. Semantic definitions, tests, retrieval quality, prompt design, and ongoing evaluation still need owners. The synthetic contract demo is not legal advice or certified financial reporting.

## Which infrastructure did we avoid managing?

Compare only the workflow you exercised. In this deployment path you submitted source/build instructions instead of manually building and pushing a container image, and used a platform-provided authenticated endpoint instead of configuring its TLS/ingress yourself. The account and integrations were prepared, not absent. The app still has server routes and application logic; "no API layer" is inaccurate for a Next.js app with API routes.

On your current AWS or other stack, some of these responsibilities may already be managed or shared. Compare application hosting/deployment, employee identity, access grants, SQL access, logging, and optional AI retrieval/orchestration. Do not assume AWS requires a second application database, self-managed Kubernetes, a hand-built vector stack, or a fixed number of services. This lab does not evaluate ingestion, pub/sub, model serving, general-purpose transactional databases, or a CDN, so do not map those products from it.

## Is this just Kubernetes, and who owns what?

This lab exercises the Application Service abstraction; it does not establish the internals of Snowflake's scheduler. Platform-managed build/runtime operations remove specific manual tasks in the tested path. Your team still owns source, dependencies, correctness, authorization design, data contracts, budget, and incident response. Do not treat managed infrastructure as production-ready application code.

## Can I debug it like my existing application?

Use local reproduction, explicit type/tests, live service logs, and actual service status. This workshop does not demonstrate SSH access or remote debugger attachment. Event-table telemetry requires supported configuration and instrumentation; it is not automatically equivalent to your APM's tracing, alerting, dashboards, or retention. The supplied read helper's error-to-empty-array behavior is a known teaching fixture: a plausible zero and HTTP 200 can conceal a query failure. Production should distinguish query failures from genuine empty results.

## What costs money?

Potential costs include app build/runtime compute, SQL warehouse compute, stored data/artifacts/telemetry, CoCo use, and the AI services/models used by the facilitator. Idle service compute and retained storage are not automatically free. Inspect actual suspension settings and the applicable pricing/contract; do not infer costs from request counts alone. Historical metering may lag and account-level compute totals do not necessarily attribute cost to one app. Logging retention has cost and policy implications; there is no blanket "no second bill" promise.

## Can I roll back?

Record actual package versions, not assumed sequential names. A facilitator can review deploying a prior compatible version using the supported Application Service lifecycle path. Code rollback does not reverse `Flagged` records or other database changes. Do not guess version flags, use Native App version commands, or assume an old runtime remains deployable without checking it.

## Is the data Iceberg, and is the app portable?

The supplied setup creates ordinary Snowflake tables; this lab provides no evidence that its data is Iceberg v3 or exposed through an open catalog. Next.js/TypeScript source can be adapted for another host, but the SQL, connection helper, policies/grants, deployment configuration, and AI integration are platform-specific work to replace. Portability is not zero-cost migration.

## What about outages, networking, and production terms?

The app depends on Snowflake and the data/services it calls. Running near the data is not independence from platform incidents. Confirm current availability, support/SLA terms, region/account eligibility, network paths, and recovery requirements with the administrator and account team. Do not treat historical preview wording or a workshop success as current contractual evidence. Build-time network permission does not automatically authorize the same egress at runtime; use reviewed integrations rather than a broad allow-all recovery shortcut.

## Why not use the latest CLI or generate the whole app?

Reproducibility matters more than adding an untested upgrade mid-session. Local command checks used CLI `3.18.0.dev0`, Node `22.12.0`, and npm `10.9.0`. Release `3.29.0` was discovered but not installed/tested here. Keep `snowflake.yml` plus build-only `app.yml` and the supplied lockfile until a separately approved rehearsal supports a change. The optional [scaffold prompt](../coco-prompts/scaffold-app.md) is take-home work. The timed [feature exercise](06-build-reclamation.md) separates planning, approved local implementation and evidence review; [add-writeback.md](../coco-prompts/add-writeback.md) is the detailed rescue reference, not the main prompt.

## What did we learn to delegate?

CoCo helps inspect source, propose a bounded change, act within an approved scope and collect evidence. The participant still checks identity/target, reviews diffs, approves live effects and challenges missing proof. Local mocked tests do not prove deployed writes; generated summaries do not replace observed outputs. The facilitator's runtime Cortex Agent answers business questions and is not the development assistant.

Tool availability depends on the delivery surface. Use manual fallbacks when a tool is unavailable and label supplied observations honestly. Parallel read-only reviews are optional only after support is verified; sequential review is sufficient. No new agent or full-app scaffold is required.

## What still blocks release?

Dependency vulnerabilities, an obtainable supported delivery CLI, fresh-account deployments/access proofs and timed persona rehearsals remain release gates until verified. This content redesign does not close them, and a schedule totaling 180 minutes is not a measured rehearsal.

## What is the next production step?

Choose one internal use case and measure the missing proof: least-privilege ownership, visitor/action authorization, error handling, audit trail, load/latency, operational alerts, cost attribution, credential rotation, or recovery. Do not point this ACCOUNTADMIN workshop app at real customer data as-is. Use [scorecard.md](../scorecard.md) to assign a concrete owner and success condition.