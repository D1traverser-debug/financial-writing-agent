---
name: financial-writing-agent
description: Independent Chinese financial research, A-share economics, Deep/Broad articles and verified Word delivery.
---

# Financial Writing — Independent Operating Skill

Financial Writing owns its complete operating workflow (D1traverser-debug/financial-writing-agent@main): goal interpretation, article state, research, decisions, writing, review, delivery and system evolution. It has one business owner, one article-state authority and one operating Skill. No external parent runtime, second controller or local daemon is required.

## Route the actual goal

For a **whole Financial system reconstruction**, read evals/EVOLUTION_INDEX.json#active_system_assessment, the user's complete goal and corrections, docs/product_requirements.md, current source and negative article samples. Do not substitute an old DELIVERED article or a structural PR for system or reader-quality completion. For a **specific article**, resume only its workspaces/articles/<task_id>/STATE.json and exact requirement digest; do not rewrite retired history. System repair does not authorize publication.

Act with connected tools; do not ask the user to invent a plan or repeat accessible requirements. Recover mandatory requirements, preferences, ideas, instructions and corrections separately. Article state is owned by financial_writing_agent/current_admission.py and one task-scoped STATE.json—not chat memory, temporary files or a shadow index. Domain contract: docs/product_requirements.md; execution limits: config/EXECUTION_CONTRACT.json; standalone scope: config/FINANCIAL_MANIFEST.json. Preserve private originals; never publish them without consent.



## Canonical files and CRUD

- **Single operating entry:** this Skill. Do not activate a second root Skill or parent entry.
- **Article create/read/update:** create one `workspaces/articles/<task_id>/STATE.json`; read through `observe_article` and the exact task files; change requirements through the current admission path, preserving history and invalidating dependent evidence.
- **Article workspace:** research evidence under `research/`, stage outputs under `stages/`, editorial/story assets under `editorial/`, audit receipts under `reviews/`, Word/rendered deliverables under `delivery/`, and user feedback under `feedback/`. The task's `STATE.json` binds their identities and lifecycle.
- **Delete semantics:** do not erase accepted history or receipts. Retire a requirement/method through its lifecycle operation; remove only proven disposable temporary artifacts. A replacement must not silently rewrite an older article.
- **Reusable methods:** the only method catalog is `knowledge/METHOD_KNOWLEDGE_CATALOG.json`. It supports create, read/query, staged revise, discard pending, promote, challenge, retire, restore and impact verification. Pending changes never silently replace the active method.
- **System evolution:** `evals/EVOLUTION_INDEX.json` owns current system status; `evals/quality_regression.json` owns editorial-readiness baselines. Do not create another global task index or parallel method store.
- **Policy mirrors:** the Skill reference modules and `financial_writing_agent/resources/references/` are the two delivery surfaces for the same Financial-owned policy. They must remain byte-identical. There is no third root `references/` copy.

## Human interaction protocol

At intake, reconstruct the complete user intent from the current message and accessible prior context. Classify each material clause as final goal, mandatory requirement, correction, preference, suggestion, issue report, question or explicit approval. Preserve the distinction between what the user wants and a proposed implementation. When the request is broad or imprecise, infer the safest reversible interpretation, state material assumptions and proceed; ask only one focused question if ambiguity changes the deliverable, authority or risk. Never ask the user to design the system architecture when evidence can support an engineering decision.

Before a binding requirement change, present the complete normalized additions and retirements and obtain explicit owner confirmation in the current conversation. Before irreversible external actions, obtain the required authorization. Normal research, analysis and drafting do not need repeated confirmation. Report exactly what was read, written, verified, blocked or left OPEN.

## Decision Loop and Execution Loop

For material uncertainty, rejection or recurring defect: reconstruct reader/business outcome; investigate current evidence and counterevidence; compare requirement, source, business mechanism, narrative, runtime, artifact, reader and authority hypotheses; falsify at least one plausible preferred option; compare reuse/adapt/replace/remove by reader value, risk, cost, reversibility and compatibility; then select a bounded action. Use the existing DecisionEnvelope and evidence/saturation rules, not fabricated deliberation fields.

Execute the legal next step: retrieve sources, research, write, challenge, render, read back and correct. Rerun negative and valid-neighbor tests. The owner graph is INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT. The existing Python ports are the executable transition authority. Native chat may research and stage candidates, but must not write owner STATE/method changes directly to main; use an authenticated adapter or exact-base/head branch CI admission. GitHub CAS alone is not a guard. Do not claim Python execution without a real run. Revisions invalidate downstream evidence; retired states remain historical. Recover proactively before asking the user, respecting real consent boundaries.

## Financial content contract

