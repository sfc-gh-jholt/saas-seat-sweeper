"""QA validator for the SaaS Seat Sweeper workshop package.

Runs static checks against the sql/ and lab-instructions/ directories to catch
regressions before delivery. Complements (does not replace) release-checklist.md
and its live-account rehearsal requirements. Historical maintainer records are
not dependencies of the public workshop repository.

Usage:
    uv run scripts/qa_validator.py
    uv run scripts/qa_validator.py --sql-only
    uv run scripts/qa_validator.py --verbose
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import html5lib

from build_guide import MODULE_IDS, build, canonical_prompt, clock, load_agenda, markdown_tree, package_path, text_of

REPO_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = REPO_ROOT / "sql"
LAB_DIR = REPO_ROOT / "lab-instructions"
APP_DIR = REPO_ROOT / "reference-app"
PROMPT_DIR = REPO_ROOT / "coco-prompts"


@dataclass
class Issue:
    severity: str  # "CRITICAL" | "WARNING"
    file: str
    message: str


@dataclass
class Report:
    issues: list[Issue] = field(default_factory=list)

    def add(self, severity: str, file: str, message: str) -> None:
        self.issues.append(Issue(severity, file, message))

    @property
    def critical_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "CRITICAL")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "WARNING")

    def print_summary(self) -> None:
        print(f"\n{'=' * 60}")
        print("QA Validator Report")
        print(f"{'=' * 60}")
        if not self.issues:
            print("No issues found. Total: 0 critical, 0 warning")
            return
        for issue in self.issues:
            print(f"[{issue.severity}] {issue.file}: {issue.message}")
        print(f"\nTotal: {self.critical_count} critical, {self.warning_count} warning")


def check_sql_syntax(report: Report) -> None:
    """Regex-level checks for known failure patterns (see ISSUES_LOG.md)."""
    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        raw_text = sql_file.read_text()
        text = _strip_sql_comments(raw_text)
        rel = sql_file.relative_to(REPO_ROOT).as_posix()

        # ISSUE-001: WITH ROW ACCESS POLICY must precede AS SELECT, not follow it.
        # Heuristic: flag "WITH ROW ACCESS POLICY" appearing after a "FROM" on an
        # earlier line within the same CREATE VIEW statement (i.e. trailing usage).
        for match in re.finditer(r"CREATE(?:\s+OR\s+REPLACE)?\s+VIEW.*?;", text, re.IGNORECASE | re.DOTALL):
            stmt = match.group(0)
            if "WITH ROW ACCESS POLICY" in stmt.upper():
                as_idx = re.search(r"\bAS\b", stmt, re.IGNORECASE)
                policy_idx = stmt.upper().find("WITH ROW ACCESS POLICY")
                if as_idx and policy_idx > as_idx.start():
                    report.add(
                        "CRITICAL",
                        rel,
                        "WITH ROW ACCESS POLICY appears after AS SELECT (see ISSUES_LOG.md ISSUE-001). "
                        "It must appear between the view name and AS.",
                    )

        # ISSUE-002: REVOKE ... TO ROLE is invalid; must be FROM ROLE.
        for m in re.finditer(r"REVOKE\s+.+?\s+TO\s+ROLE", text, re.IGNORECASE):
            report.add(
                "CRITICAL",
                rel,
                f"REVOKE statement uses 'TO ROLE' instead of 'FROM ROLE' (see ISSUES_LOG.md ISSUE-002): "
                f"...{m.group(0)[-60:]}",
            )

        # Balanced parens (rough heuristic, ignores strings/comments)
        if text.count("(") != text.count(")"):
            report.add("WARNING", rel, "Unbalanced parentheses (heuristic count, may include comments/strings).")

        # Legacy Cortex namespace check (per HOL generator conventions)
        if re.search(r"SNOWFLAKE\.CORTEX\.COMPLETE\(", text, re.IGNORECASE):
            report.add("CRITICAL", rel, "Uses legacy SNOWFLAKE.CORTEX.COMPLETE() — use AI_COMPLETE() instead.")
        if re.search(r"SNOWFLAKE\.CORTEX\.SENTIMENT\(", text, re.IGNORECASE):
            report.add("CRITICAL", rel, "Uses legacy SNOWFLAKE.CORTEX.SENTIMENT() — use AI_SENTIMENT() instead.")


def _strip_sql_comments(text: str) -> str:
    """Remove -- line comments so they don't pollute reference/definition regex matches."""
    return re.sub(r"--.*", "", text)


