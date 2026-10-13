# Financial Writing Agent — Global System Audit + Live E2E Repair (2026-10-13)

Status: **BOUNDED GLOBAL AUDIT COMPLETE FOR CURRENT SCOPE / REPAIRS APPLIED / HOSTED-CI EXECUTION EVIDENCE OPEN**  
System task: `financial-writing:system-audit`  
Current repository authority: `D1traverser-debug/financial-writing-agent@main`  
Live E2E sample: `ice-snow-economy-20261013`  
Assurance ceiling: **CURRENT-MAIN AUTHORITY REVIEW + LOCAL EXECUTED REGRESSIONS + LIVE DOCX REGENERATION/RENDER QA + GITHUB STATE REREAD; NO PROVIDER-ATTESTED INDEPENDENT SEMANTIC REVIEW; HOSTED CI JOB STEPS UNAVAILABLE**

## 1. Why this audit reopened

The user explicitly said `继承财经写作系统`, intending continuation of the **Financial Writing system-wide audit/maintenance work**. The chat incorrectly treated the phrase as Bare CONTINUE, discovered the default USER article workspace, and resumed the ice-snow article instead.

Universal `ENTRYPOINT.md` defines this as Named CONTINUE: exact owner/task manifest + short checkpoint should be attempted before global discovery. Therefore the misroute was a real continuation-control defect, not merely a conversational misunderstanding.

The same turn also exposed a second problem: the article owner state claimed a complete DUAL delivery set, but neither Deep nor Broad Word binary was retrievable in the fresh chat. This is a higher-layer recurrence of the 2026-10-12 visible-output-contract incident.

The completed ice-snow article was therefore used as a live E2E evidence sample for the full-system review rather than being treated as proof that the system was healthy.

## 2. Scope actually inspected

Current-main surfaces inspected in this pass:

1. Universal continuation entry semantics and explicit SYSTEM_INFRA eligibility/resolution behavior;
2. Financial `continuity/TASK_INDEX.md`, USER workspace metadata and new engineering/system-task recovery surface;
3. single-owner architecture and canonical workflow/state/TaskContract boundary;
4. current research package for the ice-snow article;
5. Editorial plan, Deep/Broad publication source and prior EDITORIAL_AUDIT / FINAL_AUDIT evidence;
6. Natural Authorial Prose / structural-rhythm rules;
7. Word delivery policy, current artifact metadata and actual fresh-chat file availability;
8. owner guard output reconciliation model;
9. blocked/system-impact lifecycle and quality-promotion boundaries;
10. policy/rule-ownership consistency and reference mirrors;
11. pytest regression additions and current GitHub Actions execution evidence.

This is a bounded current-system audit. It is not a claim that every future topic/provider/product behavior has been exhaustively proven.

## 3. Confirmed defect FW-GA-20261013-01 — Named continuation could not reliably resume system-level Financial work

Severity: **P1 control-plane / recovery correctness**  
Class: `CONTINUATION_ROUTING_AND_SYSTEM_TASK_REGISTRATION`

### Evidence

- User phrase: `继承财经写作系统`.
- Universal current entry rule: Named CONTINUE should resolve exact owner/task first; Bare CONTINUE is a different path.
- Financial repo had durable global-audit/rebuild evidence under `evals/`, but its continuity task index exposed only `financial-writing:main` as a resumable Financial task.
- The chat incorrectly entered Bare discovery and resumed an article FINAL_AUDIT.

### Root cause

Two layers combined:
1. execution error: the chat misclassified a named continuation as bare;
2. persistence/routing asymmetry: system-wide Financial work had evidence files but no explicit resumable engineering task manifest/checkpoint.

### Repair

Created explicit durable task:
- `financial-writing:system-audit`;
- class `SYSTEM_INFRA`;
- visibility `EXPLICIT_ONLY`;
- owner `FINANCIAL_WRITING_AGENT_ENGINEERING`;
- task manifest + HANDOFF under `continuity/tasks/financial-writing-system-audit/`.

Updated `continuity/TASK_INDEX.md` so:
- bare Financial continuation still exposes only the default USER article workspace;
- `财经写作系统 / 财经写作全局审视 / financial-writing:system-audit` are Named CONTINUE routes to the explicit system task.

Universal resolver already supports explicit resumable SYSTEM_INFRA tasks and title/display-name substring matching, so the new candidate fits the current runtime model rather than creating another resolver.

### Validation / remaining boundary

Owner-side authority reread confirms both candidates and the explicit-only separation. A future **fresh-chat product trace** using `继承财经写作系统` is still required to prove end-to-end product routing after this repair; repository structure alone cannot self-certify product discovery.

## 4. Confirmed defect FW-GA-20261013-02 — terminal output identity did not prove current user-visible file availability

Severity: **P0 user-visible delivery reliability**  
Class: `ARTIFACT_LIFECYCLE_AND_VISIBLE_DELIVERY`  
Recurrence status: **RECURRED_AFTER_FIX**

### Prior failure class

