#!/usr/bin/env python3
"""Synthetic tool fixtures only, created in temporary directories."""
import contextlib
from datetime import datetime, timedelta, timezone
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

import audit
import completion
import test_audit


class CompletionTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_audit.AuditToolTests()
        self.fixture.setUp()
        self.root = self.fixture.root

    def tearDown(self):
        self.fixture.tearDown()

    def call(self, *argv):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            result = completion.main(["--root", str(self.root), *map(str, argv)])
        return result, stream.getvalue()

    def extend(self):
        categories = ["mathematics_physics", "customer_support", "reading_comprehension", "practical_reasoning"]
        tasks = [dict(task_id=f"M{i:02d}", category=categories[i // 8], stage="main_draft", task_version="0.1", title="Synthetic main fixture", prompt=f"Unassessed synthetic main prompt {i}") for i in range(32)]
        references = [dict(task_id=t["task_id"], reference_version="0.1", verification_status="pending_dominic", expected_answer="Synthetic reference", checklist=["Synthetic check"], evidence=["Synthetic evidence"], ambiguity_notes="Synthetic fixture only") for t in tasks]
        self.fixture.write_json("02_tasks/main_tasks.json", tasks)
        self.fixture.write_json("03_references/main_references.json", references)
        self.fixture.verifications.extend(dict(task_id=t["task_id"], reference_version="0.1", decision="", reviewer="", verified_at="", notes="") for t in tasks)
        self.fixture.save_verifications()
        return self.fixture.tasks + tasks

    def full_baseline(self):
        tasks = self.extend()
        base = datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=4)
        for row in self.fixture.verifications:
            row.update(decision="verified", reviewer="Codex (AI)", verified_at=base.isoformat())
        self.fixture.save_verifications()
        provenance = []
        labels = []
        for task in tasks:
            for slot in "AB":
                rid = task["task_id"] + "-" + slot
                raw, prompt = audit.expected_paths(rid)
                raw_bytes = b"Synthetic candidate, never an assessed response.\r\n"
                prompt_bytes = task["prompt"].encode()
                (self.root / raw).write_bytes(raw_bytes)
                (self.root / prompt).write_bytes(prompt_bytes)
                provenance.append(dict(response_id=rid, task_id=task["task_id"], slot=slot, task_version="0.1", model="Synthetic test model", generated_at=(base + timedelta(minutes=1)).isoformat(), date_precision="datetime", source="Synthetic tests", session_id="synthetic-" + rid, settings="unknown", collector="Codex (AI)", source_status="ai_recorded", imported_at=(base + timedelta(minutes=2)).isoformat(), prompt_sha256=audit.digest(prompt_bytes), reply_sha256=audit.digest(raw_bytes), raw_path=raw, actual_prompt_path=prompt))
                row = self.fixture.completed_row()
                row.update(response_id=rid, task_id=task["task_id"], reviewer="Codex (AI)", reviewed_at=(base + timedelta(hours=3)).isoformat(), round="final_baseline")
                labels.append(row)
        self.fixture.write_csv("04_responses/provenance.csv", provenance, audit.PROVENANCE_FIELDS)
        pilot = [dict(row, round="pilot_initial", reviewed_at=(base + timedelta(minutes=10)).isoformat()) for row in labels[:16]]
        pilot_csv = self.root / "synthetic-pilot.csv"
        pilot_csv.write_text(audit.csv_text(pilot, audit.ANNOTATION_FIELDS))
        with patch.object(completion, "now", return_value=base + timedelta(hours=1)):
            code, output = self.call("freeze", "--annotations", pilot_csv, "--output", self.root / "pilot_snapshot")
        self.assertEqual(code, 0, output)
        rubric = self.root / "synthetic_rubric.md"
        rubric.write_text("Synthetic rubric only")
        decision = dict(final_rubric_version="0.1", decided_by="Codex (AI)", decided_at=(base + timedelta(hours=2)).isoformat(), decision_rationale="Synthetic no-change pilot decision; not assessed work.", rubric_path=rubric.name, rubric_sha256=audit.digest(rubric.read_bytes()), pilot_snapshots=[dict(path="pilot_snapshot", submitted_sha256=audit.digest(pilot_csv.read_bytes()))])
        self.decision = self.root / "synthetic_decision.json"
        self.decision.write_text(json.dumps(decision))
        baseline_csv = self.root / "synthetic-baseline.csv"
        baseline_csv.write_text(audit.csv_text(labels, audit.ANNOTATION_FIELDS))
        self.baseline = self.root / "baseline_snapshot"
        with patch.object(completion, "now", return_value=base + timedelta(hours=4)):
            code, output = self.call("freeze", "--annotations", baseline_csv, "--output", self.baseline)
        self.assertEqual(code, 0, output)
        return tasks, labels, base

    def test_full_catalog_preserves_pending_pilot_template_and_blank_templates(self):
        self.extend()
        code, output = self.fixture.call("validate")
        self.assertEqual(code, 0, output)
        self.assertIn("Responses recorded: 0/80", output)
        self.assertIn("pending: 16", output)
        path = self.root / "all_blank.csv"
        code, output = self.call("template", "--round", "final_baseline", "--rubric-version", "actual-test-version", "--output", path)
        self.assertEqual(code, 0, output)
        rows = audit.read_csv(path, audit.ANNOTATION_FIELDS)
        self.assertEqual(len(rows), 80)
        self.assertTrue(all(not row[f] for row in rows for f in audit.ANNOTATION_FIELDS if f not in audit.METADATA_FIELDS))
        before = path.read_bytes()
        self.assertEqual(self.call("template", "--round", "x", "--rubric-version", "x", "--output", path)[0], 1)
        self.assertEqual(path.read_bytes(), before)

    def test_wrong_full_balance_fails(self):
        self.extend()
        path = self.root / "02_tasks/main_tasks.json"
        tasks = json.loads(path.read_text())
        tasks[0]["category"] = tasks[-1]["category"]
        path.write_text(json.dumps(tasks))
        code, output = self.fixture.call("validate")
        self.assertEqual(code, 1)
        self.assertIn("exactly 10", output)

    def test_ai_collector_is_explicit_and_status_has_null_empty_means(self):
        self.fixture.verify_first()
        code, output = self.fixture.import_first(extra=("--collector", "Codex (AI)"))
        self.assertEqual(code, 0, output)
        provenance = audit.read_csv(self.root / "04_responses/provenance.csv", audit.PROVENANCE_FIELDS)
        self.assertEqual(provenance[0]["source_status"], "ai_recorded")
        code, output = self.call("status")
        self.assertEqual(code, 0, output)
        report = json.loads(output)
        self.assertEqual(report["ai_complete_reviews"], 0)
        self.assertEqual(report["human_complete_reviews"], 0)
        self.assertIsNone(report["metrics"]["score_dimensions"]["accuracy"]["mean"])
        self.assertIsNone(report["metrics"]["material_error_rate"]["fraction"])
        rows = list(self.fixture.annotations)
        rows[0] = dict(self.fixture.completed_row(), reviewer="Codex (AI)")
        self.fixture.write_csv("05_annotations/annotations.csv", rows, audit.ANNOTATION_FIELDS)
        code, output = self.call("status")
        self.assertEqual(code, 0, output)
        report = json.loads(output)
        self.assertEqual(report["ai_complete_reviews"], 1)
        self.assertEqual(report["human_complete_reviews"], 0)
        self.assertEqual(report["metrics"]["score_dimensions"]["accuracy"], dict(observations=1, mean=2))

    def test_freeze_rejects_unsubmitted_then_preserves_bytes_and_refuses_overwrite(self):
        path = self.root / "05_annotations/annotations.csv"
        code, output = self.call("freeze", "--annotations", path, "--output", self.root / "empty")
        self.assertEqual(code, 1)
        self.assertFalse((self.root / "empty").exists())
        self.fixture.verify_first()
        self.assertEqual(self.fixture.import_first()[0], 0)
        row = self.fixture.completed_row()
        path.write_text(audit.csv_text([row], audit.ANNOTATION_FIELDS))
        target = self.root / "original"
        code, output = self.call("freeze", "--annotations", path, "--output", target)
        self.assertEqual(code, 0, output)
        self.assertEqual((target / "submitted.csv").read_bytes(), path.read_bytes())
        self.assertEqual(self.call("freeze", "--annotations", path, "--output", target)[0], 1)
        (target / "submitted.csv").write_bytes(b"changed")
        with self.assertRaisesRegex(audit.AuditError, "CSV changed"):
            completion.snapshot(self.root, target)

    def test_final_requires_real_records_decision_and_timezone(self):
        code, output = self.call("validate-final", "--baseline", "absent", "--decision", "absent")
        self.assertEqual(code, 1)
        self.assertIn("40 verified tasks and 80 collected", output)
        self.full_baseline()
        code, output = self.call("validate-final", "--baseline", self.baseline, "--decision", self.decision)
        self.assertEqual(code, 0, output)
        decision = json.loads(self.decision.read_text())
        decision["decided_at"] = "2026-01-01T12:00:00"
        self.decision.write_text(json.dumps(decision))
        code, output = self.call("validate-final", "--baseline", self.baseline, "--decision", self.decision)
        self.assertEqual(code, 1)
        self.assertIn("timezone", output)

    def test_blind_recheck_selection_timing_privacy_and_pairing(self):
        tasks, baseline, base = self.full_baseline()
        destination = self.root / "recheck"
        with patch.object(completion, "now", return_value=base + timedelta(hours=23)):
            code, output = self.call("recheck", "--baseline", self.baseline, "--decision", self.decision, "--seed", "867", "--output", destination)
        self.assertEqual(code, 1)
        self.assertIn("24 hours", output)
        with patch.object(completion, "now", return_value=base + timedelta(hours=26)):
            code, output = self.call("recheck", "--baseline", self.baseline, "--decision", self.decision, "--seed", "867", "--output", destination)
        self.assertEqual(code, 1)  # First review old enough; selected baselines still too recent.
        self.assertIn("baseline reviews at least 24 hours", output)
        code, output = self.call("recheck", "--baseline", self.baseline, "--decision", self.decision, "--seed", "867", "--output", destination)
        self.assertEqual(code, 0, output)
        mapping_path = destination / "PRIVATE/private_map.json"
        private = json.loads(mapping_path.read_text())
        selected_ids = set(private["response_mapping"].values())
        task_ids = {rid.rsplit("-", 1)[0] for rid in selected_ids}
        self.assertEqual(len(task_ids), 16)
        for category in audit.CATEGORIES:
            self.assertEqual(sum(t["task_id"] in task_ids and t["category"] == category for t in tasks), 4)
        packet = (destination / "review/review_packet.md").read_text()
        self.assertNotIn("Synthetic test model", packet)
        self.assertNotIn("Synthetic validation example", packet)
        for rid in selected_ids:
            self.assertNotIn(rid, packet)
        rows = audit.read_csv(destination / "review/annotations.csv", audit.ANNOTATION_FIELDS)
        self.assertTrue(all(row["task_id"] == "" and row["reviewer"] == "" and row["accuracy"] == "" for row in rows))
        lookup = {row["response_id"]: row for row in baseline}
        for row in rows:
            original = lookup[private["response_mapping"][row["response_id"]]]
            neutral_id = row["response_id"]
            row.update(original)
            row.update(response_id=neutral_id, task_id="", round="blind_recheck", reviewed_at=completion.now().isoformat())
        rows[0].update(clarity="1", total="9")
        recheck_csv = destination / "review/annotations.csv"
        recheck_csv.write_text(audit.csv_text(rows, audit.ANNOTATION_FIELDS))
        frozen = self.root / "recheck_snapshot"
        code, output = self.call("freeze", "--annotations", recheck_csv, "--mapping", mapping_path, "--output", frozen)
        self.assertEqual(code, 0, output)
        code, output = self.call("compare-recheck", "--baseline", self.baseline, "--decision", self.decision, "--mapping", mapping_path, "--recheck", frozen)
        self.assertEqual(code, 0, output)
        report = json.loads(output)
        self.assertEqual(report["overall_exact_match"], dict(numerator=79, denominator=80, fraction=79/80, excluded_pairs=0))
        self.assertEqual(report["whole_response_exact_match"]["numerator"], 15)
        self.assertEqual(report["changes_needing_human_explanation"][0]["response_id"], private["response_mapping"][rows[0]["response_id"]])
        private["seed"] = 999
        mapping_path.write_text(json.dumps(private))
        code, output = self.call("compare-recheck", "--baseline", self.baseline, "--decision", self.decision, "--mapping", mapping_path, "--recheck", frozen)
        self.assertEqual(code, 1)
        self.assertIn("mapping frozen", output)

    def test_paired_metrics_missing_scores_are_excluded_not_zero(self):
        before = self.fixture.completed_row()
        after = dict(before, accuracy="", total="", correction_required="deferred")
        result = completion.paired_metrics([before], [after])
        self.assertEqual(result["overall_exact_match"]["denominator"], 4)
        self.assertEqual(result["overall_exact_match"]["excluded_pairs"], 1)
        self.assertIsNone(result["per_dimension_exact_match"]["accuracy"]["fraction"])
        self.assertIsNone(result["whole_response_exact_match"]["fraction"])
        self.assertIsNone(result["correction_decision_exact_match"]["fraction"])
        self.assertIsNone(completion.paired_metrics([], [])["overall_exact_match"]["fraction"])
        with self.assertRaisesRegex(audit.AuditError, "unique"):
            completion.paired_metrics([before], [after, after])
        with self.assertRaisesRegex(audit.AuditError, "absent"):
            completion.paired_metrics([before], [dict(after, response_id="absent")])


if __name__ == "__main__":
    unittest.main(verbosity=2)
