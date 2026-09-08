# Make your own first decisions

This folder contains blank templates. A preassigned ID, round or rubric version does not mean a response exists or a review has occurred.

Use the four-response batches after collection. First read the task and the verified reference. Then assess one response at a time, giving 0–2 for each dimension. Write your reason and any necessary corrected answer before asking AI for advice. You can submit your answers here, in the workbook, or in CSV.

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
Rubric version: 0.1
```

Your rationale should identify the claim, omission or instruction at issue, point to the calculation or evidence, and explain how it supports your ratings. For an entirely satisfactory response, state what you checked; “looks good” is not enough. Do not change scores to achieve a desired total.

If a verified key appears wrong, flag it. Verification does not make the key infallible. Pause affected judgments, state the uncertainty, and save any still-valid scores. A response that correctly asks for necessary missing information can be fully satisfactory; an ambiguous task does not automatically make its response poor.

## Workbook and CSV

`pilot_annotation_template.xlsx` has two sheets:

- `Scores`: five ratings, total, material error, correction decision and status.
- `Notes`: rationale, corrected answer, error categories, uncertainty, reviewer, timestamp, round and rubric version.

Join them by response ID when exporting. Keep ID, round and version columns intact. The total remains blank until all five scores are numbers. All human decision and text fields start blank, including reviewer and date. Grey cells contain metadata or the calculated total; pale yellow cells are for your inputs.

The single-table `annotations.csv` is the exchange format. CSV exports must preserve commas, line breaks and quotes in your text. Use the coordinator or a proper CSV export, not manual comma-joining. The coordinator calculates the arithmetic total before validating a direct CSV or chat submission; it is not another judgment you need to make. The Python validator checks that a complete row includes the required fields, that totals match and that material errors have corrections. The workbook is not a substitute for validation, and pasting into a workbook can bypass entry controls. Expand row heights as needed to read long rationales and corrected answers.

The initial master template uses planned task/slot IDs. Actual blind batches use neutral response IDs assigned after import. Submit the batch file with its name so the coordinator can apply its saved ID map without exposing model metadata.

## Preserve the record

After a submission, copy it unchanged into `initial/` with the actual submission date and batch ID. The working copy may continue to grow, but the submitted original is never overwritten. AI feedback goes in `06_quality/ai_coaching.csv` only after the corresponding submission. Coaching is advice; any changed decision must be made and explained by Dominic.

After all pilot first decisions are saved, agree on revisions to the guidelines. Save `rubric_v0.2.md` if another draft is needed, then `rubric_v1.0.md` when ready. Reapply v1.0 to the 16 pilot responses and use it for the remaining 64. Keep final rows in `revised/` with a link to the initial record and log both changed and unchanged judgments. Do not overwrite the v0.1 labels or retroactively relabel them as v1.0.

The later blind recheck is a separate round with fresh IDs and earlier labels hidden. It is not the same operation as bringing the pilot onto the final rubric.
