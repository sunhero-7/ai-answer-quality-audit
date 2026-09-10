#!/usr/bin/env python3
"""Cross-check collector observations against preserved provenance.

This verifies consistency of saved records, not vendor authorship or hidden model context.
"""
import argparse
from collections import defaultdict
from datetime import datetime
import json
from pathlib import Path
import sys
import audit


def check(root):
    tasks, refs, verifications, errors, _ = audit.load_preparation(root)
    provenance = audit.read_csv(root / '04_responses/provenance.csv', audit.PROVENANCE_FIELDS)
    problems, recorded = audit.validate_provenance(root, tasks, verifications, provenance)
    errors.extend(problems)
    records = [json.loads(line) for line in (root / '04_responses/agent_capture_log.jsonl').read_text().splitlines() if line.strip()]
    by_id = {row['response_id']: row for row in provenance}
    if len({x['response_id'] for x in records}) != len(records):
        errors.append('Repeated response IDs in capture log')
    if {x['response_id'] for x in records} != set(by_id):
        errors.append('Capture log and provenance do not cover the same responses')
    missing_launch = []
    known_order = []
    same_reply = defaultdict(list)
    for rec in records:
        rid = rec['response_id']; row = by_id.get(rid)
        if row is None:
            continue
        for capture, stored in [('task_id','task_id'),('slot','slot'),('child_task_name','session_id'),('model','model'),('prompt_sha256','prompt_sha256'),('reply_sha256','reply_sha256')]:
            if rec.get(capture) != row.get(stored):
                errors.append(f'{rid}: capture {capture} does not match provenance {stored}')
        capture_time = audit.timestamp(rec['captured_at'])
        if rec['generation_date'] != row['generated_at'] or capture_time.date().isoformat() < rec['generation_date']:
            errors.append(f'{rid}: date records are inconsistent')
        if rec.get('launched_at'):
            launch = audit.timestamp(rec['launched_at'])
            verified = audit.timestamp(verifications[row['task_id']]['verified_at'])
            if launch < verified or capture_time < launch:
                errors.append(f'{rid}: verification, launch and capture timestamps are out of order')
            else:
                known_order.append(rid)
        else:
            missing_launch.append(rid)
        same_reply[row['reply_sha256']].append(rid)
    return {
        'captured_responses': len(records),
        'provenance_records': len(provenance),
        'distinct_recorded_contexts': len({x['session_id'] for x in provenance}),
        'verification_before_observed_launch': len(known_order),
        'launch_timestamp_unrecorded': missing_launch,
        'identical_reply_groups': [ids for ids in same_reply.values() if len(ids) > 1],
        'errors': errors,
        'pass': not errors,
        'limits': [
            'Collector-observed timestamps and identifiers are not independent vendor attestation.',
            'A task-only request does not reveal or verify the hidden system prompt or exact model configuration.',
            'Missing launch times are reported as unknown, never reconstructed as precise timestamps.',
            'Genuine identical responses remain separate observations; no output is regenerated to create diversity.'
        ]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    try:
        report = check(args.root)
    except (OSError, ValueError, KeyError, audit.AuditError) as exc:
        print(f'Capture-log check failed: {exc}', file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report['pass'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
