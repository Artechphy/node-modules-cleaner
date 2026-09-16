import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from node_modules_cleaner import CleanerConfig, SECONDS_PER_DAY, discover_node_modules, run_cleanup


class CleanerTests(unittest.TestCase):
    NOW = 2_000_000_000.0

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.temp_dir.name)
        self.root = self.base / "Documents"
        self.root.mkdir()
        self.reports = self.base / "reports"

    def tearDown(self):
        self.temp_dir.cleanup()

    def make_project(self, name: str, age_days: int, recent_dependency: bool = False) -> Path:
        project = self.root / name
        module = project / "node_modules" / "demo"
        module.mkdir(parents=True)
        package_json = project / "package.json"
        package_json.write_text('{"name":"demo"}\n', encoding="utf-8")
        dependency = module / "index.js"
        dependency.write_text("module.exports = true;\n", encoding="utf-8")
        old_time = self.NOW - (age_days * SECONDS_PER_DAY)
        dependency_time = self.NOW - SECONDS_PER_DAY if recent_dependency else old_time
        os.utime(dependency, (dependency_time, dependency_time))
        os.utime(package_json, (old_time, old_time))
        os.utime(module, (old_time, old_time))
        os.utime(module.parent, (old_time, old_time))
        os.utime(project, (old_time, old_time))
        return project

    def config(self, mode: str = "audit", exclusions=()):
        return CleanerConfig(self.root, 30, mode, tuple(exclusions), self.reports)

    def test_discovers_only_outer_real_node_modules(self):
        project = self.make_project("old", 40)
        nested = project / "node_modules" / "demo" / "node_modules"
        nested.mkdir()
        outside = self.base / "outside" / "node_modules"
        outside.mkdir(parents=True)
        (self.root / "linked").symlink_to(outside.parent, target_is_directory=True)

        found = discover_node_modules(self.root.resolve(), ())

        self.assertEqual(found, [(project / "node_modules").resolve()])

    def test_audit_reports_old_directory_without_deleting(self):
        project = self.make_project("old", 40)

        payload, report = run_cleanup(self.config("audit"), now=self.NOW)

        self.assertTrue((project / "node_modules").exists())
        self.assertEqual(payload["summary"]["would_delete"], 1)
        self.assertEqual(payload["results"][0]["status"], "eligible")
        self.assertTrue(report.exists())

    def test_apply_deletes_old_directory(self):
        project = self.make_project("old", 40)

        payload, _report = run_cleanup(self.config("apply"), now=self.NOW)

        self.assertFalse((project / "node_modules").exists())
        self.assertEqual(payload["summary"]["deleted"], 1)

    def test_recent_dependency_access_prevents_deletion(self):
        project = self.make_project("active", 40, recent_dependency=True)

        payload, _report = run_cleanup(self.config("apply"), now=self.NOW)

        self.assertTrue((project / "node_modules").exists())
        self.assertEqual(payload["results"][0]["status"], "recent")

    def test_recent_project_manifest_prevents_deletion(self):
        project = self.make_project("active-manifest", 40)
        recent = self.NOW - SECONDS_PER_DAY
        os.utime(project / "package.json", (recent, recent))

        payload, _report = run_cleanup(self.config("apply"), now=self.NOW)

        self.assertTrue((project / "node_modules").exists())
        self.assertEqual(payload["results"][0]["status"], "recent")

    def test_keep_marker_prevents_deletion(self):
        project = self.make_project("protected", 40)
        marker = project / ".node-modules-cleaner-keep"
        marker.touch()

        payload, _report = run_cleanup(self.config("apply"), now=self.NOW)

        self.assertTrue((project / "node_modules").exists())
        self.assertEqual(payload["results"][0]["status"], "kept")

    def test_exclusion_prevents_discovery(self):
        project = self.make_project("protected/project", 40)

        payload, _report = run_cleanup(self.config("apply", ("protected/**",)), now=self.NOW)

        self.assertTrue((project / "node_modules").exists())
        self.assertEqual(payload["summary"]["found"], 0)

    def test_refuses_home_or_filesystem_root(self):
        with self.assertRaises(ValueError):
            run_cleanup(CleanerConfig(Path.home(), report_dir=self.reports), now=self.NOW)
        with self.assertRaises(ValueError):
            run_cleanup(CleanerConfig(Path("/"), report_dir=self.reports), now=self.NOW)


if __name__ == "__main__":
    unittest.main()
