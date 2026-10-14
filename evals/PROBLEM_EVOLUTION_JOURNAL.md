# Financial Writing — Problem & Evolution Journal

Status: `CURRENT_DURABLE_PROBLEM_LEDGER`
Journal revision: `1.0`
Initial backfill window: `2026-10-12` through `2026-10-15`
Owner: `DOMAIN:financial_writing`
Purpose: one durable chronology for later Financial maintenance and UAOS parent guidance.

## How to use this journal

This file is the single index of problems actually encountered during Financial Writing work. It records not only final fixes, but also the path taken: what failed, how it was detected, what assumption was wrong, what alternatives were considered, what was tried, what verification succeeded or failed, and what remains open.

Detailed incident/eval files remain the evidence authority for their specific event. This journal links and summarizes them so a future controller does not have to reconstruct the history from scattered chats, commits and audit files.

Historical notes may mention architecture that was later retired. Those entries are evidence of what happened at the time, not current routing authority.

### Required entry fields for future problems

For a material problem, retain:
- date/time or authoritative state timestamp;
- scope/task;
- symptom and user-visible consequence;
- detection source;
- micro diagnosis;
- macro goal/architecture alignment;
- governing assumption challenged;
- external research/method evidence when required;
- alternatives considered and rejected;
- action taken;
- verification/evidence;
- final result;
- system/evolution impact;
- remaining unknown/blocker;
- parent-upcall status.

Small/local defects may use a compact entry but must still appear here.

---

## P-20261012-01 — Publishable article bypassed the Financial owner workflow

Status: `CLOSED_WITH_LIVE_PATH_REPAIR`
Scope: Financial runtime / GitHub-chat execution.

Symptom: a real article experiment skipped capability handshake, owner state, Research, Editorial, Title and audits, performed no current fact research, created no Word/audit artifact, and still returned pseudo-final prose.

Diagnosis: the repository had strong owner-native/Python semantics, but the user's actual operating mode was GitHub + GPT chat. The supported runtime path did not match the real product surface, so declaration-only rules could be bypassed.

Assumption challenged: `more reminders in the Skill are enough` and `Site/MCP must exist before valid work can happen` were both rejected.

Action: introduced an explicit GITHUB_CHAT owner path with durable article state, staged evidence, bounded `CHAT_SELF_REVIEW`, reproducible publication source and no free-form publishable fallback. Also hardened persistence of material negative feedback.

Verification/result: structural and contract evidence were added; later live Financial work successfully used the GitHub-chat path and the architecture was subsequently simplified again into the current direct-domain model.

Evidence: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-12.md`.

System impact: established the principle that supported execution topology must match the user's real host, not only repository-native code.

Parent guidance: historical; current UAOS/Financial direct-child architecture supersedes the old adapter wording.

---

## P-20261012-02 — Negative/corrective feedback had a persistence crash window

Status: `CLOSED`
Scope: owner-native learning persistence.

Symptom: raw USER_REJECTION/USER_FEEDBACK/USER_EDIT could be persisted before the system-impact obligation, so a process interruption could leave negative evidence without `PENDING_REVIEW`.

Diagnosis: the learning sample and system-impact obligation were written in separate steps with an unsafe gap.

Action: moved immediate system-impact reconciliation to the persistence boundary; later methodology evidence remains separate and is not fabricated.

Evidence/result: documented and regression-covered in `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-12.md`.

System impact: user rejection is durable evidence at first save, not an optional later interpretation.

---

## P-20261012-03 — Recent-task discovery used duplicated/shadow filtering logic

Status: `HISTORICAL_OPEN_THEN_SUPERSEDED_BY_ARCHITECTURE_REBUILD`
Scope: old owner-native task discovery.

Symptom: runtime and MCP wrapper could disagree about whether COMPLETE tasks with unresolved maintenance remained discoverable.

Diagnosis: the same business rule existed in two consumers.

Action at the time: left explicitly open rather than claiming a fix; recommended moving filtering to one authority. Later continuity/runtime simplification removed the old control topology from current authority.

Evidence: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-12.md`.