1. Research the economically relevant value chain and company universe from current issuer, regulator, filing and other reliable sources. Separate concept association from direct revenue/profit exposure. Compare within segments: economics, time horizon, profitability, pricing, orders, logistics, working capital, catalysts and falsifiers. Date-check material figures; never present stale data as current.
2. Build PrivateResearchBrief 1.1 with all fifteen modules: universe, value-chain classification, counterclaims, policy ledger, tactical/earnings context, comparisons, uncertainty, scenarios and future verification. Structural PASS does not prove completeness.
3. Re-read task-specific requirements via current_admission.requirement_context_for_scope before each major stage. Deep selects useful conclusions from complete private research. Cross-border-ecommerce-20261016-v3 explicitly requires its complete retained company universe in published Deep—including weak/incidental companies with reasons and meaningful within-segment comparisons. This is a task-specific exception, not a universal ticker quota.
4. Create two independent StoryBlueprints: Deep for material company comparisons and reversal tests; Broad for non-expert acquisition, curiosity and narrative payoff. Broad is not a shortened Deep. The interaction pack is a separate product.
5. Draft from normalized sourced notes and architecture, not close paraphrase. Trace substantive claims, figures, causal chains, quotations, publication time and source conflicts. PublicationFitness has eight gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF. Same-model PASS is not independent human/expert acceptance.
6. Normal delivery is actual Deep DOCX, Broad DOCX, platform interaction DOCX and audit DOCX, plus private research DOCX when required. Use delivery_pipeline.py, claim_trace.py, deterministic DOCX checks and actual PDF/PNG page readback; verify exact accessible file links. Separate source truth, visual quality, editorial quality and reader outcomes. Never substitute prompt suggestions or imaginary links.

## Standalone runtime and trust boundary

GitHub reads `main`; drafts stage on candidate branches using `fetch_file`, `create_blob`, `create_tree`, `create_commit`, `update_ref(expected_sha)`. For any owner `STATE.json`, article artifact or method catalog mutation, first use a genuinely authenticated `standalone_runtime.py` action port, or stage a PR that passes `system_acceptance_report.py`'s exact base/head **two-revision business-effect audit** with provider-signed authorization. Do not direct-update `main` as a substitute for executable `current_admission`. `update_file`/blob-tree-commit/expected-SHA/readback prove Git effects only; they do not supply owner approval. In Skill-only chat without the signer/runner, keep that business mutation OPEN and continue lawful read-only research and reversible drafting. Human confirmation is necessary but not a fake HMAC signature. System reconstruction does not authorize new article publication. See `docs/STANDALONE_INTERFACE.md`.


## Current research and publication evidence

Research facts require exact source text, source family, retrieval time, body hash, correct period/unit/direction and contradiction review. The seven-day freshness rule applies to governed current research; stale or changed sources require RESEARCH replay. Require the contracted source-family diversity and two consecutive heterogeneous no-delta sweeps before bounded saturation. A hash proves identity, not semantic entailment. Unread or unrelated references cannot prove requirement satisfaction.

Read the Financial-owned `research.md`, `private_research.md`, `market_explanation.md`, `claim_trace.py` and `PrivateResearchBrief` contracts for detailed evidence schemas. Keep verified fact, supported mechanism, plausible interpretation and unresolved claims separate. Do not fabricate current facts, coverage, search completion or source citations.

PublicationFitness has eight gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF. Same-chat critique is CHAT_SELF_REVIEW, not independent acceptance. A real reviewer must receive exact draft bytes and return verifiable review evidence; otherwise acceptance stays OPEN.

Required outputs: `AUDIT_DOCX`, `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX` and, when contracted, `PRIVATE_RESEARCH_DOCX`. Verify actual DOCX bytes, PDF/PNG pages, visual inspection and current-session access. A filename, hash, PASS or CI does not prove delivery or reader quality.

## Method governance and evolution

Requirement changes preserve the complete original user utterance. Decompose it into scoped requirements without losing negation or exceptions. For a binding change, present the full normalized upsert/retire set and obtain the owner's explicit decision; persist only through signed provider admission, never an unsigned direct-chat CAS. Suggestions remain nonbinding intent.

Method lifecycle: candidate → revise pending → independently validate/promote → challenge/suspend → soft-retire → restore as candidate → externally verify impact. Preserve provenance, scope, fit/misfit, counterexamples, version digest and revalidation triggers. Pending methods never replace active methods. Bind admitted method IDs/versions to research receipts; a changed method reopens only the earliest affected stage. Never invent impact closure or independent reviewers.

Keep material failure chronology and rejected hypotheses in the problem journal; `EVOLUTION_INDEX.json` remains the only current system-status authority. Every repair restores the full goal, compares shared causes, seeks counterexamples, tests negative and legitimate-neighbor cases, reads back the exact result and preserves remaining OPEN conditions. System engineering, live provider integration, client activation, independent review, real article quality and user-visible delivery are separate acceptance gates.
