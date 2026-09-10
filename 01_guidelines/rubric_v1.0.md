# Annotation guidelines v1.0 — AI assisted audit

**Project:** AI Answer Quality Audit: Annotation, Feedback and Correction  
**Prepared:** 10 September 2026  
**Status:** Adopted by Codex (AI) after the 16-response AI pilot. The five scoring anchors are retained. Owner review is pending; this is not a human-agreed rubric or evidence of human annotation.

## 1. What to judge

Judge each candidate response against its task, supplied passage or fictional policy, and the reference you have checked. A reference is evidence to inspect, not an unquestionable answer. Accept equivalent correct reasoning and reasonable alternatives allowed by the task. Do not reward a confident tone, length, or agreement with your preferred wording.

Keep model identity and the other candidate's scores hidden where practical. Judge each response on its own. Read the entire response before deciding: a correct final number does not cancel incorrect reasoning.

## 2. Five independent scores

Use only integer **0, 1, or 2**. A blank means no decision yet, never zero. Score all five dimensions when the evidence permits. No factual claim in a response does not itself lower accuracy; judge omissions under completeness and failures to answer under the relevant dimensions.

| Dimension | 2 | 1 | 0 |
| --- | --- | --- | --- |
| **Accuracy** | Claims, reasoning, calculations and units are correct and supported. Inferences are presented with appropriate certainty. | Some useful content is correct, but there is a localized factual, calculation, unit or unsupported-claim error. | The central conclusion is wrong, or serious errors make the answer substantially unreliable. |
| **Instruction-following** | Meets every explicit applicable requirement, including format, limits and requested method. | Misses a minor requirement while carrying out the main request. | Ignores the main request or violates a central constraint. |
| **Relevance** | Content serves the requested purpose; necessary context is relevant. | Answers the task but contains noticeable unnecessary material or tangents. | Mostly unrelated or fails to address the requested subject. |
| **Completeness** | Includes all information and steps needed for the requested answer. | Omits a secondary requested element or useful supporting detail, while the main answer remains usable. | Omits the main answer or information essential to using it. |
| **Clarity** | Readable, coherent, precise and easy to follow for the intended reader. | Understandable with effort because of avoidable ambiguity, awkward structure or unexplained notation. | Confusing, contradictory or disorganized enough to obscure the meaning. |

**Boundary cases:** A harmless typo can still earn clarity 2. A correct answer with no working loses completeness only if the task asks for working or the reasoning is needed to understand it. Extra explanation is not a relevance error when it helps answer the task. A wrong numerical answer may be perfectly clear. A polished response can still be inaccurate. “Exactly three bullets” is an explicit requirement: four bullets normally merit instruction-following 1 if the requested content is otherwise delivered; missing a crucial scheduling constraint normally merits 0. Justify exceptional cases.

An optional **total out of 10** is simple arithmetic and may be recorded only when all five scores are numeric. There is no pass mark or total-score cutoff for correction. A total cannot establish that a response is factually safe or useful, and is not a basis for model rankings.

## 3. Separate related dimensions

One problem may affect two dimensions, but only when there are two distinct consequences. Explain each effect instead of automatically lowering several scores.

- A missing requested reason affects completeness; it also affects instruction-following if the request explicitly requires that reason. The correct claim itself need not lose accuracy.
- An invented policy affects accuracy. Add instruction-following only if it also breaches an explicit constraint, such as using only the supplied policy.
- A wrong answer to the right question affects accuracy; it is not automatically irrelevant.
- Omitting a limiting condition affects completeness. If the omission turns the statement into a false general claim, accuracy also falls.
- Excess length affects relevance when content is unnecessary, clarity when it obscures meaning, and instruction-following when it violates an explicit limit. Identify which effects actually occur.

Do not count the same defect twice within a dimension. Do not average away a central failure because other sentences are good.

## 4. Error tags and uncertainty

Choose one `primary_error`: the most consequential defect, explained in the rationale. Record other distinct defects in `secondary_errors`, separated by semicolons, for example `missing_content;unclear_expression`. Leave secondary errors blank if absent. Do not repeat the primary tag there. Use `none` as the primary tag when no error is identified, with blank secondary errors.

