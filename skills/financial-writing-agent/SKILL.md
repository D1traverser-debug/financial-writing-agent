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

- **Single Financial operating entry:** this Skill. The CAOS entry is governance-only.
- **Article create/read/update:** create one `workspaces/articles/<task_id>/STATE.json`; read through `observe_article` and the exact task files; change requirements through the current admission path, preserving history and invalidating dependent evidence.
- **Article workspace:** research evidence under `research/`, stage outputs under `stages/`, editorial/story assets under `editorial/`, audit receipts under `reviews/`, Word/rendered deliverables under `delivery/`, and user feedback under `feedback/`. The task's `STATE.json` binds their identities and lifecycle.
- **Delete semantics:** do not erase accepted history or receipts. Retire a requirement/method through its lifecycle operation; remove only proven disposable temporary artifacts. A replacement must not silently rewrite an older article.
- **Reusable methods:** the only method catalog is `knowledge/METHOD_KNOWLEDGE_CATALOG.json`. It supports create, read/query, staged revise, discard pending, promote, challenge, retire, restore and impact verification. Pending changes never silently replace the active method.
- **System evolution:** `evals/EVOLUTION_INDEX.json` owns current system status; `evals/quality_regression.json` owns editorial-readiness baselines. Do not create another global task index or parallel method store.
- **Policy mirrors:** the Skill reference modules and `financial_writing_agent/resources/references/` are the two delivery surfaces for the same Financial-owned policy. They must remain byte-identical. There is no third root `references/` copy.

## Human interaction protocol

At intake, reconstruct the full intent and classify each clause: goal, requirement, correction, preference, suggestion, issue, question or approval. Keep user outcomes distinct from implementation proposals. For ambiguity, infer a safe reversible path, state material assumptions and proceed; ask one focused question only when deliverable, authority or risk changes. Do not outsource architecture decisions to the user when evidence supports a choice.

New standalone-created tasks bind `task_intake_contract_version=1.0`. They cannot leave INTAKE until the complete prompt-bound `TaskIntakeManifest` is validated and a separate trusted reviewer signs `task_intake_review`. The manifest must map every binding requirement and preference to its source clause, preserve nonbinding ideas separately, bind the exact output contract and success criteria, validate the writing execution profile, and declare required knowledge/capability routes. The INTAKE transition creates revision 1 of TaskRequirementAuthority from the reviewed manifest and binds its exact digest into the initial Portfolio Context. Do not create a context with an empty requirement projection and fill requirements later. Resume must match the persisted manifest digest and profile. Legacy tasks without the marker retain their historical compatibility; do not silently retrofit them. Contract details: `docs/task_intake_and_goal_outcome.md`.

Binding requirement changes need the complete normalized upsert/retire set and explicit owner confirmation. Irreversible external actions need authorization; ordinary research, analysis and drafting do not. Report what was read, written, verified, blocked and left OPEN.

## Decision Loop and Execution Loop

For defects: recover the reader outcome; test evidence and counterevidence; compare requirement, source, mechanism, narrative, runtime, artifact, reader and authority; falsify the preferred option; compare reuse/adapt/replace/remove by value, risk and reversibility. Use DecisionEnvelope; choose a bounded action.

Execute, read back, correct and rerun negative/neighbor tests. Owner graph: INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT. The 16 semantic passes are model-orchestrated. `portfolio_coordinator.run_next_portfolio_stage` runs one task-bound stage, persists typed artifact+context atomically, reads back/cross-binds them, then admits via `standalone_runtime.py`. Model supplies pass outputs; provider authenticates/persists. `execute_portfolio_writing` is test replay only. Provider Action NOT_DEPLOYED; no canonical persistence or owner-state writes until live.

At `FINAL_AUDIT`, a goal-first task must also pass the independent user-goal outcome gate. Read the exact current Word binaries, extract their actual text, build `goal_outcome.build_goal_outcome_challenge`, and obtain a separate `independent_goal_outcome_review` attestation. The review must cover every active requirement and every manifest success criterion, with evidence references and exact hashes for the current article deliverables. Pass the attestation as `goal_outcome_review` in the final action. PASS alone is not enough: the signed review must say PASS, every requirement and success criterion must be satisfied, the final state must persist the proof, and the visible-delivery readback must also pass. REVISE routes to the signed allowed revision target; FAIL blocks. Never infer user acceptance from an independent review.

Scopes derive from `required_outputs`. RESEARCH receives ALL, RESEARCH, PRIVATE_RESEARCH and every requested product scope; EDITORIAL/TITLE receive ALL+Deep/Broad; DRAFT/audit receive ALL+requested products; DELIVERY receives ALL+DELIVERY+requested products. Owner/portfolio due checks share one projection. Product passes get ALL+own scope through the current stage. Reject inactive scopes and impossible stage pairs; apply the full-universe gate only to its requested product.

