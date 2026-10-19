"""Synthetic evidence checks; these tests do not establish animation quality."""

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw

SCRIPT = Path(__file__).resolve().parents[1] / "skills/amea/scripts/amea_project.py"
TEST_TEMP = Path(__file__).resolve().parent / ".work"
TEST_TEMP.mkdir(exist_ok=True)
sys.path.insert(0, str(SCRIPT.parent))
import amea_project as amea


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="amea-test-", dir=TEST_TEMP)
        self.base = Path(self.temp.name)
        self.assertTrue(self.base.resolve().is_relative_to(TEST_TEMP.resolve()))
        self.root = self.base / "project"
        self.brief = self.base / "brief.txt"
        self.brief.write_text("Synthetic animation fixture.", encoding="utf-8")
        amea.init_project(self.root, "create", self.brief, width=64, height=48, fps="24")

    def tearDown(self):
        self.temp.cleanup()

    def fixture(self):
        root, data = amea.load_project(self.root)
        folder = root / "shots/s1"
        folder.mkdir()
        drawings = []
        for index, x in enumerate((4, 18, 32)):
            path = folder / f"r{index}.png"
            image = Image.new("RGBA", (64, 48), (0, 0, 0, 0))
            ImageDraw.Draw(image).rectangle((x, 10, x + 12, 30), fill="black")
            image.save(path)
            drawings.append({"id": f"d{index}", "role": "inbetween" if index == 1 else "key",
                             "origin": "canvas", "motion_note": f"Fixture state {index}",
                             "rough": path.relative_to(root).as_posix(),
                             "final": path.relative_to(root).as_posix()})
        # A minimal container fixture tests recognition only; it is not genuine editable Krita art.
        kra = folder / "fixture.kra"
        with zipfile.ZipFile(kra, "w") as archive:
            archive.writestr("mimetype", "application/x-krita")
            archive.writestr("maindoc.xml", "<DOC/>")
        data["design_files"] = ["brief.txt"]
        shot = {"id": "s1", "start_frame": 0, "frame_count": 6,
                "intent": "Synthetic integrity fixture", "motion_note": "Three different raster states",
                "motion": "drawn", "change_ids": [],
                "inbetween_policy": {"decision": "required", "reason": "Fixture has a middle state"},
                "drawings": drawings,
                "exposures": [{"start": index * 2, "end": index * 2 + 2, "drawing_id": f"d{index}"}
                              for index in range(3)],
                "krita": {"rough": "shots/s1/fixture.kra", "final": "shots/s1/fixture.kra"},
                "pencil_test": None}
        data["shots"] = [shot]
        data["audio"] = {"decision": "silent", "reason": "Synthetic timing fixture", "assets": []}
        amea.write_json(root / "project.json", data)
        return root, data, shot

    def review(self, data, shot, stage):
        fingerprint = amea.stage_fingerprint(self.root, data, shot, stage)
        amea.write_json(self.root / "shots/s1/reviews" / f"{stage}.json",
                        {"status": "pass", "fingerprint": fingerprint,
                         "observations": ["Synthetic review fixture only"], "issues": []})

    def test_creation_requires_no_video(self):
        root, data = amea.load_project(self.root)
        self.assertEqual(data["source_assets"], [])
        self.assertEqual(data["mode"], "create")
        report = amea.validate_project(root, require_complete=True)
        self.assertFalse(report["structural_passed"])
        self.assertFalse(report["recorded_reviews_current"])

    def test_source_modes_require_and_preserve_input(self):
        target = self.base / "edit"
        with self.assertRaises(amea.ProjectError):
            amea.init_project(target, "edit", self.brief)
        self.assertFalse(target.exists())
        source = self.base / "source.bin"
        source.write_bytes(b"source identity")
        amea.init_project(target, "edit", self.brief, [source])
        _, data = amea.load_project(target)
        copied = target / data["source_assets"][0]["path"]
        self.assertEqual(copied.read_bytes(), source.read_bytes())
        copied.write_bytes(b"changed evidence")
        report = amea.validate_project(target, stage="rough")
        self.assertFalse(report["structural_passed"])
        self.assertIn("Source integrity", " ".join(report["errors"]))

    def test_no_overwrite_or_external_paths(self):
        with self.assertRaises(amea.ProjectError):
            amea.init_project(self.root, "create", self.brief)
        with self.assertRaises(amea.ProjectError):
            amea.local_file(self.root, "../brief.txt")
        with self.assertRaises(amea.ProjectError):
            amea.local_file(self.root, str(self.brief.resolve()))
        with self.assertRaises(amea.ProjectError):
            amea.safe_id("../outside")
        with self.assertRaises(amea.ProjectError):
            amea.local_output(self.root, "../outside")

    def test_missing_inbetween_and_timing_gap_fail(self):
        root, data, shot = self.fixture()
        shot["exposures"][1]["start"] = 3
        amea.write_json(root / "project.json", data)
        report = amea.validate_project(root, stage="rough")
        self.assertFalse(report["structural_passed"])
        shot["exposures"][1]["start"] = 2
        shot["drawings"][1]["role"] = "key"
        amea.write_json(root / "project.json", data)
        report = amea.validate_project(root, stage="rough")
        self.assertIn("inbetweens", " ".join(report["errors"]))

    def test_repeated_identical_rasters_do_not_establish_drawn_motion(self):
        root, data, shot = self.fixture()
        for drawing in shot["drawings"][1:]:
            shutil.copyfile(root / shot["drawings"][0]["rough"], root / drawing["rough"])
        report = amea.validate_project(root, stage="rough")
        self.assertIn("distinct drawings", " ".join(report["errors"]))

    def test_prepare_parallel_references_do_not_create_reviews(self):
        root, data, shot = self.fixture()
        result = amea.prepare_references(root, "s1", "rough", workers=2)
        destination = Path(result["prepared"])
        self.assertEqual(len(list(destination.glob("onion-*.png"))), 3)
        self.assertTrue((destination / "contact-000.png").is_file())
        self.assertTrue((destination / "exposures.csv").is_file())
        self.assertFalse((root / "shots/s1/reviews/rough.json").exists())
        self.assertEqual(result["drawings_created"], 0)
        self.assertEqual(result["workers"], 2)

    def test_reused_drawing_gets_occurrence_specific_onions(self):
        root, data, shot = self.fixture()
        shot["frame_count"] = 8
        shot["exposures"].append({"start": 6, "end": 8, "drawing_id": "d0"})
        amea.write_json(root / "project.json", data)
        result = amea.prepare_references(root, "s1", workers=1)
        onions = sorted(Path(result["prepared"]).glob("onion-*.png"))
        self.assertEqual(len(onions), 4)
        self.assertNotEqual(amea.sha256(onions[0]), amea.sha256(onions[-1]))

    def test_reviews_bind_native_art_and_timing(self):
        if not all(amea.discover_executable(name) for name in ("ffmpeg", "ffprobe")):
            self.skipTest("FFmpeg/FFprobe unavailable")
        root, _, _ = self.fixture()
        amea.pencil_test(root, "s1")
        root, data = amea.load_project(root)
        shot = data["shots"][0]
        self.review(data, shot, "rough")
        report = amea.validate_project(root, stage="rough", require_complete=True)
        self.assertTrue(report["structural_passed"], report)
        with (root / shot["krita"]["rough"]).open("ab") as stream:
            stream.write(b"updated native artifact")
        report = amea.validate_project(root, stage="rough", require_complete=True)
        self.assertFalse(report["recorded_reviews_current"])

    def test_adding_final_art_does_not_stale_rough_review(self):
        root, data, shot = self.fixture()
        before = amea.stage_fingerprint(root, data, shot, "rough")
        shot["drawings"][0]["final"] = "unregistered-final-file.png"
        shot["krita"]["final"] = "unregistered-final.kra"
        after = amea.stage_fingerprint(root, data, shot, "rough")
        self.assertEqual(before, after)

    def test_pencil_test_count_and_no_automatic_review(self):
        if not all(amea.discover_executable(name) for name in ("ffmpeg", "ffprobe")):
            self.skipTest("FFmpeg/FFprobe unavailable")
        root, data, shot = self.fixture()
        result = amea.pencil_test(root, "s1")
        info, stream = amea.probe_video(result["pencil_test"])
        self.assertEqual(int(stream["nb_read_frames"]), 6)
        self.assertFalse(any(item["codec_type"] == "audio" for item in info["streams"]))
        report = amea.validate_project(root, stage="rough", require_complete=True)
        self.assertFalse(report["recorded_reviews_current"])
        root, data = amea.load_project(root)
        self.review(data, data["shots"][0], "rough")
        report = amea.validate_project(root, stage="rough", require_complete=True)
        self.assertTrue(report["structural_passed"], report)

    def test_final_integrity_and_downstream_change_coverage(self):
        if not all(amea.discover_executable(name) for name in ("ffmpeg", "ffprobe")):
            self.skipTest("FFmpeg/FFprobe unavailable")
        root, _, _ = self.fixture()
        result = amea.pencil_test(root, "s1")
        root, data = amea.load_project(root)
        shot = data["shots"][0]
        data["final_video"] = Path(result["pencil_test"]).relative_to(root).as_posix()
        data["changes"] = [{"id": "c1", "scope": "persistent", "start_frame": 0,
                            "end_frame": None, "affected_shots": ["s1"]}]
        shot["change_ids"] = ["c1"]
        amea.write_json(root / "project.json", data)
        self.review(data, shot, "rough")
        self.review(data, shot, "final")
        report = amea.validate_project(root, require_complete=True)
        self.assertTrue(report["structural_passed"], report)
        data["changes"][0]["affected_shots"] = []
        amea.write_json(root / "project.json", data)
        report = amea.validate_project(root, require_complete=True)
        self.assertFalse(report["structural_passed"])
        self.assertIn("coverage", " ".join(report["errors"]))