Lesson: duplicated discovery semantics are a drift source; current architecture must keep one owner path.

---

## P-20261012-04 — Parent observation of Financial authority was stale

Status: `CLOSED_BY_LATER_PARENT/CHILD_RELEASES`
Scope: UAOS ↔ Financial binding observation.

Symptom: Universal still referenced an older Financial head after Financial had evolved.

Diagnosis: parent observation was treated as if it remained valid after child mutation.

Action: require parent reread only after final child head is known. Later UAOS/Financial production releases refreshed the binding and current authority now uses direct registered-child activation.

Evidence: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-12.md`; current UAOS `CURRENT_SYSTEM.json`.

System impact: parent assurance is observational and version-bound, never timeless.

---

## P-20261012-05 — Default DUAL contract produced only 2 visible files instead of 3

Status: `CLOSED`
Scope: task/output contract parity.

Symptom: a live zero-memory task should have produced `FINANCE_DEEP_DOCX + FINANCE_BROAD_DOCX + AUDIT_DOCX`, but visible delivery had only Broad + Audit.

Diagnosis: GITHUB_CHAT carried stage semantics but did not mechanically bind the complete canonical TaskContract/default output semantics. Review also praised internal trajectory before reconciling final outputs to the initial contract.

Wrong path tried: a candidate repair attempted per-article branch discovery as a new authority dimension. It was rejected because it added state/discovery complexity without fixing the 3→2 contract defect.

Action: unified default routing/output contract semantics, persisted immutable required outputs, rejected silent mode narrowing, required exact output reconciliation at DELIVERY/FINAL, and moved output-contract reconciliation earlier in end-of-run review.

Evidence/result: `evals/FINANCIAL_LIVE_E2E_TASK_OUTPUT_CONTRACT_INCIDENT_2026-10-12.md`.

System impact: adapter parity means input/default contract + workflow + invalidation + outputs + terminal semantics, not workflow graph alone.

---

## P-20261012-06 — Evolution propagation missed active consumers

Status: `CLOSED_WITH_CONSUMER-COMPLETE_RULE`
Scope: maintenance/change propagation.

Symptom: a prior rule calibration updated canonical behavior but left contradictory assertions in Skill/static-audit/eval consumers.

Diagnosis: impact mapping covered intended writers but not every active consumer/mirror/harness.

Action: maintenance now requires consumer-complete propagation and stale-assertion search before claiming PASS.

Evidence: `evals/FINANCIAL_LIVE_E2E_TASK_OUTPUT_CONTRACT_INCIDENT_2026-10-12.md`.

Lesson: a rule is not promoted merely because its primary source changed.

---

## P-20261012-07 — Maintenance accidentally created temporary branches while using the wrong GitHub action

Status: `HISTORICAL_HYGIENE_INCIDENT`
Scope: GitHub mutation safety.

Symptom: several `tmp-should-not-create*` branches were accidentally created during maintenance.

Diagnosis: wrong connector action/tool selection during mutation.

Action at the time: explicitly removed authority from those refs and documented cleanup debt instead of claiming deletion that available tooling could not prove.

Evidence: `evals/FINANCIAL_LIVE_E2E_TASK_OUTPUT_CONTRACT_INCIDENT_2026-10-12.md`.

System impact: strengthened mutation-sentinel discipline and contributed to the later candidate-branch / controlled-promotion topology.

---

## P-20261013-01 — `继承财经写作系统` was misrouted to an article instead of system maintenance

Status: `CLOSED_IN_OLD_TOPOLOGY__CURRENT_TOPOLOGY_LATER_REBUILT`
Scope: continuation intent resolution.

Symptom: a named request for the Financial system-wide audit was treated as bare continuation and resumed a completed article.

Diagnosis: execution misclassification plus no durable explicit system-maintenance target in the then-current Financial continuity layer.

Action at the time: created an explicit-only system audit task and named continuation route. Later UAOS/Financial architecture removed the old domain continuity controller and now uses UAOS selection + direct child work plane.

Evidence: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-13.md`.

