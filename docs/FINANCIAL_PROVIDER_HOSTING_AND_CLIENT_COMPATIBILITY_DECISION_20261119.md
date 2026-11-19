# Financial Provider Action — Hosting and ChatGPT Client Compatibility Decision

**Date:** 2026-11-19  
**Status:** DESIGN DECISION CANDIDATE — NO HOST OR CLIENT ACTIVATED  
**Business owner:** Financial Writing  
**Existing canonical runtime:** `financial_writing_agent.standalone_runtime` + `financial_writing_agent.portfolio_coordinator`  
**Existing protocol:** `docs/FINANCIAL_PROVIDER_ACTION_PROTOCOL_V1_20261115.md`  
**CAOS:** External session-level governance only. No CAOS code, configuration, runtime or plugin is changed.

## 1. Decision summary

Select **Google Cloud Run (request-based Python container) as the preferred hosting candidate**, subject to explicit account eligibility, billing controls, ChatGPT client compatibility and security review.

Do not deploy yet. This decision selects a technical direction; it does not authorize creation of a Google Cloud project, linking a billing account, accepting a payment method, creating OAuth/GitHub Apps, provisioning resources, or enabling repository write credentials.

The Financial Provider Action remains an adapter around the existing Financial owner runtime. It must not become a second business controller, task registry, article-state store or method catalog.

## 2. Why Cloud Run is the best current fit

The existing Financial runtime is Python 3.11+, depends on Pydantic and python-docx, and owns deterministic admission, Word artifact checks, signed effect verification and portfolio-stage execution. A host should run that exact package rather than porting its business rules into another language.

Cloud Run supports containerized Python services, request-based billing and scale-to-zero behavior. Its published request-based Free Tier currently includes 2 million requests/month, 180,000 vCPU-seconds/month and 360,000 GiB-seconds/month. The documented North America outbound transfer allowance is 1 GB/month. The Free Tier is aggregated per billing account; usage beyond included quotas is billed. Tokyo (`asia-northeast1`) is a Tier 1 Cloud Run region, but actual regional cost and outbound-transfer treatment must be checked before deployment.

**Critical billing condition:** standard Cloud Run in a user-managed Google Cloud project requires an active Cloud Billing account even when usage is expected to remain within Free Tier. The Free Tier is not equivalent to “no billing account” or a guaranteed zero invoice. A Cloud Billing Budget spend cap can pause Cloud Run workloads when the configured cap is reached, causing service interruption; it is a safety control, not a substitute for usage monitoring and budget review.

An optional Google Cloud Starter Tier exists for eligible personal Google Accounts and can provision a limited Cloud Run environment without a billing account. It is managed by Google, has restricted regions/configuration and is exposed through supported Google AI Studio workflows. Eligibility, region, ability to deploy this exact existing container and access to required secret-management features are unverified. Do not design production around Starter Tier until a proof-of-concept demonstrates all required capabilities.

## 3. Hosting alternatives considered

| Host | Finding for this system | Decision |
|---|---|---|
| Google Cloud Run | Runs the existing Python container; HTTPS endpoint; request-based billing; scales to zero; Tokyo region available. Billing account and overage controls remain material. | **Preferred candidate**, not yet authorized/deployed. |
| Cloudflare Workers Free | 100,000 requests/day but 10 ms CPU per invocation. A JavaScript edge adapter could proxy/authenticate, but the Financial Python runtime and Word processing should not be rewritten or duplicated there. | Not the primary runtime. Reconsider only as an optional edge layer if a concrete security/latency need emerges. |
| Vercel Hobby | A free personal-project tier exists, but suitability for a private business workflow and its commercial-use restrictions require a separate terms review. It does not remove the need for durable auth/idempotency storage and exact Git CAS. | Not selected. |
| Render Free | Free web services can sleep when idle and are not a dependable always-responsive production mutation endpoint; local filesystem persistence is not a durable source of truth. | Not selected. |
| DigitalOcean Droplet | Requires a continuously provisioned paid VM and ongoing OS/security maintenance. The connected account previously showed no existing droplet. | Not selected for the no/low-cost first deployment. |
| GitHub Actions / issue comments | CI is suitable for testing; public issue comments are not a private owner-approval channel and do not provide the required live MCP owner session. | Not a production provider. |

## 4. Proposed runtime topology

```text
ChatGPT Financial client
  └─ Remote MCP Streamable HTTP over HTTPS
       └─ Financial Provider Action (Cloud Run candidate)
            ├─ MCP/OAuth authorization boundary
            ├─ GitHub App user identity verification
            ├─ short-lived task/operation execution grants
            ├─ separate owner confirmation surface
            ├─ provider attestation signer
            ├─ existing standalone_runtime admission functions
            ├─ existing portfolio_coordinator stage runner
            ├─ GitHub App repository-scoped CAS/readback
            └─ minimal operational store
                 ├─ OAuth session/refresh-token envelope
                 ├─ nonce/action replay ledger
                 └─ idempotency/outcome reconciliation
```

