"""Synthetic Git fixtures for the public repository boundary; no network."""
from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import unittest

import check_repository
import package_workshop


class RepositorySafetyTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        for name in package_workshop.DOCUMENTS:
            if name.endswith('.ipynb'):
                (self.root / name).write_bytes((package_workshop.ROOT / name).read_bytes())
            else:
                (self.root / name).write_text("Fixture\n")
        for name in package_workshop.DIRECTORIES:
            (self.root / name).mkdir()
            (self.root / name / "source.md").write_text("Fixture\n")
        shutil.copyfile(package_workshop.ROOT / ".gitignore", self.root / ".gitignore")
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.root), *arguments], check=True, capture_output=True)

    def test_portable_sources_match_and_private_files_are_ignored(self):
        for name in ("starter-app/.env.local", "reference-app/snowflake.yml", "sql/test.pem",
                     "scripts/config.toml", "private-notes.md", "starter-app/credentials.json"):
            (self.root / name).write_text("synthetic private fixture\n")
            self.git("check-ignore", name)
        paths = check_repository.check(self.root)
        self.assertIn("starter-app/source.md", paths)
        self.assertIn(".gitignore", paths)

    def test_force_added_private_file_is_rejected(self):
        (self.root / "starter-app/.env.local").write_text("synthetic fixture\n")
        self.git("add", "--force", "starter-app/.env.local")
        with self.assertRaisesRegex(ValueError, "Git/package mismatch"):
            check_repository.check(self.root)

    def test_old_staged_secret_is_rejected_after_worktree_cleanup(self):
        path = self.root / "starter-app/source.md"
        path.write_text("-----BEGIN " + "PRIVATE KEY-----\n")
        self.git("add", "starter-app/source.md")
        path.write_text("Now clean\n")
        with self.assertRaisesRegex(ValueError, "credential pattern"):
            check_repository.check(self.root)

    def test_staged_notebook_output_rejected_after_worktree_cleanup(self):
        path = self.root / 'START_HERE.ipynb'
        clean = path.read_bytes()
        notebook = json.loads(clean)
        cell = next(cell for cell in notebook['cells'] if cell['cell_type'] == 'code')
        cell['execution_count'] = 1
        path.write_text(json.dumps(notebook))
        self.git('add', 'START_HERE.ipynb')
        path.write_bytes(clean)
        with self.assertRaisesRegex(ValueError, 'Clear notebook outputs'):
            check_repository.check(self.root)

    def test_internal_url_is_rejected(self):
        (self.root / "starter-app/source.md").write_text("https://github.com/" + "snowflake-corp/private")
        with self.assertRaisesRegex(ValueError, "Internal-only URL"):
            check_repository.check(self.root)


if __name__ == "__main__":
    unittest.main()
