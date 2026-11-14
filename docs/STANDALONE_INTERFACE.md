# Financial Writing standalone operation contract

## Business and authority

Only Financial Writing controls its domain tasks, methodology, source checks, Word output and lifecycle. Its canonical manifest is config/FINANCIAL_MANIFEST.json; its canonical operating Skill source is skills/financial-writing-agent/SKILL.md. One current Article Aggregate per task lives at workspaces/articles/<task_id>/STATE.json. No external parent runtime, local daemon or second task owner is required.



## Canonical file and CRUD map

- Operating entry: `skills/financial-writing-agent/SKILL.md`.
- Domain authority: `config/FINANCIAL_MANIFEST.json`, `config/FINANCIAL_CAPABILITIES.json` and `config/EXECUTION_CONTRACT.json`.
- Data/file map: `config/DATA_AUTHORITY.json`.
- Article business state: one `workspaces/articles/<task_id>/STATE.json` per task. It binds requirements, current stage, artifact identities, execution receipts, intent history and recovery status.
- Article files: `research/`, `editorial/`, `stages/`, `reviews/`, `delivery/` and `feedback/` live beneath the same task directory. Do not create a global article index or store an article's current state in a separate database.
- Method CRUD: `knowledge/METHOD_KNOWLEDGE_CATALOG.json` is the only reusable-method store. Revisions are staged; retirement preserves history; promotion and impact closure require evidence.
- System evolution: `evals/EVOLUTION_INDEX.json` is the current system status/evolution index; `evals/quality_regression.json` is the quality baseline.
- Policy/reference content has two synchronized copies only: the Skill modules under `skills/financial-writing-agent/references/` and the Python package modules under `financial_writing_agent/resources/references/`.

## Human interaction and authorization

Recover the complete user request and available corrections before asking follow-up questions. Distinguish binding requirements from preferences, ideas, issue reports and questions. Use reversible defaults for non-material ambiguity; ask one focused question only when ambiguity changes the outcome or safety boundary. Show the complete normalized requirement change and obtain explicit owner confirmation in the current conversation before a binding write. Preserve prior receipts and read back every GitHub mutation by exact content/blob identity. If the connected GitHub provider cannot perform a required write, mark only that action OPEN and continue safe work.

## Financial native client and one executable owner-effect boundary

**Read-only client:** ChatGPT following the Financial Skill can observe `main`, recover original user requirements and previous task state, retrieve sources, prepare research, draft articles and stage reversible candidate files. The GitHub connector authenticates transport permissions, **not** that Python's current-admission code executed or that the user approved the exact semantic mutation. No external CAOS parent/Host/controller is needed.

**Side effects:** Work that changes the authoritative article `STATE.json`, its bound stage files or the method catalog must be admitted by the existing `financial_writing_agent.standalone_runtime` authenticated Python port **or** be submitted on a candidate branch whose exact `base.sha` → `head.sha` data change is revalidated by `scripts/system_acceptance_report.py` in CI. The latter now uses `financial_writing_agent.whole_system_assurance.audit_repository_business_changes` and the owner validators: it forbids unsigned/self-attested state rewrites, unbound artifact-only edits and migrated-history modifications. It also requires append-only method governance evidence. A direct GitHub update to unprotected `main` is **not** an approved business execution route; CI observation is not the same as enforced branch protection.

**Operational order:** (1) read exact current `main` SHA and required original user evidence; (2) classify intent and build a bounded candidate without altering canonical owner data; (3) for effectful article/method actions obtain real provider signatures and, where needed, the owner's confirmation of the entire normalized change; (4) submit candidate branch/PR and run exact-base/head admission; (5) on fully green relevant gates, advance the existing authoritative `main` by reviewed merge; (6) read back actual resulting blob, provider effect and deliverables. Stale CAS/revoked authority/unknown outcomes require reconciliation rather than blind retries.

