# Financial Writing Agent v0.8

A deterministic A-share financial-writing runtime with material-complete deep analysis, explicit-scope market explanation, recoverable checkpoints, proof-bearing semantic audits, executable system-impact escalation, a unified Reader Funnel, Natural Authorial Prose / Writing DNA assurance, raw learning-evidence capture and Word-only delivery.

## Core behavior
- `FINANCE_DEEP`: material-complete within the bounded audited research universe.
- `FINANCE_BROAD`: selective traffic-oriented compression while preserving evidence and uncertainty boundaries; title/opening must expose a non-niche financial stake so readers do not need pre-existing sector interest.
- Multi-company topics preserve complete material coverage in Deep and leave an evidence-based company comparison map rather than an undifferentiated basket.
- Publication content: Word only; article body is not pasted into chat.
- QA: `WRITING_AUDIT_REPORT.docx` plus a concise visible chat checklist.
- No publication tables, no underlines, no publication-tail source appendix, and no image/cover/section-visual/avatar/sticker workflow.
- Final risk disclaimer is one inline italic `风险提示：...` paragraph.
- Numbering hierarchy: `一、二、三 → （1）（2）（3） → ①②③`.
- Bold skim path uses explicit selected anchors; company names are not blanket-bolded on every occurrence.

## Semantic audit authority
A semantic `PASS` is no longer a status bit that a chat caller can self-submit.

`RESEARCH_AUDIT`, `EDITORIAL_AUDIT` and `FINAL_AUDIT` PASS require a current owner-runtime stage execution trajectory plus persisted audit provenance bound to the exact task/stage. `WorkflowController` verifies that proof before advancing, and `WritingEngine.complete()` verifies it again before COMPLETE.

The public MCP tool `run_semantic_audit_stage` is the proof-bearing certification gateway. It runs the owner-native OpenAI Agents SDK audit stage on the server. If the required SDK/model runtime is unavailable, the task becomes recoverably `BLOCKED` at the exact audit cursor; it never falls back to chat self-certification.

The historical schema token `INDEPENDENT_EXECUTOR` means **stage-separated owner-runtime judge execution** in this contract. It is not provider-attested isolation. True provider-attested isolation remains a separate unimplemented assurance class and requires an external execution identity/trace.

## Market Explanation scope
Every ResearchPackage explicitly declares `market_explanation_scope` as `REQUIRED` or `NOT_MATERIAL` with a reason. A company universe alone does not activate price-formation analysis.

Use `REQUIRED` when the article materially explains market selection, leadership, price reaction, continuation/reversal or another cross-sectional price-formation question. When active, separate economic benefit from market selection, compare competing mechanisms, preserve `why_this / why_not`, continuation/reversal conditions and causal confidence:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

## Reader Funnel and Writing DNA
CTR, title hooks, reader profile, first-screen retention, continuation and completion are one funnel:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

The prose gate audits fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration.

`record_writing_learning_sample` stores raw task-level evidence from user edits, feedback, acceptance/rejection and post-publication performance. A single sample is `RAW_EVIDENCE_ONLY` and never auto-promotes itself into a durable rule.

For `USER_EDIT`, `USER_FEEDBACK` and `USER_REJECTION`, evidence capture also creates a durable system-impact review obligation. `review_writing_system_impact` must compare at least two mechanisms with explicit failure modes and record whether the incident is local-only, requires no change with reason, or requires the Universal maintenance/evolution loop. An unresolved review cannot be silently bypassed at COMPLETE. If system maintenance is required, a non-authoritative control signal remains visible until a later exact review replay attaches durable maintenance and validation refs at at least `REGRESSION_VERIFIED` assurance.

## Quality-promotion evidence
Quality promotion is intentionally stricter than runtime correctness:
- complete regression/held-out cases carry immutable artifact identities and are re-verified at promotion time;
- candidate change/counterexample evidence must semantically support the candidate, not merely resolve to a real ref;
- zero hard regressions requires a real regression execution receipt bound to the exact candidate/change, not an empty list supplied by the caller;
- pairwise judge refs and judge-run semantics are verified separately;
- callback presence does not prove independent execution identity.

The current FINANCE_DEEP corpus remains diagnostic only because it still lacks a second held-out topic family. No current evidence proves prose quality improved.

## Recoverable fail-closed runtime
Mandatory failures route to `BLOCKED` with a persisted recovery cursor. After the blocker is repaired, `resume_blocked_task` resumes the exact saved stage instead of starting a duplicate workflow or falling back to free-form writing.

Changes to research, editorial plans, titles or drafts invalidate the affected downstream evidence and stale artifacts. Material research changes also invalidate prior factual knowledge-writeback decisions.

## Word contract
- H1: `24px = 18pt`
- H2: `20px = 15pt`
- Body: `18px = 13.5pt`
- H3: currently `12pt`
- zero publication tables
- zero underlines
- no end-of-article `资料来源 / 参考资料 / 参考来源 / 来源汇总` appendix
- one final italic `风险提示：...` paragraph, with no numbered risk H1
- deterministic numbering and explicit bold preservation
- required artifact presence before Mechanical PASS
- stale render pages cleared before rerender
- no server-local filesystem paths in public artifact contracts or audit Word

## Runtime surface
`financial_writing_agent/plugin_server.py` is the single public MCP registration surface. v0.8.1 exposes **19 typed tools** and one Word resource template. `run_semantic_audit_stage` is the only public route that can request owner-runtime semantic PASS certification; ordinary audit-submit tools cannot self-certify PASS. `review_writing_system_impact` is the owner action-level bridge from material writing feedback into the Universal maintenance/evolution control loop.

There is no compatibility shim, legacy `CHAT_TEXT`, visual/sticker contract or canned `structure_patterns.md` library on current `main`.

`main` is code/rule truth. Promotion requires SDK/MCP smoke, unit/trajectory tests, executable contract evals, static authority/version checks, isolated wheel install and DOCX render smoke.
