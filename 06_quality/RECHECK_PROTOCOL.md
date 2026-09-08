# Planned self-consistency check

Status: **not started**. There are no initial ratings yet. No selection or result is claimed at this checkpoint.

1. Freeze the final rubric and the first complete review of all 80 responses under that rubric. Keep earlier pilot ratings separately. Use this final-rubric first review as the comparison baseline; comparing different rubric versions would mix consistency with guideline changes.
2. Record the actual first-review timestamps. Select the recheck sample at least 24 hours after the project's first review. Also require each selected response's baseline review to be at least 24 hours old before its recheck. Use timezone-aware timestamps and compare elapsed hours, not calendar dates alone.
3. Select 16 responses: four per category. Within each category use a reproducible random sample of four distinct task IDs, then randomly choose one of the two responses per selected task. Record the actual seed, eligible IDs and selection time. Do not select based on correctness or whether a rating changed. Record exclusions before sampling. This gives 16 responses from 16 tasks and reduces duplicated task context.
4. Produce a separate packet with fresh shuffled IDs, the original task and response, and access to the same final reference. Hide earlier ratings, rationales, corrections, coaching and model metadata. Keep the mapping outside the packet. Document any accidental exposure and whether Dominic recalls a case.
5. Dominic completes all 16 fresh reviews independently before comparisons are revealed. Preserve those submissions unchanged with timestamps and rubric version.
6. Compare the two rounds. Dominic explains each changed dimension or correction decision in a separate revision log, identifying oversight, changed interpretation or unresolved uncertainty. Preserve both values even if the later decision is better supported.

## Calculations and denominators

The planned sample is **16 responses × 5 dimensions = 80 paired scores**. This is self-consistency for one reviewer; it is not inter-annotator agreement. Do not claim a second reviewer from AI coaching or code review.

- **Per-dimension exact match:** matching valid score pairs ÷ responses with a valid score in both rounds for that dimension. With complete data, the denominator is 16 for each dimension.
- **Overall exact match:** matching valid dimension pairs ÷ all valid dimension pairs. With complete data the denominator is 80, not 16 or the dataset's 400 scores.
- **Whole-response exact match:** responses with all five scores present and identical ÷ responses with all five paired scores present. With complete data the denominator is 16.
- **Mean absolute change:** sum of `abs(second_score − first_score)` over valid dimension pairs ÷ number of those pairs. This distinguishes one-point from two-point changes.
- **Correction-decision exact match:** identical yes/no decisions ÷ responses with a yes/no decision in both rounds. Report deferred or uncertain cases separately.

Report counts before percentages, for example `matching pairs / valid pairs`, and count excluded/missing pairs explicitly. If no pairs are available, the result is **not available**, never 0% or 100%. Report the 16 sampled responses and any incompleteness; do not quietly substitute a different sample.

The final report will state the actual interval, sampling method, prior rubric revision/coaching, and memory limitations. Do not claim stable personal reliability from this small check.
