"""Packaging safety checks; all fixtures are local synthetic data."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location("package_workshop", Path(__file__).with_name("package_workshop.py"))
package_workshop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package_workshop)


class PackageSafetyTests(unittest.TestCase):
    def test_credentials_and_build_output_are_excluded(self):
        for path in ("starter-app/.env.local", "starter-app/node_modules/a.js",
                     "reference-app/snowflake.yml", "scripts/.venv/a.py",
                     "starter-app/connections.toml", "starter-app/cache.tsbuildinfo"):
            self.assertTrue(package_workshop.excluded(Path(path)), path)

    def test_source_and_lockfile_are_kept(self):
        for path in ("starter-app/package-lock.json", "starter-app/app/page.tsx", "lab-instructions/00-overview.md"):
            self.assertFalse(package_workshop.excluded(Path(path)), path)

    def test_active_starter_write_endpoint_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "reclamation"):
            package_workshop.validate({"starter-app/app/api/reclaim/route.ts": b"export const POST = null"})

    def test_private_key_is_rejected(self):
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        with self.assertRaisesRegex(ValueError, "credential pattern"):
            package_workshop.validate({"notes.md": marker.encode()})

    def test_archive_is_deterministic_and_has_no_environments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in package_workshop.DOCUMENTS:
                (root / name).write_text("Fixture\n")
            for name in package_workshop.DIRECTORIES:
                (root / name).mkdir()
                (root / name / "source.md").write_text("Synthetic content\n")
            (root / "starter-app" / ".env.local").write_text("DO_NOT_PACKAGE=value")
            archive_path = package_workshop.package(root)
            first = archive_path.read_bytes()
            package_workshop.package(root)
            self.assertEqual(first, archive_path.read_bytes())
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()
                self.assertIn("seat-sweeper/package-manifest.json", names)
                self.assertFalse(any(".env" in name for name in names))


if __name__ == "__main__":
    unittest.main()