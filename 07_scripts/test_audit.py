"""Tool tests use synthetic temporary fixtures, never assessed portfolio answers."""

import contextlib
import csv
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().with_name("audit.py")
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("audit", SCRIPT)
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


class AuditToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "synthetic-project"
        for folder in ["02_tasks", "03_references", "04_responses/raw", "04_responses/prompts", "05_annotations"]:
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        self.tasks = [
            {"task_id": f"S{i+1:02}", "category": sorted(audit.CATEGORIES)[i//2], "stage": "pilot", "task_version": "0.1", "title": "Synthetic tool fixture", "prompt": f"Synthetic test prompt {i+1}\nUnicode: café"}
            for i in range(8)
        ]
        self.write_json("02_tasks/pilot_tasks.json", self.tasks)
        self.write_json("03_references/pilot_references.json", [
            {"task_id": task["task_id"], "reference_version": "0.1", "verification_status": "pending_dominic", "expected_answer": "Synthetic expected answer, outside assessed dataset.", "checklist": ["Synthetic check."], "evidence": ["Synthetic evidence."], "ambiguity_notes": "No ambiguity in this synthetic fixture."}
            for task in self.tasks
        ])
        self.verifications = [
            dict(task_id=task["task_id"], reference_version="0.1", decision="", reviewer="", verified_at="", notes="")
            for task in self.tasks
        ]
        self.save_verifications()
        self.write_csv("04_responses/provenance.csv", [], audit.PROVENANCE_FIELDS)
        self.annotations = []
        for task in self.tasks:
            for slot in "AB":
                row = dict.fromkeys(audit.ANNOTATION_FIELDS, "")
                row.update(response_id=f"{task['task_id']}-{slot}", task_id=task["task_id"], round="pilot_initial", rubric_version="0.1")
                self.annotations.append(row)
        self.write_csv("05_annotations/annotations.csv", self.annotations, audit.ANNOTATION_FIELDS)
        self.reply = self.root / "synthetic-reply.txt"
        self.prompt = self.root / "synthetic-prompt.txt"
        self.reply_bytes = b"Synthetic reply only.\r\nWhitespace retained.  \r\n\xc3\xa9\n"
        self.reply.write_bytes(self.reply_bytes)
        self.prompt.write_bytes(self.tasks[0]["prompt"].encode("utf-8"))

    def tearDown(self):
        self.temp.cleanup()

    def write_json(self, path, values):
        (self.root / path).write_text(json.dumps(values), encoding="utf-8")

    def write_csv(self, path, rows, fields):
        (self.root / path).write_text(audit.csv_text(rows, fields), encoding="utf-8", newline="")

    def save_verifications(self):
        self.write_csv("03_references/reference_verification.csv", self.verifications, audit.VERIFICATION_FIELDS)

    def verify_first(self):
        self.verifications[0].update(decision="verified", reviewer="Synthetic test reviewer", verified_at="2026-09-08T09:00:00+01:00")
        self.save_verifications()

    def call(self, *argv):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            result = audit.main(["--root", str(self.root), *argv])
        return result, stream.getvalue()

    def import_first(self, slot="A", session="synthetic-chat-1", extra=()):
        return self.call("import-response", "--task-id", "S01", "--slot", slot,
                         "--reply", str(self.reply), "--actual-prompt", str(self.prompt),
                         "--model", "Synthetic test model", "--generated-at", "2026-09-08",
                         "--source", "Synthetic fixture", "--session-id", session, *extra)

    def completed_row(self):
        row = dict(self.annotations[0])
        row.update(reviewer="Synthetic test reviewer", reviewed_at="2026-09-08T10:00:00+01:00",
                   annotation_status="complete", accuracy="2", instruction_following="2",
                   relevance="2", completeness="2", clarity="2", total="10",
                   primary_error="none", uncertainty_flag="no", material_error="no",
                   correction_required="no", rationale="Synthetic validation example only.")
        return row

    def test_preparation_passes_with_honest_pending_counts(self):
        code, output = self.call("validate")
        self.assertEqual(code, 0, output)
        self.assertIn("Responses recorded: 0/16; missing: 16", output)
        self.assertIn("pending: 16", output)
        self.assertIn("does not mean the project is complete", output)
        code, output = self.call("validate", "--require-collected")
        self.assertEqual(code, 1)
        self.assertIn("16 of 16 planned responses are missing", output)

    def test_import_refuses_unverified_reference_and_malformed_verification(self):
        code, output = self.import_first()
        self.assertEqual(code, 1)
        self.assertIn("must verify", output)
        self.assertFalse((self.root / "04_responses/raw/S01-A.txt").exists())
        self.verify_first()
        self.verifications[0]["verified_at"] = "2026-09-08T09:00:00"
        self.save_verifications()
        code, output = self.import_first()
        self.assertEqual(code, 1)
        self.assertIn("timezone", output)
        self.verifications[0]["verified_at"] = "2026-09-08T09:00:00Z"
        self.verifications[0]["reviewer"] = ""
        self.save_verifications()
        code, output = self.import_first()
        self.assertEqual(code, 1)
        self.assertIn("requires reviewer", output)

    def test_import_preserves_exact_bytes_hashes_and_date_precision(self):
        self.verify_first()
        code, output = self.import_first()
        self.assertEqual(code, 0, output)
        self.assertEqual((self.root / "04_responses/raw/S01-A.txt").read_bytes(), self.reply_bytes)
        self.assertEqual((self.root / "04_responses/prompts/S01-A.txt").read_bytes(), self.prompt.read_bytes())
        rows = audit.read_csv(self.root / "04_responses/provenance.csv", audit.PROVENANCE_FIELDS)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["reply_sha256"], audit.digest(self.reply_bytes))
        self.assertEqual(rows[0]["prompt_sha256"], audit.digest(self.prompt.read_bytes()))
        self.assertEqual(rows[0]["settings"], "unknown")
        self.assertEqual(rows[0]["date_precision"], "date")
        self.assertEqual(rows[0]["source_status"], "user_recorded")
        code, output = self.call("validate")
        self.assertEqual(code, 0, output)
        self.assertIn("Responses recorded: 1/16", output)

    def test_duplicate_id_and_session_prevent_overwrites(self):
        self.verify_first()
        self.assertEqual(self.import_first()[0], 0)
        original = (self.root / "04_responses/provenance.csv").read_bytes()
        self.reply.write_text("Replacement test text", encoding="utf-8")
        code, output = self.import_first(session="synthetic-chat-2")
        self.assertEqual(code, 1)
        self.assertIn("already imported", output)
        self.assertEqual((self.root / "04_responses/raw/S01-A.txt").read_bytes(), self.reply_bytes)
        code, output = self.import_first(slot="B")
        self.assertEqual(code, 1)
        self.assertIn("session_id is already used", output)
        self.assertEqual((self.root / "04_responses/provenance.csv").read_bytes(), original)
        self.assertFalse((self.root / "04_responses/raw/S01-B.txt").exists())

    def test_prompt_whitespace_mismatch_is_refused(self):
        self.verify_first()
        self.prompt.write_bytes(self.prompt.read_bytes() + b"\n")
        code, output = self.import_first()
        self.assertEqual(code, 1)
        self.assertIn("Actual prompt differs", output)
        self.assertFalse((self.root / "04_responses/raw/S01-A.txt").exists())

    def test_wrong_pilot_category_balance_fails(self):
        self.tasks[0]["category"] = self.tasks[-1]["category"]
        self.write_json("02_tasks/pilot_tasks.json", self.tasks)
        code, output = self.call("validate")
        self.assertEqual(code, 1)
        self.assertIn("exactly 2 in each of 4 categories", output)

    def test_exact_category_names_and_substantive_reference_fields_required(self):
        for task in self.tasks[:2]:
            task["category"] = "unplanned_category"
        self.write_json("02_tasks/pilot_tasks.json", self.tasks)
        code, output = self.call("validate")
        self.assertEqual(code, 1)
        self.assertIn("exactly 2 in each of 4 categories", output)
        refs = audit.read_json_array(self.root / "03_references/pilot_references.json")
        refs[0].update(expected_answer="", checklist=[], evidence=[""], ambiguity_notes="")
        self.write_json("03_references/pilot_references.json", refs)
        code, output = self.call("validate")
        self.assertEqual(code, 1)
        for field in ["expected_answer", "checklist", "evidence", "ambiguity_notes"]:
            self.assertIn(field, output)

    def test_known_generation_timestamp_order_is_checked(self):
        now = datetime.now(timezone.utc).replace(microsecond=0)
        verified = now - timedelta(hours=2)
        self.verify_first()
        self.verifications[0]["verified_at"] = verified.isoformat()
        self.save_verifications()
        code, output = self.import_first(extra=("--generated-at", (verified - timedelta(seconds=1)).isoformat()))
        self.assertEqual(code, 1)
        self.assertIn("precedes reference verification", output)
        code, output = self.import_first(extra=("--generated-at", (now + timedelta(days=1)).isoformat()))
        self.assertEqual(code, 1)
        self.assertIn("later than the current import time", output)
        code, output = self.import_first(extra=("--generated-at", (now - timedelta(hours=1)).isoformat()))
        self.assertEqual(code, 0, output)
        self.assertIn("date precision: datetime", output)
        code, output = self.call("validate")
        self.assertEqual(code, 0, output)
        records = audit.read_csv(self.root / "04_responses/provenance.csv", audit.PROVENANCE_FIELDS)
        records[0]["imported_at"] = (now - timedelta(hours=3)).isoformat()
        self.write_csv("04_responses/provenance.csv", records, audit.PROVENANCE_FIELDS)
        code, output = self.call("validate")
        self.assertEqual(code, 1)
        self.assertIn("generation timestamp is later than import timestamp", output)

    def test_modified_reply_bytes_fail_hash_check(self):
        self.verify_first()
        self.assertEqual(self.import_first()[0], 0)
        (self.root / "04_responses/raw/S01-A.txt").write_bytes(b"Altered fixture")
        code, output = self.call("validate")
        self.assertEqual(code, 1)
        self.assertIn("reply_sha256 does not match saved bytes", output)

    def test_score_total_and_material_correction_constraints(self):
        row = self.completed_row()
        self.assertEqual(audit.annotation_errors(row, "test"), [])
        row["total"] = "10.0"
        self.assertEqual(audit.annotation_errors(row, "test"), [])
        row["accuracy"] = "3"
        self.assertTrue(any("integer 0, 1 or 2" in error for error in audit.annotation_errors(row, "test")))
        row = self.completed_row()
        row.update(material_error="yes", primary_error="factual_error")
        self.assertTrue(any("requires correction_required yes" in error for error in audit.annotation_errors(row, "test")))
        row["correction_required"] = "yes"
        self.assertTrue(any("requires a corrected_answer" in error for error in audit.annotation_errors(row, "test")))
        row["corrected_answer"] = "A synthetic correction."
        self.assertEqual(audit.annotation_errors(row, "test"), [])

    def test_clarification_preserves_pending_correction_and_unknown_scores(self):
        row = self.completed_row()
        row.update(annotation_status="needs_clarification", accuracy="", total="",
                   primary_error="reference_issue", uncertainty_flag="yes",
                   uncertainty_note="Synthetic reference is unresolved; cannot correct yet.",
                   material_error="yes", correction_required="yes",
                   rationale="Synthetic reference is unresolved; clarification is needed before a sound correction.")
        self.assertEqual(audit.annotation_errors(row, "test"), [])
        row.update(material_error="uncertain", correction_required="deferred")
        self.assertEqual(audit.annotation_errors(row, "test"), [])
        row["annotation_status"] = "complete"
        problems = audit.annotation_errors(row, "test")
        self.assertTrue(any("uncertain is allowed only" in error for error in problems))
        self.assertTrue(any("deferred only" in error for error in problems))

    def test_submitted_annotations_require_rationale_and_no_duplicate_tags(self):
        row = self.completed_row()
        row["rationale"] = ""
        self.assertTrue(any("specific rationale" in error for error in audit.annotation_errors(row, "test")))
        row = self.completed_row()
        row.update(primary_error="factual_error", secondary_errors="factual_error;unit_error;unit_error")
        self.assertTrue(any("must not be duplicated" in error for error in audit.annotation_errors(row, "test")))

    def test_blind_export_omits_model_metadata_and_preserves_raw_bytes(self):
        self.verify_first()
        self.assertEqual(self.import_first()[0], 0)
        self.assertEqual(self.import_first(slot="B", session="synthetic-chat-2")[0], 0)
        before = (self.root / "04_responses/provenance.csv").read_bytes()
        output_path = self.root / "05_annotations/batch01"
        code, output = self.call("blind-batch", "--task-ids", "S01", "--output", str(output_path))
        self.assertEqual(code, 0, output)
        packet = (output_path / "review_packet.md").read_text(encoding="utf-8")
        self.assertNotIn("Synthetic test model", packet)
        self.assertNotIn("S01-A", packet)
        self.assertNotIn("S01-B", packet)
        mapping = json.loads((output_path / "private_map.json").read_text(encoding="utf-8"))["response_mapping"]
        self.assertEqual(set(mapping.values()), {"S01-A", "S01-B"})
        rows = audit.read_csv(output_path / "annotations.csv", audit.ANNOTATION_FIELDS)
        self.assertEqual(len(rows), 2)
        for row in rows:
            self.assertIn(row["response_id"], mapping)
            for field in audit.ANNOTATION_FIELDS:
                if field not in audit.METADATA_FIELDS:
                    self.assertEqual(row[field], "")
            self.assertEqual((output_path / "responses" / f"{row['response_id']}.txt").read_bytes(), self.reply_bytes)
        self.assertEqual((self.root / "04_responses/provenance.csv").read_bytes(), before)
        self.assertEqual(self.call("blind-batch", "--task-ids", "S01", "--output", str(output_path))[0], 1)
        submitted_bytes = (output_path / "annotations.csv").read_bytes()
        code, output = self.call("validate", "--annotations", str(output_path / "annotations.csv"))
        self.assertEqual(code, 0, output)
        self.assertIn("checked 2 mapped responses in memory", output)
        self.assertEqual((output_path / "annotations.csv").read_bytes(), submitted_bytes)
        # Explicit mapping supports a submitted copy kept in another folder.
        submitted_copy = self.root / "submitted-synthetic.csv"
        submitted_copy.write_bytes(submitted_bytes)
        code, output = self.call("validate", "--annotations", str(submitted_copy), "--mapping", str(output_path / "private_map.json"))
        self.assertEqual(code, 0, output)
        mapping_document = json.loads((output_path / "private_map.json").read_text(encoding="utf-8"))
        mapping_document["response_mapping"][next(iter(mapping))] = "S01-B"
        for key in mapping_document["response_mapping"]:
            mapping_document["response_mapping"][key] = "S01-B"
        (output_path / "private_map.json").write_text(json.dumps(mapping_document), encoding="utf-8")
        code, output = self.call("validate", "--annotations", str(output_path / "annotations.csv"))
        self.assertEqual(code, 1)
        self.assertIn("repeats an original response ID", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
