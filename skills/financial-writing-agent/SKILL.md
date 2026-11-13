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

Before a binding requirement change, present the full normalized set of additions and retirements for explicit owner confirmation. Before irreversible external actions, obtain the required authorization. Normal research, analysis and drafting do not need repeated confirmation. Report exactly what was read, written, verified, blocked or left OPEN.

## Decision Loop and Execution Loop

For material uncertainty, rejection or recurring defect: reconstruct reader/business outcome; investigate current evidence and counterevidence; compare requirement, source, business mechanism, narrative, runtime, artifact, reader and authority hypotheses; falsify at least one plausible preferred option; compare reuse/adapt/replace/remove by reader value, risk, cost, reversibility and compatibility; then select a bounded action. Use the existing DecisionEnvelope and evidence/saturation rules, not fabricated deliberation fields.

Execute the legal next step: retrieve sources, research, write, challenge, render, read back and correct. Rerun negative and valid-neighbor tests. The owner graph is INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT. Use current_admission.build_initial_state, advance_state, apply_task_requirement_change and attach_material_feedback. Recovery/evolution ports are owner_lifecycle.resume_blocked_state, proactive_resolution.record_proactive_resolution_state and owner_lifecycle.review_system_impact_state. Revisions invalidate downstream evidence; retired states remain historical. Recover proactively before asking the user, respecting real consent boundaries.

## Financial content contract

1. Research the economically relevant value chain and company universe from current issuer, regulator, filing and other reliable sources. Separate concept association from direct revenue/profit exposure. Compare within segments: economics, time horizon, profitability, pricing, orders, logistics, working capital, catalysts and falsifiers. Date-check material figures; never present stale data as current.
2. Build PrivateResearchBrief 1.1 with all fifteen modules: universe, value-chain classification, counterclaims, policy ledger, tactical/earnings context, comparisons, uncertainty, scenarios and future verification. Structural PASS does not prove completeness.
3. Re-read task-specific requirements via current_admission.requirement_context_for_scope before each major stage. Deep selects useful conclusions from complete private research. Cross-border-ecommerce-20261016-v3 explicitly requires its complete retained company universe in published Deep—including weak/incidental companies with reasons and meaningful within-segment comparisons. This is a task-specific exception, not a universal ticker quota.
4. Create two independent StoryBlueprints: Deep for material company comparisons and reversal tests; Broad for non-expert acquisition, curiosity and narrative payoff. Broad is not a shortened Deep. The interaction pack is a separate product.
5. Draft from normalized sourced notes and architecture, not close paraphrase. Trace substantive claims, figures, causal chains, quotations, publication time and source conflicts. PublicationFitness has eight gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF. Same-model PASS is not independent human/expert acceptance.
6. Normal delivery is actual Deep DOCX, Broad DOCX, platform interaction DOCX and audit DOCX, plus private research DOCX when required. Use delivery_pipeline.py, claim_trace.py, deterministic DOCX checks and actual PDF/PNG page readback; verify exact accessible file links. Separate source truth, visual quality, editorial quality and reader outcomes. Never substitute prompt suggestions or imaginary links.

## Standalone runtime and trust boundary

The Financial-owned provider interface is financial_writing_agent/standalone_runtime.py. Read-only observe_article exposes stage, legal next action, persisted blocked cursor, open impact and active requirement IDs. Guarded operations: CREATE_ARTICLE, CHANGE_REQUIREMENTS, ADVANCE_STAGE, ATTACH_FEEDBACK, RESUME_BLOCKED, RECORD_PROACTIVE_RESOLUTION and REVIEW_SYSTEM_IMPACT. All recovery/evolution writes use the same owner state, authenticated CAS and independent second readback.

A live client must supply authenticated Git reads, a real external authorization provider, conditional Git Blob compare-and-swap, independent readback and exact required-artifact bytes. Provider HMAC attestations bind provider, audience, authenticated actor, full request digest, prior state SHA and freshness. Boolean callbacks, model-authored actor strings, caller-selected keys and action flags are never authorization. The verifier does not authenticate a ChatGPT session or sign messages; the host provider must do so and protect keys outside model-visible input. Without live write capability, continue permissible research/editorial work, leave state mutation OPEN and report the limitation.

