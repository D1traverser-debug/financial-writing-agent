# Financial Provider Action Protocol v1

**Status:** DRAFT CONTRACT — NOT DEPLOYED  
**Transport target:** MCP Streamable HTTP over HTTPS  
**Business authority:** Financial Writing repository and its existing Article Aggregate / method catalog  
**Canonical implementation:** financial_writing_agent.standalone_runtime and financial_writing_agent.portfolio_coordinator  
**Related decision:** docs/FINANCIAL_PROVIDER_BRIDGE_DECISION_20261115.md

This document defines the narrow action boundary required to make the Skill-only ChatGPT client capable of authenticated Financial state transitions. It does not create a second business controller. The ChatGPT model remains responsible for semantic research, analysis, writing and stage outputs. The provider authenticates the owner, runs deterministic admission, persists immutable artifacts and signed receipts, and verifies exact readback.

## 1. Trust domains

| Principal | Responsibility | Must not be trusted for |
|---|---|---|
| ChatGPT model + Financial Skill | Interpret the user's goal, research, produce stage outputs, compare alternatives and decide the next legal business action. | Authenticating the human, self-approving binding requirement changes, inventing provider signatures or claiming a write succeeded. |
| Authenticated owner | Grant a scoped execution session and approve exact binding requirement changes. | Technical provider execution or independent editorial review. |
| Financial Provider Action | Authenticate owner, validate request scope, sign action/effect attestations, execute existing Python admission code, perform Git CAS and exact readback. | Replacing the model's semantic work or acting as an independent reviewer of its own outputs. |
| GitHub App | Read and persist Financial repository objects using least privilege. | Proving owner intent by itself. |
| Independent method/editorial reviewer | Provide separately authenticated review evidence where the contract requires it. | Reusing the owner/provider identity to self-certify. |

The provider must resolve the authenticated human identity from its OAuth session and GitHub's authenticated-user endpoint. It must compare that identity with the configured repository owner identity. It must never trust an actor ID, owner principal, approved flag, original message or confirmation claim supplied only in model tool arguments.

The current verifier trust domain uses audience financial-writing-agent and requires FINANCIAL_PROVIDER_ATTESTATION_KEY, FINANCIAL_TRUSTED_PROVIDER_ID and FINANCIAL_OWNER_PRINCIPAL. The provider derives the owner principal from the authenticated OAuth identity; it does not accept that value from the model. Independent method review uses FINANCIAL_METHOD_REVIEW_KEY and FINANCIAL_METHOD_REVIEW_PROVIDER_ID in a separate trust domain.

## 2. Authentication and authorization

### 2.1 Owner session

The MCP server authenticates the human through OAuth. A successful connection alone is not a blanket write grant.

The model may call request_execution_grant with:
- task_id;
- requested operation set;
- maximum number of stage/action transitions;
- requested expiry;
- a concise human-readable purpose.

The provider creates a one-time approval challenge. The authenticated owner reviews and approves the exact repository, task, operation set, transition limit and expiry in a provider-owned confirmation surface. The grant is bound server-side to the authenticated principal and MCP session. The model receives only a non-authoritative grant reference; it is not a bearer signing key or GitHub credential.

A grant must be short-lived, revocable, single-owner, task-scoped and least-privilege. It must not authorize binding requirement changes, method promotion, publication or other separately gated actions unless those scopes are explicitly approved in a separate challenge.

### 2.2 Binding requirement changes

For CHANGE_REQUIREMENTS, the provider creates a separate challenge containing:
- the complete original user-message text and source reference presented for owner confirmation;
- current task ID and requirement revision/digest;
- the complete normalized additions, edits and retirements;
- the canonical change digest;
- the expected current state blob SHA.

The provider UI must show the full message and exact normalized change. The owner explicitly approves that digest while authenticated. Only then may the provider issue the owner_message and owner_change_approval attestations expected by the existing runtime. A model-provided string such as approved=true is never sufficient.

