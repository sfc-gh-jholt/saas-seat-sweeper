"""Offline renderer/QA regression tests; fixtures never touch workshop sources."""

import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from subprocess import CompletedProcess, TimeoutExpired

from build_guide import MINUTES, MODULE_IDS, ROOT, build, canonical_prompt, load_agenda, package_path
from qa_validator import Report, check_canonical_modules, check_generated_apps, check_guide, validate_html


class GuideTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "lab-instructions").mkdir()
        (self.root / "coco-prompts").mkdir()
        (self.root / "coco-prompts/exercise.md").write_text("# Source\n\n```text\nInspect the target.\nAsk before writes.\n```\n")
        (self.root / "introduction.md").write_text("# Introduction\n\nBuild an internal application with CoCo.\n\n## Three-hour agenda\n\nElapsed session times.\n")
        (self.root / "scripts").mkdir()
        (self.root / "scripts/guide-template.html").write_text((ROOT / "scripts/guide-template.html").read_text())
        self.agenda = {"title": "Seat Sweeper", "modules": []}
        for module_id, minutes in zip(MODULE_IDS, MINUTES):
            title = module_id.split("-", 1)[1].replace("-", " ").title()
            filename = f"lab-instructions/{module_id}.md"
            self.agenda["modules"].append({"id": module_id, "title": title, "minutes": minutes, "file": filename})
            (self.root / filename).write_text(f"# {title}\n\n**Duration:** {str(minutes) + ' minutes' if minutes else 'Untimed reference'}\n\n"
                "## Action\n\nDo the exercise.\n\n[Prompt CoCo: Inspect first](../coco-prompts/exercise.md)\n\n"
                "### Your decision\n\nApprove only the reviewed scope.\n\n## Expected evidence\n\nRecord the result.\n\n"
                "## Time limit\n\nStop at the cutoff.\n\n## Recovery\n\nAsk for help.\n")
        self.write_agenda()

    def write_agenda(self):
        (self.root / "agenda.json").write_text(json.dumps(self.agenda))

    def append(self, text, index=0):
        source = self.root / self.agenda["modules"][index]["file"]
        source.write_text(source.read_text() + "\n" + text + "\n")

    def test_deterministic_full_parity_and_structure(self):
        first = build(self.root)
        self.assertEqual(first, build(self.root))
        (self.root / "lab-guide.html").write_text(first)
        report = Report()
        check_canonical_modules(report, self.root)
        check_guide(report, self.root)
        self.assertEqual(report.issues, [])
        tree, errors = validate_html(first)
        self.assertEqual(errors, [])
        self.assertEqual(len([n for n in tree.iter("button") if n.get("class") == "btn btn-primary complete"]), 12)
        self.assertIn("Untimed reference", first)
        self.assertIn("180 minutes", first)

    def test_introduction_agenda_and_source_parity(self):
        document = build(self.root)
        tree, errors = validate_html(document)
        self.assertEqual(errors, [])
        pages = [node for node in tree.iter('section') if 'step' in node.get('class', '').split()]
        self.assertEqual(pages[0].get('id'), 'introduction')
        self.assertEqual(len(pages), 14)
        rows = pages[0].find('.//ol').findall('li')
        self.assertEqual(len(rows), 12)
        self.assertEqual(rows[0].find('span').text, '00:00 - 00:10')
        self.assertEqual(rows[-1].find('span').text, '02:50 - 03:00')
        self.assertEqual([row.find('a').get('href') for row in rows], ['#' + item for item in MODULE_IDS[:-1]])
        self.assertFalse(list(pages[0].iter('button')))
        source = self.root / 'introduction.md'
        source.write_text(source.read_text() + '\nUpdated introduction.\n')
        self.assertNotEqual(document, build(self.root))

    def test_opening_prompt_has_bounded_orientation_scope(self):
        source = ROOT / "lab-instructions/00-overview.md"
        prompt = canonical_prompt(ROOT, source, "../coco-prompts/workshop-orient.md")["text"]
        for boundary in (
            "Read only introduction.md and agenda.json",
            "reuse them",
            "Do not list directories",
            "read application code or other modules",
            "report its exact path and stop rather than searching",
            "at most 180 words",
            "exactly four bullets",
            "not verified application behavior",
            "Stop after the briefing",
        ):
            self.assertIn(boundary, prompt)
        self.assertNotIn("starter's entry points", prompt)
        document = build(ROOT)
        tree, errors = validate_html(document)
        self.assertEqual(errors, [])
        cards = [node for node in tree.iter("section")
                 if node.get("data-source") == "coco-prompts/workshop-orient.md"]
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].find("./pre/code").text, prompt)

    def test_exact_prompt_and_provenance(self):
        prompt = '  Preserve indentation & <tags>.\n\n"Quotes", Unicode: café.\nTrailing spaces.  \n'
        path = self.root / "coco-prompts/exercise.md"
        path.write_text("# Do not copy this\n\n```text\n" + prompt + "```\n\nNot this either.\n")
        document = build(self.root)
        tree, errors = validate_html(document)
        self.assertEqual(errors, [])
        cards = [node for node in tree.iter("section") if node.get("class") == "prompt-card"]
        for card in cards:
            self.assertEqual(card.find("./pre/code").text, prompt)
            self.assertEqual(card.get("data-source"), "coco-prompts/exercise.md")
            self.assertEqual(card.get("data-sha256"), hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(card.get("data-prompt-sha256"), hashlib.sha256(prompt.encode()).hexdigest())
        metadata = json.loads(next(node.text for node in tree.iter("script") if node.get("type") == "application/json"))
        self.assertEqual(metadata["sections"][1]["dataSources"][1]["path"], "coco-prompts/exercise.md")
        path.write_text(path.read_text().replace("Inspect", "Review") + "\nChanged provenance.\n")
        self.assertNotEqual(build(self.root), document)

    def test_prompt_sources_fail_closed(self):
        source = self.root / "lab-instructions/00-overview.md"
        for href in ("../../outside.md", "../coco-prompts/%2e%2e/agenda.json", "../README.md",
                     "https://example.com/prompt.md", "//example.com/prompt.md", "../coco-prompts/missing.md",
                     "../coco-prompts/exercise.md#part", "../coco-prompts/exercise.md?raw=1"):
            with self.subTest(href=href), self.assertRaises(ValueError):
                canonical_prompt(self.root, source, href)
        (self.root / "coco-prompts/link.md").symlink_to(source)
        with self.assertRaises(ValueError):
            canonical_prompt(self.root, source, "../coco-prompts/link.md")

    def test_prompt_fence_contract(self):
        path = self.root / "coco-prompts/exercise.md"
        for body in ("no fence", "```bash\nwrong\n```", "```text\n```", "```text\nunfinished",
                     "```text\none\n```\n\n```text\ntwo\n```", "```text\none\n```\n\n```bash\nextra\n```"):
            with self.subTest(body=body):
                path.write_text(body)
                with self.assertRaises(ValueError):
                    build(self.root)

    def test_semantic_panels_disclosures_and_single_timing(self):
        self.append("## Manual commands\n\n```bash\nprintf test\n```\n\n### Nested command\n\nDetails.\n\n"
                    "## Recovery commands\n\nRescue.\n\n## Checklist\n\nKeep visible.")
        tree, errors = validate_html(build(self.root))
        self.assertEqual(errors, [])
        section = next(node for node in tree.iter("section") if node.get("id") == MODULE_IDS[0])
        content = section.find("./div[@class='module-content']")
        for kind in ("decision", "evidence", "recovery"):
            self.assertTrue(any(node.get("class") == "semantic-panel panel-" + kind for node in content.iter()))
        disclosures = list(content.iter("details"))
        self.assertEqual(len(disclosures), 2)
        self.assertTrue(all("open" not in node.attrib for node in disclosures))
        self.assertEqual(disclosures[0].find("./summary/h2").get("id"), "00-overview--manual-commands")
        self.assertFalse(any(node.get("class") == "semantic-panel panel-recovery" for disclosure in disclosures for node in disclosure.iter()))
        self.assertEqual(len([node for node in section.iter() if node.get("class") == "step-duration"]), 1)
        self.assertNotIn("Duration:", "".join(content.itertext()))
        self.assertIsNotNone(content.find("h2[@id='00-overview--checklist']"))

    def test_outcome_and_cutoff_preserved_without_duplicate_timing(self):
        path = self.root / self.agenda["modules"][0]["file"]
        path.write_text(path.read_text().replace("**Duration:** 10 minutes", "A concrete outcome.\n\n**Time limit:** 10 minutes, 00:00-00:10. Stop generation at minute 8."))
        tree, errors = validate_html(build(self.root))
        self.assertEqual(errors, [])
        section = next(node for node in tree.iter("section") if node.get("id") == MODULE_IDS[0])
        self.assertEqual(section.find("./header/div[@class='step-outcome']/p").text, "A concrete outcome.")
        self.assertIn("Stop generation at minute 8.", "".join(section.itertext()))
        self.assertNotIn("Time limit:", "".join(section.itertext()))

    def test_missing_prompt_and_decision_fails_qa(self):
        path = self.root / self.agenda["modules"][0]["file"]
        path.write_text(path.read_text().replace("[Prompt CoCo: Inspect first](../coco-prompts/exercise.md)", "").replace("### Your decision", "### Notes"))
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.critical_count, 2)

    def test_source_drift_fails(self):
        (self.root / "lab-guide.html").write_text(build(self.root))
        self.append("New canonical evidence.")
        report = Report()
        check_guide(report, self.root)
        self.assertTrue(any("drift" in issue.message for issue in report.issues))

    def test_invalid_agenda_order_and_minutes(self):
        self.agenda["modules"][0]["minutes"] = 11
        self.write_agenda()
        with self.assertRaises(ValueError):
            load_agenda(self.root)
        self.agenda["modules"][0]["minutes"] = 10
        self.agenda["modules"].reverse()
        self.write_agenda()
        with self.assertRaises(ValueError):
            load_agenda(self.root)

    def test_markdown_features_and_code_escaping(self):
        self.append('```html\n<script>alert("x")</script>\n```\n\n| Left | Right |\n| --- | --- |\n| **Bold** | `code` |\n\n- outer\n    - inner\n\n<details><summary>More</summary><p>Reference</p></details>')
        result = build(self.root)
        tree, errors = validate_html(result)
        self.assertEqual(errors, [])
        self.assertIsNotNone(tree.find(".//div[@class='table-wrap']/table"))
        self.assertIsNotNone(tree.find(".//ul/li/ul/li"))
        self.assertIsNotNone(tree.find(".//details/summary"))
        self.assertIn('&lt;script&gt;', result)

    def test_malicious_markdown_cannot_execute(self):
        self.append('<script>fetch("https://evil.invalid")</script>\n\n<p onclick="alert(1)">Text</p>\n\n[bad](javascript:alert(1))\n\n<iframe src="https://evil.invalid"></iframe>')
        tree, errors = validate_html(build(self.root))
        self.assertEqual(errors, [])
        self.assertEqual(len(list(tree.iter("script"))), 2)
        self.assertFalse(list(tree.iter("iframe")))

    def test_metadata_escape_and_single_pass_template(self):
        self.agenda["title"] = '</script><script>alert(1)</script> @@NAV@@'
        self.write_agenda()
        self.append('Literal @@SECTIONS@@ token.')
        tree, errors = validate_html(build(self.root))
        self.assertEqual(errors, [])
        self.assertEqual(len(list(tree.iter("script"))), 2)
        metadata = next(n for n in tree.iter("script") if n.get("type") == "application/json")
        self.assertEqual(json.loads(metadata.text)["intent"], self.agenda["title"])

    def test_cross_module_and_duplicate_heading_anchors(self):
        self.append('[Next](01-run-starter.md#action)\n\n[Here](#action)\n\n## Action\n\nSecond action.')
        result = build(self.root)
        self.assertIn('href="#01-run-starter--action"', result)
        self.assertIn('href="#00-overview--action"', result)
        self.assertIn('id="00-overview--action_1"', result)
        self.assertEqual(validate_html(result)[1], [])

    def test_missing_link_and_escaping_path_fail(self):
        self.append('[Recovery](../checkpoints/missing.md)')
        with self.assertRaises(ValueError):
            build(self.root)
        with self.assertRaises(ValueError):
            package_path(self.root, self.root, '../outside')

    def test_images_inline_and_remote_rejected(self):
        (self.root / "assets").mkdir()
        # Signature suffices for the encoding contract, not a visual image test.
        (self.root / "assets/logo.png").write_bytes(b'\x89PNG\r\n\x1a\n')
        self.append('![Logo](../assets/logo.png)')
        self.assertIn('src="data:image/png;base64,', build(self.root))
        self.append('![Remote](https://example.invalid/logo.png)')
        with self.assertRaises(ValueError):
            build(self.root)

    def test_broken_anchor_missing_checkpoint_and_orphan_fail(self):
        self.append('[Invalid](#missing)')
        (self.root / "lab-instructions/99-obsolete.md").write_text('obsolete')
        source = self.root / self.agenda["modules"][1]["file"]
        source.write_text(source.read_text().replace('## Recovery', '## Notes'))
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.critical_count, 3)

    def test_structural_validator_detects_repair_and_unsafe_assets(self):
        document = '<!DOCTYPE html><html><head><title>Bad</title></head><body><p><div id="same">Bad</div></p><div id="same"><a href="#missing">Link</a><img src="https://example.invalid/a.png" onload="bad()"></div></body></html>'
        errors = validate_html(document)[1]
        for expected in ('HTML5 parse error', 'Duplicate HTML id', 'Broken guide anchor', 'Nonportable asset', 'Inline event handler'):
            self.assertTrue(any(expected in error for error in errors), expected)

    def test_obsolete_claim_and_subactivity_overrun_fail(self):
        self.append('## One (8 minutes)\n\n## Two (8 minutes)\n\n8–10 systems avoided.')
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.critical_count, 2)

    def test_published_time_limit_contract_and_window(self):
        source = self.root / self.agenda["modules"][0]["file"]
        source.write_text(source.read_text().replace("**Duration:** 10 minutes", "**Time limit:** 10 minutes, 00:00-00:10").replace("## Time limit\n\nStop at the cutoff.\n", ""))
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.issues, [])
        source.write_text(source.read_text().replace("00:00-00:10", "00:10-00:20"))
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.critical_count, 1)
        self.assertIn("time window", report.issues[0].message)

    def test_missing_and_conflicting_timing_fail(self):
        source = self.root / self.agenda["modules"][0]["file"]
        source.write_text(source.read_text().replace("**Duration:** 10 minutes", "No timing declaration."))
        self.append("**Time limit:** 99 minutes", index=1)
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.critical_count, 2)

    def test_faq_time_limit_is_untimed(self):
        source = self.root / self.agenda["modules"][-1]["file"]
        source.write_text(source.read_text().replace("**Duration:**", "**Time limit:**"))
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.issues, [])
        source.write_text(source.read_text().replace("Untimed reference", "10 minutes"))
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.critical_count, 1)

    def test_missing_inline_checkpoint_fails(self):
        self.append("Recover with `checkpoints/writeback/`.")
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.critical_count, 1)
        self.assertIn("inline-code checkpoint", report.issues[0].message)

    def test_byte_parity_rejects_line_ending_drift(self):
        (self.root / "lab-guide.html").write_bytes(build(self.root).replace("\n", "\r\n").encode())
        report = Report()
        check_guide(report, self.root)
        self.assertEqual(report.critical_count, 1)
        self.assertIn("drift", report.issues[0].message)

    def test_package_relative_link_and_spaces(self):
        (self.root / "recovery notes.md").write_text("# Recovery\n")
        self.append("[Recovery](../recovery%20notes.md#recovery)")
        self.assertIn('href="recovery%20notes.md#recovery"', build(self.root))
        report = Report()
        check_canonical_modules(report, self.root)
        self.assertEqual(report.issues, [])

    def test_generated_app_check_is_read_only(self):
        (self.root / 'scripts/prepare_apps.py').write_text('pass\n')
        with patch('qa_validator.REPO_ROOT', self.root), patch('subprocess.run', return_value=CompletedProcess([], 0, '', '')) as run:
            report = Report()
            check_generated_apps(report)
        self.assertEqual(report.issues, [])
        self.assertEqual(run.call_args.args[0][-1], '--check')

    def test_generated_app_check_reports_missing_drift_and_timeout(self):
        with patch('qa_validator.REPO_ROOT', self.root):
            report = Report()
            check_generated_apps(report)
            self.assertEqual(report.critical_count, 1)
            (self.root / 'scripts/prepare_apps.py').write_text('pass\n')
            with patch('subprocess.run', return_value=CompletedProcess([], 1, 'Missing starter', '')):
                report = Report()
                check_generated_apps(report)
                self.assertEqual(report.critical_count, 1)
                self.assertIn('Missing starter', report.issues[0].message)
            with patch('subprocess.run', side_effect=TimeoutExpired('prepare_apps.py', 120)):
                report = Report()
                check_generated_apps(report)
                self.assertEqual(report.critical_count, 1)
                self.assertIn('could not finish', report.issues[0].message)


