"""Acceptance-record behavior tests; synthetic records never establish real animation quality."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "tests/.work"
WORK.mkdir(exist_ok=True)
sys.path.insert(0, str(ROOT / "tools"))
import delivery_gate


class DeliveryGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="acceptance-", dir=WORK)
        self.root = Path(self.temp.name).resolve()
        self.manifest = self.root / "delivery.json"
        (self.root / "request.txt").write_text("Synthetic requirement fixture.", encoding="utf-8")
        (self.root / "plan.txt").write_text("Synthetic plan evidence.", encoding="utf-8")
        self.data = {
            "schema_version": 1, "stage": "plan", "request_files": ["request.txt"],
            "requirements": [{"id": "r1", "text": "Fixture constraint", "acceptance": "Fixture content present",
                              "checks": ["document"]}],
            "artifacts": [{"id": "a1", "path": "plan.txt"}],
            "reviews": [{"id": "v1", "method": "document", "requirement_ids": ["r1"], "artifact_ids": ["a1"],
                         "status": "pending", "observations": []}], "issues": [],
        }
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def record(self, review_id="v1"):
        self.save()
        signature = delivery_gate.Acceptance(self.manifest).fingerprint(review_id)
        review = next(item for item in self.data["reviews"] if item["id"] == review_id)
        review.update(status="pass", observations=["Synthetic observation, not a perceptual quality claim."],
                      fingerprint=signature)
        self.save()

    def test_calculating_fingerprint_does_not_review_or_modify_files(self):
        before = self.manifest.read_bytes()
        result = delivery_gate.Acceptance(self.manifest).fingerprint("v1")
        self.assertEqual(len(result), 64)
        self.assertEqual(self.manifest.read_bytes(), before)
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_current_complete_record_is_limited_to_its_stage(self):
        self.record()
        report = delivery_gate.check(self.manifest)
        self.assertTrue(report["recorded_acceptance_current"], report)
        self.assertEqual(report["stage"], "plan")
        self.assertIn("not certified", report["artistic_quality"])
        self.data["stage"] = "final"
        self.save()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_request_criteria_and_evidence_changes_invalidate_review(self):
        for change in ("request", "criteria", "evidence"):
            with self.subTest(change=change):
                self.record()
                if change == "request":
                    (self.root / "request.txt").write_text("Changed request.")
                elif change == "criteria":
                    self.data["requirements"][0]["acceptance"] = "Changed acceptance"
                    self.save()
                else:
                    (self.root / "plan.txt").write_text("Changed evidence.")
                self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_added_requirement_and_missing_required_review_cannot_pass(self):
        self.record()
        self.data["requirements"].append({"id": "r2", "text": "Further constraint", "acceptance": "Observed",
                                          "checks": ["document"]})
        self.save()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        self.data["requirements"].pop()
        self.data["requirements"][0]["checks"].append("visual")
        self.record()
        self.assertIn("missing current visual review", " ".join(delivery_gate.check(self.manifest)["errors"]))

    def test_open_issue_and_unreviewed_resolution_cannot_pass(self):
        self.data["issues"] = [{"id": "i1", "description": "Fixture defect", "requirement_ids": ["r1"],
                                "checks": ["document"], "artifact_ids": ["a1"], "state": "open"}]
        self.record()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        self.data["issues"][0].update(state="resolved", resolution_review_ids=["v1"])
        self.save()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        self.data["reviews"][0]["issue_ids"] = ["i1"]
        self.record()
        self.assertTrue(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        self.data["issues"][0]["description"] = "Different defect"
        self.save()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_declared_frame_coverage_combines_reviews_but_rejects_gaps(self):
        self.data["requirements"][0]["frame_ranges"] = [[0, 12]]
        self.data["reviews"][0]["frame_ranges"] = [[0, 5]]
        second = copy.deepcopy(self.data["reviews"][0])
        second.update(id="v2", frame_ranges=[[6, 12]])
        self.data["reviews"].append(second)
        self.record("v1")
        self.record("v2")
        self.assertIn("incomplete current document frame coverage", " ".join(delivery_gate.check(self.manifest)["errors"]))
        second["frame_ranges"] = [[5, 12]]
        self.record("v2")
        self.assertTrue(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        second["frame_ranges"] = [[0, 20]]
        self.save()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_invalid_or_unrecorded_frame_scope_cannot_cover_declared_scope(self):
        self.data["requirements"][0]["frame_ranges"] = [[0, 12]]
        self.record()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        for span in ([[4, 4]], [[-1, 4]], [[False, 4]], [[0, 1.5]]):
            with self.subTest(span=span):
                self.data["reviews"][0]["frame_ranges"] = span
                self.save()
                self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_issue_resolution_needs_its_own_methods_artifacts_and_frame_scope(self):
        (self.root / "repair.txt").write_text("Repair evidence")
        self.data["artifacts"].append({"id": "a2", "path": "repair.txt"})
        self.data["issues"] = [{"id": "i1", "description": "Fixture defect", "requirement_ids": ["r1"],
                                "checks": ["visual"], "artifact_ids": ["a2"], "frame_ranges": [[0, 4]],
                                "state": "resolved", "resolution_review_ids": ["v2"]}]
        closing = copy.deepcopy(self.data["reviews"][0])
        closing.update(id="v2", issue_ids=["i1"], frame_ranges=[[0, 4]])
        self.data["reviews"].append(closing)
        self.record("v1")
        self.record("v2")
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        closing.update(method="visual")
        self.record("v2")
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        closing.update(artifact_ids=["a2"], frame_ranges=[[0, 2]])
        self.record("v2")
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])
        closing["frame_ranges"] = [[0, 4]]
        self.record("v2")
        self.assertTrue(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_unrelated_artifact_change_does_not_stale_an_independent_review(self):
        (self.root / "other.txt").write_text("Separate evidence")
        self.data["artifacts"].append({"id": "a2", "path": "other.txt"})
        self.record()
        (self.root / "other.txt").write_text("Updated independent evidence")
        self.assertTrue(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_reused_checker_rehashes_files_between_checks(self):
        self.record()
        checker = delivery_gate.Acceptance(self.manifest)
        self.assertTrue(checker.check()["recorded_acceptance_current"])
        (self.root / "plan.txt").write_text("Modified after the preceding check")
        self.assertFalse(checker.check()["recorded_acceptance_current"])

    def test_reused_checker_reloads_changed_contract_before_checking_or_fingerprinting(self):
        self.record()
        checker = delivery_gate.Acceptance(self.manifest)
        before = checker.fingerprint("v1")
        self.data["stage"] = "rough"
        self.save()
        self.assertNotEqual(checker.fingerprint("v1"), before)
        self.assertFalse(checker.check()["recorded_acceptance_current"])
        self.record()
        self.assertTrue(checker.check()["recorded_acceptance_current"])
        self.data["requirements"][0]["checks"].append("visual")
        self.save()
        self.assertFalse(checker.check()["recorded_acceptance_current"])

    def test_missing_empty_escaping_and_self_referential_evidence_fail(self):
        for path in ("missing.bin", "empty.bin", "../outside.txt", "delivery.json"):
            with self.subTest(path=path):
                (self.root / "empty.bin").touch()
                self.data["artifacts"][0]["path"] = path
                self.save()
                self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_duplicates_unknown_references_and_empty_schema_fail(self):
        original = copy.deepcopy(self.data)
        for change in ("duplicate", "unknown", "empty"):
            with self.subTest(change=change):
                self.data = copy.deepcopy(original)
                if change == "duplicate":
                    self.data["requirements"].append(copy.deepcopy(self.data["requirements"][0]))
                elif change == "unknown":
                    self.data["reviews"][0]["artifact_ids"] = ["absent"]
                else:
                    self.data["requirements"] = []
                self.save()
                self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_bare_pass_without_observations_fails(self):
        self.record()
        self.data["reviews"][0]["observations"] = []
        self.save()
        self.assertFalse(delivery_gate.check(self.manifest)["recorded_acceptance_current"])

    def test_cli_returns_failure_for_incomplete_and_success_for_current_record(self):
        command = [sys.executable, str(ROOT / "tools/delivery_gate.py")]
        pending = subprocess.run([*command, "check", str(self.manifest)], capture_output=True, text=True)
        self.assertEqual(pending.returncode, 2, pending.stderr)
        fingerprint = subprocess.run([*command, "fingerprint", str(self.manifest), "--review", "v1"],
                                     capture_output=True, text=True)
        self.assertEqual(fingerprint.returncode, 0, fingerprint.stderr)
        self.assertEqual(len(json.loads(fingerprint.stdout)["fingerprint"]), 64)
        self.record()
        passed = subprocess.run([*command, "check", str(self.manifest)], capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stderr)


if __name__ == "__main__":
    unittest.main()