**Unavailable external provider:** A native Skill-only session cannot run local Python or create the required independent owner signature. If no authenticated port/signing provider is actually connected, **do not fabricate receipt IDs or treat current-chat consent as a provider signature**. Mark only the affected canonical state/method mutation OPEN and continue research, candidacy and other non-effectful tasks. Full end-to-end user outcome stays NOT_READY until the real client passes the live port checks.

No second task ledger is introduced: `workspaces/articles/<task_id>/STATE.json`, `knowledge/METHOD_KNOWLEDGE_CATALOG.json`, `evals/EVOLUTION_INDEX.json` and `docs/product_requirements.md` remain the sole respective authorities. Candidate branches are disposable implementation vehicles, not additional business owners.

## Optional Python provider-adapter contract

The module financial_writing_agent.standalone_runtime exports observe_article and admit_article_action.

An action proposal requires exactly: schema_version=1.0; domain_id=financial_writing; action_id; task_id; operation; expected_state_blob_sha (null only for CREATE_ARTICLE); parameters.

Operations and business admission:
- CREATE_ARTICLE: accepts prompt, source_refs, target_platforms and optional expressly quoted distribution override; invokes current_admission.build_initial_state.
- CHANGE_REQUIREMENTS: accepts evidence_ref, upserts/retire_ids; invokes current_admission.apply_task_requirement_change and invalidates dependent stage artifacts.
- ADVANCE_STAGE: accepts owner-valid stage artifact, DecisionEnvelope, PrivateResearchBrief, StoryBlueprints, PublicationFitness, review and delivery parameters; invokes current_admission.advance_state. Stage artifacts must exist and match Git Blob SHA. Due requirement satisfaction must reference the current stage artifact plus provider-read source snapshots; unread references are rejected. On FINAL_AUDIT only, `supplemental_delivery_artifacts` supplies required private research Word resources.
- ATTACH_FEEDBACK: accepts sample and system_impact; invokes current_admission.attach_material_feedback.
- RESUME_BLOCKED: uses persisted canonical FAIL cursor and repair evidence; replays invalidation before progression.
- RECORD_PROACTIVE_RESOLUTION: records a scoped owner-native recovery attempt, attempted sources, outcome and safety bounds.
- REVIEW_SYSTEM_IMPACT: reviews and closes evidence-bound feedback system impact, preserving immutable prior diagnosis.
- observe_article: read-only, validates the actual article, returns stage, next action, blocked-review recovery cursor, open system-impact summaries, active requirement IDs, revision/digest, output metadata and persisted visible-delivery status; does not infer independent quality.

Before any current article advances through DELIVERY or FINAL_AUDIT, the same provider artifact_reader must retrieve each required DOCX binary at its article-scoped resource_ref. The port checks the Git Blob SHA, declared SHA-256, canonical file name, unique source path, ZIP/Word XML integrity and opening as a real Word document. Current FINANCE_DEEP_DOCX and FINANCE_BROAD_DOCX must also carry task-scope and claim-trace evidence bound to the current requirement digest and exact DRAFT artifact. The runtime validates current-session canonical build evidence and actual rendered-page inspection before the state write.

Before both DELIVERY and FINAL_AUDIT writes, the runtime revalidates the seven-day research brief/source freshness window and requires current source-body hashes to match the admitted RESEARCH receipt; stale or changed source bytes require a RESEARCH replay. Before FINAL_AUDIT terminal CAS, the runtime rereads the exact RESEARCH and DRAFT artifact bytes and calls `delivery_availability.build_visible_delivery_receipt`. If the current state contains an admitted PrivateResearchBrief, the request must include `parameters.supplemental_delivery_artifacts` with a source-bound, current-session `PRIVATE_RESEARCH_DOCX`. The visible resource set must exactly match core outputs plus required supplements; every file must be provider-read, hash/Word validated and backed by current delivery evidence. The persisted `VISIBLE_DELIVERY_READY` receipt means current-session presentability only, not semantic entailment, independent editorial acceptance or reader outcome.

