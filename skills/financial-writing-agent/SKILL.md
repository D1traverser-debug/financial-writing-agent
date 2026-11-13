---
name: financial-writing-agent
description: Independent Chinese financial research, A-share economics, Deep/Broad articles and verified Word delivery.
---

# Financial Writing — Independent Operating Skill

Financial Writing owns its complete operating workflow (D1traverser-debug/financial-writing-agent@main): goal interpretation, article state, research, decisions, writing, review, delivery and system evolution. It has one business owner, one article-state authority and one operating Skill. No external parent runtime, second controller or local daemon is required.

## Route the actual goal

For a **whole Financial system reconstruction**, read evals/EVOLUTION_INDEX.json#active_system_assessment, the user's complete goal and corrections, docs/product_requirements.md, current source and negative article samples. Do not substitute an old DELIVERED article or a structural PR for system or reader-quality completion. For a **specific article**, resume only its workspaces/articles/<task_id>/STATE.json and exact requirement digest; do not rewrite retired history. System repair does not authorize publication.

Act with connected tools; do not ask the user to invent a plan or repeat accessible requirements. Recover mandatory requirements, preferences, ideas, instructions and corrections separately. The only durable article business-state authority is one task-scoped STATE.json in this repository. In ChatGPT sessions, the active executor is the model following this Skill plus the user's connected GitHub connector; no separate hosted Python/MCP service is required. The Python package is a machine-readable contract, reference implementation and CI test target; do not claim to import or execute its modules merely because they exist in the repository. Domain contract: docs/product_requirements.md; execution limits: config/EXECUTION_CONTRACT.json; standalone scope: config/FINANCIAL_MANIFEST.json. Preserve private originals; never publish them without consent.



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

Before a binding requirement change, present the complete normalized set of additions and retirements and obtain explicit owner confirmation in the current conversation. For the native ChatGPT path, that confirmation authorizes the GitHub write; preserve the complete original user message and the confirmation in the task's intent history. Do not invent message IDs, signatures or hashes. The optional Python adapter has a separate signed-provider contract. Before other irreversible external actions, obtain the required authorization. Normal research, analysis and drafting do not need repeated confirmation. Report exactly what was read, written, verified, blocked or left OPEN.

## Decision Loop and Execution Loop

For material uncertainty, rejection or recurring defect: reconstruct reader/business outcome; investigate current evidence and counterevidence; compare requirement, source, business mechanism, narrative, runtime, artifact, reader and authority hypotheses; falsify at least one plausible preferred option; compare reuse/adapt/replace/remove by reader value, risk, cost, reversibility and compatibility; then select a bounded action. Use the existing DecisionEnvelope and evidence/saturation rules, not fabricated deliberation fields.

Execute the legal next step: retrieve sources, research, write, challenge, render, read back and correct. Rerun negative and valid-neighbor tests. The owner graph is INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT. The Python modules define the graph schemas and invariants; in ChatGPT, enact the same legal transitions against the existing STATE.json using the native GitHub connector. For one text file, use update_file with its exact current blob SHA, then fetch it again. For an atomic multi-file write, create_blob for each artifact, create_tree from the exact current main tree SHA, create_commit with the exact current main SHA as parent, update_ref on main with expected_sha equal to that previous head and force=false, then fetch every changed file at the new commit SHA and compare the readback. Upload DOCX bytes through create_blob with base64 encoding. On a stale expected_sha conflict, reread main and recompute; never force or blindly retry. Do not claim to call current_admission or owner_lifecycle functions unless an actual Python runtime was mounted and executed. Revisions invalidate downstream evidence; retired states remain historical. Recover proactively before asking the user, respecting real consent boundaries.

## Financial content contract

