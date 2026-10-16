"""Deterministically build the portable guide from agenda.json and Markdown."""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit
from xml.etree import ElementTree as ET

import bleach
import html5lib
import markdown

ROOT = Path(__file__).resolve().parent.parent
MODULE_IDS = (
    "00-overview", "01-run-starter", "02-configure-deployment", "03-deploy-v1",
    "04-access", "05-break", "06-build-reclamation", "07-deploy-v2",
    "08-operate", "09-ask-demo", "10-scorecard", "11-cleanup", "12-honest-faq",
)
MINUTES = (10, 15, 15, 25, 15, 10, 25, 20, 15, 10, 10, 10, 0)
TAGS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "strong",
    "em", "a", "code", "pre", "blockquote", "hr", "br", "table", "thead",
    "tbody", "tr", "th", "td", "details", "summary", "img", "del",
}


def package_path(root: Path, base: Path, value: str) -> Path:
    path = (base / unquote(value)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path escapes package: {value}")
    return path


def load_agenda(root: Path) -> dict:
    agenda = json.loads((root / "agenda.json").read_text(encoding="utf-8"))
    if not isinstance(agenda, dict) or not isinstance(agenda.get("title"), str) or not agenda["title"].strip():
        raise ValueError("agenda.json requires a nonempty title")
    modules = agenda.get("modules")
    if not isinstance(modules, list) or not all(isinstance(item, dict) for item in modules):
        raise ValueError("agenda.json requires a modules array")
    if tuple(item.get("id") for item in modules) != MODULE_IDS:
        raise ValueError("Agenda module IDs/order do not match the approved deploy-first path")
    if tuple(item.get("minutes") for item in modules) != MINUTES or any(type(item.get("minutes")) is not int for item in modules):
        raise ValueError("Agenda durations must match the approved 180-minute schedule; FAQ is untimed")
    sources = set()
    for item in modules:
        if not isinstance(item.get("title"), str) or not item["title"].strip():
            raise ValueError(f"Missing title: {item['id']}")
        if not isinstance(item.get("file"), str):
            raise ValueError(f"Missing source file: {item['id']}")
        source = package_path(root, root, item["file"])
        if source.parent != (root / "lab-instructions").resolve() or source.suffix != ".md" or not source.is_file():
            raise ValueError(f"Missing canonical Markdown module: {item['file']}")
        if source in sources:
            raise ValueError(f"Duplicate module source: {item['file']}")
        sources.add(source)
    return agenda


def markdown_tree(text: str) -> ET.Element:
    rendered = markdown.markdown(text, extensions=["fenced_code", "tables", "sane_lists", "toc"])
    safe = bleach.clean(
        rendered, tags=TAGS,
        attributes={"a": ["href", "title"], "img": ["src", "alt", "title"],
                    "code": ["class"], "ol": ["start"],
                    **{f"h{level}": ["id"] for level in range(1, 7)}},
        protocols=["https", "http", "mailto", "tel"], strip=False,
    )
    return html5lib.parseFragment(safe, treebuilder="etree", namespaceHTMLElements=False)


def text_of(node: ET.Element) -> str:
    return "".join(node.itertext()).strip()


def serialize(tree: ET.Element) -> str:
    return html5lib.serialize(tree, tree="etree", quote_attr_values="always", omit_optional_tags=False,
                              alphabetical_attributes=True)


def image_data(root: Path, path: Path) -> str:
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"Missing local image: {path.name}")
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".gif": "image/gif", ".webp": "image/webp"}.get(path.suffix.lower())
    if not mime:
        raise ValueError(f"Only passive raster image assets are supported: {path.name}")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def canonical_prompt(root: Path, source: Path, href: str) -> dict:
    """Read exactly one top-level text fence, never resolve outside prompt sources."""
    link = urlsplit(href)
    if link.scheme or link.netloc or link.query or link.fragment or not link.path:
        raise ValueError(f"Prompt source must be a plain local Markdown path: {href}")
    path = package_path(root, source.parent, link.path)
    prompt_root = (root / "coco-prompts").resolve()
    if (not prompt_root.is_relative_to(root.resolve()) or not path.is_relative_to(prompt_root)
            or path.suffix != ".md" or not path.is_file()):
        raise ValueError(f"Prompt source must exist inside coco-prompts/: {href}")
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    if "\r" in text:
        raise ValueError(f"Prompt source must use LF line endings for exact copying: {href}")
    blocks, fence, language, lines = [], None, None, []
    for line in text.splitlines(keepends=True):
        marker = re.fullmatch(r"(`{3,}|~{3,})([^\n]*)\n?", line)
        if fence is None:
            if marker:
                fence, language, lines = marker[1], marker[2].strip(), []
        elif line.rstrip("\n").rstrip() == fence:
            blocks.append((language, "".join(lines)))
            fence = None
        else:
            lines.append(line)
    if fence or len(blocks) != 1 or blocks[0][0] != "text" or not blocks[0][1].strip():
        raise ValueError(f"Prompt source requires exactly one nonempty fenced text block: {href}")
    prompt = blocks[0][1]
    return {"type": "file", "path": path.relative_to(root.resolve()).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "promptSha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(), "text": prompt}


def embed_prompts(root: Path, source: Path, tree: ET.Element) -> list[dict]:
    records = []
    for parent in list(tree.iter()):
        for index, paragraph in enumerate(list(parent)):
            if paragraph.tag != "p" or len(paragraph) != 1:
                continue
            link = paragraph[0]
            label = text_of(link)
            if (link.tag != "a" or not label.startswith("Prompt CoCo:")
                    or (paragraph.text or "").strip() or (link.tail or "").strip()):
                continue
            record = canonical_prompt(root, source, link.get("href", ""))
            title = label.removeprefix("Prompt CoCo:").strip()
            if not title:
                raise ValueError("Prompt CoCo link needs a title")
            card = ET.Element("section", {"class": "prompt-card", "aria-label": label,
                "data-source": record["path"], "data-sha256": record["sha256"],
                "data-prompt-sha256": record["promptSha256"]})
            ET.SubElement(card, "p", {"class": "prompt-label"}).text = "Prompt CoCo"
            ET.SubElement(card, "h3", {"class": "prompt-title"}).text = title
            ET.SubElement(ET.SubElement(card, "pre", {"class": "prompt-text"}), "code").text = record["text"]
            provenance = ET.SubElement(card, "p", {"class": "prompt-source"})
            provenance.text = "Source: " + record["path"] + " | SHA-256 " + record["sha256"][:12]
            card.tail = paragraph.tail
            parent.remove(paragraph)
            parent.insert(index, card)
            records.append({key: value for key, value in record.items() if key != "text"})
    return records


def semantic_sections(tree: ET.Element) -> None:
    """Wrap trusted generated components after sanitization; preserve heading IDs."""
    panels = {"your decision": "decision", "expected evidence": "evidence",
              "verification checkpoint": "evidence", "recovery": "recovery"}
    collapsed = {"manual commands", "recovery commands", "why this matters", "if blocked"}
    nodes = list(tree)
    for node in nodes:
        tree.remove(node)
    stack = [(0, tree)]
    for node in nodes:
        heading = re.fullmatch(r"h([1-6])", str(node.tag))
        if heading:
            level = int(heading[1])
            while len(stack) > 1 and stack[-1][0] >= level:
                stack.pop()
            label = text_of(node).casefold()
            if label in panels or label in collapsed:
                parent = stack[-1][1]
                if label in collapsed:
                    wrapper = ET.SubElement(parent, "details", {"class": "command-disclosure"})
                    summary = ET.SubElement(wrapper, "summary")
                    summary.append(node)
                else:
                    wrapper = ET.SubElement(parent, "section", {"class": "semantic-panel panel-" + panels[label],
                        "aria-labelledby": node.get("id", "")})
                    wrapper.append(node)
                stack.append((level, wrapper))
                continue
        # A new prompt is a primary action, never buried inside the prior decision.
        if node.get("class") == "prompt-card":
            while len(stack) > 1 and stack[-1][1].get("class", "").startswith("semantic-panel"):
                stack.pop()
        stack[-1][1].append(node)


def render_module(root: Path, item: dict, module_files: dict[Path, str]) -> tuple[str, str, list[dict]]:
    source = package_path(root, root, item["file"])
    tree = markdown_tree(source.read_text(encoding="utf-8"))
    outcome_node = None
    for node in list(tree):
        if node.tag in {"h2", "h3"}:
            break
        if node.tag == "p":
            text = text_of(node)
            if re.match(r"(?:Duration|Time limit):", text, re.I):
                # Retain allocation and cutoff guidance, not the redundant duration/window.
                remainder = re.sub(r"^(?:Duration|Time limit):\s*(?:\d+\s*(?:minutes|min)\b(?:,?\s*\d{2}:\d{2}\s*[-–]\s*\d{2}:\d{2})?|Untimed(?: reference)?)[.\s]*", "", text, flags=re.I)
                tree.remove(node)
                if remainder:
                    note = ET.Element("p", {"class": "time-guidance"})
                    note.text = remainder
                    tree.insert(1, note)
            elif outcome_node is None:
                outcome_node = node
    # Agenda supplies the visible title. Keep the original Markdown H1 anchor for deep links.
    first_h1 = tree.find("h1")
    if first_h1 is not None:
        first_h1.tag = "span"
        first_h1.text = None
        for child in list(first_h1):
            first_h1.remove(child)
    prompt_sources = embed_prompts(root, source, tree)
    for node in tree.iter():
        if "id" in node.attrib:
            node.set("id", f"{item['id']}--{node.get('id')}")
        if node.tag == "a" and node.get("href"):
            link = urlsplit(node.get("href"))
            if link.scheme or link.netloc:
                continue
            target = package_path(root, source.parent, link.path) if link.path else source
            if target in module_files:
                anchor = module_files[target]
                node.set("href", f"#{anchor}--{unquote(link.fragment)}" if link.fragment else f"#{anchor}")
            else:
                if not target.exists():
                    raise ValueError(f"{item['file']}: broken package link: {node.get('href')}")
                node.set("href", quote(target.relative_to(root.resolve()).as_posix(), safe="/")
                         + (f"#{link.fragment}" if link.fragment else ""))
        if node.tag == "img":
            link = urlsplit(node.get("src", ""))
            if link.scheme or link.netloc or not link.path:
                raise ValueError(f"{item['file']}: image must be a local package asset")
            node.set("src", image_data(root, package_path(root, source.parent, link.path)))
    for parent in list(tree.iter()):
        for index, node in enumerate(list(parent)):
            if node.tag == "table":
                wrapper = ET.Element("div", {"class": "table-wrap", "tabindex": "0", "role": "region", "aria-label": "Scrollable table"})
                parent.remove(node)
                parent.insert(index, wrapper)
                wrapper.append(node)
    outcome = ""
    if outcome_node is not None and outcome_node in list(tree):
        outcome = serialize(outcome_node)
        tree.remove(outcome_node)
    semantic_sections(tree)
    return serialize(tree), outcome, prompt_sources


def clock(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def build(root: Path = ROOT) -> str:
    root = root.resolve()
    agenda = load_agenda(root)
    modules = agenda["modules"]
    files = {package_path(root, root, item["file"]): item["id"] for item in modules}
    introduction = {"id": "introduction", "file": "introduction.md"}
    files[package_path(root, root, introduction["file"])] = introduction["id"]
    intro_content, intro_outcome, _ = render_module(root, introduction, files)
    agenda_rows, elapsed = [], 0
    for item in modules:
        if not item["minutes"]:
            continue
        finish = elapsed + item["minutes"]
        agenda_rows.append(
            f'<li><span class="agenda-time">{clock(elapsed)} - {clock(finish)}</span>'
            f'<a href="#{item["id"]}">{html.escape(item["title"])}</a>'
            f'<span class="agenda-duration">{item["minutes"]} min</span></li>')
        elapsed = finish
    nav = ['<li><a class="nav-link" href="#introduction"><span class="nav-text">Introduction &amp; agenda</span></a></li>']
    sections = [
        '<section class="step introduction" id="introduction" aria-labelledby="title-introduction">'
        '<header class="step-header"><span class="step-tag">Start here / Hands-on lab</span>'
        '<h1 class="step-title" id="title-introduction" tabindex="-1">Build with CoCo:<br>SaaS Seat Sweeper</h1>'
        f'<div class="step-outcome">{intro_outcome}</div>'
        '<p class="interaction-pattern">3 hours / Two deployments / One meaningful feature</p>'
        '<p><a class="btn btn-primary" href="#00-overview">Start the lab</a> '
        '<a class="btn" href="#introduction--three-hour-agenda">View the agenda</a></p></header>'
        f'<div class="module-content">{intro_content}<ol class="agenda-list" aria-label="Three-hour lab agenda">'
        + ''.join(agenda_rows) + '</ol>'
        '<p><a href="#12-honest-faq">Honest FAQ</a> is untimed reference.</p></div>'
        '<nav class="step-nav" aria-label="Introduction controls"><a class="btn btn-primary" href="#00-overview">Start the lab</a></nav></section>'
    ]
    provenance = [{"id": "introduction", "title": "Introduction and agenda", "minutes": 0,
                   "dataSources": [{"type": "file", "path": "introduction.md",
                                    "sha256": hashlib.sha256((root / "introduction.md").read_bytes()).hexdigest()},
                                   {"type": "file", "path": "agenda.json"}]}]
    elapsed = 0
    for index, item in enumerate(modules):
        module_id, title, minutes = item["id"], html.escape(item["title"]), item["minutes"]
        timing = f"{clock(elapsed)} - {clock(elapsed + minutes)} | {minutes} minutes" if minutes else "Untimed reference"
        journey = {0: "Orient & inspect", 2: "Deploy & prove", 5: "Pause", 6: "Build & verify", 8: "Operate & reflect", 11: "Close & reference"}
        if index in journey:
            nav.append(f'<li class="journey-label">{journey[index]}</li>')
        nav.append(f'<li><a class="nav-link" href="#{module_id}"><span class="nav-num">{index:02d}</span>'
                   f'<span class="nav-text">{title}</span></a></li>')
        content, outcome, prompt_sources = render_module(root, item, files)
        controls = []
        if index:
            controls.append(f'<a class="btn" href="#{modules[index - 1]["id"]}">Previous</a>')
        else:
            controls.append('<a class="btn" href="#introduction">Introduction</a>')
        if minutes:
            controls.append(f'<button class="btn btn-primary complete" type="button" data-module="{module_id}" aria-pressed="false">Mark complete</button>')
        if index + 1 < len(modules):
            controls.append(f'<a class="btn" href="#{modules[index + 1]["id"]}">Next</a>')
        sections.append(f'<section class="step" id="{module_id}" data-minutes="{minutes}" aria-labelledby="title-{module_id}">'
                        f'<header class="step-header"><span class="step-tag">{"Module " + str(index).zfill(2) if minutes else "Reference"}</span>'
                        f'<h1 class="step-title" id="title-{module_id}" tabindex="-1">{title}</h1>'
                        f'<div class="step-outcome">{outcome}</div>'
                        f'<div class="step-duration">{timing}</div>'
                        f'<p class="interaction-pattern">{"Inspect / propose / approve / act / verify" if minutes and index != 5 else "Pause and return" if index == 5 else "Explore when needed"}</p></header>'
                        f'<div class="module-content">{content}</div>'
                        f'<nav class="step-nav" aria-label="Module controls">{"".join(controls)}</nav></section>')
        provenance.append({"id": module_id, "title": item["title"], "minutes": minutes,
                           "dataSources": [{"type": "file", "path": item["file"],
                                            "sha256": hashlib.sha256((root / item["file"]).read_bytes()).hexdigest()}, *prompt_sources]})
        elapsed += minutes
    metadata = {"intent": agenda["title"], "producerNotes": "Generated by scripts/build_guide.py; edit canonical Markdown and agenda.json, then regenerate. No build timestamp by design.",
                "dataSources": [{"type": "file", "path": "agenda.json"}, {"type": "file", "path": "scripts/guide-template.html"}],
                "sections": provenance}
    logo = ""
    for candidate in ("assets/snowflake-logo.png", "assets/logo.png", "reference-app/public/snowflake-logo.png", "reference-app/public/logo.png"):
        asset = package_path(root, root, candidate)
        if asset.is_file():
            logo = f'<img class="brand-logo" src="{image_data(root, asset)}" alt="Snowflake">'
            break
    values = {"TITLE": html.escape(agenda["title"]), "TOTAL": str(elapsed),
              "COUNT": str(sum(item["minutes"] > 0 for item in modules)), "LOGO": logo,
              "NAV": "\n".join(nav), "SECTIONS": "\n".join(sections),
              "METADATA": json.dumps(metadata, ensure_ascii=True, sort_keys=True, indent=2).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")}
    template = (root / "scripts" / "guide-template.html").read_text(encoding="utf-8")
    # One substitution pass: content that resembles a template token is never re-interpreted.
    return re.sub(r"@@([A-Z]+)@@", lambda match: values[match.group(1)], template)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Check exact regeneration parity without writing")
    args = parser.parse_args()
    try:
        result = build(args.root)
        destination = args.root / "lab-guide.html"
        if args.check:
            if not destination.exists() or destination.read_bytes() != result.encode("utf-8"):
                print("Guide is stale; run build_guide.py", file=__import__("sys").stderr)
                return 1
            print("Guide regeneration parity: PASS")
        else:
            destination.write_bytes(result.encode("utf-8"))
            print(f"Generated {destination.resolve()}")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"Guide generation failed: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())