If the owner cannot inspect or approve the exact change, the request remains OPEN and no canonical requirement mutation occurs.

### 2.3 Independent review

Method promotion and impact verification use the separate FINANCIAL_METHOD_REVIEW_KEY / FINANCIAL_METHOD_REVIEW_PROVIDER_ID trust domain, or a versioned successor with equivalent separation. The owner identity and owner Provider Action must not sign the independent review.

## 3. MCP tool contract

All tools are authenticated to the same owner session. Inputs are strict JSON objects; unknown fields are rejected. No tool accepts a GitHub token, provider key, raw HMAC signature or arbitrary repository path from the model.

### 3.1 provider_status

Input: empty object.

Output:
- provider_id, provider_version, protocol_version;
- authenticated_principal and owner_match (boolean);
- GitHub App installation status and repository binding;
- signing-key presence only (never key material);
- branch/state-write policy verification;
- active session grant scopes and expiry;
- capability status: READY or NOT_READY with explicit open gates.

This tool must never return credentials, OAuth access tokens, signing keys or private environment values.

### 3.2 observe_article

Input:
- task_id: string.

Provider calls standalone_runtime.observe_article with provider-backed state and effect readers. Output includes exact state path/blob SHA, task requirement revision/digest, stage/status, next action, required/recorded outputs, authorization/effect history and explicit false values for unverified editorial/owner outcomes.

No model-generated summary may replace the returned exact state identity.

### 3.3 request_execution_grant

Input:
- task_id: string;
- operations: non-empty enum list;
- max_actions: bounded positive integer;
- expires_in_seconds: bounded positive integer;
- purpose: short human-readable string.

Output:
- challenge_id;
- approval_url;
- challenge_digest;
- status: PENDING_OWNER_APPROVAL.

After the owner approves in the provider UI, a subsequent call reports APPROVED, REJECTED or EXPIRED. The provider binds the grant to the OAuth principal and MCP session. The model cannot approve its own challenge.

### 3.4 run_portfolio_stage

Input:
- task_id;
- expected_state_blob_sha;
- grant_id;
- action_id;
- stage_outputs: mapping of exact pass identifiers and scope identifiers to model-produced output objects;
- research_audit_output: required only for RESEARCH_AUDIT;
- requirement_satisfaction: stage-scoped evidence claims.

The provider:
1. Reads and validates the actual Article Aggregate state and exact blob SHA.
2. Verifies the active owner grant, task scope, allowed operation, action ID and expected state SHA.
3. Reads the latest immutable portfolio context and verifies its Git blob SHA, SHA-256, task ID, requirement digest, stage, generation and status.
4. Determines the exact required pass set from the canonical writing kernel for the current stage. Missing or extra pass outputs are rejected.
5. Supplies the model-produced pass outputs through deterministic execute_pass/research_audit callbacks to portfolio_coordinator.run_next_portfolio_stage. The provider does not call another LLM or reinterpret the business content.
6. Persists the immutable stage artifact and next context as one artifact bundle. It rereads every object and checks exact bytes and Git blob SHA.
7. Invokes standalone_runtime.admit_article_action with an owner authorization signer bound to the authenticated session, exact request digest, prior state SHA and action ID.
8. Writes the new owner STATE and detached effect receipt in one Git tree/commit. The ref update must be non-force and fail on a stale parent.
9. Reads back the exact STATE and effect receipt, recomputes their Git blob SHAs, validates the persisted authorization/effect chain and verifies task/stage/status bindings.
10. Returns success only after all readbacks pass.

For INTAKE, the stage output set is empty and the coordinator creates the initial context. For RESEARCH_AUDIT, research_audit_output is required and the pass-output map must match that stage's exact contract. For all other stages, the exact pass/scope output set is derived from the canonical kernel; clients cannot choose a different stage order.

