#!/usr/bin/env python3
"""Preserve submitted reviews and measure the audit without inventing results.

Commands: freeze, status, validate-final, recheck, compare-recheck.
Run with --help or COMMAND --help. All times require an explicit UTC offset.
Checksums detect changed bytes; they cannot certify authorship or independence.
Use a coordinator to prepare blind packets. PRIVATE/ must stay out of the
reviewer's view until the recheck is submitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import random
import secrets
import shutil
import sys
import tempfile

import audit


def now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def read_object(path):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise audit.AuditError(f"Cannot read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise audit.AuditError(f"{path}: expected a JSON object")
    return value


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def require_no_errors(errors):
    if errors:
        raise audit.AuditError("\n".join(errors))


def context(root):
    tasks, refs, verification, errors, verified = audit.load_preparation(root)
    provenance = audit.read_csv(root / "04_responses/provenance.csv", audit.PROVENANCE_FIELDS)
    problems, recorded = audit.validate_provenance(root, tasks, verification, provenance)
    require_no_errors(errors + problems)
    return tasks, refs, provenance, recorded, verified


def submitted_rows(root, path, mapping=None):
    tasks, _refs, _provenance, recorded, _verified = context(root)
    rows = audit.read_csv(path, audit.ANNOTATION_FIELDS)
    if mapping:
        rows, expected = audit.map_blind_annotations(rows, mapping)
    else:
        expected = {row["response_id"] for row in rows}
    errors, _counts = audit.validate_annotations(rows, tasks, recorded, expected)
    if not rows or len(expected) != len(rows):
        errors.append("A submission must contain one row per response and cannot be empty")
    for row in rows:
        if row["annotation_status"] not in {"complete", "needs_clarification"}:
            errors.append(f"{row['response_id']}: submit a complete review or explicit needs_clarification")
        try:
            if audit.timestamp(row["reviewed_at"]) > now():
                errors.append(f"{row['response_id']}: reviewed_at is in the future")
        except ValueError:
            pass  # Detailed error is already supplied by annotation validation.
    require_no_errors(errors)
    return rows


def publish_directory(destination, populate):
    """Build a new directory beside its destination, never replace a submission."""
    if destination.exists():
        raise audit.AuditError(f"Output already exists: {destination}; originals will not be overwritten")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=".audit-", dir=destination.parent))
    try:
        populate(temporary)
        if destination.exists():
            raise audit.AuditError("Destination appeared during preparation; choose a new path")
        temporary.rename(destination)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def freeze_command(args):
    mapping = args.mapping
    if mapping is None and (args.annotations.parent / "private_map.json").is_file():
        mapping = args.annotations.parent / "private_map.json"
    rows = submitted_rows(args.root, args.annotations, mapping)
    data = args.annotations.read_bytes()
    mapping_data = mapping.read_bytes() if mapping else None
    manifest = {
        "frozen_at": now().isoformat(), "submitted_sha256": audit.digest(data),
        "row_count": len(rows), "rounds": sorted({r["round"] for r in rows}),
        "rubric_versions": sorted({r["rubric_version"] for r in rows}),
        "mapping_sha256": audit.digest(mapping_data) if mapping_data else None,
        "notice": "Original submitted bytes. This records submission, not independent proof of human authorship.",
    }
    def populate(folder):
        (folder / "submitted.csv").write_bytes(data)
        if mapping_data:
            (folder / "private_map.json").write_bytes(mapping_data)
        (folder / "manifest.json").write_text(json_text(manifest), encoding="utf-8")
    publish_directory(args.output, populate)
    print(f"Preserved {len(rows)} submitted rows in {args.output}; no original overwritten.")
    return 0


def snapshot(root, folder):
    manifest = read_object(folder / "manifest.json")
    csv_path = folder / "submitted.csv"
    if audit.digest(csv_path.read_bytes()) != manifest.get("submitted_sha256"):
        raise audit.AuditError(f"Snapshot CSV changed: {folder}")
    mapping = None
    if manifest.get("mapping_sha256"):
        mapping = folder / "private_map.json"
        if audit.digest(mapping.read_bytes()) != manifest["mapping_sha256"]:
            raise audit.AuditError(f"Snapshot mapping changed: {folder}")
    elif (folder / "private_map.json").exists():
        raise audit.AuditError(f"Unrecorded snapshot mapping: {folder}")
    rows = submitted_rows(root, csv_path, mapping)
    if len(rows) != manifest.get("row_count"):
        raise audit.AuditError(f"Snapshot row count changed: {folder}")
    frozen_at = audit.timestamp(manifest.get("frozen_at", ""))
    if frozen_at > now() or any(audit.timestamp(row["reviewed_at"]) > frozen_at for row in rows):
        raise audit.AuditError(f"Snapshot times are out of order: {folder}")
    return rows, manifest


def final_baseline(root, baseline_folder, decision_path):
    tasks, refs, provenance, recorded, verified = context(root)
    if len(tasks) != 40 or len(recorded) != 80 or verified != 40:
        raise audit.AuditError(f"Final audit needs 40 verified tasks and 80 collected responses; recorded {verified} verified and {len(recorded)} responses")
    decision = read_object(decision_path)
    for field in ["final_rubric_version", "decided_by", "decided_at", "decision_rationale", "rubric_path", "rubric_sha256"]:
        if not isinstance(decision.get(field), str) or not decision[field].strip():
            raise audit.AuditError(f"Rubric decision requires {field}; record the actual pilot decision")
    decided_at = audit.timestamp(decision["decided_at"])
    if decided_at > now():
        raise audit.AuditError("Rubric decision timestamp is in the future")
    rubric_path = (root / decision["rubric_path"]).resolve()
    if not rubric_path.is_relative_to(root.resolve()) or audit.digest(rubric_path.read_bytes()) != decision["rubric_sha256"]:
        raise audit.AuditError("Documented final rubric path/hash does not match its saved bytes")
    pilot_records = decision.get("pilot_snapshots")
    if not isinstance(pilot_records, list) or not pilot_records:
        raise audit.AuditError("Rubric decision needs pilot_snapshots containing the original 16 pilot submissions")
    pilot_rows = []
    for entry in pilot_records:
        if not isinstance(entry, dict) or not entry.get("path") or not entry.get("submitted_sha256"):
            raise audit.AuditError("Each pilot snapshot needs path and submitted_sha256")
        rows, manifest = snapshot(root, root / entry["path"])
        if manifest["submitted_sha256"] != entry["submitted_sha256"]:
            raise audit.AuditError("Rubric decision pilot snapshot checksum differs")
        if audit.timestamp(manifest["frozen_at"]) > decided_at:
            raise audit.AuditError("Pilot originals must be frozen before the rubric decision")
        pilot_rows.extend(rows)
    pilot_ids = {f"{task_id}-{slot}" for task_id, task in tasks.items() if task["stage"] == "pilot" for slot in "AB"}
    if len(pilot_rows) != 16 or {row["response_id"] for row in pilot_rows} != pilot_ids or any(row["round"] != "pilot_initial" for row in pilot_rows):
        raise audit.AuditError("Rubric decision must cite exactly the 16 original pilot_initial reviews")
    baseline, manifest = snapshot(root, baseline_folder)
    expected = {f"{task_id}-{slot}" for task_id in tasks for slot in "AB"}
    if len(baseline) != 80 or {row["response_id"] for row in baseline} != expected:
        raise audit.AuditError("Final baseline must contain exactly one review for each of the 80 responses")
    for row in baseline:
        if row["round"] != "final_baseline" or row["rubric_version"] != decision["final_rubric_version"] or row["annotation_status"] != "complete":
            raise audit.AuditError(f"{row['response_id']}: requires complete final_baseline review under documented final rubric")
        if audit.timestamp(row["reviewed_at"]) < decided_at:
            raise audit.AuditError(f"{row['response_id']}: final baseline review predates final rubric decision")
    first_review = min(audit.timestamp(row["reviewed_at"]) for row in pilot_rows + baseline)
    return tasks, refs, baseline, manifest, decision, first_review


def ratio(numerator, denominator):
    return {"numerator": numerator, "denominator": denominator,
            "fraction": numerator / denominator if denominator else None}


def metrics(rows):
    """Use each observed complete, valid record once; no blank-to-zero conversion."""
    complete = [r for r in rows if r["annotation_status"] == "complete" and not audit.annotation_errors(r, r["response_id"])]
    result = {"complete_valid_responses": len(complete), "score_dimensions": {}}
    for field in audit.SCORES:
        values = [int(row[field]) for row in complete if row[field] in {"0", "1", "2"}]
        result["score_dimensions"][field] = {"observations": len(values), "mean": sum(values) / len(values) if values else None}
    result["material_error_rate"] = ratio(sum(r["material_error"] == "yes" for r in complete), sum(r["material_error"] in {"yes", "no"} for r in complete))
    result["correction_required_rate"] = ratio(sum(r["correction_required"] == "yes" for r in complete), sum(r["correction_required"] in {"yes", "no"} for r in complete))
    result["primary_error_counts"] = dict(Counter(r["primary_error"] for r in complete))
    return result


def status_command(args):
    tasks, _refs, provenance, recorded, verified = context(args.root)
    path = args.annotations or args.root / "05_annotations/annotations.csv"
    rows = audit.read_csv(path, audit.ANNOTATION_FIELDS)
    expected = None
    if args.annotations is None and len(tasks) == 40 and len(rows) == 16:
        expected = {f"{task_id}-{slot}" for task_id, task in tasks.items() if task["stage"] == "pilot" for slot in "AB"}
    errors, counts = audit.validate_annotations(rows, tasks, recorded, expected)
    if len({r["response_id"] for r in rows}) != len(rows):
        errors.append("Status needs one review per response; select one round before calculating metrics")
    require_no_errors(errors)
    report = {"generated_at": now().isoformat(), "project_status": "in_progress", "prepared_tasks": len(tasks),
              "planned_responses": len(tasks) * 2, "verified_references": verified,
              "collected_responses": len(recorded), "annotation_status_counts": dict(counts),
              "metrics": metrics(rows),
              "reviewer_complete_counts": dict(Counter(r["reviewer"] for r in rows if r["annotation_status"] == "complete")),
              "ai_complete_reviews": sum(r["annotation_status"] == "complete" and "(AI)" in r["reviewer"] for r in rows),
              "human_complete_reviews": sum(r["annotation_status"] == "complete" and "(AI)" not in r["reviewer"] for r in rows),
              "collection_source_counts": dict(Counter(r["source_status"] for r in provenance)),
              "limitations": ["Collection provenance is collector-recorded, not independently authenticated.",
                              "This status command does not certify project completion or human authorship.",
                              "Metrics include only complete valid rows; blanks and unresolved rows are excluded."]}
    print(json_text(report), end="")
    return 0


def validate_final_command(args):
    _tasks, _refs, baseline, _manifest, decision, _first = final_baseline(args.root, args.baseline, args.decision)
    print(f"Final baseline structurally valid: {len(baseline)}/80 complete, rubric {decision['final_rubric_version']}.")
    print("The delayed independent recheck, change explanations, report and walkthrough remain separate completion requirements.")
    return 0


def recheck_command(args):
    tasks, refs, baseline, manifest, decision, first_review = final_baseline(args.root, args.baseline, args.decision)
    selected_at = now()
    if selected_at - first_review < timedelta(hours=24):
        raise audit.AuditError("Wait at least 24 hours after the first review before selecting a recheck")
    eligible = {row["response_id"]: row for row in baseline if selected_at - audit.timestamp(row["reviewed_at"]) >= timedelta(hours=24)}
    rng = random.Random(args.seed)
    selected = []
    eligibility = {}
    for category in sorted(audit.CATEGORIES):
        by_task = {task_id: sorted(rid for rid in eligible if eligible[rid]["task_id"] == task_id)
                   for task_id, task in tasks.items() if task["category"] == category}
        by_task = {task_id: ids for task_id, ids in sorted(by_task.items()) if ids}
        eligibility[category] = by_task
        if len(by_task) < 4:
            raise audit.AuditError(f"{category}: need 4 distinct tasks with baseline reviews at least 24 hours old; currently {len(by_task)}")
        selected.extend(rng.choice(by_task[task_id]) for task_id in rng.sample(sorted(by_task), 4))
    rng.shuffle(selected)
    mapping = {f"R-{index:02d}-{secrets.token_hex(3).upper()}": response_id for index, response_id in enumerate(selected, 1)}
    private = {"response_mapping": mapping, "selected_at": selected_at.isoformat(), "first_review_at": first_review.isoformat(),
               "seed": args.seed, "eligible_by_category": eligibility, "baseline_submitted_sha256": manifest["submitted_sha256"],
               "final_rubric_version": decision["final_rubric_version"],
               "baseline_reviewed_at": {rid: eligible[rid]["reviewed_at"] for rid in selected},
               "exclusions": {row["response_id"]: "baseline less than 24 hours old" for row in baseline if row["response_id"] not in eligible}}
    def populate(folder):
        review = folder / "review"
        (review / "responses").mkdir(parents=True)
        (folder / "PRIVATE").mkdir()
        (folder / "PRIVATE/private_map.json").write_text(json_text(private), encoding="utf-8")
        packet = ["# Blind self-consistency recheck\n\nComplete all 16 reviews before opening comparisons or PRIVATE/. Use the same final rubric. Record any remembered case or accidental exposure separately; wording may reveal its source. Task and model identifiers, earlier scores, rationales and corrections are omitted.\n\n"]
        annotations = []
        for neutral, response_id in mapping.items():
            task_id = eligible[response_id]["task_id"]
            reply = (args.root / audit.expected_paths(response_id)[0]).read_bytes()
            (review / "responses" / f"{neutral}.txt").write_bytes(reply)
            packet.append(f"## {neutral}\n\n### Task\n\n" + audit.fenced(tasks[task_id]["prompt"]) + "\n### Candidate\n\n" + audit.fenced(reply.decode("utf-8")))
            packet.append("\n### Verified reference\n\n" + audit.fenced(refs[task_id]["expected_answer"]) + "\n" + "\n".join("- " + item for item in refs[task_id]["checklist"]) + "\n\n")
            packet.append("### Reference evidence and ambiguity notes\n\n" + "\n".join("- " + item for item in refs[task_id]["evidence"]) + "\n\n" + refs[task_id]["ambiguity_notes"] + "\n\n")
            row = dict.fromkeys(audit.ANNOTATION_FIELDS, "")
            row.update(response_id=neutral, round="blind_recheck", rubric_version=decision["final_rubric_version"])
            annotations.append(row)
        (review / "review_packet.md").write_text("".join(packet), encoding="utf-8")
        (review / "annotations.csv").write_text(audit.csv_text(annotations, audit.ANNOTATION_FIELDS), encoding="utf-8", newline="")
        (review / "final_rubric.md").write_bytes((args.root / decision["rubric_path"]).read_bytes())
        (review / "exposure_log.csv").write_text("response_id,recall_or_exposure,recorded_at,notes\n", encoding="utf-8")
    publish_directory(args.output, populate)
    print(f"Created {args.output / 'review'} with 16 candidates from 16 tasks, four per category.")
    print(f"Coordinator only: {args.output / 'PRIVATE/private_map.json'}. Do not publish or expose before all rechecks are submitted.")
    return 0


def paired_metrics(baseline, recheck):
    old = {r["response_id"]: r for r in baseline}
    if len(old) != len(baseline) or len({r["response_id"] for r in recheck}) != len(recheck):
        raise audit.AuditError("Comparison requires unique response IDs in each round")
    if any(r["response_id"] not in old for r in recheck):
        raise audit.AuditError("Recheck contains a response absent from baseline")
    dimensions = {}
    changes = []
    all_matches = all_pairs = whole_matches = whole_pairs = decision_matches = decision_pairs = total_change = 0
    for field in audit.SCORES:
        pairs = [(int(old[r["response_id"]][field]), int(r[field])) for r in recheck
                 if old[r["response_id"]][field] in {"0", "1", "2"} and r[field] in {"0", "1", "2"}]
        matches = sum(a == b for a, b in pairs)
        dimensions[field] = {**ratio(matches, len(pairs)), "excluded_pairs": len(recheck) - len(pairs)}
        all_matches += matches
        all_pairs += len(pairs)
        total_change += sum(abs(a - b) for a, b in pairs)
    for row in recheck:
        before = old[row["response_id"]]
        if all(before[f] in {"0", "1", "2"} and row[f] in {"0", "1", "2"} for f in audit.SCORES):
            whole_pairs += 1
            whole_matches += all(before[f] == row[f] for f in audit.SCORES)
        if before["correction_required"] in {"yes", "no"} and row["correction_required"] in {"yes", "no"}:
            decision_pairs += 1
            decision_matches += before["correction_required"] == row["correction_required"]
        for field in audit.SCORES + ["correction_required"]:
            if before[field] != row[field]:
                changes.append({"response_id": row["response_id"], "field": field, "baseline": before[field], "recheck": row[field], "explanation": None})
    return {"measure": "single-reviewer self-consistency", "sampled_responses": len(recheck), "per_dimension_exact_match": dimensions,
            "overall_exact_match": {**ratio(all_matches, all_pairs), "excluded_pairs": len(recheck) * 5 - all_pairs},
            "whole_response_exact_match": ratio(whole_matches, whole_pairs),
            "mean_absolute_change": {"sum_absolute_change": total_change, "denominator": all_pairs, "mean": total_change / all_pairs if all_pairs else None},
            "correction_decision_exact_match": {**ratio(decision_matches, decision_pairs), "excluded_pairs": len(recheck) - decision_pairs},
            "changes_needing_human_explanation": changes}


def compare_command(args):
    _tasks, _refs, baseline, manifest, decision, first_review = final_baseline(args.root, args.baseline, args.decision)
    mapping = read_object(args.mapping)
    if mapping.get("baseline_submitted_sha256") != manifest["submitted_sha256"] or mapping.get("final_rubric_version") != decision["final_rubric_version"]:
        raise audit.AuditError("Recheck mapping does not identify this frozen baseline and final rubric")
    recheck, recheck_manifest = snapshot(args.root, args.recheck)
    if audit.digest(args.mapping.read_bytes()) != recheck_manifest.get("mapping_sha256"):
        raise audit.AuditError("Comparison mapping must match the mapping frozen with the recheck submission")
    selection = mapping.get("response_mapping", {})
    if not isinstance(selection, dict) or len(selection) != 16 or len(set(selection.values())) != 16 or {r["response_id"] for r in recheck} != set(selection.values()):
        raise audit.AuditError("Recheck must preserve all 16 selected responses without replacements")
    selected_tasks = [row["task_id"] for row in recheck]
    categories = Counter(_tasks[task_id]["category"] for task_id in selected_tasks)
    if len(set(selected_tasks)) != 16 or set(categories) != audit.CATEGORIES or set(categories.values()) != {4}:
        raise audit.AuditError("Recheck needs 16 distinct tasks and exactly four per category")
    selected_at = audit.timestamp(mapping.get("selected_at", ""))
    if selected_at - first_review < timedelta(hours=24):
        raise audit.AuditError("Sample was selected less than 24 hours after the first review")
    previous = {r["response_id"]: r for r in baseline}
    for row in recheck:
        if row["round"] != "blind_recheck" or row["rubric_version"] != decision["final_rubric_version"]:
            raise audit.AuditError("Recheck must use blind_recheck round and the same final rubric")
        if row["reviewer"] != previous[row["response_id"]]["reviewer"]:
            raise audit.AuditError("Self-consistency requires the same recorded reviewer in both rounds")
        reviewed_at = audit.timestamp(row["reviewed_at"])
        baseline_at = audit.timestamp(previous[row["response_id"]]["reviewed_at"])
        if reviewed_at < selected_at or selected_at - baseline_at < timedelta(hours=24) or reviewed_at - baseline_at < timedelta(hours=24):
            raise audit.AuditError(f"{row['response_id']}: recheck or selection timing violates the 24-hour protocol")
    report = paired_metrics(baseline, recheck)
    report["incomplete_reviews"] = sum(r["annotation_status"] != "complete" for r in recheck)
    report["limitations"] = ["Small single-reviewer sample; memory and prior coaching can affect results.", "Original and recheck judgments are preserved; changed decisions need the reviewer's own explanation."]
    print(json_text(report), end="")
    return 0


def template_command(args):
    tasks, _refs, _verification, errors, _verified = audit.load_preparation(args.root)
    require_no_errors(errors)
    if not args.round.strip() or not args.rubric_version.strip():
        raise audit.AuditError("Provide the actual round and rubric version")
    rows = []
    for task_id, task in tasks.items():
        if args.stage == "pilot" and task["stage"] != "pilot":
            continue
        for slot in "AB":
            row = dict.fromkeys(audit.ANNOTATION_FIELDS, "")
            row.update(response_id=f"{task_id}-{slot}", task_id=task_id, round=args.round, rubric_version=args.rubric_version)
            rows.append(row)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with args.output.open("x", encoding="utf-8", newline="") as handle:
            handle.write(audit.csv_text(rows, audit.ANNOTATION_FIELDS))
    except FileExistsError as exc:
        raise audit.AuditError("Template output already exists; originals will not be overwritten") from exc
    print(f"Created {len(rows)} blank review rows at {args.output}; no ratings or reviewer identity supplied.")
    return 0


def parser():
    result = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    result.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = result.add_subparsers(dest="command", required=True)
    template = commands.add_parser("template", help="Create a blank review CSV with explicit round and rubric version")
    template.add_argument("--round", required=True)
    template.add_argument("--rubric-version", required=True)
    template.add_argument("--stage", choices=["pilot", "all"], default="all")
    template.add_argument("--output", type=Path, required=True)
    template.set_defaults(handler=template_command)
    freeze = commands.add_parser("freeze", help="Preserve submitted CSV bytes in a new snapshot directory")
    freeze.add_argument("--annotations", type=Path, required=True)
    freeze.add_argument("--mapping", type=Path)
    freeze.add_argument("--output", type=Path, required=True)
    freeze.set_defaults(handler=freeze_command)
    status = commands.add_parser("status", help="Print actual counts and null-safe metrics as JSON")
    status.add_argument("--annotations", type=Path)
    status.set_defaults(handler=status_command)
    for name, handler in [("validate-final", validate_final_command), ("recheck", recheck_command), ("compare-recheck", compare_command)]:
        command = commands.add_parser(name)
        command.add_argument("--baseline", type=Path, required=True, help="Frozen snapshot directory of all 80 final_baseline reviews")
        command.add_argument("--decision", type=Path, required=True, help="Documented actual final rubric decision JSON")
        command.set_defaults(handler=handler)
        if name == "recheck":
            command.add_argument("--seed", type=int, required=True, help="Choose and record before selection; do not reroll based on ratings")
            command.add_argument("--output", type=Path, required=True)
        if name == "compare-recheck":
            command.add_argument("--mapping", type=Path, required=True, help="Coordinator's PRIVATE/private_map.json from selection")
            command.add_argument("--recheck", type=Path, required=True, help="Frozen snapshot of the 16 submitted rechecks")
    return result


def main(argv=None):
    args = parser().parse_args(argv)
    args.root = args.root.resolve()
    try:
        return args.handler(args)
    except (audit.AuditError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
