"""Build a deterministic, allowlisted local workshop archive; never upload it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = (
    ".gitignore", "README.md", "introduction.md", "dataset-guide.md", "lab-guide.html", "agenda.json", "scorecard.md",
    "admin-preflight.md", "facilitator-guide.md", "deployment-checkpoint.md",
    "teardown-guide.md", "release-checklist.md",
    "validation-results.md", "rehearsal-record.md",
)
DIRECTORIES = ("lab-instructions", "coco-prompts", "sql", "starter-app", "reference-app", "checkpoints", "scripts")
EXCLUDED_PARTS = {"node_modules", ".next", ".git", ".venv", "__pycache__", "dist", ".pytest_cache", ".snowflake", ".cortex", "coverage", "out", "output"}
EXTENSIONS = {".md", ".json", ".ts", ".tsx", ".js", ".mjs", ".css", ".yml", ".yaml", ".sql", ".svg", ".png", ".py", ".toml", ".lock", ".html"}
PRIVATE = re.compile(r"/Users/|/home/[\w.-]+/|JGH-DEMO|DEMOJHOLTAWSW|NHB17718|fne4qtbp|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|snowflakecomputing\.app", re.I)
TOKEN = re.compile(r"eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}")


def excluded(relative: Path) -> bool:
    return (bool(set(relative.parts) & EXCLUDED_PARTS)
            or relative.name.startswith(".env")
            or relative.suffix in {".env", ".pem", ".p8", ".key", ".p12", ".pfx", ".log", ".zip", ".bak", ".orig", ".swp"}
            or relative.name in {"snowflake.yml", "connections.toml", "config.toml", "credentials.json", "snowflake.log"}
            or relative.name.endswith(".tsbuildinfo")
            or (relative.suffix not in EXTENSIONS and relative.name not in {".gitignore", ".python-version"}))


def collect(root: Path = ROOT) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for name in DOCUMENTS:
        path = root / name
        if not path.is_file():
            raise ValueError(f"Required release file missing: {name}")
        files[name] = path.read_bytes()
    for name in DIRECTORIES:
        directory = root / name
        if not directory.is_dir():
            raise ValueError(f"Required release directory missing: {name}")
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(root)
            if excluded(relative):
                continue
            if path.is_symlink():
                raise ValueError(f"Symlink not allowed in release: {relative}")
            if path.is_file():
                files[relative.as_posix()] = path.read_bytes()
    return files


def validate(files: dict[str, bytes]) -> None:
    for name, data in files.items():
        if Path(name).suffix == ".png":
            continue
        text = data.decode("utf-8")
        # The scanner itself necessarily contains the patterns it rejects.
        if name == "scripts/package_workshop.py":
            continue
        if PRIVATE.search(text) or TOKEN.search(text):
            raise ValueError(f"Private identifier, endpoint, path, or credential pattern in {name}; review before packaging")
    if "starter-app/app/api/reclaim/route.ts" in files:
        raise ValueError("Starter contains a live reclamation endpoint")
    if "starter-app/app/api/ask/route.ts" in files:
        raise ValueError("Starter contains an active agent endpoint")


def package(root: Path = ROOT, check_only: bool = False) -> Path:
    files = collect(root)
    validate(files)
    destination = root / "dist" / "seat-sweeper-deploy-first.zip"
    if check_only:
        print(f"Package preflight passed: {len(files)} files")
        return destination
    manifest = {
        "format": 1,
        "release_status": "See release-checklist.md and validation-results.md; not a claim of live rehearsal",
        "files": {name: hashlib.sha256(data).hexdigest() for name, data in sorted(files.items())},
    }
    files["package-manifest.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    destination.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo("seat-sweeper/" + name, date_time=(2026, 10, 15, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive CRC verification failed")
        for name, data in files.items():
            if archive.read("seat-sweeper/" + name) != data:
                raise ValueError(f"Archive content mismatch: {name}")
    print(f"Created and verified {destination} ({len(files)} files)")
    print(f"SHA-256: {hashlib.sha256(destination.read_bytes()).hexdigest()}")
    return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate inputs without writing an archive")
    args = parser.parse_args()
    package(check_only=args.check)