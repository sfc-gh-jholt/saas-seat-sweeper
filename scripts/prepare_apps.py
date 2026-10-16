#!/usr/bin/env python3
"""Derive starter and small completed-writeback overlay; never contact Snowflake.

Usage: python3 scripts/prepare_apps.py [--output-root PATH] [--check]
The output root receives starter-app/ and checkpoints/completed-writeback/.
Source: reference-app/ plus checkpoints/starter-overlay/. No independent app copy.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OMIT = {
    "README.md", "snowflake.yml", "app/api/ask/route.ts", "app/api/reclaim/route.ts",
    "components/ask-chat.tsx", "components/use-ask-chat.ts", "lib/reclaim.ts",
    "__tests__/api/reclaim.test.ts", "__tests__/components/reclaim.test.tsx",
}
WRITEBACK = (
    "app/api/reclaim/route.ts", "lib/reclaim.ts", "components/inactive-users-card.tsx",
    "__tests__/api/reclaim.test.ts", "__tests__/components/reclaim.test.tsx",
)
SKIP_DIRS = {"node_modules", ".next", ".git", ".snowflake", "coverage", "out", "output"}
ROOT_FILES = {"package.json", "package-lock.json", "tsconfig.json", "next-env.d.ts", "next.config.mjs", "postcss.config.mjs", "vitest.config.ts", "components.json", "app.yml", "icon.svg", ".gitignore"}
SOURCE_DIRS = {"app", "components", "lib", "public", "__tests__", "scripts"}


def source_files(root):
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = sorted(name for name in dirs if name not in SKIP_DIRS and not name.startswith("."))
        for name in dirs:
            if (Path(directory) / name).is_symlink():
                raise ValueError(f"Symlink directory is not packaged: {name}")
        for name in sorted(names):
            path = Path(directory) / name
            rel = path.relative_to(root)
            if name.startswith(".env") or path.suffix in {".pem", ".p8", ".key", ".log", ".tsbuildinfo"} or name == ".DS_Store":
                continue
            if rel.parts[0] in SOURCE_DIRS or rel.as_posix() in ROOT_FILES:
                if path.is_symlink():
                    raise ValueError(f"Symlink is not packaged: {rel}")
                yield rel.as_posix(), path.read_bytes()


def outputs():
    reference = dict(source_files(ROOT / "reference-app"))
    starter = {name: data for name, data in reference.items() if name not in OMIT}
    # Exact sentinel: fail closed if the reference secret configuration changes.
    secret = "\nsecrets:\n  - name: SEAT_SWEEPER_PAT\n    secret: SAAS_SEAT_SWEEPER.APP.SEAT_SWEEPER_PAT\n"
    manifest = starter["app.yml"].decode()
    if manifest.count(secret) != 1:
        raise ValueError("Reference app.yml secret block changed; review participant generation")
    starter["app.yml"] = manifest.replace(secret, "\n").encode()
    overlay_root = ROOT / "checkpoints/starter-overlay"
    for path in sorted(overlay_root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Overlay symlinks are forbidden")
        if path.is_file():
            starter[path.relative_to(overlay_root).as_posix()] = path.read_bytes()
    # Contextual copy, not a second maintained Overview implementation.
    replacements = {
        "The lab app keeps operational tables, governed views, semantic models, Cortex Search, the Cortex Agent, App Runtime, telemetry, and cost controls inside one Snowflake perimeter.":
        "This diagram shows the completed facilitator reference. Your starter reads governed views and contract terms; agent functionality is demonstrated separately.",
        "One app demonstrates governed reads, operational write-back, contract intelligence, and an AI route grounded in Snowflake data.":
        "Deploy governed reads first, add write-back next, and observe the separate facilitator AI demonstration.",
        "Prompts and lab instructions now track this same product shape so participants build toward the reference experience.":
        "This participant app needs no Ask credentials or agent objects.",
    }
    home = starter["app/page.tsx"].decode()
    for old, new in replacements.items():
        if home.count(old) != 1:
            raise ValueError("Overview copy changed; review starter overlay")
        home = home.replace(old, new)
    starter["app/page.tsx"] = home.encode()
    starter["next-env.d.ts"] = b'/// <reference types="next" />\n/// <reference types="next/image-types/global" />\n'
    completed = {f"files/{name}": reference[name] for name in WRITEBACK}
    completed["manifest.json"] = (json.dumps({
        "format": 1,
        "files": {name: hashlib.sha256(reference[name]).hexdigest() for name in WRITEBACK},
        "remove": ["__tests__/components/starter.test.tsx"],
    }, indent=2, sort_keys=True) + "\n").encode()
    return {"starter-app": starter, "checkpoints/completed-writeback": completed}


def sync(destination, files, check=False):
    # macOS /var is an OS symlink; canonicalize the parent, not the output itself.
    destination = destination.parent.resolve() / destination.name
    if destination.is_symlink():
        raise ValueError(f"Refusing symlink destination: {destination}")

    def safe_target(name):
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts or not relative.parts:
            raise ValueError(f"Invalid generated file path: {name}")
        target = destination / relative
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
            raise ValueError(f"Refusing symlink destination: {target}")
        return target

    marker = safe_target(".generated.json")
    previous = json.loads(marker.read_text()) if marker.exists() else {}
    differences = []

    def comparable_content(name, content):
        # Next rewrites this scaffold during build/dev. Accept only its known output,
        # not arbitrary edits, and keep packages independent of generated route types.
        if name == "next-env.d.ts":
            prefix = b'/// <reference types="next" />\n/// <reference types="next/image-types/global" />\n'
            footer = b'\n// NOTE: This file should not be edited\n// see https://nextjs.org/docs/app/api-reference/config/typescript for more information.\n'
            for route in (b'./.next/types/routes.d.ts', b'./.next/dev/types/routes.d.ts'):
                if content == prefix + b'import "' + route + b'";\n' + footer:
                    return prefix
        return content

    # Validate every change before writing anything, preserving hand edits on failure.
    for name, content in files.items():
        target = safe_target(name)
        if not target.exists() or comparable_content(name, target.read_bytes()) != content:
            differences.append(name)
            if not check and target.exists() and hashlib.sha256(comparable_content(name, target.read_bytes())).hexdigest() != previous.get(name):
                raise ValueError(f"Refusing to overwrite hand edits: {target}")
    removed = sorted(previous.keys() - files.keys())
    for name in removed:
        target = safe_target(name)
        if target.exists():
            differences.append(name)
            if not check and hashlib.sha256(target.read_bytes()).hexdigest() != previous[name]:
                raise ValueError(f"Refusing to delete hand edits: {target}")
    hashes = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(files.items())}
    if previous != hashes:
        differences.append(".generated.json")
    if not check:
        for name, content in files.items():
            target = safe_target(name)
            # Restore known build-generated scaffolding to its portable source form.
            if not target.exists() or target.read_bytes() != content:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
        for name in removed:
            safe_target(name).unlink(missing_ok=True)
        destination.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=ROOT)
    parser.add_argument("--check", action="store_true", help="Check byte-for-byte drift; do not write")
    args = parser.parse_args()
    results = outputs()
    changes = {}
    for name, files in results.items():
        destination = args.output_root.resolve() / name
        if name == "starter-app" and (destination / "snowflake.yml").exists():
            raise ValueError("Refusing to generate over a participant deployment target; use a clean --output-root")
        changes[name] = sync(destination, files, args.check)
    print(json.dumps({"mode": "check" if args.check else "generate", "changes": changes}, indent=2))
    if args.check and any(changes.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()