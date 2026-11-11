# Financial Writing — owner-wide reconstruction audit, 2026-11-11

**Status:** CAOS child-contract R1 implementation and source/identity hardening candidate; **whole-system editorial product NOT_READY**. This is a source-based engineering and product audit, *not* an independent certification of 317 Git tree entries, model cognition, live publication, or readership. No files or configuration in `cognition-agent-os` have been changed.

## Authority and pinned evidence

- Canonical Financial business owner: `D1traverser-debug/financial-writing-agent@main`; baseline `e580cd4dfda8db47674803451c9adfff9e3cf975`. Its `STATE.json` per article owns stage, admitted task requirements and execution receipts. This branch is **non-production**.
- Prior whole-system acceptance owner: `evals/EVOLUTION_INDEX.json#active_system_assessment`; follow `evals/FINANCIAL_WHOLE_SYSTEM_OWNER_REVIEW_20261018.md` R0–R6 rather than creating another canonical state/evolution index.
- Current source/contract authority: `docs/product_requirements.md`, `docs/architecture.md`, `config/EXECUTION_CONTRACT.json`, `financial_writing_agent/current_admission.py`, and real current article state.
- `workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json` is **IN_PROGRESS / RESEARCH**, with two admitted source-bound user requirements, no stage artifacts and no admitted quality evidence. Its v2 predecessor is marked `MIGRATED_HISTORY`. The 2026-10-16 rejection remains negative evidence, not confirmation that newer semantic gates have passed.
- `evals/quality_regression.json`: `GENERAL_EDITORIAL_QUALITY=NOT_READY__HELDOUT_DIVERSITY_INSUFFICIENT`, `PERSONALIZED_WRITING_DNA=NOT_READY`; only the named negative Deep and a separate held-out Deep baseline are recorded. No Broad editorial-quality or current-kernel reader-success claim is authorized.
- The original baseline `.uaos` manifests pointed to legacy UAOS; the current candidate now replaces the operative declarations with CAOS, assigns `CAOS_SKILL.md` as canonical child entry, and adds an owner-native `caos_bridge.py` for guarded write/CAS/readback. The **real pinned CAOS `domain_contract._native_contract`** has passed cross-repository CI conformance and sees no legacy-parent declaration. This verifies static read-only parent discovery, **not** live ChatGPT invocation or installed CAOS Host action. CAOS source/config is unchanged.

## Audit matrix and observed assurance limits

| Surface | Real owner/interface | Evidence now | Open failure or acceptance gap |
|---|---|---|---|
| User goal and corrections | `task_requirements.py`, `current_admission.py` | Revision, digest, stage-bound satisfaction | Natural-language extraction and actual requirement-to-published-text fidelity unverified |
| Runtime, task identity, workflow | `owner_guard.py`, `current_admission.py`, `workflow_spec.py` | One Article Aggregate, 10-stage graph, receipts and historical-resume gate | Reproduce current-source bypasses and actual provider CAS; no universal tool interception |
| Source discovery and economics | `private_research.py`, `schemas.py` | Mandatory 15-module research brief 1.1 and claim/coverage schema | Nonempty source-reference strings are not independently checked source facts; live dates/quotes must be verified |
| Causal decision/research competition | `cognition_governance.py` | DecisionEnvelope, competing candidates and saturation representation | A populated schema does not prove source-search completeness or proper causal inference |
| Reader article design | `story_quality.py`, `writing_kernel.py` | Blueprint + focused passes + eight fitness gates | No current-kernel end-to-end article independently accepted; no proven higher retention |
| Financial accuracy and compliance | `checks.py`, policy | Mechanical redlines and named gates | Actual issuer/company/market/regulatory facts still require point-in-time primary-source checks |
| Authorship/originality | `story_quality.py`, style reference | Text-evidence rubric and original-source comparison contract | Same-model audit is not independent plagiarism or voice certification |
| Deep/Broad/interaction | task contract, references, document builder | Separate modes, complete private vs selective public research | Broad quality not admitted; writing passes are declarative rather than a proven autonomous model runtime |
| DOCX bytes, render, availability | `delivery_pipeline.py`, `delivery_availability.py` | Canonical builder receipt, hash, current-resource callback and final presentation check | Render/visual PASS flags are caller-provided; no independent actual visual-readback guarantee from string flags |
| Durable revisions and learning | article state, `EVOLUTION_INDEX.json`, knowledge catalog | Versioned history and method cases | Real negative transfer, future-task improvement, owner correction burden not measured |
| Parent/control activation | `.uaos`, `UAOS_SKILL.md` | Historical pointer-only metadata | Old parent references do not automatically route through CAOS; no real native ChatGPT CAOS→Financial trace |
| Release and security | pytest/CI, GitHub | Baseline `main` Actions success at `39124790615` | CI is engineering assurance, not a live publication/reader result; branch protection and all native tool writes not proven |

