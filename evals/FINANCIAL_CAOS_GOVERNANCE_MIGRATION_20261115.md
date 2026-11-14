# Financial Writing — CAOS Chat Governance Migration Audit

Date: 2026-11-15
Status: CANDIDATE__CI_PENDING__NOT_MERGED
Repository: `D1traverser-debug/financial-writing-agent`
Branch: `migration/caos-chat-governance-20261115`
CAOS source: `D1traverser-debug/cognition-agent-os@main` (read-only)

## Owner goal

The owner explicitly selected CAOS as the cross-project cognition and governance system for all business domains: A-share stock recommendation, Novel Writing, Financial Writing and Video production. The migration applies to governance authority and cognitive method; it does not move each domain's business runtime, task identity, state or permissions into CAOS.

## Root cause

Financial Writing's 2026-11-11 standalone reconstruction correctly removed the historical hosted parent runtime, parent task identity, bridge, permission proxy and duplicated state. However, its active manifest, capability profile, Skill and architecture also described cognition as wholly Financial-owned and explicitly stated that no CAOS parent/governance was required. This conflated two separate concerns:

1. **Runtime/business authority:** Financial must remain independently executable and own article/task state, requirements, method catalog, effects and publication permissions.
2. **Cross-project cognition governance:** CAOS must govern complete-goal recovery, cross-layer root-cause investigation, professional method comparison, decision rechallenge, execution discipline, independent acceptance and cross-domain learning in the active ChatGPT session.

The old standalone runtime decision is preserved; only the governance authority boundary is updated.

## Compared architectures

| Candidate | Decision | Reason |
|---|---|---|
| Restore the historical CAOS-hosted child/bridge from PR #52 | REJECT | Reintroduces a runtime/API dependency, old parent identity and a second execution authority; contradicts the successful Financial standalone reconstruction. |
| Keep Financial completely outside CAOS cognition governance | REJECT | Conflicts with the owner's explicit 2026-11-15 cross-project governance instruction and leaves cognition fragmented across domains. |
| Copy CAOS kernel or create another Financial cognition controller | REJECT | Duplicates the parent cognition system and splits decision authority. |
| CAOS external ChatGPT-session governance + Financial-owned standalone business runtime and evidence/admission gates | SELECTED | Gives one cross-project cognition authority while preserving the independently executable Financial domain and all business-state/permission boundaries. |

## Implemented candidate changes

- Added `config/CAOS_GOVERNANCE.json` and `CAOS_FINANCIAL_ENTRY.md`.
- Rebound `FINANCIAL_MANIFEST.json`, `FINANCIAL_CAPABILITIES.json` and `EXECUTION_CONTRACT.json` to `CAOS_CHAT_GOVERNED_EXTERNAL`.
- Updated README, Financial Skill, architecture and standalone interface to activate CAOS governance for material/systemic and cross-project decisions.
- Clarified that Financial's `DecisionEnvelope` and native admission modules are domain evidence/authorization contracts, not a second cross-project cognition controller.
- Extended static audit and single-owner tests to require CAOS governance metadata while rejecting runtime/API/Host dependencies.
- Recorded the migration candidate in the existing Financial evolution index; no parallel task registry was created.

## Preserved invariants

- `FINANCIAL_WRITING_OWNER` remains the only Financial business owner.
- `workspaces/articles/{task_id}/STATE.json` remains the only article state authority.
- Task-scoped requirement revision/digest and all prior requirement/evidence history remain intact.
- `knowledge/METHOD_KNOWLEDGE_CATALOG.json` remains the only reusable method authority.
- `evals/EVOLUTION_INDEX.json` remains the only Financial system evolution authority.
- `financial_writing_agent.standalone_runtime` remains the Financial owner-effect/admission boundary.
- `external_parent_required=false` and `external_host_required=false` remain true: no CAOS runtime/API/Host dependency.
- No parent task identity, business-state mirror, automatic runtime upcall or CAOS permission grant is introduced.
- No article business state, article deliverable, signed receipt or historical audit is rewritten.
- The CAOS source repository/code/branches/PRs/configuration and installed Skill assets are untouched.

## Historical provenance policy

The old CAOS-hosted integration in PR #52, the standalone replacement in PR #60, the final parent-pointer cleanup in PR #62, the retired UAOS experiments and the asset-governance migration remain historical evidence. They are not current startup instructions or active runtime dependencies. This migration does not rewrite Git history or delete historical branches.

## Acceptance still required

- Exact-head Financial full CI and static/whole-tree audits.
- Fresh independent code and security review against the final PR head.
- Review the actual mainline readback and post-merge CI.
- Independently confirm no active UAOS binding, no reintroduced parent runtime and no changed article/business state.
- Financial's real authenticated provider effects, independent editorial acceptance and real reader outcome remain separate NOT_READY gates; CAOS governance migration does not promote them.
