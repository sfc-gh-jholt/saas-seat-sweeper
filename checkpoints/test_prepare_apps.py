#!/usr/bin/env python3
"""Offline generation/overlay contract tests; never executes SQL or deployment."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


generator = load("prepare_apps", ROOT / "scripts/prepare_apps.py")
installer = load("apply_writeback", ROOT / "checkpoints/apply_writeback.py")


class GenerationTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(generator.outputs(), generator.outputs())
        with tempfile.TemporaryDirectory() as temporary:
            for name, files in generator.outputs().items():
                target = Path(temporary) / name
                generator.sync(target, files)
                self.assertEqual(generator.sync(target, files, check=True), [])
                self.assertEqual(generator.sync(target, files), [])

    def test_participant_boundary(self):
        starter = generator.outputs()["starter-app"]
        self.assertNotIn("snowflake.yml", starter)
        self.assertNotIn("app/api/reclaim/route.ts", starter)
        self.assertNotIn("app/api/ask/route.ts", starter)
        self.assertNotIn("secrets:", starter["app.yml"].decode())
        self.assertNotIn("version:", starter["app.yml"].decode())
        self.assertIn("public/seat-sweeper-reference-architecture.png", starter)
        self.assertIn("scripts/copy-standalone.mjs", starter)
        self.assertIn("no agent endpoint", starter["app/ask/page.tsx"].decode())
        for name in starter:
            self.assertFalse(any(part in generator.SKIP_DIRS for part in Path(name).parts), name)
        # Only fixed-purpose GETs remain; no arbitrary query or mutation routes.
        for name, content in starter.items():
            if name.startswith("app/api/") and name.endswith("route.ts"):
                self.assertNotRegex(content.decode(), r"export async function (POST|PUT|PATCH|DELETE)")
                self.assertNotIn("request.json()", content.decode())

    def test_overlay_preserves_participant_config_and_ask(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = generator.outputs()
            for name, files in outputs.items():
                generator.sync(root / name, files)
            app = root / "starter-app"
            manifest = app / "snowflake.yml"
            manifest.write_text("participant configuration must not change\n")
            preserved = {name: (app / name).read_bytes() for name in ["snowflake.yml", "app.yml", "app/ask/page.tsx", "package-lock.json"]}
            installer.apply(app, root / "checkpoints/completed-writeback", dry_run=True)
            self.assertFalse((app / "app/api/reclaim/route.ts").exists())
            installer.apply(app, root / "checkpoints/completed-writeback")
            for name, content in preserved.items():
                self.assertEqual((app / name).read_bytes(), content)
            self.assertTrue((app / "app/api/reclaim/route.ts").is_file())
            self.assertFalse((app / "app/api/ask/route.ts").exists())
            self.assertFalse((app / "__tests__/components/starter.test.tsx").exists())

    def test_next_generated_types_do_not_create_false_drift(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            prefix = b'/// <reference types="next" />\n/// <reference types="next/image-types/global" />\n'
            generator.sync(root, {"next-env.d.ts": prefix})
            for route in ["./.next/types/routes.d.ts", "./.next/dev/types/routes.d.ts"]:
                (root / "next-env.d.ts").write_bytes(prefix + f'import "{route}";\n\n// NOTE: This file should not be edited\n// see https://nextjs.org/docs/app/api-reference/config/typescript for more information.\n'.encode())
                self.assertEqual(generator.sync(root, {"next-env.d.ts": prefix}, check=True), [])
                self.assertEqual(generator.sync(root, {"next-env.d.ts": prefix}), [])
                self.assertEqual((root / "next-env.d.ts").read_bytes(), prefix)
            (root / "next-env.d.ts").write_bytes(prefix + b"// participant edit\n")
            with self.assertRaises(ValueError):
                generator.sync(root, {"next-env.d.ts": prefix})

    def test_check_reports_drift_without_changing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generator.sync(root, {"test.txt": b"original"})
            marker = (root / ".generated.json").read_bytes()
            self.assertIn("test.txt", generator.sync(root, {"test.txt": b"changed"}, check=True))
            self.assertEqual((root / "test.txt").read_bytes(), b"original")
            self.assertEqual((root / ".generated.json").read_bytes(), marker)

    def test_refusal_does_not_partially_overwrite_other_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generator.sync(root, {"first.txt": b"first", "last.txt": b"last"})
            (root / "last.txt").write_bytes(b"hand edit")
            with self.assertRaises(ValueError):
                generator.sync(root, {"first.txt": b"new first", "last.txt": b"new last"})
            self.assertEqual((root / "first.txt").read_bytes(), b"first")
            self.assertEqual((root / "last.txt").read_bytes(), b"hand edit")

    def test_removed_files_and_unsafe_inventory_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "output"
            generator.sync(root, {"old.txt": b"original"})
            generator.sync(root, {})
            self.assertFalse((root / "old.txt").exists())
            outside = root.parent / "outside.txt"
            outside.write_bytes(b"preserve")
            (root / ".generated.json").write_text(json.dumps({"../outside.txt": "invalid"}))
            with self.assertRaises(ValueError):
                generator.sync(root, {})
            self.assertEqual(outside.read_bytes(), b"preserve")
            for name in ["../escape.txt", str(outside)]:
                with self.assertRaises(ValueError):
                    generator.sync(root, {name: b"bad"})

    def test_generator_rejects_symlink_outputs_and_marker(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root / "outside"
            outside.mkdir()
            destination = root / "output"
            destination.symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                generator.sync(destination, {"test.txt": b"bad"})
            destination.unlink()
            destination.mkdir()
            (destination / "nested").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                generator.sync(destination, {"nested/test.txt": b"bad"})
            marker = outside / "marker.json"
            marker.write_text("{}")
            (destination / ".generated.json").symlink_to(marker)
            with self.assertRaises(ValueError):
                generator.sync(destination, {"test.txt": b"bad"})
            self.assertEqual(marker.read_text(), "{}")

    def test_overlay_rejects_symlink_destinations_before_writing(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, files in generator.outputs().items():
                generator.sync(root / name, files)
            app = root / "starter-app"
            before = (app / "components/inactive-users-card.tsx").read_bytes()
            outside = root / "outside.ts"
            outside.write_bytes(b"preserve")
            (app / "lib/reclaim.ts").symlink_to(outside)
            with self.assertRaises(ValueError):
                installer.apply(app, root / "checkpoints/completed-writeback")
            self.assertEqual(outside.read_bytes(), b"preserve")
            self.assertEqual((app / "components/inactive-users-card.tsx").read_bytes(), before)
            self.assertFalse((app / "app/api/reclaim/route.ts").exists())

    def test_overlay_rejects_unexpected_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, files in generator.outputs().items():
                generator.sync(root / name, files)
            checkpoint = root / "checkpoints/completed-writeback"
            manifest = json.loads((checkpoint / "manifest.json").read_text())
            manifest["files"]["snowflake.yml"] = "bad"
            (checkpoint / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                installer.apply(root / "starter-app", checkpoint)
            self.assertFalse((root / "starter-app/app/api/reclaim/route.ts").exists())

    def test_hand_edits_and_bad_hashes_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generator.sync(root, {"test.txt": b"original"})
            (root / "test.txt").write_bytes(b"participant edit")
            with self.assertRaises(ValueError):
                generator.sync(root, {"test.txt": b"new reference"})
            outputs = generator.outputs()
            generator.sync(root / "starter-app", outputs["starter-app"])
            checkpoint = root / "checkpoint"
            generator.sync(checkpoint, outputs["checkpoints/completed-writeback"])
            (checkpoint / "files/lib/reclaim.ts").write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                installer.apply(root / "starter-app", checkpoint)


def build_recovery():
    """Exercise an isolated generated participant app, not the facilitator app."""
    with tempfile.TemporaryDirectory(prefix="seat-sweeper-recovery-") as temporary:
        root = Path(temporary).resolve()
        subprocess.run([sys.executable, str(ROOT / "scripts/prepare_apps.py"), "--output-root", str(root)], check=True)
        app = root / "starter-app"
        checkpoint = root / "checkpoints/completed-writeback"
        preserved_names = ["app.yml", "package-lock.json", "app/ask/page.tsx"]
        (app / "snowflake.yml").write_text("# Offline participant target sentinel; never deployed.\n")
        preserved_names.append("snowflake.yml")
        preserved = {name: (app / name).read_bytes() for name in preserved_names}
        installer.apply(app, checkpoint, dry_run=True)
        if (app / "app/api/reclaim/route.ts").exists():
            raise AssertionError("Dry run installed a write endpoint")
        installer.apply(app, checkpoint)
        installer.apply(app, checkpoint)  # Recovery can be repeated safely.
        for name, content in preserved.items():
            if (app / name).read_bytes() != content:
                raise AssertionError(f"Recovery changed protected file: {name}")
        if (app / "app/api/ask/route.ts").exists() or "secrets:" in (app / "app.yml").read_text():
            raise AssertionError("Recovery unexpectedly enables Ask credentials")
        # Do not inherit credentials or the active Desktop connection. Tests mock DB I/O.
        environment = {key: value for key, value in os.environ.items() if not key.startswith(("SNOWFLAKE_", "SNOWSQL_", "SEAT_SWEEPER_"))}
        environment.update({"SNOWFLAKE_HOME": str(root / "no-credentials"), "NEXT_TELEMETRY_DISABLED": "1"})
        for command in [["npm", "ci", "--include=dev"], ["npm", "test"], ["npm", "run", "typecheck"], ["npm", "run", "build"]]:
            print(f"Recovery command ({app}): {' '.join(command)}", flush=True)
            subprocess.run(command, cwd=app, env=environment, check=True)
        routes = json.loads((app / ".next/server/app-paths-manifest.json").read_text())
        for route in ["/page", "/licenses/page", "/inventory/page", "/ask/page", "/api/reclaim/route"]:
            if route not in routes:
                raise AssertionError(f"Missing built route: {route}")
        if "/api/ask/route" in routes:
            raise AssertionError("Built recovery app unexpectedly includes Ask endpoint")
        standalone = app / ".next/standalone"
        for name in ["server.js", "public/icon.svg", "public/seat-sweeper-reference-architecture.png"]:
            if not (standalone / name).is_file():
                raise AssertionError(f"Missing standalone asset: {name}")
        if not any((standalone / ".next/static").rglob("*.js")):
            raise AssertionError("Missing standalone JavaScript assets")
        print("Recovery build passed: protected config preserved, no Ask/PAT, five routes and standalone assets verified", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-recovery", action="store_true", help="Also clean-install, test, typecheck, and build the generated completed overlay in a temporary app")
    args, remaining = parser.parse_known_args()
    result = unittest.main(argv=[sys.argv[0], *remaining], exit=False).result
    if not result.wasSuccessful():
        raise SystemExit(1)
    if args.build_recovery:
        build_recovery()