## R1 common-path cause and repair

**Observed source defect (baseline `main@e580cd4`):** `owner_guard._validate_artifact_ref` accepted a stage artifact when its raw string began with `workspaces/articles/<task_id>/`; it did not reject parent traversal, ambiguous path segments or backslashes. New `task_id` required only a nonempty string, and `artifact_hygiene` did not independently bind a migrated manifest's declared successor to its authority path. Presentation filenames were not constrained to basenames.

These are **identity and provenance boundary defects**. They may allow aliasing and false attribution in subsequent path handling; whether a specific remote write could have escaped was not demonstrated. The repair reuses the one Financial state owner and introduces a small shared, pure POSIX-path canonicalizer (no alternate DB/controller):

- `financial_writing_agent/path_identity.py`: one canonical article slug, relative Git path, workspace-ref and basename policy.
- `owner_guard.py`: use it for new/current article identities, stage refs and delivery metadata.
- `artifact_hygiene.py`: enforce canonical artifact manifest paths, exactly one current STATE authority, and exact migrated successor mapping.
- `delivery_availability.py`: enforce same identity and presentation filename policy.
- `tests/test_financial_identity_boundaries_20261111.py`: targeted malicious input/neighbor cases and legal canonical controls.

**Disconfirming tests:** historical article IDs wrongly rejected; valid migrated history rejected; legal Word basenames rejected; blocked unsafe aliases admitted; another public mutation surface bypassing these checks. All are merge blockers until exact-head CI and a source-bound review pass. No current article `STATE.json` or historical receipt is rewritten.

## Competing explanations and architecture choice

1. **Insufficient rule/prompt volume:** contradicted as sole root by extensive existing contracts plus a real rejected Word deliverable. Repeating more anti-AI phrases risks template prose.
2. **Weak artifact/identity boundary:** concretely evidenced by the source predicates above. Chosen narrow shared invariant, not a new orchestration platform.
3. **Weak source→claim→published assertion verification:** supported by nonempty-reference validation and absence of independently witnessed end-to-end articles. Requires genuine source/claim/readback experiments, not more JSON fields.
4. **Research/publication confusion:** historically confirmed; current `CORE/SUPPORT/OMIT_WITH_REASON` and `EVENT_TO_COMPANY` contracts address the mechanism, yet current actual task replay remains open.
5. **Lack of model/tool execution:** `pyproject.toml` publishes no runnable agent CLI or MCP server; declarative passes do not prove native model execution. Do not solve by declaring a new agent/controller in documentation.
6. **Full rewrite versus bounded refactor:** rewriting state/permissions and historical receipts has high migration cost without evidence of better reader outcomes. Retain one Article Aggregate and compare end-to-end articles before choosing large replacement.
7. **Parent rename as 'integration':** reject; editing a manifest pointer without verified CAOS native client/tool round trip is a false completion claim.
8. **CI means product ready:** contradicted by `quality_regression.json`, actual owner rejection, and current v3 empty quality evidence.

**Selection:** maintain and harden current single Financial business owner, solve cross-entry shared defects, then validate a real current-kernel article against independent original facts, effective story alternatives, genuinely rendered downloadable Word resources, and audience/user evidence. No automatic promotion from unit tests.

## Remaining product acceptance (not claimed complete)

