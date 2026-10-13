# Financial Writing Agent v0.8

An A-share financial-writing owner with material-complete Deep analysis, explicit-scope market explanation, durable staged checkpoints, bounded semantic-review assurance, executable system-impact escalation, Reader Funnel / Natural Authorial Prose / Writing DNA controls and Word delivery.

## Current operating model
This user's current production mode is **GitHub-mounted authority + GPT chat execution**. A Site/MCP deployment is optional/future, not required for normal use.

Financial Writing therefore has two execution adapters behind one business owner:
- **OWNER_NATIVE / Python** — the deterministic state machine + owner-native audit runtime when those capabilities are actually available in the current session.
- **GITHUB_CHAT / CHAT_BRIDGED** — current GPT chat executes the same business sequence while GitHub stores per-article state and stage artifacts under `workspaces/articles/{task_id}` according to `continuity/GITHUB_CHAT_EXECUTION.json`.

GITHUB_CHAT is not permission to write freely from the prompt. It must create/resume durable state before research/drafting, checkpoint every material stage, and reread GitHub after writes. Normal stage mutations use `github_chat_guard.py`; BLOCKED recovery and material-feedback system-impact lifecycle mutations use `github_chat_lifecycle.py`. Chat memory is never execution truth.

## Core behavior
- `FINANCE_DEEP`: material-complete within the bounded audited research universe.
- `FINANCE_BROAD`: selective traffic-oriented compression while preserving evidence and uncertainty; title/opening must expose a truthful non-niche financial stake.
- Multi-company Deep topics preserve complete material coverage and an evidence-based company comparison map rather than an undifferentiated basket.
- Publication content is delivered as Word when current-session document tooling is available; the durable GitHub publication source remains regeneration authority.
- No publication tables, no underlines, no publication-tail source appendix, and no image/cover/section-visual/avatar/sticker workflow.
- Final risk disclaimer is one inline italic `风险提示：...` paragraph.
- Numbering hierarchy: `一、二、三 → （1）（2）（3） → ①②③`.
- Bold skim path uses selected semantic anchors, and every exact occurrence of user-supplied A-share company/stock names is mechanically bolded in Word.

## Workflow
Canonical sequence:

`INTAKE → RESEARCH → RESEARCH_AUDIT → EDITORIAL → TITLE → DRAFT → EDITORIAL_AUDIT → DELIVERY → MECHANICAL_AUDIT → FINAL_AUDIT`

OWNER_NATIVE can reach `COMPLETE` only through its controller and proof-bearing gates. GITHUB_CHAT normally ends as `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`: the article can be useful/delivered, but same-chat self-review is not relabeled as owner-native certification.

## Semantic audit authority
For OWNER_NATIVE, Research/Editorial/Final semantic PASS requires the current owner-runtime trajectory plus persisted provenance bound to the exact task/stage. `run_semantic_audit_stage` is the MCP certification gateway when that runtime exists.

For GITHUB_CHAT, Research/Editorial/Final red-team artifacts carry `CHAT_SELF_REVIEW`. They may identify defects and force revision but may not become `INDEPENDENT_EXECUTOR`, owner-native semantic PASS or provider-attested isolation. Missing stronger review leaves certification OPEN; it does not justify a fake PASS.

The historical schema token `INDEPENDENT_EXECUTOR` means stage-separated owner-runtime judge execution only, not provider-attested isolation.

## Research / Market Explanation
Every ResearchPackage or equivalent GitHub research artifact declares `market_explanation_scope = REQUIRED | NOT_MATERIAL` with a reason. A company universe alone does not activate price-formation analysis.

When active, separate economic benefit from market selection, compare competing mechanisms, preserve `why_this / why_not`, continuation/reversal conditions and causal confidence:
`VERIFIED_FACT → SUPPORTED_MECHANISM → PLAUSIBLE_INTERPRETATION → UNRESOLVED`.

