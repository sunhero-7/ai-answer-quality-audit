# Draft-material checks: CS03–CS10 and RC03–RC10

Prepared on 10 September 2026 by a Codex AI drafting agent. These are provisional remaining-task materials, not collected candidate responses or Dominic's annotation decisions.

Files:

- `tasks.json`: eight customer-support tasks and eight reading-comprehension tasks.
- `references.json`: sixteen matching draft keys, each with an answer, checklist, evidence and ambiguity notes.
- `build.py`: reproducible authoring source for the two JSON files.

The drafting agent read each policy/passage against its reference, independently of the example answer's wording, and checked whether the claimed facts, calculations and uncertainty boundaries follow. This is an AI author check, not a second independent reviewer or human verification. All reference statuses remain `pending_dominic`; the coordinator must record any further AI review separately and must not label it Dominic's verification.

Mechanical checks completed:

- Both JSON files parse; each has sixteen rows with one-to-one matching IDs and no duplicate IDs.
- The task categories contain eight `customer_support` and eight `reading_comprehension` records.
- Every task has stage `main_draft` and version `0.1`; every reference has version `0.1` and status `pending_dominic`.
- All required reference fields are nonempty; bracketed policy/passage citations used in evidence exist in the corresponding prompt.
- All sixteen example answers fit their prompt's word limit using whitespace-separated word counts. Counts range from 50 to 93 words, with additional margin below each applicable limit.
- Original passages and fictional policies are fully embedded in the prompts. No external factual sources or copyrighted passages are required to solve them.
- No candidate model replies, initial ratings, human rationales or assessed corrections were generated in this subtask.

Content checks and deliberate boundaries:

| Task | Checked outcome or boundary |
| --- | --- |
| CS03 | Preliminary parcel checks are already done; a review update within two business days is not guaranteed resolution or a next-day replacement. |
| CS04 | 26 May misses the 25 May deadline for June; July remains eligible with confirmation, and a July-only pause resumes billing 1 August. May is not partly refunded. |
| CS05 | One damaged £12 bowl gives an eligible £12 item refund after approval, not a £36 whole-order refund. Two photos and the order number are needed; return instructions must precede postage. |
| CS06 | Exact Friday 10:00 receipt is included in the full-refund boundary, so £48 is eligible. Reading time does not control the amount. |
| CS07 | £30 × 10% = £3; eligible subtotal £27; £27 + £10 + £4 = £41. The after-discount £30 gift threshold is not met, and codes cannot be combined. |
| CS08 | Wednesday 13:45 fits staffed hours and a Monday request has sufficient notice in the stated week. The toilet doorway width remains unknown despite the 'accessible' label. |
| CS09 | Support cannot edit a dispatched address. Redirection is only a possible carrier option; absent remedy promises do not prove remedies are impossible. |
| CS10 | Age, class date, voucher expiry and availability are missing. Evening minimum age is 16; the event itself must be no later than expiry. |
| RC03 | The approved three-session trial differs from the original permanent-opening proposal. The newsletter correction fixes an inaccurate account; trial success is not reported. |
| RC04 | Noor's action and the final cupboard location are explicit. The S3 speaker remains ambiguous; Bea may be a natural interpretation but is not certain. |
| RC05 | Both speakers share the water-saving aim and permit aspects of the other proposal. The committee requests quotes without purchasing. |
| RC06 | 15/20 = 75% of respondents, with no justified generalisation to all 50. The two answer groups may overlap; their exact intersection is unknown. |
| RC07 | The 7 October replacement supplies 12 October, 12:00, Room B and £6. Finding an older copy later does not make its contents a newer announcement. |
| RC08 | The summary preserves donation days/location, two label fields, secure homemade envelopes, three exclusions and optional donations. The exclusion wording was clarified during drafting to avoid ambiguity about loose versus unlabelled seeds. |
| RC09 | The found key and lock action are explicit; emotion, sender identity and motive require separate treatment. Multiple supported, qualified reaction inferences are acceptable. |
| RC10 | A contradicted; B not established; C supported; D not established; E not established. The task explicitly distinguishes sending from receiving and absent evidence from incompatible evidence. No announced date does not establish a scheduled event or prove the absence of a private schedule. |

Limitations and integration notes:

- These tasks should remain provisional until the pilot has informed the final rubric and remaining-task design. They have not been tested with genuine candidate generations.
- AI author checks cannot certify that every key is correct. Dominic's review has not occurred. Any user-authorised AI-only verification should name the AI reviewer and remain distinct from human verification.
- RC04 and RC10 intentionally test uncertainty. Reviewers should read their explicit conventions before rating a reply; an unsupported certainty is different from a defensible qualified reading.
- Customer-support replies must not claim unperformed account actions. The examples explain conditional next steps and do not perform cancellations, bookings, refunds or shipments.
- Word counts above describe reference examples only and are not measurements of uncollected candidate answers.
