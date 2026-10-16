# Financial Writing Agent

A-share publishable financial-writing domain registered under Universal Agent OS (UAOS), while retaining ownership of product requirements, article identity/state, research/writing architecture, domain learning/evals and deliverables.

## Current authority

Parent/common governance: `D1traverser-debug/universal-agent-os@main`.
Financial business authority: `D1traverser-debug/financial-writing-agent@main` after controlled promotion; candidate work remains on its candidate ref.

A fresh chat may select Financial Writing directly; normal article turns run under `DOMAIN:financial_writing` without a live UAOS business proxy.

Binding/authority surfaces: `UAOS_SKILL.md`, `.uaos/MANIFEST.json`, `.uaos/ADAPTER.json`, `.uaos/CAPABILITIES.json`, `config/EXECUTION_CONTRACT.json`, `docs/product_requirements.md`, `docs/architecture.md`.

Article identity authority is `workspaces/articles/{task_id}/STATE.json::task_id`. There is no second Financial controller/task index/lease/resume runtime.

## Financial Writing 1.0 kernel / 1.0.2 domain candidate

External lifecycle remains:
`INTAKE -> RESEARCH -> RESEARCH_AUDIT -> EDITORIAL -> TITLE -> DRAFT -> EDITORIAL_AUDIT -> DELIVERY -> MECHANICAL_AUDIT -> FINAL_AUDIT`.

New tasks use `financial_writing_agent.current_admission`, bind `writing_kernel_version=1.0`, and require DecisionEnvelope at RESEARCH, StoryBlueprint at EDITORIAL, and product-specific PublicationFitness at EDITORIAL_AUDIT.

The 1.0.2 candidate adds `financial_writing_agent.resume_compatibility`: a historical pre-current-kernel state remains immutable/readable provenance but cannot silently inherit current semantic quality. Ordinary current-quality continuation requires a current-kernel successor/replay; explicit historical/provenance-only continuation remains bounded to historical semantics.

## Research, story construction and acceptance

Research is value-chain first: prior cognition recall -> material-chain preflight -> company universe -> current evidence -> adversarial/counterexample search -> saturation -> thesis competition -> Company Decision Map where applicable.

`FINANCE_DEEP` separates research completeness from publication selectivity. Complete research does not force the article to reproduce the entire research map. Selective publication accounts for researched material classes as CORE / SUPPORT / OMIT_WITH_REASON when any class is omitted. Deep retains company grounding, explicit Chinese H1 numbering and no arbitrary default word ceiling.

For event-led finance stories, `EVENT_TO_COMPANY` requires each material section to bind event/change -> mechanism -> company exposure -> operating/financial expression -> verification/reversal condition. A company name alone is not causal grounding.

`FINANCE_BROAD` remains a separate acquisition rebuild rather than shortened Deep.

Current publication acceptance requires evidence-backed Fact Integrity, Retention, Company Grounding, Structure/Numbering, Originality, Authorial Style, Compliance and Payoff. Originality uses source-compared evidence; close paraphrase/patchwriting requires revision and same-chat review cannot prove zero plagiarism.

Natural prose is material/story/voice first. Generic scaffolding is a diagnostic, not a phrase blacklist or humanizer stage.

## Knowledge and evolution

Financial retains topic cognition and method/failure-pattern cognition. Cataloging knowledge does not automatically promote a rule.

Every detected problem activates the UAOS-hosted cognition floor. Financial-owned evolution uses evidence -> competing hypotheses -> root-scope admission -> evolution disposition -> candidate branch/PR -> reproducible eval -> controlled promotion -> production reread -> live observation. Common/cross-domain changes are raised to UAOS as parent upcalls without transferring Financial business ownership.

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

CI also builds/installs the wheel and runs DOCX render smoke. Same-chat semantic review remains `CHAT_SELF_REVIEW`; stronger independence claims require distinct execution evidence.