Revisions invalidate downstream evidence; preserve history. Recover first; respect consent. Never claim persistence/readback without a real run.

## Financial content contract

### Fixed workflow, adaptive expression

All article tasks use the same ten-stage workflow. A prompt-bound `writing_execution_profile` in Portfolio Context 1.1 records the invariant workflow, exact requirements/preferences and scoped locked/open decision-domain bindings. Derive it with `references/execution_profile.md`: LOCKED requires active explicit/corrective IDs; OPEN carries no hard IDs. It is context, not a router or authority. TaskRequirementAuthority remains authoritative; every semantic pass receives the same profile. Requirement changes refresh it and invalidate affected evidence. Context 1.0 remains readable.

1. Research material value-chain and company economics from current issuer, regulator and filing sources; distinguish direct financial exposure from theme association and preserve counterevidence.
2. Complete the fifteen applicable PrivateResearchBrief 1.1 modules; keep evidence gaps, uncertainty and rejected hypotheses visible.
3. Re-read scoped requirements before major stages. Deep selects from audited research; a user-specified exhaustive company universe is task-specific, never a universal quota.
4. Build independent Deep and Broad StoryBlueprints. Deep serves company economics; Broad serves non-expert acquisition; Interaction is a first-class product, not a shortened article.
5. Draft from sourced notes, trace material claims, and run all eight PublicationFitness gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF.
6. Deliver contracted DOCX and audit outputs; verify binaries, rendered pages, visual quality and exact links. CI and same-chat PASS are not independent acceptance.

## Standalone runtime and trust boundary

Use GitHub connector and `fetch_file` for reads; stage code only on candidate branches via `create_blob` → `create_tree` → `create_commit` → `update_ref(expected_sha)`. Do not direct-update `main`; Git CAS is not owner approval. Canonical owner-state/method writes require hosted Financial Provider Action: owner auth, `standalone_runtime.py`, signed provider admission, effect receipt, atomic CAS and exact readback. NOT_DEPLOYED; no substitute path.

## Current research and publication evidence

Research facts need exact source text/family, retrieval time, body hash, period/unit/direction and contradiction review. Governed sources expire after seven days; stale or changed sources reopen RESEARCH. Require contracted source-family diversity and two heterogeneous no-delta sweeps before bounded saturation. Hashes prove identity, not entailment; unread/unrelated refs cannot satisfy requirements. Read Financial-owned `research.md`, `private_research.md`, `market_explanation.md`, `claim_trace.py` and `PrivateResearchBrief` for schemas. Separate verified fact, supported mechanism, interpretation and unresolved claims; never fabricate facts, coverage or citations.

PublicationFitness gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE, PAYOFF. Same-chat review may clear INTERNAL_DELIVERY_READINESS only against exact draft bytes; Word remains uncertified. Publication certification requires independently verified review. Deliver actual `AUDIT_DOCX`, `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX` and, if contracted, `PRIVATE_RESEARCH_DOCX`; verify binaries, rendered PDF/PNG pages, visual inspection and current-session access. Filename, hash, PASS or CI alone proves neither delivery nor reader quality.

## Method governance and evolution

Preserve the original utterance; decompose it into scoped requirements without losing negation or exceptions. Binding changes require explicit owner approval and signed provider admission, never unsigned chat CAS. Suggestions remain nonbinding.

Method lifecycle: candidate → revise pending → independent validation/promotion → challenge/suspend → soft-retire → restore as candidate → external impact verification. Preserve provenance, scope, fit/misfit, counterexamples, version digest and revalidation triggers. Pending methods never replace active ones. Bind admitted versions to research receipts; changes reopen the earliest affected stage. Never invent impact closure or reviewers.

`EVOLUTION_INDEX.json` is the sole current system-status authority; keep failure chronology and rejected hypotheses in the problem journal. Each repair restores the full goal, compares shared causes, seeks counterexamples, tests negative and valid-neighbor cases, reads back exact results and preserves OPEN conditions. Engineering, provider integration, client activation, independent review, article quality and delivery are separate gates.

Before claiming completion, replay each goal through actual research, Deep/Broad prose, review, revision and Word; probe missing/changed/conflicting inputs. For system-wide stability, evaluate multiple topic families and prior accepted/rejected artifacts: keep the core workflow fixed while story form and voice remain content-led. A pass DAG/mock PASS is not an article; each resumable stage artifact must be persisted, provider-read back, digest-matched and owner-admitted.

## Effect writes
`financial_writing_agent.standalone_runtime.py` verifies signed provider admission (article v1.1; method v1.0), effect receipt v1.0, atomic CAS and exact reread. No signer means no mutation; legacy history stays unbound.
