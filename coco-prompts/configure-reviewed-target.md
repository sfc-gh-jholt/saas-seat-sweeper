# Configure the reviewed target

Approve exact dry-run settings and local configuration scope first.

```text
Apply only the deployment configuration we just reviewed for our participant starter. Restate the approved connection, account, role, service FQN, warehouse and prepared integration references. Stop on a mismatch, existing target conflict, missing value, or different CLI manifest format.

Generate or narrowly update the reviewed local manifest, then validate and inspect the local bundle. Preserve the build-only app.yml, lockfile and app source. Report changed configuration and evidence that source/static assets are included while .env files, credentials, dependencies, build debris and backups are excluded. Never display secret values. Do not create prerequisites, change authentication/network policy, deploy, or assume setup refreshed a file it skipped. If blocked, propose the module's configuration checkpoint for review rather than overwriting unrelated files.
```
