# Standalone Skill execution profile

## Purpose
`STANDALONE_SKILL` is the explicit non-deployed execution profile for a new conversation that can read this Skill/repository but cannot call the Financial Writing Agent MCP Runtime.

It exists to reduce instruction drift when Runtime is absent. It is **not** equivalent to Runtime enforcement and must never be described as deterministic execution. The goal is to reproduce the Runtime's control discipline with an explicit shadow ledger, frozen contracts, stage gates and final evidence rather than relying on conversational memory.

## Activation and non-degradation rule
Choose the execution profile before research:

1. If Financial Writing Agent Runtime tools are available, use `RUNTIME`; do not choose standalone for convenience.
2. If Runtime is genuinely unavailable/not deployed and the task is being executed by reading the Skill, choose `STANDALONE_SKILL` before any research/writing.
3. Do not silently switch an already-started Runtime task into standalone because a tool/gate failed. A Runtime task remains Runtime-owned and must be repaired/resumed or reported BLOCKED.
4. Do not invent MCP calls, task IDs, gate receipts, artifact checksums or render resources in standalone mode.

A standalone run must label its internal execution profile as `STANDALONE_SKILL`. It may reach `STANDALONE_COMPLETE`; it must never pretend it reached Runtime `COMPLETE`.

## ShadowTaskLedger — mandatory control plane
Before research, create one compact in-session `ShadowTaskLedger`. Keep it in working state and update it after every stage before continuing. When an already-authorized writable workspace/file destination is available, persist a checkpoint outside the product GitHub repository; otherwise keep it in-session and do not claim cross-conversation resumability.

Minimum fields:
- `execution_profile = STANDALONE_SKILL`;
- `task_fingerprint`: current user request/topic/platform/output intent;
- `effective_time_boundary`: freeze the current execution time or the user's explicit historical cutoff before research;
- `distribution_mode`, `content_mode`, `delivery_channel`, `visuals_enabled`;
- `source_obligations`: every user-supplied source/reference;
- `current_stage`;
- stage statuses using only `NOT_STARTED / PASS / REVISE / BLOCKED / N_A`;
- research/title/draft revision counters;
- `knowledge_context` decision and refs/reason;
- `research_coverage` and `evidence_ledger` refs/summary;
- frozen acceptance contract(s);
- required outputs and artifact identities actually produced;
- final evidence keys and render/page inspection state where applicable;
- blockers/unresolved items;
- exact `next_action`.

A genuinely new task always starts with a fresh ShadowTaskLedger. Never import another task's selected title, outline, draft, blockers, stage, artifacts or next action merely because they exist in the same or another conversation. Reuse only durable knowledge/experience that is independently relevant and reverified.

## Stage graph
Use the same legal stage order as Runtime.

