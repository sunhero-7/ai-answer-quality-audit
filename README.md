# AI Answer Quality Audit

**WORK IN PROGRESS — AI audit complete; owner review pending**  
Independent portfolio project owned by **Dominic Da Silva**  
Started 8 September 2026 · Updated 10 September 2026 · Original target 15 September 2026

An inspectable evaluation project covering **40 tasks and 80 model responses** in mathematics and physics, fictional customer support, original reading comprehension and practical reasoning. The repository preserves the prompts, replies, reference evidence, scoring decisions, corrections when needed, and checking tools.

**The current evaluation is AI-produced. Dominic has not independently checked the keys or annotated the responses.** On 10 September, Dominic asked AI to complete the work for his later review. The [method-change record](00_plan/METHOD_CHANGE_2026-09-10.md) explains this change from the original human-first plan. No human hours or completed delayed human recheck are claimed.

## Review the work

Start with the [owner review guide](START_HERE.md). The [checkpoint](CHECKPOINT.md) records current status and outstanding work.

| Activity | Recorded | Scope |
|---|---:|---:|
| Original tasks and reference checklists | 40 |40|
| Reference checks by AI | 40 |40|
| References independently verified by Dominic |0|40|
| Genuine separate candidate responses saved |80|80|
| AI pilot reviews preserved |16|16|
| AI evaluations under the final rubric |80|80|
| Independent initial annotations by Dominic |0|80|
| Delayed human blind rechecks |0|16|

Blank human template rows are placeholders, not collected responses or completed reviews. The target date and original 15-hour estimate are plans, not actual work records.

## Repository contents

- [Task catalogue](02_tasks/CATALOGUE.md), [pilot tasks](02_tasks/pilot_tasks.json) and [remaining tasks](02_tasks/main_tasks.json).
- [Pilot reference review](03_references/pilot_reference_review.md), [remaining reference review](03_references/main_reference_review.md) and [attributed verification record](03_references/reference_verification.csv).
- [Unedited candidate replies](04_responses/raw/), [actual task prompts](04_responses/prompts/), [provenance](04_responses/provenance.csv) and [agent capture log](04_responses/agent_capture_log.jsonl).
- [Original pilot rubric](01_guidelines/rubric_v0.1.md), [annotation guide](05_annotations/ANNOTATING.md) and [collection method](04_responses/COLLECT_RESPONSES.md).
- [Human pilot workbook](05_annotations/pilot_annotation_template.xlsx), [blank human annotation CSV](05_annotations/annotations.csv) and [blank human reference form](03_references/human_reference_verification.csv).
- [Python workflow](07_scripts/WORKFLOW.md), [recheck protocol](06_quality/RECHECK_PROTOCOL.md), [QA log](06_quality/qa_log.csv) and [revision log](06_quality/revision_log.csv).
- [AI assistance log](00_plan/ai_assistance_log.csv), [actual progress log](00_plan/progress_log.csv) and [original week plan](00_plan/WEEK_PLAN.md).

## AI evaluation results

Read the [two-page report](08_portfolio/AI_AUDIT_REPORT.pdf), [editable report](08_portfolio/AI_AUDIT_REPORT.docx), [GitHub report text](08_portfolio/AI_AUDIT_REPORT.md), [annotated workbook](05_annotations/ai_evaluation.xlsx) or [CSV](05_annotations/ai_evaluation.csv). The [metrics JSON](06_quality/ai_metrics.json) makes the denominators inspectable. The [walkthrough outline](08_portfolio/WALKTHROUGH_OUTLINE.md) is written for an honest presentation of AI assistance.

The AI evaluator assigned all 80 replies 10/10 and identified no corrections as necessary. This ceiling effect limits what the run demonstrates about correction practice and distinctions between score levels.

These are AI judgments on this dataset. Human accuracy, human annotation consistency and general model performance cannot be inferred from them.

## Method and limits

Each task has two genuine separately generated answers. Every candidate was requested in a new agent context containing only its clean task, with no reference key, rubric or counterpart response. The collector retained the first complete final answer without editing or selecting for errors. Exact underlying model identifiers and sampling settings were not exposed, so the records say so. No comparison between different models is claimed.

AI checked the keys before generation and evaluated each response on five 0–2 dimensions: accuracy, instruction-following, relevance, completeness and clarity. A material factual error requires correction regardless of the total. The first 16 pilot decisions are kept separately from the final-rubric baseline. A score total has no pass/fail threshold.

The same AI system family may influence task design, reference checks, generation and assessment. This can conceal shared errors and produce an optimistic assessment. A small, deliberately selected sample does not estimate general performance. Saved-file hashes detect changes to captured bytes; they do not independently prove vendor authorship or correct capture.

The originally planned 24-hour human recheck has not occurred, so its self-consistency result is unavailable. The tools preserve that timing requirement for a future real recheck. AI preparation and annotation are explicitly disclosed; any later human decisions should be added with actual dates and without overwriting these records.

## Run the checks

Use Python 3.10 or newer from the repository root. No API key or external Python package is required for the audit checks.

```sh
python3 -m unittest discover -s 07_scripts -p 'test*.py' -v
python3 07_scripts/audit.py validate
```

The 20 tests use temporary synthetic fixtures outside the assessed dataset. Structural validation alone does not mean the portfolio is complete. Once the AI evaluation file is present, validate its records and recompute metrics with:

```sh
python3 07_scripts/audit.py validate --require-collected --annotations 05_annotations/ai_evaluation.csv
python3 07_scripts/completion.py status --annotations 05_annotations/ai_evaluation.csv
```

The [workflow guide](07_scripts/WORKFLOW.md) also covers immutable submissions, final-rubric decisions and delayed blind packets. Keep private ID mappings outside version control while a blind review is pending.