@unittest.skipUnless(os.environ.get("GUIDE_BROWSER_TESTS") == "1", "Set GUIDE_BROWSER_TESTS=1 with the browser dependency group")
class BrowserTests(unittest.TestCase):
    """Exercise the actual generated guide; never open participant app links."""

    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)
        executable = os.environ.get("GUIDE_BROWSER_EXECUTABLE")
        cls.browser = cls.playwright.chromium.launch(executable_path=executable)
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 900}, offline=True)
        self.addCleanup(self.context.close)
        self.context.route("https://**/*", lambda route: route.abort())
        self.context.route("http://**/*", lambda route: route.abort())
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.requests = []
        self.page.on("request", lambda request: self.requests.append(request.url))
        self.page.add_init_script("""for (const name of ['localStorage', 'sessionStorage']) {
          Object.defineProperty(window, name, {get() {throw new Error('Storage denied');}});
        }""")
        self.page.goto((ROOT / "lab-guide.html").as_uri())
        self.page.wait_for_function("document.querySelectorAll('.step:not([hidden])').length === 1")

    def tearDown(self):
        self.assertEqual(self.errors, [])
        self.assertFalse([url for url in self.requests if url.startswith(('http:', 'https:'))])

    def select_module(self, module_id):
        self.page.locator(f'.nav-link[href="#{module_id}"]').click()
        self.page.wait_for_function("id => !document.getElementById(id).hidden", arg=module_id)

    def test_introduction_default_and_agenda_navigation(self):
        self.assertTrue(self.page.locator('#introduction').is_visible())
        self.assertEqual(self.page.locator('#introduction .complete').count(), 0)
        self.assertEqual(self.page.locator('#progress').get_attribute('max'), '12')
        self.page.locator('#introduction .step-header').get_by_role('link', name='Start the lab', exact=True).click()
        self.page.wait_for_function("!document.getElementById('00-overview').hidden")
        self.page.locator('[id="00-overview"] .step-nav').get_by_role('link', name='Introduction', exact=True).click()
        self.page.wait_for_function("!document.getElementById('introduction').hidden")
        self.page.locator('#introduction .agenda-list a[href="#06-build-reclamation"]').click()
        self.page.wait_for_function("!document.getElementById('06-build-reclamation').hidden")

    def test_desktop_sidebar_and_navigation(self):
        self.assertEqual(self.page.locator('.nav-link').count(), 14)
        main = self.page.locator('main').bounding_box()
        sidebar = self.page.locator('.sidebar').bounding_box()
        self.assertAlmostEqual(main['x'], sidebar['x'] + sidebar['width'], delta=1)
        for module_id in MODULE_IDS:
            self.select_module(module_id)
            self.assertEqual(self.page.locator('.step:not([hidden])').count(), 1)
            self.assertEqual(self.page.locator('.nav-link[aria-current="step"]').get_attribute('href'), '#' + module_id)
        self.page.get_by_role('link', name='Previous', exact=True).filter(visible=True).click()
        self.page.wait_for_function("!document.getElementById('11-cleanup').hidden")
        self.assertTrue(self.page.locator('[id="11-cleanup"]').is_visible())
        self.page.get_by_role('link', name='Next', exact=True).filter(visible=True).click()
        self.page.wait_for_function("!document.getElementById('12-honest-faq').hidden")
        self.assertTrue(self.page.locator('[id="12-honest-faq"]').is_visible())

    def test_narrow_layout_all_modules_and_copy_controls(self):
        self.page.set_viewport_size({"width": 360, "height": 800})
        for module_id, theme in [(module_id, theme) for theme in ('light', 'dark') for module_id in ('introduction', *MODULE_IDS)]:
            self.page.evaluate("theme => document.documentElement.style.colorScheme = theme", theme)
            self.select_module(module_id)
            self.page.locator('.step:not([hidden]) details').evaluate_all("nodes => nodes.forEach(node => node.open = true)")
            metrics = self.page.evaluate("""() => ({width: innerWidth, scroll: document.documentElement.scrollWidth,
              badButtons: [...document.querySelectorAll('.step:not([hidden]) button')].filter(node => {
                const box = node.getBoundingClientRect(); return box.left < 0 || box.right > innerWidth;
              }).length})""")
            self.assertLessEqual(metrics['scroll'], metrics['width'], module_id)
            self.assertEqual(metrics['badButtons'], 0, module_id)
            self.assertEqual(self.page.locator(f'[id="{module_id}"] .copy-button').count(), self.page.locator(f'[id="{module_id}"] pre > code').count())
        self.select_module('01-run-starter')
        self.page.locator('.step:not([hidden]) .copy-button').first.click()
        self.page.wait_for_function("document.getElementById('copy-status').textContent.length > 0")

    def test_deep_links_skip_link_and_repeat_navigation(self):
        self.page.goto((ROOT / 'lab-guide.html').as_uri() + '#06-build-reclamation--expected-evidence')
        self.page.wait_for_function("!document.getElementById('06-build-reclamation').hidden")
        self.assertTrue(self.page.locator('[id="06-build-reclamation"]').is_visible())
        self.page.locator('.skip-link').focus()
        self.page.keyboard.press('Enter')
        self.page.wait_for_function("document.activeElement.id === 'main'")
        self.page.wait_for_function("!document.getElementById('06-build-reclamation').hidden")
        self.assertTrue(self.page.locator('[id="06-build-reclamation"]').is_visible())
        self.select_module('04-access')
        self.select_module('04-access')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'title-04-access')
        self.page.goto((ROOT / 'lab-guide.html').as_uri() + '#%ZZ')
        self.page.wait_for_function("!document.getElementById('introduction').hidden")
        self.assertTrue(self.page.locator('[id="introduction"]').is_visible())

    def test_completion_reset_and_no_storage(self):
        for module_id in MODULE_IDS[:-1]:
            self.select_module(module_id)
            self.page.locator(f'[id="{module_id}"] .complete').click()
        self.assertEqual(self.page.locator('#progress').get_attribute('value'), '12')
        self.assertEqual(self.page.locator('.nav-link.done').count(), 12)
        self.select_module(MODULE_IDS[-1])
        self.assertEqual(self.page.locator('[id="12-honest-faq"] .complete').count(), 0)
        self.page.locator('#reset-progress').click()
        self.assertEqual(self.page.locator('#progress').get_attribute('value'), '0')
        self.assertEqual(self.page.locator('.nav-link.done').count(), 0)

    def test_copy_success(self):
        self.select_module('01-run-starter')
        self.page.evaluate("""() => Object.defineProperty(navigator, 'clipboard', {value: {
          writeText: async text => { window.copiedText = text; }
        }, configurable: true})""")
        self.page.locator('.step:not([hidden]) details').evaluate_all("nodes => nodes.forEach(node => node.open = true)")
        self.page.locator('.step:not([hidden]) [data-copy-kind="code"]').first.click()
        self.page.wait_for_function("window.copiedText !== undefined")
        self.assertEqual(self.page.evaluate('window.copiedText'), self.page.locator('.step:not([hidden]) pre:not(.prompt-text) > code').first.text_content())
        self.assertEqual(self.page.locator('#copy-status').text_content(), 'Code copied.')

    def test_copy_denial_selects_exact_code(self):
        self.select_module('01-run-starter')
        self.page.evaluate("""() => Object.defineProperty(navigator, 'clipboard', {value: {
          writeText: async () => { throw new Error('Denied'); }
        }, configurable: true})""")
        self.page.locator('.step:not([hidden]) details').evaluate_all("nodes => nodes.forEach(node => node.open = true)")
        self.page.locator('.step:not([hidden]) [data-copy-kind="code"]').first.click()
        self.page.wait_for_function("document.getElementById('copy-status').textContent.includes('Code selected')")
        self.assertEqual(self.page.evaluate('document.activeElement.value.slice(document.activeElement.selectionStart, document.activeElement.selectionEnd)'), self.page.locator('.step:not([hidden]) pre:not(.prompt-text) > code').first.text_content())

    def test_prompt_copy_exact_sources_and_denial(self):
        self.page.evaluate("""() => Object.defineProperty(navigator, 'clipboard', {value: {
          writeText: async text => { window.copiedText = text; }
        }, configurable: true})""")
        for module_id in MODULE_IDS:
            self.select_module(module_id)
            for card in self.page.locator('.step:not([hidden]) .prompt-card').all():
                self.assertTrue(card.is_visible())
                source = canonical_prompt(ROOT, ROOT / 'lab-guide.html', card.get_attribute('data-source'))
                card.get_by_role('button', name='Copy prompt', exact=True).click()
                self.assertEqual(self.page.evaluate('window.copiedText'), source['text'])
                self.assertEqual(self.page.locator('#copy-status').text_content(), 'Prompt copied.')
        self.select_module('06-build-reclamation')
        self.page.evaluate("""() => Object.defineProperty(navigator, 'clipboard', {value: {
          writeText: async () => { throw new Error('Denied'); }
        }, configurable: true})""")
        card = self.page.locator('.step:not([hidden]) .prompt-card').first
        card.get_by_role('button', name='Copy prompt', exact=True).click()
        self.page.wait_for_function("document.getElementById('copy-status').textContent.includes('Prompt selected')")
        self.assertEqual(self.page.evaluate('document.activeElement.value.slice(document.activeElement.selectionStart, document.activeElement.selectionEnd)'), card.locator('code').text_content())

    def test_disclosure_anchor_and_keyboard_focus(self):
        self.select_module('06-build-reclamation')
        self.assertTrue(self.page.locator('[id="06-build-reclamation--recovery"]').is_visible())
        disclosure = self.page.locator('.step:not([hidden]) details').first
        self.assertFalse(disclosure.evaluate('node => node.open'))
        disclosure.locator('summary').focus()
        self.page.keyboard.press('Enter')
        self.assertTrue(disclosure.evaluate('node => node.open'))
        self.page.goto((ROOT / 'lab-guide.html').as_uri() + '#06-build-reclamation--manual-commands')
        self.page.wait_for_function("document.getElementById('06-build-reclamation--manual-commands').closest('details').open")
        self.assertTrue(self.page.locator('[id="06-build-reclamation--manual-commands"]').is_visible())

    def test_themes_and_inline_assets(self):
        for expected in ['light', 'dark', 'system']:
            self.page.locator('#theme-toggle').click()
            self.assertEqual(self.page.locator('#theme-toggle').text_content(), 'Theme: ' + expected)
            self.assertEqual(self.page.evaluate('document.documentElement.style.colorScheme'), 'light dark' if expected == 'system' else expected)
        self.assertEqual(self.page.locator('iframe, script[src], link[rel="stylesheet"]').count(), 0)
        self.assertTrue(self.page.evaluate("[...document.images].every(image => image.src.startsWith('data:') && image.complete && image.naturalWidth > 0)"))


if __name__ == "__main__":
    unittest.main()