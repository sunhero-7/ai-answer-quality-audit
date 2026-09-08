# Teaching examples — outside the assessed dataset

These two invented examples illustrate rubric v0.1. They are not pilot tasks, collected model responses, or portfolio annotation results. Their ratings are teaching suggestions, not answers for any assessed item.

## Example A: a clear and relevant factual error

**Prompt:** “In one sentence, state the colour of Mira's umbrella. Passage: Mira carried a yellow umbrella.”  
**Invented answer:** “Mira's umbrella was blue.”

**Teaching ratings:** accuracy 0; instruction-following 2; relevance 2; completeness 2; clarity 2. Total 8/10.

**Primary error:** `factual_error`. **Secondary errors:** blank. **Uncertainty:** `no`. **Material error:** `yes`. **Correction required:** `yes`. **Annotation status:** `complete`.

**Rationale:** The passage explicitly says yellow; the answer's only factual claim contradicts it. The response otherwise supplies the requested information in a clear, relevant sentence. The central answer is wrong, so correction is required even with a total of 8.

**Corrected answer:** “Mira's umbrella was yellow.”

## Example B: a task that needs clarification

**Prompt:** “Which of the two boxes is heavier? The red box weighs 4 kg.”  
**Invented answer:** “The red box is heavier.”

**Teaching record:** `annotation_status=needs_clarification`; `primary_error=task_ambiguity`; `secondary_errors=unsupported_claim`; `uncertainty_flag=yes`; `material_error=uncertain`; `correction_required=deferred`. Leave all five scores and the total blank in this provisional example.

**Uncertainty note:** “The other box's weight is missing. Request its weight or clarify whether the intended answer should identify insufficient information.”

**Rationale:** The supplied information cannot establish which box is heavier. The candidate's certainty is unsupported, but a missing fact prevents verification of the actual comparison and the prompt's intended expectation. Clarify the task/reference before final scoring. Blank scores represent a deferred decision, not zero. Leave the corrected answer blank until the correction decision is resolved.

These examples show why scores, error tags, uncertainty, and the correction decision answer different questions. Use the checked evidence and rubric for each assessed response; do not copy these ratings as patterns.