Output:
- task_id, action_id, executed_stage, next_stage, business_status;
- state_ref, previous_state_blob_sha, resulting_state_blob_sha;
- stage_artifact_ref/blob_sha when applicable;
- portfolio_context_ref/blob_sha/SHA-256 when applicable;
- effect_receipt_ref/blob_sha;
- provider_commit_ref;
- authorization/effect verification status;
- child_state_cas_verified and effect_receipt_readback_verified;
- explicit semantic/editorial/owner outcome flags.

The tool must not claim article completion or editorial acceptance merely because a stage transition was admitted.

### 3.5 admit_article_action

Input: exact existing standalone_runtime article action proposal:
- schema_version;
- domain_id;
- action_id;
- task_id;
- operation;
- expected_state_blob_sha;
- parameters.

The provider rejects any operation outside the existing OPERATIONS allowlist, unknown parameter keys, stale state SHA, invalid task path, missing grant or missing special-purpose approval. It then calls standalone_runtime.admit_article_action with real provider readers, signer and atomic bundle CAS writer.

CHANGE_REQUIREMENTS additionally requires an approved owner-change challenge. RECORD_OWNER_INTENT requires verifiable source-message evidence. RESUME_BLOCKED and REOPEN_METHOD_DEPENDENCY must satisfy the existing recovery and dependency checks.

### 3.6 observe_method_catalog / admit_method_action

observe_method_catalog calls standalone_runtime.observe_method_catalog with exact catalog and effect readers.

admit_method_action accepts the existing schema_version, domain_id, action_id, operation, expected_catalog_blob_sha and parameters. It requires an owner grant, exact prior catalog SHA, a signed owner action authorization, separate method promotion/impact evidence where applicable, and atomic catalog/effect bundle CAS with exact readback.

The owner Provider Action cannot supply the independent method-review attestation.

### 3.7 request_owner_change_confirmation / owner_change_status

The first tool creates a provider-owned approval challenge for a binding requirement change and returns an approval URL plus challenge digest. The second reads the status. Approval occurs only in the provider UI after OAuth reauthentication and exact-digest review. The model cannot call a tool to approve on the owner's behalf.

## 4. Existing Python callback mapping

The HTTP/MCP layer is an adapter only. It must call the existing contracts:

- observe_article -> standalone_runtime.observe_article
- article writes -> standalone_runtime.admit_article_action
- method reads -> standalone_runtime.observe_method_catalog
- method writes -> standalone_runtime.admit_method_action
- one business-stage transition -> portfolio_coordinator.run_next_portfolio_stage

The provider supplies:
- state_reader and catalog_reader backed by exact GitHub blob reads;
- artifact_reader and portfolio_context_reader backed by exact GitHub blob reads;
- bundle_cas_writer and artifact_bundle_writer backed by Git Data API blobs/tree/commit and a non-force ref update against the exact parent;
- authorization_verifier that signs only after authenticated owner/grant checks;
- effect_attestation_signer that signs the exact runtime-provided effect claims;
- effect_receipt_reader backed by exact GitHub reads;
- source_snapshot_reader and owner_instruction_reader backed by immutable, task-scoped evidence records;
- independent_editorial_verifier and method promotion/impact verifiers backed by separate reviewer trust domains.

A callback returning booleans, strings or unsigned dictionaries is not provider evidence. No fallback to direct connector writes, local-only hashes or synthetic model signatures is allowed.

## 5. Persistence and concurrency protocol

For a canonical state transition, the provider:
1. Reads the current ref SHA and exact current state/catalog blob SHA.
2. Validates expected SHA equals the current blob SHA.
3. Constructs the new state/catalog and signed effect receipt in memory.
4. Creates blobs for both objects.
5. Creates one Git tree containing both objects.
6. Creates one commit parented to the exact observed ref SHA.
7. Updates the ref with force=false. A concurrent update must make this non-fast-forward update fail.
8. Reads both resulting paths at the resulting commit SHA.
9. Verifies exact bytes, Git blob SHAs, state/catalog validity and signature chain.
10. Returns ADMITTED only after all checks pass.

