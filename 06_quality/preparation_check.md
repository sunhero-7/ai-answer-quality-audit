# Preparation quality check

Status: technical preparation checked; human evaluation not started.

- Eight unique task IDs and matching reference IDs; exactly two in each named category.
- Eight prompt files match task JSON byte for byte. No reference key or rubric is appended.
- Review document contains the same prompts, expected answers and checklists as the JSON records.
- Sixteen unique planned annotation slots; every human score, decision, explanation, correction, reviewer and timestamp remains blank.
- Zero raw candidate responses and zero provenance records; all eight human reference decisions remain blank.
- Workbook has two sheets with matching IDs, score/decision input validation, blank-aware totals and frozen headers/IDs. Inspected saved XML for blank inputs, cached blank totals, controls and panes.
- Rendered both workbook sheets and inspected score, decision and written-review regions. No clipped populated content or formula errors observed.
- Tested the total formula using synthetic values in a separate scratch workbook: missing inputs remain blank, five zero ratings total zero, and mixed values sum correctly. No synthetic ratings were written into assessed rows.
- AI reference checks verified arithmetic and schedule feasibility. An RC02 wording mismatch was corrected in the draft key before human verification; the revision log records it.

These checks were performed by Codex. They do not constitute Dominic's reference verification, human annotation, a second reviewer, authenticity verification of external model outputs, or native Excel application testing.

The import and validation tool passed 13 tests using temporary synthetic fixtures outside the assessed dataset. Tests exercised reference gating and completeness, category balance, exact-byte preservation, duplicate prevention, timestamp ordering, score and correction constraints, and blind batch ID mapping. The separate collection-required check correctly reported that replies and verification are still missing. See `validation_2026-09-08.txt` for the saved real preparation check.
