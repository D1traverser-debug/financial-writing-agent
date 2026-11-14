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

Execute the legal next step: research, write, challenge, render, read back and correct; rerun negative and valid-neighbor tests. Owner graph: INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT. The 16 passes use `start_portfolio_context` + `execute_portfolio_stage`, one existing stage per call, bound to `task_id` and `task_requirement_digest`. Persist each returned context as its stage artifact, provider-read it back, validate hash chains and admit the Article Aggregate transition through `standalone_runtime.py` before resuming. `RESEARCH_AUDIT` is separate. `execute_portfolio_writing` is in-memory replay/test only. Hashes detect mutation, not provider signatures, semantic proof or acceptance. Native chat may stage candidates but cannot write owner STATE/method changes; use authenticated admission, not Git CAS alone. Never claim execution, persistence or readback without a real run. Revisions invalidate downstream evidence; retired states remain historical. Recover before asking the user, respecting consent.

## Financial content contract

1. Research the economically relevant value chain and company universe from current issuer, regulator, filing and other reliable sources. Separate concept association from direct revenue/profit exposure. Compare within segments: economics, time horizon, profitability, pricing, orders, logistics, working capital, catalysts and falsifiers. Date-check material figures; never present stale data as current.
2. Build PrivateResearchBrief 1.1 with all fifteen modules: universe, value-chain classification, counterclaims, policy ledger, tactical/earnings context, comparisons, uncertainty, scenarios and future verification. Structural PASS does not prove completeness.
3. Re-read task-specific requirements via current_admission.requirement_context_for_scope before each major stage. Deep selects useful conclusions from complete private research. Cross-border-ecommerce-20261016-v3 explicitly requires its complete retained company universe in published Deep—including weak/incidental companies with reasons and meaningful within-segment comparisons. This is a task-specific exception, not a universal ticker quota.
4. Create two independent StoryBlueprints: Deep for material company comparisons and reversal tests; Broad for non-expert acquisition, curiosity and narrative payoff. Broad is not a shortened Deep. The interaction pack is a separate product.
5. Draft from normalized sourced notes and architecture, not close paraphrase. Trace substantive claims, figures, causal chains, quotations, publication time and source conflicts. PublicationFitness has eight gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF. Same-model PASS is not independent human/expert acceptance.
6. Normal delivery is actual Deep DOCX, Broad DOCX, platform interaction DOCX and audit DOCX, plus private research DOCX when required. Use delivery_pipeline.py, claim_trace.py, deterministic DOCX checks and actual PDF/PNG page readback; verify exact accessible file links. Separate source truth, visual quality, editorial quality and reader outcomes. Never substitute prompt suggestions or imaginary links.

## Standalone runtime and trust boundary

Read `main`; stage drafts on candidate branches and use exact-head admission. Owner-state/method writes require signed authorization, provider effect receipt, atomic CAS and exact readback. Never direct-update `main`; CAS is not owner approval. Without signer/runner, no canonical mutation.

## Current research and publication evidence

Research facts need exact source text/family, retrieval time, body hash, period/unit/direction and contradiction review. Governed sources expire after seven days; stale or changed sources reopen RESEARCH. Require contracted source-family diversity and two heterogeneous no-delta sweeps before bounded saturation. Hashes prove identity, not entailment; unread/unrelated refs cannot satisfy requirements. Read Financial-owned `research.md`, `private_research.md`, `market_explanation.md`, `claim_trace.py` and `PrivateResearchBrief` for schemas. Separate verified fact, supported mechanism, interpretation and unresolved claims; never fabricate facts, coverage or citations.

PublicationFitness gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE, PAYOFF. Same-chat review may clear INTERNAL_DELIVERY_READINESS only against exact draft bytes; Word remains uncertified. Publication certification requires independently verified review. Deliver actual `AUDIT_DOCX`, `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX` and, if contracted, `PRIVATE_RESEARCH_DOCX`; verify binaries, rendered PDF/PNG pages, visual inspection and current-session access. Filename, hash, PASS or CI alone proves neither delivery nor reader quality.

## Method governance and evolution

Requirement changes preserve the complete original user utterance. Decompose it into scoped requirements without losing negation or exceptions. For a binding change, present the full normalized upsert/retire set and obtain the owner's explicit decision; persist only through signed provider admission, never an unsigned direct-chat CAS. Suggestions remain nonbinding intent.

Method lifecycle: candidate → revise pending → independently validate/promote → challenge/suspend → soft-retire → restore as candidate → externally verify impact. Preserve provenance, scope, fit/misfit, counterexamples, version digest and revalidation triggers. Pending methods never replace active methods. Bind admitted method IDs/versions to research receipts; a changed method reopens only the earliest affected stage. Never invent impact closure or independent reviewers.

Keep material failure chronology and rejected hypotheses in the problem journal; `EVOLUTION_INDEX.json` remains the only current system-status authority. Every repair restores the full goal, compares shared causes, seeks counterexamples, tests negative and legitimate-neighbor cases, reads back the exact result and preserves remaining OPEN conditions. System engineering, live provider integration, client activation, independent review, real article quality and user-visible delivery are separate acceptance gates.

Before claiming completion, replay every user goal through actual pass inputs, source evidence, Deep/Broad prose, review, revision and Word. Probe missing/changed/conflicting inputs. A pass DAG or mock PASS is not an executed article. For resumable execution, also prove each stage artifact was persisted, provider-read back, matched to its task/requirement digest and admitted by the single Article Aggregate before continuing. A complete in-memory pass trace is not a persisted workflow.

## Effect writes
`financial_writing_agent.standalone_runtime.py` verifies signed provider admission (article v1.1; method v1.0), effect receipt v1.0, atomic CAS and exact reread. No signer means no mutation; legacy history stays unbound.
