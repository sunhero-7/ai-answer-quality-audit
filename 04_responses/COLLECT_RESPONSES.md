# Collect genuine responses

No candidate responses are included yet. Use an accessible model in a fresh conversation for each generation, after verifying the corresponding reference. Record the actual model and collection method used.

## Before collecting

Verify the reference for each task first. In `03_references/reference_verification.csv`, enter `verified`, your name, the real verification timestamp with timezone, and any notes. Use `revise` or `needs_clarification` if appropriate. Record only dates and times actually known; do not invent a verification time.

If a task or key changes, save a new version before generation. Candidate prompt files are in `02_tasks/prompts/`. Each contains the exact task, including any necessary passage or policy, and nothing from the reference key or scoring rubric. Do not copy from the reference-review document into a candidate chat.

## First collection batch

Use these exact files, copying their complete contents. The A/B slot is recorded locally and is not added to the prompt.

| Task | Prompt file | Fresh generation 1 | Fresh generation 2 |
|---|---|---|---|
| MP01 | `02_tasks/prompts/MP01.txt` | MP01-A | MP01-B |
| MP02 | `02_tasks/prompts/MP02.txt` | MP02-A | MP02-B |

Later repeat for CS01, CS02, RC01, RC02, PR01 and PR02. Sixteen separate conversations produce the pilot's 16 responses.

1. Open a new conversation with the chosen model. Use no prior project context, custom project instructions, reference files, rubric, examples, or previous answer. Prefer a context-isolated mode if available. Record any remembered/personalised context or other settings that cannot be disabled as a limitation.
2. Paste the clean task prompt exactly. Send it once. Do not ask for a specific quality level, add an instruction to make errors, or select among multiple outputs.
3. Keep the first complete response exactly as it appears, including mistakes, caveats and formatting. An ordinary refusal is still a candidate. Log interrupted or failed generations separately before any retry; preserve what was captured. Do not silently regenerate to obtain a more interesting answer.
4. Save the reply as a UTF-8 `.txt` file. Keep an exported conversation or local source reference where available. Record the model label actually displayed, generation date (and time only if known), unique conversation ID/link/local label, source method, and only settings you can verify. For example `Chat UI; settings not exposed` is honest; an assumed temperature is not.
5. Repeat the same prompt in another fresh conversation for slot B. Never show B the response from A. Two outputs from the same model are allowed; describe them as two separate generations.

The generator must not see the key or rubric. You can read the verified key while annotating. The separation applies to generation and to AI-suggested scores, not to your access to evidence.

## Record the originals and metadata

Save the reply files and identify each one with this metadata. Retain the actual prompt too; changed prompts must be reviewed and versioned rather than silently treated as the planned task.

```text
Task ID:
Slot: A or B
Displayed model name:
Generation date: YYYY-MM-DD
Generation time/timezone, only if known:
Unique conversation ID, link or local label:
Source method: pasted/exported from [chat interface]
Known settings: unknown if not exposed
Reply filename:
Actual prompt: exact contents of the named prompt file, or attach the actual text
Collection limitations or failed attempts:
```

Do not paste your intended correction in place of the response. Retain the original, create neutral display IDs, and prepare the first four responses with no suggested ratings. If the model/version cannot be identified, record the displayed label and limitation; do not invent a model name.

## Optional local import

Use Python 3.10 or newer from the project folder. Paths below are relative to this folder. Replace example metadata with what actually happened; the placeholders are not evidence of generation. The current script is scoped to the eight-task pilot; extend and test it for the remaining dataset after pilot decisions are saved.

```bash
python3 07_scripts/audit.py import-response \
  --task-id MP01 --slot A \
  --reply saved-reply.txt \
  --actual-prompt 02_tasks/prompts/MP01.txt \
  --model 'DISPLAYED MODEL LABEL' \
  --generated-at 'YYYY-MM-DD' \
  --source 'Chat interface; manual UTF-8 capture' \
  --session-id 'UNIQUE LOCAL CONVERSATION LABEL' \
  --settings 'unknown'

python3 07_scripts/audit.py validate
python3 07_scripts/audit.py validate --require-collected
python3 07_scripts/audit.py blind-batch \
  --task-ids MP01,MP02 --output 05_annotations/batch_01

python3 07_scripts/audit.py validate \
  --annotations 05_annotations/batch_01/annotations.csv
```

The importer rejects overwrites, duplicate session labels, unverified keys and altered prompts. It records file hashes (digital fingerprints), which can detect later changes to captured files. A matching hash does **not** independently prove which vendor generated a response or whether the manual copy matched the screen.

The blind-batch folder contains a response packet and blank CSV plus a private ID mapping. Keep the mapping and provenance closed while scoring. They are physically separate files, not secure access controls. If you collected the outputs yourself, disclose that origin may be remembered.

Batch validation uses the adjacent private mapping in memory without changing the submitted CSV. If the CSV has been moved, pass `--mapping batch-folder/private_map.json`. If only a generation date is known, the script cannot establish the order of reference verification and generation within that day. Preserve that limitation and do not invent a time. Failed attempts, prompt changes and interrupted outputs belong in `collection_events.csv` with any retained capture.

The validator can check structure, completeness and consistency of records. It cannot decide whether your reasoning is correct or certify that a reply is authentic. Substantive review and any AI coaching follow Dominic's saved independent decisions.
