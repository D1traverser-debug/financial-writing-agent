# Financial Writing standalone operation contract

## Business and authority

Only Financial Writing controls its domain tasks, methodology, source checks, Word output and lifecycle. Its canonical manifest is config/FINANCIAL_MANIFEST.json; its authoritative hosted operating Skill is skills/financial-writing-agent/SKILL.md. One current Article Aggregate per task lives at workspaces/articles/<task_id>/STATE.json. No CAOS parent, legacy UAOS runtime, local daemon or independent second task owner is assumed.

## Native input operations

The module financial_writing_agent.standalone_runtime exports observe_article and admit_article_action.

An action proposal requires exactly: schema_version=1.0; domain_id=financial_writing; action_id; task_id; operation; expected_state_blob_sha (null only for CREATE_ARTICLE); parameters.

Operations and business admission:
- CREATE_ARTICLE: accepts prompt, source_refs, target_platforms and optional expressly quoted distribution override; invokes current_admission.build_initial_state.
- CHANGE_REQUIREMENTS: accepts evidence_ref, upserts/retire_ids; invokes current_admission.apply_task_requirement_change and invalidates dependent stage artifacts.
- ADVANCE_STAGE: accepts owner-valid stage artifact, DecisionEnvelope, PrivateResearchBrief, StoryBlueprints, PublicationFitness, review and delivery parameters; invokes current_admission.advance_state. Stage artifacts must exist and match Git Blob SHA.
- ATTACH_FEEDBACK: accepts sample and system_impact; invokes current_admission.attach_material_feedback.
- RESUME_BLOCKED: uses persisted canonical FAIL cursor and repair evidence; replays invalidation before progression.
- RECORD_PROACTIVE_RESOLUTION: records a scoped owner-native recovery attempt, attempted sources, outcome and safety bounds.
- REVIEW_SYSTEM_IMPACT: reviews and closes evidence-bound feedback system impact, preserving immutable prior diagnosis.
- observe_article: read-only, validates the actual article, returns stage, next action, blocked-review recovery cursor, open system-impact summaries, active requirement IDs, revision/digest and output metadata; does not infer independent quality.

Before any current article advances through DELIVERY or FINAL_AUDIT, the same provider artifact_reader must retrieve each required DOCX binary at its article-scoped resource_ref. The port checks the Git Blob SHA, declared SHA-256, canonical file name, unique source path, ZIP/Word XML integrity and opening as a real Word document. This is binary existence and integrity only; per-page visual QA and independent editorial judgment have separate gates.

Every mutation, including recovery and problem governance, requires a caller-supplied **externally authenticated authorization_verifier** returning exactly true, a trusted state reader returning actual raw Git blob content/state/hash, conditional/create-only CAS writer, and second independently fetched readback. Missing/denied permissions, stale SHA, mismatched blob, noncanonical path, missing stage artifact or unknown provider result are NOT a verified completion. Never blindly retry uncertain non-idempotent writes.

Current-stage FAIL must persist a legal revision_target; illegal targets are rejected before CAS. Recovery uses the same canonical state and provider readback, with synthetic negative regression evidence.

This is a Python adapter contract, **not a deployed remote API**. To use it in a chat, the connected Financial app must supply the real provider functions. A model should not promise direct native CLI/plugin invocation merely because the module exists.

## Independent financial business method

Decision loop and execution loop are defined in the standalone Skill and references/maintenance.md. They are concrete Financial behaviors: sourced value-chain and company economics, competing causal theses, 15-module private research, reader-oriented Deep/Broad story selection, source-originality/claim checks, actual Word artifact rendering and feedback-driven improvements. These do not call CAOS. Importing a historical CAOS bridge is forbidden in the standalone runtime.

## Deployment and product acceptance

GitHub CI and a model session are not a full deployed Financial service. A practical standalone connection must verify actual connector availability, user grant, provider CAS on a real sample (no destructive fixtures), source-to-claim evidence and readback of real delivered Word bytes, independently checked pages and editorial/reader acceptance. Current cross-border v3 is still an unfinished research task and cannot be re-labeled accepted. Production incident reports and domain changes are controlled under evals/EVOLUTION_INDEX.json only.

## Owner-intent and domain-method governance extension (2026-11-12)

The standalone `admit_article_action` adds `RECORD_OWNER_INTENT` and a provider-supplied `owner_instruction_reader` callback. A nonbinding item must cite an authenticated user message and is appended to the same article's `intent_history`, without changing `task_requirement_authority`. The existing `CHANGE_REQUIREMENTS` now requires `intent_evidence={intent,source_ref,verbatim_excerpt,classification_reason}` and an authenticated original-message reader with the exact `source_ref`, `source_role=user`, `authenticated_actor`, UTF-8 text and SHA-256. Only USER_REQUIREMENT, USER_CORRECTION or USER_PREFERENCE can activate a scoped requirement. Retire requires USER_CORRECTION. A model-written label, invented chat URL or assistant-role message is rejected before article CAS. Semantic intent ambiguity still requires human/reader adjudication rather than a fabricated machine PASS.

The same Financial-only Python module offers `observe_method_catalog(catalog_reader=...)` and `admit_method_action(request,catalog_reader=...,catalog_cas_writer=...,authorization_verifier=...,promotion_verifier=...,impact_verifier=...)`. A method action has exactly `schema_version,domain_id,action_id,operation,expected_catalog_blob_sha,parameters`; it can write ONLY `knowledge/METHOD_KNOWLEDGE_CATALOG.json`. Parameters include `knowledge_id,proposed_record,decision_envelope,evidence_refs,affected_stages` and optional promotion or impact proof. Permitted operations: CREATE, REVISE, DISCARD_PENDING, PROMOTE, CHALLENGE, RETIRE, RESTORE and VERIFY_IMPACT. A status of ACTIVE requires provider-verified candidate/hash/test review. Impact completion requires provider-verified evidence for every originally affected stage. All writes use exact Git Blob CAS and a second catalog readback. Legacy records are queryable as LEGACY_DECLARED, not automatically certified active. The catalog and its append-only event history are the existing method authority, **not** a second controller or independent task ledger.