If the provider loses the response after commit, the outcome is UNKNOWN, not FAILED or SUCCESS. It must reconcile by action_id and exact effect-receipt path before any retry. Reuse of an existing action ID with different request bytes is rejected. Existing immutable artifact paths may be reused only when the exact bytes match.

Branch-protection compatibility is an OPEN deployment gate. Do not silently grant bypass or weaken protection to make the provider work.

## 6. Error contract

At minimum, callers must distinguish:
- AUTHENTICATION_REQUIRED
- OWNER_IDENTITY_MISMATCH
- OWNER_GRANT_REQUIRED / OWNER_GRANT_EXPIRED / OWNER_GRANT_SCOPE_MISMATCH
- OWNER_CHANGE_APPROVAL_REQUIRED / OWNER_CHANGE_DIGEST_MISMATCH
- METHOD_REVIEWER_NOT_INDEPENDENT
- PROVIDER_NOT_READY / GITHUB_APP_NOT_INSTALLED / BRANCH_POLICY_NOT_VERIFIED
- TASK_NOT_FOUND / TASK_ID_MISMATCH / STALE_STATE_SHA
- ACTION_ID_REPLAY / NONCE_REPLAY / REQUEST_DIGEST_MISMATCH
- STAGE_ORDER_MISMATCH / STAGE_OUTPUT_SET_MISMATCH / REQUIREMENT_DIGEST_MISMATCH
- ARTIFACT_WRITE_FAILED / ARTIFACT_READBACK_MISMATCH
- CAS_CONFLICT / BUNDLE_WRITE_OUTCOME_UNKNOWN
- EFFECT_ATTESTATION_INVALID / EFFECT_RECEIPT_READBACK_MISMATCH
- METHOD_CATALOG_INVALID / METHOD_EFFECT_CHAIN_INVALID

Errors must be structured and non-secret. Do not return stack traces, environment values, GitHub tokens, HMAC keys or OAuth tokens.

## 7. Operational requirements

- HTTPS only; OAuth-protected MCP session.
- Strict input schemas, request-size limits, rate limits and bounded stage output payloads.
- Persistent nonce/action idempotency store; durable audit trail without secrets.
- Secret-manager-backed provider and reviewer keys, rotated independently.
- Dedicated GitHub App with repository-scoped least privilege; no administration, Actions, secrets or organization access.
- Health/readiness endpoint distinguishes process health from mutation readiness.
- Startup self-test verifies configuration presence only and never prints secret values.
- No state mutation while branch protection, owner identity, signer, App installation or readback is unverified.
- No paid infrastructure is provisioned without explicit owner approval.

## 8. Acceptance tests

Positive tests:
- OAuth owner identity resolves to the repository owner.
- A scoped grant authorizes only the approved task and operations.
- One stage executes from the exact current context and persists exact stage/context/state/effect bytes.
- The returned provider commit and both readbacks match exact expected Git blob SHAs.
- Method catalog mutation and separate reviewer evidence pass independently.

Negative/adversarial tests:
- wrong OAuth principal, repository, task, audience, provider, operation or grant scope;
- model-supplied actor/approved flags without authenticated provider authority;
- altered original message, normalized change or confirmation digest;
- stale state/catalog SHA and concurrent ref update;
- repeated action ID, repeated nonce, expired grant and grant revocation;
- missing/extra stage pass outputs, wrong stage, stale requirement digest and cross-task artifact reference;
- provider timeout before commit and timeout after commit;
- partial blob creation, mismatched write receipt, altered post-write bytes and missing effect receipt;
- owner attempting to self-sign independent method review;
- attempted direct GitHub connector mutation outside the provider.

**Current status:** the protocol is specified, but the hosted provider, OAuth app, GitHub App installation, signing keys, deployment host and fresh-session ChatGPT action invocation are NOT DEPLOYED / NOT VERIFIED.