Every mutation through this optional Python adapter, including recovery and problem governance, requires a caller-supplied **externally authenticated authorization_verifier** returning a provider-signed attestation. `verify_action_authorization` checks provider, audience, authenticated actor, operation/task/action, full request digest, expected prior state SHA, nonce and freshness; a Boolean `true` is not authorization. The host must protect signing keys outside model-visible input. A trusted state reader must return actual raw Git blob content/state/hash, the conditional/create-only CAS writer must return the exact new Blob SHA, and a second independent readback must match the candidate. Missing/denied permissions, stale SHA, mismatched blob, noncanonical path, missing stage artifact or unknown provider result are NOT a verified completion. Never blindly retry uncertain non-idempotent writes.

Current-stage FAIL must persist a legal revision_target; illegal targets are rejected before CAS. Recovery uses the same canonical state and provider readback, with synthetic negative regression evidence.

This section documents the signed Python admission contract. The native Skill route alone is a research/candidate client, not an interchangeable trusted executor. Execute the Python port only when genuinely installed and authenticated; otherwise the exact-base/head CI guard remains fail-closed for missing signed business effects.

## Independent financial business method

Decision loop and execution loop are defined in the standalone Skill and skills/financial-writing-agent/references/maintenance.md. They are concrete Financial behaviors: sourced value-chain and company economics, competing causal theses, 15-module private research, reader-oriented Deep/Broad story selection, source-originality/claim checks, actual Word artifact rendering and feedback-driven improvements. These are implemented inside Financial and do not call an external parent runtime. No parent bridge is part of the active package; current Financial admission rejects legacy parent-upcall dispositions.

## Deployment and product acceptance

GitHub CI and a model session are not a full deployed Financial service. A practical standalone connection must verify actual connector availability, user grant, provider CAS on a real sample (no destructive fixtures), source-to-claim evidence and readback of real delivered Word bytes, independently checked pages and editorial/reader acceptance. Current cross-border v3 is still an unfinished research task and cannot be re-labeled accepted. Production incident reports and domain changes are controlled under evals/EVOLUTION_INDEX.json only.

## Owner-intent and domain-method governance extension (2026-11-12)

The standalone `admit_article_action` adds `RECORD_OWNER_INTENT` and a provider-supplied `owner_instruction_reader` callback. A nonbinding item must cite an authenticated user message and is appended to the same article's `intent_history`, without changing `task_requirement_authority`. The existing `CHANGE_REQUIREMENTS` now requires `intent_evidence={intent,source_ref,verbatim_excerpt,classification_reason}` and an authenticated original-message reader with the exact `source_ref`, `source_role=user`, `authenticated_actor`, UTF-8 text and SHA-256. Only USER_REQUIREMENT, USER_CORRECTION or USER_PREFERENCE can activate a scoped requirement. Retire requires USER_CORRECTION. A model-written label, invented chat URL or assistant-role message is rejected before article CAS. Semantic intent ambiguity still requires human/reader adjudication rather than a fabricated machine PASS.

The same Financial-only Python module offers `observe_method_catalog(catalog_reader=...)` and `admit_method_action(request,catalog_reader=...,catalog_cas_writer=...,authorization_verifier=...,promotion_verifier=...,impact_verifier=...)`. A method action has exactly `schema_version,domain_id,action_id,operation,expected_catalog_blob_sha,parameters`; it can write ONLY `knowledge/METHOD_KNOWLEDGE_CATALOG.json`. Parameters include `knowledge_id,proposed_record,decision_envelope,evidence_refs,affected_stages` and optional promotion or impact proof. Permitted operations: CREATE, REVISE, DISCARD_PENDING, PROMOTE, CHALLENGE, RETIRE, RESTORE and VERIFY_IMPACT. A status of ACTIVE requires provider-verified candidate/hash/test review. Impact completion requires provider-verified evidence for every originally affected stage. All writes use exact Git Blob CAS and a second catalog readback. Legacy records are queryable as LEGACY_DECLARED, not automatically certified active. The catalog and its append-only event history are the existing method authority, **not** a second controller or independent task ledger.