1. Research the economically relevant value chain and company universe from current issuer, regulator, filing and other reliable sources. Separate concept association from direct revenue/profit exposure. Compare within segments: economics, time horizon, profitability, pricing, orders, logistics, working capital, catalysts and falsifiers. Date-check material figures; never present stale data as current.
2. Build PrivateResearchBrief 1.1 with all fifteen modules: universe, value-chain classification, counterclaims, policy ledger, tactical/earnings context, comparisons, uncertainty, scenarios and future verification. Structural PASS does not prove completeness.
3. Re-read task-specific requirements via current_admission.requirement_context_for_scope before each major stage. Deep selects useful conclusions from complete private research. Cross-border-ecommerce-20261016-v3 explicitly requires its complete retained company universe in published Deep—including weak/incidental companies with reasons and meaningful within-segment comparisons. This is a task-specific exception, not a universal ticker quota.
4. Create two independent StoryBlueprints: Deep for material company comparisons and reversal tests; Broad for non-expert acquisition, curiosity and narrative payoff. Broad is not a shortened Deep. The interaction pack is a separate product.
5. Draft from normalized sourced notes and architecture, not close paraphrase. Trace substantive claims, figures, causal chains, quotations, publication time and source conflicts. PublicationFitness has eight gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF. Same-model PASS is not independent human/expert acceptance.
6. Normal delivery is actual Deep DOCX, Broad DOCX, platform interaction DOCX and audit DOCX, plus private research DOCX when required. Use delivery_pipeline.py, claim_trace.py, deterministic DOCX checks and actual PDF/PNG page readback; verify exact accessible file links. Separate source truth, visual quality, editorial quality and reader outcomes. Never substitute prompt suggestions or imaginary links.

## Active ChatGPT runtime and persistence

The production ChatGPT path is ChatGPT model + this Financial Skill + the user's existing GitHub connector + current research tools + Python/document tooling when available. This is the standalone runtime. The Skill-only plugin does not itself grant GitHub permission or host Python/MCP, but it does not need to: the already-connected GitHub connector is the persistence provider. No CAOS runtime, local daemon, paid API or custom hosted MCP service is required.

### GitHub read/write protocol

- Read the repository's actual main head and the relevant files before every task. Use the connected GitHub provider's repository and file-read operations; do not rely on stale chat summaries.
- For a single UTF-8 text-file update, use update_file with the exact current blob SHA, then fetch the file again at the resulting commit.
- For an atomic multi-file update, create_blob for each text or binary artifact; create_tree using the exact current main tree SHA; create_commit with the exact current main head as parent; update_ref on main with expected_sha equal to the previous main head and force=false; then fetch every changed path at the new commit SHA and compare the exact content/blob identity.
- DOCX and other binary artifacts use create_blob with base64 encoding. Store the resulting binary under the same article workspace and bind its path and digest in that article's STATE.json.
- If expected_sha conflicts, stop, reread main, reconstruct the current state and recompute the change. Never force-push or blindly retry. If a write result is uncertain, inspect the actual branch head and exact file readback before taking another action.
- For a binding requirement change, preserve the complete user message, show the normalized additions/retirements, wait for explicit confirmation in the current conversation, then commit the state and dependent invalidations atomically. Record the original message and confirmation in the article's intent history. Do not fabricate message IDs, signatures or provider receipts.
- Apply the same GitHub CAS/readback protocol to the single method catalog. Keep pending revisions separate from active methods; promotion and impact closure still require evidence and must not be self-certified.
- The Python standalone_runtime.py adapter is an optional reference implementation and CI test target for a separately hosted integration. It is not directly callable from a Skill-only chat. Its HMAC provider requirements apply only when that optional adapter is actually invoked; they are not prerequisites for native ChatGPT GitHub tool operations.
- If the GitHub connector is missing or lacks write permission, continue safe research and drafting, but leave persistence/transition OPEN and report the exact missing permission. If DOCX generation or page rendering is unavailable, do not claim binary delivery or visual QA.

## Standalone runtime and trust boundary

