"""Read-only prepublication check for the complete proposed Git file set.

Does not stage, commit, install hooks, publish, or contact a remote.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess

from package_workshop import ROOT, collect, validate

# Public source must not depend on employee-only collaboration sites or repos.
INTERNAL_LINK = re.compile(
    r'https?://(?:[^/\s]*snowflake\.slack\.com|[^/\s]*snowflake\.atlassian\.net'
    r'|github\.com/snowflake-corp|app\.dataops\.live/snowflake)/', re.I
)


def check(root: Path = ROOT) -> list[str]:
    expected = collect(root)
    validate(expected)
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True, capture_output=True,
    )
    candidates = {name.decode("utf-8") for name in result.stdout.split(b"\0") if name}
    extra = sorted(candidates - expected.keys())
    missing = sorted(expected.keys() - candidates)
    if extra or missing:
        raise ValueError(f"Git/package mismatch; unexpected paths: {extra}; ignored required paths: {missing}")
    for name, data in expected.items():
        if Path(name).suffix == ".png":
            continue
        if INTERNAL_LINK.search(data.decode("utf-8")):
            raise ValueError(f"Internal-only URL in {name}; review before publishing")
    # Check the index as well: an old staged version could contain removed secrets.
    staged = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        check=True, capture_output=True,
    )
    for entry in staged.stdout.split(b"\0"):
        if not entry:
            continue
        metadata, raw_name = entry.split(b"\t", 1)
        mode, object_id, stage = metadata.decode().split()
        name = raw_name.decode("utf-8")
        if mode not in {"100644", "100755"} or stage != "0":
            raise ValueError(f"Unsupported index entry: {name}")
        blob = subprocess.run(
            ["git", "-C", str(root), "cat-file", "blob", object_id],
            check=True, capture_output=True,
        ).stdout
        validate({name: blob})
        if Path(name).suffix != ".png" and INTERNAL_LINK.search(blob.decode("utf-8")):
            raise ValueError(f"Internal-only URL in staged {name}")
    return sorted(candidates)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List reviewed candidate paths")
    args = parser.parse_args()
    try:
        paths = check()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Repository check failed: {error}\n")
    print(f"Repository preflight passed: {len(paths)} candidate files; no commit or upload performed.")
    if args.list:
        print("\n".join(paths))
