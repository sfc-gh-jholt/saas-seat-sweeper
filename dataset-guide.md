# From synthetic sources to application-ready data

The app is one consumer of the dataset, not the whole lab. Module 01 introduces how the data is built and how one metric reaches the UI. The administrator runs the build before the session; participants inspect its design and verify the prepared result before deploying.

## Four source tables and their grain

All source tables live in `SAAS_SEAT_SWEEPER.RAW`.

- **EMPLOYEES:** one employee record identified by `emp_id`, with department, manager and email. The seed is designed to generate 2,000 employees across five departments.
- **CONTRACTS:** one synthetic agreement per `contract_id`. Ten supplied agreements contain renewal fields and free-text terms. These are illustrative, not current vendor pricing or legal advice.
- **ASSETS:** one tracked product or hardware type per `asset_id`. Fifteen supplied entries carry monthly seat cost and an optional contract reference. Several assets can share one contract; some have no contract.
- **EMPLOYEE_ASSETS:** one assignment per intended `(emp_id, asset_id)` key, with activity date and status. One employee can have many assignments. Assignment counts are not distinct employee counts.

The key declarations describe intended relationships; the administrator must verify duplicates and orphan references rather than treating declarations as proof of clean data.

## How the dataset is built

The build recipe is already supplied. Read these files; do not execute them as participant setup:

1. [01_setup.sql](sql/01_setup.sql) prepares the database, schemas, warehouse and workshop roles.
2. [02_seed_data.sql](sql/02_seed_data.sql) creates the four source tables. It generates employees, inserts fixed asset/contract examples, randomly samples employee/asset pairs, and assigns activity dates and statuses. A final insert ensures every employee has an assignment to asset 15. Total assignments and opportunity values vary between builds.
3. [03_rbac_demo.sql](sql/03_rbac_demo.sql) joins source records into app-facing views and attaches the department policy to the spend and inactive-assignment RLS views. Inventory and contract views expose shared synthetic context.
4. The administrator verifies counts, intended key uniqueness, references, nonempty contract text and eligible paid inactive assignments, then records the baseline.

Status and activity date are sampled independently. Do not infer that every `Inactive` row is at least 30 days old, or that the seed guarantees exactly 15% of assignments appear in the app. Read the predicates, not just script comments.

The scripts are guarded first-run setup, not repeatable migrations. Existing tables cause the seed to refuse execution; DDL may already have committed before an error. The full execution and recovery procedure is in [administrator preflight](admin-preflight.md#4-bootstrap-data-and-policy-objects-once). Never rerun the seed to match a screenshot or reset feature-test data.

## Where preparation becomes a business metric

For remaining opportunity, `V_INACTIVE_USERS` joins assignments to employees and assets, retaining `status = 'Inactive'` and activity at least 30 days ago. `V_INACTIVE_USERS_RLS` adds the department policy. The app's `getInactiveUsers` read then retains positive monthly seat costs. `computeMetrics` sums those assignment costs and multiplies the monthly amount by 12 for annualized opportunity.

That is a multi-layer contract: source grain, join keys, status/date predicates, policy context, paid-seat filter and aggregation. Active-spend reporting uses a different status predicate. A flagged assignment leaves the inactive opportunity set; this does not prove vendor cancellation or a lower bill.

Source evidence: [view definitions](sql/03_rbac_demo.sql) and [starter data helpers](starter-app/lib/seat-sweeper-data.ts).

## The participant data-prep exercise

Within Module 01, ask CoCo to explain the build recipe and trace one assignment through the metric. Review the intended grain and filters, then approve only the prepared read-only baseline checks and local launch.

Capture one matching direct-view/UI metric and one modeling risk, such as duplicate assignments inflating totals or null activity dates excluding records. Use the administrator's recorded checks for the broader dataset; a single reconciled metric is not a comprehensive quality audit. Missing preparation is a facilitator blocker, not authorization to recreate tables.

## Adapting this to your own data later

After the workshop, replace the synthetic inputs in a separately approved sandbox. Likely inputs include an employee directory, vendor seat assignments/activity, and procurement agreements; these are suggested source categories, not connectors implemented in this lab.

Before loading, agree on stable employee/product IDs, assignment grain, handling of missing activity, time zones, currency and monthly cost normalization. Reconcile duplicate and orphan records, define the inactivity rule with the business owner, and preserve the app-facing view contract or review the application changes it requires. Decide who owns refreshes and access policies. This extension is not part of the timed three-hour path.
