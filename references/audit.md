# Audit module

## Independence

The final auditor must re-evaluate the frozen final artifact. Writer self-assessment is not evidence of passing.

## Two kinds of gates

### Mechanical gates
Use deterministic code where possible: required artifacts, delivery channel, file identity, Word style rules, stock-name bolding, forbidden actionable phrases, disclaimer presence, and successful render output.

### Semantic gates
Use an independent judge for: evidence support, reasoning continuity, negative evidence, why-this/why-not, title truthfulness, title/opening兑现, information density, structure-topic fit, platform fit, compliance nuance and remaining uncertainty.

## Audit report

Generate `WRITING_AUDIT_REPORT.docx` from the final run state. It must include:
- task contract and distribution mode;
- source/evidence boundary;
- stage-by-stage PASS / REVISE / FAIL / N/A results;
- mechanical check results;
- semantic judge results;
- defects found and fixes applied;
- remaining boundaries;
- final artifact identities.

A missing audit report is a completion failure under `WORD_FILE_ONLY`.

## Fail closed

No artifact may be marked COMPLETE while an applicable Must-Pass item lacks evidence. Changes to facts, title, opening, H1 structure, body logic or formatting invalidate the affected prior checks and require re-audit.
