#!/usr/bin/env python3
"""Portable, standard-library checks and collection support for the pilot and full forty-task audit.

This program does not generate answers, rate responses, verify a reference's
substance, or establish vendor authorship. Provenance is collector-recorded;
SHA-256 checks detect changes to the saved bytes. Fresh session IDs document
the collector's account of separate generations, not independent proof.

Examples (run from the project folder):
  python3 07_scripts/audit.py validate
  python3 07_scripts/audit.py import-response --task-id MP01 --slot A \
      --reply reply.txt --actual-prompt prompt.txt --model "Recorded model" \
      --generated-at 2026-09-09 --source "Web chat" --session-id "chat-unique-1"
  python3 07_scripts/audit.py blind-batch --task-ids MP01,CS01 --output batch01

Before importing, a named reviewer must verify the matching reference version in
03_references/reference_verification.csv. The actual prompt must match the
task's prompt exactly, including whitespace. Use a fresh chat for each reply.
Blind exports preserve exact response bytes in separate text files. Their
private_map.json, the original provenance, and original filenames must be kept
out of the reviewer's view. Candidate text itself may reveal model identity.
No suggested labels or scores are produced.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from datetime import date, datetime, timezone
from decimal import Decimal, InvalidOperation
import hashlib
import io
import json
from pathlib import Path
import re
import secrets
import shutil
import sys
import tempfile


PROVENANCE_FIELDS = [
    "response_id", "task_id", "slot", "task_version", "model", "generated_at",
    "date_precision", "source", "session_id", "settings", "collector",
    "source_status", "imported_at", "prompt_sha256", "reply_sha256",
    "raw_path", "actual_prompt_path",
]
VERIFICATION_FIELDS = [
    "task_id", "reference_version", "decision", "reviewer", "verified_at", "notes",
]
ANNOTATION_FIELDS = [
    "response_id", "task_id", "round", "rubric_version", "reviewer", "reviewed_at",
    "annotation_status", "accuracy", "instruction_following", "relevance",
    "completeness", "clarity", "total", "primary_error", "secondary_errors",
    "uncertainty_flag", "uncertainty_note", "material_error", "correction_required",
    "rationale", "corrected_answer",
]
SCORES = ["accuracy", "instruction_following", "relevance", "completeness", "clarity"]
ERROR_TAGS = {
    "none", "factual_error", "calculation_error", "unit_error", "unsupported_claim",
    "instruction_violation", "off_topic", "missing_content", "unclear_expression",
    "task_ambiguity", "reference_issue",
}
CATEGORIES = {"mathematics_physics", "customer_support", "reading_comprehension", "practical_reasoning"}
METADATA_FIELDS = {"response_id", "task_id", "round", "rubric_version"}
ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*\Z")


class AuditError(Exception):
    """Action cannot proceed without corrected input."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def timestamp(value: str) -> datetime:
    """Require a complete ISO timestamp with a known UTC offset."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", value):
        raise ValueError("use YYYY-MM-DDTHH:MM:SS+01:00 or a timestamp ending Z")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("a timezone offset or Z is required")
    return parsed


def generation_precision(value: str) -> str:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        date.fromisoformat(value)
        return "date"
    timestamp(value)
    return "datetime"


def read_json_array(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
        raise AuditError(f"{path}: expected a JSON array of objects")
    return data


def read_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != fields:
                raise AuditError(f"{path}: expected CSV headers {','.join(fields)}")
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error) as exc:
        raise AuditError(f"Cannot read {path}: {exc}") from exc
    for number, row in enumerate(rows, 2):
        if None in row or any(value is None for value in row.values()):
            raise AuditError(f"{path}: row {number} has the wrong number of columns")
    return rows


def csv_text(rows: list[dict], fields: list[str]) -> str:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def read_utf8_bytes(path: Path) -> bytes:
    try:
        data = path.read_bytes()
        decoded = data.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise AuditError(f"Cannot read UTF-8 text {path}: {exc}") from exc
    if not decoded.strip():
        raise AuditError(f"{path}: text is empty")
    return data


def load_preparation(root: Path) -> tuple[dict, dict, dict, list[str], int]:
    pilot_tasks = read_json_array(root / "02_tasks/pilot_tasks.json")
    tasks = list(pilot_tasks)
    refs = read_json_array(root / "03_references/pilot_references.json")
    main_path = root / "02_tasks/main_tasks.json"
    main_ref_path = root / "03_references/main_references.json"
    if main_path.exists() != main_ref_path.exists():
        raise AuditError("main_tasks.json and main_references.json must be provided together")
    main_tasks = read_json_array(main_path) if main_path.exists() else []
    tasks.extend(main_tasks)
    if main_path.exists():
        refs.extend(read_json_array(main_ref_path))
    verification = read_csv(root / "03_references/reference_verification.csv", VERIFICATION_FIELDS)
    errors: list[str] = []
    task_by_id: dict[str, dict] = {}
    for row in tasks:
        task_id = row.get("task_id")
        if not isinstance(task_id, str) or not ID_PATTERN.fullmatch(task_id):
            errors.append("Task has a missing or invalid task_id")
            continue
        if task_id in task_by_id:
            errors.append(f"Duplicate task_id: {task_id}")
        task_by_id[task_id] = row
        for field in ["category", "stage", "task_version", "title", "prompt"]:
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f"{task_id}: missing text field {field}")
        expected_stage = "pilot" if row in pilot_tasks else "main_draft"
        if row.get("stage") != expected_stage:
            errors.append(f"{task_id}: stage must be {expected_stage} in its source file")
    counts = Counter(row.get("category") for row in pilot_tasks if isinstance(row.get("category"), str))
    if len(pilot_tasks) != 8 or len({row.get("task_id") for row in pilot_tasks}) != 8 or set(counts) != CATEGORIES or set(counts.values()) != {2}:
        errors.append(f"Pilot must have 8 unique tasks and exactly 2 in each of 4 categories ({', '.join(sorted(CATEGORIES))}); got {dict(counts)}")
    if main_path.exists():
        counts = Counter(row.get("category") for row in tasks if isinstance(row.get("category"), str))
        if len(tasks) != 40 or len(task_by_id) != 40 or set(counts) != CATEGORIES or set(counts.values()) != {10}:
            errors.append(f"Full audit must have 40 unique tasks and exactly 10 in each of 4 categories; got {dict(counts)}")

    ref_by_id: dict[str, dict] = {}
    for row in refs:
        task_id = row.get("task_id")
        if not isinstance(task_id, str):
            errors.append("Reference has a missing or invalid task_id")
            continue
        if task_id in ref_by_id:
            errors.append(f"Duplicate reference task_id: {task_id}")
        ref_by_id[task_id] = row
        for field in ["reference_version", "verification_status", "expected_answer", "ambiguity_notes"]:
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f"{task_id}: missing reference field {field}")
        for field in ["checklist", "evidence"]:
            values = row.get(field)
            if not isinstance(values, list) or not values or any(not isinstance(value, str) or not value.strip() for value in values):
                errors.append(f"{task_id}: reference {field} must be a nonempty array of nonempty strings")
    if set(task_by_id) != set(ref_by_id):
        errors.append("Reference task IDs do not exactly match prepared task IDs")

    verification_by_id: dict[str, dict] = {}
    verified = 0
    for row in verification:
        task_id = row["task_id"]
        if task_id in verification_by_id:
            errors.append(f"Duplicate reference verification task_id: {task_id}")
        verification_by_id[task_id] = row
        if task_id not in ref_by_id:
            errors.append(f"Verification refers to unknown task {task_id}")
            continue
        if row["reference_version"] != ref_by_id[task_id].get("reference_version"):
            errors.append(f"{task_id}: verification reference_version does not match reference")
        decision = row["decision"]
        if decision not in {"", "verified", "revise", "needs_clarification"}:
            errors.append(f"{task_id}: invalid reference decision {decision!r}")
        if decision:
            valid = True
            if not row["reviewer"].strip():
                errors.append(f"{task_id}: reference decision requires reviewer")
                valid = False
            try:
                timestamp(row["verified_at"])
            except ValueError as exc:
                errors.append(f"{task_id}: invalid verified_at ({exc})")
                valid = False
            if decision in {"revise", "needs_clarification"} and not row["notes"].strip():
                errors.append(f"{task_id}: {decision} requires reference notes")
                valid = False
            if decision == "verified" and valid and row["reference_version"] == ref_by_id[task_id].get("reference_version"):
                verified += 1
        elif any(row[field].strip() for field in ["reviewer", "verified_at"]):
            errors.append(f"{task_id}: recorded review details need a reference decision")
    if set(verification_by_id) != set(task_by_id):
        errors.append("Reference verification must have exactly one row for each prepared task")
    return task_by_id, ref_by_id, verification_by_id, errors, verified


def expected_paths(response_id: str) -> tuple[str, str]:
    return (f"04_responses/raw/{response_id}.txt", f"04_responses/prompts/{response_id}.txt")


def validate_provenance(root: Path, tasks: dict, verification: dict, rows: list[dict]) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    seen: set[str] = set()
    sessions: set[str] = set()
    for row in rows:
        response_id = row["response_id"]
        task_id = row["task_id"]
        slot = row["slot"]
        if response_id in seen:
            errors.append(f"Duplicate provenance response_id: {response_id}")
        seen.add(response_id)
        for field in PROVENANCE_FIELDS:
            if not row[field].strip():
                errors.append(f"{response_id}: missing provenance {field}")
        if task_id not in tasks or slot not in {"A", "B"} or response_id != f"{task_id}-{slot}":
            errors.append(f"{response_id}: invalid task/slot/response ID combination")
            continue
        if row["task_version"] != tasks[task_id].get("task_version"):
            errors.append(f"{response_id}: task_version mismatch")
        if row["session_id"] in sessions:
            errors.append(f"{response_id}: session_id reused; each response must use a fresh session")
        sessions.add(row["session_id"])
        if verification.get(task_id, {}).get("decision") != "verified":
            errors.append(f"{response_id}: reference has not been verified")
        try:
            if generation_precision(row["generated_at"]) != row["date_precision"]:
                errors.append(f"{response_id}: date_precision does not match generated_at")
        except ValueError as exc:
            errors.append(f"{response_id}: invalid generated_at ({exc})")
        try:
            timestamp(row["imported_at"])
        except ValueError as exc:
            errors.append(f"{response_id}: invalid imported_at ({exc})")
        if row["date_precision"] == "datetime":
            try:
                generated_at = timestamp(row["generated_at"])
                verified_at = timestamp(verification.get(task_id, {}).get("verified_at", ""))
                imported_at = timestamp(row["imported_at"])
                if generated_at < verified_at:
                    errors.append(f"{response_id}: generation timestamp precedes reference verification")
                if generated_at > imported_at:
                    errors.append(f"{response_id}: generation timestamp is later than import timestamp")
            except ValueError:
                # The corresponding timestamp problem is reported elsewhere.
                pass
        if row["source_status"] not in {"user_recorded", "ai_recorded"}:
            errors.append(f"{response_id}: source_status must be user_recorded or ai_recorded")
        if row["collector"] == "Codex (AI)" and row["source_status"] != "ai_recorded":
            errors.append(f"{response_id}: AI collection must be identified as ai_recorded")
        raw_path, prompt_path = expected_paths(response_id)
        for field, expected in [("raw_path", raw_path), ("actual_prompt_path", prompt_path)]:
            if row[field] != expected:
                errors.append(f"{response_id}: {field} must be {expected}")
        for relative, hash_field in [(raw_path, "reply_sha256"), (prompt_path, "prompt_sha256")]:
            try:
                data = read_utf8_bytes(root / relative)
                if digest(data) != row[hash_field]:
                    errors.append(f"{response_id}: {hash_field} does not match saved bytes")
                if hash_field == "prompt_sha256" and data != tasks[task_id].get("prompt", "").encode("utf-8"):
                    errors.append(f"{response_id}: saved actual prompt does not exactly match task prompt")
            except AuditError as exc:
                errors.append(str(exc))
    planned = {f"{task_id}-{slot}" for task_id in tasks for slot in "AB"}
    for folder in [root / "04_responses/raw", root / "04_responses/prompts"]:
        if folder.exists():
            for path in folder.glob("*.txt"):
                if path.stem not in seen:
                    errors.append(f"Untracked response/prompt file: {path.relative_to(root)}")
    return errors, seen & planned


def annotation_errors(row: dict, label: str) -> list[str]:
    errors: list[str] = []
    if not any(row[field].strip() for field in ANNOTATION_FIELDS if field not in METADATA_FIELDS):
        return errors
    status = row["annotation_status"]
    if status not in {"in_progress", "complete", "needs_clarification"}:
        errors.append(f"{label}: started annotation needs a valid annotation_status")
    if not row["reviewer"].strip():
        errors.append(f"{label}: started annotation requires reviewer")
    try:
        timestamp(row["reviewed_at"])
    except ValueError as exc:
        errors.append(f"{label}: invalid reviewed_at ({exc})")
    submitted = status in {"complete", "needs_clarification"}
    for field in SCORES:
        if row[field] and row[field] not in {"0", "1", "2"}:
            errors.append(f"{label}: {field} must be an integer 0, 1 or 2")
        if status == "complete" and not row[field]:
            errors.append(f"{label}: complete annotation requires {field}")
    all_scores = all(row[field] in {"0", "1", "2"} for field in SCORES)
    if all_scores:
        expected = sum(int(row[field]) for field in SCORES)
        try:
            correct_total = Decimal(row["total"]) == expected
        except InvalidOperation:
            correct_total = False
        if not correct_total:
            errors.append(f"{label}: total must be {expected}")
    elif row["total"]:
        errors.append(f"{label}: total must be blank until all five scores are valid")
    primary = row["primary_error"]
    if primary and primary not in ERROR_TAGS:
        errors.append(f"{label}: invalid primary_error {primary!r}")
    if submitted and not primary:
        errors.append(f"{label}: submitted annotation requires primary_error")
    secondary = row["secondary_errors"].split(";") if row["secondary_errors"] else []
    if any(tag not in ERROR_TAGS - {"none"} for tag in secondary):
        errors.append(f"{label}: secondary_errors must use additional valid tags separated by semicolons")
    if len(set(secondary)) != len(secondary) or primary in secondary:
        errors.append(f"{label}: error tags must not be duplicated")
    if primary == "none" and secondary:
        errors.append(f"{label}: primary_error none cannot have secondary errors")
    if row["uncertainty_flag"] not in {"", "yes", "no"} or (submitted and not row["uncertainty_flag"]):
        errors.append(f"{label}: uncertainty_flag must be yes or no for submitted annotations")
    material_choices = {"", "yes", "no"}
    if status == "needs_clarification":
        material_choices.add("uncertain")
    if row["material_error"] not in material_choices or (submitted and not row["material_error"]):
        errors.append(f"{label}: material_error must be yes or no; uncertain is allowed only for needs_clarification")
    if row["uncertainty_flag"] == "yes" and not row["uncertainty_note"].strip():
        errors.append(f"{label}: uncertainty yes requires uncertainty_note")
    if status == "needs_clarification" and row["uncertainty_flag"] != "yes":
        errors.append(f"{label}: needs_clarification requires uncertainty_flag yes")
    correction = row["correction_required"]
    if correction not in {"", "yes", "no", "deferred"} or (submitted and not correction):
        errors.append(f"{label}: invalid or missing correction_required")
    if correction == "deferred" and status != "needs_clarification":
        errors.append(f"{label}: correction may be deferred only for needs_clarification")
    if row["material_error"] == "yes":
        if correction != "yes":
            errors.append(f"{label}: material_error yes requires correction_required yes regardless of total")
        if primary == "none":
            errors.append(f"{label}: material_error yes cannot use primary_error none")
    if correction == "yes" and not row["corrected_answer"].strip() and status != "needs_clarification":
        errors.append(f"{label}: correction_required yes requires a corrected_answer")
    if correction in {"no", "deferred"} and row["corrected_answer"].strip():
        errors.append(f"{label}: corrected_answer must be blank when correction_required is {correction}")
    if submitted and not row["rationale"].strip():
        errors.append(f"{label}: submitted annotation requires a specific rationale")
    return errors


def validate_annotations(rows: list[dict], tasks: dict, recorded: set[str], expected_responses: set[str] | None = None) -> tuple[list[str], Counter]:
    errors: list[str] = []
    counts: Counter = Counter()
    seen: set[tuple] = set()
    planned = {f"{task_id}-{slot}": task_id for task_id in tasks for slot in "AB"}
    expected = set(planned) if expected_responses is None else expected_responses
    covered: set[str] = set()
    for row in rows:
        response_id = row["response_id"]
        key = (response_id, row["round"], row["rubric_version"])
        label = "/".join(key)
        if key in seen:
            errors.append(f"Duplicate annotation record: {label}")
        seen.add(key)
        covered.add(response_id)
        if response_id not in planned or row["task_id"] != planned.get(response_id):
            errors.append(f"{label}: unknown response or mismatched task_id")
        if not row["round"].strip() or not row["rubric_version"].strip():
            errors.append(f"{label}: round and rubric_version are required")
        started = any(row[field].strip() for field in ANNOTATION_FIELDS if field not in METADATA_FIELDS)
        if started and response_id not in recorded:
            errors.append(f"{label}: annotation has started before the response was imported")
        counts[row["annotation_status"] or "pending"] += 1
        errors.extend(annotation_errors(row, label))
    if expected != covered:
        errors.append(f"Annotation coverage must contain all {len(expected)} expected responses; missing {len(expected - covered)}, unexpected {len(covered - expected)}")
    return errors, counts


def map_blind_annotations(rows: list[dict], mapping_path: Path) -> tuple[list[dict], set[str]]:
    """Read coordinator mapping and copy rows in memory; never rewrite submitted CSV."""
    try:
        document = json.loads(mapping_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Cannot read blind mapping {mapping_path}: {exc}") from exc
    mapping = document.get("response_mapping") if isinstance(document, dict) else None
    if not isinstance(mapping, dict) or not mapping or any(not isinstance(key, str) or not isinstance(value, str) or not key or not value for key, value in mapping.items()):
        raise AuditError("Blind mapping must have a nonempty response_mapping object of neutral IDs to original response IDs")
    if len(set(mapping.values())) != len(mapping):
        raise AuditError("Blind mapping repeats an original response ID")
    submitted_ids = {row["response_id"] for row in rows}
    if submitted_ids != set(mapping):
        raise AuditError(f"Blind annotation IDs must exactly match the selected mapping; missing {len(set(mapping) - submitted_ids)}, unexpected {len(submitted_ids - set(mapping))}")
    for row in rows:
        expected_task = mapping[row["response_id"]].rsplit("-", 1)[0]
        if row["task_id"] and row["task_id"] != expected_task:
            raise AuditError(f"{row['response_id']}: submitted task_id conflicts with blind mapping")
    mapped_rows = [dict(row, response_id=mapping[row["response_id"]], task_id=mapping[row["response_id"]].rsplit("-", 1)[0]) for row in rows]
    return mapped_rows, set(mapping.values())


def validate_command(args: argparse.Namespace) -> int:
    root = args.root
    tasks, refs, verification, errors, verified = load_preparation(root)
    provenance = read_csv(root / "04_responses/provenance.csv", PROVENANCE_FIELDS)
    provenance_errors, recorded = validate_provenance(root, tasks, verification, provenance)
    errors.extend(provenance_errors)
    path = args.annotations if args.annotations else root / "05_annotations/annotations.csv"
    annotations = read_csv(path, ANNOTATION_FIELDS)
    mapping_path = args.mapping
    if mapping_path is None and args.annotations and (path.parent / "private_map.json").is_file():
        mapping_path = path.parent / "private_map.json"
    expected_responses = None
    if args.annotations is None and len(tasks) == 40 and len(annotations) == 16:
        expected_responses = {f"{task_id}-{slot}" for task_id, task in tasks.items() if task["stage"] == "pilot" for slot in "AB"}
    if mapping_path:
        annotations, expected_responses = map_blind_annotations(annotations, mapping_path)
    annotation_problems, counts = validate_annotations(annotations, tasks, recorded, expected_responses)
    errors.extend(annotation_problems)
    expected = len(tasks) * 2
    missing = expected - len(recorded)
    if args.require_collected and missing:
        errors.append(f"Collection required: {missing} of {expected} planned responses are missing")
    if args.require_collected and verified != len(tasks):
        errors.append(f"Collection required: {len(tasks) - verified} references await valid verification")
    print(f"Prepared tasks: {len(tasks)}; reference records: {len(refs)}/{len(tasks)}")
    print(f"Reference decisions recorded as verified: {verified}/{len(tasks)}")
    print(f"Responses recorded: {len(recorded)}/{expected}; missing: {missing}")
    print(f"Annotation rows: {len(annotations)}; complete: {counts['complete']}; needs clarification: {counts['needs_clarification']}; in progress: {counts['in_progress']}; pending: {counts['pending']}")
    if mapping_path:
        print(f"Blind batch: checked {len(expected_responses)} mapped responses in memory; submitted CSV unchanged.")
    print("Provenance is collector-recorded. Hashes check saved bytes, not vendor authorship or answer quality.")
    date_only = sum(row["date_precision"] == "date" for row in provenance)
    if date_only:
        print(f"DATE-ONLY CAVEAT: {date_only} generation records lack a time/timezone; exact order relative to reference verification and import cannot be established from those dates.")
    if errors:
        print(f"Validation errors: {len(errors)}")
        for message in errors:
            print(f"ERROR: {message}")
        return 1
    print("Structural validation: PASS. This does not mean the project is complete.")
    if missing or verified < len(tasks) or counts["pending"] or counts["in_progress"] or counts["needs_clarification"]:
        print("PENDING: collection and/or human review remains outstanding; see counts above.")
    return 0


def import_command(args: argparse.Namespace) -> int:
    root = args.root
    tasks, _refs, verification, errors, _verified = load_preparation(root)
    if errors:
        raise AuditError("Preparation errors must be fixed before importing:\n" + "\n".join(errors))
    if args.task_id not in tasks:
        raise AuditError(f"Unknown task_id {args.task_id}")
    if verification[args.task_id]["decision"] != "verified":
        raise AuditError(f"{args.task_id}: a named reviewer must verify this reference version before collection/import")
    for field in ["model", "generated_at", "source", "session_id", "settings", "collector"]:
        if not getattr(args, field).strip():
            raise AuditError(f"--{field.replace('_', '-')} must not be blank")
    try:
        precision = generation_precision(args.generated_at)
    except ValueError as exc:
        raise AuditError(f"Invalid --generated-at: {exc}") from exc
    task = tasks[args.task_id]
    imported_at = datetime.now(timezone.utc).replace(microsecond=0)
    if precision == "datetime":
        generated_at = timestamp(args.generated_at)
        verified_at = timestamp(verification[args.task_id]["verified_at"])
        if generated_at < verified_at:
            raise AuditError("Generation timestamp precedes reference verification; references must be verified before collection")
        if generated_at > imported_at:
            raise AuditError("Generation timestamp is later than the current import time")
    response_id = f"{args.task_id}-{args.slot}"
    prompt = read_utf8_bytes(args.actual_prompt)
    reply = read_utf8_bytes(args.reply)
    if prompt != task["prompt"].encode("utf-8"):
        raise AuditError("Actual prompt differs from task.prompt. Copy the saved prompt exactly, including whitespace; do not edit the recorded actual prompt to conceal a difference.")
    provenance_path = root / "04_responses/provenance.csv"
    existing = read_csv(provenance_path, PROVENANCE_FIELDS)
    if any(row["response_id"] == response_id for row in existing):
        raise AuditError(f"{response_id} is already imported; originals will not be overwritten")
    if any(row["session_id"] == args.session_id for row in existing):
        raise AuditError("session_id is already used. Each response needs its own fresh chat/session.")
    raw_path, prompt_path = expected_paths(response_id)
    targets = [root / raw_path, root / prompt_path]
    if any(path.exists() for path in targets):
        raise AuditError("A target response/prompt file already exists; originals will not be overwritten")
    record = {
        "response_id": response_id, "task_id": args.task_id, "slot": args.slot,
        "task_version": task["task_version"], "model": args.model,
        "generated_at": args.generated_at, "date_precision": precision,
        "source": args.source, "session_id": args.session_id, "settings": args.settings,
        "collector": args.collector, "source_status": "ai_recorded" if args.collector == "Codex (AI)" else "user_recorded",
        "imported_at": imported_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "prompt_sha256": digest(prompt), "reply_sha256": digest(reply),
        "raw_path": raw_path, "actual_prompt_path": prompt_path,
    }
    # A lock prevents simultaneous imports from dropping rows or reusing IDs.
    lock = provenance_path.with_suffix(".lock")
    try:
        lock_handle = lock.open("x")
    except FileExistsError as exc:
        raise AuditError(f"Import lock exists: {lock}. Wait for the other import; investigate a stale lock before removing it.") from exc
    created: list[Path] = []
    temporary: Path | None = None
    try:
        with lock_handle:
            current = read_csv(provenance_path, PROVENANCE_FIELDS)
            if current != existing:
                raise AuditError("Provenance changed during import; retry")
            for path, data in zip(targets, [reply, prompt]):
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("xb") as handle:
                    created.append(path)
                    handle.write(data)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=provenance_path.parent, prefix=".provenance-", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(csv_text(existing + [record], PROVENANCE_FIELDS))
            temporary.replace(provenance_path)
            temporary = None
    except Exception:
        for path in created:
            path.unlink(missing_ok=True)
        raise
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)
        lock.unlink(missing_ok=True)
    print(f"Imported {response_id}; reply and actual prompt preserved byte for byte.")
    print(f"Generation date precision: {precision}. Provenance is collector-recorded, not independently authenticated.")
    if precision == "date":
        print("DATE-ONLY CAVEAT: exact generation order relative to reference verification and import cannot be established from the recorded date.")
    return 0


def fenced(text: str) -> str:
    runs = re.findall(r"`+", text)
    fence = "`" * max(3, 1 + max((len(run) for run in runs), default=0))
    return fence + "text\n" + text + ("" if text.endswith("\n") else "\n") + fence + "\n"


def blind_command(args: argparse.Namespace) -> int:
    root = args.root
    tasks, _refs, verification, errors, _verified = load_preparation(root)
    provenance = read_csv(root / "04_responses/provenance.csv", PROVENANCE_FIELDS)
    problems, recorded = validate_provenance(root, tasks, verification, provenance)
    errors.extend(problems)
    if errors:
        raise AuditError("Fix validation errors before making a blind batch:\n" + "\n".join(errors))
    task_ids = [value.strip() for value in args.task_ids.split(",")]
    if not task_ids or any(not value for value in task_ids) or len(task_ids) != len(set(task_ids)):
        raise AuditError("--task-ids must be a nonempty comma-separated list without duplicates")
    if any(task_id not in tasks for task_id in task_ids):
        raise AuditError("--task-ids includes an unknown task")
    requested = {f"{task_id}-{slot}" for task_id in task_ids for slot in "AB"}
    if not requested <= recorded:
        raise AuditError(f"Import both replies before exporting these tasks. Missing: {', '.join(sorted(requested - recorded))}")
    destination = args.output
    if destination.exists():
        raise AuditError(f"Output already exists: {destination}; choose a new batch folder")
    # Do not place a review export inside raw, prompts, or other assessed folders.
    protected = [root / name for name in ["02_tasks", "03_references", "04_responses", "07_scripts"]]
    if any(destination.resolve().is_relative_to(path.resolve()) for path in protected):
        raise AuditError("Choose a separate batch folder outside the task, reference, response and script source folders")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".blind-batch-", dir=destination.parent))
    rows = []
    mapping = {}
    packet = [
        "# Initial annotation batch\n\n",
        "Read each task and candidate. Make your own ratings, rationale and corrections in annotations.csv. ",
        "Use the verified reference and rubric supplied separately. No ratings are suggested here.\n\n",
        "Keep private_map.json, original response filenames and provenance out of the reviewer's view. ",
        "Recorded model metadata is omitted; candidate wording can still reveal identity. ",
        "Exact UTF-8 candidate files are in responses/.\n\n",
    ]
    try:
        (temporary / "responses").mkdir()
        (temporary / "prompts").mkdir()
        for task_id in task_ids:
            prompt = tasks[task_id]["prompt"]
            (temporary / "prompts" / f"{task_id}.txt").write_bytes(prompt.encode("utf-8"))
            packet.append(f"## Task {task_id}\n\n" + fenced(prompt) + "\n")
            response_ids = [f"{task_id}-A", f"{task_id}-B"]
            secrets.SystemRandom().shuffle(response_ids)
            for response_id in response_ids:
                while True:
                    neutral = "R-" + secrets.token_hex(4).upper()
                    if neutral not in mapping:
                        break
                mapping[neutral] = response_id
                data = (root / expected_paths(response_id)[0]).read_bytes()
                (temporary / "responses" / f"{neutral}.txt").write_bytes(data)
                packet.append(f"### Candidate {neutral}\n\n" + fenced(data.decode("utf-8")) + "\n")
                row = dict.fromkeys(ANNOTATION_FIELDS, "")
                row.update(response_id=neutral, task_id=task_id, round=args.round, rubric_version=args.rubric_version)
                rows.append(row)
        (temporary / "review_packet.md").write_text("".join(packet), encoding="utf-8")
        (temporary / "annotations.csv").write_text(csv_text(rows, ANNOTATION_FIELDS), encoding="utf-8", newline="")
        (temporary / "private_map.json").write_text(json.dumps({
            "warning": "Coordinator only. Do not show this mapping during blind scoring. Preserve it to map submitted labels back without changing originals.",
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "response_mapping": mapping,
        }, indent=2) + "\n", encoding="utf-8")
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary)
        raise
    print(f"Created {destination}: {len(task_ids)} tasks, {len(rows)} candidates, all human annotation fields blank.")
    print("PRIVATE: keep private_map.json and original provenance away from the reviewer. Model identity may remain in candidate wording.")
    print("Validate this batch with --annotations PATH/annotations.csv; its sibling private_map.json is used in memory, without changing submitted annotations.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1], help="Project folder (default: parent of 07_scripts)")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate", help="Check preparation, provenance and annotation structure")
    validate.add_argument("--require-collected", action="store_true", help="Fail unless all prepared replies are recorded and references verified")
    validate.add_argument("--annotations", type=Path, help="Override annotation CSV; a sibling private_map.json enables blind batch validation")
    validate.add_argument("--mapping", type=Path, help="Explicit private blind-ID mapping; rows are mapped only in memory")
    validate.set_defaults(handler=validate_command)
    collect = commands.add_parser("import-response", help="Import a genuine, unedited reply and its actual prompt")
    collect.add_argument("--task-id", required=True)
    collect.add_argument("--slot", choices=["A", "B"], required=True)
    collect.add_argument("--reply", type=Path, required=True)
    collect.add_argument("--actual-prompt", type=Path, required=True)
    collect.add_argument("--model", required=True)
    collect.add_argument("--generated-at", required=True, help="YYYY-MM-DD when only date is known, otherwise an ISO timestamp with timezone")
    collect.add_argument("--source", required=True, help="Actual platform or collection source")
    collect.add_argument("--session-id", required=True, help="Unique ID for this fresh generation/chat; never reuse")
    collect.add_argument("--settings", default="unknown", help="Record known settings, otherwise unknown")
    collect.add_argument("--collector", default="Dominic Da Silva", help="Actual collector; use Codex (AI) for AI collection")
    collect.set_defaults(handler=import_command)
    blind = commands.add_parser("blind-batch", help="Export a small batch with randomly assigned response IDs")
    blind.add_argument("--task-ids", required=True)
    blind.add_argument("--output", type=Path, required=True)
    blind.add_argument("--round", default="pilot_initial")
    blind.add_argument("--rubric-version", default="0.1")
    blind.set_defaults(handler=blind_command)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.root = args.root.resolve()
    try:
        return args.handler(args)
    except (AuditError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