## Reader Funnel and Writing DNA
CTR, title hooks, reader profile, first-screen retention, continuation and completion form one funnel:
`qualified impression → click → first-screen retention → continued reading → completion → promised insight delivered`.

The prose gate audits fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration.

OWNER_NATIVE `record_writing_learning_sample` stores raw user edits, feedback, acceptance/rejection and post-publication evidence. GITHUB_CHAT persists equivalent evidence in the exact article workspace. A single sample is evidence only; it never auto-promotes itself into policy.

Material `USER_EDIT`, `USER_FEEDBACK` and `USER_REJECTION` must also create a durable system-impact review obligation. In GITHUB_CHAT the evidence and OPEN system-impact item are checkpointed together; `github_chat_lifecycle.review_system_impact_state` then classifies the item, optionally emits a non-authoritative Universal control signal, and moves a closed item into history. Any GITHUB_CHAT closure is `SELF_ATTESTED_CHAT_EVIDENCE_BINDING`, not independent verification or owner-native methodology proof.

## Quality-promotion evidence
Quality promotion is stricter than runtime correctness:
- complete regression/held-out cases carry immutable artifact identities and are re-verified at promotion time;
- candidate-change/counterexample evidence must semantically support the candidate;
- hard-regression PASS requires a real execution bound to the exact candidate/change;
- blind pairwise runs use position swap and verified execution/evidence refs;
- callback presence does not prove independent execution identity.

Current FINANCE_DEEP evidence remains diagnostic because held-out diversity is still insufficient. No current evidence proves prose quality improved.

## Recoverability and anti-bypass
OWNER_NATIVE mandatory failures use persisted `BLOCKED` recovery cursors and `resume_blocked_task`.

GITHUB_CHAT review-stage FAIL blocks in place. Recovery requires `github_chat_lifecycle.resume_blocked_state`, non-empty repair evidence, the persisted failed review artifact/decision, invalidation of that failed evidence, and a fresh review artifact at the exact same stage before later advancement.

GITHUB_CHAT otherwise resumes from GitHub `STATE.json` + exact stage refs. If GitHub write, current web evidence, document tooling or another exact stage capability is unavailable, the affected action stays BLOCKED/OPEN. The system must not jump from a user prompt to a pseudo-final article merely because GPT can produce fluent prose.

Changes to research, editorial plans, titles or drafts invalidate affected downstream evidence and stale artifacts.

## Word contract
- H1 `18pt`, H2 `15pt`, body `13.5pt`, H3 currently `12pt`
- zero publication tables
- zero underlines
- no end-of-article source appendix
- one final italic `风险提示：...` paragraph, no rendered numbered risk H1
- deterministic numbering and explicit semantic bold preservation
- every user-supplied A-share company/stock name mechanically bold at every exact occurrence
- required artifact/check evidence must reflect what actually ran
- stale render pages are cleared before rerender when render QA is available

## Runtime surfaces
`financial_writing_agent/plugin_server.py` remains the single public MCP registration surface for the optional owner-native MCP path. v0.8.1 exposes 19 typed tools and one Word resource template.

`continuity/GITHUB_CHAT_EXECUTION.json` is the owner-local adapter for the current GitHub + GPT-chat path. `financial_writing_agent/github_chat_guard.py` owns normal guarded chat transitions/feedback capture; `financial_writing_agent/github_chat_lifecycle.py` owns bounded BLOCKED recovery and system-impact lifecycle mutation. These do not create a second business-rule authority; they adapt the existing owner workflow at explicitly self-attested chat assurance.

There is no compatibility shim, legacy `CHAT_TEXT`, visual/sticker contract or canned `structure_patterns.md` library on current `main`.

`main` remains code/rule truth. Repository/CI correctness, current-session execution, independent review and live writing quality are separate evidence classes and must never be collapsed. The owner-local chat guards do not by themselves solve outer final-response admission, non-forgeable Continuity lease fencing, or physical GitHub write interception; those remain separate control-plane boundaries.