class PackagingTests(unittest.TestCase):
    def test_standalone_links_and_archive_members(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="amea-package-", dir=TEST_TEMP) as directory:
            self.assertTrue(Path(directory).resolve().is_relative_to(TEST_TEMP.resolve()))
            root = Path(directory) / "AMEA"
            shutil.copytree(source / "skills", root / "skills", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copytree(source / "tools", root / "tools", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copyfile(source / "README.md", root / "README.md")
            shutil.copyfile(source / "QUALITY-AUDIT.md", root / "QUALITY-AUDIT.md")
            shutil.copyfile(source / "LICENSE", root / "LICENSE")
            shutil.copyfile(source / ".gitignore", root / ".gitignore")
            for requirement in source.glob('requirements*.txt'):
                shutil.copyfile(requirement,root / requirement.name)
            spec = importlib.util.spec_from_file_location("amea_builder", root / "tools/build_package.py")
            builder = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(builder)
            result = builder.build(root)
            content = Path(result["standalone_instructions"]).read_text(encoding="utf-8")
            self.assertEqual(Path(result['standalone_instructions']).name,'CHATGPT-AMEA.md')
            for name in ("amea-create", "amea-recreate", "amea-edit", "amea-3d"):
                self.assertIn(f"skills/{name}/SKILL.md", content)
            self.assertNotIn("](../", content)
            with zipfile.ZipFile(result["archive"]) as archive:
                names = archive.namelist()
                self.assertEqual(len(names), len(set(names)))
                self.assertTrue(all(name.startswith("AMEA/") for name in names))
                self.assertFalse(any("__pycache__" in name for name in names))
                self.assertIn('AMEA/requirements-2d.txt',names)
                self.assertIn('AMEA/requirements-hunyuan.txt',names)
                self.assertIn('AMEA/CHATGPT-AMEA.md',names)
                self.assertIn('AMEA/QUALITY-AUDIT.md',names)
                self.assertIn('AMEA/LICENSE',names)
                self.assertIn('AMEA/.gitignore',names)
                self.assertIn('AMEA/tools/delivery_gate.py',names)
                self.assertIn('AMEA/skills/amea/references/first-delivery.md',names)
                self.assertFalse(any('/projects/' in name or '/runtime/' in name or '/.work/' in name for name in names))
                self.assertLess(Path(result['archive']).stat().st_size,2_000_000)
                self.assertIsNone(archive.testzip())


if __name__ == "__main__":
    unittest.main()
