# AI Answer Quality Audit

**WORK IN PROGRESS — pilot preparation**  
Independent portfolio project by **Dominic Da Silva**  
Started: 8 September 2026 · Target completion: **15 September 2026**

This project will document how I assess AI answers, explain quality decisions, write corrections and check the consistency of my own judgments. The planned scope is **40 tasks and 80 genuine model responses**, covering mathematics and physics, customer support with fictional policies, reading comprehension, and practical reasoning.

The repository currently contains preparation materials and blank templates. **Human reference verification, response collection and annotation have not started. There are no evaluation results or model performance claims yet.** The target date is a plan, not a completion claim.

## Progress

As of **8 September 2026**:

| Activity | Prepared or completed | Planned total |
|---|---:|---:|
| Draft tasks prepared | 8 | 40 |
| Draft reference checklists prepared | 8 | 40 |
| References verified by Dominic | 0 | 40 |
| Genuine model responses collected | 0 | 80 |
| Responses annotated by Dominic | 0 | 80 |
| Delayed blind recheck responses | 0 | 16 |

The workbook and CSV contain **16 blank pilot response slots**. Their IDs are placeholders, not evidence of collected answers or completed reviews. See the [current checkpoint](CHECKPOINT.md) and [week plan](00_plan/WEEK_PLAN.md).

## Explore the project

- [Draft annotation rubric](01_guidelines/rubric_v0.1.md): five scoring dimensions, decision boundaries and error tags.
- [Eight pilot tasks](02_tasks/pilot_tasks.json) and [clean generation prompts](02_tasks/prompts/): two tasks in each category.
- [Draft reference review](03_references/pilot_reference_review.md) and [human verification record](03_references/reference_verification.csv): all references await Dominic's verification.
- [Response collection protocol](04_responses/COLLECT_RESPONSES.md): capture unedited outputs and record provenance.
- [Blank annotation workbook](05_annotations/pilot_annotation_template.xlsx), [CSV template](05_annotations/annotations.csv) and [annotation guide](05_annotations/ANNOTATING.md).
- [Import and validation script](07_scripts/audit.py), [synthetic tool tests](07_scripts/test_audit.py) and [saved preparation validation](06_quality/validation_2026-09-08.txt).
- [Delayed recheck protocol](06_quality/RECHECK_PROTOCOL.md) and [planned final report](08_portfolio/REPORT_SPECIFICATION.md).

## Evaluation method

Each response will receive a separate **0–2 score** for accuracy, instruction following, relevance, completeness and clarity. A total is descriptive and is calculated only when all five scores are recorded. **Every material factual error requires correction, regardless of the total score.** Unresolved task or reference issues are recorded explicitly.

The eight-task pilot comes first. Dominic will verify each reference before collecting two fresh, unedited generations for that task, then make the initial ratings, rationales and corrections independently. The generating model must not receive the reference key, rubric or another candidate's response. Two generations from the same model are acceptable; that does not establish a comparison between different models.

After reviewing the pilot, the rubric will be revised with reasons and applied consistently to all 80 responses, including the pilot. Original judgments and later changes will be preserved. Sixteen eligible responses will receive a blind recheck at least 24 hours after their baseline reviews, with earlier labels and coaching hidden. The resulting measure will be described as **self-consistency**; no second human reviewer has participated. Hiding metadata and earlier judgments cannot eliminate memory effects.

## AI assistance and my contribution

At this checkpoint, **Codex, with collaborating AI agents, drafted all project content and tooling**: the structure, tasks, reference checklists, rubric, protocols, blank workbook and CSV templates, Python script, tests and public documentation. AI also performed technical preparation checks. These checks do not constitute human verification or annotation. The [AI assistance log](00_plan/ai_assistance_log.csv) records this support.

Dominic chose the completion target and is the project owner. His substantive evaluation work—reference verification, initial ratings, explanations, corrections and delayed rechecks—is **still pending**. AI coaching may follow a saved human submission; it must not supply assessed ratings or corrections before that submission. No human working hours are claimed at this stage.

## Run the preparation checks

Use **Python 3.10 or newer** from the repository root. The script and tests use the Python standard library; no API key or external package is required.

```bash
python3 07_scripts/test_audit.py
python3 07_scripts/audit.py validate
```

The 13 tool tests use temporary synthetic fixtures outside the assessed dataset. Structural validation can pass while every human review remains pending; it reports those missing counts explicitly. To require collection to be complete, run:

```bash
python3 07_scripts/audit.py validate --require-collected
```

That stricter command is **expected to fail at the current preparation stage**. The tool supports the eight-task pilot; it will need to be extended and tested before the remaining 32 tasks are added. It checks record consistency and saved-file hashes, not answer quality or vendor authorship.

## Planned outcome and limits

The intended final deliverables are a completed annotated dataset, preserved feedback and corrections, a self-consistency analysis and a short report reflecting on actual findings. They will be added as the work is completed. This small, deliberately varied convenience sample is intended to demonstrate an evaluation process; it cannot establish general model performance.

Public records should use local source labels where account details or private conversation links would otherwise be exposed. Private blind-batch ID maps remain outside version control. The original model text will be kept separate from corrected answers.