- **R1 structural:** exact-head CI for the final candidate, current/legacy and path-adversarial tests, actual new-task and delivery-state readback; ensure real CAOS parent `domain_contract` sees zero legacy binding. The pinned-parent native test passed in CI #42981344176 at `56553f3`, but new commits need a new exact-head CI and real native provider permissions remain separately gated.
- **R2 real owner outcome:** independently verify current cross-border sources and the user's preserved full-universe/Deep requirement, create admitted current DecisionEnvelope and private research 1.1, independently assess distinct Deep/Broad, build/render/re-read DOCX, and get owner/product acceptance. Preserve v3 RESEARCH without fake advancement.
- **R3 editorial eval:** real negative and diverse unseen heldout cases for each requested mode, evidence-bound candidate-vs-baseline and position swaps, positive audience/user case when available; do not manufacture grading events or claim DNA ready.
- **R4 source-to-paragraph:** verify claims, original timestamps and company financial mechanisms against primary documents, bind significant requirements to actual output paragraphs with negative source-drift tests.
- **R5 architecture:** compare measurable owner time, regressions, cognitive tokens, latency and quality for existing vs simplified pass/control arrangements before removing compatibility; mechanically generated policy mirrors are not extra policy owners.
- **R6 production:** scoped review, exact-head CI, authorized merge/readback and real native fresh-session delivery. No deploy/account/plugin actions without authorization.

No fixed percentage is warranted. Stopping at this source/CI level yields **R1 candidate only, product still NOT_READY**.

## 2026-11-11 implementation reconciliation

Read-only CAOS parent implementation examined: `cognition-agent-os@9686ced:src/cognition_agent_os/domain_contract.py`, including its hardcoded `.uaos` protocol paths, `_native_contract` cross-file identity/legacy-parent checks, `CHILD_CONTRACT_OBSERVATION_V1` and explicit no-business-approval flags. Child response is not a parent grant. This report's initial pre-migration risk description is historical baseline evidence and is superseded by the current branch readback.

Current candidate modifies only the Financial child: (1) CAOS Manifest, Adapter, Capabilities, `config/EXECUTION_CONTRACT.json`, canonical `CAOS_SKILL.md`, legacy pointer/discovery references; (2) owner-native `caos_bridge.py` with mandatory external grant, single current aggregate, CAS and independent readback; (3) shared article/path/Word output identity checks and adversarial tests; (4) mirrored knowledge/maintenance references, audit scripts and existing regression assertions; (5) CI's actual pinned CAOS parent code conformance, wheel and DOCX smoke; (6) this report and existing `EVOLUTION_INDEX.json` under a single Financial evolution owner.

**Important residual distinction:** even perfect code/CI cannot establish the article's narrative/retention quality, real company-source correctness, the user's later private-report vs Deep-appendix wording conflict, an installed native ChatGPT CAOS Skill, or a real external grant. The v3 cross-border task remains RESEARCH, its historical explicit requirement identifiers are not deleted or quietly replaced, and any later correction must enter owner-native requirement admission with versioned evidence instead of rewriting history.

## R1 → R2 additional source-real defects fixed in this candidate

### A. Missing PRIVATE_RESEARCH_SYNTHESIS from the actual work graph

**Direct code evidence:** before repair, `financial_writing_agent/writing_kernel.py::WritingPass` and `PASS_DEPENDENCIES` had `RESEARCH_ADVERSARIAL → THESIS_ADJUDICATION` with no `PRIVATE_RESEARCH_SYNTHESIS`; yet both `docs/product_requirements.md` and `docs/architecture.md` required private synthesis before adjudication, and current `current_admission` had the separate private brief 1.1 stage gate. Hypothesis “just more drafting rules” does not explain a missing graph dependency; “mandatory form alone guarantees internal order” is false. **Fix:** add the explicit pass contract, evidence inputs and output, and require it upstream of thesis. Update `config/EXECUTION_CONTRACT.json#internal_passes` and executable graph parity regression. Syntactic pass presence is not semantic source verification.

### B. Global Deep company coverage defeated editorial selectivity

**Direct code evidence:** `checks.py::check_deep_company_grounding` previously emitted an omission error for **every** MATERIAL researched company absent from public Deep, regardless of the article’s `StoryBlueprint.publication_scope_decisions` and the product mandate to separate complete private research from reader-oriented selective public content. Concurrent `config/policy.json` and packaged policy declared `finance_deep_material_complete=true` and all MATERIAL company mentions required, contradicting `docs/product_requirements.md` scope accounting. The real user also has specific tasks that can require visible complete retained universe; these exceptions must not be lost. **Selected repair:** policy 0.9.2, research complete, editorial selective by default, with `CORE/SUPPORT/OMIT_WITH_REASON` as the publication-scope condition; `check_deep_company_grounding(..., require_complete_material_universe=True)` remains available to explicitly admitted, currently authoritative task-specific obligations. A generic utility check still demands named comparative discussion for material multi-company research. Negative and neighbor controls verify default omission is legal while the explicit strict mode rejects it. No historical v3 requirement silently edited.

