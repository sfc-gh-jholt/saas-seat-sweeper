#!/usr/bin/env python3
"""Apply only the generated writeback files. Review with --dry-run first."""
import argparse
import hashlib
import json
from pathlib import Path


def apply(target, checkpoint, dry_run=False):
    target = target.resolve()
    if not (target / "package.json").is_file():
        raise ValueError("Target must be an existing participant app")
    manifest = json.loads((checkpoint / "manifest.json").read_text())
    allowed = {
        "app/api/reclaim/route.ts", "lib/reclaim.ts", "components/inactive-users-card.tsx",
        "__tests__/api/reclaim.test.ts", "__tests__/components/reclaim.test.tsx",
    }
    if manifest.get("format") != 1 or set(manifest["files"]) != allowed or manifest.get("remove") != ["__tests__/components/starter.test.tsx"]:
        raise ValueError("Unexpected overlay manifest")
    contents = {}
    for name, digest in manifest["files"].items():
        source = checkpoint / "files" / name
        contents[name] = source.read_bytes()
        if hashlib.sha256(contents[name]).hexdigest() != digest:
            raise ValueError(f"Overlay checksum mismatch: {name}")
    for name in [*contents, *manifest["remove"]]:
        destination = target / name
        if not destination.resolve().is_relative_to(target) or destination.is_symlink() or any(parent.is_symlink() for parent in destination.parents):
            raise ValueError(f"Unsafe destination: {destination}")
    for name, content in contents.items():
        print(f"{'Would replace' if dry_run else 'Replace'} {name}")
        if not dry_run:
            destination = target / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(content)
    for name in manifest["remove"]:
        print(f"{'Would remove' if dry_run else 'Remove'} {name}")
        if not dry_run:
            (target / name).unlink(missing_ok=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    apply(args.target, Path(__file__).resolve().parent / "completed-writeback", args.dry_run)