# Financial Provider Bridge — Architecture Decision

**Decision date:** 2026-11-15  
**Decision:** A dedicated hosted Financial Provider Action is required for canonical owner-state and method-catalog mutations.  
**Deployment status:** NOT DEPLOYED.  
**Scope:** Financial Writing repository and runtime only. No CAOS code, configuration, plugin or runtime is modified.

## 1. Problem statement

The current private ChatGPT release is Skill-only (0.1.3). Its package has no hosted MCP/Python action endpoint. The Skill can guide model reasoning, but it cannot invoke Python functions in financial_writing_agent.standalone_runtime or portfolio_coordinator.

The connected GitHub connector provides repository operations. It does not execute the Financial admission runtime, authenticate the semantic owner intent, issue provider attestations, or create the atomic owner-state/effect-receipt bundle through that runtime. A Git commit SHA/CAS is concurrency evidence, not proof that the owner approved the exact semantic action.

The repository is public. An issue-comment command bus is rejected because request payloads, research inputs and owner instructions could become publicly visible. The current GitHub integration also exposes no workflow-dispatch action; the archive workflow is manual-only and is not a native Financial execution endpoint.

Therefore the existing declaration that no hosted provider is required conflicts with the actual signed-admission contract and the verified Skill-only client capability.

## 2. Alternatives and decision

| Candidate | Finding | Decision |
|---|---|---|
| Skill + direct GitHub connector only | No callable Python runtime or trusted signer; direct Git commits cannot prove owner authorization or signed effects. | Reject as production write path. Retain for repository reads and code-candidate work. |
| GitHub Actions as the native chat provider | Workflow dispatch is not exposed by the connected tool; manual dispatch requires a separate UI. Issue comments are public in this repository and are not an acceptable private command channel. | Reject as the native chat path. Retain Actions for CI and separately approved administration only. |
| Dedicated hosted Financial Provider Action (MCP over HTTPS) | Exposes callable Financial-owned tools to ChatGPT, executes the existing Python admission/coordinator code, authenticates the owner, signs exact actions/effects and uses GitHub App CAS/readback. | **Select.** This is a transport/authentication/admission adapter, not a second business controller or external parent. |

The Skill remains the single business entrypoint and the ChatGPT model remains the active semantic orchestrator. The Provider Action only authenticates, validates, executes deterministic admission/persistence, and returns exact receipts.

## 3. Required provider contract

### 3.1 Identity and owner intent

- Authenticate the human through GitHub OAuth (or an equivalent identity provider with a verifiable account binding); do not trust authenticated_actor, owner IDs, approvals or source text supplied by the model.
- Verify the authenticated account against the configured Financial repository owner identity at request time.
- Issue short-lived, revocable session capabilities scoped to the Financial repository, task ID, allowed operations and expiry. No broad repository or administration token is exposed to the model.
- Binding requirement changes require a separate owner approval challenge over the complete original message reference and the exact normalized mutation digest. The owner approves that exact digest through an authenticated provider confirmation surface.
- Method promotion/impact review uses a separate reviewer identity and separate signing key/provider, never the article owner acting as their own reviewer.

### 3.2 Signed admission and effects

Reuse the existing provider_attestation.py contracts unless a versioned DecisionEnvelope authorizes a compatible change.

- Sign the exact action request: audience, provider ID, authenticated actor, action ID, task ID, operation, previous state/catalog blob SHA, canonical request digest, nonce and issue time.
- Enforce freshness, one-time nonce/action IDs, exact task/operation scope and stale-SHA rejection.
- Execute standalone_runtime.admit_article_action / admit_method_action and portfolio_coordinator.run_next_portfolio_stage inside the provider process; do not duplicate business rules in the HTTP layer.
- Write the owner STATE or method catalog and its detached effect receipt in one Git tree/commit. Update the ref non-force against the exact parent; on conflict, stop and reread rather than force.
- Sign the effect receipt over the exact resulting blob SHA, prior SHA, request digest, authorization digest, actor, provider and runtime version.
- Read back both exact blobs from GitHub after commit; recompute Git blob SHA and validate the state/effect pair before returning success.
- Treat timeout-after-commit as an unknown outcome until idempotent readback resolves it. Never retry a mutation with a new action ID until the prior result is reconciled.

### 3.3 Least privilege and data handling

- Use a dedicated GitHub App installation restricted to this repository. Grant only the permissions required for metadata and contents operations; do not grant administration, workflow, secrets or organization permissions.
- Keep signing keys and OAuth credentials in a managed secret store. Never place them in repository files, prompts, tool arguments, CI logs or model-visible output.
- The model receives only short-lived scoped session material and non-secret receipts. It never receives the GitHub App private key or provider signing key.
- Use HTTPS, strict request schemas, bounded payloads, audit logging without secrets, replay protection, rate limits and explicit revocation.
- Canonical state writes must respect the repository's branch-protection policy. Do not silently add an App bypass or write directly to main until the branch-protection and state-write design is independently verified.

