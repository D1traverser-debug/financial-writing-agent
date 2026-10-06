# Audit module

## Independence
The final auditor re-evaluates the frozen final artifact/state. Writer self-assessment is not evidence of passing.

## Mechanical gates
Use deterministic code where possible for required artifacts, delivery channel, file identity, Word styles/numbering, stock-name bolding, actionable red-line phrases, risk/disclaimer presence/minimum substance, expected embedded image count and successful render output.

## Semantic gates
Use an independent judge for:
- evidence support and source boundary;
- reasoning continuity and paragraph/section transitions;
- negative evidence and why-this/why-not;
- title truthfulness and title/opening payoff;
- information density and structure-topic fit;
- platform fit;
- anti-AI style/template repetition;
- unsupported extreme/superlative language, including rhetorical “最…” claims;
- compliance nuance;
- risk warning/disclaimer information quality and concision;
- visual/article semantic alignment, non-duplicative image hooks and avatar treatment when visuals are enabled;
- remaining uncertainty.

## Audit report
Generate `WRITING_AUDIT_REPORT.docx` from final state. Include task contract/distribution, source/evidence boundary, stage-by-stage PASS/REVISE/FAIL/N/A, mechanical results, semantic results, defects/fixes, remaining boundaries, knowledge reuse/writeback references when available, visual manifest identity when applicable and final artifact identities.

A missing audit report is a completion failure under `WORD_FILE_ONLY`.

## Visible checklist
The final chat response must include a concise checklist status covering: runtime/gates, research/evidence, structure/style/continuity, Word/render, compliance/risk disclaimer, visuals if applicable, and knowledge reuse/writeback if applicable. Under `WORD_FILE_ONLY` this checklist must not paste the article body.

## Fail closed
No artifact may be COMPLETE while an applicable Must-Pass item lacks evidence. Changes to facts, title, opening, H1 structure, body logic, visual placement/assets or formatting invalidate affected checks and require re-audit.