Lesson carried forward: semantic intent resolution must distinguish controller/system work from article work; historical task artifacts must not regain routing authority.

---

## P-20261013-02 — Historical artifact identity was mistaken for current-session file availability

Status: `CLOSED`
Scope: visible delivery.

Symptom: owner state contained canonical Word names/hashes, but the user could not actually receive Deep/Broad files in the fresh chat.

Diagnosis: the system conflated durable publication source, historical binary identity and present-tense user-visible availability.

Action: added a visible-delivery presentation gate requiring fresh current resource refs, verifier success, canonical hash matching for unchanged binaries, and fresh mechanical/render QA for regenerated binaries.

Live repair: missing ice-snow Deep/Broad Word binaries were regenerated from exact durable publication sources, mechanically checked, rendered and visibly delivered; a current-session receipt verified all required outputs.

Evidence/result: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-13.md`.

System impact: `filename + hash` is identity evidence, not current availability evidence.

---

## P-20261013-03 — Self-review falsely passed extreme repeated section geometry

Status: `CLOSED_WITH_GUARD`
Scope: writing quality / audit reliability.

Symptom: an ice-snow Deep article had five substantive H1s each with exactly three H2 children `(3,3,3,3,3)`, while same-chat audit claimed structure varied naturally.

Diagnosis: rhetorical phrase checks existed, but macro structure geometry remained mostly same-model semantic self-judgment.

Action: added a narrow structure-geometry guard for extreme repeated child-count patterns and bound regressions to the real failing article.

Evidence: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-13.md`.

System impact: same-chat review can self-confirm authored structure; deterministic guards should cover demonstrated extreme failure classes without turning every structure into a quota.

---

## P-20261013-04 — Canonical comparison policy contained technology-shaped fixed dimensions

Status: `CLOSED`
Scope: cross-topic Financial writing generality.

Symptom: policy fixed dimensions such as overseas exposure and technology optionality even for non-technology topics.

Diagnosis: a topic-specific successful template had been over-promoted into a universal rule.

Action: replaced fixed cross-topic dimensions with topic-specific dimensions derived from current audited evidence; retained examples as non-binding only.