| Tag | Use for |
| --- | --- |
| `factual_error` | A false claim about the passage, policy, world or reasoning; use a more specific calculation/unit tag when appropriate. |
| `calculation_error` | An arithmetic, algebraic or numerical procedure error. |
| `unit_error` | Incorrect dimensions, conversion, unit label or missing unit essential to interpreting a quantity. |
| `unsupported_claim` | A claim or inference asserted more strongly than the available evidence supports; it need not be proven false. |
| `instruction_violation` | An explicit task requirement is missed or contradicted. |
| `off_topic` | Irrelevant material or failure to address the requested subject. |
| `missing_content` | Necessary or requested information is absent. |
| `unclear_expression` | Wording, notation or organization obscures meaning. |
| `task_ambiguity` | The prompt is defective or leaves materially different interpretations unresolved. |
| `reference_issue` | The reference seems wrong, incomplete or inconsistent with the prompt. |

Task/reference tags describe a dataset problem, not a model failure. Keep them separate from model-error counts in later reporting. A single unit-conversion mistake does not need both `unit_error` and `calculation_error` unless there are distinct mistakes.

Set `uncertainty_flag` to `yes` when you have meaningful doubt about the evidence, interpretation or judgement. Explain exactly what is uncertain and what would resolve it in `uncertainty_note`. Use `no` with a blank note when no meaningful uncertainty remains.

If a defective prompt or key blocks fair judgement, set `annotation_status=needs_clarification`, flag uncertainty, explain the defect and leave affected scores blank. You may record clearly supportable scores provisionally. Do not guess a reference interpretation to finish a row. Otherwise, use `annotation_status=complete` after completing all required decisions. An unresolved row is not a completed annotation.

## 5. Rationale and correction

Record `material_error` as `yes`, `no`, or `uncertain`. A material factual error changes the central answer, meaning, calculation, constraint satisfaction or action a reader would reasonably take. A small numerical or wording difference is material when it changes the decision. Explain this judgement in `rationale`; do not infer it from the total.

Record `correction_required` as:

- **`yes`** when there is a material factual error, or another defect needs fixing to meet the task or make the response usable. **Every `material_error=yes` requires `correction_required=yes`, regardless of total.**
- **`no`** when the response is usable as written and identified imperfections do not require correction. Explain any low score alongside this decision.
- **`deferred`** when unresolved evidence or clarification prevents deciding whether or how to correct. This is a pending decision, not “no correction needed.” Explain the next check.

Write a specific `rationale` identifying the decisive claim, omission or instruction; explain the relevant evidence, dimension effects, materiality and correction decision. “Good answer” or “wrong” alone is insufficient. For a fully satisfactory answer, identify what you checked. Do not mechanically restate five score definitions.

When correction is required and the task is clear, write a complete, usable replacement in `corrected_answer`, following the original instructions. Do not supply only a critique. Keep it blank for `no` or `deferred`; explain deferral in the rationale. If a known material error needs correction but a defective task prevents writing a valid replacement, retain `correction_required=yes`, use `needs_clarification`, leave the replacement blank and explain why.

## 6. Attribution and preservation

For this run, the user explicitly asked AI to complete reference checks and evaluation before the owner reviews them. Record these ratings, error decisions, rationales and corrections as `Codex (AI)`. Do not populate the preserved blank human templates or attribute this work to Dominic. A later owner review is separate, with any prior exposure to AI suggestions disclosed.

The 16 first pilot reviews under v0.1 are frozen unchanged. This version retains the five score anchors, material-error rule and error taxonomy. Reapply it to the pilot and use it for the remaining 64 responses. Keep final-baseline rows and revision reasons separately from the original pilot.

The following clarifications address interpretation and reproducibility; they do not change the pilot's scores:

- An explicitly requested inference can be appropriately qualified by the response's framing as an inference. Judge certainty in context; do not require a particular word such as “may” when the distinction is otherwise clear.
- A minor incidental detail within a requested point does not necessarily create an extra numbered point. Check the requested structure and substantive content together.
- For a word-limited response, count whitespace-separated visible words after ignoring standalone Markdown list markers and numbering. Retain hyphenated words and times as single tokens. Where a separate sentence is requested after a limited summary, apply the summary limit to that summary alone. If an alternative reasonable tokenisation changes a borderline decision, flag that uncertainty instead of treating the count as indisputable.
- Identical replies from independently recorded generations stay in the dataset. Similarity is an observation, not a reason to replace an answer.

No delayed human recheck has occurred. The original 24-hour protocol remains available for future genuine reviews. An immediate AI assessment must not be presented as that recheck or as evidence of independent human consistency.