These APIs have synthetic provider/eval coverage, not proof of a deployed ChatGPT client. Current conversation text and owner confirmation are required inputs but not substitutes for a signed binding-approval provider or executable business-state admission. The Skill plugin still requires the user to install/select it and connect the existing GitHub provider in a fresh session.

## Verified method-use dependency and native replay

When the research DecisionEnvelope explicitly lists exact `METHOD-...` knowledge IDs in `learned_items`, `admit_article_action(ADVANCE_STAGE)` requires an actual `method_catalog_reader` for `knowledge/METHOD_KNOWLEDGE_CATALOG.json`. Each method must be ACTIVE; its effective record SHA and catalog revision are bound to the persisted RESEARCH receipt. Pending, unpromoted revisions do not change effective method bytes and therefore do not invalidate running tasks. Later stage transitions reread the catalog and block if an adopted method was changed/challenged/retired with a corresponding versioned change event; an unrelated catalog entry is ignored.

The same action port supports `REOPEN_METHOD_DEPENDENCY` (no user-supplied rollback target) to reconstruct the earliest affected stage from verified method change events and to invalidate dependent owner artifacts through the existing Financial graph. The old receipt, requirements digest and original task demand remain unchanged. Missing catalog reader, unverifiable change provenance, stale CAS or unneeded reopen are rejected. This is actual provider-bound code and synthetic replay, **not** a claim of a deployed native ChatGPT connector or global discovery of every old article dependency.

## Semantic intent admission and client release boundary (2026-11-12)

The HMAC rules apply to the executable Python provider adapter and signed owner-state CI admission. The active ChatGPT Skill path uses the complete user message and explicit confirmation to prepare a candidate but does not perform a binding main mutation without authenticated effect admission. Binding CHANGE_REQUIREMENTS through the optional Python adapter requires a provider-signed owner message and a provider-signed explicit approval of the exact canonical mutation. financial_writing_agent/provider_attestation.py verifies HMAC-SHA256 attestations bound to provider ID, audience, authenticated actor, timestamp, nonce, source reference and exact source/mutation digests. The signing key is deployment configuration and is never accepted from model input. The authenticated owner message and stored verbatim excerpt must preserve the complete original user utterance byte-for-byte; selective excerpts are rejected because they can remove negation or scope. The complete utterance is source evidence, not a requirement-template constraint: the AI may propose multiple scoped requirement statements from one complex instruction. The provider must present the entire normalized upsert/retire set and obtain explicit owner approval of that exact canonical mutation; its signature binds the source SHA-256 and full mutation SHA-256, and the article state CAS is bound to the expected prior state SHA. Without that signed approval, no requirement mutation is admitted. Missing key, missing provider, wrong actor, wrong source, wrong mutation, expired signature or incomplete source fails closed before STATE.json changes. The verifier module does not itself authenticate a ChatGPT session or sign messages: a real host provider must perform those operations. Pytest uses synthetic keys and signers only; it is **not live semantic certification**.

The private Financial ChatGPT Skill plugin release is documented at `config/CHATGPT_FINANCIAL_PLUGIN.json`. It was actually created and its archive read back, but does not host a Python/MCP API or independently authorize GitHub. Its creation is **not evidence of user installation or native live execution**. The seven-gate system completion definition and current OPEN evidence are in `evals/FINANCIAL_INDEPENDENT_ACCEPTANCE_REAUDIT_20261112.md` and the machine gate `financial_writing_agent.acceptance_gates`. Run `scripts/system_acceptance_report.py` after engineering tests; it must not promote green CI to system acceptance.


## Signed provider trust boundary and two-phase repository hygiene (2026-11-12)

The signed provider trust boundary below applies to the optional Python adapter, not the active ChatGPT-native GitHub connector path. The current candidate replaces Boolean/callback trust with signed provider attestations for owner messages, exact owner approvals and action authorization. HMAC verification is fail-closed, audience/provider/actor/claim bound and freshness limited. Production still requires a separately deployed host signer that authenticates the actual user and protects keys; the Skill or verifier module cannot manufacture that identity.