`FINANCIAL_LIVE_E2E_TASK_OUTPUT_CONTRACT_INCIDENT_2026-10-12.md` recorded a live mismatch where DUAL required three Word outputs but only two were visibly delivered. The prior repair strengthened exact required-output reconciliation.

### New recurrence

The ice-snow owner state reconciled all three output **identities**:
- Deep Word;
- Broad Word;
- audit Word.

But in the fresh chat, neither canonical article Word binary could be resolved from current Conversation/Library surfaces. The previous count/hash repair therefore passed while user-visible availability failed at a higher layer.

`owner_guard` historically validated delivery metadata as `kind + file_name + sha256`. That is correct for identity/reconciliation but insufficient for present-tense availability.

### Root cause

The system conflated three different facts:
1. durable publication source exists;
2. a historical binary identity/hash existed;
3. the user can receive a verified binary **now**.

Only (1) and (2) were represented in durable owner state.

### Repair

Added `financial_writing_agent.delivery_availability.build_visible_delivery_receipt` as a **presentation gate**, not a second task state machine.

The gate requires:
- exact current resource set equals `required_outputs`;
- current `resource_ref` for every output;
- current-session verifier success;
- unchanged historical binary must match the canonical state hash;
- if old binary is unavailable, regeneration is allowed only from durable source identity;
- regenerated binary is explicitly a new instance;
- regenerated instance requires fresh mechanical QA and fresh render QA;
- its actual new SHA-256 is reported rather than reusing the old hash.

Propagated the invariant into:
- `config/policy.json` and packaged policy mirror;
- `skills/financial-writing-agent/SKILL.md`;
- `references/delivery.md` and both mirrors;
- `config/rule_ownership.json`;
- Financial task index;
- regression tests.

### Live instance repair / validation

The missing ice-snow Deep/Broad Word binaries were rebuilt from the exact durable publication sources:
- Deep source git blob: `79be75d2cfe1a58a30a1a5b547a82d223c168a38`;
- Broad source git blob: `9aa181f5534cbea111a2cfaa8a7abafa07451da1`.

Fresh rebuilt instances:
- `ice_snow_economy_deep_redelivery_20261013.docx` — SHA-256 `a23fdc5d8ea82cedeed627c1e2d989a67e3b70fd94ff5c27d7e050ffebe1624b`;
- `ice_snow_economy_broad_redelivery_20261013.docx` — SHA-256 `3b54adfcf3a9ed726e8a679819f70bde8d8797bba9bb7528771a950db3f4876d`.

Both passed fresh deterministic checks: 0 tables, 0 underlines, required title/H1 typography, all supplied A-share company occurrences bold, exactly one final fully italic risk paragraph. Deep rendered to 9 pages and Broad to 4 pages; every page was visually inspected in the current session with no clipping, overlap or missing glyphs.

The current audit Word binary remained resolvable and matched its canonical SHA-256 `02a7e8069ae59f26f889ffd5f7e555d101f5189471431505abc3b70db2922157`.

A real current-session visible-delivery receipt was then built successfully across all three outputs. This validates the repaired distinction between historical canonical identity and current presentation instance.

## 5. Confirmed defect FW-GA-20261013-03 — structural template geometry escaped semantic audit

Severity: **P1 writing-quality / audit reliability**  
Class: `DETERMINISTIC_QUALITY_GUARD_COVERAGE_GAP`

### Evidence from live Deep article

The current `style.md` already warns against:
- repeated section geometry;
- every section using the same conclusion/three-points/summary mold;
- mechanically forcing every H1 to exactly three children.

Yet the ice-snow Deep article has five H1 sections and the H2 child-count sequence is exactly:

`(3, 3, 3, 3, 3)`.

The prior EDITORIAL_AUDIT nevertheless stated that geometry varied according to analytical need and marked `structural_rhythm_naturalness` / `template_redundancy_control` PASS. This statement is contradicted by the publication structure itself.

### Root cause

The deterministic style guard focused on repeated rhetorical phrase clusters. Macro section geometry remained largely a same-model semantic judgment, which could self-confirm the structure it had just authored.

`CHAT_SELF_REVIEW` was honestly labeled, so this is **not** an independence-label fraud. It is a coverage gap demonstrated by the limits of self-review.

### Repair

Added `financial_writing_agent.structure_geometry.analyze_structure_geometry`.

Current narrow hard condition:
- four or more consecutive substantive H1 sections;
- each has the same child count;
- repeated child count is at least three.

This extreme pattern requires REVISE. Short/mixed structures and H1-only Broad compression do not fail.

Live regression tests bind the actual ice-snow publication files:
- Deep must report `(3,3,3,3,3)` and `requires_revise=true`;
- Broad `(0,0,0,0)` remains legal.

Policy and Skill now make the structure-geometry guard part of the Writing DNA boundary.

### Historical article disposition

The existing terminal ice-snow Deep output remains a historical live-E2E sample; its prior `CHAT_SELF_REVIEW=PASS` is no longer treated as proof that the structure was optimal. The new guard proves the current system would reject that geometry on a future/fresh draft. This audit does not silently rewrite a terminal article state outside the canonical owner transition model.

