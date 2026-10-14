# Problem / Evolution Journal Entry Schema

Version: `1.0`
Effective: `2026-10-15`

Material entries in `evals/PROBLEM_EVOLUTION_JOURNAL.md` should preserve these fields when applicable:

- `problem_id`
- `observed_at`
- `scope`
- `status`
- `symptom`
- `user_visible_consequence`
- `detection_source`
- `micro_diagnosis`
- `macro_alignment`
- `governing_assumption_challenged`
- `external_research_or_method_evidence`
- `alternatives_considered`
- `failed_or_rejected_paths`
- `action_taken`
- `verification`
- `result`
- `system_or_evolution_impact`
- `remaining_unknowns_or_blockers`
- `parent_upcall_status`
- `evidence_refs`

The schema is descriptive and does not create a second runtime/state authority. Compact local-problem entries may omit fields that are genuinely not material, but must still retain enough history to explain what failed and what was done.