The Financial branch archive is deliberately two-phase after an exact manifest: PLAN records all branch names and SHAs; ARCHIVE runs under a full non-main creation/update/deletion freeze and creates immutable archive tags only; PRUNE requires a second reviewer approval after the owner removes only the deletion rule while leaving creation/update frozen. The workflow checks the same manifest SHA and final inventory. See docs/FINANCIAL_BRANCH_ARCHIVE_OPERATOR_SETUP_20261112.md for the live repository state and owner-side prerequisites. The current repository settings are not yet configured, so no destructive prune is authorized.


## System acceptance gate v1.2 — exact evidence binding (2026-11-13)

The system gate evaluator is intentionally stricter than the article action API's unit tests:

- G1 verifies a provider-signed original owner message (source reference, user role, authenticated owner and recomputed UTF-8 SHA-256), then a separate provider-signed explicit owner approval bound to the exact canonical change SHA-256. The confirmation reference must equal the signed approval record reference.
- G5 compares the activated plugin ID and release ID to the exact values in `config/FINANCIAL_MANIFEST.json`; an arbitrary plugin with valid-looking prefixes is not Financial activation.
- G7 requires a complete archive manifest and final inventory digest, verified archive-tag readback, a single remaining `main` branch, active main protection, pull-request-only merges with at least one approval, stale approvals dismissed on new pushes, approval of the latest reviewable push, administrator enforcement, up-to-date `test` CI, and force-push/deletion disabled.

These are externally evidenced release gates, not synthetic self-certification. CI fixtures use test-only signing keys and do not close live gates. The current main branch is still unprotected; no repository-administration setting is changed by this Python acceptance evaluator.

## Signed action-effect receipt contract v1.0 (2026-11-14)

A signed action-authorization receipt proves that a trusted provider authorized a request against a prior state SHA. It does **not**, by itself, prove which exact state bytes the authorized action produced. The article write path therefore uses two linked receipts:

- The appended STATE.json execution receipt carries authorization_contract_version=1.1, the provider-signed authorization_verification, effect_contract_version=1.0, and the exact effect_receipt_ref.
- workspaces/articles/<task_id>/actions/<action_id>.effect.json carries a provider-signed action_effect attestation. Its claims bind the exact action/task/operation, prior state Git blob SHA (or NEW_FILE), resulting state Git blob SHA, canonical request SHA-256, exact authorization-attestation SHA-256, contract version and admission runtime.

The action-effect attestation must use the same authenticated actor and provider as the action authorization. The state and effect receipt are written in one atomic Git tree/commit/CAS operation; the provider then reads back both exact blobs. The runtime independently recomputes the state blob SHA, verifies the effect signature and claim bindings, and checks that the latest effect result SHA equals the current state SHA. A commit URL, a successful write response, a state-only readback or a model-authored receipt is not a substitute.

The optional Python adapter now requires bundle_cas_writer, effect_attestation_signer and effect_receipt_reader for article mutations. The legacy single-file cas_writer callback is not sufficient to admit a state mutation. observe_article requires the effect-receipt reader whenever it encounters a v1.1 action receipt and verifies the complete persisted authorization/effect chain. A missing, altered, replayed, wrong-provider, wrong-actor or discontinuous effect receipt fails closed.

Historical signed authorization contract v1.0 remains readable as legacy_effect_unbound_receipts; historical bytes are not rewritten or retroactively certified. Once an article has an effect-bound v1.1 receipt, a later v1.0 or unsigned receipt cannot roll the history back. New mutations must use v1.1 authorization plus v1.0 effect receipt.

The PR audit reads the exact before/after Git blobs. A new article-state mutation must include a new, create-only effect receipt in the same candidate revision, and the signature must bind the resulting STATE.json bytes in that revision. This audit is an additional deterministic guard, not branch protection or live provider proof. Synthetic pytest signers and CI prove code behavior only; the live user-authenticated signer, atomic Git provider and independent business/editorial outcomes remain separate OPEN gates.