Single formal mode / sticker:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → STANDALONE_COMPLETE`

DUAL:
`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL[FINANCE_DEEP] → TITLE[FINANCE_DEEP] → DRAFT[FINANCE_DEEP] → BROAD_DERIVATION[FINANCE_BROAD: EDITORIAL → TITLE → DRAFT] → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT → STANDALONE_COMPLETE`

Never jump forward because later work is easier. Before changing `current_stage`, record why the current stage passed and what concrete evidence supports it.

Revision invalidation is mandatory even without Runtime. When an upstream item changes, mark every dependent downstream PASS as `NOT_STARTED` or `REVISE` and rebuild it. At minimum:
- research/factual change invalidates editorial, title, draft and all downstream audits/delivery;
- selected structure/section-contract change invalidates title/draft and downstream checks that depend on them;
- selected-title/hook promise change invalidates draft/editorial audit/final hook evidence;
- draft change invalidates editorial audit, delivery, mechanical audit and final audit;
- delivery/artifact change invalidates mechanical/final artifact evidence.

Use the configured research/title/draft revision budgets as self-counted ceilings. Do not reset counters to escape a limit. If repeated revision exhausts the applicable budget, mark `BLOCKED` and explain the unresolved defect instead of looping.

## Mandatory shadow gates
### INTAKE
Freeze task intent, output mode, platform, source list, effective time boundary, delivery channel and visual decision. Distinguish genuinely new work from explicit continuation. In standalone mode, continuation across conversations is allowed only when the prior task checkpoint/artifacts are actually available and can be identified unambiguously; otherwise ask one targeted question or start a new task.

### RESEARCH
Load `research.md` + `knowledge.md`. Build explicit working records for:
- `SourceCompletion`: each user source = `FULL / PARTIAL / DUPLICATE_ORIGINAL / UNAVAILABLE`, with fallback and impact when not FULL;
- `EvidenceLedger`: material claims, source, verification status, source-group independence, core-safe status;
- `Coverage`: event/timeline, concept graph, industry/transmission chain, relevant universe, material-company depth, fundamentals/realization stage, market selection/roles, `why_this / why_not`, negative evidence, omissions, counts, time integrity, market-data capability and explicit stop reason;
- knowledge recall = PASS with real refs or N_A with reason.

Recommendation/stock-comparison articles must research the relevant universe before selecting the final written subset. Every stock that materially affects the recommendation/comparison must be deeply checked, not added from familiarity.

No title/outline/body work begins while a core claim is unresolved or a material user source is silently unaccounted for.

### RESEARCH_AUDIT
Re-read research as a skeptical reviewer, not as its author. Explicitly test:
- missing branch/company/source;
- contradiction/counterexample;
- source independence;
- stale/future-dated claim relative to `effective_time_boundary`;
- Level-2/tick/market-microstructure overreach;
- whether `why_this / why_not` is actually supported;
- whether coverage stopped for a defensible reason rather than fatigue.

If any material defect exists, target RESEARCH and invalidate downstream work.

### EDITORIAL
Load `editorial.md` + `style.md`. Build TopicDNA first. Generate candidate structures from TopicDNA before looking at recent outline fingerprints.

For each applicable formal mode freeze a draftable section contract containing selected structure, side focus, company-selection basis and for each H1: directional conclusion, reader gap, payoff requirement, logical blocks and any justified H3 requirement.

For DUAL, only FINANCE_DEEP is allowed here. FINANCE_BROAD planning is forbidden until the FINANCE_DEEP draft is frozen.

### TITLE
Run the Hook Engine. Generate 8–12 genuinely different hook mechanisms when the formal mode requires them. Each candidate records factual anchor, reader stake, primary information gap, opening payoff and cognitive-load judgment. Reject superficial paraphrase sets and unsupported dramatic anchors.

Freeze the selected title into the acceptance contract before drafting.

### DRAFT
Write only against the frozen contract. Formal drafts start with exactly one independent lead followed by H1. Preserve evidence strength and distinguish confirmed fact / industrial inference / market expectation / rumor-hypothesis.

When evidence supports a stock/company conclusion, state the current evidence-bounded judgment directly. Empty postponement such as “再看A再看B/继续观察/能否走出来还要看市场” cannot substitute for a present conclusion. Genuine uncertainty must identify the exact unknown, why it is unknown, what resolves it and how outcomes alter the judgment.

### BROAD_DERIVATION
Only after FINANCE_DEEP draft + acceptance contract are frozen. Build FINANCE_BROAD in order: structure → headline → draft.

Before passing this stage, prove manually:
- broad is materially more compressed/lower-friction than deep;
- broad does not introduce a stock absent from the deep mother's material stock set;
- no material fact, evidence strength, company ranking, stock judgment, decisive causal conclusion or risk boundary was silently changed;
- at least one complete core causal chain remains;
- title/opening/H1 packaging is stronger for acquisition without fake suspense or factual distortion.

### EDITORIAL_AUDIT
Run style audit first, then general editorial audit. Re-read the frozen draft from zero rather than relying on the author's drafting rationale. Check template fingerprints, prompt leakage, repetitive rhythm, stitched transitions, empty hedge language, hook payoff, stock-judgment clarity, reasoning continuity and DUAL derivation fidelity.

### DELIVERY
Load `delivery.md` and `visuals.md` when applicable. Produce every required output actually requested. If Word is required and document-generation capability is unavailable, mark delivery BLOCKED rather than claiming publication-ready Word. If visuals are enabled but real image generation/file access is unavailable, record the real limitation; never invent files or paths.

### MECHANICAL_AUDIT
Perform every mechanically observable check that the available environment permits: output presence, document hierarchy, stock-name bolding, markdown leakage, empty paragraphs, prohibited action language, risk section, image count/placement, file identity/readback and render-page inspection.

Unavailable mechanical capabilities must be explicit N_A/BLOCKED according to whether the output can still satisfy the user's requirement. Do not convert “not checked” into PASS.

### FINAL_AUDIT
Load `audit.md` and build the same criterion-keyed evidence inventory required by Runtime. Evidence must point to concrete final content/artifacts, not generic statements such as “checked”. Re-run source completion, omission, count, time, market-data, counterexample, hook/payoff, stock-judgment, compliance/risk and DUAL derivation checks against the frozen final output.

For every material H1, map the frozen directional conclusion / reader gap / payoff requirement to its actual final location. For every required artifact, verify existence and identity with the strongest readback available in the current environment.

## Standalone completion barrier
`STANDALONE_COMPLETE` is allowed only when all of the following are true:
- every mandatory stage/gate is PASS or a legitimately documented N_A;
- no material source obligation is silently incomplete;
- no core claim is unresolved;
- the acceptance contract matches the final draft(s);
- DUAL deep→broad derivation checks pass when applicable;
- required outputs actually exist;
- available mechanical/file/render checks were performed and recorded;
- final criterion-keyed evidence is complete;
- no unresolved blocker remains.

If one of these cannot be proven, do not call the task complete. Return the best completed artifacts plus the exact blocked/unverified boundary.

## User-facing behavior
The shadow ledger is primarily an execution control structure, not a wall of process text for the user. Do not dump it unless asked. Work autonomously through the stages and only surface concise progress/blockers when useful.

Do not ask the user to remind you about normal gates, research breadth, title hooks, stock-judgment specificity, DUAL ordering or audits. Those are Agent responsibilities.

At the end, if the user asks about assurance level, state the execution profile accurately: `STANDALONE_SKILL` is a disciplined self-audited run, not Runtime-enforced execution. Never claim deployment-grade determinism without the Runtime.