def check_sql_object_references(report: Report) -> None:
    """Verify that tables/views referenced with FROM/JOIN are defined somewhere in sql/."""
    defined: set[str] = set()
    referenced: dict[str, str] = {}

    define_pattern = re.compile(
        r"CREATE(?:\s+OR\s+REPLACE)?\s+(?:TABLE|VIEW|DYNAMIC\s+TABLE)\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.]+)",
        re.IGNORECASE,
    )
    ref_pattern = re.compile(r"(?:FROM|JOIN)\s+([\w.]+)", re.IGNORECASE)

    for sql_file in sorted(SQL_DIR.glob("*.sql")):
        text = _strip_sql_comments(sql_file.read_text())
        for m in define_pattern.finditer(text):
            defined.add(m.group(1).upper().split(".")[-1])
        for m in ref_pattern.finditer(text):
            name = m.group(1).upper().split(".")[-1]
            if name not in ("TABLE", "GENERATOR"):
                referenced[name] = sql_file.relative_to(REPO_ROOT).as_posix()

    for name, rel in referenced.items():
        if name not in defined:
            report.add(
                "WARNING",
                rel,
                f"References object '{name}' that is not defined via CREATE TABLE/VIEW/DYNAMIC TABLE in any "
                "sql/*.sql file (may be a Snowflake system table/view — verify manually).",
            )


def check_lab_instructions(report: Report) -> None:
    """Check the canonical agenda, not the superseded workshop filenames."""
    check_canonical_modules(report, REPO_ROOT)


def check_canonical_modules(report: Report, root: Path) -> None:
    try:
        agenda = load_agenda(root)
    except (ValueError, OSError, KeyError) as error:
        report.add("CRITICAL", "agenda.json", str(error))
        return
    canonical = {item["file"] for item in agenda["modules"]}
    for path in (root / "lab-instructions").glob("*.md"):
        if path.relative_to(root).as_posix() not in canonical:
            report.add("CRITICAL", path.name, "Orphan lab module is not in the canonical agenda; retire the obsolete flow.")
    elapsed = 0
    for item in agenda["modules"]:
        source = root / item["file"]
        tree = markdown_tree(source.read_text(encoding="utf-8"))
        headings = [text_of(node) for node in tree.iter() if node.tag in {"h1", "h2", "h3", "h4"}]
        h1s = tree.findall("h1")
        if len(h1s) != 1 or not text_of(h1s[0]).casefold().endswith(item["title"].casefold()):
            report.add("CRITICAL", item["file"], "Markdown H1 must match agenda title (an optional module prefix is allowed).")
        timings = [text_of(node) for node in tree.findall("p")
                   if re.match(r"(?:Duration|Time limit):", text_of(node), re.I)]
        if item["minutes"]:
            if not timings:
                report.add("CRITICAL", item["file"], "Missing Duration or Time limit paragraph.")
            for timing in timings:
                match = re.match(r"(?:Duration|Time limit):\s*(\d+)\s*(?:min|minutes)\b", timing, re.I)
                if not match or int(match.group(1)) != item["minutes"]:
                    report.add("CRITICAL", item["file"], "Markdown time limit must match agenda minutes.")
                window = re.search(r"(\d{2}:\d{2})\s*[-–]\s*(\d{2}:\d{2})", timing)
                if window and window.groups() != (clock(elapsed), clock(elapsed + item["minutes"])):
                    report.add("CRITICAL", item["file"], "Markdown time window differs from cumulative agenda schedule.")
            for required, aliases in {
                "action": ("action",), "evidence/checkpoint": ("expected evidence", "verification checkpoint"),
                "recovery": ("recovery",),
            }.items():
                if not any(any(alias in heading.casefold() for alias in aliases) for heading in headings):
                    report.add("CRITICAL", item["file"], f"Missing {required} heading.")
        elif not timings or any(not re.search(r"\buntimed\b", timing, re.I) for timing in timings):
            report.add("CRITICAL", item["file"], "FAQ timing must explicitly say untimed.")
        elapsed += item["minutes"]
        subminutes = [int(match.group(1)) for heading in headings[1:]
                      if (match := re.search(r"\((\d+)\s*min(?:utes)?\)", heading, re.I))]
        if sum(subminutes) > item["minutes"] and item["minutes"]:
            report.add("CRITICAL", item["file"], "Declared sub-activity minutes exceed this module's timebox.")
        prompt_links = [node for paragraph in tree.iter("p") if len(paragraph) == 1
                        and not (paragraph.text or "").strip() and not (paragraph[0].tail or "").strip()
                        for node in paragraph if node.tag == "a" and text_of(node).startswith("Prompt CoCo:")]
        if item["minutes"] and item["id"] != "05-break":
            if not prompt_links:
                report.add("CRITICAL", item["file"], "Missing standalone Prompt CoCo source link.")
            if "your decision" not in [heading.casefold() for heading in headings]:
                report.add("CRITICAL", item["file"], "Missing Your decision approval boundary.")
        for link in prompt_links:
            try:
                canonical_prompt(root, source, link.get("href", ""))
            except (ValueError, OSError) as error:
                report.add("CRITICAL", item["file"], str(error))
        check_markdown_links(report, root, source, tree)
        for paragraph in tree.iter("p"):
            for code in paragraph.iter("code"):
                value = text_of(code)
                if value.startswith("checkpoints/") and not package_path(root, root, value).exists():
                    report.add("CRITICAL", item["file"], f"Missing inline-code checkpoint path: {value}")
        check_claims(report, item["file"], tree)