### 4.1 Keep business truth in GitHub

- Article `STATE.json`, requirement history, method catalog, immutable stage artifacts, portfolio contexts and detached effect receipts remain in the existing Financial repository.
- Do not duplicate article state, method state, task status or editorial history in Firestore/SQL.
- An operational store may hold only short-lived OAuth/session material, nonce consumption, idempotency keys, lease/lock metadata and unknown-outcome reconciliation pointers. It is not a second business-state authority.
- Every successful write must use the existing Git Data API bundle CAS protocol, non-force ref update against the exact parent, exact readback and signature-chain verification.

### 4.2 Minimal service split

For the first controlled deployment, use one Python service with narrow internal modules rather than microservices:
1. `mcp_transport`: Streamable HTTP tool discovery and request/response framing only.
2. `oauth_boundary`: MCP authorization-server endpoints/metadata, PKCE/state/CSRF checks, session binding and token rotation.
3. `github_identity`: GitHub App user authorization, authenticated `/user` lookup and owner-principal match.
4. `grant_service`: short-lived task/operation grants and provider-owned exact-digest owner confirmation.
5. `financial_adapter`: calls the existing standalone runtime and portfolio coordinator; no copied business rules.
6. `github_cas`: least-privilege GitHub App installation-token handling, blobs/tree/commit/ref CAS and readback.
7. `operational_store`: durable nonce/idempotency/session state only.
8. `attestation`: provider action/effect signing; separate reviewer trust domain.

Do not add a queue, second controller, generic agent framework or external orchestration platform unless measured execution behavior proves it is required.

## 5. Identity: do not conflate three credentials

The deployment has three separate trust questions:

1. **ChatGPT-to-MCP client authorization.** ChatGPT must obtain a scoped OAuth token for the MCP server. The server must implement the MCP authorization contract, discovery metadata, authorization-code flow, PKCE, refresh-token behavior and revocation expected by the supported ChatGPT client.
2. **Human-to-Financial owner identity.** The provider must establish the actual GitHub account identity, query GitHub's authenticated-user endpoint, and compare it with the configured Financial repository owner. A model-supplied username, actor ID or `approved=true` is never proof.
3. **Provider-to-GitHub repository access.** A dedicated GitHub App installation, restricted to the Financial repository and minimum contents/metadata permissions, performs repository operations. Its installation credential is not returned to the model.

Use expiring GitHub App user-to-server tokens with refresh-token rotation where supported. GitHub documents eight-hour user access tokens and six-month refresh tokens; refresh tokens rotate when used. Request `offline_access` when appropriate and implement refresh-token replacement atomically. A GitHub App user token is not a substitute for the separate repository-scoped installation token.

Provider and independent reviewer signing keys must remain separate. Owner/provider must never self-sign independent method/editorial review.

## 6. ChatGPT client compatibility is a deployment gate

The existence of a valid remote MCP endpoint does not prove that the current ChatGPT account/workspace can connect to it or invoke write tools.

Current OpenAI Help Center documentation states:
- Full custom MCP server support, including write/modify actions, is available to ChatGPT Business and Enterprise/Edu customers on web, subject to workspace policy.
- ChatGPT Pro can connect custom MCP servers with read/fetch permissions only.
- Plus is not listed in the documented supported plans for custom MCP server connections.

Therefore, before any hosting spend or production credentials:
1. Verify the exact account/workspace plan and the actual Plugins/Apps UI.
2. Verify that the account can create a custom MCP connection with write actions, not only read/fetch.
3. Verify OAuth refresh-token support and complete a fresh-session tool scan.
4. If the current account cannot invoke write actions, stop the ChatGPT integration path. Do not misrepresent a private Skill, GitHub connector, Plugin Creator archive or browser automation as equivalent to a production MCP write channel.
5. Present the minimum viable alternatives for explicit owner choice: use an eligible Business/Enterprise/Edu workspace, or keep the provider in local/standalone operator mode until an eligible ChatGPT client exists. Do not upgrade a plan or buy anything automatically.

## 7. Operational persistence and cost controls

