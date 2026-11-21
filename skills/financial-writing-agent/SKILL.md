---
name: financial-writing-agent
description: Independent Chinese financial research, A-share economics, Deep/Broad articles and verified Word delivery.
---

# Financial Writing — Independent Operating Skill

Financial Writing owns its complete workflow: goal, article state, research, decisions, writing, review, delivery and evolution. It has one business owner, one article-state authority and one Skill. No CAOS runtime, parent controller or local daemon is required. Canonical owner-state/method writes require a Financial-owned hosted Provider Action (transport/admission only, not a parent controller); it is NOT_DEPLOYED.

CAOS governance for material/systemic decisions and cross-project work is defined in `CAOS_FINANCIAL_ENTRY.md` and `config/CAOS_GOVERNANCE.json`; it is session-level only, with no runtime/API dependency or permission authority.

## Route the actual goal

For a **whole Financial system reconstruction**, read evals/EVOLUTION_INDEX.json#active_system_assessment, the complete user goal/corrections, product requirements, current source and negative samples; do not substitute an old DELIVERED article or a structural PR for reader-quality proof. For a **specific article**, resume only its task STATE and exact requirement digest; preserve retired history. System repair does not authorize publication.

Act with connected tools; do not ask the user to invent a plan or repeat accessible requirements. Recover mandatory requirements, preferences, ideas, instructions and corrections separately. Article state is owned by financial_writing_agent/current_admission.py and one task-scoped STATE.json—not chat memory, temporary files or a shadow index. Domain contract: docs/product_requirements.md; execution limits: config/EXECUTION_CONTRACT.json; standalone scope: config/FINANCIAL_MANIFEST.json. Preserve private originals; never publish them without consent.




## Canonical files and CRUD

- **Sole entry/state:** this Skill is Financial's only operating entry; CAOS is governance-only. Article CRUD uses one `workspaces/articles/<task_id>/STATE.json` via `observe_article` and `current_admission.py`; every requirement change preserves history and invalidates downstream evidence.
- **Task layout:** `research/`, `stages/`, `editorial/`, `reviews/`, `delivery/` and `feedback/` hold source evidence, stage/blueprint outputs, audits, Word/renders and feedback bound to that STATE.
- **Lifecycle:** retire requirements/methods; preserve accepted history/receipts. Only proven disposable artifacts may be removed. Never silently rewrite a prior article.
- **Method CRUD:** `knowledge/METHOD_KNOWLEDGE_CATALOG.json` alone supports create, read/query, staged revision, discard, promotion, challenge, retirement, restoration and impact verification; pending edits never replace active rules.
- **Evolution:** `evals/EVOLUTION_INDEX.json` tracks system status; `evals/quality_regression.json` tracks editorial readiness. No shadow global index or method store.
- **Mirrors:** `skills/financial-writing-agent/references/` and `financial_writing_agent/resources/references/` must remain byte-identical; no third `references/` copy.

## Human interaction protocol

At intake, classify every user clause as goal, requirement, correction, preference, suggestion, issue, question or approval. Keep binding outcomes separate from implementation ideas; infer reversible assumptions and ask only when missing information changes deliverable, authority or risk.

New standalone tasks bind `task_intake_contract_version=1.0`; INTAKE cannot exit without a prompt-bound `TaskIntakeManifest` and signed independent `task_intake_review`. Map prompt clauses to requirements/preferences, separate nonbinding ideas, and bind outputs, success criteria, execution profile and knowledge/capability routes. Admit revision 1 of TaskRequirementAuthority and its digest in the first Portfolio Context. Resume must match the manifest/profile; markerless legacy tasks remain legacy. Details: `docs/task_intake_and_goal_outcome.md`.

Binding requirement changes need the complete normalized upsert/retire set and explicit owner confirmation. Irreversible external actions need authorization; ordinary research, analysis and drafting do not. Report what was read, written, verified, blocked and left OPEN.

## Decision Loop and Execution Loop

For defects: recover the reader outcome; test evidence and counterevidence; compare requirement, source, mechanism, narrative, runtime, artifact, reader and authority; falsify the preferred option; compare reuse/adapt/replace/remove by value, risk and reversibility. Use DecisionEnvelope; choose a bounded action.

Execute, read back, correct and rerun negative/neighbor tests. Owner graph: INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT. The 16 semantic passes are model-orchestrated. `portfolio_coordinator.run_next_portfolio_stage` runs one task-bound stage, persists typed artifact+context atomically, reads back/cross-binds them, then admits via `standalone_runtime.py`. Model supplies pass outputs; provider authenticates/persists. `execute_portfolio_writing` is test replay only. Provider Action NOT_DEPLOYED; no canonical persistence or owner-state writes until live.

At `FINAL_AUDIT`, goal-first tasks require signed `independent_goal_outcome_review` bound to actual current Word binaries. It must assess every active requirement and success criterion with evidence. Only all-SATISFIED PASS may terminate; REVISE uses the existing allowed target; FAIL blocks. Visible-delivery readback remains separate. Reviewer PASS is not user acceptance.

Scopes derive from `required_outputs`: RESEARCH gets ALL, research/private-research and active product scopes; later stages receive only their active scopes. Reject inactive scopes and invalid stage pairs. Full-universe gates apply only to the requested product.