def check_markdown_links(report: Report, root: Path, source: Path, tree) -> None:
    for node in tree.iter("a"):
        value = node.get("href", "")
        link = urlsplit(value)
        if link.scheme or link.netloc:
            continue
        try:
            target = package_path(root, source.parent, link.path) if link.path else source
            if not target.exists():
                raise ValueError(f"Broken package/checkpoint link: {value}")
            if link.fragment and target.suffix == ".md":
                target_ids = {element.get("id") for element in markdown_tree(target.read_text(encoding="utf-8")).iter()}
                if unquote(link.fragment) not in target_ids:
                    raise ValueError(f"Broken Markdown heading anchor: {value}")
        except ValueError as error:
            report.add("CRITICAL", source.relative_to(root).as_posix(), str(error))


def check_claims(report: Report, filename: str, tree) -> None:
    prose = " ".join(text_of(node) for node in tree.iter() if node.tag in {"p", "li", "td"})
    for pattern, message in (
        (r"\b8\s*[-–]\s*10\s+(?:systems|services)\s+(?:avoided|replaced)", "Predetermined systems-avoided claim"),
        (r"\bno second bill for retention\b", "Unsupported retention-cost claim"),
        (r"\b(?:0|9) of 9 steps complete\b", "Obsolete step-count claim"),
        (r"\bthis buys credibility\b", "Facilitator stage direction in participant content"),
    ):
        if re.search(pattern, prose, re.I):
            report.add("CRITICAL", filename, message)


class TagStack(HTMLParser):
    """Check explicit nesting in addition to HTML5 parser repair diagnostics."""

    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        if tag not in self.VOID:
            self.errors.append(f"Non-void HTML tag self-closed: {tag}")

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Misnested closing tag: {tag}")
        else:
            self.stack.pop()


def validate_html(text: str) -> tuple[object, list[str]]:
    parser = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("etree"), namespaceHTMLElements=False)
    tree = parser.parse(text)
    errors = [f"HTML5 parse error at {position}: {code}" for position, code, _ in parser.errors]
    stack = TagStack()
    stack.feed(text)
    stack.close()
    errors.extend(stack.errors)
    if stack.stack:
        errors.append(f"Unclosed tags: {stack.stack}")
    ids = set()
    for node in tree.iter():
        if not isinstance(node.tag, str):
            continue
        node_id = node.get("id")
        if node_id:
            if node_id in ids:
                errors.append(f"Duplicate HTML id: {node_id}")
            ids.add(node_id)
        if node.tag in {"iframe", "object", "embed", "base", "video", "audio", "form"}:
            errors.append(f"Forbidden embedded element: {node.tag}")
        for name, value in node.attrib.items():
            if name.lower().startswith("on"):
                errors.append(f"Inline event handler: {name}")
            if name in {"href", "src"} and urlsplit(value).scheme.lower() in {"javascript", "vbscript"}:
                errors.append(f"Unsafe URL: {name}")
            if name in {"src", "srcset", "poster"} and not (node.tag == "img" and name == "src" and value.startswith(("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/gif;base64,", "data:image/webp;base64,"))):
                errors.append(f"Nonportable asset: {node.tag}.{name}")
        if node.tag == "link":
            errors.append("Linked asset instead of inline asset")
        if node.tag == "style" and re.search(r"@import|url\s*\(", node.text or "", re.I):
            errors.append("CSS asset request is not portable")
        if node.tag == "script" and node.get("type") != "application/json":
            if re.search(r"\b(?:eval|fetch|XMLHttpRequest|WebSocket|Worker|localStorage|sessionStorage)\b|new\s+Function|sendBeacon|document\.cookie|\.innerHTML\s*=", node.text or ""):
                errors.append("Unsafe or network/storage-dependent script")
    for node in tree.iter("a"):
        href = node.get("href", "")
        if href.startswith("#") and unquote(href[1:]) not in ids:
            errors.append(f"Broken guide anchor: {href}")
        if href.lower().startswith("data:"):
            errors.append("Data URI navigation is not allowed")
    return tree, errors


