# AI Answer Quality Audit

Annotation, feedback and correction

**AI-produced evaluation. Owner review pending.** 10 September 2026.

Codex (AI) evaluated 80 saved model responses across 40 original tasks. The evaluator marked 0/80 responses (0.0%) for correction and identified material errors in 0/80 (0.0%). The mean score was 10.00/10. These results describe the AI evaluator's decisions on this task set. Dominic's own review is pending.

## Results across four categories

| Category | Responses | Mean / 10 | Material errors | Corrections |
| --- | ---: | ---: | ---: | ---: |
| Mathematics and physics | 20 | 10.00 | 0 | 0 |
| Customer support | 20 | 10.00 | 0 | 0 |
| Reading comprehension | 20 | 10.00 | 0 | 0 |
| Practical reasoning | 20 | 10.00 | 0 | 0 |

## Method

The task set covers mathematics and physics, fictional customer support, original reading passages and practical reasoning, with ten tasks per category. Each task has two separately saved candidate responses. Reference answers were checked by AI before collection.

The capture log records 80 distinct task-only contexts. Reference verification preceded 77 observed launches; launch times for three replies were unrecorded. Exact model and sampling settings were not exposed. Saved-file hashes detect changed bytes, not vendor authorship.

Codex (AI) scored accuracy, instruction following, relevance, completeness and clarity from 0 to 2 under rubric 1.0. The records retain reasons, error tags, uncertainty and correction decisions. A material error requires correction regardless of total. The 16 original pilot reviews were frozen under v0.1 before the documented v1.0 clarification; their scores did not change.

Mean scores out of 2: accuracy 2.00; instruction following 2.00; relevance 2.00; completeness 2.00; clarity 2.00. All denominators are 80.

Validation: the tool suite passed 20 tests using temporary fixtures. These tests check tools and record integrity, not the substantive correctness of AI ratings.

## Feedback and corrections

No primary errors were recorded by the AI evaluator in this sample.

### RC04-A: Who promised to collect the notebook?

The response correctly identifies Noor as the mover, leaves the speaker of the ambiguous pronoun unresolved, and combines the notebook-on-chair fact with the chair's final location in the store cupboard. The AI evaluator scored all five dimensions 2/2.

No correction was required in the recorded AI assessment.

Good evidence discipline includes stating what the passage leaves unresolved.

### CS06-A: Cancellation at the deadline

The response includes exactly Friday 10:00 in the full £48 cancellation-refund window, distinguishes receipt time from later staff reading, asks for the missing booking reference and anchors the payment timeline to processing. The AI evaluator scored all five dimensions 2/2.

No correction was required in the recorded AI assessment.

A correct support answer preserves deadline boundaries and avoids claiming that an unperformed action is complete.

## Limitations

All 80 responses received 10/10, creating a ceiling effect. The assessed sample therefore provides no evidence of correction practice or discrimination between the lower scoring anchors. Perfect AI ratings should not be read as independently verified perfection.

The same AI system family contributed to task preparation, reference checking and evaluation, so shared assumptions or overlooked errors may persist. The sample is small, intentionally varied and not a representative benchmark of general model performance.

No independent human annotations or corrections are claimed. The planned 16-response human blind recheck after at least 24 hours has not been performed. Human self-consistency is unavailable; no second human reviewer or inter-annotator result is claimed.

The completed deliverable is an AI-produced worked audit for owner review. It demonstrates the process and evidence trail, not Dominic's independent annotation ability. No replacement answers were invented where the evaluator found no correction necessary.

## Evidence

[Review all 80 AI annotations](../05_annotations/ai_evaluation.csv), [open the workbook](../05_annotations/ai_evaluation.xlsx), [inspect collection provenance](../04_responses/provenance.csv), and [run the validation tools](../07_scripts/WORKFLOW.md).

Source CSV SHA-256: `0d665ce4b23bb6cadace2e4f411d22e92b187544c1ed94d36b2d6543ca423e3d`.
