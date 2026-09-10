# Collection and review tools

Python 3.10+ is sufficient; both scripts use only the standard library. Run commands from the repository root. Records describe who actually performed the work. AI reference checks, collection and evaluations must identify `Codex (AI)`; they are not Dominic's independent judgments. The original blank human pilot CSV can remain separate from the AI evaluation CSV.

## Validate and collect

```sh
python3 07_scripts/audit.py validate
python3 07_scripts/audit.py import-response --task-id MP01 --slot A \
  --reply /absolute/path/to/genuine-reply.txt \
  --actual-prompt 02_tasks/prompts/MP01.txt \
  --model 'Actual recorded model' --generated-at 'ACTUAL_TIME_WITH_TIMEZONE' \
  --source 'Actual collection source' --session-id 'Actual unique session ID' \
  --collector 'Codex (AI)'
```

Use actual values. Each imported candidate must come from a separate generation that saw the task only. The matching reference must be recorded as verified before collection. The tool checks prompt bytes, saved-response hashes and known timestamp order; it cannot authenticate vendor authorship, model separation, actual human authorship or independence. `--collector` defaults to Dominic for manual collection; AI collection records `source_status=ai_recorded`.

If main task/reference files exist, validation requires 40 unique tasks with ten per category. The original pilot files still require eight tasks with two per category. Every prepared task needs its own verification row; pending rows are allowed. The default 16-row human pilot template remains valid with a full 40-task catalog, and its 16 pending rows do not imply that the full audit is annotated.

## Preserve originals and calculate actual metrics

```sh
python3 07_scripts/completion.py template --round final_baseline \
  --rubric-version ACTUAL_VERSION --output /absolute/path/to/new-blank.csv
python3 07_scripts/audit.py validate --require-collected \
  --annotations 05_annotations/ai_evaluation.csv
python3 07_scripts/completion.py status --annotations 05_annotations/ai_evaluation.csv
python3 07_scripts/completion.py freeze --annotations /absolute/path/to/submitted.csv \
  --output 05_annotations/initial/ACTUAL_NEW_SNAPSHOT_NAME
```

The template command leaves reviewer, ratings, rationale and correction fields blank. `--stage pilot` limits it to the pilot. Do not overwrite the original human template with AI evaluations. Use `--round pilot_initial` for the first pilot evaluation and preserve it before coaching or rubric changes. The status JSON separates AI and human complete-review counts and uses only complete valid records for metrics. No observations means a `null` mean/rate, not zero. Select exactly one round: repeated response IDs are rejected so multiple reviews cannot inflate denominators.

`freeze` accepts complete or explicit needs-clarification submissions, preserves the original CSV bytes and adds a checksum manifest. It refuses an existing destination. A blind batch can be frozen with `--mapping /absolute/path/to/private_map.json`; the mapping is also copied and hashed. No checksum proves that a person made the judgments, and deliberate edits to both data and manifest are outside this tool's protection.

## Document the actual final rubric decision

After the 16 original pilot submissions are frozen, write a decision JSON using actual facts:

```json
{
  "final_rubric_version": "ACTUAL_VERSION",
  "decided_by": "ACTUAL_PERSON_OR_AI_REVIEWER",
  "decided_at": "ACTUAL_TIMESTAMP_WITH_TIMEZONE",
  "decision_rationale": "Explain the actual pilot findings, changes or justified decision to retain the rubric.",
  "rubric_path": "01_guidelines/ACTUAL_RUBRIC_FILE.md",
  "rubric_sha256": "SHA256_OF_THAT_FILE",
  "pilot_snapshots": [
    {"path": "05_annotations/initial/ACTUAL_PILOT_SNAPSHOT", "submitted_sha256": "CHECKSUM_FROM_ITS_MANIFEST"}
  ]
}
```

Multiple pilot snapshots are supported, but together they must identify exactly the 16 original `pilot_initial` reviews. The version is not automatically changed to 1.0. A documented decision can retain 0.1 if that is what actually happened. Review all 80 responses under that final rubric with round `final_baseline`, then freeze the resulting CSV in a new folder.

```sh
python3 07_scripts/completion.py validate-final \
  --baseline 05_annotations/revised/ACTUAL_BASELINE_SNAPSHOT \
  --decision 01_guidelines/ACTUAL_DECISION.json
```

This validates the final baseline only. It does not declare the whole portfolio complete, establish independent human performance or substitute for the delayed recheck and final write-up.

## Optional delayed single-reviewer recheck

A coordinator runs selection at least 24 elapsed hours after the first review. Every eligible baseline must also be at least 24 hours old. Choose a seed before inspecting outcomes and do not reroll to obtain preferred cases.

```sh
python3 07_scripts/completion.py recheck \
  --baseline 05_annotations/revised/ACTUAL_BASELINE_SNAPSHOT \
  --decision 01_guidelines/ACTUAL_DECISION.json \
  --seed ACTUAL_INTEGER_SEED --output /absolute/path/to/new-recheck-folder
```

The output contains `review/` and `PRIVATE/private_map.json`. Give the reviewer only `review/`. Selection uses four distinct eligible tasks per category, then one eligible response per task, producing 16 responses from 16 tasks. The private mapping records seed, eligibility, exclusions, selection time and baseline identity. The packet supplies original task/candidate text, verified reference and final rubric; it omits task IDs, model metadata and previous reviews. Candidate wording may reveal identity, and a reviewer may remember cases. Record accidental exposure or recall in the supplied exposure log.

Preserve all 16 rechecks before revealing comparisons:

```sh
python3 07_scripts/completion.py freeze \
  --annotations /absolute/path/to/new-recheck-folder/review/annotations.csv \
  --mapping /absolute/path/to/new-recheck-folder/PRIVATE/private_map.json \
  --output 05_annotations/recheck/ACTUAL_NEW_SNAPSHOT
python3 07_scripts/completion.py compare-recheck \
  --baseline 05_annotations/revised/ACTUAL_BASELINE_SNAPSHOT \
  --decision 01_guidelines/ACTUAL_DECISION.json \
  --mapping /absolute/path/to/new-recheck-folder/PRIVATE/private_map.json \
  --recheck 05_annotations/recheck/ACTUAL_NEW_SNAPSHOT
```

The same recorded reviewer and final rubric are required in both rounds. Comparison reports exact counts and denominators: at most 80 paired dimensions, 16 paired responses and 16 correction decisions. Missing pairs are excluded and counted. Changed values are reported with an empty explanation for the reviewer to supply separately. This is a small self-consistency check; it is not evidence from a second reviewer. A 24-hour human recheck that has not happened must remain explicitly unperformed.

## Tool tests

```sh
python3 -m unittest discover -s 07_scripts -p 'test*.py' -v
```

All synthetic fixtures live in temporary directories and are never assessed dataset records.