def check_guide(report: Report, root: Path = REPO_ROOT) -> None:
    try:
        agenda = load_agenda(root)
        generated = build(root)
        if generated != build(root):
            report.add("CRITICAL", "lab-guide.html", "Regeneration is nondeterministic.")
        published_bytes = (root / "lab-guide.html").read_bytes()
        published = published_bytes.decode("utf-8")
        if published_bytes != generated.encode("utf-8"):
            report.add("CRITICAL", "lab-guide.html", "Source/render drift. Run scripts/build_guide.py.")
        tree, errors = validate_html(published)
        for error in errors:
            report.add("CRITICAL", "lab-guide.html", error)
        landing = next((node for node in tree.iter("section") if node.get("id") == "introduction"), None)
        if landing is None:
            report.add("CRITICAL", "lab-guide.html", "Missing introduction landing page.")
        else:
            agenda_list = landing.find(".//ol[@class='agenda-list']")
            expected_links = ["#" + item["id"] for item in agenda["modules"] if item["minutes"]]
            if agenda_list is None or [node.get("href") for node in agenda_list.iter("a")] != expected_links:
                report.add("CRITICAL", "lab-guide.html", "Introduction agenda differs from timed modules.")
        sections = [node for node in tree.iter("section") if node.get("class") == "step"]
        if [node.get("id") for node in sections] != list(MODULE_IDS):
            report.add("CRITICAL", "lab-guide.html", "Rendered module IDs/order differ from agenda.")
        for section, item in zip(sections, agenda["modules"]):
            if section.get("data-minutes") != str(item["minutes"]):
                report.add("CRITICAL", item["id"], "Rendered duration differs from agenda.")
            timings = [node for node in section.iter() if node.get("class") == "step-duration"]
            if len(timings) != 1:
                report.add("CRITICAL", item["id"], "Expected one rendered timing display.")
            if any(re.match(r"(?:Duration|Time limit):", text_of(node), re.I) for node in section.iter("p")):
                report.add("CRITICAL", item["id"], "Duplicate source timing in rendered body.")
            if item["minutes"] and item["id"] != "05-break":
                for css_class in ("prompt-card", "semantic-panel panel-decision", "semantic-panel panel-evidence", "semantic-panel panel-recovery"):
                    if not any(node.get("class") == css_class for node in section.iter()):
                        report.add("CRITICAL", item["id"], f"Missing semantic component: {css_class}")
            for card in [node for node in section.iter() if node.get("class") == "prompt-card"]:
                source = canonical_prompt(root, root / "lab-guide.html", card.get("data-source", ""))
                code = card.find("./pre/code")
                if code is None or code.text != source["text"]:
                    report.add("CRITICAL", item["id"], "Embedded prompt differs from canonical fence.")
                if card.get("data-sha256") != source["sha256"] or card.get("data-prompt-sha256") != source["promptSha256"]:
                    report.add("CRITICAL", item["id"], "Prompt source/hash provenance mismatch.")
            title = section.find("./header/h1")
            if title is None or text_of(title) != item["title"]:
                report.add("CRITICAL", item["id"], "Rendered title differs from agenda.")
        metadata_node = next((node for node in tree.iter("script") if node.get("id") == "snowflake-report-metadata"), None)
        if metadata_node is None:
            report.add("CRITICAL", "lab-guide.html", "Missing source provenance metadata.")
        else:
            metadata = json.loads(metadata_node.text or "")
            if [item["id"] for item in metadata["sections"]] != ["introduction", *MODULE_IDS]:
                report.add("CRITICAL", "lab-guide.html", "Provenance section IDs differ from agenda.")
        check_claims(report, "lab-guide.html", tree)
    except (OSError, ValueError, KeyError) as error:
        report.add("CRITICAL", "lab-guide.html", str(error))


