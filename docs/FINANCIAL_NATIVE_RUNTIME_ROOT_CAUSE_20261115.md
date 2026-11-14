# Financial Writing native-runtime root cause and continuation record

**Date:** 2026-11-15  
**Scope:** Financial Writing repository only. No CAOS code, configuration, PR, plugin assets or runtime were changed.  
**Candidate branch:** `repair/financial-requirement-bound-owner-stage-coordinator-20261114`  
**Verified candidate commit:** `aee8461abbe0aa87837854ecc55e4b55bcb563d9`  
**Exact-head CI run:** [43637154181](https://github.com/D1traverser-debug/financial-writing-agent/actions/runs/43637154181) — SUCCESS  
**Open candidate PR:** [#84](https://github.com/D1traverser-debug/financial-writing-agent/pull/84) — DRAFT, not merged.

## 1. What was verified

The exact-head CI run completed all 19 workflow steps successfully. The measured Python line coverage was 85.9474% (6,636 of 7,721 statements). The run included unit/trajectory/hostile tests, exact-head verification, whole-owner and two-revision mutation admission, whole-tree audit, executable contract evaluations, static single-owner audit, standalone wheel installation, DOCX render smoke, four synthetic Word product renders, and a negative-case business replay.

This is engineering evidence only. It is not evidence that the native ChatGPT client invoked the Python admission runtime, that a live provider signed an action, that a real article was produced, or that a separate editor accepted it.

The provider-capability probe was added to CI and its output was parsed back from the artifact. In the latest run, all three expected values were empty in the runner:
- `FINANCIAL_PROVIDER_ATTESTATION_KEY`
- `FINANCIAL_TRUSTED_PROVIDER_ID`
- `FINANCIAL_OWNER_PRINCIPAL` (mapped from the GitHub secret `FINANCIAL_EXPECTED_OWNER_PRINCIPAL`)

The probe records only presence/absence; it never reads or prints secret values. The CI environment therefore did not demonstrate an available trusted signer or owner identity. This does not establish whether a secret was never created or was unavailable to that workflow; it establishes only that no value reached the process.

The owner-principal environment mapping was corrected to match `financial_writing_agent.provider_attestation.OWNER_ENV`. The probe now writes valid JSON and parses the exact persisted bytes back before passing.

## 2. Root cause: native execution and provider admission are disconnected

The current Financial plugin package is a private Skill-only package (v0.1.2). Its archive can be read back, but installation in the user's active client and a fresh-session invocation are not verified. The package has no hosted Python/MCP action endpoint.

The canonical Skill describes the 16-pass portfolio flow using `start_portfolio_context` and `execute_portfolio_stage`, then says to admit state changes through `standalone_runtime.py`. The candidate branch adds `portfolio_coordinator.run_next_portfolio_stage`, which can execute one stage, persist immutable stage/context artifacts, read them back, cross-bind their hashes and request Article Aggregate admission.

These are Python functions, not native ChatGPT tools. The current native client path has the GitHub connector for repository reads/writes, but no callable provider action that executes these Python functions or produces their HMAC attestations. The GitHub connector's Git commit/CAS operations alone do not execute `current_admission`, authenticate the semantic owner intent, or create a trusted signed effect receipt.

The Python verifier explicitly fails closed unless all of the following are supplied by a trusted provider:
- `FINANCIAL_PROVIDER_ATTESTATION_KEY`
- `FINANCIAL_TRUSTED_PROVIDER_ID`
- `FINANCIAL_OWNER_PRINCIPAL`

The coordinator therefore cannot be honestly called the live native runtime merely because its synthetic callback tests pass. The Skill-only package plus direct GitHub connector currently has no proven path to invoke the coordinator and signer.

## 3. Current business state and assurance boundary

The latest exact-head whole-system projection reports:
- system status: `NOT_READY__REQUIRES_SIGNED_EXTERNAL_EVIDENCE`;
- open gates: original goal/semantic correction, legal article graph/recovery, method knowledge lifecycle/impact, provider-authenticated runtime/CAS, native plugin client activation, independent external adversarial review, and main-branch hygiene;
- active article `cross-border-ecommerce-20261016-v3`: still at `RESEARCH`, with 0 of 4 required Word products recorded;
- negative-case replay: no reproduced weak assurance paths, but product readiness remains NOT_READY because live source authority, semantic support, independent editorial review and reader outcomes are unverified;
- branch inventory: 118 branches and one open PR, observed in a zero-mutation dry run only.

## 4. Decision

Do not bypass signed admission with direct writes to owner `STATE.json` or the method catalog. Do not synthesize a provider HMAC in the model, accept Git CAS as owner authorization, or label a green CI run as production acceptance.

Keep PR #84 in Draft. Its coordinator and requirement-binding changes are a tested candidate, not a complete runtime integration. Do not merge it solely because CI is green.

The viable next integration is a trusted provider-side admission bridge. A GitHub Actions/GitHub App implementation may avoid a separate hosted Python/MCP service, but it still requires a real trusted identity boundary, protected trusted workflow source, least-privilege write authority, externally provisioned secrets, exact request binding, atomic owner-state/effect-receipt CAS and exact post-write readback. Any workflow handling a PR must execute trusted code from the protected base revision and treat PR content only as untrusted data; it must never execute code from the PR head with privileged secrets. The archive-only GitHub App must not be repurposed as a general business writer.

Before enabling writes, independently verify branch/ruleset protection and provider identity. Keep missing capabilities OPEN. The existing two-phase branch archive/prune process remains a separate administrative operation; this audit performed no branch deletion.

## 5. Next legal work

1. Provision a dedicated least-privilege provider identity and the three required secrets outside the repository; confirm only their presence, never expose their values.
2. Implement the trusted provider bridge against the existing `standalone_runtime` contracts, with replay, stale-SHA, wrong-actor, wrong-task, altered-payload, partial-write, timeout-after-commit and exact-readback tests.
3. Verify the native Financial Skill is installed and invoke it in a fresh ChatGPT session against a real provider action; record the exact provider and state/effect receipts.
4. Only after the action path works, run the real active article through its actual stage graph. Preserve its existing task requirements; do not publish or silently alter requirements.
5. Obtain independent editorial/business review and actual reader/delivery evidence. Keep branch archive/prune and main protection verification separate.

**Stop condition:** no system-completion claim until the live provider, native client, real article, independent review and remaining external gates have evidence at the exact accepted main revision.