### 3.4 Drive-backed source-file adapter — 2026-11-19 extension

Financial source originals are stored in the private Google Drive folder `ChatGPT/Financial Writing Agent/00_Source_Library` (folder ID `1l9STZjrrqg37_qKrBcKZ2zRkjC7pM0MQ`). GitHub remains the authority for source identity/lifecycle metadata, signed source-action effects, article state, and exact task-source bindings. This is a raw-object/control-plane split, not a second article-state authority.

The hosted Financial Provider Action must therefore add a least-privilege Google Drive adapter limited to this folder. For CREATE or ADD_VERSION it must upload a new immutable Drive file, fetch the exact file ID and revision, read the actual bytes, recompute SHA-256, and only then commit the GitHub source record plus signed effect receipt through expected-SHA CAS and exact readback. Existing Drive versions must never be overwritten.

Drive upload and GitHub metadata admission are not one atomic transaction. If the Drive upload succeeds but GitHub CAS fails, the object remains unreferenced and must be reconciled; it must not be silently deleted. If a committed GitHub source record points to missing or changed Drive bytes, source use is blocked. Timeouts remain unknown until both providers are read back.

The existing GitHub App contract remains responsible for canonical article-state and method/source-metadata writes. The Drive adapter is an additional narrowly scoped capability, not a second controller. The folder is provisioned and verified owner-only, but the hosted Drive source adapter and source CRUD tools are **NOT_DEPLOYED**. The existing Skill-only client cannot claim source-file CRUD or provider-attested source admission.

## 4. ChatGPT tool surface

The hosted endpoint should expose a narrow Financial-only tool set, at minimum:

1. provider_status: report provider identity, installed client, capability and readiness without returning secrets.
2. observe_article: read and verify the exact task state, requirement digest, receipts and current stage.
3. admit_article_action: authenticate and admit one scoped owner action.
4. run_portfolio_stage: execute one current business stage, persist its immutable stage/context artifacts, read them back and admit the Article Aggregate transition.
5. observe_method_catalog and admit_method_action: method CRUD through the same owner/effect boundary.
6. request_owner_confirmation / confirm_owner_change: separate challenge and exact-digest confirmation for binding requirement changes.
7. list_sources / observe_source / read_source_version / admit_source_action: Drive-backed source discovery, exact-version reads, and owner-authorized CREATE / ADD_VERSION / RETIRE / RESTORE with GitHub source-record/effect CAS.

No tool may report a stage as persisted or complete, or a source version as admitted, without exact provider readback and an admitted effect receipt. The Skill-only package remains useful for reasoning but is not a production mutation client.

## 5. Deployment and external gates

- The connected DigitalOcean account returned zero droplets. This does not rule out other hosting, but no existing droplet was available through that connection.
- The Plugin Creator guide's default Sites MCP hosting path is not available in the current tool catalog: neither the Sites skill nor its Site MCP server reference is present. Do not substitute an unapproved host.
- No hosting target, domain, OAuth app, GitHub App installation or provider signing key is currently verified.
- The GitHub branch-protection endpoint is not readable through the current integration (403); the ruleset read returned no rulesets. Main-branch protection therefore remains OPEN, not certified absent or present.
- The provider must not be deployed with write credentials until owner identity, branch protection, least-privilege GitHub App permissions, secret storage and recovery behavior are verified.
- No paid compute, domain, managed database or external service is provisioned by this decision. Provisioning requires explicit owner approval.

## 6. Acceptance sequence

1. Implement the provider service and OpenAPI/MCP tool contract with unit, integration and adversarial tests.
2. Configure GitHub OAuth and a least-privilege GitHub App; verify the authenticated account against the repository owner.
3. Provision the provider signing key in the host's secret manager; confirm presence only, never expose its value.
4. Deploy to an approved HTTPS host and connect/install the companion ChatGPT action.
5. In a fresh ChatGPT session, prove real tool invocation and exact owner-message/approval binding.
6. Execute positive and negative provider tests: wrong actor, wrong audience, altered payload, stale SHA, replayed nonce, concurrent CAS, partial write, timeout after commit, wrong task, wrong stage and altered readback.
7. Verify the private Drive source folder, then test the source two-phase protocol: upload/readback, GitHub source-record/effect CAS, orphan-object reconciliation, exact Drive revision mismatch, and timeout-after-upload/after-commit recovery.
8. Ingest one explicitly authorized real source file, reread the exact Drive file/revision, verify raw and normalized SHA-256, bind it to one article task, and independently validate the binding.
9. Run the actual article from its current admitted state only after provider acceptance; revalidate current research and preserve the full task-specific company-universe requirements.
10. Obtain independent editorial/business review and actual delivery/reader evidence. Keep all remaining system gates OPEN until their evidence exists.

**Stop rule:** A green CI, installed Skill, GitHub connector write, Git commit, synthetic HMAC or successful mock callback is not proof of a live Financial Provider Action.