Revisions invalidate downstream evidence; preserve history. Recover first; respect consent. Never claim persistence/readback without a real run.

## Financial content contract

### Fixed workflow, adaptive expression

All tasks use the same ten-stage workflow. Portfolio Context 1.1 binds the prompt-specific WritingExecutionProfile (requirements/preferences and scoped LOCKED/OPEN decisions); TaskRequirementAuthority remains the sole authority. Requirement changes refresh the profile and invalidate affected evidence. Context 1.0 remains readable.

1. Research material value-chain and company economics from current issuer, regulator and filing sources; distinguish direct financial exposure from theme association and preserve counterevidence.
2. Complete the fifteen applicable PrivateResearchBrief 1.1 modules; keep evidence gaps, uncertainty and rejected hypotheses visible.
3. Re-read scoped requirements before major stages. Deep selects from audited research; a user-specified exhaustive company universe is task-specific, never a universal quota.
4. Build independent Deep and Broad StoryBlueprints. Deep serves company economics; Broad serves non-expert acquisition; Interaction is a first-class product, not a shortened article.
5. For real session-generated Word outside the canonical builder, run `scripts/real_delivery_preflight.py` on the exact contracted portfolio and reject failed typography, H1 color/bold, risks, company/skim emphasis, missing files and identical Deep/Broad prose. This receipt is mechanical-only, not independent source truth. See `docs/REAL_PORTFOLIO_DELIVERY_PREFLIGHT.md`.
6. Draft from sourced notes, trace material claims, and run all eight PublicationFitness gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF.
7. Deliver contracted DOCX and audit outputs; verify binaries, rendered pages, visual quality and exact links. CI and same-chat PASS are not independent acceptance.

## Standalone runtime and trust boundary

Use GitHub connector and `fetch_file` for reads; stage code only on candidate branches via `create_blob` → `create_tree` → `create_commit` → `update_ref(expected_sha)`. Do not direct-update `main`; Git CAS is not owner approval. Canonical owner-state/method writes require hosted Financial Provider Action: owner auth, `standalone_runtime.py`, signed provider admission, effect receipt, atomic CAS and exact readback. NOT_DEPLOYED; no substitute path.

## Current research and publication evidence

Research facts need exact source text/family, retrieval time, body hash, period/unit/direction and contradiction review. Sources expire after seven days; stale or changed sources reopen RESEARCH. Require source-family diversity and two heterogeneous no-delta sweeps before saturation. Hashes prove identity, not entailment. Use the Financial research, market-explanation, claim-trace and PrivateResearchBrief schemas; separate facts, mechanisms, interpretations and unknowns.

PublicationFitness gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE, PAYOFF. For `FACT_INTEGRITY_AUDIT` and `PLATFORM_INTERACTION_AUDIT`, load `skills/financial-writing-agent/references/audit.md` (mirror: `financial_writing_agent/resources/references/audit.md`). Fact audit gets `audited_evidence`, `selected_thesis`, `company_decision_map`, `change_conditions`, `publication_distillation`; check each material claim's entity, metric, period, value/unit, direction, comparator and evidence ref. Never infer attribution from sentence order or aggregate numbers; numeric/source trace is not semantic entailment. Same-chat review clears INTERNAL_DELIVERY_READINESS only against exact draft bytes; Word stays uncertified. Certification needs independent review. Deliver `AUDIT_DOCX`, `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX` and, if contracted, `PRIVATE_RESEARCH_DOCX`; verify binaries, renders and access. Filename, hash, PASS or CI alone prove neither delivery nor reader quality.

## Method governance and evolution

Preserve the original utterance; decompose it into scoped requirements without losing negation or exceptions. Binding changes require explicit owner approval and signed provider admission, never unsigned chat CAS. Suggestions remain nonbinding.

Method lifecycle: candidate → revise pending → independent validation/promotion → challenge/suspend → soft-retire → restore as candidate → external impact verification. Preserve provenance, scope, fit/misfit, counterexamples, version digest and revalidation triggers. Pending methods never replace active ones. Bind admitted versions to research receipts; changes reopen the earliest affected stage. Never invent impact closure or reviewers.

`EVOLUTION_INDEX.json` is the sole current system-status authority; keep failure chronology and rejected hypotheses in the problem journal. Each repair restores the full goal, compares shared causes, seeks counterexamples, tests negative and valid-neighbor cases, reads back exact results and preserves OPEN conditions. Engineering, provider integration, client activation, independent review, article quality and delivery are separate gates.

Before claiming completion, replay each goal through actual research, Deep/Broad prose, review, revision and Word; probe missing/changed/conflicting inputs. For system-wide stability, evaluate multiple topic families and prior accepted/rejected artifacts: keep the core workflow fixed while story form and voice remain content-led. A pass DAG/mock PASS is not an article; each resumable stage artifact must be persisted, provider-read back, digest-matched and owner-admitted.

## Effect writes
`financial_writing_agent.standalone_runtime.py` verifies signed provider admission (article v1.1; method v1.0), effect receipt v1.0, atomic CAS and exact reread. No signer means no mutation; legacy history stays unbound.
