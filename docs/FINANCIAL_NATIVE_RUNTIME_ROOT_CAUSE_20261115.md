# Financial Writing native-runtime root cause and continuation record

**Date:** 2026-11-15  
**Scope:** Financial Writing repository and its private ChatGPT Skill package only. No CAOS code, configuration, PR, plugin assets or runtime were modified.  
**Candidate branch:** repair/financial-requirement-bound-owner-stage-coordinator-20261114  
**Code/test head at latest source verification (before documentation-only refresh):** dd3dec1f09f7e9eb1687b1ef152fdf1262a3832b  
**Latest fully green CI:** [43682430042](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43682430042) — SUCCESS on 18203d8ab33febd284c020d6dbed97f6e24822a2. The latest code/test head dd3dec1 and current documentation-only branch head have no check runs; exact-head CI is NOT VERIFIED.  
**Open candidate PR:** [#84](https://github.com/D1traverser-debug/financial-writing-agent/pull/84) — DRAFT, not merged.

## 1. Engineering evidence and its boundary

The latest fully green run after the CI security correction completed all 20 reported job steps:
- 675 tests passed.
- Total Python statement coverage: 88% (7,731 statements; 961 uncovered).
- Portfolio Coordinator: 88%.
- Standalone Runtime: 86%.
- Writing Kernel: 80%.
- The run included the PR CI secret-isolation regression test, whole-owner/two-revision admission checks, whole-tree inventory, executable contract evaluations, standalone wheel installation, DOCX render smoke, four synthetic Word-product renders and negative-case business replay.

Run 43682430042 is on commit 18203d8, not on the current candidate head dd3dec1. It passed 675 tests at 88% total statement coverage (7,731 statements; 961 uncovered), with Portfolio Coordinator 88%, Standalone Runtime 86% and Writing Kernel 80%. Subsequent commits added the Provider Action V1 protocol, protocol-to-runtime contract tests, and corrected two case-sensitive test assertions. These latest changes have been source-inspected, but exact-head CI has not run: the current commit has no check runs and combined status is pending with no statuses. Do not treat the latest tests as passed until CI runs on dd3dec1 or a descendant.

A green CI is engineering evidence only. It does not prove native ChatGPT invocation, a live trusted provider signature, a real article delivery, independent editorial acceptance or reader outcomes.

## 2. Security finding: PR CI previously exposed a provider-secret path

The earlier CI workflow checked out and executed pull-request-head code while passing FINANCIAL_PROVIDER_ATTESTATION_KEY, FINANCIAL_TRUSTED_PROVIDER_ID and FINANCIAL_OWNER_PRINCIPAL into the same job. One step then executed scripts/system_acceptance_report.py from that PR head. A malicious PR could have modified that script to read or exfiltrate any available secret. The earlier presence-only probe at run 43673501899 showed all three values were false in that runner; there is no evidence that a value was present or leaked.

The candidate branch has corrected this trust boundary:
- Removed the provider-secret probe from the pull_request CI workflow.
- Removed all provider secret environment variables from the PR-executed acceptance script step.
- Removed the branch-inventory step and its GITHUB_TOKEN from the PR CI workflow; branch administration remains in the separate manual/main-only workflow.
- Added tests/test_ci_trust_boundary_20261115.py, which asserts that PR CI references no secrets or GITHUB_TOKEN and that the privileged archive workflow remains manual and main-only.
- CI run 43682023560 passed this regression test.

Do not reintroduce provider secrets into a workflow that checks out or executes PR-head code. The provider signing key belongs only in the dedicated trusted provider's managed secret store.

## 3. Root cause: native execution and provider admission are disconnected

The private ChatGPT plugin was updated to version 0.1.3, release pluginrel_6af9484ec2b081919a2689deeb4902f3. Its exact files were read back and checked. It remains a Skill-only package: it has no hosted MCP/Python action endpoint. Plugin installation/live action execution is still NOT_VERIFIED; Plugin Management reported the app as not_installed.

The canonical Skill describes the 16-pass portfolio flow using start_portfolio_context and execute_portfolio_stage. The candidate branch adds portfolio_coordinator.run_next_portfolio_stage, which can execute one stage, persist immutable stage/context artifacts, read them back, cross-bind hashes and request Article Aggregate admission.

These are Python functions, not native ChatGPT tools. The connected GitHub connector can read repository content and make candidate code changes, but it does not execute the Financial admission runtime, authenticate semantic owner intent, issue provider attestations, or create the atomic owner-state/effect-receipt bundle through that runtime. A Git commit SHA/CAS is concurrency evidence, not proof of owner authorization.

The repository is public. An issue-comment command bus is rejected because private requests, research inputs and owner instructions could become public. The current GitHub integration exposes no workflow-dispatch action, so the manual archive workflow is not a native chat execution endpoint.

The previous machine declarations incorrectly said that a hosted service was unnecessary. The manifest, capability contract, execution contract, architecture and canonical Skill have now been aligned: Financial remains independent of any parent controller, but canonical state/method mutations require a Financial-owned hosted Provider Action.

## 4. Provider architecture decision

The selected architecture is a dedicated hosted Financial Provider Action over MCP/HTTPS. It is a transport, authentication and deterministic admission adapter, not a second business controller.

The provider must:
- Authenticate the human through GitHub OAuth or equivalent identity proof; never trust owner identity or approval text supplied by the model.
- Bind actions to the authenticated repository owner, exact task, operation, prior blob SHA, request digest, nonce and expiry.
- Require a separate authenticated confirmation surface for binding requirement changes.
- Execute the existing standalone_runtime and portfolio_coordinator code rather than duplicating business rules.
- Use a least-privilege GitHub App, sign exact authorizations and effect receipts, commit state plus receipt atomically, reject stale ref updates and read back exact resulting blobs.
- Keep all signing and OAuth secrets outside the repository, prompts, model-visible tool arguments and CI logs.

The Plugin Creator's default Sites MCP hosting skill/server reference is not available in the current tool catalog. The connected DigitalOcean account returned zero droplets. No hosting target, domain, OAuth app, GitHub App installation or provider signing key has been verified. No paid infrastructure has been provisioned. The deployment path therefore remains OPEN pending an approved host and implementation.

The GitHub branch-protection endpoint returned 403 through the current integration and the ruleset read returned an empty list. This does not certify whether protection exists; main-branch hygiene remains OPEN. No provider write credentials may be enabled until branch-protection and the state-write policy are independently verified.

See docs/FINANCIAL_PROVIDER_BRIDGE_DECISION_20261115.md for the alternatives, exact provider contract, tool surface and acceptance sequence. The concrete MCP tool/persistence contract is now specified in docs/FINANCIAL_PROVIDER_ACTION_PROTOCOL_V1_20261115.md; it remains a draft and is not deployed.

## 5. Current business state and immutable task requirements

The active article remains:
- Task: cross-border-ecommerce-20261016-v3.
- State path: workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json.
- State blob SHA at the prior observation: 17ae95d71d6147a26b90a13536374de15d90c1be.
- Current stage at the prior observation: RESEARCH; status IN_PROGRESS.
- Required Word products: AUDIT_DOCX, FINANCE_DEEP_DOCX, FINANCE_BROAD_DOCX and PLATFORM_INTERACTION_PACK_DOCX.
- Recorded delivery products: 0 of 4.

Requirement revision 1 has digest 641bfaee46fbce8b5a3c363a54cd364f1c318bca5102ebe70001d968302051dd. Preserve both binding requirements:
1. Build a complete retained A-share cross-border-ecommerce research pool from multiple current concept/economic sources; deduplicate by ticker; verify inclusion; classify every retained company by economic role; compare directness, business purity, financial realization, event transmission and reversal conditions within material sub-segments.
2. FINANCE_DEEP must visibly carry the complete retained company universe. Material companies require explicit within-segment comparison. Weak/incidental names may be grouped compactly only with an explicit reason; they must not silently disappear.

The prior V2 package described 174 companies and used 2026-10-16 as its as-of date. It is historical input, not current research authority. The negative replay rejected it as stale. No current news, policy, constituent list, filings or company financial evidence was revalidated by CI.

## 6. Whole-system acceptance remains NOT READY

Seven gates remain OPEN:
- Original goal and semantic correction.
- Legal article graph and recovery.
- Method knowledge CRUD and impact.
- Provider-authenticated runtime CAS.
- Native Financial plugin client activation.
- Independent external adversarial review.
- Financial main-branch hygiene.

The negative replay reproduced no weak-assurance bypass paths. This is safety evidence, not successful business delivery.

## 7. Next legal sequence

1. Obtain an explicit host/platform and cost decision; do not provision paid compute or a domain without approval.
2. Implement and test the hosted Financial Provider Action against the existing standalone_runtime contracts.
3. Verify owner OAuth, least-privilege GitHub App installation, branch protection, secret storage, atomic CAS and exact readback.
4. Connect/install the companion ChatGPT action and prove invocation in a fresh session.
5. Only then resume the real article from its admitted state, revalidate all current sources and the complete retained company universe, produce all four Word products and obtain independent editorial/reader evidence.
6. Keep PR #84 in Draft. Do not merge solely because CI is green. Do not delete branches or modify CAOS.

**Stop condition:** no system-completion claim until the live provider, native client, real article, independent review and remaining gates have verifiable evidence at an accepted main revision.
