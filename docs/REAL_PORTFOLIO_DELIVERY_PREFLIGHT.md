# Real portfolio Word preflight (mechanical gate; not owner certification)

This entry exists because a real 2026-11-21 ice/snow finance delivery used an independent document styling path and was presented after a partial check. A valid Word binary and successful render did not enforce the canonical 20pt title, 18pt red H1, 13.5pt body, explicit skim anchors and final italic risk paragraph.

## Operational invocation

When actual DOCX files are produced outside the canonical Financial builder (such as a session-only drafting route), do **not** use a lighter ad hoc QA. Before saying they pass mechanical QA, call the existing checker through:

```bash
python scripts/real_delivery_preflight.py --manifest /path/to/task-delivery-manifest.json --out-json /path/to/task-preflight.json
```

The JSON manifest includes `task_id`, `required_outputs`, `artifacts` (kind→actual DOCX path), and `article_evidence` for each long form with explicit `stock_names` and `required_bold_anchors`. The exact allowed output set is task-specific. Missing output, missing metadata, missing italic risk paragraph, wrong title/H1/body typography, nonred/nonbold H1, unbold company occurrence or absent declared anchor must FAIL. Incorrect risk placement after the final visible paragraph must FAIL. The command exits 1 when mechanical QA fails.

`article_evidence` must come from the current task and audited research; this CLI cannot prove that the input company universe is complete or that an anchor is editorially meaningful. An empty or falsified company list does not become source truth merely by passing this command.

## Assurance boundary

A positive receipt certifies **SESSION_FILE_MECHANICAL_CHECK_ONLY**. The code explicitly holds publication certification, independent reader acceptance and owner-state admission OPEN; neither this tool nor synthetic GitHub CI evaluates factual entailment, narrative value or user satisfaction. Continue research and independent semantic review through the existing Financial owner graph. The hosted owner-signed Financial Provider Action is still necessary for canonical task-state/method writes. No CAOS runtime, duplicate task ledger, new default article template or task-specific company quota is introduced.

## Root hypotheses and counterexamples

* Missing policy: contradicted by the existing policy and `check_docx`.
* Bypass/partial ad hoc preflight: directly observed in the ice/snow delivery and this added CLI prevents false mechanical PASS when invoked.
* A weak final source-to-company semantic audit: separately supported by pending PR #95; this patch does **not** claim to solve it.
* ChatGPT native entry selection/obedience: remains NOT_TESTED. An executable CLI does not impose a platform-level tool hook.

If a future valid neighboring task needs a different authorized typography or delivery contract, change the canonical policy through the Financial requirement process and test both positive and negative examples; do not hardcode the ice/snow article into general rules.

For a task requiring both Deep and Broad, identical visible prose in the two files is an additional hard negative. Distinct bytes alone are not sufficient, and different visible prose is **not proof** of independent reader journeys; this remains a semantic editorial obligation.
