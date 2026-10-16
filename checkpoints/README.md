# App recovery checkpoints

`starter-app/` and `completed-writeback/` are generated from `reference-app/` by `scripts/prepare_apps.py`, not separately maintained solutions. `starter-overlay/` contains only the read-only control, informational Ask page, participant README, and starter behavior test. The shared table, data helper, contract drawer, dependency lockfile, build pipeline, and assets come from the reference.

## Generate or check (from the package root)

```bash
python3 scripts/prepare_apps.py
python3 scripts/prepare_apps.py --check
python3 checkpoints/test_prepare_apps.py
python3 checkpoints/test_prepare_apps.py --build-recovery
```

The optional `--build-recovery` check generates into a temporary directory, applies the overlay twice, preserves a participant-target sentinel and the Ask/build/lock files, then runs `npm ci --include=dev`, `npm test`, `npm run typecheck` (`tsc --noEmit`), and `npm run build`. It clears inherited Snowflake connection environment variables, uses mocked database calls, verifies built routes/static assets, and deletes only its temporary directory on exit. No PAT, SQL execution, or deployment is required.

The generator also accepts `--output-root <clean-staging-directory>`. It writes `starter-app/` and `checkpoints/completed-writeback/` under that directory, plus deterministic SHA-256 `.generated.json` inventories. It refuses to overwrite detected hand edits or a starter with `snowflake.yml`; use a clean staging directory for packaging. Node modules, builds, environments, credentials, and the facilitator manifest are excluded. The parent packager must copy the checkpoint instructions/apply script and prompt card alongside the generated app. Keep source overlays and generator if regeneration is desired. Do not ship build outputs or dependency directories from tested working trees.

## Completed write-back overlay

Run from the package root, replacing the target with your participant app path:

```bash
python3 checkpoints/apply_writeback.py --target starter-app --dry-run
python3 checkpoints/apply_writeback.py --target starter-app
```

This intentionally replaces the five listed write-back source/test files and removes the read-only-only UI test. Save your work first. It verifies overlay hashes, preserves all other files (including participant `snowflake.yml`, build-only `app.yml`, and informational Ask), and neither installs dependencies nor deploys. Then run `npm test`, `npm run typecheck`, and `npm run build` in the participant app before the second deployment. Do not regenerate over a participant's completed exercise.

Repeat the same HTTP POST to demonstrate zero rows affected; do not rely on clicking a row that vanishes after a successful refresh. Flagging changes review status, not vendor billing. The labeled empty-on-read-error diagnosis fixture remains intentional.