def check_reference_app(report: Report) -> None:
    """Heuristics for regressions specific to the reference Next.js app (ISSUE-010/011/012)."""
    if not APP_DIR.exists():
        return

    # ISSUE-010: Server Components (no "use client") must not fetch relative /api/* URLs.
    for tsx_file in sorted(APP_DIR.rglob("*.tsx")):
        if "node_modules" in tsx_file.parts:
            continue
        text = tsx_file.read_text()
        rel = tsx_file.relative_to(REPO_ROOT).as_posix()
        is_client = text.lstrip().startswith('"use client"') or text.lstrip().startswith("'use client'")
        if not is_client and re.search(r"""fetch\(\s*["']/api/""", text):
            report.add(
                "CRITICAL",
                rel,
                "Server Component (no 'use client') calls fetch() on a relative /api/ URL — "
                "this fails with 'Failed to parse URL' (see ISSUES_LOG.md ISSUE-010). "
                "Use a direct querySnowflake() call instead, or mark the file 'use client'.",
            )

    required_routes = [
        APP_DIR / "app" / "page.tsx",
        APP_DIR / "app" / "licenses" / "page.tsx",
        APP_DIR / "app" / "inventory" / "page.tsx",
        APP_DIR / "app" / "ask" / "page.tsx",
    ]
    for route_file in required_routes:
        if not route_file.exists():
            report.add(
                "CRITICAL",
                route_file.relative_to(REPO_ROOT).as_posix() if route_file.exists() else route_file.as_posix().replace(f"{REPO_ROOT.as_posix()}/", ""),
                "Missing required premium app route. Expected Overview, Licenses, Inventory, and Ask routes.",
            )

    shell_file = APP_DIR / "components" / "app-header.tsx"
    if shell_file.exists():
        shell_text = shell_file.read_text()
        for expected in ["Overview", "Licenses", "Inventory", "Ask"]:
            if expected not in shell_text:
                report.add(
                    "WARNING",
                    shell_file.relative_to(REPO_ROOT).as_posix(),
                    f"Sidebar shell does not mention required nav item '{expected}'.",
                )
    else:
        report.add("CRITICAL", "reference-app/components/app-header.tsx", "Missing app shell/sidebar component.")

    # ISSUE-011: querySnowflake() results should be normalized with lowercaseKeys() before use.
    # Exclude template utility routes that are intentionally out of scope for Seat Sweeper's own
    # data model (owner's/caller's-rights demo, current-timestamp demo) — they already handle
    # their own uppercase column names correctly (e.g. `rows[0]?.TIME`).
    template_utility_routes = {"app/api/query/route.ts", "app/api/time/route.ts"}
    for ts_file in sorted((APP_DIR / "app" / "api").rglob("*.ts")) + sorted((APP_DIR / "app").rglob("*.tsx")):
        if "node_modules" in ts_file.parts:
            continue
        rel = ts_file.relative_to(REPO_ROOT).as_posix()
        if rel.endswith(tuple(f"reference-app/{r}" for r in template_utility_routes)):
            continue
        text = ts_file.read_text()
        if "querySnowflake(" in text and not re.search(r"lowercaseKeys(<[^>]*>)?\(", text) and "UPDATE " not in text.upper():
            report.add(
                "WARNING",
                rel,
                "Calls querySnowflake() without lowercaseKeys() — Snowflake returns UPPERCASE column "
                "names by default (see ISSUES_LOG.md ISSUE-011). Verify this call doesn't need normalization "
                "(e.g. DML with no column-keyed result use) before ignoring.",
            )


