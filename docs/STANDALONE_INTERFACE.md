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
- observe_article: read-only, validates the actual article, returns stage, revision, digest and output metadata; does not infer independent quality.

Every mutation, including recovery and problem governance, requires a caller-supplied **externally authenticated authorization_verifier** returning exactly true, a trusted state reader returning actual raw Git blob content/state/hash, conditional/create-only CAS writer, and second independently fetched readback. Missing/denied permissions, stale SHA, mismatched blob, noncanonical path, missing stage artifact or unknown provider result are NOT a verified completion. Never blindly retry uncertain non-idempotent writes.

Current-stage FAIL must persist a legal revision_target; illegal targets are rejected before CAS. Recovery uses the same canonical state and provider readback, with synthetic negative regression evidence.

This is a Python adapter contract, **not a deployed remote API**. To use it in a chat, the connected Financial app must supply the real provider functions. A model should not promise direct native CLI/plugin invocation merely because the module exists.

## Independent financial business method

Decision loop and execution loop are defined in the standalone Skill and references/maintenance.md. They are concrete Financial behaviors: sourced value-chain and company economics, competing causal theses, 15-module private research, reader-oriented Deep/Broad story selection, source-originality/claim checks, actual Word artifact rendering and feedback-driven improvements. These do not call CAOS. Importing a historical CAOS bridge is forbidden in the standalone runtime.

## Deployment and product acceptance

GitHub CI and a model session are not a full deployed Financial service. A practical standalone connection must verify actual connector availability, user grant, provider CAS on a real sample (no destructive fixtures), source-to-claim evidence and readback of real delivered Word bytes, independently checked pages and editorial/reader acceptance. Current cross-border v3 is still an unfinished research task and cannot be re-labeled accepted. Production incident reports and domain changes are controlled under evals/EVOLUTION_INDEX.json only.
