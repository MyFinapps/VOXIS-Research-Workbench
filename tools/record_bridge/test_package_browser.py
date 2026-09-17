"""Packaging provenance checks in disposable Git repositories."""
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import package_browser


class PackageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "user.name", "Synthetic Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.source = self.root / "nested"
        self.source.mkdir()
        (self.source / "sample.txt").write_bytes(b"preserved\r\nbytes\n")
        self.git("add", ".")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "synthetic fixture")
        self.commit = self.git("rev-parse", "HEAD").decode().strip()
        patcher = patch.object(package_browser, "FILES", ["sample.txt"])
        patcher.start()
        self.addCleanup(patcher.stop)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE)

    def test_resolves_identity_and_preserves_committed_bytes(self):
        commit, contents = package_browser.checked_contents(self.source, self.commit[:12])
        self.assertEqual(commit, self.commit)
        self.assertEqual(contents, {"sample.txt": b"preserved\r\nbytes\n"})

    def test_dirty_file_and_wrong_commit_are_rejected(self):
        (self.source / "sample.txt").write_bytes(b"different")
        with self.assertRaisesRegex(ValueError, "differs"):
            package_browser.checked_contents(self.source, self.commit)
        self.git("add", ".")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "changed fixture")
        with self.assertRaisesRegex(ValueError, "differs"):
            package_browser.checked_contents(self.source, self.commit)

    def test_unknown_reference_is_rejected(self):
        with self.assertRaises(subprocess.CalledProcessError):
            package_browser.checked_contents(self.source, "not-a-commit")