def check_prompt_alignment(report: Report) -> None:
    """Ensure CoCo prompts describe the same premium app contract as the reference app."""
    prompt_files = [
        PROMPT_DIR / "scaffold-app.md",
        PROMPT_DIR / "add-writeback.md",
        PROMPT_DIR / "add-ask-panel.md",
    ]

    for prompt_file in prompt_files:
        if not prompt_file.exists():
            report.add("CRITICAL", prompt_file.relative_to(REPO_ROOT).as_posix(), "Missing required CoCo prompt file.")
            continue
        text = prompt_file.read_text()
        if not re.search(r"lowercaseKeys|normaliz", text, re.IGNORECASE):
            report.add(
                "WARNING",
                prompt_file.relative_to(REPO_ROOT).as_posix(),
                "Prompt does not require Snowflake result key normalization (lowercaseKeys or equivalent).",
            )

    scaffold = PROMPT_DIR / "scaffold-app.md"
    if scaffold.exists():
        text = scaffold.read_text()
        for term in ["Overview", "Licenses", "Inventory", "Ask"]:
            if term.casefold() not in text.casefold():
                report.add(
                    "WARNING",
                    scaffold.relative_to(REPO_ROOT).as_posix(),
                    f"Scaffold prompt is missing premium app contract term: '{term}'.",
                )

    writeback = PROMPT_DIR / "add-writeback.md"
    if writeback.exists() and "/licenses" not in writeback.read_text():
        report.add(
            "WARNING",
            writeback.relative_to(REPO_ROOT).as_posix(),
            "Writeback prompt should target the /licenses route.",
        )

    ask = PROMPT_DIR / "add-ask-panel.md"
    if ask.exists() and "/ask" not in ask.read_text():
        report.add(
            "WARNING",
            ask.relative_to(REPO_ROOT).as_posix(),
            "Ask prompt should wire the existing /ask route, not a disconnected panel.",
        )


def check_generated_apps(report: Report) -> None:
    """Check app-agent outputs without generating or overwriting participant work."""
    import subprocess

    generator = REPO_ROOT / "scripts" / "prepare_apps.py"
    if not generator.is_file():
        report.add("CRITICAL", "scripts/prepare_apps.py", "Missing starter/checkpoint generator.")
        return
    try:
        result = subprocess.run(
            [sys.executable, str(generator), "--check"], cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        report.add("CRITICAL", "starter-app/", f"Generated app check could not finish: {error}")
        return
    if result.returncode:
        report.add("CRITICAL", "starter-app/", "Starter/checkpoint generation parity failed; await the app owner or obtain the prepared package.\n"
                   + (result.stdout + result.stderr).strip()[:2000])


def check_reference_app_types(report: Report) -> None:
    """Run `npx tsc --noEmit` in reference-app/ — `next build` alone skips type validation (ISSUE-012)."""
    if not APP_DIR.exists() or not (APP_DIR / "node_modules").exists():
        report.add(
            "WARNING",
            "reference-app/",
            "Skipped `tsc --noEmit` check: node_modules not found. Run `npm install` in reference-app/ first.",
        )
        return

    import subprocess

    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=APP_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        report.add(
            "CRITICAL",
            "reference-app/",
            f"`npx tsc --noEmit` failed (next build alone does not catch this — see ISSUES_LOG.md ISSUE-012):\n"
            f"{result.stdout.strip()[:2000]}",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--sql-only", action="store_true", help="Only run SQL checks")
    scope.add_argument("--guide-only", action="store_true", help="Only check canonical modules and generated guide")
    parser.add_argument("--skip-tsc", action="store_true", help="Skip the tsc --noEmit check (slower, needs npm install)")
    parser.add_argument("--verbose", action="store_true", help="Print files as they're checked")
    args = parser.parse_args()

    report = Report()

    if args.guide_only:
        check_lab_instructions(report)
        check_guide(report)
        report.print_summary()
        return int(report.critical_count > 0)

    if args.verbose:
        print(f"Checking SQL files in {SQL_DIR} ...")
    check_sql_syntax(report)
    check_sql_object_references(report)

    if not args.sql_only:
        if args.verbose:
            print(f"Checking lab instructions in {LAB_DIR} ...")
        check_lab_instructions(report)
        check_guide(report)

        if args.verbose:
            print(f"Checking CoCo prompts in {PROMPT_DIR} ...")
        check_prompt_alignment(report)

        if args.verbose:
            print(f"Checking reference app in {APP_DIR} ...")
        check_reference_app(report)
        check_generated_apps(report)

        if not args.skip_tsc:
            if args.verbose:
                print("Running tsc --noEmit (this may take a moment) ...")
            check_reference_app_types(report)

    report.print_summary()
    return 1 if report.critical_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