## 6. Confirmed defect FW-GA-20261013-04 — canonical policy carried technology-shaped fixed comparison dimensions

Severity: **P1 authority consistency / cross-topic generality**  
Class: `STALE_CROSS_TOPIC_POLICY`

### Evidence

`config/policy.json` previously fixed company comparison dimensions to:
- order visibility;
- realization speed;
- earnings sensitivity;
- overseas exposure;
- technology optionality.

That list is appropriate for some technology/manufacturing topics but not a universal Financial Writing invariant. The current editorial reference correctly requires TopicDNA and evidence-specific comparison dimensions. The ice-snow Editorial plan in fact used different dimensions: demand distance, realization speed, profit sensitivity, adverse variable and evidence strength.

### Repair

Removed the fixed universal list and replaced it with:
- `TOPIC_SPECIFIC_FROM_CURRENT_AUDITED_EVIDENCE`;
- explicit prohibition on a fixed cross-topic comparison list;
- non-binding generic examples only.

Updated both source and packaged policy so static mirror integrity remains possible.

## 7. Areas reviewed with no new confirmed defect in this pass

### Research / evidence

The live ice-snow research package used policy/industry material plus listed-company disclosures, maintained a Universe Coverage Ledger, distinguished MATERIAL / SECONDARY / REFERENCE_ONLY and preserved attribution gaps. No new systemic research-recall defect was proven from this sample.

### Workflow / owner state

Canonical stage order, immutable TaskContract, DUAL output contract, main-only article state and downstream invalidation remain coherent in the current inspected implementation. No second business-state authority was introduced by this repair.

### BLOCKED / system-impact lifecycle

Current owner lifecycle retains canonical recovery targets, downstream invalidation and maintenance closure assurance requirements. No new concrete defect was established in the inspected path.

### Independent semantic review

Provider-attested independent review remains unavailable. This is an **OPEN assurance boundary**, not a defect to paper over with another persona/agent. The legal terminal remains `DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN`.

## 8. Validation actually executed

Executed in this chat/container:
- visible-delivery availability unit regression: **6/6 PASS**;
- live Deep geometry check: `(3,3,3,3,3)` → **REVISE trigger confirmed**;
- live Broad geometry check: `(0,0,0,0)` → **no false fail**;
- rebuilt Deep mechanical checks: **PASS**;
- rebuilt Broad mechanical checks: **PASS**;
- Deep current render: **9/9 pages visually inspected PASS**;
- Broad current render: **4/4 pages visually inspected PASS**;
- current audit Word SHA matched canonical identity;
- full three-output current-session visible-delivery receipt: **VISIBLE_DELIVERY_READY**;
- Financial TASK_INDEX reread: default USER and explicit-only SYSTEM candidate separation present;
- source/package policy mirror now shares the updated blob identity;
- delivery source/skill/package reference mirrors were written identically.

New repository regression tests added:
- `tests/test_delivery_availability.py`;
- `tests/test_structure_geometry.py`;
- `tests/test_global_audit_regressions_20261013.py`.

## 9. Hosted CI evidence — OPEN, not PASS and not a code-failure conclusion

Current workflow definition contains real steps for install, pytest, contract eval, static audit, retired-runtime audit, wheel smoke and DOCX render smoke.

The latest observed push run for commit `2983a60a8465082eda71c5fed81d42fb92b78023` is GitHub run `38397865130` with overall conclusion `failure`, but its job payload has `steps=null` and job-log retrieval returns `404 BlobNotFound`. Therefore no test-step failure can be attributed from this run, and the run cannot be counted as a hosted PASS either.

Status: `HOSTED_CI_EXECUTION_EVIDENCE_UNAVAILABLE__OPEN`.

## 10. Complexity / architecture effect

Net additions are intentionally bounded:
- one explicit-only system audit task/checkpoint for already-existing engineering work;
- one stateless visible-delivery presentation gate;
- one stateless structure-geometry quality checker;
- regression tests and existing-authority updates.

Not added:
- no new business owner;
- no new article state store;
- no Library/Drive task authority;
- no alternate workflow;
- no new persona reviewer;
- no parallel terminal semantics.

The new system task is excluded from bare/default USER discovery, so normal article-writing startup remains unchanged.

## 11. Current conclusion

The Financial Writing system is **materially stronger but not globally certified**.

Closed in this scoped pass:
1. system-level Financial audit work now has a durable explicit continuation target;
2. current visible-delivery availability is separated from historical artifact identity and mechanically gated;
3. the live missing-Word incident was concretely repaired with new verified artifact instances;
4. extreme repeated H1/H2 geometry now has a deterministic regression gate bound to the actual failing article;
5. stale technology-shaped universal comparison dimensions were removed from canonical policy.

Still OPEN:
- fresh-chat product trace proving `继承财经写作系统` resolves the new task end to end;
- hosted CI execution evidence for current main;
- provider-attested independent semantic review;
- open-world quality/generalization beyond the inspected live sample and existing regression corpus.

These OPEN items must not be converted into a claim of global perfection, but they also do not erase the concrete repairs and current-session evidence above.
