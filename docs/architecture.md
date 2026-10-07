# Financial Writing Agent — Architecture

## 1. Goal
Build a reliable A-share financial content system that starts from a fresh conversation, develops broad/deep cognition before selective writing, adapts to formal distribution or image-first WeChat sticker posts, produces publication-ready Word artifacts, and proves completion through independent gates.

## 2. Core architecture
The system uses a **deterministic outer runtime with model-driven inner stages**.

Deterministic Python owns TaskContract/content-mode routing, legal state transitions, checkpoint/resume, recoverable BLOCKED metadata, fail-closed behavior, knowledge recall/writeback decisions, required outputs, visual receipts, Word construction, mechanical/render checks and completion authority.

High-judgment model work owns live research synthesis, TopicDNA, editorial structure, title/hook generation, drafting, a dedicated anti-AI/style judgment, final semantic red-team, and creative image generation.

## 3. Runtime graph
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → COMPLETE`

Failures route to `BLOCKED`; there is no fallback edge to ordinary free-form writing. A genuine `engine.block()` records the originating stage. After the dependency/contract defect is repaired, the explicit resume path returns only to that recorded stage, so recovery cannot become an arbitrary stage skip.

## 4. Content modes
### FORMAL_ARTICLE
Unspecified platform defaults to `DUAL`: one complete research/cognition base, independently edited `FINANCE_DEEP` and `FINANCE_BROAD` versions. Default formal delivery is `WORD_FILE_ONLY` and new Word articles include visuals unless explicitly disabled.

### WECHAT_STICKER_POST
Explicit 微信贴图 requests use a separate contract and `WECHAT_STICKER_POST.docx`. Current title/body/image limits and recommendation mechanics are external changing facts, so the draft includes a source-backed `PlatformConstraintSnapshot` rather than permanent remembered limits.

## 5. Cognition and connected knowledge
Research should know substantially more than the final content includes: event chronology, concept graph, industry/transmission chain, A-share universe, fundamentals, why-this/why-not, market-selection mechanisms, and relevant short-term market roles/signals.

Connected Notion/Drive/StockBase/EventBase operations remain ChatGPT-orchestrator actions using the user's actual connectors. The runtime has two distinct gates:
- `knowledge_context`: pre-research durable-knowledge recall decision. PASS requires actual retrieved references; N_A requires an explicit reason.
- `knowledge_sync`: pre-final durable writeback decision. PASS requires actual writeback receipts; N_A requires an explicit reason.

The Python runtime never impersonates external account credentials. Reused durable knowledge remains subject to current re-verification.

## 6. Editorial, acceptance and style assurance
Structure comes from current TopicDNA rather than rotating templates. DUAL modes generate and select their structures independently after the shared research base exists. Continuous report-style prose and logical paragraph/section transitions are preferred for formal articles. Chinese structural hierarchy is deterministic: `一、二、三 → （1）（2）（3） → ①②③`.

Selected titles and mode structures freeze a `WritingAcceptanceContract` before DRAFT. Draft title/H1 structure is checked against that frozen contract rather than merely trusted from the writer.

Anti-AI quality is an independent semantic sub-gate. A dedicated style judge checks template fingerprints, repetitive constructions, over-regular rhythm, empty bridges, stitched transitions and unsupported extreme/superlative language, including rhetorical `最…`. General editorial audit cannot PASS until the style gate does.

Final semantic evidence is criterion-keyed. Formal modes must explicitly prove headline/title identity, independent lead, first-three-sentence payoff, H1 structure, side focus, company-selection basis, headline factual anchor, opening payoff, bold skim-reading skeleton, reasoning continuity and compliance/risk; DUAL adds cross-version consistency.

## 7. Visual architecture
The model side plans/generates real assets; MCP stores a `VisualPackage`; deterministic Word delivery embeds only recorded assets. Formal defaults use a 16:9 hero plus semantic section images at roughly one per 700 Chinese characters, with semantic boundaries taking priority over counting. Images are centered and uncropped. Sticker mode accepts dedicated image-first/vertical assets when current platform evidence supports them.

Rendered DOCX pages are exposed as resources for actual page inspection. Conversion success alone is not visual QA.

## 8. Risk/compliance
Public financial content requires a topic-specific risk warning/disclaimer with high information density and relatively short wording. Mechanical QA enforces presence/minimum substance and lexical red lines; semantic audit checks disguised actionable guidance and whether extreme language exceeds evidence strength. Disclaimer text cannot cure actionable trading instructions.

## 9. Persistent layers and consistency
- GitHub `main`: executable code/rule truth.
- Hosted MCP persistent store: per-task executable checkpoint truth in production.
- SQLite: local/CI/reference implementation of per-run state.
- Persistent artifact/object storage: production Word/render/manifest identity and bytes.
- Notion/Drive: human-readable governance/mirror layers, not runtime authority.
- Shared market knowledge layer: future common EventBase/StockBase/topic cognition for writing/stock-picking/review; today only the writing-side read/write receipt contract is implemented, so cross-agent synchronization must not be overstated.

Checkpoint storage must be atomic and reject stale concurrent writes rather than silently replacing a newer task state. Production persistence must provide at least the same lost-update protection as the reference store.

## 10. Assurance classes
1. Deterministic assertions: transitions, BLOCKED recovery target, schemas, knowledge-gate decisions, mandatory gate inventory, required outputs, hierarchy, file/image identity/checksum, risk floor, render/mechanical checks.
2. Independent semantic judges: research completeness, title/body evidence support, first-three-sentence payoff, bold scan skeleton, style/continuity, platform fit, visual alignment and compliance.
3. Trajectory/eval tests: verify stage order, stale-state rejection, recovery and fail-closed behavior.

Passing one class never substitutes for another.

## 11. Promotion rule
v0.2.1 remains a candidate until clean CI passes and one user-authorized real article E2E completes with live model research/drafting, real visual generation/insertion, Word render, semantic red-team, visible audit/checklist, durable recovery (including a deliberate interruption or recoverable BLOCKED path), and final artifact checksum/readback. Major sticker behavior should also receive a real platform regression before being treated as production-proven.