These APIs have synthetic provider/eval coverage, not evidence that an end-user Financial ChatGPT plugin or actual authenticated user-message connector is installed. Missing provider authentication fails closed.

## Verified method-use dependency and native replay

When the research DecisionEnvelope explicitly lists exact `METHOD-...` knowledge IDs in `learned_items`, `admit_article_action(ADVANCE_STAGE)` requires an actual `method_catalog_reader` for `knowledge/METHOD_KNOWLEDGE_CATALOG.json`. Each method must be ACTIVE; its effective record SHA and catalog revision are bound to the persisted RESEARCH receipt. Pending, unpromoted revisions do not change effective method bytes and therefore do not invalidate running tasks. Later stage transitions reread the catalog and block if an adopted method was changed/challenged/retired with a corresponding versioned change event; an unrelated catalog entry is ignored.

The same action port supports `REOPEN_METHOD_DEPENDENCY` (no user-supplied rollback target) to reconstruct the earliest affected stage from verified method change events and to invalidate dependent owner artifacts through the existing Financial graph. The old receipt, requirements digest and original task demand remain unchanged. Missing catalog reader, unverifiable change provenance, stale CAS or unneeded reopen are rejected. This is actual provider-bound code and synthetic replay, **not** a claim of a deployed native ChatGPT connector or global discovery of every old article dependency.

## Semantic intent admission and client release boundary (2026-11-12)

Binding CHANGE_REQUIREMENTS requires a provider-signed owner message and a provider-signed explicit approval of the exact canonical mutation. financial_writing_agent/provider_attestation.py verifies HMAC-SHA256 attestations bound to provider ID, audience, authenticated actor, timestamp, nonce, source reference and exact source/mutation digests. The signing key is deployment configuration and is never accepted from model input. The authenticated owner message and stored verbatim excerpt must preserve the complete original user utterance byte-for-byte; selective excerpts are rejected because they can remove negation or scope. The complete utterance is source evidence, not a requirement-template constraint: the AI may propose multiple scoped requirement statements from one complex instruction. The provider must present the entire normalized upsert/retire set and obtain explicit owner approval of that exact canonical mutation; its signature binds the source SHA-256 and full mutation SHA-256, and the article state CAS is bound to the expected prior state SHA. Without that signed approval, no requirement mutation is admitted. Missing key, missing provider, wrong actor, wrong source, wrong mutation, expired signature or incomplete source fails closed before STATE.json changes. The verifier module does not itself authenticate a ChatGPT session or sign messages: a real host provider must perform those operations. Pytest uses synthetic keys and signers only; it is **not live semantic certification**.

The private Financial ChatGPT Skill plugin release is documented at `config/CHATGPT_FINANCIAL_PLUGIN.json`. It was actually created and its archive read back, but does not host a Python/MCP API or independently authorize GitHub. Its creation is **not evidence of user installation or native live execution**. The seven-gate system completion definition and current OPEN evidence are in `evals/FINANCIAL_INDEPENDENT_ACCEPTANCE_REAUDIT_20261112.md` and the machine gate `financial_writing_agent.acceptance_gates`. Run `scripts/system_acceptance_report.py` after engineering tests; it must not promote green CI to system acceptance.


## Signed provider trust boundary and two-phase repository hygiene (2026-11-12)

The current candidate replaces Boolean/callback trust with signed provider attestations for owner messages, exact owner approvals and action authorization. HMAC verification is fail-closed, audience/provider/actor/claim bound and freshness limited. Production still requires a separately deployed host signer that authenticates the actual user and protects keys; the Skill or verifier module cannot manufacture that identity.

The Financial branch archive is deliberately two-phase after an exact manifest: PLAN records all branch names and SHAs; ARCHIVE runs under a full non-main creation/update/deletion freeze and creates immutable archive tags only; PRUNE requires a second reviewer approval after the owner removes only the deletion rule while leaving creation/update frozen. The workflow checks the same manifest SHA and final inventory. See docs/FINANCIAL_BRANCH_ARCHIVE_OPERATOR_SETUP_20261112.md for the live repository state and owner-side prerequisites. The current repository settings are not yet configured, so no destructive prune is authorized.


## System acceptance gate v1.2 — exact evidence binding (2026-11-13)

The system gate evaluator is intentionally stricter than the article action API's unit tests:

- G1 verifies a provider-signed original owner message (source reference, user role, authenticated owner and recomputed UTF-8 SHA-256), then a separate provider-signed explicit owner approval bound to the exact canonical change SHA-256. The confirmation reference must equal the signed approval record reference.
- G5 compares the activated plugin ID and release ID to the exact values in `config/FINANCIAL_MANIFEST.json`; an arbitrary plugin with valid-looking prefixes is not Financial activation.
- G7 requires a complete archive manifest and final inventory digest, verified archive-tag readback, a single remaining `main` branch, active main protection, pull-request-only merges with at least one approval, disabled force pushes/deletion and the required `test` CI status check.

These are externally evidenced release gates, not synthetic self-certification. CI fixtures use test-only signing keys and do not close live gates. The current main branch is still unprotected; no repository-administration setting is changed by this Python acceptance evaluator.