Preferred initial configuration, subject to testing:
- Cloud Run request-based billing; minimum instances = 0; no always-on container.
- Conservative maximum instance count and bounded request concurrency for the first private pilot. Concurrency controls are operational safeguards, not substitutes for CAS.
- Short request deadlines and bounded tool payloads; long research/writing remains model-side and is not executed as a long-running provider task.
- No local-disk business persistence. Cloud Run instances are replaceable.
- Use a durable operational store only for OAuth/session, nonce and idempotency metadata. Firestore's published no-cost quota is 1 GiB storage, 50,000 reads/day, 20,000 writes/day and 20,000 deletes/day; billing/feature eligibility must be checked for the selected project.
- Store provider/GitHub App secrets in an approved secret manager; never in repo, image, source archive, environment dump, logs or tool outputs.
- Configure billing budgets/alerts and a spend cap before enabling any paid-tier resource. Confirm what happens at cap (service pauses/returns 5xx); do not treat budget alerts alone as a hard cap.
- Keep logs secret-free; redact authorization headers, OAuth codes, access/refresh tokens, HMAC material and owner confirmation payloads.
- Use health/readiness separation: process health may be healthy while mutation readiness remains NOT_READY.

## 8. Security and acceptance gates before any real write

**Identity and OAuth**
- MCP OAuth metadata, authorization code, PKCE S256, CSRF/state binding, audience, issuer, expiry, refresh rotation, logout/revocation and session-to-owner binding.
- Wrong GitHub user, wrong repository owner, expired/revoked token and wrong MCP client all fail closed.
- Refresh token storage is encrypted; refresh-token rotation is transactional; concurrent refresh requests cannot reuse an old token.

**Owner authorization**
- Exact task, operation set, transition count, expiry and purpose displayed on provider-owned approval surface.
- Binding requirement change shows the full original message and complete normalized change digest.
- Owner must reauthenticate/confirm outside model arguments; approval is one-time and revocable.

**GitHub write**
- GitHub App installation restricted to the one Financial repository.
- No administration, workflow, secrets or organization permissions.
- No force push, branch-protection bypass or broad PAT.
- CAS conflict, duplicate action, nonce replay, timeout-after-commit, partial bundle write and altered readback all have explicit safe outcomes.

**Operational recovery**
- Durable idempotency record keyed by action ID and canonical request digest.
- A timeout after commit returns UNKNOWN until exact effect receipt and state are read back.
- Same action ID with different bytes is rejected.
- No blind retry with a new action ID while the previous outcome is unresolved.

**Independent review**
- Independent reviewer has a separate identity, provider and signing key.
- Owner/provider cannot self-approve method promotion or editorial certification.
- If no separate reviewer is configured, the related action remains blocked.

**ChatGPT client**
- A fresh ChatGPT session discovers the expected tools and OAuth flow.
- Read-only probes pass before write tools are enabled.
- A synthetic non-production repository/task is used for adversarial write tests before any production article mutation.

## 9. Deployment sequence

1. **Client eligibility check first.** Confirm ChatGPT custom MCP write access. If unavailable, pause hosted deployment.
2. **Local service prototype.** Implement transport, OAuth boundary and provider adapter behind an interface; run against synthetic GitHub fixtures and local ephemeral credentials only.
3. **Security review.** Test identity spoofing, CSRF, PKCE, replay, refresh rotation, token leakage, owner-grant scope, stale SHA, concurrent CAS and timeout recovery.
4. **Account/host eligibility.** Confirm Cloud Run/Starter Tier access, billing-account status, region, terms, secret manager and spend-cap support. No resource creation before explicit owner approval.
5. **Private staging deployment.** Deploy with read-only GitHub App permissions first. Validate health, OAuth and exact owner match.
6. **Write staging.** Add repository-scoped write permission only after branch policy is verified; test a disposable staging task and exact readback.
7. **ChatGPT fresh-session activation.** Connect and scan tools; verify read-only, owner grant, negative cases, then one controlled staging mutation.
8. **Independent review.** Obtain a separate technical reviewer for exact deployed image digest, source commit, OAuth configuration and threat model.
9. **Production enablement.** Only after all gates pass, allow a bounded pilot. Article/editorial quality gates remain separate.

## 10. Current blockers and non-claims

- No Google Cloud project, Cloud Billing account, Starter Tier eligibility, Cloud Run service, OAuth application, GitHub App installation or provider signing key has been verified.
- No hosting or paid service has been provisioned.
- No live Financial Provider Action exists.
- No ChatGPT custom MCP write-capable client has been verified for the active account/workspace.
- No independent reviewer service or key exists.
- The existing provider protocol is a draft contract; no deployed implementation or live mutation has been proven.
- PR #91's exact-head CI is green, but it has no independent review and remains a draft. Its status synchronization is not product acceptance.
- The historical cross-border v3 article remains at RESEARCH with 0/4 outputs; this system task does not resume it.

**Decision:** Cloud Run is the preferred Python host candidate. The immediate next step is a local no-credential provider prototype plus a ChatGPT plan/client-eligibility check. Cloud deployment remains blocked until owner authorization, eligible write-capable ChatGPT client, billing controls, identity, repository policy and independent review are verified.