Before DELIVERY and FINAL_AUDIT writes, artifact_reader must retrieve each required actual DOCX and verify Git Blob SHA, SHA-256, canonical task-scoped resource_ref, ZIP/Word integrity and exact task bindings. FINANCE_DEEP_DOCX and FINANCE_BROAD_DOCX must carry current task-scope and source-claim trace receipts bound to the active requirement digest and exact DRAFT artifact blob. The current-session delivery receipt must also prove canonical build and actual rendered-page inspection; a raw DOCX hash is not sufficient. The runtime revalidates the seven-day research freshness window and unchanged source-body hashes before DELIVERY and FINAL_AUDIT; stale or changed sources require replay from RESEARCH.

Before FINAL_AUDIT can commit the terminal state, the runtime rereads the exact RESEARCH and DRAFT artifact bytes. If an admitted PrivateResearchBrief exists, supply `supplemental_delivery_artifacts` containing a freshly built, rendered and source-bound `PRIVATE_RESEARCH_DOCX`. The runtime checks the exact visible output set, actual provider bytes, current-session delivery evidence and the private-brief digest, then persists a `VISIBLE_DELIVERY_READY` receipt. Missing, stale or tampered files fail before CAS. It proves current-session presentability, not factual entailment, independent editorial acceptance or reader outcomes. `observe_article` exposes the persisted visible-delivery status.

## Current research and publication evidence

A real ADVANCE_STAGE leaving RESEARCH requires source_snapshot_reader to retrieve exact UTF-8 text, SHA-256, ISO-8601 retrieved_at and source_family—not model-written source labels. Current as-of briefs and snapshots expire after seven days; sources must span at least two families. Old dated material remains historical until reverified. The cross-border v3 174-ticker retained baseline is a dated historical floor, not today's market universe; verify its structured research artifact and Deep publication coverage.

Every due task requirement must be satisfied at its affected stage with evidence references that resolve to the actual current stage artifact and source snapshots previously read by the provider source reader. Unread, invented or unrelated references are rejected. This is byte/reference provenance, not automatic semantic proof that the requirement is substantively fulfilled; unresolved semantic judgments stay OPEN.

A claim trace with the same number but opposite growth/decline, unit/period or explicit metric direction is blocked. Passing this redline is not semantic entailment. Financial causal claims, issuer/regulator authority, calculations and originality still need primary evidence and editorial challenge.

If PublicationFitness claims INDEPENDENT_EXECUTOR, the host must provide a real authenticated independent_editorial_verifier and exact DRAFT-byte readback bound to reviewed_article_sha256. A reviewer name or third-party PASS label is not acceptance. Missing proof leaves EDITORIAL_ACCEPTANCE=OPEN. For live Word presentation, resource_binary_reader must retrieve actual DOCX bytes for every requested output; validate real SHA, ZIP/Word XML and signed per-page PNG rendering. A mock verifier, filename or synthetic CI portfolio is not user fulfillment.

## Method governance and evolution

CHANGE_REQUIREMENTS preserves the complete provider-authenticated original user utterance and rejects selective excerpts. The utterance is source evidence, not a requirement-template constraint: decompose a complex instruction into multiple scoped, traceable requirements when appropriate. Before any write, show the complete normalized upsert/retire set for explicit owner confirmation; the trusted provider must sign that exact mutation, bound to the full source SHA-256 and canonical mutation SHA-256. A source hash alone, Boolean callback, model-authored actor or unconfirmed proposal never authorizes a write. Action authorization is separately signed and bound to action/task/operation, full request digest and expected prior state SHA. Ideas remain nonbinding RECORD_OWNER_INTENT.

Method CRUD uses observe_method_catalog/admit_method_action, staged revisions, signed independent promotion, non-destructive retirement and signed impact review. Re-read and verify complete signed receipts on catalog reads; prevent replay; an ACTIVE method must match its latest signed promotion. Production still needs a separate real provider/reviewer trust adapter. Full contract: docs/STANDALONE_INTERFACE.md and skills/financial-writing-agent/references/maintenance.md.

Every repair follows: restore full goal → competing shared causes → counterexamples → architecture comparison → bounded implementation → exact-head CI and negative tests → merge/readback → real article and reader-outcome validation → retain/revise/rollback. Green tests establish engineering only. Owner acceptance, original sources, independent reading and user-accessible deliverables are separate gates. Do not claim completion while any required real article remains unaccepted.

Open domain modules selectively from skills/financial-writing-agent/references/: research.md, private_research.md, market_explanation.md, reader_value.md, editorial.md, hooks.md, style.md, audit.md, delivery.md, maintenance.md and proactive_resolution.md. These modules are Financial-owned operating knowledge. Repository branch hygiene is a maintenance concern, not part of article production.