Evidence: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-13.md`.

System impact: generalized Financial rules must encode the decision principle, not one topic's vocabulary.

---

## P-20261013-05 — Hosted GitHub CI returned failure without usable step/log evidence

Status: `CLOSED_BY_LATER_WORKING_CI__HISTORICAL_INFRA_EVIDENCE`
Scope: assurance.

Symptom: runs ended `failure` with `steps=null` and log retrieval errors, so neither PASS nor code-test failure could be honestly claimed.

Diagnosis: external runner/evidence availability problem, not enough information to attribute a product defect.

Action: maintained an explicit assurance boundary; local executed regressions and render QA were reported separately. Later Financial releases obtained normal candidate and production CI with actual passing steps.

Evidence: `evals/FINANCIAL_GLOBAL_SYSTEM_AUDIT_2026-10-13.md`; later production CI evidence.

Lesson: a red status without executable step evidence is not automatically a code diagnosis.

---

## P-20261014-01 — Financial identity was incorrectly coupled to UAOS/controller task identity

Status: `CLOSED`
Scope: parent/child architecture.

Symptom: an intermediate inheritance design required UAOS task ID and Financial `STATE.task_id` to be equal, creating dual/competing identity semantics.

Diagnosis: inheritance was implemented as identity takeover instead of capability/governance inheritance.

Action: removed parent-child article-ID equality/binding logic, restored Financial-owned article identity/state/workflow/output ownership, and made UAOS router/controller identity an external distinct namespace with optional opaque child state reference only.

Verification: Financial 0.8.3 architecture/regression suite passed; subsequent 0.8.4+ product authority retained the decoupled model.

System impact: common governance inheritance must not transfer domain business identity ownership.

---

## P-20261015-01 — Declared cognition/evolution inheritance was not yet sufficiently encoded in Financial maintenance/product authority

Status: `CLOSED_AT_CONTRACT_LEVEL`
Scope: UAOS common capability inheritance.

Symptom: Financial declared cognition/evolution capabilities, but parent common semantics and Financial maintenance wording were not yet fully aligned to the current every-problem research/reflection floor; product requirements were also dispersed.

Diagnosis: capability IDs alone do not prove semantic inheritance.

Action: Financial 0.8.4/profile16 adopted the explicit four-part problem-response floor, domain-vs-parent evolution ownership, direct domain activation and one current product-requirements authority with acceptance mapping.

Verification: candidate + production CI and production reread passed.

Evidence: `evals/FINANCIAL_UAOS_COGNITION_EVOLUTION_PRODUCT_AUDIT_2026-10-15.md`.

Important later finding: this contract-level closure did **not** guarantee proactive execution when evidence was incomplete; see P-20261015-09.

---

## P-20261015-02 — Huangjiu article candidate branch was accidentally mutated with an unintended `dummy` file

Status: `CLOSED_NO_MAIN_POLLUTION`
Scope: GitHub mutation execution.

Symptom: while starting the Huangjiu article candidate branch, an incorrect file-update call created/changed an unintended `dummy` file on the candidate branch.

Diagnosis: tool/action misuse during candidate mutation.

Action: stopped, researched GitHub contents/SHA semantics, reset the candidate ref back to the exact main SHA, then compared branch vs main and confirmed they were identical before continuing.

Result: `main` was never polluted; article work resumed from a clean branch/state.

System impact: incident was recorded as deliberation evidence but not promoted into a new global writing rule because it was a one-off execution/tooling incident already covered by mutation discipline.

---

## P-20261015-03 — Publication copy exposed research provenance as writing scaffolding

Status: `CLOSED_WITH_READER-VALUE_RULE`
Scope: article prose.

User feedback: publication text should not read like `研报指出 / 公开资料显示` merely to prove research happened.

Diagnosis: research provenance and publication voice were being conflated.

Action: full provenance remains in research/audit evidence, while publication prose removes source-framing unless speaker identity is part of the claim semantics. Deterministic source-leak checks were added.

System impact: source privacy became a publication boundary rather than a superficial style preference.

Evidence: reader-value evolution files and current `references/reader_value.md`.

---

## P-20261015-04 — Reader-value weaknesses: title/opening/H1 hooks, company comparison, information density and section transitions

Status: `CLOSED_AT_RULE/EVAL_LEVEL__LIVE_OBSERVATION_CONTINUES`
Scope: Financial publishing quality.

User feedback exposed several coupled weaknesses: titles and first sentences could feel generic; material-company coverage did not always culminate in a useful named comparison; H1→H2 transitions could be abrupt; information density could be lower than the apparent structure suggested.

Diagnosis: prior quality controls focused more on correctness/compliance than on reader decision utility and continuation value.

Action: introduced publication-source privacy, reader funnel, Company Decision Map/named evidence-bounded comparative verdict, H1 image-safe lead, Broad-as-acquisition-product and interaction-pack semantics. Current rules remain non-actionable and topic-specific.

Verification: regression tests and production CI passed; live article observation remains the real quality judge.

---

## P-20261015-05 — Huangjiu Broad DOCX pushed the risk paragraph onto a nearly empty extra page

Status: `CLOSED_LOCAL_LAYOUT_FIX`
Scope: Word rendering.

Symptom: first Broad render created an unnecessary near-empty fourth page containing the risk paragraph.

Diagnosis: vertical spacing/layout balance, not article-content failure.

Action: compacted Broad vertical spacing only, preserved required typography, rerendered to three pages and reinspected page by page.

Result: final Broad DOCX passed deterministic and visual QA.

System impact: no domain-wide rule added beyond existing render-QA obligations.

---

## P-20261015-06 — Audit DOCX style hierarchy rendered ordinary text like red large headings

Status: `CLOSED_LOCAL_RENDER_FIX`
Scope: audit Word rendering.

Symptom: the first audit-report style mapping made normal text look like red large headings.

Diagnosis: document-style hierarchy error.

Action: rebuilt the audit report hierarchy so only section headings use red 18pt styling, body remains black 13.5pt, rerendered and visually checked.

Result: final audit DOCX passed render inspection.

System impact: local formatting defect; retained as evidence for future document-builder regressions if repeated.

---

## P-20261015-07 — Current-session delivery needed proof beyond durable article state

Status: `CLOSED`
Scope: Huangjiu final delivery.

Symptom/risk: canonical hashes and durable state alone could not prove the three current sandbox files were actually available in this session.

Action: built a fresh visible-delivery receipt against the three current resource paths and canonical SHA-256 identities.

Result: all required outputs verified current and unchanged; no regeneration was required.

System impact: confirmed the earlier visible-delivery architecture on a second real article.

---

## P-20261015-08 — First anti-AI repair itself became a higher-order AI template

Status: `CLOSED_WITH_0.9.1__POST-PROMOTION_OBSERVATION_OPEN`
Scope: Natural Authorial Prose / writing evolution.

User feedback: the initial explanation of how to remove AI flavor still read like a rule-compliant AI answer. The system was replacing one template with another through paragraph-role variation, sentence-shape variation, `verdict -> evidence -> boundary`, and other generation-time prescriptions.

Micro diagnosis: the assistant answered an authorial problem by producing another enumerated rule system.

Assumption challenged: corpus-level AI/human stylometric differences can be translated directly into universal per-article generation instructions.

External research/practitioner review: academic work on post-editing/personal style plus public Writing Skills, Agent workflows and Xiaohongshu-oriented practitioner examples. The useful pattern was voice/material first + distinct critic passes; the negative pattern was humanizer quotas, forced slang/short sentences/emotion/interaction phrases.

Alternatives:
A. add more anti-AI bans/quotas — rejected;
B. voice/material first, AI-pattern diagnosis after drafting — selected;
C. generic draft then humanizer post-pass — rejected as primary strategy.

Action: Financial 0.9.1 made template signals diagnostic rather than generation mandates, prioritized user-approved/edited samples, forbade fabricated human details/platform caricature, made same-model Reader/Editor/Style passes non-independent, and required minimum-effective revision.

Verification: first PR CI failed one newly added brittle exact-string test; that test was corrected to check semantics rather than exact prose. Second candidate CI passed all tests/evals/static audits/wheel/render; production CI #1011 passed. Production commit `d7d1bbe9e662e6d9d3a1f408431f75858b637b19`.

Evidence: `evals/USER_FEEDBACK_SYSTEM_IMPACT_2026-10-15_VOICE_FIRST_ANTI_AI.md` and current `references/reader_value.md`.

---

## P-20261015-09 — Inherited cognition existed, but the assistant still externalized a recoverable dependency to the user

Status: `CURRENT_REPAIR_CANDIDATE`
Failure class: `PROACTIVE_RESOLUTION_GAP`
Scope: Financial evidence/voice resolution; possible UAOS common-capability implication.

Trigger: after promoting voice-first writing, the assistant said that future user-approved/user-edited articles would become the highest-grade voice evidence. The user correctly challenged why the inherited cognition/evolution system did not immediately try to recover or derive usable evidence itself.

Micro diagnosis: the system had a strong **problem-response** contract after a defect was recognized, but no explicit **pre-escalation recovery** obligation when information/preferences were incomplete. The assistant therefore noticed a missing ideal input and converted it into a future user dependency instead of continuing to search existing evidence.

Macro goal: the Agent should reduce user work. Inherited cognition should express itself as autonomous evidence recovery and candidate testing, not merely better reflection after failure.

Assumption challenged: `absence of highest-tier evidence means the next useful action is to wait for the user to provide it`.

Selected repair:
- create `references/proactive_resolution.md`;
- before asking the user for recoverable evidence, inspect current project authority, approved/edited samples already present, durable corrections/rejections, accepted outputs/performance, current context, platform conventions and external method evidence;
- build a provisional evidence-bound candidate with confidence/unknowns/validation plan when safe;
- ask the user only when unresolved alternatives materially change the result or proceeding would invent a fact/preference/approval;
- absence of a perfect voice sample is not a default blocker.

Verification plan: regression test must assert the rule is discoverable from maintenance authority and explicitly forbids turning missing top-tier voice evidence into an automatic user blocker.

System impact: Financial-local behavior fix plus `UAOS_PARENT_GUIDANCE` item below. Do not directly mutate UAOS common authority from the child domain.

---

## P-20261015-10 — Problem history was fragmented across chats, article state and separate eval files

Status: `CURRENT_REPAIR_CANDIDATE`
Failure class: `EVOLUTION_HISTORY_FRAGMENTATION`
Scope: maintenance observability / future parent guidance.

Trigger: user explicitly required every encountered problem and the path taken to be stored together for later total-controller guidance.

Diagnosis: Financial had detailed incident/eval evidence, but no single chronological index. A future controller would need to reconstruct causal history from many files and chat memory, increasing the chance of repeating abandoned ideas or losing why a rule exists.

Action: create this journal as the durable index; keep detailed eval files as evidence authorities; update maintenance guidance so every new problem is appended here, with compact entries for small defects and full chronology for material/systemic/cross-domain events.

Verification plan: repository test checks journal existence, current maintenance pointer and required logging semantics.

System impact: no second state machine or evolution controller; this is an evidence index only.

---

## P-20261015-11 — UAOS entry/version metadata drift was observed

Status: `PARENT_GUIDANCE_OPEN`
Owner: `UAOS`, not Financial.
Scope: parent authority documentation consistency.

Observed issue: during current-session review, an entrypoint/version label was observed as stale relative to `CURRENT_SYSTEM.json` (`CURRENT_SYSTEM` is UAOS 2.5.2). The production controller version remained determinable from `CURRENT_SYSTEM.json`, but stale entry metadata is a maintenance/drift issue.

Financial action: record only; do not mutate parent authority from child context.

Requested parent outcome: total controller should scan current entry/bootstrap/version surfaces for stale release/candidate labels and enforce version-identity consistency after promotion.

Current parent evidence: `D1traverser-debug/universal-agent-os@main:CURRENT_SYSTEM.json` reports `2.5.2`, schema `2.17`, updated `2026-10-15T04:52:00+08:00`.

---

# Parent Guidance Queue

The following items should be presented to UAOS/总控 when the user requests cross-domain guidance:

1. `PROACTIVE_RESOLUTION_GAP` — decide whether all registered child Agents should be required to attempt available-context/evidence recovery before turning a recoverable dependency into a user question or future placeholder.
2. `EVOLUTION_HISTORY_INTERFACE` — decide whether UAOS should define a common child-facing problem/evolution journal schema or merely require each domain to expose one durable evidence index.
3. `VERSION_METADATA_DRIFT` — scan parent bootstrap/entry/release metadata after promotion and add a common consistency check if not already present.
4. `INHERITANCE_BEHAVIOR_VS_DECLARATION` — current contracts prove capability inheritance structurally; parent guidance should consider whether live behavioral probes are required to prove that inherited cognition is actually invoked proactively, not only declared in child capability manifests.

# Current open observation items

- Financial 0.9.1 voice-first writing still requires live article/user observation to prove it reduces rule-compliant AI voice without reducing factual density or company decision utility.
- `P-20261015-09` proactive-resolution repair must pass candidate/production checks before being called promoted.
- provider-attested independent semantic review remains unavailable; same-chat critic passes stay `CHAT_SELF_REVIEW`.
- open-world writing quality is never globally certified by the current finite regression corpus.
