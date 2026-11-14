# CAOS Governance Entry — Financial Writing Agent

Status: CANDIDATE__NOT_MERGED
Effective date: 2026-11-15
Domain: FINANCIAL_WRITING
Authority Context: DOMAIN:financial_writing
Repository: D1traverser-debug/financial-writing-agent

## 1. Governance boundary

CAOS is the cross-project cognition and governance system for Financial Writing work in the active ChatGPT session. Its source repository is `D1traverser-debug/cognition-agent-os`. Use the installed `cognition-parent-chatgpt-intake` Skill when available.

This is a Financial-owned integration contract. It does not copy CAOS implementation, create a second controller, start a daemon, or add a CAOS runtime/API dependency.

**CAOS source is read-only.** Do not create, edit, delete, rename, merge, or otherwise mutate CAOS repository code, documentation, branches, pull requests, configuration, releases, or installed Skill assets.

Governance mode is `CHAT_GOVERNED_EXTERNAL`: CAOS governs complete-goal recovery, cross-layer root-cause investigation, method research and comparison, decision rechallenge, execution discipline, independent acceptance and cross-domain learning in the active ChatGPT session. It does not create Financial task identities, own Financial business state, grant Financial permissions, or make automatic runtime calls.

Financial remains independently executable as a business domain. The standalone Financial Skill and its authenticated owner-effect boundary remain the only Financial business execution path. CAOS governance is not a runtime dependency and does not replace Financial's financial-domain expertise, evidence contracts or authorization gates.

## 2. Authority ownership

| Concern | Authority |
| --- | --- |
| Complete user-goal recovery, cross-layer root-cause investigation, professional method research, alternatives, counterexample testing, decision rechallenge, execution governance, independent acceptance and cross-domain learning | CAOS governance in the active ChatGPT session |
| Article identity and state, task requirements and revision digests, source research, financial analysis, DecisionEnvelope evidence, Deep/Broad story architecture, writing, review, Word production, method catalog, feedback and domain evolution | Financial Writing Agent |
| Provider-signed article/method effects, external user confirmation, publication, external sharing and reader/platform outcomes | Authenticated provider and/or user, according to the Financial execution contract |

Financial remains the sole owner of `FINANCIAL_WRITING_OWNER`, task-scoped `task_id`, `workspaces/articles/{task_id}/STATE.json`, requirement authority, method catalog and evolution state. CAOS governance context is not a Financial business identity. No parent task ledger, lease, runtime proxy, business-state mirror, permission grant or duplicate continuation system is introduced.

The Financial `DecisionEnvelope` and native admission modules remain domain evidence/authorization contracts. They do not constitute a second cross-project cognition controller. CAOS owns cross-project cognition governance; Financial owns finance-specific research, article decisions and business execution.

## 3. Startup protocol

For a new Financial task or continuation:

1. Activate CAOS governance in the current ChatGPT session for every material/systemic Financial decision and every cross-project decision. If CAOS governance is unavailable, do not claim a CAOS-governed acceptance.
2. Read this file, `config/CAOS_GOVERNANCE.json`, `README.md`, `config/FINANCIAL_MANIFEST.json`, `config/FINANCIAL_CAPABILITIES.json`, `config/EXECUTION_CONTRACT.json`, `config/DATA_AUTHORITY.json`, and the Financial Skill.
3. Resolve the exact Financial task from its task-scoped `STATE.json`, current requirement revision/digest and authoritative artifacts. Do not reconstruct business state from CAOS memory, historical parent records or a stale summary.
4. Read the exact current sources, private research, method records, story blueprints, review receipts and Word artifacts needed for the requested action.
5. Apply Financial's owner-native requirement, source freshness, evidence, writing, article-state, signed effect, provider readback and publication boundaries.
6. For material/systemic changes, use CAOS governance to challenge the complete goal, causal layers, methods, alternatives, counterexamples, assumptions, rollback and verification plan before changing Financial-owned code or rules.
7. Execute only through the Financial owner-admission/provider path. CAOS does not grant write, publication, signing, payment or external sharing permission.
8. Verify actual committed state, exact article artifacts, source evidence, Word binaries/rendered pages and user-visible outcomes independently. CI is engineering evidence, not proof of current financial truth, editorial quality or reader success.

## 4. Preserved standalone and business invariants

- The single Financial operating Skill remains `skills/financial-writing-agent/SKILL.md`; this CAOS entry is a governance contract, not a second business Skill.
- `FINANCIAL_MANIFEST.json` remains `STANDALONE_FINANCIAL_DOMAIN`; no external CAOS runtime, API, Host or bridge is required.
- Financial retains the only article business-state authority: `workspaces/articles/{task_id}/STATE.json`.
- Financial retains the only method authority: `knowledge/METHOD_KNOWLEDGE_CATALOG.json`.
- Financial retains the only domain evolution authority: `evals/EVOLUTION_INDEX.json`.
- Existing article identities, requirement revisions, source receipts, Word deliverables, feedback, method history and signed effect history are not rewritten by this governance migration.
- Missing authenticated provider/signing capability leaves only the affected business-state mutation OPEN; it does not authorize a simulated PASS.
- General editorial quality, real article quality and reader/platform outcomes remain NOT_READY until independently evidenced.

## 5. Historical cleanup

The current Financial main branch has no active UAOS manifest, adapter, capability profile or parent Skill binding. Old UAOS/CAOS-hosted child branches, unmerged compatibility experiments, dated audits and Git history remain historical provenance only. They are not current startup instructions, business-state authorities, runtime dependencies or permission sources.

Do not restore the old hosted CAOS bridge from historical PRs. The selected architecture is CAOS external ChatGPT-session governance plus an independently executable Financial business domain.