### C. Shallow named-company verdict falsely passed mechanical decision guard

**Reproduced negative:** “甲公司有优势，乙公司也不错。” satisfied the original company-comparison regular expression because a generic comparative word and two company names were treated as a meaningful financial verdict. **Selected bounded tripwire:** `check_company_decision_utility` now requires a financial/business-mechanism signal as well as named companies and comparative language, with positive and negative tests. This is an improvement in mechanical resistance to empty company lists, **not** evidence that the model independently checked true causal explanations, audited source citations, reader interest or economic exposure. Those require actual cited content review and withheld/real-user cases.

### Scope and independent assurance decision

The changes repair real causal mismatches across contracts, policy, graph and current checks. Existing source/factual evidence, story choice, 15-module private research depth, the active cross-border requirement conflict, live artifact presentation and publication outcomes remain separate open acceptance tasks. Finite promotion gate: current PR head CI including real CAOS parent remote GitHub observation, complete old/new pytest and DOCX render; then controlled **Financial** merge and production readback. No CAOS file mutation or claim of whole-system editorial quality.

## Verified initial production release and superseded candidate comparison

**Promoted Financial main:** `9bf0cc4e90b124eb0b730c255722354dbd2dea1f`, PR #52, merged 2026-11-11. Candidate head `03fa630747225e867d593b03e2ce496551a362c5` passed GitHub Actions #42983168142; production head passed #42983349995. Both included real pinned CAOS parent code and remote exact-commit Financial source reobservation, full pytest, contract/static audits, installed-wheel smoke and LibreOffice DOCX render smoke. Reobserved CAOS `main@9686cedeb3fd8171ecf70eab33aaea641217b04a` unchanged. This is **production engineering assurance** only.

**Retired-era branch comparison:** old Financial PR #37 proposes a broad `schema_version=1.3` and mandatory GitHub network source resolution inside every in-process owner state validator. That route adds authenticated boundary checks but also introduces runtime/network coupling, a migration burden to current task-requirement authority/private research 1.1 and risks duplicating current Article Aggregate pathways if cherry-picked blindly. Current CAOS-originated mutations instead enter an explicit external-grant + owner-native aggregate + provider CAS + independent readback bridge; the general out-of-band GitHub permission/host-complete-mediation limitation remains outside what any child Python library can physically enforce. One demonstrably reusable guard from the historical branch, **type-strict JSON equality**, is adopted in a small post-production follow-up test to prevent Python `0 == False` readback confusion. Historical PR #37 remains provenance of alternative attempts, not a current production authorization.

Old PR #49 bound a Financial persistent-asset profile to the **retired UAOS** `PERSISTENT_ASSET_POLICY.json`; its controller pointer cannot be merged unchanged after the CAOS migration. Durable article state remains exclusively Financial GitHub `STATE.json`; Notion and Drive legacy files are research/historical evidence, not a second current controller. Do not treat the obsolete PR as a hidden active governance plane.

**R2-R6 reality:** no real current-kernel article has yet been independently accepted by an editor/user, the v3 cross-border scope correction and fresh research audit are not published, and zero measured reading-retention or audience-success results are recorded. These facts remain `NOT_READY` notwithstanding confirmed code promotion. Hosted ChatGPT CAOS invocation is not proven simply by the imported parent read-only contract.

## External asset governance adoption after CAOS production

Old Financial PR #49 was an unmerged UAOS-specific asset profile. The original inventory of Chat/Memory, Notion ArticleBase/IndustryBase, migrated Notion controls, retired Google Drive continuity, Library Word deliverables, notifications, automation and temporary sandbox had operational value, but its hard dependency on `universal-agent-os@main:config/PERSISTENT_ASSET_POLICY.json` was not valid under CAOS and risked restoring a second parent. The **bounded selected reuse** is `config/PERSISTENT_ASSET_PROFILE.json` version 2.0: exactly one current GitHub Financial authority, external surfaces classified as data/reference/history/delivery only, and an explicit boundary saying the child cannot physically intercept account Memory, permissions or native ChatGPT storage. Historical automation is UNVERIFIED rather than asserted current. The profile does not claim parent-hosted asset CRUD or copy old UAOS policy. CI and targeted tests cross-check singular authority, absent control-plane claims and current CAOS parent identity. No Notion, Drive, Memory or CAOS mutation accompanies this adoption.
