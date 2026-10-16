# Guide generation and offline QA

`introduction.md` supplies the default landing page's lab outline. Its linked agenda is generated directly from `agenda.json`; it adds no timed module or completion control. Module 00 links back to it, and existing module anchors are unchanged.

`agenda.json` and its `lab-instructions/*.md` modules are canonical. Do not hand-edit
`lab-guide.html`. Edit `guide-template.html` only for presentation or interactions.
The renderer preserves the sidebar layout, system/light/dark themes, module
navigation, exact prompt/code copying (with a selected readonly text-field fallback),
and in-memory progress. Blue prompt cards lead the workbench; amber decision
panels identify human review, evidence stays neutral blue, and green indicates
only participant-marked completion.
No external scripts, fonts, images, storage, or runtime network requests are used.

From the package root:

```bash
uv sync --locked --project scripts
uv run --project scripts scripts/build_guide.py
uv run --project scripts scripts/build_guide.py --check
uv run --project scripts scripts/test_workshop.py -v
uv run --project scripts scripts/qa_validator.py --guide-only
uv run --project scripts scripts/qa_validator.py --skip-tsc
```

All paths may be absolute; these commands do not depend on the current directory
when both project and script paths are absolute. `--root PATH` on the renderer
supports another complete package. `--check` never writes. Generation is
deterministic (UTF-8, stable source hashes, no clock timestamps). Exit status is
nonzero on invalid inputs or parity drift.

## Authoring contract

- Agenda schema: `{ "title": "...", "modules": [{ "id": "...", "title": "...", "minutes": 10, "file": "lab-instructions/00-overview.md" }] }`.
- The approved 13 module IDs and durations are validated in order: twelve timed
  modules total 180 minutes, including break and cleanup; FAQ has zero minutes.
- Each Markdown H1 ends with its agenda title. Timed modules have a matching
  `**Time limit:** N minutes` (or `**Duration:** N minutes`) paragraph and Action,
  Expected evidence (or Verification checkpoint), and Recovery headings. An explicit
  `HH:MM-HH:MM` window must match the cumulative agenda. Conflicting timing
  declarations fail. FAQ timing explicitly says Untimed.
- Main prompts use a standalone paragraph, with no surrounding text:
  `[Prompt CoCo: Review the target](../coco-prompts/plan-deployment.md)`.
  The referenced UTF-8/LF Markdown must contain exactly one nonempty top-level
  fenced `text` block. Its contents, including whitespace and final newline, are
  embedded once and copied as-is by **Copy prompt**, never **Copy code**. Other
  prose in that source is not copied. Missing files, query/fragment URLs, remote
  sources, traversal and symlink escapes outside `coco-prompts/` fail closed.
- Each prompt card records the package-relative source, full source SHA-256 and
  prompt-text SHA-256 in data attributes; section metadata includes both hashes.
  A short visible source/hash helps identify which prompt is in use.
- `Your decision`, `Expected evidence` / `Verification checkpoint`, and `Recovery`
  headings become distinct visible panels. `Manual commands`, `Recovery commands`,
  `Why this matters`, and `If blocked` become closed details panels. Heading IDs
  stay intact; deep links automatically open containing details. A new prompt
  exits the preceding semantic panel rather than becoming part of its decision.
- The introductory paragraph becomes the outcome header. Source Duration/Time
  limit declarations are replaced by one agenda-derived timing display; additional
  allocation/cutoff prose is preserved visibly. Sidebar journey labels carry no
  duplicated module timings. Main Recovery content is never collapsed.
- Each timed module except the break requires an inline prompt and Your decision.
- Use normal Markdown tables, nested lists, fenced code, and links. A pinned
  Python-Markdown parser renders content; Bleach allowlists passive markup and
  html5lib performs structured transformations. Raw `details`/`summary` is supported.
  Forbidden raw markup is escaped, not executed. Headings get module-prefixed IDs.
- Module links become internal anchors. Other local links remain package-relative
  and require adjacent package files. The HTML and its assets are standalone;
  linked source/checkpoint downloads still require the full package. Documentation
  links are ordinary hyperlinks, never fetched by generation or QA.
- Local PNG/JPEG/GIF/WebP images are embedded as data URIs. Remote images and
  paths escaping the package fail generation. A logo at `assets/snowflake-logo.png`,
  `assets/logo.png`, or the corresponding `reference-app/public/` path is embedded
  if present. SVG is not accepted as an untrusted image input.

## Checks and limits

Guide QA checks two generations plus committed-file parity; canonical module IDs,
order, titles and times; declared sub-activity overruns; missing module contract
sections; orphan old modules; package/checkpoint links and Markdown anchors; known
obsolete claims; duplicate IDs; broken guide anchors; explicit tag nesting;
HTML5 parse/repair errors; network assets and prohibited scripting patterns.
The JavaScript pattern check is a regression guard, not a full security analyzer.

The broader validator retains existing SQL/app/prompt regression heuristics and
runs `prepare_apps.py --check` to verify starter/checkpoint byte parity without
writing app files. Missing or drifting generated apps fail; wait for the app owner
rather than generating over participant work. Inline `checkpoints/...` references
in participant prose must resolve, as must normal Markdown links.
`--sql-only` runs historical SQL heuristics; these do not compile or run SQL.
The default broader run also invokes local `npx tsc --noEmit` if dependencies exist;
use `--skip-tsc` during concurrent app edits. Legacy tracker IDs and old 00-08
filenames are no longer release requirements. `--guide-only` and `--sql-only` are
mutually exclusive.

## Optional offline browser suite

The default test command runs 27 fixture tests and explicitly skips 10 browser tests.
Enable the pinned optional `browser` group and point at an existing Chromium/Chrome
executable, or use an already-installed Playwright Chromium browser:

```bash
uv sync --locked --group browser --project scripts
GUIDE_BROWSER_TESTS=1 GUIDE_BROWSER_EXECUTABLE="/path/to/chrome" uv run --locked --group browser --project scripts scripts/test_workshop.py -v
```

Omit `GUIDE_BROWSER_EXECUTABLE` to use Playwright's installed Chromium. This does
not install/download a browser automatically; an unavailable browser is a test
error when browser testing is explicitly enabled. Generate the guide first.
The suite opens only the local guide with network requests blocked and browser
storage access denied. It checks the introduction plus all 13 modules at 1440px and at 360px in light
and dark themes with disclosures expanded, left-aligned sidebar/content layout,
next/previous/deep/repeated/skip-link navigation, keyboard disclosure controls,
completion/reset, canonical prompt source/hash parity, copy controls, and inlined
assets. All embedded prompts are compared byte-for-byte with their canonical
text payload after simulated clipboard success. Denial selects a readonly text
field so terminal newlines survive manual copy (DOM text selection drops them
in Chrome). Success and denial are simulated deterministically, not a claim
about clipboard permissions in every host sandbox.

Static or browser success is **not** deployment, authorization, external-link
availability, or timing-rehearsal verification. No command here deploys an app,
executes Snowflake SQL, uploads content, or builds an archive.