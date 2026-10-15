# Financial Writing Agent

A-share publishable financial-writing domain registered under Universal Agent OS (UAOS) for shared governance and cross-domain coordination, while retaining independent ownership of product requirements, article identity/state, research/writing architecture, domain learning/evals and deliverables.

## Current authority

Parent/common-governance authority: `D1traverser-debug/universal-agent-os@main`.

Financial business authority: `D1traverser-debug/financial-writing-agent@main` after controlled promotion. Candidate architecture work occurs on its candidate ref without transferring ownership.

A fresh chat may select Financial Writing directly; normal article turns run under `DOMAIN:financial_writing` and do not require a live UAOS business proxy.

Domain entry/binding metadata:
- `UAOS_SKILL.md`
- `.uaos/MANIFEST.json`
- `.uaos/ADAPTER.json`
- `.uaos/CAPABILITIES.json`
- `config/EXECUTION_CONTRACT.json`

Product/architecture authority:
- `docs/product_requirements.md`
- `docs/architecture.md`

Article identity authority: `workspaces/articles/{task_id}/STATE.json::task_id`. There is no second Financial controller/task index/lease/resume runtime.

## Financial Writing 1.0 kernel

The stable external lifecycle remains:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

New tasks use `financial_writing_agent.current_admission`, which binds `writing_kernel_version=1.0` while delegating canonical business-state transitions to `owner_guard.py`.

Current hard admissions:
- RESEARCH forward transition requires an admitted `DecisionEnvelope`;
- EDITORIAL forward transition requires the long-form product `StoryBlueprint` objects;
- EDITORIAL_AUDIT PASS/REVISE requires product-specific `PublicationFitness` evidence.

Historical states without the kernel marker remain readable/resumable through the prior owner guard and are not rewritten.

## Research, writing and acceptance

Research is value-chain first: prior cognition recall -> full material chain preflight -> company-universe recall -> current evidence -> adversarial/counterexample search -> auditable saturation -> thesis competition -> Company Decision Map when applicable.

`FINANCE_DEEP` keeps complete material finance coverage with named company/case grounding, explicit Chinese H1 numbering and no default word-count ceiling. `FINANCE_BROAD` is a separate acquisition rebuild rather than shortened Deep.

Current publication acceptance requires evidence for: Fact Integrity, Retention, Company Grounding, Structure/Numbering, Originality, Authorial Style, Compliance and Payoff. Semantic PASS evidence must point to the text; a list of PASS labels is insufficient.

Natural prose is material/story/voice first. Generic scaffolding is a post-draft diagnostic, not a phrase blacklist. Research sources are evidence rather than prose templates; close paraphrase/patchwriting requires revision.

## Knowledge and evolution

Financial retains both topic cognition and method/failure-pattern cognition. `knowledge/METHOD_KNOWLEDGE_CATALOG.json` preserves learned methods with provenance, fit/misfit, adoption state and revalidation conditions. Cataloging does not automatically promote a rule.

Every detected problem activates the UAOS-hosted cognition floor. Financial-owned system evolution uses evidence -> alternatives/counterexamples -> DecisionEnvelope -> candidate branch/PR -> reproducible eval -> controlled promotion -> production reread -> live observation. Common/cross-domain changes upcall UAOS.

## Product/output contract

New ordinary work defaults to `PORTFOLIO + WORD_FILE_ONLY`:
- `FINANCE_DEEP_DOCX`
- `FINANCE_BROAD_DOCX`
- `PLATFORM_INTERACTION_PACK_DOCX`
- `AUDIT_DOCX`

Historical `DUAL` and historical `FINANCE_BROAD` semantics remain immutable.

## Verification

Run:
```bash
pytest -q
python scripts/eval_contracts.py
python scripts/static_audit.py
python scripts/retired_runtime_static_audit.py
```

CI additionally builds/installs the wheel and runs DOCX render smoke tests. Same-chat semantic review remains `CHAT_SELF_REVIEW`; stronger independence claims require distinct execution evidence.
