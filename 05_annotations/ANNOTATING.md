# Review the annotations and preserve later judgments

**Current AI run:** the completed AI records belong in `ai_evaluation.csv` and `ai_evaluation.xlsx`, with reviewer `Codex (AI)`. The original blank files described below are preserved for a later human exercise. If you have seen AI ratings or corrections, disclose that exposure; a later review of those answers is not a blind independent first annotation. See the method-change record and final rubric.

This folder contains completed AI evaluations alongside the original blank human templates. A preassigned ID, round or rubric version in a template does not mean a human review has occurred.

For a later owner review, inspect a small batch at a time against the task and AI-checked reference. Use the final rubric v1.0, record your own reasoning and disclose prior exposure to AI judgments. Save a new dated review file; do not overwrite the completed AI file or relabel the old blank v0.1 template as a submitted review. For a genuinely unassisted first exercise, use fresh responses whose proposed ratings you have not seen.

## Copyable submission form

```text
Response ID:
Accuracy:
Instruction-following:
Relevance:
Completeness:
Clarity:
Status: complete / needs_clarification
Primary error:
Secondary errors, if any:
Uncertainty: yes / no
Uncertainty note, if yes:
Material factual error: yes / no / uncertain
Correction required: yes / no / deferred
Rationale:
Corrected answer, if required:
Reviewer:
Review date and time, with timezone:
Rubric version: 1.0
```

Your rationale should identify the claim, omission or instruction at issue, point to the calculation or evidence, and explain how it supports your ratings. For an entirely satisfactory response, state what you checked; “looks good” is not enough. Do not change scores to achieve a desired total.

If a verified key appears wrong, flag it. Verification does not make the key infallible. Pause affected judgments, state the uncertainty, and save any still-valid scores. A response that correctly asks for necessary missing information can be fully satisfactory; an ambiguous task does not automatically make its response poor.

## Preserved original human workbook and CSV

`pilot_annotation_template.xlsx` has two sheets:

- `Scores`: five ratings, total, material error, correction decision and status.
- `Notes`: rationale, corrected answer, error categories, uncertainty, reviewer, timestamp, round and rubric version.

Join them by response ID when exporting. Keep ID, round and version columns intact. The total remains blank until all five scores are numbers. All human decision and text fields start blank, including reviewer and date. Grey cells contain metadata or the calculated total; pale yellow cells are for your inputs.

The single-table `annotations.csv` is the exchange format. CSV exports must preserve commas, line breaks and quotes in your text. Use the coordinator or a proper CSV export, not manual comma-joining. The coordinator calculates the arithmetic total before validating a direct CSV or chat submission; it is not another judgment you need to make. The Python validator checks that a complete row includes the required fields, that totals match and that material errors have corrections. The workbook is not a substitute for validation, and pasting into a workbook can bypass entry controls. Expand row heights as needed to read long rationales and corrected answers.

The initial master template uses planned task/slot IDs. Actual blind batches use neutral response IDs assigned after import. Submit the batch file with its name so the coordinator can apply its saved ID map without exposing model metadata.

## Preserve the record

After a submission, copy it unchanged into `initial/` with the actual submission date and batch ID. The working copy may continue to grow, but the submitted original is never overwritten. AI feedback goes in `06_quality/ai_coaching.csv` only after the corresponding submission. Coaching is advice; any changed decision must be made and explained by Dominic.

For the completed AI run, v1.0 was adopted after the 16 original pilot decisions were frozen. It was then applied to all 80 responses; the pilot scores were unchanged. The decision record and revision log explain the clarifications. The initial pilot snapshot is in `initial/ai_pilot_2026-09-10/`, and the final baseline is in `revised/ai_baseline_2026-09-10/`. These are AI decisions, not a human-agreed rubric or human submission. Preserve these originals when adding any later owner review.

The later blind recheck is a separate round with fresh IDs and earlier labels hidden. It is not the same operation as bringing the pilot onto the final rubric.