The active ChatGPT runtime is the model plus this Skill and the user's connected GitHub connector. The GitHub connector performs authenticated repository reads and writes; Git blob/tree/commit operations plus expected_sha compare-and-swap and exact file readback provide the persistence boundary. The Skill package itself does not grant those permissions.

The optional Python adapter in financial_writing_agent/standalone_runtime.py remains a stricter reference implementation for a separately deployed host. It requires authenticated source/actor, explicit action authorization, exact Git content/SHA, conditional CAS, independent second readback and actual artifact bytes. Signed attestations bind actor, audience, full request, prior state SHA and freshness. Model-written identities, hashes, booleans or callbacks are not authorization for that adapter. Do not claim the adapter executed unless an actual Python runtime was mounted and run.

The private ChatGPT package is Skill-only; it has no hosted Python/MCP endpoint and grants no GitHub permission. The native path uses the existing connected GitHub connector instead of requiring a new service. Do not claim installation or fresh-session activation without evidence. If the connector is unavailable, continue safe read-only work and leave only the affected mutation OPEN. See docs/STANDALONE_INTERFACE.md and the acceptance-gate module.

## Current research and publication evidence

Research facts require exact source text, source family, retrieval time, body hash, correct period/unit/direction and contradiction review. The seven-day freshness rule applies to governed current research; stale or changed sources require RESEARCH replay. Require the contracted source-family diversity and two consecutive heterogeneous no-delta sweeps before bounded saturation. A hash proves identity, not semantic entailment. Unread or unrelated references cannot prove requirement satisfaction.

Read the Financial-owned `research.md`, `private_research.md`, `market_explanation.md`, `claim_trace.py` and `PrivateResearchBrief` contracts for detailed evidence schemas. Keep verified fact, supported mechanism, plausible interpretation and unresolved claims separate. Do not fabricate current facts, coverage, search completion or source citations.

PublicationFitness has eight gates: FACT_INTEGRITY, RETENTION, COMPANY_GROUNDING, STRUCTURE_NUMBERING, ORIGINALITY, AUTHORIAL_STYLE, COMPLIANCE and PAYOFF. Same-chat critique is CHAT_SELF_REVIEW, not independent acceptance. A real reviewer must receive exact draft bytes and return verifiable review evidence; otherwise acceptance stays OPEN.

Required outputs: `AUDIT_DOCX`, `FINANCE_DEEP_DOCX`, `FINANCE_BROAD_DOCX`, `PLATFORM_INTERACTION_PACK_DOCX` and, when contracted, `PRIVATE_RESEARCH_DOCX`. Verify actual DOCX bytes, PDF/PNG pages, visual inspection and current-session access. A filename, hash, PASS or CI does not prove delivery or reader quality.

## Method governance and evolution

Requirement changes preserve the complete original user message. Decompose it into scoped requirements where appropriate, but never use selective excerpts that lose negation or exceptions. In the native ChatGPT path, present the complete normalized upsert/retire set and obtain explicit owner confirmation in the current conversation before writing through GitHub CAS. Do not invent a message ID, external signature or digest. The optional Python adapter retains its separate signed-provider requirement. Suggestions remain nonbinding intent.

Method lifecycle: candidate → revise pending → independently validate/promote → challenge/suspend → soft-retire → restore as candidate → externally verify impact. Preserve provenance, scope, fit/misfit, counterexamples, version digest and revalidation triggers. Pending methods never replace active methods. Bind admitted method IDs/versions to research receipts; a changed method reopens only the earliest affected stage. Never invent impact closure or independent reviewers.

Keep material failure chronology and rejected hypotheses in the problem journal; `EVOLUTION_INDEX.json` remains the only current system-status authority. Every repair restores the full goal, compares shared causes, seeks counterexamples, tests negative and legitimate-neighbor cases, reads back the exact result and preserves remaining OPEN conditions. System engineering, live provider integration, client activation, independent review, real article quality and user-visible delivery are separate acceptance gates.
