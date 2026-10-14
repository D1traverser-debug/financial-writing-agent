# Proactive Resolution Maintenance Change — 2026-10-15

Status: `CANDIDATE`
Owner: `DOMAIN:financial_writing`
Trigger: user identified that inherited cognition/evolution existed contractually but the assistant still externalized a recoverable voice-evidence dependency instead of attempting autonomous recovery.

## Failure class
`PROACTIVE_RESOLUTION_GAP`

## User outcome
Reduce user work. When relevant evidence/preferences may already exist, the Agent should search/recover/infer provisionally/test before asking the user to repeat or provide them later.

## Alternatives considered

### A. Do nothing; wait for explicit user samples
Rejected. This reproduces the observed failure and makes cognition inheritance passive.

### B. Infer a fixed personal writing style from thin context and persist it as truth
Rejected. This risks fabricating preferences and overfitting one conversation/article.

### C. Evidence recovery + provisional candidate + validation + bounded escalation
Selected. Recover the strongest available durable/context evidence first; when still incomplete, use an explicitly provisional candidate with confidence/unknowns/validation plan; ask the user only when ambiguity materially changes the outcome or proceeding would invent facts/preferences/approval.

## Scope
Financial-local execution rule now. Potential cross-domain generalization is a non-mutating UAOS parent-guidance item, not directly promoted from the child.

## Durable surfaces
- `references/proactive_resolution.md`
- `references/maintenance.md` revision 1.1
- `evals/PROBLEM_EVOLUTION_JOURNAL.md`
- `evals/PROBLEM_EVOLUTION_JOURNAL_INDEX.json`
- `evals/PARENT_GUIDANCE_HANDOFF.md`
- regression: `tests/test_proactive_resolution_problem_journal_20261015.py`

## Acceptance
Candidate is acceptable only if full Financial CI passes and current authority is reread after promotion. The new rule must not weaken factual/approval boundaries, create a second evolution controller, or mutate UAOS parent authority directly.
